# Pappydapimp69/sweety — lessons

Project: Pappydapimp69/sweety. Newest first.

---

## E18 — size coop gap from measured reach
- Date: 2026-10-17
- Project: Pappydapimp69/sweety
- Tags: [gamedev][level-design][coop][physics]
- What: The gap a gliding player crosses only when the partner's gust throws him. It was sized twice by reasoning and both times he fell short.
- Why built: The twist room needs the gust: alone he must fall short, with it he must make it.
- Design: Glide caps the fall at 2.2 tiles/s. The gust sets vx 15 for 0.35 s and vy to at most -9, so it adds lift only if he is not already rising faster.
- Got right: The idea. The solo and helped reaches really differ.
- Where/why it failed: Measured reaches were 17.5 tiles alone, 20.6 with an early gust, 25.9 with a gust at the peak. A gust while rising adds no lift, so helper timing moves the reach by 25%. The first two gaps were sized from the good-timing case.
- Fix: Measure all three with a short script, then put the edge between solo reach and the WORST-timed helped reach (19: 1.5 margin either side).
- Why this fix: Players gust early, and a gap that needs perfect timing turns a puzzle into a reflex test.
- Rule of thumb: Size a helped-movement gap from measured reaches: solo, worst-timed help and best-timed help, then sit between solo and worst-timed.
- Provenance (verified/assumed): Verified first-hand. A reach script on the real sim gave 17.47 / 20.61 / 25.88. tests/puzzles.test.mjs holds alone-fails, gust-passes and gust-without-pinwheel-fails.
- Link: Pappydapimp69/sweety commit c5537ab; session_01Gs4s9Xnn7DrHixqVcK7JXf

## E17 — hazard corridor pockets
- Date: 2026-10-17
- Project: Pappydapimp69/sweety
- Tags: [gamedev][level-design][coop][testing]
- What: A saw corridor meant to need the partner's time-stop. A lone player waited in the gap between two saws and moved on whenever the next saw was up, and got through.
- Why built: The clocktower and finale corridors gate Spice behind Sugar's freeze. Saws were 3 tiles apart.
- Design: Saws on vertical ping-pong paths, kill radius 0.425, player width 0.75, all in phase. The co-op test only tried walking straight through.
- Got right: Straight-through walking dies, so the existing negative control passed.
- Where/why it failed: A gap wider than two kill radii plus a body is a safe pocket. Hopping pocket to pocket needs only one saw's up-window per hop. 20 of 24 start phases got a lone player through.
- Fix: Space hazards so no pocket fits a body: spacing below 2 x 0.425 + 0.75 = 1.6. Saws went 1.5 apart. The whole run then needs one joint up-window that is too short even with a dash.
- Why this fix: It removes the strategy instead of tuning timing, and it keeps the freeze as the only way through.
- Rule of thumb: A hazard corridor is a gate only if no gap between hazards fits a body; test it with a wait-in-the-gap hopper, not a straight-line runner.
- Provenance (verified/assumed): Verified first-hand with a scripted hopper over 24 start phases: 20/24 got through with 3-tile spacing, 0/24 with 1.5. Both cases are kept as a test and its control in tests/puzzles.test.mjs.
- Link: Pappydapimp69/sweety commit 6b1bcb6; session_01Gs4s9Xnn7DrHixqVcK7JXf

## E16 — countdown overshoots below zero
- Date: 2026-10-17
- Project: Pappydapimp69/sweety
- Tags: [gamedev][state][testing]
- What: A gust-throw bot never fired: its "not being pushed" check `!p.pushT` was false forever after the first push.
- Why built: The bot gusts the partner once he is airborne and not already pushed.
- Design: The sim decrements `pushT -= DT` while it is above 0, so it stops one step below zero (-0.0167).
- Got right: The sim's own checks use `> 0`, so the game was correct.
- Where/why it failed: A truthiness test treats any nonzero leftover as "still running". The value read as pushed forever, and the check had worked earlier only because that player had never been pushed (exact 0).
- Fix: Test countdowns with `<= 0` / `> 0` at every reader, or clamp to 0 when they expire.
- Why this fix: Readers outside the sim (bots, UI, tests) don't know the decrement overshoots; clamping or comparing makes it safe for all of them.
- Rule of thumb: A countdown decremented by dt ends below zero, not at zero; never read it as a boolean.
- Provenance (verified/assumed): Verified first-hand by printing pushT = -0.016666 after a push and a 0 before one. The bot worked once changed to `<= 0`.
- Link: Pappydapimp69/sweety commit c5537ab; session_01Gs4s9Xnn7DrHixqVcK7JXf

