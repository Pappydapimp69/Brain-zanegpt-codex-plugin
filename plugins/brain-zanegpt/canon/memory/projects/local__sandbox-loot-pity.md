# local/sandbox-loot-pity — lessons

Project: local/sandbox-loot-pity. Newest first.

---

## E2 — sandbox13 silent zero weight fallback picks wrong item
- Date: 2026-07-11
- Project: local/sandbox-loot-pity
- Tags: [algorithm][state]
- What: A cumulative-weight `weightedPick(items)` function subtracts each
  item's weight from a random roll until it goes negative, and falls back
  to `return items[items.length - 1]` after the loop as insurance against
  float rounding slop leaving a tiny positive remainder. Once every item's
  effective weight legitimately collapses to `0` (via the decay bug in the
  companion entry), that fallback stops being a rare rounding correction
  and fires on effectively EVERY call — deterministically returning
  whichever item happens to be last in the array, regardless of its actual
  weight, 96,856 times out of 100,000 in the confirmed run.
- Why built: Floating-point weight sums can leave the roll loop with a
  residual value that never goes negative due to rounding — a fallback
  return prevents `undefined`/a crash in that edge case, which is a
  reasonable, common defensive pattern for cumulative-weight sampling.
- Design: Instrumented `weightedPick` to count how often the fallback path
  fired vs. the normal loop-exit path, across 100k pulls, once total pool
  weight had degenerated toward zero (from the paired decay bug).
- Got right: The intent behind the fallback — never let float rounding
  crash or return `undefined` — is correct and worth keeping. The flaw is
  narrowly that the SAME fallback silently absorbs a completely different,
  much more common failure mode (total weight is genuinely zero, not just
  rounding-imprecise) and produces a plausible-looking, non-crashing result
  either way, so nothing about the function's output distinguishes "one in
  a million rounding slop" from "the entire pool has zero weight."
