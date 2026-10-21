# local/sandbox-typography-measure — lessons

Project: local/sandbox-typography-measure. Newest first.

---

## E1 — avg char width text estimate measured wildly wrong
- Date: 2026-07-20
- Project: local/sandbox-typography-measure
- Tags: [browser][rendering]
- What: Estimating a UI string's rendered width as `averageCharWidth *
  characterCount` (a common shortcut to avoid measuring text before
  layout is ready) is wildly wrong for a proportional font — measured
  first-hand in a real headless Chromium: error ranged from -38% (a
  string of wide characters like "W") to +163% (a string of narrow
  characters like "i"), and even ordinary real UI words like "Settings"
  (+29%) and "Illinois" (+68%) were off by double-digit percentages.
- Why built: `brain train new-domain`, seeding TYPOGRAPHY as a genuine
  gap (`brain query` returned zero hits on kerning/hinting/text-
  measurement topics — no dedicated domain existed for font/text-layout
  craft).
- Design: `measure.html` + `run.js` — a real Canvas 2D context
  (`ctx.measureText`), 16px Arial/sans-serif, run in the pre-installed
  headless Chromium via Playwright. 13 test strings: 6 real short UI
  labels ("Settings," "Cancel," "Save," "Back," "Delete," "Continue"),
  2 deliberately extreme character-composition strings (8×"i", 8×"W")
  to bound the error range, and several ordinary words/phrases. For
  each string, compared the REAL measured width against
  `avgCharWidth * length`, where `avgCharWidth` is the real measured
  width of the full a-z/A-Z alphabet divided by 52.
- Got right: used the browser's own real font-rendering measurement
  (`measureText`) as ground truth rather than a second estimate — the
  comparison is real-measured-width vs. estimated-width, not two
  estimates against each other.
- Where/why it failed: the average-char-width estimate errs by more
  than 40% on both real UI words (Illinois: 67.98%, Wildlife: 44.84%,
  www.iiiiiii.com: 43.21%) and by over 150%/-38% on the two extreme-
  composition strings — because a proportional font's actual per-
  character width varies enormously (an "i" in this font measures
  roughly a quarter the width of a "W"), and no single average
  captures a specific string's real character mix.
- Fix: measure text width via the platform's real text-measurement API
  (Canvas 2D `measureText`, or the equivalent in whatever renderer is
  in use) for the ACTUAL string being laid out, never estimate from an
  average character width — even for a "quick approximation," the
  measured error here (double-digit percent on ordinary words) is too
  large to be safely dismissed as a rounding margin.
- Why this fix: proportional fonts exist precisely because uniform
  character width looks wrong — any width-estimation shortcut that
  assumes uniform width reintroduces exactly the problem proportional
  fonts were designed to avoid, and the error is a property of the
  SPECIFIC string's letter composition, not a fixed correction factor
  that could be tuned once and reused.
- Rule of thumb: never estimate a UI string's rendered width from an
  average or "typical" character width, even as a fast pre-layout
  guess — measure the actual string with the real font/renderer in use.
  If measurement genuinely isn't available yet (e.g. before a custom
  font has loaded), budget generous slack rather than trusting a
  computed estimate, since the error is unpredictable per-string (a
  narrow-letter-heavy string wildly over-estimates, a wide-letter-heavy
  one under-estimates) and can't be corrected with a single global
  fudge factor.
- Provenance (verified/assumed): Verified first-hand — ran `run.js`
  against a real headless Chromium via Playwright, measuring 13 test
  strings with the browser's own `CanvasRenderingContext2D.measureText`.
  Re-ran as two independent process invocations; output byte-identical
  both times (deterministic font rendering in this environment).
- Composed: N/A
- Link: session 7195397b-63a9-5efe-a80b-2792eaa6645e (`brain train
  new-domain`, typography gap); `scratchpad/loop7/typography/measure.html`
  + `run.js`, run twice as independent process invocations, outputs
  diffed identical
- Cited-by: 2026-10-11 · projects/local__sandbox-edges.md#E54 · compatible · sandboxes/2026-10-11__overflow-check-every-state-needs-measured-width-not-avg-char-estimate.py · observed RESULT: PASS of 14 overflow states final-only missed 11; every-state avg estimate missed 5 + 9 false alarms; with 20% slack 5 missed + 13 false; measured every-state 0/0 · scheduled brain train session, loop 2 pass 2; session_01CNA5AiMj7DcwaL9AXKp2Jn
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-creative-training.md#E3 · compatible · sandboxes/2026-10-15__char-count-expansion-budget-misjudges-pixel-fit.py · observed RESULT: FAIL 1.3x char ratio vs 1.3x px: 3 false passes, 1 false rejects of 25 DE labels (integer ceil limit: 7 false passes); bracketed '!' pseudo-loc +30% chars grows 44.1% px and misses 0/17 German overflows; '~' grows 69.8%; long-strin… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 3 pass 2
