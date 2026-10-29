import csv, io, json, sqlite3
from pathlib import Path
DB_PATH = Path(__file__).resolve().parent / "monitoring.db"

def connect():
    conn=sqlite3.connect(DB_PATH); conn.row_factory=sqlite3.Row; return conn

def initialize_database():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS metrics(id INTEGER PRIMARY KEY AUTOINCREMENT,timestamp TEXT NOT NULL,cpu_percent REAL,memory_percent REAL,disk_percent REAL,uptime_seconds INTEGER,payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS alerts(id INTEGER PRIMARY KEY AUTOINCREMENT,timestamp TEXT NOT NULL,severity TEXT NOT NULL,category TEXT NOT NULL,rule TEXT NOT NULL,message TEXT NOT NULL,payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS file_baselines(path TEXT PRIMARY KEY,sha256 TEXT NOT NULL,checked_at TEXT NOT NULL);
        """)

def save_metrics(m):
    initialize_database()
    with connect() as db:
        db.execute("INSERT INTO metrics(timestamp,cpu_percent,memory_percent,disk_percent,uptime_seconds,payload) VALUES(?,?,?,?,?,?)",
        (m["timestamp"],m["cpu_percent"],m["memory"]["percent"],m["disk"]["percent"],m["uptime_seconds"],json.dumps(m)))

def get_metrics(limit=60):
    initialize_database()
    with connect() as db:
        rows=db.execute("SELECT payload FROM metrics ORDER BY id DESC LIMIT ?",(max(1,min(int(limit),1000)),)).fetchall()
    return [json.loads(r["payload"]) for r in reversed(rows)]

def save_alerts(alerts):
    if not alerts:return
    initialize_database()
    with connect() as db:
        for a in alerts:
            db.execute("INSERT INTO alerts(timestamp,severity,category,rule,message,payload) VALUES(?,?,?,?,?,?)",
            (a["timestamp"],a["severity"],a["category"],a["rule"],a["message"],json.dumps(a)))

def get_alerts(limit=100):
    initialize_database()
    with connect() as db:
        rows=db.execute("SELECT payload FROM alerts ORDER BY id DESC LIMIT ?",(max(1,min(int(limit),1000)),)).fetchall()
    return [json.loads(r["payload"]) for r in rows]

def get_setting(key,default=None):
    initialize_database()
    with connect() as db: row=db.execute("SELECT value FROM settings WHERE key=?",(key,)).fetchone()
    return json.loads(row["value"]) if row else default

def set_setting(key,value):
    initialize_database()
    with connect() as db:
        db.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(key,json.dumps(value)))

def metrics_csv():
    rows=get_metrics(1000); out=io.StringIO()
    fields=["timestamp","cpu_percent","memory_percent","disk_percent","uptime_seconds"]
    writer=csv.DictWriter(out,fieldnames=fields);writer.writeheader()
    for m in rows: writer.writerow({"timestamp":m["timestamp"],"cpu_percent":m["cpu_percent"],"memory_percent":m["memory"]["percent"],"disk_percent":m["disk"]["percent"],"uptime_seconds":m["uptime_seconds"]})
    return out.getvalue()
