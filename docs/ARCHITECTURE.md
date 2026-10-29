# Architecture and Data Flow

```mermaid
flowchart TD
  A[psutil collectors] --> B[Monitoring service]
  B --> C[Diagnostic engine]
  C --> D[SQLite metrics and alerts]
  B --> D
  D --> E[FastAPI REST API]
  E --> F[React + Vite + Tailwind dashboard]
  E --> G[CSV / HTML report export]
  H[File SHA-256 baseline] --> E
  I[Auth log + network inventory + process heuristics] --> E
  J[Optional NVD CPE lookup] --> E
```

## Request lifecycle
1. Dashboard requests the current sample.
2. Collectors gather resource and host inventory data.
3. The diagnostic engine applies current thresholds and evaluates consecutive samples.
4. The service stores the sample and resulting alerts in SQLite.
5. API returns JSON to the dashboard.
6. User can review history, change thresholds, run defensive checks, or export reports.
