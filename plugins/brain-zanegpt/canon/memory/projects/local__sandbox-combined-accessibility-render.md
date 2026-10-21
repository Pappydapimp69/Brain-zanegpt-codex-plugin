# local/sandbox-combined-accessibility-render — lessons

Project: local/sandbox-combined-accessibility-render. Newest first.

---

## E2 — combined accessibility hue locked retrofit needs real check
- Date: 2026-07-13
- Project: local/sandbox-combined-accessibility-render
- Tags: [accessibility][gamedev]
- What: Combined a "retrofit a locked-hue palette to be CVD-safe by
  adjusting luminance only" kernel with the actual CVD-simulation
  two-pass check. Approving retrofit candidates by comparing raw lightness
  values against a flat "15 points of separation" rule of thumb passed
  cases that the real CVD-simulation check rejected — some locked hues
  needed roughly 25-30 raw lightness points of separation, not 15, because
  lightness doesn't map linearly or hue-independently onto CVD-simulated
  luminance.
- Why built: The 15-point rule of thumb is a fast, cheap approximation
  meant to avoid running the full CVD-simulation matrices on every
  candidate value during iteration — this combined test specifically
  checked whether the shortcut and the real check agree.
- Design: Took entity pairs with locked (unchangeable) hues and swept
  luminance-only retrofit candidates, comparing pass/fail under the flat
  15-point raw-lightness threshold against pass/fail under the actual
  protanopia/deuteranopia/tritanopia simulation matrices, across multiple
  different hue pairs.
- Got right: The 15-point heuristic is a reasonable, fast filter for SOME
  hues — it wasn't uniformly wrong, which is exactly what made it
  dangerous: it looked validated by the hues where it happened to agree
  with the real check.
- Where/why it failed: CVD simulation matrices don't apply a uniform
  luminance transform across all hues — the perceptual luminance a locked
  hue needs under a specific CVD simulation is hue-dependent, so a single
  flat raw-lightness threshold is only correct for the hue(s) it happened
  to be calibrated against. Different hues required meaningfully more
  separation (measured ~25-30 points vs. the assumed 15) to actually pass
  the real simulation, meaning the flat threshold silently approved
  retrofits that were not actually CVD-safe.
- Fix: Never approve a locked-hue retrofit against the flat threshold
  directly — always run the candidate luminance values through the real
  CVD-simulation two-pass check before accepting them. Additionally: when
  luminance is independently pinned by an unrelated constraint (e.g. UI
  layer/tiering rules) at the same time the hue is locked, verify a
  feasible fix even EXISTS before committing to the "lock hue, adjust
  luminance" approach — there are cases with no achievable luminance-only
  solution.
- Why this fix: The heuristic exists to save the cost of running the real
  check on every candidate, but a heuristic that's only correct for some
  inputs and silently wrong for others is worse than no heuristic — it
  produces false confidence rather than an honest fast-fail. The real
  check is the actual authority; the heuristic can only ever be a
  hint about where to start searching, never a substitute for validation.
- Rule of thumb: Any perceptual-safety heuristic derived by calibrating
  against a subset of cases (a flat raw-value threshold standing in for a
  matrix-based simulation) should be treated as a search hint, not a
  pass/fail gate — always validate the actual candidate against the real
  authoritative check before accepting it, especially when the underlying
  transform (CVD simulation, color space conversion, perceptual mapping)
  is known to be non-uniform across the input's other dimensions (hue,
  in this case). Also check retrofit feasibility explicitly whenever
  multiple independent constraints (locked hue + pinned luminance) stack —
  a fix approach can be structurally infeasible even before you start
  tuning values.
- Provenance (verified/assumed): Verified first-hand — compared the flat
  15-point threshold against the real CVD-simulation matrices across
  multiple locked-hue pairs, measuring the actual required separation at
  roughly 25-30 points for some hues where the real check rejected what
  the heuristic approved, in a combined accessibility-render sandbox
  stacking the palette-retrofit kernel with the CVD-simulation check.
- Link: session (dog-game-continue-oc3xqh); combined-accessibility-render
  sandbox, pass2.js/pass5.js (retrofit-vs-real-check comparison).
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-brain-viz-growth.md#E3 · compatible · no sandbox · Sandbox: `sandbox-brain-viz-color-redundancy.js`; W3C WCAG 2.2 Use of Color: `https://www.w3.org/TR/WCAG22/#use-of-color`; W3C WCAG 2.2 Non-text Contrast: `https://www.w3.org/TR/WCAG22/#non-text-contrast`

