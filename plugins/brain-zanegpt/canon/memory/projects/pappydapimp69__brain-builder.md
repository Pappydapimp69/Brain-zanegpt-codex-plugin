# pappydapimp69/brain-builder — lessons

Project: pappydapimp69/brain-builder. Newest first.

---

## E11 — difficulty must scale off the player
- Date: 2026-07-26
- Project: pappydapimp69/brain-builder
- Tags: [gamedev][balance][gamedesign][simulation]
- What: Scaling enemy difficulty off an ACCUMULATING meter rather than off the player
  diverges uncontrollably. Raid strength was derived from a "heat" (attention) meter that
  rises every day: at heat 60 a raider fielded ~91 axis total against a day-10 player's
  ~24. Every loud policy therefore lost every duel, and because losing cost condition and
  condition gates training, loud play ended up WEAKER than hiding — the stance meant to be
  the aggressive option was strictly dominated on its own headline benefit. Re-deriving the
  raider from the player's own axes with the meter as a MULTIPLIER (0.62 to 1.12) fixed it
  in one change: raid-farming became viable, while attention still decided how dangerous
  each raid was.
- Why built: A 30-day campaign where drawing attention onto yourself is meant to be a real
  strategy — you flare, something comes for you, and surviving it is your best growth event.
- Design: Deterministic campaign sim; raids resolved as real duels through the shared
  combat engine; 300-seed policy tournament over fixed suppression policies.
- Got right: Making the meter a multiplier on a player-derived baseline rather than
  removing it. The meter still does its job — a loud player faces harder versions of the
  same fight — but it can no longer outrun the player's growth curve.
- Where/why it failed: An accumulating meter and a player's power grow on unrelated curves.
  Heat rises roughly linearly with days spent loud; player axes rise with training days
  and are gated by condition. Nothing ties them, so any difficulty derived from the meter
  alone will eventually be either trivial or impossible, and which one depends on play
  style rather than design. The failure also presented misleadingly: the visible symptom
  was "the aggressive stance is underpowered", which invites tuning the stance.
- Fix: Derive the encounter from the player's own stats, and apply the accumulating meter
  as a bounded multiplier on top. Same fiction (something read your power and decided it
  could take you), self-correcting balance.
- Why this fix: A difficulty curve has to be anchored to the quantity it is meant to
  challenge. Anchoring it to a side-effect of play style makes the anchor drift.
- Rule of thumb: Scale an encounter off the PLAYER, with any accumulating meter (heat,
  notoriety, threat) as a bounded MULTIPLIER — never off the meter alone. A meter and the
  player's power grow on unrelated curves, so meter-only difficulty is eventually trivial
  or impossible depending on play style, and it presents as "this stance is underpowered".
- Provenance (verified/assumed): Verified first-hand — measured in
  sandbox/suppression-policies.mjs. Before: loud policies 0.00 win rate with
  lower end-of-run power than the hiding policy. After: best 0.70, three
  policies competitive, burst patterns among them at 20,330 BP against
  turtling's 951.
- Composed: sandbox-dbz-team-combat/E4, sandbox-power-scaling/E2
- Link: brain-builder @ claude/brain-install-link-mode-5ykmu8, src/sim/campaign.mjs
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-brain-builder-e11-is-a-domain-instance-of-e2.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX

## E10 — synthetic event dispatched on wrong target silently no ops
- Date: 2026-07-30
- Project: pappydapimp69/brain-builder
- Tags: [gamedev][input][browser][javascript]
- What: Bridged gamepad button presses onto existing keyboard handling by
  dispatching a synthetic `KeyboardEvent('keydown', {key})` on `document`. Every
  actual listener for that event (`addEventListener('keydown', ...)` in two
  separate modules) was registered on `window`, not `document`. A `KeyboardEvent`
  defaults `bubbles: false`, so the event never propagated from its dispatch
  target up to the window-level listeners — and `dispatchEvent` does not throw,
  return an error, or warn when zero listeners catch an event. The result: every
  gamepad-driven action (face buttons for day actions, D-pad for stance, mute,
  restart) was a complete, silent no-op for an entire shipped commit. Only the
  skip-hold control kept working, because it was wired as a direct mutation of a
  shared `Set` rather than through an event at all.
- Why built: Adding gamepad input by bridging onto the game's existing keyboard
  event listeners, to reuse their guards (busy state, screen checks, disabled
  buttons) instead of duplicating them for a second input surface.
- Design: `window.addEventListener('keydown', fn)` in both `main.mjs` and
  `campaign-ui.mjs`; a per-frame gamepad poll intended to dispatch a synthetic
  key event per newly-pressed button/stick-crossing.
- Got right: The BRIDGE STRATEGY itself (reuse the existing listener instead of
  a parallel gamepad-specific action resolver) was sound and is not what failed —
  only the dispatch TARGET was wrong. The fix was a one-line change
  (`document.dispatchEvent` → `window.dispatchEvent`) once found.
- Where/why it failed: `document` and `window` are both plausible-looking
  dispatch targets for a "global" synthetic keyboard event, and code that
  dispatches on the wrong one produces no error of any kind — the browser
  considers "an event with no listeners" a completely normal, silent outcome.
  Compounding this, the bug was originally shipped and REPORTED as working from
  code review/reasoning alone, with no actual browser execution to check it —
  which is exactly backwards for a class of bug (event target + bubbling
  mismatch) that is invisible to static reading and only detectable by actually
  firing the event and checking for an effect.
