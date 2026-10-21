# local/stream-gate-lock-reset-and-scrollback-carry-state-machine — lessons

Project: local/stream-gate-lock-reset-and-scrollback-carry-state-machine. Newest first.

---

## E1 — stream gate lock reset and scrollback carry state machine
- Date: 2026-10-17
- Project: local/stream-gate-lock-reset-and-scrollback-carry-state-machine
- Tags: [ux][interaction][testing][sandbox]
- What: A deterministic state machine for a two-slide simulated terminal demo that streams literal output line by line, gates explanation chunks behind a click, holds a one-action lock, and shares one scrollback, used to check the rules the stream-then-gate kernel states.
- Why built: The kernel was a shipped interaction never exercised outside the browser; its lock-reset sentence and its gate-only-explanations sentence are exact claims a small model can check.
- Design: Two slides of 9 chunks each (3 explanation chunks per slide); stream cost 40 ms per line, 15 ms per blank, 0 under reduced motion; the lock is held while streaming or while a gate is pending; slide change optionally resets it; leaving at each of 6 gate positions tests stranding; a mid-stream exit with and without cancelled timers is the break case.
- Got right: Gating only explanations took 6 clicks against 18 if every chunk were gated (the 18 is arithmetic, not simulated); stream time was 190 ms on slide 0 and 0 under reduced motion; the shared scrollback held all 18 lines across both slides; with the lock reset a slide change stranded 0 of 6 gate positions.
- Where/why it failed: Without the reset on slide change, all 6 of 6 gate positions stranded the next slide (run refused), and with timers left uncancelled a mid-stream exit leaked 2 ghost lines onto the old slide; a pure sketch of the kernel would have missed both.
- Fix: On every slide or route change, release the lock, drop any pending gate and cancel stream timers in the same handler; keep the scrollback list outside the per-slide state.
- Why this fix: The lock and the gate belong to an action in flight, and navigation abandons that action, so ownership must end with it; the scrollback belongs to the session so it survives.
- Rule of thumb: In a two-slide stream-and-gate demo, leaving at a pending gate stranded 6 of 6 times without a lock reset on slide change and 0 of 6 with it, and uncancelled timers leaked 2 ghost lines, so reset the lock, the gate and the timers together on navigation.
- Provenance (verified/assumed): Verified first-hand by running the state machine; it models the logic only, not a browser, so real event timing and touch handling were not tested, and the 40 ms and 15 ms delays are assumed.
- Composed: ideas:UX/interaction-pattern/stream-output-then-gate-the-explanation-behind-a-click, ideas:UX/interaction-pattern/carry-demo-state-and-scrollback-across-separate-steps, ideas:UX/accessibility/scroll-effects-break-keyboard-and-vestibular-safety
- Picked-by: current-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-17__stream-gate-lock-reset-and-scrollback-carry-state-machine.py
- Prediction: Gating only explanations needs 6 clicks versus 18; reduced motion gives 0 ms; without a lock reset all 6 gate positions strand and with one 0; scrollback keeps all lines. Assumes navigation cancels pending timers; the uncancelled-timer exit was built to break it and leaked ghost lines.
- Observed: RESULT: PASS clicks 6 vs 18; stream ms 190 vs reduced 0; strands with reset 0/6 without 6/6; uncancelled timers leak 2 ghost lines
- Scenarios: 1) gate explanations only versus every chunk; 2) normal versus reduced-motion stream time; 3) leave at each of 6 gate positions with and without lock reset; 4) shared scrollback across two slides; 5) BREAK: leave mid-stream with timers cancelled and not
- Link: brain train auto loop 2 pass 5, scheduled run 2026-10-17; session_01696mc4JbaRUYgcwwnaPSG1

