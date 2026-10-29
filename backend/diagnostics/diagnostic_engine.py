"""Rule-based diagnostics with configurable thresholds and sustained-sample analysis.

These findings are triage hints, not proof of a hardware fault or security compromise.
"""
from datetime import datetime, timezone

DEFAULT_THRESHOLDS = {
    "cpu_warning": 70.0, "cpu_critical": 90.0,
    "memory_warning": 75.0, "memory_critical": 90.0,
    "disk_warning": 80.0, "disk_critical": 90.0,
    "sustained_samples": 3, "established_connections_warning": 150,
    "listening_ports_warning": 30, "failed_logins_warning": 10,
}


def validate_thresholds(values):
    merged = {**DEFAULT_THRESHOLDS, **(values or {})}
    for key in ("cpu_warning", "cpu_critical", "memory_warning", "memory_critical", "disk_warning", "disk_critical"):
        merged[key] = float(merged[key])
        if not 0 <= merged[key] <= 100:
            raise ValueError(f"{key} must be between 0 and 100")
    for name in ("cpu", "memory", "disk"):
        if merged[f"{name}_warning"] >= merged[f"{name}_critical"]:
            raise ValueError(f"{name.title()} warning threshold must be lower than critical threshold")
    merged["sustained_samples"] = int(merged["sustained_samples"])
    if not 2 <= merged["sustained_samples"] <= 30:
        raise ValueError("sustained_samples must be between 2 and 30")
    for key in ("established_connections_warning", "listening_ports_warning", "failed_logins_warning"):
        merged[key] = int(merged[key])
        if not 0 <= merged[key] <= 100000:
            raise ValueError(f"{key} must be between 0 and 100000")
    return merged


def _top_process(processes, field):
    """Return the top process by field, if the collector supplied process data."""
    valid = [p for p in (processes or []) if isinstance(p, dict)]
    if not valid:
        return None
    item = max(valid, key=lambda p: float(p.get(field) or 0))
    if float(item.get(field) or 0) <= 0:
        return None
    return item