- Fix: Dispatch on `window` directly, matching where every real listener is
  registered. More generally: when bridging a synthetic DOM event onto existing
  listeners, dispatch on the SAME node the target listeners are registered on
  (or set `bubbles: true` and dispatch on a genuine descendant of it) — treating
  `window`/`document`/`documentElement` as interchangeable "global" targets for
  event dispatch is the mistake.
- Why this fix: The listeners' registration target is the one ground truth for
  where a dispatched event must land; matching it exactly needs no reasoning
  about bubbling behavior at all, which is one less thing that can be wrong.
- Rule of thumb: A synthetic event that silently does nothing is indistinguishable,
  by inspection alone, from a synthetic event that works — `dispatchEvent`
  returns normally either way. Before trusting a synthetic-event bridge (any
  device-to-existing-listener input bridge, not just gamepad), fire it against a
  live page and assert an observable effect, exactly once, before shipping. Code
  review of the dispatch call site cannot catch a target/bubbling mismatch;
  running it can.
- Provenance: Verified first-hand. A throwaway Playwright script loaded the real
  page, called the test-surface hooks to reach the campaign screen, then compared
  `document.dispatchEvent(new KeyboardEvent('keydown', {key:'1'}))` (the shipped,
  buggy code) against `window.dispatchEvent(...)` (the fix) and read the
  campaign's `day` state before/after each: the document-dispatch left it
  unchanged (bug confirmed), the window-dispatch advanced it (fix confirmed).
  Also independently verified ArrowRight cycling stance (Open -> Flared) and 'm'
  toggling the mute button's own label, both via `window.dispatchEvent`.
- Composed: N/A
- Link: brain-builder @ claude/brain-install-link-mode-5ykmu8, src/main.mjs
  (pollGamepad), src/present/campaign-ui.mjs

## E9 — side flag not cosmetic tag in a generalized encounter
- Date: 2026-07-30
- Project: pappydapimp69/brain-builder
- Tags: [gamedev][simulation][refactor][combat]
- What: Generalizing a 1-boss-vs-party fight engine to support a multi-fighter escort
  group, a per-fighter `isBoss` flag that USED to be purely descriptive ("this one is
  the boss") became, silently, the mechanism deciding which SIDE an actor's turn
  attacks — `if (actor.isBoss) attack the party pool; else attack the defenders' own
  pool`. Building escort fighters via the same `makeFighter(id, axes, {kind, aoeShare,
  aoeScale, targetRule})` call used for the boss, but without `isBoss:true`, produced
  escorts that fell into the "attack your own side" branch and never touched the party
  at all — friendly fire on the boss, or on each other, instead. Every trace-existence
  and outcome test stayed green throughout, because the fight still ran to completion,
  produced a non-empty trace, and terminated normally — bossWon still resolved
  correctly by pure coincidence in some setups. Only a test that checked WHICH id an
  attack actually landed on (party vs. defenders) caught it.
- Why built: Adding escort roles (brute/skirmisher/channeler/warden) to an arrival
  fight, so a raid/arrival can field more than one enemy at once, per a filed
  enemy-role-not-headcount kernel already in this project's ideas repo.
- Design: `runEncounter(rng, party, boss, opts)` normalizes `boss` to a `defenders`
  array (`Array.isArray(boss) ? boss : [boss]`) so a single boss stays a 1-element
  array; each acting fighter's per-tick branch is keyed on `actor.isBoss` to decide
  its target pool. This was an existing, load-bearing design from before escorts
  existed — the bug was in NOT re-reading that branch's precondition when building a
  second kind of monster-side fighter.
- Got right: The fix is one line per escort (`isBoss: true` alongside `kind`,
  `aoeShare`, `aoeScale`, `targetRule`), and the field's job is now stated explicitly
  in a comment at both the flag's declaration in `makeFighter` and at every
  construction site, specifically so the next monster-side fighter builder does not
  repeat this.
- Where/why it failed: The flag's ORIGINAL purpose (mark the one specially-scripted
  AoE-capable fighter) and its ACCIDENTAL new purpose (route targeting by side) were
  never unified into one documented contract when the encounter shape generalized from
  exactly-one-defender to N defenders. A field whose name says one thing
  (`isBoss` — "this is the boss") but whose read site enforces another
  ("this decides your team") is exactly the kind of drift a rename or a second field
  would have prevented, but the cheaper real fix was just documenting the actual
  contract at every read AND write site.
