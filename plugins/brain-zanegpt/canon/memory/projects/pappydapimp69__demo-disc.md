# pappydapimp69/demo-disc — lessons

Project: pappydapimp69/demo-disc. Newest first.

---

## E53 — scheduled hits outlive their attacker
- Date: 2026-10-17
- Project: Pappydapimp69/Demo-disc
- Tags: [gamedev][state][combat]
- What: In Stonewake Two Hands an enemy attack is a string of hits scheduled at fixed times when the wind-up starts. A
  parry counter that killed the attacker on hit 1 left hit 2 pending, so a dead, invisible wolf still dealt 4 damage.
  Separately, the lesson fight could be won before its lessons ran, skipping them.
- Why built: The string was a list of future events owned by the actor, but only the actor's turn start read its
  liveness; nothing on death touched its pending events.
- Design: Hits resolve in update() when their time comes; the counter damages the attacker inside landHit.
- Got right: Reproduced exactly (1 HP wolf, parry hit 1, leave hit 2 unanswered: party lost 4), then 0 after the fix,
  with a regression check.
- Where/why it failed: Any event scheduled ahead by an entity is a promise made on its behalf; death did not revoke it.
  The same shape appeared in the tutorial: the fight's win condition ran before the lessons scheduled on it.
- Fix: When the counter kills the attacker, mark the rest of its string done; the lesson foe's HP is floored at 30%
  until the break lesson, so the fight cannot end with lessons pending.
- Why this fix: Ending the owner's pending events at the moment it dies is local and cannot miss a future hit type;
  the floor keeps the tutorial on the real rules instead of a scripted foe.
- Rule of thumb: When an entity can die mid-sequence, cancel every event it has scheduled at the moment of death, and
  make any scripted sequence that depends on an entity outlive-proof (floor it until the sequence ends).
- Provenance (verified/assumed): verified first-hand: the 1-HP wolf repro (4 damage before, 0 after) and the robot run that skipped lessons before the HP floor and passed them after.
- Composed: N/A
- Link: https://github.com/Pappydapimp69/Demo-disc/pull/1, commits d65ecec and 5e25158; https://claude.ai/code/session_0189x5cwDWHdyFUT5WmrVCJq

## E52 — new early branch in a handler skips cleanup and declarations
- Date: 2026-10-17
- Project: Pappydapimp69/Demo-disc
- Tags: [javascript][input][gamedev]
- What: Two bugs of one shape shipped in the same Stonewake Two Hands input code and passed the full smoke suite: a
  title-hold cleanup line placed after the pointer handler's existing up/cancel return never ran, and a new mode
  branch inserted at the top of onKey read `left`/`ok` before their const declaration further down (a TDZ
  ReferenceError at the ending choice). A code-review bot (Codex) caught both on the PR.
- Why built: Features were added by prepending early-return branches to long event handlers, without moving the
  handler's own declarations and per-event cleanup above them.
- Design: Each handler ran shared cleanup, then declared helpers, then dispatched by mode with early returns.
- Got right: Reproduced both first with real CDP touches and a key press (one thumb at a time started the demo; Z at the
  choice threw), fixed by moving the cleanup into the up branch and the consts to the top, and added regression checks.
- Where/why it failed: Tests drove the game through the API and simultaneous touches, never a sequential tap-release-tap
  or a key at that one screen, so neither ordering bug was on any tested path.
- Fix: Declarations and per-event bookkeeping go first in the handler, early-return mode branches after them; a
  regression check now covers each path.
- Why this fix: Ordering the handler as declare, clean up, then dispatch makes any new branch safe wherever it is
  inserted; a test per path alone would not stop the next insertion.
- Rule of thumb: When adding an early-return branch to an event handler, put it after the handler's declarations and
  per-event cleanup; check the up/cancel path and every key path the new branch can see.
- Provenance (verified/assumed): verified first-hand: both bugs reproduced in Playwright (demo started from sequential taps; ReferenceError on Z at the choice) and fixed with passing regression checks.
- Composed: pappydapimp69__dog/E9
- Link: https://github.com/Pappydapimp69/Demo-disc/pull/1, commit d65ecec; https://claude.ai/code/session_0189x5cwDWHdyFUT5WmrVCJq

## E51 — lesson arrow and pass test must share one map
- Date: 2026-10-17
- Project: Pappydapimp69/Demo-disc
- Tags: [onboarding][softlock][testing]
- What: In the Stonewake Two Hands pitch, the GUARD lesson's on-screen arrow pointed at STRIKE while the lesson's pass
  test waited for a skill use, so a player following the arrow repeated the lesson forever. Every state-level test
  passed, because the autopilot chose GUARD directly from its own decision table.
- Why built: Each lesson had a pass test (ok) and, separately, a hand-written map from lesson id to the button the
  arrow should point at; a new lesson was added to the first list and not to the second, which defaulted to STRIKE.
- Design: Lessons observe live battle stats and advance when the counter moves; the coach draws a blinking arrow over
  the wanted button, found by name in the live button layout.
- Got right: A real-touch robot that presses only what the screen shows (it reads the button the lesson names and taps
  its drawn box) got stuck in the GUARD lesson for 200 s and exposed the defect the autopilot hid.
- Where/why it failed: Two sources of truth for one lesson (what passes it vs what the arrow shows), and a test player
  that read the game's internal decision instead of the screen.
- Fix: Added the missing ids to the arrow map, and made every hero lesson move on after three wrong presses with an
  AGAIN hint ("tap where the arrow is"), so no future mismatch can strand a player; a smoke check asserts it.
- Why this fix: The escape bounds the cost of any future arrow/pass mismatch to three turns, and the robot run catches
  the mismatch itself; neither depends on remembering to update two lists.
- Rule of thumb: Derive a tutorial's pointer and its pass test from one table, give every step an N-wrong-tries escape,
  and test it with a player that presses only what is drawn, not the autopilot's own choice.
- Provenance (verified/assumed): verified first-hand: the robot stalled 200 s in the GUARD lesson before the fix and passed it after; the three-press escape has a smoke check.
- Composed: pappydapimp69__seven/E21
- Link: https://claude.ai/code/session_0189x5cwDWHdyFUT5WmrVCJq, Demo-disc commit 9859c0a

