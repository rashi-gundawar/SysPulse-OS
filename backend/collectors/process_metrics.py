import psutil

def collect_process_metrics(limit=100):
    rows = []
    for proc in psutil.process_iter(["pid", "name", "username", "memory_percent", "status"]):
        try:
            info = proc.info
            rows.append({"pid": info.get("pid"), "name": info.get("name") or "unknown",
                         "username": info.get("username") or "unavailable",
                         "memory_percent": round(float(info.get("memory_percent") or 0), 2),
                         "status": info.get("status") or "unknown",
                         "cpu_percent": round(proc.cpu_percent(interval=None), 2)})
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return sorted(rows, key=lambda x: x["memory_percent"], reverse=True)[:max(1, min(int(limit), 500))]
