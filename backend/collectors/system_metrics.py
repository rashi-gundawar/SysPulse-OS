from datetime import datetime, timezone
import psutil

def collect_system_metrics():
    cpu = psutil.cpu_percent(interval=0.15)
    vm = psutil.virtual_memory()
    swap = psutil.swap_memory()
    now = datetime.now(timezone.utc)
    return {
        "timestamp": now.isoformat(),
        "cpu_percent": round(cpu, 2),
        "memory": {"total": vm.total, "available": vm.available, "used": vm.used, "percent": round(vm.percent, 2)},
        "swap": {"total": swap.total, "used": swap.used, "percent": round(swap.percent, 2)},
        "uptime_seconds": max(0, int(now.timestamp() - psutil.boot_time())),
    }