## E50 — audit the pitch against the whole original
- Date: 2026-10-17
- Project: Pappydapimp69/Demo-disc
- Tags: [pitch][process][gamedesign]
- What: The Stonewake Two Hands playable pitch shipped three times with whole systems of the original game missing,
  and each gap surfaced only when the owner asked: magic and items, then a tutorial, then (on a self-audit forced by
  the owner's "strike one") the map walk with the two-thumb stick, the second ending and two heroes' skills.
- Why built: The pitch was built outward from the new combat feature, so anything the feature did not touch never
  entered the checklist, and the owner had to supply the questions the agent should have asked itself.
- Design: The fix was a feature inventory of the ORIGINAL game (map, chests, campfire, four heroes and their skills,
  items, gear, optional fight, both endings, boss tricks) checked against the pitch flow line by line, each gap
  filled and each new step pinned to a real game event with a test of the full lesson order.
- Got right: The audit found three real gaps at once, and a real-touch robot run exposed a fourth (the GUARD lesson
  arrow pointed at STRIKE, so a player could repeat it forever), fixed with a three-strikes escape on every lesson.
- Where/why it failed: Each round answered only the latest message. Nothing compared the pitch to the original
  feature list, so missing systems looked like "not asked for" instead of "missing".
- Fix: Before presenting any rework or pitch of an existing product, list the original's features and check every
  one against the new build; then drive the full flow with a robot that presses only what a player can see.
- Why this fix: A feature list is cheap and turns silent omissions into a visible table; the robot catches flow
  traps (soft-locks, wrong arrows) that state-level tests pass straight through.
- Rule of thumb: When reworking or pitching an existing game, audit the new build against the original's full
  feature list before showing it; never let the owner be the one to find a missing system.
- Provenance (verified/assumed): verified first-hand in this session: three owner prompts each exposed a missing system, the self-audit found three more, and the robot run found the GUARD soft-lock.
- Composed: pappydapimp69__dog/E23
- Link: https://claude.ai/code/session_0189x5cwDWHdyFUT5WmrVCJq, Demo-disc commit 9859c0a

## E49 — a stat that only acts in contact is free points in a solo budget
- Date: 2026-10-17
- Project: pappydapimp69/Demo-disc
- Tags: [gamedesign][balance][racing]
- What: Kart-racer roster with zero-sum stat points over speed, accel, handling, grip and weight, checked
  by AI time trials of all 24 character and vehicle combos on all three tracks.
- Why built: Brain's balance lessons warn that options along one power axis collapse to a dominant pick,
  so each line had to be a trade-off; the time trials were the check.
- Design: Each combo drove 3 laps solo on each track with the same AI; I compared each to the best per
  track and asked whether one combo was fastest everywhere.
- Got right: Running all three tracks, not one: the first pass showed one combo (BEN on the go-kart)
  fastest on all three, which a single-track check would have called a track quirk.
- Where/why it failed: Weight was in the zero-sum budget but only acts in bumps, which a solo time trial
  never has, so light combos spent weight points for free speed elsewhere and dominated the trials.
- Fix: Took weight out of the budget (kept as flavour for bumps) and rebalanced the rest; after that the
  fastest combo differed by track and all 24 three-track totals sat within 12 percent.
- Why this fix: A budget only balances stats that the measurement values; a stat whose effect needs an
  interaction the measurement lacks is free in it, and players optimising solo times will find that too.
- Rule of thumb: Before balancing a stat budget, check that every stat in it can cost or win something in
  the measurement you balance against; leave the rest out of the budget or measure the interaction.
- Provenance (verified/assumed): Verified first-hand: 72 time trials before and after with the shipped
  game's AI and physics; the time trials are a proxy for human driving, named as such.
- Composed: N/A
- Link: games/trolleydash/game.js CHARS/VEHS; session_011p52L2CkFXcsYRwjDu6tG9

## E48 — shortcut value must be measured with and without boost
- Date: 2026-10-17
- Project: pappydapimp69/Demo-disc
- Tags: [gamedesign][racing][level-design]
- What: Six kart-track shortcuts (three narrow road alleys, three off-road cuts) timed from 40 samples
  before each entry to just past its exit, on the main line and through the cut, with and without a boost.
- Why built: The design intent was alleys that save about a second for a narrow risk, and off-road cuts
  that only pay with a boost; guessed geometry gave a 2.6 s alley and cuts no better than boosting on road.
- Design: A test hook drives a solo kart with the same AI and physics at three lanes; four modes per
  shortcut (main, cut, main+boost, cut+boost); the shipped test asserts the intended sign of each gap.
- Got right: Measuring both boosted modes: a cut's value is cut+boost against main+boost, not against the
  plain main line, because the boost also speeds the main line; final gaps 0.4 to 1.7 s with a boost.
- Where/why it failed: First layouts: one alley saved 2.6 s (a dominant line), one skipped 672 units (past
  the lap counter's limit), and boosting into a cut was slower because the AI kept a drift through the exit.
- Fix: Reshaped each shortcut against the measurement until alleys save 0.9 to 1.1 s, off-road cuts lose
  0.1 to 0.9 s unboosted and gain with a boost, and every skip stays under the counter's 600-unit limit.
- Why this fix: The risk/reward of a shortcut is a relation between four times; only measuring all four on
  the real geometry shows whether it is dominant, useless, or a real choice.
- Rule of thumb: Judge an off-road shortcut by cut-with-boost against main-with-boost; a cut that only beats
  the plain main line is a trap, and one that beats both unboosted is a new main line.
- Provenance (verified/assumed): Verified first-hand: timed with the shipped game's own AI and physics at
  three lanes; the asserting test is in the smoke suite.
- Composed: N/A
- Link: games/trolleydash/game.js timeShortcut; session_011p52L2CkFXcsYRwjDu6tG9

## E47 — backing over the line must uncount the lap
- Date: 2026-10-17
- Project: pappydapimp69/Demo-disc
- Tags: [gamedev][racing][state]
- What: Lap counting for a kart racer where progress = laps x track length + distance along the
  centreline, and a stuck detector rescues any kart whose progress does not beat its best for 3 s.
- Why built: Trolley Dash needs laps that count only through checkpoints, shortcuts that may jump ahead,
  and a rescue for karts pinned by items or walls.
- Design: Lap++ when the distance wraps forward with both checkpoints crossed; the rescue compares current
  progress with the best ever seen, so it keeps progress and only fixes placement.
- Got right: A 36-race sweep with full logging of each rescue (track position, terrain, speed, route) is
  what found it; the per-kart trace showed best progress one lap ahead of current progress.
- Where/why it failed: A kart bumped backwards over the line after its lap counted lost a full lap of
  progress (s wrapped from 10 to 4125 with lap unchanged), so the stuck detector fired every 3 s for a
  whole lap: 12 rescues for one kart, 26 to 47 karts unfinished over 36 races with the related bugs.
- Fix: Backing over the line un-counts the lap and re-arms the checkpoints, so driving forward over it
  counts the lap again; progress is then continuous in both directions.
- Why this fix: Progress must be monotonic in position, not in time: any counter that only increments
  turns a small backward step across a boundary into a jump of one whole period.
- Rule of thumb: A wrapped coordinate needs symmetric boundary handling: decrement on a backward crossing
  exactly as you increment on a forward one, or a 1-unit reverse becomes a 1-lap loss.
- Provenance (verified/assumed): Verified first-hand: traced in the shipped game; after this and two
  related fixes the same 36-race sweep had 2 unfinished karts (from 47) and 49 rescues (from 94).
- Composed: N/A
- Link: games/trolleydash/game.js track(); session_011p52L2CkFXcsYRwjDu6tG9

## E46 — racing ai must drift into the corner not its steering
- Date: 2026-10-17
- Project: pappydapimp69/Demo-disc
- Tags: [gamedev][ai][racing]
- What: Kart-racer AI that steers at a lookahead point on the centreline and starts a drift when a bend is
  coming; its drift direction was taken from the sign of its current steering error.
- Why built: Trolley Dash's AI shares the player's stepKart (drift locks a turn direction and lowers grip),
  so AI drifting had to choose a direction the same way a player commits to one.
- Design: Profiled one AI kart for 30 s on the real track (terrain share, average speed, wall hits) and a
  full 8-kart race, comparing drift logic variants on the same seed.
- Got right: Profiling on the real track, not a test field: it showed the AI on grass 52 percent of the time
  with 9 to 23 wall hits per 30 s, while a no-drift AI was on grass 10 percent with 0 walls and finished.
- Where/why it failed: Steering error often points the other way at corner entry (still correcting the last
  bend), so the drift locked the wrong direction and held it for the whole corner, sliding off the road.
- Fix: Take the drift direction from the bend ahead (heading change between now and the lookahead point),
  start only when the steering agrees and the bend is a hairpin, end it when the bend straightens.
- Why this fix: A drift is a commitment for the whole corner, so it must be chosen from the corner's
  geometry; the steering error is a short-term correction signal and flips sign at corner entry.
- Rule of thumb: When an AI enters a committed manoeuvre (a drift, a jump, a lane change), pick its
  direction from the path ahead, not from the instantaneous control error.
- Provenance (verified/assumed): Verified first-hand: same-seed profiles of the shipped game, numbers
  above; final AI averaged 113 units/s, 14 percent grass, 0 walls, all 8 karts finished.
- Composed: N/A
- Link: games/trolleydash/game.js aiInput; session_011p52L2CkFXcsYRwjDu6tG9

## E45 — pitch a feel change as a playable demo
- Date: 2026-10-17
- Project: Pappydapimp69/Demo-disc
- Tags: [pitch][gamedesign][onboarding]
- What: The first pitch for Stonewake's two-thumb combat was a doc page holding a 38 s screen recording of the
  prototype, charts and a roadmap. The owner rejected it as weak and asked for a real demo. The second pitch was
  the game itself: hold both thumbs to begin, one fight that teaches each verb by doing it, the titan finale,
  then an end card with the player's own numbers and the plan. Left alone, it plays itself with ghost thumbs.
- Why built: A change to how a game FEELS under the thumbs cannot be judged by watching it. The reader has to
  have their hands on it, and the first page must ask for the very thing the pitch is about.
- Design: Each lesson observes the live battle stats (block, parry, actions, strings, skills, breaks) and advances
  when its counter moves, so the tutorial runs on the real rules. Foe-turn lessons slow time and repeat with an
  AGAIN line until passed. The end card reads the totals the player just produced. Attract mode reuses the
  autopilot and draws a fingertip wherever it pressed.
- Got right: One flow serves three readers: the hands-on player, the watcher (attract mode) and the test suite.
  The watch-mode test asserts the lesson order block>parry>strike>string>skill>break and reaching the card, and a
  real-touch run (CDP multi-touch on an emulated phone) completed it in about 100 s.
- Where/why it failed: The recorded film shrank pixel art to a small box, separated the evidence from any way to
  feel it, and spent its words on charts. The playable build sat at the bottom of the page behind the film.
- Fix: Make the artifact page the game itself, full screen. Put the pitch content on the in-game end card (your
  numbers, old vs new taps, five milestones) and a one-line note beside the canvas on desktop.
- Why this fix: The proof becomes the reader's own play, and their own stats land in the same moment as the plan,
  so nothing has to be taken on trust. One code path means the pitch cannot drift from the build.
- Rule of thumb: Pitch a feel or controls change as a playable demo whose first screen demands the new input,
  teaches by doing on the real rules, and ends on the player's own numbers. A film of it reads as weak.
- Provenance (verified/assumed): verified first-hand: the owner's rejection of the film pitch, the watch-mode and two-thumb-hold smoke checks, and the real-touch run to the end card.
- Composed: pappydapimp69__the-game-prologue/E15, pappydapimp69__dog/E95
- Link: https://claude.ai/code/session_0189x5cwDWHdyFUT5WmrVCJq, Demo-disc commits 3769b3f and d411324

## E44 — rate change must redraw the next arrival gap
- Date: 2026-10-17
- Project: pappydapimp69/Demo-disc
- Tags: [simulation][determinism][testing]
- What: Added a timed surge to an arrival process that draws exponential gaps; the surge produced no extra
  people at all, and the first fix silently changed every other level's arrivals.
- Why built: GOING UP's LUNCH BELL needed a time-varying arrival rate on top of the existing Poisson
  arrivals (next gap drawn from the rate in force when the previous person arrived).
- Design: rate = surge rate inside the bell window, base rate otherwise; the fix redraws the pending gap
  whenever the in-window flag changes.
- Got right: A gap drawn at the quiet rate (about 3 s) sailed straight past a 10 to 15 s window; redrawing
  on the change brought 48 people in the 15 s window after 11 in the 45 s before.
- Where/why it failed: The change detector compared a flag that returned undefined (a && chain on levels
  without a bell) with false, so it fired every frame and redrew the gap on all levels, shifting results.
- Fix: Make the window test return a strict boolean, so the change detector only fires on real changes;
  an unrelated zoning test (longest wait 26 vs 40 s) caught the drift.
- Why this fix: Change detection is only as good as the equality it uses; a value that is sometimes
  undefined never equals its stored copy and turns an edge trigger into a per-frame one.
- Rule of thumb: When an arrival rate changes, redraw the pending gap at the new rate, and compare strict
  booleans in any edge trigger; keep a seeded regression test on an unrelated level to catch drift.
- Provenance (verified/assumed): Verified first-hand: traces of the shipped game before and after, and the
  zoning regression test that failed then passed.
- Composed: N/A
- Link: games/goingup/game.js people(); session_011p52L2CkFXcsYRwjDu6tG9

## E43 — pre positioning lifts does not help a one way surge
- Date: 2026-10-17
- Project: pappydapimp69/Demo-disc
- Tags: [elevator][dispatch][gamedesign]
- What: Planned a GOING UP day where a known lunch surge (upper floors to the lobby) rewards parking lifts
  in position before it starts; measured sweep and zoned dispatch with and without parking first.
- Why built: The milestone plan assumed that knowing when a spike comes makes pre-positioning valuable,
  which would have been the day's lesson on screen.
- Design: Two lifts, ten floors, base 0.35 people/s, then 3 people/s from floors 3-9 to the lobby for 15 s;
  parks at (9,6), (9,9) or (6,3) set 10 s before the bell and released after it.
- Got right: Measured before writing the tip: sweep without parking had the best longest wait (21 s);
  every parking pattern was worse (24 to 30 s), and zoned dispatch was worse again.
- Where/why it failed: Parking did not help because the surge is a carrying problem: every rider goes to
  the lobby, so lifts parked high wait for the first calls and then make the same full trips down.
- Fix: Shipped the day with an honest tip (waiting in position does not help, carrying does) and kept
  parking as a tool for up-peak days, where lifts waiting at the lobby do save time.
- Why this fix: A tip that teaches a measured falsehood would mislead players exactly where the game claims
  to be about the real problem; the measurement decides the copy.
- Rule of thumb: Pre-positioning pays when response time is the bottleneck; in a one-direction surge where
  capacity is the bottleneck, keep the cars moving instead.
- Provenance (verified/assumed): Verified first-hand with the shipped game's seeded simulation, numbers
  above; a separate bug (arrival gaps drawn at the quiet rate skipped the surge) was fixed first.
- Composed: demo-disc/E15, ideas:ELEVATOR-CONTROL/dispatch/nearest-first-starves-the-far-floor
- Prediction: Written before the first run: parking two lifts on the upper floors before the bell would
  cut the longest wait by a third.
- Observed: No parking 21 s longest wait; parking (9,6) 28 s, (9,9) 30 s, (6,3) 24 s. Refuted.
- Scenarios: sweep and zoned, each with no parking and three parking patterns; (9,9) built to break it.
- Link: games/goingup/game.js LUNCH BELL; session_011p52L2CkFXcsYRwjDu6tG9

## E42 — patient queues need fewer servers than square root staffing
- Date: 2026-10-17
- Project: pappydapimp69/Demo-disc
- Tags: [queueing][staffing][gamedesign]
- What: LOBBY's SEASON 2 shift lets the player rent servers (each costs 3 happy players) for a stream of
  4-player lobbies with an offered load of about 5.5 busy servers; I measured net score for 2 to 9 servers.
- Why built: I planned to teach the square-root staffing rule (load + beta x root(load), about 8 here) as
  the in-game answer, and checked it against the game's own simulation before putting it on screen.
- Design: The smart autopilot played the same seeded 60 s shift once per server count; net = happy players
  minus rent; players wait up to 24 to 42 s before quitting, and a match runs 12 s.
- Got right: Measuring before teaching: the net curve was 2:34, 3:51, 4:68, 5:81, 6:82, 7:79, 8:76, 9:73,
  peaking at 6 (load plus about one), so the screen now says rent about the load plus one.
- Where/why it failed: The square-root rule's 8 servers overshot by two: it sizes for a short wait target,
  but these players tolerate 24 to 42 s, so the queue absorbs bursts and extra servers only cost rent.
- Fix: Size servers from the actual tolerance: with long patience run near the load (load + 0.5 to 1.5);
  use load + beta x root(load) only when the wait target is short relative to the service time.
- Why this fix: Square-root staffing is derived for a probability-of-waiting target; when abandonment only
  starts after several service times, utilisation can run high before anyone leaves.
- Rule of thumb: Before staffing by load + root(load), check how long customers will actually wait; patient
  queues are cheapest at about the load plus one server.
- Provenance (verified/assumed): Verified first-hand: eight seeded runs of the shipped game's simulation,
  numbers above; the beta value is from the existing staffing lesson, not re-derived here.
- Composed: local__sandbox-kernel-queueing-theory/E1
- Prediction: Written before the first run: the best net would land at the square-root rule's 8 servers.
- Observed: Best net 82 at 6 servers (81 at 5, 76 at 8, 34 at 2); prediction refuted by two servers.
- Scenarios: server counts 2, 3, 4, 5, 6, 7, 8, 9 on one seeded shift; 2 servers built to break it.
- Link: games/lobby/game.js SEASON 2; session_011p52L2CkFXcsYRwjDu6tG9

## E41 — second thumb needs a choice and a lockout
- Date: 2026-10-17
- Project: Pappydapimp69/Demo-disc
- Tags: [gamedesign][input][mobile]
- What: Stonewake Two Hands moved a turn-based RPG's defense from one tap anywhere to two thumb pads:
  heavy hits must be BLOCKED with the left pad, swift hits can be PARRIED with the right pad for no damage
  plus a counter, and parrying a heavy is punished. A tap before the timing window locks that pad until the hit lands.
- Why built: The owner asked for two-thumb portrait combat with more depth. A second thumb that only
  duplicates the first adds input surface (Brain T13) without adding a decision.
- Design: Each enemy action is a string of hits marked heavy or swift. The ring closes on the pad the hit
  wants. The safe answer (block) works on everything, and the greedy answer (parry) works only on swift hits
  with a tighter window (75 ms vs 130 ms) and pays out WAKE and break. Bots with human timing spread
  (sd 35-100 ms), a 10% colour misread rate and a both-pads masher were run 100 boss fights each.
- Got right: Skill separated in order. Win rate / lowest HP: sharp 100%/0.84, average-parry 100%/0.62,
  average-block-only 99%/0.43, casual 81%/0.11, masher 23%/0.02, no defense 0%/0. Parrying beat
  block-only even with a 1-in-10 misread.
- Where/why it failed: Without the early-press lockout, alternating presses on both pads every 90 ms
  would land inside every window and beat honest play. The first balance pass also let a 4-member party
  finish late bosses in 2 rounds, so the defense never mattered.
- Fix: A per-hand lockout on early taps (pressing before the window disables that pad until the hit lands)
  made the masher the second-worst profile. Bosses now scale HP by 1+0.25(n-1) and attack by 1+0.12(n-1)
  with party size n, which brought late fights back to 5-9 rounds.
- Why this fix: The lockout prices a wrong guess on the pad that was pressed, so it punishes mashing
  without shrinking the window for an honest early-but-close press. Party-size scaling keeps the boss's
  output growing with the party, which acting twice alone does not (demo-disc E33).
- Rule of thumb: Give a second thumb a decision (which pad, safe vs greedy), not a copy of the first.
  Lock out a pad on early presses or mashing both beats skill. Check it with a masher bot and a misread bot.
- Provenance (verified/assumed): verified first-hand by the Playwright sims and smoke checks quoted above. The human timing spreads are modeled from bots; real-player rates are a separate open item.
- Composed: pappydapimp69__demo-disc/E32, pappydapimp69__demo-disc/E33, pappydapimp69__mirage/E26, ideas:RPG/combat/ki-blast-deflect
- Link: https://claude.ai/code/session_0189x5cwDWHdyFUT5WmrVCJq, Demo-disc commit d8c9970

## E40 — recorded video drifts from wall clock
- Date: 2026-10-17
- Project: Pappydapimp69/Demo-disc
- Tags: [film][tooling][testing]
- What: A pitch film was recorded with Playwright recordVideo while a script drove real CDP touch events and
  logged a wall-clock timestamp for each beat (battle start, parry, block). The plan was to cut the film by
  those log times.
- Why built: Cutting the film from the robot's own event log looked faster and more exact than scrubbing
  the footage by eye.
- Design: The log started after page load, and the video started when the page opened, so a fixed offset
  was expected and measured once, at the first battle flash.
- Got right: Measuring the offset from a visible event (the full-screen white flash at battle start, found
  by frame brightness) gave a true anchor of about +3 s at 16 s.
- Where/why it failed: The offset was not constant. It grew from about +3 s at 16 s to about +12 s by the end
  of a 100 s recording, because the encoder's timestamps lag under load. Cuts placed by log time near the end
  landed on the wrong moments.
- Fix: Build 1 fps contact sheets with timestamps (ffmpeg fps=1 then a PIL grid). Pick every cut from the
  frames, then re-sample the cut film at 2 fps to place captions.
- Why this fix: Contact sheets read the video's own clock, so drift cannot move a cut. They also show
  idle stretches to trim, which a log of events does not.
- Rule of thumb: Never cut a Playwright screen recording by wall-clock log times; its clock drifts under
  load (+3 s to +12 s over 100 s here). Find cuts on the frames themselves with a contact sheet.
- Provenance (verified/assumed): verified first-hand: offset measured by frame brightness at the first flash and by the victory panel at the end of the same recording.
- Composed: N/A
- Link: https://claude.ai/code/session_0189x5cwDWHdyFUT5WmrVCJq

## E39 — faro two card goals mostly unreachable
- Date: 2026-10-17
- Project: pappydapimp69/Demo-disc
- Tags: [card-magic][permutation][exhaustive]
- What: Added a FARO hand that asks the player to put two cards into two slots with one shuffle sequence;
  my first goal (ace to 7, last card to 4 in a 16-card deck) had no solution and the par solver crashed.
- Why built: A two-card goal is the natural next step after single-card binary placement, but faros move
  every card at once, so a pair's positions are one joint state that the shuffles may never reach.
- Design: Exhaustive BFS over the tuple of the goal cards' positions under IN and OUT faros, used both as
  the in-game par solver and in a sandbox over 8, 16 and 52-card decks.
- Got right: Searching the position tuple, not the whole deck, keeps the solver tiny (at most n^2 states)
  and gives the exact par; FARO's two-card hand ships with par 5 from that search.
- Where/why it failed: In power-of-two decks almost nothing is reachable: cards 0 and 5 reach 32 of 240
  joint positions in 16 cards (24 of 56 in 8), and the top and bottom cards always mirror each other.
- Fix: Pick multi-card goals from the reachable set (run the BFS, choose a state at the depth you want)
  instead of choosing slots by hand; 52 cards are forgiving (2600 of 2652 reachable) but still not total.
- Why this fix: The faro group on a 2^k deck is small (order k shuffles), so hand-picked targets are
  unreachable most of the time; generating goals from the search makes every hand solvable by design.
- Rule of thumb: When one move transforms every piece at once, a goal for several pieces is one joint
  state; generate it from the reachable set, never pick it by hand.
- Provenance (verified/assumed): Verified first-hand: the shipped game's par solver hit an unreachable
  goal, and the sandbox enumerated every joint state for 8, 16 and 52 cards.
- Composed: zanegpt/E11
- Sandbox: sandboxes/2026-10-17__faro-two-card-goals-mostly-unreachable.py
- Prediction: Written before the first run: in a 16-card deck over half of the 240 ordered position pairs
  would be reachable for a given card pair, with only the top/bottom pair special.
- Observed: RESULT: PASS two-card faro goals: 16 cards reach only 32/240 joint positions, 52 cards
  2600/2652; top and bottom always mirror (sum n-1). The prediction was refuted for power-of-two decks.
- Scenarios: 8-card, 16-card and 52-card decks, each for the top/bottom pair (built to BREAK it, the
  mirrored pair) and for cards 0 and 5.
- Link: games/faro/game.js planMulti; session_011p52L2CkFXcsYRwjDu6tG9
- Cited-by: 2026-10-19 · projects/pappydapimp69__brainwork.md#E483 · compatible · sandboxes/2026-10-19__hanoi-bfs-optimum-vs-formula-and-heuristic.py · observed RESULT: PASS BFS matched 2^n-1 for 3 pegs (n=1..8) and the Frame-Stewart recursion for 4 pegs (n=1..7, optimum 25 at n=7); all pegs^n states reachable; applying the 3-peg formula to 4 pegs overstates the optimum at n=[3, 4, 5, 6, 7] (127 v… · brain train auto loop 2 pass 6; session_01Xs9BRpt5ZfygjApJGsbMEk

## E38 — particle liquid tunneling and crust
- Date: 2026-10-15
- Project: Pappydapimp69/demo-disc
- Tags: [gamedev][physics][simulation][testing]
- What: A browser pin-pull puzzle simulates water, lava, gold and stone as radius-7 particles, with lava + water ->
  stone and lava + gold -> melted gold. Its completability test (play each level's stated solution, require a win)
  failed on 2 of 3 levels for three separate physics reasons, none visible in a casual play-through.
- Why built: Real-liquid pin puzzles need the reaction order to matter, so the levels depend on water reaching every
  lava particle before the gold falls.
- Design: Position-based particles with gravity, rect collision push-out, spatial-hash pair separation, and reactions
  applied on contact. Each level declares a solution and its traps, and the test steps the simulation directly
  through a test hook with no real-time waits.
- Got right: The completability test caught all three faults and pinned each to a number, so every fix was verified
  the same way (all 3 levels: solution wins, every trap loses, the auto-solving hint wins).
- Where/why it failed: (1) Tunneling: falling at up to 900 px/s is 15 px per tick, more than the particle radius, so
  water passed through 10-12 px walls and pins and left the world (42 water became 7 with no drain open). (2) Crust:
  freezing stone in place on reaction formed a skin between the remaining water and lava, and the reaction stalled
  with exposed lava left (12 lava in the pool). (3) Settle check: particles resting in a position-based stack keep a
  residual velocity from gravity each tick, so a "max speed under 40" settle test never fired and the knight never
  moved.
- Fix: Cap each velocity component below one radius per tick (400 px/s at 60 Hz, 6.7 px). Make stone a dynamic
  heavy granular particle, and add a density swap (stone and gold 3, lava 2, water 1; a heavier particle resting on
  a lighter one trades places) so stone sinks out and fresh lava keeps meeting water. Replace the settle test with time
  since the triggering pin was pulled.
- Why this fix: Substepping costs a multiple of the frame time, and the cap is one clamp. Buoyancy by position swap
  keeps the reaction front fresh without a pressure solver. A time-based trigger is deterministic where the
  velocity-based one depended on solver residue.
- Rule of thumb: In a particle-liquid puzzle, cap speed under one radius per tick or liquid tunnels through thin
  walls. Make reaction products sink by density rather than freezing in place, or they seal off the reaction. Never
  use max particle speed as a "settled" signal in a position-based stack. Prove each level with a stepped
  completability test.
- Provenance (verified/assumed): Verified first-hand: water fell 42 to 7 through walls before the cap and was kept
  after, pool lava stalled at 12 with frozen stone and reached 0 with density swap plus relayout, the settle counter
  stayed 0 across 720 ticks, and the final run printed ALL PASS (26 checks).
- Composed: N/A
- Link: session https://claude.ai/code/session_0169rjPqYDYawkbeTUEzoNKo (demo-disc/games/only1/game.js, tests/smoke.mjs)
- Cited-by: 2026-10-15 · projects/local__win-only-level-test-passes-tunnelling-run.md#E1 · compatible · sandboxes/2026-10-15__win-only-level-test-passes-a-run-where-12-of-40-particles-tunnelled.py · observed RESULT: PASS 3/3; fixed 60 won=True tunnelled=0 basin=40; 30fps won=True tunnelled=0; 20fps won=True tunnelled=12 basin=28; 12fps won=False tunnelled=17 basin=23 (12 fps lost, refuting part of my prediction) · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 1 pass 2 (edge demo-disc + brain), 2026-10-15
- Cited-by: 2026-10-15 · projects/pappydapimp69__zanegpt.md#E16 · compatible · sandboxes/2026-10-15__pin-puzzle-speed-cap-only-stops-tunneling-under-a-fixed-step-accumulator.py · observed iteration 1 RESULT: FAIL (hitch 0/100: it fell after the crossing). Iteration 2 RESULT: PASS cap holds at fixed 60 Hz (0) and under the accumulator (0, 0) but raw 30 fps tunnels 33/100 and one 1/20 s hitch 167/1000 when swept over its posi… · https://claude.ai/code/session_01TQvFfNiYzpWZZDPgWeMoBC (brain train auto pass 2)
- Cited-by: 2026-10-15 · projects/local__particle-speed-cap-per-tick-fixed-step.md#E1 · compatible · sandboxes/2026-10-15__particle-speed-cap-is-per-tick-and-only-guards-a-fixed-step.py · observed RESULT: PASS 4/4; fixed+accumulator clean at all rates; variable dt: 30fps (True, False), 10fps (True, False), hitch (True, False) (tunnelled, exploded) - no explosion anywhere, the cap clamps it · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto loop 3 pass 2 (edge demo-disc + brain), 2026-10-15

## E37 — juice ab identical mechanics
- Date: 2026-10-15
- Project: Pappydapimp69/demo-disc
- Tags: [experiment][gamedesign][determinism]
- What: Pop It, a bubble arcade that switches juice (hit-stop, screen shake, particles, climbing pop pitch, squash)
  on or off per round from a shuffled balanced block, to test whether game feel changes how real players play.
- Why built: tension T9 says a headless sim proves systems but not feel; a human A/B is only clean if the juice arm
  changes feedback and nothing the score depends on.
- Design: gameplay spawns from one seeded stream, all cosmetic randomness (particles, shake offsets) from a second
  stream; hit-stop freezes the entire simulation including the round clock and the reaction timer.
- Got right: an autopilot acting in simulation time gives byte-identical results under the same seed: 4190 points,
  93 popped, 0 escaped with juice on and off, while hit-stop ticks were 279 vs 0.
- Where/why it failed: hit-stop by definition pauses play, which hands a human extra wall-clock aiming time per pop,
  so juice-on rounds are slightly easier for people even though identical in game time.
- Fix: freeze the round clock with the hit-stop (game time per round stays equal), keep it to 3 ticks, and log the
  total stopped ticks per round so the analysis can control for the extra wall time.
- Why this fix: removing hit-stop would remove part of the treatment being tested; logging it keeps the treatment
  intact and the confound measurable.
- Rule of thumb: Before a human juice A/B, prove the arm is feedback-only: same seed plus same timed inputs must give
  the same score with juice on and off (cosmetics on their own stream); log hit-stop time, since it adds wall time.
- Provenance (verified/assumed): verified first-hand by the shipped smoke test (identical 4190/93/0 on and off);
  the size of the hit-stop wall-time effect on humans is unmeasured until players send data.
- Composed: demo-disc/E14
- Link: session https://claude.ai/code/session_0165jfQbaW5xxNCE9kqoELSQ, commit e4e4a0c (Pappydapimp69/Demo-disc)

## E36 — equal budget cap must bind
- Date: 2026-10-15
- Project: Pappydapimp69/demo-disc
- Tags: [experiment][memorization][testing]
- What: IQ Test 2026, a Leitner-box learning game that assigns each real player one miss rule (reset to box 1 vs
  drop one box) to compare them "at equal review budget", with a daily cap on reviews.
- Why built: Brain's open tension asks which Leitner miss rule wins for real learners; the toy model compared them
  at equal review budget, so the human version had to hold effort equal too.
- Design: 12 cards, 4 new per day, intervals 1/2/4/8/16 days, due cards lowest box first up to a daily cap, cold
  tests on day 7/14/28 before that day's reviews; a simulated forgetting learner drove 30 days per rule.
- Got right: logging the backlog (due beyond the cap) per session made it visible whether the cap ever acted, and
  every missed review was checked to move by its arm's rule.
- Where/why it failed: the first cap (16 a day) never bound: peak due was 9, backlog 0 every day, so the cap was
  decorative and the reset arm would simply have bought extra reviews, an unequal-effort comparison.
- Fix: cap lowered to 6; the backlog went to 3, 2, 3 on days 3-5 (the heavy early days) for both arms, so the
  budget now actually rations work, and the session log records the backlog.
- Why this fix: equal effort is only enforced where the constraint is active; measuring backlog proves it is, and
  the cap stays above the steady-state load so it does not starve late days.
- Rule of thumb: An "equal budget" experiment arm is only equal where the cap binds: simulate the load first and log
  the overflow (due beyond the cap) per session; a 16-cap with peak load 9 bound 0 days, a 6-cap bound days 3-5.
- Provenance (verified/assumed): verified first-hand in a headless run of the shipped game (30 simulated days per
  rule, backlog strings logged); how often the cap binds for real players is the open part, measured by the game itself.
- Composed: N/A
- Link: session https://claude.ai/code/session_0165jfQbaW5xxNCE9kqoELSQ, commit e4e4a0c (Pappydapimp69/Demo-disc)

## E35 — ceiling check before human ab
- Date: 2026-10-15
- Project: Pappydapimp69/demo-disc
- Tags: [experiment][balance][testing]
- What: tuning Pop It's difficulty before using score, escapes and reaction time as outcome measures in a human
  experiment on game feel.
- Why built: if every player pops every bubble, juice cannot show an effect on performance however large it is; the
  measure has to have room to move in both directions.
- Design: an autopilot with a reaction-time parameter (latency before tapping plus a cooldown of 0.6x that between
  taps) swept 0.3 to 0.8 s over six seeds, reading the percentage popped.
- Got right: sweeping a skill parameter instead of running one "good player" exposed the ceiling immediately and
  gave a target spread to tune toward.
- Where/why it failed: at the first tuning (bubbles 120-230 px/s, a spawn every 0.7 s) the autopilot popped 100% at
  every reaction time from 0.3 to 0.8 s, so performance was at ceiling and a juice effect on it was undetectable.
- Fix: bubbles at 320-560 px/s and a spawn every 0.36 s: popped 100/98/82/61% at reaction 0.3/0.45/0.6/0.8 s, and
  the shipped test asserts a slower player lets more escape (8 vs 44).
- Why this fix: typical human tap latency on moving targets sits in the 0.5-0.8 s band, which now spans a wide range
  of outcomes, while the fastest players still have headroom near the top.
- Rule of thumb: Before a human A/B on a performance measure, sweep an autopilot's skill parameter and check the
  measure is off its ceiling across the plausible human band; a 100% pop rate at every reaction 0.3-0.8 s hides any effect.
- Provenance (verified/assumed): verified first-hand by the sweep and the shipped smoke assertion; that real players
  fall in the 0.5-0.8 s band is assumed from typical tap-latency figures, not measured here.
- Composed: demo-disc/E2
- Link: session https://claude.ai/code/session_0165jfQbaW5xxNCE9kqoELSQ, commit e4e4a0c (Pappydapimp69/Demo-disc)

## E34 — timed hit grades follow a gaussian model and skill is worth only 13 percent
- Date: 2026-10-15
- Project: pappydapimp69/demo-disc
- Tags: [gamedev][balance][sandbox]
- What: Checking the Stonewake timed-hit system (PERFECT under 70 ms x1.6, GOOD under 160 ms x1.25, else OK x1.0,
  plus a chained-PERFECT combo of +10% per step up to +50%) against the grade counts logged by the playtest.
- Why built: The playtest profiles (skilled, average, casual) were tuned by eye; the question was whether a closed-
  form model predicts their grade rates, and how much timing skill is actually worth in damage.
- Design: Tap error modelled as N(0.02, sigma) with sigma .07/.11/.15; grade rates from the normal CDF compared
  with logged counts (n = 69/80/103) by binomial z; expected damage per attack with the combo computed exactly as
  a Markov chain over the PERFECT streak; then an alternative multiplier set (2.0 / 1.2 / 0.6) for comparison.
- Got right: The Gaussian model matches the real-game playtest for all three profiles within |z| < 2 (skilled
  .66/.31/.03 vs .65/.32/.03; casual .36/.35/.29 vs .34/.38/.28), so grade rates can be set on paper before
  playtesting.
- Where/why it failed: Timing skill is worth very little: skilled vs casual expected damage is only x1.13 from the
  grade multipliers; the combo lifts it to x1.24 (my prediction said under x1.2 with the combo, refuted). A
  1.6/1.25/1.0 ladder makes a timing game whose timing barely matters.
- Fix: Widen the ladder so the bottom grade costs something, e.g. PERFECT x2.0, GOOD x1.2, OK x0.6, which gives
  x1.31 on grades alone at the same windows, and check the separation with the model before any playtest.
- Why this fix: Penalising sloppy hits moves the spread without making the windows harder, so the average player's
  PERFECT rate (about 47-53%) stays the same while the skill payoff becomes visible.
- Rule of thumb: Model timed-hit grades as a Gaussian tap error against the windows and compute skilled vs casual
  damage before tuning; a 1.6/1.25/1.0 ladder makes timing skill worth only about 13%.
- Provenance (verified/assumed): verified first-hand by the stdlib sandbox below, which embeds the grade counts
  copied from this session's real-game playtest logs; the sigma values are the playtest's own model inputs.
- Composed: demo-disc/E32
- Sandbox: sandboxes/2026-10-15__timed-hit-grades-follow-a-gaussian-model-and-skill-is-worth-only-13-percent.py
- Prediction: Model within |z| < 2 of the observed rates for all three profiles; skilled/casual damage ratio under
  1.2 even with the combo; the 2.0/1.2/0.6 ladder separates more than the current grades.
- Observed: RESULT: PASS model matches the playtest within |z|<2 for all 3 profiles; skilled vs casual damage only
  x1.13 from grades, x1.24 with combo; 2.0/1.2/0.6 multipliers give x1.31. The under-1.2-with-combo part of the
  prediction was refuted (1.24).
- Scenarios: 1) model vs playtest for skilled, average and casual; 2) exact combo expectation per profile; 3)
  skilled/casual damage ratio, built to BREAK the assumption that timing skill is worth a lot of damage; 4) an
  alternative multiplier ladder.
