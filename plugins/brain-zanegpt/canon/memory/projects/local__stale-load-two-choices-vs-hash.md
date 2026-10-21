# local/stale-load-two-choices-vs-hash — lessons

Project: local/stale-load-two-choices-vs-hash. Newest first.

---

## E1 — stale load two choices vs hash
- Date: 2026-10-15
- Project: local/stale-load-two-choices-vs-hash
- Tags: [load-balancing][queueing][sandbox][testing]
- What: With real queues that drain (not the kernel's cumulative work), stale least-loaded still
  herds (peak queue 89 vs 27 for two choices at a report every 100 jobs), but two choices on
  that stale report did worse than a blind hash (peak 27 vs 22.6, mean 5.4 vs 3.5).
- Why built: Weakest-link train pick: the load-balancing kernel was modelled with cumulative assigned
  work and no departures, so its ranking (two choices 1.12 vs hash 1.14 at stale reports) was
  untested on queues that empty, which is how real servers behave.
- Design: 10 servers each draining one unit per tick, arrivals every mean size / 9 ticks (90%
  utilisation), 20,000 jobs, equal sizes or 5% of jobs 40x. Report of queue lengths refreshed
  every 1, 10 or 100 arrivals. Policies: least-loaded and two choices by the report
  (deterministic LCG picks), round-robin, one LCG pick (hash). Metrics: peak queue on any
  server and time-mean queue.
- Got right: The kernel's main claims survive departures: fresh least-loaded is best (peak 1.0), stale
  least-loaded herds badly (89 at R 100), and two choices degrades far less (27); with heavy
  tails fresh least-loaded kept the peak at 40 against 95 for two choices.
- Where/why it failed: At R 100 two choices lost to a blind hash on equal jobs (peak 27.0 vs 22.6, mean 5.41 vs
  3.52): a 100-job-old report is worse than no report, since both choices often look equally
  light. Round-robin's heavy-tail peak of 3268 is an artefact: my heavy-job pattern repeats
  every 100 jobs and aliases with the 10-server rotation.
- Fix: Use two choices only while the load report is fresher than a few jobs per server; once it is
  roughly 10 jobs per server old, fall back to random or hashed placement, and test any
  rotation policy with non-periodic job sizes.
- Why this fix: Two choices helps by reading a real difference between two servers; when the report is older
  than the queues' turnover, the difference it reads is noise, and acting on it concentrates
  arrivals on whichever server looked light at the last refresh.
- Rule of thumb: With draining queues, stale least-loaded herds (89 vs 27 peak at a 100-job-old report) but
  two choices on that report lost to a blind hash (27 vs 22.6); drop the report once it is
  older than queue turnover.
- Provenance (verified/assumed): Verified first-hand by the sandbox below; fluid queues with deterministic arrivals and an
  LCG, not real latency; the round-robin heavy-tail number is an aliasing artefact of my
  periodic size pattern and is not a claim.
- Composed: ideas:LOAD-BALANCING/dispatch/least-loaded-herds-on-stale-load-info
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__stale-load-two-choices-vs-hash.py
- Prediction: Written before running: at R 100 stale least-loaded's peak >= 2x two choices'; fresh least-
  loaded best; heavy tails round-robin peak >= 2x fresh least-loaded's.
- Observed: RESULT: PASS equal R100 peak least 89.0 vs two 27.0; fresh least best (1.0); heavy R1 rr
  3268.2 vs least 40.0 (aliasing artefact); equal R100 two 27.0/5.41 vs hash 22.6/3.52; heavy
  R100 least 262.5 vs two 184.4.
- Scenarios: 1) equal jobs at report ages 1, 10, 100; 2) heavy-tailed jobs at the same ages; 3) blind
  hash baseline, built to break the claim that two choices always beats no information.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

