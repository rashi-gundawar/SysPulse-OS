# Automated diagnostic flowchart

```mermaid
flowchart TD
 A[Collect CPU, RAM, disk, uptime, process and network metrics] --> B[Load and validate saved thresholds]
 B --> C{Current value at critical threshold?}
 C -- Yes --> D[Create critical snapshot finding]
 C -- No --> E{Current value at warning threshold?}
 E -- Yes --> F[Create warning snapshot finding]
 E -- No --> G[No snapshot finding for this metric]
 D --> H[Inspect recent consecutive samples]
 F --> H
 G --> H
 H --> I{Configured number of samples remain above warning?}
 I -- Yes --> J[Calculate average and peak; create sustained finding]
 I -- No --> K[Evaluate network and failed-login heuristics]
 J --> K
 K --> L[Enrich findings with likely causes and recommended actions]
 L --> M[Persist metrics and alerts]
 M --> N[Dashboard, alert history and report]
```

## Diagnostic logic
- Current CPU, RAM and disk values are compared with independent warning and critical thresholds.
- Sustained rules evaluate a configurable window of consecutive samples and report the average and peak value.
- CPU and RAM findings can mention the top process returned by the process collector.
- Findings contain a plausible cause and practical next action. These are triage hypotheses, not definitive root-cause analysis.
- Network connection counts and available failed-login logs are heuristic signals; they can produce false positives and do not prove compromise.
