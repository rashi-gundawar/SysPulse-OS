from backend.collectors.system_metrics import collect_system_metrics
from backend.collectors.disk_metrics import collect_disk_metrics
from backend.collectors.process_metrics import collect_process_metrics
from backend.collectors.network_metrics import collect_network_metrics
from backend.diagnostics.diagnostic_engine import diagnose, DEFAULT_THRESHOLDS
from database.database_manager import initialize_database,save_metrics,save_alerts,get_metrics,get_setting
from backend.security_checks import failed_login_summary

def collect_report(persist=True):
    initialize_database()
    sysm=collect_system_metrics(); disk=collect_disk_metrics("/")
    login_summary=failed_login_summary()
    metrics={**sysm,"disk":disk,"network":collect_network_metrics(),"failed_logins":login_summary}
    history=[]
    for sample in get_metrics(30):
        history.append({"cpu_percent":sample.get("cpu_percent",0),"memory_percent":sample.get("memory",{}).get("percent",0),"disk_percent":sample.get("disk",{}).get("percent",0)})
    history.append({"cpu_percent":metrics["cpu_percent"],"memory_percent":metrics["memory"]["percent"],"disk_percent":metrics["disk"]["percent"]})
    processes=collect_process_metrics(100)
    diagnosis=diagnose(metrics,get_setting("thresholds",DEFAULT_THRESHOLDS),history,processes=processes)
    metrics["diagnostics"]=diagnosis
    if persist:save_metrics(metrics);save_alerts(diagnosis["alerts"])
    return {"metrics":metrics,"diagnostics":diagnosis,"processes":processes}
if __name__=="__main__":
    import json;print(json.dumps(collect_report(),indent=2))
