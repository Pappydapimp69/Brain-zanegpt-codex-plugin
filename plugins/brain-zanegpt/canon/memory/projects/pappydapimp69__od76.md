# Pappydapimp69/OD76 — lessons

Project: Pappydapimp69/OD76. Newest first.

---

## E16 — bank reset progression on personal bests
- Date: 2026-09-29
- Project: Pappydapimp69/OD76
- Tags: [game-design][progression]
- What: A run-reset companion level now converts only newly reached all-time-high levels into permanent endurance for later arena runs.
- Why built: A fixed fatigue ceiling made every arena attempt terminate around the same stage, so repeated runs produced resources but did not make the companion better at the arena activity itself.
- Design: The temporary level still resets every run, while a saved personal-best level grants a fixed endurance increase for each newly crossed level only after the run ends.
- Got right: Banking at run end preserves the intended first-run wall, makes later stage records feel earned, and gives the temporary level system permanent meaning without adding a manual allocation screen.
- Where/why it failed: A fixed ceiling created identical future limits, while rewarding every repeated level would allow safe early-stage repetition to farm permanent capacity without setting a stronger record.
- Fix: Compare the completed run's level against the saved all-time best, bank only the positive difference, and apply the resulting capacity beginning with the next run.
- Why this fix: Personal-best gating aligns permanent growth with actual forward progress, preserves the reset-run rhythm, and closes the repeatable low-risk farming vector.
- Rule of thumb: When temporary run progression should create permanent growth, bank only newly crossed personal-best thresholds and activate the reward on the following run.
- Provenance (verified/assumed): Verified first-hand in OD76 with save migration, repeated-level rejection, next-run capacity, reset behavior, and full regression coverage.
- Composed: N/A
- Link: session / B118 Arena Endurance
- Cited-by: 2026-10-15 · projects/local__personal-best-banking-stalls.md#E1 · compatible · sandboxes/2026-10-15__personal-best-banking-stalls-and-a-small-capped-per-run-term-does-not-unstick-it.py · observed RESULT: FAIL 1/3; k2 PB-only drought>20 in 20/20 seeds; k2 + capped per-run drought<10 in 0/20; k20 median PBs 25 of 80 runs · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 3 pass 2 (edge brainwork + od76), 2026-10-15

## E15 — threat pick by array order not arrival time
- Date: 2026-09-29
- Project: Pappydapimp69/OD76
- Tags: [game-design][ai]
- What: OD76's Cover arc scanned enemy shots with a time-ordered comparison, then scanned enemies and assigned the best threat unconditionally, so the last qualifying enemy in array order beat every shot.
- Why built: Cover spends on whatever actually hits the player first, so its arc must point at the soonest threat.
- Design: Two passes over shots and bodies, each qualifying by closest approach or lookahead window, feeding one chosen threat.
- Got right: Qualification rules were sound: a shot needs its closest approach inside the window, a body needs to be inside the lookahead.
- Where/why it failed: The second pass overwrote the first regardless of urgency, so the arc could point away from the thing that hit the player.
- Fix: Rank both passes on entry time, meaning when the thing reaches the player, on one shared 0.28s scale, and take the soonest.
- Why this fix: One shared time scale makes shots and bodies comparable, and leaves the qualification rules and Cover's cooldown untouched.
- Rule of thumb: When choosing among threats from different sources, compare them on one arrival-time scale, and never let a later scan overwrite an earlier pick.
- Provenance (verified/assumed): first-hand, read the commit message describing the ordering bug and the guards added. Three of five new guards were reported to fail against the old ordering.
- Composed: N/A
- Link: OD76 commit f4f6f45 (B85)

## E14 — spawn edges by perimeter not by label
- Date: 2026-09-29
- Project: Pappydapimp69/OD76
- Tags: [game-design][procgen]
- What: OD76 chose an enemy's entry edge with equal odds per edge label, so on a wide or tall screen the short edges got as many enemies as the long ones.
- Why built: Enemies enter from screen edges, and how visible each entry is depends on the edge length.
- Design: Sample entry positions by visible perimeter length instead of equal edge labels, keeping rosters, cadence, caps, HP, damage and drops unchanged.
- Got right: Deterministic edge-share checks at 390x844 portrait and 1280x720 landscape confirm the split follows the real screen shape.
- Where/why it failed: Equal labels crowd the short edges, so portrait phones saw uneven pressure compared with landscape.
- Fix: Weight each edge by its visible length, so entry density per screen pixel is even.
- Why this fix: It fixes the distribution at its source, per layout, without touching any balance number.
- Rule of thumb: When spawning around a rectangle, weight by edge length; equal odds per side over-concentrate on short sides.
- Provenance (verified/assumed): first-hand, read the commit and loop record, which report the two fixed viewport checks. The in-app browser ignored a mobile viewport override, so mobile coverage came from those regression dimensions.
- Composed: N/A
- Link: OD76 commit 914feac (B88)

