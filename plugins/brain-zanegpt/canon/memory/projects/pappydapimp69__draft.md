# pappydapimp69/draft — lessons

Project: pappydapimp69/draft. Newest first.

---

## E15 — reject and nudge scale dependent like recursion e6
- Date: 2026-07-13
- Project: pappydapimp69/draft
- Tags: [algorithm][gamedesign][procgen]
- What: `brain train seams` (draft + the-game-the-recursion, shared=11 tags). Composed: projects/pappydapimp69__the-game-the-recursion.md#E6 (Delaunay+MST vs. simpler all-pairs+MST is SCALE-DEPENDENT — equivalent at small room counts, roughly a dozen or fewer; prefer the simpler deterministic one there, but the comparison isn't stated as holding at larger scale) and projects/pappydapimp69__draft.md#E11 (dog#E19-style reject-and-nudge scatter — reject a candidate if distance < sum of both real radii — sandbox-confirmed as an alternative to structural segregation, verified at draft's real scale of ~28 nodes). Sandbox-confirmed draft#E11's own algorithm choice carries the same scale-dependent character recursion#E6 already names for a different algorithm pair: reject-and-nudge is cheap at draft's tested scale (2 rejections placing 28 nodes) but its cost rises steeply with density and it starts outright FAILING to place nodes well before an absurd scale (147/200 placed, 53 failures, at a fixed area only ~7x draft's tested one).
- Why built: draft#E11 verified reject-and-nudge as "the better choice" at the one scale it was actually tested (draft's real ~28-node layout) without stating whether that preference holds generally — recursion#E6, filed independently, already establishes the exact right FRAME for this kind of comparison (explicitly scale-bounded, not a blanket preference) but was never applied back to draft#E11's own choice.
- Design: `sandbox.py` — zero RNG, zero wall-clock. Deterministic candidate generation via a fixed golden-angle spiral (no randomness, same technique in spirit as a Fibonacci/sunflower point distribution) oversupplying 6x the target node count. `reject_and_nudge(n, area_side)` places nodes greedily from the deterministic candidate sequence, rejecting any candidate closer than `2*radius` to an already-placed node, up to a bounded per-node attempt budget before counting a placement failure. Ran at n=10,28,60,120,200 while holding the placement area FIXED (not scaled with n, so density genuinely increases) — a first version that scaled area proportionally with n was caught and corrected before filing: it held density constant and produced zero rejections at every scale, an invalid test of the scale-dependency claim.
- Got right: At n=28 (draft's actual real-world scale), the algorithm performed almost exactly as draft#E11 recorded — only 2 rejections, 0 failures, all 28 nodes placed — confirming draft#E11's own verification was accurate for the scale it was tested at.
- Where/why it failed: rejections-per-node rose from 0.00 (n=10) → 0.07 (n=28) → 1.78 (n=60) → 3.11 (n=120) → 5.26 (n=200), and at n=200 the algorithm failed to place 53 of 200 nodes outright within its attempt budget — a real, measurable degradation curve, not a cliff-edge coincidence, that draft#E11's single-scale verification gave no visibility into.
- Fix: Not a code fix — a verification-scope gap, same shape as this session's earlier composed finding (dog#E16 vs the-game-the-waiting-city#E16: a single-scale stress test giving a false sense of general validity). Treat draft#E11's "prefer reject-and-nudge over structural segregation" as scale-bounded, matching recursion#E6's own explicit framing — verify at the ACTUAL target scale before reusing the recommendation elsewhere, and re-test if node count or placement density grows meaningfully past what was originally checked.
- Why this fix: The corrected sandbox is the valuable part here — the first (flawed) attempt would have produced a false negative for this whole composition (zero rejections at every scale, wrongly suggesting no scale-dependency exists), caught only by checking the test's own construction, not just its output.
- Rule of thumb: A reject-and-nudge / rejection-sampling style placement algorithm's cost is a function of DENSITY (node count relative to available area), not node count alone — a verification at one scale (draft#E11's ~28 nodes) says nothing about behavior at higher density, and the degradation is gradual (rising rejection cost) well before it becomes outright placement failure. Any "prefer the simpler/rejection-based algorithm" recommendation (recursion#E6's own frame) needs its stated scale bound re-checked whenever reused at a meaningfully different node count or area.
- Provenance (verified/assumed): Verified first-hand — built `sandbox.py` (zero RNG, zero wall-clock, deterministic golden-angle candidate spiral, fixed placement area across all tested n), confirmed near-zero rejection cost at draft's real scale (n=28) and a clear, monotonic rise in rejections-per-node through n=200, including 53 outright placement failures at that scale. Confirmed deterministic/reproducible across two independent process invocations of `python3 sandbox.py`, output diffed byte-identical. First sandbox attempt (area scaled proportionally with n, holding density constant) produced a false negative — zero rejections at every scale — caught and corrected before filing, not reported as the result.
- Link: session (brain train seams: draft + the-game-the-recursion); sandbox `sandbox.py`, scratchpad `gap10/` (run twice as separate process invocations, outputs diffed byte-identical; corrected version only)
- Composed: pappydapimp69/the-game-the-recursion/E6, pappydapimp69/draft/E11

## E14 — scrub safety depends on elapsed time source
- Date: 2026-07-13
- Project: pappydapimp69/draft
- Tags: [gamedev][determinism][testing][animation]
- What: `brain train edge` (dog + draft, shared=12 tags). Composed: projects/pappydapimp69__draft.md#E7 (for scrub-safe bit-identical output, make ONLY the state that needs it a PURE FUNCTION OF ELAPSED TIME) and projects/pappydapimp69__dog.md#E22 (a virtual-clock API can fire the correct NUMBER of steps while its reported elapsed time doesn't match what a real per-frame dt-accumulator sums to under an actual observed slowdown — verify it actually drives the engine's own dt bookkeeping, don't assume nominal step size). Sandbox-confirmed draft#E7's bit-identical guarantee silently breaks when the scrub path's elapsed-time SOURCE (a virtual clock assuming nominal step size) diverges from the playback path's real accumulated dt — exactly dog#E22's gap — even though the pure-function formula itself is untouched and correct.
- Why built: draft#E7 states its guarantee purely in terms of the FORMULA ("a pure function of elapsed time" gives bit-identical output under scrub vs playback) and never specifies what "elapsed time" must be measured FROM. dog#E22 independently warns that a virtual-clock API's reported elapsed time is not automatically trustworthy. Neither entry connects the two — draft#E7 assumes a correct elapsed-time input exists; dog#E22 shows that assumption itself needs verification.
- Design: `sandbox.py` — zero RNG, zero wall-clock. A draft#E7-style pure function `pure_rotation(elapsed) = (elapsed * 90) % 360`. Playback path: real per-frame dt accumulator summed over 8 fixed frame times reflecting an actual observed slowdown (dog#E2/E22's finding — headless frames genuinely running longer than nominal, ~0.020s vs a 0.016s nominal step, fixed values not random). Scrub path: a virtual clock that fires the correct step COUNT (8) but assumes each step was the nominal 0.016s, unaware of the real slowdown — computing `elapsed = 0.016 * 8`.
- Got right: draft#E7's pure-function formula itself is exactly correct and never in question — both paths call the identical `pure_rotation` function; nothing about the composition disputes that design.
- Where/why it failed: real accumulated elapsed came out `0.16`, virtual clock elapsed came out `0.128` — a real, measurable divergence purely from WHICH elapsed-time source was used, with the same step count on both sides. `playback_rotation` (14.4°) and `scrub_rotation` (11.52°) differ — draft#E7's bit-identical guarantee fails, and nothing about `pure_rotation` is buggy; the bug (if this is wired up in a real scrub-safe animation) would be entirely in trusting a virtual clock's assumed step size over the real per-frame dt sum.
- Fix: Not applied to any shipping code (composition/flagging entry). Any draft#E7-style "pure function of elapsed time" implementation must source its `elapsed` from the SAME accumulation dog#E22 already prescribes verifying (a real per-frame dt sum, or a virtual clock explicitly confirmed via dog#E22's own method — "a cheap per-frame probe that it actually advances YOUR engine's own dt bookkeeping" — to match it), never from a virtual clock's assumed nominal step size taken on faith.
- Why this fix: draft#E7 and dog#E22 were each correct and complete for what they individually described — the value here is only that draft#E7's guarantee has an unstated dependency dog#E22 already knows how to verify, so a future session implementing scrub-safety doesn't have to independently rediscover that a virtual clock's elapsed time needs the same scrutiny dog#E22 already gives it.
- Rule of thumb: A "pure function of elapsed time" scrub-safety guarantee (draft#E7) is only as trustworthy as its elapsed-time SOURCE — verify that source matches the real per-frame dt-accumulator's sum (dog#E22's own prescribed check), especially under any headless/test-harness/slowed timing context, before trusting bit-identical output between scrub and continuous playback.
- Provenance (verified/assumed): Verified first-hand — built `sandbox.py` (zero RNG, zero wall-clock, 8 fixed frame-dt values reflecting an observed slowdown, one virtual-clock nominal-step assumption), confirmed real accumulated elapsed (0.16) diverges from virtual clock elapsed (0.128), and confirmed the identical pure function produces different, non-bit-identical output (14.4 vs 11.52) from those two elapsed-time sources. Confirmed deterministic/reproducible across two independent process invocations of `python3 sandbox.py`, output diffed byte-identical. (First sandbox attempt used frame-dt values that coincidentally summed to the same total as the virtual clock's assumption — caught before filing, corrected to values reflecting a real systematic slowdown rather than symmetric jitter that cancels out.)
- Link: session (brain train edge: dog + draft); sandbox `sandbox.py`, scratchpad `gap6/` (run twice as separate process invocations, outputs diffed byte-identical)
- Composed: pappydapimp69/draft/E7, pappydapimp69/dog/E22

## E13 — narrative paradox tension settled by sandbox
- Date: 2026-07-18
- Project: pappydapimp69/draft
- Tags: [gamedesign][narrative]
- What: Tension T19 ("plot coherence vs perceived player agency, the
  narrative paradox") rests on a reasoned position citing external
  interactive-narrative literature (Riedl/Young drama managers, Yu &
  Riedl presentation-steering, Emily Short salience/storylets): a fixed
  authored spine + a drama manager that selects among pre-authored,
  never-pruned variants based on salience/quality "steers ~70-74% of
  choices while removing no branch — structural agency intact." That
  claim had never been verified first-hand with a built model in this
  system — only cited. `brain train gap` targeted this tension as the
  real gap to settle.
- Why built: `brain train gap`'s own rule (tension T22): a reasoned or
  cited argument is a CANDIDATE, never verification — settle it by
  building and running a sandbox model that reproduces the claimed
  behavior, or refutes it.
- Design: `sandbox.py` — a deterministic 8-beat fixed story spine; every
  beat holds a POOL of pre-authored variant lines (a contentless generic
  default plus 1-4 tag-gated variants), NEVER pruned between
  playthroughs. A drama-manager function selects, per beat, the
  highest-quality variant whose full prerequisite tag set is satisfied
  by the player's real accumulated choice history (a "requires ⊆
  history" check) — pure presentation-steering, not branch-removal: the
  full pool exists identically for every playthrough. Four hand-scripted
  (non-random) playthroughs: two maximally-contrasting "pure" arcs
  (mercy+diplomat, ruthless+aggressive) and two deliberately MIXED arcs
  that partially satisfy either extreme (diplomat-only-no-mercy;
  spared-rival-but-then-aggressive) — the mixed ones are the sharper
  test of whether the manager does real selection or a disguised binary
  bucket.
- Got right: measured three things directly instead of reasoning about
  them: (1) COHERENCE — fraction of beats landing a real, tag-satisfied
  callback vs. a generic default; (2) AGENCY — how many of 8 beats
  differ in content between contrasting playthroughs; (3) STEERING RATE
  — fraction of all selections across all playthroughs that were
  non-default, to compare against the cited 70-74% figure.
- Where/why it failed: N/A — this sandbox settles an open tension, it
  does not report a bug. The one genuine risk it specifically tested
  for (and did NOT find): that a "salience-steered" mechanism might
  secretly collapse to a disguised binary branch (mercy-path vs.
  ruthless-path) rather than real per-tag selection. It did not — the
  two deliberately mixed playthroughs correctly avoided EVERY full-arc
  callback variant (`b4_mercy_diplomat`, `b4_ruthless_aggressive`,
  `b7_full_mercy_arc`, `b7_full_ruthless_arc` all absent from their
  selections) and instead landed on partial, less-specific callbacks —
  confirming the mechanism responds to the REAL tag set, not a coarse
  playstyle classification.
- Fix: N/A — no code fix, this is a design-tension settlement.
- Why this fix: not applicable in the bug-fix sense; the sandbox's
  measured numbers are the finding.
- Rule of thumb: for an interactive-narrative system torn between a
  fixed authored spine (coherence) and real player agency: model the
  "drama manager" as PURE PRESENTATION-STEERING over a static, complete
  variant pool (never pruning a branch, never inventing content) keyed
  by a prerequisite-tag-subset check against real accumulated player
  choices, and verify it doesn't secretly reduce to a small number of
  coarse buckets by testing DELIBERATELY MIXED playthroughs (partial tag
  satisfaction), not just the two most extreme, opposite ones — the
  extremes alone cannot distinguish "real per-tag selection" from "a
  disguised binary branch with two names."
- Provenance (verified/assumed): Verified first-hand — built and ran
  `sandbox.py` (zero RNG, zero wall-clock, hand-scripted deterministic
  playthroughs). Results: committed-playstyle coherence 75% (6/8 beats,
  both pure playthroughs), genuinely mixed playthroughs measurably LOWER
  (50% and 62%) as expected; agency divergence 6/8 beats between the two
  pure-opposite playthroughs and 5/8 between the two mixed ones;
  aggregate steering rate 65.6% (21/32 selections across all four
  playthroughs) — in the same ballpark as, but not an exact match to,
  the cited external 70-74% figure, which this sandbox's own numbers
  suggest is a property of the SPECIFIC authored content density (how
  many tag-gated variants exist per beat) rather than a mechanism-
  inherent constant. Re-ran the script as two independent process
  invocations; output byte-identical both times.
- Composed: N/A (settles tension T19 directly; not composed from two
  memory entries)
- Link: session 7195397b-63a9-5efe-a80b-2792eaa6645e (`brain train gap`,
  targeting open tension T19); sandbox
  `scratchpad/train_gap/sandbox.py`, run twice as independent process
  invocations, outputs diffed identical

## E12 — polling catches flakiness not scheduler drift
- Date: 2026-07-18
- Project: pappydapimp69/draft
- Tags: [testing][harness][determinism]
- What: dog#E22's prescribed headless-testing methodology ("never compute
  a fixed wait from an assumed timing ratio — poll for the real observed
  state transition instead, with a generous timeout") reliably avoids
  FALSE FAILURES, but gives a FALSE ALL-CLEAR for the-game-prologue#E20's
  exact class of bug (a tick scheduler that re-anchors `nextTickAt = now
  + TICK_MS` and permanently loses ticks under sustained lower
  framerate) — a polling test just asks "did the target state eventually
  arrive within a generous timeout," and the buggy scheduler DOES
  eventually reach the target tick count, just measurably slower than
  ideal, so the poll passes with zero signal that anything is wrong.
- Why built: `brain train edge` returned dog + the-game-prologue as the
  single highest-value untested pair again (12 shared tags, one edge
  already filed between different entries this session). dog#E22
  (verified first-hand: don't trust a fixed timing ratio or an unverified
  virtual-clock API for headless game-loop tests, poll for the real
  state instead) and the-game-prologue#E20 (verified first-hand against
  real shipping code: a live, currently-unfixed scheduler bug losing up
  to ~12% of ticks under sustained low framerate, invisible to the
  existing golden-fingerprint replay suite) are both about headless
  testing of real-time game loops, but neither had been checked against
  the other — does dog#E22's own prescribed fix actually catch
  prologue#E20's bug, or does it just look like it would?
- Design: `sandbox.py` — zero RNG driving the measurement (a seeded
  PRNG only constructs the deterministic jittery frame-delta sequence,
  mirroring prologue#E20's own harness design). Two scheduler
  implementations: `run_buggy_scheduler` (prologue#E20's real shipped
  shape — re-anchors the next tick threshold to the actual firing time,
  discarding overshoot) and `run_fixed_scheduler` (the known-correct
  drain-and-subtract accumulator prologue#E20 itself cites as the fix,
  from `sandbox-combined-game-loop#E1`/`#E2`). Two independent test
  methodologies run against both schedulers on the SAME frame-delta
  sequence: `dog_e22_style_poll_test` (dog#E22's exact prescription —
  did the target tick arrive within a generous timeout, no fixed ratio)
  and `prologue_e20_style_drift_assertion` (an explicit comparison of
  real elapsed time at the target tick against the ideal elapsed time
  for that tick count, within a tolerance).
- Got right: dog#E22's polling methodology behaves exactly as advertised
  for its OWN stated purpose — it never produces a false failure; both
  the buggy and correct schedulers pass it, because both eventually
  reach the target tick within the generous timeout.
- Where/why it failed: under a sustained lower-framerate frame sequence,
  the buggy scheduler reaches the target tick (50) after 5835.6ms of
  real time against an ideal of 5000ms — a 16.7% permanent drift,
  consistent with prologue#E20's own live measurement (~6.6% at a
  smaller framerate gap, worse here at a larger one). dog#E22's polling
  test reports `passed: True` for this exact run — it has no assertion
  anywhere that compares real elapsed time to the ideal for the tick
  count reached, so a scheduler that is measurably, permanently slower
  than correct looks identical, from that test's perspective, to one
  that is not.
- Fix: not a code fix — this composes two TEST-METHODOLOGY lessons, not
  a bug in either project's shipped code. The gap is closed by adding
  `prologue_e20_style_drift_assertion` (explicit real-elapsed-time-vs-
  ideal-tick-count comparison) as a SEPARATE, additional check alongside
  — not instead of — dog#E22's polling approach: polling still correctly
  avoids flaky false failures from timing-ratio assumptions, while the
  drift assertion is what actually catches a scheduler that has silently
  desynced from real time.
- Why this fix: the two methodologies check orthogonal properties —
  polling checks "did the expected state eventually occur" (robust
  against timing noise, blind to systematic drift); the drift assertion
  checks "did it occur at the RIGHT real time" (exactly what a scheduler
  bug like prologue#E20's violates). Neither subsumes the other; a test
  suite built only around dog#E22's prescription (a reasonable, correct
  response to that project's OWN flakiness problem) provides zero
  coverage of the entirely different bug class prologue#E20 found.
- Rule of thumb: a "poll for the real state transition, don't compute a
  fixed wait" testing methodology (dog#E22, the correct fix for ratio-
  based test flakiness) is necessary but not sufficient for any real-
  time scheduler whose correctness depends on tick-count-per-elapsed-
  real-time (the-game-prologue#E20's class of property) — polling alone
  can only ever detect "it never arrived," never "it arrived late in a
  way that will compound over a real session." Any project with BOTH a
  flakiness-motivated polling test harness AND a real-time scheduler
  advancing authoritative game state needs a SEPARATE, explicit
  assertion comparing real elapsed time against the ideal for the state
  reached — add it alongside polling, not as a replacement for it.
- Provenance (verified/assumed): Verified first-hand — built and ran
  `sandbox.py` (seeded-PRNG-constructed but otherwise deterministic
  frame-delta sequence), confirming the polling test reports `passed:
  True` for BOTH the buggy scheduler (16.7% real drift, 835.6ms late at
  tick 50) and the correct scheduler, while the explicit drift assertion
  correctly fails only on the buggy scheduler and passes on the correct
  one. Re-ran as two independent process invocations, output
  byte-identical both times.
- Composed: pappydapimp69/dog/E22, pappydapimp69/the-game-prologue/E20
- Link: session 7195397b-63a9-5efe-a80b-2792eaa6645e (`brain train
  edge`, top-ranked pair dog + the-game-prologue); sandbox
  `scratchpad/train_edge/sandbox.py`, run twice as independent process
  invocations, outputs diffed identical

## E11 — reject on sum of radii generalizes to spiral arms
- Date: 2026-07-18
- Project: pappydapimp69/draft
- Tags: [algorithm][gamedesign]
- What: dog#E19's fix mechanism for a min-distance-rejection scatter
  (reject a candidate on `distance < minDist + otherPoint.radius`,
  checked against EVERY already-placed point regardless of category,
  not a flat threshold) generalizes cleanly to draft#E8's spiral-arm
  collision (a two-arm layout with asymmetric populations, 20 nodes vs
  8, where the bigger arm's spiral wrapped past 180 degrees and
  collided with the smaller arm) — applied as reject-and-nudge in
  strict biggest-total-first global order across BOTH arms combined, it
  eliminates the collision using the ORIGINAL, oversized footprint
  sizing (no need for draft#E8's footprint-shrink), and — unlike
  draft#E8's shipped radius-band-floor fix, which fully segregates the
  smaller arm into a radius range entirely outside the bigger one —
  it keeps the two arms sharing a substantial real radius range
  (interleaved), closer to the "two spiral arms" visual the original
  design spec actually asked for.
- Why built: `brain train group` surfaced dog + draft as an untested
  seam (shared tags: algorithm, architecture, gamedesign, gamedev,
  input, process, state, tooling, ui). dog#E19 (scatter-rejection must
  use the sum of real radii, not a flat distance) and draft#E8 (spiral-
  arm collision, fixed via radius-band separation) are both about
  guaranteeing minimum separation between placed objects of varying
  size, in different domains (a scatter algorithm vs. a spiral layout)
  — the open question was whether dog#E19's fix mechanism is a genuine,
  general alternative to draft#E8's specific fix, not just a
  superficially-similar-sounding lesson.
- Design: `sandbox.py` — zero RNG, zero wall-clock, uses the real
  Sprout node totals (20 idea totals, 8 memory totals) and the real
  fixed spiral constants (PAD=18, B=46). Three approaches compared on
  identical inputs: (A) the two arms laid out fully independently with
  the ORIGINAL oversized footprint sizing draft#E8 actually shipped
  with first (before the fix) — reproduces the real collision. (B)
  draft#E8's REAL shipped fix — shrunk footprint sizing AND a radius-
  band floor pushing the smaller arm's r0 out past the bigger arm's
  entire outer reach. (C) dog#E19's exact mechanism applied instead —
  ALL nodes from both arms merged into one list, sorted biggest-total-
  first (global order), each placed by nudging it outward along its
  OWN already-computed angle only until `distance < fp_a + fp_b` fails
  against every previously-placed node from EITHER arm — using the
  ORIGINAL oversized footprint sizing, with no shrink.
- Got right: Approach A reproduces the real bug exactly as shipped (18
  real colliding pairs, worst case a distance of 108.9 against a
  required 223.2 — a big idea node and a big memory node landing on
  top of each other). Approach B (the real shipped fix) is fully
  collision-free, confirming the earlier fix still holds.
- Where/why it failed: N/A — this sandbox exists to test whether an
  ALTERNATIVE fix generalizes, not to find a new bug; draft#E8's shipped
  fix is not being second-guessed as broken.
- Fix: N/A (no code change proposed) — this is a verified alternative,
  not a replacement; draft#E8's shipped radius-band fix is simpler to
  reason about (one arm strictly outside the other, collision
  structurally impossible regardless of tuning) and was kept as-is.
- Why this fix: recorded as a composed finding, not applied as a code
  change, because Draft's shipped fix already works and is simpler; the
  value here is establishing that dog#E19's general mechanism is a real,
  verified alternative for future projects where full radius
  segregation between categories is NOT visually acceptable (e.g. a
  design that specifically wants two categories genuinely interleaved,
  not one nested entirely inside the other) — approach C achieved 0
  collisions AND kept 392px of real radius-range overlap between the
  two arms, using the harder (unshrunk) footprint sizing, while approach
  B necessarily produces 0px of overlap by construction.
- Rule of thumb: dog#E19's rejection rule (`distance < sum of BOTH real
  radii`, checked against every already-placed entity, not a flat/
  partial threshold) is a general-purpose fix for ANY placement/spacing
  algorithm with asymmetric object sizes across categories — not
  specific to scatter algorithms. When a spacing collision must be
  fixed WITHOUT fully segregating the colliding categories into
  disjoint regions (radius bands, angle sectors, etc.), prefer sorting
  ALL contested objects together by size (biggest/most-constrained
  first) and placing each via reject-and-nudge against every previously
  placed object regardless of category, over a structural
  segregation fix — segregation is simpler to reason about and
  collision-proof by construction, but reject-and-nudge preserves
  visual/positional interleaving that segregation cannot.
- Provenance (verified/assumed): Verified first-hand — ran `sandbox.py`
  reproducing draft#E8's real original bug (18 colliding pairs with the
  original, pre-shrink footprint sizing), confirmed draft#E8's actual
  shipped fix is collision-free, and confirmed dog#E19's mechanism
  (applied globally across both arms, biggest-first) is ALSO fully
  collision-free using the harder unshrunk footprint sizing, while
  measurably preserving 392px of real radius-range overlap between the
  two arms (vs. 0px under the shipped fix's full segregation).
- Composed: pappydapimp69/dog/E19, pappydapimp69/draft/E8
- Link: session 7195397b-63a9-5efe-a80b-2792eaa6645e (`brain train
  group`, candidate pair dog + draft); sandbox
  `scratchpad/train_group2/sandbox.py`
- Cited-by: 2026-07-13 · projects/pappydapimp69__draft.md#E15 · compatible · no sandbox · session (brain train seams: draft + the-game-the-recursion); sandbox `sandbox.py`, scratchpad `gap10/` (run twice as separate process invocations, outputs diffed byte-identical; corrected version only)

## E10 — node repo local clone can be stale vs cache
- Date: 2026-07-18
- Project: pappydapimp69/draft
- Tags: [process][tooling]
- What: During `brain train group`, its own instructions ("pull BOTH
  systems' existing entries via `brain query <slug>` each, or read their
  project files") were followed by reading `/home/user/memory/projects/
  pappydapimp69__dog.md` directly — the project-linked local clone, not
  the CLI's machine-wide cache. That file was **50 commits behind**
  `~/.brain/memory` (the live cache): dog's lessons stopped at E35 in the
  local clone vs E55 in the cache, missing 20 real entries including the
  exact one (dog#E39) needed for the composition being investigated.
- Why built: every linked project's own `CLAUDE.md` states "Do not read
  the node repos directly — use the CLI," but `brain train`'s own agent
  instructions explicitly offer "or read their project files" as an
  accepted alternative to `brain query` for pulling a specific system's
  full lesson history — without specifying WHICH of the two directories
  with an identical relative shape (`<project>/../memory/projects/*.md`
  the local per-project clone, vs `~/.brain/memory/projects/*.md` the
  shared cache) that instruction means.
- Design: Brain's architecture (per Brain's own README) is: knowledge
  repos live once per machine in `~/.brain`, and each linked project
  gets its own local clone/mirror at install time. `brain update`/`brain
  sync` explicitly refresh the `~/.brain` cache; nothing in the normal
  session workflow re-pulls each individual project's separate local
  clone of the SAME repos after that initial install.
- Got right: `brain query` and `brain sync` themselves always read/write
  through the fresh `~/.brain` cache — the staleness only exists in the
  side-channel "or read their project files" path, and only because two
  directories happen to look interchangeable by relative path shape.
- Where/why it failed: nothing signals the staleness at read time — the
  stale file opens, parses, and reads exactly like a normal, current
  project file; there is no version stamp, no warning, no error. It
  surfaced only because a specific expected entry (dog#E39) was missing
  from the file actually read, prompting a manual `git log --oneline`
  comparison between the local clone and the cache, which showed the
  clone frozen at a commit from several days earlier while the cache had
  continued advancing (steward promotions, new proposals, syncs from
  other sessions/projects all landing in the cache, none of them ever
  reaching the project's own separate clone).
- Fix: re-read the same entries from `~/.brain/memory/projects/*.md`
  (the live cache) instead of the project-linked clone, confirmed the
  cache was current via `git log`, and proceeded with the fresh content;
  the composed lesson this was building toward (dog#E20 + dog#E39 +
  the-game-prologue#E6) depended on dog#E39 existing at all, which the
  stale clone did not have.
- Why this fix: `~/.brain/<repo>` is the ONE location Brain's own tooling
  (`brain update`, `brain sync`) actually keeps current; a project's
  separate local clone of the same repos has no such guarantee once the
  session is running, so it is never the right fallback for "read the
  project files directly" when currency matters, which it always does
  for mining/composing new lessons against existing ones.
- Rule of thumb: when a Brain-oriented instruction says "read the
  project/node repo files directly" as a fallback to the CLI, and more
  than one directory on disk has the identical relative-path shape
  (a project's own local clone vs the machine-wide `~/.brain` cache),
  default to the CACHE path (`~/.brain/<repo>/...`), not a project's own
  clone — the cache is the only one `brain update`/`brain sync` promise
  to keep current. If a project's own clone must be used instead (e.g.
  no cache access), diff its `git log --oneline` against the cache's
  first, since a stale read looks identical to a fresh one until an
  entry you expected to exist turns out to be missing.
- Provenance (verified/assumed): Verified first-hand — compared `git log
  --oneline` between `/home/user/memory` and `~/.brain/memory`, showing
  the project clone frozen at `bba6f60` ("Install Brain cognitive system
  link (full mode)") while the cache had 50 additional commits past that
  point; confirmed dog#E39 (needed for the in-progress composed lesson)
  exists in the cache's copy of `pappydapimp69__dog.md` and is absent
  from the project clone's copy.
- Composed: N/A
- Link: session 7195397b-63a9-5efe-a80b-2792eaa6645e (`brain train
  group`, candidate pair dog + the-game-prologue, prior to filing
  `resolver-branch-inert-under-fixed-vocab-capture`)

## E9 — resolver branch inert under fixed vocab capture
- Date: 2026-07-18
- Project: pappydapimp69/draft
- Tags: [ui][gamedesign][input]
- What: A dog#E20-shaped single-action-resolver (one function returns AT
  MOST ONE candidate action/verb id, extended by adding a new branch —
  no new UI wiring) sitting on top of a the-game-prologue#E6-shaped
  input-capture layer (a `poll()` that only promotes raw captured ids
  into one-shot "presses" for a FIXED hardcoded vocabulary) silently
  produces NO effect for a brand-new UI zone: the resolver's new branch
  is entirely correct and returns the right id, but the capture layer
  drops that id's raw click event before the resolver ever receives a
  press for it, so nothing fires — with no error, no wrong branch, and
  no signal anywhere in the resolver itself.
- Why built: `brain train group` surfaced dog + the-game-prologue as an
  untested seam (shared tags: architecture, browser, determinism,
  gamedesign, gamedev, harness, input, process, state, testing, tooling,
  ui). Pulling both projects' entries: dog#E20 (single-action-resolver,
  "new verb = new branch, no new UI wiring") and its own later extension
  dog#E39 ("valid only while there's truly ONE selectable target; a
  SECOND item on the same surface needs real selection state") together
  describe one failure axis for this pattern — "which of N targets."
  the-game-prologue#E6 (a fixed-vocabulary input-capture layer silently
  dropping ids for a newly-added UI surface, e.g. a title screen) reads
  as a structurally similar "fixed vocabulary breaks under growth"
  pattern, but at a DIFFERENT layer and along a DIFFERENT axis than
  E39 — the question was whether these actually compose into a genuinely
  new failure mode, or just restate one of the two lessons.
- Design: `sandbox.py` — zero RNG, zero wall-clock. `context_action()`
  is dog#E20's exact shape: one function, one new branch for a brand-new
  UI zone ("startNewSaga"), returning at most one candidate id.
  `poll_broken()` reproduces prologue#E6's exact original bug (`{name:
  True for name in raw_events if name in FIXED_ACTIONS}`, dropping
  anything outside `{"confirm","cancel","alt"}`); `poll_fixed()` is
  prologue#E6's real shipped fix (promote ANY captured id as a one-shot
  press). `interact()` is the single chokepoint dog#E20 describes,
  firing only if a press actually arrived for the resolved id. A third
  function, `run_isolated_resolver_test()`, models what an isolated
  unit test of the resolver alone looks like — feeding `interact()` a
  synthetic press directly, bypassing `poll()` entirely, matching how
  both dog#E20 and prologue#E6 independently describe their own bugs as
  invisible "in isolation."
- Got right: dog#E20's resolver claim holds exactly as advertised in
  BOTH capture-layer variants — `resolved_id == "startNewSaga"` in every
  run, confirming the single-resolver pattern itself needed zero new UI
  wiring to add the branch, exactly as dog#E20 claims.
- Where/why it failed: under the broken (fixed-vocabulary) capture
  layer, `interact()` returns `None` despite a real click on the new zone
  and a fully correct resolver branch for it — `presses` comes back `{}`
  because `poll_broken()` silently dropped `"startNewSaga"` before the
  resolver ever saw a press. This is a THIRD distinct way a "new verb =
  new branch, no new UI wiring" claim can quietly fail — not dog#E39's
  "which of N simultaneous targets" (there is exactly one target here,
  E39 doesn't apply), but "does an event for this target ever arrive at
  this layer at all." The isolated resolver-only test (bypassing
  `poll()`) reports a clean pass in every case, confirming the failure is
  invisible to exactly the kind of test each source lesson independently
  warned looks fine in isolation.
- Fix: not a new code fix — this sandbox exists to test whether the
  composition holds, and it does; the fix is prologue#E6's own real
  shipped fix (open-set one-shot press promotion, fixed vocabulary
  reserved only for continuously-holdable actions needing real edge
  detection), which the sandbox's `poll_fixed()` confirms is also
  sufficient to unblock a dog#E20-shaped resolver sitting above it.
- Why this fix: dog#E20's "no new UI wiring needed" claim is really "no
  new wiring needed IN THE RESOLVER" — it says nothing about the layer
  beneath the resolver that decides which raw events even become
  deliverable presses. prologue#E6's fix (make one-shot press promotion
  open-set) is the correct complement: it makes the capture layer's
  guarantee match what a growing single-resolver pattern actually needs
  from it.
- Rule of thumb: when a single-action-resolver pattern (dog#E20) is
  extended with a new verb/UI zone, correctness of the new resolver
  BRANCH is not sufficient — also confirm the input-CAPTURE layer
  beneath it is open-set (delivers a press for ANY captured id, not just
  a pre-known fixed vocabulary), or the new branch will be silently
  inert for real clicks on the new zone with zero error anywhere.
  Testing the resolver in isolation (a synthetic press fed directly)
  cannot catch this — only a full zone-click → capture → resolver
  pipeline test can. This composes with, but is distinct from, dog#E39
  ("single-target resolver breaks once a SECOND item joins the same
  surface" — a selection-count problem): this is an event-delivery
  problem that occurs even with exactly one new target.
- Provenance (verified/assumed): Verified first-hand — built and ran
  `sandbox.py` (zero RNG, zero wall-clock), confirming the resolver
  branch resolves correctly in all cases, `interact()` returns `None`
  under the broken fixed-vocabulary capture layer despite a real click
  event for the new zone, `interact()` fires correctly under the fixed
  open-set capture layer, and the isolated resolver-only test reports a
  false clean pass in a way that would mask this exact bug. Re-ran the
  script as two independent process invocations; output byte-identical
  both times.
- Composed: pappydapimp69/dog/E20, pappydapimp69/dog/E39,
  pappydapimp69/the-game-prologue/E6
- Link: session 7195397b-63a9-5efe-a80b-2792eaa6645e (`brain train
  group`, candidate pair dog + the-game-prologue); sandbox
  `scratchpad/train_group/sandbox.py`, run twice as independent process
  invocations, outputs diffed identical
- Cited-by: 2026-07-20 · projects/local__sandbox-capture-layer-starves-tutorial.md#E1 · compatible · no sandbox · session (this conversation, "brain train external research prologue" — draft + the-game-prologue seam); scratchpad `sandbox_capture_layer_starves_tutorial.mjs`; external source: https://generalistprogrammer.com/tutorials/game-analytics-complete-data-tracking-guide-2025.
- Cited-by: 2026-07-20 · projects/local__sandbox-capture-layer-starves-tutorial.md#E2 · compatible · no sandbox · session 7195397b-63a9-5efe-a80b-2792eaa6645e (bare `brain train`, re-verifying the flagged single-source edge `sandbox-capture-layer-starves-tutorial + draft`); sandbox `scratchpad/reverify_capture/sandbox.mjs`, run twice as independent process invocations, outputs diffed identical
- Cited-by: 2026-09-28 · projects/local__sandbox-capture-layer-starves-tutorial.md#E4 · compatible · no sandbox · scheduled brain train session 2026-09-28
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-august-10-draft-positive-control-fidelity.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-07-13 · projects/pappydapimp69__dog.md#E58 · compatible · no sandbox · session (brain train edge: dog + draft); sandbox `sandbox.py`, scratchpad `gap2/` (run twice as separate process invocations, outputs diffed byte-identical)
- Cited-by: 2026-10-20 · projects/pappydapimp69__brainwork.md#E550 · compatible · sandboxes/2026-10-20__ddmin-with-lazy-positive-control-draft.py · observed RESULT: PASS ddmin stalls on one of two causes (['P'] then ['S']); lazy control blames a healthy predicate. Faithful control with healthy predicate: True; lazy: False. · scheduled brain train run, 2026-10-20; session_01AxvhKMfKUmYVr8Ree8rqE7

## E8 — spiral arm collision asymmetric populations
- Date: 2026-07-18
- Project: pappydapimp69/draft
- Tags: [gamedesign][algorithm]
- What: A two-arm spiral/radial layout (28 nodes total: 20 on one arm, 8 on
  the other, each node's angular spacing derived from its own on-screen
  footprint via `theta += (prevMax+thisMax+PAD)/r`) visually collided —
  the 20-node arm's spiral wrapped past 300 degrees and crossed directly
  into the 8-node arm's territory, so individual node "orbit" circles from
  the two different arms overlapped and visually merged at the end of a
  timelapse animation once every node was revealed.
- Why built: building a real-data growth visualization ("Sprout") with two
  categories (ideas domains, memory tag-buckets) laid out as two spiral arms
  180 degrees apart per a design spec, biggest-total nearest the core,
  tapering outward, each grown node becoming its own "tiny galaxy" of
  satellite rings.
- Design: the per-node angular-spacing formula and its constants (PAD=18,
  a fixed spiral-pitch constant B=46) were given explicitly by the design
  spec and correctly implemented; per-node footprint sizing (core radius +
  glow halo + satellite ring budget, used both for the SAME arm's own
  internal spacing AND for camera safety) was my own invention, not spec-
  fixed, and was sized generously (~100-110px per node at the largest
  nodes) without checking it against the fixed spacing constants.
- Got right: within a SINGLE arm, adjacent nodes never overlapped — the
  spacing formula correctly kept same-arm neighbors apart regardless of
  footprint size, at every population count tested.
- Where/why it failed: the two arms have very unequal populations (20 vs
  8) and the spacing formula only reasons about the CURRENT arm's own
  neighbors; nothing in it (or in the two arms merely starting 180 degrees
  apart) prevents one arm's spiral from wrapping angle-wise into the other
  arm's physical territory once its total angular sweep exceeds 180
  degrees. With generously-sized per-node footprints and a real 20-node
  arm, the sweep reached ~315 degrees before rescaling — comfortably far
  enough to overlap the other, much shorter (8-node, <60 degree) arm's
  region. This is a real, sandbox-confirmed visual collision, only caught
  by rendering the FINAL frame (every node revealed) and looking at it —
  it was invisible in early-timeline screenshots where few nodes had
  spawned yet.
- Fix: two changes. (1) Shrank the per-node footprint formula roughly 2x
  (smaller core/halo radii, smaller ring-gap, and — critically — dropped
  the full satellite-ring budget from the SPACING footprint entirely,
  since translucent ring outlines are cheap to let brush a neighbor while
  solid cores must never touch) — this reduces but does not eliminate the
  wrap, since PAD is spec-fixed and 20 nodes' worth of PAD alone forces
  over 180 degrees of sweep at any reasonable footprint size. (2) Gave the
  smaller arm its own radius FLOOR, computed as (bigger arm's actual outer
  reach) + (smaller arm's own biggest-node footprint) + PAD, so the
  smaller arm's entire radius range starts strictly beyond the bigger
  arm's outer edge — this makes collision structurally impossible
  regardless of how much either arm's angle sweeps, independent of node
  count or footprint tuning.
- Why this fix: angular separation (each arm gets its own 180-degree
  half) cannot be relied on once one arm's population is large enough that
  its own natural spacing needs more than 180 degrees of sweep — this is
  a structural fact of the population imbalance, not a tunable-constant
  bug, so no amount of footprint-shrinking alone would have been provably
  safe for an arbitrary future node count. Radius-band separation removes
  the dependency on angle entirely.
- Rule of thumb: for a shared-origin multi-arm/multi-category radial or
  spiral layout, do not assume "started N degrees apart" keeps categories
  visually separated once population counts are asymmetric across
  categories — verify by rendering the layout with every item present
  (not just a few), and if any category's own required angular sweep can
  exceed its allotted angular share, separate categories by a RADIUS band
  (derived from the actual, measured outer reach of the others) rather
  than by angle alone; radius-band separation is collision-proof by
  construction, angle-only separation is not once population is uneven.
- Provenance (verified/assumed): verified first-hand — reproduced via a
  live headless screenshot at the animation's final frame (all 28 nodes
  revealed) showing real node-to-node overlap between the two arms;
  confirmed fixed via a second full timeline sweep (every ~6-7 seconds)
  after the radius-band change, with the same final-frame screenshot
  showing two cleanly separated regions and zero overlapping cores.
- Composed: N/A
- Link: session 7195397b-63a9-5efe-a80b-2792eaa6645e, Sprout artifact build
  (spiral-galaxy growth timelapse), Step 8.5 broad-sweep verification
- Cited-by: 2026-07-18 · projects/pappydapimp69__draft.md#E11 · compatible · no sandbox · session 7195397b-63a9-5efe-a80b-2792eaa6645e (`brain train group`, candidate pair dog + draft); sandbox `scratchpad/train_group2/sandbox.py`

## E7 — scrubbable timeline needs pure function of time
- Date: 2026-07-18
- Project: pappydapimp69/draft
- Tags: [gamedesign][state]
- What: A slow ambient rotation for a scrubbable canvas timelapse (a
  "galaxy" drifting/spinning over the whole animation, plus temporary
  extra "kick" spins during a few scripted cutscene moments) was
  implemented as `rotAtTime(simT)` — a pure function that recomputes the
  correct rotation angle from scratch given any timestamp — instead of
  the more obvious `state.rot += rotVel*dt` per-frame accumulator pattern
  used for everything else that visually "drifts" in the same build
  (camera scale, flash/title-card fades all use a per-frame `smooth()`
  toward a target).
- Why built: the artifact exposes `window.__viz.seek(t)` for arbitrary
  scrubbing (a user dragging the transport bar, or a verification script
  jumping straight to `dur()` or to a specific cutscene's peak) — the
  rotation angle at an arbitrary scrubbed-to timestamp must exactly match
  whatever it would have been had playback run continuously to that same
  point, with no visible pop when scrubbing forward vs letting it play.
- Design: `rotAtTime(t) = ROT_SPEED*t + sum of each cutscene's own kick
  contribution (an eased function of how far past that cutscene's own
  start time t already is)` — every term is a closed-form function of the
  single input `t`, with no reference to any prior frame's state.
  `seek(t)` and the live per-frame step call the exact same function.
- Got right: scrubbing to any point (including the exact end via
  `dur()`, or mid-cutscene) produces bit-identical rotation to reaching
  that point by continuous playback — verified directly by the
  headless test harness, which jumps straight to `dur()` and to each
  cutscene's peak with no intermediate frames ever simulated, and never
  saw a rotation discontinuity or an accumulated-drift artifact.
- Where/why it failed: this is a design tradeoff, not a bug — the real
  cost is that this pattern is noticeably more work to write correctly
  than the per-frame accumulator used everywhere else in the same file
  (camera scale, fades): every effect that touches rotation has to be
  expressed as a closed-form eased function of elapsed-time-since-its-
  own-start, rather than "just add a value each frame," and adding a
  NEW kind of transient rotation effect later means writing another
  closed-form contribution term, not just tweaking a velocity value in
  the frame loop.
- Fix: N/A — this was chosen deliberately, up front, specifically for
  the one state variable (rotation) that a verification/scrub codepath
  needed to jump to arbitrary times for; the other, non-rotation drifting
  values in the same build (camera scale, flash, title-card fade) were
  deliberately LEFT as per-frame accumulators, because scrubbing only
  needs THEIR END STATE at the target time to look reasonable (a
  `seek()` call recomputes them from a hard formula at seek-time anyway,
  not by replaying accumulated smoothing), not bit-exact continuity with
  hypothetical continuous playback.
- Why this fix: the two patterns were deliberately assigned per-variable
  based on what scrubbing to an arbitrary point actually needs from that
  variable — visually continuous ambient motion across arbitrary seeks
  (rotation) needs a pure function; a value that just needs to reach the
  RIGHT value by the target time, with the actual visual smoothing only
  mattering during continuous forward playback, is fine as a per-frame
  accumulator recomputed fresh on seek.
- Rule of thumb: before choosing "accumulate this every frame" for any
  animated/drifting value in a build that must support scrubbing to
  arbitrary timestamps (a video-like transport bar, an automated test
  harness that jumps straight to specific moments, a replay/seek
  feature), ask whether that SPECIFIC value needs bit-identical output
  whether reached by scrubbing or by continuous playback. If yes, make it
  a pure function of elapsed time with no reference to prior frames — if
  the value only needs to look reasonable at whatever time you land on
  (and a seek can cheaply recompute a plausible instantaneous value from
  scratch), a per-frame accumulator reset-on-seek is simpler and fine.
- Provenance (verified/assumed): verified first-hand — the headless
  verification harness for this build repeatedly `seek()`s directly to
  `dur()` and to specific cutscene peak timestamps with zero prior frames
  ever simulated, and produced correct, driftless rotation state at every
  one of those jumps across multiple independent test runs.
- Composed: N/A
- Link: session 7195397b-63a9-5efe-a80b-2792eaa6645e, Sprout artifact
  build (spiral-galaxy growth timelapse), `rotAtTime`/`seek` implementation
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-draft-recursion-purity-is-relative-to-a-named-clock.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-scrub-vs-roll-count.md#E1 · compatible · no sandbox · session (brain train combined: draft + the-game-the-waiting-city); sandbox `sandbox.js`, scratchpad `braintrain_combined/` (run twice as separate process invocations, outputs diffed byte-identical)
- Cited-by: 2026-08-01 · projects/local__sandbox-edge-draft-opticon-scrub.md#E1 · compatible · no sandbox · this session; `brain train edge` (draft + opticon, 14 shared tags)
- Cited-by: 2026-09-28 · projects/local__sandbox-kernel-system-cutscene.md#E2 · compatible · sandboxes/2026-09-28__train-gap-b07.py · session 2026-09-28, brain train gap batch 7 loop 32
- Cited-by: 2026-07-20 · projects/local__sandbox-seed-vs-replay-verification.md#E1 · compatible · no sandbox · session (this conversation, "brain train edges" — dog + draft, the top-ranked untested pair); scratchpad `sandbox_seed_vs_replay_verification.mjs`.
- Cited-by: 2026-07-13 · projects/pappydapimp69__draft.md#E14 · compatible · no sandbox · session (brain train edge: dog + draft); sandbox `sandbox.py`, scratchpad `gap6/` (run twice as separate process invocations, outputs diffed byte-identical)
- Cited-by: 2026-07-13 · projects/pappydapimp69__test.md#E23 · compatible · no sandbox · session (brain train edge: draft + test); sandbox `sandbox.py`, scratchpad `gap7/` (run twice as separate process invocations, outputs diffed byte-identical)
- Audited: 2026-10-13 · modeled · Read the entry; it has no stored sandbox, only a claim that a headless harness seeking to the end and to cutscene peaks saw rotation identical to continuous playback, so question 1 (does a model compute the result) cannot be checked from the entry. The claim concerns a real canvas artifact, and the only evidence is the author's harness, which is not shipped. I ran a small stdlib check of the underlying arithmetic: a per-frame accumulator at 1/60 s, 1/30 s and 0.0166 s drifts from the closed form rotation by about 1e-11 over 600 s (and the accumulated value depends on the timestep), while a pure function of time returns the identical value for any path, so the design rule holds in principle. The Rule of thumb is about when bit-identical output is needed, which the entry reasons rather than measures (no accumulator-versus-pure comparison is recorded), so it is graded modeled, not pass. · scheduled brain train session, loop 1 pass 3 audit; session_01UeKMwUeVxtmySB3P82SSXJ

## E6 — real data sparser than spec assumed
- Date: 2026-07-18
- Project: pappydapimp69/draft
- Tags: [process][gamedesign]
- What: A detailed build spec for a real-data growth timelapse assumed a
  scale it did not verify against the actual data ("expect roughly 6-10
  shift/pivot days out of 20-35 total days") — reconstructing the real
  git history of the two source repos showed only 4 distinct calendar
  dates of activity total, not 20-35. The shift-day guidance's ratio
  (~25-35%) was kept, applied to the real day count (4) instead of the
  assumed one, rather than either forcing the spec's absolute numbers
  (impossible — there is no way to manufacture 20+ real days that don't
  exist) or padding with invented "pivot" days to make the animation feel
  as populated as the spec implied.
- Why built: the spec's own governing rule, stated elsewhere in the same
  document, was stricter than its own scale assumption: "don't fabricate
  any narrative, number, or date — every caption and delta must trace
  back to a real commit." Reconstructing the actual commit history is a
  required first step specifically so that every later creative decision
  (captions, which days are "shifts", pacing) is grounded in what really
  happened, not in what a template assumed would have happened.
- Design: ran the real reconstruction FIRST, before writing any
  caption or picking any shift day, and let the real day count (4) —
  not the spec's example count — set the denominator for every
  downstream proportional decision (shift-day ratio, how compressed the
  resulting animation would be, how much per-day pacing room to give).
- Got right: every caption, every date, and both real per-category
  totals in the finished artifact trace to an actual commit — verified
  by a headless replay whose end-state exactly matched the reconstructed
  real final totals, and by hand-checking the reconstructed date list
  against `git log --format=%ad --date=short` on the real tracked files.
- Where/why it failed: the tradeoff, not a bug: a spec's own worked
  example/scale assumption can be wrong for the ACTUAL target data
  without the spec author having lied or erred about anything checkable
  in advance — an assumption like "20-35 days" is often just the
  author's mental model of "how much history probably exists," written
  before anyone actually walked the real commit log. Discovering the
  mismatch only happens if the reconstruction step is actually run against
  real data before any creative decision is locked in, rather than
  building the creative structure to match the spec's stated scale and
  discovering later, downstream, that the real data doesn't support it
  (at which point far more work is invalidated).
- Fix: kept the spec's ratio-based guidance (shift days as a fraction of
  total real days) rather than its absolute-count guidance, and reported
  the discrepancy explicitly to the requester alongside the finished
  artifact rather than silently shipping a "20-35 day feeling" experience
  built from only 4 real days of padding/invention.
- Why this fix: a ratio generalizes correctly to any real day count; an
  absolute count baked in from an assumption does not, and any attempt to
  hit the absolute count (either by inventing intermediate days or by
  reclassifying non-pivot days as pivots to hit a target number) would
  have violated the spec's own stricter "never fabricate" rule, which
  takes precedence over a scale assumption stated elsewhere in the exact
  same document.
- Rule of thumb: when a spec gives both (a) a hard rule about a data
  property (e.g., "never fabricate," "must be real") and (b) a worked
  example or scale assumption calibrated to an expected data size (e.g.,
  "expect N of M items"), treat (a) as load-bearing and (b) as
  illustrative — run the real data reconstruction FIRST, before any
  downstream creative/structural decision locks in, and if the real
  scale differs sharply from the assumption, re-derive (b)'s guidance as
  a RATIO against the real count rather than forcing the absolute
  numbers or bending rule (a) to preserve them. Surface the scale
  mismatch explicitly rather than silently absorbing it.
- Provenance (verified/assumed): verified first-hand — the real
  reconstruction script's two sanity-asserts (per-category delta sums
  equal real final totals) passed for both source repos, the resulting
  date list was hand-confirmed against `git log --date=short` output
  directly, and the finished artifact's shift-day count (3 picked from 4
  real days) was a deliberate, reported adaptation of the spec's stated
  ratio, not an attempt to hit its stated absolute range.
- Composed: N/A
- Link: session 7195397b-63a9-5efe-a80b-2792eaa6645e, Sprout artifact
  build — real growth-data reconstruction step, prior to any caption or
  SHIFTS authoring
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E13 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E5 — memory proposal wrong directory silent noop
- Date: 2026-07-18
- Project: pappydapimp69/draft
- Tags: [process][tooling]
- What: Wrote three fully-formed memory proposals directly into the
  Brain machine-wide knowledge CACHE's incoming folder
  (`~/.brain/memory/incoming/`) instead of the current PROJECT's own
  local mirror (`<project>/.brain/memory/incoming/`). `python3
  scripts/validate.py` run from inside the cache repo reported
  "validation passed" for these files (their schema was fine), and
  `brain sync` run afterward reported "synced (full) — 0 pushed to main,
  0 held" with no error of any kind.
- Why built: `brain mine`'s own instructions say to write proposals into
  `.brain/memory/incoming/<date>__<slug>.md`; the CLI has TWO directories
  matching that relative suffix — the project's local per-repo mirror
  (`<project_root>/.brain/...`, what `brain sync` actually reads FROM)
  and the shared machine-wide cache (`~/.brain/<repo>`, what `brain sync`
  reads/writes ON THE OTHER SIDE, i.e. main). Both are real, both accept
  writes, both pass schema validation — nothing about writing to the
  wrong one produces an error at write time.
- Design: `brain sync`'s actual contract (per `bin/brain`'s own
  `local_root()`) is: copy files FROM `<project_root>/.brain/memory/
  incoming/` INTO the cache's `incoming/`, then push. A file placed
  directly in the cache's `incoming/` already sits on the "destination"
  side of that copy, so sync has nothing to copy for it, and correctly
  reports zero pushed — that is accurate behavior for what sync's
  contract actually promises, not a bug in sync itself.
- Got right: the schema/content of the proposals was entirely correct
  (validate.py passed cleanly) — the mistake was purely about which of
  two same-shaped directories to write into, not the proposal content.
- Where/why it failed: "0 pushed to main, 0 held" reads identically to
  the genuinely correct state (nothing new to sync) and identically to
  this failure state (three real proposals stranded in the wrong spot) —
  there is no distinguishing signal in `brain sync`'s own output between
  "I had nothing to do" and "I had something to do but couldn't find it
  because it's in the wrong of two same-named directories." The only way
  this surfaced was checking `git status --short` inside the CACHE
  repo directly and noticing the three files as untracked there, which is
  not a step the CLI's own success-looking output prompts you to take.
- Fix: moved the three files from `~/.brain/memory/incoming/` to
  `<project_root>/.brain/memory/incoming/` (the project's own local
  mirror, verified empty except a `stubs.md` placeholder beforehand), then
  re-ran `brain sync`, which correctly reported "3 pushed to main, 0
  held."
- Why this fix: matches `brain sync`'s actual documented contract
  (`local_root()` = `<project_root>/.brain`) rather than either of the two
  directories' bare relative-path similarity, which was the actual source
  of the confusion.
- Rule of thumb: when a CLI's write target is described only by a
  relative suffix path (here `.brain/memory/incoming/...`) and more than
  one real, valid-looking absolute root could match it (a project-local
  mirror vs a machine-wide shared cache with an identical internal
  layout), confirm the ABSOLUTE path before writing, not just that the
  relative suffix matches instructions — and treat a "0 pushed, 0 held"
  (or any "nothing to do") success message from a sync/promote step as
  ambiguous rather than confirmatory: verify by checking `git status` in
  the actual expected source location for content you just wrote, since a
  correctly-reported empty sync and a silently-stranded write look
  identical from the tool's own output.
- Provenance (verified/assumed): verified first-hand — reproduced the
  exact "0 pushed, 0 held" result from the wrong location, confirmed the
  three files as untracked via `git status --short` in the cache repo,
  moved them, and confirmed "3 pushed to main, 0 held" from the same
  `brain sync` command run again with no other change.
- Composed: N/A
- Link: session 7195397b-63a9-5efe-a80b-2792eaa6645e, "Brain mine brain for
  non bug lessons" task, prior to filing story-gated-auto-roster /
  procedural-single-file-game-architecture / cutscene-presentation-from-
  combat-data proposals
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E43 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E5 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-10-08 · projects/pappydapimp69__brain.md#E95 · compatible · sandboxes/2026-10-08__zero-count-groundtruth-check.py · observed RESULT: PASS of 3 failing worlds, naive trust flagged 0, source-count check flagged 3, directory comparison pinpointed 1 (prediction refuted for the directory comparison). · brain train pass 4

## E4 — story gated auto roster
- Date: 2026-07-18
- Project: pappydapimp69/draft
- Tags: [gamedesign][state]
- What: Party composition is driven entirely by story progression, never by an
  upfront player-chosen roster. A single `storyIdx` counter (advanced by
  clearing bosses) gates both which fighters can be recruited and which bosses
  are even present on the map; recruits are found on specific maps
  (`recruits:[{x,y,fid,intro}]`) or auto-join at a scripted `storyIdx` (Vegeta
  joins automatically once `storyIdx===5`). Party is capped at 3: two
  permanent core members (Goku, Gohan) plus one rotating "support" slot filled
  by whichever other recruit the player picked up most recently.
- Why built: explicit user request — "The game should not let the player
  select their team at the start. It should follow the story. New party
  members are added automatically as the story advances or found on the map."
  The alternative (a pick-3-from-the-full-roster screen before playing) is the
  genre-default and was deliberately rejected.
- Design: `storyIdx` is the single source of truth for BOTH roster unlocks and
  boss availability, so the two can never drift out of sync (can't fight
  Vegeta before he's a possible ally, can't recruit Piccolo after his boss
  fight if that's supposed to gate him). Recruitment is a map-trigger side
  effect (`recruitMember(fid)`), not a menu choice.
- Got right: guarantees narrative coherence for free — there is no code path
  where the fiction and the mechanical unlock state disagree, because they
  read the same counter. Removes an entire pre-game screen (stat comparison,
  team theorycrafting) that has nothing to do with the story and that a
  frequent first-time-player complaint in this genre is confusing/overwhelming.
- Where/why it failed: this is a deliberate tradeoff, not a bug — but the real
  cost surfaced during build: the player loses "build your team before you
  start" agency entirely, and the rotating single support slot means an early
  recruit (e.g., Krillin, picked up in the first hour) is mechanically retired
  the moment a later recruit takes the slot, with no in-fiction reason given
  for WHY that character stopped fighting — it just silently drops out of the
  active three.
- Fix: kept the core (Goku+Gohan) permanent so the two most narratively
  central fighters are never benched, and constrained the rotation to a single
  slot instead of exposing full squad management — the tradeoff is accepted
  deliberately rather than solved (a bench/swap-back UI was explicitly out of
  scope for this request).
- Why this fix: matches the explicit ask (story drives the party, not the
  player) while bounding the downside to "one character rotates," not "your
  whole strategy resets every recruit."
- Rule of thumb: when a request says "the story should choose X, not the
  player," find ONE state variable that already tracks story progress and gate
  every related unlock off that same variable — never introduce a second
  counter/flag for a mechanically-adjacent system (roster, shop unlocks, map
  access), or the two will eventually disagree.
- Provenance (verified/assumed): verified first-hand — implemented and
  headless-tested across the full 18-map story arc (Playwright run confirmed
  recruits appear/lock as expected, Vegeta auto-joins at the scripted index,
  and no boss was reachable before its story gate). The "feels like a real
  cost" framing of the rotating-slot tradeoff is a design judgment, not a
  measured player-behavior finding — no real players have played this build.
- Composed: N/A
- Link: session 7195397b-63a9-5efe-a80b-2792eaa6645e, commit 55b02fa
  "Story-driven roster, crit-only cut-scenes, single-enemy auto-target"
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E14 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-10-15 · projects/pappydapimp69__zanegpt.md#E13 · compatible · sandboxes/2026-10-15__rhyme-letter-scope-per-section-type-keeps-chorus-repeats-linked-without-cross-verse-false-links.py · observed RESULT: PASS global table false links 6 (missed 0); per-instance reset missed 8 chorus links and 42 printed look-alikes; per-section-type scope 0 false / 0 missed (look-alikes 34). · brain train auto run 2 pass 2 (edge); session_01Hecxxt7Wfrejc8A3YVX1ht

## E3 — procedural single file game architecture
- Date: 2026-07-18
- Project: pappydapimp69/draft
- Tags: [gamedesign][architecture]
- What: The entire game (18 maps, all character/enemy/NPC sprites, cut-scene
  animation, and a full multi-layer background-music + ambiance + SFX engine)
  is procedurally generated at runtime from a single self-contained HTML file
  with zero external assets — sprites are canvas-drawn primitives dispatched
  through a spec table (`drawChar`→`drawHuman`/bespoke drawers), music is
  synthesized via Web Audio (oscillator voices, a look-ahead scheduler,
  deterministic per-theme melody generation), no images/audio files, no
  bundler, no CDN.
- Why built: the deployment target is a static GitHub Pages site serving one
  `index.html`, and the project's constraints favor zero build step, no binary
  asset pipeline, and CSP-safety (no inline-image/audio blobs, no third-party
  asset hosting). Procedural generation was the only way to hit "at least 15
  maps, all different environments" plus full music/SFX without authoring or
  sourcing dozens of art/audio assets by hand.
- Design: A small set of parametric building blocks (per-environment palette
  table `ENVS`, a grid generator `mkGrid`, a sprite-spec dispatcher, a
  deterministic melody generator seeded per theme name) is combined
  combinatorially — 18 distinct maps and 12+ enemy sprite types come from
  maybe a dozen actual drawing/generation functions, not 18+12 hand-authored
  assets.
- Got right: zero asset-loading failures, zero CDN/CSP issues, instant
  portability (the whole game is one file, verified to run headless via
  Playwright with no network dependency), and adding a new environment/enemy
  is a data-table entry (new `ENVS` key, new sprite spec) rather than new
  binary assets to source, license, and ship.
- Where/why it failed: the real, felt tradeoff (not a bug): procedurally-drawn
  content is visually/aurally simpler than authored art or recorded music, and
  every piece of "visual richness" (e.g., legible terrain, distinguishable
  sprites) has to be re-earned in code rather than by an artist iterating in an
  image tool — this session's own follow-up complaint ("rocks blend into
  grass") was a direct consequence: an emoji glyph's color is not something the
  developer controls, unlike a hand-authored sprite's palette.
- Fix: kept the constraint (no external assets) but added a data-driven escape
  hatch — an `_ENVKIND` table lets specific environments opt out of the
  generic emoji-glyph renderer and use bespoke canvas-drawn primitives
  (`drawRockTile`, `drawTreeTile`) wherever contrast/legibility actually
  matters, while environments where the generic emoji render was already fine
  keep it. The constraint (procedural, single-file) was never relaxed;
  quality was recovered by adding a second procedural renderer, not by adding
  an asset.
- Why this fix: preserves every benefit of the zero-asset architecture
  (portability, CSP-safety, no asset pipeline) while addressing the actual
  complaint (contrast), because the fix is still 100% code — no image was
  added to the repo.
- Rule of thumb: choosing "procedurally generate everything" over "author/
  source assets" trades content richness for portability/CSP-safety/zero
  build-step — budget for a per-category escape hatch (a table that lets a
  specific case opt into a bespoke procedural renderer) rather than assuming
  the generic procedural approach will look acceptable everywhere; the
  categories that most need the escape hatch are the ones humans use for
  spatial/gameplay-critical judgment (walkable vs blocked terrain), not
  decorative flourishes.
- Provenance (verified/assumed): verified first-hand across this session — the
  zero-asset build was deployed and confirmed running via GitHub Pages +
  headless Playwright screenshots at every stage; the contrast failure and its
  fix were both directly observed (user-supplied screenshot showing the
  problem, then a follow-up headless screenshot confirming the fix).
- Composed: N/A
- Link: session 7195397b-63a9-5efe-a80b-2792eaa6645e, commits af6cfb2 "New
  multi-layer music engine + expand world to 17 environments" and 0324f54
  "Draw rocks and trees as canvas terrain so they contrast with grass"
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E30 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E2 — cutscene presentation from combat data
- Date: 2026-07-18
- Project: pappydapimp69/draft
- Tags: [gamedesign][state]
- What: Critical-hit cut-scene presentation (a lunging melee impact vs a fired
  ki beam) is derived from one existing combat-balance field, `move.beam`
  (`physical = !move.beam`), rather than introducing a separate
  presentation-only field (e.g. `cutsceneType`) on each move.
- Why built: user feedback specifically distinguished the two on narrative/
  visual grounds ("A critical rush cut scene should be physical attacks, not
  ki attacks") — Rush is a melee move and was incorrectly playing a beam
  animation because the original cut-scene code didn't branch on move type at
  all.
- Design: every move already carries `beam` for cost/animation/hit-VFX
  purposes during normal (non-crit) resolution; the crit cut-scene branch was
  written to reuse that same field as its sole presentation switch instead of
  adding new data.
- Got right: zero risk of the two systems (balance data vs cut-scene
  presentation) drifting apart — a move's beam-ness cannot silently disagree
  with its cut-scene type, because there is only one flag, checked in one
  place, at both call sites.
- Where/why it failed: the tradeoff (not a bug): this couples two concerns
  that are conceptually independent — combat balance/cost semantics and
  camera/animation presentation. A future move that is mechanically "ki-costed"
  (drains the ki pool, so `beam:true` for cost purposes) but should read as a
  physical strike on-screen (or vice versa) has no way to express that without
  either lying about its own `beam` flag (breaking cost/VFX elsewhere) or
  re-introducing the exact per-move duplication this design avoided.
- Fix: none needed yet — every move authored so far has beam-ness and
  cut-scene-physicality in agreement, so the coupling has not yet produced a
  wrong result. Left as a known, accepted constraint rather than pre-building
  a second field for a case that doesn't exist in the current move roster.
- Why this fix: adding a speculative `cutsceneType` field for zero current
  moves that need it would be exactly the kind of premature abstraction this
  project avoids; the actual failure mode (a future move needing the two to
  diverge) is cheap to fix later by introducing an optional override field
  read as `move.cutscenePhysical ?? !move.beam` at that point.
- Rule of thumb: when two systems (balance data, presentation) can both be
  driven off one existing boolean and every current instance agrees, reuse the
  flag rather than mint a parallel field — but note explicitly (in a comment or
  a lesson like this one) that the two are coupled, so the day a new instance
  needs them to disagree, the fix is a fallback-defaulted override field, not a
  full field rename/migration.
- Provenance (verified/assumed): verified first-hand — before the fix, Rush
  (a physical move) was directly observed (via cut-scene review, per user
  report) playing the beam-fire animation; after the fix, headless verification
  confirmed physical moves trigger the lunge/impact branch and ki moves trigger
  the beam branch, across the current move roster.
- Composed: N/A
- Link: session 7195397b-63a9-5efe-a80b-2792eaa6645e, commit 1c937fe
  "Critical cut-scene: physical (melee) for Rush, beam only for ki moves"
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E28 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E1 — js object literal key collision
- Date: 2026-07-15
- Project: pappydapimp69/draft
- Tags: [javascript][state][gamedev]
- What: A factory that builds a runtime "unit" from a static definition wrote `return { id, side, def, name:def.name, atk:def.atk, def:def.def, spd:def.spd, ... }` — intending `def` (shorthand) to store a reference to the whole definition object AND `def:def.def` to store the scalar defense stat under the same key. The later key silently overwrote the shorthand, so `unit.def` held the defense number, not the definition — and it threw only on the one untested read path.
- Why built: Convenience: keep the source definition on the instance (for `unit.def.ai`, `unit.def.moves`, `unit.def.phase`) while also flattening the common stats (`atk`, `def`, `spd`) for the damage formula.
- Design: One object literal carrying both the reference and the derived scalar, under the same name.
- Got right: The scalar stat path was correct — `unit.def` really did hold the defense number, so `computeDamage(atk, tgt, move)` (which reads `tgt.def`) produced correct results, and every combat/damage test passed.
- Where/why it failed: In a JS object literal, later keys overwrite earlier ones with the SAME name. `def:def.def` (the number) clobbered the `def` shorthand (the object reference). So `unit.def` was the defense number, not the definition. Nothing broke until the ONE code path that read the object's other fields ran: the enemy-AI selector did `e.def.ai.length` → `number.ai` is `undefined` → `Cannot read properties of undefined (reading 'length')`. It threw on the first enemy turn only, killing the async turn chain and soft-locking the battle. Invisible to any test that touched only the scalar stat.
- Fix: Store the reference under a DISTINCT name: `src:def` for the definition, keep `def:def.def` for the scalar. Update the ~5 definition reads (`e.src.ai`, `e.src.moves`, `t.src.phase`, `e.src.regenPerTurn`).
- Why this fix: The collision was structural, not a typo — two conceptually different things (a reference and one of its fields) were given one name. Naming them apart removes the ambiguity at the source; no read site can pick the wrong one.
- Rule of thumb: When an object literal both spreads/shorthands a source AND sets a key derived from that source, never reuse the source's name for the derived value — the derived value wins and the reference vanishes. The failure is delayed and path-specific: it passes every test that reads only the scalar and throws only where the lost reference is dereferenced. Grep for a key that appears twice (once shorthand/spread, once computed) in the same literal.
- Provenance (verified/assumed): Verified first-hand — headless Playwright playthrough of the DBZ RPG build: the crash reproduced as a PAGEERROR on the first enemy turn (soft-lock, 0 further player turns); after renaming to `src`, a full four-saga autoplay completed to victory with 0 console/page errors across 200+ actions.
- Composed: sandbox-dbz-combat/E2, sandbox-dbz-combat/E4, sandbox-dbz-team-combat/E2, sandbox-combined-loop-combat/E1 — the same build also re-exercised these combat-design rules (Pareto-diverse moves, persistent binding ki, defense as pre-cap mitigation, floor-once-at-boundary) in one playable damage function; they held.
- Link: Pappydapimp69/Draft `index.html` (`mkUnit`), commit 9c758db
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E12 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-07-20 · projects/local__sandbox-validation-ladder-vs-key-collision.md#E1 · compatible · no sandbox · session (this conversation, "train brain on edges external research" — draft + test, the top untested pair); scratchpad `sandbox_validation_ladder_vs_key_collision.mjs`; external source: ESLint no-dupe-keys documentation and community-confirmed spread-operator limitation (eslint.org/docs/latest/rules/no-dupe-keys).
