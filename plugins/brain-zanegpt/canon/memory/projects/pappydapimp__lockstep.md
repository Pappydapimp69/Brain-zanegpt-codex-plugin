# PappyDaPimp/lockstep — lessons

Project: Lockstep — a two-player couch co-op arena in Phaser (TypeScript/Vite);
players only win together (carry/defend, revive, tether). Newest first.

---

## E10 — Harness blocks pushing to external remotes regardless of auth
- Tags: [process][harness][git]
- Date: 2026-06-15
- What: Pushing the finished Lockstep repo to its GitHub remote from the agent session.
- Why built: Ship the work to `github.com/PappyDaPimp/lockstep`.
- Design: Run `git push` to the external GitHub remote from inside the agent's execution environment.
- Got right: Local commits, branch, and remote config were all correct.
- Where/why it failed: The harness hard-blocks pushing to any GitHub remote outside the original
  execution environment — regardless of permission rules or the user's explicit authorization. The
  push is refused at the environment layer, not by git or GitHub, so no credential/config fix helps.
- Fix: Don't fight it — generate a `.bat` (or shell script) containing the push commands and hand it
  to the user to run on their own machine; they drive the last mile.
- Why this fix: The block is environment policy, not a fixable auth problem; routing the push through
  the user's local machine is the only reliable path.
- Rule of thumb: If a push to an external remote is refused no matter the auth, it's the
  harness/environment blocking it — hand the user a script to push locally instead of retrying.
- Provenance: firsthand from the Lockstep session (relayed via its build-letter); observed behavior,
  not assumed.
- Link: session 2026-06-15; `letters/lockstep-build-letter.md`.
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E50 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E9 — A help-multiplier became a penalty at the hard end
- Tags: [gamedesign]
- Date: 2026-06-15
- What: Objective-count difficulty model `count = floor(base · f^k)`.
- Why built: Scale per-level workload by difficulty without making combined-objective levels overwhelming.
- Design: `f` = difficulty factor (easy 0.8 / normal 1.0 / hard 1.2); `k` = combo exponent (1 for a
  single objective, 2 when combined), capped at 2.
- Got right: Applying the factor twice for combos keeps total workload bounded as objective types stack.
- Where/why it failed: A naive symmetric `f^k` makes Hard combos explode (×1.44) — penalizing exactly
  the players who opt into harder multi-objective levels, an unintended difficulty cliff.
- Fix: Make the combo exponent one-way — `k` only applies when `f < 1` (Easy thins combos); at
  Normal/Hard the combo multiplier collapses to `f^1`.
- Why this fix: The combo adjustment was intended as mercy on Easy, not a surcharge on Hard; gating it
  on `f < 1` preserves the intent and removes the cliff.
- Rule of thumb: A multiplier meant to help should be clamped so it can't silently become a penalty at
  the other end of the range.
- Link: session 2026-06-15 (design discussion); `arc/src/systems/LevelGenerator.ts`,
  `arc/src/config/objectives.ts`; commit e335061.

## E8 — Phaser overlap callback args aren't positionally ordered
- Tags: [phaser][physics]
- Date: 2026-06-15
- What: Arcade-physics overlap callbacks for projectile↔enemy↔operative collisions.
- Why built: Apply damage/effects on contact.
- Design: Registered overlaps and read the callback args positionally (`bolt` = first arg, target = second).
- Got right: Group-vs-group cases happened to line up.
- Where/why it failed: `overlap(group, sprite)` does NOT guarantee (object1, object2) order — for
  operative overlaps the args came back swapped, so `bolt` was actually the Operative and
  `bolt.deactivate()` threw; the exception aborted `world.step` and the rest of `update()` every frame,
  freezing camera/AI/everything with no surfaced console error.
- Fix: A type-based resolver `pick(a, b, Ctor)` (`core/overlap.ts`) used in every overlap callback;
  never index by position.
- Why this fix: Resolving participants by `instanceof` is order-independent and immune to Phaser's
  internal arg ordering.
- Rule of thumb: Never trust positional args in a physics overlap callback — resolve each participant by type.
- Link: session 2026-06-15; `arc/src/core/overlap.ts`, `arc/src/systems/CombatSystem.ts`; commit e335061.