## E13 — dead duplicate stylesheet is a trap
- Date: 2026-09-29
- Project: Pappydapimp69/OD76
- Tags: [maintenance][web]
- What: OD76 kept a styles.css that nothing referenced (not index.html, the build, the workflow or the tests), last synced with the inline style block 39 builds earlier.
- Why built: It began as the stylesheet and stayed after styles moved inline.
- Design: An inline style block shipped, while the orphan file was still in the repo root with a plausible name.
- Got right: Verifying its 72 selectors were a strict subset of the 87 shipping ones proved deleting it changed nothing rendered.
- Where/why it failed: A future editor would change styles.css expecting the game to change and see nothing happen, wasting time.
- Fix: Delete the file after checking it is referenced nowhere and its rules are a subset of what ships.
- Why this fix: The subset check turns a guess into evidence, and removing it eliminates the wrong place to edit.
- Rule of thumb: An unreferenced file that duplicates a live source of truth is a trap; prove it is dead, then delete it.
- Provenance (verified/assumed): first-hand, read the commit message giving the reference search and selector comparison. The deletion is described as cleanup only, with no rendering change.
- Composed: N/A
- Link: OD76 commit 59fdfcc

## E12 — announce on the latch not the threshold
- Date: 2026-09-29
- Project: Pappydapimp69/OD76
- Tags: [game-design][feedback]
- What: OD76's boss escalation praise fired the instant a boss crossed half health, but the pattern change only latches at the next attack boundary, up to a full cycle (about 4 to 5 seconds) later.
- Why built: A mid-fight cue tells the player the boss is escalating, so it should coincide with the change they can see.
- Design: Threshold check fired the cue; the phase-two flag was set later inside the boss cycle logic.
- Got right: Bosses without a phase two keep the immediate cue, since there is no later change to wait for.
- Where/why it failed: For up to a full cycle the game announced an escalation the player could not see, so the cue felt wrong.
- Fix: Hold the cue and fire it on the frame the phase-two flag turns true, for the boss keys that have a phase two.
- Why this fix: Tying the cue to the actual state change makes announcement and behaviour land together with no change to boss stats or timings.
- Rule of thumb: Fire feedback on the frame the state actually changes, not on the condition that will eventually cause it.
- Provenance (verified/assumed): first-hand, read the commit message with the predicted cycle lengths. Browser runs reported the cue 103 frames (4.12s) after the threshold, matching the predicted cycle.
- Composed: N/A
- Link: OD76 commit 9542876 (B84)

## E11 — survey prefills stats asks only opinions
- Date: 2026-09-29
- Project: Pappydapimp69/OD76
- Tags: [game-design][playtest]
- What: OD76 has an in-game playtest survey that fills play stats automatically and asks the player only the opinion questions.
- Why built: Playtest feedback needed both hard numbers (time, runs, highest stage, deaths, fatigue stops, training) and impressions, and players skip long forms.
- Design: Stats are tracked in localStorage and inserted into a plain-text report; the player answers opinion questions and copies or shares the text; unsent answers persist as a draft.
- Got right: Separating measured facts from opinions shortens the form and makes the numbers trustworthy, and the draft stops lost work.
- Where/why it failed: Asking players to recall stats gives unreliable numbers and a long form lowers completion.
- Fix: Log objective stats silently and prefill them, ask only what needs a human, and deliver as copyable plain text.
- Why this fix: Feedback arrives with real numbers attached, so an opinion like 'too hard' can be checked against the deaths and stage recorded.
- Rule of thumb: In a playtest form, measure whatever can be measured and ask humans only for opinions, with a saved draft.
- Provenance (verified/assumed): first-hand, read the survey commit description and the later commits that extended its stats. The report format is described there; a completed player report was not in view.
- Composed: N/A
- Link: OD76 commits B117 (c51fd2d, 437c2d3, f2efacf, 8a21e67, 0267d48, 3154a1d)

