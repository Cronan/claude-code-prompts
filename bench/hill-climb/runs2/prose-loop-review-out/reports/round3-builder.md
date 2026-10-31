### Builder findings — round 3
B-1 | blocker | RUNBOOK.md:56-61 (with 43, 46) | Step 13 says "start the service, then repeat step 9". Step 9 filters `journalctl --since "<start>"`, defined as "the time from step 8". Step 13's start command (line 60) prints no time. If the engineer reuses the step 8 time, the filter includes the error lines from the failed new-key run, which is why Rollback was entered. This applies to a step 9 failure and to a step 7 failure that was followed by a start. | Rollback's check can never print `-- No entries --` on that path. Every rollback after a step 9 failure then ends at step 14 and pages the platform lead, although the old key was restored correctly. This breaks Definition of done 3. | Change line 60 to `sudo systemctl start ingest.service && date -u '+%F %T'`. Append to line 56 after "then repeat step 9": "using the time printed here as `<start>`". No lines are added; the file stays at 68. | Read steps 13 and 9 in order as the on-call engineer. The only `<start>` available must be the one printed by step 13. Orchestrator: run the modified line on the dummy host and confirm it prints one `YYYY-MM-DD HH:MM:SS` line. | high

### Feature proposal (optional, at most 1)
None.

### Out of scope (optional, one line each)
- Step 6's "go to step 14" branch leaves the service stopped, but the runbook never says so. Step 14 pages the lead anyway, so this is not blocking.
