# Pappydapimp69/Opticon — lessons

Project: Pappydapimp69/Opticon. Newest first.

---

## E45 — own escape and item legibility
- Date: 2026-08-12
- Project: pappydapimp69/opticon
- Title: two bugs the suite could never have found, because both were about what the player was told
- Tags: [gamedev][architecture][testing][ux][gamedesign]
- What: Two defects reported from actual play of Opticon within minutes of each other, against a build with 1854 green logic assertions and thirteen browser harnesses. Neither was a crash, a wrong number, or an unhandled state. Both were the game being correct and illegible: "I won as a prisoner without reaching the gate myself", and "items exist and have icons, but they have no description or clear use case — I picked up a pair of scissors and had no idea what it was for".
- Why built: `checkEndConditions` ended the game on `prisoners.some(p => p.escaped)`, a rule written when there was exactly one prisoner, where "anybody escaped" and "you escaped" are the same predicate. Item pickup is automatic — you walk over a tile and now you carry it, with no shop, no inspect step and no confirmation — and the HUD chip showed the icon and the noun and that was the entire briefing.
- Design: In single-player Prisoner mode the human drives prisoner 0 while two AI companions run their own escapes. The item rules were written down correctly and completely, inside a collapsed `<details>` panel on the main menu that a player has to leave the game to read, and arming a targeted item had no visible effect at all until a direction followed.
- Got right: Both reports were taken as sensory truth about the experience rather than argued with, and both turned out to be about information rather than state — which is what made the fixes structural (an identity in the rules, a required field in the item table) instead of cosmetic patches.
- Where/why it failed: Whenever a companion happened to touch the gate first, the human got a full ESCAPED screen — "You slipped past the eye and reached the gate" — while standing in a cell on the far side of the map, and a win in their persisted W/L record. The companions feature silently split "anybody escaped" from "you escaped" and nothing in the rules layer noticed, because the rules layer had no concept of which prisoner is the player: it knew the board and whose turn it was, but "which of these is you" lived only in the UI layer (`humanControlsPrisoner`, in main.js), so the rules could not express a personal win condition even in principle. On the item side, pressing the key to arm a targeted item looked like a dead button.
- Fix: Give the rules layer an explicit `humanPrisoner` index, null when the human is in the Watcher seat, and grade a human prisoner by their own fate — their escape wins, their capture loses, and what the group managed becomes a line on the end screen rather than the verdict; with no human prisoner the institutional rule stands unchanged and the Watcher must still run the whole table. For items, make `blurb` (what it does) and `use` (how to fire it) required fields of the item definition itself, plus a `targeted` flag; render them in a caption under the chips for whichever item is highlighted; and change the hint bar when an item is armed, mirroring the treatment the Watcher's targeted skills already had.
- Why this fix: When a feature scales a single actor to N, every predicate that quantifies over that actor needs an audit — `some()` and `every()` are identical at N=1 and mean opposite things at N=3, and the compiler, the types and the tests all stay silent through the change, so the scale-out looks like a data change and is actually a semantics change. A system that decides outcomes for a player needs a handle on that player. On the item side, the regression test checks the DATA rather than only the rendering: every entry in the item table must carry a `blurb` over 25 characters, a `use`, and a boolean `targeted`, and every targeted item's instruction must mention the direction step, so a new item added with just a label and an icon fails in CI before anyone has to play it. Explanatory copy is usually treated as content and therefore untestable; making it a required field of the definition turns "we forgot to document it" into a schema violation.
- Rule of thumb: When a feature pluralises an actor, audit every predicate that quantifies over it, because `some` and `every` coincide at N=1 and diverge at N>1 while staying perfectly type-correct — and if a system decides outcomes for a player, it needs an explicit handle for which entity that player is, not one that lives in the UI layer. Make explanatory copy a required field of the thing it explains, so a missing description is a schema violation rather than a content oversight. And note what both defects share: comprehensive automated coverage checks that the system does the right thing, and neither of these was the system doing the wrong thing — one told the player they had achieved something they hadn't, the other told them nothing at all, and no assertion about game state can catch either, which is the argument for playing it rather than only testing it.
- Provenance (verified/assumed): VERIFIED first-hand — both defects were reported from actual play within minutes of each other against a build with 1854 green logic assertions and thirteen browser harnesses; the false ESCAPED screen and persisted win were reproduced from a companion reaching the gate first, and the item-table schema test (blurb over 25 characters, a use string, a boolean targeted, and a direction step named for every targeted item) was added and runs in CI.
- Composed: N/A
- Link: Opticon; checkEndConditions; item table and HUD chips; item schema regression test

## E44 — mutation audit oldest code first
- Date: 2026-08-12
- Project: pappydapimp69/opticon
- Title: a mutation audit scored 1/12 on new code and 5/16 on old code in the same repo
- Tags: [testing][process][architecture][gamedev][verification]
- What: A deliberate-defect (mutation) audit of a game's test suite, run twice against the same repo with different targets. Round 1 mutated the systems written that week — custody, guards, the post-release grace — and scored 1 survivor out of 12. Round 2 mutated the systems written earliest and touched least — noise decay, field of view, lamp line-of-sight, door cost, gaze geometry, exposure tiers, belt capacity, decoy range, the round limit — and scored 5 out of 16 from the same suite.
- Why built: Four real defects had been found in one week by playing the game or by being asked a pointed question, not by a suite of 1859 assertions and thirteen browser harnesses. Finding holes one at a time is not a method. The audit was the obvious experiment: break one rule, run everything, record what notices.
- Design: A shell loop that substitutes one exact source string, runs the whole suite, and restores. Because the runner is `set -e`, a caught mutation exits within seconds and only survivors pay the full runtime — which makes the cost roughly proportional to how bad the news is. Kept as a script and deliberately NOT wired into the normal suite: sixteen mutations is about an hour of wall-clock.
- Got right: Running it twice with different targets rather than trusting the first score. The 1/12 was read as reassurance for about an hour before the obvious question surfaced — those were the systems whose tests had been written the same week, by the same hand, alongside the code. Re-aiming at the oldest code produced a five-fold worse result from the same suite.
- Where/why it failed: Three separate ways the instrument and the suite lied. (1) Assertions written against the constant they check: `ap === GUARD_ACTION_POINTS - GUARD_CAPTURE_COST` puts the same constant on both sides of the equals sign and holds for every value including zero, so a guard capturing for free passed everything; its sibling set the guard to `GUARD_CAPTURE_COST - 1` points, which under a mutated cost of 0 is -1 and passed for a completely different reason than the one under test. (2) A harness that crashed instead of failing: an uncaught 20s timeout threw out of an async IIFE, leaked its browser and server, printed a bare stack trace, and was scored by the audit as "the mutation was caught" — the instrument's own failure mode was indistinguishable from a result. (3) A mutation silently skipped: one search string did not match the file, so that mutation never ran, and the skip line reads almost identically to a caught line, so the audit reported on fifteen mutations while appearing to report on sixteen.
- Fix: Assertions rewritten against literals, paired with the property that makes the constant matter (`cost >= 2`: "a grab must cost materially more than a step"), and boundaries bracketed from both sides (2 points fails, 3 succeeds). Harnesses now exit 2 for "could not set myself up" and 3 for an unexpected throw, after tearing down, so neither can be mistaken for an honest red. Every new assertion was re-run under its own mutation to confirm it now fails.
- Why this fix: A literal is the only thing that can disagree with the implementation. Pairing it with a property means the literal is not the sole anchor, so an intentional future change fails loudly once and is re-decided rather than silently adapting. Distinct exit codes matter because an audit is only as trustworthy as its ability to tell a red apart from a crash.
- Finding: Not every surviving mutation is a hole. The fifth survivor — an anti-stall constant — was chased rather than patched and turned out to be dead code: with it disabled, 24/24 games still resolved with zero timeouts at every paranoia setting, because a later change (pricing risk into the route instead of refusing routes) had removed the deadlock it guarded against. The test written in response deliberately does NOT pin that constant; it pins the outcome the constant existed for. Writing a test to justify a value that provably does nothing is cargo cult, and it converts dead code into permanently-frozen dead code.
- Rule of thumb: Coverage tracks how recently something was written, not how important it is. Aim a mutation audit at the OLDEST code — the opposite of where attention naturally goes and of where the last commit touched. And when a mutation survives, ask whether the code is untested or simply dead before writing a test for it.
- Provenance (verified/assumed): VERIFIED first-hand — both audit rounds were run against Opticon beta-0.55.0-0.56.0 via `game/tests/mutation-audit.sh`, the 1/12 and 5/16 scores are the recorded outputs, each rewritten assertion in `game/tests/core-invariants.mjs` was re-run under its own mutation and observed to fail, and the dead-constant survivor was confirmed by disabling it and watching 24/24 games still resolve. The generality of the recency-tracks-coverage claim beyond this repo remains an assumption.
- Composed: N/A
- Link: Opticon beta-0.55.0-0.56.0; game/tests/mutation-audit.sh; game/tests/core-invariants.mjs; Tension T29 and T30

## E43 — guards as pawns
- Date: 2026-08-12
- Project: pappydapimp69/opticon
- Title: a secondary threat outgrew the primary one, and the fix was a resource bar, not a nerf dial
- Tags: [gamedev][balance][measurement][architecture][gamedesign]
- What: Opticon is a panopticon game — a Watcher rotates a 90-degree gaze from a central tower and prisoners sneak past it. A later feature, DISPATCH, sent physical guard squads that caught prisoners on plain line-of-sight, ignoring light, noise and the gaze entirely. Attributing every capture by the rules' own log message over 300 games per tier showed the guards making 40/75/83% of captures on easy/medium/hard, so the premise mechanic was responsible for 17% of deaths on the hardest tier.
- Why built: DISPATCH was added as a secondary pressure on top of the gaze, and nothing in its design was wrong in isolation. What was never checked is what share of outcomes each hazard owned once both were live, which is the only number that says whether a lever on one of them can matter.
- Design: The repair replaces the guard's CONTRACT rather than its numbers — sight cut to Chebyshev 1 (one square, diagonals included), and lifespan replaced with a 7-point action bar where a burst window buys 3 squares for 1 point for the first 2 turns, every square costs 1 point after that, and a capture costs 3. The bar's size is the difficulty knob.
- Got right: Attributing outcomes with the rules' own log rather than inventing an instrument. One cheap pass over the outcome log asking "what is actually killing them?" is what broke a deadlock that five carefully built experiments had not.
- Where/why it failed: Five separate attempts to make prisoners self-regulate against the gaze had each been built, measured, and found inert — caution thresholds, a waking yard that lit the map over time, a tighter round limit, better-aimed fear, and deleting guards entirely. Every one was correctly implemented and every one measured ~3pt or less. They shared a cause nobody had checked: the lever was priced against a hazard responsible for a minority of outcomes, and tuning a mechanic that only decides 17% of games cannot move the game no matter how well the tuning works.
- Fix: Replace the guard's contract with the action bar described above rather than reaching for the available nerf dials (fewer guards, shorter lifespan, longer cooldown). This inverted the split to gaze 82/55/46% while keeping difficulty ordering (escape 66/52/29%) and role symmetry (human-Watcher capture 70/48/30%, human-Prisoner 27/48/71%).
- Why this fix: A resource bar demotes a mechanic without flattening it, where a nerf dial cannot. A shorter lifespan makes a guard uniformly worse at everything; a bar makes it situationally strong — the burst window is genuinely frightening, and the cost of a capture means a squad that catches someone has largely spent itself. The threat keeps a shape and a counterplay (walk two squares wide of one and it never knew you were there; make it spend its bar) instead of just a smaller number, and difficulty tiers survive because a bigger bar buys more DECISIONS rather than more lethality. The bar also became a visual tell almost for free — a guard's ring and light dim as it runs down — so "how much chase does this one have left" is readable from the board, and a resource the opponent can see is a resource they can play around, where one they cannot see is just hidden variance.
- Rule of thumb: When a tuning lever measures inert no matter how well it is built, stop iterating on the lever and attribute OUTCOMES first — a lever on a hazard that decides a minority of games cannot move the game. And when demoting a mechanic that has taken over, prefer a resource bar to a nerf dial: a bar preserves the threat's shape, its counterplay and the difficulty ordering, and if the opponent can see it, it becomes something they can play around rather than hidden variance.
- Provenance (verified/assumed): VERIFIED first-hand — the capture attribution was run over 300 games per tier using the rules' own log messages, giving guards 40/75/83% of captures before the change and gaze 82/55/46% after, with escape at 66/52/29% and role symmetry at 70/48/30% and 27/48/71%. Caveat carried forward: every prior measurement on this system was taken through two bugs since fixed (an AI prisoner that read the true gaze, and a binary avoid-set that discarded risk under pressure), so old numbers describe a game that no longer exists and were re-run rather than cited.
- Composed: N/A
- Link: Opticon DISPATCH; guard action bar; capture attribution pass
- Cited-by: 2026-10-09 · projects/pappydapimp69__brainwork.md#E42 · compatible · sandboxes/2026-10-09__last-click-credit-vs-incremental-lift.py · observed RESULT: PASS display last-click 0 vs lift 54 at f=0; credit = 60*f, equal to the lift only at f=0.9, +6 over at f=1.0; brand credit 140 to 80 as f rises, true lift 0 throughout. · scheduled brain train run, kernel mode pass 1; session_01MiqdeTN5cV7j1vm5wkPKVF

