# Test Plan and Demonstration Checklist

## Automated tests
Run `python -m unittest discover -s tests -v` from the root after installing requirements. Record the actual result and any platform-specific skips/failures.

## Manual integration
- [ ] `/api/health` returns status `ok`.
- [ ] Dashboard loads and fetch requests work without CORS errors.
- [ ] CPU/RAM/disk/uptime appear and chart updates after several samples.
- [ ] Process table supports text filtering, sorting and minimum CPU/RAM filters.
- [ ] Save alert thresholds; invalid warning >= critical values are rejected.
- [ ] Sustained warning appears after enough consecutive samples.
- [ ] Create a baseline for a file you own; edit it; integrity check reports `CHANGED`.
- [ ] Security checks explain when auth logs or socket visibility are unavailable.
- [ ] Optional CPE lookup handles invalid query and network errors.
- [ ] CSV and HTML report downloads work.
- [ ] Browser print dialog can save report/dashboard as PDF.

## Safe demo scenario
Temporarily set CPU warning to a low value such as 1%, save, and observe a warning; restore normal thresholds afterward. Do not stress the machine or change files you do not own.
