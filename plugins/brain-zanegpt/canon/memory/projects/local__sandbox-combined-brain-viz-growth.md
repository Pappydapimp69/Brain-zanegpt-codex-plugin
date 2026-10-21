# local/sandbox-combined-brain-viz-growth — lessons

Project: local/sandbox-combined-brain-viz-growth. Newest first.

---

## E14 — growing axes smoothed camera lags bursts
- Date: 2026-10-01
- Project: local/sandbox-combined-brain-viz-growth
- Tags: [viz][camera][animation]
- What: Animated running-total line chart (Brain things and connections, Jun 14 to today) whose axes grow with the data:
  the x-range ends just past the pen and the y-top is a nice ceiling above the current maximum, both eased per frame.
- Why built: with fixed axes sized to the final totals the first weeks drew as a flat strip and the last days as a vertical
  sliver against the right edge, so the user saw the line "go past the chart" and asked for a chart that grows and zooms
  out as the line progresses; Brain's garden-viz/E1 says a growth camera follows live extents.
- Design: target extents from the drawn content (x: pen + 4%, floor 10 days; y: niceTop(1.12 x max)), eased with
  k = 1 - exp(-dt / 0.3 s) while playing and snapped when paused; ticks re-derived from the live range (days, Mondays,
  months by span; 10-1000 nice steps by top).
- Got right: one continuous zoom-out, no act boundary; the event-paced clock and the growing axes compose, so the busy
  final days get both screen time and vertical room.
- Where/why it failed: the eased y-top lagged a bulk import (257 entries land within one calendar day, about 0.2 s of
  playback), so the head sat above the plot area for several frames with its label outside the chart; the ease alone
  cannot keep up with a step in the content.
- Fix: after easing, clamp every frame to the drawn content: xe >= pen + 1%, ye >= 1.05 x current max; the ease only
  governs the comfortable padding above that floor.
- Why this fix: the invariant "content inside the frame" must hold per frame, so it belongs to a hard clamp computed from
  the content, while easing is only for the padding that may lag without breaking anything.
- Rule of thumb: Grow-with-the-data axes need two parts: a per-frame hard floor from the drawn content and a separate eased padding; easing alone lags bursts and lets the head leave the plot.
- Provenance (verified/assumed): first-hand: the lag showed in a headless frame at 1.5 s (258 things drawn, y-top 200);
  after the clamp the same frame and frames at 2.3, 3.5 and 11 s stayed inside, on desktop and phone width.
- Composed: sandbox-combined-garden-viz/E1, sandbox-combined-brain-viz-growth/E7
- Link: https://claude.ai/code/session_01PgH3HZiwHdwLMt5FmTr1rn

## E13 — links as orbits not lines
- Date: 2026-10-01
- Project: local/sandbox-combined-brain-viz-growth
- Tags: [viz][growth-visualization][layout]
- What: Brain growth film (V5) draws no persistent link lines; a link is a brief flash plus a change in motion: each memory
  project orbits the heaviest project it is linked to (pull = link weight x mass), carrying its own satellites, and a linked
  idea falls from the rim into orbit around the project that used it.
- Why built: the user said lines between points mean nothing to a viewer and asked for every change to visibly change the
  system; four earlier versions drew links as lines and read as a hairball or a web.
- Design: host = argmax over heavier linked neighbours of weight x mass, with 1.3x hysteresis; orbit radii by birth order
  (g1 * sqrt(k)) plus 0.6 of the child's extent; Kepler speed sqrt(M/r^3); bodies chase their moving orbit slot with a
  saturated spring (accelerating fall far out, damped settle close in); systems pack around the smoothed centre of mass.
- Got right: the hierarchy needs no layout solver and is stable; it produced 13 real mergers (a system centre gaining a heavier
  linked star), and the final frame reads as a galaxy with arms because the post-link systems trail off the main one.
- Where/why it failed: area packing by the farthest satellite inflated the main system to 8 units, so stars shrank to specks;
  low far-field damping flung fallers off screen; mass-order flips between two linked hubs counted as fake mergers; lone
  unlinked projects on their own shell left an empty annulus.
- Fix: pack by radius of gyration (1.7 x), cap speed relative to the system size, count a merger only when the new centre was in
  another system, put unlinked projects on the rim with the unlinked ideas, and centre the frame on the smoothed centre of mass.
- Why this fix: each fix ties a visual quantity to a physical one (extent to mass spread, membership to linkage), so the picture
  stays explainable in one paragraph of rules.
