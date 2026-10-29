import hashlib, os, re, urllib.parse, urllib.request, json
from pathlib import Path
from datetime import datetime, timezone
import psutil
from backend.collectors.network_metrics import collect_network_metrics

SUSPICIOUS_NAME_HINTS=("mimikatz","keylogger","cryptominer","xmrig","nc.exe")

def sha256_file(path):
    digest=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(65536),b""):digest.update(chunk)
    return digest.hexdigest()

def create_baseline(path):
    resolved=str(Path(path).expanduser().resolve(strict=True))
    if not Path(resolved).is_file():raise ValueError("Baseline path must be a regular file")
    return {"path":resolved,"sha256":sha256_file(resolved)}

def check_baseline(path,expected_hash):
    try:
        actual=sha256_file(path)
        return {"path":path,"status":"MATCH" if actual==expected_hash else "CHANGED","expected_sha256":expected_hash,"actual_sha256":actual}
    except OSError as exc:return {"path":path,"status":"ERROR","message":str(exc)}

def failed_login_summary():
    candidates=[Path("/var/log/auth.log"),Path("/var/log/secure")]
    available=[p for p in candidates if p.exists() and os.access(p,os.R_OK)]
    if not available:
        return {"available":False,"count":None,"source":None,"message":"No readable auth.log/secure file found; check OS and permissions."}
    path=available[0]
    try:
        lines=path.read_text(errors="replace").splitlines()[-50000:]
        matches=[line for line in lines if re.search(r"failed password|authentication failure|invalid user",line,re.I)]
        return {"available":True,"count":len(matches),"source":str(path),"sample":matches[-5:],
                "message":"Count covers the most recent 50,000 lines, not a complete forensic audit."}
    except OSError as exc:return {"available":False,"count":None,"source":str(path),"message":str(exc)}

def run_security_checks():
    hints=[]
    for proc in psutil.process_iter(["pid","name"]):
        try:
            name=(proc.info.get("name") or "").lower()
            if any(token in name for token in SUSPICIOUS_NAME_HINTS):
                hints.append({"type":"process_name_heuristic","severity":"REVIEW","pid":proc.info.get("pid"),"name":proc.info.get("name"),
                              "message":"Name matched a review heuristic; validate the process before taking action."})
        except (psutil.NoSuchProcess,psutil.AccessDenied):pass
    return {"checked_at":datetime.now(timezone.utc).isoformat(),"process_name_hints":hints,
            "network":collect_network_metrics(),"failed_logins":failed_login_summary(),
            "notes":["Process-name matches can be false positives.","Listening ports and connection counts are context signals, not proof of compromise.","Some metrics and logs require elevated permissions."]}

def nvd_cve_lookup(cpe_name, results=10):
    # Explicit CPE lookup only. Best-effort public NVD API request; do not use as a full vulnerability assessment.
    if not cpe_name or not cpe_name.startswith("cpe:2.3:"):
        raise ValueError("Enter a CPE 2.3 name beginning with cpe:2.3: (example format: cpe:2.3:a:vendor:product:version:*:*:*:*:*:*:*)")
    query=urllib.parse.urlencode({"cpeName":cpe_name,"resultsPerPage":max(1,min(int(results),20))})
    req=urllib.request.Request("https://services.nvd.nist.gov/rest/json/cves/2.0?"+query,headers={"User-Agent":"SysPulse-Student-Project/1.0"})
    try:
        with urllib.request.urlopen(req,timeout=8) as response:data=json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        return {"available":False,"query":cpe_name,"message":f"NVD lookup unavailable: {exc}","vulnerabilities":[]}
    vulns=[]
    for item in data.get("vulnerabilities",[]):
        cve=item.get("cve",{})
        descriptions=cve.get("descriptions",[])
        desc=next((d.get("value","") for d in descriptions if d.get("lang")=="en"),"")
        metrics=cve.get("metrics",{})
        score=None
        for family in ("cvssMetricV40","cvssMetricV31","cvssMetricV30","cvssMetricV2"):
            if metrics.get(family):
                score=metrics[family][0].get("cvssData",{}).get("baseScore");break
        vulns.append({"id":cve.get("id"),"published":cve.get("published"),"score":score,"description":desc[:500]})
    return {"available":True,"query":cpe_name,"total_results":data.get("totalResults",len(vulns)),"vulnerabilities":vulns}
