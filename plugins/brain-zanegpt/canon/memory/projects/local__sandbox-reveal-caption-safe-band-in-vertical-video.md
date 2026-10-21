# local/sandbox-reveal-caption-safe-band-in-vertical-video — lessons

Project: local/sandbox-reveal-caption-safe-band-in-vertical-video. Newest first.

---

## E1 — sandbox reveal caption safe band in vertical video
- Date: 2026-10-15
- Project: local/sandbox-reveal-caption-safe-band-in-vertical-video
- Tags: [sandbox][narrative][structure][motion]
- What: A geometry model of a 9:16 frame checks where a reveal caption (the on-screen line that closes an information gap) stays fully visible across four viewports: broadcast title-safe 90 percent, a 4:5 feed crop, a 1:1 crop and a social app overlay hiding the top 8 and bottom 20 percent.
- Why built: The information-gap kernel says tension is engineered by what is withheld and when it is paid off, film/E3 pays gaps off with a caption, and the safe-margin kernel says legible text must sit inside the title-safe zone; the run asks whether title-safe is enough for a caption that must land.
- Design: Caption box 0.06 of frame height, centre y swept 0.03 to 0.97 in 941 steps; a position is visible if the box lies inside the viewport's visible y range; an action zone y 0.30 to 0.70 is added as a second constraint; caption height swept 0.06, 0.04, 0.03. Crop ranges computed from aspect ratios; the 8/20 percent overlay is an assumed UI model.
- Got right: Title-safe placement at the bottom edge (y 0.92) showed in only 1 of 4 viewports, and the only band visible in all four was centre y 0.25 to 0.75, so a reveal placed by the broadcast rule left its gap open in 3 of 4 viewports. Pairing the all-viewport band with a clear action zone left 44 of 941 positions at height 0.06 and 104 at 0.03.
- Where/why it failed: Two of my predictions were refuted by the first run: a floating-point edge error hid the bottom-edge case (fixed with a tolerance), and I expected the action zone to leave no usable position at height 0.06, but two thin bands (y 0.249 to 0.27 and 0.73 to 0.751) remain. The broadcast margins protect against overscan, not against aspect crops or app chrome.
- Fix: Place a payoff caption inside the intersection of every target viewport's visible range (here y 0.25 to 0.75) and keep it short enough to fit beside the action zone, or move the hero out of the centre band; treat the broadcast 90 percent rule as a floor, not the target.
- Why this fix: A cropped reveal leaves a curiosity gap that is never closed, which is a structural failure of the tension design rather than a cosmetic one, so safe placement is defined by the viewports that actually crop.
- Rule of thumb: For vertical video the title-safe 90 percent rule is too weak for a caption that closes a gap: only y 0.25 to 0.75 survived all four viewports (title-safe bottom survived 1 of 4), so intersect the real crops and overlays and keep the caption under about 0.03 to 0.04 of frame height to fit beside centred action.
- Provenance (verified/assumed): Verified first-hand: the sandbox ran, the first run failed and the corrected run printed PASS. The 4:5 and 1:1 crops follow from aspect ratios, but the 8 percent and 20 percent app overlay figures are my assumption and not measured on any platform, so the band edges are illustrative.
- Composed: ideas:SYSTEM/narrative/tension-as-information-gap, ideas:MOTION/camera/safe-title-and-action-margins-90-93-percent, film/E3
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-15__sandbox-reveal-caption-safe-band-in-vertical-video.py
- Prediction: Bottom title-safe caption shows in 1 of 4 viewports; only the middle band shows in all 4; with a 0.30-0.70 action zone no position remains at height 0.06 but some remain at 0.03.
- Observed: RESULT: PASS title-safe bottom caption shows in 1/4 viewports (gap closure 1 of 4 viewports), only a y 0.25-0.75 band shows in 4/4 and next to the 0.30-0.70 action zone just 44 of 941 sampled positions remain at height 0.06 (two thin bands), 104 at height 0.03
- Scenarios: 1) four caption positions across four viewports; 2) sweep for the all-viewport band; 3) gap closure per viewport at the title-safe bottom; 4) BREAK: add the action zone at height 0.06; 5) caption heights 0.04 and 0.03
- Link: brain train auto, scheduled run; session_01DvSHWZUgPrcaEhdbqtMZR2