## E15 — partner targeted powers gate solo
- Date: 2026-10-15
- Project: Pappydapimp69/sweety
- Tags: [couch-multiplayer][level-design]
- What: In a two-player co-op platformer, each power (pins, slam pads) affects only the PARTNER's footing. A deterministic BFS sandbox checked whether such gates have any solo route.
- Why built: Co-op gates built with self-usable powers kept leaking solo routes, and one player could clear "co-op" puzzles alone.
- Design: 1-D vertical gate. Players stand on the ground, the ledge or pins; jump 3; pin reach 3; PIN_MAX 2. The pin is usable by the partner only, the caster only, or anyone.
- Got right: Partner-targeted pins on a 5-high gate: solo=False, duo=True. Self and shared pins on the same gate: solo=True (not structural co-op).
- Where/why it failed: Partner-targeting alone does not guarantee co-op. A 3-high gate (at or below the solo jump) leaks a solo route. The pin budget also caps duo reach: an 8-high gate is unsolvable even for two players with PIN_MAX 2.
- Fix: Size each gate in a band: above the solo jump envelope and at or below what the duo can reach with the power budget. Back it with a solo negative-control bot.
- Why this fix: The targeting rule removes self-help; the height band removes layout leaks and dead gates; the bot checks both on real levels.
- Rule of thumb: A power that only changes the partner's world makes a gate structurally co-op only when the gate sits above the solo envelope and within the duo's budgeted reach; check both edges.
- Provenance (verified/assumed): Verified first-hand. The sandbox ran 5 scenarios; sweety tests/play.test.mjs solo negative controls pass on the real levels. Assumed: the 1-D model transfers to 2-D layouts with horizontal gaps.
- Composed: ideas:COUCH-MULTIPLAYER/role-balance/reactive-pacing-injects-complications-on-strong-performance, ideas:COUCH-MULTIPLAYER/level-design/scheduled-disruption-events
- Sandbox: sandboxes/2026-10-15__partner-targeted-powers-gate-solo.py
- Prediction: Partner-targeted gates 5 and 8: solo=False, duo=True. Self and shared on 5: solo=True. Partner on 3: solo=True.
- Observed: RESULT: PASS. Gate 5 partner: solo=False duo=True. Self and shared: solo=True. Gate 3: solo=True. Gate 8: duo=False (prediction wrong; PIN_MAX 2 caps duo reach at 6).
- Scenarios: 1) partner-targeted, gate 5; 2) self-targeted, gate 5; 3) shared, gate 5; 4) BREAK: partner-targeted, gate 3 (layout leak); 5) partner-targeted, gate 8 (budget cap)
- Link: Pappydapimp69/sweety branch ccr-3432c267-04v162; session_01Gs4s9Xnn7DrHixqVcK7JXf
- Audited: 2026-10-15 · modeled · Read the entry and its stored sandbox and re-ran it. The outcomes are computed by a breadth-first search over player heights and placed pins, not written in: solo and duo reachability come from the search, and the entry honestly records that its gate-8 prediction was wrong. I also swept the gate height beyond the five stored cases using the sandbox's own function: with partner-targeted pins and the stored limits (jump 3, pin budget 2), gates 2 and 3 leak a solo route, gates 4 to 6 are co-op only (solo false, duo true), and gates 7 to 9 are unsolvable even for two; with a pin budget of 3 the duo band extends to gate 8. That supports the rule's two-edged band and its claim that the budget sets the upper edge. The rule is narrower than the claim's real-world scope, though: the model is a one-dimensional vertical gate with invented constants, the entry itself assumes the model transfers to two-dimensional layouts with horizontal gaps, and the passing solo negative-control tests on the real sweety levels were not re-run here. The claim concerns a real game's levels but was tested against a hand-written model, so the verdict is modeled, not pass. · brain train auto loop 2 pass 3 audit; session_01Kx9Pq1H5qpcbvZJ9u2DPKR

