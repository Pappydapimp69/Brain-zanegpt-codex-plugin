# pappydapimp69/mirage — lessons

Project: pappydapimp69/mirage. Newest first.

---

## E31 — serializer live reference
- Date: 2026-09-09
- Project: pappydapimp69/mirage
- Tags: [state][testing]
- What: `serializeRun(sim)` — the snapshot half of a save system for a seeded-deterministic game, packing a run into a plain object that goes to localStorage as JSON and comes back through `deserializeRun`.
- Why built: The world is never serialised, only regenerated from its seed, so the payload carries every piece of mutable run state instead — positions, meters, throttle countdowns, cached paths, per-companion latches. Several of those had already been found missing and added, each one caught by a divergence test that runs an original and a restored run forward together and requires them to stay identical.
- Design: Copy on the way out. Every structure in the payload is built fresh — `path.map(n => ({cx, cz}))`, `inventory.map(s => ({...s}))`, `{...sim.stats}`, `[...c.known.pylons]` — so the payload owns everything in it.
- Got right: The copying discipline itself, and the divergence test, which is what eventually surfaced this. The fields that gate rng draws had all been identified and were correct.
- Where/why it failed: Two fields out of roughly forty were handed over by REFERENCE rather than copied — a pylon's `primedBy` array and a companion's `givenUpPylons` object. Real saves never noticed, because `JSON.stringify` on the way to localStorage snapshots them; the aliasing only exists for a caller that restores straight from the returned object. That caller was the divergence test. The two runs then shared a pylon's `primedBy`: a companion in the ORIGINAL run added themselves to a pylon in the RESTORED one, which handed the restored run a second pair of hands a tick early, confirmed the pylon there and nowhere else, and left the two runs permanently one tick out of phase. 12 of 60 seeds forked; the test's own fixture seed was not one of them, so it read green for the whole life of the bug and the failure was blamed on an unrelated map change that happened to move the fixture onto a forking world.
- Fix: Copy both (`[...(p.primedBy || [])]`, `{...(c.givenUpPylons || {})}`). A new test asserts the payload shares no mutable structure with the sim in the strong form — mutate the sim after packing, and the payload must not move. A second test round-trips through JSON, because that is the path a real save takes and nothing was pinning it. The direct-restore test is kept: it is the one that can see aliasing.
- Why this fix: The serialiser's contract is a self-contained snapshot, and thirty-eight of forty fields already honoured it. Testing through the JSON hop alone would have made the symptom disappear while leaving the defect, which matters the moment any other caller — a co-op handoff, a replay, an undo — restores without stringifying.
- Rule of thumb: A serialiser whose output is always immediately JSON-encoded has an untested contract: encoding hides every live reference it hands out. Assert the strong form directly — mutate the source after packing and require the payload not to move — because the aliasing is invisible on the production path and appears only in tests, replays or in-process handoffs, where it reads as a bug in whatever changed last.
- Provenance (verified/assumed): Verified — 12/60 seeds forked on resume before the fix and 0/60 after, measured on both the old and new map so the fix is not map-specific; 0/60 through a JSON hop either way, which is what proves no player was affected. The one-tick mechanism was traced to the exact tick and actor with a per-tick diff and a temporary trace inside `activatePylon`. The new guard was negative-controlled by reverting each copy. Assumed — that `primedBy` and `givenUpPylons` were the only two; the audit was by reading all forty fields, not by an automatic check, and the payload-vs-sim identity test only covers the structures it names.
- Composed: N/A
- Link: mirage c53bf32 "serializeRun handed out live references, and two runs edited each other"
- Cited-by: 2026-10-15 · projects/pappydapimp69__brainwork.md#E286 · compatible · sandboxes/2026-10-15__sharecode-replace-vs-merge-rng-timer-state.py · observed RESULT: PASS replace import matches reference 1/1, merge with a stale gate timer diverges, merge only works when timer coincides, unencoded alias moves, encoded copy is stable · brain train auto session pass 2; session_0147KUptpmmgHdXXTSmtxr1C

## E30 — fixture measured the wall
- Date: 2026-09-09
- Project: pappydapimp69/mirage
- Tags: [testing][gamedev]
- What: Three test fixtures in a game whose maps are generated from a seed, all of which went red when the map's grid was enlarged from 46 to 65 cells per side.
- Why built: Each was a reasonable fixture: teleport the party 30 units from a pylon and check a brittle companion breaks formation toward it; stand one companion 5 units from the lead and check the monster flicker picks them; run for 8 seconds and check the party keeps up.
- Design: Each set up its situation with literal world coordinates or by inheriting whatever the seeded world happened to provide.
- Got right: All three were testing something real, and none of them was a bad test in intent. Two of the three had comments explaining a previous fix, so they had been maintained.
- Where/why it failed: Every one had been passing for a reason that was not the reason it claimed. `p.x + 30` was inside the map only because the map used to be 120m across; at 169m the pylon sits nearer the rim and the party was teleported outside the world, where it could not move at all. The flicker test never set the lead's yaw, so it inherited a seeded starting facing and only passed because that facing happened to include the companion — the flicker picks only companions ON SCREEN. The keep-up assertion was the worst: following had been removed from this game entirely, replaced by wandering plus an explicit CALL verb, so companions have not kept up for a long time. It passed because the old map's rim stopped a sprinting lead after ~30 units and the party caught up against the wall. The assertion was measuring the boundary, not the party.
- Fix: Ask the world instead of assuming it — search for a walkable cell about 30 units from the pylon that can path back to it. Set the yaw explicitly, using the module's own bearing convention rather than a guessed sign. Replace the keep-up assertion with what the design actually promises: CALL summons a companion and they come.
- Why this fix: A fixture that inherits an unstated condition is only as valid as the day it was written. Stating the precondition makes the test say what it needs, and a test that asserts a promise the design has withdrawn is worse than no test, because its green is read as evidence.
- Rule of thumb: When a change to a world CONSTANT turns tests red, do not assume the change broke them — check what each was passing BECAUSE of. A boundary, a default facing, a spawn distance is a silent precondition, and the tests that inherit one go green for a reason nobody wrote down. The replacement assertion needs its own negative control: the first rewrite here ("calling brings them in") passed with the call deleted, because a separate periodic mechanic closed the gap anyway, so it was re-pinned on the summon latch that nothing else sets.
- Provenance (verified/assumed): Verified first-hand — the off-map teleport was confirmed by computing the world half-extent (84.5) against the target (100.2); the keep-up case by running the identical 8-second input on both map sizes (18/5/17/17/12 units apart at 46, 49/54/53/66/63 at 65); the inert replacement assertion by deleting the CALL and watching the test still pass, then re-pinning it and watching it go red. Assumed — that no other fixture in the suite carries the same class of unstated precondition; only the three that went red were audited.
- Composed: N/A
- Link: mirage a9b168f "The basin at twice the area — mirage-0.15.0"

## E29 — unread field is not plumbing
- Date: 2026-09-09
- Project: pappydapimp69/mirage
- Tags: [architecture][state]
- What: A 3D game whose world grid size lived as a module constant `GRID = 46` imported directly by the renderer, the AI, the collision helpers and the tests — while every world object ALSO carried `world.grid` and `world.cell` in its returned shape. The owner asked for one of the two map types (the authored camp) to be twice the area, which it could not be while both maps shared one constant.
- Why built: The shape field was added when a second map type (an authored camp, alongside procedurally generated basins) started returning the same object as the generator. It looked like the per-instance plumbing was already in place.
- Design: Give the camp its own `CAMP_GRID`, make the existing `world.grid` field the thing consumers read, and pass the grid explicitly to the helpers that have no world to read it from (`cellToWorld`, `worldToCell`, `inBounds`).
- Got right: Not trusting the field. Grepping for `world.grid` before planning the change is what turned "this is already plumbed, just set it" into a five-module job with a blueprint.
- Where/why it failed: `world.grid` was written by both map builders and read by NOBODY — not one consumer in the codebase. Every one of them imported the module constant instead. The field had been correct and dead since the day it was added, so it carried no evidence about whether the code could handle a second value; the two agreed only because one of them was never consulted. Setting it to 63 on the camp would have changed nothing at all, and the map would have been silently drawn, walked and pathed at 46: the renderer indexes `cellKind` by stride, so the whole map shifts a cell per row with nothing thrown.
- Fix: Every consumer reads `world.grid`. Helpers with no world take `grid` as a REQUIRED, validated argument. `floodFill` derives the stride from `Math.sqrt(blocked.length)` — the array already encodes it unambiguously. `render.js` stopped importing the constant entirely, so a missed call site is a ReferenceError.
- Why this fix: Deriving beats passing, and passing beats defaulting. A `grid = GRID` default was the tempting shape and is the worst of the three: a forgotten argument then yields a plausible number that places things tens of metres from where the map says they are, and the only symptom is a world that looks subtly wrong. Required-and-checked converts every missed site into a stack trace on the first frame.
- Rule of thumb: A per-instance field that nothing reads is not plumbing — it is a second copy of a constant, kept honest by never being asked. Before sizing work off "the field is already there", grep for its READERS; zero readers means the whole job is still ahead of you, and the field's current correctness is worth nothing as evidence.
- Provenance (verified/assumed): Verified — grep found `world.grid` read at exactly one site in the whole repo (a test asserting it equals the constant). After the change, basins were proven byte-identical across 8 seeds: blocked grids, feature placement and a 60-second six-companion sim run all hash the same before and after. The camp's enlargement was exercised by the browser tutorial playing start to finish, all 7 objectives. Assumed — nothing; the required-argument guards were each negative-controlled (called without the argument, watched throw).
- Composed: N/A
- Link: mirage 21277ac "The camp at twice the area — mirage-0.14.0"; docs/blueprint-camp-2x.md

## E28 — scratch buffer caps the domain
- Date: 2026-09-09
- Project: pappydapimp69/mirage
- Tags: [state][algorithm]
- What: A BFS pathfinder called several times a second per companion, with two module-level scratch arrays (`Int32Array`/`Uint8Array` of `GRID * GRID`) reused across calls instead of allocated per call.
- Why built: The allocation was real garbage — six companions repathing a few times a second each is two fresh typed arrays per call, in the hot loop of a long-running simulation. Hoisting them out is the correct optimisation and it is commented as such.
- Design: Allocate once at module load, `fill()` them at the top of each call. Safe because the function is synchronous, single-threaded and never re-entrant — all three true, all three stated in the comment.
- Got right: The re-entrancy reasoning, which is the failure everyone looks for with shared scratch state. It was sound and stayed sound.
- Where/why it failed: The buffers were sized from the constant that was true when they were written. When a second map type arrived with a larger grid, the pathfinder was handed a world it could not index: the BFS wrote past the end of `prev`, and two tests died on "Invalid array length". Loud here only by luck — a `Uint8Array` read past the end returns `undefined` rather than throwing, so the near miss was a companion that silently stops following with no error at all. The comment justified the sharing and never mentioned that the SIZE was an assumption about the domain.
- Fix: `scratch(cells)` grows both buffers when the world handed in needs more, called with `grid * grid` at the top of each path. Never shrinks — the largest map seen sets the high-water mark, which is the point of hoisting them.
- Why this fix: It keeps the whole benefit (no per-call allocation in the steady state) and drops the only part that was a hidden constraint. Growing on demand costs one comparison per call.
- Rule of thumb: A hoisted scratch buffer silently caps the domain of the function that uses it. Sizing it from a constant is a bet that the constant is the maximum forever — write the size as a function of the ARGUMENT and grow on demand, or the optimisation becomes a bounds check nobody knew was there.
- Provenance (verified/assumed): Verified by negative control — the growth call was removed, two camp tests failed with "Invalid array length", and it was restored. The truncation-rather-than-throw path is reasoned from `Uint8Array` semantics, not observed, since the `Int32Array` write threw first.
- Composed: N/A
- Link: mirage 21277ac "The camp at twice the area — mirage-0.14.0", src/world.js findPath

## E27 — precondition field
- Date: 2026-09-09
- Project: pappydapimp69/mirage
- Tags: [process][method]
- What: A second index over Brain, keyed by PRECONDITION ("I am changing a constant") instead of by conclusion ("a default lives twice"), so a lesson surfaces at the moment it is needed rather than when you already know its answer. Built by hand as `tools/triggers.mjs`; the open question was which schema field a generator should read to build it from the canon automatically.
- Why built: Brain's matcher is keyword-based over conclusions. At the moment a lesson is needed, the agent's head holds the SITUATION, not the answer, and no query it would think to type bridges that — `brain query fov` returns nothing for "I am about to narrow the camera default". Every failure in one session was already recorded; none surfaced.
- Design: The stated plan was to generate the index from each entry's own `Where/why it failed:` field, on the assumption that the precondition already lives there. Tested it before building: back-test the 14 hand-written triggers against the 12 source entries that exist in the canon (718 memory entries, exported with `brain export --full`), scoring each field of each source entry on the fraction of that trigger's `when:` vocabulary it could have produced.
- Got right: Testing the assumption before writing the generator, and negative-controlling it. Also right that the precondition IS somewhere in the schema — the index does not need a new field, only the correct one.
- Where/why it failed: `Where/why it failed:` recovered 19.4% of the `when:` vocabulary and won for ZERO of the 12 triggers. `What:` recovered 44.5% (8 wins) and `Rule of thumb:` 41.9% (2 wins). Hand-reading a 24-entry spread across the corpus showed why: 1 entry states a precondition outright, ~7 state a general mechanism, ~16 are a post-hoc causal narrative of one incident — "the clear left N default nodes at the front", "the capture step was fatal". The field answers "what went wrong", which is only knowable AFTER the fact, so it is written in the past tense about one specific incident. That is the correct thing for it to hold; it is simply not a precondition.
- Fix: Read `What:` for the precondition and `Rule of thumb:` for the generalisation. Corrected the claim in `tools/triggers.mjs`'s own header and filed the refutation in `docs/WORKING-LIST.md`.
- Why this fix: `What:` opens by naming the thing being built or changed, in the present tense and generically — it is the situation the author was IN. `Rule of thumb:` is already the lesson stated as a standing instruction. Between them they win 10 of 12. Neither is a length artefact: `Rule of thumb:` averages 39 words against the failure field's 42 and still more than doubles its recall, and every field was scored against shuffled trigger/entry pairings as a negative control (lift +37.9 and +39.7 against +15.0).
- Rule of thumb: A field that records what WENT wrong cannot also index what you are ABOUT to do — it is written after the fact, about one incident. Before generating a retrieval index from a schema field, back-test the hand-written index you already have against every field and negative-control it against shuffled pairings; the field whose NAME sounds right lost here to two whose names do not.
- Provenance (verified/assumed): Verified first-hand — 718-entry canon parsed from `brain export --full`; 12 of 14 triggers mapped to source entries by their own `from:` lines; per-field recall, win counts, mean field lengths and the shuffled-pairing control all measured, and 24 failure fields sampled at a fixed stride and read by hand. Assumed — that content-word overlap is a fair proxy for "could have generated this `when:`"; a generator using paraphrase rather than vocabulary reuse could score differently, though the 0-of-12 win count does not depend on the proxy's calibration. Not tested — whether a generator built on `What:` + `Rule of thumb:` actually produces usable triggers.
- Composed: N/A
- Link: session — mirage branch claude/brain-install-vohzag, docs/WORKING-LIST.md "Denied"