def diagnose(metrics, thresholds=None, history=None, processes=None):
    """Evaluate current values and recent samples; include plausible causes/actions."""
    t = validate_thresholds(thresholds)
    history = history or []
    alerts = []
    now = metrics.get("timestamp") or datetime.now(timezone.utc).isoformat()
    top_cpu = _top_process(processes, "cpu_percent")
    top_mem = _top_process(processes, "memory_percent")
    memory = metrics.get("memory") or {}
    disk = metrics.get("disk") or {}
    disk_free = disk.get("free_gb")
    disk_total = disk.get("total_gb")

    specs = [
        ("CPU", float(metrics.get("cpu_percent", 0) or 0), t["cpu_warning"], t["cpu_critical"],
         "High CPU can result from a compute-heavy workload, a runaway/stuck process, background updates, or unexpected activity.",
         "Sort processes by CPU, verify the top process is expected, check recent workload changes, and investigate persistent high use.", top_cpu, "cpu_percent"),
        ("Memory", float(memory.get("percent", 0) or 0), t["memory_warning"], t["memory_critical"],
         "High RAM use can be caused by many active applications, a large workload, cache use, or a possible memory leak.",
         "Sort processes by memory, close or restart only understood applications, and compare memory usage across samples to see whether it keeps growing.", top_mem, "memory_percent"),
        ("Disk", float(disk.get("percent", 0) or 0), t["disk_warning"], t["disk_critical"],
         "The monitored filesystem is approaching capacity; logs, caches, downloads, databases, or application data may be contributing.",
         "Check the filesystem and identify large files/logs; archive or remove only files you recognize, and confirm free space after cleanup.", None, "disk_percent"),
    ]

    for label, value, warning, critical, cause, action, culprit, history_key in specs:
        if value >= critical:
            severity = "CRITICAL"
        elif value >= warning:
            severity = "WARNING"
        else:
            continue
        if label == "CPU" and culprit:
            cause += f" The current top CPU process is {culprit.get('name', 'unknown')} (PID {culprit.get('pid', 'unknown')}, {float(culprit.get('cpu_percent') or 0):.1f}% reported process CPU)."
        elif label == "Memory" and culprit:
            cause += f" The largest reported process by memory is {culprit.get('name', 'unknown')} (PID {culprit.get('pid', 'unknown')}, {float(culprit.get('memory_percent') or 0):.1f}% of system memory)."
        if label == "Disk" and disk_free is not None:
            action += f" Reported free space: {disk_free} GB" + (f" of {disk_total} GB." if disk_total is not None else ".")
        alerts.append({"timestamp": now, "severity": severity, "category": label,
                       "rule": "snapshot_threshold", "value": round(value, 2),
                       "threshold": critical if severity == "CRITICAL" else warning,
                       "message": f"{label} usage is {value:.1f}% (warning {warning:.0f}%, critical {critical:.0f}%).",
                       "likely_cause": cause, "recommended_action": action})

    n = t["sustained_samples"]
    for label, key, warning, critical in [
        ("CPU", "cpu_percent", t["cpu_warning"], t["cpu_critical"]),
        ("Memory", "memory_percent", t["memory_warning"], t["memory_critical"]),
        ("Disk", "disk_percent", t["disk_warning"], t["disk_critical"]),
    ]:
        recent = history[-n:]
        if len(recent) == n and all(float(sample.get(key, 0) or 0) >= warning for sample in recent):
            average = sum(float(sample.get(key, 0) or 0) for sample in recent) / n
            max_value = max(float(sample.get(key, 0) or 0) for sample in recent)
            severity = "CRITICAL" if all(float(sample.get(key, 0) or 0) >= critical for sample in recent) else "WARNING"
            if label == "CPU":
                cause = "CPU utilization remained elevated across consecutive samples, suggesting a sustained workload rather than a single short spike."
                action = "Review the top CPU processes, scheduled jobs, background updates, and whether the workload is expected; compare with a normal baseline."
            elif label == "Memory":
                cause = "Memory utilization remained elevated across consecutive samples; a memory-intensive workload or steadily growing process may be responsible."
                action = "Compare process memory over time. If one process grows continuously, inspect its logs/configuration and restart it only if safe; check swap pressure too."
            else:
                cause = "Disk utilization remained above the warning threshold. Capacity may continue to decline as logs, caches, or application data grow."
                action = "Check filesystem growth and large directories, set log rotation/retention, and plan capacity expansion if growth is expected."
            alerts.append({"timestamp": now, "severity": severity, "category": label,
                           "rule": "sustained_threshold", "value": round(average, 2),
                           "threshold": warning, "samples": n,
                           "message": f"{label} usage stayed at/above {warning:.0f}% for {n} consecutive samples (average {average:.1f}%, peak {max_value:.1f}%).",
                           "likely_cause": cause, "recommended_action": action})

    network = metrics.get("network") or {}
    counts = network.get("counts") or {}
    established = int(counts.get("established", 0) or 0)
    listening = int(counts.get("listening", 0) or 0)
    if established >= t["established_connections_warning"]:
        alerts.append({"timestamp": now, "severity": "WARNING", "category": "Network", "rule": "connection_count_heuristic",
                       "message": f"Established connection count is {established} (configured threshold {t['established_connections_warning']}).",
                       "likely_cause": "Many active connections may be normal for browsers, development tools, or servers; an unexpected increase can also indicate misconfiguration or unusual activity.",
                       "recommended_action": "Inspect owning processes and remote endpoints where permissions allow, compare with a known-good baseline, and investigate only unfamiliar connections."})
    if listening >= t["listening_ports_warning"]:
        alerts.append({"timestamp": now, "severity": "WARNING", "category": "Network", "rule": "listener_count_heuristic",
                       "message": f"Listening socket count is {listening} (configured threshold {t['listening_ports_warning']}).",
                       "likely_cause": "Several services are accepting connections; count alone does not indicate compromise.",
                       "recommended_action": "Identify each listening service and confirm it is required. Disable only services you understand and are authorized to change."})

    failed = metrics.get("failed_logins") or {}
    failed_count = int(failed.get("count", 0) or 0)
    if failed_count >= t["failed_logins_warning"] and failed_count > 0:
        alerts.append({"timestamp": now, "severity": "WARNING", "category": "Security", "rule": "failed_login_threshold",
                       "message": f"Failed-login events found: {failed_count} (configured threshold {t['failed_logins_warning']}).",
                       "likely_cause": "Repeated authentication failures may result from mistyped credentials, a misconfigured service, or attempted unauthorized access.",
                       "recommended_action": "Review available authentication logs and timestamps, verify legitimate services, and follow your organization's account-lockout/MFA policy. Log access may be unavailable on some systems."})

    order = {"CRITICAL": 3, "WARNING": 2, "INFO": 1}
    health = "HEALTHY" if not alerts else max((a["severity"] for a in alerts), key=lambda s: order.get(s, 0))
    return {"overall_health": health, "alerts": alerts, "thresholds": t,
            "diagnostic_summary": {"rules_evaluated": 7, "sustained_samples_required": n,
                                   "samples_available": len(history), "method": "configurable rule-based thresholds and consecutive-sample analysis"}}