## E14 — sweety switch colour shared across sections
- Date: 2026-10-12
- Project: Pappydapimp69/sweety
- Tags: [gamedev][level-design][state]
- What: In a level built from sections, a switch colour (group 1-4) was global, so holding the first cloud's switch also
  ran a second, same-coloured cloud 70 tiles later; by the time players arrived it had drifted to the far end.
- Why built: Only four switch colours exist (tile letters), so later sections reuse colours already used earlier in a chapter.
- Design: Plates set pressed[g]; doors, bridges and moving platforms read pressed[g] directly.
- Got right: Doors and bridges sharing a colour were harmless: they only matter where a player stands, and earlier ones are
  behind the players.
- Where/why it failed: Movers have hidden state that accumulates while powered (their clock), so a far-away press changes them
  invisibly; the effect only shows up sections later.
- Fix: Movers answer only switches whose position is within 30 tiles of the middle of their path (pressed switches are
  recorded with their x each step); a sim test drives one switch and asserts the far same-coloured mover stays put.
- Why this fix: It keeps four readable colours for players and needs no new tiles; locality matches what players expect.
- Rule of thumb: When switch channels are reused across a level, anything with accumulating state (movers, timers) must answer only
  nearby switches, or presses leak into machines the players have not reached yet.
- Provenance (verified/assumed): verified first-hand: a bot found the second cloud at x 117.7 before the section began; the scoping test
  fails without moverPowered.
- Composed: N/A
- Link: Pappydapimp69/sweety branch ccr-3432c267-04v162; session_01Gs4s9Xnn7DrHixqVcK7JXf

## E13 — sweety stall indicator read after drain
- Date: 2026-10-12
- Project: Pappydapimp69/sweety
- Tags: [networking][ui][state][gamedev]
- What: An online "Waiting for partner" overlay showed on 92% of frames during perfectly smooth lockstep play, because it
  tested "is the next tick ready?" right after the loop had consumed every ready tick.
- Why built: Players must see when the partner stalls (paused, lagging, reading a story card) and not otherwise.
- Design: Each frame runs every tick whose two inputs are known, then sets stall = ready(next) ? 0 : stall + dt and shows the
  overlay past 0.8 s.
- Got right: Thresholding on accumulated stall time rather than on one frame was right; only the predicate was wrong.
- Where/why it failed: The drain loop exits exactly when the next tick is NOT ready, so a post-drain readiness check is false almost every
  frame by construction; the accumulator only reset on the rare frame where a future input had already arrived.
- Fix: Count progress instead: stall resets when this frame ran at least one tick (n > 0) or the next is ready; measured
  0% overlay in two real browsers.
- Why this fix: Progress made is the honest signal of "not waiting"; it is independent of when inputs happen to arrive within a frame.
- Rule of thumb: A "stalled" indicator must test whether work was DONE this frame, never whether more is ready right after a loop that
  drains until nothing is.
- Provenance (verified/assumed): verified first-hand: a reviewer reproduced 92% at 0-100 ms latency; after the fix tests/online.mjs measures 0%/0%.
- Composed: N/A
- Link: Pappydapimp69/sweety branch ccr-3432c267-04v162; session_01Gs4s9Xnn7DrHixqVcK7JXf

## E12 — sweety safe point recorded before hazard check
- Date: 2026-10-12
- Project: Pappydapimp69/sweety
- Tags: [gamedev][state][physics]
- What: A gentle-mode "respawn where you last stood safely" recorded the safe point during movement, before hazards were
  checked in the same step, so the step that killed you also saved the lethal spot: an endless death loop.
- Why built: Gentle mode for a less experienced player: falls and spikes put you back where you stood.
- Design: After landing on solid ground (not a moving platform, head or bridge), store the feet position as safe.
- Got right: Excluding things that can vanish (lantern stones, bridges, platforms) from safe spots was right.
- Where/why it failed: Upside-down Spice's feet were on solid roof while his body was in ceiling spikes; the safe check only
  looked at the floor under the feet, and ran before touch() killed him.
