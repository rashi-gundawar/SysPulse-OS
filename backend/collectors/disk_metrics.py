import psutil

def collect_disk_metrics(path="/"):
    usage = psutil.disk_usage(path)
    return {"path": path, "total": usage.total, "used": usage.used, "free": usage.free, "percent": round(usage.percent, 2)}
