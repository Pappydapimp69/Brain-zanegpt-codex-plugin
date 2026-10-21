# pappydapimp69/the-game-the-answering-deep — lessons

Project: pappydapimp69/the-game-the-answering-deep. Newest first.

---

## E13 — the game the answering deep shared rng stream is an ordinal space
- Date: 2026-07-13
- Project: pappydapimp69/the-game-the-answering-deep
- Tags: [determinism][architecture][testing]
- What: Composing `the-game-the-answering-deep#E3` (a shared single-stream seeded RNG means an unrelated content change — gating a free-roam enemy behind a quest — shifts every subsequent `nextInt()` draw in a tick, silently flipping a passing probabilistic smoke test with zero logic change to the system under test; the fix shipped was to structurally isolate that one test) with `sandbox-combined-save-system#E2` (an ORDINAL/positional reference into a reshapeable space — an array index, a program counter — fails SILENTLY, valid-but-wrong, when the space is reshaped; a SYMBOLIC reference — a stable name/id — fails LOUDLY, a detectable dangling reference instead; fix: address by symbolic key, not position) found that a shared RNG stream's linear draw sequence is itself an ordinal/positional space in E2's exact sense, and E2's general fix (symbolic addressing beats positional addressing under reshape) transfers directly and completely closes the underlying bug class E3 only patched one instance of.
- Why built: `brain train group` surfaced `the-game-the-answering-deep + sandbox-combined-save-system` as an untested seam requiring sandbox verification, not just reasoning, per current policy (tension T22).
- Design: Deterministic Node.js sandbox (mulberry32 seeded, zero wall-clock/Math.random). Two architectures built side by side: (A) one shared stream — mirrors the real E3 bug shape: patrol AI rolls 2 draws/tick per entity unconditionally, then a 1-D fire cellular automaton rolls spread checks against left/right neighbors, both drawing from the same generator in fixed order; (B) symbolically-keyed substreams — each patrol entity and the fire system get their own private generator derived via FNV-1a hash of `masterSeed::key`. Tested all three reshape operations E2 names (removal, insertion, reorder) against both architectures, plus a fixed-population replay-safety check, plus a 500-seed x {ticks, spreadChance, playerPos} = 30,000-config parameter scan to measure how routine the flip is under ordinary (non-cherry-picked) parameters.
- Got right: Tested all three of E2's named reshape operations (not just the one — removal — the real E3 bug happened to hit) to confirm the mechanism is general, not specific to that one scenario. Confirmed the keyed-substream fix preserves fixed-population replay-safety with bit-identical full traces (not just matching pass/fail booleans), ruling out "isolation traded away determinism to get invariance" as a hidden cost. Ran a large parameter scan (30,000 configs) instead of a single demonstration to establish the flip is routine, not a rare edge case, matching how the real E3 bug surfaced from an ordinary smoke test.
- Where/why it failed: Under the shared-stream architecture, removing, inserting, or reordering unrelated population members each independently flipped the fire-spread outcome (e.g. `caughtFire: false` with one population, `true` at a different tick with another) with zero change to the fire logic itself. Across the 30,000-config parameter scan, this flip occurred in 8793 configs (~29%) — confirming it as a routine occurrence, not a cherry-picked edge case. Under the keyed-substream architecture, all three reshape operations produced bit-identical full tick-by-tick fire traces regardless of population changes (0 flips), while fixed-population replay across two independent runs remained identical (replay-safe).
- Fix: Not applied to shipping code (flagging only, per instructions — this is a from-first-principles reimplementation of the documented mechanics, not a claim about current exact source lines; the actual `state.rng`/`ai.js`/`fire.js` were not re-cloned for this composition). If `state.rng` is still a single shared stream as E3's own description states, the general fix is to give each independent RNG-consuming concern (each entity, each subsystem) its own substream keyed by a stable name/id, rather than a single linear draw sequence — the same generalized fix `save-system#E2` already names for ordinal references generally.
- Why this fix: E3's shipped fix (isolate one specific smoke test from the shared stream) treats the symptom at the one call site it broke; it does not close the underlying architectural choice, so it leaves every OTHER current or future probabilistic test/mechanic sharing that same stream exposed to the identical silent entanglement from any future entity-population change. The keyed-substream architecture is strictly stronger: one architectural change protects every current and future RNG consumer against every future reshape, rather than requiring each new probabilistic test to be manually walled off as a recurring maintenance cost.
- Rule of thumb: A single shared-stream PRNG's draw sequence is an ordinal/positional space exactly like an array index or program counter — any subsystem implicitly relying on "whatever draws happen to land next" is an ordinal reference into that space, and inherits the identical failure signature ordinal references generally have under reshape: silent, valid-but-wrong divergence (every draw still "succeeds," it's just now the wrong draw) rather than a loud, detectable error. When a probabilistic-test-flips-from-unrelated-change bug (E3's shape) is diagnosed as "shared RNG stream entanglement," don't treat the fix as scoped to the one broken test — recognize it as a save-system#E2-shaped ordinal-vs-symbolic addressing problem, and consider the general fix (symbolically-keyed substreams per concern) instead of per-instance isolation, since the general fix protects every present and future consumer of the stream in one change.
- Provenance (verified/assumed): VERIFIED first-hand — deterministic Node.js sandbox (mulberry32, no wall-clock/Math.random), tested all three of E2's named reshape operations (removal, insertion, reorder) against both a shared-stream and a keyed-substream architecture, confirmed the shared-stream architecture flips under all three (matching E3's real bug shape) while the keyed-substream architecture produces bit-identical traces under all three plus preserves fixed-population replay-safety, and ran a 30,000-config parameter scan (500 seeds x ticks x spreadChance x playerPos) finding the flip occurs in ~29% of ordinary configurations. This composition is a from-first-principles reimplementation of the documented mechanics (matching E3's own textual description of `state.rng`/`ai.js`/`fire.js`); its scope stops short of the exact current source lines of the live repo — no live-unfixed bug is being asserted with high confidence, only an architectural risk worth checking against the real source.
- Composed: the-game-the-answering-deep/E3, sandbox-combined-save-system/E2
- Link: session (brain train 3 groups + 2 edges, sandboxed until satisfied, loop 3), sandbox scripts rng-ordinal-vs-symbolic.js and scan.js, no code change to a shipping project

## E12 — the game the answering deep constant roll count is necessary not sufficient
- Date: 2026-07-13
- Project: pappydapimp69/the-game-the-answering-deep
- Tags: [determinism][testing][gamedev]
- What: `the-game-the-waiting-city#E9` established that every AI decision must consume a CONSTANT number of RNG rolls regardless of outcome, explicitly framed as protection against "a later content tweak silently re-perturbing unrelated entities' rolls in the same tick." `the-game-the-answering-deep#E3` shows that discipline being followed correctly (patrol AI consistently rolls exactly 2 rolls/tick, "always roll regardless of outcome, by deliberate determinism discipline") — and RNG entanglement happening anyway: an unrelated content change (gating a previously-free-roam enemy behind a new quest, matching an already-established pattern) broke a passing fire/burn residual-damage smoke test with zero logic changes to the tested system, because the total SET of active entities in a tick changed, shifting every subsequent entity's position in the shared RNG stream — a class of entanglement constant-per-decision roll counts don't cover at all.
- Why built: `brain train group` surfaced `the-game-the-answering-deep + the-game-the-waiting-city` as an untested seam; reading both projects' RNG-discipline entries revealed waiting-city#E9's stated protection is narrower than its own framing suggests — it covers "does a decision's OUTCOME change its own roll count," not "does the POPULATION of decision-makers change."
- Design: N/A — a recorded-lessons synthesis, not a new build.
- Got right: answering-deep#E3's own fix already correctly targeted the actual layer where the gap lives — not the sim's RNG discipline (which was already correct and stayed unchanged) but the TEST's own isolation, structurally excluding other RNG-consuming entities from the scenario under test rather than tuning coordinates to happen to work against the current stream. Composing the two entries surfaces WHY that was the right fix and waiting-city#E9's own discipline couldn't have prevented this class of break: constant-roll-count-per-decision is a SIM-correctness property (replay stays bit-exact for a fixed entity population), not a TEST-isolation property (a probabilistic test asserting on stream-position-dependent outcomes is coupled to total draw count regardless of how disciplined any individual decision is).
- Where/why it failed: N/A for the composition itself — both source fixes were already correct and complete for what each was solving. The gap is that reading either entry alone doesn't make clear that BOTH disciplines are needed simultaneously and cover different failure classes: waiting-city#E9's discipline (constant rolls per decision) is necessary for sim-level determinism to survive CONTENT changes that alter a decision's branch, but is NOT sufficient to make PROBABILISTIC TESTS immune to entanglement from content changes that alter entity POPULATION — that requires the separate, additional discipline answering-deep#E3's fix demonstrates (structurally isolate the mechanic under test from the shared RNG stream).
- Fix: Not applicable — both source projects already applied the correct fix for their respective layer (sim discipline in waiting-city, test isolation in answering-deep); this entry names the combined, complete rule for future test-authoring in any project sharing this sim architecture.
- Why this fix: A team that only knows waiting-city#E9's rule might reasonably (and incorrectly) conclude "our AI already follows constant-roll-count discipline, so our probabilistic tests are safe from unrelated content changes" — answering-deep#E3 proves that inference false, and the combined rule prevents that specific, plausible mistake.
- Rule of thumb: Constant-roll-count-per-decision (waiting-city#E9) is necessary for a deterministic sim's replay to survive content changes that alter a decision's own branch, but it is NOT sufficient to make a multi-tick probabilistic TEST immune to entanglement from content changes that alter the total entity population sharing the tick — those are two different disciplines addressing two different failure classes, and a test suite needs BOTH: the sim's own constant-roll-count discipline, AND explicit isolation of whatever mechanic a probabilistic test asserts on (exclude other RNG-consuming entities, or assert on relative/isolated behavior rather than absolute stream position) — neither discipline substitutes for the other.
- Provenance (verified/assumed): VERIFIED first-hand — both source entries (waiting-city#E9, answering-deep#E3) read directly; the composition and the "necessary but not sufficient" framing is new reasoning in this session, not independently re-verified against either project's live source beyond what each entry already verified for itself.
- Composed: the-game-the-waiting-city/E9, the-game-the-answering-deep/E3
- Link: session (brain train on groups and test 5 new edges), no code change — a recorded-lessons synthesis

## E11 — answering deep fire generation cap
- Date: 2026-07-09
- Project: pappydapimp69/the-game-the-answering-deep
- Tags: [gamedev][simulation][cellular-automaton]
- What: A thrown-molotov fire hazard, capped to "spread only a few tiles and
  burn out in a couple seconds" via a fixed Chebyshev radius from its origin,
  never actually extinguished in live play — it kept relighting itself
  indefinitely within that radius instead of dying out.
- Why built: `fire.js` models fire as a small cellular automaton: each tile
  has a fuel counter that decays every TICK, and every open neighbor gets one
  fixed-probability spread roll per TICK. A hard cap on how far any single
  ignition could travel (`MAX_SPREAD_RADIUS`, checked against the ignition's
  remembered origin point before each spread roll) was added specifically so
  a molotov couldn't grow into an unbounded, room-filling blaze.
- Design: A fire tile is plain `{fuel}` state keyed by coordinate, plus one
  remembered `ignitionOrigin` for the whole blaze. Every TICK: each lit
  tile's `fuel` decays by a fixed amount and the tile is deleted outright
  once it hits 0 — no record is kept that it was ever lit. Independently,
  each lit tile rolls one fixed-probability spread check against every open
  neighbor, gated ONLY by `distance(ignitionOrigin, neighbor) <=
  MAX_SPREAD_RADIUS`; a won roll (re)creates that neighbor as a fresh lit
  tile with full fuel. Decay and spread are two separate per-tick
  mechanisms with no shared memory between them.
- Got right: The radius cap DID correctly bound the fire's spatial extent —
  it truly never spread further than the radius from its origin, exactly as
  designed and as its own dedicated test verified.
- Where/why it failed: A radius cap only bounds WHERE a tile can be lit, not
  HOW MANY TIMES. A tile whose fuel reaches 0 is simply deleted with no
  memory of ever having burned. Any of its still-lit NEIGHBORS — which share
  the same origin and are still within the same radius — can roll a fresh
  catch against that now-"unlit" tile on a later tick, re-igniting it as if
  for the first time. With several tiles alive at once inside a small,
  fully-open radius, this created a self-sustaining ping-pong: the blaze
  visually behaved like a real fire (individual tiles catching and dying)
  but the POPULATION never reliably hit zero, because total ignition events
  over the object's lifetime were literally unbounded — only reach was
  capped, not count.
- Fix: Replaced the geometric radius model with a generation-capped spawn
  BUDGET. Every fire tile stores `{fuel, generation, spawnsLeft}`; the root
  ignition is generation 0 with a fixed child allowance (e.g. 5), each
  spread child is generation+1 with its OWN (smaller) allowance (e.g. 2),
  and generation 2+ gets zero allowance. A tile only converts a successful
  spread roll into an actual ignition while ITS OWN `spawnsLeft > 0`,
  decrementing on every use; the budget belongs to the SPREADING (parent)
  tile and is spent the instant it's used, regardless of whether the target
  location has been on fire before. Total ignition events across one whole
  blaze's lifetime is now a small fixed number (1 + 5 + 5*2 = 16 in this
  case) that can only ever decrease, never replenish — so full
  extinguishment is structurally guaranteed in a small bounded number of
  ticks, independent of how favorably the RNG rolls.
- Why this fix: A cap on WHERE (radius/distance from origin) does not imply a
  cap on HOW MANY TIMES a location can be relit by different spreaders
  sharing that same bounded area — those are two independent invariants, and
  a self-sustaining local hazard only needs the FIRST one violated to read as
  "never truly extinguishes" even though it's honestly, individually, always
  decaying. Only a finite, non-replenishing total-event budget (attached to
  the spreader, spent on use, never restored) actually forces eventual
  termination; a spatial cap alone cannot, no matter how tight the radius.
- Rule of thumb: For any local, self-propagating hazard/effect in a
  cellular-automaton-style sim (fire, poison gas, an infection, a chain
  reaction) that must eventually fully die out: a cap on spatial REACH
  (radius from origin, blast distance, etc.) only bounds where it can go, not
  how many times a location can be re-triggered by neighbors sharing that
  same bounded area. If individual cells have no memory of having already
  fired, re-triggering can sustain the effect indefinitely inside the
  reachable area even though the cap is textbook-correctly enforced. Give
  the effect a genuinely finite, monotonically-decreasing TOTAL EVENT BUDGET
  (e.g. a generation-based spawn allowance owned by the spreading cell, not
  the target) instead of — or in addition to — a spatial cap, whenever
  "eventually fully extinguishes" is itself a requirement, not just "stays
  small."
- Provenance: Verified first-hand — user-reported in live play ("it looks
  like a real fire... but then those newly lit tiles relight the old tile
  again so it burns forever"), root-caused by re-reading `fire.js`'s spread
  loop and confirming a burnt-out tile carries no post-death state, fix
  designed collaboratively with the user (who proposed the generation/budget
  shape directly), and confirmed post-fix via both a live-in-browser replay
  and a dedicated smoke test that runs `stepFire` up to 30 times from a
  single root ignition and asserts the fire tile set reaches exactly zero.
- Link: commit "Stage 9: Lurker/Shell return, fire generation-cap rewrite,
  Igniter tuning, flashbang mechanic" in
  pappydapimp69/the-game-the-answering-deep.

## E10 — answering deep state aware quest dialog
- Date: 2026-07-09
- Project: pappydapimp69/the-game-the-answering-deep
- Tags: [gamedev][gamedesign][state]
- What: Wren's NPC dialog (`wrenDialogFor`, src/app/quest-dialog.js) is computed live from the current quest-chain progress instead of being a single flat 3-line array shown identically at every stage of the game. The function is a priority ladder of `done()/active()/offered()` checks that returns different real spoken lines for each milestone (learn-to-listen, the three-way branch, the-sounding-line, sound-the-deep, the finale, the arc-complete epilogue).
- Why built: Playtest feedback: "the quest dialog needs to be rewritten, there really isn't anything there right now" — the one static array made the NPC say the same thing at the intro as at the finale, so it read as placeholder and gave the player no read on where they were in the chain.
- Design: A pure function of `world` that mirrors the exact priority structure game.js's `computeGuide()` already uses for the HUD banner (most-progressed state checked first, falling through to earlier stages), but authored as prose Wren would actually say rather than a one-line objective hint. Reads `world.quests.completed/active/offered`, `world.arc.complete`, `world.arc.bossSpawned`.
- Got right (the choice made): Derive the dialog text from live quest state at read time via a priority-ordered state machine, rather than storing static per-NPC text (or hand-authoring a separate line set triggered imperatively at each quest transition).
- Where/why it failed (the tradeoff accepted): A static text array (or a switch keyed by an explicit "current chapter" enum) is trivially predictable and every possible line is visible in one place. Deriving lines from live quest booleans gives that up: the dialog is now COUPLED to quest ids and their progression semantics — the ladder's ordering is load-bearing (a mis-ordered `done()` check shows the wrong stage's lines), it silently references quest ids that must stay in sync with content.js, and there is no single place that lists "what Wren says" — you have to mentally execute the ladder against a hypothetical quest state to know. Renaming or removing a quest id can leave a branch permanently unreachable with no compile error.
- Fix (what was implemented instead of the naive approach): One priority-ordered pure function returning the lines for the most-progressed matching state, reusing the already-proven `computeGuide()` ordering discipline, instead of a static array or scattered imperative "on quest X complete, set Wren.lines = …" mutations spread across the reducer.
- Why this fix: Reusing the HUD's existing most-progressed-first ordering means the dialog and the objective banner can never disagree about what stage the player is in, and a pure function of world state stays replay-safe and testable (the smoke suite drives it through the whole accept-to-completion path). Imperative per-transition mutation would have spread dialog state across the reducer and risked the same last-write races the modal system already hit.
- Rule of thumb: For NPC/quest dialog that must track progress, compute the line from live quest state with a priority ladder (most-progressed first) and reuse whatever ordering your objective/HUD system already trusts — but treat it like data-driven content: the branch ids are now unchecked references, so cover the ladder with a smoke playthrough so a renamed/removed quest can't silently strand a line.
- Provenance (verified/assumed): Verified first-hand by reading src/app/quest-dialog.js in full (the `wrenDialogFor` priority ladder and its header stating it mirrors `computeGuide()`), and the Stage 10 commit body describing the rewrite from "one flat 3-line array." The separate same-dispatch modal-overwrite race fixed in the same commit is a distinct BUG lesson already filed (incoming/…modal-overwrite-race, #E5) and is not this entry.
- Link: commit a2ffa9a (Stage 10: "Wren's dialog is now state-aware … instead of one flat 3-line array")

## E9 — answering deep ping gated onboarding
- Date: 2026-07-09
- Project: pappydapimp69/the-game-the-answering-deep
- Tags: [gamedesign][state][gamedev]
- What: To teach the player the game's signature verb (PING), the ambient "you can see a little around yourself" sight radius is gated behind a new authoritative `player.hasPinged` flag — off at spawn, permanently set the instant the player first pings. Before that first ping the world renders fully black except the player's own tile. There is no tutorial string; discovery is forced by the darkness plus the always-visible control legend.
- Why built: Playtest feedback was that ping — the whole game's core verb — went unintroduced and players couldn't find the controls. The team wanted onboarding without adding explanatory UI/tutorial copy.
- Design: One authoritative boolean (`state.player.hasPinged`), one line in reduce.js's PING case that sets it one-way, and one condition in renderer.js that only grants the ambient radius when it's set. Persistent light sources (vents, fire, torches) are explicitly NOT gated — those are a separate always-on modality; only the generic self-illumination radius is withheld.
- Got right (the choice made): Teach the signature verb through a deliberately information-starved world state (a black screen that resolves the moment you try the verb) rather than by adding a tutorial string or tooltip.
- Where/why it failed (the tradeoff accepted): A tutorial string ("Press Q to ping") is unambiguous, universally understood, and impossible to get stuck on. Gating sight instead gives that up: a brand-new player is dropped into a fully black screen with no explicit instruction, which reads as a bug or a broken build if they don't connect it to the control legend, and the whole scheme leans entirely on that legend being present and read. It trades guaranteed comprehension for discovery, and a player who never experiments can stall at a black screen.
- Fix (what was implemented instead of the naive approach): A one-way `hasPinged` gate on the ambient radius (one flag, one reducer line, one renderer condition, no new UI) instead of a tutorial modal/string — deliberately making the absence of the verb visible (nothing to see) so the only always-shown affordance (the control legend) becomes the thing the player tries.
- Why this fix: Onboarding that makes the player DO the core verb once, unprompted, teaches it more durably than copy they skip — and here it does double duty as fiction (the deep genuinely is lightless until you call into it), so the mechanic and the theme reinforce each other at zero UI cost. Acceptable only because a persistent, always-visible control legend already existed to catch the player.
- Rule of thumb: You can teach a signature verb by withholding the world until the player uses it (make the absence visible), instead of writing tutorial copy — but only ship it when there's an always-present affordance pointing at the verb, or "elegant discovery" becomes "stuck on a black screen." Gate only the generic/ambient affordance; leave separate always-on modalities alone.
- Provenance (verified/assumed): Verified first-hand — `state.player.hasPinged` is set one-way in src/sim/reduce.js:401 ("one-way: the ambient sight radius gate opens for good") and read as the ambient-radius condition in src/app/renderer.js:161-175, with persistent light sources unaffected. Intent ("rather than add a tutorial string") is stated in the Stage 5 commit body.
- Link: commit 56e4dc5 (Stage 5: ping-gated onboarding — the deep starts genuinely dark)

## E8 — answering deep ordered dither choice
- Date: 2026-07-09
- Project: pappydapimp69/the-game-the-answering-deep
- Tags: [gamedev][gamedesign][rendering]
- What: To make the already-computed graduated light falloff (light.js's 0-100 field) actually visible on screen — the renderer's tile gate had been binary (drawn full-brightness or skipped) — the team overlaid an ORDERED DITHER (a fixed 4x4 Bayer threshold pattern, src/app/dither.js) rather than a smooth alpha gradient. Six precomputed darkness buckets (0/20/40/60/80/100), each a fixed count of "on" Bayer cells, are looked up per already-drawn tile.
- Why built: The falloff existed only in sim math; players couldn't eyeball how comfortable a tile would be for a light-averse creature. The natural fix — fade tiles with a per-pixel alpha gradient — was rejected.
- Design: A 4x4 Bayer matrix (sized to match the game's own 4x4 native tile-sprite grid), six threshold buckets baked once at module load into tiny pixel defs, overlaid on top of whatever is already drawn. The darkest "visible" bucket stops at 14/16 cells, never full black; true black is reserved for tiles that fail the visibility gate and are never drawn at all.
- Got right (the choice made): Fake the gradient with a deterministic ordered-dither pattern in the game's existing blocky pixel grain, instead of a smooth alpha gradient.
- Where/why it failed (the tradeoff accepted): A smooth alpha gradient is the obvious, higher-fidelity way to show a continuous 0-100 field and would give truly smooth falloff. The dither choice gives that up on two fronts: (1) fidelity — falloff is quantized into six visible steps with a stippled texture, not a continuous ramp; (2) it is BAKED to opaque pixels — pixelart.js writes each pixel at alpha 255 or skips it, so there is no per-pixel alpha to fade with, meaning "semi-transparent" had to be faked via a near-black (not true black) color plus varying cell counts. And to keep a barely-lit tile from being swallowed, the darkest bucket is deliberately capped at 14/16, so a lit-but-dim tile can never render as fully dark even when the field says it is near zero.
- Fix (what was implemented instead of the naive approach): DITHER_DEFS precomputed at module load, a `ditherBucket()` snap-to-nearest-20, and a single overlay draw per already-culled tile — reusing pixelart.js's existing cached nearest-neighbor sprite pipeline — instead of introducing per-pixel alpha blending that the renderer otherwise never uses anywhere.
- Why this fix: In a hand-authored, nearest-neighbor, no-anti-aliasing pixel-art renderer, a soft alpha gradient reads as a foreign technique dropped into a blocky world; matching the falloff's grain to the same chunkiness as every other sprite keeps the whole frame coherent, and costs only a module-load precompute plus one cached lookup per tile.
- Why this fix: A visual technique should match the medium it lives in even at the cost of raw fidelity; consistency of "grain" reads as intentional art, where a lone smooth gradient reads as a bug.
- Rule of thumb: To visualize a continuous field inside a pixel-art (or any deliberately-lo-fi) renderer, reach for an ordered dither in the existing grain before a smooth alpha gradient — accept quantization and a capped darkest step in exchange for looking native. Reserve the true extreme (full black / zero) for the actual cutoff, never for a value that's still being drawn.
- Provenance (verified/assumed): Verified first-hand by reading src/app/dither.js in full — the header states the smooth-alpha rejection and the pixelart opaque-pixel constraint, `THRESHOLDS` caps the 100 bucket at 14, and `DITHER_DEFS`/`ditherBucket` implement the precompute-and-snap. NOTE: the general reusable technique is also already captured in the ideas repo (idea-repository.md, "ordered-dither-for-graduated-visibility"); this memory entry records the project-specific DECISION and the concrete costs accepted (quantization, no per-pixel alpha, capped darkest bucket), which is the tradeoff framing, not the portable recipe.
- Link: commit 9724a54 (Stage 8: "a new ordered-dither overlay … not a smooth alpha gradient")

## E7 — answering deep lightaverse role field
- Date: 2026-07-09
- Project: pappydapimp69/the-game-the-answering-deep
- Tags: [gamedev][gamedesign][state]
- What: The three enemy behaviour variants that ship in Phase 4 — quencher (a saboteur that snuffs unguarded torches), guardian (stands its post, never hunts), and flashbang (throws a flash bottle instead of a molotov) — are NOT separate enemy kinds. They are all the single `igniter` (`lightAverse`) kind, differentiated by a per-INSTANCE `role` string set in content.js (`igniter-elite1: role 'flashbang'`, `quencher1: role 'quencher'`, `igniter-guardian1: role 'guardian'`). The behaviour forks live as `if (e.role === 'quencher')` / `=== 'guardian'` / `=== 'flashbang'` branches inside the one shared `decideLightAverseAction` in ai.js.
- Why built: Stage 8 had already collapsed the whole bestiary down to the single Igniter played as hide-and-seek. Later feedback asked for three more distinct encounters (guard-the-flame saboteur, a stationary guardian, a flash-throwing finale boss). The team wanted the new content without reintroducing the per-kind plumbing (sprite, palette entry, stats block, quest-target existence gating, smoke coverage) that a brand-new enemy kind drags in.
- Design: One `lightAverse` decision function owns lurk/curious/flee for every Igniter; a per-instance `role` field selects a wholly separate sub-routine (quencher) or flips one predicate (guardian never goes curious; flashbang swaps the thrown bottle's `kind` to `'flash'`). Instances with no role fall through to the default hide-and-seek. The kind-level machinery (sprite, stats, `harmless`, quest existence-gating) is shared and authored once.
- Got right (the choice made): Model enemy behaviour VARIANTS as per-instance data (`role`) on one shared kind, dispatched by conditional branches in the shared decision function, rather than minting a new enemy kind (with its own sprite/palette/stats/validation surface) per variant.
- Where/why it failed (the tradeoff accepted): Separate kinds would have given each variant its own clean, independently-typed home and let the content validator/sprite-map checks treat it as a first-class id with compile-time-ish coverage. The role-field choice gives that up: the variants' logic is now hidden inside `if (e.role === '…')` branches in one growing function, so the differences are invisible to the kind registry, easy to miss when reading content.js (a `role` string is just data), and every new variant makes `decideLightAverseAction` accrete another special-case rather than adding a self-contained unit. There is no schema that enforces which role strings are valid.
- Fix (what was implemented instead of the naive approach): Instead of `kinds: { quencher, guardian, flashbangThrower }` each with duplicated sprite/stat/validation scaffolding, a single `igniter` kind plus a free-text `role` field per placed instance, read at the top of the shared decision function to route to a variant sub-routine or toggle a single predicate. The finale flash bottle reuses the exact molotov travel physics, only swapping the landed bottle's `kind`.
- Why this fix: When variants share ~90% of their behaviour and all their presentation, the incremental cost of a new kind (sprite + palette + stats + quest-existence gating + smoke tests, per the project's own data-driven-content discipline) dwarfs the cost of one data field plus a branch. Keeping them one kind means the shared hide-and-seek machine is authored and tested once and every variant inherits it for free.
- Rule of thumb: If a new "enemy/entity type" differs from an existing one only in a couple of behaviour beats and shares all its art and stats, add a per-instance variant tag and branch on it — don't mint a whole new type. Accept that the variants become less visible and lose per-type validation, and add an explicit allow-list / smoke assertion for the variant tags to claw some of that safety back.
- Provenance (verified/assumed): Verified first-hand by reading src/sim/ai.js (`decideLightAverseAction`, `decideQuencherAction`, the `e.role` branches and the guardian `&& e.role !== 'guardian'` predicate) and src/sim/content.js lines 185-187 (the three `role`-carrying instances of the one `igniter` kind). Design intent confirmed by the Stage 9/10 commit messages.
- Link: commits a2ffa9a (Stage 10: guardian + quencher roles) and 4e9a448 (Stage 9: flashbang per-instance role field)

## E6 — answering deep flashbang sim telegraph
- Date: 2026-07-09
- Project: pappydapimp69/the-game-the-answering-deep
- Tags: [gamedev][state][gamedesign]
- What: The flashbang's "landed, arming, about to go off" telegraph lives in AUTHORITATIVE sim state, not in the renderer. A thrown flash bottle lands, becomes a real pending bottle `{armed:true, armTicks: FLASH_ARM_TICKS}` in `state.hazards.bottles`, and counts down in the reducer's TICK case; detonation is one discrete authoritative event (`flash_detonated`, proximity-scaled). Only the screen WHITEOUT afterwards is presentation-only (src/app/flash-decay.js, a reversed charge-ramp decay curve). The same discipline is applied to enemy spawns (`ENEMY_SPAWN_DELAY_TICKS`): the entity genuinely isn't in `state.enemies` yet during its telegraph.
- Why built: The flashbang needed a fair, readable ~3-second "it's about to blow" warning window. The tempting cheap version is a renderer-side delay (draw the bottle, wait 3s of wall-clock, then apply the effect).
- Design: Arming and countdown are fields on the authoritative, fingerprinted `state`; the reducer drains an armed bottle each tick and emits the detonation as a discrete event scaled by chebyshev distance. The cosmetic whiteout reads that event and decays on its own clock in the presentation layer, owning zero gameplay consequence.
- Got right (the choice made): Put the telegraph/arming window in authoritative sim state (real, deterministic, fingerprinted) and keep only the cosmetic flash decay in the renderer — rather than implementing the delay as a renderer-only wall-clock timer.
- Where/why it failed (the tradeoff accepted): A renderer-only delay is cheaper: no new authoritative fields, no WORLD_VERSION bump, no golden-fingerprint churn, and the sim stays smaller. Putting the telegraph in sim gives that up — it adds `armed`/`armTicks` (and the spawn-delay analog) to the fingerprinted state, so it costs a WORLD_VERSION/fingerprint update and enlarges the authoritative surface that every save and replay must carry. The payment buys correctness the cheap version can't: the telegraph and detonation are the SAME timeline the sim runs, so they replay bit-exact and a headless golden replay actually exercises them, and the delay can't drift or be skipped by a dropped frame.
- Fix (what was implemented instead of the naive approach): A landed flash bottle is re-stored as an `armed` bottle with an `armTicks` countdown decremented in reduce.js's TICK case, detonating via a discrete `flash_detonated` event — instead of a `setTimeout`/wall-clock delay in game.js. The whiteout intensity/decay is the ONLY part left to flash-decay.js, deliberately carrying no sim effect.
- Why this fix: In a determinism-first sim guarded by a golden-fingerprint replay, any gameplay-affecting timing that lives only in the presentation layer is invisible to the replay and can silently diverge — so anything that changes what happens to the player (a telegraph that gates real damage) belongs in the authoritative reducer even at the cost of state-surface growth; only genuinely cosmetic decay stays out.
- Rule of thumb: Draw the sim/presentation line by consequence, not by convenience: if a delay/telegraph changes what happens to the player, it goes in the authoritative (fingerprinted, replayable) state even though that costs a version bump and a bigger save; keep the renderer for effects that own zero gameplay outcome. A wall-clock timer in the view layer that gates real damage is a determinism hole.
- Provenance (verified/assumed): Verified first-hand by reading src/sim/reduce.js (the header at lines 43-74 explicitly contrasts the "honest, sim-enforced telegraph" against a renderer-only delay; the armed-bottle countdown at lines 137-157 and the discrete `flash_detonated` event at 146) and the flashbang description in the Stage 9 commit body ("a real 3-second sim-state telegraph (not a renderer-only delay) … the screen whiteout itself is a presentation-only decay").
- Link: commit 4e9a448 (Stage 9: flashbang mechanic)

## E5 — answering deep detection vs comfort axes
- Date: 2026-07-09
- Project: pappydapimp69/the-game-the-answering-deep
- Tags: [gamedesign][state][gamedev]
- What: The light-averse Igniter reacts to TWO different light-derived signals that are deliberately kept as separate axes: DETECTION is a discrete event — `state.echo.lit`, meaning a fresh PING pulse just touched this tile — and is the only thing that makes the creature flee/startle/throw. COMFORT is a continuous field — `lightAt()` on light.js's graduated 0-100 scale — and only governs whether the creature is willing to STOP on a tile (`LIGHT_IDLE_THRESHOLD`) or which way to break a flee tie. Standing/persistent light (torches, vents, fire, the player's charge glow) never reveals the creature by itself.
- Why built: Phase 4's signature verb is the echo ping — "ping to reveal the world, but every ping tells sound-reactive things where you are." For that to be the meaningful risk, being SEEN had to be tied to the act of pinging, not to ambient brightness. But the game also wanted light to matter physically (a thing that hates light shouldn't want to sit in it), so light couldn't be purely cosmetic either.
- Design: `decideLightAverseAction` reads `state.echo.lit[x,y]` as a boolean reveal trigger (curious/lurk -> flee, plus a one-shot throw if caught close). Separately it reads `lightAt()` only in two places: to refuse to end a tick at rest on a tile brighter than `LIGHT_IDLE_THRESHOLD` (18), and to bias `stepAwayFromDark` while fleeing. It otherwise crosses arbitrarily bright ground without hesitation while actually moving somewhere.
- Got right (the choice made): Split "am I detected" from "am I comfortable" into two independent inputs — a discrete pulse event for detection and a continuous field for comfort — rather than the intuitive single rule "bright tile = spotted."
- Where/why it failed (the tradeoff accepted): The single-signal model ("if the creature is standing in bright light, it's been seen") is simpler to implement, simpler to explain, and matches most players' first instinct. Splitting the axes gives that up: there are now two light-ish signals a reader must keep straight and never let bleed into each other, and the game must actively teach players the counterintuitive rule that lighting a torch next to a hiding thing does NOT flush it out — only a ping does. A player who assumes "I lit the room, so I can see it" is wrong by design, which is a real comprehension cost.
- Fix (what was implemented instead of the naive approach): Detection keyed strictly on the transient `echo.lit` set (pruned every tick, so it's a true event not a state), with comfort read from the persistent light field only for rest-eligibility and flee tie-breaks. Torches were then deliberately made LOUD (igniting one echo-reveals its surroundings like a pulse) so that light acquisition still carries a detection cost through the ping channel, not the brightness channel — closing the loop the split opened.
- Why this fix: Tying detection to the player's active, costly verb (the ping) rather than to a passive world property makes stealth a consequence of what the player DOES, which is more legible and more fair than punishing them for ambient conditions they didn't cause. Keeping comfort continuous but non-blocking lets light shape behaviour (where it rests) without turning it into a second, accidental detection system.
- Rule of thumb: When one world property (light, noise, heat) could plausibly drive several distinct mechanics, decide up front whether each mechanic wants the DISCRETE event or the CONTINUOUS field, and wire them to separate signals — don't let one number quietly mean both "detected" and "uncomfortable," or the two behaviours entangle and you can't tune one without moving the other.
- Provenance (verified/assumed): Verified first-hand by reading src/sim/ai.js — the `decideLightAverseAction` header explicitly names the two axes, the `revealed` check reads `state.echo.lit`, and the only `lightAt()` reads are the `LIGHT_IDLE_THRESHOLD` rest-gate and the darkest-neighbor override. Torch-loudness confirmed in the Stage 8 commit body.
- Link: commit 9724a54 (Stage 8: hide-and-seek redesign; "Two axes kept deliberately separate")
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E36 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E4 — answering deep silent sprite fallback recurrence
- Date: 2026-07-09
- Project: pappydapimp69/the-game-the-answering-deep
- Tags: [rendering][gamedev][content]
- What: A new enemy kind shipped with no entry in the kind-keyed sprite map,
  silently rendering as a plain colored square — the exact same class of bug
  a prior fix in this same project had already eliminated for every OTHER
  creature kind.
- Why built: `src/app/sprites.js` exports `ENEMY_SPRITES`, a plain object
  keyed by `enemyKind.id`; `renderer.js` does `const def =
  ENEMY_SPRITES[e.kind]; if (def) drawPixelSprite(...); else
  fillSquashed(...)` — a deliberate graceful fallback so a missing/typo'd
  key degrades to a colored block instead of crashing.
- Design: The fallback is correct defensive design in isolation (never
  crash on unmapped content), but it also means a missing map entry
  produces ZERO signal anywhere — no error, no failing test, no lint —
  because nothing in the content-validation ladder (`validate.js`) or the
  smoke suite checks that every `enemyKinds` id has a corresponding sprite;
  sprites are a presentation concern the sim-side validator has no reason
  to know about.
- Got right: The fallback itself, and `validate.js`'s general
  referential-integrity philosophy (every kind/id used somewhere must
  resolve) — this bug is specifically the one place that philosophy wasn't
  extended to the presentation layer.
- Where/why it failed: A new enemy kind (`igniter`) was added to
  `content.js` and to the AI/reducer logic, and worked mechanically end to
  end (spawns, fights, dies, drops loot) — the missing sprite was invisible
  in every automated test (sim-level tests never touch `sprites.js` at
  all) and only surfaced via an actual live playthrough with visual
  inspection.
- Fix: Added the missing `ENEMY_SPRITES.igniter` entry, verified with the
  same one-off "does every `CONTENT.enemyKinds` id have a matching sprite
  key" script the ORIGINAL instance of this bug (a different, larger stale-
  key mismatch across the whole kind set) was diagnosed with.
- Why this fix: Matches the established sprite-authoring pattern in the
  file exactly (a dedicated palette-letter set + a 10x10 silhouette
  distinct from every other kind) rather than introducing a new pattern.
- Rule of thumb: Whenever a kind-keyed content collection (enemy kinds, item
  types, quest objective types, etc.) has a PARALLEL kind-keyed presentation
  map that a graceful fallback silently covers for, adding a new kind to the
  content side is a two-file change, not one — and nothing will catch a
  forgotten second file unless you make it catch it. Added the cheap fix
  alongside this one: two smoke tests asserting every `enemyKinds`/NPC id in
  CONTENT resolves in `ENEMY_SPRITES`/`NPC_SPRITES`, turning this from "only
  visible on a live playthrough" into "fails the build" — the same coverage
  `validate.js` already gives every OTHER referential-integrity gap in this
  project, just extended one layer further into presentation.
- Provenance: Verified first-hand — found via live-QA Playwright screenshots
  (a plain colored square where every other enemy has a distinct sprite),
  confirmed via the same node-script sprite-mapping check used originally,
  fixed and re-verified visually.
- Link: commit "Bug pass: fix death wiping all progress, and a missing
  Igniter sprite" in pappydapimp69/the-game-the-answering-deep.
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E32 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-10-08 · projects/pappydapimp69__brainwork.md#E20 · compatible · sandboxes/2026-10-08__js-only-content-silently-indexes-empty-so-core-web-vitals-tiebreak-never-gets-to-run.py · observed RESULT: PASS 8/8 checks; csr page is empty until queue delay 10, empty forever when cost>budget or script errors, and CWV never rescues relevance 0; budget 60 > cost 50 rescues it · scheduled brain train auto pass 5, session_01StBYFbuqvtkXnufHNhQ8RJ

## E3 — answering deep rng entanglement
- Date: 2026-07-09
- Project: pappydapimp69/the-game-the-answering-deep
- Tags: [determinism][testing][gamedev]
- What: A passing smoke test (fire/burn residual-damage timing) broke after an
  unrelated content change — gating a previously-free-roam enemy behind a new
  quest — with no logic change to the system under test at all.
- Why built: The game's sim is a seeded-RNG, integer-only, fully deterministic
  reducer (`state.rng`, `nextInt(state.rng, n)` everywhere), fingerprint-replay
  tested. A new quest branch needed an existing free-roam enemy
  (`igniter1`) to become existence-gated (spawned only after its quest is
  accepted), matching the established anti-softlock pattern already used for
  every other quest-tied kill target.
- Design: Enemy AI (`ai.js`) consumes `state.rng` unconditionally for
  patrol-state entities — two rolls every TICK a patrolling enemy is
  processed, "always roll regardless of outcome" by deliberate determinism
  discipline (so replay never depends on how many neighbors/options happened
  to be open). This is correct and intentional in isolation.
- Got right: The per-entity roll discipline itself is sound — it's exactly
  why the sim stays bit-exact. The bug was downstream, not in that code.
- Where/why it failed: A smoke test constructed a fresh `makeWorld(1)`, put
  the player 6 tiles from an ignition point, then looped `TICK` up to 20
  times checking that residual burn damage stopped after a fixed window. It
  passed while `igniter1` was still free-roam (present in every fresh world,
  consuming 2 patrol rolls per TICK) and failed the moment `igniter1` became
  quest-gated (absent from a fresh world, consuming zero rolls) — because
  removing those rolls shifted EVERY subsequent `nextInt(state.rng, ...)`
  call in the run, including the unrelated fire-spread cellular automaton's
  spread rolls, which now happened to reach the player's new tile within the
  test's 20-tick window and re-ignited them. The test's assumption ("far
  enough that this can't be flakily reached by fire spread") was tuned
  against one specific RNG stream, not proven against the mechanic.
- Fix: Isolated the test from the cellular automaton entirely by walling off
  the ignition point's 4 neighbors before igniting, so it can never spread —
  matching an existing sibling test in the same file that already used this
  exact technique for a different assertion (fuel decay). The test now only
  exercises the residual-burn timer, the thing it actually claims to test.
- Why this fix: Isolating the code path under test from every OTHER
  RNG-consuming system is the only fix that doesn't just re-tune a coordinate
  and get lucky again under the next unrelated content change.
- Rule of thumb: In a single-seeded-stream deterministic sim, any test that
  loops many ticks and asserts on the OUTCOME of a probabilistic subsystem
  (spread, AI rolls, loot, etc.) is implicitly coupled to the total RNG draw
  count of everything else that ran in the same world — including entity
  population, which can change for reasons that have nothing to do with the
  system under test (a quest-gating change, a new enemy kind, content
  reordering). Multi-tick probabilistic tests must structurally isolate the
  mechanic being tested (block spread paths, remove other entities, etc.),
  not just pick coordinates/timings that happen to work against today's
  stream. A test that passes only because of an incidental RNG offset is a
  latent flake waiting for the next unrelated change.
- Provenance: Verified first-hand — found by running the full smoke suite
  after a git-committed content change, diagnosed by reasoning through
  `ai.js`'s patrol-roll code path and confirmed by isolating the fire tile
  and re-running (test went from failing to passing with no other change).
- Link: commit "Stage 7: a real branch point — the quest chain stops
  mirroring Phase 3's" in pappydapimp69/the-game-the-answering-deep.
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E33 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-prologue.md#E19 · compatible · no sandbox · session (brain train 3 groups + 2 edges, sandboxed until satisfied, loop 3), sandbox script rng_entangle_sandbox.mjs (live import of real repo source, real BFS pathfinder, verbatim-reproduced AI dispatch loop), latent fragility flagged in this same shipping repo, not fixed (pending explicit confirmation per this session's established pattern)
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-the-answering-deep.md#E12 · compatible · no sandbox · session (brain train on groups and test 5 new edges), no code change — a recorded-lessons synthesis
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-the-answering-deep.md#E13 · compatible · no sandbox · session (brain train 3 groups + 2 edges, sandboxed until satisfied, loop 3), sandbox scripts rng-ordinal-vs-symbolic.js and scan.js, no code change to a shipping project
- Cited-by: 2026-10-08 · projects/local__seeded-rng-save-load-vs-shared-stream-coupling.md#E1 · compatible · sandboxes/2026-10-08__seeded-rng-save-load-vs-shared-stream-coupling.py · observed RESULT: PASS resume exact=True shared-stream outcomes changed in 9/20 ticks, split streams in 0/20 · scheduled brain train pass 5

## E2 — answering deep respawn checkpoint
- Date: 2026-07-09
- Project: pappydapimp69/the-game-the-answering-deep
- Tags: [save][state][gamedev]
- What: A "respawn on defeat" feature silently wiped 100% of a player's
  session progress (quests, coins, inventory) AND immediately overwrote the
  on-disk save with the wiped state — with no error, no warning, framed to
  the player as a minor "you rise where you began" setback.
- Why built: The game's live loop (`game.js`) captures `let respawn =
  JSON.stringify(world)` once at `startGame()` and, on the player's HP
  reaching 0, does `world = JSON.parse(respawn)` to send them back to a
  known-good state rather than a hard game-over.
- Design: `respawn` was intended as a checkpoint, but was only ever assigned
  the ONE time, at boot (fresh new game OR a resumed save's initial load) —
  never reassigned anywhere else in the file. Meanwhile the REAL save
  (`saveGame(world)`, localStorage) IS correctly refreshed after every
  command, so the persisted save and the in-memory respawn checkpoint
  silently diverged the moment the player did anything at all.
- Got right: The actual save-to-disk logic was already correct and
  frequent (`dispatch()` calls `saveGame(world)` after every non-fatal
  command) — the bug was entirely in the SEPARATE, stale in-memory
  checkpoint used specifically for the death/respawn path, not in the save
  system itself.
- Where/why it failed: Any death, at any point past the first command of
  the session, restored the SESSION-START snapshot — not "recent
  checkpoint," but literally however far back `respawn` was last (i.e.
  never) refreshed. The defeat handler then called `saveGame(world)` on
  that stale-restored state, so even reloading the page didn't recover
  anything — the wipe was written straight to disk. A newly-added lethal
  hazard system in the same game (fire/burn damage, capable of killing a
  full-HP player in well under 15 seconds) turned this from a rare edge
  case into something a normal player pursuing new content would hit
  quickly and often.
- Fix: Two parts. (1) Refresh the checkpoint on the SAME gate as the save
  call (`if (!world.flags.ended && world.player.hp > 0) { saveGame(world);
  respawn = JSON.stringify(world); }`) so it always reflects the most
  recent alive, non-ended state. (2) Do NOT restore the checkpoint's
  literal position on respawn — teleport to the region's spawn point
  instead, fully heal, and clear any transient hazard status (e.g.
  "on fire"). Restoring literal death position turned out to be its own
  bug: a checkpoint refreshed this aggressively (every single command,
  including the one right before a fatal blow) can land the player
  immediately adjacent to the very enemy that just killed them — and since
  that enemy's real-time attack cooldown (tracked in a `game.js` closure
  variable, NOT part of saved/restored world state, so it survives a
  respawn untouched) had already elapsed by the time the hold-to-confirm
  UI gesture finished, the enemy could strike again the instant the world
  resumed, chain-killing before the player regained any control.
- Why this fix: Splitting "what checkpoint to restore" (recent progress)
  from "where to place the player" (a known-safe spawn tile) resolves both
  problems with one change, and matches what the feature's own flavor text
  already promised ("You rise where you began") — the ORIGINAL boot-only
  bug had accidentally gotten the position half of this right (boot is
  always safe) while getting the progress half catastrophically wrong; a
  naive fix that only refreshed the checkpoint would have gotten progress
  right while introducing the new adjacent-enemy chain-death failure mode.
- Rule of thumb: A "return to a safe/known state on failure" checkpoint has
  (at least) two independent axes — WHAT PROGRESS to keep, and WHERE/WHEN
  to place the player — and conflating them (one JSON snapshot standing in
  for both) tends to get exactly one axis right by accident. Explicitly
  decide both: refresh progress as often as the real save does (same gate,
  ideally the same call site so they can't drift again), but resolve
  position/status independently — typically to a fixed known-safe location,
  not "wherever the checkpoint happened to be taken." Also: any mutable
  state that lives OUTSIDE the restored snapshot (here, a per-enemy attack-
  cooldown map, a plain closure variable never touched by save/load) does
  NOT reset when you "go back" — audit for it, or it becomes an invisible
  carry-over that only manifests as a race with real time.
- Provenance: Verified first-hand — found via a dedicated live-QA Playwright
  session (a subagent instructed to actually play the game, not just run
  the unit/replay suite), reproduced deterministically via direct command
  dispatch against the real `window.__game` instance, and confirmed fixed
  the same way (checkpoint survives death; no chain-death).
- Link: commit "Bug pass: fix death wiping all progress, and a missing
  Igniter sprite" in pappydapimp69/the-game-the-answering-deep.

## E1 — answering deep modal overwrite race
- Date: 2026-07-09
- Project: pappydapimp69/the-game-the-answering-deep
- Tags: [ui][event-ordering][gamedev]
- What: A newly-written, state-aware NPC dialog (multiple real lines per
  quest-chain stage, replacing a flat placeholder array) was live-QA'd as
  "working" from a state inspection, but a screenshot of the actual UI never
  showed it — the player-visible modal was always the generic quest-offer
  box with empty flavor text.
- Why built: A single TALK command can produce more than one presentation-
  relevant event in the same dispatch: `talked` (npc dialog should show) and,
  when a quest is available, `quests_offered` (an offer modal with the
  quest choices should show). Both were handled in the same `onEvent`
  switch, each unconditionally setting `view.modal`.
- Design: `onEvent(e)` is a flat switch on event type; each case that opens a
  modal does so with one unconditional `view.modal = mkModal(...)` write.
  This is simple and has worked fine everywhere else in the codebase because
  almost every OTHER event type is the only UI-affecting event in its batch.
- Got right: The new dialog-generation logic itself (`wrenDialogFor`, a
  function of live quest state rather than a static array) was completely
  correct — verified independently by reading `view.modal.lines` right after
  dispatching `talked` alone, before `quests_offered` had a chance to fire.
- Where/why it failed: `reduce.js`'s TALK case always pushes `talked` first
  and `quests_offered` second (when applicable) into the SAME events array;
  `onEvent` processes that array in order, and each case's `view.modal =
  ...` assignment has no awareness of what a PRIOR event in the same batch
  just set. Since a quest is offerable almost every time the player talks to
  this NPC, the second write almost always won — the offer modal (built
  with a hardcoded empty `lines: []`) silently threw away the dialog modal
  set one line earlier in the exact same event loop. A raw-dispatch state
  check (`view.modal.lines` right after the `talked` event alone) can look
  correct while the actual multi-event flow the player experiences never
  shows it.
- Fix: Instead of two competing modal-producing event handlers, folded the
  same dialog-generation call into the offer modal's own `lines` field, so
  the SECOND event's modal carries the content the first one would have
  shown, rather than discarding it. One event's UI effect now composes with
  the next instead of racing it.
- Why this fix: The umbrella problem is "last write wins" across sequential
  events from one user action — the real fix is making the later handler
  AWARE of (or itself responsible for including) what the earlier one would
  have shown, not reordering the events or trying to detect "was there a
  modal already."
- Rule of thumb: When one user action can synchronously emit MULTIPLE
  presentation-relevant events in sequence (common in a `reduce -> events[]
  -> for(e of events) onEvent(e)` architecture), and more than one of those
  events independently sets the same piece of UI state (a modal, a toast
  slot, a focus target), check for a last-write-wins race before trusting a
  live QA pass that only inspects one event's effect in isolation. Verify by
  reading the ACTUAL post-dispatch UI state (the real `view`/DOM/screenshot)
  after the FULL batch of events from one real user action, not just after
  the specific event you're testing fires alone. If two events want to
  affect the same UI slot, make the later one compose with (not silently
  discard) whatever the earlier one produced.
- Provenance: Verified first-hand — the bug was caught specifically because
  a live-in-browser QA pass took a screenshot of the real UI after a full
  TALK-with-offer flow, and the flavor lines were visibly missing from it
  despite an earlier isolated state check (`view.modal.lines` right after
  the bare `talked` event) showing them present. Fixed and re-verified with
  the same live screenshot showing both the dialog lines and the quest
  choices together.
- Link: commit "Stage 10: quest dialog rewrite, torch-quencher, guardian
  role, trainer-torch onboarding" in
  pappydapimp69/the-game-the-answering-deep.
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E26 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E37 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E46 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-wrong-sky.md#E16 · compatible · no sandbox · session (brain train 3 groups + 2 edges, sandboxed until satisfied), sandbox script verify_modal_race.mjs (imports real project source, no mocks), no code change to a shipping project — fix pending explicit confirmation