- Link: session_0169rjPqYDYawkbeTUEzoNKo (brain train on the Stonewake playtest data)

## E33 — a boss acting twice is a constant factor not party scaling
- Date: 2026-10-15
- Project: pappydapimp69/demo-disc
- Tags: [gamedev][balance][sandbox]
- What: Testing the Stonewake change "bosses act twice once you have companions, so their threat grows with the
  party" against brain-builder E5 (a single-target boss makes difficulty a step function of party size N; AoE fixes it).
- Why built: The commit message claimed the second action makes boss threat grow with N; that is a claim about
  scaling, and the earlier lesson says only output that scales with N (AoE) changes the scaling.
- Design: Deterministic expected-value round sim with Stonewake-like numbers (20 damage per member per round, 90 HP
  members, 300 HP boss, 18 per hit, boss focuses the weakest member), party sizes 1-4, four rules: single action,
  two actions when N >= 2, AoE every action, and the game's mix (two actions, AoE every third round).
- Got right: E5 reproduces from a new angle: a single-target boss gets steadily weaker as N grows (party HP left
  0.10 at N=2, 0.85 at N=4), and AoE cuts that slope roughly in half (+0.40 against +0.75 from N=2 to N=4).
- Where/why it failed: Acting twice is a constant factor, not scaling: from N=2 to N=4 leftover HP still climbs
  +0.70, nearly the single-target slope (+0.75); it just shifts the curve. My first prediction that AoE would keep
  leftover HP flat across N was also wrong: the boss still dies in about 1/N rounds, so AoE halves the slope only.
- Fix: Keep the extra action as a tuning knob for a fixed party size, but scale threat with N through AoE turns
  (crystal rain, eruption) and per-boss HP, since Stonewake's party size per boss is fixed by the story anyway.
- Why this fix: Story-fixed N makes per-boss tuning valid, while AoE is the only lever that changes the slope if N
  ever varies (optional fights, a downed member, the finale with four).
- Rule of thumb: Extra boss actions multiply threat by a constant; only output that scales with party size (AoE)
  changes how difficulty moves with N, and even AoE only halves the slope.
- Provenance (verified/assumed): verified first-hand by the stdlib sandbox below; numbers copied from its run.
- Composed: brain-builder/E5, demo-disc/E32
- Sandbox: sandboxes/2026-10-15__a-boss-acting-twice-is-a-constant-factor-not-party-scaling.py
- Prediction: Single-target leftover HP rises with N; acts-twice still rises with nearly the same slope; AoE keeps
  leftover HP flat (within 0.1) from N=2 to N=4.
- Observed: RESULT: PASS slope N=2->4 single +0.75, acts-twice +0.70, AoE +0.40; leftover HP N=2->4: single
  0.10->0.85, acts-twice 0.00->0.70, AoE 0.00->0.40, game mix 0.00->0.55. The AoE-flat prediction was refuted.
- Scenarios: 1) single action; 2) two actions from N=2, built to BREAK the claim that acting twice scales threat
  with the party; 3) AoE on every action; 4) the game's mix.
- Link: session_0169rjPqYDYawkbeTUEzoNKo (brain train on the Stonewake boss changes, demo-disc commit 91ce487)
- Cited-by: 2026-10-17 · projects/pappydapimp69__demo-disc.md#E41 · compatible · no sandbox · https://claude.ai/code/session_0189x5cwDWHdyFUT5WmrVCJq, Demo-disc commit d8c9970

## E32 — judge rpg difficulty with human timing profiles not the test autopilot
- Date: 2026-10-15
- Project: pappydapimp69/demo-disc
- Tags: [gamedev][balance][testing]
- What: Judging and tuning the Stonewake RPG's difficulty (timed-hit turn-based battles, three golem bosses, a
  finale) after the user asked whether the game was actually good.
- Why built: The smoke tests already beat every boss with an autopilot that taps perfectly and blocks every hit,
  which proved the fights were winnable but said nothing about whether they were hard, or whether skills mattered.
- Design: A Playwright playtest that plays through real pointer events with a human timing model (tap error ~
  N(0.02, sigma) s, a block-attempt rate) in three profiles: skilled (sigma .07, blocks 95%, uses counters), average
  (sigma .11, 70%, counters) and casual (sigma .15, 40%, FIGHT only); it logs win, seconds, tries and LOWEST party HP.
- Got right: The profiles separated what the perfect autopilot could not: before the changes casual FIGHT-only
  play won every fight; after adding telegraphed tricks it clears the tutorial golem at 12% HP but fails the
  shell, burrow and finale fights, while counter-using profiles win first try.
- Where/why it failed: Three measurement traps: the perfect autopilot made every boss look trivially easy; ending
  HP hid real danger because a level-up on the win refills HP (needs lowest HP during the fight); and a damage
  multiplier on the counter (glass x1.5 on a fire-weak boss) let tactical play delete 230 HP bosses in 1 round.
- Fix: Tune against profile outcomes and min-HP, make counters EXPOSE a boss (break shell, stun) instead of
  multiplying damage, and give bosses a second action only when the party has 2+ members so threat scales with N.
- Why this fix: The profile gate states the design intent as data (casual fails trick bosses, average wins in one
  or two tries), and counters that expose rather than multiply keep fights 30-45 s instead of one round.
- Rule of thumb: Tune RPG difficulty with human-timing player profiles and the lowest HP during each fight, not a
  perfect test autopilot or end-of-fight HP; make counters expose the boss, not multiply damage.
- Provenance (verified/assumed): verified first-hand: all numbers come from the playtest runs this session (casual
  pre-change won all fights at 70%+ HP; post-change casual cave/desert/finale lost 4 of 4 tries, skilled and
  average won first try). The timing sigmas are my modelling choice, stated as such in Design.