- Fix: Mark a safe candidate during movement and commit it after the hazard pass, only for players still alive.
- Why this fix: "Safe" now means survived this step, which is the property the respawn relies on.
- Rule of thumb: Record a respawn/safe point only after the step's hazard checks, and only if the player survived them.
- Provenance (verified/assumed): verified first-hand: reviewer repro 55 deaths in 20 s; a sim test passes with the fix and fails with
  the old order.
- Composed: N/A
- Link: Pappydapimp69/sweety branch ccr-3432c267-04v162; session_01Gs4s9Xnn7DrHixqVcK7JXf

## E11 — sweety rising hazard checkpoint before trigger
- Date: 2026-10-12
- Project: Pappydapimp69/sweety
- Tags: [gamedev][level-design][state][coop]
- What: A finale flood starts when either player passes its trigger; if the partner was still behind the climb's checkpoint
  flag, every respawn landed below the waterline and drowned again (44 deaths in 90 s, no way out online).
- Why built: A timed climb ahead of rising water, with a "back off on death" rule so a death is never a loop.
- Design: On a death the water drops to (checkpoint y + 1 + grace); checkpoints are flags players touch.
- Got right: Lowering the water relative to the checkpoint was right for anyone who had touched the climb flag.
- Where/why it failed: The rule assumed the active checkpoint is above the hazard's path, but in co-op one player can start the hazard
  while the other's latest checkpoint is an earlier one whose route runs beneath the waterline.
- Fix: When the hazard activates, set the checkpoint to the hazard section's own flag, so every respawn is on the climb.
- Why this fix: The hazard owns its safe point; it no longer depends on who touched which flag.
- Rule of thumb: A timed hazard must set its own checkpoint when it starts; in co-op the partner's last flag can sit on a route the
  hazard covers.
- Provenance (verified/assumed): verified first-hand: reviewer script flood_skip2 went from 44 drownings to 0 and Sugar reached the climb; a sim test
  pins the checkpoint switch.
- Composed: N/A
- Link: Pappydapimp69/sweety branch ccr-3432c267-04v162; session_01Gs4s9Xnn7DrHixqVcK7JXf

## E10 — sweety moving platform rider carry
- Date: 2026-10-12
- Project: Pappydapimp69/sweety
- Tags: [gamedev][physics][state]
- What: Riders on moving one-way platforms in a fixed-step tile platformer: a rider on a
  descending platform lost ground contact every step (gravity from rest is slower than the
  platform), so onGround flickered and jumps were eaten.
- Why built: Clouds, gears and ferries in a co-op platformer must carry a player smoothly
  in any direction, including down, and let them jump at any moment.
- Design: Movers advance first each step (prev and current position kept); players land on
  a platform when their previous bottom was at or above the platform's PREVIOUS top and their
  new bottom reaches its current top; riders get the platform's dx after landing.
- Got right: Testing the one-way landing against the platform's previous y (not its current
  y) is what lets a rising platform scoop the rider up instead of passing through them.
- Where/why it failed: Carrying only dx after the move left vertical motion to gravity, and
  a player falling from rest moves 1/60 tile in the first step while the platform drops
  faster, so the rider hovered for several steps on every descent.
- Fix: Before each player moves, pre-carry riders by the platform's dx and by its dy when dy
  is downward; the normal landing then snaps them back on in the same step.
