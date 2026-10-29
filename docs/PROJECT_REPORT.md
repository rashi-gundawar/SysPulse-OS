# PROJECT REPORT
## System Resource Monitoring and Automated Performance Diagnostic Framework with Security Threat Detection and Alerting

**Stack:** Python, psutil, FastAPI, SQLite, React, Vite, Tailwind CSS, Recharts.

## Abstract
This project provides a local monitoring framework that collects system resource metrics, records historical samples, diagnoses threshold breaches and sustained high utilization, and presents results in a dashboard. It adds configurable alert settings, process inspection, network-connection inventory, file-integrity baselines, accessible Linux failed-login log analysis, simple network-count heuristics and an optional CPE-based NVD CVE lookup. SQLite stores metrics, settings, alerts and file baselines. CSV and HTML/printable reporting support review and demonstration. The application is an academic prototype and does not replace EDR, antivirus, SIEM or professional vulnerability assessment.

## 1. Problem statement
Users need one interface to observe CPU, RAM, disk, uptime and processes, understand persistent performance problems, retain history and review basic defensive security indicators. Single command-line snapshots do not provide a combined history, threshold management and explanatory dashboard.

## 2. Objectives
1. Collect live CPU, memory, swap, disk, process, network and uptime information.
2. Apply configurable warning and critical thresholds.
3. Detect sustained high utilization across consecutive samples.
4. Provide likely causes and recommended investigative actions.
5. Store metric history and alert records in SQLite.
6. Offer searchable/sortable process data in the dashboard.
7. Check file integrity using SHA-256 baselines.
8. Inventory listening sockets, process-name hints and accessible failed-login records.
9. Offer optional NVD CVE lookup for a user-provided CPE query.
10. Export metric CSV and a downloadable HTML report.
11. Include unit and API integration test suites.

## 3. Scope and exclusions
Included are local system telemetry, rule-based diagnosis, history, dashboard, file integrity, basic log parsing, network inventory and optional public vulnerability-data lookup. Excluded are automatic remediation, malware classification, packet inspection, comprehensive software inventory, guaranteed vulnerability matching, remote multi-host monitoring, authenticated users and push/email delivery.

## 4. Architecture
The collector layer uses psutil. The diagnostic layer evaluates snapshot and consecutive-sample rules. FastAPI validates settings and serves metrics, security checks and exports. SQLite persists samples, alerts, settings and file hashes. The React dashboard renders charts, tables and configuration controls. Refer to `ARCHITECTURE.md` and `DIAGNOSTIC_FLOWCHART.md`.

## 5. Diagnostic methodology
Current CPU, RAM and disk values are compared to configurable warning and critical levels. A sustained alert is created when each sample in a configured recent window remains at or above its warning threshold; the finding includes the sample count, average and peak. CPU and memory findings can include the top process identified by the process collector. Each finding supplies a likely-cause hypothesis and a practical recommended action, such as inspecting resource-heavy processes, checking whether workload changes are expected, reviewing filesystem growth, or validating listening services. Network-count and available failed-login log heuristics can also create findings. This is explainable rule-based triage, not machine learning or definitive root-cause analysis; findings may be false positives and should be verified by an administrator.

## 6. Security checks
- **File integrity:** SHA-256 hash comparisons show whether a selected file's content changed after a baseline was created.
- **Process-name heuristics:** a small review list identifies names that deserve verification; false positives and false negatives are expected.
- **Network inventory:** counts established/listening connections and lists visible listeners. Open ports are not inherently malicious.
- **Failed login parsing:** searches readable `/var/log/auth.log` or `/var/log/secure` files for common failure patterns, limited to the latest 50,000 lines. Systemd journal, different formats, permissions and log rotation may limit results.
- **Optional CVE lookup:** asks the NVD public API about a supplied CPE 2.3 name. Accurate CPE/version matching is essential; this is not an automated inventory-based vulnerability assessment.

## 7. Data design
SQLite tables: `metrics` stores timestamp and serialized telemetry; `alerts` stores diagnostic events; `settings` stores JSON threshold configuration; `file_baselines` stores path, SHA-256 digest and baseline timestamp.

## 8. Installation and usage
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
uvicorn backend.api:app --reload
```
Second terminal:
```bash
cd dashboard
npm install
npm run dev
```
Open the local Vite URL, usually `http://localhost:5173`. API documentation: `http://127.0.0.1:8000/docs`.

## 9. Testing
Run automated tests with `python -m unittest discover -s tests -v`. Tests cover collector shape, threshold logic, sustained alerts, network heuristics, basic database reads and API endpoints. Record the actual output from the target machine. Do not state that tests passed until they have been executed successfully. Manual steps are in `TEST_PLAN.md`.

## 10. Limitations
Metrics describe the environment where Python runs; WSL2 measurements do not equal Windows host measurements. Some socket and log data require permissions. The NVD API requires internet access and a correctly specified CPE. The app has no authentication and should not be exposed beyond localhost. Security findings are review indicators, not proof of compromise.

## 11. Future work
Potential improvements include authenticated access, configurable retention, email notifications, host-specific log adapters, improved baselining, richer network anomaly analysis, signed PDF reports, and a maintained asset inventory for vulnerability assessment.

## 12. Conclusion
The prototype combines resource collection, historical storage, explainable threshold diagnostics and defensive host checks in one dashboard. Its modular architecture supports future development and demonstrates API design, database persistence, system programming, frontend visualization and security monitoring concepts.

## References
- psutil: https://psutil.readthedocs.io/
- FastAPI: https://fastapi.tiangolo.com/
- SQLite: https://www.sqlite.org/docs.html
- React: https://react.dev/
- Tailwind CSS: https://tailwindcss.com/docs
- NVD CVE API: https://nvd.nist.gov/developers/vulnerabilities