- Rule of thumb: To show that links change a system, make each link a change in motion (orbit the heaviest linked neighbour, fall in, merge) and only flash the line; persistent lines between points read as noise.
- Provenance (verified/assumed): first-hand: ran on the real data (456 projects, 1140 memory links, 92 captured ideas), counted 13
  mergers and 92 landings, and checked screenshots at 5, 10, 20, 30.5, 33, 38 and 49 s on desktop and phone width.
- Composed: sandbox-combined-brain-viz-growth/E9, ideas:VIZ/growth-visualization/phyllotaxis-sprout-galaxy
- Link: https://claude.ai/code/session_01PgH3HZiwHdwLMt5FmTr1rn

## E12 — growth film event clock
- Date: 2026-10-01
- Project: local/sandbox-combined-brain-viz-growth
- Tags: [viz][animation][timeline]
- What: Brain growth film (V5): one continuous 45 s timeline from first commit to today, replacing two acts with a hand-set
  speed change at the memory-ideas link.
- Why built: with a calendar clock the last 2.9 of 109 days would get under 1 s; the earlier fix split the film into acts with
  different speeds, which the user read as two separate stories and said Act 2 did not affect Act 1.
- Design: an event clock: every change (entry, idea, tension, resolution, CLI commit, connection) gets an equal slice of the
  runtime, plus a 10% share by calendar time so quiet weeks do not vanish; events sharing a timestamp get consecutive slices.
  Date and pace (days/s falling to hours/s) are read back through the inverse map; the ruler spaces real dates by the same clock.
- Got right: the post-link burst took 31% of the runtime with no hand-set boundary (link at 30.8 of 45 s); bulk commits spread
  out instead of landing in one frame.
- Where/why it failed: acts with hand-picked speeds made the boundary itself the story and hid that growth was continuous; the
  speed-up was an editing choice, not something the data produced.
- Fix: screen time = (event index + beta * N * calendar fraction) / ((1 + beta) * N) * duration, beta 0.1, with a piecewise-linear
  inverse for date readouts.
- Why this fix: the clock derives from the data, so dense periods slow themselves and nothing has to be warped by hand.
- Rule of thumb: When a growth story is back-loaded in calendar time, drive the film by an event clock (equal screen time per change, plus a small calendar share) instead of splitting it into acts with hand-set speeds.
- Provenance (verified/assumed): first-hand: computed 3719 events, measured the link at 30.8 s of 45 (31% after), and checked
  the date/pace readouts and ruler in screenshots at 5, 20, 30.5, 38 and 49 s.
- Composed: sandbox-combined-brain-viz-growth/E7, sandbox-combined-brain-viz-growth/E9
- Link: https://claude.ai/code/session_01PgH3HZiwHdwLMt5FmTr1rn

## E11 — viz islands need community weighted springs
- Date: 2026-10-01
- Project: local/sandbox-combined-brain-viz-growth
- Tags: [viz][growth-visualization][layout]
- What: Brain growth animation (V4, galaxy framing): memory projects as bodies in one physics sim, memory links as springs,
  ideas kernels as dust that falls in when linked. Act 1 had to show islands forming, not a uniform cloud.
- Why built: the user said Act 1 grouping was understated across three versions; preflight found Louvain modularity 0.50 with
  26 communities at the link date, so the structure was real and the renderer was hiding it.
- Design: plain force layouts (Fruchterman-style springs, then LinLog with degree-weighted repulsion) drawn per frame; then a
  community-weighted model: Louvain (multi-level, resolution 2) on the FINAL project graph fixes labels; links inside a
  community are short strong springs, links across are long weak springs; islands are connected components of active
  intra-community links, with cohesion to the island centroid and island-island repulsion.
- Got right: islands form only when their own links exist (labels set spring strength, never position), so growth order is
  preserved; measured separation (centroid distance over summed RMS radii) instead of eyeballing.
- Where/why it failed: 161 of 196 projects are one connected component at the link date, so every unweighted variant drew a
  ball/hairball; LinLog pushed hubs to the rim with long spokes. Multi-level Louvain at resolution 1 merged Act 1 into one
  97-project island (same failure at a coarser grain); resolution 3 split islands too thin (separation 1.57).
- Fix: resolution-2 communities from the final graph; intra springs k=3, rest 0.05 plus both entry-cluster radii; cross springs
  k=0.25, rest 0.5; island repulsion sqrt(na*nb)/(d^2+0.02). Result at the link date: 11 islands of 3+ projects, separation
  median 2.79 (p25 2.31); at the end 22 islands, median 1.50.
- Why this fix: connectivity is not clustering; a layout only shows groups when the force model itself distinguishes within-group
  from between-group links, and community detection is the honest source for that distinction.