- Fix: Set `isBoss: true` on every monster-side fighter, not only the headline boss,
  at every construction site (`arrivalRoster`'s escorts in `campaign.mjs`, and every
  test/sandbox fighter built for a multi-defender fight). Documented the flag's real
  meaning ("the side flag runEncounter's targeting branch keys on, not a cosmetic
  tag") inline at the `makeFighter` declaration and at the escort construction site.
- Why this fix: Cheaper and lower-risk than renaming the field or splitting it into
  `isBoss` (cosmetic) + `side` (mechanical) this late — the flag already had exactly
  the right VALUE needed (true for every monster-side fighter), it was only being
  under-applied. A rename remains a good follow-up if a THIRD meaning ever gets loaded
  onto the same field.
- Rule of thumb: When a fight/turn engine's per-actor branch is keyed on a flag that
  reads as descriptive ("is this the boss") but the branch body actually encodes
  something structural ("which side do you attack"), audit EVERY construction site
  that builds a fighter for that side when you add a new one — a trace-exists /
  outcome-resolves test suite will not catch "the new fighter type fights the wrong
  side" if the fight still runs to a normal-looking completion regardless. Test WHO
  hit WHOM, not just that a fight happened and ended.
- Provenance: Verified first-hand. Caught by a unit test asserting the real
  first-attacker id in a hand-inspected trace, then confirmed by printing
  `derive()`-level stats for the exact repro (kaen vs. boss+warden) and watching the
  warden deal zero damage to the party across a full encounter before the fix, and
  correct (~27 dmg/hit) damage after. Full test suite (159 tests after this fix) and
  two balance sandboxes re-run clean post-fix.
- Composed: N/A
- Link: brain-builder @ claude/brain-install-link-mode-5ykmu8, src/sim/campaign.mjs
  (arrivalRoster), src/sim/encounter.mjs (makeFighter/runEncounter), test/enemies.test.mjs,
  test/battle.test.mjs, sandbox/enemy-roster.mjs
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-august-10-brain-builder-conjunct-rates-cannot-see-a-routing-defect.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-09-28 · projects/local__sandbox-combined-august-10-predicted-vs-observed-blind-to-misroute.md#E1 · compatible · no sandbox · brain train scheduled pass, 2026-09-28

## E8 — canonical serialization at the boundary
- Date: 2026-07-26
- Project: pappydapimp69/brain-builder
- Tags: [state][save][determinism][testing]
- What: A save round trip that continues the RNG stream perfectly can still be
  NON-CANONICAL — the same generator state written two different ways. The sfc32 PRNG ends
  its step with `| 0`, so its state words are SIGNED between calls; the restore path read
  them back with `>>> 0`, unsigned. Both paths normalize before use, so the restored stream
  was byte-identical and a stream-continuation test passed cleanly. But `serialize(load(
  serialize(x)))` did not equal `serialize(x)`, which silently breaks anything built on
  comparing saves: byte equality, save diffing, deterministic state hashing, golden-file
  fingerprints, and "has this changed since last write" checks.
- Why built: Adding save/resume to a 30-day campaign, then writing a browser-side check
  that the loaded campaign matched the live one field by field.
- Design: `serializeCampaign` / `deserializeCampaign` over plain JSON, with the PRNG's raw
  state words persisted so a restore is O(1) rather than a replay from seed.
- Got right: Persisting the raw state words at all — that is what makes an O(1) restore
  possible — and testing stream CONTINUATION rather than merely that the restored state was
  structurally valid.
- Where/why it failed: The mismatch is invisible to every behavioural test, because
  behaviour is identical. It only appears the moment something compares two serializations,
  which in my case was a diagnostic that reported a bare `same: false` with no field named
  — so the first two attempts to fix it went to the wrong layer. The signed/unsigned split
  is also easy to miss because both representations print as plausible integers.
- Fix: Normalize at the serialization BOUNDARY (`>>> 0` on write), and assert canonical
  form directly: `JSON.stringify(serialize(deserialize(serialize(c))))` must equal
  `JSON.stringify(serialize(c))`. Separately, make any comparison diagnostic report WHICH
  field differed rather than a single boolean.
- Why this fix: Canonicalizing on write means there is exactly one byte representation of a
  given state, which is the property every comparison downstream actually depends on.
  Normalizing only on read leaves the writer free to emit variants.
- Rule of thumb: "The restored stream is identical" does not imply "the serialization is
  canonical". Normalize representation at the write boundary and assert
  `serialize(deserialize(serialize(x))) === serialize(x)` as its own test — a stream or
  behaviour test cannot see the difference, and anything that hashes, diffs or byte-compares
  saves depends on it. Watch for signed/unsigned specifically: JS bitwise ops end signed
  (`| 0`) while restores commonly read unsigned (`>>> 0`).
- Provenance (verified/assumed): Verified first-hand. The stream-continuation test passed
  while the canonical-form test failed; both now exist in test/save.test.mjs, and the
  round trip was additionally exercised in a real browser through localStorage.
- Composed: the-game-prologue/E1
- Link: brain-builder @ claude/brain-install-link-mode-5ykmu8, src/sim/save.mjs
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-brain-builder-wrong-sky-version-bump-blind-spot.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E13 · compatible · no sandbox · August-10 sandboxes/loop08_canonicalizing_a_save_breaks_every_golden.mjs

## E7 — replay a resolved trace for animated combat
- Date: 2026-07-26
- Project: pappydapimp69/brain-builder
- Tags: [gamedev][architecture][rendering][determinism][testing]
- What: To animate combat, resolve the fight FIRST in the deterministic sim, have it emit
  a TRACE of every action (`{tick, from, to, dmg, crit, aoe}`), and make the visual layer
  a pure replay of that trace. Three properties fall out for free and are otherwise
  expensive to get: (1) the animation cannot disagree with the outcome, because display HP
  is derived by replaying the same trace the sim produced; (2) skip is trivially correct —
  apply every remaining entry and stop — so watch/skip parity is a two-line function
  rather than a second code path; (3) the balance model the sandbox measured is literally
  the model the player watches, so there is no visual-only combat implementation to drift
  out of agreement with the verified one.
- Why built: The game's climax was a strength comparison between abstract sums
  (self + disciples + fortification) with no fight to watch. Replacing it with a real
  encounter required either animating the sim or writing a second combat system for show.
- Design: `sim/encounter.mjs` runs an ATB fight and optionally records a trace.
  `present/battle.mjs` groups the trace into visual beats, paces them, and fires shake /
  hit-flash / particles / floating numbers / hitstop / sound per beat. Attack STYLE (melee
  dash vs beam) is chosen in presentation from a deterministic hash of actor and tick,
  because it changes nothing about the outcome and therefore must not consume sim RNG.
- Got right: Deriving display HP from the trace rather than tracking it separately. It
  makes "the animation agrees with the sim" true by construction, and the test for it
  (recompute expected HP from the trace, compare) is three lines.
- Where/why it failed: Two specific mismatches between trace shape and visual shape had
  to be fixed. An AoE arrives as one entry PER TARGET on the same tick from the same
  attacker; treating each as its own beat fired several near-simultaneous screen flashes
  that refreshed faster than the flash could decay, pinning it high and washing the entire
  frame to grey. And hitstop pauses the playback timeline, so applying it to all ~150
  beats of a long fight added roughly 30 seconds of accumulated freeze and pushed the
  climax past a minute.
- Fix: Group same-tick same-attacker AoE entries into ONE beat carrying several hits, and
  apply hitstop only to hits that carry weight (medium and above, or a crit). Both are
  presentation-side transforms of the trace; the sim did not change.
- Why this fix: The trace is a record of what happened MECHANICALLY, which is not the same
  granularity as what happened VISUALLY. One sweeping attack is one visual event and
  several mechanical ones. The mapping between the two belongs in presentation.
- Rule of thumb: For animated combat, resolve the fight deterministically and emit a
  trace, then make the visuals a pure replay of it — you get outcome-agreement, provable
  skip parity, and one balance model instead of two. But convert trace granularity to
  VISUAL granularity explicitly: group simultaneous same-source hits into one beat, and
  never apply a timeline-pausing effect (hitstop) per mechanical event.
- Provenance (verified/assumed): Verified first-hand. Skip/watch HP parity, trace-derived
  HP equality, and outcome agreement are asserted in test/battle.test.mjs; the grey-out
  and the minute-long fight were both observed in browser screenshots before the fix.
- Composed: sandbox-dbz-team-combat/E1, the-game-the-recursion/E8
- Link: brain-builder @ claude/brain-install-link-mode-5ykmu8, src/present/battle.mjs
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-brain-builder-dog-trace-replay-parity-vs-order-dependence.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E26 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-10-08 · projects/local__sandbox-one-state-vector-pheromone-view-outcome.md#E1 · compatible · sandboxes/2026-10-08__one-state-vector-pheromone-view-outcome.py · observed RESULT: PASS shared tau agrees (0 mismatches) but only with one shared predicate (S3 4 ticks) and no eased presentation value (S5 1); authored parallel view drifts on 3. The first run failed only because my steady-state tolerance was 1e-9… · scheduled brain train session 2026-10-08

## E6 — feedback channel that always fires says nothing
- Date: 2026-07-26
- Project: pappydapimp69/brain-builder
- Tags: [gamedev][rendering][ui][gamedesign]
- What: A feedback channel that fires on EVERY event stops carrying information and
  starts destroying it. Three instances in one session, same shape: a full-screen white
  flash fired on every hit refreshed faster than it decayed (170ms decay against beats
  every ~115ms), so it sat permanently high and washed the whole frame to flat grey —
  the channel meant to say "that one landed" was on continuously, and it also hid
  everything else. Ambient ki particles emitted at suppression scale >= 0.9 fired on the
  neutral stance too, filling the frame with haze that buried the disciples standing
  beside the player. And floating stat-gain markers, one per axis, stacked four wide
  labels on the same spot because a training day moves all four axes — illegible.
- Why built: Adding layered impact feedback (the filed convention is that no single
  channel sells an impact and three or four together do), and visible feedback for
  campaign actions to replace an event log.
- Design: Canvas presentation layer; shake, body flash, screen flash, particles, floating
  numbers and synthesized sound as independent channels triggered per event by weight tier.
- Got right: Keeping the channels INDEPENDENT rather than bundling them into one "hit
  effect". That is what made the fix surgical — the screen flash could be restricted to
  heavy/ultimate/crit hits while light hits kept shake, body flash and particles, so light
  hits still read as hits.
- Where/why it failed: Each failure looked like a rendering or colour bug rather than a
  frequency bug. The grey-out in particular reads as "my background is wrong" or "my
  compositing is wrong"; the actual cause was upstream, in how often something fired.
- Fix: Gate the loudest channels on the events that EARN them, and cap them. Screen flash
  only on heavy/ultimate/crit and clamped; ambient emission only at the genuinely loud
  stance (scale > 1.5, not > 0.9); one HEADLINE marker per event (the largest delta,
  above a threshold) rather than one per changed field, stacked vertically if several are
  in flight. Then assert the bound: a test plays a whole fight and fails if peak flash
  exceeds a threshold.
- Why this fix: Salience is relative. A channel's value comes from the contrast between
  firing and not firing, so the fix is always frequency and headroom rather than intensity.
- Rule of thumb: A feedback channel that always fires says nothing — and a full-screen one
  actively hides the frame. Reserve the loudest channels for the events that earn them,
  clamp their peak, and TEST the bound by playing a whole sequence and asserting the peak
  never exceeds it. For a multi-field change, float ONE headline marker, not one per field.
- Provenance (verified/assumed): Verified first-hand. All three were visible in browser
  screenshots and invisible to a fully green test suite; the flash bound is now asserted
  in test/battle.test.mjs and the single-marker rule in test/diorama.test.mjs.
- Composed: N/A
- Link: brain-builder @ claude/brain-install-link-mode-5ykmu8,
  src/present/battle.mjs, src/present/diorama.mjs
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E28 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E5 — single target boss step function
- Date: 2026-07-26
- Project: pappydapimp69/brain-builder
- Tags: [gamedev][balance][gamedesign][simulation]
- What: With a single-target-only boss, an N-versus-1 fight is a STEP FUNCTION in
  N, not a difficulty curve. Measured boss win rate by party size: 1.00 (1v1),
  1.00 (2v1), 0.00 (3v1), 0.00 (4v1) — monotonic, so a monotonicity assertion
  passed, but no party size produced a close fight. The same cliff appeared along
  the boss-strength axis: sweeping how strong a boss must be for a fair 3v1 gave
  0.14 -> 0.56 -> 0.99 across two increments, so exactly one authored value was
  ever fair. Cause: party damage output scales linearly with N while a
  single-target boss's output is fixed, so either the party out-races the boss or
  it does not, and there is no attrition middle ground for variance to act in.
  Giving the boss AoE on 35% of its actions (at 0.6x damage each) made its output
  scale with N too, and the response became smooth: 1.00, 1.00, 0.79, 0.16, 0.01.
- Why built: Party size is a progression axis in this game (you recruit and train
  disciples), so it has to work as a difficulty dial rather than an on/off switch.
- Design: Deterministic ATB encounter engine, seeded PRNG, 200 seeds per cell.
  Swept party size 1..5 against a fixed boss, and separately swept boss stat scale
  at fixed party size, measuring win rate and mean fight length.
- Got right: Asserting MONOTONICITY (more attackers must never do worse) rather
  than forcing each encounter shape to even odds. Re-tuning a mitigation constant
  per party size so every shape reads 50/50 would have made party size stop
  mattering BY CONSTRUCTION — the constant silently compensates for the extra
  fighter — which deletes the reward for the whole recruitment axis. The filed
  precedent (sandbox-dbz-team-combat#E4) says the constant does not transfer
  across encounter shapes; it does not say to force even odds in each, and doing
  that is a design error even though it makes every number look good.
- Where/why it failed: A monotonicity check alone is too weak to catch this — a
  step function is perfectly monotonic. The failure was invisible until the sweep
  printed the whole series rather than a pass/fail, and until boss strength was
  swept at single-point granularity instead of in steps of 2.
- Fix: Give the boss damage that scales with the number of targets (AoE on a
  fraction of its actions). Then assert smoothness explicitly, not just
  monotonicity: check that no single increment of the difficulty parameter swings
  the win rate by more than a set number of points, and print the full series so a
  cliff is visible.
- Why this fix: For party size to be a dial, both sides' output must scale with
  it; otherwise the ratio of the two is a threshold test. AoE is the cheapest way
  to make boss output N-dependent, and it is also what real games in the genre do.
- Rule of thumb: A single-target boss makes N-versus-1 difficulty a step function
  in N — the boss needs output that scales with party size (AoE) before party size
  can be a difficulty dial. And a monotonicity assertion is too weak to catch a
  cliff, since a step function is monotonic: assert SMOOTHNESS (bounded change per
  increment) and print the whole series.
- Provenance (verified/assumed): Verified first-hand. All win rates are measured
  output of sandbox/balance-sweep.mjs steps 2 and 3 in this repo, before and after
  adding BOSS_AOE_SHARE.
- Composed: sandbox-dbz-team-combat/E1, sandbox-dbz-team-combat/E4,
  sandbox-power-scaling/E2
- Link: brain-builder @ claude/brain-install-link-mode-5ykmu8,
  src/sim/encounter.mjs BOSS_AOE_SHARE
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-brain-builder-waiting-city-smoothness-blind-to-zero-variance.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-mirage-brain-builder-sweep-the-axis-the-failure-varies-on.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-opticon-brain-builder-party-size-correctness-is-a-step-function.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E27 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-10-15 · projects/pappydapimp69__demo-disc.md#E33 · compatible · sandboxes/2026-10-15__a-boss-acting-twice-is-a-constant-factor-not-party-scaling.py · observed RESULT: PASS slope N=2->4 single +0.75, acts-twice +0.70, AoE +0.40; leftover HP N=2->4: single 0.10->0.85, acts-twice 0.00->0.70, AoE 0.00->0.40, game mix 0.00->0.55. The AoE-flat prediction was refuted. · session_0169rjPqYDYawkbeTUEzoNKo (brain train on the Stonewake boss changes, demo-disc commit 91ce487)

## E4 — clamp that binds erases variance
- Date: 2026-07-26
- Project: pappydapimp69/brain-builder
- Tags: [gamedev][balance][testing][gamedesign]
- What: A %-of-max-HP damage cap is the only damage rule that survives an extreme
  attacker:defender ratio sweep (sandbox-power-scaling#E2). But a cap tuned to bind
  during ORDINARY same-tier play erases every stat difference and all crit variance
  at once, because a clamped hit is a constant: mean fight length collapsed onto
  the exact values 7.0, 13.0 and 19.0 rounds with zero spread across 40 seeds, and
  the response to the balance constant degenerated from a curve into a step
  function. Measuring the fraction of hits the cap clamped (~100%) is what
  diagnosed it; win rates alone looked merely "wrong", not "structurally inert".
  Re-tuning the attack/HP coefficients so ordinary hits land well below the ceiling
  dropped cap binding to 0-9% in even matchups while still clamping 100% of hits at
  a 6.2x damage ratio — where the cap is supposed to act.
- Why built: Adopting the cap from a filed lesson into a game with a different stat
  scale. The cap's guarantee is a MINIMUM hits-to-kill; what the lesson does not
  say is what the cap costs when it is active more often than intended.
- Design: Deterministic sweep, seeded PRNG, with cap-binding telemetry counting
  what fraction of resolved hits had their pre-cap value exceed the ceiling.
  Verified the cap still bounds fight length at extreme mismatch afterwards:
  damage grew 6.2x while mean fight length shrank only 1.5x.
- Got right: Keeping the cap UNIFORM — no stat pierces it. An earlier revision let
  the technique axis scale the ceiling, which turns the guarantee from "minimum 5
  hits" into "minimum 5/pierce hits" and gives away the exact ratio-independence
  the cap was adopted for. An anti-tank stat belongs in the pre-cap mitigation
  term, not in the ceiling.
- Where/why it failed: Fight lengths landing on suspiciously round constants
  (7.0/13.0/19.0) is the tell, and it is easy to read as a coincidence rather than
  as evidence that nothing stochastic is reaching the outcome. Without the binding
  counter I spent a revision tuning the wrong constant.
- Fix: Tune the damage and HP coefficients so a mitigated same-tier hit sits well
  below the ceiling, keeping the cap as a BACKSTOP for extreme ratios rather than
  an always-on clamp. Instrument the binding rate permanently and treat a high
  rate in even matchups as a failure in its own right.
- Why this fix: The cap's value is entirely in the tail — it exists to stop
  one-shots at absurd ratios. In the body of the distribution it only destroys
  information, since every clamped hit is the same number regardless of who threw
  it. Keeping it in the tail preserves both properties.
- Rule of thumb: A clamp is only free where it does not bind. A %-max-HP damage
  cap that binds during ordinary play erases all stat and crit variance and
  collapses fight length to an exact constant — tune coefficients so the cap is a
  backstop for extreme ratios, keep it UNIFORM (a pierceable cap surrenders the
  guarantee it exists for), and instrument the binding RATE, because a round
  constant in an outcome metric is the symptom you will otherwise misread.
- Provenance (verified/assumed): Verified first-hand. All figures are measured
  output of sandbox/balance-sweep.mjs in this repo across revisions 2-4.
- Composed: sandbox-power-scaling/E2, sandbox-dbz-merged/E1,
  sandbox-combined-loop-combat/E1
- Link: brain-builder @ claude/brain-install-link-mode-5ykmu8,
  src/sim/combat.mjs resolveHit + sandbox/balance-sweep.mjs cap telemetry

- Cited-by: 2026-08-29 · projects/local__sandbox-combined-mirage-brain-builder-negative-control-needs-binding-rate.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-opticon-brain-builder-constant-rng-fakes-the-binding-rate.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-09-28 · projects/local__sandbox-kernel-rpg-combat.md#E1 · compatible · sandboxes/2026-09-28__train-gap-b04.py · session 2026-09-28, brain train gap batch 4 loop 20
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E19 · compatible · no sandbox · August-10 sandboxes/loop06_seed_variance_without_outcome_variance.md
- Audited: 2026-10-14 · modeled · Read the entry; it has no stored sandbox in sandboxes/, so the model itself could not be inspected and I judged the claim from its text alone. The core mechanism is sound arithmetic: when every hit is clamped to a constant fraction of max HP, fight length is a fixed ceiling of HP over the cap, so exact round constants with zero spread follow, and the cap-binding counter it describes is a computed telemetry value, not an assumed answer. However the numbers (7.0/13.0/19.0 rounds, 0-9% binding, 6.2x ratio) come from the author's own hand-written combat model of one game, and the Rule of thumb states a general claim about any percent-max-HP cap in ordinary play, which depends on that game's coefficient scale. Tested system is a bespoke model, scope narrower than the rule, no script to rerun, so modeled rather than pass. · scheduled brain train auto loop 1 pass 3; session_01BwMXpnGN7oKqipFnskBS6R
- Cited-by: 2026-09-30 · projects/pappydapimp69__brainwork.md#E385 · compatible · sandboxes/2026-09-30__resource-cost-binding-rate-flat-vs-scaled.py · observed RESULT: PASS flat [0.4, 0.0, 0.0, 0.0] scaled [0.4, 0.4, 0.4, 0.4] · scheduled training session pass 2

## E3 — canvas inset does not stretch
- Date: 2026-07-26
- Project: pappydapimp69/brain-builder
- Tags: [browser][rendering][canvas][ui][testing]
- What: A full-screen canvas styled `position: fixed; inset: 0; display: block` stayed
  at its INTRINSIC 300x150 size. `inset: 0` does not stretch a REPLACED element
  (canvas, img, video, iframe): with `width: auto`, CSS resolves a replaced element's
  used width from its intrinsic size and treats the over-constrained left/right pair
  as ignorable, so the element sits at 300x150 in the top-left corner. The game
  meanwhile measured `clientWidth`/`clientHeight` (300/150), sized its backing store
  to match, and drew as though that were the viewport — so everything rendered tiny
  and top-left-anchored, with the camera's `translate(w/2, h/2)` centring on (150, 75).
  No exception, no console warning, no failed assertion of any kind.
- Why built: Bringing up the render spine for a canvas game and capturing screenshots
  of the intro cinematic for review.
- Design: Playwright + headless Chromium at a 1280x720 viewport, screenshotting the
  page at a series of authored timestamps.
- Got right: Taking screenshots AT ALL, and looking at them. The page booted cleanly,
  the clock advanced, every marker fired in order, watch/skip parity held, and 61 unit
  tests passed — the entire automated suite was green while the game was drawing into
  a 300x150 box. This is the concrete demonstration of the "automated verification
  covers wiring, not looks" ceiling: no state-based assertion has any reason to inspect
  the canvas's used CSS size.
- Where/why it failed: `inset: 0` reads as "stretch to fill" because that is exactly
  what it does for non-replaced elements, so the CSS looks obviously correct. The
  failure then presents as a rendering/camera/scale bug — my first hypotheses were all
  in the transform stack — because the visible symptom is a mis-scaled scene, and the
  actual cause is two layers away in CSS layout.
- Fix: Size the canvas explicitly — `width: 100%; height: 100%` (or explicit vw/vh) —
  never relying on `inset`/`top+bottom+left+right` alone. Diagnose by measuring
  `getBoundingClientRect()` and `clientWidth/Height` in the page rather than reasoning
  about the transform, since those two numbers separate "CSS never sized it" from "my
  camera maths is wrong" in one step.
- Why this fix: An explicit width/height overrides intrinsic sizing for replaced
  elements, which is the only thing that makes the used size follow the viewport.
- Rule of thumb: `position: fixed; inset: 0` does NOT stretch a canvas/img/video — a
  replaced element with `width: auto` keeps its INTRINSIC size (300x150 for canvas) and
  silently ignores the over-constrained insets. Set width/height explicitly. And when a
  canvas scene renders small or corner-anchored, measure the element's used size FIRST;
  a full green suite proves nothing about it, because no state assertion reads CSS
  layout.
- Provenance (verified/assumed): Verified first-hand. Measured in headless Chromium at
  a 1280x720 viewport: `clientWidth/Height` and `getBoundingClientRect()` both reported
  300x150 while `window.innerWidth/Height` reported 1280x720, with
  `getComputedStyle().position === 'fixed'` and `inset === '0px'`. Setting
  `width:100%; height:100%` changed the measurement to 1280x720 with no other edit.
- Composed: N/A
- Link: brain-builder @ claude/brain-install-link-mode-5ykmu8, index.html #stage
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E7 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E2 — bounded lever cannot balance unbounded
- Date: 2026-07-26
- Project: pappydapimp69/brain-builder
- Tags: [gamedev][balance][gamedesign][architecture]
- What: Designing four stat axes so each owns a distinct lever, I gave the
  "technique" axis mitigation PENETRATION (it divided the defender's mitigation)
  while "power" scaled raw damage. No coefficient made technique competitive. A
  round robin over all 35 equal-stat-total builds measured technique at r = -0.70
  correlation with win rate — investing in it made you strictly worse — with every
  strongest build sitting at minimum technique and every weakest technique-stacked.
  The cause is structural, not numeric: penetration acts on a damage FRACTION,
  which is bounded above by 1.0, so its total achievable value tops out near 1.9x;
  power multiplies raw damage with no ceiling. Replacing penetration with flat
  mitigation-bypassing "true damage" — an unbounded term — moved technique to
  r = -0.35 and made it win its intended niche 0.39 vs power's 0.01.
- Why built: A DBZ-style RPG needs power to be a vector rather than a scalar
  (ideas: multi-axis-progression / escalation-legibility names DBZ as the
  cautionary case for a single collapsed power number). That requires each axis to
  be genuinely worth investing in.
- Design: Deterministic round-robin tournament: enumerate every build on a coarse
  grid summing to a fixed stat total, play all pairings at 24 seeds each, then
  compute the Pearson correlation of each axis value against that build's win
  rate. |r| near 1 means the axis alone decides outcomes; near 0 means it trades
  off against the others.
- Got right: The correlation test itself. Hand-picking two builds and tuning them
  to parity — which is what I did first — proves almost nothing, because it tunes
  those two builds. The round robin diagnosed WHICH axis was broken and in which
  direction, immediately, and a negative correlation is a far clearer signal than
  a losing matchup.
- Where/why it failed: Three coefficient revisions in a row failed to fix
  technique, because I was tuning magnitude when the problem was shape. A second,
  compounding cause hid in the same place: the mitigation term was
  `reach = K + attackerAttack`, which quietly handed the anti-armour role to the
  power axis as well — raising power both increased raw damage AND thinned the
  defender's mitigation, so power did its own job plus technique's. Against a
  defense-heavy foe, +24 power won 0.42 while +24 technique won 0.00: the
  designated anti-tank stat was worse at anti-tank than the damage stat.
- Fix: Give the underdog axis an UNBOUNDED lever (flat damage that bypasses
  mitigation entirely), and make sure no other axis touches that lever — `reach`
  became a flat global constant so power scales only `raw`. Separately, remove any
  side-effect that lets one axis do two jobs: power had also been granting HP,
  which kept it ahead of technique even in technique's own niche (technique dealt
  more expected damage per hit, 63.6 vs 47.0, and still lost 0.71 vs 0.82, purely
  on the +128 hp that 32 points of power handed it).
- Why this fix: Bounded and unbounded quantities have different asymptotics, so no
  scalar coefficient can equalise them across the stat range — you can match them
  at one point and they diverge everywhere else. And an axis with a side-effect on
  a second lever is competing in two categories at once; the only fix is to
  delete the side-effect, not to compensate for it.
- Rule of thumb: A BOUNDED stat lever (anything acting on a fraction, rate, or
  percentage that saturates at 1.0) cannot be balanced against an UNBOUNDED one
  (a raw multiplier) by tuning coefficients — the shape has to change. Test axis
  balance with a round robin over equal-total builds and a per-axis correlation,
  not with hand-picked matchups; a negative correlation names the trap stat
  outright.
- Provenance (verified/assumed): Verified first-hand. All correlations and win
  rates are measured output of sandbox/balance-sweep.mjs in this repo.
- Composed: sandbox-dbz-team-combat/E2, sandbox-dbz-merged/E1,
  sandbox-power-scaling/E2
- Link: brain-builder @ claude/brain-install-link-mode-5ykmu8,
  sandbox/balance-sweep.mjs step 1 + src/sim/stats.mjs
- Cited-by: 2026-08-29 · projects/local__sandbox-combined-brain-builder-e11-is-a-domain-instance-of-e2.md#E1 · compatible · no sandbox · session_014mRpopK9xnhvk35tT8ozkX

## E1 — balance constant scale transfer
- Date: 2026-07-26
- Project: pappydapimp69/brain-builder
- Tags: [gamedev][balance][testing][process]
- What: Adopting a balance constant from a filed lesson, I swept the exact range
  that lesson quoted ("K=3 to K=6", so 1..12) and every encounter shape reported
  an EMPTY usable band — no value of K produced a fair fight at 3v1 or 4v1. The
  constant was not wrong; the RANGE was, because that project's defense stat
  lived on a different scale than this one's (its mitigation values were ~10-30,
  ours reach 360 because the defense axis caps at 120 and is scaled 3x). The
  entire usable regime for K sat outside the swept window, at 55-90. Two further
  transfer failures compounded in the same run: the sweep used 40 seeds, whose
  0.079 standard error cannot resolve a 50/50 claim (the symmetric control duly
  read a meaningless 0.63, which at 1000 seeds resolved to 0.49); and the
  inherited CAP_FRACTION of 0.2 was measured against that project's attack/HP
  coefficients, so against ours the cap bound on ~100% of hits.
- Why built: Building a DBZ-style RPG damage model. Retrieval surfaced
  sandbox-dbz-team-combat#E3/#E4, which establish that a pre-cap mitigation
  constant fixes a %-max-HP damage cap in team fights and that the constant does
  not transfer across encounter shapes. I took the quoted numeric range as the
  search space rather than as one project's answer.
- Design: Deterministic sweep (seeded sfc32, no wall clock, no Math.random) over
  a 4-axis stat model. Swept K across a range, 200 seeds per cell, measuring win
  rate, mean fight length, and the fraction of hits clamped by the cap. The
  cap-binding telemetry is what diagnosed it.
- Got right: Running a symmetric mirror-match control BEFORE trusting any sweep
  number, per sandbox-dbz-team-combat#E5. It was the control that exposed the
  sample-size problem, and the cap-binding counter that exposed the coefficient
  problem — neither would have been visible from win rates alone.
- Where/why it failed: Three separate silent failures, all reading as "the
  design is broken" rather than "the harness is mis-scaled". (1) EMPTY bands at
  every shape, because the usable K regime was ~5x outside the swept window.
  (2) A mirror match reading 0.63 with no bias present. (3) Fight length landing
  on EXACT constants with zero spread — mean rounds of precisely 7.0, 13.0, 19.0
  — because a cap binding on ~100% of hits erases crit and every stat difference,
  turning the K response from a curve into a step function.
- Fix: Sweep the range implied by YOUR OWN scale, not the range quoted in the
  source lesson: compute where the constant's regime must lie from your stat
  magnitudes, then sweep several times wider. Size samples from the resolution
  the claim needs (a 50/50 claim needs ~1000 seeds, not 40). And instrument the
  mechanism, not just the outcome — a cap-binding rate is what distinguishes "my
  constant is wrong" from "my constant is irrelevant because a clamp upstream is
  eating every difference".
- Why this fix: A balance constant is a ratio between two scales that both live
  in the source project. Porting the number without porting the scales carries
  over neither the value nor the range. Instrumenting the clamp turns three
  indistinguishable "it's broken" symptoms into three separately diagnosable ones.
- Rule of thumb: A balance constant transfers across neither encounter shape nor
  STAT SCALE nor sample size — treat a quoted numeric range as one project's
  answer, never as your search space, and instrument the clamp so you can tell a
  wrong constant from an irrelevant one.
- Provenance (verified/assumed): Verified first-hand. All numbers above are
  measured output of sandbox/balance-sweep.mjs in this repo across four
  revisions; the revision log in that file records each failure.
- Composed: sandbox-dbz-team-combat/E3, sandbox-dbz-team-combat/E4,
  sandbox-dbz-team-combat/E5, sandbox-power-scaling/E2
- Link: brain-builder @ claude/brain-install-link-mode-5ykmu8,
  sandbox/balance-sweep.mjs revision log rev2
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E3 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