## E42 — custody and screen relative
- Date: 2026-08-12
- Project: pappydapimp69/opticon
- Title: the identity mapping that hid a feature, and turning a terminal state into a playable one
- Tags: [gamedev][input][camera][gamedesign][testing]
- What: Opticon's Watcher d-pad already resolved directions through the live camera — project each world cardinal, pick the one whose on-screen direction best matches the requested one — but the Prisoner's movement never did; it was hardcoded up=North. Both the prisoner third-person camera and the overview orbit freely, so the moment the view turned, pressing up walked you sideways. In the same session, capture was changed from a terminal state to a playable one, which surfaced two further generalisable errors.
- Why built: The Prisoner side was written when only the Watcher had a free camera, so up=North was true when it was written and quietly stopped being true when the prisoner camera gained orbit. Capture was `p.alive = false` — the eye found you and you stopped existing — which is a non-event for the player it happens to, so it was replaced with custody.
- Design: Custody seizes the prisoner on the tile they were taken on, unable to move, for three of their own turns before processing. Four exits each answer a different reason you are still in the cell: a Shim (certain, beats a posted guard), a Flare (thrown, so it works from inside a cell, and drags a quadrant's guards to the light), a companion who ends their turn adjacent, or bare hands. A guard that stands watch beats everything except the Shim and pays an action point a turn to do it, so holding you is a real cost to the Watcher. The direction resolver takes the tile the direction is given FROM, defaulting to the map centre, because under perspective world-North does not project to the same screen direction at the top of the map as at the bottom, so a prisoner's own move must resolve from the prisoner's tile.
- Got right: Resolving through the camera that actually drew the frame, rather than through a stored camera pose, and asserting the SIGN of the avatar's movement after that projection — the property Brain opticon#E24 had already warned about ("a camera-relative movement sign error passes every displacement-magnitude test — inverted controls still moved").
- Where/why it failed: The reusable part is not the fix, it is why nothing caught it: at the default camera pose the correct mapping and the hardcoded one are the same function. Every test that pressed a movement key started at the default view, so the bug was invisible to the entire suite, and two other tests (`["KeyW","KeyD","KeyS","KeyA"][worldDir]`) had baked the same assumption into their own helpers — fixing the product broke one of them and left the other passing by luck. The custody work then produced two more: the first draft used a 0.3 per-turn struggle chance with a comment claiming "~66% of unequipped prisoners are processed", when 1 - 0.7^3 is a 66% ESCAPE rate for a prisoner carrying nothing, and measured, AI-vs-AI escape went 66/52/29% to 81/61/40% — capture stopped meaning anything. And the AI's rescue diversion initially let a companion walk up to ten tiles to a cell, reasoning that three turns buys three moves and an over-long detour would be self-correcting; it was not, it marched companions toward the one tile the tower had just proved it was watching, and hard-tier escape fell 29% to 21% while easy rose.
- Fix: Resolve prisoner movement through the live camera from the mover's own tile, and test deliberately off the identity case — four camera azimuths, including two sitting diagonally between cardinals — asserting that the chosen cardinal is the ARGMAX of the four rather than merely one whose sign is acceptable. Drop the struggle chance to 0.15, where the same three turns come to 39%. Cap the rescue diversion at one turn's reach so it is an opportunistic detour rather than a march, which recovered the numbers. And give every gate that read `p.alive && !p.escaped` as "this prisoner can do things" its third condition, in movement, window-breaking, item use, the gaze scan and guard capture.
- Why this fix: An earlier draft asserted "the requested axis dominates" and failed at diagonal camera angles — correctly, because at a camera sitting between two cardinals no cardinal is dominantly "up"; the honest contract is "closest available", and it is checkable at every angle, which a dominance contract is not. The struggle-rate correction matters because a per-attempt probability inside an N-attempt window is not the number you feel. And the diversion cap matters because self-correcting incentives do not substitute for a bound.
- Rule of thumb: Whenever a transform has an identity case, the identity case is where all your fixtures live, so a mapping bug outside it is invisible to the whole suite — test deliberately off the identity, and assert the argmax rather than the sign. Always write down the COMPOUNDED odds, not the per-attempt one: 0.3 per turn over three turns is a 66% escape, not poor odds. A helper that is generous "because it punishes itself" does not self-correct; bound it. And adding a state to an entity silently reinterprets every predicate that was previously exhaustive, so `alive` quietly stops meaning "can act".
- Provenance (verified/assumed): VERIFIED first-hand — the hardcoded up=North mapping was confirmed invisible to the existing suite and the argmax assertion was written and run at four camera azimuths including two diagonals; the struggle-rate error was measured as AI-vs-AI escape moving 66/52/29% to 81/61/40% and corrected to 39% at 0.15; the ten-tile rescue diversion was measured dropping hard-tier escape 29% to 21% and recovered once capped; and the two HUD/Shim bugs below were found in the first scripted browser playthrough after the suite was green.
- Composed: opticon/E24, opticon/E11
- Link: Opticon; prisoner movement resolver; custody; game/tests browser playthrough
- Note: The browser found what 1859 assertions could not — the HUD's Held counter and cell instructions sat a turn stale because they refresh on player input and custody begins and ends on turns that are not the player's, and pressing a Shim ARMED it instead of firing it, because `armItemSlot` auto-fired on a hardcoded `kind === MUFFLE || kind === FEATHER` and broke the moment a third untargeted item existed. The fix was to read the item's own `targeted` field instead of a list of the kinds that existed when the branch was written, and the regression test now iterates every untargeted item rather than the two that were broken.

## E41 — assertions that cannot fail
- Date: 2026-08-12
- Project: pappydapimp69/opticon
- Title: assertions that restate the implementation cannot fail
- Tags: [testing][process][architecture][verification]
- What: Asked plainly why problems were being left unsolved, the answer turned out to be mechanical rather than temperamental: the stopping condition in use was "the suite is green and the requested thing works", not "there are no open problems". A flaky test is the exact shape that survives that rule, because it stops being a signal the moment a re-run passes. Two failures in the same session had already been written off as machine load, and they were not.
- Why built: The project had 1859 assertions and thirteen browser harnesses, which is enough coverage that greenness had become the stopping condition rather than one input to it. That is the state in which an assertion incapable of failing is indistinguishable from one that is doing work.
- Design: Four defects were found one at a time, every one invisible to that suite. A browser harness set `turn = "Prisoner"` but never waited for the human's prisoner to hold the turn, so it raced the AI's timer. The same harness searched for a neighbour of the exit requiring plain floor, but the exit sits on the map edge, so on many seeds it found none, pressed nothing at all, and reported a feature failure for a setup that never ran. It teleported the avatar ~30 tiles and then asked the renderer which key pointed at the gate while the camera was still eased onto the old position, and under perspective that far off-centre the answer is a different cardinal, so "step West" resolved to a key that walked South — an artifact that had been seen in a second harness earlier and dismissed in one line as "a test artifact" without being chased. And three "smoke" scenarios drove 5-7 keypresses while asserting only "no console errors" and "the game object exists", so they would pass with every keypress ignored, which is why a run showing the player sitting on its spawn at round 1 had been looked at and passed over.
- Got right: Changing method rather than looking harder. The first instance of the real defect was found by hand and the second only by mutation, which is the evidence that reading a passing suite is not a way to find assertions that cannot fail.
- Where/why it failed: The generalisable defect is assertions that restate the implementation, in two distinct instances. A test claimed to prove that bluffing "reaches" a difficulty tier and accepted `positionDiffers || beliefDiffers` as evidence — that OR is the whole trap, because an internal belief value can move while being structurally unable to reach behaviour, and it was doing exactly that: across 120 full games the two settings produced byte-identical results, because two independent gates severed belief from routing on that tier, and splitting belief from behaviour showed a claim moved the belief in 30/30 turns and moved the prisoner in 4/30. The second instance was `ap === GUARD_ACTION_POINTS - GUARD_CAPTURE_COST`, the same constant on both sides of the equals sign, true for every possible value including zero, whose sibling assertion set the guard to `GUARD_CAPTURE_COST - 1` points — under a mutated cost of 0 that is -1 points, passing for a completely different reason than the one under test. Both were written in good faith and read perfectly well.
- Fix: Break one rule at a time on purpose, run the whole suite, and record whether anything noticed. Twelve deliberate defects — custody clock length, gaze immunity, capture cost, an inverted direction mapping, removed gates, disabled rescues, an always-succeeding dice roll — scored 1 survivor out of 12, and that survivor was the constant-relative hole. Then apply the rules it exposes: an assertion about a constant must use a LITERAL or it tests nothing about that constant, paired with the property that makes the constant matter (`cost >= 2`, "materially more than a step") so the literal is not the only thing pinning it; count and assert the OUTER effect, never `inner || outer`, printing any internal value separately; make a harness that cannot set itself up fail in its own voice with a distinct exit code and message rather than as a red on the feature; and wrap async harnesses so an uncaught throw cannot leak a browser and a server behind a bare stack trace.
- Why this fix: A literal is the only thing that can disagree with the implementation, and an OR over an inner and an outer signal is green whenever either moves, which is why both assertions survived review. A setup failure wearing a feature failure's clothes cost three separate misdiagnoses here and also polluted the mutation audit itself, which read one harness crash as "the mutation was caught" — so distinguishing the two is not tidiness, it is what makes the audit's own numbers trustworthy.
- Rule of thumb: An assertion that restates the implementation cannot fail, and no amount of reading a green suite will tell you which of your assertions those are — only breaking the thing on purpose will. Never assert `innerValueMoved || behaviourMoved`; assert the outer effect and print the inner one. Never assert a constant against an expression built from that same constant; use a literal plus the property that makes the constant matter. And make a harness that cannot set itself up say so in its own voice, with a distinct exit code, because a setup failure that looks like a feature failure corrupts every conclusion downstream of it.
- Provenance (verified/assumed): VERIFIED first-hand — all four harness defects were found and fixed, the belief-versus-behaviour split was measured across 120 full games (byte-identical results, then 30/30 belief moves against 4/30 prisoner moves once separated), and the twelve-mutation audit was run and scored 1 survivor out of 12.
- Composed: N/A
- Link: Opticon; game/tests/mutation-audit.sh; game/tests/core-invariants.mjs
- Cited-by: 2026-09-09 · projects/pappydapimp69__zanegpt.md#E4 · compatible · no sandbox · session https://claude.ai/code/session_01HEhYc3p6SBh1KP1VhxmjPs — commit f570d34 (hidden-rule-hazard)
- Cited-by: 2026-10-08 · projects/pappydapimp69__brainwork.md#E13 · compatible · sandboxes/2026-10-08__pause-guard-test-scope-mutation-audit.py · observed RESULT: PASS 4 missing-pause-check mutants; survivors base-only=4 partial=3 whole-state=0 · scheduled brain train auto pass 2

## E40 — grace counted in the wrong clock
- Date: 2026-08-10
- Project: pappydapimp69/opticon
- Tags: [gamedev][testing][turn-based][state]
- What: The rule is "a prisoner who struggles free gets to play their turn and cannot be captured again by the watcher on their next turn". The first half worked; the second did not, because the immunity was counted in ROUNDS while the rule is phrased in the freed prisoner's OWN turns.
- Why built: `RELEASE_GRACE_ROUNDS = 1` with `p.graceUntilRound = game.round + 1`, checked in the gaze sweep as `game.round <= p.graceUntilRound`. It reads correctly, and `round` sounds like a lap of the table.
- Design: A per-prisoner round number, set on release from custody, consulted by the Watcher's gaze sweep between turns.
- Got right: The reprieve existing at all, and being watcher-only — a released prisoner standing beside a guard is still catchable, which is the intended asymmetry and survived unchanged.
- Where/why it failed: `game.round` increments once per PRISONER TURN, not once per lap, so "1 round" is one SOMEBODY ELSE'S turn. With three prisoners alive the window closed on the scan immediately BEFORE the freed prisoner's own next turn: reproduced with guards removed and the prisoner on a lit tile inside the gaze — freed on round 1 with grace through round 2, safe on rounds 2 and 3, seized on round 4. They never received the turn the rule promises. The bug scaled with party size and vanished entirely at one prisoner, which is the configuration a manual check uses.
- Fix: Count the grace in the freed prisoner's own turns, spent at the end of each of their turns, granting one extra when the release lands during their own turn (the turn they are standing in will spend a ticket before the promised one begins).
- Why this fix: Store the duration in the units the RULE is written in, so the number cannot silently bake in the actor count.
- Rule of thumb: When a rule is phrased in ONE actor's turns ("your next turn", "once per your visit") and the engine keeps a different clock (a global round, a tick, a frame), store the duration in the rule's units and decrement it on that actor's own event. And test it by advancing the real loop — a test that manipulates the clock variable directly can only re-assert the conversion it was written from.
- Provenance (verified/assumed): Verified first-hand. The existing test asserted the implementation (`graceUntilRound === round + RELEASE_GRACE_ROUNDS`) and moved `g.round` by hand, so the formula that WAS the bug could only ever be confirmed; a replacement that drives real turns showed the seizure on round 4 of 4 before the fix and a surviving prisoner with move points after it. Balance unmoved at 200 games/tier (easy 74->73, medium 52->50, hard 27->27), as expected at a 0.15 struggle chance.
- Composed: N/A
- Link: pappydapimp69/opticon claude/brain-install-bhr36y, game/src/rules.js + game/tests/custody.mjs
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-opticon-brain-builder-party-size-correctness-is-a-step-function.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX

## E39 — a binary avoid set with a fallback cannot express caution
- Date: 2026-08-03
- Project: pappydapimp69/opticon
- Tags: [gamedev][ai][pathfinding][balance][method]
- What: Every lever intended to make the prisoner AI act cautiously measured
  at roughly the same tiny effect — caution/dawdle thresholds ~3pt,
  bluff-gullibility ~3pt, prisoner-skill tiers ~3pt — and each was
  independently recorded in the tension ledger as "a weak lever" (T25). They
  were not weak. They shared one bottleneck nobody had looked at.
- Why built: The AI routed with `bfsPath(map, sx, sy, tx, ty, avoid)`, where
  `avoid` is a Set of soft-blocked tiles.
- Design: Build an avoid-set of dangerous tiles each turn, hand it to BFS.
- Got right: The avoid-set itself was correctly computed; the danger predicate
  was right. The failure was one line below it.
- Where/why it failed: `bfsPath` retries WITHOUT the avoid-set whenever no
  avoiding route exists. So risk is binary per tile AND self-cancelling in
  aggregate: raise fear and the set grows until the fallback fires, at which
  point risk stops mattering entirely. "Safer but longer" — the trade the
  whole game is about — was not expressible, so no tuning of any threshold
  could ever produce it. Measured: dropping the caution threshold from 0.34
  to 0.15 moved speed 2.90 -> 2.81 tiles/turn and escape-vs-a-staring-Watcher
  94% -> 96%, i.e. nothing, in the direction of nothing.
- Fix: Added `costPath`, a uniform-cost (Dijkstra) search where entering a
  tile costs `1 + penalty(x, y)`, and gave the AI a `riskAversion` tier knob
  expressed in tiles ("how far I will walk to dodge a tile I am certain is
  watched"). No fallback is needed or present: the cheapest route always
  exists, it just runs through danger when danger is unavoidable.
- Why this fix: A cost converts risk and tempo into the same unit, so a
  detour happens exactly when it is worth it, and belief strength (0.25 for
  "no idea") buys a proportionate detour instead of falling under a threshold
  and buying nothing.
- Rule of thumb: A soft constraint implemented as a filter-plus-fallback is
  not a soft constraint — it is a hard one that silently switches itself off
  under pressure, and it will make every knob upstream of it measure weak.
  The tell is a cluster of independent levers that all measure the same small
  effect: suspect a shared downstream bottleneck before concluding the levers
  are weak. When an agent must trade safety against progress, price both in
  one unit and let a cost search decide; keep thresholds only for genuinely
  binary calls (hold position, spend an item). Verify with a BEHAVIOUR metric
  and a COST metric together — safety that is free is not caution, it is just
  a better move, and only the pair proves a real trade.
- Provenance (verified/assumed): Verified first-hand. `costPath` with zero
  penalty reproduces BFS path length on 40/40 sampled maps; with risk priced,
  7/40 routes detour and initially-risky routes lose 53% of their risky
  tiles; a route is still found on 30/30 maps when every tile is priced at
  1000. Behaviour: turns ended standing on a lit, genuinely-watched tile fall
  4.2% -> 1.7% as aversion rises 0 -> 9, while rounds rise 9.1 -> 10.1
  (active Watcher) and 15.6 -> 17.5 (staring Watcher) — the cost that makes
  it a trade. Effect saturates near aversion 9, consistent with
  sandbox-pathfinding-astar-heuristic#E1's finding that weighted-search
  tuning is steeply nonlinear and its useful range narrow.
- Composed: local__sandbox-pathfinding-astar-heuristic#E1 (weighted-search
  tuning range), opticon#E22 (a pathfinding cost regression that hid as a 6x
  whole-sim slowdown with no visible symptom — why the heap here is real)
- Link: game/src/pathfind.js (costPath), game/src/prisonerAI.js
  (riskPenalty, PRISONER_SKILL.riskAversion), game/tests/risk-routing.mjs,
  build beta-0.49.0
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E14 · compatible · no sandbox · August-10 sandboxes/loop05_div_counts_sources_not_assumptions.py — bears directly on open tension T20
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E17 · compatible · no sandbox · August-10 sandboxes/loop07_conjunction_gated_branches.md

## E38 — an ai opponent reading hidden state invalidates the mechanic it opposes
- Date: 2026-08-03
- Project: pappydapimp69/opticon
- Tags: [gamedesign][ai][asymmetric-hidden-info][testing]
- What: In a hidden-information game whose entire premise is that the Prisoner
  cannot know where the Watcher is looking, the prisoner AI read
  `game.watcher.facing` — the true gaze — directly, on every danger check.
  The watcher AI likewise read prisoner coordinates on one path. Reported by
  the project owner, not by any test.
- Why built: The AI was written to play WELL, and the true state was the
  cheapest signal available to make it play well.
- Design: `dangerous(x, y)` = tile is lit AND `inWatcherGaze(watcher.facing,
  x, y)`. A per-turn `gullible` roll (easy 0.55 / medium 0.22 / hard 0.0)
  substituted last turn's public claim for the truth some of the time.
- Got right: The watcher AI's own targeting was already honest — its
  suspicion scoring reads only `game.noise`, light state and the exit
  quadrant, all public. Only one incidental path leaked.
- Where/why it failed: The leak does not merely make the AI strong, it
  INVALIDATES THE OPPOSING MECHANIC. The bluff exists solely to corrupt the
  Prisoner's estimate of the gaze; against an AI that reads the true value
  the estimate does not exist, so on hard (`gullible: 0`) bluffing was
  provably inert — the field was never consulted. A whole verb the human
  Watcher is taught, and given a skill and a cooldown for, did nothing. The
  `gullible` knob had been measured at "~3pt effect, near-inert" and recorded
  as a weak lever (T25); it was actually a weak PATCH over an
  information leak, and no amount of tuning it could have worked.
- Fix: The prisoner AI now carries a belief distribution over the four
  facings, updated only from what a human prisoner can also observe — the
  public claim, where a companion was just caught, and the printed rule that
  the eye turns at most 90° per turn (so belief diffuses each turn). Danger
  became probabilistic: `gazeRisk` sums belief over the facings whose wedge
  covers the tile, compared against a per-tier threshold. The watcher AI's
  occupancy pre-check was deleted; it only front-ran a refusal the rules
  already return, so removing it costs a wasted attempt — exactly what a
  human risks doing the same thing blind.
- Why this fix: A belief makes the bluff evidence rather than a dice roll, so
  it now moves behaviour on every tier that listens to claims at all, and
  "hard ignores talk" becomes a stated skill property instead of a hole.
- Rule of thumb: In an asymmetric hidden-information game, an AI reading the
  hidden state does not just make it strong — it silently deletes whatever
  mechanic exists to manipulate the opponent's ESTIMATE of that state, and
  the deletion shows up as "that lever measures weak," which invites tuning
  the lever instead of finding the leak. Give the AI a belief updated from
  the same observations the human gets, and enforce the boundary by TRAPPING
  the property (`Object.defineProperty` with a recording getter) during the
  AI's turn — a source grep is defeated by an alias or a destructure, an
  accessor is not. Assert the AI actually ran in the same test, or a no-op
  passes it.
- Provenance (verified/assumed): Verified first-hand. The trap test records
  0 reads after the fix and **42,079** reads when the original omniscient
  check is restored verbatim. Balance re-measured over 300 games/tier: escape
  44/24/13% (was 48/25/14%), 0% timeouts; the role-direction sim stays
  correctly signed in both directions (human-Watcher capture 84/75/68%
  falling, human-Prisoner 50/75/92% rising). A claim now changes belief or
  behaviour in 30/30 sampled games on easy and medium, 0/30 on hard by design.
- Composed: opticon#E28 (the bluff snapshot that made `lastBluff` exist at
  all), opticon#E9 (auditing every consumer of shared state against "who is
  allowed to see this")
- Link: game/src/prisonerAI.js (updateGazeBelief, gazeRisk, dangerous),
  game/src/watcherAI.js (firstOpenDoor), game/tests/fair-information.mjs,
  build beta-0.48.0
- Cited-by: 2026-08-10 · projects/pappydapimp69__mirage.md#E7 · compatible · no sandbox · pappydapimp69/mirage main, tests/balance.mjs `deceived` policy + tools/sandboxes/oracle-vs-deception.mjs

## E37 — a layout test that measures before render passes about nothing
- Date: 2026-08-03
- Project: pappydapimp69/opticon
- Tags: [testing][ui][layout][harness]
- What: Wrote a geometry test to lock in a HUD layout rebuild (overlapping
  skill labels, a status rail wrapping to three ragged rows on a phone). It
  reported PASS — including when I deliberately restored the exact broken CSS
  to check it had teeth. Two independent reasons, both silent.
- Why built: Every existing test asserted on state and text; nothing asserted
  on geometry, which is why layout defects visible in any screenshot had
  shipped repeatedly.
- Design: Collect bounding boxes for the HUD's elements at five viewports and
  assert no pair overlaps, nothing leaves the viewport, nothing is clipped.
- Got right: Distrusting the green run enough to re-inject the original defect
  and confirm the test caught it — which is the only reason either bug below
  was found.
- Where/why it failed: (1) MEASURED TOO EARLY. The ability bars are rebuilt
  from the rAF loop a frame or two after the turn label changes, so the test
  measured 12 chrome elements and ZERO chips. With none of the colliding
  parts present, "no overlap" was true and meaningless. (2) MEASURED THE
  WRONG NODES. The first version collected chip boxes but not the name
  labels — and the actual defect was labels overflowing a fixed-width chip
  and drawing over each other, which is invisible to a chip-only measurement
  because the chips themselves never moved.
- Fix: Poll for the interactive elements to exist before measuring; assert a
  minimum count of CONTROLS actually measured so an empty HUD fails loudly
  instead of passing; add the label nodes to the selector set; and compute
  overlap inside `page.evaluate` so `el.contains()` can exclude nesting (a
  label legitimately intersects its own chip — containment is not collision,
  and serialized rectangles alone cannot distinguish them).
- Why this fix: The count assertion is the part that generalises — it converts
  "found nothing to check" from a pass into a failure, which is the only
  defence against the whole class.
- Rule of thumb: A test that asserts the ABSENCE of something (no overlap, no
  error, no leak) passes trivially when its subject failed to load, so it must
  first assert the subject is PRESENT — count what you measured and fail if
  the count is implausible. Two corollaries for UI geometry specifically:
  wait for the thing that renders asynchronously (a rAF-driven rebuild lands
  after the state change that triggered it, so state-based readiness is not
  render-based readiness), and measure the node that actually MOVES — the
  overflowing child, not the stable parent. And always verify an
  absence-assertion by re-injecting the real defect; a green run against known
  -broken input is the only proof the test is wired to anything.
- Provenance (verified/assumed): Verified first-hand. The false pass was
  observed twice against the original CSS restored verbatim; after the fix the
  same restored CSS fails with the specific colliding pairs named, and the
  repaired layout passes at 1280x800, 390x844 and 320x640 for both roles.
- Composed: N/A
- Link: game/tests/hud-layout.mjs, game/css/style.css, game/index.html,
  build beta-0.46.0
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-recursion-opticon-measuring-the-wrong-node-certifies-the-layout-bug.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX

## E36 — conflict markers shipped because the check was scoped to named files
- Date: 2026-08-03
- Project: pappydapimp69/opticon
- Tags: [process][git][testing][deploy]
- What: Shipped `<<<<<<< HEAD` conflict markers to production inside
  `index.html`, along with two `<script type="module">` tags pointing at the
  same `main.js` at different `?v=` strings — so the live game loaded its
  entire module graph TWICE (two rAF loops, two input handlers, two audio
  graphs). Caught only by eyeballing a `curl` of the deployed page and
  noticing it reported two different build strings.