## E10 — mashing buys upgrades at stage end
- Date: 2026-09-29
- Project: Pappydapimp69/OD76
- Tags: [game-design][ux]
- What: The stage-end upgrade screen in OD76 opened while the player was still mashing buttons in combat, so cards were bought, selected or skipped by accident.
- Why built: Between stages the player picks Overdrive skills, boss rewards, Pip traits, heart skills and Sound Lab items, all permanent choices.
- Design: Pointer, keyboard and gamepad input is dropped for 0.7s after the screen opens, and every purchase needs a completed hold to confirm.
- Got right: A hold-to-confirm gate makes each purchase deliberate, and one shared rule covers every upgrade screen so behaviour is consistent.
- Where/why it failed: Instant-tap purchases at a moment of high input activity let panic mashing spend resources the player never chose.
- Fix: Ignore all input for 0.7s at screen open, require a completed hold to buy, and shorten a repeat hold on the same card to 0.7s instead of 1.8s, resetting on any other input.
- Why this fix: The open-delay removes the accident window and the shortened repeat hold keeps buying several levels of one upgrade quick, which a flat long hold would make tedious.
- Rule of thumb: Any screen that follows fast action needs an input dead-zone plus a deliberate confirm, and a shorter repeat path so the safety does not become a chore.
- Provenance (verified/assumed): first-hand, read the commit messages and their described behaviour for the delay, hold and repeat rules. The play feel comes from the commit authors' notes.
- Composed: N/A
- Link: OD76 commits B117 (c51fd2d, 437c2d3, f2efacf, 8a21e67, 0267d48, 3154a1d)

## E9 — empty need degrades recovery not blocks it
- Date: 2026-09-29
- Project: Pappydapimp69/OD76
- Tags: [game-design][systems]
- What: In OD76's ranch, a week that begins with hunger or cleanliness at 0 adds +10 fatigue each (+20 with both), while Pip can still always sleep.
- Why built: Needs already existed, but an empty need had little consequence, so players could ignore food and washing.
- Design: Empty needs raise fatigue at the start of the week, so the rest that week recovers less instead of being disabled.
- Got right: Pip is never locked out of resting, so a neglected ranch cannot dead-end into an unrecoverable state.
- Where/why it failed: A hard block on rest at 0 food would trap a player who has no food and cannot rest to recover; a pure warning changed nothing.
- Fix: Charge the penalty as extra fatigue when the week starts, before the drain, and leave rest always available.
- Why this fix: The penalty is felt and stacks with neglect, yet every state stays recoverable by ordinary play.
- Rule of thumb: Punish a depleted need by degrading recovery, and never by removing the only recovery action.
- Provenance (verified/assumed): first-hand, read the commit description of the week-start rule and the always-sleep guarantee. Play impact is reported by the commit author, not measured here.
- Composed: N/A
- Link: OD76 commits B117 (c51fd2d, 437c2d3, f2efacf, 8a21e67, 0267d48, 3154a1d)

## E8 — companion as ability turns off companion bonuses
- Date: 2026-09-29
- Project: Pappydapimp69/OD76
- Tags: [game-design][balance]
- What: OD76's Guardian ability was reworked so Pip becomes the Guardian: while Pip guards or is stunned he counts as away, and gathering, auto-fire, heart skills, Cover, Rally, Pip Catch and resonance all switch off.
- Why built: Guardian is a defensive hold, and the old version refilled shields on press while Pip kept fighting, stacking two large benefits.
- Design: Blocks charge once Pip returns to orbit, the flight home costs at most 10% HEAT, releasing gives a clean knockback pulse, and a break gives the same pulse then stuns Pip for 1.8s.
- Got right: Simulation drove the return cost cap, and switching off every Pip bonus while he is the Guardian keeps the ability's power bounded and its trade-off readable.
- Where/why it failed: With Pip still active during Guardian, the player got a defense refill and all companion bonuses at once, so the ability had no real cost.
- Fix: Make Pip the resource: he must fly home to charge it, is unavailable while guarding, and is stunned if it breaks.
- Why this fix: Tying the ability to the companion's presence makes the cost automatic and visible, without a separate cooldown number to tune.
- Rule of thumb: When an ability draws on a companion, mark the companion as away for its whole duration so his passive bonuses cannot stack on top.
- Provenance (verified/assumed): first-hand, read the commit series from the Guardian proposals to the shipped rework. The balance outcome comes from the commit authors' simulation notes and playtests.
- Composed: N/A
- Link: OD76 commits B117 (c51fd2d, 437c2d3, f2efacf, 8a21e67, 0267d48, 3154a1d)

