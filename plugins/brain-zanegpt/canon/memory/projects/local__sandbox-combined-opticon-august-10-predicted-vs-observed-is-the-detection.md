# local/sandbox-combined-opticon-august-10-predicted-vs-observed-is-the-detection — lessons

Project: local/sandbox-combined-opticon-august-10-predicted-vs-observed-is-the-detection. Newest first.

---

## E1 — sandbox combined opticon august 10 predicted vs observed is the detection
- Date: 2026-08-29
- Project: local/sandbox-combined-opticon-august-10-predicted-vs-observed-is-the-detection
- Tags: [observability][state][testing][method]
- What: A deterministic sandbox (200 fixed turns, modular arithmetic instead of RNG) running opticon#E28's clear-before-read lifecycle bug on a per-turn public-claim field, instrumented with august-10#E17's per-conjunct marginal rates alongside the outcome counter.
- Why built: opticon#E28 records that a "bluff" field cleared at end-of-turn was always null by the time the next turn's AI danger-check read it, making the whole branch dead code since it shipped, and prescribes an explicit snapshot before the clear. august-10#E17 records that an outcome counter at 0 reads identically for correctly-rare and structurally-impossible, and prescribes instrumenting each conjunct's marginal rate and multiplying. This tests whether E17's remedy actually reaches E28's dead branch.
- Design: A field set on roughly a quarter of turns, cleared at end of turn, and read by a danger check occurring on roughly two-fifths of turns, run with and without a snapshot taken before the clear. Both the outcome counter and each conjunct's marginal rate are recorded.
- Got right: Holding both conjunct rates identical across the buggy and fixed runs by construction, so the only quantity that changes is the outcome — which is what makes the predicted-versus-observed contradiction the sole detectable signal.
- Where/why it failed: With the bug the outcome counter is 0, indistinguishable from a correctly-rare mechanic. august-10#E17's conjunct instrumentation reports both preconditions fully healthy — the field is set on 25% of turns and the check runs on 40% — so the rates alone describe a healthy system. The detection is available only as a contradiction: multiplying the marginals predicts a nonzero fire rate, and the observed 0 contradicts that prediction. The snapshot fix fires 22 times on the identical schedule.
- Fix: Compute and record the PREDICTED fire rate from the conjunct marginals alongside the observed count, and alarm on the discrepancy — instrumenting the conjuncts without carrying out the multiplication and comparison provides no detection at all for a lifecycle defect between them.
- Why this fix: august-10#E17's remedy is easy to adopt halfway, as a set of marginal-rate gauges on a dashboard. Those gauges read healthy under opticon#E28's bug, because the bug lives in the ordering between the two conjuncts rather than in either one. Only the explicit multiply-and-compare step converts E17's instrumentation into a detector, and E17 states it ("instrument each conjunct's marginal rate and multiply") in a way that makes the multiply look like arithmetic rather than the essential act.
- Rule of thumb: august-10#E17's conjunct instrumentation detects opticon#E28's clear-before-read dead branch only via the predicted-versus-observed contradiction, never from the rates themselves — sandbox-confirmed both marginals reading fully healthy (0.250 and 0.400) at an outcome of 0, with the snapshot fix firing 22 times on the identical schedule; record the predicted rate and alarm on the discrepancy.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b13/l31.py) and confirmed the buggy run yields fired=0 with bluff_rate 0.250 and check_rate 0.400, and the snapshot fix yields fired=22 with identical conjunct rates. opticon#E28 and august-10#E17 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__opticon/E28, pappydapimp69__august-10/E17
- Link: session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-09-28 · projects/local__sandbox-combined-august-10-predicted-vs-observed-blind-to-misroute.md#E1 · compatible · no sandbox · brain train scheduled pass, 2026-09-28