- Composed: N/A
- Link: session_0169rjPqYDYawkbeTUEzoNKo (demo-disc commit 91ce487)
- Cited-by: 2026-10-15 · projects/pappydapimp69__demo-disc.md#E33 · compatible · sandboxes/2026-10-15__a-boss-acting-twice-is-a-constant-factor-not-party-scaling.py · observed RESULT: PASS slope N=2->4 single +0.75, acts-twice +0.70, AoE +0.40; leftover HP N=2->4: single 0.10->0.85, acts-twice 0.00->0.70, AoE 0.00->0.40, game mix 0.00->0.55. The AoE-flat prediction was refuted. · session_0169rjPqYDYawkbeTUEzoNKo (brain train on the Stonewake boss changes, demo-disc commit 91ce487)
- Cited-by: 2026-10-15 · projects/pappydapimp69__demo-disc.md#E34 · compatible · sandboxes/2026-10-15__timed-hit-grades-follow-a-gaussian-model-and-skill-is-worth-only-13-percent.py · observed RESULT: PASS model matches the playtest within |z|<2 for all 3 profiles; skilled vs casual damage only x1.13 from grades, x1.24 with combo; 2.0/1.2/0.6 multipliers give x1.31. The under-1.2-with-combo part of the prediction was refuted (1.… · session_0169rjPqYDYawkbeTUEzoNKo (brain train on the Stonewake playtest data)
- Cited-by: 2026-10-17 · projects/pappydapimp69__demo-disc.md#E41 · compatible · no sandbox · https://claude.ai/code/session_0189x5cwDWHdyFUT5WmrVCJq, Demo-disc commit d8c9970

## E31 — survivorlike offer pool size
- Date: 2026-10-15
- Project: pappydapimp69/Demo-disc
- Tags: [gamedesign][probability][sandbox]
- What: Exact model of a survivor-like pick-1-of-3 level-up: the chance a target upgrade, or a two-piece
  synergy, is ever offered in L level-ups, as the pool size n, removals and rarity weights change.
- Why built: Training Brain on game genres; survivor-likes and roguelites had no kernel, and pool size is
  the hidden lever that decides whether players can build the combos the designer wrote.
- Design: Closed form 1 - (C(n-1,3)/C(n,3))^L with inclusion-exclusion for two pieces, checked against a
  brute-force enumeration of every offer sequence at n=6, L=3; Fractions throughout.
- Got right: Closed form matched brute force exactly (7/8); n=30 gave 0.878 and n=60 0.642 as predicted,
  a two-piece synergy at n=30 gave 0.771, and the 90 percent pool cap at L=20 is n=27 (3L/ln10 = 26.1).
- Where/why it failed: I predicted maxed items leaving the pool would add more than 0.05 at n=30; it added
  0.048, so pool shrinkage late in a run is a weaker lever than I expected.
- Fix: Treat pool size and level-up count as the main dials and shrinkage as a small one; rarity weights
  are the strongest lever (weight 1/4 dropped a target from 0.88 to 0.41).
- Why this fix: Shrinkage only starts after several level-ups, so it touches the late offers alone, while
  pool size and rarity change every offer of the run.
- Rule of thumb: In a pick-1-of-3 level-up, keep the active pool under about 3L/ln10 for a 90 percent
  chance to see any given upgrade; each added weapon quietly makes two-piece synergies rarer.
- Provenance (verified/assumed): Verified first-hand: sandbox run, closed form confirmed by exhaustive
  enumeration; uniform offers are a modelled assumption, named in the rarity scenario.
- Composed: ideas:GAME-DESIGN/genre-catalog/name-the-genre-by-its-verb-and-loop, ideas:SYSTEM/gamedesign/turret-kind-not-tier
- Sandbox: sandboxes/2026-10-15__survivorlike-offer-pool-size.py
- Prediction: Written before the first run: L=20, n=30 about 0.88, n=60 about 0.64, a two-piece synergy at
  n=30 about 0.75, and maxed-item removal adding more than 0.05 at n=30.
- Observed: RESULT: PASS P(seen) n=30 0.878 n=60 0.642, 2-piece n=30 0.771, pool cap for 90% at L=20 is
  n=27, maxed-out removal +0.048, rarity 1/4 -> 0.414. The removal prediction (over 0.05) was refuted.
- Scenarios: S0 brute force vs closed form; S1 pools 15-90; S2 pool cap search; S3 shrinking pool; S4 a rare
  target at weight 1/4 (built to BREAK the pool rule: same n, far lower odds).
- Link: ideas/2026-10-15__survivorlike-offer-pool-size.md; session_011p52L2CkFXcsYRwjDu6tG9

## E30 — sight gags in spoof ads
- Date: 2026-10-15
- Project: pappydapimp69/Demo-disc
- Tags: [game-ads][comedy][creative-arts]
- What: Applied the Carroll sight-gag taxonomy to the beats of two shipped spoof ads (FARO, GOING UP) and to
  the ad-to-game cut of all 15 disc entries.
- Why built: The sight-gag kernel says a payoff carried by a caption is the weakest place for it; the disc's
  ads are caption-heavy on purpose, so it needed testing against a format that parodies captions.
- Design: A table of 24 in-ad beats read from the ad.html timelines, each tagged image or caption, payoff or
  not, with a Carroll type or none; plus a per-entry tag for whether the game reframes what the ad was.
- Got right: 0 of 24 in-ad beats fit a Carroll type and 6 of 7 payoffs ride a caption, while 14 of 15
  ad-to-game cuts are switch images; the honest Stonewake trailer is the one with no switch.
- Where/why it failed: The kernel's caption warning does not hold inside a parody of a caption-driven
  format: the WRONG and FAIL stamps are the trope being copied, so cutting them would break the parody.
- Fix: Keep caption payoffs inside a spoof ad and put the sight gag at the format boundary: the ad is the
  first image, the game is the reframe, which is Carroll's switch image across the cut.
- Why this fix: The copied trope needs its captions to read as the real format, and the disc's joke lands
  only when the player taps play and sees what the ad really was.
- Rule of thumb: In a parody of a caption-driven format, caption payoffs are the copied trope, not a
  weakness; put the real sight gag at the boundary, where the next thing reframes the whole piece.
- Provenance (verified/assumed): Verified first-hand: beats read from the two ad.html files and the README
  rows of shipped pairs, and the audit script was run on that table.
- Composed: ideas:COMEDY-CRAFT/visual-gags/sight-gag-taxonomy, ideas:COMEDY/fake-mobile-ad/copy-the-ad-format-exactly-then-let-it-turn-on-itself, ideas:COMEDY/fake-mobile-ad/reusable-fake-ad-grammar-kit
- Sandbox: sandboxes/2026-10-15__sight-gags-in-spoof-ads.py
- Prediction: Written before the first run: at most 2 of 24 in-ad beats fit a Carroll type, at least 6 of 8
  payoffs ride a caption, and all ad-to-game cuts are switch images.
- Observed: RESULT: PASS 0 Carroll-typed beats in 24 in-ad beats, 6/7 payoffs on a caption, 14/15 ad->game
  cuts are switch images; the honest Stonewake trailer has none. Payoff count was 7, not 8 as I guessed.
- Scenarios: S1 in-ad beat typing; S2 payoff carrier count; S3 ad-to-game cuts including the honest
  Stonewake trailer (built to BREAK it: an honest trailer has no switch).
- Link: ideas:COMEDY-CRAFT/visual-gags/sight-gag-taxonomy; session_011p52L2CkFXcsYRwjDu6tG9

## E29 — deckbuilder thin vs add
- Date: 2026-10-15
- Project: pappydapimp69/Demo-disc
- Tags: [gamedesign][economy][sandbox]
- What: Exact-enumeration model of a deckbuilder turn (draw 5, play best 3) comparing removing a weak card
  with adding a new card of each value, from a 5 Strike / 4 Defend / 1 Bash starter.
- Why built: Training Brain on game genres it had no kernel for; deckbuilders had none, and the cut-vs-add
  choice is the genre's core economy decision.
- Design: All C(n,5) hands enumerated with Fractions; value = sum of the best 3 cards; key-card odds tracked by
  position. Scenarios vary deck size and how many drawn cards can be played.
- Got right: Cutting a Defend gave +0.389 per turn and P(Bash) 1/2 to 5/9; an added card needed value 8 (deck
  mean 6.0) to beat that cut, and an added 6 lost value (-0.108).
- Where/why it failed: My prediction that thinning would LOSE value when every drawn card is playable was
  wrong (+0.556 observed), and I predicted the add threshold near 7 but it was 8.
- Fix: Restated the rule: removing a below-mean card helps whenever the deck is bigger than the hand,
  whatever the play limit; it only stops when the hand covers the whole deck (+0.000).
- Why this fix: Removing a below-mean card raises the mean of every draw, so the play limit only changes how
  much it helps, while hand-covers-deck makes the draw fixed and removal moot.
- Rule of thumb: In a deckbuilder, cut below-mean cards before adding merely good ones; an added card must
  beat the cards you actually play, not the deck average, or it dilutes the hand.
- Provenance (verified/assumed): Verified first-hand by running the exact sandbox; the card values are a
  modelled damage-equivalent scale chosen for the starter shape.
- Composed: ideas:GAME-DESIGN/genre-catalog/name-the-genre-by-its-verb-and-loop, ideas:GAME-DESIGN/idle-math/exponential-cost-over-linear-production-makes-the-wall
- Sandbox: sandboxes/2026-10-15__deckbuilder-thin-vs-add.py
- Prediction: Written before the first run: cutting a Defend beats adding any card worth under about 7;
  with hand >= deck thinning gains 0; when every drawn card is playable, cutting a Defend loses value.
- Observed: RESULT: PASS remove-Defend +0.389/turn; an added card must be worth >= 8 (deck mean 6.0) to
  beat it; thinning gains nothing when hand covers deck (+0.00) and still gains when you can play every
  card drawn (+0.556). The play-all prediction was refuted and the threshold was 8, not 7.
- Scenarios: S1 starter cut Defend vs cut Strike; S2 add values 5-15; S3 5-card deck where the hand covers
  the deck (built to BREAK it); S4 play every drawn card (prediction refuted).
- Link: ideas/2026-10-15__deckbuilder-thin-vs-add.md; session_011p52L2CkFXcsYRwjDu6tG9

## E28 — spoof ad two dial joke types
- Date: 2026-10-15
- Project: pappydapimp69/Demo-disc
- Tags: [game-ads][comedy][creative-arts]
- What: Tagged the 14 shipped Demo Disc spoof ads on two dials, the ad's lie axis (5) and how the game
  answers it (7: genre swap, same word, real skill, backstage, role swap, tone flip, payoff twist), and
  built a planner that picks the next ad's joke type from the unused cells.
- Why built: The owner asked for new kinds of jokes in future ads. The kit audit showed every ad used one
  lie axis, so the jokes risked becoming one joke; a second dial gives a menu instead of a single trope swap.
- Design: Least-used-first planner over the 35 cells, skipping cells the disc already has and never
  repeating either dial of the previous ad; baseline copies the most-used cell. A premise is the ad hook
  plus the game recipe, with ad verb != game verb and no disclaimer field.
- Got right: The disc uses only 10 of 35 cells, the rules-breaking lie axis 0 of 14 times, and real skill
  is the most-used answer (4). The planner gave 8 new cells with 0 adjacent repeats, the copy-the-hit
  baseline repeated a dial 8 of 8 times.
- Where/why it failed: With one answer type allowed the planner finds no legal next ad at all, and with 2
  axes by 2 answers it runs dry after 2 ads; the rotation needs width on both dials to work.
- Fix: Keep at least 3 answer types and 3 lie axes in play, and start from the unused cells the planner
  lists (rules x genre swap, crowd x backstage, rules x role swap, prize x genre swap) before reusing one.
- Why this fix: The adjacency rule removes the previous ad's row and column, so with k options per dial a
  fresh cell needs k >= 2 on each and k >= 3 to survive more than a couple of ads once cells are used up.
- Rule of thumb: Pick a spoof ad's joke on two dials, what the ad lies about and how the game answers the
  lie, and change both dials from the last ad; copying the last hit repeats a dial every time.
- Provenance (verified/assumed): Verified first-hand: tags read from the Demo Disc README and ads built in
  this session; the sandbox was run and reproduced every number above.
- Composed: ideas:COMEDY/fake-mobile-ad/premise-slot-machine-from-the-five-misleading-ad-patterns, ideas:COMEDY/fake-mobile-ad/reusable-fake-ad-grammar-kit, fake-ad-kernel-source-check/E1
- Sandbox: sandboxes/2026-10-15__spoof-ad-two-dial-joke-types.py
- Prediction: Written before the first run: rules axis 0/14, at most 8 cells used, rotation 0 adjacent
  repeats, naive baseline at least 3, and fewer than 6 ads before a 2x2 grid runs dry.
- Observed: RESULT: PASS disc uses 10/35 cells, rules axis 0/14; rotation 0 adjacent repeats vs naive 8,
  8/8 new cells; planner fails with 1 answer type and runs dry at 2 with 2x2. The cells-used prediction
  (at most 8) was wrong: 10 were used.
- Scenarios: S1 audit of the 14 shipped pairs; S2 8-ad rotation vs copy-the-hit; S3 one answer type only
  (built to BREAK it: no legal ad); S4 2 axes x 2 answers (runs dry at 2).
- Link: ideas/incoming/2026-10-15__spoof-ad-two-dial-joke-types.md; session_011p52L2CkFXcsYRwjDu6tG9
- Audited: 2026-10-15 · modeled · Bridge recheck. E28 composes local__fake-ad-kernel-source-check#E1, whose own run came out FAIL because the kernel had renamed one study pattern ('borrowed fame' for 'popular externalization'). I read E28 and its stored sandbox sandboxes/2026-10-15__spoof-ad-two-dial-joke-types.py, re-ran it (RESULT: PASS, 10/35 cells, rules axis 0/14, rotation 0 adjacent repeats against 8, 8/8 new cells, dry at 2 on a 2x2 grid), and probed it with a separate script that imports its planner. The only thing E28 takes from E1 is the vocabulary of five lie axes, and the sandbox already uses the corrected meaning ('crowd' commented as popular externalization). Renaming that axis back to borrowed_fame gave an identical 8-ad plan, so the claim does not depend on the contradicted entry. Its own evidence is weaker than the PASS suggests. The tallies (10 of 35 cells used, rules axis 0 of 14, real skill used 4 times) are real counts of first-hand tags. But the rotation's 0 adjacent repeats and 8/8 new cells are enforced by the planner's own skip rules. The copy-the-hit baseline repeats a dial 8 of 8 times because it copies one cell 8 times. The one-answer-type break fails by definition once the previous ad used that answer. So those numbers restate the design and do not test it. The Fix's "keep at least 3 per dial" was not run in the stored sandbox. My probe supports it: three 3x3 grids taken from the disc's axes sustained 7, 7 and 9 ads, and fresh grids sustained 1 ad at 2x2, 8 at 3x3 and 15 at 4x4. The claim's real target is new kinds of jokes that land with viewers, and only a hand-written dial model was tested. Verdict modeled: it survives without E1 and the combinatorics hold, but the rotation numbers come from the planner's construction, not from testing, and joke quality is not measured. · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 2 pass 3

## E27 — a looping ad tile must end on the call to action not a story button
- Date: 2026-10-15
- Project: pappydapimp69/demo-disc
- Tags: [film][editing][design]
- What: Stonewake ad v3 followed the film-trailer pattern of a story button after the title: logo and call to
  action at 19.2-23.6 s, then the game's real ending (the eye closing) as the last shot, on a tile that loops.
- Why built: The trailer-grammar kernel ends on a button (one last taste after the title), and the honest-footage
  kernel suggested the real ending as that button, so the last frame was gameplay with no prompt to play.
- Design: Title and PLAY THE DEMO FREE line, then 2.4 s of the captured CALM ending; the demo-disc catalog plays
  each trailer muted-or-not in a looping video tile, so the loop restarted from that gameplay frame.
- Got right: Showing the real ending kept the ad honest and resolved the FIGHT/CALM question visually, which is why
  it stays in the cut; only its position was wrong.
- Where/why it failed: The user's verdict was that the ad must end on the call to action and, if anything, loop. A
  film button assumes the title already sold the ticket; an ad's last frame is the one on screen when the viewer
  decides, and in a looping tile the end must also flow back into the opening.
- Fix: Moved the eye closing before the logo, ended on a pulsing PLAY button drawn in the game's own menu style held
  for about 4 s, then a 0.4 s fade to black that matches the hook's fade-in, with audio tails faded out by the end.
- Why this fix: The call to action is held longest and last, the story still resolves before it, and the loop seam
  (black to black, eye closed to eye opening) turns the restart into part of the story instead of a jump.
- Rule of thumb: An ad ends on its call to action, held, never on a story button after it; for a looping tile, fade
  the last frame into the first so the restart reads as one piece.
