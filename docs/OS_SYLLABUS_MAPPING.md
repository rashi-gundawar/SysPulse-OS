# OS syllabus mapping and simulator notes

## Unit I — Operating Systems Overview
The dashboard reports resource utilization and uptime. The Kernel & Android page explains kernel responsibilities and kernel structures (monolithic, microkernel, hybrid, modular), user/kernel space, system calls and Linux boot flow. Use a Linux terminal for shell-command demonstrations.

## Unit II — Process Concepts and CPU Scheduling
The process manager lists visible processes with PID, process name, CPU and memory use. The scheduling lab supports FCFS, non-preemptive SJF, non-preemptive Priority (lower number means higher priority), and Round Robin. It computes completion time, turnaround time, waiting time, averages and a Gantt timeline.

Formulas:
- Turnaround time = completion time − arrival time
- Waiting time = turnaround time − burst time
- Average waiting time = sum of waiting times / number of processes
- Average turnaround time = sum of turnaround times / number of processes

## Unit III — Synchronization and Deadlock
The page describes mutual exclusion, hold-and-wait, no preemption and circular wait, and introduces Peterson's solution and semaphores. It is an educational explanation, not a live lock monitor or production concurrency test.

## Unit IV — Memory Management
The allocation simulator compares First Fit, Best Fit and Worst Fit on user-entered memory blocks and process sizes. The page replacement simulator supports FIFO, LRU and Optimal and shows the frame state after every reference, plus page hits and faults.

## Unit V — File and I/O Management
The live dashboard shows filesystem usage. The disk scheduling lab supports FCFS, SSTF, SCAN and C-SCAN and reports request order and total head movement. The model is illustrative and does not measure real physical-disk latency.

## Unit VI — Kernel Internals and Android OS
The Kernel & Android page summarizes kernel duties, system calls, the Linux boot sequence, PCB/task-structure concepts, Android Runtime (ART), HAL, native libraries, application framework and application layer.

## Boundaries
Simulators do not change the host operating system. They are designed to make syllabus algorithms visible and testable. Results should be checked against worked examples before being used in a report.