- Rule of thumb: When a knowledge graph is one giant component, a force layout shows a hairball; weight springs by detected community (strong/short inside, weak/long across) and tune resolution by a measured island-separation ratio, not by eye.
- Provenance (verified/assumed): first-hand: ran all four layouts on the real Brain data (456 projects, 1140 links), measured the
  separation ratio for resolutions 1.5, 2 and 3, and checked screenshots at t=14 s and the link date.
- Composed: sandbox-combined-brain-viz-growth/E9, ideas:VIZ/growth-visualization/phyllotaxis-sprout-galaxy
- Link: https://claude.ai/code/session_01PgH3HZiwHdwLMt5FmTr1rn

## E10 — frozen sim time keeps fresh highlights lit
- Date: 2026-10-01
- Project: local/sandbox-combined-brain-viz-growth
- Tags: [viz][animation][timeline]
- What: An animation drives everything from a sim time derived from screen time (play, rewind, one-third replay, then a hold
  where sim time is frozen at the end). Fresh-event highlights (new link flash, landing flash, comet trail) are computed
  as sim_time minus event_time.
- Why built: keeping state a pure function of sim time makes scrubbing, rewind and slow-motion replay free.
- Design: every effect age = st - t_event, with st = simAt(t); the hold segment maps all of t in [45, 50] to st = 26.
- Got right: rewind and replay needed no special cases; slowed effects in the replay read as genuine slow motion.
- Where/why it failed: in the hold, events within the last highlight window before the end stay "fresh" forever, because their
  age stops growing; the final frame showed a blown-out white starburst of links and a stray comet trail that never faded.
- Fix: a screen-time factor calm = 1 - smoothstep(45, 46.2, t) multiplies every freshness term (link flash, entry pop, dust pop,
  landing flash, comet trail), so highlights decay in real time even while sim time is frozen.
- Why this fix: decay of attention cues belongs to the viewer's clock, while positions belong to the data clock; one factor keeps
  the pure-function design and needs no per-effect state.
- Rule of thumb: If an animation maps screen time to a sim time that can freeze, any effect aged by sim time stays lit at the freeze; fade attention highlights by screen time and positions by sim time.
- Provenance (verified/assumed): first-hand: the bug showed in a headless screenshot at t=49 s; after the fix the same frame was
  clean, and frames at 31 s (replay) and 26.5 s (rewind) were unchanged.
- Composed: sandbox-combined-brain-viz-growth/E7
- Link: https://claude.ai/code/session_01PgH3HZiwHdwLMt5FmTr1rn

## E9 — brain viz semantic anchor warp
- Date: 2026-07-13
- Project: local/sandbox-combined-brain-viz-growth
- Tags: [viz][animation][state][timeline][testing]
- What: When Brain Viz has authored story beats but data-sized animation durations, a raw proportional timeline drifts away from the intended semantic stages. Pin captions and stage changes to semantic anchors, then piecewise-warp the data motion between those anchors.
- Why built: The retrieved Brain memory warned that data-sized text and authored motion drift under scale factors unless pinned at semantic anchors. This loop retested that rule against the five-stage Brain Viz garden timeline.
- Design: The sandbox modeled five stage counts `[4, 16, 64, 256, 305]` with square-root data durations. It compared authored equal anchors `[0, .25, .5, .75, 1]` against cumulative data-duration anchors, then compared that with a semantic warp that preserves authored anchors.
- Got right: The raw data-duration timeline had `maxLinearDrift: 0.455`, large enough for captions and stage visuals to desynchronize. The semantic warp had `maxWarpedDrift: 0`.
- Where/why it failed: Data-sized timing solves pacing, but if captions follow authored story positions and marks follow raw duration positions, the viewer sees the wrong words attached to the wrong visual moment.
- Fix: Define semantic anchors first, then map data-sized motion inside each interval. Captions, buttons, and stage labels stay pinned to the anchors.
- Why this fix: It keeps the human-facing story stable while preserving data-sensitive motion inside each stage.
- Rule of thumb: If a visualization has both authored narrative beats and data-sized motion, anchor the narrative first and warp the motion between anchors.
- Provenance (verified/assumed): Verified first-hand in `scripts/brain-viz-three-train.mjs` on 2026-07-13.
- Composed: test/E11, brain/E5
- Link: `scripts/brain-viz-three-train.mjs`
- Cited-by: 2026-10-01 · projects/local__sandbox-combined-brain-viz-growth.md#E11 · compatible · no sandbox · https://claude.ai/code/session_01PgH3HZiwHdwLMt5FmTr1rn
- Cited-by: 2026-10-01 · projects/local__sandbox-combined-brain-viz-growth.md#E12 · compatible · no sandbox · https://claude.ai/code/session_01PgH3HZiwHdwLMt5FmTr1rn
- Cited-by: 2026-10-01 · projects/local__sandbox-combined-brain-viz-growth.md#E13 · compatible · no sandbox · https://claude.ai/code/session_01PgH3HZiwHdwLMt5FmTr1rn

