import psutil

def collect_network_metrics():
    counts = {"established": 0, "listening": 0, "other": 0}
    listeners = []
    try:
        for conn in psutil.net_connections(kind="inet"):
            status = (conn.status or "OTHER").upper()
            if status == "ESTABLISHED":
                counts["established"] += 1
            elif status == "LISTEN":
                counts["listening"] += 1
                if len(listeners) < 100:
                    addr = conn.laddr
                    listeners.append({"ip": getattr(addr, "ip", "") if addr else "",
                                      "port": getattr(addr, "port", None) if addr else None,
                                      "pid": conn.pid, "family": str(conn.family)})
            else:
                counts["other"] += 1
    except (psutil.AccessDenied, PermissionError):
        return {"available": False, "reason": "Permission denied; connection visibility is restricted.",
                "counts": counts, "listeners": []}
    return {"available": True, "reason": None, "counts": counts, "listeners": listeners}
