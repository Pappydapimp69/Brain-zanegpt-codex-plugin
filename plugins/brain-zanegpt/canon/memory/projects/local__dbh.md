# local/dbh — lessons

Project: local/dbh. Newest first.

---

## E6 — pages dynamic build stuck
- Date: 2026-07-06
- Project: local/dbh
- Tags: [github][pages][deployment][actions]
- What: DBH RPG's GitHub Pages site remained unpublished because the `pages-build-deployment` run stayed queued for over 13 hours with no jobs, while the Pages API reported `status: building`.
- Why built: The repo was configured for Pages and had a static root, but no explicit workflow existed. The dynamic Pages builder was stuck even though Actions were enabled and the `github-pages` environment allowed the `master` branch.
- Design: Diagnose Pages with `gh api repos/:owner/:repo/pages`, `gh api repos/:owner/:repo/pages/builds/latest`, `gh run list`, and environment branch policy checks. Then add `.github/workflows/deploy-pages.yml` using `actions/configure-pages`, `actions/upload-pages-artifact`, and `actions/deploy-pages`.
- Got right: The workflow deployed immediately and moved Pages from `building` to `built`. A content-level HTTPS check returned `200` and included the game page.
- Where/why it failed: The existing Pages configuration was present, but the generated dynamic workflow had no jobs and never completed. Without checking Actions runs, the failure looked like a generic Pages delay.
- Fix: Commit and push an explicit GitHub Pages workflow from `master` that uploads the static repo root and deploys through the `github-pages` environment.
- Why this fix: It replaces an opaque stuck dynamic builder with a visible, inspectable Actions run whose logs and status can be checked directly.
- Rule of thumb: When Pages says "building" for a long time, inspect the Actions run; if it is queued with no jobs, use an explicit deploy workflow and verify environment branch policy.
- Provenance (verified/assumed): Verified first-hand — DBH RPG GitHub Pages publishing fix; HTTPS check confirmed 200 after the fix.
- Link: C:\Users\Kompooter\Documents\dbh\.github\workflows\deploy-pages.yml
- Cited-by: 2026-08-10 · projects/pappydapimp69__august-10.md#E1 · compatible · no sandbox · August-10 .github/workflows/pages.yml (both fixes commented inline)
- Cited-by: 2026-10-09 · projects/pappydapimp69__brain.md#E117 · compatible · sandboxes/2026-10-09__relative-refs-break-at-a-missing-trailing-slash-and-js-fetch-paths-follow-the-page-not-the-script.py · observed RESULT: PASS plain-relative 5/5 at root, 5/5 at /myrepo/, 0/3 at /myrepo no redirect, 5/5 with redirect; absolute-path 3/3 at root vs 0/2 at /myrepo/; deeper page 1/3; stuck deploy served 404 while status said building; one-shot check 404… · brain train auto loop 2 pass 5 gap, unattended run 2026-10-09; session_01A7os5bwK2BHc7rwnvxx6Ts
- Audited: 2026-10-15 · pass · Read the entry. There is no sandbox because none is needed: the claim is about a real system (GitHub Pages' dynamic builder) and the evidence is a real before/after on it - a pages-build-deployment run queued 13 hours with no jobs while the Pages API said building, then an explicit configure-pages / upload-pages-artifact / deploy-pages workflow that moved it to built with an HTTPS 200 content check. Q1: nothing is assumed; the outcome came from the system. Q2: the Rule (inspect the Actions run when Pages says building; if queued with no jobs, use an explicit deploy workflow and check environment branch policy) matches what was done, though it rests on one incident and does not say how often the dynamic builder sticks. Q3: real system, so not modeled. Corroboration: brain E117 later observed a stuck deploy serving 404 while the status said building, and both SEVEN (.github/workflows/deploy.yml) and SEVIN (pages.yml) ship explicit upload-pages-artifact workflows, the practice this entry recommends. Limit: n = 1 and dated 2026-07; GitHub may have changed the builder since. · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 1 pass 3 (audit), 2026-10-15
- Reverified: 2026-10-15 · pass · sandboxes/2026-10-15__rebuild-dbh-e6-explicit-pages-workflow-on-seven-runs.py · observed RESULT: PASS 4/4; explicit workflow: 65/66 SEVEN deploys succeeded, max queue 0s, max run 49s, 0 dynamic-builder runs; the stuck-builder half is not reproducible here · Not blind (I audited this entry earlier in the session), and the stuck dynamic builder cannot be reproduced on demand, so this rebuild tests the fix half on independent real data: all 68 GitHub Actions runs of Pappydapimp69/Seven (2026-08-29 to 2026-10-11, fetched through the GitHub API on 2026-10-15 and embedded in the sandbox), a repo that deploys through an explicit upload-pages-artifact workflow. 65 of 66 SEVEN deploys succeeded, no run waited in the queue at all (max 0 s), the longest took 49 s, and none used the dynamic pages-build-deployment builder - consistent with the entry's fix. Differences from the original: a different repo and two months of runs instead of one incident; what is NOT re-verified is the failure itself (dynamic builder queued for hours with no jobs). · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 3 pass 4 (rebuild), 2026-10-15

## E5 — opening_arc_overlay
- Date: 2026-07-06
- Project: local/dbh
- Tags: [gamedev][onboarding][save][rpg]
- What: The first playable onboarding pass needed to teach the DBH RPG core loop without destabilizing the existing 55-objective campaign and save data. The solution was an opening-arc state layer stored under `state.flags.openingArc`, with its own step booleans, guide text, map marker, starter-technique choice, boss spawn, and completion save.
- Why built: The project already had movement, NPCs, destructibles, loot, shops, combat, XP, skill points, and saves, but New Game did not sequence those systems into a readable first 10 minutes. Reordering the whole campaign objective array would have broken existing objective indexes and older saves.
- Design: Keep the main objective list mostly stable and add a local onboarding controller that listens to existing gameplay events: movement distance, talking to Mira, breaking a training crate, picking up the training capsule, buying from the shop, defeating the sparring drone, selecting a starter skill, defeating Mira's Trial Echo, and saving. The Metro Crater exit checks `openingArc.complete` before allowing travel to Dust Barrens.
- Got right: The implementation reused the existing game verbs instead of creating a separate tutorial mode. The same `talk`, `damageDestructible`, `checkPickups`, `showShop`, `defeatEnemy`, and `checkExits` paths now feed the opening arc, so the player learns the real game loop.
- Where/why it failed: An early draft tried to reuse the main objective progression too directly. That created a risk where breaking the training crate would also trigger the later rockslide objective because destructible completion was globally mapped to objective 10.
- Fix: The training crate now completes only the opening blast objective, while later destructibles still complete the rockslide objective. The arc's guide target also walks through its own state in order instead of treating all incomplete early states as a return-to-mentor target.
- Why this fix: It protects the existing campaign and save contract while still making the opening feel authored. It also keeps future passes free to tune the opening arc without touching later story progression.
- Rule of thumb: When onboarding an already-built RPG prototype, prefer a small state overlay that observes real systems over reshuffling global campaign indexes. Gate the first exit if needed, and map tutorial objects narrowly so they do not satisfy later quests.
- Provenance (verified/assumed): Verified first-hand — built during the Opening Training Arc pass after the research blueprint on DBZ games, 2D action RPGs, game feel, and first-10-minute loops.
- Link: src/main.js
- Cited-by: 2026-10-12 · projects/pappydapimp69__sevin.md#E12 · compatible · no sandbox · Sevin commits 4ffdd9c, 62b7ba4; session_0125c7UeqZXhwxqnu8spbVdh

## E4 — new game must reset state
- Date: 2026-07-06
- Project: local/dbh
- Tags: [gamedev][save][ux][state]
- What: In DBH RPG, the `New` button originally opened character creation without resetting map state, inventory, objectives, defeated enemies, destructibles, RNG, or save-adjacent player progress.
- Why built: The early prototype treated character creation as the beginning of play. Once save/load, species, forms, maps, and progression existed, that shortcut became misleading.
- Design: Add a start screen with Continue, New Game, and Controls. Make `startNewGame()` create a fresh `makeWorld()` state, reapply species defaults, restore compatibility defaults, and then open character creation.
- Got right: The game already had a single authoritative `makeWorld()` constructor, so the reset path could reuse that instead of manually clearing individual fields.
- Where/why it failed: Character creation was UI-only. Opening it did not imply a new save or new world, so players could think they had restarted while stale entities and flags remained.
- Fix: Route the New button through a real reset function and keep Continue/Load separate.
- Why this fix: It preserves the single source of truth and prevents partial cleanup bugs as systems accumulate.
- Rule of thumb: Once a game has persistent world state, "new" must call the world constructor or equivalent full reset path before showing setup UI.
- Provenance (verified/assumed): Verified first-hand — DBH RPG basics-first pass.
- Link: C:\Users\Kompooter\Documents\dbh\src\main.js

## E3 — internal blueprints not gameplay
- Date: 2026-07-06
- Project: local/dbh
- Tags: [gamedev][backlog][testing][separation-of-concerns]
- What: The project had internal expansion blueprints exposed as a player-facing in-game checklist with buttons, save flags, XP, coins, and reward items. The user clarified that the blueprints are for the agent's build process, not part of gameplay.
- Why built: The backlog still needed to be actionable. Removing blueprint UI entirely would avoid confusing players, but the agent also needed a way to prove each cycle was actually built and not merely declared complete.
- Design: The implementation moved closure state into `docs/BLUEPRINT_CLOSURE_LOG.md` and smoke tests. Player-facing UI, controls, rewards, and save fields were removed. Each closed cycle now has evidence in the closure log plus one or more smoke assertions that guard the shipped behavior.
- Got right: The final shape keeps the backlog useful for development while preventing internal planning terms from leaking into the game world. Smoke now checks both positive implementation evidence and negative constraints such as no blueprint controls or reward functions.
- Where/why it failed: The first implementation treated blueprint stages as a meta-progression system. That failed because the same concept had two audiences: the agent needed a backlog, while the player needed a coherent RPG. Mixing them created UI and rewards that did not belong to the game fiction.
- Fix: Remove `showExpansionBlueprints`, `completeBlueprintStage`, blueprint hotkeys, blueprint buttons, and blueprint save fields. Add an internal closure log, a next-slice contract, and smoke assertions for every closed cycle.
- Why this fix: It preserves build accountability without adding fictional noise or save-schema clutter. It also lets future agents continue autonomously from documented evidence instead of replaying the same audit.
- Rule of thumb: If a roadmap item is for the agent, close it with docs and tests. Only add game UI when the player can understand it as part of the game's world or controls.
- Provenance (verified/assumed): Verified first-hand — observed during the DBH RPG backlog closure pass after the user clarified: "The blueprints are for you, not part of the gameplay."
- Link: docs/BLUEPRINT_CLOSURE_LOG.md, docs/NEXT_SLICE_CONTRACT.md, scripts/smoke.mjs

## E2 — modal minigame loop
- Date: 2026-07-05
- Project: local/dbh
- Tags: [gamedev][ui][loop][minigame][canvas]
- What: During the DBH RPG build, modal-hosted minigames such as Aura Forge and Sky Courier opened correctly but could not animate or process timed input because the global update function returned early whenever the modal was open.
- Why built: The game uses modal dialogs for focused screens like character creation, shops, skill trees, inventory, and minigames. Most modals should pause exploration, so an early return looked like a clean global rule.
- Design: Keep ordinary modals paused, but route modal-hosted active minigames through `updateMinigame(dt)` before returning from the main update loop. This preserves focused UI while keeping the minigame simulation alive.
- Got right: The pause rule protected the overworld from moving behind shops and menus. The minigames already had isolated update functions, so the fix could remain small.
- Where/why it failed: The pause rule treated every modal as passive UI. Canvas minigames are active simulations embedded in the modal, so they need time progression and input checks even while exploration remains paused.
- Fix: Change the update guard from "if modal open, return" to "if modal open and a minigame exists, update the minigame and HUD, then return; otherwise return."
- Why this fix: It keeps the useful modal pause behavior for shops, inventory, and character creation while allowing active modal experiences to run without special-casing each minigame in the event layer.
- Rule of thumb: If an overlay can contain a live game surface, separate "pause overworld" from "pause all simulation"; modal state is not the same thing as global pause state.
- Provenance (verified/assumed): Verified first-hand — DBH RPG Stage 4 autonomous build, `src/main.js` update loop and modal minigame systems.
- Link: C:\Users\Kompooter\Documents\dbh\src\main.js

## E1 — large iteration loops data guard
- Date: 2026-07-05
- Project: local/dbh
- Tags: [workflow][gamedev][testing][autonomy][data-driven]
- What: DBH RPG received a request to repeat 20 autonomous blueprint/build cycles, each split into five stages with Brain query/mine/sync rhythm. The implementation turned those cycles into `src/expansionBlueprints.js` data and added smoke tests that assert 20 blueprints and 100 total stages.
- Why built: A purely conversational "I repeated this" would be hard to verify, easy to lose, and disconnected from the playable artifact. The game needed a durable representation of the requested iteration plan.
- Design: Store every cycle as structured data with title, focus, five stages, query topic, work description, and reward. Expose it through an in-game Blueprint board and document the workflow in `docs/ITERATION_BLUEPRINTS.md`. Extend smoke tests to guard both the 20-cycle count and five-stage-per-cycle shape.
- Got right: The result is inspectable in code, visible in-game, saved through player flags, and covered by validation. The request's repetition became a usable production-planning system instead of transcript-only evidence.
- Where/why it failed: The raw request was larger than a single manual edit loop. Without a data boundary, the project would invite copy-paste sprawl and make it unclear whether the "20 times" requirement had actually been satisfied.
- Fix: Introduce a dedicated expansion blueprint module, a docs artifact, an in-game modal surface, saved completion flags, and smoke-count checks.
- Why this fix: Data makes repetition auditable and extensible. Tests catch accidental deletion or incomplete cycles. UI makes the plan part of the player-facing prototype instead of a private build note.
- Rule of thumb: For very large autonomous iteration requests, create a durable data model plus validation first, then execute the loop against that model.
- Provenance (verified/assumed): Verified first-hand — DBH RPG 20-cycle autonomous expansion pass, smoke tests confirm the 20×5 shape.
- Link: C:\Users\Kompooter\Documents\dbh\src\expansionBlueprints.js

