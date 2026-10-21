# local/sandbox-combined-dog-opticon-two-silent-losses-inside-one-coarse-assertion — lessons

Project: local/sandbox-combined-dog-opticon-two-silent-losses-inside-one-coarse-assertion. Newest first.

---

## E1 — sandbox combined dog opticon two silent losses inside one coarse assertion
- Date: 2026-08-29
- Project: local/sandbox-combined-dog-opticon-two-silent-losses-inside-one-coarse-assertion
- Tags: [testing][harness][state][gamedev]
- What: A deterministic sandbox (fixed dispatch sequence, no RNG) running a test harness that forces setup state through a shallow-copy getter and then dispatches actions past a global input interceptor, measuring what reaches the game against what a coarse assertion would accept.
- Why built: dog#E21 records that a getter exposing internal state via a shallow copy silently discards writes made through it, reading exactly like "the game ignored my forced state." opticon#E14 records that a global "any input skips this" interceptor can silently eat an existing test's first post-transition action, and that a green suite only proves the specific assertions in it survived. Both are silent losses in the same harness path, so this tests what they do to a suite together.
- Design: A game exposing `get_state()` as `dict(self._state)` and a dispatch path with an optional intro-phase interceptor. The harness forces HP to 50 through the getter, then dispatches two damage actions, run with and without the interceptor. The intended scenario is 50 HP minus two hits, ending at 30.
- Got right: Measuring the actual end state against the intended one rather than only against the coarse assertion, which is what makes the size of the gap visible instead of just its sign.
- Where/why it failed: The forced HP never lands — the shallow copy is discarded — so the run starts at 100 and ends at 80 rather than the intended 30. Adding the interceptor eats the first dispatch as well, ending at 90 with only one action applied. An assertion of the obvious shape, "HP decreased," is true at 80, at 90 and at the intended 30 alike, so both silent losses land inside the range the assertion accepts and the suite is green while the scenario under test never ran.
- Fix: Assert the exact expected value rather than a direction of change, and assert that the setup took effect before exercising anything — read the state back through the same getter and check the forced field, which converts dog#E21's silent discard into an immediate failure.
- Why this fix: The two losses are independent in mechanism but identical in signature: each removes something from the scenario without raising anything, and each moves the result further from the intended value in the same direction the coarse assertion is checking. A directional assertion therefore gets more likely to pass as more of the scenario is lost, which is the inverse of what a test should do.
- Rule of thumb: dog#E21's discarded setup write and opticon#E14's eaten first action are independent silent losses that both land inside a directional assertion's accepted range — sandbox-confirmed an intended end state of 30 arriving as 80 and 90 while "HP decreased" holds in every case; assert exact values and verify the setup took effect before exercising anything.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b4/l13.py) and confirmed the forced HP of 50 is discarded (run ends at 80 instead of 30), the interceptor eats the first dispatch (ends at 90, acted=1), and a "HP decreased" assertion is true in both runs and in the intended run. dog#E21 and opticon#E14 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__dog/E21, pappydapimp69__opticon/E14
- Link: session_014mRpopK9xnhvk35tT8ozkX