- Provenance (verified/assumed): verified first-hand: user feedback on v3, and the v4 render checked frame by frame
  (eye closes 19.2-21.6, button from 23.3 to 27.6, black at 28 into the hook's fade-in).
- Composed: ideas:FILM/trailer-grammar/cold-open-three-acts-button-cut-to-the-beat, ideas:GAME-ADS/honest-footage/capture-real-gameplay-through-the-games-test-hooks
- Polarity: incompatible
- Link: session_0169rjPqYDYawkbeTUEzoNKo (Stonewake ad v4, film21.html, demo-disc commit 9809dd5)

## E26 — fake ad kit audit misses the disclaimer
- Date: 2026-10-15
- Project: pappydapimp69/Demo-disc
- Tags: [creative-arts][game-ads][comedy]
- What: The new half's strongest creative path, the fake-ad premise slot machine with the fake-ad grammar kit, run
  with the source-check lesson, against the four spoof ads built for the Demo Disc this session.
- Why built: The kit is meant to be reused so every ad reads as a mobile ad in the first second, and the slot
  machine warns that a channel reads as templated when every video uses the same swap; neither had been checked
  against ads actually shipped.
- Design: A script that pattern-matches each ad's render source and soundtrack spec for the kit's eleven elements,
  plus each premise classified by trope and by which of the study's five mismatch axes its joke uses.
- Got right: Every ad carried 8 or 9 of the 11 elements (finger cursor, FAIL stamp with TRY AGAIN, 99 percent text,
  fail sting, pulsing INSTALL NOW, five-star end card), so the format reads instantly as intended.
- Where/why it failed: None carried the "not all images represent actual gameplay" disclaimer, the kit's most
  telling detail, and all four premises use the same mismatch axis (gameplay disguise) out of five, which is the
  templating the slot-machine kernel warns about.
- Fix: Add the tiny disclaimer to the shared ad kit's end card, and rotate the swap axis across future ads:
  narrative pretense, borrowed fame, ruleset distortion and incentive illusion are all unused on the disc.
- Why this fix: The disclaimer is a one-line kit change that lands on every ad at once, and varying the axis is
  the kernel's own remedy for a channel that starts to read as one joke repeated.
- Rule of thumb: Audit shipped spoof ads against the kit: these four carried 8-9 of 11 elements but no disclaimer,
  and all four used one swap axis of five; put the disclaimer in the kit and rotate axes.
- Provenance (verified/assumed): Verified first-hand: the script scanned the four ad sources (its embedded snapshot
  equals the live scan); the premise-to-axis mapping is my classification of each ad's joke.
- Composed: ideas:COMEDY/fake-mobile-ad/premise-slot-machine-from-the-five-misleading-ad-patterns, ideas:COMEDY/fake-mobile-ad/reusable-fake-ad-grammar-kit, fake-ad-kernel-source-check/E1
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-15__fake-ad-kit-audit-misses-the-disclaimer.py
- Prediction: Each ad carries at least 8 of the 11 kit elements, none carries the disclaimer, and all four use the
  same swap axis.
- Observed: RESULT: PASS 8-9 of 11 per ad; disclaimer 0/4; one axis (gameplay disguise) across 4/4; level counter
  missing on FARO, help-him caption only on VEER.
- Scenarios: 1) VEER; 2) EMBERS; 3) GOING UP; 4) FARO, the ad without a level counter, built to BREAK the
  every-element claim
- Link: brain train creative arts (new half), session 2026-10-15; session_011p52L2CkFXcsYRwjDu6tG9

## E25 — interleaving cinematic and gameplay every shot reads as jumping
- Date: 2026-10-15
- Project: pappydapimp69/demo-disc
- Tags: [film][editing][design]
- What: Stonewake ad v2 alternated a cinematic HD-2D diorama shot and a real top-down gameplay shot almost every
  two seconds across seven locations (hill, village, forest, cave, dunes, stone face, logo); the user's verdict on
  watching it was that the ad jumps around too much.
- Why built: The alternation came from two good rules applied shot by shot: show real gameplay early and often
  (honesty, the ASA line) and keep a cinematic look for scale; plus a three-companion montage for the journey.
- Design: 16 shots, 34% gameplay, gameplay cut in at 2.4, 6.6, 14.2, 20.8 and 25.0 s, each between two cinematic
  shots of different places, each cut changing camera (side view vs top-down), grade, and art scale at once.
- Got right: The individual shots read, the hook landed by 1.05 s, and the real gameplay kept the ad honest; the
  problem was only how they were ordered, not what they showed.
- Where/why it failed: Every cut changed look, place and camera axis together, so the eye had to re-find the
  subject 15 times in 26 s; a montage of three similar recruit shots (forest, cave, dunes) added three more
  places without adding a cause, and a half-second hand shot barely read.
- Fix: Regroup into blocks so the look changes only twice: one continuous 4 s cinematic opening, an unbroken run of
  real gameplay (dialogue, timed hit, walk to the boss), then a cinematic climax in the same place, joined by a
  match cut on the titan's eye at the same screen position; cut the recruit montage and the hand, and halve shake.
- Why this fix: Gameplay keeps the same share and the story chain stays intact, while the viewer re-orients only at
  the two block boundaries, and the match cut makes even that boundary feel continuous.
- Rule of thumb: When an ad mixes cinematic and real gameplay, group each look into a block and change look only at
  block boundaries, joined by a match cut; alternating looks every shot reads as jumping.
- Provenance (verified/assumed): verified first-hand: the user watched v2 and reported it jumps around too much;
  v3 regrouped as described (shots 16 to 11, looks changed 2 times instead of 9).
- Composed: ideas:GAME-ADS/honest-footage/capture-real-gameplay-through-the-games-test-hooks, ideas:FILM/trailer-pacing/shots-shorten-into-the-climax-then-the-title-breathes, ideas:GAME-ADS/game-trailers/gameplay-first-thumbstopper-rising-line-with-accents
- Link: session_0169rjPqYDYawkbeTUEzoNKo (Stonewake cinematic v2 -> v3, film21.html)

## E24 — file url images taint a canvas film so embed them as data uris
- Date: 2026-10-15
- Project: pappydapimp69/demo-disc
- Tags: [rendering][canvas][tooling]
- What: The deterministic canvas film renderer (Playwright opens filmNN.html over file:// and reads each frame with
  canvas.toDataURL) broke as soon as the Stonewake v2 trailer drew real gameplay frames from PNG strips.
- Why built: The v2 ad cuts real captured gameplay (180x320 frames packed into strips) between the cinematic shots
  so the ad represents the actual game; the strips were loaded as hidden img elements next to the HTML file.
- Design: Hidden img tags with relative src, drawn with drawImage onto the output canvas at integer scale; the page
  load event waits for them, so render(t) can draw them synchronously.
- Got right: Hidden img tags are a sound way to make a scrubbed film wait for its images: the load event covers
  them, unlike new Image() objects created in script, so frame 0 never renders before the footage exists.
- Where/why it failed: Chromium treats every file:// image as cross-origin, so drawing one taints the canvas and
  toDataURL throws a SecurityError ("Tainted canvases may not be exported"); the first still failed and no frame
  could be read back. Nothing in the page itself errors, only the export.
- Fix: Embed the strips in the HTML as base64 data URIs at build time (a few lines of Python replacing each src),
  which are same-origin, so the canvas stays clean and exports work under file://.
- Why this fix: It keeps the film a single self-contained file, needs no local web server or browser flags, and
  the strips are small (about 260 KB of PNG for five clips) because the footage is stored at the game's grid.
- Rule of thumb: In a canvas film rendered over file:// and read back with toDataURL, embed every image as a data
  URI; a file:// image taints the canvas and only the export fails.
- Provenance (verified/assumed): verified first-hand: the render threw the SecurityError on the first still with
  file:// src and ran cleanly for all stills and 624 frames after embedding data URIs.
- Composed: N/A
- Link: session_0169rjPqYDYawkbeTUEzoNKo (Stonewake cinematic v2, film21.html)

## E23 — tilt shift gradient is exact on the ground and wrong on upright sprites
- Date: 2026-10-15
- Project: pappydapimp69/demo-disc
- Tags: [rendering][canvas][sandbox]
- What: Choosing depth-of-field blur for 2D pixel diorama shots (HD-2D look), where film20 set each layer's blur by
  hand and the cheap alternative is a screen-space tilt-shift band that blurs by distance from a horizontal line.
- Why built: Held et al. (ACM TOG 2010) say blur is proportional to |1/z_focus - 1/z| and that linear vertical
  gradients approximate tilt-shift; the trailer needed to know when the cheap gradient is right and when it lies.
- Design: Pinhole camera 10 units up, pitched 35 degrees down; computed true blur K*|1/zf-1/z| for ground points,
  a ground row, an upright 60-unit titan at depth 200, and compared inverse-depth blur with blur linear in depth.
- Got right: On a ground plane inverse depth is affine in screen y, so signed blur is exactly linear in y (max
  residual 4e-16 px); the tilt-shift band is exact there. Blur is constant along a ground row, so a horizontal
  gradient only invents depth. Inverse-depth blur caps far layers at K/zf (1.33 px) instead of growing.
- Where/why it failed: Upright objects break the band: the titan's true blur is 1.08 px over its whole height, but
  the y-gradient blurs its head at 2.80 px (2.6x) because the head sits higher on screen than its feet. Blur that
  grows linearly with depth fails the other way, reaching 444431 px at infinity.
- Fix: Blur the ground with the vertical band if it is cheap, but blur each upright sprite or layer as one piece at
  the value for its foot's depth, using r = K*|1/zf - 1/z| clamped to a maximum.
- Why this fix: The foot point is where the sprite meets the plane, so it carries the sprite's true depth, and one
  blur per layer is the same cost as the cached pre-blurred layers canvas already needs.
- Rule of thumb: Tilt-shift's vertical blur band is exact only on the ground; blur each upright sprite or layer
  as one piece at its foot's depth with r = K*|1/zf - 1/z|.
- Provenance (verified/assumed): verified first-hand by the stdlib sandbox below (projection and blur arithmetic,
  numbers copied from the run). That viewers read it as miniature comes from Held et al. and is cited, not tested.
- Composed: ideas:ART/diorama/one-depth-per-layer-drives-parallax-blur-fog-and-scale
- Sandbox: sandboxes/2026-10-15__tilt-shift-gradient-is-exact-on-the-ground-and-wrong-on-upright-sprites.py
- Prediction: Ground blur linear in screen y to float precision; constant along a ground row; titan head blurred at
  least 2x its true value by the y-gradient; inverse-depth blur at infinity equals K/zf = 1.33 px.
- Observed: RESULT: PASS ground blur linear in screen y (resid 4e-16); constant along x; upright titan: y-gradient
  gives head 2.8px vs true 1.08px; far blur caps at K/zf
- Scenarios: 1) ground plane, 21 points; 2) one ground row across X; 3) upright titan, built to BREAK the idea that
  a tilt-shift band is a general depth-of-field; 4) inverse-depth vs linear-in-depth blur on far layers.
- Link: session_0169rjPqYDYawkbeTUEzoNKo (Brain training for HD-2D diorama shots)

## E22 — symmetric soft clip adds no octave so virtual bass needs bias
- Date: 2026-10-15
- Project: pappydapimp69/demo-disc
- Tags: [audio][dsp][sandbox]
- What: Making trailer sub drops and braam fundamentals audible on phone speakers (which roll off below about
  100-200 Hz) by saturating a copy of the sub so the ear rebuilds the missing fundamental from its harmonics.
- Why built: The demo-disc ads play mostly on phones; the 28-60 Hz subs in the numpy scores vanish there, and the
  research recipe said gentle saturation adds the 2nd to 4th harmonics that small speakers can reproduce.
- Design: DFT-measured harmonics 2-4 of a 50 Hz sine after the cubic soft clipper x - x^3/3 (drive 1.5), after the
  same clipper with a +0.3 DC bias, and after a full-wave rectifier, all relative to the fundamental.
- Got right: Saturation does add strong harmonics: the symmetric clip puts H3 at -13 dB, and the biased clip gives
  H2 -15 dB, H3 -15 dB, H4 -22 dB, which is the 2nd-to-4th series the virtual-bass recipe asks for.
- Where/why it failed: A symmetric clipper is an odd function, so it makes ONLY odd harmonics: H2 and H4 measured
  -238 dB (numerical zero). The octave above the sub, the harmonic that most strongly implies the fundamental,
  never appears. A full-wave rectifier goes the other way and cancels the fundamental entirely.
- Fix: Add a DC bias (or use any asymmetric curve) before the clipper on the band-limited sub copy, remove the DC
  afterwards, high-pass the result above the phone's roll-off, and mix it under the original sub.
- Why this fix: Asymmetry is the only thing that creates even harmonics, and one bias constant is the cheapest way
  to get it; the original sub still carries the weight on speakers that can play it.
- Rule of thumb: For virtual bass, use an asymmetric (DC-biased) saturator; a symmetric soft clip adds only odd
  harmonics, so the octave that implies the missing fundamental never appears.
- Provenance (verified/assumed): verified first-hand by the stdlib sandbox below; all dB values are copied from the
  run. How well listeners rebuild the fundamental is from the research source (NTU virtual-bass paper), stated
  separately here and in the AUDIO small-speakers kernel.
- Composed: ideas:AUDIO/small-speakers/phones-drop-the-sub-so-add-its-harmonics
- Sandbox: sandboxes/2026-10-15__symmetric-soft-clip-adds-no-octave-so-virtual-bass-needs-bias.py
- Prediction: Symmetric clip H2 and H4 below -80 dB with H3 above -40 dB; biased clip H2 above -30 dB and H4 above
  -40 dB; rectifier fundamental near zero with energy at 2F0.
- Observed: RESULT: PASS symmetric clip H2 -238 dB H3 -13 dB H4 -238 dB (odd only); +0.3 bias H2 -15 dB H4 -22 dB;
  rectifier puts all energy at 2F0
- Scenarios: 1) symmetric soft clip, built to BREAK the recipe's claim that gentle saturation yields the 2nd-4th
  harmonics; 2) the same clip with +0.3 DC bias; 3) full-wave rectifier.
- Link: session_0169rjPqYDYawkbeTUEzoNKo (Brain training for trailer sound)

## E21 — shared comb feedback spreads reverb tails by delay length
- Date: 2026-10-15
- Project: pappydapimp69/demo-disc
- Tags: [audio][dsp][sandbox]
- What: Sizing a Schroeder/Freeverb comb-bank reverb tail for synthesized trailer hits (braam, taiko, sub drop),
  which in audio20.py had no reverb at all and sounded small and dry.
- Why built: A trailer impact reads as huge mostly from its tail; the numpy score needed a reverb whose decay time
  could be set in seconds rather than tuned by ear through a feedback knob.
- Design: Feedback comb y[n]=x[n-D]+g*y[n-D] decays 60 dB in T=-3D/(fs*log10 g). Measured each comb and the summed
  bank by Schroeder backward integration (fit -5..-35 dB, extrapolate to -60) over the eight Freeverb lengths.
- Got right: The formula matches measurement for a single comb (D=1557, g=.84: 1.40 s predicted, 1.41 s measured),
  and solving g_i=10^(-3*D_i/(fs*T)) per comb makes the whole bank hit a 3.0 s target (measured 2.99 s).
- Where/why it failed: One shared g across combs of different length gives each comb a different decay: 1.00 s to
  1.45 s (x1.45) at g=.84. My first-run guess that the sum would track the longest comb was wrong; it measured
  1.31 s, between the mean 1.24 s and the longest 1.45 s, so neither number predicts the tail.
- Fix: Derive each comb's feedback from the target T and its own delay length instead of one roomsize knob, then
  measure the summed impulse response with backward integration before trusting the number.
- Why this fix: It turns reverb length into a direct parameter (seconds) that matches the trailer's beat timing,
  and keeps every comb ringing out together so the tail does not thin into one long resonant comb.
- Rule of thumb: Set comb-reverb feedback per comb from the target decay time and that comb's delay length; one
  shared feedback spreads tails by the delay ratio and the summed decay matches no single formula.
- Provenance (verified/assumed): verified first-hand by the stdlib sandbox below (three scenarios, numbers copied
  from the run). The claim that a tail makes impacts read bigger is craft judgement, kept separate from the maths.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__shared-comb-feedback-spreads-reverb-tails-by-delay-length.py
- Prediction: Single comb within 5% of 1.40 s; shared g spread about x1.45 (1617/1116); summed bank measures close to
  the longest comb (~1.45 s); per-comb g lands within 5% of 3.0 s.
- Observed: RESULT: PASS formula 1.40~1.41s; shared-g spread x1.45, sum 1.31s sits between mean 1.24s and longest
  1.45s; per-comb g hits 2.99s of 3.0s. The 'tracks longest' part of the prediction was refuted.
- Scenarios: 1) single comb formula vs measurement; 2) shared g across eight Freeverb combs, built to BREAK the idea
  that one roomsize gives one decay; 3) per-comb g solved for a 3.0 s target.