## E7 — record only rewards stall or snowball
- Date: 2026-09-29
- Project: Pappydapimp69/OD76
- Tags: [game-design][progression]
- What: Designing how Pip's maximum fatigue grows so arena runs can reach deeper stages over many runs, using only "first time you reach a new level or stage" (record) rewards.
- Why built: A flat per-stage fatigue cost capped runs near stage 10, and players wanted gradual, non-farmable growth that still works past stage 50.
- Design: Simulated many runs with per-stage cost min(25, 4+stage), Pip levels from estimated XP, and record rewards paid on level or stage milestones, with the gain applied to the next run.
- Got right: Simulating instead of reasoning by feel exposed both failure modes before any code was written, and showed that a per-run source is needed alongside records.
- Where/why it failed: Level-only records paid out entirely in run 1 and every later run stalled at stage 11. A record reward of +1 per new stage number plus milestone bonuses exploded instead, past stage 999 by run 20.
- Fix: Add a source earned every run that scales with current max (5% of max, floored at 5 and capped at 25, paid when a run ends exhausted), and keep record rewards as bonuses on top.
- Why this fix: A record reward that pays less than a stage costs stalls, one that pays more snowballs; only a capped, percent-of-max per-run term gives steady growth without a free loop.
- Rule of thumb: Record-only progression rewards either stall or run away; pair them with a capped per-run term and simulate 40+ runs before shipping.
- Provenance (verified/assumed): first-hand, ran the simulations and read the fatigue code. XP per stage is an estimate, so exact stage numbers are approximate; the stall and runaway shapes held across every variant tried.
- Composed: N/A
- Link: session_01Ao86eEdRmKAAS2Tg8HmKWx
- Cited-by: 2026-10-15 · projects/local__personal-best-banking-stalls.md#E1 · compatible · sandboxes/2026-10-15__personal-best-banking-stalls-and-a-small-capped-per-run-term-does-not-unstick-it.py · observed RESULT: FAIL 1/3; k2 PB-only drought>20 in 20/20 seeds; k2 + capped per-run drought<10 in 0/20; k20 median PBs 25 of 80 runs · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 3 pass 2 (edge brainwork + od76), 2026-10-15

## E6 — perk gated on a second purchase reads as broken
- Date: 2026-09-29
- Project: Pappydapimp69/OD76
- Tags: [game-design][ux]
- What: OD76 Pip Sound packs have gameplay perks (shield recovery, damage, HEAT) that only activate at rank min(pack level, paired mix level), and pack descriptions describe audio that the pack does not add to the music.
- Why built: Packs pair with Sound Lab mixes so the two upgrade tracks reinforce each other through a Resonance bonus.
- Design: Resonance rank is the lower of the pack level and its mix layer level; each pack changes only Pip's short voice cues, while music parts come from the mixes.
- Got right: Taking the minimum of two levels stops one maxed pack from bypassing the other progression track.
- Where/why it failed: A pack owned without its paired mix does nothing at all, and its text ("toy-like pops") reads as a music or effect change, so players believe the unlock is broken.
- Fix: Proposed, not shipped: state the pairing requirement on the pack card, and have each pack add an audible arena layer when unlocked.
- Why this fix: Players judge an upgrade by whether they hear or feel it right away; a hidden dependency on another purchase makes a working system look dead.
- Rule of thumb: If a purchase only works when another purchase is also owned, say so where it is bought, and give it a standalone effect the player can perceive.
- Provenance (verified/assumed): first-hand, read the rank function, the perk hooks and the cue code in the source. Not yet observed in a live playthrough, so the player-perception claim comes from the user's own confusion in this session.
- Composed: N/A
- Link: session_01Ao86eEdRmKAAS2Tg8HmKWx

