# local/two-save-bugs-mask-each-other — lessons

Project: local/two-save-bugs-mask-each-other. Newest first.

---

## E1 — two save bugs mask each other so fixing one doubles divergence
- Date: 2026-10-15
- Project: local/two-save-bugs-mask-each-other
- Tags: [state][testing][determinism]
- What: Composed the seeded-rng restore lesson (save the cached spare gaussian that lives outside the state
  word) with the seam-replan-save lesson (two subsystems saving in separate steps corrupt silently),
  testing a save with a missing spare, a torn rng/sim pair, both, and a tick cross-check at load.
- Why built: Each lesson names one save defect and its fix. A real save can have both at once, and the question
  was whether they add up, and whether a load-time check catches either.
- Design: Deterministic. Mulberry32 with a Box-Muller gaussian that caches its spare; a 1,000-tick walker
  drawing one gaussian per tick; save at every tick 100 to 899, resume, compare the next 50 positions.
  Modes: atomic with spare; atomic without spare; rng saved one tick before the sim (torn) with spare;
  torn without spare. Both halves record the tick for a cross-check.
- Got right: The atomic, complete save never diverged; dropping the spare diverged at 400 of 800 save points
  (whenever a spare was pending); the torn save diverged at all 800; the tick cross-check flagged
  every torn save and no spare-only fault, so it catches one axis and is blind to the other.
- Where/why it failed: I predicted torn plus missing spare would diverge at all 800; it diverged at only 400. When the tick
  between the two saves only consumed the cached spare, the state words did not move, and dropping the
  spare made the resumed generator produce exactly the pair the run would draw next: the two bugs
  cancel half the time. Fixing only the spare raised divergence from 400 to 800.
- Fix: Save all draw-gating state in one atomic snapshot and test each fix with the other defect present
  and absent; never judge a save fix by whether divergence went down, since removing one of two
  masking bugs can make it go up.
- Why this fix: Two defects on different axes can cancel, so a fix that is correct on its own can look like a
  regression, and a team that measures divergence would revert it.
- Rule of thumb: Two save bugs can mask each other: a torn rng/sim save plus a dropped spare gaussian diverged at 400
  of 800 save points, but fixing only the spare raised it to 800; snapshot all draw-gating state
  atomically, and a tick cross-check catches tearing but not missing state.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry with my own generator and walker.
- Composed: local__2026-10-13__seeded-rng-state-restore-vs-count-replay-and-hidden-state-fingerprint-order/E1, local__sandbox-seam-replan-save/E1
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__two-save-bugs-mask-each-other-so-fixing-one-doubles-divergence.py
- Prediction: atomic 0; no spare about half; torn all 800; torn and no spare all 800; cross-check flags 100
  percent of torn saves and 0 of spare-only.
- Observed: RESULT: FAIL 4/5; diverged A 0, B 400, C 800, D 400 of 800; tick cross-check flags B 0, C 800, D 800
- Scenarios: 1) atomic with spare; 2) atomic without spare; 3) torn with spare; 4) built to BREAK the 'defects
  add up' reading: torn and no spare (they cancelled half the time); 5) tick cross-check on each
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 2 pass 2 (edge), 2026-10-15