- Link: session_0169rjPqYDYawkbeTUEzoNKo (Stonewake cinematic trailer audio review)

## E20 — portrait pixel canvas tap targets need 22 art px at 180 wide
- Date: 2026-10-15
- Project: pappydapimp69/demo-disc
- Tags: [gamedev][mobile][sandbox]
- What: Sizing touch targets in portrait pixel-art games on a phone (Stonewake renders 180x320 art px at x4, tiles
  12 px, a tap-to-walk map and a FIGHT/SKILL/ITEM/RUN menu), measured in Apple's points.
- Why built: The research pass suggested a 320x180 canvas at x6 makes an 18x32 sprite about 36x64 pt, close to the
  44 pt minimum; that arithmetic assumed a landscape 1080-wide canvas, not our portrait 180-wide one.
- Design: Converted art pixels to points on a 390 pt wide, 3x portrait phone for 180, 320 and 640 wide canvases,
  both filling the width and snapped to an integer device-pixel scale, then compared 12 px, 16 px and 18x32
  sprites with the 44 pt minimum from Apple's games HIG.
- Got right: At 180 wide one art pixel is about 2 pt (2.17 when filling the width, 2.00 at integer x6), so an 18x32
  hero is 36x64 pt and the canvas is a sound choice for phone pixel art.
- Where/why it failed: A 12 px tile is only 24 pt and a 16 px tile 32 pt, both under 44 pt; integer snapping makes
  it worse (need 22 art px instead of 20.3). A 640 wide canvas shown on a portrait phone makes an 18 px sprite 6 pt.
- Fix: Size every tap target in art px as at least 44*canvas_width/390 (22 at 180 wide), and make anything smaller
  forgiving: snap the tap to the nearest tile, walk-to-tap, or a larger invisible hit area.
- Why this fix: The visual pixel grid can stay small and crisp while the touch grid meets the platform minimum;
  only the hit areas grow, so the art and integer scale are untouched.
- Rule of thumb: In portrait pixel games, a tap target needs at least 44*canvas_width/390 art px (22 at 180 wide);
  12 to 16 px tiles are 24 to 32 pt, so give them a larger hit area or snap taps to the nearest tile.
- Provenance (verified/assumed): verified first-hand by the stdlib sandbox below (unit arithmetic copied from the
  run). The 44 pt minimum is Apple's HIG, cited; the 390 pt phone width is the assumed reference device.
- Composed: ideas:ART/pixel-art/one-grid-integer-scale-no-mixels
- Sandbox: sandboxes/2026-10-15__portrait-pixel-canvas-tap-targets-need-22-art-px-at-180-wide.py
- Prediction: At 180 wide integer x6 one art px = 2.00 pt, so a 12 px tile is 24 pt and 44 pt needs 22 art px;
  16 px also misses; 640 wide drops an 18 px sprite to about 6 pt.
- Observed: RESULT: PASS at 180 wide integer x6: 1 art px = 2.00 pt; 12px tile 24 pt, 16px 32 pt, both < 44; need
  22 art px (fill: 20.3); 640 wide: 18px sprite 6.0 pt
- Scenarios: 1) 12 px tile at 180 wide; 2) 16 px tile, built to BREAK the idea that a 16x16 tile is a fine tap
  target; 3) integer snap vs fill-width; 4) 640x360 canvas shown on a portrait phone.
- Link: session_0169rjPqYDYawkbeTUEzoNKo (Brain training for pixel character sprites)

## E19 — parallax speed is inverse depth and canvas zoom is not a dolly
- Date: 2026-10-15
- Project: pappydapimp69/demo-disc
- Tags: [rendering][canvas][sandbox]
- What: Choosing per-layer motion for 2D pixel dioramas in the Stonewake cinematic trailer (film20), where layer
  drift was hand-picked (titan -30 px, foreground -160 px over the same shot) and the push-ins zoomed the canvas.
- Why built: A fake-3D pixel shot sells scale through parallax; hand-picked speeds can contradict the story, such as
  a mountain-sized titan sliding as if it stood a few metres behind the village.
- Design: Pinhole projection x=F*(X-camX)/(Z-camZ). Measured layer shifts for a sideways truck, per-layer scale for a
  dolly-in, and compared them with one uniform canvas zoom matched on the hero layer.
- Got right: Truck shift is exactly F*dx/Z, so the ratio between two layers equals their inverse depth ratio
  (fg at 0.5 vs village at 4: 8x). A dolly by d scales each layer by Z/(Z-d): fg 2.50, hero 1.43, titan 1.005.
- Where/why it failed: A canvas zoom applies the hero's 1.43 to every layer, so near layers under-grow and far
  layers over-grow and the shot reads flat. Linear speed sets like .2/.5/1 put the farthest layer only 5 units back;
  a giant 60 units back needs a factor of 0.017, near-static.
- Fix: Give every layer a depth Z, derive its drift as speed=Zfocus/Z and its push-in scale as Z/(Z-d), and keep
  truly huge distant subjects almost still while the foreground rushes.
- Why this fix: One depth number per layer replaces several hand-tuned speeds, keeps truck and dolly consistent
  with each other, and makes scale an output of the camera rather than a guess per shot.
- Rule of thumb: Derive 2D layer drift as Zfocus/Z and push-in scale as Z/(Z-d) from one depth per layer; a canvas
  zoom gives zero parallax, and a huge distant subject should barely move.
- Provenance (verified/assumed): verified first-hand by the stdlib sandbox below (projection arithmetic). The claim
  that near-static giants read as bigger is craft judgement from the research pass, kept separate.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__parallax-speed-is-inverse-depth-and-canvas-zoom-is-not-a-dolly.py
- Prediction: fg/village shift ratio exactly 8; dolly 0.3 gives fg about 2.5 and titan under 1.01 while a matched
  canvas zoom gives 1.43 to all; titan factor 1/60 = 0.017.
- Observed: RESULT: PASS truck shift fg/village = 8x = depth ratio; dolly .3 scales fg 2.50 hero 1.43 titan 1.005;
  distant giant needs factor 0.017, not ~.2
- Scenarios: 1) sideways truck across four depths; 2) dolly-in vs one uniform canvas zoom; 3) linear speed factors,
  built to BREAK the idea that evenly spaced speeds are a fine stand-in for depth.
- Link: session_0169rjPqYDYawkbeTUEzoNKo (Stonewake cinematic trailer review)

## E18 — measure the cut list against a trailer pacing curve before review
- Date: 2026-10-15
- Project: pappydapimp69/demo-disc
- Tags: [film][editing][sandbox]
- What: Checking the Stonewake cinematic cut (film20, 26 s, 13 shots) against measured trailer pacing rather than by
  watching stills, after the user asked whether it was the best Brain could do.
- Why built: The review method was a contact sheet of stills, which cannot see pacing; a shot list is already in
  render(t) as time ranges, so pacing can be measured as numbers against published or re-run data.
- Design: Reference is Redfern's US Horror Trailers shot-length set (Zenodo 4479068, 50 trailers, 6762 shots),
  re-run this session: mean ASL 1.09 s, 61 cuts/min, median shot by third 0.96/0.79/0.54 s, and the tenth decile
  lengthening for the title. Compared film20's ASL, cut rate, thirds, longest body hold and hook time.
- Got right: The ending matches the reference shape: the cut speeds up into a 0.8 s silence and a 0.8 s strike,
  then holds a long title and button, like the reference tenth decile lengthening to 0.77 s.
- Where/why it failed: film20 averages 2.0 s per shot (1.8x the reference, 30 cuts/min against 61), its thirds go
  2.0/1.4/1.4 s so the climax never speeds up (reference falls 0.79 to 0.54), its longest body hold (titan stands,
  3.6 s) sits at 61% where the reference cuts fastest, and the hook (the eye opening) lands at 3.6 s, past 3 s.
- Fix: Extract the cut list as data and score it against the reference curve before any visual review: a hook
  inside 3 s, about 1 s average, each third shorter than the last, and long holds only as deliberate stopdowns or
  reveals that are counted and justified.
- Why this fix: Pacing is invisible in a contact sheet and easy to rationalise while watching; a numeric check is
  cheap, repeatable on every edit, and states exactly which shot to split or trim.
- Rule of thumb: Score a trailer's cut list against a measured pacing curve before reviewing it by eye: hook by
  3 s, about 1 s per shot, each third shorter, and every long hold counted as a deliberate stopdown or reveal.
- Provenance (verified/assumed): verified first-hand: I re-ran the shot-length analysis on the downloaded dataset
  (numbers matched the research report), and the sandbox numbers are copied from its run. The reference is horror
  film trailers; that it transfers to a 25 s game ad is an open question, filed as a tension.
- Composed: ideas:FILM/trailer-grammar/cold-open-three-acts-button-cut-to-the-beat, ideas:GAME-ADS/structure/hook-in-three-seconds-sound-off
- Sandbox: sandboxes/2026-10-15__measure-the-cut-list-against-a-trailer-pacing-curve-before-review.py
- Prediction: film20 ASL about 2 s, roughly double the reference; no shortening from middle to last third; the
  titan hold falls in the 50-75% band; hook later than 3 s.
- Observed: RESULT: PASS film20 ASL 2.0s (1.8x ref), 30 cuts/min vs 61; thirds 2.0/1.4/1.4 flat into the climax
  (ref falls .79->.54); longest body shot 'titan stands' 3.6s at 61%; hook at 3.6s > 3 s
- Scenarios: 1) ASL and cut rate; 2) median shot by third; 3) where the longest body hold sits; 4) first-to-last
  third shortening ratio (0.70 vs 0.56); 5) hook time, built to BREAK the assumption that the cut already
  followed the trailer-grammar kernel.
- Link: session_0169rjPqYDYawkbeTUEzoNKo (Stonewake cinematic trailer review)

## E17 — karplus strong loop delay is n plus or minus half by averaging neighbour
- Date: 2026-10-15
- Project: pappydapimp69/demo-disc
- Tags: [audio][dsp][sandbox]
- What: Tuning Karplus-Strong plucked strings (harp, lute, plucked ostinato) for the synthesized trailer and game
  scores, where every other instrument is tuned exactly from midi().
- Why built: Plucks are the cheapest convincing acoustic timbre in a numpy score, but a detuned pluck against exact
  sine pads sounds sour, and the detune is easy to miss when each note is checked alone.
- Design: Measured pitch by autocorrelation with parabolic interpolation for N=round(fs/f) at 110, 440 and 1760 Hz,
  in the textbook form y[n]=.5(y[n-N]+y[n-N-1]) and in the common ring-buffer shortcut that averages a slot with the
  next slot.
- Got right: The two-tap average adds half a sample of delay, so the textbook loop sounds at fs/(N+.5) (within 2
  cents). Naive N=round(fs/f) is fine low down (110 Hz: -2.5 cents) and slightly flat mid-range (440 Hz: -4.5).
- Where/why it failed: The ring-buffer shortcut sounds at fs/(N-.5) instead (N=100: 443.2 Hz, not 438.8), so the
  correction flips sign with the indexing. High notes cannot be fixed by integer N at all: 1760 Hz lands at -31
  cents, and worst-case integer rounding passes 10 cents above about 509 Hz at 44.1 kHz.
- Fix: Compute N from fs/f minus the half-sample of whichever loop form is used, measure one note to confirm the
  sign, and above about 500 Hz add a fractional delay (first-order allpass or linear interpolation) in the loop.
- Why this fix: Measuring once catches the indexing sign, and the fractional delay is the only thing that removes
  the rounding error; raising the sample rate just moves the threshold up.
- Rule of thumb: A Karplus-Strong loop sounds at fs/(N+.5) or fs/(N-.5) depending on which neighbour it averages;
  measure one note to get the sign, and add a fractional delay for notes above about 500 Hz at 44.1 kHz.
- Provenance (verified/assumed): verified first-hand by the stdlib sandbox below; all pitches and cents values are
  copied from the run.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__karplus-strong-loop-delay-is-n-plus-or-minus-half-by-averaging-neighbour.py
- Prediction: Naive 440 Hz about -4.7 cents, 1760 Hz about -31 cents, half-sample model within 2 cents, threshold for
  10 cents near 500 Hz. Written before the run; the ring-buffer sign flip was NOT predicted (first run measured
  443.2 Hz and failed the model).
- Observed: RESULT: PASS textbook FS/(N+.5) and ring-buffer FS/(N-.5) both within 2c; naive 110/440/1760 =
  -3/-4/-31c; 1760 after half-sample fix still -31c; 10c worst-case threshold ~509Hz
- Scenarios: 1) 110 Hz naive N; 2) 440 Hz naive N; 3) ring-buffer variant at N=100; 4) 1760 Hz after the half-sample
  correction, built to BREAK the idea that the correction is enough.
- Link: session_0169rjPqYDYawkbeTUEzoNKo (Brain training for trailer sound)

## E16 — dithered text needs a crisp layer
- Date: 2026-10-15
- Project: pappydapimp69/Demo-disc
- Tags: [rendering][canvas][art]
- What: The Last Note, a 1-bit rhythm game that draws everything into a 240x427 buffer, runs a 4x4 Bayer
  dither to two inks, and scales the result up 3x with nearest-neighbour sampling.
- Why built: The dithered 1-bit look is the game's style, and drawing text into the same buffer kept one
  render path for everything on screen.
- Design: Text was filled into the low-resolution buffer at 7 to 12 px, then dithered and upscaled along
  with the art.
- Got right: The art read well: silhouettes, light shafts and the casket survive dithering because they are
  large shapes with clear edges.
- Where/why it failed: Text at 7 to 12 px had grey anti-aliased edges, and the dither turned those into
  scattered dots; after the 3x upscale the player reported it too pixelated to read.
- Fix: Queue each text call with its position through the current canvas transform, skip the 1-bit buffer,
  and draw the queue at full resolution after the upscale, in the same two inks with an outline.
- Why this fix: The style lives in the art, not the letters; capturing the transform keeps text attached to
  scaled scenes, and two-ink colouring keeps it inside the 1-bit palette.
- Rule of thumb: Never dither small text: render it in a separate crisp layer over the dithered art, mapped
  through the art's transform and drawn in the same palette.
- Provenance (verified/assumed): Verified first-hand: a player report plus before and after screenshots of
  the game at phone size.
- Composed: film/E21, brain/E1
- Link: Demo-disc commit "The Last Note: readable text and a how-to card before every funeral"; session_011p52L2CkFXcsYRwjDu6tG9

## E15 — dispatcher must board where it stands
- Date: 2026-10-15
- Project: pappydapimp69/Demo-disc
- Tags: [elevator][dispatch][state]
- What: The automatic dispatch rules in Going Up, an elevator game, where a lift picks its next floor from
  calls and its riders' destinations, and people board only when the doors open on arrival.
- Why built: A dispatch rule must never pick the floor the lift is already standing at, or it loops opening
  its doors forever, so the current floor was filtered out of the candidate floors.
- Design: Candidates were the floors with waiting people plus the riders' destinations, minus the current
  floor, and boarding happened only inside the arrival handler.
- Got right: Filtering the current floor stopped the door loop, and a full lift was restricted to its riders'
  floors so it no longer chased calls it could not take.
- Where/why it failed: On the morning-rush level everyone waits at the lobby, where the lift starts; the lobby
  was filtered out and nothing else was requested, so the lift never moved and delivered nobody (0 in the
  game, 0 of 40 in the sandbox).
- Fix: Before choosing a target, if people are waiting at the lift's own floor and it has room, open the doors
  and board them there; then pick the next floor.
- Why this fix: It keeps the never-target-your-own-floor rule that prevents the loop, and serves the one case
  that rule hides: work that is already at the lift.
- Rule of thumb: A dispatcher that never targets its own floor must board people there explicitly, or the
  floor where it stands goes unserved (0 of 40 delivered when everyone waits at the lift).
- Provenance (verified/assumed): Verified first-hand in the game (0 delivered on the rush level before the
  fix, finished after) and by the sandbox below.
- Composed: ideas:ELEVATOR-CONTROL/dispatch, brainwork/E270
- Sandbox: sandboxes/2026-10-15__dispatcher-must-board-where-it-stands.py
- Prediction: Without boarding at its own floor the lift delivers 0 while the lobby queue grows; with it,
  nearly everyone is delivered.
- Observed: RESULT: PASS 0 delivered and 40 stuck without it; 39 delivered and 0 waiting with it.
- Scenarios: 1) no boarding at the current floor; 2) boarding at the current floor first, the case built to
  BREAK the claim that filtering alone is enough
- Link: Demo-disc commit "Add Going Up: the ad is a tower stacker, the game runs the lifts inside it"; session_011p52L2CkFXcsYRwjDu6tG9
- Cited-by: 2026-10-17 · projects/pappydapimp69__demo-disc.md#E43 · compatible · no sandbox · observed No parking 21 s longest wait; parking (9,6) 28 s, (9,9) 30 s, (6,3) 24 s. Refuted. · games/goingup/game.js LUNCH BELL; session_011p52L2CkFXcsYRwjDu6tG9

