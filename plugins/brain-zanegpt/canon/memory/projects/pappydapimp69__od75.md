# Pappydapimp69/OD75 — lessons

Project: Pappydapimp69/OD75. Newest first.

---

## E5 — game build loop closes on public state
- Date: 2026-08-19
- Project: Pappydapimp69/OD75
- Tags: [process][gamedev][deployment][testing][browser][state]
- What: A reusable game-build loop must treat local tests, assembled-bundle checks, deployment success, and the public build as four distinct states. Completion requires the public page to expose the intended build stamp and cache key.
- Why built: Repeated OD75 build cycles needed to turn playtest feedback into small versioned modules without reporting success while GitHub Pages still served the previous bundle.
- Design: Scope one player-visible change, preflight authoritative state and every input route, validate the source and assembled bundle, deploy the exact commit, then independently request the public page and assert its build stamp and cache key. Browser tests reread current element or entity positions after responsive reflow or autonomous movement.
- Got right: Static marker and override-order checks caught assembly mistakes before deployment. A versioned cache key made the public artifact identifiable. Centralizing repeat-input protection at the authoritative state transition covered pointer, keyboard, and gamepad callers with one guard.
- Where/why it failed: Workflow completion alone is an insufficient completion signal because Pages can remain in its service-side deploy step after source verification and assembly pass, and the public URL continues serving the old build during that interval. Fixed-coordinate browser actions are similarly insufficient after movement or layout reflow because they test stale geometry rather than current state.
- Fix: Monitor the exact deployment commit through completion, then fetch the public URL and require both the expected build stamp and versioned script key. In browser preflight, poll for timing and reread live geometry immediately before interaction. When a reported input bug is not reproducible on one device path, harden the shared state transition instead of adding a device-only patch.
- Why this fix: It verifies the artifact the player actually receives and places correctness at the shared authority boundary, where all input routes converge.
- Rule of thumb: A game build is not shipped when CI is green; it is shipped when the public artifact identifies itself as the intended build. Poll for when, reread for where, and guard behavior where all inputs converge.
- Provenance (verified/assumed): Verified first-hand by Codex during OD75 B53-B58 modular build and GitHub Pages deployment loops on 2026-08-15 through 2026-08-19. B58 passed source and assembly checks while Pages still served B57 until the deployment completed; public stamp and cache-key checks distinguished the states.
- Composed: N/A
- Link: C:\Users\Kompooter\.codex\skills\game-build-loop\SKILL.md

## E4 — game build loop closes on public state
- Date: 2026-08-19
- Project: pappydapimp69/od75
- Title: game build loops close on public state, not local or CI state
- Tags: [process][gamedev][deployment][testing][browser][state]
- What: A reusable game-build loop must treat local tests, assembled-bundle checks, deployment success, and the public build as four distinct states. Completion requires the public page itself to expose the intended build stamp and cache key.
- Why built: Repeated OD75 build cycles needed to turn playtest feedback into small versioned modules without reporting success while GitHub Pages still served the previous bundle.
- Design: Scope one player-visible change, preflight authoritative state and every input route, validate the source and the assembled bundle, deploy the exact commit, then independently request the public page and assert its build stamp and cache key. Browser tests reread current element or entity positions after responsive reflow or autonomous movement rather than reusing coordinates captured earlier.
- Got right: Static marker and override-order checks caught assembly mistakes before deployment. A versioned cache key made the public artifact identifiable at all. Centralizing repeat-input protection at the authoritative state transition covered pointer, keyboard, and gamepad callers with one guard.
- Where/why it failed: Workflow completion alone is an insufficient completion signal — Pages can remain in its service-side deploy step after source verification and assembly both pass, and the public URL continues serving the old build during that interval. Fixed-coordinate browser actions are similarly insufficient after movement or layout reflow, because they test stale geometry rather than current state.
- Fix: Monitor the exact deployment commit through completion, then fetch the public URL and require both the expected build stamp and the versioned script key. In browser preflight, poll for timing and reread live geometry immediately before interaction. When a reported input bug is not reproducible on one device path, harden the shared state transition instead of adding a device-only patch.
- Why this fix: It verifies the artifact the player actually receives, and it places correctness at the shared authority boundary where all input routes converge, rather than at whichever route happened to reproduce the report.
- Rule of thumb: A game build is not shipped when CI is green; it is shipped when the public artifact identifies itself as the intended build. Poll for when, reread for where, and guard behavior where all inputs converge.
- Provenance (verified/assumed): VERIFIED first-hand during the OD75 B53-B58 modular build and GitHub Pages deployment loops, 2026-08-15 through 2026-08-19 — B58 passed source and assembly checks while Pages was still serving B57 until the deployment completed, and the public stamp and cache-key checks were what distinguished the two states.
- Composed: N/A
- Link: OD75 B53-B58; game-build-loop SKILL.md