- Why built: A post-squash-merge divergence (opticon#E7) required merging the
  remote branch back in. Three files conflicted.
- Design: Resolve the conflicts, verify no markers remain, run the suite, ship.
- Got right: The resolution logic itself was correct, and the diff-vs-master
  check confirmed the branch carried only the intended new work.
- Where/why it failed: The verification was scoped to the files the merge
  output *happened to name* — I ran `grep -c '^<<<<<<<'` against exactly the
  two files I had just edited, not the tree. `index.html` also conflicted but
  its line scrolled out of a `tail`-truncated merge summary, so it was never
  in the checked set, and `git add -A` committed it markers and all. Every
  downstream gate was blind to it by construction: markers are inert text to
  an HTML parser so the page still rendered; the browser tests still passed
  because a duplicated `<script>` merely re-runs a module that re-assigns the
  same `window.__opticon` global; and the full suite had been run BEFORE the
  merge, so the merge product was never actually tested.
- Fix: Resolved `index.html`, and added `game/tests/no-conflict-markers.mjs`
  as the FIRST entry in `run-all.sh` — it walks the whole tree for
  line-anchored marker shapes, and separately asserts each entry point is
  referenced exactly once and that every `?v=` cache-buster equals the `BUILD`
  string. Verified it fails on a re-injected copy of the real defect before
  trusting it.
- Why this fix: A marker-only check would have missed half of this — a merge
  can duplicate a line cleanly with no markers left behind, and the duplicate
  `<script>` was the part with actual runtime consequences. The `?v=` vs
  `BUILD` assertion is the cheap invariant that catches both halves at once.
- Rule of thumb: Verify a merge against the WHOLE TREE, never against the file
  list you read out of the merge output — that list is truncatable, and the
  file you did not think to check is exactly the one that slips through.
  Re-run the full suite AFTER resolving, not before merging; a green run on
  the pre-merge tree says nothing about the merge product. And treat
  "the tests passed" as weak evidence for defects that are inert to the
  parser and invisible to assertions — for those, the check has to be a
  structural invariant (referenced exactly once, versions all equal), because
  no behavioural test was ever looking.
- Provenance (verified/assumed): Verified first-hand — observed the deployed
  page serving both `beta-0.44.0` and `beta-0.45.0` in the same HTML, read the
  literal markers out of the live response, then confirmed the new guard fails
  on a re-injected copy of the defect and passes once resolved.
- Composed: opticon#E7 (the post-squash divergence that forced the merge)
- Link: game/index.html, game/tests/no-conflict-markers.mjs,
  game/tests/run-all.sh, builds beta-0.45.0 → beta-0.45.1
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E13 · compatible · no sandbox · August-10 sandboxes/loop08_canonicalizing_a_save_breaks_every_golden.mjs
- Cited-by: 2026-08-03 · projects/pappydapimp69__mirage.md#E4 · compatible · no sandbox · MIRAGE crafting-deception session; `tools/stamp-version.mjs` and the "every module import and asset URL carries the current BUILD token" check in tests/logic.test.mjs.

## E35 — check the end condition after the move that can end it
- Date: 2026-08-03
- Project: pappydapimp69/opticon
- Tags: [gamedev][state][turn-based][lifecycle]
- What: A human Watcher who ended the turn that hit the round limit reached
  `status: "captured", timedOut: true` — a genuinely finished game — with no
  result overlay, no W/L recorded, and no indication anything had happened.
  The game just sat there looking playable.
- Why built: The human end-turn handler was ordered
  `checkOver(); if (isOver(g)) return; endWatcherTurn(g); …handoff…`.
- Design: `checkOver()` is the app-level "did the game end → show the result"
  step; `endWatcherTurn()` is the rules-level move. The guard was written to
  catch the case that was salient at the time — a scan capturing the last
  prisoner, which `watcherScan()` detects *before* the handler runs.
- Got right: For the salient case the order is correct — `watcherScan()` runs
  its own `checkEndConditions()`, so the pre-handoff `checkOver()` does catch
  a capture ending. The bug is only in what the guard does NOT cover.
- Where/why it failed: `endWatcherTurn()` is itself an ending move — it
  advances `game.round` (so it is what trips `ROUND_LIMIT`) and, when no
  living prisoner remains to activate, declares the capture. Both endings are
  therefore created *after* the only `checkOver()` on that path, and nothing
  downstream re-checks: the `!isOver(g)` guards below it simply decline to
  schedule the next AI turn, so the game goes quiet instead of finishing. The
  human Prisoner's `doEndPrisonerTurn()` had the same shape with no
  `checkOver()` at all.
- Fix: Call `checkOver()` again immediately after `endWatcherTurn(g)` /
  `endPrisonerTurn(g)`, before the handoff, and return if the game is over.
  Added an explicit `app.resultRecorded` latch so the extra call cannot
  double-show the overlay or double-count the win/loss record.
- Why this fix: The end-condition check belongs *after* every call that can
  create an end condition, not once per handler at whichever point the
  author's example case happened to need it. The latch makes the check
  idempotent, so adding it at more points is cheap and safe rather than a new
  double-fire risk.
- Rule of thumb: In a turn/state machine, a "did we finish?" check must sit
  after EVERY mutation that can finish it — and the easiest ones to miss are
  the bookkeeping calls (advance the round, pick the next actor) that read
  like plumbing but quietly own a terminal condition. Two tells that a check
  is misplaced: it runs before the state-changing call in the same handler,
  and the code after it only ever tests `!isOver()` to decide whether to
  continue — that shape fails silently, because "don't schedule the next
  turn" and "the game is over and should say so" look identical at runtime.
  Make the terminal check idempotent (latch the side effects) so it can be
  called defensively everywhere instead of exactly once.
- Provenance (verified/assumed): Verified first-hand. Reproduced in a browser
  (round set to `ROUND_LIMIT`, human Watcher presses end-turn → status
  `captured`, `timedOut: true`, `overlayHidden: true`, title still `"—"`),
  fixed, re-ran the same repro to green (`title: "TIME UP"`), and covered
  both roles with a new Playwright regression test
  (`game/tests/end-of-turn-over.mjs`) that asserts the timeout actually fired
  before asserting the overlay, so it cannot pass vacuously.
- Composed: N/A
- Link: game/src/main.js (`handleWatcherIntent` endTurn, `doEndPrisonerTurn`,
  `checkOver`), game/tests/end-of-turn-over.mjs, build beta-0.44.0

## E34 — screen secrecy and input authority are different questions
- Date: 2026-08-01
- Project: pappydapimp69/opticon
- Tags: [ui][gamedesign][turn-based]
- What: Live Playwright QA (playing as Watcher vs. an AI Prisoner) caught the
  hint bar and touch D-pad panel showing Prisoner move instructions/controls
  during the AI Prisoner's own turn, to a human playing Watcher.
- Why built: `hintFor()` and `updateHud()`'s panel-toggle both branched
  purely on `game.turn === "Prisoner"` to decide which role's controls to
  teach/show.
- Design: The codebase already had two correctly-used, distinct gates:
  `shouldShowWatcherInfo()` (screen-secrecy — what a role is allowed to SEE)
  and `humanControlsPrisoner()`/`humanControlsWatcher()` (input-authority —
  who is allowed to ACT right now), the latter already correctly used to gate
  real input handling in `handlePrisonerIntent`/`handleWatcherIntent`.
- Got right: Because input handling was already gated on
  `humanControlsPrisoner()`/`humanControlsWatcher()`, tapping the wrongly-shown
  D-pad during the AI's turn silently no-op'd — this was a confusing-UI bug,
  not a security/gameplay-hijack bug. Verified by tracing the input handlers,
  not assumed.
- Where/why it failed: `game.turn` answers "which role is acting" but not
  "does the human control that role right now" (it could be the AI opponent,
  or — in single-player Prisoner mode with AI companions — another AI
  companion's own turn within the human's group). The HUD/hint layer reused
  `game.turn` as if it answered the second question too.
- Fix: Added `humanControlsCurrentTurn()` (routes to the existing
  `humanControlsPrisoner()`/`humanControlsWatcher()` based on `game.turn`).
  `hintFor()` now shows a neutral "Watching the X's turn…" message instead of
  role controls when the human doesn't control the current turn.
  `updateHud()` takes a 5th `humanControlsTurn` param gating which touch panel
  is `.active`.
- Why this fix: Reused the same input-authority functions already trusted to
  gate actual input, instead of inventing a third gate — the display layer
  now agrees with the input layer about who's really acting.
- Rule of thumb: In any asymmetric-information / turn-based system, "what is
  this viewer allowed to SEE" and "is this viewer allowed to ACT right now"
  are different axes. A single `whoseTurnIsIt` variable answers neither by
  itself — a UI surface that teaches or enables controls needs the
  input-authority check, not just the turn variable; a UI surface that reveals
  secret state needs the screen-secrecy check. Conflating either with
  `game.turn` produces a bug the corresponding correct gate elsewhere in the
  codebase should have made obviously wrong by comparison.
- Provenance (verified/assumed): Verified first-hand — reproduced via live
  Playwright QA screenshot, traced `handlePrisonerIntent`/`handleWatcherIntent`
  to confirm input itself was already safely gated, and wrote a scripted
  Playwright repro (mid-AI-turn snapshot + post-turn-return snapshot) that
  fails on the pre-fix code path and passes after the fix.
- Composed: N/A
- Link: game/src/main.js (`humanControlsCurrentTurn`, `hintFor`),
  game/src/ui.js (`updateHud`), build beta-0.42.0

## E33 — svg transform attribute vs css animation
- Date: 2026-08-01
- Project: Pappydapimp69/Opticon
- Tags: [browser][svg][animation][css]
- What: An SVG element's static `transform` ATTRIBUTE (e.g. a rotate used to draw a diamond marker) is silently discarded the instant a CSS `transform` (e.g. an `animation: ... scale(...)`) is applied to that same element — not composed with it, replaced.
- Why built: Adding a reveal "pop-in" animation (CSS `transform: scale(...)` keyframes) to exploration-entry markers in brain-viz, which were drawn as `<rect transform="rotate(45 x y)">` to render as diamonds.
- Design: Gave the `<rect>` both the static rotate (as an SVG presentation attribute) and, via a shared `.mark` class, the animated CSS transform for the reveal pop.
- Got right: Caught this before shipping by reasoning through the interaction rather than only visually spot-checking one frame — the bug is invisible at the animation's rest state (start and end both happen to look like "no transform" from a quick glance) and only wrong mid-animation and, worse, PERMANENTLY once any CSS transform has ever been applied (browsers don't restore the attribute-based transform after the CSS animation completes).
- Where/why it failed: Per the CSS Transforms spec, when both an SVG `transform` presentation attribute and a CSS `transform` property target the same element, the CSS property wins outright — it does not multiply/compose with the attribute. The moment the `.pop` animation class was added, the diamond's rotate vanished for that animation's `scale()` value, and stayed vanished afterward.
- Fix: Split the element in two — an inner, un-animated `<g transform="rotate(...)">` holding the actual shape, wrapped by an outer `<g class="mark">` that is the ONLY element CSS ever touches. Static, attribute-based transforms and CSS-animated transforms now live on different elements and can't collide.
- Why this fix: The two transform systems (SVG presentation attributes and CSS) are just fundamentally not additive on one element — the only reliable fix is giving each system its own element in the tree, not trying to combine values.
- Rule of thumb: Before adding a CSS `transform` (directly or via an `animation`/`transition`) to any SVG element, check whether that element already carries a static `transform` ATTRIBUTE for something else (a rotation, a diamond/rhombus shape, a manual offset) — if so, move the animation to a wrapping `<g>` instead of the element itself, don't assume the two will compose.
- Provenance (verified/assumed): verified — read the CSS Transforms Level 1 spec's SVG interaction section directly, then confirmed the failure mode by inspection before shipping (never actually shipped the broken version to compare against, since the fix was applied pre-emptively during code review of the new animation).
- Composed: N/A
- Link: Pappydapimp69/Opticon claude/opticon-3d-browser-game-3lxa2y, tools/brain-viz.template.html

## E32 — ai never exercised tiered mechanic
- Date: 2026-08-01
- Project: Pappydapimp69/Opticon
- Tags: [gamedesign][ai][testing][balance]
- What: Tiering a game mechanic's numeric parameters by difficulty and re-running the balance sandbox produced a result byte-identical to a flat-medium control with no tiering at all — the tiering appeared to do nothing.
- Why built: Tension T25 needed DISPATCH (a Watcher-only guard-dispatch skill) tiered by difficulty (guard speed/lifespan/cooldown/sight-range) so a human Watcher's difficulty setting would mean something measurable, per the sandbox's own prior finding that earlier AI-behavior levers were too weak.
- Design: A `DISPATCH_TIER` table resolved once per game into `game.dispatchTier`, read by both the human skill-use path and the AI opponent's `pickSkills`.
- Got right: Running a flat-tier control alongside the "fixed" result before reporting it — the two being identical was the tell that something upstream was broken, not that the lever was weak.
- Where/why it failed: The AI-controlled Watcher's `pickSkills` function had a hardcoded preference list of skills it would ever use, and DISPATCH had never been added to it since the skill was built — the AI had never fired DISPATCH once, in any game, ever. Tiering its numeric parameters was therefore tuning a mechanic that was never exercised by the very agent the sandbox measures (the sandbox always routes the Watcher's turn through the AI, using tier-of-AI-behavior to simulate "which role the human plays" rather than a literal human). The numeric fix was real but silently no-op'd by an unrelated wiring gap one layer up.
- Fix: Grepped the AI decision function for the skill's own name (`grep -n DISPATCH watcherAI.js`) and got zero hits — immediate confirmation. Added the skill to the AI's preference order plus a target-selection heuristic, then re-measured; the tiered parameters started producing a strongly monotonic difficulty spread (9-17 points per tier vs ~3 for prior levers).
- Why this fix: A parameter you can point to as "wired through" is not the same claim as "actually invoked by the code path under test" — the second is a separate fact that has to be checked directly, not inferred from the first being true.
- Rule of thumb: Before reporting ANY before/after measurement of a tuning change to an AI-driven system, run a flat/unchanged control through the same harness. An identical-to-control result is not evidence the lever is weak — it is a specific signal to go grep whether the AI decision code even calls the changed thing, before trusting the numbers at all.
- Provenance (verified/assumed): verified — grepped watcherAI.js's pickSkills order list and confirmed SKILLS.DISPATCH was absent; after adding it, sandbox/t25-role-direction.mjs moved from 28/24/24% (both tiered and flat-control) to 82/74/65% (human-Watcher) and 48/74/92% (human-Prisoner).
- Composed: N/A
- Link: Pappydapimp69/Opticon claude/opticon-3d-browser-game-3lxa2y, Tension T25
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E17 · compatible · no sandbox · August-10 sandboxes/loop07_conjunction_gated_branches.md
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E19 · compatible · no sandbox · August-10 sandboxes/loop06_seed_variance_without_outcome_variance.md
- Cited-by: 2026-08-10 · projects/pappydapimp69__mirage.md#E7 · compatible · no sandbox · pappydapimp69/mirage main, tests/balance.mjs `deceived` policy + tools/sandboxes/oracle-vs-deception.mjs