## E14 — cosmetic rolls need their own stream
- Date: 2026-10-15
- Project: pappydapimp69/Demo-disc
- Tags: [determinism][testing][gamedev]
- What: Adding a daughter character's speech lines to The Boss's Bad Day, a fight whose hit rolls come from a
  seeded RNG and whose tests assert win or fail outcomes for scripted players on every level.
- Why built: The lines needed variety (a random pick from a pool each time she reacts), and the easy way is
  to draw that pick from the game's existing seeded stream.
- Design: The lines got their own seeded stream (derived from the level seed), separate from the stream that
  rolls the knight's hits, so flavour rolls can never move gameplay rolls.
- Got right: With a separate stream the fight replayed identically: every existing win and fail test for the
  scripted players passed unchanged after the lines were added.
- Where/why it failed: In the sandbox, drawing the line picks from the gameplay stream changed 30 of 30
  seeded fights, because every flavour draw shifts every later hit roll; outcome tests would have flipped for
  reasons unrelated to the change.
- Fix: Give cosmetic randomness (dialogue, particles, idle animations) its own seeded stream, and keep the
  gameplay stream for rolls that decide outcomes only.
- Why this fix: It removes the coupling instead of re-tuning tests after each content change, and both
  streams stay seeded, so replays and saves remain exact.
- Rule of thumb: Cosmetic rolls need their own seeded stream: sharing the gameplay stream changed 30 of 30
  seeded fights the moment flavour lines were added.
- Provenance (verified/assumed): Verified first-hand by the sandbox below and by the game's unchanged test
  results after the lines shipped.
- Composed: dog/E12, test/E2
- Sandbox: sandboxes/2026-10-15__cosmetic-rolls-need-their-own-stream.py
- Prediction: On the shared stream at least 25 of 30 seeded fights change; on a separate stream none do.
- Observed: RESULT: PASS shared stream changed 30/30 fights; own seeded stream 0/30.
- Scenarios: 1) no flavour; 2) flavour on the shared stream; 3) flavour on its own stream, built to BREAK
  the claim that seeding alone keeps fights reproducible
- Link: Demo-disc commit "The Boss's Bad Day: your daughter reacts from her cage"; session_011p52L2CkFXcsYRwjDu6tG9
- Cited-by: 2026-10-15 · projects/pappydapimp69__demo-disc.md#E37 · compatible · no sandbox · session https://claude.ai/code/session_0165jfQbaW5xxNCE9kqoELSQ, commit e4e4a0c (Pappydapimp69/Demo-disc)

## E13 — solver and game must consume the deck the same way
- Date: 2026-10-15
- Project: pappydapimp69/demo-disc
- Tags: [gamedev][testing][puzzle]
- What: A TriPeaks solitaire game picked seeds whose deals a depth-first solver proved winnable, then a test
  replayed the solver's move list in the real game through the test hook.
- Why built: Random TriPeaks deals are often unwinnable; the demo needed every season to be clearable, so the
  game only accepts deals the solver can finish.
- Design: Solver state is (removed mask, stock index, waste card) and draws stock[sp] moving forward; the game
  kept its stock as an array and drew from it on tap.
- Got right: Replaying the solver's exact path in the live game instead of asserting the solver returned a path.
- Where/why it failed: All three solved seasons stalled with 15-24 cards left: the game drew with stock.pop()
  (from the end) while the solver drew stock[sp] (from the front), so after the first draw the game's waste
  card differed from the one the solution assumed.
- Fix: The game draws with stock.shift(), the same order the solver uses; all three replays then cleared the
  board (40, 51 and 49 moves).
- Why this fix: The deal is only proven winnable under the solver's state transitions; the game must apply
  the identical transitions or the proof says nothing about what the player gets.
- Rule of thumb: When a solver certifies generated content, test by replaying its move list through the real
  game; any difference in how state is consumed (draw order, tie-breaks) silently voids the certificate.
- Provenance (verified/assumed): verified first-hand: replays stalled before the fix and cleared after it.
- Composed: N/A
- Link: pappydapimp69/demo-disc commit ea9df17; session_0169rjPqYDYawkbeTUEzoNKo

## E12 — particle spacing pushes through walls
- Date: 2026-10-15
- Project: pappydapimp69/demo-disc
- Tags: [gamedev][physics][simulation]
- What: A draw-physics water game used circle particles colliding with line segments (drawn lines and the
  glass walls) plus a neighbour-spacing pass for cheap incompressibility.
- Why built: The player draws ramps that steer water into a glass, so drops must slide along arbitrary
  polylines and pile up inside a cup to a fill line.
- Design: Integrate, resolve each drop against every segment, then push overlapping neighbours apart; one
  step per 60 Hz tick with a 700 px/s speed cap.
- Got right: Counting drops inside the cup polygon as the fill metric, and a spatial hash for the spacing pass.
- Where/why it failed: Water leaked through the glass: the spacing pass ran after collision and pushed drops
  across walls, and at 700 px/s a drop moved 11.7 px per tick against an 11 px contact radius.
- Fix: Two substeps per tick, resolve walls again after the spacing pass, and choose the push-out side from the
  drop's previous position; the glass then held water and all 4 levels' known solutions filled it.
- Why this fix: The constraint applied last wins, so walls must be the last constraint, and side-from-previous
  stops a deep overlap from being resolved onto the wrong side.
- Rule of thumb: In particle fluids with wall segments, resolve walls after any particle-particle pass and pick
  the side from the previous position; keep per-substep travel below the contact radius.
- Provenance (verified/assumed): verified first-hand: leaking before, all four solution runs filling after.
- Composed: N/A
- Link: pappydapimp69/demo-disc commit f200bef; session_0169rjPqYDYawkbeTUEzoNKo

## E11 — cache static canvas patterns
- Date: 2026-10-15
- Project: pappydapimp69/demo-disc
- Tags: [rendering][canvas][performance]
- What: A ukiyo-e solitaire game redrew its wood-grain paper texture and the seigaiha wave-scale pattern on
  all 28 card backs from scratch every frame.
- Why built: The woodblock style needs a textured paper background and patterned card backs; the drawing kit
  was first written for a deterministic film renderer where per-frame cost did not matter.
- Design: Paper grain is 70 wavy strokes; each card back draws hundreds of concentric arcs, clipped.
- Got right: Sharing one drawing kit between the ad film and the playable game kept them visually identical.
- Where/why it failed: In the game the same test run (200 render calls) took 14.6 s, about 70 ms per frame,
  far below 60 fps, because static art was being rebuilt every frame.
- Fix: Paint each static layer once into an offscreen canvas keyed by its size and blit it with drawImage;
  the same 200-call run dropped to 5.3 s (2.7x faster) with identical output.
- Why this fix: The paper and card backs never change, so caching costs nothing visually and removes the
  heaviest per-frame work without changing the look.
- Rule of thumb: Code reused from an offline film renderer into a real-time game must have its static layers
  cached to offscreen canvases; per-frame cost that is free in a film is a frame-rate bug in a game.
- Provenance (verified/assumed): verified first-hand: timed the same 200-render test run before and after.
- Composed: N/A
- Link: pappydapimp69/demo-disc commit ea9df17; session_0169rjPqYDYawkbeTUEzoNKo

## E10 — nearest first hides starvation in the mean
- Date: 2026-10-15
- Project: pappydapimp69/Demo-disc
- Tags: [elevator][dispatch][starvation]
- What: Going Up, a game where you run the lifts in an office tower; its AUTO switches run nearest-first or
  a one-direction sweep, and stars go by the longest wait, not the average.
- Why built: To make the elevator kernel playable: nearest-first keeps busy floors happy and strands the
  far floor; a sweep bounds the wait. The level design needed to know at which load that shows.
- Design: One lift, 9 floors, busy floors 0 to 3 plus a top-floor caller for 10 percent of people, four
  loads from 0.4 to 1.1 people per second, six seeds each, with longest and mean wait measured.
- Got right: The sweep's longest wait stayed bounded at every load (13 to 35 s), and in the game the
  nearest rule stranded the top floor until someone took the stairs while the sweep's longest was 12 s.
- Where/why it failed: My prediction that the rules tie at light load was wrong: nearest-first's longest
  wait was already 2.6 times the sweep's (33 against 13 s) while mean waits differed by only 0.5 s, and it
  grew to 577 s at 1.1 per second.
- Fix: Judge dispatch rules by the longest wait (or a high percentile), at light load as well as near
  capacity; the game scores stars by the longest wait for this reason.
- Why this fix: The mean averages the starved caller into a crowd of short trips, so it moves by under a
  second while one person waits half a minute or more; only a tail metric shows it.
- Rule of thumb: Nearest-first starvation shows at light load too, but only in the tail (2.6x longest wait,
  0.5 s apart on the mean); measure the longest wait, not the average.
- Provenance (verified/assumed): Verified first-hand with the sandbox below and the Going Up game tests.
- Composed: ideas:ELEVATOR-CONTROL/dispatch, brainwork/E270, ideas:QUEUEING/capacity-planning
- Sandbox: sandboxes/2026-10-15__nearest-first-hides-starvation-in-the-mean.py
- Prediction: Written first: the rules tie on longest wait at light load and nearest-first only separates
  near capacity. Refuted on the first run; the claim was restated from what the run showed.
- Observed: RESULT: PASS at 0.4 per s longest wait 32.8 against 12.6 s with means 3.2 and 2.7 s; at 0.9
  per s 394 against 22 s; at 1.1 per s 577 against 35 s.
- Scenarios: 1) 0.4 per s, built to BREAK the starvation claim at light load; 2) 0.7; 3) 0.9; 4) 1.1
- Link: Demo-disc commit "Add Going Up: the ad is a tower stacker, the game runs the lifts inside it"; session_011p52L2CkFXcsYRwjDu6tG9

## E9 — elmsley binary is also shortest
- Date: 2026-10-15
- Project: pappydapimp69/Demo-disc
- Tags: [card-magic][permutation][exhaustive]
- What: Faro, a puzzle game where the only moves are perfect in and out faro shuffles, with par counts
  for sending the ace to a target slot, restoring a deck, and bringing a buried ace to the top.
- Why built: Par needs the fewest shuffles for each hand, and the canon gives Elmsley's binary rule for
  placing the top card but does not say whether that rule is also the shortest route.
- Design: Breadth-first search over a single card's position under the two faros, for every target
  position at deck sizes 8, 16, 32, 52 and 54, compared with the length of the binary rule.
- Got right: The binary rule landed the top card correctly at every position and every size tested, and
  the game's par for each hand matched the search exactly.
- Where/why it failed: Before checking, par could have been set from the binary rule alone; had a shorter
  route existed, players finding it would have beaten par, which would read as a bug.
- Fix: Compute par by search, and keep the binary rule as the explanation shown to the player, now that
  the search confirms the two agree.
- Why this fix: Each faro at most doubles the card's distance from the top, so no route can be shorter
  than the bit length; the search confirms this exhaustively instead of relying on that argument.
- Rule of thumb: Elmsley's binary rule is also the fewest faros for every position (n = 8 to 54), and any
  card returns to the top within 6 faros at 52.
- Provenance (verified/assumed): Verified first-hand by exhaustive search in the sandbox and by the game
  tests, which solve every hand at par.
- Composed: zanegpt/E11, ideas:CARD-MAGIC/faro-shuffle, one-faro-slip-only-disturbs-cards-below-it/E1
- Sandbox: sandboxes/2026-10-15__elmsley-binary-is-also-shortest.py
- Prediction: The binary rule is correct and no shorter route exists for any position.
- Observed: RESULT: PASS correct and shortest at every position for n = 8, 16, 32, 52, 54; worst case back
  to the top 3, 4, 5, 6, 6 faros.
- Scenarios: 1) n=8; 2) n=16; 3) n=32; 4) n=52; 5) n=54, the size where out-faro restore takes 52, built
  to BREAK any reliance on the 52-card case
- Link: Demo-disc commit "Add Faro: the ad is a find-the-ace casino, the game is a perfect-shuffle puzzle"; session_011p52L2CkFXcsYRwjDu6tG9
- Audited: 2026-10-15 · pass · Bridge recheck. E9 cites one-faro-slip-only-disturbs-cards-below-it/E1 in Composed, and that entry's numbers were failed by a rebuild (0.75 home and 0.92 landing against its half and 4 in 5). E9's claim does not depend on it: every statement in E9 is about PERFECT faros (binary rule correct, no shorter route by breadth-first search, worst case back to the top), and the stored sandbox never models a slip or imports anything from the slip entry, so the citation is context, not a premise, and the claim survives without it. I read the entry and sandboxes/2026-10-15__elmsley-binary-is-also-shortest.py and reran it: PASS, 0 wrong and 0 shorter routes at n = 8, 16, 32, 52, 54, worst case to the top 3, 4, 5, 6, 6. The model does not assume its answer: Elmsley placement and the BFS shortest path are computed separately and compared. Its one hand-written piece is the single-card position formula where(), so I checked it against a real deck interleave (split, alternate cards, in and out) at all five sizes: 0 mismatches over every card and both faros. Scope: the Rule of thumb says n = 8 to 54, which reads as every size, but only five sizes were run; I extended the stored functions to every even n from 4 to 54 and found 0 failures, so the even-size reading holds; odd deck sizes (where an in or out faro is not a clean half split) remain untested and the rule should say even n. The game par claim rests on the game's own tests, which I did not run. The slip entry's dispute should not propagate here: E9 says nothing about imperfect faros. · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 3 pass 3
- Reverified: 2026-10-15 · pass · sandboxes/2026-10-15__rebuild-faro-binary-rule-minimal-routes.py · observed RESULT: PASS even n 8..54 rule-wrong 0 and BFS-shorter 0 of 744 targets; worst to-top n=52 6, n=8 3; odd-n mismatches 23 · Rebuilt from the claim only. My fixture tracks a single card's position through in and out faros and runs breadth-first search over the n positions for every even n from 8 to 54 (744 start-at-top targets), comparing the shortest route with the binary recipe (target position in binary, high bit first, 1 means in, 0 means out). Result: the recipe landed on the target every time and BFS never found a shorter route (0 of 744). My first run showed 24 phantom mismatches that were my own bug (target 0 was given one out-shuffle instead of zero moves); fixing that left 0. The worst shortest route from any position to the top at n=52 is 6, matching the claim, and 3 at n=8. As a break case the same recipe gave 23 mismatches on odd decks, so the claim is correctly limited to even n. Differences from the original: single-card BFS rather than the game's par table, and I did not check the restore-deck or buried-ace par counts, only the position routes and the to-top bound. · session_01A5ZkeepCfk7CHTSxS7qQ4k

## E8 — bleach saturation makes glances costly
- Date: 2026-10-15
- Project: pappydapimp69/Demo-disc
- Tags: [gamedesign][dark-adaptation][survival]
- What: Embers, a night-watch game where looking at the campfire warms you but costs night sight (a glance
  about 2 night-minutes, a stare saturating near 17), and you can only drive off what you can see.
- Why built: To turn the dark-adaptation kernel into a choice, so the player has to decide how often and how
  long to look at the fire, against cold that forces them to look sometimes.
- Design: A stdlib model of the same rules (cost saturates with look length, a new look takes the max of the
  old debt, recovery one night-minute per second, cold 3.4 per s, warming 8 per s), run for look lengths
  from 0.5 s to 12 s, plus the game's own autopilots on five nights.
- Got right: Saturation makes short glances the priciest warmth: 0.57 night-minutes of sight per warmth
  point at 0.5 s against 0.16 at 12 s, and in the game only-glancing froze on the coldest night.
- Where/why it failed: The longest blind stretch is not monotonic in look length: 2.5 s looks gave 5.5 s,
  12 s stares 23 s, but 5 s looks gave 85 s, because they come back before the debt clears and keep night
  sight under half all night. My prediction had only the two ends and missed the trap in the middle.
- Fix: Pick a look length together with its spacing: either short looks spaced past their recovery time
  or rare long ones, and test the middle explicitly; in the game, 2.5 s looks taken only when nothing is
  close survived all five nights.
- Why this fix: What decides blindness is whether the debt pays down between looks, which depends on look
  length and spacing together; the per-warmth cost alone points at long stares, which leave a stretch
  longer than a threat's 12 s approach.
- Rule of thumb: With a saturating cost, short looks are dearest per unit of benefit, but the worst choice
  is a mid-length look repeated before its debt clears (5 s here: half-blind all night).
- Provenance (verified/assumed): Verified first-hand with the sandbox below and the Embers game tests
  (glance froze, stare lost all three lives, medium looks survived every night).
- Composed: ideas:DARK-ADAPTATION/campfire, night-sight-cost-saturates-after-ten-seconds/E1
- Sandbox: sandboxes/2026-10-15__bleach-saturation-makes-glances-costly.py
- Prediction: 0.5 s glances freeze and cost over 3 times more sight per warmth than 12 s stares; 2.5 s
  looks stay warm with a blind stretch under 12 s; 12 s stares leave one of 12 s or more.
