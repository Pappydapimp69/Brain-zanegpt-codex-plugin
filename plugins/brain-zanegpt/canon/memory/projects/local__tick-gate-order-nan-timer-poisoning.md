# local/tick-gate-order-nan-timer-poisoning — lessons

Project: local/tick-gate-order-nan-timer-poisoning. Newest first.

---

## E1 — tick gate order nan timer poisoning
- Date: 2026-09-30
- Project: local/tick-gate-order-nan-timer-poisoning
- Tags: [gamedev][state][determinism][testing]
- What: Composition of the tick-ordering rule (gate flag must update before the input read) with the NaN-poisoning rule (one NaN silently breaks downstream shared state), on a 1-frame cancel window.
- Why built: The untested seam between the combat-window entry and the NaN entry: a NaN phase timer would make the gate comparison false forever, mimicking a one-frame-late gate but permanently.
- Design: Deterministic 12-frame tick loop with a window [4,5) on a phase timer; orders before/after, frame-perfect and late input, NaN injected at frame 0, with and without an isFinite resync guard.
- Got right: Gate-before-read accepted the frame-perfect input (1); gate-after-read dropped it (0) and accepted only a frame-late input (1).
- Where/why it failed: A NaN timer made every window comparison false: 0 of 12 input frames accepted, with no exception, so it looks like dropped cancels rather than a crash.
- Fix: Update the gate before the read within the tick, and isFinite-guard the timer at the boundary so a NaN is resynced (guarded run accepted 1).
- Why this fix: Ordering fixes the by-construction lateness, while the guard restores the comparison that NaN silently disables; the two failures share the symptom but not the cause.
- Rule of thumb: A missed cancel has two silent causes, gate ordering and a NaN timer; test frame-perfect input for the first and assert isFinite on phase timers for the second.
- Provenance (verified/assumed): Verified first-hand by running the shipped sandbox on a synthetic loop; not tested inside a real game engine.
- Composed: sandbox-dbz-combat/E1, dog/E3
- Polarity: compatible
- Sandbox: sandboxes/2026-09-30__tick-gate-order-nan-timer-poisoning.py
- Prediction: Before-order accepts 1, after-order 0 (1 if input is late), NaN timer accepts 0 across all 12 input frames, guarded timer accepts at least 1.
- Observed: RESULT: PASS before=1 after=0 after_late=1 nan=0 guarded=1
- Scenarios: 1) gate before read; 2) gate after read built to break; 3) late input under after-order; 4) NaN timer; 5) NaN with guard
- Link: scheduled train pass 4
- Audited: 2026-10-13 · pass · Read the entry and its stored sandbox. The result is computed, not built in: a 12-frame loop moves a timer, a gate flag is recomputed either before or after the input read, and acceptances are counted (1 / 0 / 1 for before / after / late input; 0 of 12 under NaN). The claim that a missed cancel has gate-order and NaN causes is covered by the model. Caveats: the NaN is injected at frame 0 and the guard runs after injection in the same frame, so the guard case only shows resync at the moment of injection (it accepts 1, the same as the clean run) and does not show a NaN arriving mid-window or a guard that resyncs to the wrong value; the order and NaN scenarios are never crossed; a guard that sets the timer to the current frame hides drift. The model is a synthetic loop, not an engine, which the entry states itself. Rule of thumb (test frame-perfect input, assert isFinite on phase timers) is within what was tested. · scheduled brain train auto loop 1 pass 3, 2026-10-13; session_011eTW7aDHC86vQjq7f9sRQG
