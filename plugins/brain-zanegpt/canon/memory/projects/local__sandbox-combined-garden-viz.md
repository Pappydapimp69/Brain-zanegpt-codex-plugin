# local/sandbox-combined-garden-viz — lessons

Project: local/sandbox-combined-garden-viz. Newest first.

---

## E9 — garden viz reveal schedule needs integer time and size aware pacing
- Date: 2026-07-13
- Project: local/sandbox-combined-garden-viz
- Tags: [viz][growth-visualization][determinism][animation][testing]
- What: A Brain garden visualization reveal schedule can fail two different ways at once: a frame-driven scheduler that discards overshoot reveals different sprout counts at different frame rates, and a flat per-batch duration makes large growth batches flash by instead of reading as a crescendo.
- Why built: The requested target was `brain Viz garden schedule`. The interaction claim was that Brain's garden/growth visualization pacing lesson needs the deterministic fixed-timestep scheduling discipline: batch pacing controls how growth feels, but the reveal clock itself must be on an integer drain schedule or equal wall-clock durations produce different visible garden states.
- Design: Built `sandbox-garden-viz-schedule.js`, a deterministic JavaScript model with: - Garden reveal batch sizes `[1, 4, 16, 64]`. - A bad scheduler that advances at most one tick per frame and discards overshoot. - A fixed scheduler that drains an integer millisecond accumulator. - Equal 1000ms frame schedules at 60fps and 30fps. - Flat per-batch pacing and `sqrt(n)` batch pacing. - Per-batch tick-span measurements for sprout legibility.
- Got right: The sandbox separates clock determinism from animation pacing. The same model proves that a stable tick count and a readable growth cadence are separate requirements.
- Where/why it failed: With the overshoot-discarding scheduler and flat pacing, the 60fps schedule revealed 31 sprouts while the 30fps schedule revealed only 4 over the same 1000ms wall time. Flat pacing also gave the 64-sprout batch only `0.313` ticks per sprout, making the largest batch the least legible.
- Fix: Drive the reveal from an integer/fixed-point accumulator that drains all due ticks, and allocate batch reveal budgets sub-linearly with size, such as `sqrt(n)`, rather than giving every batch the same duration.
- Why this fix: The integer-drain scheduler revealed the same count at 60fps and 30fps: 6 vs 6. The `sqrt(n)` pacing raised the 64-sprout batch from `0.313` ticks per sprout under flat pacing to `2.469`, preserving a visible crescendo without making duration scale linearly.
- Rule of thumb: For growth visualizations, use integer time for "how many events should exist by now" and size-aware pacing for "how should the batch feel." A beautiful garden layout still needs a deterministic reveal clock.
- Provenance (verified/assumed): Verified first-hand on 2026-07-13 by running `node sandbox-garden-viz-schedule.js` in `C:\Users\Kompooter\Documents\Brain`. Observed: float reset + flat pacing at 60fps revealed 31/85 sprouts; float reset + flat pacing at 30fps revealed 4/85; integer drain + sqrt pacing revealed 6/85 at both 60fps and 30fps. Flat pacing tick-per-sprout for the 64 batch was `0.313`; sqrt pacing raised it to `2.469`.
- Composed: brain/E5, sandbox-combined-game-loop/E2
- Link: Sandbox: `sandbox-garden-viz-schedule.js`; related local artifact: `brain-garden-viz.html`
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E47 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E8 — garden sqrt reveal pacing
- Date: 2026-07-13
- Project: local/sandbox-combined-garden-viz
- Tags: [viz][animation][growth-visualization][pacing][testing]
- What: For a Brain Viz garden, simultaneous growth batches should not all receive the same animation duration. A flat duration makes a 256-node batch read as a flash, while linear duration makes large batches drag. A square-root duration gives visible scale without making large updates unusably slow.
- Why built: The prior Brain lesson said flat event batches erase magnitude. This loop re-tested that rule specifically for a garden-style Brain Viz where new lessons may arrive in uneven bursts.
- Design: The sandbox compared reveal timings for batches `[4, 16, 64, 256]` under flat, linear, and square-root schedules. It measured the ratio between fastest and slowest reveal rates. External research was used only to ground the value of animated transitions for helping viewers track changing graphics; the timing law itself was sandboxed.
- Got right: Flat `2s` timing produced a `64x` rate swing from small to large batches. Linear timing produced a `1x` rate swing but made the 256-node batch take `32s`. Square-root timing produced durations `[1.3, 2.6, 5.2, 10.4]` and an `8x` rate swing: enough for scale to be felt, but not a flash or a long stall.
- Where/why it failed: The naive "make animation smooth" rule is underspecified. Smooth flat timing hides magnitude. Linear timing preserves constant per-node rate but punishes users for large growth events.
- Fix: Set reveal duration proportional to `sqrt(batchSize)`, then cap it for product-specific patience. Keep small and medium batch tests in the suite so a large-batch fix does not regress ordinary updates.
- Why this fix: Square-root timing is sub-linear: larger batches take longer, so the user feels growth, but the time cost grows slower than the event count.
- Rule of thumb: When a visualization animates bursts, duration should communicate magnitude without charging one second per item. Start with square-root scaling and test the small, medium, and large cases.
- Provenance (verified/assumed): Verified first-hand in `scripts/brain-viz-garden-training.mjs` on 2026-07-13. External check: Heer and Robertson's "Animated Transitions in Statistical Data Graphics" reports that appropriately designed animated transitions can improve graphical perception: https://idl.uw.edu/papers/animated-transitions.
- Composed: brain/E5, sandbox-graph-viz/E4
- Link: `scripts/brain-viz-garden-training.mjs`