## E8 — brain viz playback tolerance
- Date: 2026-07-13
- Project: local/sandbox-combined-brain-viz-growth
- Tags: [viz][animation][state][testing]
- What: A Brain Viz playback timeline that advances by accumulated `dt` can fail to complete exactly at the intended endpoint. At 30 ticks of `1/30`, JavaScript produced `0.9999999999999999`, so an exact `elapsed >= 1` completion check never fired. The fix is to complete within a half-tick tolerance and snap the playhead to the target.
- Why built: The user asked for three Brain training loops on Brain Viz with sandbox verification. This loop re-tested the retrieved animation lesson against the Brain Viz timeline/playback control.
- Design: `scripts/brain-viz-three-train.mjs` simulated a one-second playback timeline advanced by `30` ticks of `1/30`. It compared exact completion against a tolerance check using `duration - dt / 2`, then snapped the timeline to `1`.
- Got right: The sandbox observed `elapsedAfterThirtyTicks: 0.9999999999999999`, `exactComplete: false`, `toleranceComplete: true`, and `snapped: 1`.
- Where/why it failed: The exact comparison fails because frame-time accumulation is floating-point arithmetic, not an integer counter. The bug is easy to miss because other frame rates may round in the opposite direction.
- Fix: Use tolerance-based completion at timeline boundaries and snap to the exact stage endpoint when the tolerance fires.
- Why this fix: The tolerance absorbs one-frame numerical error, and snapping prevents the UI from visually resting at 99.999%.
- Rule of thumb: Never gate Brain Viz playback completion on exact accumulated time. Complete within a frame tolerance and snap to the semantic endpoint.
- Provenance (verified/assumed): Verified first-hand in `scripts/brain-viz-three-train.mjs` on 2026-07-13.
- Composed: sandbox-anim/E1, brain/E5
- Link: `scripts/brain-viz-three-train.mjs`
- Cited-by: 2026-10-08 · projects/pappydapimp69__brain.md#E98 · compatible · sandboxes/2026-10-08__narration-novelty-gate-and-cue-timing.py · observed RESULT: PASS novelty gate 6/6 on constructed captions, paraphrase of visible count slips through=True; exact cue compare drops the final stinger for 3 of 4 dts, half-tick tolerance 4/4 each · scheduled brain train auto pass 5, 2026-10-08

## E7 — brain viz labels need shared timeline pins
- Date: 2026-07-13
- Project: local/sandbox-combined-brain-viz-growth
- Tags: [viz][animation][sync][growth-visualization][testing]
- What: When a Brain visualization uses piecewise timeline warping for growth events, text labels and data marks must share the same semantic pins. If visuals are pinned but labels are placed by a separate linear scale, labels drift away from the events they describe.
- Why built: The requested target was `brain/viz`. The interaction claim was that data-sized text/motion synchronization composes with Brain's growth visualization pacing: once the visual timeline is warped to make growth readable, every annotation tied to those events must use the same warp.
- Design: Built `sandbox-brain-viz-label-warp.js`, a deterministic model with: - Three growth events: `seed` at tick 0, `sprout` at tick 20, and `canopy` at tick 80. - A pinned visual timeline mapping tick 20 to time 30. - A naive label strategy using a linear tick-to-time scale. - A fixed label strategy using the same piecewise pins as the visual. - Drift measured as absolute difference between visual event time and label time.
- Got right: The sandbox isolates the synchronization bug from rendering. It measures whether labels and marks agree on semantic event time after timeline warping.
- Where/why it failed: With pinned visuals and linear labels, the `sprout` label drifted by 5 timeline units. The endpoints still matched, so checking only the start/end of the animation would miss the mid-timeline label drift.
- Fix: Define semantic timeline pins once and use the same piecewise warp for visual marks, labels, and authored motion. Do not maintain a separate linear label scale after introducing pacing warps.
- Why this fix: When labels used the same pinned warp as the visual, max drift dropped from 5 to 0 across all events.
- Rule of thumb: If a Brain/Viz timeline is warped for readability, the warp is part of the data contract. Labels, marks, and motion all consume the same pins.
- Provenance (verified/assumed): Verified first-hand on 2026-07-13 by running `node sandbox-brain-viz-label-warp.js` in `C:\Users\Kompooter\Documents\Brain`. Observed: visual pinned + label linear = max drift 5, drift by label `seed:0,sprout:5,canopy:0`; visual pinned + label pinned = max drift 0, drift by label `seed:0,sprout:0,canopy:0`.
- Composed: test/E11, brain/E5
- Link: Sandbox: `sandbox-brain-viz-label-warp.js`; related artifacts: `brain-viz.html`, `brain-garden-viz.html`
- Cited-by: 2026-10-01 · projects/local__sandbox-combined-brain-viz-growth.md#E10 · compatible · no sandbox · https://claude.ai/code/session_01PgH3HZiwHdwLMt5FmTr1rn
- Cited-by: 2026-10-01 · projects/local__sandbox-combined-brain-viz-growth.md#E12 · compatible · no sandbox · https://claude.ai/code/session_01PgH3HZiwHdwLMt5FmTr1rn
- Cited-by: 2026-10-01 · projects/local__sandbox-combined-brain-viz-growth.md#E14 · compatible · no sandbox · https://claude.ai/code/session_01PgH3HZiwHdwLMt5FmTr1rn

