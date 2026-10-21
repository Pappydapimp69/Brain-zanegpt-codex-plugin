# local/sandbox-combined-opticon-brain-builder-party-size-correctness-is-a-step-function — lessons

Project: local/sandbox-combined-opticon-brain-builder-party-size-correctness-is-a-step-function. Newest first.

---

## E1 — sandbox combined opticon brain builder party size correctness is a step function
- Date: 2026-08-29
- Project: local/sandbox-combined-opticon-brain-builder-party-size-correctness-is-a-step-function
- Tags: [gamedesign][testing][state][method]
- What: A deterministic sandbox (pure integer turn arithmetic, no RNG) evaluating whether a "safe until your own next turn" reprieve survives to the protected actor's next turn, as a function of party size, under a global-clock duration and under a duration stored in the rule's own actor-turn units.
- Why built: opticon#E40 records that a rule phrased in one actor's turns but stored against a global clock silently bakes in the actor count — the reprieve expired on the scan immediately before the freed prisoner's own next turn, a bug that scaled with party size and vanished at one actor, which is the configuration manual checks use. brain-builder#E5 warns that a step function is monotonic and so passes a monotonicity assertion, prescribing a smoothness check. This tests what shape opticon#E40's bug has when swept over party size.
- Design: A reprieve granted at global tick 0 with a duration of one global unit, against the protected actor's own next turn arriving after all other actors have acted. Party sizes 1 through 6, evaluated under the global-unit duration and under a duration equal to the actor count (the rule's own units).
- Got right: Expressing both the bug and its fix in the same arithmetic so the sweep measures a single variable — the units the duration is stored in — rather than comparing two differently-structured implementations.
- Where/why it failed: The global-clock reprieve holds at one actor and fails at every party size from 2 to 6. Correctness as a function of party size is therefore a step: True at N=1, False for all N>=2. That shape is monotonic, so a sweep over party size checking only for monotonic degradation accepts the cliff — exactly brain-builder#E5's warning, arriving here on a correctness axis rather than a difficulty one.
- Fix: Sweep correctness over party size and apply brain-builder#E5's smoothness assertion to that sweep, flagging any single-step collapse between adjacent sizes; and store rule durations in the units the rule is written in, decrementing on the owning actor's own event.
- Why this fix: opticon#E40's bug is invisible at N=1 and total at N>=2, which means both a single-actor manual check and a monotonicity-only sweep pass. brain-builder#E5's smoothness criterion was recorded for difficulty curves, but the property it detects — an abrupt one-step change that monotonicity cannot see — is exactly what an actor-count-dependent rule bug looks like, so E5's assertion transfers to correctness sweeps.
- Rule of thumb: opticon#E40's global-clock reprieve bug has a STEP shape over party size (correct at N=1, broken at every N>=2), so it passes both a single-actor manual check and a monotonicity-only sweep — apply brain-builder#E5's smoothness assertion to correctness sweeps, not just difficulty curves, to catch a one-step collapse between adjacent sizes.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b8/l21.py) and confirmed the global-unit reprieve holds only at N=1 and fails at N=2 through 6, while storing the duration in actor-turn units holds at every size. opticon#E40 and brain-builder#E5 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__opticon/E40, pappydapimp69__brain-builder/E5
- Link: session_014mRpopK9xnhvk35tT8ozkX