## E7 — garden phyllotaxis packing
- Date: 2026-07-13
- Project: local/sandbox-combined-garden-viz
- Tags: [viz][growth-visualization][garden][layout][testing]
- What: For a Brain Viz garden, placing new memory nodes by birth-order phyllotaxis produces a more even field than spokes or seeded random orbit placement. The layout still needs a separate overlap pass for large labels, but phyllotaxis is the better first placement for "growth from a center."
- Why built: The user asked for five Brain training loops combining Brain Viz, garden metaphor, external research, and sandbox verification. This loop tested whether "garden growth" should be a real spatial rule or just decorative language.
- Design: `scripts/brain-viz-garden-training.mjs` generated 240 nodes with three deterministic strategies: golden-angle phyllotaxis, 8-spoke radial placement, and seeded random orbit placement. It measured nearest-neighbor coefficient of variation and rectangle overlaps. External research checked that the golden angle is a real phyllotaxis pattern, not an invented visual trope.
- Got right: The phyllotaxis field had nearest-distance CV `0.040`, compared with `0.513` for spokes and `0.563` for seeded random. It also reduced raw overlap pressure compared with spokes: `385` overlaps vs `1016`.
- Where/why it failed: Phyllotaxis did not solve label collisions by itself. With the modeled label rectangles it still had `385` overlaps. So the correct lesson is not "phyllotaxis solves layout"; it is "phyllotaxis gives the growth field a strong first distribution before a label/clearance pass."
- Fix: Use phyllotaxis as the first placement pass for garden-growth memory nodes, then run a separate overlap-removal pass for visible labels and large marks.
- Why this fix: The first pass controls the visual metaphor and spatial uniformity. The second pass controls readability. Combining them keeps the garden metaphor honest without pretending biology solves UI labels.
- Rule of thumb: If the visual claim is "knowledge grows," make growth order spatially meaningful. Use golden-angle phyllotaxis for the birth-order field, but reserve collision freedom for a separate readability pass.
- Provenance (verified/assumed): Verified first-hand in `scripts/brain-viz-garden-training.mjs` on 2026-07-13. External check: Okabe, "Biophysical optimality of the golden angle in phyllotaxis," Scientific Reports, reports the golden angle around 137.5 degrees as a common phyllotactic divergence and models its adaptive optimality: https://www.nature.com/articles/srep15358. Fowler, Hanan, and Prusinkiewicz's "Modelling Spiral Phyllotaxis" uses geometric phyllotaxis models to generate plant-like spiral patterns: https://algorithmicbotany.org/papers/modelling-spiral-phyllotaxis.pdf.
- Composed: sandbox-graph-viz/E3, brain/E5
- Link: `scripts/brain-viz-garden-training.mjs`

