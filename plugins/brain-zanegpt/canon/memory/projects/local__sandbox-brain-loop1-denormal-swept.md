# local/sandbox-brain-loop1-denormal-swept — lessons

Project: local/sandbox-brain-loop1-denormal-swept. Newest first.

---

## E2 — subnormal fixed point independently reproduced across three decay scenarios
- Date: 2026-07-18
- Project: local/sandbox-brain-loop1-denormal-swept
- Tags: [physics][testing][determinism]
- Composed: local__sandbox-brain-loop1-denormal-swept/E1, local__sandbox-collision/E1
- What: `brain train` flagged `sandbox-brain-loop1-denormal-swept + sandbox-collision` as a single-source edge (the whole composed claim — decaying velocity gets stuck at a nonzero float32 subnormal, and that stuck value overflows a swept-collision time-of-impact formula to `+Infinity` — rests on E1 alone). Independently re-verified the full claim with three fresh scenarios (different decay law, boundary, sign, and starting velocity each; none reused from E1): `v0=12, decay=0.83`; `v0=3, decay=0.97`; `v0=-8.5, decay=0.9`. All three confirm the same mechanism E1 found, from parameters E1 never used.
- Why built: E1's own composed edge to sandbox-collision was itself flagged by `brain train edge` as single-sourced — the exact case the tool's priority order says to re-verify before extending coverage elsewhere. A second, independently-parameterized sandbox is what actually raises the edge from single- to multi-source, not re-reading the same run.
- Design: Deterministic Node script (`sandbox_denormal_swept.mjs`), no RNG, no wall-clock. For each scenario: repeatedly `v = Math.fround(v * decay)`, tracking (a) the step an `Math.abs(v) < 1e-5` epsilon check first trips, (b) the step `v` becomes a FIXED POINT under further decay (`Math.fround(v*decay) === v`, nonzero), (c) whether a naive `t = Math.fround((boundary - x) / v)` first goes non-finite, and (d) whether an explicit `Number.isFinite(t) && Math.abs(t) <= 1e7` guard stays false for every remaining step once `v` is stuck (i.e., the fix holds forever, not just at the moment of failure).
- Got right: E1's core mechanism reproduces exactly, with three parameter sets E1 didn't test: velocity pins at a nonzero float32 subnormal fixed point in all three (`2.80e-45`, `2.24e-44`, `-5.61e-45`) rather than ever reaching exact `0` — confirming this is a general IEEE-754-rounding property of repeated sub-unity multiplication, not an artifact of E1's specific `v *= 0.9` decay rate or its `v = 5` start.
- Where/why it failed: In every scenario, the epsilon-threshold rest check trips well before the stuck point (76 vs. 563 steps, 415 vs. 3332, 130 vs. 986 — roughly 7-8x earlier each time; E1's own single-scenario ratio was ~140x, so the gap size clearly depends on the decay/epsilon choice, but the DIRECTION — epsilon always trips first — held in all three independent parameterizations). And in every scenario, once `v` reaches its stuck value, the naive `t=(boundary-x)/v` immediately and permanently overflows to `Infinity`, which a check that only tests for `NaN` (not `Infinite`) would miss, and which a naive "is t > 0" collision-scheduler would treat as a real (if absurd) future hit.
- Fix: Same fix as E1, now confirmed to generalize — an explicit `Number.isFinite(t) && Math.abs(t) <= MAX_SANE_TOI` guard on any computed time-of-impact, independent of whatever epsilon threshold gates the velocity itself. Verified in this run: once a scenario's `v` gets stuck, the guard correctly rejects the overflowed `t` on every single subsequent step through the end of a 5000-step run (never once passes a bad value through), for all three scenarios.
- Why this fix: A defensive range/finite check on the CONSUMER of a decaying value (the TOI formula) doesn't depend on getting the PRODUCER's epsilon threshold right — this run's three different, untuned epsilon-vs-stuck-point gaps (7-8x rather than E1's 140x) show that gap size isn't something a caller should rely on being "big enough"; the finite/range guard is what actually holds regardless.
- Rule of thumb: (unchanged from E1, now on firmer footing) any formula dividing by a value that can legitimately decay toward zero needs an explicit finite/range check on its result — IEEE-754 division by a subnormal overflows silently to `Infinity`, not `NaN`, and passes through a `NaN`-only guard. Added: don't assume the gap between "epsilon trips" and "value reaches its stuck point" is dramatic (E1 saw ~140x; three fresh parameterizations here saw only ~7-8x) — the guard on the consumer side is what actually matters, not the size of that gap.
- Provenance (verified/assumed): Verified first-hand — `sandbox_denormal_swept.mjs` run to completion for all three scenarios, deterministic (no RNG, no wall-clock; `Math.fround` for float32 semantics), each scenario's stuck value, epsilon-trip step, overflow step, and per-step guard result printed and checked programmatically (`allPass` gate on all four conditions per scenario; exits 1 if any scenario fails to reproduce — script would have reported "CLAIM DID NOT REPRODUCE — do not file" and nothing would have been filed). Scope: this run covers only the physics/TOI angle, same as E1's own physics half — E1's separate audio-context angle was outside this run's scope and is unaffected either way.
- Link: session (this conversation, "brain train zen groups" → clarified to bare `brain train`); scratchpad `sandbox_denormal_swept.mjs`.

