# SysPulse OS — Operating System Monitoring & Algorithm Lab

SysPulse OS is an academic project aligned with a six-unit Operating Systems syllabus. It combines live host resource monitoring with interactive, educational simulations of core OS algorithms.

## Main modules

- **Overview:** live CPU, memory, disk and uptime cards; historical resource trends; recent diagnostic findings.
- **Process manager:** current process list, search by name/PID, sorting by CPU or memory.
- **CPU scheduling lab:** FCFS, non-preemptive SJF, non-preemptive Priority and Round Robin. Includes editable arrival/burst/priority inputs, Gantt chart, completion time, waiting time, turnaround time and averages.
- **Memory lab:** First Fit, Best Fit and Worst Fit contiguous allocation; FIFO, LRU and Optimal page replacement with frame history, page hits and faults.
- **Deadlocks & synchronization:** three selectable resource-allocation scenarios (two-process cycle, three-process cycle, and recoverable wait), wait-for dependency traces, all four Coffman conditions, a step-through Peterson example, and an interactive semaphore ownership/wait queue.
- **Disk scheduling lab:** FCFS, SSTF, SCAN and C-SCAN ordering, head movement summary and chart.
- **Kernel & Android:** selectable kernel architecture layers, three step-through request traces (file I/O, process creation/scheduling, and page-fault handling), Linux boot lifecycle, and Android platform layers.

## Syllabus mapping

| College unit | SysPulse OS module |
|---|---|
| I — OS overview, kernels, Linux shell | Overview + Kernel & Android |
| II — processes, threads, CPU scheduling | Process manager + CPU Scheduling |
| III — synchronization and deadlock | Deadlocks & Sync |
| IV — memory management and virtual memory | Memory Lab |
| V — file/I/O management and disk scheduling | Overview + Disk Scheduling |
| VI — Linux kernel internals and Android | Kernel & Android |

## Technology stack

- Frontend: React, Vite, Tailwind CSS, Recharts, Lucide
- Backend: Python, FastAPI, psutil
- Storage: SQLite for the existing metrics and diagnostic history
- Tests: Python `unittest` and API integration tests

## Run on Windows PowerShell (VS Code)

Open the extracted project root (the folder containing `requirements.txt`, `backend`, `dashboard`, `database`, `docs`, and `tests`).

### 1. Backend terminal

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m uvicorn backend.api:app --reload
```

If PowerShell blocks activation, use the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m uvicorn backend.api:app --reload
```

Keep this terminal open. Backend API documentation: http://127.0.0.1:8000/docs

### 2. Frontend terminal

Open a second terminal, from the project root:

```powershell
cd dashboard
npm install
npm run dev
```

Open the local URL printed by Vite, usually http://localhost:5173.

## Important interpretation notes

- Algorithm labs are **simulations** using editable example inputs. They do not change Windows' real scheduler, physical memory allocation, page tables, or disk-head behavior.
- Live monitoring describes the host information visible to the Python process. Permissions and Windows/WSL differences can affect fields.
- Diagnostic causes are hypotheses for investigation, not guaranteed root causes.
- The current backend retains its existing defensive checks. These are basic indicators, not a full antivirus, EDR, IDS, or vulnerability scanner.
- A Windows-specific Security Event Log integration for failed logons is not included in this OS-focused redesign; the existing failed-login parser may report N/A on Windows.
- Verify the app and run tests on your own machine before claiming all functions passed. Take genuine screenshots of the running app for your submission.

## Suggested demonstration

1. Show live CPU, RAM, disk and uptime.
2. Open Processes, sort by memory, and search for a process.
3. Run FCFS and Round Robin; explain the Gantt chart and average waiting time.
4. Run First Fit/Best Fit/Worst Fit with the same blocks and process sizes.
5. Compare FIFO, LRU and Optimal page faults with the same reference string.
6. Run FCFS and SSTF disk scheduling and compare head movement.
7. Compare the three deadlock examples, run the semaphore wait/signal controls, and step through Peterson's algorithm.
8. In System Internals, step through file I/O, process startup, and page-fault traces; then demonstrate Linux boot and Android layers.
9. Show stored history and diagnostic findings.

## Project structure

```text
system-resource-monitor-final/
├── backend/       # FastAPI, collectors, diagnostics and security checks
├── database/      # SQLite persistence
├── dashboard/     # React/Vite UI and OS algorithm labs
├── docs/          # Architecture, report and demo notes
├── tests/         # Backend unit and API tests
├── requirements.txt
└── README.md
```


## System Internals page
The System Internals page provides interactive educational explorers for kernel architecture, the Linux boot lifecycle, and Android architecture. These are simulations and do not inspect or control live kernel internals.


## Updated interactive examples

- **Deadlock example 1:** P1 holds R1 and waits for R2 while P2 holds R2 and waits for R1; the simulator highlights the circular wait.
- **Deadlock example 2:** P1, P2, and P3 form a three-process resource cycle.
- **Deadlock example 3:** P1 waits for R2 while P2 can finish and release it, demonstrating that waiting is not automatically deadlock.
- **Semaphore demo:** use `wait()` / `signal()` controls to see resource ownership and a blocked queue.
- **Kernel traces:** step through a file read, process creation/scheduling, or page-fault resolution across the user/kernel boundary.

These examples are deterministic teaching models, not live kernel instrumentation.