## E6 — brain viz growth total clamp
- Date: 2026-07-13
- Project: local/sandbox-combined-brain-viz-growth
- Tags: [viz][git][tooling][testing]
- What: A Brain Viz growth timeline built from positive event deltas can overdraw the current truth. The event stream is useful for animation, but the current total must be parsed independently and used as a clamp.
- Why built: The retrieved Brain memory warned that summing positive per-commit deltas can inflate a growth stream. This loop retested the rule against Brain Viz's "lessons growing over time" presentation.
- Design: `scripts/brain-viz-three-train.mjs` modeled a true current total of `305` lessons and a history stream `[56, 38, -22, 91, 160, -18, 45]`. It compared positive-only accumulation, signed accumulation, and a positive stream clamped to the true total.
- Got right: Positive-only accumulation produced `390`, overdraw by `85`. The clamp returned `305`, overdraw by `0`.
- Where/why it failed: The animation stream and the current-state truth are different sources. A history rewrite, correction, deletion, or negative delta can make positive-only animation arithmetic disagree with the actual current corpus.
- Fix: Parse the current total independently, animate the event stream only up to that total, and make any excess explicit as discarded animation history rather than visible knowledge.
- Why this fix: The independent total acts as a ground truth anchor. The animation can still show growth, but it cannot display more lessons than actually exist.
- Rule of thumb: For Brain Viz growth timelines, event streams are animation input, not truth. Clamp them to a separately parsed current total.
- Provenance (verified/assumed): Verified first-hand in `scripts/brain-viz-three-train.mjs` on 2026-07-13.
- Composed: brain/E2, brain/E3
- Link: `scripts/brain-viz-three-train.mjs`
- Cited-by: 2026-07-18 · projects/pappydapimp69__brain.md#E10 · compatible · no sandbox · session (Sprout viz data-refresh work), artifact f928d8da-8237-42af-a10a-2b1c38ccc60f

## E5 — brain viz growth stream must clamp before scheduling
- Date: 2026-07-13
- Project: local/sandbox-combined-brain-viz-growth
- Tags: [viz][git][growth-visualization][tooling][testing]
- What: A Brain visualization that turns git-history positive deltas into growth marks must clamp the event stream to the true HEAD total before scheduling marks. Otherwise a rename, rebase, or hand-corrected anchor can make the visualization draw more growth events than the artifact actually contains.
- Why built: The requested target was `brain combined on brain Viz`. The interaction claim was that brain#E2's "positive deltas can exceed the true current total" becomes a visual overdraw bug when those deltas feed a growth visualization scheduler.
- Design: Built `sandbox-brain-viz-growth-clamp.js`, a deterministic model with: - A true HEAD total of 10. - A git-derived positive-delta stream of 4, 5, 4, and 3 events. - A naive visual scheduler that draws one mark per positive delta. - A fixed scheduler that clamps the event stream to the true HEAD total before assigning visual indices.
- Got right: The sandbox measures the visual consequence, not just the accounting mismatch. It counts overdrawn marks whose visual index exceeds the true total.
- Where/why it failed: The naive positive-delta stream produced 16 source events for a true total of 10. The visualization overdrawn 6 marks and ended at visual count 16, falsely implying more current content than exists.
- Fix: Compute the true total independently from HEAD/current canon, then clamp or reconcile the derived history event stream before creating scheduled visual marks.
- Why this fix: Clamping before scheduling produced 10 source events, 0 overdrawn marks, and final visual count 10, exactly matching the true HEAD total.
- Rule of thumb: History is a narrative source, not an accounting source. For Brain/Viz growth charts, schedule from a history stream only after it is reconciled to the current canonical total.
- Provenance (verified/assumed): Verified first-hand on 2026-07-13 by running `node sandbox-brain-viz-growth-clamp.js` in `C:\Users\Kompooter\Documents\Brain`. Observed: positive deltas only = 16 source events, true HEAD total 10, 6 overdrawn marks, final visual count 16; clamped to HEAD total before scheduling = 10 source events, true HEAD total 10, 0 overdrawn marks, final visual count 10.
- Composed: brain/E2, brain/E5
- Link: Sandbox: `sandbox-brain-viz-growth-clamp.js`; related artifacts: `brain-viz.html`, `brain-garden-viz.html`
- Cited-by: 2026-07-18 · projects/pappydapimp69__brain.md#E10 · compatible · no sandbox · session (Sprout viz data-refresh work), artifact f928d8da-8237-42af-a10a-2b1c38ccc60f