## E1 — loop1 subnormal fixed point is domain independent and breaks swept toi
- Date: 2026-07-13
- Project: local/sandbox-brain-loop1-denormal-swept
- Tags: [physics][dsp][testing]
- Composed: local__sandbox-combined-audio-realtime/E2, local__sandbox-collision/E1
- What: The "a decaying signal never reaches exact zero, it gets stuck at a
  nonzero subnormal fixed point" finding was previously only verified in an
  audio feedback-decay context. Re-verified it with a physics restitution
  velocity instead (`v *= 0.9` per bounce, no audio anywhere) and confirmed
  the identical mechanism, then fed the decaying velocity into a
  swept-collision time-of-impact formula (`t = (boundary - x) / v`) and
  found a new failure: once `v` is subnormal, `t` overflows to `+Infinity`
  rather than a small-but-valid number.
- Why built: `denormals-silently-tank-cpu` and `swept-collision-for-fast-movers`
  were both single-source kernels (each verified from exactly one prior
  angle). Re-verifying the denormal finding from a genuinely different
  domain (physics, not audio) tests whether it's a general floating-point
  property or an audio-specific artifact, and pairing it with
  swept-collision (which consumes velocity directly in a division) was the
  most natural genuinely-different partner to test it against.
- Design: Two deterministic Node scripts, no RNG, no wall-clock. (1) Iterate
  `v = v * 0.9` starting from `v = 5` for 20,000 iterations with three rest-
  check variants (none, `Math.abs(v) < 1e-6`, `v === 0`), and separately
  count iterations to cross an epsilon=1e-6 threshold vs. the subnormal
  boundary (`Number.MIN_VALUE * 2`). (2) Directly evaluate
  `t = (boundary - x) / v` for a range of `v` values including a manufactured
  subnormal (`Number.MIN_VALUE * 5`) and exact `0`, checking `Number.isFinite(t)`
  and whether `t` falls in `[0,1]`.
- Got right: The swept-collision kernel's own time-of-impact formula is
  otherwise exactly correct for any normal-range velocity (verified: t was
  finite and in-range for v=5 and v=0.001) — the failure is specific to the
  subnormal/zero tail of the input domain, not a general defect in the
  formula.
- Where/why it failed: (1) The subnormal-fixed-point mechanism is a pure
  IEEE-754 property of repeated multiplication by a constant < 1 — it has
  nothing to do with audio; the physics velocity hit the identical stuck-
  nonzero state (verified: `v * 0.9 === v` held at the end of the run,
  finalV ≈ 2.5e-323), and an exact-zero rest check never triggered across
  all 20,000 iterations, exactly mirroring the audio kernel's warning. (2)
  Swept-collision's `t = distance/v` formula silently breaks down at the
  extreme low end of v's range: dividing a normal-magnitude numerator by a
  subnormal (or zero) denominator overflows to `+Infinity` in double
  precision, which a naive swept-collision implementation with no
  finite/range check on `t` would treat as a real (if bizarre) result rather
  than rejecting it.
- Fix: Two independent, narrow fixes rather than one shared one. For the
  decay side: use a magnitude-threshold rest/sleep check
  (`Math.abs(v) < epsilon`), never exact-zero equality — verified this trips
  at iteration 147, roughly 140x earlier than the ~20,000+ iterations needed
  to approach the subnormal range, which is why real physics engines with a
  sane epsilon rarely hit this in practice. For the swept-collision side:
  validate any computed `t` is `Number.isFinite(t) && t >= 0 && t <= 1`
  before trusting it, as defense-in-depth independent of whether the
  upstream velocity is properly floored — this is a one-line guard that
  makes the formula robust to a subnormal, zero, or otherwise degenerate
  input regardless of why it got there.
- Why this fix: The two fixes target different layers on purpose — the
  epsilon-threshold rest check prevents velocity from ever reaching the
  danger zone in normal operation, while the finite/range check on `t`
  contains the failure defensively if it ever does anyway (a stale object,
  a modified restitution curve, an object exempted from sleep). Relying on
  only one of the two leaves a gap: epsilon-only fails if some other code
  path bypasses the sleep system; range-check-only still lets an
  un-slept object burn CPU on subnormal arithmetic every tick even though
  it's now "handled safely."
- Rule of thumb: A finding verified in only one domain (here: "decaying
  signals get stuck at a nonzero subnormal, never reach exact zero") is
  worth re-testing in a structurally different domain before trusting it as
  general — it held identically for a physics restitution velocity with zero
  audio code involved, confirming it's a floating-point property, not an
  audio artifact. Separately: any formula that divides by a value which can
  legitimately decay toward zero (a velocity, a rate, a remaining-lifetime)
  needs an explicit finite/range check on its result, because IEEE-754
  division by a subnormal doesn't fail loudly (no NaN, no exception) — it
  silently overflows to `Infinity`, which passes right through code that
  only checks for `NaN`.
- Provenance (verified/assumed): Verified first-hand — both scripts run to
  completion with recorded numeric output (finalV ≈ 2.5e-323 with `v*0.9
  === v` confirmed true; epsilon-threshold sleep at iteration 147 vs. no
  convergence to the subnormal boundary within 100,000 iterations once
  already inside the fixed point; `t=Infinity, finite=false` for both a
  manufactured subnormal v and v=0, vs. finite in-range t for v=5 and
  v=0.001).
- Link: session (dog-game-continue-oc3xqh); scratchpad
  loop1-denormal-swept-bounce.mjs.
- Cited-by: 2026-07-18 · projects/local__sandbox-brain-loop1-denormal-swept.md#E2 · compatible · no sandbox · session (this conversation, "brain train zen groups" → clarified to bare `brain train`); scratchpad `sandbox_denormal_swept.mjs`.
- Cited-by: 2026-07-20 · projects/local__sandbox-phantom-voice-eats-budget.md#E1 · compatible · no sandbox · session (this conversation, "continue training" — re-verifying the denormal-swept + audio-realtime single-source edge from an unexplored angle); scratchpad `sandbox_phantom_voice_eats_budget.mjs`.