- Why this fix: It keeps a single source of truth (the platform's own motion) and costs one
  extra moveX/moveY per rider, with no special-cased ground flag.
- Rule of thumb: Carry riders by the platform's full delta BEFORE their own physics, and test
  one-way landings against the platform's previous position, or descents flicker and rises
  tunnel.
- Provenance (verified/assumed): verified first-hand: tests/powers.test.mjs (rider stays on a
  moving platform, carried more than 1.5 tiles) and the clock chapter bot riding gears and a ferry.
- Composed: N/A
- Link: Pappydapimp69/sweety branch ccr-3432c267-04v162, src/sim.js step() ride pre-pass; session_01Gs4s9Xnn7DrHixqVcK7JXf

## E9 — sweety lockstep verify by input tape
- Date: 2026-10-12
- Project: Pappydapimp69/sweety
- Tags: [networking][determinism][testing][gamedev]
- What: Verifying a deterministic-lockstep online mode by letting each peer's scripted bot
  react to its own copy of the world failed: under the 4-tick input delay the reactive bots
  overshot targets and looped, so a whole chapter never finished, though the netcode was right.
- Why built: A browser couch co-op game gained online play (WebRTC data channel via the
  PeerJS public broker, room codes and a ?join= link) on top of its deterministic fixed-step sim.
- Design: Each peer sends only its own player's packed inputs tagged with the tick they apply
  to, DELAY ticks ahead; a tick runs when both inputs are known; every 120 ticks both send an
  FNV-1a fingerprint of the state JSON and the host resends its state on a mismatch.
- Got right: Removing Math.cos and ** from the sim (smoothstep instead) before going online,
  so two browser engines compute bit-identical worlds; a guard test bans transcendentals.
- Where/why it failed: Reactive bots measure the controller, not the netcode: delay changes
  what a closed-loop controller does, so a bot failure under delay says nothing about desync.
- Fix: Record the inputs of a full OFFLINE play-through as a tape (with DELAY idle ticks
  prepended), feed each peer its own column of the tape one entry per scheduled tick, and
  assert both peers finish and both match the offline end fingerprint; same tape in two real
  browsers through the real broker.
- Why this fix: An open-loop tape makes online and offline the same computation, so any
  difference is a netcode or determinism bug; it passed in node with 7+/-9 frame latency and
  in two Chromium profiles, with zero resyncs.
- Rule of thumb: Test lockstep with open-loop input tapes replayed against an offline
  fingerprint, never with closed-loop bots, which react to the delay you are testing.
- Provenance (verified/assumed): verified first-hand: tests/lockstep.test.mjs (garden and
  the 176-wide finale), tests/online.mjs (two browsers, real PeerJS broker), negative
  control with hashes suppressed keeps a divergence.
- Composed: N/A
- Link: Pappydapimp69/sweety branch ccr-3432c267-04v162, src/lockstep.js, src/net.js; session_01Gs4s9Xnn7DrHixqVcK7JXf

## E8 — sweety lift flush with ledge is a wall
- Date: 2026-10-12
- Project: Pappydapimp69/sweety
- Tags: [gamedev][physics][level-design]
- What: A lift whose path ended exactly at a ledge's height left its rider unable to step off: eased motion stops a hair
  below the target, so the rider's body overlapped the ledge's top row and the ledge acted as a wall.
- Why built: A switch on a high ledge runs a lift that carries the partner up beside it.
- Design: Platforms ping-pong between two points with smoothstep easing; riders step off sideways onto tiles.
- Got right: Easing makes the ride gentle; the rider carry and one-way landing worked.
- Where/why it failed: Tile collision treats any overlap of a solid cell as a wall, and a top surface 0.03 tiles low is enough
  to put the rider's feet inside the ledge's top row.
- Fix: End the lift 0.2 tiles ABOVE the ledge top so the rider steps off and drops onto it.
- Why this fix: A small drop is invisible to players and absorbs any easing or float error at the end of travel.
- Rule of thumb: Stop lifts and moving platforms slightly above the surface a rider walks onto, never flush with it.
- Provenance (verified/assumed): verified first-hand: traced the rider stuck at x 87.25 with the lift at 7.03 against a ledge top of 7;
  the toolbox bot passes after the change.
- Composed: N/A
- Link: Pappydapimp69/sweety branch ccr-3432c267-04v162; session_01Gs4s9Xnn7DrHixqVcK7JXf

## E7 — sweety leash correction after respawn
- Date: 2026-10-12
- Project: Pappydapimp69/sweety
- Tags: [gamedev][physics][coop][state]
- What: A co-op leash (max gap 22 tiles) undid the whole overshoot in one moveX; after one player respawned 40 tiles back,
  the other moved 20 tiles in a single step, through walls and over pits, because moveX only checks the end column.
- Why built: A shared camera needs both players within one screen, so moving further apart is blocked.
- Design: After both players move, if the gap exceeds the leash, pull back whoever moved away by the full excess.
- Got right: Blocking only the player who moved away (not both) and skipping the leash while one is dead were right.
- Where/why it failed: A teleport (respawn) can make the gap far larger than one step of movement could, and a correction sized to the gap
  instead of to the step becomes a teleport of its own, through geometry a per-step collision check never samples.
- Fix: Undo at most that player's own movement this step (min(over, |dx|)); the gap then closes by walking.
- Why this fix: The correction can never exceed motion that was already collision-checked, so it cannot cross anything.
- Rule of thumb: Size any constraint correction to the motion that caused it this step, never to the whole violation, or a teleport
  elsewhere turns the correction into a teleport through walls.
- Provenance (verified/assumed): verified first-hand: reviewer repro moved Spice 92.26 -> 72.05 in 1/60 s; after the fix 0.02 tiles; a sim test fails
  with the old pull restored.
- Composed: N/A
- Link: Pappydapimp69/sweety branch ccr-3432c267-04v162; session_01Gs4s9Xnn7DrHixqVcK7JXf

## E6 — sweety fuzz from route states
- Date: 2026-10-12
- Project: Pappydapimp69/sweety
- Tags: [testing][gamedev][physics]
- What: After scripted route bots finished every chapter and two adversarial code reviews found 15 bugs, a seeded
  button-mashing fuzzer with physical invariants (no NaN, nobody inside a solid tile for 30 steps, same seed -> same
  world) still found two collision bugs in seconds: a rider snapped up into a ceiling by a rising head, and a
  gentle-mode respawn putting big Spice into a small-only tunnel.
- Why built: A co-op platformer with stacking, gravity flips, sizes, lifts and respawn rules has state combinations
  nobody scripts on purpose.
- Design: Held directions change every 5-45 steps and buttons are tapped (closer to hands than white noise); 12
  seeds x 6000 steps per level in the suite, 200 seeds in a one-off scan; plus mashing started from every checkpoint
  and from states reached by replaying the route bots part-way (flipped, small/big, riding, mid-puzzle).
- Got right: Invariants are about physics, not goals, so the fuzzer needs no knowledge of the levels; a 30-step
  tolerance ignores legitimate one-frame overlaps (lantern stones appearing, doors).
- Where/why it failed: Route bots only visit the intended path and reviews reason about code paths they think of;
  neither stands on a partner's head under a low ceiling and jumps, or dies big after standing somewhere small.
- Fix: Keep the invariant fuzzer in the pure suite (about 4 s), seed it also from mid-route states, and
  negative-control it by disabling wall collision (every level fails at once).
- Why this fix: It is cheap, deterministic, and finds the bug class (bodies in walls) that ends in soft-locks.
- Rule of thumb: After route bots and reviews, run a seeded mash fuzzer with physical invariants, started from
  mid-route states too; random play alone never gets past the first gate.
- Provenance (verified/assumed): verified first-hand: both bugs reproduced from the fuzz seed, fixed, and each fix's
  targeted test fails with the fix removed; 200-seed and checkpoint/route scans then clean.
- Composed: N/A
- Link: Pappydapimp69/sweety branch ccr-3432c267-04v162, tests/fuzz.test.mjs; session_01Gs4s9Xnn7DrHixqVcK7JXf

## E5 — sweety fixed step jump peak below analytic
- Date: 2026-10-12
- Project: Pappydapimp69/sweety
- Tags: [gamedev][physics][testing]
- What: A platformer tuned to a 3.33-tile jump (v=20, g=60, v*v/2g) peaked at only
  3.17 tiles under the fixed 60 Hz semi-implicit Euler step, so 3-tile rises designed
  "within reach" were unreachable in practice.
- Why built: Level geometry was authored from the analytic jump height so one player
  clears 3-high walls and needs a partner's head for 4-high ones.
- Design: Fixed-step sim (dt 1/60), gravity added to vy before position, ASCII levels
  with integer-row ledges, scripted two-player bots that drive the real sim.
- Got right: Scripted play-through bots ran through every chapter in node and caught it
  before any human played: the bot hit the underside of a stone 3 rows up every time.
- Where/why it failed: Semi-implicit Euler loses about half a step of rise per jump
  (here 0.16 tiles), and a 0.17-tile margin above a ledge leaves almost no airtime to
  move sideways onto it, so a "reachable" 3-row rise was effectively a wall.
- Fix: Measure the real peak in a test (step the sim, track min feet y) and design
  solo rises at 2 rows with the stack-only gate at 4; lowered the launch ledge and the
  crawl hole the same way.
- Why this fix: The test pins the true number the levels depend on, so retuning gravity
  or jump speed later fails loudly instead of silently breaking level reachability.
- Rule of thumb: Design platform rises from the jump height MEASURED in the fixed-step
  sim, not v*v/2g, and leave a margin of at least a third of a tile for sideways travel.
- Provenance (verified/assumed): verified first-hand: measured 3.17 vs 3.33 in the sim,
  bots stuck on 3-row rises and passed after lowering them to 2.
- Composed: N/A
- Link: Pappydapimp69/sweety branch ccr-3432c267-04v162, tests/sim.test.mjs; session_01Gs4s9Xnn7DrHixqVcK7JXf

## E4 — sweety door occupancy snapshot
- Date: 2026-10-12
- Project: Pappydapimp69/sweety
- Tags: [gamedev][state][physics]
- What: A pressure-plate door that "never closes on a player" was implemented as
  "solid unless someone overlaps it", checked inside the collision pass, so a player
  walking INTO a closed door overlapped it mid-move and the door opened for them.
- Why built: Co-op doors must not crush or trap the player standing in the doorway when
  the partner steps off the plate.
- Design: Tile collision asks solidTile(x, y) during moveX; the door rule asked whether
  any player currently overlaps the door cell.
- Got right: The rule itself (hold the door while occupied) is the right player-facing
  behaviour and a test pins it.
- Where/why it failed: The mover's own tentative position is already applied when the
  collision query runs, so "is anyone in the door" is always true for the player
  testing it: an occupancy predicate read during resolution answers about the future.
- Fix: Snapshot occupied door cells once at step start (before anyone moves) and have
  the door read only that snapshot during collision.
- Why this fix: The snapshot is the state the rule is actually about (who was standing
  there), and it is order-independent across players in the same step.
- Rule of thumb: Any "is something here" predicate that changes solidity must read a
  snapshot from before the move, never live positions the collision pass is resolving.
- Provenance (verified/assumed): verified first-hand in review of sim.js and by the
  solo-player negative control that must fail to pass the door.
- Composed: N/A
- Link: Pappydapimp69/sweety branch ccr-3432c267-04v162, src/sim.js heldDoors; session_01Gs4s9Xnn7DrHixqVcK7JXf

## E3 — sweety counted latch for menu taps
- Date: 2026-10-12
- Project: Pappydapimp69/sweety
- Tags: [input][state][gamedev][ui]
- What: A boolean press latch (set on key/pad edge, cleared when the frame reads it) dropped
  menu moves: two quick taps of Down inside one slow frame (headless SwiftShader, ~100 ms)
  latched once, so the cursor moved one row instead of two, intermittently.
- Why built: Menus and gameplay share one input module that latches edges so a tap between
  frames is never lost.
- Design: Per device and action, keydown/pad-poll edges set latch=true; read() returns
  xPressed and clears the latch.
- Got right: Latching (consumer-drained) already fixed the lost-tap-between-frames case.
- Where/why it failed: A boolean collapses N edges to 1; anything that counts presses (menu
  navigation, value steppers) silently loses moves when the frame rate dips, and it shows up
  as a flaky test, not a crash.
- Fix: Store a count per latch (edge -> +1), expose the counts as taps, and have menus move
  by the summed count; gameplay still reads count > 0 as a press.
- Why this fix: It keeps every existing boolean caller working and makes the menu exact at
  any frame rate; the flaky browser test passed 3 runs in a row afterwards.
- Rule of thumb: A consumer-drained latch must COUNT edges, not flag them, wherever the
  consumer acts per press (menus, steppers), or slow frames eat taps.
- Provenance (verified/assumed): verified first-hand: tests/browser.mjs pause-menu check
  failed intermittently (index 1 for 2 downs) and passed consistently after counting.
- Composed: N/A
- Link: Pappydapimp69/sweety branch ccr-3432c267-04v162, src/input.js latch counts; session_01Gs4s9Xnn7DrHixqVcK7JXf

## E2 — sweety coop one way gate strands partner
- Date: 2026-10-12
- Project: Pappydapimp69/sweety
- Tags: [gamedev][level-design][coop]
- What: Five co-op sections shared one shape: a switch on a ledge holds a door below open for the partner, and the ledge
  ends in a one-way drop. If the switch-holder walked off the drop first, the partner was stuck behind the door for good.
- Why built: Classic co-op gate: one climbs (stack, launch, vent, pins), holds the switch, the other walks through.
- Design: Doors open while a plate of their colour is pressed; the plate sits on the ledge; the route continues off the
  ledge's far edge.
- Got right: Earlier sections (a door with a plate on both sides, a relay) were symmetric and could not strand anyone.
- Where/why it failed: Scripted bots only play the intended order, so an out-of-order move (leaving the switch early) was never
  tried; with no hazard in reach, the stuck player cannot even die to respawn. An adversarial reviewer found it.
- Fix: A second plate of the same colour on the far side of every such door, so whoever got through can let the other in;
  plus a pause item that returns both players to the checkpoint, sent as an input so online stays deterministic.
- Why this fix: The far plate removes the trap in-world with no new mechanic; the regroup input is a universal escape hatch.
- Rule of thumb: Every co-op gate must be reopenable from the far side by whoever got through, and every chapter needs a
  both-players "back to checkpoint" that does not depend on dying.
- Provenance (verified/assumed): verified first-hand: reviewer repros in five sections; a sim test strands Sugar beyond door B and shows
  the far switch lets Spice through (and a negative control shows the door stays shut without it).
- Composed: N/A
- Link: Pappydapimp69/sweety branch ccr-3432c267-04v162; session_01Gs4s9Xnn7DrHixqVcK7JXf

## E1 — sweety completability bot worst takeoff
- Date: 2026-10-12
- Project: Pappydapimp69/sweety
- Tags: [gamedev][testing][level-design]
- What: A scripted co-op bot finished a climb in one run and failed the identical jump in the
  next, because earlier phases left the jumper 0.35 tiles further back on a 3-tile step; the
  jump (rise 2, gap 3.5) only worked from the best end of the takeoff span.
- Why built: Bots play every chapter through in node so level edits cannot silently make a
  chapter unfinishable for two humans.
- Design: Phase-scripted bots drive the real sim; each phase walks or jumps toward a target
  and a done-predicate checks arrival.
- Got right: The bot failure surfaced the marginal jump before any human played it; the same
  bots also exposed a head-bump under an overhanging step and a ferry path through a pillar.
- Where/why it failed: A passing play-through proves the jump works from wherever the bot
  happened to stand, not from the whole span a player may jump from, so a jump with near-zero
  margin passes or fails on unrelated upstream drift.
- Fix: Treat an intermittent bot failure on a jump as a level bug: lowered the ledge so the
  jump has slack from anywhere on the step, and kept the bot.
- Why this fix: Humans take off from arbitrary points with arbitrary momentum; slack across
  the span is what makes the jump fair, and the bot then passes deterministically.
- Rule of thumb: A completability bot passing proves one takeoff point; when a jump passes
  or fails on upstream drift, widen the level's margin, do not tune the bot's start.
- Provenance (verified/assumed): verified first-hand: same jump traced from x 162.87 (lands)
  and 162.52 (hits the face) in the sim; passed after the ledge drop.
- Composed: N/A
- Link: Pappydapimp69/sweety branch ccr-3432c267-04v162, tests/phases.mjs homePhases; session_01Gs4s9Xnn7DrHixqVcK7JXf