## E4 — brain viz color transitions need path sampling
- Date: 2026-07-13
- Project: local/sandbox-combined-brain-viz-growth
- Tags: [viz][accessibility][animation][visualdesign][testing]
- What: A Brain/Viz palette can pass endpoint checks and still become confusable during an animated color/luminance transition. Accessibility validation has to sample the transition path, not just the start and end colors.
- Why built: The requested target was `brain train seams brain/viz`. The interaction claim was that Brain/Viz's growth and animation marks compose with the accessibility-render finding: animated visual states need trajectory checks because midpoint colors can collide with unrelated marks even when endpoints are safe.
- Design: Built `sandbox-brain-viz-transition-palette.js`, a deterministic luminance model with: - A third visual mark at luminance 50. - A confusion threshold of +/-3 luminance points. - A risky endpoint-safe transition from 35 to 65. - A safe endpoint-safe transition from 35 to 42. - 21 sampled points across each transition.
- Got right: The sandbox separates endpoint validation from path validation. It catches the failure exactly where it lives: the interpolated states.
- Where/why it failed: The 35-to-65 transition passed endpoint checks against the third mark, but 5 sampled midpoints were confusable: t=0.4, 0.45, 0.5, 0.55, and 0.6. Endpoint-only validation would report the palette safe.
- Fix: For Brain/Viz animated color changes, sample the full transition path at frame-level or equivalent resolution against every nearby mark/class. Adjust the path, add non-color encodings, or choose endpoint pairs whose interpolation stays outside confusion bands.
- Why this fix: The path-safe 35-to-42 transition also passed endpoint checks and had 0 confusable samples, proving the check needs to validate the whole path rather than reject animation categorically.
- Rule of thumb: In Brain/Viz, palette accessibility is temporal when colors animate. Validate the in-between states, not only the designed swatches.
- Provenance (verified/assumed): Verified first-hand on 2026-07-13 by running `node sandbox-brain-viz-transition-palette.js` in `C:\Users\Kompooter\Documents\Brain`. Observed: endpoint-safe 35-to-65 transition had endpoint pass `true`, 5 confusable samples, range `0.4,0.45,0.5,0.55,0.6`; endpoint-safe 35-to-42 transition had endpoint pass `true` and 0 confusable samples.
- Composed: the-game-the-recursion/E12, sandbox-combined-accessibility-render/E1
- Link: Sandbox: `sandbox-brain-viz-transition-palette.js`; related artifacts: `brain-viz.html`, `brain-garden-viz.html`

