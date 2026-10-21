# local/sandbox-combined-opticon-august-10-stall-detector-fix-ladder — lessons

Project: local/sandbox-combined-opticon-august-10-stall-detector-fix-ladder. Newest first.

---

## E1 — sandbox combined opticon august 10 stall detector fix ladder
- Date: 2026-08-29
- Project: local/sandbox-combined-opticon-august-10-stall-detector-fix-ladder
- Tags: [ai][testing][method][observability]
- What: A deterministic sandbox (three fixed 60-tick series, no RNG) running a no-progress detector under three gating rules — better-than-previous, better-than-best-ever, and best-ever-plus-a-minimum-rate — against an oscillating signal, an ambient-drift signal, and a truly stuck signal.
- Why built: opticon#E5 records that a stall detector must gate its reset on "better than best-ever" rather than "better than the immediately prior observation," because a turn-over-turn delta is blind to slow oscillation. august-10#E12 records that the threshold must further be a RATE — a minimum gain per patience window — because ambient drift of 0.01/tick mints a fresh best-ever every tick and the detector never fires. This tests whether the two are alternatives, refinements, or a ladder where each fix leaves the next gap open.
- Design: Three signals chosen to isolate each failure mode: a slow oscillation around a flat mean, a monotone ambient drift of 0.01/tick that never closes the real task gap, and a genuinely flat series. Each is run through all three gating rules with the same patience window of 10.
- Got right: Including the truly-stuck control alongside the two pathological signals, which confirms all three gates fire correctly at t=10 on an unambiguous stall and so isolates the differences to the pathological cases rather than to overall detector sensitivity.
- Where/why it failed: The gates form a strict ladder, each defeated by the case the next one fixes. On the oscillating signal the previous-observation gate never fires across 60 ticks while the best-ever gate correctly fires at t=11 — opticon#E5's finding. On the ambient-drift signal the best-ever gate itself never fires, because each tick's 0.01 gain mints a fresh best; only august-10#E12's rate gate fires, at t=10. Every failure presents identically as a detector reporting continuous progress.
- Fix: Adopt the rate-gated form directly rather than the best-ever form, since best-ever is a strict intermediate that leaves a live gap; and when auditing an existing detector, test it against both an oscillating and a slow-drifting signal, because a single pathological fixture will certify whichever gate happens to handle that one case.
- Why this fix: The two lessons read as independent corrections to the same detector but are ordered — opticon#E5's fix is necessary and insufficient, and stopping there produces a detector that passes the oscillation regression test its own fix was written for while remaining fully blind to drift. The identical symptom across all three failures means the gap cannot be found by observing the detector's output.
- Rule of thumb: opticon#E5's best-ever stall gate and august-10#E12's minimum-rate gate are a ladder, not alternatives — sandbox-confirmed the previous-observation gate never fires on oscillation (best-ever fires t=11) and the best-ever gate never fires on 0.01/tick ambient drift (rate gate fires t=10), with all three firing at t=10 on a truly flat series; go straight to the rate form.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b2/l8.py) and confirmed oscillating: prev never / best-ever t=11 / rate t=11; ambient drift: prev never / best-ever never / rate t=10; truly stuck: all three t=10. opticon#E5 and august-10#E12 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__opticon/E5, pappydapimp69__august-10/E12
- Link: session_014mRpopK9xnhvk35tT8ozkX