## E5 — additive toll with no in run recovery caps depth
- Date: 2026-09-29
- Project: Pappydapimp69/OD76
- Tags: [game-design][economy]
- What: OD76's arena stage toll adds fatigue every stage clear (4 plus the stage number, capped at 25), while the only ways to lower fatigue are ranch rest and food, reachable only by leaving the arena.
- Why built: The toll was meant to make Pip's condition matter and to tie the ranch to arena progress.
- Design: A rising additive cost per stage, fatigue slowdowns at 60 and 80, and forced return at 100, with no recovery source inside the run.
- Got right: Fatigue tiers give the player visible warning before the hard stop.
- Where/why it failed: A run starting at 0 fatigue reaches about 68 after stage 8, 81 after stage 9 and 95 after stage 10, so nearly every run ends near stage 10 regardless of skill, the top complaint from players.
- Fix: Add an in-run recovery source (snacks eaten at the stage gate) and a growing maximum, so depth is not fixed by a constant budget.
- Why this fix: The ceiling came from a fixed budget divided by a rising cost; only changing the budget or adding recovery moves it, while tuning the per-stage cost just shifts the wall.
- Rule of thumb: When a run has a rising cost and a fixed budget with no in-run refill, compute the stage where the sum crosses the budget; that is your real difficulty cap.
- Provenance (verified/assumed): first-hand, summed the toll formula from the source and confirmed the numbers by script. The player complaint about the stage 8 wall is reported by the user, not measured in play.
- Composed: N/A
- Link: session_01Ao86eEdRmKAAS2Tg8HmKWx
- Cited-by: 2026-09-30 · projects/local__sandbox-rising-cost-depth-cap-whole-run-vs-step-test.md#E1 · compatible · sandboxes/2026-09-30__rising-cost-depth-cap-whole-run-vs-step-test.py · observed RESULT: PASS whole-run sim cap 8 equals summed-curve cap; per-step test passes to stage 58; recovery 20 lifts it to 12 · scheduled brain train pass 5

## E4 — cancel before shared release
- Date: 2026-09-29
- Project: Pappydapimp69/OD76
- Tags: [javascript][input]
- What: Charged actions must be marked cancelled before a shared focus-loss release handler invokes their ordinary release path.
- Why built: OD76 centralizes blur and visibility cleanup so held keyboard, pointer and gamepad actions cannot remain stuck after focus leaves the game.
- Design: Skill-specific capture listeners marked pending charges cancelled, while an older shared blur listener released any held skill through the normal stop function.
- Got right: Complete JSDOM regressions covered focus loss and passed, and the shared cleanup correctly cleared movement and hold state.
- Where/why it failed: Chromium browser fixtures showed that listener ordering could let the shared release run before the skill-specific cancellation listener, firing a charged skill and spending HEAT on blur. The DOM simulation did not expose the ordering difference.
- Fix: The shared focus-release boundary now marks every pending charged skill cancelled before it calls the shared stop function. Skill-specific listeners remain defensive.
- Why this fix: Cancellation becomes an invariant of the authoritative boundary instead of depending on event-listener phase or registration order.
- Rule of thumb: When one boundary both cancels and releases state, set the cancellation flag inside that boundary before invoking any polymorphic release callback; never rely on a separate listener running first.
- Provenance (verified/assumed): Verified in OD76 with three failing Chromium focus-loss assertions before the fix, all browser assertions passing after it, and 344 complete-game JSDOM regressions passing.
- Composed: N/A
- Link: session / B117 Skeleton 1 consolidation

## E3 — worktree agents start on default branch
- Date: 2026-09-26
- Project: Pappydapimp69/OD76
- Tags: [process][git][agents]
- What: For B116, five worktree sub-agents were fanned out after the scaffold had been committed AND pushed to the feature branch.
- Why built: To correct the B115 lesson, which said worktrees branch from "the last committed tree".
- Design: Each agent's first step was `git fetch origin <feature-branch> && git checkout --detach FETCH_HEAD`. It then edited only its own module and test file.
- Got right: All five agents landed on the scaffold commit (a4d7651). Integration was a file copy plus `git apply --3way` of each agent's small diff to a shared test file. The one conflict, in a shared test file, came from two agents editing adjacent lines, and resolving it took a single merge.
- Where/why it failed: In B115 the worktrees had started on the repo's DEFAULT branch (origin/main at c68a55f) even though the scaffold was pushed to the feature branch. Committing and pushing alone does not move a worktree's base.
- Fix: Tell every worktree agent to fetch the feature branch and check it out detached before doing any work.
- Why this fix: The worktree base is not under the orchestrator's control, but the agent's first command is.
- Rule of thumb: Worktree agents start on the default branch; make "fetch + checkout the feature branch detached" their first step, and merge shared-test edits with `git apply --3way`.
- Provenance (verified/assumed): Verified. In B115 the worktree HEAD was c68a55f (main) with the scaffold on the feature branch. In B116 the checkout step put all five agents on a4d7651.
- Composed: N/A
- Link: session_01MiKGTn5dUCKACyoy3hzBAB, OD76 3f1623c