## E3 — brain viz categories cannot be color only
- Date: 2026-07-13
- Project: local/sandbox-combined-brain-viz-growth
- Tags: [viz][accessibility][visualdesign][web][testing]
- What: Brain/Viz category marks cannot rely on hue alone. When hue is removed or collapsed into luminance, two categories with the same brightness become indistinguishable unless another channel such as label, shape, or pattern carries the category identity.
- Why built: The requested target was `external brain train brain/viz combined until satisfied`. The interaction claim was that Brain/Viz category colors must compose with external accessibility rules: palette choice is not enough when the visual information is categorical.
- Design: Built `sandbox-brain-viz-color-redundancy.js`, a deterministic model with: - Three Brain/Viz marks: `soil`, `water`, and `pest-control`. - `soil` and `water` assigned different hues but the same luminance. - A hue-only category encoding projected through grayscale/luminance. - A redundant encoding that also includes a category label channel. - Collision detection over category keys.
- Got right: The sandbox tests the accessibility failure at the information channel level. It does not ask whether the colors look pleasant; it asks whether category identity survives when hue is unavailable.
- Where/why it failed: Under hue-only encoding after luminance projection, `soil` and `water` collided. The categories were not uniquely recoverable. With a redundant label channel, all categories stayed unique.
- Fix: Encode Brain/Viz categories with at least one non-color channel: direct labels, shapes, patterns, icons, or grouped layout. Keep color as reinforcement, not the only carrier of meaning.
- Why this fix: The redundant label channel produced zero category collisions while the hue-only projection produced `soil~water`. That confirms the missing guarantee is redundant coding, not just a better hue pick.
- Rule of thumb: For Brain/Viz category marks, color can decorate or reinforce meaning but cannot be the sole key. Every category needs a non-color identity path.
- Provenance (verified/assumed): Verified first-hand on 2026-07-13 by running `node sandbox-brain-viz-color-redundancy.js` in `C:\Users\Kompooter\Documents\Brain`. Observed: hue-only category marks after grayscale/luminance projection = unique categories `false`, collision `soil~water`; color + redundant label channel = unique categories `true`, no collisions. External verification: W3C WCAG 2.2 includes Success Criterion 1.4.1 Use of Color, which requires color not be the only visual means of conveying information, and Success Criterion 1.4.11 Non-text Contrast, which covers graphical objects required to understand content.
- Composed: the-game-the-recursion/E12, sandbox-combined-accessibility-render/E2
- Link: Sandbox: `sandbox-brain-viz-color-redundancy.js`; W3C WCAG 2.2 Use of Color: `https://www.w3.org/TR/WCAG22/#use-of-color`; W3C WCAG 2.2 Non-text Contrast: `https://www.w3.org/TR/WCAG22/#non-text-contrast`
- Cited-by: 2026-10-10 · projects/local__sandbox-silhouette-first-cue-audit.md#E1 · incompatible · sandboxes/2026-10-10__silhouette-first-needs-a-size-floor-and-a-backdrop-outline.py · observed RESULT: FAIL predictions held=2/5 failed=P1,P2,P5; S1 grey recolour=28/28 shape=4 (deutan recolour 5, shape 0); sweep shape/lumspread f8=4/1 on the area-mean metric; eased-bg worst plain=28 outlined=0 (outline 4.75:1); post-hoc prop-only p… · session_01YFLLRpDsfZpRstb2KT2MQy
- Cited-by: 2026-10-10 · projects/local__sandbox-silhouette-size-floor-metric-audit.md#E1 · incompatible · sandboxes/2026-10-10__silhouette-size-floor-survives-peak-and-viewer-metrics-but-not-area-mean.py · observed RESULT: FAIL held=4/9 failed=P3,P4,P5,P6,P9; defensible=['raw-peak', 'V1-peak', 'V2-peak', 'V1-W', 'V2-W']; S8 counts 16px/2px area-mean 4/4, raw-peak 0/0, V1-peak 0/4, V2-peak 0/12, V1-W 0/0, V2-W 0/4 at nominal; at half the window top th… · session_01YFLLRpDsfZpRstb2KT2MQy

## E2 — brain viz batch filters must compose once
- Date: 2026-07-13
- Project: local/sandbox-combined-brain-viz-growth
- Tags: [viz][canvas][animation][growth-visualization][performance][testing]
- What: A Brain/Viz growth reveal can use `sqrt(n)` pacing and still stutter if every newly revealed mark applies an expensive canvas filter individually. Size-aware timing controls visual cadence; filter/compositing strategy controls render cost.
- Why built: The requested target was `Brain train brain viz`. The interaction claim was that brain#E5's sublinear batch pacing composes with wrong-sky#E3's canvas-filter cost warning: a large batch that is paced correctly can still become expensive if each mark pays its own filter cost.
- Design: Built `sandbox-brain-viz-filter-batch-cost.js`, a deterministic cost model with: - Growth batch sizes `[4, 16, 64, 256]`. - `sqrt(n)` reveal budgets. - A per-mark filter strategy costing `base draw + filter` for every mark. - A composited strategy drawing marks unfiltered and applying one filter pass per batch. - Cost per budget tick as the measured pressure on reveal smoothness.
- Got right: The sandbox keeps timing and rendering cost separate. That shows why a pacing fix can be correct but incomplete.
- Where/why it failed: With per-mark canvas filters, the 256-mark batch cost `3328` units over `320` budget ticks, or `10.4` cost per budget tick. The small 4-mark batch was only `1.3`, so the large batch still produced a cost spike despite sublinear pacing.
- Fix: Draw the batch into an unfiltered layer or buffer, then apply the visual filter once to the composited result. Keep per-mark work to simple draw operations.
- Why this fix: The one-pass composited strategy reduced the 256-mark batch to `296` cost over `320` budget ticks, or `0.925` cost per budget tick, while preserving the same `sqrt(n)` reveal budget.
- Rule of thumb: For Brain/Viz growth batches, pace by batch size and composite expensive effects by pass count. Do not let per-mark filters reintroduce a linear cost spike inside a fixed reveal budget.
- Provenance (verified/assumed): Verified first-hand on 2026-07-13 by running `node sandbox-brain-viz-filter-batch-cost.js` in `C:\Users\Kompooter\Documents\Brain`. Observed: per-mark canvas filter cost per budget tick rose from `1.3` at size 4 to `10.4` at size 256; one composited filter pass kept the size-256 batch at `0.925` cost per budget tick.
- Composed: brain/E5, the-game-wrong-sky/E3
- Link: Sandbox: `sandbox-brain-viz-filter-batch-cost.js`; related artifacts: `brain-viz.html`, `brain-garden-viz.html`
- Cited-by: 2026-10-09 · projects/local__2026-10-09__two-futures-timelapse-fit-min-axis-and-composite-filter-cost.md#E1 · compatible · sandboxes/2026-10-09__two-futures-timelapse-fit-min-axis-and-composite-filter-cost.py · observed RESULT: PASS counters equal at t0 and diverge (1 vs 401); H-only clips 68% on portrait, min-axis 0 (landscape 640x720 clips 1%, stacked 414x448 clips 0%); per-mark overruns 88 frames, composite 0; composite fails at N=1000 · scheduled brain train auto pass 5 (gap mode)