## E3 — upgrade clarity is not importance
- Date: 2026-08-12
- Project: Pappydapimp69/OD75
- Tags: [gamedev][ux][progression]
- What: A playtest showed that upgrade screens can be individually understandable yet still create fatigue when too many choices do not feel equally consequential.
- Why built: OD75 accumulated several between-stage progression surfaces: emotional/Prism upgrades, Boss Bonds, Heart/Pip attributes, Overdrive management, and a Sound Lab. Each screen explained its mechanics, but the player reported that only the Prism, Boss, and Heart pages felt immediately important because their effects were obvious in combat.
- Design: The build originally treated clear explanatory copy as sufficient justification for surfacing every progression system as a repeated between-stage decision. Sound and Overdrive collection therefore received the same interruption weight as immediate combat growth.
- Got right: The individual cards described what their upgrades did, and the three combat-direct pages were perceived as meaningful rather than confusing. The user could articulate the distinction precisely: the problem was not comprehension, but perceived gameplay importance.
- Where/why it failed: Sound Lab and Overdrive management still felt somewhat pointless despite being understandable. Repeatedly interrupting play for systems with weaker immediate feedback made the overall progression flow feel overwhelming and flattened the reward hierarchy.
- Fix: Reframe progression around consequence and frequency: keep immediate combat-impact decisions prominent, while moving inspection/collection-oriented systems toward optional or consolidated surfaces. The active design direction also gives previously cosmetic/secondary systems explicit combat contribution through Pip Ascended so their importance can be earned rather than merely explained.
- Why this fix: It aligns interruption cost with perceived consequence. A system that matters later can remain deep without demanding the same repeated modal attention as a choice that changes the next fight immediately.
- Rule of thumb: Clear copy explains an upgrade; it does not make the upgrade feel important. Spend repeated interruption budget in proportion to immediate gameplay consequence, and consolidate or defer lower-impact progression until its effect is visibly earned.
- Provenance (verified/assumed): Verified first-hand from the user's live OD75 playtest feedback on 2026-08-12 and the shipped B34-B37 iteration responding to duplicate screens, gamepad navigation, and readability. The proposed Pip Ascended consolidation is design direction only, and its gameplay effect remains an open assumption for this entry.
- Composed: N/A
- Link: Pappydapimp69/OD75 commit 01a29698fa4aea976cdd3060b30c471750e9433e and 2026-08-12 playtest session

