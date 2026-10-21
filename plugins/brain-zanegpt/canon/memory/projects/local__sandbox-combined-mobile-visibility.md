# local/sandbox-combined-mobile-visibility — lessons

Project: local/sandbox-combined-mobile-visibility. Newest first.

---

## E1 — mobile hidden state is not viewport visibility
- Date: 2026-07-13
- Project: local/sandbox-combined-mobile-visibility
- Tags: [mobile][ui][browser][testing][gamedev]
- What: Checking that mutually exclusive mobile control clusters have the right hidden classes does not prove the active cluster is visible. A `100vh` layout can put bottom-anchored controls below the real mobile visual viewport while headless/no-chrome geometry and hidden-state assertions both pass.
- Why built: `brain train` selected the high-value untested seam `dog + the-game-wrong-sky`. The interaction claim was that dog#E25's mobile co-active-state testing needs actual geometry/visibility evidence, because wrong-sky#E7's `100vh` mobile chrome failure can make a correctly selected control cluster disappear below the fold in a way headless tests do not model.
- Design: Built `sandbox-mobile-vh-visibility.js`, a deterministic geometry model with: - A 64px bottom control cluster and 16px bottom margin. - A headless/no-mobile-chrome case where layout and visual viewport are both 800px. - A mobile-chrome case where the layout viewport remains 800px but the visual viewport is 700px. - A `100vh` layout path that sizes from the layout viewport. - A `100dvh` layout path that sizes from the visual viewport. - Hidden-state checks separated from visible-pixel checks.
- Got right: The sandbox keeps state correctness and viewport visibility as separate measurements. That makes it clear why class assertions and headless screenshots can both miss a real device failure.
- Where/why it failed: In the mobile-chrome `100vh` case, the active prompt cluster's hidden-state check passed, but its box was positioned from 720px to 784px while the visual viewport ended at 700px. It had 0 visible pixels. The same `100vh` geometry was fully visible in the headless/no-chrome case, so headless geometry alone would falsely pass.
- Fix: Use `100dvh`/`100dvw` with `vh`/`vw` fallbacks for mobile viewport-sized game UI, and verify bottom-anchored controls by visible geometry in the co-active state, not only by hidden classes. Treat headless-green/mobile-broken reports as a signal to model or inspect the visual viewport explicitly.
- Why this fix: With `100dvh` under the same mobile visual viewport, the control box moved to 620px-684px and had all 64 pixels visible while the hidden-state check still passed. That proves the missing evidence was viewport visibility, not cluster selection.
- Rule of thumb: For mobile game controls, "the right cluster is not hidden" is not enough. Assert that the active cluster's bounding box intersects the visual viewport, especially for bottom-anchored UI and `vh`-sized canvases.
- Provenance (verified/assumed): Verified first-hand on 2026-07-13 by running `node sandbox-mobile-vh-visibility.js` in `C:\Users\Kompooter\Documents\Brain`. Observed: headless/no mobile chrome with `100vh` = hidden state passes, 64 visible pixels, fully visible; mobile chrome showing with `100vh` = hidden state passes, 0 visible pixels, not fully visible; mobile chrome showing with `100dvh` = hidden state passes, 64 visible pixels, fully visible.
- Composed: dog/E25, the-game-wrong-sky/E7
- Link: Sandbox: `sandbox-mobile-vh-visibility.js`

