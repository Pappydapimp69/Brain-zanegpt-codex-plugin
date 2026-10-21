# local/transcendental-drift-forks-only-when-it-feeds-state — lessons

Project: local/transcendental-drift-forks-only-when-it-feeds-state. Newest first.

---

## E1 — transcendental drift forks a run only when it feeds state
- Date: 2026-10-15
- Project: local/transcendental-drift-forks-only-when-it-feeds-state
- Tags: [determinism][testing][state]
- What: Re-verified and declared the seeded-rng kernel as the-game-prologue E1 uses it (canonicalize state
  before hashing, save state words, grep-guard transcendental math in the sim), with my own fixture,
  and pushed the transcendental and guard parts to where they stop holding.
- Why built: The-game-prologue E1 quoted the seeded-rng kernel in prose only, and its transcendental-math ban was
  a rule without a measured failure; the question was when differing sin() implementations actually
  fork a run, and what a grep guard misses.
- Design: Stdlib. Hashing: equal states built in different key order with -0.0 against 0.0, and a NaN state,
  under plain json and a canonical serializer. Transcendentals: libm sin against a range-reduce-by-
  float-pi Taylor sin (as two engines might ship) on 20,000 large arguments, driving a branch-only sim
  (100,000 steps, branch on sin > 0.5) and a feedback sim (logistic step plus 1e-3 sin(1000 x)).
  Guard: a banned-name regex on clean code, a planted Math.sin, and an alias Math['sin'].
- Got right: Plain json split equal states and a NaN state never equals its own round trip; the canonical
  serializer gave one hash and rejected NaN. The two sin() differed on every large argument (up to
  6.6e-10). In the feedback sim the runs differed from step 1 and were more than 0.1 apart by step 75.
  The guard caught the planted call and passed clean code.
- Where/why it failed: The branch-only sim never diverged in 100,000 steps despite the differing sin(), so the
  transcendental ban protects state that FEEDS on the result, not every use; my first prediction was
  wrong there. The grep guard missed the alias Math['sin'], so it is a tripwire, not a proof.
- Fix: Ban transcendental math where its result feeds sim state or sits near a branch threshold (or replace
  it with a table or fixed-point version), canonicalize before hashing, and back the grep guard with a
  cross-runtime golden replay that would catch an alias.
- Why this fix: The feedback case is where last-bit differences amplify into a different world within dozens of
  steps; a golden replay across two runtimes tests the outcome the grep only approximates.
- Rule of thumb: Two correct sin() implementations differ in the last bits on every large argument; that forked a
  feedback sim within 75 steps but never a branch-only sim in 100,000, so ban transcendentals where
  they feed state, and back the grep guard (it missed Math['sin']) with a cross-runtime replay.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry; the 'fast sin' stands in for a second engine's
  libm, real browsers were not compared.
- Composed: ideas:SYSTEM/determinism/seeded-rng, pappydapimp69__the-game-prologue/E1, pappydapimp69__seven/E48
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__transcendental-drift-forks-a-run-only-when-it-feeds-state.py
- Prediction: iteration 1: plain json splits key order and -0, NaN never equal; canonical one hash and rejects
  NaN; sin impls differ on > 10% of large args and the branching sim diverges; grep guard catches
  planted but misses alias. Iteration 2: a feedback sim diverges within 200 steps and the branch-only
  sim never does.
- Observed: RESULT: PASS 8/8; plain json splits equal states, canonical one hash; NaN never equals itself; sin
  impls differ on 100.0% of args, branch-only sim traces agree, feedback sim differs at step 1 and is
  > 0.1 apart by step 75; grep guard catches planted True, misses alias True
- Scenarios: 1) key order plus -0.0; 2) NaN; 3) two sin implementations; 4) branch-only sim (iteration 1
  prediction refuted); 5) feedback sim; 6) built to BREAK the guard: an aliased call (it slipped
  through)
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto loop 3 pass 1 (kernel declare SYSTEM/seeded-rng), 2026-10-15
- Audited: 2026-10-15 · modeled · I read the entry and its stored sandbox (sandboxes/2026-10-15__transcendental-drift-forks-a-run-only-when-it-feeds-state.py), reran it (RESULT: PASS 8/8, same numbers as stored), and ran a few side probes in my scratchpad without shipping them. Bridge recheck on pappydapimp69__seven/E48. The contradiction on E48 is the incompatible Cited-by from seven E89. It refutes only E89's composition: anything that indexes a draw is save state. E48 itself was reverified as a pass. E1's sandbox never uses PRNG state words. Its rng field is inert dict data, and the part E48 shares with it (hashing with sorted or canonical keys) is recomputed independently in E1's own fixture. So E1's claim does not rest on E48, and it survives with that citation removed. Does the model test the claim? The hashing, NaN and grep-guard parts genuinely test what they state, including a negative control that the alias slips through. The transcendental part only models the real situation. The stand-in fast_sin is a 13th-order Taylor series with an error of up to 6.6e-10. In units in the last place (ulps), that is a median of 54,751 ulps and a maximum of 3.2e8 ulps against libm. Two real libms differ by about one ulp, so "differ in the last bits" overstates what was tested. When I perturbed sin by exactly one ulp, the feedback sim still forked, but the states were more than 0.1 apart only at step 1039, not step 75. The direction holds and the speed does not. The branch-only result is confounded. In the stored sim not one of 100,000 steps fell within 7e-10 of the 0.5 threshold. Even when I made the branch feed state (x += 0.001 when sin > 0.5), the libm and stand-in runs ended identical. So "never a branch-only sim in 100,000" reflects how close the arguments came to the threshold, not whether the result feeds state. The entry's Fix line already names nearness to a threshold, but its Rule of thumb credits feeding. No real browsers or engines were compared, as the entry itself says. Verdict: modeled. · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 1 pass 3
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-auto-training.md#E8 · compatible · sandboxes/2026-10-15__exact-threshold-angles-let-a-cosmetic-sin-branch-fork-a-shared-rng-stream-across-runtimes.py · observed RESULT: PASS designer-angle cosmetic branch forked gameplay 8/8 via shared stream (split 0/8, generic angles 0/8); state-word reload exact True, cross-runtime fork seen by state-word fingerprint at tick 1013 vs hp-only at 1013. Per-seed hp… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 5 pass 2