## E26 — omniscient bot cannot price deception
- Date: 2026-08-10
- Project: pappydapimp69/mirage
- Title: an omniscient bot cannot price a mechanic whose cost is an information gap
- Tags: [testing][gamedesign][verification][ai-agents][balance]
- What: MIRAGE is a first-person survey game whose entire difficulty is a deception layer — a `percept` module derives what the player is SHOWN from what the sim knows is TRUE, and lies about markers, pylons, compass heading and party state. Its balance harness drives complete headless runs with scripted policies that read `sim` directly, and those policies were being used to tune the difficulty of the deception.
- Why built: The harness exists to check that a basin is completable at all, which is a job an omniscient policy does well and cheaply. The failure was one of scope creep rather than of construction: a tool built as a completability oracle was quietly promoted to a difficulty instrument, and its own header already said why that does not follow.
- Design: Two scripted policies drive full headless runs over the real sim, reading ground truth for every decision, with a pressure assertion asserting that the hardest tier must not be a walkover. The deception layer sits entirely outside what those policies can observe.
- Got right: The harness header already documented that the scripted bots read `sim` directly, and the pressure assertion was in place and did fire. The apparatus said what it was; the reasoning on top of it is what went wrong.
- Where/why it failed: A cohesion fix (companions now hold a reachable formation) removed most of the game's isolation drain as a side effect, since that multiplier is measured from the party centroid and a permanently scattered party had been paying it on several members at once. The pressure assertion started failing, and the obvious response was to raise the base drain rate until the bot started losing again — 1.05 to 1.9, plus a per-tier cut to the opening calm window. That tuning was invalid: the bots are never shown a marker that isn't there and never believe a companion who is wrong, so tuning a deception game's drain rate against an omniscient bot sets the difficulty for a player who CANNOT be deceived and then ships it to one who can. It would have been the harshest change in the project, justified entirely by a number that could not measure the thing it was named after.
- Fix: Add a third `deceived` policy that runs an actual `percept` alongside the sim and takes every decision from it — phantom markers compete with real ones on distance and are logged on arrival as false entries, phantom pylons and dead-but-live-looking pylons are chased as relief, the compass lie rotates the step actually taken, and the party is believed fine because the chorus agrees. Two failures on the way each had it silently scoring a meaningless 100%: it outran the mechanic (an omniscient bot finished the whole survey in 96 seconds, inside the game's 90-second opening calm window, having never hallucinated once, so zero false logs meant it never met the deception, not that deception was cheap — fixed by starting deceived runs past the ramp), and it read its own affliction (the policy branched on `sim.player.hallucinating` and so dived for a pylon the instant it went under, never walking to a phantom marker).
- Why this fix: "Am I hallucinating" is precisely the fact a deceived mind does not have, so a handicapped agent must be denied the flag NAMING its handicap, not just the data behind it. With both corrections, at the ORIGINAL drain rate the deceived bot scores 67% on standard and 25% on bleak, with ~24 and ~68 false log entries per run — the tiers separate, the pressure is real, and no tuning was ever needed.
- Rule of thumb: When a system's difficulty, cost or risk IS an information gap, an agent on the privileged side of that gap is a completability oracle only, and its success rate must never drive tuning. Build a handicapped agent that consumes the same derived view the human does, then check two things before trusting its first green: that it lived long enough to meet the mechanism at all, and that it is not reading a state flag that names the very limitation it is supposed to be under.
- Provenance (verified/assumed): VERIFIED first-hand — the 1.05 to 1.9 drain increase was made and then shown unnecessary by the deceived policy scoring 67% on standard and 25% on bleak at the original rate with ~24 and ~68 false log entries per run; the 96-second omniscient completion inside the 90-second calm window and the `sim.player.hallucinating` branch were both observed as the causes of the deceived bot's meaningless 100% scores.
- Composed: N/A
- Link: MIRAGE balance harness; src/percept.js; deceived policy
- Cited-by: 2026-10-17 · projects/pappydapimp69__demo-disc.md#E41 · compatible · no sandbox · https://claude.ai/code/session_0189x5cwDWHdyFUT5WmrVCJq, Demo-disc commit d8c9970

## E25 — took the report literally
- Date: 2026-08-03
- Project: pappydapimp69/mirage
- Title: take the sensory words literally before mapping them onto a same-named system
- Tags: [process][debugging][gamedev][ui][ux]
- What: When a user reports a SENSORY problem, take the sensory words literally before mapping them onto a system you already know about. MIRAGE's player said "the world feels distorted immediately". The project had a prominent distortion FEATURE — a hallucination vignette — so that is what got investigated, across three rounds. None of it was the thing being reported.
- Why built: The hallucination vignette is the game's signature visual effect and the only thing in the codebase named for distortion, so the vocabulary collision between the player's plain description and the system's internal name was immediate and total. Every hypothesis that followed inherited it.
- Design: Three rounds of investigation, each aimed at the vignette: a stale-module cache bug, a CSS class overriding an inline opacity, and a grace window. All three were real defects and all three were fixed — which is precisely what made the wrong track so durable, because each round ended in a genuine repair and a plausible story.
- Got right: Measuring the player's other claim rather than dismissing it. They had blamed "the movement controls", and movement was checked and found mathematically exact — constant input, 0.0000 lateral deviation over 240 ticks. Keeping that measurement instead of arguing about it is what left the symptom unexplained and the investigation open.
- Where/why it failed: The actual cause surfaced only when the same player, playtesting weeks of work later, wrote it out in full: "the world feels distorted and misshapen. Straight isn't straight, it's curved." That is a LENS description, not an effect description. Three.js's PerspectiveCamera takes a VERTICAL fov and the game shipped 72 there, which is 105 degrees HORIZONTAL at 16:9 and 119 at ultrawide — deep fisheye, bowing straight lines toward the frame edges and sweeping edge geometry past the camera when walking. It was present in literally every frame since the first commit and invisible to every test, because a wrong-but-consistent projection renders perfectly.
- Fix: Ask "distorted how — brighter, warped, laggy, wrong shape?" before opening any code, so the sensory report is resolved into a description rather than a system name. Correct the camera to hold a constant HORIZONTAL angle across aspect ratios (Hor+), and add an explicit assertion of that shipping invariant, which a vertical-fov camera silently violates as the window changes shape.
- Why this fix: A player's mislocated CAUSE is normal and useful data rather than an error — this player blamed the movement controls, and a fisheye lens does make lateral motion swing across the frame, so it genuinely feels like locomotion. Treating the reported symptom as sensory truth and the reported cause as a hypothesis keeps both pieces of information instead of discarding the half that was wrong. The invariant assertion is needed because projection settings are silent defects: nothing errors, nothing flickers, the frame is stable.
- Rule of thumb: Take a user's sensory words literally before mapping them onto a system that happens to share the name — vocabulary collision actively steers an investigation wrong, and three real fixes in a row is not evidence you are on the right track. Treat the reported symptom as truth and the reported cause as a hypothesis, and assert projection and camera invariants explicitly, because a wrong-but-consistent projection renders perfectly and no test will notice.
- Provenance (verified/assumed): VERIFIED first-hand — three rounds of fixes to the hallucination vignette were made and none changed the reported symptom; the lateral-deviation measurement (0.0000 over 240 ticks of constant input) was run; and the vertical-fov-72 camera was confirmed to produce 105 degrees horizontal at 16:9 and 119 at ultrawide, present since the first commit.
- Composed: N/A
- Link: MIRAGE camera / PerspectiveCamera fov; session

## E24 — screenshotting a live sim
- Date: 2026-08-03
- Project: pappydapimp69/mirage
- Title: screenshotting a live simulation is not a snapshot
- Tags: [testing][gamedev][process][debugging][browser]
- What: Screenshotting a live simulation is not a snapshot, and three separate false conclusions came out of forgetting that in one session. A capture under software GL takes SECONDS of wall time and the game's rAF loop keeps running the whole time, so the state you set up when you asked for the picture is not the state in the picture.
- Why built: The captures existed to check perceptual features by eye — a phantom taking a vacated formation slot, a companion briefly rendered as a monster — because those are exactly the features no assertion can judge. The probe therefore had to set up sim state and then photograph it, which is where the assumption that a capture is instantaneous entered.
- Design: A headless browser harness drove the real game, set up the condition it wanted to photograph by writing sim state directly, and then asked for a PNG of the canvas, with an A/B pair captured back to back for before-and-after comparison.
- Got right: Distrusting the first reading. Each of the three findings looked exactly like a game bug, and in each case going back to the apparatus rather than the feature is what resolved it — the features were all fine.
- Where/why it failed: Three ways, all harness bugs that presented as game bugs. First, state was set up too late in the sim's own life: a "the phantom takes a vacated formation slot" feature reported as not firing because the probe teleported the party into place and vacated a slot in the same instant, when the feature reads a slot MEMORY that only fills while the party is genuinely in formation and the hallucination's own onset clears it — ten seconds of ordinary play before the trigger and it worked exactly as designed. Second, the control frame drifted into the experimental one: an A/B of "ordinary companion" versus "briefly rendered as a monster" produced two near-identical monster frames, because the flag was cleared correctly and then ~2 seconds of real frames rendered while the PNG composited, during which the effect's own 0.45/s roll fired again, so the "before" picture was an "after" picture. Third, the obvious freeze drew over the subject: using the game's own pause to stop time worked perfectly and rendered the pause MENU across the thing being photographed.
- Fix: Freeze the specific mechanism rather than the world — stub the effect's rng gate so nothing new starts, and set its expiry far in the future so the current one takes the code's existing mid-effect hold path, which yields a genuinely controlled frame with the scene still visible. Require sim state to be correct AT CAPTURE TIME rather than at request time, and where a mechanism has a warm-up (a memory that fills, an anchor that seeds), pay that warm-up in sim time before triggering.
- Why this fix: Freezing the world is either impossible or destructive — the game's own pause is the only global freeze available and it draws UI over the subject — whereas freezing one mechanism reuses a hold path the code already has and leaves everything else rendering normally. Paying the warm-up matters because a probe that skips it is testing a state the game never actually reaches.
- Rule of thumb: A screenshot of a live simulation is a capture over an interval, not an instant, so the same "measure, don't assume" discipline that catches a gameplay bug has to be applied to the OBSERVATION APPARATUS. Freeze the mechanism, not the world; make state correct at capture time rather than request time; and pay any warm-up in sim time before triggering, or the probe will report a working feature as broken.
- Provenance (verified/assumed): VERIFIED first-hand — all three false conclusions were produced and then resolved in one session, the drifted A/B was traced to the effect's 0.45/s roll re-firing during the ~2 second composite, the vacated-slot feature was confirmed correct once ten seconds of ordinary play preceded the trigger, and the mechanism-freeze approach was used to obtain the controlled frames.
- Composed: N/A
- Link: MIRAGE screenshot harness; src/percept.js; session

## E23 — rng gating is save state
- Date: 2026-08-03
- Project: pappydapimp69/mirage
- Title: anything that gates when an rng draw happens is save state
- Tags: [gamedev][state][save][determinism][testing]
- What: In a seeded-deterministic sim, anything that gates WHEN an rng draw happens is save state, however cosmetic the thing it gates appears to be. Building save/load for MIRAGE (mulberry32, one 32-bit state word, restored O(1)), the snapshot carried every obviously-authoritative field — positions, meters, world flags, inventory, the rng word itself — and a resumed run still drifted, even though field-by-field equality at t=0 was perfect.
- Why built: MIRAGE is seeded-deterministic by design, so a save is only correct if a resumed run is indistinguishable from an uninterrupted one. That makes the save shape a correctness question rather than a convenience question.
- Design: The snapshot was assembled from what reads as authoritative state — entity positions, player meters, world flags, inventory contents, and the rng state word restored in O(1) per the-game-prologue#E1. Restoration rebuilt each of those fields directly, and a round-trip equality check compared the deserialized object against the original field by field.
- Got right: Restoring the rng state word itself, and doing it in O(1) rather than by replaying draws, so the stream position was at least representable in the save at all. The failure was in what else phases that stream, not in the stream's own handling.
- Where/why it failed: What was missing were four throttle countdowns — `sightTimer` (gates the throttled sighting sweep), `remarkCooldown` (gates ambient chatter), `repathTimer`, and a companion's cached `path`. None of them is game state in any intuitive sense; one of them literally only decides when a character says a line. But each decides which TICK an rng-consuming branch fires on, so restoring them zeroed re-phased every later draw. The failure mode is the dangerous kind: the resumed run had byte-identical positions, meters, pylon charges and item flags, and a silently different stream position, which would have surfaced hours later as "my save loaded and then the basin went weird", with nothing to bisect.
- Fix: Include every draw-gating countdown and cached path in the snapshot, and replace round-trip equality with a forward-run comparison — serialize, deserialize, then tick the original and the restored copy the same number of steps and compare a fingerprint that includes `rng.snapshot()`. Add a negative control that deserializes with a deliberately corrupted rng word and asserts the fingerprints DIVERGE, so the check cannot silently stop being able to detect drift. A cheap audit for the missing fields: grep the sim for every `*Timer` / `*Cooldown` / cached-path field assigned during a tick and ask of each "does any branch downstream of this draw?"
- Why this fix: Round-trip equality can only see the fields you already thought to save, so it is structurally incapable of finding an omission; running both sims forward compares the consequence instead of the representation, which is where a phase difference actually shows up. The negative control exists because a fingerprint check that has never been observed to fail is not known to be sensitive to anything. The corollary for the save-shape decision is that a cached path is worth SAVING rather than recomputing, even though it is derivable, precisely because recomputing it re-phases the draws.
- Rule of thumb: In a seeded-deterministic sim, the save set is not "the state that matters", it is "everything that can change WHEN a draw happens" — throttle countdowns, cooldowns, repath timers and cached paths all qualify however cosmetic they look. And prove it by running the original and the restored sim forward and comparing a fingerprint that includes the rng word, with a corrupted-word negative control, rather than by asserting round-trip field equality.
- Provenance (verified/assumed): VERIFIED first-hand — the drift was observed on a resumed run whose t=0 field-by-field equality was perfect, the four missing countdowns were identified as its cause, and the forward-run fingerprint test plus its corrupted-rng-word negative control were both run and observed to fail and pass in the expected directions.
- Composed: the-game-prologue/E1
- Link: MIRAGE save/load; session
- Cited-by: 2026-10-15 · projects/pappydapimp69__brainwork.md#E286 · compatible · sandboxes/2026-10-15__sharecode-replace-vs-merge-rng-timer-state.py · observed RESULT: PASS replace import matches reference 1/1, merge with a stale gate timer diverges, merge only works when timer coincides, unencoded alias moves, encoded copy is stable · brain train auto session pass 2; session_0147KUptpmmgHdXXTSmtxr1C

## E22 — grace window disabled difficulty
- Date: 2026-08-03
- Project: pappydapimp69/mirage
- Title: a grace window sized without measuring run length disabled difficulty entirely
- Tags: [gamedev][balance][gamedesign][process][testing]
- What: A player-requested "calm opening" window must be sized against MEASURED run length, or it silently deletes the systems it sits in front of. Asked for "a 5 minute delay before the meter starts to move", MIRAGE got a flat 300s no-drain window — against a basin that a scripted bot completes in ~200s. The entire typical run fell inside the window.
- Why built: The request was a direct player report about the opening minutes feeling hostile, and a flat no-drain window is the most literal possible implementation of "five minutes before the meter moves". Nothing about the request itself was wrong; the number was simply never checked against how long a run actually lasts.
- Design: A flat 300-second window during which the survival meter does not drain at all, applied per basin, sitting in front of the drain system and therefore in front of everything the drain feeds — difficulty tiers, companion lucidity, and the deception layer built on top of them.
- Got right: The balance harness was already reporting per-tier rows, which is the only reason the collapse was visible at all rather than being felt vaguely as "the game got easier". Having a table to look at is what turned this into a five-minute diagnosis.
- Where/why it failed: With no drain anywhere in the typical run, the difficulty multiplier had nothing to multiply, and the harness returned BYTE-IDENTICAL results for careful, reckless and bleak — same win rate, same completion time, same markers found. It also cut the game's other core event, companions hallucinating, from 0.88 to 0.21 episodes per run, which is the same complaint the same player had filed separately. The fix for one report caused the other.
- Fix: Replace the cliff with a ramp — a dead-calm window followed by a linear ease to full drain, which gives the requested calm opening while restoring tier separation. Attribute the change with a controlled run: a zero-window control reproduced the ORIGINAL win rates, which is what proved the window rather than the unrelated AI-behaviour changes that landed in the same session was the cause. Add an explicit assertion that at full drain, gentle < standard < bleak must hold as rates.
- Why this fix: Without the zero-window control the two changes in that session were confounded and either could have been blamed, so the control is what makes the conclusion a measurement instead of a guess. The tier-ordering assertion turns a silent collapse into a loud one, because identical rows across difficulty tiers is a specific smell — it means a multiplier has been zeroed upstream, not that tuning is off.
- Rule of thumb: Size any grace, tutorial or calm-opening window against measured run length, not against the wall-clock number a player named — a window longer than a typical run deletes every system behind it. Identical (not merely converged) rows across difficulty tiers means a multiplier was zeroed upstream; assert the ordering. And when two changes land in one session, run a control that reverts one of them before attributing the effect. Note also that win RATE was the wrong metric to tune on here, because the harness bot reads sim truth and is blind to the deception layer (T23) — cumulative party-seconds-lost separated the tiers cleanly while win rates stayed flat.
- Provenance (verified/assumed): VERIFIED first-hand — the byte-identical per-tier balance rows were produced by the repo's own harness, the 0.88 to 0.21 drop in companion hallucination episodes per run was measured, and the zero-window control run was executed and observed to reproduce the original win rates, which is what separated the window from the concurrent AI-behaviour changes.
- Composed: N/A
- Link: MIRAGE balance harness; tension T23

## E21 — diagnostic artifacts must not fail suites
- Date: 2026-08-03
- Project: pappydapimp69/mirage
- Title: a capture that asserts nothing must not be able to fail a suite
- Tags: [testing][process][ci][browser]
- What: MIRAGE's browser smoke test saved review screenshots purely so a human could look at a frame. Under software GL, compositing a full-viewport animated overlay over a live WebGL canvas took a MEASURED 177 seconds, blew the timeout, and failed an otherwise entirely green run. The capture asserted nothing and was still able to turn the suite red.
- Why built: The screenshots exist for human review of the hallucination overlay — there is no automated judgement of how a frame looks, so the capture was never an assertion in the first place. It was simply written inline, in the same fatal path as the checks around it.
- Design: The smoke test drives a real browser, runs its assertions, and captures frames at chosen moments. Capture and assertion shared one control flow and one timeout budget, so any failure in either aborted the run identically.
- Got right: Measuring instead of guessing. Reading the renderer's own draw-call and triangle counters took one probe and showed them identical between the lucid frame and the hallucinating one (21 calls / 21546 triangles), which proved the scene was not the cause and the cost was the compositor.
- Where/why it failed: The capture step was fatal, so an environment limitation presented as a correctness failure on a run where every real assertion had passed. The instinct was to blame the several plausible rendering changes in flight that day, and without the counter probe that is where the debugging cycle would have gone. An earlier instance of the same timeout had a different cause entirely — pure machine contention from a parallel agent running its own browser tests, at load average 13.7 — which the same measurement habit identifies and no amount of reading the diff would.
- Fix: Separate assertions from artifacts. Diagnostic output (screenshots, traces, profiles, dumps) is attempted and, on failure, NOTED and skipped, never fatal, while every real assertion around it still runs. And before "fixing" a slow or flaky capture, measure whether the thing under test actually got heavier — read the renderer's own counters and the machine load first.
- Why this fix: A suite that goes red for a reason unrelated to correctness costs a debugging cycle every time and, worse, teaches the team to distrust red, which is the expensive part. Moving the diagnosis from "which of today's commits made rendering slow" to "the environment cannot composite this in time" is a completely different fix, and only a measurement can make that move.
- Rule of thumb: A flaky ASSERTION and a flaky ARTIFACT need opposite responses — make the assertion deterministic, make the artifact non-fatal. Anything that asserts nothing should never be able to fail a suite, and before blaming recent commits for a slow capture, read the renderer's own draw-call and triangle counters and the machine load.
- Provenance (verified/assumed): VERIFIED first-hand — the 177-second composite was measured, the identical 21-call / 21546-triangle counts were read from the renderer in both the lucid and hallucinating frames, and the earlier occurrence of the same timeout was observed under a load average of 13.7 caused by a parallel agent's browser tests.
- Composed: N/A
- Link: MIRAGE browser smoke test; session

## E20 — correctness tested perceptual feature never seen
- Date: 2026-08-03
- Project: pappydapimp69/mirage
- Title: a correctness-tested perceptual feature that no player ever perceived
- Tags: [gamedev][gamedesign][testing][ux][perception]
- What: MIRAGE's "monster flicker" briefly renders a real nearby companion as a monster (wrong colour, wrong proportions) while the player is hallucinating. It shipped with five passing unit tests. A real player finished a whole session and reported "I didn't see any monsters." A second, sibling report — "other AI members didn't seem to hallucinate like they did before" — turned out to have exactly the same shape.
- Why built: The party's lucidity meters are invisible by design, so every tell has to be behavioural or perceptual. The flicker is the peak tell: the person next to you is also wrong.
- Design: `percept.js` rolls `MONSTER_CHANCE_PER_SEC = 0.07` per second of hallucinating, requires a companion within `MONSTER_SIGHT = 20` units, picks one uniformly, and shows it for 0.35-0.85s.
- Got right: Keeping the lie in one pure module made the whole diagnosis measurable headlessly — Node scripts driving the real sim, no browser. And the existing tests were not wrong; they proved exactly what they claimed, which is the point.
- Where/why it failed: The unit tests forced the roll (`sim.rng.chance = () => true`) and stood a companion five units away, so they tested the MECHANISM and never the RATE, and the rate had been set against an imagined episode. Measured on recorded runs, three independent gates multiplied: the median lead-hallucination episode is ~7 seconds (you go under, you reach a pylon or burn a dose) against a rate sized for a minute; the median nearest-companion distance while the lead is under is ~22 units, just outside the 20-unit gate, because companions hold formation behind a lead who outruns them (player sprint 7.4 vs companion walk 4.6) and lag further as they fray; and the formation slot is derived from the lead's yaw, so the party sits permanently BEHIND the camera and an unbiased pick spent ~4 rolls in 5 on a body the player could not see, each still firing the audio sting. End to end that is one visible flicker per ~110 seconds of hallucinating — an 8s episode showed a monster 8% of the time, a 20s episode 37%. The companion half was the same class of error by a different mechanism: a companion who goes under immediately picks a phantom goal uniformly over the whole grid and beelines, median distance from the lead ~48-64 units, with only ~7-12% of gone-seconds spent both in legible range and on screen, so "nobody else hallucinated" was a literally accurate perceptual report about a mechanic firing correctly, off-screen, every time.
- Fix: Tuned against recorded play rather than by feel — rate 0.07 to 0.45/s, sight 20 to 26, duration 0.35-0.85s to 0.5-1.25s; restrict the pick to companions actually ON SCREEN, so there are fewer total flickers, all of them seen, and the audio sting always has something attached; give a hallucinating companion a ~7s dwell where they stand and turn where they broke, then a 2.5-6s stall on arriving anywhere, with phantom goals drawn from a bounded radius instead of the whole grid; fire their first "gone" line immediately on breaking (the only tell that survives distance and fog) on its own 5-11s cadence from a pool grown 9 to 16 lines with no back-to-back repeats; and draw a gone companion on their OWN heading instead of turned to face the lead.
- Why this fix: The rate is now derived from a measured episode length and a measured party geometry, and the strobe risk is bounded by an explicit upper-bound assertion rather than by taste. Measured after, same seeds and same scripted player behaviour: sees a monster in an 8s episode 8% to 45%, 20s 37% to 85%, 60s 78% to 100%; median wait for the first one 23.6s to 8.6s; on-screen duty cycle 0.5% to 3.9%; companion median distance while gone 63.8u to 35.6u; gone-seconds visible 7% to 20%.
- Rule of thumb: For any feature whose whole purpose is to be PERCEIVED, "does the mechanism fire" and "does a player ever see it" are different test axes, and the first tells you nothing about the second. Before tuning a probability-per-second, measure the length of the window it actually rolls in and the fraction of that window its gates are open — the product is the real rate. Then assert on the OBSERVED rate from both sides: a floor (a normal session must contain one) and a ceiling (it must not strobe). A correctness suite that stubs the roll and hand-places the actors will pass at any rate, including zero.
- Provenance (verified/assumed): VERIFIED first-hand in MIRAGE on 2026-08-03 — diagnosed with throwaway Node harnesses driving `state.js` and `percept.js` headlessly (a full-run recorder over the balance bot, an offline parameter sweep replayed against recorded traces, and a controlled same-initial-conditions scenario harness, since two full runs on one seed diverge the moment an rng draw count differs and an uncontrolled A/B measures nothing); the regression suite `tests/hallucination.test.mjs` has 13 of its 20 checks failing against the pre-fix build. One contributing factor is separately owned: a later-added 300s per-basin grace window cut companion hallucination episodes ~4x, 0.88/run to 0.21/run.
- Composed: N/A
- Link: src/percept.js (updateMonsterFlicker and the tuning block); src/party.js (LOST_DWELL / phantomGoal / companionRemark); tests/hallucination.test.mjs

## E19 — action tied hallucinations
- Date: 2026-08-03
- Project: pappydapimp69/mirage
- Title: a perceptual lie that never changes is a lie the player solves once
- Tags: [gamedev][gamedesign][ui][testing][perception]
- What: MIRAGE has five hallucination kinds. Two of them (PHANTOM_MARKER's camera-turn drift and the monster flicker) react to what the player does. The other four each set exactly ONE value at onset — a compass offset, a phantom pylon position, a canned agreement string, a phantom companion's formation slot — and then never changed again for the rest of the episode. All four were correct, tested, and stable. All four were also solved in about three seconds: you notice the compass is 90 degrees out, you subtract 90, and the hallucination is over while the mechanical state is still running.
- Why built: The module's own founding rule is "a hallucination that re-randomises every frame reads as a graphics bug; one that holds still reads as a place." That rule is correct, and it produced static lies, because stable and inert were never separated.
- Design: Each of the four got a twist tied to a VERB the player performs, with the seeded onset value kept as the opening position. WRONG_WAY — the compass error grows while you hold a committed heading and releases all at once when you stop; growth is imperceptible per frame, the release is the event. FALSE_ANCHOR — the phantom pylon backs off to a fixed distance on the same bearing, but only once you have closed on it AND let it out of your view, so an approach that never breaks eye contact really does arrive. CHORUS — the agreement answers the player's own decisions (survey, pickup, item use) instead of only their check-ins, escalates in three tiers, and preferentially speaks in the voice of somebody who could not have said it. DOUBLED_PARTY — the sixth body moves into the formation slot of a companion who has actually gone under or strayed, and the roster shows one confident (false) row for exactly that person against five "you can't tell"s.
- Got right: Keeping every draw at onset, so no per-tick path consumes rng and a seed still fully describes a run. And keeping "never moves while on screen" for the receding pylon — that constraint is the difference between reading as a place and reading as a glitch.
- Where/why it failed: Twice, in the same shape, and both times the mechanism was already firing correctly. First, the compass drift was sized in RADIANS (0.022 rad per unit walked) while the HUD compass is EIGHT LETTERS — half a radian of accumulated error can change nothing a player can see, and measured, only 13% of twenty-second episodes ever produced a visible settle, the first landing around t=22s against this game's ~7s median hallucination. Second, the settle was gated on the FEET being still, so measured, it released itself in the middle of the player's 180-degree look-around sweeps: 4.1 settles per minute of which only 1.9 were witnessable, because a compass letter changing while you are turning is the least remarkable thing on screen.
- Fix: Rate the tell in the units the PLAYER'S INSTRUMENT resolves, not the units the code stores — the settle threshold is now one full compass point (pi/4), which guarantees the letter changes — and gate "stopped" on the head as well as the feet, so the release lands in a beat where the player is holding position and looking at something. Measured after: a settle is witnessed in 55% of 8s episodes, 88% of 20s, 100% of 60s, at ~4/min, with the between-times creep at 0.010 rad/tick, invisible frame to frame.
- Why this fix: Both failures are the same one the monster flicker shipped with ("a mechanism that fires correctly but off-screen has not fired at all"), one layer further in: it is not enough for the event to be on screen, it has to be on screen IN THE UNIT THE DISPLAY QUANTISES TO, and at a MOMENT where it reads as anomalous rather than as ordinary.
- Rule of thumb: Size a perceptual tell against the resolution of the widget that shows it and against what else is happening when it fires — not against the internal quantity. A tell smaller than one increment of its own display fires into a rounding error; a tell that fires during a motion the player themselves initiated is indistinguishable from that motion.
- Provenance (verified/assumed): VERIFIED first-hand — measured over a 40-seed sweep of the repo's established "realistic player" drive model, at three episode lengths, for all four kinds, each with a ceiling condition (adversarial input) and a control condition (the behaviour the twist is supposed to punish); the before and after rates quoted here are that harness's recorded output.
- Composed: mirage/E1
- Link: mirage src/percept.js; tests/kinds.test.mjs
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E25 · compatible · sandboxes/2026-10-11__call-bearing-tell-must-be-sized-to-perceivable-resolution.py · observed RESULT: FAIL 4/5 predictions held; LR 24=5.00 8=2.67 4=3.17; silence c0.9 k1=0.909, c0.3 k3=0.745. Missed: the 4-quadrant ratio was 3.17, not under 1.5. · session; Seven docs/IDEAS.md "Disappearance and return"; brain train pass on disappearance; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E32 · incompatible · sandboxes/2026-10-11__find-chance-tuning-survives-8-direction-hearing.py · observed RESULT: FAIL 3/4 predictions held; worst miss at 8 points 0.207; total hours 24pt 10 vs 8pt 14. Probe at noise 4: hours 1-5 all 0.293, hour 6 0.742. · session; Seven docs/IDEAS.md "Disappearance and return"; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E46 · compatible · sandboxes/2026-10-11__on-screen-recede-cannot-be-both-invisible-and-unbeatable.py · observed RESULT: PASS 4/4; invisible recede delay x1.053/x1.111/x1.250; tripling needs f=0.667; off-screen stops at look-away >= 0.4 · session; brain train auto pass 5 (gap), tension T1; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E55 · compatible · sandboxes/2026-10-11__believable-hallucination-renders-the-players-learned-prior.py · observed RESULT: PASS 4/4; believed junction/open q0.8: 0.800/0.020; q0.5: 0.500/0.020; q0.1: 0.100/0.020; weak tell 0.667 · session; brain train loop on hallucination as an art style (loop 3); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E56 · compatible · sandboxes/2026-10-11__fourth-wall-sanity-effects-wear-out-shuffle-bag-and-variants.py · observed RESULT: FAIL 3/4; M=N random 6.06 shuffle 8.00; M=3N shuffle 11.78 duds 0.33 vs variants 16.71 duds 0.00 · session; brain train loop on hallucination as an art style (loop 2); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E57 · compatible · sandboxes/2026-10-11__hallucination-flicker-needs-a-window-cap-not-an-average-rate.py · observed RESULT: FAIL 4/5; worst windows jitter 7/8/8 capped 3/3/3; cap keeps 0.75 at 2.0/s · session; brain train loop on hallucination as an art style (loop 5); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E58 · compatible · sandboxes/2026-10-11__more-hallucinated-voices-turn-words-into-texture.py · observed RESULT: PASS 3/3; 4 voices one place 0.216 spread 1.000; 12 spread 0.130; max half-intelligible 2 vs 4 · session; brain train loop on hallucination as an art style (loop 1); session_01NHKVhTvCnvtvZ2NGLSPYj6

## E18 — coop possession avoids schema change
- Date: 2026-08-01
- Project: pappydapimp69/mirage
- Tags: [gamedev][coop][architecture][state]
- What: Added 2-player couch co-op to a 3D game whose entire sim was written against a single `sim.player`. Player two POSSESSES one of the five existing AI companions instead of being added as a new body.
- Why built: The owner asked for couch co-op. The obvious shape — add a second player character to the world — would have changed party size, which every balance-bearing rule in the game keys off (the six-mind dissolve loss condition, the "return with 2+ companions" win condition, drain contagion across the party, the balance harness's win-rate thresholds).
- Design: `sim.humans` is a slot-indexed array with `humans[0] === sim.player`, so every existing call site that reads `sim.player` keeps meaning exactly what it meant and the whole prior test suite passes untouched. Characters carry `humanSlot` (null = AI-driven). `possess()`/`release()` move a companion between the party AI and a human. The party AI skips steering a possessed companion but still runs its sighting/memory update, so a joined player is genuinely a second pair of eyes.
- Got right: Possession-over-addition meant ZERO balance re-tuning — the balance harness reported the same win-rate band after the feature as before, because the party is still six minds and still loses on the same conditions. Also right: giving each human their own perception object rather than sharing one, which turned an existing single-player mechanic (a hidden per-mind hallucination meter) into the co-op mode's whole point for free — two players are shown genuinely different worlds and neither screen is labelled as the unreliable one.
- Where/why it failed: Two real bugs the design did NOT prevent on its own. (1) Possession was silently lost at every level transition: the campaign's `carryOver` payload rebuilds all character objects, so a joined player's pad went dead at each new basin with no error — it reads as a broken controller, not a lost slot. (2) Forwarding player two's button presses to the existing action handler would have fired the LEAD's survey/pickup from across the map, because every verb (`logMarker`/`pickupItem`/`useItem`/`craftItem`) is written against `sim.player`.
- Fix: (1) Carry `humanSlot` through `carryOver` and rebuild the human roster in slot order on the far side, so `humans[i]` still means "slot i" after a transition. (2) Deliberately DROP player two's action queue for now and scope them to move/look/sight, rather than shipping a verb that silently acts on someone else's character; threading an actor param through the verb functions is the follow-up.
- Why this fix: A possessed-character design makes drop-out trivially correct (the AI that was driving that mind a moment ago just resumes) but it does NOT automatically make identity survive world rebuilds — identity has to be explicitly carried in whatever payload crosses the rebuild, and that is exactly the schema pressure networked co-op is warned about, showing up in a game with no network and no save file.
- Rule of thumb: When retrofitting local co-op onto a single-protagonist sim, have player two POSSESS an existing AI actor rather than spawning a new one — the actor already has the state, the AI is already the correct drop-out handler, and no balance rule that keys off actor count changes. But expect the per-player identity you just added to leak into every payload that survives a world rebuild (level transition, save, snapshot): if it is not explicitly carried there, a joined player's controller goes silently dead at the boundary, which players read as broken hardware rather than a lost slot. And do not forward the new player's inputs into verbs written against the original protagonist — one input edge driving another character's action is worse than the verb simply not being available yet.
- Provenance (verified/assumed): Verified first-hand. Both failures were hit and fixed in this session; the fixes are covered by 12 new pure-logic assertions plus a new real-browser test that reads the actual GL viewport/scissor state to confirm the screen splits, and by re-running the balance harness to confirm the win-rate band was unchanged.
- Composed: mirage/E1
- Link: Pappydapimp69/mirage branch claude/brain-install-bhr36y
- Cited-by: 2026-10-15 · projects/pappydapimp69__brainwork.md#E282 · compatible · sandboxes/2026-10-15__dropout-teardown-order-and-role-handoff.py · observed RESULT: PASS only unpossess-before-parent adopts (1/4 orders), party size 6 vs 5, but an adopted AI leaves the info-holding role hollow and silences the pacing trigger (fires True vs False) · brain train auto session pass 5; session_0147KUptpmmgHdXXTSmtxr1C

## E17 — default lives twice only one copy moved
- Title: a default lives twice, and only one copy moved
- Date: 2026-08-30
- Project: pappydapimp69/mirage
- Tags: [ui][defaults][testing][browser]
- What: Narrowing the camera default (`DEFAULT_HFOV` 90 -> 78) left the pause menu's lens ladder at 80/90/100 with `class="sel"` hard-coded on the 90 button. The camera ran 78 and the menu said 90 — and on a fresh profile it said it in static markup, before any JS could disagree. Nothing threw. The value had two homes: a constant in the renderer and a set of `data-fov` buttons in `index.html` whose pre-selected state is the default's second, silent declaration.
- Why built: a playtester reported "up on the stick moves me forward and slightly right", and the fix touched both the input deadzone (a real cross-axis leak) and the lens (residual barrel bending the straight line the stick actually walked). Only the lens half had a duplicate copy.
- Design: the runtime path was fine — `refreshSettings` toggles `.sel` from stored prefs. The hole is only visible with NO stored prefs, i.e. the first thing a new player sees, which is exactly the state a returning-user test never reaches.
- Got right: The runtime path. `refreshSettings` toggles the selected control from stored preferences correctly, and always did — which is exactly why the hole survived: it is only reachable with NO stored preferences, i.e. the first thing a new player sees and the one state a returning-user test never reaches.
- Where/why it failed: the existing `tests/fov.mjs` asserted the default NUMBER (`def.h===90`) and so went red immediately — but a test that had merely been updated to 78 would have gone green while the menu still lied, because it never read the menu on a fresh profile.
- Fix: move the ladder with the default (70 / 78 / 90, `sel` on 78), set `main.js`'s pre-load `fovPref` to the same 78, and add an assertion that on a FRESH profile the pre-selected button equals the camera's actual angle — `def.sel === String(def.h)` — which compares the two copies to each other instead of either to a literal.
- Why this fix: asserting each copy against a hard-coded number means a future change edits both the code and both assertions, and the drift reappears. Asserting the copies against EACH OTHER survives the next retune with no edit.
- Negative control: reverted `sel` to the 90 button; the new assertion failed ("menu shows undefined but camera is at 78") and the old number assertion stayed green. Restored.
- Rule of thumb: when a default is also rendered as a pre-selected control, the markup is a second declaration of that constant. Changing the constant without changing the markup ships a UI that lies on first launch only. Test the two copies against each other, on a profile with nothing stored.
- Provenance (verified/assumed): VERIFIED first-hand — tests/fov.mjs went red on the stale assertion, the new fresh-profile assertion was negative-controlled (reverted `sel` to the 90 button, watched it fail with "menu shows undefined but camera is at 78", restored), and the whole browser suite is green after the ladder move.
- Link: session; src/render.js DEFAULT_HFOV; src/main.js fovPref; index.html [data-fov]; tests/fov.mjs
- Cited-by: 2026-09-28 · projects/pappydapimp69__brain.md#E49 · compatible · no sandbox · session 2026-09-28, brain train edge target `brain + mirage`; sandbox scratchpad/sbx/negctl.py
- Cited-by: 2026-09-28 · projects/pappydapimp69__brain.md#E50 · compatible · no sandbox · session 2026-09-28, brain train writing loop 1; sandbox scratchpad/sbx/writebar.py
- Cited-by: 2026-10-09 · projects/pappydapimp69__brain.md#E101 · compatible · 2026-10-09__empty-alt-vs-missing-alt-toy-model.py · observed RESULT: PASS missing alt voiced as file name only on filename-readers; audit flagged 1; alt="" on a meaningful image is silent everywhere. · brain train auto pass 1, session 01EzGMQhUbptmRNUnqW1q9k1

## E16 — a guard that never failed is unmeasured
- Date: 2026-08-28
- Project: pappydapimp69/mirage
- Tags: [testing][process][verification]
- What: A test written from the same mental model as its feature cannot detect a defect in that model, and no amount of green tells you which of your tests those are. Demonstrated by construction: one implementation with a switchable defect, and two tests over it that differ ONLY in whether they re-derive the real caller's conditions or reuse the convenient assumption the implementation was written under. Both pass on correct code. On the injected defect the shared-assumption test still passes and the real-caller test fails. The suite is green in three of those four cells, so greenness carries no information about which guard is load-bearing — only running a guard against the defect it claims to catch does.
- Why built: `brain train gap` asks for a real gap, and `brain query negative-control` returned 0 memory, 0 tension, 0 idea, 0 exploration. This session produced four separate instances of the pattern in one codebase (a hidden-state leak whose smoke assertion asserted the leak; an Opticon grace-period test that asserted the buggy formula; tutorial steps pinned to synthetic events that no real emitter produced; a mouse-look probe returning a yaw delta of 0.0000 and passing), so the absence of coverage was conspicuous.
- Design: The defect is a switch rather than a rewrite, so both tests run against literally the same function in both conditions and nothing differs but the flag. The two tests are written the way each would actually be written — the shared-assumption one holds a single object across calls because that is the convenient shape; the real-caller one reloads a fresh object each call because that is what the production caller does. Deterministic: no rng, no wall-clock, no timing.
- Got right: Modelling the assumption CONCRETELY (object lifetime) rather than as an abstraction. The failure only appears because the real caller rebuilds an object every call and the convenient test does not, which is a mechanical difference a sandbox can hold, unlike "the test shared the author's blind spot", which cannot be tested at all.
- Where/why it failed: The live instance is mirage#E11. `observe()` kept a two-event tally on the `progress` object it was handed; the unit test held one progress object across all three of its calls; the real caller rebuilt progress from localStorage every frame. The tally therefore never survived to the next event in play, and the only multi-event stage in the game was uncompletable — while its dedicated unit test passed, because it happened to supply the object lifetime the implementation assumed. It also passed a browser test and a manual pass.
- Fix: Negative-control every guard: revert the defect it exists for, confirm the guard fails, restore. Cheap, and it is the only step that distinguishes a guard from a decoration. Where a test must model a caller, model the caller's real conditions — object lifetimes, call ordering, how state is obtained — rather than the shape that is convenient to write.
- Why this fix: Both tests pass on correct code, so no amount of review of a passing suite separates them; the information exists only in the failing direction. Four guards added in this session were negative-controlled this way and two of them turned out to need their own corrections first, which would not have surfaced otherwise.
- Rule of thumb: A guard that has never been observed to fail is unmeasured, not proven — and the guards most likely to be inert are the ones written by the same person, at the same time, as the feature, because they inherit its assumptions for free. Before trusting a new test, break the thing it watches and watch it fail. When a test has to stand in for a caller, copy the caller's conditions, not its intent: object lifetime, call ordering and how state is fetched are where the shared assumption hides.
- Provenance (verified/assumed): VERIFIED first-hand — ran tests/sandbox/s5-test-sharing-the-features-assumption.mjs, observing PASS/PASS on correct code and PASS/FAIL on the injected defect, i.e. the shared-assumption guard failing to detect a defect the independent guard catches. Corroborated by the live mirage#E11 case. NOTE: the sandbox also prints a table of "green vs load-bearing guard counts" at various share rates — that table is arithmetic illustrating the consequence, NOT a measurement of any real suite, and should not be cited as evidence of how common the pattern is.
- Composed: mirage/E11
- Link: session; tests/sandbox/s5-test-sharing-the-features-assumption.mjs; src/tutorial.js observe() and tests/tutorial.mjs
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-mirage-brain-builder-negative-control-needs-binding-rate.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-09-28 · projects/pappydapimp69__brain.md#E49 · compatible · no sandbox · session 2026-09-28, brain train edge target `brain + mirage`; sandbox scratchpad/sbx/negctl.py
- Cited-by: 2026-09-28 · projects/pappydapimp69__brain.md#E54 · compatible · no sandbox · session 2026-09-28, Canon and Frontier rebuild on the real co-verification graph
- Cited-by: 2026-09-25 · projects/pappydapimp69__seven.md#E16 · compatible · no sandbox · Pappydapimp69/Seven branch claude/brain-install-vohzag, seven-0.26.0

## E15 — chain cohesion is not proximity
- Date: 2026-08-28
- Project: pappydapimp69/mirage
- Tags: [gamedesign][algorithm][state][simulation]
- What: Chain cohesion — you are "with the group" if you are within range R of ANY member, computed as a connected component over a proximity graph — is a good answer to "a party that follows you feels like an escort", but it carries four properties that do not follow from reading the rule, three of which are design-relevant and one of which is a trap. Sandbox-confirmed, all four: (A) the furthest a CONNECTED member can be from the leader is (N-1)*R, so legal spread grows LINEARLY with party size — 80m at five, 100m at six; (B) recruiting therefore has a hidden cost, widening the existing crew's legal diameter by a whole link with nobody moving; (C) a hallucinated member is a valid link to the mind that sees it, and can bridge a party that is really in two pieces so it reads as whole (2/4 connected becomes 5/5); (D) fragmentation is positional, not numerical — dropping ONE member from a six-line leaves 1/5 still with the lead if it is the one nearest them, and 5/5 if it is the tail.
- Why built: `brain train gap` asks for a real gap, and `brain query cohesion` returned 0 memory entries against 2 tensions and 3 ideas — the mechanic had just been built into MIRAGE with no recorded coverage at all.
- Design: A single `groupWith` union-find over fixed layouts, exercised four ways: a maximally-stretched line swept over N; a diameter delta between five and six; a real gap with and without a phantom link, including a two-piece party bridged by one phantom; and a single-loss sweep over every position in a six-line. Fully deterministic — fixed coordinates, no rng, no wall-clock.
- Got right: Sweeping N rather than checking one party size, which is what turns (A) from an observation into the formula (N-1)*R and makes (B) fall out of it directly. And sweeping the DROPPED POSITION rather than the drop count, which is the only way (D) is visible at all.
- Where/why it failed: Nothing failed in the shipped code — this is the mechanic's shape, not a bug. The trap is (D) combined with the game's own difficulty model: the member standing nearest the lead is load-bearing for everyone behind them, so losing them is categorically worse than losing anyone else, and nothing in the rule or the UI says so. In a game where members are lost by going under, that means the cost of a companion breaking depends entirely on where they were standing — and a player has no way to know that. (Two fixtures in this sandbox were wrong on the first run because I spaced a bridge wider than R and proved only that a phantom cannot bridge an impossible gap; both are corrected in place with a note, because the arithmetic error is easy to repeat.)
- Fix: Not a code change — a set of consequences to design against. Cap total chain length or hops if the linear-growth property is unwanted; expect (C) to make the phantom-anchor mechanic stronger than intended as party size grows; and if members are ever recruited, price (B) deliberately rather than discovering it.
- Why this fix: The properties are inherent to connected-component membership. Any attempt to remove them turns the rule back into proximity-to-leader, which is the escort behaviour cohesion exists to eliminate. They should be chosen, not inherited.
- Rule of thumb: A connectivity predicate is not a proximity predicate, and the difference grows with the population. Anything defined as "linked to anyone in the set" has a diameter of (N-1)*R rather than R, so adding members silently widens what the rule permits; a member who can be perceived but does not exist is a fully valid link; and single losses are positional — a node adjacent to the root is worth the entire subtree behind it, while a leaf is worth nothing. Sweep the population size and the removed POSITION, not just the count, or all three stay invisible.
- Provenance (verified/assumed): VERIFIED first-hand — ran tests/sandbox/s4-chain-cohesion-reach.mjs, observing the (N-1)*R relation across N=2..8, the 80m->100m diameter delta, 2/4 -> 5/5 connectivity from one bridging phantom, and the 1/5 vs 5/5 split between dropping the lead-adjacent member and the tail.
- Composed: N/A
- Link: session; src/state.js groupWith/LINK_RANGE; tests/sandbox/s4-chain-cohesion-reach.mjs
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-mirage-brain-builder-sweep-the-axis-the-failure-varies-on.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Reverified: 2026-10-11 · pass · sandboxes/2026-10-11__rebuild-mirage-e15-chain-cohesion.py · observed RESULT: PASS 4/4; reach N2=1.00, N3=2.00, N4=3.00; near-loss cuts 2; phantom holds · Own exhaustive search over a 0.5 lattice for N = 2 to 4 with R = 1: the furthest connected member is exactly (N-1)R (1, 2, 3). On a four-member line, losing the member beside the leader cuts off both others while losing the end member cuts off nobody, so losses are positional. A perceived but nonexistent member at distance 1 holds a member at 2R in the group (size 3 with it, 1 without). Directly relevant to SEVEN's phantom party members. My first draft of the positional check had a malformed condition; it was fixed before this verdict. Differs from the original: lattice search, no game code. · session; brain train rebuild pass on Seven-relevant Games lessons, 2026-10-11; session_01NHKVhTvCnvtvZ2NGLSPYj6

## E14 — sticky pick inverts when eligibility widens
- Date: 2026-08-28
- Project: pappydapimp69/mirage
- Tags: [ui][gamedesign][state][algorithm]
- What: A "pick the first eligible and HOLD it until it personally stops qualifying" selector inverts its meaning when the eligibility predicate widens from rare to common. While eligibility is rare, "first eligible, held" and "the one that matters" are the same target, so the design looks correct for as long as that regime lasts. Widen the predicate and the selector locks onto a trivial instance that qualified earlier and never sees the important one — while remaining continuously occupied, never idle, and never in error. Sandbox-confirmed: 100% of post-event ticks on the important target under rare eligibility, 0% under wide eligibility, with the selector HELD for more ticks in the broken regime (600) than in the working one (480).
- Why built: `brain train combined` queued dog + mirage. dog#E39 says a single-action resolver is only correct while there is truly ONE selectable target and needs real selection state once a sibling appears; this is the next case, where the sibling arrives not as a new UI item but as a WIDENED PREDICATE, and MIRAGE had just produced a live instance.
- Design: One selector, one set of candidates, two eligibility predicates — rare (`broken`) and wide (`broken || far`) — with an important event fired at a fixed tick to a fixed candidate, and strollers drifting in and out of `far` on staggered fixed cycles. Then each half of the candidate fix measured SEPARATELY as well as together. Fully deterministic: no rng, no wall-clock, eligibility is a pure function of tick and index.
- Got right: Measuring the two halves of the fix independently, which is where the real finding is. The intuitive fix — let an important instance PREEMPT a trivial incumbent — is worth exactly nothing on its own (0%, unchanged from broken), because releasing the hold and then re-acquiring with the same first-match rule hands the slot straight back to the same class of candidate. The unintuitive half — prioritising on ACQUIRE — is worth 95% by itself. Both together reach 100%. A fix that had shipped preemption alone would have looked principled, changed nothing, and been very hard to argue with afterwards.
- Where/why it failed: In MIRAGE the doubled-party phantom stands in the place of a companion who is "missing". Missing used to mean only "came apart", which is rare and always the interesting case. Cohesion replaced a following party with a chain, which added "wandered past the vacancy distance" — common, and uninteresting. A stroller therefore claimed the phantom in the first second of an episode and still held it minutes later, so the companion who actually broke was never the one impersonated, in roughly 30% of episodes. Nothing errored: the hallucination ran the whole time, the roster showed its one confident false line the whole time, and the phantom stood over a real absence the whole time. It simply told the wrong lie about which person.
- Fix: Prioritise on ACQUIRE (a broken candidate outranks a merely-distant one, distance breaking ties within each class) AND allow an important instance to preempt a trivial incumbent. Both, because the sandbox shows each alone is either useless or incomplete.
- Why this fix: Preemption without a prioritising acquire is a no-op dressed as a fix. A prioritising acquire without preemption leaves a window in which an incumbent taken before the important event holds through it. The two halves address different moments — who gets picked, and whether a pick can be revisited — and the failure needs both closed.
- Rule of thumb: When a selector's eligibility predicate widens, audit the HOLD, not just the pick. Stickiness is invisible while the eligible set is small, because first-and-only and most-important coincide; once qualifying becomes ordinary the selector reliably latches onto whichever trivial candidate arrived first and stays fully operational while pointed at the wrong thing. And when fixing one, measure the release rule and the acquire rule separately — the intuitive half (preemption) can be worth zero, and the unintuitive half (ordering on acquire) can be worth nearly all of it.
- Provenance (verified/assumed): VERIFIED first-hand — ran tests/sandbox/s3-sticky-pick-vs-widened-eligibility.mjs, observing 480/480 -> 0/480 on-target across the regime change and the 0% / 95% / 100% split across preempt-only, acquire-only and both. An earlier version of this sandbox measured preemption as 0% and I initially took that for a sandbox bug; it is the finding. Corroborated by the live MIRAGE case, where tests/kinds.test.mjs went from 0.7 to 1.0 takeover rate once both halves shipped.
- Composed: dog/E39, mirage/E11
- Link: session; src/percept.js updateDoubledParty; tests/sandbox/s3-sticky-pick-vs-widened-eligibility.mjs
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-mirage-waiting-city-hold-selector-turns-veto-into-livelock.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX

## E13 — window predicate degenerates like a threshold
- Date: 2026-08-28
- Project: pappydapimp69/mirage
- Tags: [gamedesign][state][testing][simulation]
- What: A bounded WINDOW predicate ("this offer stays open for N seconds") fails in exactly the shape august-10#E9 describes for a THRESHOLD predicate keyed on a resource level. Both encode an assumption about a distribution — how long the thing they are waiting for takes — and both go silently degenerate when that distribution moves, with the event still nominally occurring and its interior empty. Sandbox-confirmed: holding one constant (WINDOW=14) and changing only the arrival-time distribution from 1-4 ticks to 18-29 ticks took completion from 200/200 to 0/200 and work-done-inside-the-event from 600 to 0, with zero errors raised and the event still opening all 200 times. This is the same signature as E9's wars ending on the tick they were declared while an arsonist reached a target 0 times in 251 assigned ticks.
- Why built: `brain train combined` queued august-10 + mirage as an untested pair sharing gamedesign/state/testing/simulation tags, and MIRAGE had just produced a live instance: a pylon prime valid for PRIME_WINDOW=14s that needs a second pair of hands, calibrated when the party walked beside you and arrival was ~2s.
- Design: Two regimes over identical logic and an identical constant, differing ONLY in the arrival-time distribution, plus a sweep of the window against the shifted distribution so the result is a boundary rather than an anecdote. Fully deterministic — no rng, no wall-clock, arrival is a pure function of the iteration index.
- Got right: The sweep is what makes this more than a restatement. It locates the turnover (window 20 -> 26% completion, 26 -> 76%, 32 -> 100%) and shows the recovery point is where the window clears the UPPER TAIL of the arrival distribution, not its mean — the mean arrival in the shifted regime is 23.5, and a window of 26 still loses a quarter of all events.
- Where/why it failed: The defect is invisible to every functional test because nothing is broken: the predicate evaluates correctly, the event opens, no exception is raised, and the code path that consumes the event is never entered so it cannot fail either. In MIRAGE the cause was a design change two systems away — cohesion replaced a following party with a chain plus a CALL verb, which turned "your helper is beside you" into "your helper walks up to 25 seconds" — and the constant that quietly depended on the old arrangement lives in a different file with no reference to either.
- Fix: Set the window from the mechanism that feeds it rather than from a measurement of the old regime. MIRAGE's PRIME_WINDOW went 14 -> 32, derived from CALL_DURATION=25 plus headroom; the sandbox's sweep independently returns 100% completion at 32, from a different direction. Also removed a hardcoded duplicate of the old 14 in party.js so there is one constant rather than two agreeing by luck.
- Why this fix: A constant derived FROM the arriving mechanism cannot silently disagree with it: change the walk and the window has to be re-derived, which is a visible edit rather than a silent regime shift. Pinning it to a measurement of the old distribution is what created the failure in the first place.
- Rule of thumb: Any predicate holding a constant that encodes "how long X normally takes" — a window, a timeout, a threshold on a resource level, a termination condition — is a latent trap the moment a design change moves that distribution, and it degrades with NO error and NO failing test, because the interior of the event simply stops being reached. When you change how long something takes, grep for the constants that were waiting on it. Derive such constants from the mechanism they wait on, and size them against the distribution's UPPER TAIL, never its mean — at the mean you still lose a quarter of all events.
- Provenance (verified/assumed): VERIFIED first-hand — ran tests/../scratchpad/train/s1-window-equilibrium.mjs, a deterministic two-regime sandbox plus window sweep, observing 200/200 -> 0/200 completion, 600 -> 0 interior work, 0 errors, and the recovery boundary at window 32. Independently corroborated by the live MIRAGE case, where PRIME_WINDOW=14 against a 25s CALL walk produced a 0% deceived-bot win rate until it was raised to 32.
- Composed: august-10/E9, mirage/E11
- Link: session; MIRAGE commits fb9fd67 and the 0.12.0 stamp; src/state.js PRIME_WINDOW, src/party.js join window
- Reverified: 2026-10-11 · pass · sandboxes/2026-10-11__rebuild-mirage-e13-window-predicate.py · observed RESULT: PASS 4/4; 14 old 1.000 new 0.000; derived 1.000; no headroom 0.714 · Own enumerated call durations (base plus 0..6 ticks). A window of 14 tuned to a base of 8 completes 1.000; move the base to 25 and the same window completes 0.000 with nothing erroring, the event firing and its interior never reached. A window derived from the mechanism (duration plus headroom, 32) restores 1.000, and the same derivation without headroom completes only 0.714. Differs from the original: no game timing, exact enumeration. · session; brain train rebuild pass on Seven-relevant Games lessons, 2026-10-11; session_01NHKVhTvCnvtvZ2NGLSPYj6

## E12 — unexplained binding made a verb unaimable
- Date: 2026-08-28
- Project: pappydapimp69/mirage
- Tags: [ui][input][gamedesign][onboarding]
- What: MIRAGE's tutorial told the player to hand an item to a named companion. The `give` verb has no direct-target form — it acts on the roster SELECTION and nothing else — and selection is changed by Q/R on keyboard. Q and R were bound in input.js and appeared in NO keyboard legend, while the gamepad legend already listed `[LB]/[RB] select`. A keyboard player was therefore handed a verb with no discoverable way to aim it, and a tutorial instruction ("Give it to IREN") they could read, understand, and not carry out. This is the first real-world confirmation of the shared `assert-every-bound-verb-is-explained` kernel, with a failure mode the kernel does not cover: the missing legend entry was not cosmetic, because the unexplained binding was the ONLY way to aim a different verb the game actively asks you to use.
- Why built: A seven-stage tutorial overlay teaching one verb per stage. Two of its stages name a specific companion, which requires aiming at that companion.
- Design: The hint strip is a per-scheme string in hud.js swapped live as the player's input device changes; stage briefs are authored strings in tutorial.js. Both are edited by hand, and neither knew about the other.
- Got right: The gamepad legend WAS complete — `[LB]/[RB] select` was there — which is why this was invisible for so long: any check done on a controller, or any reading of "is selection explained anywhere", passed. The asymmetry between two hand-maintained strings is the whole defect.
- Where/why it failed: Bound verbs accrete. A mechanic lands, the input map and the hint strip get updated because they are needed to PLAY it, and the explaining text silently does not, because nothing breaks. Every functional test passes — the verb itself works perfectly, selection works perfectly, `give` works perfectly. The defect lives entirely in the gap between what is bound and what is said, which no test looked at. Compounding it, the tutorial's own briefs named a person without naming the aiming step, so neither the legend nor the brief closed the loop.
- Fix: Added `Q/R select` to the keyboard legend. Rewrote the two briefs to name the AIMING step but deliberately NOT the key — "Pick IREN out on the roster, then hand it to her" — because a keybind in stage prose duplicates the legend in text that drifts the next time a binding moves, and would be actively wrong for whichever scheme the player is not on ("press B to give" is use-item on a pad). The always-visible legend carries keys; the brief says what to do with them. Added two guards: every control legend must mention selecting, and any stage pinned to a companion id must explain how to aim at one.
- Why this fix: Keeping keys in exactly one place (the legend) and intent in another (the brief) means the two cannot contradict each other, and the scheme-swapping legend stays the single source of truth for what to press. Both guards were negative-controlled — each defect was reverted and the corresponding guard confirmed to fail — because a guard that has never failed is decoration, and this codebase has repeatedly produced tests that assert the bug rather than catch it.
- Rule of thumb: A control legend is not documentation, it is part of the mechanic, and the test for it is not "is every binding listed" but "can the player aim every verb the game asks them to use". Audit verbs that have no direct-target form with special care: they inherit their aim from a SEPARATE binding, so an unexplained selection control silently disables a fully-working verb, and every functional test still passes. Where a tutorial names a target, say what to do, never which key — prose duplicating a keybind drifts, and is wrong for whichever input scheme the reader is not holding.
- Provenance (verified/assumed): VERIFIED first-hand — found while fixing a browser test that had been calling `OFFER_ITEM` with a target argument the real handler ignores; confirmed by reading input.js's bindings against both legend strings; both new guards negative-controlled by reverting each defect and observing the specific failure; full 16-suite run green and all seven stages completing in headless Chromium at mirage-0.11.2, deploy-verified live.
- Composed: N/A
- Link: session, commits fe6c02a (fix) and b9ea815 (merge/stamp mirage-0.11.2), src/hud.js + src/tutorial.js + tests/tutorial.mjs

## E11 — cross frame tally on a rebuilt object
- Date: 2026-08-18
- Project: pappydapimp69/mirage
- Tags: [gamedev][state][testing][browser]
- What: MIRAGE's tutorial has one step that spans two events — "check in on HALDER, then on NKEM" — and it kept its half-finished tally (`progress.seen`) on the object returned by `tutorialProgress()`. That object comes from `loadSettings()`, which re-parses localStorage and constructs a NEW object on every call, and the observer calls it once per frame. The first answer was therefore recorded onto an object that no longer existed by the time the second answer arrived, and the stage was uncompletable in real play. Every other tutorial step is single-event, so this was the only step the defect could touch, and it shipped green through a unit suite, a browser suite and a manual pass.
- Why built: A seven-stage tutorial overlay that observes the real event stream rather than running a sandbox mode, with per-stage progress persisted in the existing settings payload so it survives a reload without adding a second localStorage key.
- Design: `observe(progress, stage, events, sim)` matched a frame's events against the active stage's pinned step and pushed the stage id into `progress.done` on success. Multi-target steps accumulated matched ids in `progress.seen` and only completed once every named target had been seen. `progress` was re-read from persisted settings each frame so that completion would be durable across reloads.
- Got right: The persistence decision itself was correct and deliberate — tutorial progress lives INSIDE the save payload rather than as its own raw localStorage key, which avoids the cross-slot leak where finishing gated content in any one slot disables it for every future new game in every slot. The bug was not in choosing to persist; it was in assuming one storage location could serve both durable completion and transient mid-stage state.
- Where/why it failed: Two independent things hid it, and each one alone would have been enough. First, the unit test held a single `progress` object across all three of its `observe` calls — which is precisely the assumption the production code got wrong. Written from the same mental model as the feature, it could only ever certify that model's blind spot. Second, `loadSettings`'s no-storage-key path returned `{ ...DEFAULT_SETTINGS }`, a SHALLOW copy, so every caller taking that path shared one aliased nested `tutorial` object; before any settings key exists — which is the state of every fresh page, including a fresh test page — the tally appeared to persist purely because each frame was handed that same aliased object. The first isolated browser probe therefore passed, and the defect only became reproducible once an earlier stage had written a settings key for `loadSettings` to parse instead. The aliasing was also a live corruption bug in its own right: a completed stage mutated the module-level default for the rest of the session.
- Fix: Moved the tally off the persisted record entirely and onto `tut`, the in-memory object whose lifetime is exactly the running stage, and changed the signature to `observe(progress, stage, events, sim, scratch)` so the storage is an explicit caller-supplied parameter that throws when a multi-target step is given none, rather than a property quietly written onto whatever object happened to be passed. Gave `loadSettings` a `freshSettings()` helper that deep-copies its nested defaults on both the no-key and the parse-failure path. Added a regression test that rebuilds `progress` on every call the way the frame loop actually does, and a negative test asserting the throw.
- Why this fix: Durable completion and transient mid-attempt progress have genuinely different lifetimes, so they need different homes — a half-finished tally that survived a reload into a different stage would be its own bug. Making `scratch` a required parameter that fails loudly converts a silent-forever defect into a startup crash the first time anyone adds a second multi-target step, and the deep copy removes the aliasing that was making wrong code look right.
- Rule of thumb: State that must survive from one frame to the next can only live on an object whose lifetime you can name. Any accessor that re-reads, re-parses or re-derives its result — `loadSettings()`, a selector, a getter over storage — hands back a fresh object every call, so writing cross-frame state there is a silent no-op; and when the shared-default path aliases one object instead of copying it, the broken code will appear to work in exactly the fresh-state conditions your first test runs under. Write the multi-event test so it re-derives the accumulator on every call the way the real caller does, or it will hold one object across calls and certify the very assumption under test.
- Provenance (verified/assumed): VERIFIED first-hand — reproduced in headless Chromium by driving the real verbs through the real frame loop and observing `done` stay empty after both check-ins; confirmed the isolated-probe/full-sequence split was caused by the shallow-copy aliasing by instrumenting both orderings; confirmed the fix with a regression test that rebuilds progress per call, and with all seven stages completing in a browser plus the full 16-suite run green at mirage-0.11.1, deploy-verified live.
- Composed: N/A
- Link: session, commit 99f49e4 (fix) and e153572 (merge/stamp mirage-0.11.1), tests/tutorial.mjs + tests/tutorial-play.mjs
- Cited-by: 2026-08-28 · projects/pappydapimp69__mirage.md#E13 · compatible · no sandbox · session; MIRAGE commits fb9fd67 and the 0.12.0 stamp; src/state.js PRIME_WINDOW, src/party.js join window
- Cited-by: 2026-08-28 · projects/pappydapimp69__mirage.md#E14 · compatible · no sandbox · session; src/percept.js updateDoubledParty; tests/sandbox/s3-sticky-pick-vs-widened-eligibility.mjs
- Cited-by: 2026-08-28 · projects/pappydapimp69__mirage.md#E16 · compatible · no sandbox · session; tests/sandbox/s5-test-sharing-the-features-assumption.mjs; src/tutorial.js observe() and tests/tutorial.mjs

## E10 — css pixels are not a physical unit
- Date: 2026-08-10
- Project: pappydapimp69/mirage
- Tags: [browser][ui][input][rendering][testing]
- What: A first-person browser game was reported as having a wrong "viewport zoom" and directional controls that "feel off". Both were caused by the WINDOWS DISPLAY SCALING setting (125%), which resizes the view outside the application entirely. The camera was innocent: measured horizontal FOV is 90.0 degrees at 100%, 125% and 150% scaling, before and after any fix.
- Why built: The 3D camera derives vertical FOV from aspect ratio, which is scale-invariant, so the projection was correctly suspected-and-cleared early. The HUD and the mouse were never suspected because both were written in the unit the browser hands you: CSS pixels.
- Design: HUD entirely in fixed `px` (152 values); pointer-lock camera control accumulating `e.movementX`; `renderer.setPixelRatio(devicePixelRatio)` called once at construction.
- Got right: Deriving vertical FOV from aspect rather than fixing it — that is why the projection genuinely did not move, and why the search could be narrowed to everything AROUND the 3D view.
- Where/why it failed: At 125% scaling the CSS viewport shrinks from 1920x1080 to 1536x864 while the monitor does not change, so a CSS pixel is 1.25 physical pixels. Three consequences, none of them in the renderer. (1) An 11px label becomes 25% physically larger AND takes 25% more of a smaller viewport — the world is untouched, the furniture around it grows, which reads exactly like being zoomed in. (2) Pointer-lock `movementX` is reported in CSS pixels, so the same physical mouse sweep reports 20% fewer units and the camera turns 20% slower. (3) `devicePixelRatio` is not a property of the machine — it moves with OS scaling, browser zoom, and dragging a window to a second monitor — so a ratio captured once leaves the drawing buffer at the wrong resolution for the CSS box it is stretched across.
- Fix: Root font-size derived from the viewport (`clamp(10px, 0.55vw + 0.55vh, 20px)`) with the stylesheet converted to rem, so the HUD is a constant FRACTION of the screen; hairline borders left in px because a 1px rule scaled into a viewport fraction lands on a half pixel and smears; media-query breakpoints left in px because expressing a layout threshold against a viewport-derived root size is circular. Pointer deltas multiplied by `devicePixelRatio` to recover device pixels. `setPixelRatio` re-applied on every resize, plus a re-arming `(resolution: Ndppx)` media query, because a DPR change does not reliably fire `resize`.
- Why this fix: The bug is a unit error, so the cure is to stop expressing player-visible quantities in the unit that varies. Anything the player perceives as a size or a speed has to be anchored to the screen or to the device, never to CSS pixels.
- Rule of thumb: A CSS pixel is not a physical unit. Size UI in viewport-relative units so it holds a constant share of the screen, convert pointer/mouse deltas by `devicePixelRatio` before turning them into rotation, and never cache `devicePixelRatio` — re-read it on resize and watch a resolution media query for the changes resize does not report. Test it by running the SAME physical screen at several `deviceScaleFactor` values and asserting on fractions of the viewport, not on pixel counts.
- Provenance (verified/assumed): Verified first-hand in Chromium via Playwright `deviceScaleFactor`, with a negative control run before trusting the test: with the fixes reverted it reports HUD text 25% off its share and the same physical mouse sweep turning 20% differently at 125%, and 50%/33% at 150% — matching the original report; with the fixes, all three cases are identical. The mouse probe additionally asserts it produced non-zero rotation, because the first version of it stopped at the input accumulator (rotation is applied inside `poll`) and reported 0.0000 in every column, a green that proved nothing.
- Composed: N/A
- Link: pappydapimp69/mirage main, css/style.css + src/input.js + src/render.js + tests/dpi.mjs
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E52 · compatible · no sandbox · Seven commit for seven-1.6.0, session 2026-10-11; session_01XbmpbLd4QyYTiQBBzo2Hdw
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E54 · compatible · no sandbox · Seven tests/view.mjs, session 2026-10-11; session_01XbmpbLd4QyYTiQBBzo2Hdw

## E9 — three names for one truth
- Date: 2026-08-10
- Project: pappydapimp69/mirage
- Tags: [refactor][state][testing][gamedev]
- What: After two rewrites in one session, a pylon's aliveness was recorded three ways — `spent` (the new truth), `charge` (vestigial from the discarded pool model, but still READ by percept, render and main), and `live` (written in two places, read nowhere). Only one code path updated all three together.
- Why built: The pylon went from a continuous restore-while-you-stand tap, to a charge pool you drew from repeatedly, to a single one-shot pulse. Each rewrite stopped WRITING the previous model's fields in the new path and left them in place rather than deleting them.
- Design: `activatePylon` set `spent = true`, `live = false`, `charge = 0` together; every reader elsewhere picked whichever field it had been written against at the time.
- Got right: Keeping a back-compatible read when the fields were finally removed (`spent ?? charge <= 0`), so saves written before the change still deserialise correctly.
- Where/why it failed: Any path that marked a pylon dead WITHOUT going through `activatePylon` left the others lying — a save from before the change, a test fixture, the next person's code. Such a pylon would be spent and still glow, still be offered by the HUD, and still be treated as live by the deception layer, which is a state that is neither real nor a hallucination. Every behavioural test passed throughout, because they only ever drove the one path that happened to keep the three in sync.
- Fix: Delete `charge` and `live` from the model, the save payload and every reader, leaving `spent` as the only field. Not a synchronisation helper.
- Why this fix: An invariant that says "these fields must agree" is a bug waiting for the next code path. Three names for one truth is three chances to drift; one name cannot drift.
- Rule of thumb: A refactor that changes a system's MODEL must delete the old model's fields in the same change, not merely stop writing them — and grep for READERS, not writers, before calling a field vestigial. `live` really was dead; `charge` was still deciding what the player SAW.
- Provenance (verified/assumed): Verified first-hand. Found by a purpose-built invariant sweep (tests/stress.mjs) asserting structural facts about any reachable state under long hostile-input runs; its first execution reported the disagreement on 10 of 12 seeds. After deletion, 40 seeds run clean, and the sweep now fails if either field reappears. Latent rather than live in production — the shipped build only ever reached those fields through `activatePylon`.
- Composed: N/A
- Link: pappydapimp69/mirage main, src/state.js + tests/stress.mjs
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-mirage-wrong-sky-model-consolidation-picks-the-hazardous-field.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX

## E8 — serialised cells as world coords
- Date: 2026-08-10
- Project: pappydapimp69/mirage
- Tags: [serialization][testing][gamedev][state]
- What: A save system serialised each AI agent's in-flight pathfinding route with `path.map(n => ({ x: n.x, z: n.z }))`. The nodes are GRID CELLS carrying `{cx, cz}`, not world coordinates, so every saved node was written as `{x: undefined, z: undefined}`.
- Why built: Paths are saved rather than recomputed on resume because re-deriving one draws from the shared rng stream and would fork a resumed run from the original. The field names were written from memory of what a "point" looks like in this codebase, and world points are `{x, z}` everywhere else.
- Design: `serializeRun` maps each character's `path` array into plain objects; `deserializeRun` maps them back; a round-trip equality test compares a fingerprint of the whole sim before and after.
- Got right: Saving the path at all, and saving the rng stream word alongside it — the resume-determinism test that eventually caught this only exists because that fidelity was taken seriously in the first place.
- Where/why it failed: On resume the walker aimed at `cellToWorld(undefined, undefined)` = NaN, the move came out NaN, the collision routine refused it, and the agent stood wedged until its next scheduled re-path. It never threw. More importantly it never failed the round-trip check, because BOTH sides of the comparison agreed on the same corrupted array — the bug is invisible to any test asking "does what came out equal what went in". It surfaced only as a downstream divergence: a companion who lost a fraction of a second of movement reached a pylon one tick later, shifting every subsequent draw off the shared stream and failing a determinism assertion several systems away.
- Fix: Serialise `{cx, cz}`, and add a test that asserts the restored VALUES are finite grid cells rather than asserting equality with the original.
- Why this fix: Round-trip equality proves a serialiser is a bijection with itself, not that it preserved meaning. Only a content assertion can see a field that was uniformly wrong on both sides.
- Rule of thumb: For any structure whose fields ARE a coordinate system (cell vs world, local vs global, index vs id, relative vs absolute), assert on the restored values — finite, in range, resolves to a real entity — not just on their equality to the original. And when a determinism test fails far from the change that caused it, suspect a silently degraded value upstream before suspecting the rng.
- Provenance (verified/assumed): Verified first-hand — the save round-trip test passed while a resumed companion's first tick diverged (repathTimer 0.85 vs 0.2, the signature of a walker wedged against nothing); after serialising cx/cz the resumed run tracked the original for 30+ simulated seconds, and a new assertion on `Number.isFinite(n.cx)` now fails the old code.
- Composed: N/A
- Link: pappydapimp69/mirage main, src/save.js + tests/save.test.mjs
- Cited-by: 2026-10-10 · projects/local__sandbox-kernel-serialization.md#E1 · compatible · sandboxes/2026-10-10__json-big-id-rounding-is-runtime-specific-and-needs-an-exact-bigint-guard.py · observed RESULT: PASS 14/14 checks. Observed 500/1000 corrupted at 2^53 but 501 distinct (prediction miss, edge tie-to-even), 750/1000 and 251 distinct at 2^54, round trip 1000/1000 idempotent vs 500 wrong, string transport 0 and Number(str) 500, r… · session_01YFLLRpDsfZpRstb2KT2MQy

## E7 — oracle cannot price the gap it is outside
- Date: 2026-08-10
- Project: pappydapimp69/mirage
- Tags: [testing][gamedesign][verification][ai-agents][balance]
- What: In a system whose difficulty IS an information gap, a scripted policy that reads ground truth is not a weak difficulty oracle — its success rate is INVARIANT to the strength of the deception. Sweeping deception strength from 0 to 2 phantom markers per real one moved the truth-reading policy's win rate by 0.0 percentage points (flat 100%) and the percept-reading policy's by 77.0 (100% -> 23%), over the same world, router and budget.
- Why built: MIRAGE's balance harness drives whole runs with scripted policies that read `sim` directly. After a party-cohesion change removed most of the game's incidental drain, its pressure assertion started failing, and the obvious response was to raise the base drain rate until the bot lost again (1.05 -> 1.9, plus a cut to the opening calm window). That change was authored and measured and about to ship before the project owner pointed out that the bot cannot hallucinate.
- Design: Sandbox `tools/sandboxes/oracle-vs-deception.mjs` — six real markers on a 40x40 grid placed by integer hash (no RNG, no wall clock), a `lieRate` parameter adding phantom markers that are indistinguishable when choosing where to walk and evaporate on arrival, and ONE nearest-first router run twice: once over the real list, once over the shown list. 200 seeds per cell.
- Got right: Running the honest policy at the SAME lieRate values rather than only at the tuned point — the flat 0.0pp line is the whole finding, and a single-point comparison would have shown only that one bot is better than the other, which is unremarkable.
- Where/why it failed: The intuition that an oracle is a "lower bound, so treat its numbers conservatively" is wrong in a specific way — a lower bound still MOVES with the thing it bounds, and this one does not move at all. A metric with zero sensitivity to a mechanic is indistinguishable from a valid metric that happens to be stable, which is how the drain-rate change passed both review and a fully green suite.
- Fix: Add a handicapped policy that navigates from the same derived view the player sees (a real `percept`): it walks to markers that do not exist and logs them, chases relief that recedes, steers by a compass whose error grows, and believes the party is fine because the chorus agrees. Assert difficulty against that policy only, two-sided (too-easy AND unwinnable), and revert the drain rise.
- Why this fix: The measurement has to be subject to the mechanic it is measuring. Sampling harder does not fix zero sensitivity, and no amount of caution applied to a flat line recovers the slope.
- Rule of thumb: Before tuning any constant against an automated player, ask what that player CANNOT be subjected to. If the answer names the mechanic the constant is supposed to price, the measurement has zero sensitivity to it — build a handicapped agent on the same derived view the human gets, then check two things before trusting its first result: that it survived long enough to MEET the mechanism (an omniscient bot finished the survey in 96s, inside a 90s grace window, and hallucinated zero times), and that it is not branching on the state flag that NAMES its own handicap (reading `player.hallucinating` made it dive for relief instantly and never walk into a single lie).
- Provenance (verified/assumed): Verified first-hand. Sandbox `oracle-vs-deception` at 200 seeds/cell: omniscient spread 0.0pp across lieRate 0-2, deceived spread 77.0pp; the budget where the oracle first reaches a 50% win rate (89) leaves the deceived policy at 0.0%, while the honestly-tuned budget (147) leaves the oracle at 100.0%. Field case verified in MIRAGE `tests/balance.mjs`: the `deceived` policy scores 67%/25% at BASE_DRAIN 1.05, against a proposed 1.9 justified only by the truth-reading policies.
- Composed: opticon/E38, opticon/E32, opticon/E20
- Link: pappydapimp69/mirage main, tests/balance.mjs `deceived` policy + tools/sandboxes/oracle-vs-deception.mjs
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E15 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E6 — body relative formation orbits the camera
- Date: 2026-08-10
- Project: pappydapimp69/mirage
- Tags: [gamedev][ai][gamedesign][camera]
- What: A player reported that five AI companions "just scatter and do their own thing". They were not scattering: instrumented over 6 seeds x 90s of walking they were on screen 0.0% of the time, at a median 6.2 units, with `goal=follow` 100% of the time. A perfectly disciplined squad, permanently in the one place a first-person camera can never look.
- Why built: The formation slot function returned `lead + (sin yaw, cos yaw) * r`, which is the exact NEGATIVE of the camera's forward basis `(-sin, -cos)`. The sign was never questioned because the party demonstrably followed and the code read as "a fan around the lead".
- Design: A bearing-and-radius table per companion (two walking point, two flanks, one rear guard), resolved each tick against the lead's position and facing, with a stand-off slack band to stop jitter.
- Got right: Measuring ON-SCREEN FRACTION per companion before touching the AI at all. The behaviour numbers (`goal=follow` 100%) proved the AI was working, which is what redirected the whole investigation from decision-making to visibility.
- Where/why it failed: Three further faults were stacked underneath, each invisible until the one above it was fixed. (1) Followers were capped at 4.6 units/sec against a lead who walks 4.3 and runs 7.4, so a station that MOVES could be chased but never reached — the four forward slots sat 60-89 degrees off their assigned bearing while the rear guard, whose station falls into your lap for free, held to 11. (2) A station ahead of the leader is inside geometry 31-38% of following-seconds (the leader walks around a rock; the point 7 units ahead does not), and an unreachable target does not read as unreachable — the follower paths at it, wedges, re-paths and drifts. (3) The formation was anchored to YAW, and in first person the camera IS the body, so the whole party orbited on every glance: the rear guard could not be brought into frame by a full 360-degree turn, and the flanks swirled across the screen whenever the player looked around.
- Fix: Negate the slot basis to match the camera; give followers a gap-proportional catch-up gear capped above the lead's sprint; resolve each station against collision before assigning it; and anchor bearings to a SMOOTHED DIRECTION OF TRAVEL instead of yaw, so the formation stands in the world and you look AT it.
- Why this fix: Every one of the four is a different reason a correct formation never materialises, and fixing any one alone leaves the symptom intact — which is why the first fix (the sign) moved on-screen time from 0.0% to only 45.6% and looked like a partial success rather than three remaining bugs.
- Rule of thumb: "The AI companions scatter" is usually a VISIBILITY claim, not a behaviour one — measure on-screen fraction per companion before touching decision code. And walking statistics cannot distinguish "behind you" from "gone", because both read 0%: the separating test is a stationary full 360-degree turn in which every member must enter frame at least once.
- Provenance (verified/assumed): Verified first-hand via tests/formation.mjs over 6-8 seeds x 90s: on-screen per forward companion 0.0% -> 60-71%, someone in frame 81% of walking seconds, mean bearing error 60-89 degrees -> 21-28, forward stations inside geometry 31-38% before collision-resolution. The 360-degree sweep assertion is what caught the yaw-anchoring and is now in the suite.
- Composed: N/A
- Link: pappydapimp69/mirage main, src/party.js + tests/formation.mjs
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E49 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E52 · compatible · no sandbox · Seven commit for seven-1.6.0, session 2026-10-11; session_01XbmpbLd4QyYTiQBBzo2Hdw
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E54 · compatible · no sandbox · Seven tests/view.mjs, session 2026-10-11; session_01XbmpbLd4QyYTiQBBzo2Hdw

## E5 — a refusal is a tell
- Date: 2026-08-10
- Project: pappydapimp69/mirage
- Tags: [gamedesign][ui][testing][security]
- What: MIRAGE hides exactly one fact from the player: whether their own mind is currently hallucinating. A new verb (striking a false entry from the survey record, allowed only while lucid) leaked that fact twice, in the same shape, and the first version of its test asserted the leak.
- Why built: The verb needed a gate — you cannot audit a record using the faculty that corrupted it — and the obvious implementation was to drive both the contextual prompt and the rule from one lucidity-gated helper, which is normally the right instinct (one resolver, no disagreement between what is offered and what is allowed).
- Design: `strikeTargetAt(sim, actor)` returned the strikeable entry or null, gated on `!actor.hallucinating`; the HUD's single prompt resolver and `logMarker` both called it.
- Got right: Having one resolver at all — the fix was to split it deliberately along the truth/belief line, which is a small change precisely because the seam was already in one place.
- Where/why it failed: Gating the PROMPT meant the offer simply did not appear while hallucinating, so its absence was a perfectly reliable readout of the hidden fact: walk to a known claim, see no prompt, conclude you are under. A lucidity meter with extra steps. With the prompt restored, pressing the key while under did nothing at all — no message, no change — which is the same leak one layer down: press, observe nothing, conclude.
- Fix: Split `claimedEntryAt` (what the screen shows, ungated) from `strikeTargetAt` (what the rules allow, gated); and make a refused strike emit the IDENTICAL event with identical text in identical styling, recording the attempt as a BELIEF on the observer's percept (which deliberately survives recovery) rather than as a fact on the record.
- Why this fix: Only the effect may differ. Anything else the player can observe — the presence of an affordance, an acknowledgement, a colour, a latency — reconstructs the secret from the outside.
- Rule of thumb: In any system with hidden state, A REFUSAL IS AN OBSERVATION. Ask of every gate: what does the user learn from the fact that it fired? Offer the affordance, acknowledge identically, record the refusal as a belief on the observer, and let only the effect differ — the same shape as a permissions model that must not confirm existence, or a rate limiter that must not reveal who is throttled.
- Provenance (verified/assumed): Verified first-hand in a real browser. The first smoke assertion was literally `assert(!/strike/.test(promptWhileHallucinating))` — it asserted the leak and passed; the replacement asserts the two prompt strings are byte-identical across lucid and hallucinating states and that the rules refused the verb underneath, and a logic test compares the emitted event text of a real strike against a believed one for exact equality.
- Composed: N/A
- Link: pappydapimp69/mirage main, src/state.js + src/hud.js + tests/smoke.mjs
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-mirage-opticon-redaction-is-itself-an-observation.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E38 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E9 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-10-10 · projects/local__sandbox-refusal-rule-not-bucket.md#E1 · compatible · sandboxes/2026-10-10__refusal-names-the-rule-not-the-bucket-but-never-the-secret-operand.py · observed RESULT: PASS rule-level refusal cuts guard calls to 0.57x of category-only (S1) and gives 20/20 named receipts on false positives, but naming matched VALUES drops secret-threshold recovery from 8 to 1 probe and listing ALL matched rules le… · session_01YFLLRpDsfZpRstb2KT2MQy
- Cited-by: 2026-10-10 · projects/local__sandbox-refusal-operand-disclosure.md#E1 · incompatible · sandboxes/2026-10-10__refusal-operand-disclosure-is-graded-and-priced-in-bits-no-free-design.py · observed RESULT: FAIL 3 of 27 checks refuted (pre-registered predictions: ABS16 benefit 0.63<0.75, NEAR benefit 0.90>0.45, FLOOR calls 4.75>=NOVAL 4.51). Key numbers: no operand 4.51 calls, worst 7 probes; exact operand 1.75 calls, 1 probe; 8-wide… · session_01YFLLRpDsfZpRstb2KT2MQy
- Cited-by: 2026-10-14 · projects/pappydapimp69__brainwork.md#E223 · compatible · sandboxes/2026-10-14__zero-allow-history-needs-a-benign-canary.py · observed RESULT: PASS zero-allow ambiguous in 1/3 histories (all-risky), canary separates 3/3, distinct hold leaks threshold in 7 probes, identical ack leaks none · brain train auto pass 5, 2026-10-14; session_01Fej6hmi1TecJBFrsQdbvMU

## E4 — cache bust gap recurrence
- Date: 2026-08-03
- Project: pappydapimp69/mirage
- Tags: [browser][tooling][process][debugging]
- What: On a no-build static ES-module site deployed to GitHub Pages,
  `index.html` stamped a cache-bust token onto only `css/style.css` and
  `src/main.js`, while main.js's own `import ... from "./percept.js"` (and
  state/hud/render/party/world/input/audio) carried no token at all. Those
  nested specifiers are SEPARATE cache entries. Three consecutive correct
  source fixes shipped green and the user reported "still broken" after every
  one, because every fix lived in exactly the unstamped files.
- Why built: The `?v=` token was added by hand to the two references visible
  in index.html, which is where a cache-bust "obviously" belongs. Nothing in
  the HTML hints that the entry module goes on to pin seven more URLs.
- Design: Entry-point-only stamping. `index.html` → `src/main.js?v=X`; main.js
  → bare `"./state.js"`, `"./percept.js"`, … Pages serves all of them with
  `cache-control: max-age=600` plus an ETag (verified by `curl -I` against the
  live site, not assumed).
- Got right: The source fixes themselves were correct every time, and the
  local headless verification of them was sound. The failure was entirely in
  what reached the browser, not in what was written.
- Where/why it failed: Two compounding costs. (1) The gap itself, now its
  THIRD recurrence (the-game-prologue#E8, #E17's "fix it in all of them",
  dog#E30). (2) The debugging it induced: confronted with "the fix didn't
  work," the agent re-diagnosed the symptom as a fresh logic bug twice —
  first `distortion()`'s return value, then a `.lost` CSS class overriding
  inline opacity — and shipped a real but irrelevant fix for each. Both were
  verified against LOCAL source in a headless browser; neither was ever
  loaded by the user's browser. `curl`ing the deployed module and finding the
  new code present looks like proof the fix is live and is not, because the
  entry module the page actually executes pins a different URL for its imports.
  A NEW, sharper failure mode was then found while adding a feature that
  introduced a new export (`believedKinds` in percept.js, imported by
  main.js): a PARTIAL bust is strictly WORSE than no bust at all. Stamping
  only the entry guarantees a FRESH main.js resolved against a POSSIBLY STALE
  percept.js, and the moment a release adds an export that skew stops being
  stale content and becomes an unresolved import — module load fails and the
  screen is black. Left uniformly unstamped, the browser at least serves one
  self-consistent old set that still runs and self-heals within the 600s TTL.
- Fix: Stop hand-stamping. Put ONE version token on every cache-bustable URL —
  index.html's <link>/<script> AND every relative import inside src/*.js — and
  assert it. Two sessions converged on this independently and from opposite
  ends: one from the recurrence itself, shipping `tools/stamp-version.mjs`
  (one command, no build step, still a plain static site) plus a suite check
  that every import and asset URL equals the current `BUILD` constant; the
  other from a live black-screen risk, prototyping the same rewrite as a
  deploy-time step over the assembled artifact with a guard that fails the
  deploy. The in-source version won on the merge, because the source that
  ships is then also the source the test reads — a deploy-time rewrite leaves
  the repo perpetually "wrong" and only correct in CI.
- Why this fix: It is the one place that sees every file at once, it cannot
  drift by hand, and — decisively — it is MACHINE-CHECKABLE. No behavioural
  test can catch this class of bug: the source on disk is always correct, so
  the suite is green precisely while users run old code. An invariant test
  ("every import and asset URL equals BUILD") is the only thing that fails on
  the right machine at the right time. The in-source variant beats a
  deploy-time rewrite specifically because the artifact the test reads is then
  the artifact that ships; rewriting at deploy time means the checked-in
  source is permanently in the un-stamped state and only correct inside CI,
  which puts the invariant back out of the suite's reach.
- Rule of thumb: A shipped, source-verified fix reported as having no effect
  on a static ES-module site is a deploy-integrity signal BEFORE it is a logic
  signal — check the cache-bust shape before re-diagnosing the symptom, and
  verify by what the ENTRY module resolves its imports to, never by fetching
  the changed file directly. Stamp every specifier or none: a partial bust
  manufactures a version-skew crash that a consistent stale cache never would.
- Provenance (verified/assumed): VERIFIED first-hand this session — the
  `cache-control: max-age=600` + ETag headers were read off the live Pages
  deployment with `curl -I`; a full specifier rewrite was run against a
  locally assembled copy of the real site and every specifier confirmed
  rewritten (including the vendored `../lib/three.module.js`); that rewritten
  site was then served and loaded in headless Chromium (hook present, a
  newly-added export resolved, the new DOM node present, zero console errors),
  which is the direct evidence that a fully-stamped graph boots; the guard was
  tested in BOTH directions (fires on un-stamped source, passes on stamped).
  The "partial is worse than none" conclusion is reasoned from those measured
  headers plus the observed new-export dependency, not from a reproduced black
  screen — the crash was prevented, not witnessed. The three-recurrence history
  and the two wrong diagnoses are reported from prior sessions' records.
- Composed: the-game-prologue/E8, the-game-prologue/E17, dog/E30, opticon/E36
- Link: MIRAGE crafting-deception session; `tools/stamp-version.mjs` and the
  "every module import and asset URL carries the current BUILD token" check in
  tests/logic.test.mjs.
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E32 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E3 — tick clears shared queue before earlier write is read
- Date: 2026-07-30
- Project: pappydapimp69/mirage
- Tags: [gamedev][state][events]
- What: A shared `sim.events` array is written to from two different call
  sites within the same animation frame: `handleAction()` (an input handler —
  pickup/use/craft/gather/log) runs first, then `tick()` (the periodic
  simulation step) runs second and unconditionally does
  `sim.events.length = 0` as its OWN first statement, before pushing its own
  internal events (discover/recover/hallucinate/chatter). The HUD reads
  `sim.events` once per frame, after both have run.
- Why built: `sim.events` was designed as a per-tick transient buffer —
  "cleared and refilled once per tick, read once by the HUD" — which is a
  clean contract as long as tick() is the ONLY writer. Two other call sites
  (the balance harness, and two logic tests) call `tick()` directly in a
  tight loop and count `sim.events` per call, which only works if each call
  starts clean — so the clear-at-start-of-tick() behavior is load-bearing
  elsewhere, not just incidental.
- Design: within one animation frame, `handleAction()` (input handler) runs
  first and pushes onto `sim.events`; `tick()` (periodic simulation step)
  runs second and unconditionally executes `sim.events.length = 0` as its
  own first statement before pushing its own internal events; the HUD then
  reads `sim.events` once, after both writers have already run.
- Got right: the transient-buffer design is genuinely correct and cheap for
  tick()'s own internal events, and is exercised correctly by two existing
  tests and a whole-run harness that depend on exactly this per-call
  isolation.
- Where/why it failed: an input handler's emitted event (e.g. "Flare
  secured.") never reached the screen. It existed in `sim.events` for a few
  statements, then `tick()`'s own clear (further down the SAME frame's
  call chain) deleted it before the HUD's once-per-frame read ever ran. This
  is not a "listener unsubscribes mid-dispatch" race (the more commonly
  known event-bus fragility) — it's two ordinary, individually-correct
  pieces of code sharing one mutable queue with no rule about who owns
  clearing it, so whichever one runs SECOND and clears at ITS OWN start wins
  regardless of what the first one wrote. The bug shipped invisibly for
  several commits because a weak test assertion (`text.length > 0`) was
  satisfied by an unrelated STALE line still sitting in the on-screen
  history from before either handler ran.
- Fix: at the ONE call site that runs both writers in the same frame (the
  outer per-frame step function, not tick() itself), capture the queue
  as a local array immediately before calling the periodic step, and pass
  that local capture directly to the reader as an extra argument — do NOT
  write it back into the shared queue. Writing it back was tried first and
  is wrong: since nothing else ever clears that queue, the restored entries
  persist and get re-displayed on every subsequent frame forever.
- Why this fix: it never touches the periodic step's own clear-at-start
  contract (so every OTHER caller that depends on per-call isolation is
  unaffected), and the capture is fresh-and-discarded every frame (so it
  can't leak forward the way writing back into the shared array did.
- Rule of thumb: when a periodic/tick function clears a shared queue at its
  own start "for its own internal events," and something ELSE can also
  write to that same queue earlier in the same frame, the periodic
  function's clear will silently destroy the earlier write — regardless of
  how correct each writer looks in isolation. Don't restore captured data
  back into a queue whose owner clears it at a fixed point; pass captures
  through a side channel instead, or move the clear to happen right after
  the one designated reader consumes it, never at the top of a function
  something else might have already written to this frame.
- Provenance: verified first-hand — reproduced by driving the actual
  pickup/use/craft flow in a real browser (subtitle text never changed from
  the pre-run line), then confirmed the fix by re-running the same flow and
  observing each expected line appear exactly once, in order. The "write it
  back causes infinite repeat" failure mode was also reproduced directly
  before landing the side-channel fix.
- Composed: N/A
- Link: https://github.com/Pappydapimp69/mirage commit 587d567
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E16 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-09-29 · projects/pappydapimp69__brain.md#E63 · compatible · no sandbox · session https://claude.ai/code/session_01CHKxy8KkvpqUvfaWw1qb3v

## E2 — length greater than zero assertion hides a dropped event
- Date: 2026-07-30
- Project: pappydapimp69/mirage
- Tags: [testing][harness]
- What: Three browser-driven test assertions checked
  `assert(subtitleText.trim().length > 0, "using an item produced no visible line")`
  after triggering a pickup/use/craft action, instead of checking for the
  specific text that action should have produced.
- Why built: a quick, generic "something appeared on screen" check, written
  when the feature was first added and no specific wording was worth pinning
  down yet.
- Design: the same generic pattern was copy-pasted across three assertions
  — `assert(subtitleText.trim().length > 0, "using an item produced no
  visible line")` — run immediately after triggering a pickup/use/craft
  action, checking only that the subtitle DOM element held ANY non-empty
  text, with no check of which specific text was actually present.
- Got right: it does correctly catch a fully-blank subtitle area (e.g. the
  DOM element failing to render at all).
- Where/why it failed: it passed continuously across several later commits
  even after a real bug (see the paired entry on tick() clearing a shared
  event queue) silently dropped the item/craft event entirely — because the
  subtitle area still contained a STALE, unrelated line left over from
  earlier in the same run (a start-of-run message), which by itself already
  satisfies `length > 0`. The assertion measured "is the subtitle area
  non-empty," not "did THIS action produce visible feedback," and those two
  facts came apart exactly when the real bug needed catching.
- Fix: assert a regex/substring match on the SPECIFIC text the action is
  documented to produce (e.g. `/The flare catches/`), not just non-emptiness.
- Why this fix: a specific-text assertion can only pass if that exact event
  actually reached the display this frame; a stale leftover line from
  earlier can never accidentally satisfy it the way it can satisfy a bare
  length check.
- Rule of thumb: for "did this specific action produce visible output"
  checks, a `length > 0` (or `!!text`) assertion is close to worthless if
  the UI element in question can plausibly hold OLD content from before the
  action under test — assert the actual expected text instead. Treat a
  bare non-emptiness check on a persistent/history-style UI element (log,
  subtitle feed, toast stack) as a smell during review.
- Provenance: verified first-hand — confirmed the weak assertions were
  passing while the underlying bug was reproducibly present (subtitle text
  never changed from the pre-run line across pickup/use/craft), then
  tightened all three to substring checks and confirmed they now correctly
  distinguish "worked" from "silently dropped."
- Composed: N/A
- Link: https://github.com/Pappydapimp69/mirage commit 587d567
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E11 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E48 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E1 — emit helper opts spread order clobbers discriminator
- Date: 2026-07-30
- Project: pappydapimp69/mirage
- Tags: [gamedev][state][events]
- What: A generic event-emit helper — `emit(sim, kind, text, opts = {})` →
  `sim.events.push({ kind, text, t: sim.time, ...opts })` — silently loses its
  own `kind` field whenever a caller's `opts` object happens to contain a key
  also named `kind`, because the object-literal spread of `opts` was written
  AFTER the `kind` property, so it overwrites it.
- Why built: `opts` exists so a caller can attach event-specific context
  (which companion, which item, whether it's a phantom) without the helper
  needing to know every possible extra field up front — a reasonable, common
  "base fields + spread extras" helper shape.
- Design: each event is built by a single object literal —
  `{ kind, text, t: sim.time, ...opts }` — with the helper's own reserved
  fields (`kind`, `text`, `t`) listed FIRST and the caller-supplied `opts`
  spread LAST, so any key present in `opts` is applied after, and therefore
  silently overwrites, whichever reserved field it happens to share a name
  with.
- Got right: the base shape (kind/text/timestamp + arbitrary extras) is fine;
  most call sites' `opts` never collided with a reserved field name, so this
  worked correctly for the majority of events in the same codebase.
- Where/why it failed: several call sites passed `{ kind: <item kind> }` as
  the per-item context (a natural name to reach for — "what kind of item was
  this about"), not realizing `kind` was ALSO the event-type discriminator
  the helper itself used as the first positional argument. The resulting
  event object silently had e.g. `kind: "flare"` instead of `kind:
  "itemUsed"`, so every downstream switch/if-chain keyed on the event type
  never matched, and the event was dropped with no error, warning, or
  obviously wrong value (it still looked like a plausible event object).
- Fix: reorder the push to spread `opts` FIRST, then the helper's own
  reserved fields (`kind`, `text`, `t`) LAST, so they always win regardless
  of what the caller's `opts` contains — then separately rename the
  colliding caller-side field to something that isn't a reserved name (e.g.
  `itemKind` instead of `kind`), so the per-event context still survives on
  the object under its own name.
- Why this fix: reordering the spread is a durable, one-line defense against
  ANY future caller reusing a reserved field name by accident (it fails
  safe instead of failing silent), while the rename restores the actually-
  needed data that the reorder alone would otherwise still discard.
- Rule of thumb: in any "base fields + `...extras`" object-literal helper,
  the object's own reserved/discriminator fields must be spread-ordered so
  they are applied AFTER `...extras`, never before — otherwise a caller's
  extra field with an unlucky name silently wins over the field the whole
  system dispatches on. Grep every call site for extras that use a reserved
  field name as a coincidence, not just as future hardening.
- Provenance: verified first-hand — reproduced the silent-drop by tracing
  actual emitted event objects, confirmed the reorder alone still discards
  the extra field's data (since the caller's key gets overwritten either
  way), and confirmed the combined fix (reorder + rename) preserves both the
  correct event type AND the extra context.
- Composed: N/A
- Link: https://github.com/Pappydapimp69/mirage commit d2eb64f
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-mirage-wrong-sky-emit-collision-plus-zero-magnitude.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E12 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-08-01 · projects/pappydapimp69__mirage.md#E18 · compatible · no sandbox · Pappydapimp69/mirage branch claude/brain-install-bhr36y
- Cited-by: 2026-08-03 · projects/pappydapimp69__mirage.md#E19 · compatible · no sandbox · mirage src/percept.js; tests/kinds.test.mjs