## E6 — garden overlap postprocess
- Date: 2026-07-13
- Project: local/sandbox-combined-garden-viz
- Tags: [viz][graph][layout][readability][testing]
- What: Even a good growth placement can fail as a readable visualization once labels enter the system. A Brain Viz garden should treat overlap removal as a separate post-process, not as a property of the growth algorithm.
- Why built: The phyllotaxis loop showed strong spacing but still had label overlaps. This loop isolated the label-readability problem and tested whether a simple clearance walk could remove collisions after placement.
- Design: The sandbox generated 180 phyllotaxis label rectangles, counted collisions, then applied a deterministic radial clearance walk that pushes a label outward until it no longer overlaps already placed labels.
- Got right: Before the post-process, the label field had `1569` overlaps. After the clearance walk, overlaps dropped to `0`. The radius grew by `3.413x`, making the tradeoff explicit: readability costs space.
- Where/why it failed: If overlap removal is folded into the growth placement itself, the code can hide a real tradeoff. A beautiful compact garden and a readable labeled garden are different objectives.
- Fix: Run layout in two phases: first place by semantic/growth rule, then remove overlaps with an explicit readability pass. Measure both collision count and radius growth.
- Why this fix: Separating the phases keeps the metaphor and the usability constraint from pretending to be the same thing. It also makes the cost of readability measurable.
- Rule of thumb: Do not ask the growth algorithm to also be the label layout algorithm. Semantic placement first; readability repair second.
- Provenance (verified/assumed): Verified first-hand in `scripts/brain-viz-garden-training.mjs` on 2026-07-13. External check: Dunne and Shneiderman's graph readability work frames readability as something that can be assessed through graph drawing metrics, including structural properties such as crossings and readability problems: https://www.cs.umd.edu/~ben/papers/Dunne2009Improving.pdf.
- Composed: sandbox-graph-viz/E3, sandbox-combined-graph-editor/E2
- Link: `scripts/brain-viz-garden-training.mjs`

## E5 — garden live camera clamp
- Date: 2026-07-13
- Project: local/sandbox-combined-garden-viz
- Tags: [viz][camera][growth-visualization][mobile][testing]
- What: A progress-based camera schedule is not enough for a growing Brain Viz garden. If node positions are procedural, a day/progress zoom can leave live content offscreen, especially on mobile. The camera must clamp every frame against the actual extents of visible content.
- Why built: The prior Brain lesson warned that progress-driven camera schedules miss procedurally positioned content. This loop retested that rule against a garden layout with phyllotaxis growth and mobile aspect ratios.
- Design: The sandbox generated phyllotaxis nodes for days `[12, 48, 96, 192, 305]` and tested three aspect ratios: mobile portrait `0.56`, square `1`, and wide `1.78`. It compared a scheduled zoom against a live extent clamp computed from actual node bounds.
- Got right: The scheduled camera produced `685` total offscreen nodes across the sweep, with a worst case of `198` offscreen nodes at the 305-node mobile portrait state. The live clamp produced `0` offscreen nodes in every tested aspect/day combination.
- Where/why it failed: The schedule failed because "how far along the story is" is not the same as "how large the current drawing is." Procedural placement can create wider extents earlier or later than the camera schedule expects.
- Fix: Compute the visible content bounds every frame or every growth step, then clamp zoom and pan to those live bounds. Keep the progress schedule only as a preferred camera, not as the safety constraint.
- Why this fix: The clamp uses the true current geometry, so it adapts to growth count, aspect ratio, label size, and layout spread. It handles the state the user actually sees rather than the state the timeline assumes.
- Rule of thumb: In a procedural growth visualization, progress can suggest a camera, but live geometry must veto it.
- Provenance (verified/assumed): Verified first-hand in `scripts/brain-viz-garden-training.mjs` on 2026-07-13. External context came from the same phyllotaxis literature used for the growth placement: https://www.nature.com/articles/srep15358 and https://algorithmicbotany.org/papers/modelling-spiral-phyllotaxis.pdf.
- Composed: brain/E4, sandbox-graph-viz/E3
- Link: `scripts/brain-viz-garden-training.mjs`
- Cited-by: 2026-09-29 · projects/local__sandbox-garden-viz-dog-nan-node-poisons-smoothed-camera.md#E1 · compatible · no sandbox · session_01AJo9NVvaQuzD3JbJDk6P3B