- Observed: RESULT: PASS 0.57 against 0.16 min per point, glances froze at 72 s, 2.5 s looks' longest
  blind stretch 5.5 s, 12 s stares 23.3 s; unpredicted: 5 s looks 85.3 s.
- Scenarios: 1) 0.5 s glances; 2) 1 s; 3) 2.5 s; 4) 5 s, the middle case that broke the expected monotonic
  trend; 5) 12 s stares
- Link: Demo-disc commit "Add Embers: the ad is an idle fire tapper, the game is a night watch where the fire costs your eyes"; session_011p52L2CkFXcsYRwjDu6tG9

## E7 — sky cue beats clearing seeking in woods
- Date: 2026-10-15
- Project: pappydapimp69/Demo-disc
- Tags: [gamedesign][wayfinding][audio]
- What: Veer, a game where you find a lost friend in fog by whistling and listening, built on two canon
  kernels at once: heading noise walks people in circles without a sky cue, and forest cuts a whistle's
  range from about 1.3 km to about 150 m while clearings carry it.
- Why built: The acoustics kernel's design consequence is that clearings carry a whistle several times
  farther, so heading for a clearing before whistling looked like the key skill for deep woods, and a
  level was built around that advice.
- Design: The same physics in a stdlib sandbox: 23 dB per 100 m forest, a friend 520 m away and out of
  earshot, 40 seeds, two strategies (home on the answer; or go to the nearest clearing first when nothing
  answers), each with and without a sky cue, plus in-earshot and open-ground controls.
- Got right: The sound and drift models behaved as the kernels say: deep forest cost 23.0 dB per 100 m,
  a whistle was heard at 140 m but not 180 m there, and with no sun a straight walk turned 138 degrees.
- Where/why it failed: Clearing-first barely helped: 22 of 40 found versus 18 of 40 for plain homing in
  fog. The game's own autopilot pass (one seed) had shown homing failing and clearing-first winning,
  which overstated the effect; the long blind leg toward the clearing drifts off course, so many walkers
  never reach it.
- Fix: Treat the sky cue, not the clearing, as the main lever: with a sun to hold a heading, plain
  homing found the friend 40 of 40 times. Design woods levels around whether the player can hold a
  heading; treat clearings as a modest speed-up, and test any strategy claim over many seeds.
- Why this fix: Out of earshot, every strategy depends on walking a long stretch without feedback, and
  drift is what makes that fail; a heading cue fixes the walk itself, while a clearing only helps the
  walkers who happen to reach it.
- Rule of thumb: In woods out of earshot, holding a heading matters far more than seeking a clearing
  (sky cue 18 to 40 of 40 finds; clearing-first only 18 to 22); judge a strategy over many seeds, not
  one level pass.
- Provenance (verified/assumed): Verified first-hand by the sandbox below (40 seeds per case) and by the
  Veer game tests; real hikers' drift rates and the 23 dB per 100 m forest figure come from the kernels.
- Composed: ideas:WAYFINDING/veering/without-a-sky-cue, ideas:OUTDOOR-ACOUSTICS/forest-propagation, seven/E91
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-15__sky-cue-beats-clearing-seeking-in-woods.py
- Prediction: Written before the first run: clearing-first would find the friend at least 10 more times
  out of 40 than homing in deep woods out of earshot. That prediction was wrong (+4).
- Observed: RESULT: PASS a sky cue lifts homing from 18/40 to 40/40, while clearing-first adds only
  4/40 under drift; in earshot both 40/40, in the open both 40/40, with the sun clearing-first is only
  faster (median 178 s against 192 s).
- Scenarios: 1) deep woods, fog, out of earshot; 2) same with a sky cue; 3) friend already in earshot;
  4) open ground, built to BREAK the clearing claim (no forest, so clearings cannot matter)
- Link: Demo-disc commit "Add Veer: the ad is a draw-the-path puzzle, the game is a foggy walk you play by ear"; session_011p52L2CkFXcsYRwjDu6tG9

## E6 — vacuous done predicate hangs deal
- Date: 2026-10-15
- Project: pappydapimp69/Demo-disc
- Tags: [algorithm][procgen][state]
- What: A sort puzzle (stickmen in jars) dealt by rejection sampling: reshuffle until no jar starts out
  already sorted and the solver can finish it. The game page hung on load.
- Why built: A deal that starts with a jar already solved is a free move and looks broken, so the deal
  rejects any board where some jar is already done.
- Design: The same done(jar) predicate serves the win check and the deal filter. For the win check an
  empty jar must count as done, since a solved board has empty jars.
- Got right: Reusing the win predicate kept one definition of done for the solver, the win check and the
  per-jar star, so the three could never disagree about what sorted means.
- Where/why it failed: Every deal includes empty jars, and done() is true for an empty jar, so the filter
  rejected every board: 0 of 2000 shuffles accepted, and the unbounded for(;;) loop froze the page before
  the first frame.
- Fix: Filter with any(jar is non-empty and done(jar)), keep done() as is for the win check, and give any
  rejection loop an attempt cap so a bad filter fails loudly instead of hanging.
- Why this fix: The win check and the deal filter ask different questions; the empty case is the only
  place they differ, and naming it explicitly at the filter keeps the shared predicate correct for winning.
- Rule of thumb: A predicate that is vacuously true for empty containers must not be reused as a
  rejection filter over states that always contain empties; check non-empty explicitly and cap the loop.
- Provenance (verified/assumed): Verified first-hand: the page timed out in Playwright before the fix and
  booted in 73 ms after it, and the sandbox reproduces 0 accepted vs about 99 percent accepted.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__vacuous-done-predicate-hangs-deal.py
- Prediction: With 2 empty jars the naive filter accepts 0 deals at every size; the fixed one accepts
  most; with 0 empty jars the two agree.
- Observed: RESULT: PASS naive accepts 0/2000 at 3, 5 and 7 colours; fixed accepts 1972, 1988 and 1998;
  with 0 empties both accept 1972.
- Scenarios: 1) 3 colours; 2) 5 colours; 3) 7 colours; 4) no empty jars, built to BREAK the claim
  (the bug should vanish)
- Link: Demo-disc commit "Stick Swarm: the game is now a stickman sort puzzle, not the ad"; session_011p52L2CkFXcsYRwjDu6tG9

## E5 — stage change input pause
- Date: 2026-10-15
- Project: pappydapimp69/Demo-disc
- Tags: [gamedev][input][ux]
- What: A barber game made of short tap-to-advance stages (cape on, pump the chair, spray, cut, tidy up,
  result). Players reported accidental taps counting on the next stage.
- Why built: Each ritual step is a few quick taps, so players tap in a rhythm and keep tapping for a moment
  after the step they were working on has already finished and the next one has appeared.
- Design: Model a player tapping at a steady interval who only stops once they notice the stage changed
  (reaction time), and count taps that land on the next stage, with and without an input pause.
- Got right: An input pause on every stage change that is longer than human reaction time (0.6 s) dropped
  leaked taps to zero, while the next prompt fades in so the pause reads as intentional, not as lag.
- Where/why it failed: With no pause, exactly one tap leaked into every stage change (5 of 5). A pause
  shorter than reaction time (0.15 s) still leaked 5 of 5, so a token debounce does not fix it.
- Fix: On every stage change call one pause() that ignores pointer-down and key-down until t + 0.6 s and
  also clears held state (pointer down, held buttons); moves and releases still pass through.
- Why this fix: The leak is set by reaction time, not by how fast the player taps, so the pause must be
  measured against reaction time; one shared function means no transition can forget to pause.
- Rule of thumb: After a tap-driven stage change, ignore new presses for longer than reaction time
  (about 0.5 s); a pause shorter than that still lets one tap per change through.
- Provenance (verified/assumed): Verified first-hand: sandbox model below, plus a Playwright test in the
  game showing a tap right after load is ignored and a tap after the pause counts. The 0.3 s reaction
  figure is a typical value I assumed, not measured on players.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__stage-change-input-pause.py
- Prediction: No pause leaks at least one tap per step change; a 0.6 s pause leaks none; a 0.15 s pause
  still leaks.
- Observed: RESULT: PASS no pause leaks 1 tap per step change (5 of 5); 0.6 s pause leaks 0 (also 0 for a
  fast tapper with 0.45 s reaction); 0.15 s pause leaks 5.
- Scenarios: 1) no pause; 2) 0.6 s pause; 3) fast tapper with slow reaction; 4) pause shorter than
  reaction, built to BREAK the fix
- Link: Demo-disc commit "Hair Salon: ignore taps for a beat after every stage change"; session_011p52L2CkFXcsYRwjDu6tG9

## E4 — iframe audio starts on load
- Date: 2026-10-15
- Project: pappydapimp69/Demo-disc
- Tags: [audio][browser][gamedev]
- What: A disc menu opens each game in a same-origin iframe when the player taps a tile. A game's
  music only started on the first touch inside the game, which players heard as a late start.
- Why built: The usual autoplay rule is to create or resume the AudioContext inside a tap handler
  (test#E9), so the game waited for its own first tap before starting any sound.
- Design: Call the audio unlock once as the game script loads, and keep the in-game tap unlock as a
  fallback for when the game is opened on its own with no tap behind it.
- Got right: Keeping the tap fallback means the game still gets sound when opened directly, and the
  load-time attempt is fire-and-forget, so it never blocks start (dog#E1).
- Where/why it failed: Waiting for an in-game gesture threw away the activation the player had just
  given: the tap on the menu tile that opened the iframe already allows audio in that frame.
- Fix: Create and resume the AudioContext at game load inside the iframe; start the music scheduler
  as soon as its state reads running, and also on the first in-game tap if it does not.
- Why this fix: Measured with Chromium in gesture-required autoplay mode, the iframe's AudioContext
  read running right after a menu tap, with no tap inside the game, so music can begin with the scene.
  Only Chromium was measured; Safari and Firefox rest on their documented activation rules, which is
  why the tap fallback stays.
- Rule of thumb: A same-origin iframe opened by a user tap can start Web Audio at load; try at load,
  and keep the tap-to-unlock path only as the fallback for direct opens.
- Provenance (verified/assumed): Verified first-hand in headless Chromium with the gesture-required
  autoplay policy: the iframe's context state read running after the menu tap.
- Composed: test/E9, dog/E1
- Prediction: After a tap on the menu tile, the game iframe's AudioContext reads running with no tap
  inside the game.
- Observed: Playwright, Chromium with --autoplay-policy=user-gesture-required: tile 3 tapped, iframe
  Engine.Audio.ctx.state printed running.
- Link: Demo-disc commit "Hair Salon: louder music and ASMR, and the soundscape starts as the game opens"; session_011p52L2CkFXcsYRwjDu6tG9

## E3 — held input survives tool switch
- Date: 2026-10-15
- Project: pappydapimp69/Demo-disc
- Tags: [gamedev][input][state]
- What: A barber game where clipper guards leave different hair lengths. A test autopilot cut the long
  zone first, then swapped to a shorter guard for the next zone, and the long zone came out too short.
- Why built: Cutting longest guard first should make zones independent, since a shorter guard only
  needs to touch its own zone; the autopilot plans brush positions that never touch a longer zone.
- Design: The clipper applies every tick while the pointer is down. The autopilot changed the tool on
  one tick and moved the pointer on the next, leaving the pointer down at the last long-zone position.
- Got right: The plan itself was sound: the brush-position check refused every position touching a
  zone that wanted longer hair, which is why the leak looked impossible at first read.
- Where/why it failed: The held down state survived the tool switch, so for one tick the new short
  guard was applied at the old long-zone spot: 67 top strands cut to 6 mm instead of 19 mm (27 in the
  smaller sandbox), with nothing in the planner able to see it.
- Fix: Clear the held press whenever the tool changes, so the next application needs a fresh press
  or a fresh planned position.
- Why this fix: The bug is a state leak across a mode change, not a planning error; releasing on switch
  removes it for the autopilot and for a player whose finger stays down while tapping the tray.
- Rule of thumb: When a held input applies a tool every tick, release the hold on every tool switch; a
  press that survives the switch applies the new tool at the old position.
- Provenance (verified/assumed): Verified first-hand in the game (top zone dropped to 0.89 match, back
  to 1.00 after the fix) and in the sandbox; that a real player hits it the same way is assumed.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__held-input-survives-tool-switch.py
- Prediction: A down state that survives the switch cuts some long-zone strands short; releasing on
  switch cuts none.
- Observed: RESULT: PASS held down across the switch cut 27 strands short (same at 1 and 3 ticks);
  release on switch cut 0.
- Scenarios: 1) down survives, 1 tick; 2) down survives, 3 ticks; 3) release on switch; 4) release on
  switch, 3 ticks, built to BREAK the fix
- Link: Demo-disc commit "Hair Salon: real haircuts with clipper guards and a goal per customer"; session_011p52L2CkFXcsYRwjDu6tG9

## E2 — match3 policy tests dont separate
- Date: 2026-10-15
- Project: pappydapimp69/demo-disc
- Tags: [gamedev][testing][design]
- What: Completability tests for a seeded match-3 used the same pattern as the other demos: a greedy
  "best" autopilot must win and a "worst" autopilot must lose each level.
- Why built: The disc's pin puzzle and crowd runner both proved levels fair by showing good play wins
  and bad play loses, so the match-3 reused that harness.
- Design: Seeded RNG per level; autopilot sorts valid swaps by immediate cleared-gem count, best takes
  the largest, worst the smallest; levels were played with an unreachable target to measure scores.
- Got right: Measuring raw scores per policy before picking targets, instead of guessing targets and
  tuning until tests pass.
- Where/why it failed: Policies did not separate: worst beat best on 2 of 3 levels (5440 vs 4000,
  3880 vs 2180) because cascade refills dominate the score, so no target makes best win and worst lose.
- Fix: Set targets under the best policy's measured scores, keep "good play wins" per level, and test the
  rules directly instead: an invalid swap snaps back and costs no move, the dealt board has a move, and
  running out of moves short of target loses.
- Why this fix: A worst-play-loses test only means something when skill dominates variance; in a
  cascade-heavy match-3 it would be a coin flip pinned to one seed.
- Rule of thumb: Before asserting "bad play loses", measure whether the policies actually separate; when
  chance (cascades, refills) dominates, test the rules and the win path, not a skill gap that is not there.
- Provenance (verified/assumed): verified first-hand: measured 6 policy runs, then 21 checks passing.
- Composed: N/A
- Link: pappydapimp69/demo-disc commit 348e45f; session_0169rjPqYDYawkbeTUEzoNKo
- Cited-by: 2026-10-15 · projects/pappydapimp69__demo-disc.md#E35 · compatible · no sandbox · session https://claude.ai/code/session_0165jfQbaW5xxNCE9kqoELSQ, commit e4e4a0c (Pappydapimp69/Demo-disc)

## E1 — test step hook must own the clock
- Date: 2026-10-15
- Project: pappydapimp69/demo-disc
- Tags: [gamedev][harness][process]
- What: A Playwright smoke test drove a fixed-timestep canvas game through a window.__game.step(n)
  hook, while the game's own requestAnimationFrame loop kept advancing the same simulation in real time.
- Why built: Tests needed to step the physics deterministically to prove each level is winnable by its
  solution and lost by its trap, without real-time waits.
- Design: Integer microsecond accumulator loop driven by rAF, plus a step(n) hook that calls update()
  n times directly. Both paths mutated the same state.
- Got right: Fixed timestep on an integer clock, so tick counts never depended on frame rate, and the
  hook let 26 completability checks run in seconds.
- Where/why it failed: One level intermittently never finished (state stayed play) after a slow
  screenshot: real-time rAF ticks interleaved with the stepped ticks between evaluate() calls, so the
  pin timing relative to the physics varied run to run. Passed on rerun, so it looked like a flake.
- Fix: The first step() call switches the engine to manual mode; the rAF loop keeps rendering but zeroes
  its accumulator, so only the test advances the simulation. Three consecutive full runs passed.
- Why this fix: It removes the second clock instead of widening tick budgets, which would only hide the
  race; players never call step(), so normal play is unchanged.
- Rule of thumb: When a test hook steps a game simulation, the hook must take exclusive ownership of the
  clock; a still-running real-time loop turns deterministic tests into timing-dependent flakes.
- Provenance (verified/assumed): verified first-hand: failure observed once, root-caused to the dual
  clock, fixed, then 3 consecutive full suite passes.
- Composed: N/A
- Link: pappydapimp69/demo-disc commit a00a1f2; session_0169rjPqYDYawkbeTUEzoNKo
- Cited-by: 2026-10-15 · projects/local__particle-speed-cap-per-tick-fixed-step.md#E1 · compatible · sandboxes/2026-10-15__particle-speed-cap-is-per-tick-and-only-guards-a-fixed-step.py · observed RESULT: PASS 4/4; fixed+accumulator clean at all rates; variable dt: 30fps (True, False), 10fps (True, False), hitch (True, False) (tunnelled, exploded) - no explosion anywhere, the cap clamps it · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto loop 3 pass 2 (edge demo-disc + brain), 2026-10-15