## E31 — face buttons cant cover 4 directions plus confirm
- Date: 2026-07-30
- Project: Pappydapimp69/Opticon
- Tags: [gamedev] [input] [gamepad] [ux] [game-design]
- What: The Watcher's "bluff a direction" gesture (and, later, DISPATCH's quadrant pick, which reuses the same intent) had a genuine, permanent gap on gamepad: South was structurally unreachable, from the very first commit that added gamepad bluff support, not from any later regression.
- Why built: Bluff needs 4 discrete direction choices (N/E/S/W); a standard gamepad's 4 face buttons (A/B/X/Y) look like a natural 1:1 fit.
- Design: A (index 0) was already claimed for the universal "confirm/end turn" action (used on every other screen — menu select, overlay confirm, this turn's commit) before bluff was designed, so only 3 face buttons (Y/B/X) were free to map to directions. Y→North, B→East, X→West were bound; South was left out because there was no 4th free face button, and this wasn't caught at the time because the shipped feature "worked" for 3 of 4 directions and no test asserted the 4th.
- Got right: Reserving A globally for confirm across every screen (menu, overlay, in-game turn-end) is a real, valuable consistency win — a player never has to relearn which button confirms depending on context. That constraint was correct to keep; the bug was in what got done ABOUT it (nothing), not the constraint itself.
- Where/why it failed: The direction set (4) and the free-face-button budget (3, after reserving A) simply don't divide evenly. This is a hard structural mismatch, not a bug that "regressed" — it existed from the first gamepad-bluff commit and would have existed in any feature reusing the same 4-direction vocabulary (which DISPATCH's quadrant pick, added much later, did — inheriting the same gap for free).
- Fix: The D-pad (4 physical buttons already dedicated to "move" on the Prisoner's turn) was ALREADY idle during the Watcher's turn — `move`/`break` are Prisoner-only intents that `handleWatcherIntent` never reads. Made the d-pad dual-dispatch a `"bluff"` intent with the same direction index as `"move"`, alongside the existing intent, so only one role's handler ever consumes it per turn (the same convention keyboard digits 1/2 already used for item-vs-bluff overload).
- Why this fix: No new physical control needed to be freed up or reassigned — an already-present, per-turn-idle control took the unmapped 25%, using a dispatch pattern the codebase already had a name and precedent for. Reassigning a face button (e.g. moving confirm off A) would have cost the cross-screen consistency that was worth keeping.
- Rule of thumb: Before mapping an N-choice game vocabulary onto face buttons, count what's ALREADY reserved (universal confirm/back/etc.) and check N against the REMAINING budget, not the button count on the box — 4 face buttons rarely means 4 are actually free. When the budget comes up short, look for a control that's structurally idle during that exact context (a d-pad unused on a turn where "move" doesn't apply) before reassigning an existing binding.
- Provenance (verified/assumed): verified — the same fake-gamepad Playwright harness confirms d-pad DOWN now reaches South/quadrant-2 for DISPATCH, which was unreachable by any gamepad input before this fix.
- Link: Pappydapimp69/Opticon claude/opticon-3d-browser-game-3lxa2y, game/src/input.js

## E30 — enum growth outran a hardcoded modulo
- Date: 2026-07-30
- Project: Pappydapimp69/Opticon
- Tags: [gamedev] [input] [gamepad] [enum] [debugging] [ui]
- What: A gamepad player reported "can't dispatch guards as watcher" — a brand-new 5th Watcher skill was completely unreachable via LT/RT slot-cycling, no matter how many times LT was pressed.
- Why built: The gamepad's LT/RT "slot cursor" (added earlier to let a pad player reach items and skills without claiming 4+ extra face buttons) cycles an index and RT fires whatever the cursor currently points at — a single shared mechanism reused for both the Prisoner's item list (max 2) and the Watcher's skill list.
- Design: `this.slotCursor = (this.slotCursor + 1) % 4;` — hardcoded to 4, matching the skill count AT THE TIME the LT/RT feature was built (see beta-0.24.0, #25).
- Got right: The item/skill split already degrades safely when the cursor lands past a real item (armItemSlot no-ops with an audio "blocked" cue) — so raising the cap was safe on that side by construction; no defensive work was needed there.
- Where/why it failed: A later, unrelated commit added a 5th entry to the `SKILLS` enum (the DISPATCH skill). Nothing about adding an enum entry looks like it should touch input.js at all — no import, no shared constant, no compiler/linter connection between the two files. The modulo silently kept working for the first 4 skills and simply never advanced to index 4. No error, no warning, no failing test (the existing gamepad coverage tested reachability of skills 0-3, which all still worked) — a keyboard/mouse player could reach the new skill immediately via its digit key or a chip click, so the bug was invisible on 2 of 3 input surfaces and only manifested as silence on the third.
- Fix: Replaced the literal `4` with a named `PAD_SLOT_COUNT` constant set to 5, with a comment stating explicitly that it must track (or exceed) `SKILLS`' count in rules.js, and why growing that enum without touching this constant breaks silently.
- Why this fix: A magic number with an implicit cross-file invariant is invisible to the next person (or agent) adding a 6th skill; a named constant with a comment turns an implicit coupling into a documented one — still manual, but discoverable. This is a concrete instance of a broader known law (composed-from dog#E27: "a game supporting N parallel input surfaces has no structural guarantee a NEW bindable action reaches all of them, since each surface is its own independent listener set") — the specific new mechanism here is that the surface WAS wired for the feature category (skills in general), but a capacity constant sized for the OLD count of that category silently truncated the range as the category grew, rather than the surface never being wired at all.
- Rule of thumb: Any place that cycles/indexes over "how many things are in category X" via a hardcoded number is a landmine for the day category X grows — grep for the literal count (not just the enum name) whenever adding an entry to an enum/list that something else iterates a FIXED number of times over, especially across file boundaries where no import ties them together.
- Provenance (verified/assumed): verified — a fake-gamepad Playwright harness (same `navigator.getGamepads` injection pattern as `tests/gamepad-menu-nav.mjs`) reproduced the unreachable-skill failure before the fix and confirmed LT/RT reaches index 4 after it.
- Link: Pappydapimp69/Opticon claude/opticon-3d-browser-game-3lxa2y, game/src/input.js (PAD_SLOT_COUNT), game/tests/skills.mjs
- Cited-by: 2026-10-09 · projects/pappydapimp69__brainwork.md#E48 · compatible · sandboxes/2026-10-09__radial-vs-per-axis-deadzone-snap-spurious-edges-and-hardcoded-cycle-modulo.py · observed RESULT: PASS per-axis bad-angle share 0.77 vs 0; diagonal travel x1.41; edges/rev 4 vs 4 at r=.25 and 8 vs 4 at r=.35; hardcoded modulo reaches [0, 1, 2, 3] · session_015oqQC6i1dG4qLEBR5kXrdD

## E29 — a second open playwright page throttles the first
- Date: 2026-07-30
- Project: Pappydapimp69/Opticon
- Tags: [testing] [playwright] [headless] [browser] [debugging] [gamedev]
- What: A new headless test scenario (gamepad hold-to-confirm on the intro splash) hung and then timed out waiting for a menu button that never became visible — same exact interaction sequence that already worked in a standalone test file (`gamepad-menu-nav.mjs`) failed inside a different one (`skills.mjs`) that opened it as a THIRD page.
- Why built: Extended `skills.mjs`'s existing multi-scenario structure (Watcher scenario page, then a hotseat-secrecy page) with a third scenario for a newly-fixed gamepad bug, following the file's own established pattern of opening a fresh `browser.newPage()` per scenario.
- Design: Each prior scenario's page was left open after its assertions ran (only the very first page was ever explicitly `.close()`d) — harmless as long as nothing timing-sensitive ran afterward, since the earlier scenarios only used ordinary event-driven `page.click`/`page.evaluate` calls.
- Got right: Reusing the exact same fake-gamepad injection pattern (`addInitScript` overriding `navigator.getGamepads`, same button-index hold sequence, same wait durations) as the known-working `gamepad-menu-nav.mjs` file — so when the SAME code failed in a new context, the difference had to be something about the CONTEXT, not the gamepad-simulation technique itself, which narrowed the search fast.
- Where/why it failed: The game's hold-to-confirm logic (`pollIntroHold`) is driven once per `requestAnimationFrame`, comparing elapsed wall-clock time against a threshold. Headless Chromium throttles `requestAnimationFrame` for tabs it doesn't consider foreground/active; with a second page (the still-open hotseat scenario from the PRIOR block) left alive when the third page was created, the third page's rAF loop ran too infrequently for `pollIntroHold` to accumulate 650ms of "held" time within the real 750ms `waitForTimeout` — so the intro never dismissed, the menu never appeared, and the failure surfaced three unrelated steps later as a generic "element not visible" timeout on a completely different line, not as anything pointing at rAF or tab focus.
- Fix: `await p2.close();` before opening the third page, matching the discipline the file already applied to the first page.
- Why this fix: Only one page needs to be the active/foreground tab for its rAF-driven logic to run at real-time rate; any other open page in the same browser instance is a background tab by construction and gets throttled, regardless of whether the test script ever explicitly switches focus.
- Rule of thumb: In a Playwright script that opens more than one `browser.newPage()` across sequential scenarios, close each page before opening the next UNLESS the test explicitly needs them concurrent — and treat any rAF/animation-timed assertion (holds, tweens, cooldown fills) as a first suspect the moment a multi-page headless test times out on something that works standalone, especially when the failure surfaces as a downstream "element not visible" rather than an obvious timing message.
- Provenance (verified/assumed): verified — adding the missing `.close()` call took the new scenario from a 30s timeout to passing, with the identical gamepad/hold code otherwise unchanged.
- Link: Pappydapimp69/Opticon claude/opticon-3d-browser-game-3lxa2y, game/tests/skills.mjs, game/tests/gamepad-menu-nav.mjs

## E28 — bluff field cleared before the reader ever runs
- Date: 2026-07-30
- Project: Pappydapimp69/Opticon
- Tags: [gamedev] [ai] [game-design] [state-lifecycle] [debugging]
- What: A human-facing mechanic (the Watcher's "bluff" claim) was mechanically inert — the prisoner AI's danger check referenced `game.watcher.bluff`, but that field was always null by the time the check ran, so the whole branch had been dead code since the feature shipped.
- Why built: The Watcher's bluff is meant to let a human player claim a false gaze direction to mislead a hunted prisoner; the prisoner AI's `dangerous()` helper was written to treat both the true facing AND a live bluff as risky, so a fooled AI would (in theory) avoid a tile that was actually safe.
- Design: `endWatcherTurn` clears `watcher.bluff`/`bluff2` as part of ending the Watcher's turn (ages noise, hands control to the Prisoner) — a natural place to reset per-turn claims. The prisoner AI's `dangerous()` runs during the PRISONER's turn, i.e. strictly after that clear.
- Got right: Keeping the AI's danger check as a single small pure function (`dangerous(game,x,y)`) made the fix a two-line diff once the actual timing bug was found — no architecture change needed.
- Where/why it failed: The field this mechanic depends on and the code path that reads it belong to two different turns, and nothing enforced (or tested) that the value survives the handoff. Every existing test exercised bluff-setting (Watcher's own turn) and danger-avoidance (Prisoner's turn) SEPARATELY — no test ever asserted that a bluff set on turn N actually influenced turn N+1's prisoner decision. A user report ("I can't catch anyone as Watcher") was what surfaced it — not a failing assertion.
- Fix: Snapshot the value into a new field (`watcher.lastBluff`) immediately before the clear, and have the reader consult the snapshot instead of the live field. Also added a per-difficulty-tier chance the AI actually "believes" the stale claim over the ground truth, so the mechanic has a real (if measured-small) effect, not just a non-null placeholder.
- Why this fix: A snapshot decouples "what was true during turn N" from "what turn N+1 is allowed to see," which is exactly the boundary the bug crossed silently. Fixing only the null-check without asking whether the value was EVER live at read time would have re-shipped the same dead branch under a different name.
- Rule of thumb: When a same-tick "public claim / signal" field is read by logic that runs on a LATER turn/tick/frame than the one that set it, don't assume the field survives the handoff — check what resets it, and if nothing tests the cross-turn read, that branch may already be dead code. Grep for every WRITE to the field and every READ, then ask "which turn/tick is each one on" before trusting an OR-branch that references it.
- Provenance (verified/assumed): verified — sandbox/t25-role-direction.mjs before/after (66/67/62% -> 69/67/62% capture, i.e. from zero measurable bluff effect to a small real one), full logic.test.mjs (1834/1834) and headless items/skills tests re-run clean after the change.
- Link: Pappydapimp69/Opticon claude/opticon-3d-browser-game-3lxa2y, game/src/rules.js endWatcherTurn, game/src/prisonerAI.js dangerous(). [Body restored 2026-08-01 from the original sync-commit proposal (7dc2844) — promoted empty by the steward-parse truncation bug class documented in brain#E20; PITFALLS index line was intact throughout.]
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-opticon-august-10-predicted-vs-observed-is-the-detection.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-08-01 · projects/local__sandbox-combined-opticon-prologue-latch.md#E1 · compatible · no sandbox · this session; `brain train combined` (opticon + the-game-prologue candidate pair). Note: opticon#E28's canon body was found EMPTY at composition time (steward-parse truncation at promote time, brain#E20's damage class) and was restored from its original sync-commit proposal (memory commit 69c91b8) before composing.
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E17 · compatible · no sandbox · August-10 sandboxes/loop07_conjunction_gated_branches.md
- Cited-by: 2026-08-03 · projects/pappydapimp69__opticon.md#E38 · compatible · no sandbox · game/src/prisonerAI.js (updateGazeBelief, gazeRisk, dangerous), game/src/watcherAI.js (firstOpenDoor), game/tests/fair-information.mjs, build beta-0.48.0

## E27 — a documented retry remedy became a harmful habit
- Date: 2026-07-26
- Project: Pappydapimp69/Opticon
- Tags: [devops][deployment][process]
- What: A remedy I had previously verified and written into canon — "a 404
  right after a successful Pages deploy is propagation lag; re-dispatch the
  workflow once and it clears" — hardened into a reflex, and the reflex
  eventually took the whole site down. 30 deploy runs in one day, 18 of them
  manual re-dispatches, ended with every path on the site returning a fresh
  origin 404 while the Actions runs kept reporting success.
- Why built: Two earlier memory entries (E8: deploy reports success but the
  URL 404s; E13: one clean CDN sample is not proof of convergence) correctly
  established that a post-deploy 404 is usually transient and that a second
  dispatch clears it. Both were verified first-hand at the time and were
  genuinely right about the failure they described.
- Design: The resulting loop was: deploy -> poll -> if 404, re-dispatch ->
  poll again. Applied per shipped build, and I shipped many builds in one
  session.
- Got right: The underlying diagnosis in E8/E13 was sound, and the streak-
  based verification from E13 (require N consecutive clean checks) did stop
  me from repeatedly reporting a flapping site as live.
- Where/why it failed: The remedy had no ceiling and no distinguishing test.
  "Re-dispatch once" silently became "re-dispatch whenever it's 404" across
  a long session, and nothing in the loop asked whether the 404 had CHANGED
  CHARACTER. It had: propagation-lag 404s come from some edge nodes while
  others serve, and the origin still has the site; this one returned age:0
  404s from every edge node for root AND assets, which is an origin serving
  nothing — a different failure that more dispatches can only worsen if the
  service throttles deployment frequency.
- Fix: Stop dispatching entirely on the second consecutive failure, and
  switch to a low-frequency observe-only watch. Before ANY re-dispatch,
  distinguish the two 404s: check whether different edge nodes disagree
  (propagation) or agree with age:0 on multiple paths including a known
  static asset (origin down). Only the former justifies a retry.
- Why this fix: It keeps the verified remedy for the failure it was actually
  validated against, while refusing to apply it to a superficially identical
  symptom it was never tested on.
- Rule of thumb: A verified "just retry it" remedy needs an explicit CEILING
  and a DISCRIMINATOR, or it will generalise itself into an outage. Write
  both into the lesson at the time you write the remedy: how many retries is
  too many, and what observation distinguishes the failure this remedy fixes
  from a different failure that shares its symptom. Retrying is an action on
  a shared system; the fact that it worked before is not evidence that the
  current instance is the same instance.
- Provenance (verified/assumed): Verified first-hand for the outage and its
  shape — counted 30 pages-workflow runs on the day (18 workflow_dispatch)
  from the Actions API, and confirmed via curl that root, a known CSS asset,
  and index.html all returned 404 with age:0 across three different Fastly
  edge nodes while the deploy job reported success. Scope limit: whether
  deployment-frequency throttling is the specific mechanism sits outside
  what this session established — it is the most consistent explanation for
  the evidence, but there is no access to a GitHub-side signal that would
  settle it (the Pages API path is blocked through this session's proxy), so
  the causal claim is inferred, not established.
- Composed: pages-deploy-succeeds-but-live-url-404s/E8, deploy-verify-needs-repeated-samples-not-one/E13
- Link: session 2026-07-26, Pappydapimp69/Opticon Pages outage after beta-0.31.0
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-august-10-opticon-ceiling-without-discriminator-on-a-self-feeding-gate.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E10 · compatible · no sandbox · August-10 sandboxes/loop10_a_streak_of_checks_proves_nothing_if_sticky.py

## E25 — raf polling starved behind a heavy synchronous evaluate
- Date: 2026-07-30
- Project: Pappydapimp69/Opticon
- Tags: [testing][harness][gamedev][playwright][3d]
- What: `page.waitForFunction(pred, null, {timeout})` timed out — repeatedly,
  even at 20000ms — checking a condition that a plain `page.evaluate(pred)` run
  immediately after confirmed was ALREADY true. Not a race in the app: the
  condition (a CSS class toggled synchronously inside a DOM mutation) was set
  before the wait even started polling; the wait's own polling never got to
  observe it in time.
- Why built: A headless test forces a fast game-ending state, then waits for the
  resulting screen to appear, by driving ~330 simulation steps synchronously
  inside one `page.evaluate()` call (each step includes a full Three.js render
  pass under software GL) before checking the post-condition.
- Design: `await page.evaluate(() => bigSyncLoop()); await page.waitForFunction(() => domConditionTrue());` — the obvious, idiomatic shape.
- Got right: Isolating the heavy work into one `evaluate()` call (rather than
  driving it frame-by-frame from Node) was correct and fast when it worked;
  the bug was only in HOW the follow-up condition was awaited.
- Where/why it failed: `page.waitForFunction`'s default polling strategy is
  `"raf"` — it schedules its own predicate check via `requestAnimationFrame`
  INSIDE the page. The preceding heavy synchronous call had just fully occupied
  that page's main thread; on this sandbox under concurrent CPU contention, the
  backlog of pending animation-frame work (the app's own render loop resuming)
  starved the wait's own rAF-scheduled check for the entire timeout window —
  confirmed by: a manual `page.evaluate()` immediately after the "timeout"
  reported the condition as true, and the sim's own status/ending fields were
  already correctly set. The failure was in observation, not in the app.
- Fix: Replace the `page.waitForFunction` call with a Node-side poll loop —
  `for (...) { const ok = await page.evaluate(pred); if (ok) break; await page.waitForTimeout(100); }`
  — which checks from OUTSIDE the page and does not compete with the page's own
  rAF queue for a chance to run.
- Why this fix: The thing being starved was the CHECKING mechanism, not the
  condition, so moving the poll off the page's main thread (Node driving
  `evaluate()` + a plain timer, rather than the page scheduling itself via rAF)
  sidesteps the exact resource the heavy call had just saturated.
- Rule of thumb: After any `page.evaluate()` that does substantial synchronous
  render/CPU work, do not follow it with `page.waitForFunction()` at its rAF
  polling default — it competes with the very backlog that call just created.
  Either pass `{polling: 100}` (interval-based, not raf-based) or poll from
  Node with `evaluate()` + `waitForTimeout()` instead. And when a wait times out
  on a condition you have reason to believe is already true, check the condition
  directly right after the failure before concluding the app is broken —
  widening the timeout will not fix a starved poller; the poller was never
  going to run, however long you wait.
- Provenance (verified/assumed): Verified first-hand. Reproduced the timeout
  repeatedly at both 5000ms and 20000ms, confirmed the condition was true via a
  direct `evaluate()` immediately after each failure, and confirmed the fix
  (Node-side polling) passed 5 consecutive runs after failing consistently
  before it.
- Composed: N/A
- Link: Opticon branch claude/3d-party-hallucination-game-f31dj0,
  mirage/tests/gamepad.mjs

## E26 — per surface input guards union to zero protection
- Date: 2026-07-26
- Project: pappydapimp69/opticon
- Tags: [input][ui][gamedev][architecture][testing][process]
- What: Three recorded instances of one bug class, across three projects: -
  `opticon/E14` — a global "any input skips this" interceptor, caught as a
  regression. - `dog` (today) — "any key to start" consumed Ctrl, Fn, F11 and
  R, so reaching for a browser control launched a run. - `wrong-sky/E14` — the
  general rule: the same bug class reappearing in a NEW code path that copied
  the architecture is the signal to CENTRALIZE the computation, not keep
  fixing instances by hand. The third lesson names two instances as the
  threshold. This class now has three, so the question is not whether to
  centralize but what per-instance fixing actually costs — which is
  measurable.
- Why built: Three recorded instances of one bug class (opticon#E14, dog's
  browser-key leak, and wrong-sky#E14's naming of two instances as the
  threshold to centralize) raised the question of what per-instance fixing
  actually costs, rather than whether to centralize — a question the prior
  lessons stated but never measured.
- Design: A deterministic sandbox (`sb-input-guard-divergence.mjs`) ran a
  fixed enumerated slice of the KeyboardEvent space — 28 platform keystrokes
  (bare modifiers, F1-F12, browser chords, system keys) plus 7 genuine start
  intents — through three independently-written guards: G3 (the literal
  predicate shipped in Dog today) and G1/G2 (reconstructed as the plausible
  partial fixes an author writes after hitting one symptom, matching the
  pattern recorded in opticon#E14 and wrong-sky#E14, not copied from any
  single recorded source).
- Got right: Each individual guard did exactly what its author tested for —
  the guard that inspired it always passed. The failure is not in any one
  guard's correctness against its own motivating case; it only becomes visible
  when the guards are considered together, at the app level.
- Where/why it failed: Independently-written guards do not converge; they have
  **non-overlapping** blind spots. A modifiers-only guard leaks 23 of 28
  platform keystrokes; an F-keys-plus-ctrl guard leaks 11. They are not
  nested: 17 keys leak only through the first, 5 only through the second. Each
  author fixed the symptom they personally hit and was blind in a different
  direction. The consequence is the finding worth recording. A real app has
  several such surfaces — title screen, pause card, story card, cutscene skip
  — each carrying whichever guard its author wrote. The app's true exposure is
  the UNION of what any surface accepts, and with one good guard and two
  partial ones that union was **28 of 28** platform keystrokes: every single
  one still fires somewhere. Two of three surfaces were "fixed" and the
  application-level exposure was unchanged from completely unguarded. One
  shared predicate applied to all three surfaces: 0 leaks, 0 genuine intents
  wrongly blocked. Union exposure 28 -> 0.
- Fix: Replace the independently-written per-surface guards with one shared
  predicate applied identically to every surface. Measured: three guards with
  non-overlapping blind spots left a union exposure of 28 of 28 platform
  keystrokes (completely unguarded at the app level) even though two of three
  surfaces were individually "fixed"; one shared predicate across all three
  surfaces brought union exposure to 0 of 28, with 0 genuine start intents
  wrongly blocked.
- Why this fix: Centralizing is usually argued on maintenance cost — fewer
  places to edit. The sandbox says the argument is stronger than that: with
  per-surface guards, the protection you get from fixing one surface is *zero*
  at the app level, because an attacker (here, a user's finger) only needs one
  unguarded surface. Coverage composes by union for exposure and by
  intersection for protection, so partial fixes buy nothing until the last
  surface is done. A single predicate inverts that — every improvement lands
  on every surface at once.
- Rule of thumb: For any capability claimed by MULTIPLE surfaces ("any input
  dismisses", "any click closes", "any key skips"), the app's exposure is the
  union across surfaces, not the average. Per-surface fixes therefore provide
  no protection until every surface is fixed — measure at the union, never at
  the surface you just patched, or you will report progress that does not
  exist. And treat non-overlapping blind spots as the expected outcome of
  independent fixes, not a surprise: each author guards against the symptom
  they hit. Two instances is wrong-sky/E14's threshold to centralize; the
  reason two is enough is that the second instance proves the blind spots
  differ, which is what makes convergence-by-iteration impossible.
- Provenance (verified/assumed): Verified first-hand — deterministic sandbox
  (`sb-input-guard-divergence.mjs`: a fixed enumerated slice of the
  KeyboardEvent space — 28 platform keystrokes incl. bare modifiers, F1-F12,
  browser chords and system keys, plus 7 genuine start intents — run through
  each guard; no RNG). NOTE: guard G3 is the literal predicate shipped in Dog
  today; G1 and G2 are reconstructed as the plausible partial fixes an author
  writes after hitting one symptom, not copied from recorded source. The
  divergence result depends only on their being partial in different places,
  which is the recorded pattern in opticon/E14 and wrong-sky/E14.
- Composed: opticon/E14, the-game-wrong-sky/E14,
  dog/any-key-to-start-eats-browser-controls
- Link: projects/pappydapimp69__opticon.md,
  projects/pappydapimp69__the-game-wrong-sky.md,
  projects/pappydapimp69__dog.md

## E24 — movement basis sign error passes a displacement test
- Date: 2026-07-30
- Project: Pappydapimp69/Opticon
- Tags: [gamedev][3d][input][testing][camera]
- What: A first-person movement basis with wrong signs made `W` walk BACKWARD, and
  the whole automated suite passed. The smoke test asserted the player displaced
  more than 3 units in 8 sim-seconds; it did, in the opposite direction. The same
  wrong basis also silently placed the "follow behind the lead" NPC formation
  directly IN FRONT of the camera, so five companions stood in the shot.
- Why built: MIRAGE (a first-person 3D party game) rotates screen-space WASD intent
  into world space by the camera yaw before handing it to the sim, so the sim never
  needs to know about cameras.
- Design: `move.x = ix*cos - iz*sin; move.z = -ix*sin - iz*cos`. Three's camera looks
  down -Z, so after `rotation.y = yaw` the true basis is forward = (-sin, -cos) and
  right = (cos, -sin). The correct projection is
  `x = ix*cos + iz*sin; z = -ix*sin + iz*cos`. Two sign errors, one basis.
- Got right: Separating intent from the sim was correct and worth keeping — the fix
  was three characters in one file, and the sim, tests, and NPC code needed no
  change. Deriving the formation slot from the same yaw was also right: it meant one
  bug, not two divergent conventions.
- Where/why it failed: Every automated check that could have caught it was phrased
  as a MAGNITUDE. "Did the player move?" → yes. "Did the party keep up?" → yes, they
  were 4 units away, just on the wrong side. Direction was never asserted because
  the obvious assertion (position changed) feels like it covers movement. It does
  not: a movement bug that inverts direction is indistinguishable from correct
  movement under any distance-only assertion.
- Fix: Fix the basis; then assert DIRECTION, not displacement — dot the actual
  movement delta against the camera's own forward vector and require it positive.
  And look at a rendered frame: the error was obvious in one screenshot (a wall of
  companion capsules filling the view) after being invisible to 58 passing tests.
- Why this fix: The projection of a delta onto the camera basis is exactly the
  property the code is trying to establish, so asserting it directly closes the
  whole class — including the transposed-basis and swapped-axis variants — rather
  than the single sign pair that happened to be wrong. The screenshot is the cheap
  backstop for the residue: the parts of "looks right" that are not expressible as
  a scalar.
- Rule of thumb: For anything camera-relative (movement, strafing, formation slots,
  aim), assert the SIGN of the projection onto the camera basis, never the magnitude
  of the change. A distance-only assertion passes for a control scheme that is
  exactly inverted. And in 3D, render one frame and look at it — a whole class of
  basis and orientation errors is visible instantly and invisible to arithmetic.
- Provenance (verified/assumed): Verified first-hand. Reproduced by deriving the
  basis analytically, confirmed by the passing-then-failing behaviour, and confirmed
  visually in before/after screenshots from the headless smoke test.
- Composed: N/A
- Link: Opticon branch claude/3d-party-hallucination-game-f31dj0, mirage/src/main.js
  (`step`), mirage/src/party.js (`formationSlot`)
- Cited-by: 2026-08-12 · projects/pappydapimp69__opticon.md#E42 · compatible · no sandbox · Opticon; prisoner movement resolver; custody; game/tests browser playthrough

## E23 — headless 3d capture cost not a hang
- Date: 2026-07-30
- Project: Pappydapimp69/Opticon
- Tags: [testing][harness][gamedev][3d][determinism]
- What: A Playwright screenshot taken while a full-screen overlay sat over a live
  WebGL canvas blew the default 30s timeout, and the test read as a hang. My first
  hypothesis — an animated `filter: blur() saturate()` on the overlay — was WRONG:
  removing the filter did not fix it. Measured cause: capture cost under SwiftShader
  at 1280x800 with the overlay present was ~5s (and 12s+ on the first capture after
  it appeared), versus ~0.6-1.2s without. The fix was an explicit generous timeout,
  not a code change.
- Why built: The smoke test captures review frames of a 3D game — an opening frame
  and one from inside a hallucination — because a whole class of 3D defects is
  visible in a frame and invisible to assertions.
- Design: `page.screenshot({ path })` with defaults, then
  `{ animations: "disabled" }` when the first attempt failed.
- Got right: `animations: "disabled"` IS necessary and was kept — the overlay runs an
  infinite CSS animation, and a capture that waits for the page to settle never
  settles. It was just not sufficient. Also right: measured frame rate (8-10 fps
  under software GL) before concluding anything about the page being "hung".
- Where/why it failed: A timeout on a screenshot presents identically to an infinite
  loop in page JS, so the instinct is to hunt for a runaway loop in the game. Two
  cheap measurements separated the cases: (a) a frame counter over 1s of wall time
  showed rAF still running at 8-10 fps before AND during the hallucination, and (b)
  three back-to-back captures with different options took 12s (fail), 5.1s, 0.6s —
  a warm-up/cost curve, not a deadlock. I had already committed to the blur
  hypothesis before measuring, and it survived one plausible-sounding round of
  reasoning while being false.
- Fix: Set an explicit screenshot timeout sized for software GL (90s here) and keep
  `animations: "disabled"`. Before treating a headless timeout as a hang, prove
  liveness: count rAF callbacks over a wall-clock second and read the renderer's own
  draw-call counter.
- Why this fix: The environment is genuinely slow, so the honest fix is to tell the
  harness how slow rather than to shrink what the test does. Removing the overlay
  animation to appease the screenshotter would have changed the game to suit the
  test — and, as measured, would not even have worked.
- Rule of thumb: In headless 3D, distinguish SLOW from HUNG before debugging. A
  liveness probe (frames per wall-clock second; Three's `renderer.info.render.calls`)
  costs one evaluate and tells you which problem you have. And when a plausible
  hypothesis about a perf symptom arrives before any measurement, test it by
  REMOVING it and re-measuring — mine looked right, sounded right, and was wrong.
  (Related, and separately worth keeping: an overlay animating `filter:` over a live
  WebGL canvas is still a bad idea for real players; transform/opacity are
  composited. That change was kept on its own merits, not as the fix.)
- Provenance (verified/assumed): Verified first-hand. Frame-rate probe, three-option
  capture timing comparison, and the confirmed non-fix of removing the filter are all
  observed output from this session.
- Composed: N/A
- Link: Opticon branch claude/3d-party-hallucination-game-f31dj0,
  mirage/tests/smoke.mjs (`SHOT`), mirage/css/style.css (`@keyframes breathe`)

## E22 — empty is not uncomputed in a path cache
- Date: 2026-07-30
- Project: Pappydapimp69/Opticon
- Tags: [gamedev][performance][pathfinding][caching][ai]
- What: Conflating "no path cached yet" with "cached path is empty" made five NPCs
  each run a full grid BFS on EVERY tick. Measured: 2000 simulated ticks went from
  1220ms to 205ms — ~6x — once the two states were distinguished. The per-tick cost
  of the entire rest of the simulation (drain, contagion, sightings, chatter,
  endings) was ~27µs; the thrashing path cache was ~300µs.
- Why built: Companions repath toward a moving goal at most every 0.9s; between
  recomputes they walk the cached waypoint list.
- Design: `if (!c.path || !c.path.length || c.repathTimer <= 0) { c.path = findPath(...) || [] }`.
  The guard reads as "recompute if we have no usable path or the timer expired".
- Got right: Rate-limiting repaths on a timer was the correct shape, and the BFS
  itself was fine (a 46x46 grid). The scratch-buffer reuse added later was a real but
  minor win; the sentinel was the whole effect.
- Where/why it failed: `findPath` legitimately returns `[]` — the goal cell is the
  cell you are standing in, or there is no route. An empty result is a COMPUTED
  ANSWER, but `!c.path.length` reads it as "nothing cached", so the cache never
  holds and the timer never gets consulted. It degrades silently: the game looks
  correct, the AI behaves correctly, and only throughput suffers, so nothing fails
  and nobody looks. Two separate call sites (the NPC steering and the test harness's
  own scripted bot) had the identical bug, written independently, which suggests the
  phrasing is the attractor rather than the typo.
  A second instance of the same class sat next to it: a stuck-against-geometry
  recovery set `repathTimer = 0`, i.e. "repath next tick", which for a wedged
  companion means every tick forever. Clamping it to 0.2s was invisible in play.
- Fix: Make the sentinel distinct. `null` = not computed; `[]` = computed, nothing to
  walk (steer straight at the goal). Recompute only on `path === null` or timer
  expiry. Never let a recovery path set a rate-limit timer to zero — set it to a
  small non-zero delay.
- Why this fix: Any cache whose valid value can be falsy needs a sentinel outside
  the value domain, or truthiness testing silently converts a hit into a miss. This
  is the same defect as `if (!cache[k])` on a cache that legitimately stores 0 or
  "" — the array case just hides better because `!arr.length` looks like a
  deliberate emptiness check rather than a presence check.
- Rule of thumb: If a cached computation can legitimately return empty, "is it
  empty?" is not "was it computed?" — use an explicit not-computed sentinel. And
  when profiling a game loop, suspect the cheap-looking guard around the expensive
  call before the expensive call itself: a broken guard turns an O(0.28/tick)
  amortised cost into an O(5/tick) one with no visible symptom.
- Provenance (verified/assumed): Verified first-hand by timing 2000-tick runs before
  and after (1220ms -> 205ms) and by component-timing the rest of the tick (~27µs)
  to confirm where the cost actually was.
- Composed: N/A
- Link: Opticon branch claude/3d-party-hallucination-game-f31dj0,
  mirage/src/party.js (`stepToward`), mirage/tests/balance.mjs
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-opticon-august-10-empty-cache-miss-is-a-determinism-defect.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-08-03 · projects/pappydapimp69__opticon.md#E39 · compatible · no sandbox · game/src/pathfind.js (costPath), game/src/prisonerAI.js (riskPenalty, PRISONER_SKILL.riskAversion), game/tests/risk-routing.mjs, build beta-0.49.0

## E21 — frame rate correct smoothing does not make the handoff safe
- Date: 2026-07-26
- Project: Pappydapimp69/Opticon
- Tags: [gamedev][animation][state]
- What: Fixing per-frame smoothing to be frame-rate-independent does NOT make
  the HANDOFF from that smoothing to a fixed-duration tween safe. The
  smoother is asymptotic and never exactly arrives; a tween that declares its
  own start point therefore opens with a jump equal to the leftover residual
  — measured at up to ~0.85 of a tile.
- Why built: Two motion systems ended up driving the same object. An
  exponential chase (`1 - exp(-dt/tau)`) handles idle follow — teleports, AI
  moves, anything that changes the logical position without an explicit
  animation. A fixed-duration eased tween handles a committed walk, stepping
  tile by tile. Whichever has work to do owns the object that frame.
- Design: The tween was handed grid coordinates for its origin (`from`), and
  interpolated from `worldX(from.x)` to the target tile. That is the
  logically correct start point — and it is not necessarily where the object
  currently IS.
- Got right: The smoother itself already followed the known rule (dog/E10) —
  `1 - exp(-dt/tau)`, not a constant per-frame fraction — and a control run
  in the sandbox confirms it: after 0.2s the position agrees to ~2e-3 between
  30fps and 144fps, where a constant-fraction smoother diverges wildly
  (0.62 vs 0.99). That fix is real and doing its job.
- Where/why it failed: It solves a different problem than the one at the
  seam. Exponential decay approaches its target but never reaches it, so at
  any moment the object sits some residual short. A sandbox stepping the
  chase for a given idle duration and then starting the tween measured the
  discontinuity: 0.85 tiles after a 0.02s idle, 0.61 after 0.05s, 0.14 after
  0.2s, 0.007 after 0.5s. The pop is largest exactly when the handoff is
  quickest — the case a developer is least likely to test by eye — and it
  still varies with frame rate (0.13 tiles of spread across 30/60/144fps at
  a 0.02s idle) even though the smoothing formula is frame-rate correct.
- Fix: The tween starts from the object's ACTUAL rendered position, captured
  at the moment it is queued, rather than from the grid coordinate it is told
  it begins at. Later legs of a multi-step walk can keep using exact tile
  coordinates, since by then the tween itself put the object there.
- Why this fix: It removes the class of bug rather than the instance. Any
  future caller that lets a frame render between "the simulation moved" and
  "queue the animation" is now safe by construction instead of by timing.
- Rule of thumb: Wherever a smoothed/asymptotic follower hands an object to
  an explicit tween, the tween MUST read its origin from the object's current
  transform, never from the logical/grid value it is being told it starts at.
  Making the smoother frame-rate-correct is necessary and not sufficient —
  the two are different bugs, and the seam between two motion systems is its
  own hazard, distinct from either system being individually correct.
- Provenance (verified/assumed): Verified first-hand in a deterministic
  sandbox (`sandbox/smoothing-to-tween-handoff.mjs`, no RNG, dt a parameter)
  which reproduces the pop and the frame-rate spread, and includes a control
  showing the smoother alone IS frame-rate independent plus a contrast run of
  the constant-fraction bug. SCOPE, stated honestly: in this codebase the
  defect is LATENT, not active — both current callers queue the tween in the
  same tick as the simulation move, so the residual is ~0 today. I verified
  that by reading both call sites, not by observing a pop in the running
  game. The fix was applied defensively so that timing coincidence stops
  being load-bearing; the full test suite (1834 logic assertions plus the
  headless suites) is unchanged by it, which is the expected result if the
  residual really is ~0 today.
- Composed: frame-rate-independent-smoothing/E10
- Link: beta-0.31.0+, sandbox/smoothing-to-tween-handoff.mjs
- Cited-by: 2026-08-01 · projects/local__sandbox-edge-draft-opticon-scrub.md#E1 · compatible · no sandbox · this session; `brain train edge` (draft + opticon, 14 shared tags)

## E20 — a constant rng silently disables probability parameters
- Date: 2026-07-26
- Project: Pappydapimp69/Opticon
- Tags: [testing][simulation][method]
- What: Pinning a sandbox's random source to a CONSTANT to make it
  deterministic silently disabled every probability-threshold parameter
  under test, collapsing two agent tiers into one identical agent — and the
  sandbox then reported a clean, plausible, entirely false result that I
  published before catching it.
- Why built: A deterministic sandbox was needed to settle a design question
  (does a difficulty label point the right way for each role?). Determinism
  matters because the effect sizes were small, and run-to-run noise would
  have swamped them.
- Design: Determinism was achieved the quick way — pass `() => 0.5` as the
  agent's rng, so every run is byte-identical.
- Got right: Wanting determinism at all was correct; the effects being
  measured were 2-13 points, small enough that unseeded randomness would
  have made the grid unreadable. The sandbox also correctly caught a
  genuinely inverted design before it shipped.
- Where/why it failed: Every parameter of the form `rng() < threshold`
  becomes a CONSTANT predicate under a constant rng — `0.5 < 0.4` is always
  false, `0.5 < 0.15` is always false. Two tiers whose only difference was
  0.4 vs 0.15 therefore executed identical code paths. The sandbox dutifully
  reported them as producing near-identical outcomes, which reads exactly
  like "this lever is weak" rather than "this lever is switched off." I
  reported the numbers as evidence of a working fix. A separate sanity check
  — average tiles moved per game, which came out IDENTICAL to one decimal
  place for the two tiers — is what exposed it.
- Fix: Replace the constant with a SEEDED PRNG (mulberry32 off the run
  seed). Still perfectly reproducible, but the distribution is real, so
  threshold parameters actually branch. Re-measuring flipped the conclusion:
  what had looked like a correctly-signed-but-weak lever was in fact flat.
- Why this fix: Determinism and non-degeneracy are different properties, and
  a constant only buys the first. A seeded generator buys both.
- Rule of thumb: NEVER make a simulation deterministic by pinning its random
  source to a constant — use a seeded PRNG. A constant turns every
  `rng() < p` comparison into a fixed branch, so any parameter expressed as a
  probability is silently switched off, and tiers that differ only in
  probability become the same code path. The failure is especially dangerous
  because the output looks healthy: it reports "small effect," not "error."
  Cheap guard: before trusting a tier comparison, assert the tiers produce
  DIFFERENT intermediate behaviour (step counts, action mixes) — if two
  tiers are identical to the decimal, the knob is off, not weak.
- Provenance (verified/assumed): Verified first-hand — observed the two
  tiers producing 55.3 average tiles moved per game to identical precision,
  traced it to the constant rng, swapped in a seeded PRNG, and re-ran the
  full grid; the published conclusion changed as a direct result and the
  earlier claim was withdrawn in the tension ledger.
- Composed: N/A
- Link: Tension T25 (CORRECTION entry), sandbox/t25-difficulty-semantics.mjs
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-opticon-brain-builder-constant-rng-fakes-the-binding-rate.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E19 · compatible · no sandbox · August-10 sandboxes/loop06_seed_variance_without_outcome_variance.md
- Cited-by: 2026-08-10 · projects/pappydapimp69__mirage.md#E7 · compatible · no sandbox · pappydapimp69/mirage main, tests/balance.mjs `deceived` policy + tools/sandboxes/oracle-vs-deception.mjs

## E19 — a sandbox refuted my tier design twice in one session
- Date: 2026-07-26
- Project: Pappydapimp69/Opticon
- Tags: [ai][balance][method]
- What: The same intuition — "a more careful agent is a better agent" — was
  wrong twice in one session, in two unrelated subsystems, and both times a
  small deterministic sandbox caught it within minutes where reasoning had
  produced a confident wrong answer.
- Why built: Two features needed a competence knob: an AI that decides
  whether to detour for a beneficial pickup, and difficulty tiers for an AI
  that is trying to avoid being caught. In both cases the intuitive design
  was "the better version is more careful": detour to collect useful things,
  and stop moving more often so you are heard less.
- Design: First pass at each was written from that intuition — a 3-tile
  pickup detour radius, and a "hard" tier with the HIGHEST stopping
  discipline (halt after 2 tiles rather than pressing on).
- Got right: Both subsystems already had a whole-run simulator available,
  and both times the instinct to measure rather than ship-and-hope was what
  caught the error. Keeping the sandbox deterministic (fixed seeds, fixed
  tie-breaking, no wall-clock) meant a 2-point difference was trustworthy
  signal rather than noise.
- Where/why it failed: Both designs made the agent measurably WORSE at its
  own objective. The pickup detour dropped the escape rate (41/34/13% ->
  38/32/10%); the "more disciplined" hard tier RAISED the capture rate
  against it (61/62/64%, i.e. the difficulty label pointed the wrong way).
  Same root cause both times: in a turn-based game where the opponent acts
  on the same clock, every turn spent being careful is a turn the opponent
  gets for free. Caution has a price denominated in opponent actions, and
  that price is invisible to a per-turn analysis — it only shows up when you
  score whole runs.
- Fix: Cut the detour radius to 1 (measured indistinguishable from
  baseline), and INVERT the discipline knob so the competent agent presses
  on while the careless one dawdles. Both values recorded next to their
  constants with the numbers that chose them.
- Why this fix: The correction is not "less caution is better" as a blanket
  rule — it is that caution must be priced against tempo, and the only way
  to see that price is a whole-run score.
- Rule of thumb: Treat "the better agent is the more careful agent" as a
  HYPOTHESIS, never a starting assumption, in any domain with a shared
  clock. Before shipping a competence/difficulty knob, run it through a
  whole-run simulator and confirm the metric moves the way the LABEL claims
  — including the zero/neutral setting, which is what separates "the feature
  is wrong" from "this parameter is wrong." A knob whose sign you never
  measured is a coin flip you have described as a design.
- Provenance (verified/assumed): Verified first-hand — both failures were
  observed as simulator output before any fix, both corrections re-measured
  after, all with fixed seeds and no wall-clock dependence. Numbers quoted
  above are that output, not estimates. The second case additionally
  required building a purpose-made sandbox
  (`sandbox/t25-difficulty-semantics.mjs`) that crosses two axes the shipped
  code deliberately couples.
- Composed: tempo-is-the-scarce-resource/E17
- Link: beta-0.26.0 and beta-0.30.0, Tension T25

## E18 — difficulty that tunes a shared rule inverts for one role
- Date: 2026-07-26
- Project: Pappydapimp69/Opticon
- Tags: [gamedesign][asymmetric][difficulty]
- What: In an asymmetric two-role game, the difficulty setting turned out to
  be tuning a SHARED rule (how easily anyone in the tower catches someone)
  rather than the human's opponent — which silently inverts the label for
  whichever role benefits from that rule. Measured: raising difficulty makes
  a human Watcher's job EASIER, not harder.
- Why built: Difficulty originally only changed the opponent AI's bluff
  frequency, which an AI-vs-AI balance sim cannot measure at all (bluffing
  only works on a human). A capture-exposure ladder was added so difficulty
  had a mechanical lever the sim could see: easy catches you only when lit,
  hard also when noise is merely adjacent.
- Design: One `difficulty` string flowed to two different places — the
  Watcher AI's decision tuning, and `isExposed()`, the capture rule inside
  the scan. Nobody noticed these are different axes because in the
  single-player-Prisoner case they point the same way.
- Got right: Tiering exposure DID make difficulty measurable, which was the
  original goal, and the balance sim correctly showed ordered difficulty for
  a human Prisoner. The instinct to give difficulty a sim-visible lever was
  sound.
- Where/why it failed: The capture rule is symmetric — it governs the tower,
  not the AI. So when the human IS the Watcher, "hard" hands the human a
  more forgiving capture rule while their AI opposition barely changes. A
  sandbox that separated the two axes (drive the AI's behaviour tier and the
  exposure tier independently, 240 fixed-seed games per cell of a 3x3 grid)
  measured the split: the exposure rule alone swings the capture rate by
  ~13 points easy->hard, while the AI's behaviour tier alone swings it by
  ~3. The label is dominated ~4.7:1 by a rule that helps whoever holds the
  tower.
- Fix: Route difficulty per ROLE rather than globally — the tier the human
  faces must always describe the human's opposition, so the shared rule is
  held at a neutral baseline for the side it would otherwise gift, and the
  opposing AI's own competence carries the difficulty for that role.
- Why this fix: It keeps the sim-visible lever that made difficulty
  measurable in the first place, without letting a symmetric rule masquerade
  as an opponent-strength setting for one of the two roles.
- Rule of thumb: In an asymmetric game, audit every consumer of the
  difficulty setting and ask of each: does this make the HUMAN'S OPPONENT
  better, or does it change a rule BOTH sides sit under? A shared-rule
  consumer inverts the label for whichever role the rule favours, and the
  inversion is invisible if you only ever playtest (or simulate) one role.
  Separate "opponent skill" from "world harshness" as two named axes, then
  decide per role which one the label should drive.
- Provenance (verified/assumed): Verified first-hand by building and running
  a deterministic sandbox model (`sandbox/t25-difficulty-semantics.mjs`,
  fixed seeds, fixed AI tie-breaking, no wall-clock timing) that crosses the
  two axes in a 3x3 grid of 240 games each; the reported numbers are that
  model's output, not an estimate. Required one small production change to
  make the axes separable at all (an optional exposure-tier parameter).
- Composed: tier-capture-exposure-by-difficulty/E1
- Link: Tension T25, sandbox/t25-difficulty-semantics.mjs

## E17 — tune ai detours against the sim not intuition
- Date: 2026-07-26
- Project: Pappydapimp69/Opticon
- Tags: [ai][gamedesign][balance]
- What: Teaching the AI to detour for beneficial pickups made it measurably
  WORSE at winning, and the intuitive tuning value was the wrong one — the
  cost was the detour itself, not anything about the pickups.
- Why built: A consumable-item system had just shipped, and only the human
  player could use it; the AI-controlled characters walked past every
  pickup. Making them collect and spend items looked like a pure upgrade.
- Design: At the start of each AI turn, if a pickup sits within
  `ITEM_DETOUR` tiles and the inventory isn't full, path to it instead of
  the objective for that turn; then spend carried items opportunistically
  when their preconditions are met.
- Got right: The item-spending heuristics themselves were fine, and the
  existing whole-run balance simulator (hundreds of complete games per
  difficulty tier) made the regression visible immediately instead of
  months later — this is exactly the "reachability/outcome is its own test
  axis" property that simulator was built for.
- Where/why it failed: With the detour radius set to an intuitive-feeling 3
  tiles, the win rate dropped consistently across ALL difficulty tiers
  (41/34/13% -> 38/32/10% over 150 games each). The natural reading was
  "the items must be weak or the spend heuristics wrong."
- Fix: A/B the constant against the simulator instead of theorizing. Setting
  it to 0 (never detour; only collect what the route happens to cross)
  restored the baseline EXACTLY — isolating the detour, not the items, as
  the entire cost. Setting it to 1 (grab only what's literally adjacent)
  measured indistinguishable from baseline while still leaving the AI
  carrying and spending items. Shipped 1, with the measurement recorded in
  the constant's own comment so a later "tidy-up" can't silently restore 3.
- Why this fix: The zero case is the decisive experiment — it separates
  "the new behaviour is bad" from "one parameter of it is bad," which no
  amount of reasoning about the heuristics would have settled.
- Rule of thumb: In a turn-based game where each side acts on a clock, TEMPO
  is usually the scarce resource — a detour for a beneficial pickup costs
  turns during which the opponent still gets its full action, so a
  "free" upgrade can be a net loss. Never pick a detour/greed radius by
  intuition: A/B it against a whole-run simulator including the ZERO case,
  since that's what tells you whether the feature or merely its tuning is
  at fault. Record the measured numbers next to the constant — an
  unexplained tuning value invites someone to "fix" it back later.
- Provenance (verified/assumed): Verified first-hand — three full runs of
  the balance simulator at 150 games per difficulty tier for radius 3, 0,
  and 1, with the 0 case reproducing the pre-change baseline exactly; a
  committed regression test also asserts the detour never reintroduces the
  non-termination failure a previous fix had eliminated.
- Composed: N/A
- Link: beta-0.26.0, PR #27 (Pappydapimp69/Opticon)

## E16 — validate content against the finished world not the plan
- Date: 2026-07-26
- Project: Pappydapimp69/Opticon
- Tags: [gamedesign][procgen][content]
- What: Adding consumable items whose effects target specific world objects
  (a lockpick needs a door, wire cutters need a switch) meant the item
  POOL had to be computed from the finished generated map, not from the
  generator's config — because the objects those items act on are placed
  probabilistically and a map can legitimately come out with zero of them.
- Why built: A design proposal listed four prisoner items. Two of them
  ("grapple the moat", "lockpick a door") were written against a mental
  model of the map rather than the actual generator.
- Design: Item kinds each declare a `requires` field naming the object type
  they act on (or `null` for the ones that need nothing). Placement runs as
  the LAST step of map generation, scans the finished `objects` grid for
  what is actually present, and filters the eligible pool to kinds whose
  requirement is satisfied. Kinds with no requirement guarantee the pool is
  never empty.
- Got right: Auditing the proposed items against the real generator BEFORE
  building caught two problems at design time rather than in play — a
  "grapple across the moat" item was invalid outright (the moat only rings
  the tower and prisoners never cross it, so the item had no situation to
  exist in), and door-dependent items needed the guard above. The
  `requires` field also documents the dependency in one place instead of
  leaving it implicit in placement code.
- Where/why it failed: The first draft of the design assumed map features
  that either didn't exist in the shape imagined (the moat) or existed only
  probabilistically (doors at ~70% per boundary slot, windows at 35% per
  candidate wall — a known-flaky property that had already forced a
  retry-loop in an earlier test). Placing content up front, from config,
  would have scattered unspendable items on the unlucky seeds.
- Fix: Compute the eligible pool from the finished map — after object
  placement AND after the connectivity-repair pass that can carve tiles —
  then filter. Verified by generating 200 maps and asserting no item was
  ever placed whose required object was absent.
- Why this fix: It makes the invariant structural rather than statistical.
  There is no seed on which the guarantee can fail, because the check reads
  the same grid the player will actually play on, at a point where nothing
  further will modify it.
- Rule of thumb: When adding content (items, quests, hints, tutorials) that
  depends on specific features of a PROCEDURALLY generated world, validate
  each piece against the finished artifact, not against the generator's
  config or your mental model of the layout — probabilistic placement means
  "the map has doors" is a per-seed fact, not a guarantee. Have each piece
  of content declare its dependency explicitly, and always include some
  dependency-free content so the eligible pool can never come out empty.
  Also worth doing at DESIGN time: check each proposed item against what
  the generator really produces before building any of them.
- Provenance (verified/assumed): Verified first-hand — audited the
  generator's placement functions and found the moat is tower-adjacent only
  (invalidating one proposed item) and that doors/windows are probabilistic;
  then generated 200 seeded maps asserting the placement invariant held on
  every one, plus a 60-seed assertion in the committed logic suite
  (1775 assertions passing).
- Composed: N/A
- Link: beta-0.22.0, PR #23 (Pappydapimp69/Opticon)
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-dog-opticon-scatter-fixes-are-per-axis-and-per-seed.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-opticon-recursion-per-seed-dependency-under-fixed-suite.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-10-12 · projects/pappydapimp69__brainwork.md#E164 · compatible · sandboxes/2026-10-12__koan-commentary-elimination-leak.py · observed RESULT: PASS koan irresolvability holds to 6/8 critiqued; flips at n-1=7; verse naming and post-dedupe commentary also leak; 5/5 checks. Sweep resolvable only at 7 critiqued. · session_01XCe61chZn6agE2zVwbgxdQ

## E15 — ready and usable are two different gates
- Date: 2026-07-26
- Project: Pappydapimp69/Opticon
- Tags: [gamedesign][ui][ai]
- What: Cooldown-gated abilities needed TWO separate predicates — "off
  cooldown" (`ready`) and "would actually do something right now"
  (`usable`) — because several abilities can be fully charged yet have no
  valid target, and conflating the two produced both a misleading UI and an
  AI that wasted cooldowns on no-ops.
- Why built: Four Watcher abilities on cooldowns. Three of them can be
  charged but inert: "slam a door" with no open door, "refresh noise
  traces" with no noise on the board, "add a second bluff" with no first
  bluff declared.
- Design: `skillReady(game, skill)` is the pure cooldown check.
  `skillUsable(game, skill)` is `skillReady && <per-skill precondition>`.
  The UI renders three visual states from the pair (cooling / charged-but-
  inert / ready), and the AI's chooser filters on `skillUsable` so it can
  never select an ability that will refuse.
- Got right: Making a refused use NOT spend the cooldown, decided up front.
  Every early-return in the ability handler happens before the cooldown is
  set, so a mis-click or an AI edge case costs nothing — an ability that
  "did nothing but went on cooldown anyway" is the most frustrating
  possible outcome and it's easy to write accidentally by putting the
  cooldown assignment at the top of the function.
- Where/why it failed: The first sketch had a single `canUse` check and
  put the cooldown assignment early in the handler. That shape makes two
  distinct bugs almost inevitable — the UI shows an ability as available
  when pressing it can only fail, and any caller (especially an AI picking
  greedily from "available" abilities) burns a real resource on nothing.
- Fix: Split the predicate in two, keep the cooldown assignment behind
  every precondition check, and make both the UI and the AI consume the
  same `usable` predicate rather than each re-deriving availability.
- Why this fix: One shared predicate means a future ability with a new
  precondition is automatically respected by both the renderer and the AI —
  neither has its own copy of "when is this offerable" to drift out of sync,
  which is the same class of problem as a role check duplicated across
  several turn handoffs.
- Rule of thumb: For any cooldown/charge-gated ability, model "recharged"
  and "has a valid target right now" as two separate predicates, and have
  every consumer (UI affordance, AI chooser, input handler) read the
  combined one rather than re-deriving it. Assign the cooldown only AFTER
  every precondition passes, so a refused activation is always free —
  otherwise the ability that silently did nothing still costs the player
  its full cooldown.
- Provenance (verified/assumed): Verified first-hand — the committed logic
  suite asserts each ability is "ready" but not "usable" in its inert state,
  that a refused use leaves the cooldown untouched, and that a blocked
  remote-lock (prisoner standing in the doorway) neither closes the door nor
  spends the charge; 1814 assertions passing, plus a headless test
  confirming the UI's cooling state renders after a real use.
- Composed: role-check-instance-awareness/E10
- Link: beta-0.23.0, PR #24 (Pappydapimp69/Opticon)

## E14 — global input interceptor silently eats tests first action
- Date: 2026-07-26
- Project: Pappydapimp69/Opticon
- Tags: [testing][input][regression]
- What: Adding a global "any control skips this" interceptor (an intro
  cutscene, skippable by pressing/tapping/clicking anything) silently broke
  one of eight existing headless tests that drive input immediately after a
  state transition — the other seven still passed, by coincidence.
- Why built: Standard UX convention for a skippable cutscene: any input
  should skip it, not just a dedicated button, so an impatient player never
  feels stuck.
- Design: `handleIntent()` gained a top branch — if a cutscene is active,
  call `skipIntro()` and swallow the intent instead of dispatching it.
- Got right: The gate was applied at the single existing choke point
  (`handleIntent`), so keyboard/gamepad/touch were all covered by one
  change, no per-input-method special-casing needed.
- Where/why it failed: Eight pre-existing headless tests start a game then
  immediately press a key/click a control to drive gameplay (move, break a
  window, toggle sound, teleport-then-verify). After this change, that FIRST
  post-start action always lands during the cutscene window and gets
  consumed as a skip instead of doing what the test intended. Only
  `window-break.mjs` actually failed its assertion (it directly checks
  `game.brokenWindows` after a Shift+direction press) — the other seven
  happened to not assert on anything that specific first action was
  supposed to change, so they passed despite silently not doing what their
  code implied. A regression like this can hide in a green suite.
- Fix: Every test that starts a game and then drives input was updated to
  call `renderer.skipIntro()` explicitly (via `page.evaluate`) right after
  the start-button hold completes, before any gameplay input. One test
  (`window-break.mjs`) additionally needed a second `skipIntro()` call after
  its own retry-loop, because each `#btnRestart` click re-enters
  `startGame()` and re-arms a fresh cutscene — a loop that clicks Restart N
  times needs the skip repeated, not just the initial one.
- Why this fix: Keeps the skip-on-any-input UX and lets tests stay in
  control of timing explicitly rather than either (a) hard-coding wait
  durations long enough to outlast the cutscene (slow, brittle to future
  timing changes) or (b) removing the skip-on-any-input convention (worse
  UX) to avoid disturbing tests.
- Rule of thumb: Before shipping any new "intercept ALL input for a window
  after a state transition" feature (cutscenes, loading screens, transition
  animations, a global modal), grep every existing test for input driven
  right after that transition — a green suite doesn't prove the interceptor
  is harmless, because a swallowed action only fails a test that happens to
  assert on that specific action's effect, not just "did anything throw."
- Provenance (verified/assumed): Verified first-hand — ran the full existing
  test suite after adding the interceptor, one failure surfaced
  (window-break.mjs), traced it to the retry-loop's repeated re-arming,
  fixed, reran clean. Scope note: this exercised only the paths already
  covered by the existing suite — the full suite passing is evidence for
  those specific tested paths, a narrower claim than the whole interaction
  surface.
- Composed: N/A
- Link: beta-0.19.0, commit 3c21f43
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-dog-opticon-two-silent-losses-inside-one-coarse-assertion.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-07-26 · projects/pappydapimp69__opticon.md#E26 · compatible · no sandbox · projects/pappydapimp69__opticon.md, projects/pappydapimp69__the-game-wrong-sky.md, projects/pappydapimp69__dog.md

## E13 — deploy verify needs repeated samples not one
- Date: 2026-07-26
- Project: Pappydapimp69/Opticon
- Tags: [deploy][verification][cdn]
- What: A single curl check reporting HTTP 200 with the correct build string
  was treated as proof the GitHub Pages deploy was live; the user reported
  it wasn't, and a direct recheck showed a real 404 seconds later.
- Why built: This project's own canon (E8) already documents that a Pages
  deploy can report workflow success while the live URL still 404s, fixed
  by a second `workflow_dispatch`. A Monitor loop was set up to poll until
  one clean 200+build-match sample landed, treating that as "done."
  status.
- Design: `while true; curl ...; if 200 and build matches: break`.
- Got right: Checking at all (vs. trusting the Actions run's own "success"
  status) was the right instinct — that's exactly what E8 warns against.
- Where/why it failed: A CDN (Fastly, fronting GitHub Pages) serves from
  multiple edge nodes that can be in different states during propagation —
  one `curl` hit a node that had already picked up the new deploy (200,
  correct build), the very next request (moments later, reported by the
  user) hit a different edge node still serving the stale/interim 404. A
  single sample from a CDN mid-propagation is not evidence of a stable
  state; it's evidence of ONE edge node's state at ONE instant. Root-path
  and explicit `/index.html` requests even returned different results in
  the same few seconds, most likely for the same reason.
- Fix: Re-triggered the deploy, then required 3 CONSECUTIVE clean checks
  (200 + correct build string), 20s apart, before reporting the deploy as
  live — a streak, not a single sample.
- Why this fix: A streak of N consecutive successes across a real time
  window is much stronger evidence of a converged CDN than one success,
  cheap to implement (a counter that resets on any miss), and generalizes
  to any edge-cached/multi-node deploy target, not just GitHub Pages.
- Rule of thumb: When verifying a deploy behind a CDN or any multi-node
  edge, a single successful check is a data point, not proof of
  convergence — require a short streak of consecutive successes across a
  real time window (not consecutive retries with no delay, which can all
  hit the same warm connection/node) before reporting "live." This applies
  doubly when the deploy target is already known (via a prior memory entry)
  to have a propagation-lag failure mode — one clean sample can look like
  confirmation of the fix when it's actually a lucky edge node.
- Provenance (verified/assumed): Verified first-hand — the user directly
  observed the site was not live immediately after being told it was;
  reproduced with `curl -sSI` showing a genuine GitHub-served 404 body
  ("Page not found · GitHub Pages") seconds after a 200+correct-build
  sample from a different edge node (`x-served-by` differed between the two
  requests, confirming different Fastly cache nodes).
- Composed: pages-deploy-succeeds-but-live-url-404s/E8
- Link: beta-0.19.0 deploy, session 2026-07-26
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-brain-opticon-verification-streak.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E10 · compatible · no sandbox · August-10 sandboxes/loop10_a_streak_of_checks_proves_nothing_if_sticky.py

## E12 — checking a fix precondition is not applying it
- Date: 2026-07-26
- Project: Pappydapimp69/Opticon
- Tags: [process][git][squash-merge]
- What: The squash-merge branch-staleness fix (this project's canon E7 —
  reset the branch onto the base's current tip before every subsequent PR)
  recurred anyway, on the very next commit after the last time it was
  applied correctly.
- Why built: E7's fix procedure was already known and had been applied
  successfully across five-plus prior PRs this session.
- Design: Before committing, `git log origin/master --oneline -1` was run
  and its output read/confirmed as the expected post-merge tip.
- Got right: The verification step itself was correct — it did surface the
  right tip SHA, and the habit of checking before committing is the right
  instinct.
- Where/why it failed: Reading the correct tip SHA was silently treated as
  equivalent to being ON that tip. The local branch was never actually
  `git checkout -B`'d onto it — the new commit landed on top of the OLD
  local HEAD (which still carried the pre-squash ancestry), so the branch
  diverged from master exactly the way E7 describes, and the next PR showed
  a real merge conflict (`mergeable_state: "dirty"`) despite the check
  having "passed."
- Fix: Same as E7's original fix (stash any WIP, `git checkout -B <branch>
  origin/master`, cherry-pick the new commit, force-push) — but the point of
  THIS entry isn't the fix, it's that having a documented fix and a
  verification habit didn't prevent reapplying the fix incorrectly.
- Why this fix: N/A (see E7) — this entry exists to close the gap between
  "checked" and "acted on."
- Rule of thumb: A verification step that reads a fact (a tip SHA, a
  config value, a file's contents) is not the same as a step that ACTS on
  that fact — if the two are separate statements in the workflow, the
  action can silently drift from what the check confirmed. When a known
  gotcha has a "check X, then do Y" fix, prefer making the check the thing
  that PRODUCES Y mechanically (e.g. `git checkout -B branch $(git rev-parse
  origin/master)` in one step) over a human/agent reading X and then
  separately remembering to do Y from a different mental step.
- Provenance (verified/assumed): Verified first-hand — reproduced the exact
  failure (PR reported `mergeable_state: "dirty"` with an unexpectedly high
  file/commit count), diagnosed the cause via `git log branch ^master`
  showing pre-squash commits still present, applied E7's fix, confirmed the
  same PR then showed `mergeable_state: "unstable"` (clean diff, pending
  checks only) and merged.
- Composed: squash-merge-branch-reuse-gotcha/E7
- Link: beta-0.18.0, PR #19 (Pappydapimp69/Opticon)

## E11 — viewer vantage must not be derived from turn order
- Date: 2026-07-26
- Project: Pappydapimp69/Opticon
- Tags: [rendering][camera][multi-entity]
- What: Camera follow, field-of-view masking, the exposure-danger vignette,
  and self-noise ping markers all derived "which prisoner is this for" from
  `game.activePrisoner` — whichever prisoner's turn is currently resolving.
- Why built: `game.activePrisoner` was already the correct source for turn
  logic (movement resolution, MP checks, end-turn handoff), so reusing it for
  the rendering/UX layer looked like the same value, just read from a
  different file.
- Design: A single-player human always controls exactly one prisoner
  (index 0 by construction — hotseat has exactly 1 prisoner, single-player
  companions always spawn at index 1+), but the turn state machine now
  cycles `activePrisoner` through AI companions automatically as part of
  landing multi-prisoner support (see E10 in this project's canon).
- Got right: The turn-handoff instance-awareness audit from E10 correctly
  found and fixed the input-gating side (`humanControlsPrisoner()` and its
  three call sites).
- Where/why it failed: The audit only covered "who may act." It missed a
  second, distinct category of consumer: "whose viewpoint is this frame
  rendered from." During an AI companion's automated turn,
  `game.activePrisoner` correctly pointed at the companion for turn logic —
  and the camera, FoV darkening, exposure vignette, and self-noise cue all
  silently followed it there too, yanking the human's camera onto a teammate
  and firing the danger/heartbeat cue for the companion's exposure instead
  of the human's own.
- Fix: Introduced a `humanPrisonerIndex()` accessor (always 0, matching the
  spawn-order invariant already relied on by `humanControlsPrisoner()`) and
  threaded it through as an explicit `viewedPrisoner` option into the
  renderer's per-frame update, replacing every "whose eyes is this frame
  for" read of `game.activePrisoner` in the rendering/vignette/self-noise
  path. Turn-logic reads of `game.activePrisoner` (movement, MP, handoff)
  were left untouched — they were already correct.
- Why this fix: Keeps the renderer ignorant of role/mode config (it already
  takes `showPrisoner`/`showWatcherInfo` as caller-supplied opts, same
  pattern) while making "acting index" and "viewing index" two named,
  independently-readable values instead of one field doing both jobs.
- Rule of thumb: When a shared "whose turn/entity is this" field starts
  being read by BOTH turn logic and the presentation layer, audit the
  presentation reads separately — "who may act" and "whose viewpoint is this
  rendered from" are different questions that only happen to have the same
  answer when there's exactly one controllable entity. Scaling from 1→N
  entities can silently split them.
- Provenance (verified/assumed): Verified first-hand — traced every
  `activePrisoner]` read across render.js/main.js/rules.js/ui.js/prisonerAI.js,
  classified each as turn-logic (untouched) vs. viewer-vantage (fixed),
  confirmed the fix against the full logic suite (826/826) plus the
  exposure-cue, ai-prisoners, smoke, views, and wincheck headless tests, all
  green before shipping.
- Composed: role-check-instance-awareness/E10
- Link: beta-0.17.0, commit 5a5b8b8
- Cited-by: 2026-08-12 · projects/pappydapimp69__opticon.md#E42 · compatible · no sandbox · Opticon; prisoner movement resolver; custody; game/tests browser playthrough

## E10 — role check must become instance aware at every handoff
- Date: 2026-07-26
- Project: Pappydapimp69/Opticon
- Tags: [gamedev] [architecture] [state] [multi-agent]
- What: Scaling a single-player mode from 1 controllable entity to N (single prisoner -> a 3-prisoner group) required auditing THREE separate turn-handoff points in the control flow, not one — a boolean "does the human control this role" check that was correct when the role only ever mapped to one entity became silently wrong (would have stalled the game waiting on input that never arrives) the moment that role could map to multiple entity instances, only some of which are human-controlled.
- Why built: The existing single-prisoner game had exactly one decision point gating human input: `humanControlsPrisoner()`, a pure role check (`app.config.humanRole === "Prisoner"`). Every turn-advance path assumed "if the human plays this role, the NEXT thing that happens is human input" — true by construction when the role only ever had one entity.
- Design: Adding AI companions made `game.prisoners` an array with an `activePrisoner` index that cycles among ALL of them (already correct in the sim layer, which was array-based from the start). But the human should only ever control INDEX 0 specifically, not "the Prisoner role" as a whole — companions (index > 0) are always AI, even in the mode where the human's role IS Prisoner.
- Got right: The underlying sim/turn-cycling logic (`nextActivePrisoner`, win/loss conditions checking `.some`/`.every` across all prisoners) was already fully generic and needed zero changes — it had been written array-based from the start even when only ever fed one entity. The bug was entirely in the presentation/orchestration layer's assumptions, not the simulation.
- Where/why it failed: There were THREE independent places in the turn-handoff chain that each separately decided "who acts next," and each had baked in the old singular assumption: (1) the input gate itself (`humanControlsPrisoner()`), (2) the tail of the human-Watcher's-turn-just-ended handler, and (3) the tail of the AI-Watcher's-turn-just-ended handler. Fixing only the input gate (the "obvious" place) would have left the other two silently showing "your move" banners and waiting forever whenever the next active entity was actually an AI companion — a stall that would only manifest with more than one entity per role, invisible in any test that only ever exercised the 1-entity configuration.
- Fix: Made the role check instance-aware (`g.activePrisoner === 0` gates human control, not just `humanRole === "Prisoner"`), then grepped for every OTHER place in the codebase that made the same "next actor is human" assumption implicitly, updating all three consistently to call the same instance-aware predicate rather than re-deriving the logic ad hoc at each site.
- Why this fix: A single source-of-truth predicate reused at every handoff point means a FOURTH handoff added later (if the turn state machine grows again) inherits correct behavior automatically as long as it calls the same function — rather than requiring a fresh audit of "is this yet another place with the same assumption" each time.
- Rule of thumb: When a boolean "is this human-controlled" check was written for a SINGULAR entity per role and the role is being generalized to admit MULTIPLE entities (companions, additional agents, a squad), don't just fix the one input gate that's obviously wrong — grep every OTHER decision point in the turn/state machine that implicitly assumed "if not human, it's always AI" or "there's only ever one entity to check," since a turn-based flow with N handoff points needs the SAME instance-aware audit applied at all N, not just the first one found. This generalizes a known multi-agent-scale-out failure mode (Brain: an "undo my own action" bug that indexed a per-agent stack instead of the shared stack's actual top, invisible at N=1 by mathematical necessity) — cardinality bugs are invisible until you actually run at N>1, so treat "we're about to support more than one" as a trigger to re-audit every place touching that entity, not just the newest code path.
- Provenance (verified/assumed): verified — a headless test (ai-prisoners.mjs) exercises all three single-player configurations (Prisoner-with-companions, Watcher-vs-all-AI, hotseat) and asserts the AI-turn chain actually visits every prisoner index across ~20-25 turn cycles, not just index 0; all three handoff points needed the fix before this passed (confirmed by the test stalling — activePrisoner never advancing past 0 — before the second and third fixes were applied).
- Link: Pappydapimp69/Opticon game/src/main.js (humanControlsPrisoner, handleWatcherIntent's endTurn branch, scheduleAiWatcher's tail, scheduleAiPrisoner's tail), game/tests/ai-prisoners.mjs

## E9 — gated hud still leaked via unaudited log channel
- Date: 2026-07-26
- Project: Pappydapimp69/Opticon
- Tags: [gamedesign] [gamedev] [ui] [security]
- What: A hidden-information game's core secret (which direction the "seeker" role is truly watching) was correctly role-gated on its PRIMARY display surface (the HUD stat + a 3D wedge) earlier in the project, but a SEPARATE surface reading from the same underlying event stream — a scrolling text log — had zero gating at all, unconditionally showing the real value to every viewer regardless of role. The leak sat live in a shipped beta for several releases before a playtester's unrelated complaint ("the log is boring, I never read it") prompted a closer look that surfaced it.
- Why built: Earlier in the project, a genuine leak was found and fixed: the HUD's facing stat and the 3D gaze/bluff wedge both displayed the true state unconditionally, and a fix (`shouldShowWatcherInfo()`, gating both surfaces) was applied and tested. The text log was a SEPARATE feature added around the same time, sourcing its lines from the same game-state-mutating functions (`rotateWatcher`, `setBluff`, etc.) via a simple `logMsg()` call, but nobody re-ran the "does this leak the secret" audit against it specifically — it was implicitly assumed "already handled" because the adjacent leak had already been fixed.
- Design: `logMsg(game, msg)` appended every action's description string to a flat `game.log` array with no visibility metadata; `renderLog(game)` rendered the last N entries verbatim to whichever viewer called it, with no per-viewer filtering parameter at all.
- Got right: The instinct to gate the FIRST surface found (HUD + wedge) via one shared `shouldShowWatcherInfo()` predicate was correct and reusable — the fix for the log ended up reusing that exact same predicate, just applied to a second surface.
- Where/why it failed: Fixing a leak on one presentation surface doesn't audit every OTHER surface reading from the same event/state source — a text log, a replay/history view, an achievement/summary screen, or a debug overlay can each independently leak the same secret if each was added without re-running the original "who should see this" check against it specifically. The bug was invisible to automated testing until a headless test was written that specifically asserted the log's TEXT CONTENT never contained the leaking phrase — prior tests only asserted the HUD/wedge state, never the log.
- Fix: Added a `watcherOnly` flag to the ONE log entry that reveals true state (the real rotation), and made `renderLog()` accept the same `showWatcherInfo` boolean already computed for the HUD, filtering flagged entries out for any other viewer. The adjacent bluff-declaration log line was deliberately left unflagged/public, since that's the intentionally-visible claim the whole bluff mechanic depends on — the fix required distinguishing "this event is secret" from "this event just also touches the Watcher," not blanket-hiding every Watcher-turn log line.
- Why this fix: A per-entry visibility flag, checked by every consumer of the log against the SAME role-check predicate already used elsewhere, means a THIRD future surface (if one gets added) inherits the correct behavior automatically as long as it reuses the flag and the predicate — rather than requiring a bespoke filter to be re-derived and separately verified each time a new view onto the same event stream is built.
- Rule of thumb: When a hidden-information game's secret leaks via one presentation surface and gets fixed there, explicitly enumerate every OTHER surface reading from the same underlying state/event source (log, replay, summary, debug view, notification) and audit each one against the same "who's allowed to see this" question — don't assume a fix on the first surface found implies the others were already safe. Write the regression test against the SECRET ITSELF (assert the string/value never appears for the wrong viewer), not just against the surface where the original bug was found.
- Provenance (verified/assumed): verified — a headless test (exposure-cue.mjs) drives several AI Watcher turns as a Prisoner-role viewer and asserts the log's rendered text never contains the leaking phrase; confirmed failing before the fix (log contained "Watcher turns to face ...") and passing after.
- Link: Pappydapimp69/Opticon game/src/rules.js (logMsg watcherOnly flag, rotateWatcher), game/src/ui.js (renderLog showWatcherInfo filter), game/tests/exposure-cue.mjs
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-mirage-opticon-redaction-is-itself-an-observation.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-08-03 · projects/pappydapimp69__opticon.md#E38 · compatible · no sandbox · game/src/prisonerAI.js (updateGazeBelief, gazeRisk, dangerous), game/src/watcherAI.js (firstOpenDoor), game/tests/fair-information.mjs, build beta-0.48.0

## E8 — pages deploy succeeds but live url 404s
- Date: 2026-07-26
- Project: Pappydapimp69/Opticon
- Tags: [devops] [github-actions] [github-pages] [deployment]
- What: A GitHub Pages deploy via Actions can report `success` on BOTH the build and deploy jobs, yet the live served URL returns HTTP 404 for a period afterward — not once, but reproducibly on every single deploy across an entire session (10+ occurrences), and not always cleared by exactly one retry (one occurrence needed a second `workflow_dispatch` after the first retry still 404'd, three curl checks in a row).
- Why built: Following the already-known fix for a DIFFERENT Pages issue (E3: deploys only succeed from the default branch) — merge to the default branch, then trigger `workflow_dispatch`, then curl the live URL with a cache-busting query param to confirm.
- Design: Treated "Actions run shows success" as equivalent to "content is now being served" and checked the live URL exactly once per deploy.
- Got right: The underlying deploy mechanism (actions/deploy-pages@v4, default-branch-only) works correctly and the content DOES eventually serve — this isn't a broken pipeline, just a propagation lag between "deployment recorded as successful" and "GitHub's edge/CDN actually serving it."
- Where/why it failed: A single post-deploy curl check that returns 404 was repeatedly misdiagnosable as "the deploy didn't actually work" when the Action logs show success — the two states (Action-reported success, edge-serving-live) are not synchronized, and the gap is long enough (tens of seconds, sometimes surviving one retry) to matter for any automated verification step.
- Fix: After every `workflow_dispatch` that reports success, curl the live URL with a cache-busting query param (`?cb=$RANDOM`) to confirm HTTP 200 before declaring the deploy done. If it 404s, wait ~30-40s and retry the SAME curl before concluding anything is actually broken; if still 404, re-trigger `workflow_dispatch` once more (this cleared it every time it was tried, including the one occurrence that needed two extra retries in a row) rather than escalating to inspecting Pages settings/environment config, which was never actually the problem.
- Why this fix: The 404 is a caching/propagation window, not a pipeline failure — retrying the same successful action (re-dispatch, re-check) resolves it every time it's been observed, whereas diagnosing it as a config/settings problem would be chasing a non-existent root cause.
- Rule of thumb: For GitHub Pages via Actions, "the Action succeeded" and "the URL serves the new content" are two DIFFERENT claims that must be verified separately and in sequence — never report a Pages deploy as done from Actions-run status alone; always live-curl-verify, and treat a first (or even second) 404 immediately after a reported-success deploy as an expected propagation window to retry through, not a signal to start debugging the workflow or Pages settings.
- Provenance (verified/assumed): verified — observed on every deploy this session (beta-0.7.0 through beta-0.11.0, roughly 10 deploys), always resolved by a retry (most needed exactly one extra `workflow_dispatch`; one needed two).
- Link: Pappydapimp69/Opticon .github/workflows/pages.yml; deploy verification pattern used throughout this session's `curl -s -o /dev/null -w "%{http_code}" "https://pappydapimp69.github.io/Opticon/?cb=$RANDOM"` checks.
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-brain-opticon-verification-streak.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-08-10 · projects/pappydapimp69__august-10.md#E1 · compatible · no sandbox · August-10 .github/workflows/pages.yml (both fixes commented inline)
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E10 · compatible · no sandbox · August-10 sandboxes/loop10_a_streak_of_checks_proves_nothing_if_sticky.py
- Cited-by: 2026-10-09 · projects/pappydapimp69__brain.md#E117 · compatible · sandboxes/2026-10-09__relative-refs-break-at-a-missing-trailing-slash-and-js-fetch-paths-follow-the-page-not-the-script.py · observed RESULT: PASS plain-relative 5/5 at root, 5/5 at /myrepo/, 0/3 at /myrepo no redirect, 5/5 with redirect; absolute-path 3/3 at root vs 0/2 at /myrepo/; deeper page 1/3; stuck deploy served 404 while status said building; one-shot check 404… · brain train auto loop 2 pass 5 gap, unattended run 2026-10-09; session_01A7os5bwK2BHc7rwnvxx6Ts

## E7 — squash merge reused branch conflicts
- Date: 2026-07-24
- Project: Pappydapimp69/Opticon
- Tags: [git] [process] [workflow] [tooling]
- What: Opening a second PR from the same long-lived feature branch, after the first PR from that branch was squash-merged, got rejected by the GitHub API with a real "merge conflicts" (405, `mergeable_state: "dirty"`) — even though a manual diff proved the new commit's content applied cleanly and introduced zero actual conflicting lines.
- Why built: The working pattern all session had been: branch stays checked out across many small PRs (implement → PR → squash-merge → keep working on the SAME branch → next PR), reusing one long-lived feature branch instead of a fresh branch per change, matching how the repo's default branch instructions describe an ongoing dev branch.
- Design: Each PR was created straight from the branch's current tip with no rebase step in between, on the assumption that "squash-merged into master" + "branch already contains that exact content" == "trivially mergeable next time too."
- Got right: The instinct to just keep committing to one branch across many iterations (rather than churning branches) was fine and is explicitly the repo's prescribed workflow — the missing piece was ONE step before opening each subsequent PR, not the branch-reuse strategy itself.
- Where/why it failed: A squash merge creates a brand-new commit on the target branch with a new SHA whose parent is the target's prior tip — it does NOT rewrite the source branch's history to match. The source branch still contains its own pre-squash commits (different SHAs, identical net content) with the OLD pre-PR commit as their common ancestor with master. Opening PR #2 from that same branch asks git to apply the diffs of ALL commits since that old ancestor — including the ones whose content master already has via the squash commit — a second time. Git can't recognize "this patch's net effect already exists in the target," so re-applying an already-applied patch produces literal conflict markers, not a silent no-op, even when a plain `git diff` between the two tips shows zero overlap with the truly-new change.
- Fix: Before opening each subsequent PR from a branch that had an earlier PR squash-merged, sync the branch onto the new base first: `git fetch origin <base>`, `git checkout -B <branch> origin/<base>`, then `git cherry-pick <the-new-commit-sha>` (or `git rebase origin/<base>` if there are several new commits — rebase drops already-applied commits automatically since their patch-id now matches, cherry-pick per-commit is the explicit/predictable equivalent for one new commit). Force-push (`--force-with-lease`) the result. Verify first with `git diff origin/<base> <old-tip-of-new-work>` — if that's empty except for the genuinely new file changes, the reset+replay is safe.
- Why this fix: Resetting the branch onto the base's actual current tip and replaying ONLY the commits not yet reflected there (by content, not by SHA) is the only way to make the branch's ancestry match what GitHub's mergeability check assumes; anything short of that leaves stale pre-squash commits in the branch's history that will produce this exact conflict on every future PR from that branch, not just the next one.
- Rule of thumb: A long-lived branch that gets squash-merged more than once must be re-synced onto its base (reset + replay only the unmerged commits) before EVERY subsequent PR from it — not just once, not only when a conflict actually appears. Treat "PR from a branch with prior squash-merged history" as needing this step by default, the same way `git pull --rebase` is the default after any shared-branch fast-forward, rather than debugging a "phantom" conflict after the fact.
- Provenance (verified/assumed): verified — PR #7 (beta-0.8.0) failed to merge with `mergeable_state: "dirty"` and 431 additions / 3 commits reported (should have been ~213 additions / 1 commit); reset-to-origin/master + cherry-pick of the single new commit dropped it to the correct 213 additions / 1 commit / 4 files, and the PR then merged cleanly with `mergeable_state: "unstable"` (pending-checks only, no conflict).
- Link: Pappydapimp69/Opticon PR #6 (squash-merged, beta-0.7.0) then PR #7 (beta-0.8.0, same branch `claude/opticon-3d-browser-game-3lxa2y`)
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E50 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-08-03 · projects/pappydapimp69__opticon.md#E36 · compatible · no sandbox · game/index.html, game/tests/no-conflict-markers.mjs, game/tests/run-all.sh, builds beta-0.45.0 → beta-0.45.1
- Cited-by: 2026-10-08 · projects/pappydapimp69__brainwork.md#E14 · compatible · sandboxes/2026-10-08__branch-lifetime-conflict-scaling.py · observed RESULT: PASS conflicts/merge F=200 L=.25d 0.10 1d 1.30 10d 15.6 20d 27.4 (slope 1.08, linear not quadratic); F=1e5 slope 1.85, 20d 1.95; rebase vs merge monotone 1 vs 1, edit-revert 1 vs 0; squash-prefix phantom merge 4 vs rebase 0. The qu… · scheduled brain train auto pass 5

## E6 — interact in place tile marked passable
- Date: 2026-07-25
- Project: Pappydapimp69/Opticon
- Tags: [gamedev] [algorithm] [pathfinding] [ai] [gamedesign]
- What: An AI's pathfinder routed through a tile it could never actually cross, causing the AI to waste every move point re-triggering the same tile forever — a 500+ simulated-round infinite stall, invisible until a whole-run simulator with a generous round budget was used to hunt it down.
- Why built: A "switch" tile toggles a linked light group when stepped toward; the actual move resolver already special-cased it correctly (stepping onto a switch toggles it and leaves the mover at their CURRENT tile — it never relocates them, unlike a normal floor step).
- Design: The pathfinding module's walkability check only excluded tiles with zero possible occupancy for OTHER reasons (a solid lamp fixture); it checked tile type (FLOOR) and one object exclusion, with no awareness that a SWITCH object on an otherwise-normal floor tile has the same "can never be occupied" property as a solid object, just via game-rule redirection instead of geometry.
- Got right: The move RESOLVER (the function that actually executes a step) had the special-case logic correct from the start — the bug was purely that a SEPARATE module (path planning) didn't share that knowledge, despite both needing to agree on "can a mover ever end up standing here."
- Where/why it failed: Two modules encoded "can this tile be occupied" independently — one correctly (move resolution), one incorrectly (path planning, which only modeled walkability from static tile/object type, not from the object's INTERACTION semantics). BFS found tiles "reachable" that gameplay could never actually let the mover reach, so a route requiring one wasn't just suboptimal — it was systematically dead: every attempt looked like progress to the planner (a valid path existed) but produced zero actual movement when executed, and the AI's own retry/re-plan logic had no way to detect this since it re-derived the "same" valid-looking path every turn.
- Fix: Make the SAME "can this tile ever be occupied" rule the single source of truth, or at minimum keep every consumer (path planning, connectivity/generation guarantees, move resolution) in sync with it explicitly — here, excluding the interact-in-place object type from both the pathfinder's walkability check AND the map generator's own reachability guarantee (which had the identical latent bug: it could "guarantee" a route through a tile real movement could never cross).
- Why this fix: An object whose interaction REDIRECTS or SUPPRESSES a move (toggle-in-place, a locked door needing a separate open step, anything where "step toward X" ≠ "end up standing on X") is a distinct occupancy category from plain walls — it must be excluded from any "can a path cross this" check everywhere that check exists, not just where the interaction is actually resolved.
- Rule of thumb: Whenever a tile/cell's move-resolution logic has a special case for "stepping toward this doesn't relocate you," audit EVERY OTHER place that asks "is this cell passable" (pathfinding, connectivity/reachability generation, AI planning) for the same exclusion — a walkability check and a move resolver silently disagreeing about occupancy produces routes that look valid to the planner and are invisible-until-executed dead ends, and a per-turn "did anything change" check can hide the failure indefinitely since the planner re-derives the same "valid" (but impossible) path every time.
- Provenance (verified/assumed): verified — a whole-run simulator surfaced the stall (0% capture/escape resolution on affected seeds up to a 500-round budget); after the fix, the same seeds resolved in 7-14 rounds; balance simulator's timeout rate dropped from ~10-22% to 0% across 900 games.
- Link: Pappydapimp69/Opticon game/src/pathfind.js (prisonerPassable), game/src/map.js (passableForConnectivity), game/src/rules.js (moveActivePrisoner)
- Cited-by: 2026-07-31 · projects/local__sandbox-combined-opticon-test-connectivity.md#E1 · compatible · no sandbox · this session; `brain train combined` (opticon + test candidate pair)
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E17 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E5 — stall detection needs best ever not turnover
- Date: 2026-07-24
- Project: Pappydapimp69/Opticon
- Tags: [gamedev] [algorithm] [ai] [gamedesign]
- What: A stall/deadlock detector for an AI agent reset its "stuck" counter on any turn-over-turn improvement, so a slow oscillation (advance one turn, retreat the next, repeat) never tripped it — the agent stayed genuinely stuck for 500+ simulated rounds while the counter kept reporting "just made progress."
- Why built: After fixing a separate pathing bug (see E5) that caused most infinite stalls, a small residual timeout rate remained on a few specific seeds. The counter existed as a safety net so a cautious AI could never stall a match forever: it tracked consecutive turns without a positional improvement and forced the AI to drop caution and commit once a limit was hit.
- Design: `stalledTurns` incremented when this turn's distance-to-goal was not better than last turn's, and reset to 0 the moment any single turn improved on the turn before it — i.e. progress was measured relative to the IMMEDIATELY PRIOR turn, not relative to the best position ever reached.
- Got right: The overall escalation mechanism (soft caution up to a limit, then unconditional commitment) was the right shape and needed no redesign — only the progress metric feeding it was wrong.
- Where/why it failed: A turn-over-turn delta can't distinguish "genuinely getting closer over time" from "oscillating around the same region forever." An agent bouncing between two nearby tiles produces an endless alternating sequence of small "improvements" and "regressions" relative to the PREVIOUS turn, so the reset-on-any-improvement rule fired constantly and the stall counter never accumulated enough to trigger commitment, even after hundreds of rounds of zero real progress. Confirmed via direct simulation with a raised round cap (500) that the same few seeds never resolved, and via step-by-step position logging that the agent was bouncing inside a small fixed radius the entire time.
- Fix: Track progress against the BEST value ever achieved (e.g. `bestDistToExit`, monotonically only ever decreasing), and only reset the stall counter when a turn beats that running best — not merely the prior turn. Regression (or lateral movement) never resets the counter under this scheme, no matter how it looks turn-over-turn.
- Why this fix: Best-ever tracking is monotonic and immune to noise/oscillation by construction — it only reflects cumulative real progress, so a counter driven by it can't be "reset" by a fluctuation the way a previous-turn-relative delta can. This is a general property of any "detect lack of progress" mechanism (search, optimization, retries), not specific to grid pathing.
- Rule of thumb: When building a stall/no-progress/deadlock detector, never gate the reset on "better than last observation" — gate it on "better than the best observation ever seen." A previous-turn-relative check is blind to oscillation and slow drift; a best-ever check is not, and costs nothing extra (one running minimum, no history buffer).
- Provenance (verified/assumed): verified — after switching to best-distance tracking, the 3 previously-frozen seeds (out of the residual failures) resolved in 7-14 rounds each; balance simulator's timeout rate across all three difficulties dropped to 0% over 900 simulated games (300/difficulty), holding under a standing 15% regression-ceiling test.
- Link: Pappydapimp69/Opticon game/src/prisonerAI.js (prisonerAITurn, bestDistToExit/stalledTurns fields), game/src/rules.js (createGame field init), game/tests/balance.mjs (TIMEOUT_CEILING regression guard)
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-opticon-august-10-stall-detector-fix-ladder.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E39 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E12 · compatible · no sandbox · August-10 sandboxes/loop03_stall_detector_vs_ambient_drift.py

## E4 — flat menu list nav leak
- Date: 2026-07-25
- Project: Pappydapimp69/Opticon
- Tags: [gamedev] [ui] [input] [gamepad] [gamedesign]
- What: A gamepad/keyboard menu bug reported as "every button except one launches the game directly" turned out to be a single root cause: up/down/left/right directional nav all cycled through ONE flat list mixing a difficulty row and mode/play buttons, so ANY direction could land focus on a play button, and the confirm button then instantly started a game from wherever focus landed.
- Why built: A main menu (difficulty selector + 3 play-mode buttons) needed gamepad/keyboard navigation added on top of existing mouse clicks.
- Design: `menu.els` was one flat array (all difficulty buttons concatenated with all mode buttons); a single `nav(dir)` function incremented/decremented one shared index for every directional input (up, down, left, and right all called the same `nav(±1)`); confirm called `.click()` on whatever was focused.
- Got right: Centering default focus on the primary action (not an edge) was correct in isolation and not the bug — the bug was purely the flattening.
- Where/why it failed: Because up/down/left/right were all collapsed onto one axis over one list, a player exploring the difficulty row with ANY direction key could wander focus straight onto a play-mode button (visually a different row/section entirely), and a reflexive confirm-press then instantly launched a game — reported as "everything skips to the game," when the actual defect was navigation crossing a visual/functional group boundary it should never have reached.
- Fix: Replace the flat list with per-group grids scoped by explicit `data-row`/`data-col` attributes, and split navigation into `navX(delta)`/`navY(delta)` that only ever search elements WITHIN the current group (stage/section) — horizontal movement can only change column, vertical only row, and neither can ever reach another group's elements. Additionally gated group-to-group advancement behind an explicit confirm (not directional overflow), and made the final "start" action require a HELD press rather than a tap, so no single confirm-press (however focus got there) can launch immediately.
- Why this fix: The defect wasn't really "wrong button reachable" — it was that a 2D visual layout (rows of controls, separate sections) had been flattened into a 1D data structure for navigation, so an axis (which direction moves you) lost the meaning it visually implied. Restoring the real dimensionality (which group, which row, which column) makes cross-group leakage structurally impossible rather than something to filter after the fact.
- Rule of thumb: When adding directional (gamepad/keyboard) navigation over a UI with visually distinct groups/rows, never flatten all focusable elements into one linear index — model the grid's real rows/columns/groups explicitly, and let each direction move on only its own axis within the current group. A flat list is fine for a single homogeneous row; it silently breaks the moment two different-purpose control groups sit on the same screen.
- Provenance (verified/assumed): verified — headless test mashed all 4 directions + 5 confirm-taps on the difficulty stage and the game never started; only a genuine held confirm on the final stage started it.
- Link: Pappydapimp69/Opticon game/src/main.js (menuNavX/menuNavY), game/src/input.js (pollGamepad menu branch)
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E18 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E3 — github pages deploy default branch
- Date: 2026-07-24
- Project: Pappydapimp69/Opticon
- Tags: [devops] [ci] [github-actions] [github-pages] [deployment]
- What: Automating a GitHub Pages deploy for a static browser game cost an extra full build-fix-retry cycle because of two non-obvious platform constraints that surface late (only at deploy time), not at authoring time.
- Why built: Wanted the game publicly playable for beta testing via GitHub Pages with no manual settings clicks, driven from a feature branch.
- Design: A Pages workflow (actions/configure-pages enablement:true, upload-pages-artifact path:game, deploy-pages) triggered on push to the feature branch; intent was to enable Pages and deploy in one run from that branch.
- Got right: configure-pages(enablement:true) DID enable Pages from within the workflow (the build job succeeded), so no human had to toggle the Pages setting on first; serving a subdirectory (game/) as the site root via upload-pages-artifact path worked, and relative asset paths resolved fine under the /repo/ base.
- Where/why it failed: (1) The deploy job failed instantly with zero steps and a 404 log — the signature of the github-pages environment's default protection rule that restricts deployments to the DEFAULT branch; a feature-branch run is blocked before any step runs. (2) Enabling/inspecting Pages via the REST API directly was impossible here: the agent proxy allow-lists /user but returns 403 "path not permitted through this proxy" for /repos/{o}/{r}/pages, so the only path to enable Pages was from inside an Actions run on GitHub's own infra.
- Fix: Get the site content onto the default branch (merge to master), then run the same workflow from master (workflow_dispatch with ref=master) — build + deploy both go green. Verify the live URL actually serves (200 + expected title/markers), not just that the run is green.
- Why this fix: The github-pages environment's branch policy is satisfied by the default branch; deploying from there is the friction-free path and needs no settings change. Verifying the served URL catches base-path/artifact-root mistakes a green run won't.
- Rule of thumb: For GitHub Pages via Actions, plan to deploy from the DEFAULT branch — the github-pages environment blocks non-default branches by default, and it fails at deploy setup (0 steps, 404 log), not at authoring. Also: enabling/reading Pages may be blocked over a restricted API proxy, so drive it from inside the workflow (configure-pages enablement:true), and always curl the final URL to confirm it serves.
- Provenance (verified/assumed): verified — build job enabled Pages and uploaded; feature-branch deploy failed at setup; master deploy succeeded; https://pappydapimp69.github.io/Opticon/ returned 200 with the expected title and menu markup.
- Link: Pappydapimp69/Opticon .github/workflows/pages.yml
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-august-10-opticon-not-red-and-not-deployed-are-independent.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E10 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E2 — threejs fog culls overview
- Date: 2026-07-23
- Project: Pappydapimp69/Opticon
- Tags: [gamedev] [3d] [threejs] [rendering] [camera]
- What: The atmospheric close-up camera looked correct, but switching to the overview/top camera rendered a completely black screen with no error and no warning.
- Why built: THREE.Fog(color, near, far) gives the prisoner a claustrophobic limited-sight feel matching the surveillance design.
- Design: A single global fog with near=14, far=42 tuned for the tight prisoner camera.
- Got right: Keeping camera and fog config together in one setViewMode handler made the eventual fix a two-line change.
- Where/why it failed: Fog blends geometry toward the fog color as distance approaches far, and past far everything is fully fog-colored (equal to the background here). The overview camera sits ~50 units out on a world of radius ~25, so nearly the entire scene is beyond far and dissolves into the background. It reads as "nothing rendered" and emits no console error, so it is easily misdiagnosed as a scene-graph or build bug.
- Fix: Make fog a function of the active view — tight near/far for the atmospheric cam, and push far to several times the world radius (or disable fog) for map/overview cams; set it in the view-switch handler.
- Why this fix: Fog is a per-view mood tool, not a global constant; different cameras need different depth budgets.
- Rule of thumb: When a 3D scene renders blank only from certain camera distances, suspect fog far (or the camera near/far clip planes) before the scene graph; scale distance-based effects to the camera that is actually active.
- Provenance (verified/assumed): verified — headless Chromium before/after screenshots; game/src/render.js setViewMode.
- Link: Pappydapimp69/Opticon claude/opticon-3d-browser-game-3lxa2y

## E1 — reachability vs rules tests
- Date: 2026-07-23
- Project: Pappydapimp69/Opticon
- Tags: [gamedev] [testing] [ai] [balance] [pathfinding] [simulation]
- What: All per-move rules unit tests passed (203 assertions) yet the game objective was unreachable — a simulator running 900 full headless games showed a 0% escape rate that step-level tests never caught.
- Why built: Needed an AI prisoner for single-player and a way to confirm the game is winnable from both sides before calling it a beta.
- Design: First-pass prisoner AI used greedy Manhattan-distance direction scoring; rules tests asserted individual actions (MP decrement, noise appears, capture fires) in isolation, and all were correct.
- Got right: Isolating pure logic from rendering (map/rules/AI as browser+Node ES modules) made the whole-game simulator trivial to write with zero browser.
- Where/why it failed: On a walled ring/donut map, greedy distance-scoring falls into wall local-minima — it steps into the "closest" dead end and oscillates. Compounded by spawn placed on the opposite side of a large arena (a half-circumference trek). Neither failure is observable from per-action tests; both are properties of the whole trajectory over the whole map.
- Fix: Added BFS pathfinding shared by the AI and the simulator; added a balance harness that plays hundreds of complete games per difficulty and asserts both outcomes occur and difficulty is ordered; re-placed spawn to an inner ring offset ~90 degrees from the gate for a bounded run.
- Why this fix: A simulator exercises the emergent whole-trajectory behavior that unit tests structurally cannot; it converts an invisible "unwinnable" state into a numeric signal (escape% / capture% / avg length) you can tune against.
- Rule of thumb: For any goal-directed system (game objective, agent task, workflow), add a reachability/outcome test that runs the whole thing to a terminal state many times, separate from correctness tests of the steps — "every step is correct" does not imply "the goal is reachable".
- Provenance (verified/assumed): verified — 0% to ~19% escape / ~68% capture across 900 games after the fix; game/tests/balance.mjs.
- Link: Pappydapimp69/Opticon claude/opticon-3d-browser-game-3lxa2y
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E33 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-09-30 · projects/local__sandbox-rising-cost-depth-cap-whole-run-vs-step-test.md#E1 · compatible · sandboxes/2026-09-30__rising-cost-depth-cap-whole-run-vs-step-test.py · observed RESULT: PASS whole-run sim cap 8 equals summed-curve cap; per-step test passes to stage 58; recovery 20 lifts it to 12 · scheduled brain train pass 5
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E19 · compatible · no sandbox · August-10 sandboxes/loop06_seed_variance_without_outcome_variance.md
- Cited-by: 2026-09-29 · projects/pappydapimp69__brain.md#E65 · compatible · no sandbox · session https://claude.ai/code/session_01CHKxy8KkvpqUvfaWw1qb3v
- Audited: 2026-10-14 · modeled · No sandbox is stored in sandboxes/ for this entry; its evidence is the author's own game harness (game/tests/balance.mjs in the Opticon repo, 900 headless games, 0 percent escape before and about 19 percent escape and 68 percent capture after), which I could not open from here, so I judged the text only. The mechanism is credible and computed rather than assumed: greedy Manhattan scoring on a walled ring is a known local-minimum trap and a full-trajectory run counts a terminal outcome, so a 0 percent figure is measured. But the numbers describe one bespoke map and AI, and the Rule of thumb generalizes to any goal-directed system, which one game does not cover; later entries that cite it (a rising-cost depth cap sandbox) add a second, separate system but do not change what this entry itself tested. Verdict modeled: a hand-built model of one game, narrower than the rule, and not rerunnable from the canon. · scheduled brain train auto loop 2 pass 3; session_01BwMXpnGN7oKqipFnskBS6R
