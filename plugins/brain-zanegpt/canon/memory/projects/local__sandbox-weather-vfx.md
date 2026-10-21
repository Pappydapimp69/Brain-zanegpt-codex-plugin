# local/sandbox-weather-vfx — lessons

Project: local/sandbox-weather-vfx. Newest first.

---

## E1 — dom vs canvas weather particles measured
- Date: 2026-07-18
- Project: local/sandbox-weather-vfx
- Tags: [browser][rendering][performance]
- What: Measured, first-hand in a real headless Chromium run, per-frame
  render cost of N animated weather particles (rain/snow-style: falling
  + horizontal drift, position updated every frame) implemented two
  ways — N absolutely-positioned DOM `<div>` elements with
  `style.transform` updated each frame, vs. N circles drawn to a single
  `<canvas>` with `clearRect`+redraw each frame — across particle
  counts 50/150/300/600/1200.
- Why built: `brain train new-domain`, targeting "weather effects in
  browser games" as a genuine coverage gap (`brain query` returned zero
  real hits on weather/rain/snow/fog/particle-system topics, only
  generic rendering-tag noise). "Use canvas, not many DOM nodes, for
  particle-heavy effects" is common real-world practice, but it had
  never been verified first-hand in this system — only ever assumed as
  folklore. `brain train`'s own rule (tension T22): verify with a
  sandbox, never by reasoning/citation alone.
- Design: `perf_test.html` — a self-contained page with two test
  functions, `domTest(n, frames)` and `canvasTest(n, frames)`, both
  updating the SAME per-particle physics (gravity fall + horizontal
  drift, wrap at bottom) driven by a seeded-but-deterministic initial
  scatter (mulberry32, seed fixed, used only to place starting
  positions — not driving the measurement). Each measures wall-clock
  `performance.now()` cost of its own per-frame update+render step over
  90 frames, real `requestAnimationFrame`-paced. `run_perf.js` drives
  this via Playwright against the pre-installed headless Chromium,
  running both implementations back-to-back at each particle count and
  reporting mean/p95/max per-frame cost.
- Got right: kept the exact same underlying particle physics identical
  between the DOM and canvas implementations (only the rendering
  mechanism differs), so the measured difference isolates the render
  approach itself, not incidental differences in the simulation.
- Where/why it failed: N/A — not a bug, a first-hand-measured design
  comparison. Real numbers (mean per-frame ms, this environment):
  n=50: DOM 0.75ms vs canvas 0.57ms (canvas ~1.3x cheaper); n=150: DOM
  1.39ms vs canvas 0.069ms (~20x); n=300: DOM 0.89ms vs canvas 0.10ms
  (~8.7x); n=600: DOM 1.55ms vs canvas 0.15ms (~10.5x); n=1200: DOM
  3.02ms vs canvas 0.23ms (~13.2x). DOM cost grows noticeably with N
  (forced layout/paint scales with element count); canvas cost grows
  far more slowly (a fixed per-frame `clearRect` plus cheap per-particle
  draw calls). One honest anomaly: at n=50, canvas's MAX frame time was
  41.8ms (a one-off JIT/warmup spike) vs DOM's max of only 3.6ms — the
  MEAN/P95 still favor canvas even at n=50, but a cold-start spike is a
  real, observed tail-latency cost canvas can incur that DOM did not
  show at this small scale.
- Fix: N/A — a measured finding, not a bug fix. The practical
  conclusion: for a weather effect with more than roughly 100-150
  simultaneous particles, canvas rendering leaves measurably more frame
  budget (out of a 16.7ms/frame target at 60fps) than one DOM node per
  particle; below ~50 particles the two are closer and DOM's simplicity
  (CSS-driven, no manual redraw loop) may be worth the smaller
  measured cost difference, PROVIDED a cold-start warmup spike is
  acceptable or pre-warmed.
- Why this fix: N/A in the bug sense — recorded so a future project
  making this exact choice has a real, first-hand number instead of
  folklore ("DOM doesn't scale, use canvas") to reason from.
- Rule of thumb: when choosing a rendering approach for a particle-
  heavy ambient effect (weather, sparks, confetti, floating debris),
  measure BOTH the mean/p95 AND the max/tail frame cost at the ACTUAL
  particle count the effect needs, in the ACTUAL target environment —
  DOM-per-particle cost scales with count (layout/paint overhead) while
  a single canvas's cost stays comparatively flat, but canvas can incur
  a real one-off warmup spike a DOM approach may not show at small
  scale. Don't assume the folklore answer's DIRECTION is wrong, but
  don't trust its exact MAGNITUDE without measuring in your own
  environment either — headless/software-rendered (swiftshare-style)
  browsers are a known source of atypical timing (dog#E48), so treat
  the measured ratios as directionally reliable, not as portable exact
  constants across all hardware.
- Provenance (verified/assumed): Verified first-hand — ran
  `run_perf.js` against `perf_test.html` via Playwright + the
  pre-installed headless Chromium, 90 real `requestAnimationFrame`-paced
  frames per test, 5 particle counts, both implementations driven by
  identical underlying physics. Scope limit, stated plainly rather than
  assumed away: this measurement covers the DIRECTIONAL ordering (DOM
  costs more than canvas past ~150 particles) — whether the exact
  millisecond magnitudes transfer to a real GPU-accelerated browser
  outside this headless/software-rendering environment remains an open
  question for a future session to check.
- Composed: N/A
- Link: session 7195397b-63a9-5efe-a80b-2792eaa6645e (`brain train
  new-domain`, weather-effects gap); `scratchpad/weather/perf_test.html`
  + `run_perf.js`
- Cited-by: 2026-10-11 · projects/pappydapimp69__brain.md#E136 · compatible · sandboxes/2026-10-11__weather-layers-one-canvas-per-layer-hits-context-cap.py · observed RESULT: PASS L=5 cap=3: per-layer 3/5 live (0.69ms, cheapest because 2 layers never draw); one canvas 5/5 1.15ms; DOM fallback 5/5 6.73ms; L=3 all layouts 3/3. (The "about the same total" part of the prediction missed: 0.69 vs 1.15 ms.) · brain train auto loop 2 pass 2 (edge); session_01ScEdAr4bK7Pp21fx27MXao