## E4 — garden groups need explicit rank pull
- Date: 2026-07-13
- Project: local/sandbox-combined-garden-viz
- Tags: [viz][graph][layout][growth-visualization][testing]
- What: A stable force/layout position is not evidence that garden groups appear in their intended schedule order. If group order matters, the layout needs an explicit rank/group pull rather than relying on emergent spatial positions.
- Why built: The training target was `garden viz sandbox combination groups`. The interaction claim was that graph-viz's stable-layout lessons compose with Brain's garden schedule/group visualization: stability prevents NaN/drift, but it does not encode semantic order. A scheduled sequence of garden groups needs an explicit spatial ordering force.
- Design: Built `sandbox-garden-group-rank-pull.js`, a deterministic model with: - Four scheduled garden groups: `soil`, `water`, `pest`, `harvest`. - Two nodes per group. - Stable pre-existing x positions that cluster members but do not match schedule order. - A rank-pull transform that assigns each group a target x band based on schedule rank. - Inversion count as the order metric.
- Got right: The sandbox distinguishes "group members are stably near each other" from "groups are arranged in schedule order." Those are different layout guarantees.
- Where/why it failed: Stable force positions produced order `pest,soil,harvest,water` against expected `soil,water,pest,harvest`, with 3 inversions. The layout was stable but semantically scrambled.
- Fix: When a garden visualization has a meaningful group schedule, add an explicit rank/group pull or banding term to the layout. Use force simulation for local spacing, not as the source of semantic ordering.
- Why this fix: The explicit rank pull produced order `soil,water,pest,harvest` with 0 inversions. It preserved the schedule order directly instead of hoping stable positions correlated with it.
- Rule of thumb: Stable layout is not ordered layout. If a visual schedule has semantic group order, encode that order as a layout constraint.
- Provenance (verified/assumed): Verified first-hand on 2026-07-13 by running `node sandbox-garden-group-rank-pull.js` in `C:\Users\Kompooter\Documents\Brain`. Observed: stable force positions only = order `pest,soil,harvest,water`, expected `soil,water,pest,harvest`, 3 inversions; explicit group rank pull = expected order, 0 inversions.
- Composed: sandbox-graph-viz/E3, sandbox-combined-skilltree-formula/E4
- Link: Sandbox: `sandbox-garden-group-rank-pull.js`; related artifact: `brain-garden-viz.html`

## E3 — garden group schedule needs eof safe parser
- Date: 2026-07-13
- Project: local/sandbox-combined-garden-viz
- Tags: [viz][tooling][parsing][schedule][testing]
- What: A garden visualization schedule built from parsed groups can silently omit the final group if the parser only flushes a block on blank lines or new headers and forgets EOF. The schedule then looks valid but is built from incomplete input.
- Why built: The training target was `garden viz sandbox combination groups`. The interaction claim was that Brain's block-parser lesson composes with garden group scheduling: before tuning reveal timing or layout groups, verify that every source group actually reaches the schedule.
- Design: Built `sandbox-garden-group-parser-schedule.js`, a deterministic model with: - Three garden groups: `soil`, `water`, and final EOF-terminated `pest`. - A buggy parser that flushes only on blank lines. - A fixed parser that routes new headers, blank lines, and EOF through one shared flush function. - A group schedule generated from the parsed groups.
- Got right: The sandbox measures schedule output, not just parser internals. That catches the user-visible consequence: the final garden group never gets a reveal slot.
- Where/why it failed: The buggy parser returned only 2 groups and scheduled `soil,water`; `pest` was dropped because the file ended without a blank line. The fixed parser returned 3 groups and scheduled `soil,water,pest`.
- Fix: Use one flush function for every block-ending condition, including EOF, and cross-check parsed group count against an independent source count before constructing schedule data.
- Why this fix: The shared-flush parser scheduled the EOF-terminated final group. The schedule no longer depended on whether the source file ended with a blank line.
- Rule of thumb: Before debugging garden group pacing, prove the group parser is complete. A schedule over missing groups can look orderly while silently hiding content.
- Provenance (verified/assumed): Verified first-hand on 2026-07-13 by running `node sandbox-garden-group-parser-schedule.js` in `C:\Users\Kompooter\Documents\Brain`. Observed: buggy blank-line-only flush = 2 groups, scheduled `soil,water`, final group scheduled `false`; fixed shared flush incl EOF = 3 groups, scheduled `soil,water,pest`, final group scheduled `true`.
- Composed: brain/E3, brain/E5
- Link: Sandbox: `sandbox-garden-group-parser-schedule.js`; related artifact: `brain-garden-viz.html`

