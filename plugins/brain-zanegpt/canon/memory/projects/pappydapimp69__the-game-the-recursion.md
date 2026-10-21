# pappydapimp69/the-game-the-recursion — lessons

Project: pappydapimp69/the-game-the-recursion. Newest first.

---

## E21 — float order dependence is the mechanism behind exact integer choices
- Date: 2026-07-13
- Project: pappydapimp69/the-game-the-recursion
- Tags: [algorithm][determinism][gamedev]
- What: `brain train group` (untested seams extending the main cluster) surfaced pappydapimp69/the-game-the-recursion + pappydapimp69/the-game-wrong-sky (shared: determinism, gamedesign, gamedev, input, mobile, process, quest, saga, state, ui). Composed: projects/pappydapimp69__the-game-wrong-sky.md#E12 (a textbook algorithm you can't use as-is — binary + float shadowcasting — is not the default; a slower, purpose-built exact-integer FOV buys partial occlusion + determinism-safety, worth it when the working set is small) and projects/pappydapimp69__the-game-the-recursion.md#E6 (Delaunay triangulation + MST is the standard dungeon-connection algorithm, but a simpler all-pairs-distance + MST approach — cheaper, fully-deterministic, no-RNG — produces equivalent connectivity at small room counts and is the better choice there). Both projects independently rejected a "standard," floating-point-involving algorithm in favor of an exact/integer-safe, fully-deterministic alternative, citing determinism-safety as part of the reason, at a small enough working set that the standard algorithm's real advantage (precision/scale) doesn't matter. Built and ran a minimal deterministic sandbox verifying the underlying arithmetic MECHANISM that justifies both choices — not a reimplementation of shadowcasting or Delaunay triangulation themselves, but the specific property (float64 summation is evaluation-order-dependent; exact-integer summation is not) that both projects' design reasoning depends on.
- Why built: Neither the-game-wrong-sky#E12 nor the-game-the-recursion#E6 states WHY floating-point involvement threatens determinism in the first place — both simply assert "float" is a determinism risk and "exact-integer"/"fully-deterministic" is the fix, as a design conclusion. The sandbox checks whether that underlying premise is actually true in a minimal, isolated case, rather than trusting it because two experienced authors independently believed it.
- Design: `engine.mjs` sums a fixed 10-value list (`[1e16, 1, -1e16, 1, 1, 1, 1, 1, 1, 1]`, true sum = 7 by exact arithmetic) under three fixed evaluation orders (forward, reversed, small-magnitude-values-grouped-first — standing in for the kind of reordering a different data-structure traversal, engine, or optimization pass could plausibly introduce), once using JS `number` (float64) addition and once using an exact-integer reformulation (`BigInt` summation of the same values). No RNG anywhere; all three orders are fixed, hardcoded lists.
- Got right: The exact-integer reformulation is not merely "less risky" — it produced the IDENTICAL result (8) under all three evaluation orders, confirming integer addition's associativity holds in practice as well as in theory for this case, with zero extra tuning required.
- Where/why it failed: Float64 summation gave THREE DIFFERENT results depending purely on evaluation order — `forward: 7` (matches the true exact sum), `reversed: 8`, `smallFirst: 8` — despite every order summing the exact same multiset of values with no randomness involved anywhere. The divergence is a direct, textbook consequence of float64's ~15-17 significant-digit limit: adding `1` to `1e16` first (forward order, values 1-9) rounds each `+1` away against the`1e16` magnitude, so those additions are silently no-ops until the `-1e16` cancels back down to a small number; reordering so several `+1`s accumulate BEFORE encountering the large magnitude values preserves more of them.
- Fix: The exact-integer approach (scale + `BigInt` summation) is immune to this class of divergence by construction — integer addition is exactly associative on real hardware (no rounding step), confirmed by all three orders producing the identical result, giving concrete, minimal support for why both the-game-wrong-sky#E12 (exact-integer FOV) and the-game-the-recursion#E6 (fully-deterministic all-pairs+MST, explicit "no random draw," deterministic tie-breaking) reached for integer/exact reformulations specifically, not just "more careful" floating-point code.
- Why this fix: This sandbox does not re-verify the-game-wrong-sky#E12's actual shadowcasting implementation or the-game-the-recursion#E6's actual MST implementation — it verifies the general arithmetic property both design decisions are premised on, isolated to its simplest form. The value is confirming that premise is not folklore: float64 summation order-dependence is real, measurable, and reproducible with an ordinary, non-adversarially-constructed value set (large-magnitude values interleaved with unit increments is a completely plausible real scenario — accumulated distances, opacity/visibility contributions, or edge weights spanning several orders of magnitude), and exact-integer reformulation genuinely eliminates it rather than just reducing its likelihood.
- Rule of thumb: When a design choice cites "float precision/order-dependence is a determinism risk" as justification for picking a simpler or exact-integer algorithm over a textbook floating-point one (as both the-game-wrong-sky#E12 and the-game-the-recursion#E6 independently did), that justification rests on a verifiable, not merely folklore, property — float64 summation is order-dependent for any value set spanning enough orders of magnitude, and an exact-integer reformulation removes the risk entirely rather than shrinking it; this is worth a quick isolated check (as this sandbox does) rather than taking on faith, since the alternative (exact-integer/simpler-deterministic) usually costs real implementation effort or lost precision that should be justified by more than reputation.
- Provenance (verified/assumed): VERIFIED first-hand for the underlying arithmetic mechanism — built `engine.mjs` (zero RNG, three fixed evaluation orders), confirmed float64 summation gives 3 different results (7, 8, 8) across the 3 orders for an ordinary large-magnitude-interleaved-with-small value set, and exact-integer (BigInt) summation of the identical values gives the same result (8) under all 3 orders. Confirmed deterministic/reproducible across two independent process invocations of `node engine.mjs`, output diffed byte-identical. Scope limit, stated plainly: whether the-game-wrong-sky#E12's actual shadowcasting code and the-game-the-recursion#E6's actual MST code exhibit this exact failure mode in their real implementations remains an open question this sandbox does not settle — it verifies the general mechanism their stated reasoning depends on, not their specific code paths.
- Link: session 01KxkbJUq8YajH8GokSZYYHy; `brain train group` seam (the-game-the-recursion + the-game-wrong-sky); sandbox `engine.mjs`, scratchpad `sandbox-float-vs-integer-determinism/` (run twice as separate process invocations, outputs diffed byte-identical)
- Cited-by: 2026-10-10 · projects/local__sandbox-numerics-kahan-order.md#E1 · compatible · sandboxes/2026-10-10__kahan-vs-naive-vs-neumaier-order-and-2p53.py · observed RESULT: PASS 0.1x1e6 naive err 1.33e-06 kahan 5.55e-12; 2^53+1000 ones naive lost 1000 kahan err 0; order results naive 3 kahan 2 neumaier 2 (spread naive 239 kahan 4.65); adversarial kahan 0.0 vs neumaier 2.0 · scheduled brain train auto loop 2 pass 5 (gap); session_01PQ4jLSc8kGvXwYbpjoS24m
- Cited-by: 2026-10-09 · projects/local__brain-train.md#E1 · compatible · sandboxes/2026-10-09__round-robin-dealing-vs-hash-modulo-balance-vs-stability.py · observed RESULT: PASS round-robin spread<=1 in 200/200 vs modulo median 7 worst 15 at N=42; add-one moves modulo 0% vs rr 53%; K 6->7 moves 86%/86%; 9/9 checks. Relative spread 1.00 / 0.30 / 0.10 at N=42/420/4200; remove-one moves 0 vs 50 percent;… · brain train gap pass 5 (2026-10-09); sandbox 2026-10-09__round-robin-dealing-vs-hash-modulo-balance-vs-stability.py; session_01YFLLRpDsfZpRstb2KT2MQy

## E20 — the game the recursion pinned compounding formula needs canonical order
- Date: 2026-07-13
- Project: pappydapimp69/the-game-the-recursion
- Tags: [determinism][architecture][state]
- What: Composing `sandbox-power-scaling#E1` (float64 loses exact-safe-integer representability after ~21 compounding multiplicative "arc jump" events at a representative multiplier, mattering for equality/hashing/diffing though true overflow is unreachable) with `the-game-the-recursion#E17` (a value that gates a reducer transition must be pinned in privileged state, never re-derived from the command's own payload) found E17's rule is necessary but not sufficient once the pinned value is itself a compounding power-scaling-style formula: two logically-equivalent, equally state-derived computation paths (live-sequential accumulation vs. a batch/replay/fold reconstruction a save-reload or fast-forward feature would plausibly use) are NOT guaranteed bit-identical under float64, because multiplication isn't associative under rounding — and this produces two distinct failure tiers at two very different arc-counts, with E1's own safe-integer crossover number serving as a legitimate predictor of the more serious tier.
- Why built: `brain train edge` surfaced `sandbox-power-scaling + the-game-the-recursion` as an untested seam requiring sandbox/live-code verification, not just reasoning, per current policy (tension T22). Deliberately tested a new angle distinct from the two prior recursion compositions this session (E18's staleness/invalidation angle, E19's source-trust angle) — this one is about computation-ORDER equivalence of an already-correctly-pinned, already-correctly-state-sourced value.
- Design: Deterministic Node.js sandbox (mulberry32 seeded, no wall-clock/Math.random) simulating a recursion-style `learningIdx >= threshold` gate where `threshold` is a power-scaling-style compounding product of 1-40 arc multipliers (range 1.1x-6x, matching sandbox-power-scaling#E1's own canon range), computed four logically-equivalent ways: live-sequential (ground truth, "what actually happened" during play), right-to-left fold, split-half combine, and log-sum-exp reconstruction. Measured, per arc-count across 5 seeds: bit-exact agreement between paths, whether the gate's boolean decision flips for the exact `learningIdx` a live player would have just reached, and whether a JSON-stringify golden-fingerprint (matching recursion's own `scripts/smoke.mjs` pattern) matches across paths.
- Got right: Distinguished two separate consequences (fingerprint-string mismatch vs. actual gate-boolean flip) rather than conflating "the hash changed" with "the game behaved differently" — the two have very different onset points and severities. Cloned the real repo and grepped `src/sim/reduce.js` before concluding anything about live risk, confirming current gate thresholds (`totalChoicePoints`, `depthQuotas`) are plain integer counts derived once at construction, not compounding float formulas — ruling out a live bug rather than assuming one from the sandbox result alone.
- Where/why it failed: Pure multiplication reordering (no log/exp involved) produced a bit-different float64 value as early as arc-count n=2 (seed 1), which would already break an exact-string golden-fingerprint regression test (recursion's own E14/E16 `smoke.mjs` pattern) long before anyone would suspect a problem — a low-severity but immediate cosmetic risk. The actual privileged-gate-flip risk (a real gameplay-correctness bug, not just a hash mismatch) is far more severe when it occurs but onsets much later, close to sandbox-power-scaling#E1's own headline safe-integer crossover: 23-29 arcs across the 5 seeds tested here (vs. E1's own ~21 at a similar multiplier), tracking E1's crossover within a few arcs in every seed. Sample case (seed 1, n=28 arcs): the identical logical player state (`probeIdx=2445204497691851`) evaluated the gate as `true` via live-sequential accumulation and `false` via split-half combine.
- Fix: Not applied (no live bug exists in current shipping code, per the confirmed grep of `src/sim/reduce.js` — this is a forward-looking architectural caution). If a future power-scaling-style compounding stat is ever fed into a recursion-style privileged gate, pinning it in state (E17) must additionally specify ONE canonical, reproducible computation order that every code path (live play, save-reload, undo/redo, fast-forward replay) is required to use identically — not merely "arrive at the same mathematical answer" via whatever order is locally convenient.
- Why this fix: Below the safe-integer boundary, reordering-induced float noise is far smaller than 1 unit — invisible to an integer gate comparison even though it already breaks exact-string serialization. Past the boundary, the noise becomes comparable to the gap between adjacent representable integers, so a `>=` comparison against an integer sitting exactly at the threshold can legitimately flip depending on which "equally trusted" (per E17) code path computed the pinned value.
- Rule of thumb: E17's "pin in state, not command payload" rule constrains WHERE a gate value comes from but says nothing about HOW it was computed when that value is a compounding/power-scaling-style formula output. Two code paths that both correctly satisfy E17 (both pull from state, neither trusts a command payload) can still diverge from each other due to float non-associativity. Treat this as low-severity cosmetic risk (fingerprint-test noise) below roughly the safe-integer crossover for your multiplier range (sandbox-power-scaling#E1's own number is a working predictor), and as a real behavioral-correctness risk at or beyond it — and require exactly one canonical accumulation order across every code path that can produce the pinned value, not just a single source-of-truth STATE LOCATION.
- Provenance (verified/assumed): VERIFIED first-hand — deterministic Node.js sandbox, mulberry32 seeded, 5 seeds x 40 arc-counts, measured bit-exact agreement, fingerprint-string agreement, and actual gate-boolean agreement across 4 logically-equivalent computation paths, finding fingerprint divergence as early as arc 2 and gate-flip divergence at arcs 23-29 (tracking E1's own ~21-arc safe-integer crossover). Additionally cloned the real `pappydapimp69/the-game-the-recursion` repo and grepped `src/sim/reduce.js` directly, confirming NO live bug currently exists (current gate thresholds are plain integer counts, not compounding float formulas) — this entry is a verified forward-looking architectural caution, not a claim of live-unfixed shipping behavior.
- Composed: sandbox-power-scaling/E1, the-game-the-recursion/E17
- Link: session (brain train 3 groups + 2 edges, sandboxed until satisfied, loop 3), sandbox script seam-precision-gate.mjs, live grep of src/sim/reduce.js confirming no current live bug, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-loop-combat.md#E2 · compatible · no sandbox · session (query brain for "loop: aim, compose from recorded lessons, sandbox, file" — loop 5), sandbox scripts reverify5_quantize_scaling.mjs/reverify5b.mjs, no code change to a shipping project
- Cited-by: 2026-09-28 · projects/local__sandbox-kernel-system-determinism.md#E6 · compatible · sandboxes/2026-09-28__train-gap-b04.py · session 2026-09-28, brain train gap batch 4 loop 19
- Cited-by: 2026-07-20 · projects/local__sandbox-rng-determinism-not-sufficient-for-replay.md#E1 · compatible · no sandbox · session (this conversation, "Continue" — test + the-game-the-recursion, the top untested pair); scratchpad `sandbox_rng_determinism_not_sufficient_for_replay.mjs`.

## E19 — the game the recursion trust source not value type
- Date: 2026-07-13
- Project: pappydapimp69/the-game-the-recursion
- Tags: [architecture][state][security]
- What: Composing `sandbox-astar-replan#E2` ("trust the agent's live position unconditionally, never re-validate it against occupancy") with `the-game-the-recursion#E2`/`E17` ("never trust a gate's threshold when it's supplied by the same command trying to cross the gate") looked, on first read, like a direct contradiction — one says trust a value unconditionally, the other says never trust a value. Sandbox testing showed they are NOT in tension: both are the same rule ("trust values fixed by state a process maintains independently of the current command; never trust a value the current command's own payload supplies") applied to two values that happen to sit on opposite sides of that line by ACCIDENT of which project built them, not because "positions" and "thresholds" are inherently different trust classes.
- Why built: `brain train edge` surfaced `sandbox-astar-replan + the-game-the-recursion` as an untested seam requiring sandbox verification (tension T22); the apparent surface contradiction between "trust unconditionally" and "never trust" made this worth resolving with real code rather than leaving as an unstated tension.
- Design: A self-contained BFS-pathfinding + reducer sandbox with three scenarios. Scenario A replays astar-replan#E2 (a hazard closes the agent's own cell; trusting authoritative-state position lets replanning succeed, a strict start-occupancy check incorrectly freezes it). Scenario B replays recursion#E2 (a command-payload-sourced gate threshold is bypassed by a bare param-less command; a state-held threshold isn't). Scenario C is the novel cross-test: a `TELEPORT_REPLAN` command carries a CALLER-SUPPLIED start position — the same value TYPE Scenario A says to trust unconditionally, but sourced the way Scenario B says never to trust (from the current command's own payload).
- Got right: Scenario C is the load-bearing test — it deliberately takes the exact value class (position) that Scenario A's rule says is safe to trust, and changes only its SOURCE (state-maintained vs. command-payload-supplied) to see whether the "trust positions" instinct still holds or whether it was actually source-dependent all along, not type-dependent.
- Where/why it failed: Naively applying astar-replan#E2's "trust the start unconditionally" rule to a command-payload-sourced position (rather than the authoritative-state-sourced position the original lesson was actually about) produces a real exploit: an attacker-claimed start position inside solid, fully-sealed wall geometry, with the pathfinder returning a computed 3-cell "path" walking the agent out of the wall. The rule "trust positions" is a coincidentally-correct special case of the real rule, not a general truth about the value type — it happened to be correct in astar-replan's original context only because the position there was ALSO state-maintained, not because positions in general are trustworthy.
- Fix: Validate any command-payload-sourced value that gates or roots a privileged operation (a start position for replanning, a threshold for a stage gate, or any other privileged input) against independent authoritative state before trusting it — applying recursion's actual general fix (validate command-supplied values), not the narrower literal fix ("thresholds specifically need checking") to a position, correctly rejects the wall-clip exploit (`rejected: 'illegitimate-claimed-start'`) while still leaving astar-replan#E2's own original scenario (a genuinely state-maintained position) working correctly.
- Why this fix: The two source lessons each stated a correct fix for their own specific case, but neither stated the general principle that would tell a future engineer which of the two rules applies to a NEW value they're adding — "is this a position or a threshold" is the wrong question; "does this command's own payload supply or influence this value, or is it fixed by state the process maintains independently of this command" is the right one, and it resolves both existing lessons and predicts the new exploit correctly.
- Rule of thumb: When two recorded lessons about trusting/not-trusting a value appear contradictory, check whether they're actually both instances of a single rule keyed on VALUE SOURCE (state-maintained vs. command-payload-supplied) rather than VALUE TYPE (position, threshold, or otherwise) — a "trust this unconditionally" lesson from one context can become a real vulnerability the moment the same value TYPE is re-sourced from a command payload in a different context, so a general architecture rule needs to be stated in terms of source/provenance, not surface value category, or it will mislead the next engineer who encounters the same type in a different circumstance.
- Provenance (verified/assumed): VERIFIED first-hand — built and ran a deterministic Node.js sandbox (no RNG, no wall-clock) implementing all three scenarios against one shared BFS-pathfinding + reducer system, confirming astar-replan#E2's original behavior (Scenario A, PASS), recursion#E2's original behavior (Scenario B, PASS), and the novel cross-case (Scenario C): the naive type-based rule produces a real wall-clip exploit (`naiveExploitSucceeded: true`, path length 3) while the source-based rule correctly rejects it (`fixedRejected: true`) — exit code 0, all three scenarios behaved as predicted.
- Composed: sandbox-astar-replan/E2, the-game-the-recursion/E17
- Link: session (brain train 3 groups + 2 edges, sandboxed until satisfied), sandbox script seam.js, no code change to a shipping project
- Cited-by: 2026-09-28 · projects/local__sandbox-kernel-system-architecture.md#E5 · compatible · sandboxes/2026-09-28__train-gap-b10.py · session 2026-09-28, brain train gap batch 10 loop 50
- Cited-by: 2026-07-17 · projects/pappydapimp69__garden.md#E2 · compatible · no sandbox · this session (Garden audit); `supabase/functions/vision-proxy/index.ts`, `src/vision/client.js` (`_callProxy`, `payload`)
- Cited-by: 2026-07-17 · projects/pappydapimp69__garden.md#E3 · compatible · no sandbox · this session (Garden audit); `supabase/functions/vision-proxy/index.ts`, `SCHEMA.sql` (vision_api_calls)

## E18 — the game the recursion pinned gate value needs invalidation hook
- Date: 2026-07-13
- Project: pappydapimp69/the-game-the-recursion
- Tags: [determinism][architecture][state]
- What: Composing `sandbox-combined-skilltree-formula#E3` (a value derived from a live formula, cached/pinned at one moment, silently goes stale when a formula INPUT changes for a reason unrelated to the read path — unless an explicit eager invalidation hook fires at the input's own change event) with `the-game-the-recursion#E2`/`E17` (a reducer gate threshold must be pinned in privileged state before the gated command, never re-suppliable through that command) surfaced a genuine gap neither source lesson states alone: pinning a gate value ONCE (recursion's fix) defeats the command-supplied-bypass bug, but if that pinned value is ITSELF a live-formula output (a skilltree#E3-style capacity/threshold), pinning it once without an invalidation hook silently reintroduces skilltree#E3's exact staleness bug — the gate keeps enforcing an outdated threshold after a legitimate, unrelated formula-input change (e.g. a difficulty setting), until something explicitly re-pins it.
- Why built: `brain train group` surfaced `sandbox-combined-skilltree-formula + the-game-the-recursion` as an untested seam requiring sandbox verification, not just reasoning, per the current policy (tension T22).
- Design: A toy `command -> reduce -> gate` reducer (matching recursion's own architecture) gates `ADVANCE_SPINE` on `learningIdx >= threshold`, where `threshold = evalExpr('base*difficultyMult', vars)` (a skilltree-style expr formula). Three gate modes tested: `command-supplied` (recursion's original E2 bug, a sanity-check baseline), `pinned-once` (recursion's fix as literally stated), and `pinned-with-invalidation` (recursion's fix plus skilltree#E3's eager re-pin hook, fired on a separate `SET_DIFFICULTY` command). A deterministic 48-trial sweep (6 base values x 8 old->new difficultyMult pairs) ran all three modes.
- Got right: Included the baseline sanity check (Test A, reproducing recursion's own already-known E2 bug in this harness) before testing anything new, confirming the harness itself was faithful — and Test D confirmed the invalidation-hook fix closes the staleness gap WITHOUT reopening the original command-supplied-bypass hole (a bare/decoy-payload `ADVANCE_SPINE` still used the state-held threshold, `stillBlockedDespitePayload: true`), ruling out a fix that solves one bug by reintroducing the other.
- Where/why it failed: Under `pinned-once`, the threshold was correctly resistant to command-supplied bypass but became stale the moment a LEGITIMATE, unrelated command (`SET_DIFFICULTY`) changed the formula input it was derived from — the gate kept using the old (now too-low) threshold and incorrectly allowed the transition. This is not a rare edge case: the deterministic sweep found the stale-threshold bug present in 48/48 trials under `pinned-once`, and absent in 48/48 trials under `pinned-with-invalidation`.
- Fix: Add an eager invalidation hook that re-pins the gate's cached threshold at the moment its formula's input actually changes (fired by the input-changing command, e.g. `SET_DIFFICULTY`), rather than only pinning once at construction and never touching it again.
- Why this fix: "Pin once, never touch again" and "always live-re-derive" are both wrong in different ways (the former goes stale, the latter reopens the command-supplied-bypass bug recursion#E2 was built to close) — the correct rule is pin-and-explicitly-invalidate-on-the-actual-change-event, matching skilltree#E3's own fix pattern, applied here to a gate threshold instead of a resource-pool capacity.
- Rule of thumb: When a value pinned in privileged reducer state (to defeat a command-supplied-bypass bug) is itself derived from a live formula/computation over OTHER state, "pin once at construction" is necessary but not sufficient — it must also be explicitly re-pinned at the moment any of its formula's real inputs legitimately change, via an eager invalidation hook fired by whatever command changes that input, or the pinned value silently drifts stale exactly as an un-invalidated cache would. This generalizes beyond gate thresholds to any privileged-state value whose "correct" value is itself formula-derived (difficulty scalars, resource capacities, damage multipliers).
- Provenance (verified/assumed): VERIFIED first-hand — built and ran a deterministic Node.js sandbox (no RNG, no wall-clock) implementing all three gate modes against the same toy reducer, confirming the baseline bug (Test A), the fix working as documented (Test B), the new staleness bug under pin-once (Test C, `advanceAllowed: true` three choice-points early), the invalidation-hook fix closing it without reopening the bypass (Test D), and a 48-trial deterministic sweep confirming the bug is present 48/48 under `pinned-once` and absent 48/48 under `pinned-with-invalidation` (Test E) — not a coincidence of one parameter choice.
- Composed: sandbox-combined-skilltree-formula/E3, sandbox-combined-skilltree-formula/E6, the-game-the-recursion/E17
- Link: session (brain train 3 groups + 2 edges, sandboxed until satisfied), sandbox script seam.mjs, no code change to a shipping project
- Cited-by: 2026-09-28 · projects/local__sandbox-kernel-system-architecture.md#E3 · compatible · sandboxes/2026-09-28__train-gap-b09.py · session 2026-09-28, brain train gap batch 9 loop 45

## E17 — the game the recursion gate and perturbation params must precede the command
- Date: 2026-07-13
- Project: pappydapimp69/the-game-the-recursion
- Tags: [gamedev][state][determinism]
- What: `the-game-the-waiting-city#E9` (AI decisions must live inside the authoritative reducer, with every decision consuming a CONSTANT number of RNG rolls so a later content change can't retroactively re-perturb unrelated entities sharing a tick) and `the-game-the-recursion#E2` (a stage-advance gate must never read its threshold from the SAME command trying to cross it, since the command can simply omit or vary that value) are independently-derived instances of the same higher-order rule, arrived at from two different bugs in two different sibling projects: any value that GATES or PERTURBS authoritative reducer behavior must be fixed in state BEFORE the command that depends on it is dispatched — never supplied by, or made variable through, that command's own payload or its incidental side effects.
- Why built: `brain train group` surfaced `the-game-the-recursion + the-game-the-waiting-city` as an untested seam; reading both projects' determinism-architecture entries for overlap revealed they'd each rediscovered the same abstraction from opposite specific failure shapes (a security-style gate bypass vs. a determinism/RNG-drift risk) without either entry naming the shared principle explicitly.
- Design: N/A — a recorded-lessons synthesis, not a new build.
- Got right: Recognized these as the SAME rule despite very different surface bugs (waiting-city#E9's is about drift risk from content changes shifting RNG roll counts; recursion#E2's is about an outright security-style bypass from an omittable command param) — the common shape is "a command carries or influences a value the reducer trusts to gate/perturb outcomes, and that value's source is the same untrusted command instead of privileged prior state."
- Where/why it failed: Neither entry alone states the general principle — waiting-city#E9 frames its discipline as "the determinism tax" specific to AI/RNG, and recursion#E2 frames its fix as specific to gate thresholds. Read separately, a future session designing a new reducer command has no single rule of thumb pointing at BOTH classes of bug; read together, the abstraction is obvious and reusable beyond either specific case (e.g., a damage multiplier, a difficulty scalar, a spawn count — anything a command could smuggle in that the reducer treats as authoritative).
- Fix: Not applicable — this entry's contribution is naming the shared abstraction, not patching either project (both already fixed their own specific instance).
- Why this fix: A no-op field here is itself informative: both source projects independently converged on fixes that satisfy the general rule (waiting-city#E9's constant-roll-count moves the perturbing value's determinism into privileged sim state; recursion#E2's threshold-in-prior-state moves the gating value out of the command payload) WITHOUT either project's author stating the general principle explicitly — meaning the abstraction was correct engineering instinct twice before it was ever named. Naming it now is the entire value of this entry: a future reducer-command author gets the rule stated once, instead of having to independently re-derive it a third time from a third bug.
- Rule of thumb: In a `command -> reduce -> events` architecture, before trusting any value a command reads to gate a transition or perturb an outcome (a threshold, a roll count, a multiplier, anything read inside the reducer's handling of that command), ask where that value originates — if it's part of the command's own payload, or if it can silently vary based on incidental caller-side state (like content changes altering which branch runs and therefore how many RNG draws happen), it is NOT safe as a gate/perturbation input. The value must be fixed in world/entity state BEFORE the gated or perturbing command exists, established at a privileged, one-time moment (construction, a prior tick, an earlier authoritative event) the gated command cannot itself influence.
- Provenance (verified/assumed): VERIFIED first-hand — both source entries (waiting-city#E9, recursion#E2) read directly; the shared-abstraction synthesis is new reasoning in this session, not independently re-derived against either project's live source beyond what the entries themselves already verified.
- Composed: the-game-the-waiting-city/E9, the-game-the-recursion/E2
- Link: session (brain train on groups and test 5 new edges), no code change — a recorded-lessons synthesis
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-seed-drawstream.md#E1 · compatible · no sandbox · this session's sandbox (sb2_drawstream.py); source entries the-game-the-recursion#E17 and dog#E12.
- Cited-by: 2026-09-28 · projects/local__sandbox-kernel-system-architecture.md#E1 · compatible · sandboxes/2026-09-28__train-gap-b04.py · session 2026-09-28, brain train gap batch 4 loop 18
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-the-recursion.md#E18 · compatible · no sandbox · session (brain train 3 groups + 2 edges, sandboxed until satisfied), sandbox script seam.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-the-recursion.md#E19 · compatible · no sandbox · session (brain train 3 groups + 2 edges, sandboxed until satisfied), sandbox script seam.js, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-the-recursion.md#E20 · compatible · no sandbox · session (brain train 3 groups + 2 edges, sandboxed until satisfied, loop 3), sandbox script seam-precision-gate.mjs, live grep of src/sim/reduce.js confirming no current live bug, no code change to a shipping project

## E16 — the game the recursion framerate dependent step cadence
- Date: 2026-07-13
- Project: pappydapimp69/the-game-the-recursion
- Tags: [determinism][gamedev][state]
- What: Composed `sandbox-combined-game-loop#E2` (a fixed-timestep/cadence accumulator driven by a raw float `dt` produces a different discrete-transition count across frame-rate schedules covering the same total time) against `src/app/explore.js`'s ACTUAL live movement logic (`stepCd -= dtMs; if (stepCd <= 0) { move; stepCd = STEP_MS }`, `STEP_MS = 108`, `dtMs` sourced from `main.js`'s `Math.min(nowMs - prevMs, 50)` — a raw wall-clock float, not a fixed/integer time source). Faithfully reproducing this exact logic and stress-testing it per E2's methodology (same total held-direction duration, different frame-rate schedules) found the predicted divergence, and at a magnitude far larger than E2's original ±1-tick finding: holding a direction for 60 real seconds produces 515 moves at 60fps, 540 at 144fps, and only 450 at 30fps — a ~20% difference in effective movement speed between a 30fps and a 144fps player for the identical real-world input duration. `scripts/smoke.mjs` (this project's own fingerprint/determinism regression suite) never calls `explore.update()` at all, so this path is currently completely unverified by the project's existing tests.
- Why built: `brain train combined` surfaced `sandbox-combined-game-loop + the-game-the-recursion` as an untested seam (architecture/determinism/gamedev/state/testing); unlike most seams tested this session, one side is a real shipped project's actual source rather than another sandbox, so this checked whether an already-verified sandbox failure mode reproduces in real production code rather than building a synthetic analog.
- Design: Extracted `STEP_MS = 108` and the exact `stepCd`-decrement/reset logic verbatim from `explore.js`, and the exact `dt` clamp (`Math.min(frameMs, 50)`) verbatim from `main.js`. Simulated a continuously-held direction for 5s/10s/30s/60s of total wall-clock time under steady 30/60/144fps schedules and a jittery 8-33ms-per-frame schedule (10 seeds), counting discrete move events.
- Got right: Testing multiple total durations (not just one) showed the divergence GROWS with duration (43 vs 46 vs 38 at 5s; 515 vs 540 vs 450 at 60s) — confirming this is a compounding per-cycle bias (each cycle "wastes" a framerate-dependent amount of overshoot below the `stepCd <= 0` threshold before resetting), not a one-off rounding fluke that would stay constant in absolute terms.
- Where/why it failed: At a lower frame rate, each frame's `dt` is larger, so when `stepCd` finally crosses below zero the average overshoot (how far past zero it lands before the check fires) is larger too — that overshoot is "wasted" time that doesn't count toward the next step's cooldown, so more real time elapses per move at low frame rates than at high ones. This compounds linearly with how long a direction is held, producing a real, monotonic, frame-rate-tied movement-speed advantage for higher-refresh-rate displays — not a rare edge case or a sub-millisecond rounding curiosity, but a live, currently-shipping player-fairness issue for any player whose input timing this loop gates, and it is invisible to the project's own determinism/regression suite because that suite exercises a different code path (`runDemo()`/world-state simulation) and never drives `explore.update()` across varying frame schedules.
- Fix: Not implemented — flagged as the finding, per this session's scope boundary of composing/diagnosing rather than patching other projects' shipping code without being asked. The direction sandbox-combined-game-loop#E2 already verified: drive `stepCd` from an integer/fixed-point time source with `STEP_MS` expressed as an exact integer count of base sub-units, so the drain comparison is exact and schedule-independent, rather than accumulating a raw float `dt`.
- Why this fix: N/A — diagnostic finding against a real project, not a verified patch to that project's code in this session.
- Rule of thumb: A cooldown/cadence timer gating discrete player-visible transitions (a movement step, an attack, an ability) that is decremented by a raw float per-frame `dt` will produce a real, compounding, frame-rate-dependent transition rate — this is not merely a determinism/replay-golden-test concern, it is a live gameplay-fairness bug once the cadence is short relative to typical frame time (STEP_MS=108ms against a 6-33ms frame range here) and the player holds input continuously. Before accepting a `cooldownMs -= dt` pattern in shipping input-gated movement code, stress-test it exactly the way this sandbox did: same total held-duration, multiple frame-rate schedules, compare discrete-event counts — a project's existing determinism suite testing a DIFFERENT code path (e.g. scripted world simulation) provides no coverage for this class of bug in a separate real-time input loop.
- Provenance (verified/assumed): VERIFIED first-hand — extracted and faithfully reproduced the exact constants and control flow from `src/app/explore.js` and `src/main.js` (STEP_MS=108, the real `dt` clamp expression), ran the reproduction across 4 total-duration values x 3 steady frame rates x 10 jittery-schedule seeds, directly counting discrete move events and confirming the magnitude grows with duration rather than staying flat.
- Composed: sandbox-combined-game-loop/E2, pappydapimp69/the-game-the-recursion (src/app/explore.js live code, not a prior memory entry)
- Link: session (brain train combinations), sandbox script test.mjs (verbatim-logic reproduction, no code change to the shipping project), constants/logic cross-checked directly against the-game-the-recursion's own src/app/explore.js and src/main.js at commit time of this session
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-cadence-frametick.md#E1 · compatible · no sandbox · this session's sandbox (sb1_cadence.py); source entries the-game-the-recursion#E16 and sandbox-combined-game-loop#E2.
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-dog-recursion-two-frame-rate-defects-one-symptom.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-realtime-loop.md#E1 · compatible · no sandbox · this session's sandbox (sbT.py); source entries sandbox-combined-game-loop#E2, the-game-the-recursion#E16, sandbox-dbz-combat#E1.
- Cited-by: 2026-09-28 · projects/local__sandbox-kernel-system-determinism.md#E4 · compatible · sandboxes/2026-09-28__train-gap-b02.py · session 2026-09-28, brain train gap batch 2 loop 9
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-wrong-sky.md#E19 · compatible · no sandbox · session (brain train 3 groups + 2 edges, sandboxed until satisfied, loop 2), sandbox script seam.mjs (live clone of both repos, real constants extracted verbatim), live-unfixed bug flagged at src/app/game.js line 389 (real but low severity, not applied)

## E15 — recursion input rebuild dropped a solved sibling touch pattern
- Date: 2026-07-11
- Project: Pappydapimp69/the-game-the-recursion
- Tags: [input][process][saga]
- What: While answering "identify gaps in other projects," audited the three earlier phases of this same 5-game saga that are also checked out locally (`the-game-wrong-sky`, `the-game-the-waiting-city`, `the-game-the-answering-deep`) for the same class of gap already found and fixed in this project this session (E10: on-screen touch controls shipped as a stub). Found all three earlier phases already have a complete, working, MORE ELEGANT on-screen touch UI than what this project needed to be given this session.
- Why built: This project's `P1: Input + UI rebuild (gamepad-first)` scaffolded the input layer fresh for phase 5 rather than porting the prior phases' input architecture forward.
- Design: The three earlier phases share one pattern (verified identical in `src/app/input.js` and `src/app/renderer.js` across all three): the renderer's single `render(ctx, w, view, now)` call conditionally draws an on-screen d-pad + action-button cluster directly on the canvas when `view.device === 'touch'`, and `render()` returns each drawn button's screen-space rect as a "zone" that `input.setZones(zones)` feeds back into the SAME hit-testing path used for touch AND mouse clicks on modal dialogs — one code path, no separate DOM/CSS overlay. The active `view.device` is computed as `input.hasTouch && device === 'keyboard' ? 'touch' : device`, so a touch-capable device shows the buttons immediately on first render (before any touch event has fired), while a keyboard-first desktop never shows them. `hasTouch` itself is `'ontouchstart' in window || (navigator.maxTouchPoints || 0) > 0`, with an inline comment already documenting why both checks are needed (`ontouchstart` alone false-negatives on some real touch hardware).
- Got right: This project's own touch fix (built earlier this session as `app/touch-controls.js`, a DOM-overlay + CSS-grid D-pad) is independently correct and verified end-to-end (a full touch-only Playwright e2e test proved title → run start → cutscene → movement → ability all work via touch alone) — it is not broken, just architecturally divergent from, and heavier than, the pattern already proven in this same saga.
- Where/why it failed: The gap this fixed (E10 — touch controls shipped as a stub, unplayable on phones) never needed to happen in the first place, or at minimum never needed a from-scratch DOM-based solution: the immediately-prior three phases of the same saga, built by the same author with the same architecture lineage, had already solved on-screen touch input in a way that's more elegant (no separate presentation layer, hit-zones shared between touch/mouse, capability-gated visibility with no flash-of-wrong-UI) than what got rebuilt this session. The `P1: Input + UI rebuild (gamepad-first)` task's framing ("rebuild") didn't include a step to check whether the subsystem being rebuilt already had a working solution one repo over.
- Fix: Not applied — explicitly out of scope to retrofit the canvas-integrated pattern into this project now that the DOM-based fix already ships and is verified working; documenting only, per this session's established "identify but defer" pattern for gaps that aren't asked to be fixed.
- Why this fix: The working fix already shipped and passed a real touch-only e2e test; migrating architectures now would be a pure refactor with no user-facing benefit, and is explicitly the kind of thing this session was told not to do unprompted.
- Rule of thumb: For any phase of a multi-phase saga/series sharing an author and architecture lineage, before scaffolding a subsystem "fresh," grep the immediately-prior phase's source for the same subsystem name first — a "rebuild" instruction is about producing a working result, not a mandate to start from zero, and a solved, battle-tested implementation one directory away is cheaper to port than to re-discover the same requirements from a missing-feature bug report later.
- Provenance (verified/assumed): VERIFIED first-hand — read `src/app/input.js` and `src/app/renderer.js` directly in all three sibling projects (`the-game-wrong-sky`, `the-game-the-waiting-city`, `the-game-the-answering-deep`), confirmed the `touchBtn`/`setZones`/`hasTouch` pattern is present and structurally identical (not merely similar) across all three, and confirmed via `find`/`grep` that this project (`the-game-the-recursion`) had no equivalent canvas-integrated pattern before this session's DOM-based fix.
- Link: session (identify gaps in other projects), no code change / no commit
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-prologue.md#E16 · compatible · no sandbox · session (brain analyze then brain train on a new group), no code change to a shipping project — a pure recorded-lessons synthesis per `brain train group`'s instruction

## E14 — recursion procgen seed suite is static not a growing fuzz corpus
- Date: 2026-07-11
- Project: Pappydapimp69/the-game-the-recursion
- Tags: [procgen][testing][process]
- What: While researching procgen QA methodology (property-based/fuzz testing, golden-master determinism, content-diversity metrics) for the Brain `ideas` repo, cross-checked the findings against this project's own procgen validation in `scripts/smoke.mjs`. The generator (`gen(seed, version, spec)`) is already validated by construction against a `validateMap` completability checker, run across a hardcoded seed suite `for (let s = 0; s < 20; s++)` (lines ~269-276), plus one pairwise `stableStringify(m1) !== stableStringify(mOther)` inequality check between two specific seeds (line 261) as the only content-diversity signal.
- Why built: The seed-suite-validation pattern (generate across a fixed range of seeds, assert a structural validator passes on all of them) is exactly the "verified-good corpus" shape that external procgen-QA research independently converges on as correct practice — this wasn't a gap in approach, it was already the right architecture, just at a small fixed scale.
- Design: `validateMap(map, spec)` is a pure function run per-seed in a loop; a failing seed pushes a diagnostic string into `suiteFails` and is reported via `console.error`, then the whole suite assertion fails. No seed outside `0..19` is ever exercised in CI. `mOther`'s only role is one hardcoded pairwise inequality check (seed 7 vs seed 8).
- Got right: Construction-time completability validation (not generate-then-hope), a pure/deterministic generator making seed-suite testing trivially reproducible, and a real regression gate that fails CI loudly (`suiteFails.length === 0`) rather than warning — matches current best practice for "does every generated level actually complete."
- Where/why it failed: Nothing is currently broken — this is an identified, deferred gap, not a bug. Two real limitations vs. the practice this session's research surfaced: (1) the seed range is a static `0..19` constant with no mechanism to grow — if a future generator/spec change introduces a bug at seed 47, nothing in the suite would ever exercise seed 47, and there's no persistent "known-bad seed" corpus that a fixed bug gets permanently regression-tested against once found; (2) the only diversity signal is a single hardcoded pairwise string inequality (seed 7 ≠ seed 8), which cannot detect a generator that produces superficially different-but-structurally-degenerate output (e.g. corridors-only layouts, clustered difficulty) across the wider seed space — the kind of "technically different every time, secretly always the same shape" collapse that expressive-range/entropy-based diversity metrics exist specifically to catch, and this suite has no such check.
- Fix: Not applied — explicitly deferred per instruction to document only, not modify code. The two identified improvements, if picked up later: (a) grow the seed suite into a persistent corpus — bump the tested range opportunistically, and any seed a fuzz/manual run discovers as failing gets added permanently to the suite (mirroring the OSS-Fuzz/Go-fuzzing "every failing input becomes a permanent regression case" pattern) rather than the range staying a fixed literal forever; (b) add one cheap entropy-based diversity check across the seed suite (e.g. Shannon entropy over slot-role/tile-type proportions per generated map, or an Expressive-Range-style two-metric scatter) alongside the existing single pairwise inequality, to catch structural collapse that "not byte-identical" cannot.
- Why this fix: Both are additive to the existing test file (`scripts/smoke.mjs`), don't change generator behavior, and directly close the two gaps between this project's current (already-good) practice and what the external research identified as the fuller version of the same practice — low-risk, well-scoped follow-ups rather than a redesign.
- Rule of thumb: A fixed-range seed-suite validator (`for s in 0..N`) is real regression coverage but is NOT a growing fuzz corpus and NOT a diversity check — it only proves the N seeds it happens to contain still validate, forever. Treat "does it validate on my seed suite" and "is the suite's diversity signal strong enough to catch structural collapse, not just byte-inequality" as two separate questions; a project can have excellent completability coverage and near-zero diversity coverage at the same time without either failing CI.
- Provenance (verified/assumed): VERIFIED first-hand — read `scripts/smoke.mjs` lines 252-281 directly in this session (not assumed from documentation), confirmed the exact seed range, the single pairwise diversity check, and the absence of any corpus-persistence or entropy-based diversity assertion anywhere else in the same test suite.
- Link: session (Brain training loop — procgen QA methodology research), no code change / no commit
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-opticon-recursion-per-seed-dependency-under-fixed-suite.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-07-13 · projects/local__sandbox-dbz-combat.md#E5 · compatible · no sandbox · session 01KxkbJUq8YajH8GokSZYYHy; re-verifying sandbox-dbz-combat ↔ the-game-the-recursion (currently single-source via sandbox-combined-realtime-loop#E1) from a new angle; sandbox `engine.mjs`, scratchpad `loop1-coverage-blindspots/` (run twice as separate process invocations, outputs diffed byte-identical)

## E13 — recursion ended screen has no shareable result ux or social preview tags
- Date: 2026-07-11
- Project: pappydapimp69/the-game-the-recursion
- Tags: [gamedev][web][ux]
- What: A follow-up Brain research pass on shareable-result UX (Wordle-style
  formats, clipboard API, social preview cards) prompted checking this
  project's actual ended-screen and `index.html` against those findings.
  Result: `renderEnded()` (src/main.js) draws the raw `SAGA5.<base64>.<hash>`
  export code as word-wrapped monospace text on the canvas with no
  copy-to-clipboard button anywhere in the app, and `index.html`'s `<head>`
  has zero Open Graph or Twitter Card meta tags (`grep`-confirmed: no
  `og:`, `twitter:`, or meta description present at all).
- Why built: The saga-code MECHANISM (a versioned, self-contained,
  backend-less base64 export carrying player-model + choices forward into a
  sequel game) was the actual design target and was built, tested, and
  verified correctly across this whole session — the PRESENTATION of that
  code as something a player would want to copy and share was never a
  separate design pass, so it inherited the plainest possible rendering
  (dump it as text on the canvas) once the mechanism worked.
- Design: The ended screen is presentation-only (mode `'ended'` in
  `main.js`), reading `sagaCode` (already computed by `exportSaga(world)`)
  and drawing it with the same canvas-text primitives every other screen
  uses — no DOM overlay, no button, no `<meta>` tags, since the whole app is
  a single `<canvas>` with no other interactive DOM elements until this
  session's on-screen touch controls (which also don't touch `index.html`'s
  `<head>`).
- Got right: The underlying export IS genuinely shareable in the sense that
  matters most (it's a real, versioned, self-contained code a sequel game
  can import — the hard part, the mechanism, works and is tested). Nothing
  about the actual data format needs to change for any of the UX
  improvements below.
- Where/why it failed: Three separate, independent gaps stack on top of an
  otherwise-working mechanism: (1) no copy-to-clipboard control means a
  player has to manually select monospace text off a `<canvas>` (which
  isn't even real DOM text — it's drawn pixels) to actually copy the
  code, a real friction point since canvas text can't be selected/copied by
  a browser's native text-selection at all; (2) no social preview tags mean
  a shared LINK to the game (as distinct from the code itself) renders with
  no title/description/image in any chat app, reading as a bare, untrusted
  URL rather than an inviting preview; (3) the raw base64 dump has none of
  the "spoiler-free outcome shape" design Wordle-style shares use — it
  conveys nothing readable about the run at a glance, so even if it were
  copyable, pasting it into a chat communicates nothing to the recipient
  without them separately pasting it INTO the game.
- Fix (identified, not yet applied — deliberately deferred): (1) Add a real
  DOM button on the ended screen (the app already isn't purely canvas-only
  now that on-screen touch controls exist as DOM elements) that calls
  `navigator.clipboard.writeText(sagaCode)` synchronously in its own click
  handler, with a visible-textbox fallback for unsupported contexts; (2) add
  a minimal Open Graph/Twitter Card tag set to `index.html`'s `<head>` (one
  static title/description/image for the whole game — per-result dynamic
  images aren't feasible on GitHub Pages, but ARE feasible per-ENDING since
  there are only 3 enumerable endings, if that's worth the small effort of
  3 pre-baked static images); (3) consider a short human-readable summary
  line ABOVE the raw code (e.g., "you chose to listen · dominant: merciful ·
  saved 6/8 voices") — genuinely spoiler-light since it doesn't reveal any
  actual dialogue/plot content, only the same category-level facts
  `buildFacts()`/the reveal beat already surface in-game — giving a
  recipient something to read even before they import the code themselves.
- Why this fix: All three fixes are additive to the existing, working
  export mechanism — none require touching `saga.js`'s actual encode/decode
  format, so there's no risk to the saga.v5 contract or its own test
  coverage; they only change how the ALREADY-CORRECT code is presented and
  distributed.
- Rule of thumb: When a project's core "shareable" mechanism is built and
  tested (the DATA format), audit its PRESENTATION as a separate,
  explicit step — a working export format with no copy button and no link
  preview is exactly as unshared as no export format at all, from the
  perspective of an actual player deciding whether to bother sharing it.
- Provenance: Verified first-hand — read `renderEnded()` in src/main.js and
  confirmed no clipboard/DOM button exists there; grepped `index.html` for
  `og:`/`twitter:`/meta-description and confirmed zero matches. NOT yet
  fixed or re-tested — deliberately deferred per direct instruction
  ("leave for later" pattern established earlier this session).
- Link: session following the "shareable-result UX" Brain research pass, in
  pappydapimp69/the-game-the-recursion; no fix commit yet.

## E12 — recursion palette has a red green confusable pair at similar luminance
- Date: 2026-07-10
- Project: pappydapimp69/the-game-the-recursion
- Tags: [gamedev][accessibility][visualdesign]
- What: Auditing this project's actual `PALETTE` object (src/app/palette.js)
  against a follow-up Brain research pass on color-vision-deficiency (CVD)
  design found that the `hollow` ramp (used for the hunter enemy and the
  finale antagonist — `['#5c3540', '#9e5866', '#c88996']`, a muted warm
  red/pink) and the `warden` ramp (a depth-2+ enemy —
  `['#2f4a2e', '#5c8a52', '#9bc98a']`, moss green) sit almost exactly on the
  classic red-green confusion axis that protanopia/deuteranopia collapse
  (the more common forms of CVD), AND their mid-tones land at very similar
  ROUGH perceived luminance (`0.299R+0.587G+0.114B` on `#9e5866` ≈ 110.5 vs.
  `#5c8a52` ≈ 117.8, only ~7/255 apart) — meaning the one channel that
  normally survives CVD (lightness) does NOT separate this pair either.
- Why built: `hollow` and `warden` were each authored independently, chosen
  for tonal/thematic fit (hollow: "muted warm," the thing wearing your
  shape; warden: "sickly moss-green... unlike anything else in the palette,"
  per the ramp's own code comment) rather than checked against each other or
  against any CVD-confusion model — no such check existed in this project's
  process before this research pass.
- Design: The palette is a small, fixed, hand-curated set of named 3-4-step
  ramps (`PALETTE.<name>`), each entity/tile-kind indexing exactly one ramp;
  shading only ever shifts ±1 index along a ramp (`shade()`), never computes
  arbitrary RGB. This structure is a genuine asset for a retrofit (per the
  same research pass): a locked-palette CVD fix should diagnose only the
  actually-confusable PAIRS and fix by separating LUMINANCE first, not
  redesign the palette or add new hues.
- Got right: The two entities using these ramps (the hunter — drawn with the
  `hollow` sprite/ramp — and the warden) already have visually DISTINCT
  SILHOUETTES (a gutted-humanoid shape vs. a squat, rooted, thorny-based
  blob — confirmed via a direct side-by-side sprite-sheet render this
  session), which is exactly the "redundant non-color cue" the same
  research calls out as often already free in pixel art with good silhouette
  discipline — so the actual player-facing risk is SOFTENED by shape, not
  left entirely to color. The `diver` (cool blue) and `voice`/`screamer`
  ramps sit on safer axes (blue and violet aren't the collapsed pair) and
  are not implicated by this finding.
- Where/why it failed: The mitigation is partial, not complete — silhouette
  helps at a readable size and a calm moment, but under motion, small
  on-screen size, or a fast decision (the hunter is actively chasing you
  while a warden may also be near its wake radius on the same depth-2+
  floors), color is still the FASTEST cue a player reads, and this pair
  currently gives a deuteranope/protanope player less separation on that
  fast channel than every other cross-entity pair in the palette. Separately
  (lower-severity, same audit): the `diver` (the player) and `hollow` (the
  hunter/hollow) sprites share a similar humanoid BASE silhouette (both are
  domed-head, shouldered, split-leg humanoid masks per sprites.js's DIVER/
  HOLLOW row data, differing mainly in interior detail and color) — weakening
  the "silhouette is a free redundant channel" assumption specifically for
  THIS pair, independent of the hollow/warden hue-collision finding above.
- Fix (identified, not yet applied — deliberately deferred): Per the
  retrofit playbook this same research pass produced: nudge `warden`'s or
  `hollow`'s LIGHTNESS apart in HSL/Lab space (no new hues, ramps keep their
  hue identity and thematic fit) until their mid-tones separate by a solid
  margin on both the raw palette AND a CVD-simulated pass (Chrome DevTools'
  Rendering tab → "Emulate vision deficiencies," available with zero extra
  tooling since this project is already Chromium/Playwright-tested) — plus,
  separately, consider a small silhouette differentiator between the
  `diver` and `hollow` masks (e.g., a different limb count/stance already
  used to distinguish `warden`/`screamer` from the humanoid pair).
- Why this fix: Luminance-separation is the cheapest, lowest-risk fix
  available (per the retrofit research: it's the single highest-leverage
  intervention for a small locked palette) — it changes zero hues, so the
  palette's authored thematic intent ("hollow: muted warm," "warden: sickly
  green, unlike anything else") is fully preserved, only the two ramps'
  brightness bands move apart.
- Rule of thumb: When authoring entity color ramps one at a time (a natural
  per-feature workflow — each enemy/creature gets its own ramp added when
  it's built), the resulting palette is never checked pairwise against
  EVERY other ramp for cross-entity confusability, only against "does this
  look distinct to me right now." Before shipping a palette with 4+ named
  entity ramps, run a `0.299R+0.587G+0.114B`-style luminance check (or a
  real CIEDE2000 pass) between every pair, specifically flagging any pair
  that also sits on the red-green axis — that combination is where CVD
  actually bites, and it's cheap to check even without a formal simulator.
- Provenance: Verified first-hand — read the actual hex values from
  src/app/palette.js, computed the rough luminance figures above directly
  from those values, and cross-referenced against the sprite-sheet render
  already produced this session (five creature sprites side-by-side) to
  confirm the silhouette-distinctness claims for hollow-vs-warden and
  diver-vs-hollow. NOT verified against a real CVD simulator or a real CVD
  player — the luminance figures are a standard perceptual-luminance
  approximation, not a proper CIEDE2000/Lab computation, and the fix
  described has not been applied or re-tested. Explicitly left unfixed this
  session ("leave for later" / "just write proposals").
- Link: session following the "6 virtual-control UX kernels" and "colorblind
  palette design" Brain research passes, in pappydapimp69/the-game-the-recursion;
  no fix commit yet.
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-brain-viz-growth.md#E3 · compatible · no sandbox · Sandbox: `sandbox-brain-viz-color-redundancy.js`; W3C WCAG 2.2 Use of Color: `https://www.w3.org/TR/WCAG22/#use-of-color`; W3C WCAG 2.2 Non-text Contrast: `https://www.w3.org/TR/WCAG22/#non-text-contrast`
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-brain-viz-growth.md#E4 · compatible · no sandbox · Sandbox: `sandbox-brain-viz-transition-palette.js`; related artifacts: `brain-viz.html`, `brain-garden-viz.html`
- Cited-by: 2026-07-18 · projects/local__sandbox-cvd-transition-audit.md#E1 · compatible · no sandbox · this session (brain train, external-research-verified); sandbox scratchpad `cvd-trajectory/engine.mjs` (run twice, byte-identical); sources: Brettel/Vienot/Mollon 1997 JOSA A + 1999 matrix; W3C WCAG relative luminance

## E11 — touch controls shipped without safe area inset margins
- Date: 2026-07-10
- Project: pappydapimp69/the-game-the-recursion
- Tags: [gamedev][input][mobile]
- What: The on-screen touch control layer (D-pad + four action buttons) built
  earlier this session positions its buttons via plain CSS offsets —
  `bottom: 14px; left: 14px;` for the d-pad, `bottom: 14px; right: 14px;`
  for the action cluster — with no accounting for a device's safe-area
  insets (notch/Dynamic-Island cutouts, the iOS home-indicator bar, Android's
  gesture-navigation band). This was IDENTIFIED via a follow-up Brain
  research pass, not yet fixed — deliberately deferred per explicit
  instruction rather than fixed in the same session.
- Why built: The control layer's own design/build pass focused on closing a
  far more severe gap (touch input was completely non-functional — no
  on-screen controls existed at all) and was verified against a standard
  Playwright mobile-viewport emulation, which does not model a real device's
  safe-area insets or its OS gesture-intercept bands at all.
- Design: Fixed pixel-offset positioning from the viewport edge, identical on
  every device regardless of notch/home-indicator/gesture-band geometry.
- Got right: The functional core (buttons wired into the same unified input
  vocabulary every other device uses, verified end-to-end via real touch
  events driving an entire game loop) is unaffected by this gap — this is a
  LAYOUT/PLACEMENT issue layered on top of already-correct plumbing, not a
  functional regression.
- Where/why it failed: A control placed flush against a screen edge on a
  real device risks two distinct failure modes that a `left/right/bottom:
  14px` static offset cannot distinguish between: (1) the OS's own
  edge-swipe gesture band (iOS edge-swipe-back, Android's back-gesture
  strip) can intercept the touch before the game's event listener ever
  fires, silently eating input with no error and no visual sign anything is
  wrong; (2) the button can render fully or partially UNDER a hardware
  cutout or the home-indicator bar, unreachable or invisible depending on
  device/orientation. Neither failure mode is observable in a headless
  Playwright viewport emulation (`isMobile`/`hasTouch`), which models screen
  DIMENSIONS but not a real device's safe-area geometry or OS gesture
  interception — the exact same category of "headless-green, broken on
  device" gap this session already found once with touch input itself.
- Fix (identified, not yet applied — deliberately deferred): Read the CSS
  environment variables `env(safe-area-inset-top/right/bottom/left)`
  (falling back to 0 on browsers that don't support them) and add them into
  each control cluster's offset — e.g.
  `bottom: calc(14px + env(safe-area-inset-bottom));` — so controls
  automatically clear whatever margin the specific device's chrome actually
  reserves, rather than a hand-picked constant that happens to work on
  whatever device was used to eyeball it.
- Why this fix: `env(safe-area-inset-*)` is the platform-provided value for
  exactly this problem (documented Apple/web-platform API) — reading it
  rather than guessing a fixed pixel margin means the layout is correct on
  every current and future notch/gesture-band geometry without per-device
  special-casing.
- Rule of thumb: Any on-screen control placed near a screen EDGE on a touch
  device must be inset by `env(safe-area-inset-*)`, not a hand-picked fixed
  pixel margin — treat this as load-bearing (a control can stop RECEIVING
  input entirely, not just look slightly off) rather than cosmetic, and
  don't trust a headless mobile-viewport e2e test to catch it, since those
  emulate screen size, not safe-area geometry or OS gesture interception.
- Provenance: Identified via reasoning about the shipped CSS + external
  research on safe-area-inset conventions (this session's own Brain-gap
  research pass), cross-checked against the actual `index.html` CSS to
  confirm no `env(safe-area-inset-*)` reference exists anywhere in it. NOT
  yet verified against a real device or a safe-area-aware emulation — the
  fix above is a design recommendation, not a verified, applied, and
  re-tested change. Explicitly left unfixed this session per direct
  instruction ("leave for later").
- Link: session following commit 4a73c34 ("Add on-screen touch controls")
  in pappydapimp69/the-game-the-recursion; no fix commit yet.
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-waiting-city-recursion-touch-detection-and-reachability-are-independent.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX

## E10 — on screen touch controls left as a stub shipped unplayable on phones
- Date: 2026-07-10
- Project: pappydapimp69/the-game-the-recursion
- Tags: [gamedev][input][mobile]
- What: The unified input layer detected `touchstart` events and correctly
  flipped `activeDevice` to `'touch'` (so hint text would render in touch
  language) — but nothing ever called `setTouchMove()` or injected a press
  from an actual on-screen control. The module's own comment named this
  "the on-screen control layer (P-later)" and it was never built in a later
  pass. The game shipped and was deployed to GitHub Pages, playable and
  tested extensively via keyboard/gamepad-driven Playwright e2e and manual
  desktop use, across several rounds of feature work and bug fixes.
- Why built: Device detection (which device is "active," for hint-text
  purposes) and device INPUT (an actual mechanism for that device to act) are
  two different pieces of work; the detection half is small and was built
  early, the input half is a real UI feature (on-screen buttons, layout,
  touch-event wiring) that got deferred and then never revisited, with
  nothing in the test suite positioned to catch the gap.
- Design: On-screen controls are plain DOM buttons overlaid on the game
  stage (not drawn inside the canvas), positioned via CSS grid in the two
  bottom corners: a word-labeled D-pad (arrows are the one exception to
  "words, not glyphs" — a triangle's meaning is its shape) and four labeled
  action buttons (confirm/cancel/action/skip) matching the same names every
  other device's presses already use. Each button's touchstart/touchend
  drives the SAME two input.js seams the module had always exposed —
  `setTouchMove(vec)` for the d-pad, and a new `pressTouchDown`/`pressTouchUp`
  pair for the action buttons (an edge press for menu nav, plus a HELD flag
  so the existing hold-to-dismiss cutscene gesture works unmodified from
  touch). The layer is only constructed at all when
  `navigator.maxTouchPoints > 0`, independent of `activeDevice` — so a
  touch-capable device gets it before its first touch, not only after.
- Got right: The eventual fix was cheap BECAUSE the input layer's own
  abstraction was already correct — `setTouchMove(vec)` and an injectable
  press already existed as named, documented seams in input.js from the
  start. Building the actual on-screen buttons was a couple hours of DOM +
  CSS work plumbed into two existing entry points, not an input-layer
  redesign.
- Where/why it failed: Every automated check that existed for this project —
  the deterministic smoke suite, and every Playwright e2e script written
  across the whole session — drove input via `page.keyboard.press(...)` or a
  `window.__game` dev hook, NEVER via `page.touchscreen`/real touch events,
  even on the e2e scripts that used `isMobile: true, hasTouch: true` viewport
  emulation. Those scripts verified CANVAS SIZE on a phone-shaped viewport,
  which is a real and valid check, but "the canvas is the right size" and
  "you can press anything on this device" are unrelated claims, and only the
  first one was ever tested. A phone-shaped viewport with keyboard-driven
  presses looks, to a test suite, exactly like a desktop browser that happens
  to be narrow — it never exercises the actual input path a real phone user
  is limited to.
- Fix: Built the on-screen control layer (a word-labeled D-pad + four
  action buttons, shown whenever `navigator.maxTouchPoints > 0` — independent
  of "which device is currently active" — so it's present before the first
  touch, not only after). Extended input.js with `pressTouchDown`/
  `pressTouchUp` (a touch button is both an edge press for menu nav AND a
  HELD state, so hold-to-dismiss gestures work identically from touch).
  Verified by a NEW class of e2e test: real `TouchEvent`s (or
  `Locator.tap()`) driving an entire run — title navigation, starting the
  game, a cutscene's hold-to-skip, movement, and an ability — with the
  keyboard never touched at all.
- Why this fix: The bug was invisible specifically because every existing
  test simulated a keyboard user on a phone-sized screen, never an actual
  touch-only user; the fix pairs the missing feature with the missing TEST
  CLASS, not just the missing feature, so this can't silently regress again.
- Rule of thumb: A `hasTouch`/`isMobile` viewport flag in an e2e test proves
  the LAYOUT survives a phone-shaped screen; it proves NOTHING about whether
  a real touch-only user can actually press anything, unless the test itself
  drives input via real touch/tap events rather than `page.keyboard`. If a
  project supports multiple input devices, each device needs at least one
  end-to-end test that is FORBIDDEN from using any other device's input API
  — a keyboard-driven test on a narrow viewport will pass forever while a
  whole device category is completely unplayable underneath it. Grep for
  "(P-later)" / "TODO" / "not yet built" comments in input-adjacent code
  during an audit — they mark exactly this shape of gap.
- Provenance: Verified first-hand — the failure was reproduced directly (a
  Playwright script driving only `page.touchscreen.tap()` on the deployed
  title screen: zero mode/selection change after several taps), root-caused
  by reading input.js's own comment, fixed, and then re-verified with a
  from-scratch touch-only e2e run through the whole loop (title → run start →
  cutscene advance/skip → movement → ability use), plus the full 113-check
  smoke suite (golden fingerprint unaffected — presentation-only).
- Link: commit "Add on-screen touch controls: the game was completely
  unplayable on touch-only devices" in pappydapimp69/the-game-the-recursion.
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-recursion-waiting-city-grep-prior-phase-pays-the-handoff-price.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-09-25 · projects/pappydapimp69__dark-goblin.md#E8 · compatible · no sandbox · session https://claude.ai/code/session_01S9y8kM4TmczCkWaVsNagrn · commit e82ee5d in Pappydapimp69/dark-goblin

## E9 — wrapped list row helper must advance y for single line rows too
- Date: 2026-07-10
- Project: pappydapimp69/the-game-the-recursion
- Tags: [gamedev][ui][bug]
- What: A word-wrap helper for a list of selectable rows (a choice screen's
  options, each drawn as "> label" or "  label") returned the y-coordinate of
  the last line it drew, so the caller could stack the next row beneath it.
  For a row that wrapped to 2+ lines this worked; for a row that fit on ONE
  line it silently returned the SAME y it was given, one canvas-line short of
  where the next row should actually start.
- Why built: An existing single-line word-wrap helper (already used
  correctly elsewhere, for a prompt) was adapted to also prefix a "> "/"  "
  selection marker per row and hand back a cursor position, since a caller
  now needed to stack a variable number of rows (each independently 1 or
  N lines) rather than draw one fixed block of text.
- Design: The helper's loop draws a line and increments a running `ty` by
  `lineH` every time it flushes a line MID-loop (because another word didn't
  fit), then draws the final remaining line at whatever `ty` currently is —
  by design, since that's where the last line visually belongs.
- Got right: The wrapping/measurement logic itself (word-by-word,
  `ctx.measureText` against a max width) was correct and reused an
  already-proven pattern rather than inventing a new one.
- Where/why it failed: The function's RETURN value conflated two different
  things: "the y the last line was drawn at" (correct for drawing) and "the y
  the NEXT row should start at" (what the caller actually needed). For a row
  that never wrapped (the common case for short option labels), no mid-loop
  flush ever incremented `ty`, so the last line was drawn at the y it started
  at, and that SAME y was returned — the caller's next row then overlapped it
  by a full line, drawn one line-height too high. A synthetic before/after
  screenshot test (rendering the exact three-option choice list at the exact
  narrow-viewport width from the bug report) caught this immediately: two of
  the three now-wrapped rows overlapped illegibly.
- Fix: After drawing the FINAL line, always advance `ty += lineH` before
  returning it — a single-line row now correctly reports "one line-height
  past where I was drawn" as its next-available-slot, matching the mid-loop
  behavior exactly instead of being a special case.
- Why this fix: The alternative (having the CALLER add a line-height only
  when it happens to know a row was single-line) would require the caller to
  duplicate the wrap function's own internal line-counting logic just to get
  the spacing right — the fix keeps "how many lines did this take" entirely
  inside the one function that already knows.
- Rule of thumb: A word-wrap/stacking helper that returns a cursor position
  for the CALLER to continue from must return "the next available slot," not
  "where the last thing was drawn" — audit the single-line/no-wrap path
  specifically, since that's exactly the case where a mid-loop increment
  never fires and the two meanings silently diverge. A synthetic render test
  at the reported viewport width (not just eyeballing logic) is what actually
  catches this class of off-by-one before it ships.
- Provenance: Verified first-hand — caught via a synthetic Playwright script
  rendering the exact helper function against the exact reported bug-screen
  text before shipping, confirmed fixed via a second render of the same
  script after the one-line change (`ty += lineH` added to the final-line
  branch), and confirmed via the full smoke suite (113 checks unaffected,
  this is presentation-only code with no sim/determinism surface).
- Link: commit "Cutscenes: dialogue advances on confirm, ends only on hold;
  fix choice text cutoff" in pappydapimp69/the-game-the-recursion (the
  `wrapOption` helper in src/main.js).
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-recursion-opticon-measuring-the-wrong-node-certifies-the-layout-bug.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX

## E8 — player paced dialogue over clock scheduled captions
- Date: 2026-07-10
- Project: pappydapimp69/the-game-the-recursion
- Tags: [gamedev][ui][cutscene]
- What: A cutscene's dialogue captions were originally scheduled by TIME —
  each line got a fixed on-screen window computed from the scene's total
  duration divided (or later, sized) by an estimated reading/typing rate —
  and the whole scene auto-advanced to the next spine node once its internal
  clock ran out.
- Why built: The cutscene player's markers (world-state-mutating commands)
  are legitimately time-scheduled and must stay that way for the watch-vs-
  skip determinism guarantee (skipping fires every remaining marker at once
  and must land byte-identical to watching in real time). It was natural to
  reuse that same clock to schedule captions too, since it already existed.
- Design: Two fixes were tried in sequence before landing on the real one.
  Fix attempt 1: word-wrap the caption text (it was overflowing the canvas).
  Fix attempt 2: give each caption line its own window sized from its actual
  character count at the typewriter's reveal rate, so a long line wouldn't
  get replaced mid-type by the next line's fixed timestamp. Both were correct
  as far as they went, but both were still fundamentally guessing a reading
  speed and gambling that the guess was fast enough for a fast reader and
  slow enough for a slow one — no fixed number satisfies both.
- Got right: Recognizing that "dialogue timing" and "scene/marker timing" are
  two DIFFERENT clocks with different correctness requirements, and that only
  one of them (markers) actually needs to be wall-clock-scheduled for the
  determinism contract. Splitting them let dialogue become fully player-paced
  (a confirm press completes the current line's typewriter instantly, or — once
  it's fully shown — steps to the next line; the scene never auto-advances
  need to leave a cutscene is now the SAME deliberate hold-to-dismiss gesture
  used for skipping) without touching the marker/elapsed-clock machinery the
  watch-vs-skip test depends on at all.
- Where/why it failed: The clock-paced approach failed for both fast and slow
  readers simultaneously, in different ways: a line sized for a slow reader
  wastes a fast reader's time; a line sized for a fast reader gets yanked away
  from a slow reader mid-sentence. Per-line dynamic sizing (fix attempt 2)
  narrowed the failure window but never closed it — it's still a guess.
- Fix: Kept the scene's own `elapsed` clock EXACTLY as it was (advance()/
  skip()/isEnded() untouched, so the determinism test suite needed zero
  changes) and added a second, uncapped, never-frozen presentation clock
  (`typeElapsed`) used ONLY by the typewriter reveal, plus an explicit
  caption-index pointer advanced only by player input. The scene's totalMs
  became a generous safety ceiling (letterbox/entity-animation pacing still
  reads off the ORIGINAL short authored duration via a separate constant) —
  a value picked to never realistically get hit, not a scheduling deadline.
- Why this fix: It's cheaper and structurally cleaner than trying to author
  or auto-tune a single "correct" reading speed, and it composes cleanly with
  the existing determinism-critical clock instead of trying to reconcile two
  purposes (marker timing vs. reading-comfort timing) inside one number.
- Rule of thumb: If a UI clock is being used for two purposes at once — one
  that has a real correctness requirement (determinism, replay, animation
  sync) and one that's really about human reading/reaction comfort — split
  them into two clocks before trying to tune the numbers. No fixed duration
  or rate constant satisfies both a fast and a slow human, but a
  player-input-driven pointer satisfies both by construction.
- Provenance: Verified first-hand — built, then proven via Playwright e2e that
  (a) sitting idle never leaves the cutscene, (b) a confirm press advances a
  line only once it's fully typed, (c) holding to dismiss works identically at
  any point including the last line, and (d) the golden fingerprint / full
  smoke suite (113 checks) is unaffected since none of the marker/elapsed
  machinery changed.
- Link: commits "Cutscenes: dialogue advances on confirm, ends only on hold;
  fix choice text cutoff" and the prior two cutscene-pacing commits in
  pappydapimp69/the-game-the-recursion.
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-draft-recursion-purity-is-relative-to-a-named-clock.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-07-26 · projects/pappydapimp69__brain-builder.md#E7 · compatible · no sandbox · brain-builder @ claude/brain-install-link-mode-5ykmu8, src/present/battle.mjs

## E7 — content derived cumulative quotas for substages within one spine stage
- Date: 2026-07-10
- Project: pappydapimp69/the-game-the-recursion
- Tags: [gamedev][gamedesign][architecture]
- What: Expanding a single-floor "learning" spine stage into four escalating
  descent levels needed a gate for "may the player leave THIS depth for the
  next one," on top of the existing gate for "may the player leave 'learning'
  entirely" (already a construction-fixed `totalChoicePoints` count, from an
  earlier lesson: a threshold read from a command's own payload is trivially
  bypassable by omitting it).
- Why built: Choice points are no longer evenly distributed across depths —
  the original floor kept its original six, and each of the three new floors
  added only two — so a naive generic formula (e.g. `ceil(total * depth /
  maxDepth)`) does not match the real per-depth counts and would gate some
  depths too early or too late relative to the actual content placed there.
- Design: Two options: (a) derive each depth's quota from a generic formula
  over `totalChoicePoints`/`maxDepth`, treating depths as if content were
  evenly spread, or (b) compute the ACTUAL cumulative count of choice points
  tagged for each depth directly from the content table itself, once, at
  world construction, and store that fixed array in authoritative state
  (`spine.depthQuotas`) exactly like `totalChoicePoints` already is.
- Got right: Choosing (b). Each choice point in content.js already carries
  its own `depth` field (which floor it's placed on); the app layer sums
  those into a cumulative-quota array ONCE, at world construction, and passes
  it in as `options.depthQuotas` — the same anti-bypass shape as
  `totalChoicePoints`, now applied one level deeper.
- Where/why it failed: Choosing (a) — the generic formula — would have
  silently drifted out of sync with the content the moment content.js's
  per-depth distribution changed (which it did, immediately: 6/2/2/2, not an
  even split), gating some depths before their own choices were actually
  placeable, or after a later depth's choices had already become reachable.
  This was caught by REASONING about the actual distribution before writing
  the gate, not discovered as a runtime bug — but it's the kind of drift that
  is easy to introduce later if a formula is trusted over the source data.
- Fix: `spine.depthQuotas[d-1]` = the cumulative count of `CHOICE_POINTS`
  entries with `depth <= d`, computed once in the app layer from the actual
  content array and handed to `makeWorld` as a fixed option — never
  recomputed from a formula, never re-suppliable per `ADVANCE_DEPTH`
  dispatch. Backward compatible by construction: a caller that never opts in
  (no `maxDepth`/`depthQuotas` passed) defaults to a single depth whose quota
  IS `totalChoicePoints`, so every existing test/caller is unaffected.
- Why this fix: A gate that's supposed to track "has the content assigned to
  this substage actually been exhausted" should read that fact FROM the
  content, not reconstruct an approximation of it from a shape assumption
  (even distribution) that the content is under no obligation to satisfy.
- Rule of thumb: When adding a sub-progression gate WITHIN an existing
  construction-fixed-threshold stage (levels within a level, chapters within
  an act), derive each sub-threshold from the actual per-item tags in the
  content table itself, computed once at world/level construction — not from
  a formula over aggregate counts that assumes even distribution. The
  anti-bypass property (fixed in state, never re-suppliable per command) has
  to be paired with an anti-drift property (derived from real content, not a
  shape guess) or the gate can be correct-by-construction against tampering
  while still being wrong-by-construction against the content it's meant to
  track.
- Provenance: Verified first-hand — implemented, exercised by dedicated smoke
  tests (quota-met/quota-unmet/maxDepth-exceeded/depth-skipped-entirely, plus
  a default-single-depth backward-compatibility check), and proven in a full
  Playwright playthrough of all four depths end to end with the real,
  unevenly-distributed content.
- Link: commit "Expand the game: multi-descent levels, abilities, new
  enemies, richer dialogue" in pappydapimp69/the-game-the-recursion
  (`computeDepthQuotas` in src/main.js, `ADVANCE_DEPTH` in src/sim/reduce.js).
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-august-10-recursion-aggregate-supply-does-not-imply-per-stage-supply.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX

## E6 — mst over delaunay for small room counts
- Date: 2026-07-09
- Project: pappydapimp69/the-game-the-recursion
- Tags: [gamedev][algorithm][gamedesign]
- What: A procedural map generator needed to connect a small number of
  generated rooms (roughly half a dozen to a dozen per map) into a traversable
  layout with some non-tree shortcuts. The design research going in recommended
  Delaunay triangulation + minimum-spanning-tree (the TinyKeep dungeon-
  generation approach) as the standard technique.
- Why built: A quest-spine mission graph (entry -> key -> gate -> encounter ->
  reward -> exit) needed to be laid out in 2D space and connected by carveable
  corridors, with a FEW extra loop connections beyond the minimum spanning
  tree so the map doesn't read as a single strict corridor.
- Design: Build the mission graph and its node types first (entry/key/gate/
  etc.), pack rooms into a deterministic grid of slots (no physics simulation,
  no overlap possible by construction), then connect the rooms with SOME graph
  algorithm before carving corridors between connected room centers.
- Got right (the choice made): Skip full Delaunay triangulation. Instead,
  build the minimum spanning tree directly over the COMPLETE all-pairs
  Euclidean-distance graph (every room compared to every other room) via
  Kruskal's algorithm, then re-add the shortest ~15% of the non-MST edges as
  loop/shortcut connections. No Delaunay step at all.
- Where/why it failed (the tradeoff accepted): True Delaunay triangulation
  gives better LOCALITY guarantees as room count grows large (it avoids ever
  needing to consider a far-apart pair as a candidate edge, since Delaunay's
  triangulation already prunes those) — at dozens or hundreds of rooms, an
  all-pairs graph is quadratic in edge candidates and Delaunay would be the
  right call. At this project's actual scale (single-digit to low-double-
  digit rooms per generated map), that locality benefit doesn't materialize:
  an all-pairs graph is cheap to build and its MST is IDENTICAL in practice to
  what Delaunay+MST would produce, because there simply aren't enough rooms
  for Delaunay's pruning to matter.
- Fix (what was chosen instead of a workaround): All-pairs Euclidean distance
  + Kruskal's MST + shortest-15%-of-remainder-as-loops, entirely deterministic
  and requiring NO random draw (candidate edges are sorted by distance with a
  fully deterministic tie-break on room index, so identical room layouts
  always produce identical connections) — simpler to implement and verify
  than a Delaunay triangulation routine, for identical output quality at this
  room count.
- Why this fix: Reaching for the "standard," more sophisticated algorithm from
  the reference material is not automatically the right call — its benefit
  over a simpler approach is often conditional on SCALE, and the simpler
  approach can be provably equivalent (not just "good enough") below that
  scale threshold, while being cheaper to implement, reason about, and keep
  deterministic.
- Rule of thumb: Before implementing a more sophisticated graph/geometry
  algorithm because a reference source recommends it, check whether its
  advantage over the naive version is scale-dependent, and estimate where
  your actual data sits relative to that threshold. A simpler, fully
  deterministic all-pairs approach can be exactly as correct at small N while
  being cheaper to build, test, and keep provably reproducible.
- Provenance: Verified first-hand — implemented and tested against a 20-seed
  (later spot-checked against 200 seeds) generation suite, with a validator
  that flood-fills the actual carved tiles to confirm reachability; every
  seed produced a fully connected, completable map using only the all-pairs
  MST + partial-loop approach, with no Delaunay step involved.
- Link: commit "P3: procedural map generation — authored feel, completable by
  construction" in pappydapimp69/the-game-the-recursion.
- Cited-by: 2026-07-13 · projects/pappydapimp69__draft.md#E15 · compatible · no sandbox · session (brain train seams: draft + the-game-the-recursion); sandbox `sandbox.py`, scratchpad `gap10/` (run twice as separate process invocations, outputs diffed byte-identical; corrected version only)

## E5 — fixed spine with variants over branching tree
- Date: 2026-07-09
- Project: pappydapimp69/the-game-the-recursion
- Tags: [gamedev][gamedesign][narrative]
- What: A narrative retelling that adapts to a live player-model (a signed
  trait vector built from tracked choices) needed a structure for how much
  the story itself could actually vary run to run.
- Why built: The game's core premise is "a voice that learns you and reflects
  it back" — the world/dialog/cutscenes should feel different depending on
  who the player has been, both within one run and carried in from a prior
  game via an imported save-code.
- Design: Two structures were on the table: (a) a genuine branching narrative
  tree, where different choices lead to substantively different subsequent
  content and possible endings multiply combinatorially, or (b) a FIXED
  spine of emotional beats (same ordered stages every run: intro, learning,
  reveal, hollow, finale) where only the SURFACE — which of 2-4 authored
  variants is shown at each stage — is chosen live by a salience-based
  director reading the player-model.
- Got right (the choice made): Fixed spine + 2-4 variants per stage, selected
  by a director (a salience/fuzzy-pattern matcher) rather than a true
  branching tree. Content cost is then LINEAR in (number of stages x variants
  per stage), not exponential in choices made.
- Where/why it failed (the tradeoff accepted): A true branching tree can
  produce genuinely divergent later content and multiple distinct endings
  shaped by early choices in ways a fixed-spine-with-variants structure
  cannot — two players who made very different choices in this design still
  pass through the exact same ORDERED stages, only with different flavor/
  framing at each one. The ceiling on narrative divergence is real and lower
  than a branching design's ceiling.
- Fix (what was chosen instead of a workaround): Accept the lower divergence
  ceiling deliberately, and invest the saved authoring budget into making the
  SURFACE variation feel earned and legible instead — attributed callbacks
  that name a specific past choice, confidence-gated assertions about the
  player's tendencies, and a saga-diff against an imported prior run. The
  design bet is that legible, specific-feeling surface variation reads as
  more responsive per unit of content than a branching tree's deeper-but-
  thinner-per-path divergence would, at the content budget actually
  available for this project.
- Why this fix: For a project whose available authoring budget cannot support
  the exponential growth of a real branch tree, a fixed spine with a small,
  linear number of well-crafted variants per stage — paired with genuinely
  attributed, specific-feeling callbacks — was judged to produce a MORE
  convincingly reactive experience per hour of authoring than a shallow
  branching tree that runs out of budget a few choices deep and starts
  reusing content anyway.
- Rule of thumb: When a narrative system's stated goal is "the game reacts to
  who you are," check whether the actual authoring budget can sustain genuine
  branching before committing to that structure — a fixed spine with
  state-selected surface variants (plus legible, ATTRIBUTED callbacks to
  specific past choices) can read as more responsive than a branching tree
  that's forced to be shallow, because the variation that DOES exist is
  denser and better-crafted rather than thinly spread across many rarely-seen
  branches.
- Provenance: Verified first-hand — this is the structure actually built and
  playtested end-to-end (a full scripted spine playthrough, plus a real
  browser session driving all five stages via input); not an untested design
  assumption. The ceiling/tradeoff described is a reasoned judgment made
  during design, not something empirically measured against an alternative
  branching implementation (which was never built), so the COST side of this
  entry is assumed/reasoned rather than measured, while the BENEFIT side
  (content built linearly, playthrough works, callbacks read as specific) is
  verified.
- Link: commit "P6: the retelling — a real, playable spine, closed loop to
  saga.v5" in pappydapimp69/the-game-the-recursion; design rationale also
  recorded in PROPOSAL.md §4.

## E4 — fingerprint excludes new subsystems by design
- Date: 2026-07-09
- Project: pappydapimp69/the-game-the-recursion
- Tags: [gamedev][state][testing][determinism]
- What: Two new subsystems (cutscenes, the narrative spine) were added on top
  of an existing golden replay-fingerprint test, and their state
  (`world.cutscene`, `world.spine`) was deliberately left OUT of the
  fingerprint's input object rather than folded in.
- Why built: The project already had a golden fingerprint (a hash of a fixed
  scripted playthrough's end state, asserted equal to a baked value on every
  run) guarding the whole deterministic core against regressions. Adding two
  new authoritative-state subsystems raised the question of whether the
  fingerprint's input should grow to cover them too.
- Design: `fingerprintOf(world)` builds one small, deliberately-curated object
  (tick, rng words, player position/hp, model axes, facets, arc choice, ended
  flag) that `fingerprint()` hashes. It is NOT "hash the whole world" — it was
  already scoped tightly before this decision arose.
- Got right (the choice made): Keep the golden fingerprint's input object
  UNCHANGED, and instead give each new subsystem its OWN dedicated determinism
  test with its own explicit assertion — a full watch-vs-skip hash-equality
  check for cutscenes (comparing a bespoke fingerprint of the fields cutscene
  markers actually mutate), and a full scripted-spine-twice-from-one-seed
  equality check for the narrative spine, both living in the same smoke
  suite alongside the golden check but asserting independently of it.
- Where/why it failed (the tradeoff accepted): The golden fingerprint no
  longer certifies "the ENTIRE world state is deterministic" — a bug that
  corrupted `world.cutscene` or `world.spine` in some exotic way NOT covered
  by the dedicated tests could theoretically slip past the golden check,
  since that field simply isn't in its hash input. The golden value also
  needed no update across two entire new subsystems being added, which is
  convenient but is precisely the flip side of the same gap: it didn't need
  updating BECAUSE it wasn't looking at that state at all.
- Fix (what was chosen instead of a workaround): Rather than growing the
  fingerprint's field set (which would force a new golden value baked with
  every content/subsystem addition, coupling an unrelated regression guard to
  every unrelated change) or leaving the new subsystems completely
  unverified, each new subsystem got its own SEPARATE, PURPOSE-BUILT
  determinism assertion. The golden fingerprint stays a stable, narrow
  regression guard over the original core; new subsystems earn their own
  narrower, more targeted determinism tests instead of diluting a shared one.
- Why this fix: A single shared fingerprint that tries to cover an ever-
  growing feature set becomes brittle in the opposite direction — every
  legitimate new feature forces a fingerprint churn, training the team to
  treat "the golden changed" as routine noise instead of a real signal. Split
  determinism guarding by SUBSYSTEM instead: one narrow, rarely-changing
  golden for the oldest/most-stable core, and one dedicated equality test per
  newer subsystem, each precisely scoped to what that subsystem actually
  needs to prove (byte-identical watch/skip; two full playthroughs match).
- Rule of thumb: When adding new authoritative state on top of an existing
  golden/regression hash, resist the urge to fold it into the existing
  fingerprint's input by default — ask whether a SEPARATE, purpose-scoped
  determinism assertion for the new subsystem communicates the guarantee more
  precisely and keeps the old golden's blast radius (and churn rate) stable.
  Growing one shared hash's input set trades precision and stability for
  (illusory) unification.
- Provenance: Verified first-hand — designed and implemented this way during
  the cutscene (P5) and spine (P6) passes of this project; both subsystems'
  dedicated tests independently caught real issues during development (the
  watch-vs-skip test verified the cutscene player's marker-firing contract;
  the two-full-runs-must-match test caught the reducer bug filed separately
  as `spine-gate-bypassable-via-omitted-command-param`) while the golden
  fingerprint's value never needed to change across either pass.
- Link: commits "P5: cutscenes — deterministic, data not code" and "P6: the
  retelling — a real, playable spine, closed loop to saga.v5" in
  pappydapimp69/the-game-the-recursion.
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E16 · compatible · no sandbox · August-10 sandboxes/loop02_fingerprint_blind_to_capture_bug.py

## E3 — effect vs existence gating resolved per object
- Date: 2026-07-09
- Project: pappydapimp69/the-game-the-recursion
- Tags: [gamedev][gamedesign][quest]
- What: This project's design proposal inherited a genuine, previously
  UNRESOLVED tension between two prior projects' precedents: Wrong Sky's
  `effect-gated-not-existence-gated` idea (spawn all interactables from the
  start; gate the EFFECT of interacting with them by current state — early,
  "wrong" interaction is a deliberate discovery-puzzle feature) versus this
  saga's own `the-game-prologue#E9` pitfall (existence-gate quest targets —
  don't spawn them until accepted — so pre-acceptance actions can't
  retroactively/accidentally satisfy a quest objective). Brain's read fan-out
  surfaced both, attributed, and explicitly did not resolve which one this
  new project should follow, per protocol ("keep BOTH and note the tension —
  do not resolve it; the human decides").
- Why built: The new project has BOTH kinds of object in play at once for the
  first time: discovery-flavored world objects (where early, exploratory
  interaction is meant to reward curiosity) and quest/spine-critical targets
  (where early interaction, if it were even possible, would let a player
  short-circuit or corrupt the intended progression).
- Design: Rather than adopting one rule project-wide, the proposal recorded
  the tension explicitly in its own section and made an per-kind decision
  the human could see and could have overridden.
- Got right (the choice made): Apply BOTH rules, chosen per object based on
  what the object protects — discovery/flavor objects follow Wrong Sky's
  effect-gated pattern (always present, gate the effect on current state);
  quest- and spine-critical objects (procgen's required slots, the learning
  stage's choice points, the hollow's ending choice) follow the existence-
  gated pattern (they are constructed/reachable only once their governing
  stage/quest actually needs them, per the procgen validator's slot-placement
  and reachability guarantees).
- Where/why it failed (the tradeoff accepted): This means the codebase now
  carries TWO different gating philosophies for what is conceptually "an
  interactive world object," rather than one uniform rule a future
  contributor can apply everywhere without first classifying which kind of
  object they're adding. A contributor unfamiliar with this distinction could
  misapply the wrong pattern to a new object type.
- Fix (what was chosen instead of a workaround): Document the actual dividing
  line explicitly (in the proposal, and now here) rather than leaving it
  implicit in scattered code: gate by EXISTENCE when early/premature access
  would let a player break or shortcut a system's guarantees (quest
  completability, spine ordering); gate by EFFECT-only when early access is
  itself a feature (rewarding exploration/curiosity) and no system guarantee
  is at risk from it being touched "too early."
- Why this fix: The two prior precedents were each correct FOR THE SHAPE OF
  OBJECT they were designed around — they were never actually in conflict
  about mechanism, only in what class of object each author had in mind.
  Making the classification question explicit (protects a system guarantee?
  existence-gate. Purely a discovery reward? effect-gate) resolves the
  apparent contradiction without forcing a false uniform rule onto objects
  that don't share the same risk profile.
- Rule of thumb: When Brain's read fan-out surfaces a genuine unresolved
  tension between two prior projects' precedents, look for whether the
  "conflict" is actually about two DIFFERENT classes of the thing in
  question rather than a true disagreement on mechanism — if so, the
  resolution is a classification rule (which precedent applies to which
  class), not a project-wide pick-one-and-discard-the-other decision.
- Provenance: Verified first-hand as a real design decision made during this
  project's build — the classification rule was stated in PROPOSAL.md §9
  before content was authored, and the actual content built (procgen slots
  existence-gated via ACCEPT-time construction; discovery objects, where
  present, effect-gated) followed it. Not an abstract policy left unapplied.
- Link: PROPOSAL.md §9 in pappydapimp69/the-game-the-recursion; the earlier
  entries this resolves are `ideas` fragment
  `RPG/interactable/effect-gated-not-existence-gated/always-present-discovery`
  and `projects/pappydapimp69__the-game-prologue.md#E9`.
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E15 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E2 — spine gate bypassable via omitted command param
- Date: 2026-07-09
- Project: pappydapimp69/the-game-the-recursion
- Tags: [gamedev][state][gamedesign]
- What: A reducer command (`ADVANCE_SPINE`) meant to gate a stage transition
  behind a completion threshold (`learningIdx >= requiredChoices`) read that
  threshold off the COMMAND's own payload (`cmd.requiredChoices`), defaulting
  to `0` when absent (`cmd.requiredChoices || 0`).
- Why built: A fixed narrative spine advances through ordered stages; leaving
  stage 1 ("the learning") should require all of that stage's choice points to
  have been answered. The gate needed a threshold to compare `learningIdx`
  against, and passing it as part of the dispatched command felt natural since
  the caller (the UI orchestration) already knew the count.
- Design: `reduce(state, cmd)` is the sole authoritative mutator; commands are
  plain data the caller constructs and dispatches. The gate lived entirely
  inside the `ADVANCE_SPINE` case: `if (s.stage === 1) allowed =
  s.learningIdx >= (cmd.requiredChoices || 0);`.
- Got right: The gate correctly BLOCKED an early, correctly-parameterized
  attempt (`ADVANCE_SPINE({requiredChoices: 3})` before 3 choices were made) —
  the first version of the regression test for this passed immediately, which
  is exactly the kind of "test passes at first, but only proves one path was
  exercised" trap this project's own memory catalog has flagged before.
- Where/why it failed: A SECOND test — dispatching a bare `ADVANCE_SPINE`
  with no payload at all right after the blocked attempt — advanced the stage
  anyway. `cmd.requiredChoices || 0` evaluates to `0` when the field is simply
  omitted, and `learningIdx (0) >= 0` is true. The "gate" was therefore not a
  gate on the SIM's own progress at all; it was a gate on whatever number the
  caller happened to remember to pass. Any dispatch site that forgot the
  parameter — or a future caller unaware the field was load-bearing — bypassed
  it silently, with no error, no ignored-event log entry indicating why.
- Fix: Moved the threshold into AUTHORITATIVE STATE, set exactly once at world
  construction (`spine.totalChoicePoints`, passed as a constructor option
  alongside `archetype`/`difficulty`), and changed the gate to read
  `s.learningIdx >= s.totalChoicePoints` — a value already sitting in state,
  never re-suppliable per-dispatch. A world built with no explicit
  `totalChoicePoints` defaults to `0`, meaning "ungated" (matches every
  pre-existing test, e.g. the golden demo script, which never touches the
  spine at all) — an explicit, visible default rather than a silent gap.
- Why this fix: The general principle: a structural gate must never depend on
  a value the SAME command that's trying to pass the gate also gets to supply.
  If the threshold can travel with the attempt, the attempt can simply not
  bring it (or bring a friendlier one). The threshold has to live somewhere
  the gated command cannot influence — construction-time state is the
  cheapest such place in a `command -> reduce -> events` architecture,
  because "when was this world built" is already a privileged, one-time
  moment upstream of any gated command.
- Rule of thumb: When a reducer command carries BOTH the attempt to cross a
  gate AND a parameter the gate check reads, ask whether omitting that
  parameter (accidentally or otherwise) silently opens the gate. If yes, the
  threshold belongs in state set before the gated command ever exists, not in
  the gated command's own payload — regardless of how convenient it is for
  the caller to just pass it along each time.
- Provenance: Verified first-hand. Caught by a smoke test that specifically
  tried a bare, param-less `ADVANCE_SPINE` immediately after a correctly-
  parameterized attempt had been (correctly) blocked — the asymmetry between
  the two attempts is what exposed the bypass. Fixed in the same pass and
  re-verified: the same bare dispatch now stays blocked, and a fresh
  regression test (`a bare ADVANCE_SPINE with no payload cannot bypass the
  gate`) locks it in.
- Link: commit "P6: the retelling — a real, playable spine, closed loop to
  saga.v5" in pappydapimp69/the-game-the-recursion.
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-quest-offer-batch.md#E1 · compatible · no sandbox · Sandbox: `sandbox-exclusive-offer-command-payload.js`
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-recursion-wrong-sky-withheld-command-is-an-unpinnable-gate.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E34 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-09-28 · projects/local__sandbox-kernel-system-architecture.md#E1 · compatible · sandboxes/2026-09-28__train-gap-b04.py · session 2026-09-28, brain train gap batch 4 loop 18
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-the-recursion.md#E17 · compatible · no sandbox · session (brain train on groups and test 5 new edges), no code change — a recorded-lessons synthesis

## E1 — reducer mutates a field world constructor never initialized
- Date: 2026-07-09
- Project: pappydapimp69/the-game-the-recursion
- Tags: [gamedev][state]
- What: A reducer case (`CHOOSE_OPTION`) incremented `state.spine.learningIdx
  += 1`, but the world constructor (`makeWorld`) only ever set
  `spine: { stage: 0, variantOf: {} }` — `learningIdx` was never present on
  the object. `undefined + 1` is `NaN`, and every subsequent increment stayed
  `NaN` (a number `+= 1` on `NaN` is still `NaN`).
- Why built: A new spine stage ("the learning") needed a running count of how
  many of its choice points the player had answered, gating the stage
  transition once all of them were done. The reducer case was written first
  (`recordTrait(...); state.spine.learningIdx += 1;`), assuming the field
  already existed the way `stage` did.
- Design: `world.js` and `reduce.js` are two separate files edited in the same
  pass — `reduce.js`'s new case referenced a field that was supposed to be
  added to `world.js`'s `spine` object in the same change, but the edit to
  `world.js` was written slightly later and the connection wasn't rechecked.
- Got right: Nothing about the trait-recording half of the command was wrong
  — `recordTrait` fired correctly and the axis sums were fine. Only the
  counter specific to this new stage was broken.
- Where/why it failed: Running the actual scripted spine (dispatch
  `ADVANCE_SPINE`, three `CHOOSE_OPTION`s, then attempt to leave the stage)
  surfaced it immediately: `learningIdx now NaN` printed from a debug script,
  and the stage-transition gate (`learningIdx >= totalChoicePoints`) with
  `NaN` on the left side is false no matter what's on the right — so the
  spine silently got stuck at stage 1 forever, with no thrown error anywhere.
  JavaScript's silent `undefined -> NaN` coercion on `+=` is exactly the "one
  NaN silently poisons everything downstream, no error thrown" shape this
  project's own memory catalog has hit before, just in a different subsystem
  (there: a `.z` written on a Vector2; here: a wholly-missing initializer).
- Fix: Added `learningIdx: 0` to the `spine` object literal in `makeWorld`,
  alongside `stage: 0`, at the exact point the field was designed.
- Why this fix: The reducer case and the constructor initializer are two
  halves of the SAME piece of state and must be authored (or at minimum
  reviewed) together — a case that mutates `state.X.Y` is a hard requirement
  that the constructor already put `Y` on `X` with a sane starting value.
  There is no runtime type system here to catch the gap; only running the
  actual code (or a schema/shape check) surfaces it.
- Rule of thumb: Whenever a reducer case is added that increments/mutates a
  NEW nested field on state (`state.a.b += ...`, `state.a.b.push(...)`, etc.),
  immediately re-open the constructor and confirm `b` is initialized there —
  don't trust that "I'll add it" from a few minutes earlier actually landed.
  A quick, cheap habit: grep the constructor for the exact field name right
  after writing the reducer case that touches it, before running anything.
- Provenance: Verified first-hand — caught by directly instrumenting a debug
  script that dispatched the real commands and printed the resulting events
  and state after each one; `learningIdx now NaN` was visible in that output
  before any test suite ran. Fixed and reverified via the full smoke suite
  (the scripted spine playthrough now reaches its terminal stage correctly).
- Link: commit "P6: the retelling — a real, playable spine, closed loop to
  saga.v5" in pappydapimp69/the-game-the-recursion.
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-dog-recursion-nan-gate-polarity.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-sparse-map.md#E1 · compatible · no sandbox · Sandbox: `sandbox-sparse-map-zero-nan.js`
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E6 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
