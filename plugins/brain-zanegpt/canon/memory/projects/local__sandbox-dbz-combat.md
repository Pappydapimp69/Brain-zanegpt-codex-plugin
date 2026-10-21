# local/sandbox-dbz-combat — lessons

Project: local/sandbox-dbz-combat. Newest first.

---

## E5 — two independent coverage report blind spots
- Date: 2026-07-13
- Project: local/sandbox-dbz-combat
- Tags: [testing][algorithm][process]
- What: Re-verifying the sandbox-dbz-combat ↔ the-game-the-recursion edge (currently single-source: projects/local__sandbox-combined-realtime-loop.md#E1, citing dbz-combat#E1 + recursion#E16 for a frame-rate-independence claim) from a new, independent angle — a different pair of entries. Composed: projects/local__sandbox-dbz-combat.md#E3 (when aggregating per-case "best option" results into a coverage/diversity metric, guard the no-winner sentinel — `null`/`None`/`-1` — before folding it in; an unhandled sentinel silently pollutes the tally, often coerced into a phantom set member, flipping a "nothing could do this" case into apparent coverage) and projects/pappydapimp69__the-game-the-recursion.md#E14 (a fixed `0..N` seed-suite validator is real completability coverage but not a growing fuzz corpus or a diversity check — both separate, currently-absent axes). Built and ran a sandbox confirming these are two fully INDEPENDENT blind spots in a "how well-covered is this system" report — fixing either leaves the other completely open.
- Why built: dbz-combat#E3 was recorded from a pure aggregation-logic bug (a sentinel value polluting a Set/tally); recursion#E14 was recorded from a pure test-design observation (a fixed enumeration isn't a fuzz corpus). Neither lesson states they're both instances of "a coverage report can look trustworthy while being wrong in an unrelated way" — a team that fixes dbz-combat#E3's sentinel bug could reasonably believe their coverage report is now correct, with no signal that recursion#E14's completely separate gap (the report only ever covers what was explicitly enumerated) is still open.
- Design: `engine.mjs` runs a fixed 20-seed enumeration (`SEEDS = [0..19]`, standing in for recursion#E14's "fixed 0..N seed-suite") against a deterministic `bestOptionFor(seed)` function that returns a real category for most seeds but a `null` sentinel for every 5th seed (dbz-combat#E3's exact shape, deterministic by construction, not random). A naive tally (`Set.add` on every result, including `null`) is compared against a fixed tally (sentinel cases counted separately, only real categories added to the covered set). Separately, the enumerated seed count (20) is compared against a much larger `TRUE_SPACE_SIZE` (100,000) to quantify the fraction of the real space actually exercised, independent of whether the sentinel bug is fixed.
- Got right: The fixed tally correctly resolved dbz-combat#E3's bug in isolation — 4 real categories correctly counted, 4 sentinel cases correctly separated out and reported as `noCoverageCount`, with `null` no longer appearing as a phantom 5th "category" the way the naive tally reported it.
- Where/why it failed: The naive tally's `distinct entries=5` included `null` as if it were a genuine category (`entries: null,category-1,category-2,category-3,category-0`) — dbz-combat#E3's bug reproduced exactly. Independently, even AFTER applying the fix (4 correctly-tallied real categories), the enumerated seed suite still only exercised `20/100000 = 0.0200%` of the true seed space — the fixed tally has no mechanism whatsoever to discover a category that would only appear from seed 20 onward, because it was never run. Fixing the sentinel-aggregation bug and fixing the enumeration-completeness gap are unrelated code changes addressing unrelated failure modes.
- Fix: Both must be independently audited when trusting a coverage/completability report: (1) guard every no-winner sentinel before folding a per-case result into an aggregate tally, tallying it as its own explicit "no coverage" category rather than a phantom member of the covered set (dbz-combat#E3); (2) separately track what fraction of the TRUE input space a fixed enumeration actually reaches, and pair a fixed correctness suite with an open-ended fuzz/diversity axis rather than treating "N seeds pass" as evidence about the space beyond those N (recursion#E14).
- Why this fix: Neither individual fix is new — the value of the sandbox is confirming, by explicit cross-check, that a team which has fixed ONE of these two coverage-report defects has zero evidence the other is also fixed, since they operate on different axes (aggregation correctness vs. enumeration completeness) and neither's own fix touches the other's failure mode.
- Rule of thumb: Before trusting a "how well covered is this" report, separately audit two independent axes — does the AGGREGATION correctly separate "no result" from "a real result" (never silently fold a sentinel into a tally), and does the ENUMERATION itself reach a meaningful fraction of the true input space (a fixed suite bounds coverage to what was run, regardless of how correctly those specific runs were tallied) — a report can be perfectly correct on one axis and silently wrong on the other.
- Provenance (verified/assumed): VERIFIED first-hand — built `engine.mjs` (zero RNG, zero wall-clock, deterministic 20-seed enumeration and deterministic sentinel-injection pattern), confirmed the naive tally pollutes with `null` while the fixed tally correctly separates it (4 real categories, 4 no-coverage cases), and confirmed the enumeration-coverage fraction (0.02%) is unaffected by which tally variant is used. Confirmed deterministic/reproducible across two independent process invocations of `node engine.mjs`, output diffed byte-identical.
- Link: session 01KxkbJUq8YajH8GokSZYYHy; re-verifying sandbox-dbz-combat ↔ the-game-the-recursion (currently single-source via sandbox-combined-realtime-loop#E1) from a new angle; sandbox `engine.mjs`, scratchpad `loop1-coverage-blindspots/` (run twice as separate process invocations, outputs diffed byte-identical)
- Composed: local/sandbox-dbz-combat/E3, pappydapimp69/the-game-the-recursion/E14
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E31 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E4 — sandbox dbz resource cost must bind
- Date: 2026-07-11
- Project: local/sandbox-dbz-combat
- Tags: [gamedesign][balance]
- What: A combat resource (ki/mana/stamina/cooldown/a sustain-drain)
  creates interesting decisions ONLY while its cost actually bites within
  the decision horizon, and it has a Goldilocks band on both sides. Too
  cheap: the drain never empties before a fight ends, or a "powered mode"
  outlasts combat, so it is a free permanent buff and the un-powered option
  is strictly dominated (always-on). Too dear: even the strongest option
  cannot sustain it and the content becomes unwinnable (never-on). The
  binding also erodes silently over a level curve: if enemy HP and the
  resource POOL scale but ability COSTS stay flat, the constraint
  evaporates and the late game collapses to spamming the single biggest
  move.
- Why built: To find why DBZ-style transformations and special moves often
  feel like either an always-on freebie or a useless trap, by simulating
  ki economies across fights and across a level curve.
- Design: Deterministic sims of a ki pool with drain/regen, specials with
  costs, transformation tiers with per-second drain, and enemy ladders;
  measured whether a real "when do I spend / transform" decision existed
  (do optimal strategies diverge) at various cost levels and scalings.
- Got right: Testing the SAME mechanic at several cost points and across a
  persistent-vs-per-fight resource horizon is what exposes the band;
  a single tuning pass looks fine at whatever point it was set.
- Where/why it failed: The decision only exists in a narrow cost band.
  Below it, spending/transforming is always correct (no decision); above
  it, never correct or fatal. And a per-encounter resource refill destroys
  the decision entirely regardless of tuning, because you can never run
  short across the horizon that would force a choice.
- Fix: Make the resource persistent across the decision horizon (a shared
  pool across fights, not a per-encounter refill); place cost in the band
  where a spend must beat your default option's damage-per-second by enough
  to amortize any downtime (a zero-output "charge to refund" action
  competes with your own DPS and is a tempo trap unless the payoff clears
  that bar or grants utility damage can't — range, unblockable); scale
  costs WITH the pool so the constraint keeps binding at every level; and
  bound any effect that never falls off (an uncapped %-max-HP hit is a
  constant fraction of any HP pool, so it auto-dominates as pools grow — cap
  it).
- Why this fix: A resource is only a design lever while it is scarce
  relative to what you want to do with it. Keeping cost in the binding band,
  persistent, and scaled with the pool is what preserves the scarcity that
  makes spending it a decision rather than a formality.
- Rule of thumb: A combat resource shapes decisions only while its cost
  binds within the decision horizon — too cheap makes the powered option
  always-on and dominant, too dear makes it unusable. Make it persistent
  (shared across the horizon, not refilled each fight), price a spend to
  beat your default DPS by enough to cover its downtime, scale costs with
  the pool so it keeps binding across the whole level curve (flat costs
  against a scaling pool is exactly why "the endgame is just spamming the
  biggest move"), and cap any effect whose value never falls off with scale.
- Provenance (verified/assumed): Verified first-hand this session, sim +
  adversarial re-check: a transformation sustain-drain with mode-duration
  far exceeding fight-length never bit (base form strictly dominated, zero
  forced detransforms); a per-fight ki refill made every strategy
  equivalent (no decision) while a shared pool revived it; over-costing the
  top tier made it lose outright; flat ki costs against a level-scaled pool
  collapsed a balanced 5-skill menu to 1–2 skills from mid-curve up, and
  scaling costs with the pool restored a level-invariant full spread.
- Link: session (dog-game-continue-oc3xqh); sandboxes sb-dbz-transform,
  sb-dbz-ki-combo, sb-dbz-skills. Portable kernel filed in ideas
  `idea-repository.md`
  (SYSTEM/gamedesign/a-resource-shapes-decisions-only-while-its-cost-binds).

- Cited-by: 2026-07-13 · projects/local__sandbox-combined-loop-combat.md#E1 · compatible · no sandbox · session (query brain for "brain analyze groups and train in sandbox, 3 sandbox environs"), sandbox script sweep.mjs/sweep_fixed.mjs, no code change to a shipping project
- Cited-by: 2026-07-15 · projects/pappydapimp69__draft.md#E1 · compatible · no sandbox · Pappydapimp69/Draft `index.html` (`mkUnit`), commit 9c758db
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-the-waiting-city.md#E14 · compatible · no sandbox · session (brain train 3 groups + 2 edges, sandboxed until satisfied), sandbox script sim.js, no code change to a shipping project
- Audited: 2026-10-13 · modeled · Read the entry and looked for its stored sandbox: none is stored (the Link names sb-dbz-transform, sb-dbz-ki-combo and sb-dbz-skills but no such files exist under sandboxes/), so I could not check whether those sims compute their results or build the answer in. The Provenance gives concrete outcomes (zero forced detransforms, equivalent strategies under per-fight refill, menu collapse to 1-2 skills under flat costs) that a hand-written ki model can produce, and two later stored sandboxes (resource-cost-binding-rate-flat-vs-scaled, fps-cooldown-cadence-shifts-resource-binding) do compute the flat-versus-scaled binding rate and agree on that one part. The rule is about how real combat resources feel to players, and only toy models were tested, with no playtest or real engine, and the band widths themselves are model parameters. The persistent-pool and tempo-trap claims have no stored evidence at all, so the verdict is modeled rather than pass. · scheduled brain train session, 2026-10-13, audit pass; session_01KgwUVJ8YiFpBjfevwrK7fS
- Cited-by: 2026-09-30 · projects/pappydapimp69__brainwork.md#E385 · compatible · sandboxes/2026-09-30__resource-cost-binding-rate-flat-vs-scaled.py · observed RESULT: PASS flat [0.4, 0.0, 0.0, 0.0] scaled [0.4, 0.4, 0.4, 0.4] · scheduled training session pass 2
- Cited-by: 2026-09-30 · projects/pappydapimp69__brainwork.md#E395 · compatible · sandboxes/2026-09-30__fps-cooldown-cadence-shifts-resource-binding.py · observed RESULT: PASS reset rate [0.0, 0.029, 0.074] carry rate [0.101, 0.101, 0.101]; fires reset [450, 515, 540], carry [556, 556, 556] · scheduled training session pass 3

## E3 — sandbox dbz optimality aggregation null hygiene
- Date: 2026-07-11
- Project: local/sandbox-dbz-combat
- Tags: [testing][state]
- What: A balance-analysis harness computed, per scenario, the "best skill"
  and folded those winners into a Set of "ever-optimal" skills. When a
  scenario was UNCLEARABLE, the best-skill computation returned `null`
  (nothing wins). That `null` was added to the Set and stringified to an
  empty string `''`, silently inflating the ever-optimal count with a
  phantom member and mislabeling an "impossible scenario" as if some skill
  had covered it.
- Why built: To measure skill-menu health by counting how many skills are
  ever the optimal pick across a battery of encounter scenarios — the
  metric used to distinguish a rich menu from one full of filler.
- Design: For each scenario, pick the argmax skill by the success metric,
  then accumulate winners into a Set; report the Set's size as
  "ever-optimal skills."
- Got right: The metric and the matrix approach were sound; the flaw was
  purely in aggregating results that included a no-winner sentinel.
- Where/why it failed: An unclearable scenario has no argmax, so the picker
  returned a no-result sentinel (`null`). The aggregation didn't guard the
  sentinel before inserting it, and JS coerced it into the Set as a
  distinct empty-string entry — so a scenario that NOTHING could clear
  counted toward "diversity," the opposite of the truth, and the reported
  count was off by one in a way that looked like more coverage than existed.
- Fix: Guard the no-result sentinel before aggregating — skip scenarios
  with no winner (and surface them separately as "unclearable"), rather
  than letting a `null`/`''` fall into the "ever-optimal" set.
- Why this fix: "No option wins here" and "this option won here" are
  different facts; folding the former into the latter's tally corrupts the
  exact number the analysis exists to produce. Filtering the sentinel keeps
  the aggregate measuring only real wins, and reporting unclearable
  scenarios separately preserves the (important) signal that content is
  impossible.
- Rule of thumb: When aggregating per-case "best option" results into a
  coverage/diversity metric, explicitly guard the no-winner sentinel
  (`null`/`None`/`-1`/`''`) before folding it in — an unhandled sentinel
  silently pollutes the tally (often coerced into a phantom set member) and,
  worse, flips a "nothing could do this" case into apparent coverage.
  Surface no-result cases as their own category; they're usually the most
  important finding, not noise to swallow.
- Provenance (verified/assumed): Verified first-hand this session and
  confirmed by the adversarial re-check: the harness output literally
  showed an empty-string member in the ever-optimal set
  (`{Ki Blast, Spirit Bomb, Big Bang, Galick Gun, }`) and a defensive-boss
  scenario reported as `{, Spirit Bomb}`, both traced to a `null` best-skill
  from an unclearable scenario entering the Set.
- Link: session (dog-game-continue-oc3xqh); sandbox sb-dbz-skills pass4.js
  (ever-optimal aggregation).
- Cited-by: 2026-07-13 · projects/local__sandbox-dbz-combat.md#E5 · compatible · no sandbox · session 01KxkbJUq8YajH8GokSZYYHy; re-verifying sandbox-dbz-combat ↔ the-game-the-recursion (currently single-source via sandbox-combined-realtime-loop#E1) from a new angle; sandbox `engine.mjs`, scratchpad `loop1-coverage-blindspots/` (run twice as separate process invocations, outputs diffed byte-identical)
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E38 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-09-30 · projects/local__sandbox-sentinel-and-failfast-coverage-sweep.md#E1 · compatible · sandboxes/2026-09-30__sentinel-and-failfast-coverage-sweep.py · observed RESULT: PASS naive tally counts phantom 'None' (distinct 5 vs true 4) and fail-fast covers 5 of 12 cases; guarded covers 11 with no_winner=3 errors=1 · scheduled train pass 5
- Cited-by: 2026-09-29 · projects/pappydapimp69__brain.md#E65 · compatible · no sandbox · session https://claude.ai/code/session_01CHKxy8KkvpqUvfaWw1qb3v
- Cited-by: 2026-10-15 · projects/pappydapimp69__zanegpt.md#E8 · compatible · sandboxes/2026-10-15__rhyme-assigner-no-match-sentinel-merges-orphan-lines-into-a-fake-rhyme.py · observed RESULT: PASS no-match sentinel turns free verse ABCD into AAAA (rhymed share 0.00 -> 1.00), ABAC into ABAB (0.50 -> 1.00), and an orphan-wrapped couplet ABBC into ABBA (closure 1 -> 3); fully rhymed AABB unaffected. · brain train auto pass 2 (edge); session_01Hecxxt7Wfrejc8A3YVX1ht

## E2 — sandbox dbz monotonic power axis collapse
- Date: 2026-07-11
- Project: local/sandbox-dbz-combat
- Tags: [gamedesign][balance]
- What: A set of player choices (skills, special moves, transformation
  tiers, weapons) that differ ONLY along a single monotonic "power" axis —
  raw damage, or a flat stat multiplier — collapses the menu to one
  dominant option; every other choice is dead weight. Worse, once cost is
  factored in, the flashiest biggest-number option is often literally the
  WORST pick (lowest damage-per-resource). This is the mechanical root of
  the complaint "the skills feel unimpressive": a menu of damage variants
  is a menu of one.
- Why built: To find where a DBZ-style 2D-RPG's combat/skill design fails
  to feel satisfying, by simulating skill menus, combo movesets, and
  transformation tiers and measuring which options are ever the optimal
  choice across encounters.
- Design: Built deterministic combat sims (skill × scenario optimality
  matrices; frame-stepped combo loops; a transformation-tier ladder) and
  computed, for each option, whether it is ever the correct pick.
- Got right: The metric — "is this option ever uniquely optimal in some
  scenario" — is the right lens; it exposes filler that a raw
  damage-number comparison hides.
- Where/why it failed: When options vary on one monotonic axis, the
  optimal pick is deterministic (the best ratio on that axis) and
  situation-independent, so nothing else is ever correct and no real choice
  exists. The player perceives "no impact" because there is no decision —
  just a single right answer with cosmetic variants.
- Fix: Give the options Pareto structure: each must LEAD exactly one axis
  and PAY on another, so each is the right pick in some situations and
  wrong in others. Load-bearing orthogonal axes (verified to each add
  distinct niches): target shape (single/line/AoE), burst-vs-sustained,
  range/reach, resource-efficiency, startup role (setup/confirm/finisher),
  and knockback-as-utility. A choice that leads on two axes at once
  dominates everything; one that leads on none is filler.
- Why this fix: "Impact" is not the size of a number — it's being the
  correct answer to a specific problem. A Pareto trade-off guarantees each
  option owns at least one problem where it wins and loses elsewhere, which
  is exactly what makes picking it feel meaningful.
- Rule of thumb: If a menu of combat options (skills/moves/tiers/upgrades)
  differs only along a monotonic power axis, it will collapse to one
  dominant choice and the biggest-number option will often be the worst per
  cost — the surest cause of "the abilities feel unimpressive." Make every
  option lead exactly one orthogonal axis and pay on another; audit by
  computing, per option, whether it is ever uniquely optimal across your
  real encounter types — any option that never wins anywhere is filler and
  needs a distinct axis, not a bigger number.
- Provenance (verified/assumed): Verified first-hand this session across
  three independent deterministic sandboxes and an adversarial re-check:
  pure-damage skills gave 1 of 5 ever-optimal (the biggest move the worst);
  forcing each skill to lead one axis and pay another gave 5 of 5 with
  distinct niches; the highest raw-DPS melee move had the worst combo
  because its own unpriced knockback pushed the enemy out of range;
  transformation tiers differing only by an ×N multiplier collapsed to
  "always newest," revived only by adding an orthogonal efficiency cost.
- Link: session (dog-game-continue-oc3xqh); sandboxes sb-dbz-skills,
  sb-dbz-ki-combo, sb-dbz-transform. Portable kernel filed in ideas
  `idea-repository.md` (SYSTEM/gamedesign/monotonic-power-axis-collapse).
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E40 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-07-15 · projects/pappydapimp69__draft.md#E1 · compatible · no sandbox · Pappydapimp69/Draft `index.html` (`mkUnit`), commit 9c758db
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-prologue.md#E18 · compatible · no sandbox · session (brain train on groups and test 5 new edges), src/sim/content.js (archetypes.brawler/channeler/seeker), no code change

## E1 — sandbox dbz cancel window frame ordering
- Date: 2026-07-11
- Project: local/sandbox-dbz-combat
- Tags: [gamedev][input][determinism]
- What: In a frame-stepped combat engine, the "this move can now be
  cancelled into a special" flag was set INSIDE the recovery-advance
  branch, which runs AFTER the per-frame input is sampled. So on the first
  frame the move became cancelable, the input read for that frame had
  already happened — the cancel window opened one frame too late, cancels
  fired about eleven frames late, and combos that were supposed to loop
  infinitely instead dropped/reset.
- Why built: A melee combat loop where light attacks cancel their recovery
  into special moves; the cancel-eligibility flag needed to be set as the
  move transitioned from its active frames into recovery.
- Design: A per-tick loop that (1) reads buffered input and tries to start
  a queued move if the current move is cancelable, then (2) advances the
  current move's phase timers. The cancelable flag was set in step (2).
- Got right: The rest of the loop — hitstun bookkeeping, combo-validity
  (a combo continues iff each hit's hitstun ≥ frames-to-the-next-hit),
  damage — was correct; this was a narrow ordering bug in one flag.
- Where/why it failed: Because input is sampled before phase advance within
  a tick, a flag SET during phase advance isn't visible to the input read
  until the NEXT tick — a one-frame-late window. On frame-perfect scripted
  input this converted an intended infinite into a reset (20 inputs ignored,
  max combo 31 → 1). It was masked by a cancel-ASAP policy that re-samples
  every frame, so casual testing looked "mostly fine" (still infinite, just
  fewer hits) and hid it.
- Fix: Open the cancelable window at the active→recovery transition,
  computed BEFORE the input-sampling read of the same tick (evaluate cancel
  eligibility relative to input-sampling order, not after it).
- Why this fix: Cancel eligibility is a question the input read asks, so it
  must be answered before that read within the tick. Setting it after is a
  one-frame-late buffer by construction, independent of the frame data
  values.
- Rule of thumb: In any frame-stepped/tick-based system where one step
  reads input and another mutates state, a flag that gates the input read
  must be updated BEFORE the read within the same tick — set it after and
  you get a silent one-frame-late window. In fighting/action combat this
  shows up as cancels/links that "feel dropped" only on tight timing;
  test with frame-perfect scripted input, since a re-sample-every-frame or
  cancel-ASAP policy masks the ordering bug on loose input.
- Provenance (verified/assumed): Verified first-hand this session and
  reproduced by the adversarial re-check: reverting the fix (moving the flag
  back into the recovery branch, after the input read) dropped max combo
  from 31 to 1 with 20 scripted inputs ignored and 11 combo drops; the fix
  restores the intended loop.
- Link: session (dog-game-continue-oc3xqh); sandbox sb-dbz-ki-combo
  `engine.js` (cancelable-flag placement at the active→recovery transition).
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-realtime-loop.md#E1 · compatible · no sandbox · this session's sandbox (sbT.py); source entries sandbox-combined-game-loop#E2, the-game-the-recursion#E16, sandbox-dbz-combat#E1.
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-tickorder-cancel.md#E1 · compatible · no sandbox · this session's sandbox (sb3_cancelorder.py); source entries sandbox-dbz-combat#E1 and sandbox-combined-game-loop#E1.
- Cited-by: 2026-09-29 · projects/local__sandbox-dbz-combat-gate-order-single-witness.md#E1 · compatible · no sandbox · scheduled training pass 5, session_01NomGdXQGCMAr6o2dzv6Tp2
- Cited-by: 2026-09-29 · projects/local__sandbox-dbz-combat-seven-hoisted-crit-table-loot-stream.md#E1 · compatible · no sandbox · session_01AJo9NVvaQuzD3JbJDk6P3B
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E39 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-09-30 · projects/local__tick-gate-order-nan-timer-poisoning.md#E1 · compatible · sandboxes/2026-09-30__tick-gate-order-nan-timer-poisoning.py · observed RESULT: PASS before=1 after=0 after_late=1 nan=0 guarded=1 · scheduled train pass 4
- Cited-by: 2026-09-29 · projects/pappydapimp69__brain.md#E63 · compatible · no sandbox · session https://claude.ai/code/session_01CHKxy8KkvpqUvfaWw1qb3v