## E2 — render procedural audio upgrades end to end
- Date: 2026-09-03
- Project: Pappydapimp69/OD75
- Tags: [gamedev][testing]
- What: Procedural soundtrack upgrades were validated by rendering the production Web Audio graph offline and comparing each upgrade's waveform with the same seeded baseline.
- Why built: The unlock state and note-scheduling branches were correct, but the player still could not hear a meaningful background change; scheduling assertions could not prove the final bus was audible, distinct, unclipped, or free of voice leaks.
- Design: A browser-only QA harness uses OfflineAudioContext, the production synthesizers, the production mix gain, deterministic noise and the real wave/boss scheduler. It renders baseline plus every mix at level 1 and level 4, then checks RMS, peak, normalized waveform change and the final active-voice count.
- Got right: Keeping logic tests for distinct scheduled events made level progression cheap to diagnose, while rendered checks proved all three signatures survived the complete graph in both wave and boss arrangements.
- Where/why it failed: Earlier tests stopped at owned levels and calls to oscillator helpers. Quiet overlapping voices could pass those tests while remaining masked by the base track, and long scheduled voices could exhaust a shared voice registry before reaching the output.
- Fix: Give music and combat effects separate bounded voice registries, replace overlapping unlock voices with recurring signatures, and add end-to-end offline renders with explicit lower bounds for signal and waveform change plus upper bounds for peak and lingering voices.
- Why this fix: Offline rendering is deterministic and fast, tests the same synthesis and bus code players hear, and detects both silence and dangerous loudness without depending on subjective microphone capture. Subjective recognizability remains a playtest question.
- Rule of thumb: For procedural audio progression, assert scheduling structure and render the production graph; state ownership alone cannot prove an upgrade is audible.
- Provenance (verified/assumed): Verified against OD75 B60 with 14 OfflineAudioContext renders spanning three mixes at levels 1 and 4 plus the combined level-4 arrangement during waves and bosses. All renders exceeded a 20% waveform-change threshold, remained below 0.15 peak in these fixtures, and ended with zero voices. Perceived clarity on the player's speakers remains assumed until playtesting.
- Composed: N/A
- Link: session / commit da3af30fd55a719f31ad9f57f0910bb431ebdde6

## E1 — pause guard must enclose late update wrappers
- Date: 2026-09-03
- Project: Pappydapimp69/OD75
- Tags: [gamedev][state][testing]
- What: A pause guard inside the original game update does not freeze timers added by later wrappers that continue after calling it.
- Why built: B59 adds Pip's Rally, Cover and Setup decisions and distinct boss phases to a game assembled from 48 ordered JavaScript modules.
- Design: Several modules capture update, call their predecessor, then mutate their own state. The base update checks S.run, but later bond and Ascended-duration wrappers do not inherit that early return.
- Got right: Keeping module order explicit made it possible to trace which wrappers execute after the guarded base. The new full-game test checks boss time, bond, cooldown, HEAT and Ascended duration together while the actual pause view is open.
- Where/why it failed: Returning from the base function only returns to its caller. B51 bond logic and B58 Ascended-cap logic still run in their caller wrappers even when the core update is paused. A test of the base update alone cannot establish a global pause invariant.
- Fix: Put the active-simulation guard at the final assembled update entry point, before calling any predecessor. Keep input polling and rendering outside that guard; reject new dash actions while paused or in a stage menu.
- Why this fix: The entire timer chain shares one simulation gate, so future behavior built inside that chain inherits the same pause semantics. Existing pause controls and independent modal interaction remain available.
- Rule of thumb: For decorated update loops, verify pause at the outermost assembled entry point and assert downstream state as well as the base clock.
- Provenance (verified/assumed): Verified the old wrapper control flow in b21-38.js and b21-45.js; verified the full assembled B59 pause and resume checks in Node/JSDOM and the actual browser, including desktop and phone viewports. No claim about physical controller overlays or background browser throttling.
- Composed: N/A
- Link: https://github.com/Pappydapimp69/OD75/commit/fa90baef21a3e472fbc93e10887ccf4ed7ad34c5
- Cited-by: 2026-10-08 · projects/pappydapimp69__brainwork.md#E13 · compatible · sandboxes/2026-10-08__pause-guard-test-scope-mutation-audit.py · observed RESULT: PASS 4 missing-pause-check mutants; survivors base-only=4 partial=3 whole-state=0 · scheduled brain train auto pass 2