## E2 — playtest wave words measure before tuning
- Date: 2026-09-26
- Project: Pappydapimp69/OD76
- Tags: [gamedesign][balance][method]
- What: A playtester reported "difficulty increases too fast after wave 3, specifically spawn rate."
- Why built: To soften the enemy spawn ramp.
- Design: Before tuning, simulate runs headlessly and record the spawn gap, spawns per second and the enemy cap for each run-global wave (1-18).
- Got right: The measurement showed spawn pressure was flat for global waves 1-9, then jumped at stage 4 (wave 10). The B108 difficulty tier rises there: 1.38 → 2.0 → 2.67 → 3.38 spawns/s. The HUD only ever shows WAVE 1-3 within each stage, so the player's "wave 3" meant the end of a stage and the curve step three stages in, not global wave 3. The fix eased only spawns per second above the opening tier (half the rise), leaving enemy speed, HP, caps and ranks untouched. That matched a same-session complaint that HEAT was "too fast in stages 4 and above".
- Where/why it failed: Taken literally, "after wave 3" would have tuned global wave 4 (stage 2), where nothing changes, and missed the real step.
- Fix: Map the player's words onto the HUD's own counter, and measure the actual per-wave pressure, before choosing which knob to turn.
- Why this fix: Players name what the HUD shows them. The code's internal counters (run-global wave, difficulty tier) can differ from it, so a literal reading targets the wrong transition.
- Rule of thumb: Translate playtest numbers through what the HUD displays, then measure the metric at every step before tuning. Ease the one driver the player named (spawn rate), not the whole difficulty curve.
- Provenance (verified/assumed): The flat waves 1-9 and the stage-4 jump were measured first-hand by a headless simulation. That the player meant the stage boundary is inferred from the HUD's per-stage wave display and the matching stage-4 HEAT complaint.
- Composed: N/A
- Link: session_01MiKGTn5dUCKACyoy3hzBAB, OD76 b21-103.js (B115a)

## E1 — parallel worktree agents base and gitlinks
- Date: 2026-09-26
- Project: Pappydapimp69/OD76
- Tags: [process][git][agents]
- What: One build (B115) was split across five parallel sub-agents, three of them in isolated git worktrees, each owning one numbered module and one test file.
- Why built: To implement five independent playtest changes at the same time without agents clobbering each other's half-written files (the test harness loads every module, so one agent's syntax error broke every other agent's `npm test`).
- Design: The orchestrator scaffolded stub modules, stub test files and the runner wiring in the main checkout. Each worktree agent then filled in only its own files, and the orchestrator copied the results back.
- Got right: Giving each agent a single file to own made integration a straight copy, with only a few one-line assertion merges in shared test files.
- Where/why it failed: (1) The worktrees were cut from the last pushed commit (B114), not from the orchestrator's uncommitted scaffold. The agents found no stubs and a runner still expecting the old module count, so each re-created the stubs and edited the runner itself. (2) A later `git add -A` in the main checkout staged `.claude/worktrees/*` as embedded gitlinks, and they were pushed.
- Fix: Commit and push the scaffold BEFORE spawning worktree agents. Add `.claude/worktrees/` to `.git/info/exclude` first. Untrack the gitlinks with `git rm --cached -r`.
- Why this fix: The worktree base is the committed tree, so shared scaffolding has to be committed first. Excluding the directory stops blanket staging from ever seeing nested repos.
- Rule of thumb: Before fanning out worktree agents, commit and push the shared scaffold and exclude the worktree directory; tell each agent which commit it should be on.
- Provenance (verified/assumed): Verified first-hand. Worktree HEAD was c68a55f while the scaffold was at 7e8c435. The gitlinks were committed (2f296bd) and then removed (ba51495). It is assumed that the worktree base is always the pushed HEAD in this harness.
- Composed: N/A
- Link: session_01MiKGTn5dUCKACyoy3hzBAB, OD76 commits 2f296bd, ba51495