- Where/why it failed: A single fallback branch was asked to silently
  paper over two semantically opposite situations — negligible float error
  (safe to approximate) and a genuinely broken/empty weight distribution
  (not safe to approximate, since it means "no item should have been
  pickable at all"). Because both produce the same code path and the same
  kind of return value (a normal item, no exception), there was no signal
  anywhere that would prompt someone to notice the second case was even
  happening — the function never crashes, never logs, never returns
  something obviously wrong-shaped.
- Fix: Check `total <= 0` explicitly before entering the roll loop and
  throw a clear error (`weightedPick: total weight is 0 over N candidates`)
  instead of falling through to the last-item fallback. Reserve the
  last-item fallback ONLY for the genuine post-loop float-rounding case
  (total was positive but the loop's subtraction didn't quite reach it).
- Why this fix: Separates the two situations at the one point they're
  actually distinguishable — before vs. after confirming the pool has any
  real weight at all — so a genuinely empty/zero pool fails loudly right
  where it happens, instead of returning a silently-biased-but-valid-looking
  pick that can only be caught later by noticing a suspicious distribution
  over many trials.
- Rule of thumb: A "fallback for safety" branch that returns a plausible
  default value on ANY unexpected input (not just the specific edge case it
  was written for) will silently absorb bugs that have nothing to do with
  the case it was designed for — and because the return value still looks
  normal, nothing downstream signals that anything went wrong. Scope a
  defensive fallback to the EXACT condition it's meant to catch (e.g. "loop
  exited without going negative, but total was confirmed positive"), and
  make every OTHER unexpected condition (zero/negative total, empty
  candidate list) fail loudly instead of sharing the same catch-all path.
- Provenance (verified/assumed): Verified first-hand — instrumented run
  showing the fallback firing 96,856/100,000 times once decay drove total
  weight toward zero, deterministically favoring the last array item
  (`mythic_crown` at 97,249/100,000 picks in the specific run that surfaced
  it); confirmed the explicit `total <= 0` throw catches the same condition
  immediately instead of silently mis-picking.
- Link: session (dog-game-continue-oc3xqh); sandbox-13-loot/lib.js
  (`weightedPick`), pass2d_diagnose.js.

## E1 — sandbox13 decay based dup protection defeats itself
- Date: 2026-07-11
- Project: local/sandbox-loot-pity
- Tags: [algorithm][state][gamedesign]
- What: A weighted loot table's duplicate-protection was implemented as a
  per-item multiplicative decay applied on every acquisition
  (`item.mult *= DUP_FACTOR`). Two variants were tested and BOTH silently
  defeat their own purpose at scale, in opposite directions: with a floor
  (`Math.max(FLOOR_MULT, item.mult * DUP_FACTOR)`), every item eventually
  converges to the same floor value and the table's odds revert to the
  original UNPROTECTED base-weight ratios; with no floor, a decaying double
  eventually underflows to exact `0.0`, and once every item hits zero the
  table degenerates into uniform random selection regardless of the
  original weights.
- Why built: Rarity tiers need duplicates of already-owned items to become
  progressively less likely — decaying an item's effective weight each time
  it's drawn is the obvious direct implementation of "this got picked, make
  it rarer next time."
- Design: Ran the floored variant for 100k pulls and compared early-window
  vs late-window pick rates for a rare item; ran the unfloored variant for
  100k pulls and tracked the legendary-tier pick rate over time.
- Got right: The mechanic works exactly as intended over the SHORT term —
  early pulls do show the intended suppression of recently-drawn items. The
  bug is purely a long-run/asymptotic property that a short manual test
  would never reveal.
- Where/why it failed: A relative floor caps how far any single item's
  weight can fall, but says nothing about where OTHER items' weights are —
  once every item has independently decayed down to the same floor
  (inevitable given enough draws, since decay is monotonic), the table is
  effectively uniform-at-the-floor, and dividing by the (also uniform) sum
  reproduces the original relative ratios. Removing the floor doesn't fix
  this — it just changes the failure mode: an unbounded exponential decay
  underflows to a real `0.0` (not just a very small number) after enough
  multiplications of a float less than 1, and once ALL items are exactly
  zero, a `total > 0` guard falls through and the pick becomes uniform
  (confirmed: legendary-tier rate converged to 2/9 ≈ 22.2%, exactly
  1/(item count), on a 9-item pool with only one true legendary).
- Fix: Replace multiplicative decay entirely with a hard exclusion —
  `effectiveWeight = timesOwned >= MAX_COPIES ? 0 : baseWeight *
  Math.pow(DUP_FACTOR, timesOwned)`, where an item is fully removed from
  the eligible pool (not asymptotically suppressed) once a cap is reached.
  No floor, no underflow, no reconvergence — the ratios among still-eligible
  items stay meaningfully different from each other indefinitely.
- Why this fix: A floor and an unfloored decay are both trying to express
  "this item should eventually stop being a live differentiator" through a
  CONTINUOUS weight value, which forces a choice between two failure modes
  (converge-to-uniform-at-floor or converge-to-uniform-at-zero). A discrete
  cap expresses the same intent as a boolean (still eligible / no longer
  eligible) instead, which has no asymptote to decay into.
- Rule of thumb: Any multiplicative decay applied uniformly across a
  weighted pool, run for enough iterations, converges — either back to the
  original relative ratios (if floored, since every item eventually hits
  the same floor) or to a fully uniform distribution (if unfloored, since
  every item eventually underflows to zero). If "this option should
  eventually stop being differently likely than others" is the actual
  design goal, a hard exclusion/cap is safe; if it's not the goal, decay
  alone cannot deliver lasting differentiation no matter how it's tuned —
  verify any decay-based fairness/rarity mechanic with a LONG-RUN
  simulation (tens of thousands of iterations, not a handful), since the
  short-term behavior looks correct right up until the point it inverts.
- Provenance (verified/assumed): Verified first-hand — 100k-pull
  simulations of both the floored variant (early-window pick rate 1.46% vs
  late-window 0.985%, converging toward the unprotected 1.00% baseline) and
  the unfloored variant (legendary-tier rate measured at 22335/100000,
  matching the uniform-selection prediction of 1/9 items almost exactly);
  confirmed the hard-cap fix eliminates both reconvergence patterns.
- Link: session (dog-game-continue-oc3xqh); sandbox-13-loot/pass2.js,
  pass2b_investigate.js, pass3.js (`effectiveWeight`).
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-rpg-progression.md#E6 · compatible · no sandbox · session (query brain for "stress test mega group in a sandbox environment"), sandbox script stress.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-the-waiting-city.md#E17 · compatible · no sandbox · session (brain train 3 groups + 2 edges, sandboxed until satisfied, loop 3), sandbox script sim.mjs, no code change to a shipping project
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E27 · compatible · sandboxes/2026-10-11__fading-rescue-call-decay-needs-a-floor-and-constant-draws.py · observed RESULT: PASS 5/5 predictions held; unfloored silent at night 6; floored night-6 hear 0.438; naive draws [0, 3, 0] vs constant [3, 3, 3] · session; Seven docs/IDEAS.md "Disappearance and return"; brain train pass on disappearance; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E59 · compatible · sandboxes/2026-10-11__punishing-sanity-meter-makes-a-death-spiral.py · observed RESULT: FAIL 2/3; collapse perception 0.126 punish 0.499 (x3.97); mild 0.229 · session; brain train loop on hallucination as an art style (loop 4); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Audited: 2026-10-13 · modeled · The entry has no stored sandbox, so I could only judge the described design and run a small check of my own. The described runs (100k pulls, floored vs unfloored, early vs late windows) do compute their outcome rather than assume it, and the mechanism is sound: uniform multiplicative decay applied to what gets drawn equalizes the multipliers. My own expected-value iteration (9 items, base weights 50/20/10/8/5/3/2/1/1, decay factor 0.5 per unit of pick probability, no RNG) reached uniform 1/9 per item by about step 100, long before any underflow to exactly 0.0, which supports the convergence claim and suggests the effect arrives earlier than the entry's exact-zero explanation implies. Two weaknesses: the entry says there was only one true legendary yet reports a converged rate of 2/9, which is internally inconsistent with a uniform rate of 1/9 unless two items counted as legendary; and the hand-written loot-table model stands in for a real game's table code, so the numbers cannot be rerun. Rule clauses (floored reverts to base ratios, unfloored goes uniform) are covered by the description but the stored evidence is thin; hence modeled rather than pass. · scheduled brain train loop 2 pass 3 audit; session_01HQJRG1w1a4FhntMjAUPLns
