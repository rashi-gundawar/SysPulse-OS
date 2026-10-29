from datetime import datetime, timezone
from html import escape
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, HTMLResponse
from pydantic import BaseModel, Field
from database.database_manager import initialize_database,get_metrics,get_alerts,get_setting,set_setting,metrics_csv,connect
from backend.monitoring_service import collect_report
from backend.diagnostics.diagnostic_engine import DEFAULT_THRESHOLDS,validate_thresholds
from backend.security_checks import create_baseline,check_baseline,run_security_checks,nvd_cve_lookup

app=FastAPI(title="SysPulse Monitoring and Security Triage",version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:5173","http://127.0.0.1:5173","http://localhost:4173","http://127.0.0.1:4173"],allow_methods=["*"],allow_headers=["*"])

class ThresholdSettings(BaseModel):
    cpu_warning:float=Field(70,ge=0,le=100);cpu_critical:float=Field(90,ge=0,le=100)
    memory_warning:float=Field(75,ge=0,le=100);memory_critical:float=Field(90,ge=0,le=100)
    disk_warning:float=Field(80,ge=0,le=100);disk_critical:float=Field(90,ge=0,le=100)
    sustained_samples:int=Field(3,ge=2,le=30)
    established_connections_warning:int=Field(150,ge=0,le=100000)
    listening_ports_warning:int=Field(30,ge=0,le=100000)
    failed_logins_warning:int=Field(10,ge=0,le=100000)
class BaselineRequest(BaseModel):path:str
class CpeRequest(BaseModel):cpeName:str;results:int=Field(10,ge=1,le=20)

@app.on_event("startup")
def startup():initialize_database()
@app.get("/api/health")
def health():return {"status":"ok","service":"SysPulse"}
@app.get("/api/metrics/current")
def current_metrics():return collect_report()
@app.post("/api/collect")
def collect_now():return collect_report()
@app.get("/api/metrics/history")
def history(limit:int=60):return get_metrics(limit)
@app.get("/api/processes")
def processes(limit:int=100):return collect_report(persist=False)["processes"][:max(1,min(limit,500))]
@app.get("/api/alerts")
def alerts(limit:int=100):return get_alerts(limit)
@app.get("/api/settings/thresholds")
def read_thresholds():return get_setting("thresholds",DEFAULT_THRESHOLDS)
@app.put("/api/settings/thresholds")
def update_thresholds(settings:ThresholdSettings):
    try:values=validate_thresholds(settings.model_dump())
    except ValueError as exc:raise HTTPException(status_code=422,detail=str(exc))
    set_setting("thresholds",values);return {"saved":True,"thresholds":values}
@app.get("/api/security/checks")
def security_checks():return run_security_checks()
@app.get("/api/security/failed-logins")
def failed_logins():return run_security_checks()["failed_logins"]
@app.post("/api/security/baseline")
def baseline(req:BaselineRequest):
    try:item=create_baseline(req.path)
    except (ValueError,OSError) as exc:raise HTTPException(status_code=400,detail=str(exc))
    initialize_database()
    with connect() as db:db.execute("INSERT INTO file_baselines(path,sha256,checked_at) VALUES(?,?,datetime('now')) ON CONFLICT(path) DO UPDATE SET sha256=excluded.sha256,checked_at=excluded.checked_at",(item["path"],item["sha256"]))
    return {"created":True,**item}
@app.post("/api/security/integrity-check")
def integrity_check():
    initialize_database()
    with connect() as db:rows=db.execute("SELECT path,sha256 FROM file_baselines").fetchall()
    return {"results":[check_baseline(r["path"],r["sha256"]) for r in rows],"count":len(rows)}
@app.get("/api/security/vulnerabilities")
def vulnerabilities(cpeName:str,results:int=10):
    try:return nvd_cve_lookup(cpeName,results)
    except ValueError as exc:raise HTTPException(status_code=422,detail=str(exc))
@app.get("/api/export/metrics.csv",response_class=PlainTextResponse)
def export_csv():return PlainTextResponse(metrics_csv(),media_type="text/csv",headers={"Content-Disposition":"attachment; filename=syspulse-metrics.csv"})
@app.get("/api/report")
def report():
    rows=get_metrics(1000)
    return {"title":"System Resource Monitoring and Automated Performance Diagnostic Framework with Security Threat Detection and Alerting","generated_at":datetime.now(timezone.utc).isoformat(),"samples":len(rows),"latest":rows[-1] if rows else None,"alerts":get_alerts(100),"thresholds":get_setting("thresholds",DEFAULT_THRESHOLDS),"scope":"Local monitoring and defensive triage; not a replacement for EDR or a comprehensive vulnerability scanner."}
@app.get("/api/report/download",response_class=HTMLResponse)
def report_download():
    data=report();latest=data["latest"] or {};mem=(latest.get("memory") or {}).get("percent","—");disk=(latest.get("disk") or {}).get("percent","—")
    alert_rows="".join(f"<tr><td>{escape(str(a.get('timestamp','')))}</td><td>{escape(str(a.get('severity','')))}</td><td>{escape(str(a.get('category','')))}</td><td>{escape(str(a.get('message','')))}</td></tr>" for a in data["alerts"])
    html=f"""<!doctype html><html><head><meta charset="utf-8"><title>SysPulse Project Health Report</title><style>body{{font:15px Arial;max-width:1000px;margin:40px auto;color:#172033;line-height:1.55}}h1{{color:#234ba5}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ccd4df;padding:8px;text-align:left}}.meta{{background:#eef3fb;padding:15px;border-radius:8px}}button{{padding:10px 16px}}</style></head><body><button onclick="window.print()">Print / Save as PDF</button><h1>{escape(data['title'])}</h1><div class="meta"><b>Generated:</b> {escape(data['generated_at'])}<br><b>Stored samples:</b> {data['samples']}<br><b>Latest CPU:</b> {latest.get('cpu_percent','—')}%<br><b>Latest RAM:</b> {mem}%<br><b>Latest disk:</b> {disk}%<br><b>Uptime seconds:</b> {latest.get('uptime_seconds','—')}</div><h2>Recent alerts</h2><table><thead><tr><th>Timestamp</th><th>Severity</th><th>Category</th><th>Finding</th></tr></thead><tbody>{alert_rows or '<tr><td colspan="4">No stored alerts.</td></tr>'}</tbody></table><h2>Scope and limitations</h2><p>{escape(data['scope'])} Security heuristics may produce false positives and do not establish compromise.</p><p>Generated by SysPulse student project.</p></body></html>"""
    return HTMLResponse(html,headers={"Content-Disposition":"attachment; filename=syspulse-report.html"})
