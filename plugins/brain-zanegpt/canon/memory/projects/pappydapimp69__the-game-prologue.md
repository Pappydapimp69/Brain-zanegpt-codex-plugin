# Pappydapimp69/The-game-prologue — lessons

Project: Pappydapimp69/The-game-prologue. Newest first.

---

## E27 — core defense wave floor flattens day identity
- Date: 2026-07-15
- Project: pappydapimp69/the-game-prologue
- Tags: [gamedesign][balance][pacing]
- What: A wave-defense game maps each wave to a "Brain cognitive-growth day"
  (`BRAIN_DAYS`), with enemy count meant to scale with that day's real
  knowledge-entry count (`dayFactor = knowledge / avg`) so a heavy day
  ("Inherited backlog", knowledge 29) reads as a genuinely bigger wave than a
  light one ("Interlude", knowledge 2) — this proportionality was the game's
  stated core hook (code comment: "heavy-knowledge days... become genuinely
  bigger waves... light days... become real breathers, not just smaller
  numbers for their own sake"). A prior patch added a flat `MIN_WAVE_ENEMIES`
  floor (raised from 4 to 22 per a direct user request: "waves should last
  longer, minimum 22") implemented as additive top-up filler (generic
  `pickEnemyType` calls) whenever a day's natural count fell short.
- Why built: user feedback after the floor-22 patch was vague ("it still
  feels off") — no specific symptom named. Queried `memory/PITFALLS.md` and
  found a directly relevant precedent: `projects/pappydapimp69__brain.md#E5`
  — "a flat time-budget per batch of simultaneous events makes every batch
  feel the same size regardless of real magnitude... grow the budget
  sub-linearly instead, and verify against small/medium cases too." That's
  the same shape of bug: a flat mechanism applied on top of a
  magnitude-varying signal erases the very distinction the signal exists to
  convey. Verified empirically (not guessed) before proposing a fix: wrote a
  measurement harness that computed, for every day 1-12, the day's natural
  (unpadded) enemy count vs. the actual combined-wave total after the floor.
  Result: 5 of 12 days were 61-91% generic padding, with the biggest,
  most-designed-around day ("Inherited backlog") needing 0% padding while
  small days needing up to 91% — i.e., the floor had almost fully overridden
  the day-proportional signal for most of the game's content. Supplemented
  with a web search on wave-defense design practice, which converged on the
  same principle: proportional/budget-driven enemy-count scaling (tied to
  wave number, player count, etc.) is the standard approach; flat/fixed spawn
  amounts are called out as reading "flat and predictable."
- Design: the per-day enemy-count formula was `base = 2.5 + loop*2.5;
  count = round(base * dayFactor * countMul)`. Fix: scale `base` itself
  (`8 + loop*8`, ~3.2x) so the underlying magnitude-driving formula reaches
  the requested floor through EACH day's own proportional size in the common
  case, rather than via generic top-up. Verified with the same measurement
  harness: padding for most days dropped to 0-36%; only days sitting
  immediately before a boss wave with no room left to merge forward (a real,
  narrow structural constraint — merging can never cross a boss boundary)
  still need substantial top-up (73-77%), which is an honest edge case, not
  the dominant experience it was before.
- Got right: measuring the actual padding ratio per day BEFORE proposing a
  fix, and re-measuring after, rather than reasoning about it in the
  abstract or trusting a plausible-sounding fix. Also fixed the underlying
  magnitude control (the count *formula*) instead of the *floor* or the
  *top-up mechanism* — a tempting alternative (making the top-up loop
  "day-aware" by re-invoking the day's own generator instead of a generic
  type-picker) was considered and rejected: this game's per-day enemy TYPE
  distribution is itself mostly generic (tier-gated by absolute wave number,
  not by which day it is — only 4 of 12 days carry a distinguishing
  signature-type flag), so the game's real "day identity" signal is almost
  entirely the enemy COUNT, not composition. A fix that made padding
  "flavor-aware" would have looked like it addressed the symptom while
  leaving the actual measured problem (count-flattening) untouched.
- Where/why it failed: the original floor-22 patch was implemented and
  shipped without measuring its interaction with the pre-existing
  day-proportional count design — the two features were each individually
  correct (a literal request for "minimum 22" was honored exactly; the
  day-count formula was unchanged) but composed badly. Memory already has an
  entry for this general shape (two individually-verified-sound features
  interacting to silently break a THIRD thing neither one names on its own):
  `local__sandbox-dbz-merged.md#E1` (a percent-max-HP damage cap and a
  Pareto-diverse skill menu, each independently correct, combined to
  eliminate a skill's entire niche).
- Fix: `base = 8 + day.loop * 8` in `buildDaySchedule` (was `2.5 + loop*2.5`).
  `MIN_WAVE_ENEMIES = 22` is unchanged — the floor is honored, it's just no
  longer doing most of the work.
- Why this fix: minimal — one constant, no new mechanism, no change to the
  merge logic, the floor value, boss-wave handling, or type distribution.
  Preserves the literal, explicit prior request (waves ≥ 22, longer than
  before) while restoring the proportionality that request had accidentally
  buried.
- Rule of thumb: before shipping a flat floor/cap/minimum on top of an
  existing magnitude-varying signal, measure what fraction of the floor's
  typical output is now floor-driven vs signal-driven across the FULL range
  of inputs (not just the average case) — a floor that dominates 5/12 or
  more of your content isn't a floor anymore, it's a replacement, and any
  "why does this feel flat/off/same" report after adding one should trigger
  exactly this measurement before touching anything else.
- Provenance (verified/assumed): Verified first-hand: padding-ratio
  measurement harness run against the live build both before (61-91% on
  5/12 days) and after (0-36% on 10/12 days, 73-77% on the 2 narrow
  before-boss edge cases) the fix; full regression playthrough (upgrade
  pick discipline, boss alternation, 15-wave no-NaN/no-crash, sub-200ms
  wall-clock for ~90s of simulated time) re-run and passing after the
  change. Assumed: the qualitative "feels off" report is actually about this
  count-flattening rather than some other axis (combat feel, upgrade
  pacing, control responsiveness) — the user never named the specific
  symptom, so this attribution is inferred from (a) it directly follows the
  floor-22 patch, (b) it's the single largest, most measurable regression
  that patch introduced, and (c) it matches an existing Brain precedent for
  exactly this failure shape.
- Link: session (Core Defense one-shot artifact, wave-floor proportionality
  patch); informed by projects/pappydapimp69__brain.md#E5.

## E26 — proximity fix is reactive common region is structural
- Date: 2026-07-13
- Project: pappydapimp69/the-game-prologue
- Tags: [gamedesign][ux][onboarding]
- What: External research task ("brain train external research prologue and onboarding") against `projects/pappydapimp69__the-game-prologue.md#E5` (two unrelated systems reacting to the same named game event — an onboarding checklist and a quest's kill count, both triggered by "hit a husk" — read as ONE requirement when their player-facing UI sits near each other; fix recorded as "audit adjacent text for accidentally-implied dependencies"). The mechanism prologue#E5 describes is a named, externally-documented UX phenomenon — the Gestalt LAW OF PROXIMITY (elements placed close together are perceived as a group/related, independent of whether they're actually related) — and the same body of UX literature documents a STRUCTURAL countermeasure prologue#E5 never states: the LAW OF COMMON REGION, where a shared visual boundary (a container) or deliberately increased whitespace overrides simple proximity and signals "these are NOT the same thing" before a false-relationship reading can ever ship, rather than catching it after the fact via a manual audit.
- Why built: prologue#E5's own fix is entirely reactive — "audit adjacent text for accidentally-implied dependencies the code doesn't have" is a checklist step you run AFTER noticing (or being reported) a false relationship, not a rule that prevents the NEXT unrelated-but-adjacent pairing from shipping the same way. The entry treats this incident as a one-off text-adjacency bug rather than naming the general perceptual law behind it, so nothing in canon currently tells a future session what to DO differently by default when authoring two independent event-driven UI systems.
- Design: Not a code sandbox — this is a pure external-fact claim, verified against real external sources by search (WebFetch to the primary UX sources — nngroup.com, lawsofux.com, optimalworkshop.com — returned HTTP 403 this session, confirmed via the agent proxy status endpoint to be an org egress-policy block on those hosts, not a per-site failure; WebSearch itself remained available and returned live, attributable, quotable content from those same sources, which is what this entry is verified against). Two searches: (1) "Gestalt law of proximity UX adjacent elements imply relationship Nielsen Norman Group" (2) "common region Gestalt principle prevent accidental grouping unrelated UI elements containers whitespace".
- Got right: prologue#E5's diagnosis of the ROOT CAUSE was already exactly correct — proximity alone (no shared code, no shared data) is sufficient for players (and, per the entry, even engineers investigating a "logic bug" report) to perceive a relationship. That diagnosis matches the externally-documented law precisely: "UI elements that are close together are perceived as belonging together... proximity is one of the most powerful tools at your disposal, and can easily override other factors like color and shape." prologue#E5's OWN secondary instruction — "get ground truth from a headless test before assuming a reported 'logic bug' is real" — is also good practice, independent of this composition.
- Where/why it failed: prologue#E5's prescribed fix stops at detection ("audit adjacent text"), not prevention. The external sources describe a specific, low-cost structural rule that prevents the entire failure class: "Before you add a line or a box to separate content, try adding space. If two things are related, put them close. If they are unrelated, push them apart" — and where whitespace alone isn't enough, "containers are a powerful tool... creating a clear boundary is a strong visual cue that can overpower other grouping principles such as proximity." Nothing in prologue's canon currently states this as a default authoring rule for independently-triggered event-driven UI (onboarding checklists, quest trackers, any other passive-observer system in prologue#E15's mold) — the next two unrelated systems that happen to fire UI near each other have no standing guardrail, only the hope that someone remembers to audit.
- Fix: Not applied to shipping code (flagging + canon gap only, per instructions — no prologue source was available to modify in this session). The general rule to record: whenever two independently-triggered, unrelated systems (prologue#E15's "passive observer overlay" onboarding pattern is exactly this shape, and prologue#E5's own incident is a second instance) can each emit player-facing UI, deliberately apply either increased whitespace or an explicit container boundary between them BY DEFAULT at authoring time — don't rely on an after-the-fact adjacency audit as the only safeguard.
- Why this fix: An audit is a process step that depends on someone remembering to run it, catches only what's already been noticed, and re-litigates the same judgment call every time; a structural rule (whitespace/container by default between unrelated event-driven UI) is enforced by the layout itself and prevents the NEXT instance for free, the same way prologue#E5's own existing "extract shared logic the first time you notice duplication" (prologue#E4) already prefers a structural fix over a reactive one elsewhere in this same project's canon — this composition applies that same preference to E5's own recommendation.
- Rule of thumb: When two functionally-unrelated systems can independently emit player-facing UI (an onboarding/tutorial overlay and a quest tracker are a common concrete case), the failure mode isn't a code bug — it's the Gestalt Law of Proximity: placing their output near each other is sufficient, on its own, for players AND investigating engineers to read them as one requirement. Default to visual separation (deliberate whitespace, or a container boundary per the Law of Common Region) between independently-triggered UI at AUTHORING time, not as a post-hoc audit step — "if two things are related, put them close; if they are unrelated, push them apart."
- Provenance (verified/assumed): Verified first-hand. Composition logic verified against prologue#E5's real canon text via `brain query`. External claims verified via live WebSearch results quoting/paraphrasing nngroup.com's "Proximity Principle in Visual Design" and "The Principle of Common Region: Containers Create Groupings", lawsofux.com's Law of Proximity page, optimalworkshop.com's Gestalt principles article, and uxcel.com/gestaltprinciples.com on Common Region — cross-consistent across independent sources on both principles. Caveat for full transparency: direct WebFetch page-reads of those same hosts (plus en.wikipedia.org) returned HTTP 403 this session; the agent-proxy status endpoint confirmed that as an org egress-policy block on those destination hosts for this session, not a source-side failure, so verification here rests on WebSearch's live results rather than a full-page fetch.
- Link: session (brain train external research: prologue + onboarding); WebSearch queries as listed in Design; agent-proxy status confirming the WebFetch 403s were an egress-policy block, not a retryable error
- Composed: pappydapimp69/the-game-prologue/E5

## E25 — seed difficulty last chance hit point refresh gap
- Date: 2026-07-13
- Project: pappydapimp69/the-game-prologue
- Tags: [gamedesign][difficulty][balance]
- What: `brain train new-domain difficulty` (0 existing entries tagged — seeding from a real scenario). `projects/pappydapimp69__the-game-prologue.md#E23` gates the first lethal HP crossing PER ENCOUNTER to a visible 1-hp save, rather than removing/capping the damage source itself. External research (WebSearch — direct WebFetch blocked by this session's org egress policy, confirmed via the agent-proxy status endpoint) confirms this is a well-established, NAMED design pattern — TV Tropes' "Last Chance Hit Point" — with real shipped examples (Fire Emblem: Path of Radiance halves lethal damage to leave 1 HP; Awakening's Miracle skill; Warhammer 40K: Darktide's "Until Death" survives at 1 HP + 5s invulnerability on a 90-SECOND REFRESH, not just "once per encounter"; No More Heroes 2 caps it at 5 uses total, fewer on harder difficulties).
- Why built: prologue#E23 states its gate as "per encounter, not per run, not unlimited" but doesn't specify what happens across consecutive encounters fought back-to-back. Every external example that gates on time/uses ALSO caps how often the save can retrigger ACROSS encounters (a cooldown, or a hard use-count), not just within one — a design detail prologue#E23 doesn't record either way.
- Design: Not a code sandbox — a pure external-fact seed for a genuinely uncovered domain tag, verified via WebSearch across two queries ("mercy invulnerability grace period game design one-shot kill prevention first encounter difficulty" and `"sudden death prevention" OR "last stand" game design guarantee survive first lethal hit once per encounter"`), cross-consistent across TV Tropes ("Mercy Invincibility", "Last Chance Hit Point") and independent game-specific sources (Darktide, Fire Emblem, No More Heroes 2).
- Got right: prologue#E23's core technique (gate the crossing, don't touch the damage number) matches established practice exactly, and its own boundary ("not per run, not unlimited") already avoids the crudest failure mode (a save that works every single hit, trivializing lethal damage entirely).
- Where/why it failed: N/A — not a bug in shipped code, a recorded gap. If "per encounter" is implemented as a flag that simply resets whenever a new encounter starts, a player who strings together several short, separately-triggered low-HP encounters gets a free save EVERY one of them with no cost or cooldown — every external example that persists the gate beyond one instance uses a cross-encounter throttle (a real-time refresh, or a hard use-count, often scaled by difficulty) specifically to prevent that.
- Fix: Not applied (seed entry, no source to modify). Record the open question for whoever implements or extends prologue#E23: decide explicitly whether the 1-hp-save gate resets per encounter with no cross-encounter cost, or carries a cooldown/use-budget across encounters — and if the former, that's a deliberate choice to make on purpose, not a default to fall into silently.
- Why this fix: Every real shipped example found gates BOTH within-instance (once per encounter/hit) AND across-instance (time or use budget) — prologue#E23 only records the first half, and the two are exploitable independently.
- Rule of thumb: A "guarantee one lethal-hit survival" mechanic (the named "Last Chance Hit Point" pattern) needs two independent gates, not one: bounding it WITHIN an encounter (prologue#E23 already has this) and bounding it ACROSS encounters (a cooldown or use-count) — every real shipped example found couples both; recording only the first leaves the second an open, unexamined question rather than a deliberate decision.
- Provenance (verified/assumed): Verified first-hand via WebSearch (live, attributable results citing TV Tropes' "Mercy Invincibility" and "Last Chance Hit Point" pages plus specific real-game mechanics — Darktide's 90-second refresh, No More Heroes 2's 5-use cap — cross-consistent across independent sources). prologue#E23's text re-read directly from canon via `brain query`. Caveat: direct WebFetch to tvtropes.org and related sources was not attempted separately (given this session's confirmed org egress-policy 403s on general web hosts) — verification rests on WebSearch's live results, not a full-page fetch.
- Link: session (brain train new-domain difficulty, prologue, external research); WebSearch queries as listed in Design
- Composed: pappydapimp69/the-game-prologue/E23

## E24 — accumulator fix needs a clamp or it spirals
- Date: 2026-07-13
- Project: pappydapimp69/the-game-prologue
- Tags: [gamedev][determinism][architecture]
- What: External research task (prologue domain) against `projects/pappydapimp69__the-game-prologue.md#E20` (real tick scheduler `nextTickAt = now + TICK_MS` loses ticks at low framerate — 0/400 jittery schedules matched the ideal tick count vs 400/400 for a "drain-and-subtract accumulator"). That accumulator pattern is the well-documented "Fix Your Timestep!" technique (Gaffer On Games, ~15 years canonical) — but the same literature documents a named failure mode the accumulator ALONE does not avoid: the "Spiral of Death" (a slow frame makes the accumulator run more catch-up steps, which takes more real time, which falls further behind, compounding). The standard fix is a clamp on the accumulator/max frame delta, capping catch-up steps per frame so the sim degrades to slow-but-stable instead of spiraling — prologue#E20 recommends the accumulator but records no clamp.
- Why built: prologue#E20 as written is directionally correct (accumulator beats jittery scheduling) but incomplete as an instruction — implementing "drain-and-subtract accumulator" literally, with no cap, trades a tick-drift bug for a worse one (unbounded catch-up under any real stall: a GC pause, a tab backgrounding, a slow device) with no guardrail recorded in canon.
- Design: Pure external-fact claim, verified via WebSearch (direct WebFetch to gafferongames.com returned HTTP 403 this session — same org egress-policy block as the prior loop, confirmed via the agent-proxy status endpoint). Two searches: "Glenn Fiedler fix your timestep accumulator game loop pattern" and `"spiral of death" fixed timestep accumulator clamp max frame time game loop fix`.
- Got right: prologue#E20's core comparison (accumulator vs jittery `nextTickAt`) is exactly the right fix for the bug it measured — 400/400 vs 0/400 is real, live-verified evidence the accumulator approach is correct for tick-count accuracy specifically.
- Where/why it failed: prologue#E20 never states the clamp. External sources are explicit and consistent that "clamping the maximum frame time" is the standard companion to the accumulator: "You can clamp at a maximum # of steps per-frame and the simulation will appear to slow down under heavy load... arguably better than spiraling to death." A related but distinct entry already exists in canon (`pappydapimp__lockstep.md#E6`: "Cap max frame delta or any stall becomes missed collisions") — that's the same clamp technique but recorded for a different symptom (missed collisions), never connected to prologue#E20's accumulator recommendation.
- Fix: Not applied to shipping code (flagging + canon gap only). The instruction to record: any accumulator/drain-and-subtract fix for tick loss must clamp the accumulator (or cap catch-up steps per frame) to a bounded maximum, so a real stall degrades to a temporary slowdown instead of an unbounded catch-up loop.
- Why this fix: lockstep#E6 already proves this exact team independently rediscovered the clamp technique for a different symptom — the value here is connecting it explicitly to the accumulator pattern prologue#E20 recommends, so the NEXT session implementing E20's fix doesn't have to independently rediscover the clamp after a real stall exposes the gap.
- Rule of thumb: A "drain-and-subtract accumulator" fix for tick/timestep loss is incomplete without a clamp on the accumulator (or a cap on catch-up steps per frame) — without it, a real stall (GC pause, backgrounded tab, slow device) causes the fix itself to compound into the well-documented "Spiral of Death" rather than the jitter it was meant to solve.
- Provenance (verified/assumed): Verified first-hand. prologue#E20's text re-read directly from canon via `brain query`. External claims verified via live WebSearch results quoting gafferongames.com's "Fix Your Timestep!" (via its own indexed summaries and a GameDev.net discussion thread specifically on "fix-your-timestep and the spiral of death") and a synthesized description of the accumulator-clamp technique, cross-consistent across independent results. Caveat: direct WebFetch to gafferongames.com returned HTTP 403 this session (confirmed via the agent-proxy status endpoint as an org egress-policy block, not a source failure) — verification rests on WebSearch's live results, not a full-page fetch.
- Link: session (brain train prologue domain, external research); WebSearch queries as listed in Design
- Composed: pappydapimp69/the-game-prologue/E20
- Cited-by: 2026-09-29 · projects/local__sandbox-lockstep-frame-delta-clamp-tick-parity.md#E1 · compatible · no sandbox · session (scheduled brain train pass 4)

## E23 — core defense boss onehit kill
- Date: 2026-07-15
- Project: pappydapimp69/the-game-prologue
- Tags: [gamedesign][balance]
- What: A tower-defense-style core (single shared HP pool) gets touched by
  bosses that deal 3-3.7x the damage of a regular enemy per contact (18-22 vs
  6). The contact-with-core code path already had a shield-gating grace
  window (from a prior fix, idea `SYSTEM/gamedesign/grace-window-any-hp-pool`)
  that stops SIMULTANEOUS arrivals from stacking damage in one burst — but it
  did nothing to stop a SINGLE hit from being lethal outright.
- Why built: user report "Bosses kill core in one hit." Diagnosed via direct
  Playwright reproduction (spawn a boss enemy exactly on the core, single
  `simStep`, inspect `core.hp` before/after) rather than passive/guesswork:
  confirmed a single boss contact from full 100 hp only ever did 18-22 damage
  (not remotely fatal alone). The real mechanism: the core's per-wave chip
  damage from ordinary enemies (partially offset by a 25%-of-max heal on wave
  clear) can leave it well under 22 hp by the time a boss wave (every 5th
  wave) arrives, and the boss's disproportionately large hit finishes it in
  one visible, unavoidable contact — reading to the player as "one hit kill,"
  even though the actual damage number was unremarkable and the shield-gate
  from the prior fix was working exactly as designed (gating repeat hits, not
  the first one).
- Design: contact-with-core computes `nextHp = core.hp - dmg`; previously
  applied unconditionally whenever outside the invuln window. Fix adds one
  more gate: if `nextHp <= 0` AND a per-wave `core.graceSaveUsed` flag is
  still false, clamp to `hp = 1` (not 0), consume the flag, and open a
  slightly longer invuln window (0.6s vs the normal 0.4s) instead of ending
  the game. `graceSaveUsed` resets in `startWave()` — one save available per
  wave, not per run, so it doesn't make the core permanently unkillable but
  also doesn't get "spent" once early in a 20+ wave run and then never help
  again.
- Got right: scoping the save to "per wave" rather than "per run" or
  "unlimited." Per-run would burn the safety net on an early, low-stakes wave
  and leave later boss waves exactly as exposed as before. Unlimited would
  make any single source of damage non-lethal forever, which breaks the game
  (core becomes unkillable by definition — a hit can never finish it off if a
  hit always leaves 1 hp). Per-wave means: one "how did that happen" surprise
  hit gets a warning and a second chance within that same encounter, but a
  second lethal hit — after the visible 0.6s grace flash — genuinely ends it.
- Where/why it failed: none yet reported; not deployed long enough to know
  if a single grace-save-per-wave is the right cadence (vs. per-N-waves, or
  scaling the window/reward with wave number). Flag if a later report says
  the core still feels like it dies too suddenly even with the save — the
  fix only prevents *literally one contact from full/partial hp to zero*, it
  does not reduce the underlying chip-damage accumulation across a wave that
  leaves the core low before the boss ever shows up.
- Fix: see Design above — `core.graceSaveUsed` flag, checked/consumed in the
  core contact-damage block, reset in `startWave()` and `newGame()`.
- Why this fix: minimal, additive change scoped exactly to the reported
  symptom (single-hit kill) without touching dmg values, wave pacing, or the
  already-shipped shield-gate window — consistent with the project's
  established pattern of narrow, verified patches rather than broad rebalancing.
- Rule of thumb: when one damage source (a boss, a crit, a burst mechanic) is
  a fixed multiple of the "normal" hit size against a shared HP pool that
  regenerates only in discrete chunks (not continuously), check whether that
  multiple alone can cross the full remaining-HP range the pool is expected
  to sit in between regen events — if yes, a flat/uncapped hit will
  eventually read as an "instant kill" even if the number itself is modest,
  and a once-per-encounter (not once-per-run, not unlimited) floor is a cheap
  way to convert a possible surprise kill into a visible warning without
  making the pool unkillable.
- Provenance (verified/assumed): Verified first-hand via Playwright: (1)
  direct single-contact test confirmed boss dmg alone (18-22) is not lethal
  from full hp; (2) targeted test with core pre-set below boss dmg confirmed
  the old code path would have zeroed hp/ended the game on that one contact;
  (3) post-fix, same low-hp setup now clamps to 1 hp and does NOT end the
  game, a second lethal hit after the grace window DOES end it, and the flag
  correctly resets on a fresh `newGame()`/new wave. Regression-tested against
  the existing wave-floor, single-upgrade-per-clear, and 25-wave no-NaN
  checks — all still pass.
- Link: session (Core Defense one-shot artifact, boss grace-save patch)
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-prologue.md#E25 · compatible · no sandbox · session (brain train new-domain difficulty, prologue, external research); WebSearch queries as listed in Design

## E22 — the game prologue quest kill objective matches by kind not instance
- Date: 2026-07-13
- Project: pappydapimp69/the-game-prologue
- Tags: [architecture][testing][gamedesign]
- What: Composing `sandbox-combined-narrative-flags#E1` (subscribing a quest listener by generic event TYPE alone, rather than a causal token tied to the specific triggering entity, is unsafe the instant more than one possible source of that type can exist — a same-type unrelated event silently satisfies the listener) with `the-game-prologue#E9` (quest-target entities don't exist in world state until `ACCEPT_QUEST` spawns them, making objective completion provably independent of PRE-acceptance actions) found that E9 only solves the TEMPORAL half of causal correctness — the real shipped kill-objective matching in `src/sim/reduce.js` (`obj.target === e.kind`) checks the killed enemy's KIND string, never its specific spawned entity id, inheriting narrative-flags#E1's exact type-only fragility. E9's existence-gating creates a false sense that the whole causal-token problem is solved, when a second axis (WHICH specific entity, not just WHEN) remains completely open.
- Why built: `brain train` surfaced `sandbox-combined-narrative-flags + the-game-prologue` as an untested seam requiring live-code verification, not just reasoning, per current policy (tension T22).
- Design: Imported the real, unmodified `makeWorld` (`src/sim/world.js`), `reduce` (`src/sim/reduce.js`), and `CONTENT` (`src/sim/content.js`) from this repo directly — no reimplementation. Ran four scenarios against the real "Clear the Road" quest (target kind `ironhusk`, spawned as `husk1`): (A) kill the real quest-spawned `husk1` — sanity control; (B) spawn an unrelated runtime entity sharing kind `ironhusk` (built with the exact shape `makeWorld` itself produces from `CONTENT.enemyKinds`, representing what any future content addition would look like with zero code changes) and kill ONLY that, never touching `husk1`; (C) negative control — kill the WRONG kind (`wardhusk`/`husk2`) and confirm it does NOT satisfy the `ironhusk` objective; (D) full exploit — complete the entire quest end-to-end without ever fighting `husk1`.
- Got right: Ran a sanity control (A) confirming the objective correctly advances when the real target is killed, AND a negative control (C) confirming kind-discrimination itself works fine (wrong kind does NOT falsely satisfy the objective) — isolating that the gap is specifically instance-identity, not a broken match function generally. Cross-checked the same codebase's tutorial arc system (`arcObserve`, its own entry E15), which DOES pin its boss-defeat check to a specific entity id (`e.target === arc.bossDef.id`) — confirming the "pin to instance, not type" discipline was already learned and correctly applied in one subsystem, three lines away from where it's missing.
- Where/why it failed: Scenario B's objective-progress array was bit-for-bit identical to Scenario A's (`[1,0,0,0]`) despite `husk1` never being touched — `husk1.alive` remained `1` (never killed) while the objective still advanced from killing the unrelated stray. Scenario D completed the entire quest (`quests.completed['clear-the-road'] === 1`) with `husk1.alive` still `1` at the end — the real quest-spawned target was never engaged at all. This is currently non-reachable as a player-facing bug only because prologue ships exactly one entity of each relevant kind (`ironhusk`->husk1, `wardhusk`->husk2) in its single region — an accident of current content scope, not an enforced invariant. `content.js` itself keeps an unused base `husk` kind "in case it's reused later," which would immediately create a second `ironhusk`-adjacent instance risk.
- Fix: Not applied to shipping code (flagging only, per this session's established pattern). Kill/collect objective matching should key on the causal token of the SPECIFIC spawned entity (e.g. an objective-scoped entity id set at `ACCEPT_QUEST` spawn time, matched against the killed entity's id) rather than its kind string — mirroring the pattern the same repo's `arcObserve` system already uses correctly for boss defeats.
- Why this fix: `questProgress`'s kind-based match (`obj.target === e.kind`) was presumably written this way because it's simpler when there's only ever one entity of a relevant kind — but that simplicity is exactly the "accident of current content scope" that narrative-flags#E1 warns is unsafe the instant a second same-type source can exist, and this codebase already has the correct fix pattern (`arcObserve`'s id-pinning) available to copy.
- Rule of thumb: In a quest/objective system, "target entities don't exist until accepted" (existence-gating, E9's territory) and "objective completion is checked by causal token, not by type" (E1's territory) are TWO INDEPENDENT requirements, not one — a codebase can fully satisfy the first while remaining wide open on the second, and satisfying the first can create false confidence that causal correctness is fully covered. Any kill/collect/reach-style objective matched by a kind/type/item field rather than a specific spawned entity id should be treated as latently unsafe the instant a second same-kind entity could ever exist anywhere in the game world, even when today's content makes that impossible by coincidence — check whether a sibling subsystem in the same codebase already solved this (here, `arcObserve` had) before assuming the fix needs to be invented.
- Provenance (verified/assumed): VERIFIED first-hand against the REAL, currently-shipping `pappydapimp69/the-game-prologue` source (`src/sim/world.js`, `src/sim/reduce.js`, `src/sim/content.js`), not a reimplementation — 4 scenarios including a sanity control (A), the exploit (B, D), and a negative control (C) ruling out a simpler "match is just broken" explanation. This is a live, currently-shipping structural gap, not merely theoretical — reachable the moment any future content addition introduces a second entity of an already-quest-targeted kind, which the repo's own code comments flag as a real intended future direction (the unused base `husk` kind kept "in case it's reused later").
- Composed: sandbox-combined-narrative-flags/E1, the-game-prologue/E9
- Link: session (brain train, sandboxed until satisfied), sandbox script quest_typematch_sandbox.mjs (live import of real repo source, real seeded RNG), live-unfixed structural gap flagged at src/sim/reduce.js questProgress/hitEnemy kind-matching, not applied

## E21 — stale capacity drives charge meter negative
- Date: 2026-07-13
- Project: pappydapimp69/the-game-prologue
- Tags: [gamedesign][input][state]
- What: `brain analyze graph` (untested seams: sandbox-combined-skilltree-formula ↔ the-game-prologue, shared=6 tags) surfaced this pair. Composed: projects/local__sandbox-combined-skilltree-formula.md#E3 (a lazy-refill token bucket goes stale when its CAPACITY is a dynamic formula output rather than static config — raw tokens stay above a newly-shrunk capacity in 200/200 trials until the next request happens to trigger refill; fix with an explicit re-clamp hook fired at the capacity-change event) and projects/pappydapimp69__the-game-prologue.md#E7 (a hold-to-charge meter needs an authoritative hold-counter and a rate shaped by BOTH hold duration and current fill percent — throttle near-full hard enough to override the ramp bonus). prologue#E7's own description ("rate shaped by ... current fill percent") implies a formula like `rate = f(fillPercent)`, with nothing in its text saying `fillPercent` must be clamped to `[0,1]` first. skilltree-formula#E3's exact bug (a formula-derived capacity shrinking without an explicit re-clamp) would leave a charge meter's raw value ABOVE its new capacity — driving `fillPercent` above `1.0`. Built and ran a sandbox confirming this transfers, with a worse consequence than skilltree-formula#E3's own case: the rate formula goes NEGATIVE, meaning the meter drains while the player is still holding the charge button.
- Why built: skilltree-formula#E3 was recorded in a resource/token-bucket context with no rate-formula angle; prologue#E7 was recorded describing a rate SHAPE (slows near full) with no capacity-staleness angle. Neither lesson considers what happens if prologue#E7's charge cap is ever a formula output (a stat-driven max charge, entirely plausible in an RPG with upgradeable gear/skills) rather than a fixed constant.
- Design: `engine.mjs` simulates a hold-to-charge meter with `raw` (accumulated charge) and `capacity` (starts at 100), where `rate = BASE_RATE * (1 - fillPercent)` — a direct, literal implementation of prologue#E7's own description, unclamped. At a fixed tick (200), `capacity` shrinks to 50 (skilltree-formula#E3's exact scenario: a formula recalculation, e.g. a stat debuff). Two variants: naive (no re-clamp, the bug) and fixed (skilltree-formula#E3's own prescribed fix — `raw = Math.min(raw, capacity)` fired immediately at the capacity-change event).
- Got right: Before the capacity shrink (ticks 0–199), both variants are identical and correct — the meter charges normally toward 100, rate slowing as it approaches full, exactly matching prologue#E7's intended shape.
- Where/why it failed: Immediately after the capacity shrink (tick 200), the naive variant's `fillPercent` jumped to `1.475` (raw=73.44 over the new capacity 50) and `rate` became `-19.006` — strongly negative. By tick 260, `raw` had fallen to `60.5`, DOWN from `73.1` at tick 201 — the meter was actively draining while the player, from their perspective, was still holding the charge button and expecting the meter to stay full or keep charging. This is a worse failure than skilltree-formula#E3's own recorded case (which only found the value stuck ABOVE cap until the next refill, not a runaway reversal), because prologue#E7's specific rate-shaping formula amplifies an over-100%-fill-percent into an increasingly negative rate.
- Fix: Apply skilltree-formula#E3's exact fix — an explicit re-clamp hook (`raw = Math.min(raw, capacity)`) fired AT the capacity-change event, not deferred to the meter's own lazy update path — confirmed in the sandbox to hold `fillPercent` at exactly `1.0` and `rate` at exactly `0` immediately after the shrink, with no drain.
- Why this fix: Neither individual finding is new — the value of the composition is showing that prologue#E7's rate formula, taken as literally described, is not merely "unprotected" against a formula-derived capacity the way skilltree-formula#E3's token bucket was — it actively INVERTS into meter-drains-while-held, a more severe and more player-visible failure mode than skilltree-formula#E3's own stale-until-next-refill case.
- Rule of thumb: Any rate/behavior formula that reads a resource's `fillPercent = raw/capacity` (prologue#E7's shape) must be paired with skilltree-formula#E3's re-clamp-at-capacity-change discipline the moment that resource's capacity is EVER formula-derived rather than a fixed constant — and additionally, defensively clamp `fillPercent` itself to `[0,1]` before feeding it into any rate formula, since a formula written to only ever expect `fillPercent <= 1` (as a literal reading of "rate shaped by current fill percent" would produce) can invert sign entirely once that assumption is violated, not merely produce a slightly-wrong number.
- Provenance (verified/assumed): VERIFIED first-hand — built `engine.mjs` (zero RNG, zero wall-clock, a fixed 400-tick run with a scripted capacity-shrink event at tick 200), confirmed the naive variant's fill-percent exceeds 100% (1.475) immediately after the shrink, its rate goes negative (-19.006), and its raw charge value is measurably lower 60 ticks later than immediately after the shrink (60.476 vs. 73.128) — an active drain, not merely a stale value. Confirmed the fixed variant holds fillPercent at exactly 1.0 and rate at exactly 0 throughout. Confirmed deterministic/reproducible across two independent process invocations of `node engine.mjs`, output diffed byte-identical.
- Link: session 01KxkbJUq8YajH8GokSZYYHy; `brain analyze graph` untested seam (sandbox-combined-skilltree-formula + the-game-prologue); sandbox `engine.mjs`, scratchpad `loop6-charge-meter-stale-capacity/` (run twice as separate process invocations, outputs diffed byte-identical)
- Composed: local/sandbox-combined-skilltree-formula/E3, pappydapimp69/the-game-prologue/E7
- Cited-by: 2026-10-09 · projects/local__sandbox-kernel-gamedesign-four-clauses.md#E1 · compatible · sandboxes/2026-10-09__four-clause-game-definition-ablation-and-defect-triage.py · observed RESULT: PASS every ablation fails its own probe=True, leaks={'a': ['b', 'c'], 'b': ['d'], 'c': ['b'], 'd': []}, a-b-c-d order misattributes drop-c to b while a-c-b-d attributes all=True; partial signal survivors=['a==2', 'a==2&par==0'] aft… · scheduled brain train pass 5 (gap mode)

## E20 — the game prologue tick scheduler loses ticks at low framerate
- Date: 2026-07-13
- Project: pappydapimp69/the-game-prologue
- Tags: [determinism][framerate][architecture]
- What: Composing `sandbox-combined-game-loop#E1`/`#E2` (a deterministic real-time loop must keep tick-count-for-a-fixed-wall-time-window driven by an exact integer/fixed-point accumulator with drain-and-subtract, or the tick count for the same elapsed real time depends on the frame schedule) with `the-game-prologue#E14` (the team drew a hard integer-lattice line for CONTENT — day/night, difficulty are pure integer functions of `state.tick` — but only verified it via a fixed scripted command replay, never real wall-clock scheduling) found that prologue applies E1/E2's discipline to `tick`'s MEANING but not to the mechanism that ADVANCES `tick` in real play: `src/app/game.js`'s tick scheduler (`nextTickAt = now + TICK_MS`, re-anchoring the next threshold to the actual firing time rather than the ideal schedule point) permanently banks every frame's overshoot as delay instead of carrying it as a remainder, exactly the bug class E1/E2 catalogued and fixed with an integer-lattice accumulator.
- Why built: `brain train group` surfaced `the-game-prologue + sandbox-combined-game-loop` as an untested seam requiring live-code verification, not just reasoning, per current policy (tension T22).
- Design: Built a Node.js harness that imports and executes the REAL `startGame()` from `src/app/game.js` unmodified, stubbing only inert browser globals (`window`, `navigator`, `localStorage`, a Proxy-based canvas 2D context, a controllable `requestAnimationFrame`) so the real scheduling code runs against synthetic, deterministic frame timestamps (seeded mulberry32 for jitter generation only, no wall-clock/Math.random driving the actual measurement). `initialWorld` was pre-supplied via the real `makeWorld` to skip the intro modal so the real tick-scheduling branch executes every frame. Experiment 1: ran 400 jittery frame schedules, each summing to exactly 60000ms, counting real `TICK` dispatches against the ideal count (`TOTAL_MS/TICK_MS`, floor). Experiment 2: measured real elapsed wall time to reach `world.tick=1000` under steady 60fps, 60fps-with-stalls, and steady 30fps schedules. Experiment 4 (comparison only, not shipping code): re-ran Experiment 1's identical 400 schedules through a plain drain-and-subtract accumulator, the pattern E1/E2 prescribe.
- Got right: Ran the REAL shipping `game.js` code end to end, not a reimplementation of the described pattern — the divergence measured is a property of currently-shipped code. Distinguished isolated stalls (a single or several 400ms pauses under an otherwise-fast base frame rate) from sustained lower frame rate, finding stalls are harmless/self-absorbing while sustained low frame rate produces a permanent, proportional drift — avoiding the overbroad claim "any frame variance breaks this."
- Where/why it failed: Across 400 jittery schedules summing to 60000ms each, the real scheduler matched the ideal tick count (120) in 0/400 cases, ranging from 106 to 119 ticks observed (up to ~12% ticks lost at the low end). The identical 400 schedules run through a plain drain-and-subtract accumulator (comparison-only, not shipping code) hit the ideal exactly in 400/400. Reaching `world.tick=1000` (ideal 500000ms) took 499501ms under steady 60fps AND under 60fps with one or six 400ms stalls (isolated stalls fully absorbed, no accumulated drift) — but took 532799ms under steady 30fps, a permanent +32799ms (~6.6%) drift, meaning a 30fps player needs 33.3 real seconds more than a 60fps player to reach the same in-game tick over an ~8.3-minute span.
- Fix: NOT applied to shipping code (flagging only, per this session's established pattern of not modifying shipping code without explicit confirmation). The known-correct fix pattern is already documented in `sandbox-combined-game-loop#E2`: replace `nextTickAt = now + TICK_MS` with a drain-and-subtract accumulator that carries overshoot as a remainder (`acc += dt; while (acc >= TICK_MS) { dispatch TICK; acc -= TICK_MS }`) rather than re-anchoring to the actual firing time.
- Why this fix: `nextTickAt = now + TICK_MS` discards the overshoot past each threshold every single frame; on a sustained lower frame rate, that per-frame loss doesn't average out, it accumulates linearly across the whole session, which is exactly the accumulator-vs-reset distinction sandbox-combined-game-loop#E1/E2 already names as the general fix for this bug family — the same family already documented live in `the-game-the-recursion#E16`'s movement-cadence bug and this session's `the-game-wrong-sky#E9` composition, now confirmed as a THIRD live instance in a third real shipped game.
- Rule of thumb: "Keep authoritative state on the integer lattice" (content keyed on an integer tick, per E14) is necessary but not sufficient — the SCHEDULER that advances that lattice forward in real time must independently satisfy the schedule-independent tick-count property, and a fixed-command-sequence golden-fingerprint replay test provides ZERO coverage of that scheduler, since it bypasses wall-clock scheduling entirely by construction. Any project with both a "content is a pure function of an integer tick" architecture and a real-time `requestAnimationFrame`-driven scheduler should specifically audit the scheduler's own threshold-advance logic for `nextX = now + interval` (reschedule-from-actual-firing-time, buggy) vs. accumulator drain-and-subtract (schedule-independent, correct) — the content-side integer discipline gives no assurance about the time-side discipline.
- Provenance (verified/assumed): VERIFIED first-hand against the REAL, currently-shipping `pappydapimp69/the-game-prologue` source (`src/app/game.js` lines 19, 326-329, `startGame()` executed unmodified via a Node harness with only inert browser-global stubs) — 400 jittery frame schedules (0/400 matching ideal tick count, vs. 400/400 for a comparison accumulator), plus a direct wall-time-to-fixed-tick measurement showing isolated stalls are harmless (0 drift beyond a fixed startup offset) while sustained 30fps produces a real, permanent ~6.6% game-clock slowdown relative to 60fps. This is a live, currently-shipping, real-time-scheduling bug — not a theoretical risk — undetected by the existing golden-fingerprint smoke suite because that suite replays a fixed command script and never exercises wall-clock-driven scheduling. NOT fixed in this session; flagged for explicit confirmation before any shipping-code change, per this session's established pattern.
- Composed: sandbox-combined-game-loop/E1, sandbox-combined-game-loop/E2, the-game-prologue/E14
- Link: session (brain train 3 groups + 2 edges, sandboxed until satisfied, loop 3), harness.mjs (real startGame() executed via Node with browser-global stubs, real frame-schedule sweep), live-unfixed bug flagged at src/app/game.js lines 326-329, NOT applied — pending explicit confirmation
- Cited-by: 2026-07-26 · projects/local__sandbox-combined-cutscene-resume.md#E1 · compatible · no sandbox · this session; sandbox scripts compose_cutscene_save.js and compose_testd_v2.js (scratchpad, not committed)
- Cited-by: 2026-07-18 · projects/pappydapimp69__draft.md#E12 · compatible · no sandbox · session 7195397b-63a9-5efe-a80b-2792eaa6645e (`brain train edge`, top-ranked pair dog + the-game-prologue); sandbox `scratchpad/train_edge/sandbox.py`, run twice as independent process invocations, outputs diffed identical
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-prologue.md#E24 · compatible · no sandbox · session (brain train prologue domain, external research); WebSearch queries as listed in Design

## E19 — the game prologue quest gating perturbs shared rng stream
- Date: 2026-07-13
- Project: pappydapimp69/the-game-prologue
- Tags: [determinism][architecture][testing]
- What: Composing `the-game-prologue#E9` (quest-target enemies/pickups don't exist in world state at all until `ACCEPT_QUEST` spawns them — existence-gating, chosen specifically to make quest completion provably independent of pre-acceptance player actions) with `the-game-the-answering-deep#E3` (gating a previously free-roam enemy behind a quest shifted every subsequent `nextInt(state.rng, ...)` call in the shared stream, silently breaking an unrelated fire-timing test) found the same mechanism is live in prologue's own currently-shipping code: an entirely narrative/pacing choice (WHEN a player accepts a quest) measurably changes a later, causally-unrelated RNG-driven combat outcome, purely because the quest's spawned enemy(ies) consume rolls from the same shared stream once they exist and become AI-adjacency-eligible.
- Why built: `brain train group` surfaced `the-game-prologue + the-game-the-answering-deep` as an untested seam requiring live-code verification, not just reasoning, per current policy (tension T22).
- Design: Imported prologue's real, unmodified `src/sim/world.js` (`makeWorld`) and `src/sim/reduce.js` (`reduce`, with the game's own seeded `sfc32` RNG) directly — no reimplementation. Reproduced the real app-level AI dispatch loop from `src/app/game.js` verbatim (`for (const id of Object.keys(world.enemies).sort()) { if adjacent && alive -> dispatch ENEMY_STRIKE }`, since `game.js` itself is a browser-loop file not importable headlessly), and used a real BFS pathfinder against the region's actual blocked-tile set (a naive greedy-stepping first attempt was discarded after a wall at x=10 exposed it as wrong, before trusting any results). Ran two scenarios per seed, same final unrelated action (`MELEE` on the always-present, non-quest-gated `stalker1`): (A) accept `clear-the-road` (spawns `husk1`/`husk2` per E9), walk adjacent to `husk1`, let the real AI loop drive two `ENEMY_STRIKE`s from it, then MELEE `stalker1`; (B) never accept the quest (husks never exist, per E9), MELEE `stalker1` at the equivalent point. Repeated across 8 seeds.
- Got right: Discarded a naive greedy-stepping pathfinder after it produced a wrong result against a real wall, replacing it with a real BFS against the actual blocked-tile set before trusting any measurement — avoiding a false negative from a broken harness rather than a broken mechanism. Distinguished "the derived damage number matched by chance" (2/8 seeds, expected given a narrow 3-6 damage range) from "the RNG state actually matched" (0/8 seeds — full state diverged in every single seed), correctly treating the 2 coincidental damage matches as consistent with, not contrary to, the mechanism.
- Where/why it failed: 6 of 8 seeds showed the identical unrelated `MELEE` action against `stalker1` producing a different damage roll purely because the husk quest was accepted earlier and its spawned enemy struck back once via the real AI loop — nothing about the player's gear, skill, or the stalker fight itself changed. The underlying RNG state (`{a,b,c,d}`) diverged in all 8/8 seeds; only the derived damage value occasionally landed on the same number by chance. The mechanism is structurally identical to answering-deep#E3's already-documented shape, but surfaces through prologue's adjacency-gated command-dispatch loop rather than answering-deep's unconditional per-tick "always roll" AI discipline — confirming the underlying risk (a shared RNG stream is perturbed by ANY change to which entities exist/roll and when) is not specific to one AI architecture.
- Fix: Not applied to shipping code (flagging only, per instructions). This is not currently a failing test — prologue's golden-fingerprint test (E1) replays one fixed command script (`demo.js`) and hashes the result, so it is self-consistent and won't break on its own. The exposure is real but latent: any future multi-tick probabilistic test, or balance assumption, spanning "accept this quest" and "fight this unrelated enemy" would inherit answering-deep#E3's exact fragility, and two players who play identically except for WHEN they accept the husk quest can get measurably different combat outcomes elsewhere, for reasons invisible to design and code review alike.
- Why this fix: E9's existence-gating pattern was built specifically to make quest completion provably independent of pre-acceptance actions — a genuinely correct fix for the problem it targets. This finding shows a good, deliberate content-gating pattern is ALSO, unavoidably, a population-timing change from the shared RNG stream's point of view, which is a cost E9's own entry does not name.
- Rule of thumb: In a single-shared-seeded-RNG-stream sim, any design pattern that changes the timing or existence of RNG-consuming entities — including a correct, bug-preventing pattern like quest existence-gating (E9) — is itself a population-perturbing content change from the RNG stream's perspective. This holds even when the affected systems look causally unrelated (a stalker fight has nothing to do with a husk quest) and even without an unconditional per-tick "always roll" AI discipline to blame (prologue's adjacency-gated dispatch is enough). Any content pattern that adds, removes, or delays entities (existence-gating, spawn timers, conditional unlocks) needs to be treated as an RNG-stream perturbation risk for any probabilistic test or balance assumption that spans it, not just evaluated on its own narrower correctness goal.
- Provenance (verified/assumed): VERIFIED first-hand against the REAL, currently-shipping `pappydapimp69/the-game-prologue` source (`src/sim/world.js`, `src/sim/reduce.js`, plus a verbatim-reproduced `src/app/game.js` AI dispatch loop and a real BFS pathfinder against actual map data), not a reimplementation — 8 seeds, RNG-state divergence in 8/8, derived-damage divergence in 6/8 (2/8 coincidental matches consistent with a narrow damage range). This is a live-verified latent structural fragility in currently-shipping code, not a currently-failing test — no existing test in the repo exercises this specific cross-system interaction, so nothing is currently broken, but the mechanism is real and reproducible on demand.
- Composed: the-game-prologue/E9, the-game-the-answering-deep/E3
- Link: session (brain train 3 groups + 2 edges, sandboxed until satisfied, loop 3), sandbox script rng_entangle_sandbox.mjs (live import of real repo source, real BFS pathfinder, verbatim-reproduced AI dispatch loop), latent fragility flagged in this same shipping repo, not fixed (pending explicit confirmation per this session's established pattern)
- Cited-by: 2026-09-28 · projects/local__sandbox-kernel-system-determinism.md#E3 · compatible · sandboxes/2026-09-28__train-gap-b01.py · session 2026-09-28, brain train gap batch 1 loop 4
- Cited-by: 2026-10-10 · projects/pappydapimp69__brainwork.md#E55 · compatible · sandboxes/2026-10-10__seeded-rng-save-replay-and-shared-stream-vs-per-entity-substream.py · observed RESULT: PASS S1 determinism, S2 resume equal (replay 5000 vs 1 steps), S3 leak diverges at tick 10, S4 shared stream keeps 0.11 of later rolls vs id-keyed substream 1.00 vs ordinal-keyed 0.18 · brain train auto session 2026-10-10; session_012uwXvPE6LveBmBN1pFKYfK
- Cited-by: 2026-10-12 · projects/local__sandbox-seeded-rng-state-words.md#E1 · compatible · sandboxes/2026-10-12__seeded-rng-state-words-vs-count-and-stream-splitting.py · observed RESULT: PASS state words reload exact 8/8 (replay cost 49999 rolls vs 4 words), count replay diverged 8/8, control exact 8/8, shared stream perturbed 8/8 with shift 8/8, split streams 0/8, in-stream insertion 8/8. · scheduled brain train session, loop 2 pass 1; session_018RFPy3DMrymTRHnMWEoTT9

## E18 — the game prologue archetypes independently match the pareto diversity fix
- Date: 2026-07-13
- Project: pappydapimp69/the-game-prologue
- Tags: [gamedesign][gamedev]
- What: `sandbox-dbz-combat#E2` (2026-07-11, sandbox-verified) found that a menu of options differing only along a single monotonic power axis collapses to one dominant choice, and the fix is Pareto structure — each option must LEAD exactly one axis and PAY on another. `the-game-prologue`'s actual archetype system (`src/sim/content.js`, authored 2026-07-07/09 — chronologically BEFORE the sandbox finding existed) already matches this structure exactly: three archetypes, each with a `skills: {melee, aura, perception}` triple that is a rotation of `{2,1,1}` (Brawler leads melee, Channeler leads aura, Seeker leads perception, each paying 1 on the other two axes) rather than a shared pool distributed by a single "power level."
- Why built: `brain train group` surfaced `sandbox-dbz-combat + the-game-prologue` as an untested seam; checking the sandbox's abstract finding against this project's actual, already-shipped content revealed independent, pre-existing agreement rather than needing a new test.
- Design: N/A — a recorded-lessons-vs-live-code comparison, not a new build. Read `content.js`'s `archetypes` object directly.
- Got right: Checked the ACTUAL numbers in the live file rather than just noting "this project has archetypes, that's Pareto-ish" — confirmed the specific rotational `{2,1,1}` structure is exact (not merely "differentiated somehow"), which is what makes this a genuine structural match to the sandbox's fix rather than a loose analogy.
- Where/why it failed: N/A — this is a reinforcing finding, not a bug report. Flagging an honest limit: this confirms the STRUCTURE matches the fix pattern (each archetype leads one axis, pays on the other two, no single archetype leads on two axes or none) — it does NOT confirm the archetypes are actually BALANCED in practice (that would need the same "is each option ever uniquely optimal across real encounters" measurement sandbox-dbz-combat#E2 used, which wasn't run against this project's actual combat resolution in this session).
- Fix: Not applicable — no bug, no code change proposed.
- Why this fix: A no-op field is the honest answer here, and it's itself the point: this entry exists to record that an existing design choice, made without knowledge of the later sandbox finding, already satisfies that finding's fix — evidence the Pareto-rotation pattern is discoverable by ordinary game-design instinct, not just by dedicated balance simulation, which is useful precedent for judging future archetype/skill systems by eye before reaching for a full simulation.
- Rule of thumb: A skill/archetype/stat-differentiation system that gives each option a RATIO of the same fixed point-pool across multiple axes (rotational assignment: each option's "lead" stat and "pay" stats sum to the same total) is a cheap, verifiable structural check for Pareto diversity before ever needing to simulate balance — `grep` the actual content data for whether each option's stat block is a genuine permutation of the same value set (not just "different numbers") as a fast sanity check that a menu isn't already heading toward the monotonic-collapse failure mode sandbox-dbz-combat#E2 characterized, before investing in full balance simulation.
- Provenance (verified/assumed): VERIFIED first-hand — read `sandbox-dbz-combat#E2`'s recorded entry and `the-game-prologue`'s live `src/sim/content.js` directly, confirming the exact `{2,1,1}` rotational skill-block structure across all three archetypes (`brawler: melee:2,aura:1,perception:1`; `channeler: melee:1,aura:2,perception:1`; `seeker: melee:1,aura:1,perception:2`). The claim is scoped deliberately narrowly to this structural match; in-practice balance (whether each archetype is ever uniquely optimal across real encounters) is a separate, ASSUMED-plausible-but-unmeasured question this session's reading did not test.
- Composed: sandbox-dbz-combat/E2
- Link: session (brain train on groups and test 5 new edges), src/sim/content.js (archetypes.brawler/channeler/seeker), no code change

## E17 — the game prologue deferred cache bust still unfixed
- Date: 2026-07-13
- Project: pappydapimp69/the-game-prologue
- Tags: [browser][tooling][process]
- What: `the-game-prologue#E8` (2026-07-07) documented an entry-point-only cache-bust gap (`index.html`'s `<script>` tag versioned, but none of the ~30 nested relative `import` specifiers), explicitly named the complete fix (a deploy-time rewrite of every import specifier with a per-deploy token, matching `dog#E5`'s precedent), and deferred it as out of scope. `the-game-the-waiting-city#E8` (2026-07-09) independently hit the identical gap via a player bug report, recognized it as E8's already-catalogued shape, DESIGNED AND VERIFIED the complete fix (a GitHub Actions step rewriting every relative `.js` import across the whole module graph plus the entry tag, keyed to the commit SHA), and applied it to BOTH `the-game-the-waiting-city` and `the-game-wrong-sky` in the same session — but not back to `the-game-prologue`, the project where the gap was originally catalogued. Checked directly against this repo's CURRENT state: `index.html` still reads `<script type="module" src="src/main.js?v=20260707-1">` (the literal, unchanged token from E8's original date) and `.github/workflows/deploy-pages.yml` has no import-rewrite step at all — just `actions/upload-pages-artifact@v3` with `path: '.'`. The deferred gap is still live in the one project that originally deferred it, three days after its own fix was verified working two repos over.
- Why built: `brain train edge` ranked `the-game-prologue + the-game-the-waiting-city` as the top accessible untested pair (shared=11 tags); reasoning from both projects' recorded entries surfaced that waiting-city#E8 already names this exact scenario as its own rule of thumb ("assume every sibling that copied the same pattern... ALSO has it — and fix it in all of them in the same pass") — and then checking THIS repo's actual current files confirmed the rule's own prediction: the fix pass that covered two siblings didn't cover the third, the original source of the catalogued gap.
- Design: N/A — a recorded-lessons synthesis, verified against live repo state (`index.html`, `.github/workflows/deploy-pages.yml`) rather than a new sandbox.
- Got right: Didn't stop at "the two entries reference each other" — went one step further and checked whether the specific, concrete claim (prologue still has the gap) was actually still true in the live repo right now, rather than assuming a 2026-07-07 entry's "deferred" status was necessarily still accurate three sessions later. It was.
- Where/why it failed: waiting-city#E8's own rule of thumb — fix a catalogued, deferred, sibling-shared gap in every project that has it, not just the one under investigation — was not applied to its own origin project. This is a second-order instance of the exact same failure class as the-game-prologue#E13/the-game-the-recursion#E15 pairing filed earlier this session (an explicitly-named mitigation existing as a documented lesson somewhere, but not as an enforced step run against every affected project automatically) — here even sharper, because the mitigating rule of thumb was written IN THE SAME ENTRY that fixed two of the three affected projects, and still didn't trigger a check of the third.
- Fix: Not applied in this session (a CI/CD-pipeline change to a real deployed project is outside this session's Brain-training scope without explicit confirmation) — the fix to apply, already fully specified and verified working twice: add the deploy-time import-specifier rewrite step to `.github/workflows/deploy-pages.yml` (matching the step already shipped in `the-game-the-waiting-city`'s and `the-game-wrong-sky`'s `deploy-pages.yml`, keyed to the commit SHA), covering `index.html`'s script tag and every relative `.js` import across `src/`.
- Why this fix: The fix is not a design question — it's already been designed, implemented, and verified end-to-end in two sibling projects with identical architecture; porting it is a known-safe copy, not new engineering.
- Rule of thumb: When a "fix it in every sibling that has this pattern" mitigation gets applied, explicitly re-check the ORIGIN project the gap was first catalogued in — it's easy to fix the projects a new bug report actually points at while forgetting the source project sits right there, unfixed, with its own entry still saying "deferred." A catalogued-but-deferred gap doesn't expire just because a sibling fixed its own copy; it stays open until it's checked against the actual current state of every project that shares the pattern, including the one where it was first found.
- Provenance (verified/assumed): VERIFIED first-hand — read `the-game-prologue#E8` and `the-game-the-waiting-city#E8` directly, then confirmed against this repo's live `index.html` (line 18, literal `?v=20260707-1` token unchanged) and `.github/workflows/deploy-pages.yml` (no rewrite step present) that the gap is still live right now, not just historically documented.
- Composed: the-game-prologue/E8, the-game-the-waiting-city/E8
- Link: session (brain analyze and train new edges), no code change applied in this session — diagnostic finding pending explicit confirmation to port the already-verified fix
- Cited-by: 2026-08-03 · projects/pappydapimp69__mirage.md#E4 · compatible · no sandbox · MIRAGE crafting-deception session; `tools/stamp-version.mjs` and the "every module import and asset URL carries the current BUILD token" check in tests/logic.test.mjs.
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-wrong-sky.md#E15 · compatible · no sandbox · session (brain train on groups and test 5 new edges), no code change — a live-state-verified synthesis

## E16 — the game prologue saga independence predicted its own drift
- Date: 2026-07-13
- Project: pappydapimp69/the-game-prologue
- Tags: [process][gamedev][saga]
- What: `the-game-prologue#E13` documented the saga's deliberate architecture decision — repos stay structurally independent (clone-and-freeze only, spine re-established per-repo as a documented PATTERN TO REPEAT, never shared code) — and explicitly named the accepted cost: "a genuine improvement or bug found in the spine does NOT propagate automatically — each repo would have to re-adopt it by hand... there is also drift risk." `the-game-the-recursion#E15`, filed two days later from the opposite (retrospective, concrete) direction, found exactly that predicted cost actually happening: Phase 5's `P1: Input + UI rebuild` scaffolded touch input from scratch instead of porting forward the three immediately-prior phases' already-solved, more elegant canvas-integrated touch pattern (verified structurally identical across all three siblings). Composing the two: E13 accepted drift as a cost worth paying for isolation-safety, but never turned "check whether a sibling already solved this" into a required process step — SAGA-ROADMAP.md documents WHAT must be repeated (the determinism spine, save discipline) but not a step ensuring a new phase's "rebuild" actually starts from the siblings' solution rather than from zero.
- Why built: `brain train group` surfaced `the-game-prologue + the-game-the-recursion` as an untested seam within the proven cluster, with the explicit instruction to reason from recorded lessons rather than build something new — this synthesis is exactly that: pulling both entries and checking whether they reinforce, conflict, or combine into a higher-order rule.
- Design: N/A — a reasoning synthesis over two already-verified, already-filed entries, not a new artifact or sandbox.
- Got right: The two entries reinforce cleanly rather than conflicting — E13's abstract, prospective "we accept drift risk" and E15's concrete, retrospective "here is drift risk actually costing real engineering time" are the same claim viewed from before and after the fact, which is exactly the kind of cross-verification `brain analyze`'s edge-independence metric is designed to reward (raises confidence in both, not just re-states one). Neither entry needed correction; the synthesis is additive.
- Where/why it failed: The gap isn't in either individual entry — it's in what neither one, alone, made actionable. E13 documents the tradeoff as accepted and permanent ("you trade DRY... for the guarantee no installment can ever break a shipped one") without specifying a concrete mitigation for the drift half of that tradeoff. E15's own rule of thumb ("before scaffolding a subsystem fresh, grep the immediately-prior phase's source first") is the missing mitigation — but it was derived ad hoc, mid-session, framed as a lesson for THIS project rather than as a standing process requirement for the saga as a whole, so a sixth phase starting today would have no more assurance of checking siblings than Phase 5 did before E15 was filed.
- Fix: Not implemented (no code/process change made in this session) — the concrete, actionable synthesis: SAGA-ROADMAP.md's Stage 0 checklist should explicitly require, for any subsystem a new phase scaffolds "fresh," a check of the immediately-prior phase(s)' implementation of that same subsystem before writing new code — turning E15's one-off rule of thumb into the standing mitigation E13's accepted tradeoff always needed but never specified.
- Why this fix: E13's independence choice is sound and doesn't need to change (isolation-safety is worth the duplication cost for a long-lived series) — but "accept drift risk" and "have no process step that reduces drift risk" are different decisions, and only the roadmap doc can close that gap since it's the one artifact every new phase actually starts from.
- Rule of thumb: When a deliberate architectural tradeoff names its own accepted cost (e.g., "we accept X will happen"), check whether anything in the project's own process actually mitigates X, or whether the cost is being paid in full every time with no attempt to reduce it — an explicitly-accepted cost is not the same as a cost with no available cheap mitigation, and a later concrete instance of that exact cost (like E15) is the signal to close the gap in the process doc itself, not just document the individual instance and move on.
- Provenance (verified/assumed): VERIFIED first-hand — both source entries (E13, E15) were read directly from their promoted memory entries; the composition/reasoning connecting them is new synthesis in this session, not independently re-verified against the SAGA-ROADMAP.md source text beyond what E13 already quoted.
- Composed: the-game-prologue/E13, the-game-the-recursion/E15
- Link: session (brain analyze then brain train on a new group), no code change to a shipping project — a pure recorded-lessons synthesis per `brain train group`'s instruction

## E15 — teach through observer overlay not tutorial mode
- Date: 2026-07-09
- Project: pappydapimp69/the-game-prologue
- Tags: [gamedev][gamedesign][state]
- What: How to teach the ~9 verbs of an action-RPG (move/talk/quest/pickup/
  break/melee/aura/shop/pass) to a new player. The team chose to build the
  opening arc as a sim-state OVERLAY that passively OBSERVES the events real
  gameplay already emits (`arcObserve(state, events)` runs after every
  command in reduce.js), rather than a separate scripted tutorial MODE with
  its own dedicated sandbox, locked inputs, or intercepted commands.
- Why built: the design goal (docs/PROPOSAL.md) was "teach one verb at a time
  through real play... never a separate tutorial mode." The arc is one of two
  plausible shapes for onboarding: (a) a bespoke tutorial level that scripts
  and gates the player through canned actions, or (b) an observer that watches
  the same authoritative gameplay and marks teaching steps done as they
  naturally occur.
- Design: `state.arc.steps` is a flat set of boolean teaching flags. After
  every command, `arcObserve` reads the emitted `events` and sets the matching
  step (`talked`→`s.talk`, `enemy_hit` with `kind:'aura'`→`s.aura`, etc.). It
  never intercepts or rewrites a command; the sim runs identically with or
  without the arc watching. When every step is 1 the finale boss spawns. Story
  text lives in content; only the observation/gating lives in the sim.
- Got right (the choice made): chose the observer-overlay over a separate
  tutorial mode. The player is playing the real game from frame one — the same
  reducer, the same world, the same verbs — and the tutorial is a read-mostly
  layer on top that simply notices progress. No duplicate "tutorial version"
  of any verb, no mode the game has to exit, no divergence between how a verb
  behaves in the tutorial and how it behaves after.
- Where/why it failed (the tradeoff accepted): because teaching steps are
  triggered by the SAME event stream that drives quests and combat, every step
  must be mapped NARROWLY or a stray real action satisfies a teaching step (or
  vice versa). The code comment is explicit: "the training crate completes
  `crate`; a future destructible objective won't" — each mapping is pinned to
  a specific id (`crate1`, `warden`, `training-capsule`, `clear-the-road`), not
  a generic type. A separate tutorial mode would have owned its own isolated
  objects and never had this cross-talk risk. The cost of the overlay is this
  permanent discipline: any new content that emits an event a teaching step
  listens for can accidentally advance onboarding, and the guide can only
  surface one hint at a time so ordering matters.
- Fix (what was chosen instead of the naive approach): instead of intercepting
  commands or spinning up a sandbox, the arc subscribes to already-emitted
  events and pins each teaching step to a specific entity id so it can only be
  completed by the intended object. The finale is gated on the conjunction of
  all step flags (`Object.values(s).every(v => v === 1)`), and the region exit
  is sealed until the arc completes — the arc controls PROGRESSION without
  controlling INPUT.
- Why this fix: teaching through the real systems means there is exactly one
  implementation of every verb, so what the player learns is literally the
  game they will keep playing — no tutorial-only behavior to unlearn. Observing
  events instead of intercepting commands keeps the authoritative reducer
  unaware of the tutorial, so the golden replay test and determinism are
  untouched by onboarding.
- Rule of thumb: to teach a game's verbs, prefer an observer overlay that
  watches the real event stream and marks progress, over a separate scripted
  tutorial mode — you get one canonical implementation of every verb and no
  mode to exit. The price is that every teaching trigger must be pinned to a
  SPECIFIC object/id, never a generic event type, or ordinary play will
  satisfy tutorial steps by accident; budget for that narrow mapping up front.
- Provenance (verified/assumed): verified first-hand from source — read the
  `arcObserve` header comment and body in src/sim/reduce.js (narrow per-id
  mapping, no interception, all-steps-then-spawn gate) and the design intent in
  docs/PROPOSAL.md and docs/STAGES.md Stage 4. The tradeoff (narrow-mapping
  discipline) is stated as the code's own rationale, not inferred.
- Link: commit 3e3b72c "Stage 4: the prologue arc"; src/sim/reduce.js
  (arcObserve), docs/PROPOSAL.md, docs/STAGES.md
- Cited-by: 2026-07-20 · projects/local__sandbox-capture-layer-starves-tutorial.md#E1 · compatible · no sandbox · session (this conversation, "brain train external research prologue" — draft + the-game-prologue seam); scratchpad `sandbox_capture_layer_starves_tutorial.mjs`; external source: https://generalistprogrammer.com/tutorials/game-analytics-complete-data-tracking-guide-2025.
- Cited-by: 2026-07-20 · projects/local__sandbox-capture-layer-starves-tutorial.md#E2 · compatible · no sandbox · session 7195397b-63a9-5efe-a80b-2792eaa6645e (bare `brain train`, re-verifying the flagged single-source edge `sandbox-capture-layer-starves-tutorial + draft`); sandbox `scratchpad/reverify_capture/sandbox.mjs`, run twice as independent process invocations, outputs diffed identical
- Cited-by: 2026-09-28 · projects/local__sandbox-capture-layer-starves-tutorial.md#E4 · compatible · no sandbox · scheduled brain train session 2026-09-28
- Cited-by: 2026-07-20 · projects/local__sandbox-resolver-starves-tutorial.md#E1 · compatible · no sandbox · session (this conversation, "brain train external prologue and onboarding"); scratchpad `sandbox_resolver_starves_tutorial.mjs`; external sources: https://www.nngroup.com/articles/contextual-menus-guidelines/, https://www.acagamic.com/blog/how-to-use-contextual-prompts-in-video-games.
- Cited-by: 2026-10-12 · projects/pappydapimp69__sevin.md#E12 · compatible · no sandbox · Sevin commits 4ffdd9c, 62b7ba4; session_0125c7UeqZXhwxqnu8spbVdh
- Cited-by: 2026-10-17 · projects/pappydapimp69__demo-disc.md#E45 · compatible · no sandbox · https://claude.ai/code/session_0189x5cwDWHdyFUT5WmrVCJq, Demo-disc commits 3769b3f and d411324

## E14 — sim presentation seam modifiers in sim juice out
- Date: 2026-07-09
- Project: pappydapimp69/the-game-prologue
- Tags: [gamedev][state][determinism]
- What: Where each new gameplay-adjacent feature is placed relative to the
  sim/presentation seam. The team drew a hard classification line: anything
  that CHANGES OUTCOMES (difficulty, day/night combat modifiers) lives in the
  authoritative integer reducer; anything purely FELT (screen shake, hit-stop,
  squash/lunge, cosmetic day/night tint) lives in the presentation layer and is
  a reaction to sim events, never a writer of sim state. The non-obvious call
  is hit-stop, which SOUNDS like it must affect game logic timing but was kept
  entirely presentational.
- Why built: Stages 3–5 added several features that each superficially "touch
  gameplay": a Gentle/Harsh difficulty, a day/night cycle that makes nights
  more dangerous, and juice (shake/hit-stop/squash). Each forced a placement
  decision, and the tempting shortcut — put the "modifier" or the "freeze"
  wherever it's easiest to wire — would have quietly corrupted the determinism
  guarantee the whole project is built on.
- Design: outcome-affecting modifiers are integer arithmetic inside reduce.js —
  enemy strike damage is `base + (difficulty==='harsh'?1:0) + (isNight(tick)?1
  :0)`; day/night is an integer world-clock keyed off `state.tick`
  (daynight.js, no transcendental math, so the src/sim determinism guard still
  passes) so it round-trips through save/load and replay. Juice lives in
  src/app/game.js: `hitStop(ms)`/`shake(mag,ms)` set presentation-only
  timers driven by emitted events; the day/night TINT lives in
  src/app/daynight-tint.js where easing math is free because it is
  presentation-only.
- Got right (the choice made): chose to classify by "does it change the
  outcome?" not "does it feel like gameplay?". Difficulty and night-danger are
  authoritative because they alter damage the golden replay must reproduce;
  juice is presentational because it alters nothing the sim decides. Hit-stop —
  the deceptive case — freezes gameplay LOGIC cadence but is implemented as a
  presentation-layer pause of dispatch while the render loop keeps running (so
  the shake/punch it triggered still animates), touching zero authoritative
  state. Result: the golden fingerprint was UNCHANGED across all of Stage 5's
  juice + day/night work.
- Where/why it failed (the tradeoff accepted): keeping hit-stop and all feel in
  the presentation layer means "feel timing" is NOT part of the authoritative
  timeline — it does not replay, does not appear in the golden fingerprint, and
  would not reproduce in a lockstep/replay scenario. You give up the ability for
  juice to ever influence outcomes or be part of the canonical record. The
  inverse cost: putting difficulty and day/night IN the sim means they are baked
  into the save and the fingerprint, so they cannot be changed mid-run as a mere
  UI toggle — a difficulty or clock change is a real authoritative state change,
  by design.
- Fix (what was chosen instead of a workaround): rather than the easy wiring
  (a presentation-layer damage multiplier, or a hit-stop that pauses the whole
  authoritative clock), each feature was placed by the outcome test. Modifiers
  went into the reducer as integers only (preserving the "no floats / no
  transcendental Math in src/sim" invariant); day/night was expressed as an
  integer function of `tick` so it needs no ambient clock read; juice was
  expressed as event-driven presentation timers that read sim events and write
  only render state.
- Why this fix: the sim/presentation seam only holds if placement is decided by
  a single crisp test — "does this change what the sim decides?" — applied even
  to features that FEEL like they belong on the other side. Outcome-affecting
  logic in the deterministic core keeps it replayable and testable; feel in the
  presentation layer keeps the core small and the golden fingerprint stable
  while juice is free to use floats and easing.
- Rule of thumb: at the sim/presentation seam, classify each feature by whether
  it CHANGES THE OUTCOME, not by whether it feels like gameplay. Outcome
  modifiers (difficulty, environmental damage) belong in the authoritative core
  as integers and become part of the replay/fingerprint; pure feel (shake,
  squash, tint) belongs in presentation, driven by sim events, writing only
  render state. Watch the deceptive cases — hit-stop "freezes the game" yet is
  correctly a presentation-layer pause of the render/dispatch cadence, not a
  freeze of authoritative state — and accept that feel timing is then not
  authoritative or replayable.
- Provenance (verified/assumed): verified first-hand from source — read the
  damage formula in src/sim/reduce.js (`difficulty==='harsh'` + `isNight(tick)`
  integer terms), src/sim/daynight.js (integer world-clock header comment,
  "cosmetic smoothing belongs in the presentation layer"), and the game.js
  juice block header ("Hit-stop briefly freezes gameplay LOGIC (not the render
  loop)... Screen shake and per-entity punch are pure cosmetic reactions").
  The golden-fingerprint-unchanged claim is from commit b2aeac0's own evidence
  (dd14f521 unchanged through Stage 5).
- Link: commit b2aeac0 "Stage 5: feel + ship" and 6147d6f "Stage 3"
  (difficulty); src/sim/reduce.js, src/sim/daynight.js, src/app/game.js,
  src/app/daynight-tint.js
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-prologue.md#E20 · compatible · no sandbox · session (brain train 3 groups + 2 edges, sandboxed until satisfied, loop 3), harness.mjs (real startGame() executed via Node with browser-global stubs, real frame-schedule sweep), live-unfixed bug flagged at src/app/game.js lines 326-329, NOT applied — pending explicit confirmation

## E13 — saga independent repos spine repeated not shared
- Date: 2026-07-09
- Project: pappydapimp69/the-game-prologue
- Tags: [process][gamedev][git]
- What: How to structure a 5–6 game saga that tells one continuous story. The
  team chose SIX INDEPENDENT REPOS, one per phase, where a later phase may
  clone an earlier repo and reuse its assets but can NEVER edit it, and the
  determinism/architecture spine is RE-ESTABLISHED in each repo at its own
  Stage 0 rather than imported from a shared engine/library/monorepo.
- Why built: the saga is one story across many games that will be built over a
  long span. The obvious engineering instinct is a shared engine (monorepo or
  a published `saga-core` package) so the determinism spine, save schema, and
  content systems are written once. The team chose the opposite: structural
  independence, with the ONLY cross-repo coupling being the `saga.v1` export
  code a player carries by hand.
- Design: docs/SAGA-ROADMAP.md states it directly — "Independent is
  structural, not just intentional: a later phase can clone an earlier repo and
  reuse its assets, but it can never edit it. Each phase repo is its own build,
  gated by its own `npm run smoke`, with its own STAGES.md." The determinism
  spine (integer authoritative state, seeded RNG, no ambient randomness/clock
  in src/sim, canonical-serialization golden fingerprint) is documented as "a
  pattern to repeat, not shared code to import (repos don't depend on each
  other)." Save data never crosses repos; only the export code does.
- Got right (the choice made): chose repeated-pattern independence over a
  shared engine. No repo can break another — there is no shared dependency
  whose change ripples into a shipped game. Each phase is independently
  buildable, shippable, and frozen once done (Phase 1 is "closed"); a sequel
  starts from a clone and evolves freely without fear of regressing the
  original, because it literally cannot touch it.
- Where/why it failed (the tradeoff accepted): deliberate DUPLICATION. The
  determinism spine, save-schema discipline, canonical serializer, RNG, and
  validation-ladder pattern are re-implemented in every repo instead of being
  written once and imported. A genuine improvement or bug found in the spine
  does NOT propagate automatically — each repo would have to re-adopt it by
  hand. A shared library would have given DRY and single-point fixes; the team
  traded that away for isolation. There is also drift risk: two repos can
  quietly diverge in how they implement "the same" spine.
- Fix (what was chosen instead of a workaround): rather than a monorepo or a
  versioned shared package (which would couple ship schedules and let one
  repo's change break another), the saga treats the spine as a REPRODUCIBLE
  RECIPE captured in each repo's Stage 0 + STAGES.md closure log, and captures
  cross-cutting patterns (determinism spine, additive-only save versioning) in
  SAGA-ROADMAP.md so each repo re-establishes them consistently. Assets flow by
  clone-and-freeze, progress flows by the export code — never by a live
  dependency edge.
- Why this fix: for a series of separately-shipped, long-lived artifacts where
  the top risk is one entry regressing another, isolation beats DRY. Copying a
  well-specified pattern into each repo costs some duplication but removes the
  entire class of "a shared-engine change broke a game that was already done."
  The coupling that MUST exist (player progress) is made explicit and minimal
  (one versioned code), not smuggled in through a shared codebase.
- Rule of thumb: when a project is really a series of independently-shipped,
  long-lived installments, consider making the repos structurally independent
  (clone-and-reuse, never edit) with the architecture spine repeated as a
  documented pattern rather than imported as shared code — you trade DRY and
  auto-propagating fixes for the guarantee that no installment can ever break
  a shipped one. Keep the unavoidable cross-installment coupling to a single
  explicit, versioned artifact.
- Provenance (verified/assumed): verified first-hand from docs/SAGA-ROADMAP.md,
  which states the independence rule, the "pattern to repeat, not shared code
  to import" line, and the "only the saga.v1 export code crosses repos"
  constraint verbatim; cross-checked against src/sim/saga.js (the sole
  cross-repo artifact) and docs/PROPOSAL.md. The duplication/no-auto-propagate
  cost is the direct logical consequence of the stated no-shared-code rule.
- Link: commit 3416e9b "Add saga roadmap"; docs/SAGA-ROADMAP.md, docs/
  PROPOSAL.md
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-prologue.md#E16 · compatible · no sandbox · session (brain analyze then brain train on a new group), no code change to a shipping project — a pure recorded-lessons synthesis per `brain train group`'s instruction

## E12 — saga carryover self contained signed code no backend
- Date: 2026-07-09
- Project: pappydapimp69/the-game-prologue
- Tags: [gamedev][state][tooling]
- What: How to carry a player's progress (archetype, skill levels, coins,
  named story choices) across the five separate games of an offline saga. The
  team chose a self-contained, player-visible export CODE —
  `SAGA1.<base64(canonical JSON)>.<fnv1a32 checksum>` — shown at the finale and
  pasted into the next game, rather than a backend account, cloud save, or a
  shared save file on disk.
- Why built: the saga is "single-player offline, zero dependencies, static
  hosting" (docs/PROPOSAL.md). Progress still has to survive from game 1 to
  game 2, which live in different repos/deployments. The realistic
  alternatives were (a) a server that stores each player's run, or (b) a
  self-contained code the player physically carries between games.
- Design: `exportSaga(state)` in src/sim/saga.js serializes the carried fields
  with the sim's own `stableStringify` (canonical, sorted-key), base64-encodes
  it, and appends an FNV-1a32 checksum of the payload, prefixed with a fixed
  `SAGA1` signature and a `saga.v1` version field inside the JSON.
  `importSaga(code)` validates prefix, checksum, version, and required fields,
  and NEVER throws on bad input — a mistyped code returns `{ok:false,error}`,
  not a crash. Every sequel accepts a code OR a fresh-start default.
- Got right (the choice made): chose the offline, self-contained signed code
  over a backend. No server to run, host, secure, or keep alive for a game
  meant to work offline forever; the carryover "just works" on static hosting
  with zero infrastructure, and the player owns their own progress as a string
  they can save anywhere.
- Where/why it failed (the tradeoff accepted): a checksum is integrity, not
  authenticity — FNV-1a32 detects a MISTYPED or corrupted code, but it is
  trivially recomputable, so a determined player can hand-edit the JSON, fix
  the checksum, and forge any archetype/skill/choice they want. A backend
  would have given server-authoritative, tamper-resistant progress. The team
  accepted forgeability because the game is single-player and offline — there
  is nothing to cheat against. The other accepted cost: the format is
  versioned FOREVER (the `SAGA1`/`saga.v1` contract is "decided in game 1"),
  so every future game must keep parsing old codes, and the player has to
  manually carry a code between games rather than progress syncing itself.
- Fix (what was chosen instead of a workaround): rather than reach for a
  server or cryptographic signing that offline single-player doesn't need, the
  code uses a plain integrity checksum sized to its ACTUAL threat model (typos,
  truncation, corruption — not adversaries), a fixed signature prefix for
  quick rejection of foreign strings, and an explicit version field so
  sequels can branch on format. `importSaga` treats every failure as a polite
  player mistake, never an exception.
- Why this fix: match the mechanism to the threat model. Single-player offline
  progress has no adversary, so integrity (did this code arrive intact?) is the
  real requirement and authenticity (did the player earn this?) is not worth a
  backend. Signing/versioning the format from game 1 makes the carryover a
  stable contract instead of an ad-hoc dump that every sequel has to
  reverse-engineer.
- Rule of thumb: for cross-installment progress in an offline single-player
  game, prefer a self-contained player-carried code (canonical-serialized +
  integrity checksum + fixed signature + version field) over a backend — but
  be clear that a checksum is corruption-detection, NOT anti-tamper; only add
  cryptographic signing if there is actually an adversary, and version the
  format from the first game because you will parse old codes forever.
- Provenance (verified/assumed): verified first-hand from source — read
  src/sim/saga.js in full (exact `SAGA1.<base64>.<fnv1a32>` format, checksum
  validation, never-throws import, version gate, reserved `techniques` field)
  and its header comment stating the format is "decided in game 1, versioned
  forever" and "the code is a courtesy, never a wall." The forgeability
  tradeoff is a direct read of the code (checksum is recomputable), stated
  here explicitly.
- Link: commit 3e3b72c "Stage 4: the prologue arc" (saga export); src/sim/
  saga.js, docs/PROPOSAL.md (carryover contract)

## E11 — explicit pages deploy over silent dynamic builder
- Date: 2026-07-09
- Project: pappydapimp69/the-game-prologue
- Tags: [process][tooling][git]
- What: How to deploy a zero-build static game to GitHub Pages. The team chose
  an EXPLICIT Actions workflow (`configure-pages` → `upload-pages-artifact` →
  `deploy-pages`) that runs the smoke suite as a gate first, instead of letting
  GitHub Pages' built-in dynamic builder deploy the repo automatically.
- Why built: the game is plain static ES modules with no build step, so the
  default "Deploy from a branch / dynamic Pages build" would appear to be the
  path of least resistance — no workflow file to write. The team rejected it for
  a stated, experience-backed reason.
- Design: `.github/workflows/deploy-pages.yml` triggers on push to main (and
  manual dispatch), runs `node scripts/smoke.mjs` as its first step, and only
  then configures/uploads/deploys the Pages artifact. The workflow header
  states the rationale: "Explicit workflow rather than relying on the dynamic
  Pages builder — a dynamic build can queue with no jobs and no visible
  failure... This one is inspectable in Actions," citing a prior pitfall
  (local__dbh.md#E6).
- Got right (the choice made): chose the explicit, test-gated workflow over the
  zero-config dynamic builder. Every deploy is visible in the Actions tab as a
  real run with real logs, and a deploy CANNOT ship unless the 50+ smoke tests
  (determinism golden, save/load, content validation ladder) pass — the deploy
  is a quality gate, not just a file copy.
- Where/why it failed (the tradeoff accepted): the explicit workflow is more to
  own and maintain — a YAML file with pinned action versions, permissions
  (`pages: write`, `id-token: write`), and a concurrency group — versus the
  dynamic builder's literally-nothing-to-write. If the workflow's action
  versions or Pages-permission model drift, that is now the team's problem to
  fix; the dynamic builder would have been Github's to maintain. The team
  accepted that maintenance surface to buy visibility and a test gate.
- Fix (what was chosen instead of a workaround): rather than trust the
  invisible dynamic builder (whose failure mode is a job that silently queues
  and never runs, leaving a "successful" deploy that never actually
  happened — the exact prior pitfall cited), the deploy is an explicit,
  inspectable pipeline with the smoke suite wired in as its entry gate, so a
  broken build fails loudly in Actions instead of shipping or silently
  no-op'ing.
- Why this fix: a deploy mechanism's worst failure is the SILENT one — a build
  that reports success while doing nothing sends you debugging the app when the
  new code never deployed. Paying a small, bounded maintenance cost (one
  workflow file) to make every deploy a visible, test-gated, inspectable run
  removes that entire class of phantom-deploy confusion, and the same gate stops
  a determinism/validation regression from ever reaching players.
- Rule of thumb: for static-hosting deploys, prefer an explicit, inspectable
  CI workflow with your test suite as its first gate over a zero-config
  "dynamic"/auto builder whose failure mode is a silent queue-with-no-jobs — the
  auto builder saves you a YAML file but can report success while deploying
  nothing, which is far more expensive to diagnose than the workflow is to
  maintain. Wire the smoke/test suite in as the gate so deploy doubles as a
  release check.
- Provenance (verified/assumed): verified first-hand from
  .github/workflows/deploy-pages.yml — read the full workflow (smoke step
  before configure/upload/deploy, permissions, concurrency) and its header
  comment stating the dynamic-builder-queues-silently rationale and citing
  local__dbh.md#E6. Cross-checked against commit b2aeac0's evidence that the
  workflow "runs smoke as a gate; not the dynamic builder, which can queue
  silently with no jobs."
- Link: commit b2aeac0 "Stage 5: feel + ship"; .github/workflows/
  deploy-pages.yml; prior pitfall projects/local__dbh.md#E6
- Cited-by: 2026-08-10 · projects/pappydapimp69__august-10.md#E1 · compatible · no sandbox · August-10 .github/workflows/pages.yml (both fixes commented inline)

## E10 — content snapshotted into save not referenced
- Date: 2026-07-09
- Project: pappydapimp69/the-game-prologue
- Tags: [gamedev][state][tooling]
- What: How a data-driven game's running save relates to its content
  definitions (regions, enemy kinds, items, quests, zones, archetypes in
  src/sim/content.js). The team chose to COPY content definitions INTO the
  authoritative world state at `makeWorld()` construction time, so a save is a
  self-contained snapshot — rather than storing lightweight references (ids)
  and re-reading the live CONTENT object at runtime.
- Why built: Stage 3 moved all content to pure data and made `makeWorld` build
  state from it. The choice was whether a running world should (a) hold ids and
  look up the current CONTENT at every read (small saves, always reflects the
  latest content), or (b) copy the definitions it needs into state at
  construction (self-contained saves, immune to later content edits).
- Design: `makeWorld` deep-copies what a running world needs directly into
  state: enemy stat fields are read from `CONTENT.enemyKinds` and written onto
  each enemy; `items`, `zones`, quest defs and their unlock TEMPLATES are
  `JSON.parse(JSON.stringify(...))`'d in; the boss def is copied so "the sim
  stays self-contained." The header comment states the intent: "definitions are
  copied into state at construction so a running save never shifts under a
  content edit." reduce.js can even spawn quest-unlock entities on accept
  WITHOUT importing CONTENT, because the templates already live in state.
- Got right (the choice made): chose the self-contained snapshot over live
  content references. A save loaded after a content patch behaves EXACTLY as it
  did when created — a mid-run balance tweak, a renamed field, or an added
  enemy cannot retroactively mutate an in-progress game or corrupt a save. This
  pairs with the deterministic-replay guarantee: the world is a closed system,
  so the golden fingerprint and save/load round-trip stay bit-exact.
- Where/why it failed (the tradeoff accepted): the flip side of "a save never
  shifts under a content edit" is that a save can NEVER RECEIVE a content edit.
  A balance fix, a typo correction, or a genuine content bugfix shipped after a
  player started their run will NOT reach that in-progress save — they are
  locked into the content as it existed at world creation. Reference-by-id
  would have let hotfixes reach live saves for free. Saves are also larger
  (they carry copied definitions, not just ids). The team accepted stale
  in-progress content and bigger saves in exchange for save stability and
  determinism.
- Fix (what was chosen instead of a workaround): instead of referencing live
  content (which would make every existing save a hostage to the next content
  edit), the world copies definitions in at construction and pairs this with an
  ADDITIVE-ONLY save-schema discipline (SAGA-ROADMAP.md cross-cutting note: new
  fields get defaults for old saves, never rename/remove) and a `WORLD_VERSION`
  stamp checked on load (save.js reads a foreign/old version as "no save" and
  routes to New Game rather than crashing). Content evolves for NEW games via
  `makeWorld`; existing saves stay frozen and safe.
- Why this fix: a save is a promise that the run you started is the run you
  resume. Snapshotting content into state makes that promise structural — the
  running world is a closed system with no external definition it can drift
  against — which is also exactly what deterministic replay and bit-exact
  save/load require. The cost (no hotfixes to live saves) is acceptable for a
  short single-player game where runs are 60–90 minutes, though it would need
  reconsidering for a long-lived live-service title.
- Rule of thumb: in a data-driven game, decide deliberately whether a save
  SNAPSHOTS content (copy definitions into state at construction) or REFERENCES
  it (store ids, read live content at runtime). Snapshotting buys save
  stability and deterministic replay — a save never shifts under a content edit
  — at the cost that a save can never receive one; reference buys live hotfixes
  at the cost that any content change can retroactively alter or break existing
  runs. Pair snapshotting with additive-only schema versioning and a version
  stamp that fails safe to New Game.
- Provenance (verified/assumed): verified first-hand from src/sim/world.js —
  read the header comment ("definitions are copied into state at construction so
  a running save never shifts under a content edit") and the actual deep-copy
  code (enemy stats copied from enemyKinds, `JSON.parse(JSON.stringify(...))` on
  items/zones/quest defs/unlock templates/boss), plus src/app/save.js
  (WORLD_VERSION gate, corrupt/foreign save reads as "no save"). The
  no-hotfix-to-live-saves cost is the direct consequence of the snapshot design.
- Link: commit 6147d6f "Stage 3: data-driven content"; src/sim/world.js,
  src/sim/content.js, src/app/save.js, docs/SAGA-ROADMAP.md (save versioning)

## E9 — quest gated entities agnostic of history
- Date: 2026-07-07
- Project: Pappydapimp69/The-game-prologue
- Tags: [gamedev][quest][state]
- What: quest objectives only counted progress from events that happened
  while the quest was already `active`. Killing the two husks or grabbing
  the training capsule *before* talking to the quest-giver and accepting
  permanently soft-locked "Clear the Road" at 0/2 — nothing respawned, and
  there was no path back to completion.
- Why built: a standard kill/collect/reach quest system layered over an
  open-world region where the relevant enemies and pickup were already
  present in the world from game start, for exploration/combat purposes
  independent of the quest.
- Design: `questProgress()` iterated `state.quests.active` and incremented
  progress on matching events; nothing tracked what had happened to those
  entities *before* acceptance.
- Got right: quests were already "offered, never pushed" (accepting requires
  an explicit command) — the surrounding design was sound, this was a
  narrower state-tracking gap.
- Where/why it failed: live playtesting (a human, not an automated test)
  killed the husks and grabbed the capsule while exploring before ever
  talking to the NPC, then found the quest permanently stuck.
- Fix: rejected retroactively crediting progress from world state at the
  moment of acceptance (still history-dependent, just delayed, and easy to
  get subtly wrong — e.g. double-counting a kill both retroactively and via
  a future duplicate event). Instead, the objective's target entities don't
  exist in the world AT ALL until the quest is accepted — `ACCEPT_QUEST`
  spawns them from a `quest.unlocks` list declared in content, built once at
  world-construction time and instantiated on accept. There is no "already
  did it" case to special-case because nothing was there to act on yet.
- Why this fix: objectives become provably agnostic of anything that
  happened before acceptance, by construction rather than by careful
  bookkeeping — a stronger and simpler invariant than retroactive credit.
  A non-gated entity (an always-present enemy, in this case) remains
  available for open exploration and as a stable target for mechanic-only
  tests that don't care about quest state.
- Rule of thumb: if a quest objective's completability could depend on
  actions taken before the quest exists to the player, don't try to detect
  and credit those actions after the fact — make the objective's target
  entities not exist until the quest is accepted. This is the mirror image
  of `local__dbh.md#E5` ("map tutorial objects narrowly so EARLY actions
  don't satisfy LATER quests") — same terrain (order-dependent quest state),
  opposite direction (here, early actions couldn't satisfy quest objectives
  *at all* once the quest existed).
- Provenance (verified/assumed): verified first-hand — a human playtester
  hit the exact soft-lock, the fix was implemented and verified by a
  dedicated smoke test (entities absent pre-accept; targeting them throws;
  they appear correctly on accept) plus full-arc browser e2e re-verification
  with no regressions.
- Link: src/sim/content.js (quest.unlocks), src/sim/world.js, src/sim/reduce.js (The-game-prologue)
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-prologue.md#E19 · compatible · no sandbox · session (brain train 3 groups + 2 edges, sandboxed until satisfied, loop 3), sandbox script rng_entangle_sandbox.mjs (live import of real repo source, real BFS pathfinder, verbatim-reproduced AI dispatch loop), latent fragility flagged in this same shipping repo, not fixed (pending explicit confirmation per this session's established pattern)
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-prologue.md#E22 · compatible · no sandbox · session (brain train, sandboxed until satisfied), sandbox script quest_typematch_sandbox.mjs (live import of real repo source, real seeded RNG), live-unfixed structural gap flagged at src/sim/reduce.js questProgress/hitEnemy kind-matching, not applied
- Cited-by: 2026-10-13 · projects/pappydapimp69__brainwork.md#E203 · compatible · sandboxes/2026-10-13__effect-gated-vs-existence-gated-interactables-softlock.py · observed RESULT: FAIL soft-locks existence 0, effect(current quest) 0, touched-flag 1092 of 1092; early hints existence 0, effect 1050; flag mode clean when well1 untouched: False. The kernel's claim held; the last clause of my prediction failed. · scheduled brain train session, 2026-10-13; session_01KgwUVJ8YiFpBjfevwrK7fS

## E8 — prologue entry only cache bust tradeoff
- Date: 2026-07-07
- Project: Pappydapimp69/The-game-prologue
- Tags: [browser][tooling][process]
- What: A player reported a just-shipped press-and-hold charge fix "still not working" on both keyboard and gamepad, even though CI confirmed the deploy succeeded. Re-verification (fresh Playwright repro against the local repo, a new mocked-gamepad sustained-hold e2e, press/release/repress cycles, and a direct tick-by-tick simulation of the 80%+ throttle) found the mechanic was already correct — no code bug.
- Why built: Build-step-free static ES modules on GitHub Pages, same shape as the sibling Dog Park 3D project (projects/pappydapimp69__dog.md#E5): `index.html` loads `<script type="module" src="src/main.js">` with no version token, and `main.js` statically imports ~15 other modules (game.js, input.js, reduce.js, ...) each by plain relative URL.
- Design: Cache-busting was applied ONLY to the entry script (`src/main.js?v=<manual date+counter>`), not propagated into the ~30 relative import specifiers across the module graph.
- Got right: Confirmed via a fresh, independent repro that the underlying press-and-hold logic (keyboard AND mocked-gamepad sustained hold, hold/release/re-hold ramp reset, 80%+ throttle never producing 2+ consecutive zero-gain ticks) was correct all along — didn't waste more effort chasing a phantom logic bug once caching was identified as plausible.
- Where/why it failed: An entry-point-only cache-bust guarantees a fresh fetch of `main.js` itself, but each statically-imported submodule is a SEPARATE cache entry keyed by its own unversioned URL — bumping the entry script's query string does nothing for those. A browser/tab that loaded the game before the fix shipped can still be running stale `game.js`/`input.js` from its own cache (or from an already-open, never-reloaded tab) even after the entry script is refetched.
- Fix: Applied the cheap partial fix explicitly in scope (entry-only `?v=` bump on `index.html`'s script tag, hand-maintained since there's no build step to compute a commit SHA) and documented — rather than silently leaving it implied — that this does NOT fully solve staleness for the nested import graph. Full-graph busting (matching the Dog project's actual fix: a deploy-time `sed` step rewriting every relative import specifier with a per-deploy token) was identified as the complete solution but deferred as out of scope for this fix.
- Why this fix: Matches the task's explicit scope (a cheap defensive mitigation, not a guaranteed full solution) while being honest in the commit message about the residual gap, so a future "still broken after deploy" report isn't re-diagnosed as a logic bug again without first checking whether THIS TIME it's the nested-import gap rather than the entry point.
- Rule of thumb: For build-step-free static ES-module apps, an entry-point-only `?v=` cache-bust is necessary but not sufficient — it does not cache-bust modules reached via nested relative imports, which are independent cache entries. Either bust every import specifier at deploy time (sed/build-token substitution, as in the Dog project) or explicitly document the partial-coverage tradeoff so it isn't mistaken for a complete fix.
- Provenance (verified/assumed): VERIFIED first-hand this session — read index.html and every import statement in src/, confirmed no versioning existed anywhere, confirmed via `grep` that ~30 relative imports across ~15 files would be unaffected by an entry-only query bump.
- Link: session (Investigate charge press-and-hold), commit b6e3c1d on branch claude/install-brain-system-cp5ihy
- Cited-by: 2026-08-03 · projects/pappydapimp69__mirage.md#E4 · compatible · no sandbox · MIRAGE crafting-deception session; `tools/stamp-version.mjs` and the "every module import and asset URL carries the current BUILD token" check in tests/logic.test.mjs.
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-prologue.md#E17 · compatible · no sandbox · session (brain analyze and train new edges), no code change applied in this session — diagnostic finding pending explicit confirmation to port the already-verified fix
- Cited-by: 2026-10-12 · projects/pappydapimp69__sevin.md#E9 · compatible · no sandbox · Sevin commits f31a67f, 6382018; session_0125c7UeqZXhwxqnu8spbVdh

## E7 — press and hold charge percent shaped rate
- Date: 2026-07-07
- Project: Pappydapimp69/The-game-prologue
- Tags: [input][gamedesign]
- What: a "charge aura" meter action was implemented as tap-to-add-a-flat-
  amount, edge-triggered off a single button press. This rewards mashing the
  button as fast as possible over holding it down, which reads wrong for a
  hold-to-charge fantasy and doesn't match how the mechanic is described to
  the player.
- Why built: charge was originally just another one-shot command like
  melee/interact, dispatched once per button-press edge.
- Design (the fix): press-and-hold via an authoritative hold-counter
  (`player.chargeHold`) that resets to 0 on a fresh press (an explicit
  `start: true` flag on the command) and increments on every subsequent tick
  while held; gain-per-tick ramps mildly with consecutive ticks held. The
  rate is ALSO reshaped by the meter's CURRENT fill percent: boosted when
  charging from empty, and hard-throttled — ignoring the ramp bonus entirely
  — once at or above ~80% full, so topping off the last stretch takes real
  hold time no matter how "warmed up" the hold's ramp is.
- Got right: the input layer already had a fixed one-shot action vocabulary
  (button-press edges); extending it to also expose continuous *held* state
  (already computed internally for movement/gamepad polling, just not
  surfaced) was a small, additive change, not a rearchitecture.
- Where/why it failed: player feedback specifically — the old scheme let a
  fast tapper fill the meter as effectively as (or faster than) someone
  holding the button, defeating the intended "commit to holding" feel.
- Fix: `CHARGE` becomes a repeated command dispatched on a fixed real-time
  cadence for as long as the button is held (not once per animation frame,
  to stay frame-rate independent-ish); the sim computes gain from
  `(holdTicks, currentPercent)` using only integer arithmetic (`Math.floor`
  ratios) to keep the authoritative state's determinism invariant intact —
  no floats, no engine-varying math.
- Why this fix: the ramp+percent shaping is entirely inside the
  deterministic reducer (testable with exact expected sequences), while only
  the "is the button still down" signal and the fixed dispatch cadence live
  in the presentation layer — the sim doesn't need to know about wall-clock
  time, only about how many hold-ticks have occurred.
- Rule of thumb: when a meter-fill mechanic is meant to feel like "commit to
  holding," (a) drive it from continuous held state, not edge-triggered taps
  — expose held state from the input layer even if only edge-triggered
  presses existed before; (b) reset any hold-duration ramp explicitly on a
  fresh press so a released-and-repressed hold doesn't inherit stale
  momentum; (c) shape the rate by the meter's CURRENT value, not just hold
  duration, if the design wants "fast from empty, slow near full" — and make
  the near-full throttle override the ramp bonus entirely, or a long enough
  hold defeats the intended slowdown.
- Provenance (verified/assumed): verified first-hand — the exact ramp/
  throttle sequence for a fresh hold from empty to full was hand-derived and
  then confirmed against the implementation via an exact-sequence smoke
  test; a live browser test held a real key for a fixed duration and
  confirmed the meter filled meaningfully more than an equivalent-duration
  series of taps.
- Link: src/sim/reduce.js (CHARGE case), src/app/input.js (chargeHeld), src/app/game.js (hold-cadence dispatch) (The-game-prologue)
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-prologue.md#E21 · compatible · no sandbox · session 01KxkbJUq8YajH8GokSZYYHy; `brain analyze graph` untested seam (sandbox-combined-skilltree-formula + the-game-prologue); sandbox `engine.mjs`, scratchpad `loop6-charge-meter-stale-capacity/` (run twice as separate process invocations, outputs diffed byte-identical)

## E6 — input press vocabulary not fixed list
- Date: 2026-07-07
- Project: Pappydapimp69/The-game-prologue
- Tags: [input][gamedev][ui]
- What: the unified input module's edge-triggered "presses" output was
  computed only for a fixed, hardcoded list of action names; any UI zone with
  a dynamically-chosen id outside that list (a title screen's "New Game" /
  "Controls" / archetype-card buttons) never produced a press event, even
  though it was captured into the same event-time `pending` queue as
  everything else.
- Why built: Stage 5 added a title screen (Continue/New Game/Controls,
  archetype + difficulty picker) reusing the same click/tap-zone hit-testing
  already used for in-game modals.
- Design: modal buttons had always used ids like `confirm`/`cancel`/`alt` —
  which happen to already be members of the fixed action vocabulary — so
  they worked by construction, which masked the limitation until a UI with
  differently-named zones was built.
- Got right: reusing one zone-hit-testing mechanism for both modals and a
  full title screen instead of building a second UI input path.
- Where/why it failed: the first test of the title screen found clicks/taps
  did nothing; traced to `poll()` only promoting names in a fixed `ACTIONS`
  array into the returned `presses` object, silently dropping any other
  captured id.
- Fix: any id captured into the event-time `pending` queue this frame — not
  just ids in the fixed action vocabulary — is now promoted into `presses`
  as a one-shot press. The fixed-list edge-detection (comparing against
  previous-frame state) is kept only for the small set of names that can
  also be continuously HELD (keyboard/gamepad), since those need real
  edge-detection to avoid re-firing every frame; one-shot event-captured ids
  need no such filtering.
- Why this fix: the original design conflated "the small vocabulary of
  continuously-holdable actions" with "the general set of anything a UI zone
  can be tapped or clicked," which only coincidentally lined up for modals.
- Rule of thumb: when a unified input module exposes a one-shot "press"
  concept for UI hit-zones, don't gate it behind the same fixed vocabulary
  used for held/repeatable actions — any dynamically-labeled clickable or
  tappable zone must be able to fire a press under its own id.
- Provenance (verified/assumed): verified first-hand — the title screen was
  fully unresponsive to clicks/taps before the fix and fully responsive
  after, with no other change in the diff.
- Link: src/app/input.js, src/app/title.js (The-game-prologue)
- Cited-by: 2026-07-18 · projects/pappydapimp69__draft.md#E9 · compatible · no sandbox · session 7195397b-63a9-5efe-a80b-2792eaa6645e (`brain train group`, candidate pair dog + the-game-prologue); sandbox `scratchpad/train_group/sandbox.py`, run twice as independent process invocations, outputs diffed identical

## E5 — husk quest tutorial text vs mechanic confusion
- Date: 2026-07-07
- Project: Pappydapimp69/The-game-prologue
- Tags: [gamedev][gamedesign][ux]
- What: A player reported that killing quest-target enemies (husks) with the
  basic melee attack didn't advance a "Defeat 2 husks" kill-count objective,
  but killing them with the aura-blast special attack did — implying the
  quest was silently weapon-gated, with the game having only 2 husks total
  and no respawn, so a melee-only player would look permanently stuck at 0/2.
- Why built: Investigated to find and fix the described weapon-gating bug.
- Design: The kill-tracking code (`hitEnemy` → `questProgress` in
  `src/sim/reduce.js`) passes the DEFEATED ENEMY's kind to the quest
  tracker, never the attack kind — so on a straight code read it already
  looked weapon-agnostic, contradicting the report.
- Got right: A headless ground-truth test (`makeWorld` → `TALK` → `ACCEPT_QUEST`
  → `MELEE` a husk to death → check `quests.active[...].progress`) proved
  melee kills DID advance the objective identically to blast kills, and a
  full melee-only playthrough completed the whole quest. So there was no
  weapon-gating bug in the mechanic at all — code reading gave the same
  conclusion the test confirmed, for once.
- Where/why it failed: The REAL source of the confusion was adjacent tutorial
  text — a separate onboarding checklist (`arc.steps`, gating when the
  end-game boss can spawn) had two teaching-step guide lines shown one at a
  time: "A husk blocks the road. Strike it down up close." (melee step),
  immediately followed once satisfied by "Charge your aura, then blast a
  husk from range." (aura step). The aura line names "a husk" specifically,
  even though that teaching step actually only requires ONE aura hit landed
  on ANY living enemy (a different always-present enemy works fine) — it has
  nothing to do with the quest's kill count. A player who kills a husk with
  melee, then immediately sees "blast a husk from range" surface in the same
  onscreen guide slot the quest tracker lives next to, reasonably reads it as
  "the game is telling me this kill needs to be an aura kill" — a plausible
  misreading with real consequences (the only 2 quest-targets are limited
  and non-respawning), even though the state was correct the whole time.
- Fix: (1) Reworded the aura guide line to "Charge your aura, then loose a
  blast at any foe from range." — removing the enemy-specific noun that
  implied a link to the quest's specific kill targets. (2) The stall-risk
  ask ("husks need to respawn so the quest can never permanently stall")
  went through two design iterations in the same session: a first pass
  added a runtime respawn-timer safety net (kill objective short + all
  unlocked targets of that kind dead -> a fresh copy reappears after a
  tick-gated delay); the human then redirected to a different, better
  design — instead of respawn insurance, the quest's two husks became two
  DISTINCT VARIANTS (`ironhusk`, immune to melee; `wardhusk`, immune to
  aura), each killable by exactly one method, so the quest is unstallable
  BY CONSTRUCTION (the other method always works on the other husk) rather
  than by a timer catching a hypothetical failure after the fact. A new
  generic `immune` field on the enemyKind schema (reusable for future
  enemies/buffs) plus a distinct `no_effect` refusal event (never a silent
  no-op on a wrong-method hit) shipped instead of the respawn timer, which
  was fully removed. Splitting the single "kill 2 husks" objective into two
  specific-kind objectives was a second, independent benefit of the same
  change: the quest tracker now shows two differentiated lines instead of
  one generic counter.
- Why this fix: Text that happens to name the same noun ("husk") as a
  quest's target, shown in a UI region physically next to a HUD element
  tracking that noun's kill count, will be read as if the two are the same
  requirement — even when the two subsystems (a one-time onboarding
  checklist vs. a quest's kill objective) are completely unrelated in code.
  Wording that stays generic ("any foe") when a mechanic doesn't actually
  care about a specific target avoids implying a false requirement.
- Rule of thumb: When two independent systems both react to the same kind of
  game event (here: hitting/killing an enemy of a named kind) and their UI
  surfaces render near each other, audit whether either system's PLAYER-
  FACING TEXT accidentally implies a dependency between them that the CODE
  doesn't have — a player will treat adjacent, similarly-worded on-screen
  text as one instruction, regardless of how separate the underlying state
  machines are. Prove root cause with a ground-truth headless test before
  patching perceived logic bugs — the code and the UX confusion here had two
  entirely different, unrelated locations.
- Provenance (verified/assumed): VERIFIED first-hand — reproduced via a
  headless script confirming melee kills tracked the objective correctly,
  a full melee-only quest completion, and a real-browser Playwright run
  driving the actual game UI showing the same result. Also verified the
  quest could not have practically stalled from the kill objective alone
  under the ORIGINAL shipped content (2 generic husks unlock for `n: 2`, so
  killing both by any method always satisfied it) — that specific finding
  is now superseded by the immune-variant redesign, where "stall-proof by
  construction" is the actual shipped mechanism, verified across 10
  different world seeds (including the title screen's own default boot
  seed) headlessly and once live in a real browser.
- Link: session session_01446PrGwxRiUrr6GMFX2MWK; Pappydapimp69/The-game-prologue
  @ claude/fix-husk-quest-respawn — final shipped state has NO respawn timer;
  see src/sim/content.js (enemyKinds.ironhusk/wardhusk, arc.guide.aura),
  src/sim/reduce.js (the `immune` check in MELEE/AURA_BLAST, `no_effect`
  event), src/sim/world.js (propagating `immune` into constructed state),
  scripts/smoke.mjs.
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-prologue.md#E26 · compatible · no sandbox · session (brain train external research: prologue + onboarding); WebSearch queries as listed in Design; agent-proxy status confirming the WebFetch 403s were an egress-policy block, not a retryable error

## E4 — duplicated text logic drifts fix on first sight
- Date: 2026-07-07
- Project: Pappydapimp69/The-game-prologue
- Tags: [process][gamedev]
- What: the same small piece of presentation logic — turning a quest
  objective's data (`{type, target/item/zone, n}`) into player-facing prose
  — was independently written in two UI surfaces: an in-world HUD quest
  tracker, and a quest-offer dialog. When a third objective type (`reach`)
  was added to the data model, one call site was updated and the other
  wasn't, producing a visible bug ("Find the undefined") in the
  never-updated site. This was the SECOND time the same underlying mistake
  happened — the first duplicate had already drifted once, independently,
  earlier in the project, and was fixed in only that one location without
  anyone noticing the sibling copy existed.
- Why built: each UI surface was written at a different point in the build
  (a HUD tracker in an earlier stage, an offer dialog in a later one), each
  time reimplementing the same small switch/ternary rather than reusing
  existing logic, because the duplication wasn't obvious in the moment —
  the two call sites are visually and structurally unrelated (a corner HUD
  readout vs. a modal dialog).
- Design: no shared function existed; each site had its own inline
  `type === 'kill' ? ... : ...` mapping.
- Got right: nothing structural — this is a pure process/discipline lesson,
  not a design tradeoff.
- Where/why it failed: adding a new objective TYPE is exactly the kind of
  change the project's own content/code seam is supposed to make cheap and
  safe (`SYSTEM/content/objective-types` in ideas) — but that seam only
  covers the REDUCER's handling of the type, not incidental presentation
  logic that also happens to branch on type. The seam has a blind spot at
  its edges: anything else in the codebase that also switches on the same
  discriminant needs to be found and updated too, and there was no single
  place enumerating "everywhere that branches on objective type."
- Fix: extract the duplicated logic into one function
  (`describeObjective(objective)`) used by both call sites, immediately
  upon noticing the duplication — not deferred until it caused a second bug.
- Why this fix: a single source of truth for "how does this data become
  text" makes the next new type addition a one-place edit instead of a
  find-every-caller exercise; the fix is boring but the alternative (finding
  every duplicate by hand, after each new discriminant value) doesn't scale
  and had already failed once.
- Rule of thumb: the moment you notice the same small transformation
  (especially "turn this data into player-facing text") written in two
  places, extract it right then — don't wait for it to drift a second time.
  A code/content seam that makes adding a new TYPE cheap in the reducer
  doesn't automatically protect every OTHER place in the codebase that also
  branches on that type; those call sites need their own single source of
  truth, or they will silently miss new cases one at a time.
- Provenance (verified/assumed): verified first-hand — the second drift was
  caught visually via a screenshot during unrelated (gamepad-label) testing,
  confirmed as a real bug, and fixed by extraction; a smoke test now asserts
  all objective types produce non-"undefined" text and that an unknown type
  fails loud rather than silently stringifying.
- Link: src/app/objective-text.js, src/app/renderer.js, src/app/game.js (The-game-prologue)
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-wrong-sky.md#E14 · compatible · no sandbox · session (brain train on groups and test 5 new edges), no code change — a recorded-lessons synthesis

## E3 — device hint computed at render time
- Date: 2026-07-07
- Project: Pappydapimp69/The-game-prologue
- Tags: [input][ui][gamedev]
- What: modal/dialog buttons showed a baked-in key hint ("Accept (Enter)",
  "Later (Esc)") regardless of which input device was actually active. A
  gamepad player saw "(Enter)"/"(Esc)" prompts even though A/B were the
  buttons that actually worked (the underlying action ids were already
  device-agnostic, so input functionally worked — only the printed text was
  wrong).
- Why built: each modal's button objects were constructed with a fully
  baked label string (`label: 'Accept (Enter)'`) at the moment the modal
  was opened, based on whatever assumption was convenient at that call site.
- Design: the modal-button id vocabulary (`confirm`/`cancel`/`alt`) was
  already device-agnostic by construction (it doubles as the unified input
  layer's action names) — the bug was purely in the STRING shown to the
  player, not in which input actually triggered the button.
- Got right: this project already had the underlying lesson applied at one
  layer — `pappydapimp69/test#E3` established labeling on-screen (touch)
  buttons with words instead of glyphs, and polling the gamepad every frame.
  That lesson covers *which glyphs/words a persistent on-screen button
  shows*; it doesn't cover *dialog/modal hint text that's baked in once at
  creation time*.
- Where/why it failed: found visually — a modal opened while a gamepad was
  the active device still displayed keyboard-specific hint text, an easy
  bug to miss because the buttons still worked (A confirmed, B canceled);
  only the displayed text was stale/wrong, so nothing crashed or looked
  broken in an automated functional test.
- Fix: strip the baked suffix from every button's base label; compute the
  device-specific hint fresh every render frame from the currently active
  device, via a small `keyHint(device, action) -> string` lookup
  (keyboard/gamepad/touch, where touch returns '' since the on-screen button
  IS the input and needs no key hint), and append it at draw time.
- Why this fix: a modal can stay open across a device switch (e.g. the
  player picks up a controller mid-dialog), and even when it doesn't, the
  device that was active *when the modal object was constructed* is not
  guaranteed to be the device active when it's rendered — computing the
  hint at render time removes the staleness class entirely rather than
  chasing each call site that got the assumption wrong.
- Rule of thumb: any UI text that names a physical input control (a key, a
  button glyph) must be derived from the CURRENTLY active device at the
  moment of rendering, never baked in at the moment the UI element was
  constructed — treat "which device is active" as frame-state to read, not
  as a fact to snapshot once.
- Provenance (verified/assumed): verified first-hand — a Playwright test
  that stubs `navigator.getGamepads()` to report a real button press (the
  same signal a physical controller would produce) confirmed the game
  itself detects the device switch and the modal's rendered hint updates to
  "(A)"/"(B)" with a screenshot captured as evidence.
- Link: src/app/device-labels.js, src/app/renderer.js, src/app/title.js (The-game-prologue)
- Cited-by: 2026-07-13 · projects/pappydapimp69__the-game-wrong-sky.md#E14 · compatible · no sandbox · session (brain train on groups and test 5 new edges), no code change — a recorded-lessons synthesis

## E2 — capture input edges at event time
- Date: 2026-07-07
- Project: Pappydapimp69/The-game-prologue
- Tags: [input][gamedev][harness]
- What: input handling sampled logical key/touch state once per animation
  frame; a press-and-release shorter than one frame (a fast tap, or any
  synthetic/automated input) could land and lift entirely between two polls
  and be silently dropped.
- Why built: Stage 2's unified input module (keyboard/touch/gamepad -> one
  command vocabulary), exercised end-to-end with Playwright.
- Design: originally `poll()` read `held`/`touches` state fresh each frame
  and derived press-edges purely from that per-frame snapshot.
- Got right: per-frame sampling is simple and correct for anything held
  across multiple frames (movement, gamepad sticks).
- Where/why it failed: Playwright's `keyboard.press()` fires a keydown+keyup
  pair essentially instantly; the e2e suite went from green to 4/4 failing
  the moment this was exercised, because the resulting quest-accept/attack
  commands never reached the sim's dispatch — the press-and-release
  happened between two polls.
- Fix: capture presses at EVENT time (keydown/touchstart/mousedown) into a
  `pending` queue; the next `poll()` call consumes that queue into the
  frame's `down` state regardless of whether the key/touch is still
  physically down by the time polling happens. Continuously-held state
  (movement) still comes from `held`/`touches`, sampled per frame as before.
- Why this fix: separates "was this pressed at all since the last poll"
  (event-driven, cannot be missed) from "is this currently held"
  (state-driven, fine to sample) — the bug was conflating the two.
- Rule of thumb: any input system polled once per frame must capture
  discrete press events at event time into a queue, not derive them purely
  from per-frame state sampling — a press/release pair faster than one frame
  is invisible to pure sampling, and this affects real fast human input, not
  just automated tests.
- Provenance (verified/assumed): verified first-hand — the e2e suite went
  from 4-failing to all-passing with only this change; nothing else in the
  diff.
- Link: src/app/input.js (The-game-prologue)
- Cited-by: 2026-08-01 · projects/local__sandbox-combined-opticon-prologue-latch.md#E1 · compatible · no sandbox · this session; `brain train combined` (opticon + the-game-prologue candidate pair). Note: opticon#E28's canon body was found EMPTY at composition time (steward-parse truncation at promote time, brain#E20's damage class) and was restored from its original sync-commit proposal (memory commit 69c91b8) before composing.
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E29 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E18 · compatible · no sandbox · August-10 sandboxes/loop09_event_queue_coalescing_reintroduces_the_bug.mjs
- Cited-by: 2026-07-24 · projects/pappydapimp69__dog.md#E60 · compatible · no sandbox · session — Dog Park 3D scent/cutscene build, 2026-07-24

## E1 — canonical hash prng state no transcendentals
- Date: 2026-07-07
- Project: Pappydapimp69/The-game-prologue
- Tags: [gamedev][state][testing][determinism]
- What: Golden replay/fingerprint tests hashed authoritative state via
  `JSON.stringify`, whose key order is insertion-dependent (integer-like keys
  silently reorder first per the JS spec), so two logically-identical states
  could hash differently. Separately, following the `{seed,count}` seeded-RNG
  kernel literally meant restoring a save had to replay `count` rolls (O(n)
  on every load). And nothing guarded against transcendental `Math` calls
  (`sin`/`cos`/`pow`/…) inside the "deterministic" sim, even though those are
  engine-implementation-defined and can diverge across runtimes/browsers.
- Why built: Stage 0 of a from-scratch deterministic game harness
  (sim-before-render), implementing Brain's existing
  `[SYSTEM/testing/replay-fingerprint]` and
  `[SYSTEM/determinism/seeded-rng]` kernels for real.
- Design: (1) a canonical serializer that recursively sorts object keys and
  throws loud on NaN/Infinity/undefined/-0 before hashing (FNV-1a) for the
  golden test; (2) an sfc32 PRNG whose full 4-word integer state is saved
  directly inside the world state, no replay needed to restore; (3) a smoke-
  suite guard that greps `src/sim/*.js` for banned `Math.*` transcendental
  calls and fails the build if found — IEEE-exact ops (sqrt/floor/ceil/round/
  min/max/imul) stay allowed.
- Got right: the existing kernels (golden fingerprint test, seeded-RNG
  discipline) were correct in principle — this only sharpens the concrete
  implementation of each.
- Where/why it failed: a first pass hashed with plain `JSON.stringify` and
  failed a same-object-different-insertion-order unit test immediately; a
  naive `{seed,count}` port also required O(count) work on every load,
  caught by a save/load-mid-run test.
- Fix: implement `stableStringify` (sorted keys, reject non-finite/undefined,
  normalize -0); switch RNG persistence to raw integer state words instead of
  a replay count; add a grep-based transcendental-Math guard to the smoke
  suite so the invariant is mechanical, not a code-review convention.
- Why this fix: keeps the hash a pure function of logical state rather than
  incidental key-insertion order; makes save/load O(1) instead of O(n); and
  makes "no engine-varying math in the authoritative sim" something a build
  fails on, not something a reviewer has to remember to check.
- Rule of thumb: when hashing game state for a golden/regression test, always
  canonicalize (sorted keys, reject non-finite values) before hashing; save a
  PRNG's raw state words, never a replay count; and mechanically guard
  (grep/lint) against transcendental Math in any code claimed deterministic —
  don't rely on review to catch it.
- Provenance (verified/assumed): verified first-hand — the full smoke suite
  (37/37 by the final stage) plus a live Node/Chromium fingerprint-parity
  check (identical hash across engines) on this project's Stage 0 harness.
- Link: src/sim/canonical.js, src/sim/rng.js, scripts/smoke.mjs (The-game-prologue)
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E19 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-09-28 · projects/local__sandbox-kernel-system-determinism.md#E1 · compatible · sandboxes/2026-09-28__train-gap-b01.py · session 2026-09-28, brain train gap batch 1 loop 3
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E13 · compatible · no sandbox · August-10 sandboxes/loop08_canonicalizing_a_save_breaks_every_golden.mjs
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E16 · compatible · no sandbox · August-10 sandboxes/loop02_fingerprint_blind_to_capture_bug.py
- Cited-by: 2026-07-26 · projects/pappydapimp69__brain-builder.md#E8 · compatible · no sandbox · brain-builder @ claude/brain-install-link-mode-5ykmu8, src/sim/save.mjs
- Cited-by: 2026-08-03 · projects/pappydapimp69__mirage.md#E23 · compatible · no sandbox · MIRAGE save/load; session
- Cited-by: 2026-10-08 · projects/pappydapimp69__brainwork.md#E21 · compatible · sandboxes/2026-10-08__seeded-rng-state-save-and-symbolic-keys.py · observed RESULT: PASS raw-state save exact (replay costs 5000 draws); shared stream flips 20/20; named streams 0/20; ordinal-seeded streams flip 19/20; symbolic keys 0/30 · brain train auto pass 1
- Cited-by: 2026-10-09 · projects/pappydapimp69__brainwork.md#E41 · compatible · sandboxes/2026-10-09__hmac-score-signing-needs-full-payload-and-constant-time-compare.py · observed RESULT: PASS early-exit compare leaked the full tag in 7949 queries, constant-time stopped it (5/5), and keyed-but-score-only, unkeyed and delimiter-free signing each still accepted forgeries · scheduled brain train run, gap pass 5; session_01MiqdeTN5cV7j1vm5wkPKVF
- Cited-by: 2026-10-09 · projects/pappydapimp69__brainwork.md#E44 · compatible · sandboxes/2026-10-09__seeded-rng-state-words-vs-seed-count-and-stream-coupling.py · observed RESULT: PASS state-word restore cost 0 rolls vs 100000 for seed+count, both bit-exact; one extra cosmetic roll changed 97% of later gameplay rolls on a shared stream and 0 on split streams; unmasked words diverged at roll 1 · scheduled brain train run, loop 2 kernel pass 1; session_01MiqdeTN5cV7j1vm5wkPKVF
- Cited-by: 2026-10-10 · projects/pappydapimp69__brainwork.md#E55 · compatible · sandboxes/2026-10-10__seeded-rng-save-replay-and-shared-stream-vs-per-entity-substream.py · observed RESULT: PASS S1 determinism, S2 resume equal (replay 5000 vs 1 steps), S3 leak diverges at tick 10, S4 shared stream keeps 0.11 of later rolls vs id-keyed substream 1.00 vs ordinal-keyed 0.18 · brain train auto session 2026-10-10; session_012uwXvPE6LveBmBN1pFKYfK
- Cited-by: 2026-10-11 · projects/local__seeded-rng-state-save-canonical-fingerprint-transcendental-roll-divergence.md#E1 · compatible · sandboxes/2026-10-11__seeded-rng-state-save-canonical-fingerprint-transcendental-roll-divergence.py · observed RESULT: PASS S1 resume exact (replay=12000 draws); S2 canon equal vs insertion dump differs; S3 clean runs equal and leak runs differ; S4 float-fed fingerprint diverged on 1/20 seeds; S5 integer control 0/20 · scheduled brain train loop 2 pass 1; session_015bpfiyHog3CaYStqh5GY3K
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E48 · compatible · sandboxes/2026-10-11__save-rng-state-words-survives-a-miscounted-draw.py · observed RESULT: PASS 4/4; true 6000 counted 3000; words cost 0 match; counted diverges; true-count cost 6000; sorted hash stable · session; brain train auto run 2 pass 1 (kernel, declare); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__brain.md#E141 · compatible · sandboxes/2026-10-11__seeded-rng-state-save-vs-count-replay-and-roll-order-desync.py · observed RESULT: PASS replay_cost=1000 order_desync=True shared_shift=True split_isolated=True canon_fp=True · scheduled brain train session; session_019JKZ53wDZk2PJ4F5v2qxmH
- Cited-by: 2026-10-11 · projects/pappydapimp69__brainwork.md#E111 · compatible · sandboxes/2026-10-11__seeded-rng-state-words-vs-count-canonical-hash.py · observed RESULT: PASS state-words restore 0 rolls vs count replay 5000 rolls, both exact; raw hash 6 variants vs canonical 1; unmasked signed reload diverges · session scheduled brain train run, loop 1 pass 1; session_01QZ7D84k4ubQDti8yxsPp3D
- Cited-by: 2026-10-12 · projects/pappydapimp69__brainwork.md#E127 · compatible · sandboxes/2026-10-12__seeded-rng-state-words-restore-cost-and-hidden-cache-breaks-exact-resume.py · observed RESULT: PASS state words O(1) restore exact; hidden spare cache lost words-only (exact=False), fixed with spare; shared stream 14/20 vs split 0/20. Seed plus gaussian-call-count replay was exact (prediction missed). · scheduled brain train session; loop 1 pass 1; session_01USy9B9LHrVVHAXMpNhpqtQ
- Cited-by: 2026-10-12 · projects/pappydapimp69__brainwork.md#E139 · compatible · sandboxes/2026-10-12__seeded-rng-state-words-vs-seed-count-and-shared-stream-desync.py · observed RESULT: PASS state-word restore 0 draws vs replay 500, fingerprint catches leak, shared stream desyncs on 1 cosmetic roll (split streams fix), sorted-key hash needed · scheduled brain train session; session_01F6s6QCyGv375z4gR2Gg7J5
- Cited-by: 2026-10-12 · projects/pappydapimp69__brainwork.md#E143 · compatible · sandboxes/2026-10-12__sfc32-state-save-vs-seed-count-replay-and-substreams.py · observed RESULT: PASS 12/11 checks held; replay cost 50000 vs 0; shared-stream flips 8/8; name-keyed stable=True index-keyed stable=False · brain train auto loop 2 pass 1 (kernel mode, declaring a prose-quoted link); session_01Eniw4iPSAzagvHMs1UyMoA
- Cited-by: 2026-10-12 · projects/pappydapimp69__brainwork.md#E153 · compatible · sandboxes/2026-10-12__seeded-rng-state-words-vs-count-replay-and-fingerprint.py · observed RESULT: PASS restore words=4 ints/0 rolls vs count=200000 rolls, next5 equal, lockstep 10000, seeded roundtrip True vs ambient False, raw-key-order hash equal=False canonical=True · brain train auto loop 2 pass 1; session_01SbLcvYSnUb7XWzv1N6FVpb
- Cited-by: 2026-10-12 · projects/local__sandbox-seeded-rng-state-words.md#E1 · compatible · sandboxes/2026-10-12__seeded-rng-state-words-vs-count-and-stream-splitting.py · observed RESULT: PASS state words reload exact 8/8 (replay cost 49999 rolls vs 4 words), count replay diverged 8/8, control exact 8/8, shared stream perturbed 8/8 with shift 8/8, split streams 0/8, in-stream insertion 8/8. · scheduled brain train session, loop 2 pass 1; session_018RFPy3DMrymTRHnMWEoTT9
- Audited: 2026-10-13 · pass · The entry has no stored sandbox, so I checked its claims against the real engine. In Node 22, JSON.stringify gave different strings for the same logical object built in two key orders ({"2":2,"b":1,"a":3} vs {"2":2,"a":3,"b":1}), turned -0 into 0 and NaN into null silently, which supports the canonical-serializer rule and the throw-on-non-finite design. The O(1) save of raw PRNG state words follows directly from the design and was exercised by the entry's own save/load test. Limits of the audit: the rationale that transcendental Math calls diverge across runtimes was not reproduced (the entry's parity run was Node and Chromium, both V8, so it could not show divergence), and the entry's smoke-suite results are the author's own and not shipped. The Rule of thumb's always-canonicalize and save-state-not-count parts are covered; the cross-runtime divergence is a plausible stated reason, not a demonstrated one. · brain train auto audit session 2026-10-13 (loop 2); session_01SVMqRFxH6Uuecz64bYuF9E
- Reverified: 2026-10-13 · pass · sandboxes/2026-10-13__golden-hash-canonicalize-raw-rng-state-transcendental-lint-js-key-order-model.py · observed RESULT: PASS stringify hash splits on both int-key and string-key insertion order; NaN and Infinity collide; replay costs count steps vs 1; lint catches 3/4, misses destructured alias, false-flags a comment · I rebuilt the claim blind in Python with my own fixtures: a JS-order stringify model (integer-like keys first ascending, other keys in insertion order), a 32-bit LCG for the RNG, and a regex lint. Hash of two equal states built in different insertion order split under the stringify model for both integer-like and plain string keys, and was equal under a sorted-key canonical form; NaN and Infinity both stringified to null and collided while the canonical form rejected them; replay restore cost count steps (10, 1000, 100000) against one step for a raw state restore; a Math-call regex flagged 3 of 4 bad snippets, missed a destructured alias, and flagged a comment. The claim holds in my model; the lint finding is a limit of the grep half of the rule of thumb (it needs an AST-level check or alias ban). My model of JS key order is hand-written, not run in a JS engine, and my prediction was wrong on one point (I expected plain string-key order to be stable; the claim's insertion-dependent wording is the right one). I did not open the entry's own sandbox. · scheduled brain train session; session_01JbvSxNM4UdUZG4c4NXMNMD
- Cited-by: 2026-10-13 · projects/pappydapimp69__brainwork.md#E207 · compatible · sandboxes/2026-10-13__seeded-rng-state-words-vs-replay-count-and-shared-stream.py · observed RESULT: PASS state-word load 0 draws vs 250000 for seed+count; hashes plain 24 vs canonical 1; shared stream gave 3 fingerprints over particle counts, split stream 1 · scheduled brain train session, 2026-10-13; session_01KgwUVJ8YiFpBjfevwrK7fS
- Cited-by: 2026-10-13 · projects/local__2026-10-13__seeded-rng-state-restore-vs-count-replay-and-hidden-state-fingerprint-order.md#E1 · compatible · sandboxes/2026-10-13__seeded-rng-state-restore-vs-count-replay-and-hidden-state-fingerprint-order.py · observed RESULT: PASS state restore 1 step vs replay n steps with equal draws (n=1000,20000,200000); naive hash differs True canonical True; spare-gaussian state-only restore matches only at even draw counts {1: False, 2: True, 3: False, 4: True}. · brain train auto session 2026-10-13 loop 2; session_01WtWcTgcKWwuvhJ9RsCQX9c
- Cited-by: 2026-10-14 · projects/pappydapimp69__brainwork.md#E229 · compatible · sandboxes/2026-10-14__seeded-rng-state-words-vs-replay-count-and-stream-sharing.py · observed RESULT: PASS restore mismatches 0 with 4 words vs 50000 replay calls; extra shared roll diverges at tick 1000 with 0 of 3999 later ticks equal; private generator keeps streams equal; canonical hash stable · brain train auto loop 2 pass 1; session_01AMmNLeLopueLdsbKx7q1Lv
- Cited-by: 2026-10-14 · projects/pappydapimp69__brainwork.md#E248 · compatible · sandboxes/2026-10-14__seeded-rng-state-words-save-exact-and-o1-but-draw-order-and-dropped-ticks-desync.py · observed RESULT: PASS state-words save exact (1 step vs 50000 replay); clamp ticks 5 vs 10, stalled client holds a prefix only; swapped draw order reassigns values to systems. · scheduled brain train auto loop 2 pass 1; session_01EU6f7a12wCvzUSXEbn87pv
- Cited-by: 2026-10-14 · projects/pappydapimp69__brainwork.md#E259 · compatible · sandboxes/2026-10-14__seeded-rng-full-state-save-vs-seed-count-and-where-single-stream-stops-holding.py · observed RESULT: PASS full-state True cost 4 vs 10000; leak distinct 3/3; frame-seed manipulable 6/6; order divergence 28/30 · session_017SJAeaijx8mHKPVUZV6hJB brain train auto loop 1 pass 1
- Cited-by: 2026-10-15 · projects/pappydapimp69__zanegpt.md#E9 · compatible · sandboxes/2026-10-15__seeded-rng-raw-state-save-round-trips-and-float-order-breaks-lockstep.py · observed RESULT: PASS raw-state load O(1) matches 100/100 rolls vs 5000-call replay; lockstep equal; ambient diverges at step 0; float order flips a hit (False/True) while discrete zone holds; sorted-key hash needed (raw False, sorted True). · brain train auto pass 1 (kernel); session_01Hecxxt7Wfrejc8A3YVX1ht
- Cited-by: 2026-10-15 · projects/local__transcendental-drift-forks-only-when-it-feeds-state.md#E1 · compatible · sandboxes/2026-10-15__transcendental-drift-forks-a-run-only-when-it-feeds-state.py · observed RESULT: PASS 8/8; plain json splits equal states, canonical one hash; NaN never equals itself; sin impls differ on 100.0% of args, branch-only sim traces agree, feedback sim differs at step 1 and is > 0.1 apart by step 75; grep guard catch… · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto loop 3 pass 1 (kernel declare SYSTEM/seeded-rng), 2026-10-15
- Cited-by: 2026-10-16 · projects/pappydapimp69__brainwork.md#E364 · compatible · sandboxes/2026-10-16__seeded-rng-state-words-vs-seed-count-and-canonical-hash.py · observed RESULT: PASS words restore O(1) calls=0 vs replay 5000; unmasked signed words diverge (145 diverged of 175 states with a negative word); canonical hash order-independent · scheduled brain train auto loop 1 pass 1; session_01BUPKhqp6uFZkacj8e9KczX
- Cited-by: 2026-10-17 · projects/local__name-keyed-substreams-survive-reorder-index-keyed-do-not.md#E1 · compatible · sandboxes/2026-10-17__name-keyed-substreams-survive-reorder-index-keyed-do-not.py · observed RESULT: PASS named changed (0, 0, 0) indexed changed (5, 4, 2); shared streams by hash bits {32: 0, 8: 0, 4: 0, 2: 3, 1: 4} · scheduled brain train auto loop 2 pass 1 (kernel); session_011LtaNZCrPYhhAtwJpZ1y8i
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E450 · compatible · sandboxes/2026-10-18__lockstep-needs-split-streams-and-canonical-hash.py · observed RESULT: PASS lockstep desync at tick 1 with shared cosmetic draws vs none with split streams; insertion-order hash differs for equal state, sorted equal; words restore exact; gaussian spare lost on words-only. The tick-0 part was refuted (… · scheduled brain train auto loop 2 pass 1; session_01NZDPzU2KzUnFJgGMC4knps
- Cited-by: 2026-10-20 · projects/pappydapimp69__brainwork.md#E541 · compatible · sandboxes/2026-10-20__one-seeded-stream-saves-and-replays-exactly-but-an-inserted-roll-shifts-every-later-system.py · observed RESULT: PASS state-word load 0 rolls vs 500 replayed, same next 100; shared stream 98% of later combat rolls shifted by one inserted roll, split streams 0 · session_013HyGtdP3RxMckhL1WhP9yK
- Cited-by: 2026-10-20 · projects/pappydapimp69__brainwork.md#E554 · compatible · sandboxes/2026-10-20__seeded-rng-full-state-save-vs-seed-count.py · observed RESULT: PASS full-state restore 0 rolls vs seed+count 100000 at N=100000, both exact; raw-order hash equal=False, canonical equal=True; one extra roll desyncs=True · scheduled brain train run, 2026-10-20; session_01AxvhKMfKUmYVr8Ree8rqE7