## E2 — garden confidence frontier
- Date: 2026-07-13
- Project: local/sandbox-combined-garden-viz
- Tags: [viz][graph][process][testing][knowledge-management]
- What: In a Brain Viz, raw co-verification edge count can make a large, loose cluster look more trustworthy than a smaller, better-confirmed cluster. Confidence needs to include independence and density, while untested seams should be shown as frontier pressure rather than hidden backlog.
- Why built: Brain's current analysis reports a large group with many edges but low independence, and a small pathfinding group with much higher density and independence. This loop tested whether raw edge count and confidence ranking disagree.
- Design: The sandbox modeled the current Brain group summary: a large working-memory group with `53` systems, `135/1378` edges, `20` independent edges, and `1088` seams; and a small pathfinding group with `6` systems, `12/15` edges, `6` independent edges, and `74` seams. It computed density, independence ratio, confidence as `sqrt(density * independence)`, and frontier pressure as seams per edge.
- Got right: Raw edge count selected `large-working-memory` as the leader. Confidence selected `small-pathfinding`. The large group had density `0.098`, independence `0.148`, confidence `0.120`, and frontier pressure `8.059`. The small group had density `0.800`, independence `0.500`, confidence `0.632`, and frontier pressure `6.167`.
- Where/why it failed: A graph view that sizes or ranks by edge count alone rewards coverage before trust. That is useful for aiming training, but misleading if read as certainty.
- Fix: Render three different quantities separately: raw edges as coverage, independence-adjusted confidence as trust, and seams-per-edge as frontier pressure. Do not collapse them into one "importance" mark.
- Why this fix: Coverage, trust, and frontier are different decisions. Coverage says where the system has worked. Trust says what is independently supported. Frontier pressure says where training should go next.
- Rule of thumb: In a knowledge graph visualization, edge count is not confidence. Show independence and untested seams beside it or the biggest cluster will look more proven than it is.
- Provenance (verified/assumed): Verified first-hand in `scripts/brain-viz-garden-training.mjs` on 2026-07-13 using `brain analyze groups` and `brain analyze seams` values from this session. External graph readability context: Dunne and Shneiderman, "Improving Graph Drawing Readability by Incorporating Readability Metrics": https://www.cs.umd.edu/~ben/papers/Dunne2009Improving.pdf.
- Composed: sandbox-graph-viz/E4, brain/E6
- Link: `scripts/brain-viz-garden-training.mjs`
- Cited-by: 2026-08-11 · projects/pappydapimp69__august-10.md#E14 · compatible · no sandbox · August-10 sandboxes/loop05_div_counts_sources_not_assumptions.py — bears directly on open tension T20

## E1 — garden camera needs finite live extents and center
- Date: 2026-07-13
- Project: local/sandbox-combined-garden-viz
- Tags: [viz][growth-visualization][graph][camera][testing]
- What: A garden/graph visualization camera cannot rely on a progress-only zoom schedule. It must compute finite live extents and center on them; scale alone does not fit off-center procedural content, and non-finite layout nodes must be excluded before computing the camera.
- Why built: The training target was `garden viz sandbox combination groups`. The interaction claim was that Brain's garden camera lesson composes with graph-viz's layout stability lesson: a layout can contain far/outlying or non-finite nodes, so the camera schedule has to be derived from currently live, finite geometry rather than from progress alone.
- Design: Built `sandbox-garden-camera-live-extents.js`, a deterministic model with: - Four finite garden nodes, including an outer node born at tick 3. - One NaN layout node representing force-layout contamination. - Wide and portrait viewports. - A progress-only camera fixed at origin. - A finite-live-extent camera that filters non-finite nodes, computes extents, centers on them, and clamps scale.
- Got right: The sandbox separates zoom, center, aspect ratio, and finite guards. That catches the case where a schedule happens to fit wide screens but clips on portrait.
- Where/why it failed: At tick 3, the progress schedule showed all 4 finite nodes in the wide viewport but only 3/4 in portrait. The finite live extent camera showed 4/4 in both wide and portrait. The failed first sandbox iteration also exposed that scale-only fitting is insufficient without recentering.
- Fix: For every draw/reveal frame, filter to finite live nodes, compute the current bounding box, center the camera on that box, and clamp scale against the active viewport. Treat non-finite layout output as invalid geometry for camera fitting.
- Why this fix: The finite-live camera fit every finite live node in both tested aspect ratios: wide 4/4 and portrait 4/4. The progress schedule fit wide by luck but clipped portrait, proving a schedule does not know the current geometry.
- Rule of thumb: A growth visualization camera should follow live extents, not narrative progress. Compute center and scale from finite visible content every frame.
- Provenance (verified/assumed): Verified first-hand on 2026-07-13 by running `node sandbox-garden-camera-live-extents.js` in `C:\Users\Kompooter\Documents\Brain`. Observed: progress schedule = wide 4/4 visible, portrait 3/4 visible; finite live extent clamp = wide 4/4 visible, portrait 4/4 visible.
- Composed: brain/E4, sandbox-graph-viz/E3
- Link: Sandbox: `sandbox-garden-camera-live-extents.js`; related artifact: `brain-garden-viz.html`
- Cited-by: 2026-10-01 · projects/local__sandbox-combined-brain-viz-growth.md#E14 · compatible · no sandbox · https://claude.ai/code/session_01PgH3HZiwHdwLMt5FmTr1rn
- Cited-by: 2026-09-29 · projects/local__sandbox-garden-viz-dog-nan-node-poisons-smoothed-camera.md#E1 · compatible · no sandbox · session_01AJo9NVvaQuzD3JbJDk6P3B