## E7 — Vite HMR stacked Phaser.Game instances without a dispose hook
- Tags: [phaser][vite][tooling]
- Date: 2026-06-15
- What: Vite hot-module-reload during development.
- Why built: Fast iteration.
- Design: `main.ts` constructs `new Phaser.Game(config)` at import time.
- Got right: Cold loads were fine.
- Where/why it failed: Every hot update re-ran `main.ts` and created another `Phaser.Game` without
  disposing the old one — stacked canvases/loops, and debug `window.game` pointed at a different
  instance than the visible one, yielding impossible-looking state during verification.
- Fix: `if (import.meta.hot) import.meta.hot.dispose(() => game.destroy(true))`.
- Why this fix: An engine that owns a canvas + RAF loop must be torn down on hot-dispose, or instances
  accumulate.
- Rule of thumb: With HMR, anything that grabs a global resource (canvas, loop, socket) needs an
  explicit dispose hook.
- Link: session 2026-06-15; `arc/src/main.ts`; commit e335061.

## E6 — Backgrounded tab froze the loop; huge deltas caused tunneling
- Tags: [phaser][physics][process]
- Date: 2026-06-15
- What: Phaser game-loop timing under backgrounded/occluded tabs.
- Why built: Reliable runtime verification plus robust play on focus loss.
- Design: Default RAF-driven loop + Arcade physics.
- Got right: Fine while the tab was focused.
- Where/why it failed: Backgrounded, RAF paused (`loop.time` froze, nothing updated); switching to
  setTimeout then produced huge per-frame deltas, so fast projectiles tunneled through bodies and
  overlaps silently missed.
- Fix: `fps: { forceSetTimeOut: true, min: 30 }` + `disableVisibilityChange: true` in gameConfig — loop
  keeps ticking when occluded, and delta is clamped (~33ms) so a hitch slows the sim instead of tunneling.
- Why this fix: Clamping max delta is the general cure for tunneling under frame hitches; the
  timeout/visibility flags just keep the loop alive for headless testing and alt-tab play.
- Rule of thumb: Cap your max frame delta — without it, any stall turns into missed collisions.
- Link: session 2026-06-15; `arc/src/config/gameConfig.ts`; commit e335061.
- Cited-by: 2026-09-29 · projects/local__sandbox-lockstep-delta-cap-trades-tunneling-for-sim-lag.md#E1 · compatible · no sandbox · session_01AJo9NVvaQuzD3JbJDk6P3B
- Cited-by: 2026-09-29 · projects/local__sandbox-lockstep-frame-delta-clamp-tick-parity.md#E1 · compatible · no sandbox · session (scheduled brain train pass 4)

## E5 — One-shot pickup re-fired during its despawn fade
- Tags: [phaser][physics]
- Date: 2026-06-15
- What: COLLECT-objective shard pickup on overlap.
- Why built: Count collected shards toward the objective.
- Design: `overlap(shardGroup, operative)` → increment, play a 140ms fade tween, then destroy.
- Got right: Overlap detection was correct.
- Where/why it failed: `collect()` started the fade but left the shard active with its body enabled, so
  the overlap kept firing every frame during the fade — 8 shards counted as ~10.
- Fix: On collect, immediately `setActive(false)` + disable the body (guarded against re-entry), then
  run the fade tween.
- Why this fix: The "collected" flag must flip on the same frame as the trigger; visual teardown can
  lag, collision state cannot.
- Rule of thumb: Deactivate a one-shot pickup the instant it's taken — never let a despawn animation
  gate further hits.
- Link: session 2026-06-15; `arc/src/entities/Shard.ts`; commit e335061.
- Cited-by: 2026-07-24 · projects/pappydapimp69__dog.md#E62 · compatible · no sandbox · session 01JSDkbjs8Z8kxdVQFZ8HAMu, commit 2f57452 (game.js startRecognition/finale)

## E4 — One input edge consumed by two systems
- Tags: [input][coop]
- Date: 2026-06-15
- What: The "interact" button shared by revive, escort drop/pass, and shop purchase.
- Why built: One contextual action button.
- Design: Each system independently edge-detected the same `interact` intent.
- Got right: Each behavior worked in isolation.
- Where/why it failed: Standing in a shop zone while carrying a payload and pressing interact fired both
  the escort drop and a shop buy in the same frame — two systems consuming one input edge.