## E1 — brain viz auto growth needs pause or reduced motion
- Date: 2026-07-13
- Project: local/sandbox-combined-brain-viz-growth
- Tags: [viz][accessibility][animation][web][testing]
- What: A Brain/Viz growth reveal that auto-starts and runs for more than five seconds alongside other content needs either a pause/stop/hide control or a reduced-motion/static path. Size-aware pacing alone does not make the motion accessible.
- Why built: The requested target was `external brain train brain/viz combined until satisfied`. The interaction claim was that Brain's sublinear growth pacing must compose with external web accessibility requirements: making the reveal feel better does not remove the need for user control when motion auto-runs long enough.
- Design: Built `sandbox-brain-viz-reduced-motion-pause.js`, a deterministic model with: - Brain/Viz growth batch sizes `[4, 16, 64, 256]`. - The existing `sqrt(n)` pacing model at 16ms ticks. - An auto-starting reveal presented alongside other content. - Three cases: no motion control, explicit pause control, and reduced-motion static mode. - A WCAG-style pass/fail predicate for auto-running movement over five seconds.
- Got right: The sandbox separates pacing quality from accessibility control. The same 9.6s reveal can be well paced and still require a control.
- Where/why it failed: The auto growth reveal with no control lasted `9600ms`, was moving for more than five seconds, and failed the pause/stop/hide predicate. Adding a pause control passed without changing the reveal duration. Reduced-motion static mode had duration `0ms`, so it did not trigger the moving-over-five-seconds condition.
- Fix: For Brain/Viz auto growth, provide an explicit pause/stop/hide control and honor reduced-motion preference by replacing non-essential motion with a static or greatly reduced presentation.
- Why this fix: The pause-control case passed with the full `9600ms` reveal, and the reduced-motion case passed by removing the auto-running motion. Those are complementary: one gives user control over default motion, the other respects a prior motion preference.
- Rule of thumb: Pacing is not control. Any Brain/Viz animation that auto-runs longer than five seconds beside other content needs a user control, and non-essential motion should honor reduced-motion preference.
- Provenance (verified/assumed): Verified first-hand on 2026-07-13 by running `node sandbox-brain-viz-reduced-motion-pause.js` in `C:\Users\Kompooter\Documents\Brain`. Observed: auto growth no control = `9600ms`, moving over five seconds `true`, pause control `false`, reduced motion `false`, pass `false`; auto growth with pause = `9600ms`, pass `true`; reduced motion static = `0ms`, pass `true`. External verification: W3C WCAG 2.2 Success Criterion 2.2.2 says auto-starting moving/blinking/scrolling information lasting more than five seconds alongside other content needs a mechanism to pause, stop, or hide it unless essential. MDN documents `prefers-reduced-motion` as the CSS media feature for detecting a user request to minimize non-essential motion.
- Composed: brain/E5, test/E11
- Link: Sandbox: `sandbox-brain-viz-reduced-motion-pause.js`; W3C WCAG 2.2 SC 2.2.2: `https://www.w3.org/TR/WCAG22/#pause-stop-hide`; MDN `prefers-reduced-motion`: `https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion`
- Cited-by: 2026-10-08 · projects/local__sandbox-step-transition.md#E1 · compatible · sandboxes/2026-10-08__step-transition-direction-survives-rapid-nav-only-if-retargeted.py · observed RESULT: PASS 5 scenarios; teleport at input: retarget 0.000 vs naive 0.296. First run had two harness errors of mine (settle threshold 0.01 settled early; max-jump metric dominated by normal easing speed), fixed to measure exact settle and… · brain train auto pass 1 (kernel mode)