## E1 — combined accessibility eased transition midpoint collision
- Date: 2026-07-13
- Project: local/sandbox-combined-accessibility-render
- Tags: [accessibility][gamedev][testing]
- What: Combined a verified CVD-safe hue+luminance-band assignment with an
  eased runtime color/luminance transition (e.g. a highlight or state
  change animating over 300ms). Every entity's START and END colors passed
  the CVD-safety check independently, but sampling the FULL eased
  trajectory frame-by-frame showed a mid-transition state that was fully
  CVD-confusable with a third, unrelated, stationary entity — for 50-74% of
  the 300ms transition (~9-13 frames at 60fps), not a brief flicker.
- Why built: The hue+luminance-band kernel was verified against static
  entity rosters. This combined test specifically asked whether a runtime
  transition between two individually-safe colors is itself always safe,
  since easing curves don't move linearly through perceptual space.
- Design: Built an entity roster with a locked-safe hue/luminance
  assignment, added one entity that transitions its color/luminance via an
  eased curve over 300ms, and ran the full CVD-simulation check at every
  sampled frame of the transition (not just at t=0 and t=1) against every
  other entity in the roster, including normal (non-CVD) vision.
- Got right: The START state and the END state of the transition were each
  individually verified safe against the full roster — checking endpoints
  is not wrong, it's just not sufficient on its own.
- Where/why it failed: An eased trajectory between two safe points is not
  guaranteed to stay safe along the way — easing curves are specifically
  designed to move nonlinearly through their range, and the perceptual/CVD-
  simulated distance between colors doesn't vary linearly with the eased
  parameter either. The two nonlinearities can combine so the trajectory
  passes close to (or through) a third entity's color in CVD-simulated
  space, even though neither endpoint is anywhere near it. This affected
  normal vision too, not only CVD-simulated vision, and the collision
  window was sustained (roughly half to three-quarters of the transition
  duration), not a single-frame glitch a casual look would catch.
- Fix: Sample the entire eased trajectory at ≤1-frame granularity and check
  every sampled point against the full roster (not just t=0/t=1), hard-
  failing on any non-trivial run of consecutive failing frames.
- Why this fix: Endpoint-only verification treats a transition as a
  boolean (safe/unsafe based on two states) when it's actually a continuous
  path that needs the same per-point verification the endpoints got — there
  is no shortcut that infers path-safety from endpoint-safety when the
  interpolation is nonlinear.
- Rule of thumb: Verifying only the START and END states of an animated/
  eased transition is not sufficient for any perceptual-safety property
  (CVD-confusability, contrast, brightness-flash thresholds) — the
  trajectory between them can violate the property even when both
  endpoints individually satisfy it, and the violation window can be
  sustained rather than transient. Any accessibility check on a static
  state must be re-run across the full sampled trajectory of anything that
  animates through that state space, not just at rest.
- Provenance (verified/assumed): Verified first-hand — measured the
  collision window directly at 50-74% of a 300ms transition (~9-13 frames
  at 60fps sampling), confirmed both endpoints independently pass the same
  check that fails mid-transition, and confirmed the effect is present
  under normal vision simulation as well as CVD simulation, in a combined
  accessibility-render sandbox stacking the hue/luminance kernel with an
  eased runtime transition.
- Link: session (dog-game-continue-oc3xqh); combined-accessibility-render
  sandbox, pass3.js/pass4.js (eased-transition trajectory sampling).
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-brain-viz-growth.md#E4 · compatible · no sandbox · Sandbox: `sandbox-brain-viz-transition-palette.js`; related artifacts: `brain-viz.html`, `brain-garden-viz.html`
- Cited-by: 2026-07-18 · projects/local__sandbox-cvd-transition-audit.md#E1 · compatible · no sandbox · this session (brain train, external-research-verified); sandbox scratchpad `cvd-trajectory/engine.mjs` (run twice, byte-identical); sources: Brettel/Vienot/Mollon 1997 JOSA A + 1999 matrix; W3C WCAG relative luminance