- Fix: Shop ignores the press while `isCarrying`; then buy was fully decoupled onto its own action
  (X gamepad / F keyboard) with a device-aware prompt.
- Why this fix: Overloading one button across contexts needs explicit priority or separation; a
  dedicated buy action removes the ambiguity entirely.
- Rule of thumb: If two systems read the same input edge, one will fire when you don't want it — gate by
  context or give it its own button.
- Link: session 2026-06-15; `arc/src/systems/ShopSystem.ts`, `arc/src/systems/InputSystem.ts`; commit e335061.
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E25 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E3 — A tracked stat had a reader but no writer
- Tags: [stats][process]
- Date: 2026-06-15
- What: Per-level "revives given" stat shown on the between-level screen.
- Why built: Feed the skill-point award and the stats display.
- Design: Counter on `Operative`, reset each level, rendered in the Safe House.
- Got right: Declared, reset, and displayed correctly.
- Where/why it failed: Nothing ever incremented it — the revive-completion path restored HP and played a
  sound but never bumped the reviver's counter, so it always read 0.
- Fix: Increment `reviver.revivesGiven` when `addReviveProgress()` reports completion.
- Why this fix: The completion branch is the single source of truth for "a revive happened"; the write
  belongs there, not in the UI.
- Rule of thumb: A tracked stat needs a writer at its event, not just a reader at its display.
- Link: session 2026-06-15 (review); `arc/src/systems/CoopSystem.ts`; commit e335061.
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E48 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-09-30 · projects/local__sandbox-event-writer-vs-delta-sum-ground-truth-check.md#E1 · compatible · sandboxes/2026-09-30__event-writer-vs-delta-sum-ground-truth-check.py · observed RESULT: PASS writer undercount 30/400, delta-sum overshoot 200, both silent; ground-truth cross-check catches both; clamp fixes overshoot only · scheduled train pass 5

## E2 — Tether cleanup was asymmetric when a partner went down
- Tags: [coop][state]
- Date: 2026-06-15
- What: Tether mechanic (freeze + spring-pull one operative toward the other).
- Why built: Let a player reel themselves to their partner to regroup.
- Design: `op.tetheredTo = partner.id`; each frame a spring sets the tetherer's velocity toward the
  partner; the partner's own tether is cleared in `goDown()`.
- Got right: Symmetric toggle and break-on-move-input worked.
- Where/why it failed: When the partner went down, only the downed one's `tetheredTo` was cleared — the
  live tetherer kept being reeled into the downed body. Asymmetric cleanup.
- Fix: In the spring loop, if `partner.isDown`, clear `op.tetheredTo` and skip.
- Why this fix: Tether is meaningless toward a downed partner; clearing at the point of use covers every
  path a partner can go down without scattering cleanup across events.
- Rule of thumb: Clear a relationship at the point you act on it, not only at the event that ends one side.
- Link: session 2026-06-15 (adversarial review); `arc/src/systems/CoopSystem.ts`; commit e335061.

## E1 — Shared midpoint camera framed nothing when players spawned apart
- Tags: [gamedev][coop][camera]
- Date: 2026-06-15
- What: Operative spawn placement + the shared midpoint-follow camera at level start.
- Why built: Co-op start with one camera that frames both players.
- Design: `spawnPoints[0]`/`[1]` placed P1/P2 at opposite arena corners; the single camera follows the
  midpoint of the two operatives.
- Got right: The midpoint follow keeps both framed whenever they're near each other.
- Where/why it failed: On launch the operatives sat at opposite far corners, so the midpoint was the
  empty arena center — the camera framed neither. User reported "no player mobs on screen."
- Fix: Spawn P1/P2 adjacent (side-by-side) in `MapBuilder` spawnPoints.
- Why this fix: A co-op game should literally begin together; adjacent spawns keep the shared camera
  valid until players choose to separate (split-screen handles real separation).
- Rule of thumb: In shared-camera co-op, spawn players together — a midpoint camera frames nothing if
  they start apart.
- Link: session 2026-06-15; `arc/src/systems/MapBuilder.ts`; commit e335061.
- Cited-by: 2026-07-30 · projects/pappydapimp69__dog.md#E80 · compatible · no sandbox · projects/pappydapimp69__dog.md
