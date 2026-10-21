# local/sandbox-localization-expansion — lessons

Project: local/sandbox-localization-expansion. Newest first.

---

## E1 — german text expansion overflows fixed width buttons
- Date: 2026-07-20
- Project: local/sandbox-localization-expansion
- Tags: [browser][rendering]
- What: Real English UI labels translated to German average ~31%
  wider when rendered (measured first-hand: -28% to +98% per string,
  8 real word pairs), matching the commonly-cited i18n guidance figure
  (German text typically runs 20-35% longer than English) — and a
  plausible fixed-width button sized to fit the English label overflows
  for at least one real translated label ("Settings"→"Einstellungen",
  66% wider, exceeding a 90px button).
- Why built: `brain train new-domain`, seeding LOCALIZATION as a
  genuine gap (`brain query` returned zero hits on text-expansion/i18n-
  layout topics specifically).
- Design: `measure.html` + `run.js` — a real Canvas 2D
  `measureText`, 16px Arial/sans-serif, in the pre-installed headless
  Chromium via Playwright. 8 real English/German UI-label pairs
  (Settings/Einstellungen, Save/Speichern, Cancel/Abbrechen,
  Back/Zurück, Continue/Weiter, Delete/Löschen, Language/Sprache,
  Search/Suchen) — real, commonly-used translations, not invented
  strings. Measured each pair's real rendered width and expansion
  percentage, and checked each German label against a plausible fixed
  button width (90px, sized to comfortably fit most of the English
  labels).
- Got right: used REAL word-pair translations (not synthetic/inflated
  test strings) so the measured expansion is representative of an
  actual localization pass, not an artificially extreme case.
- Where/why it failed: per-pair expansion ranged from -28.28%
  ("Language"→"Sprache," actually shorter) to +97.56%
  ("Save"→"Speichern," nearly double), averaging +31.23% across the 8
  pairs — consistent with commonly-cited localization guidance that
  German runs roughly 20-35% longer than English on average, but with
  real per-word variance wide enough that no single pair reliably
  represents the average. One label ("Einstellungen," 96.07px)
  overflowed the fixed 90px button width that comfortably fit 7 of the
  8 English originals.
- Fix: never size a UI container (button, label, nav item) to fit only
  the SOURCE-LANGUAGE text with a small fixed margin — either measure
  the actual translated string for every locale the product ships (as
  this sandbox did) and size containers to the widest real translation,
  or use a layout that can genuinely reflow/wrap/shrink text rather
  than a fixed pixel width, and test that reflow with real translated
  strings, not the original English.
- Why this fix: expansion isn't a uniform percentage you can budget
  once — the per-word variance here (-28% to +98%) means a single
  "add 30% padding" rule both under-protects the worst cases (Save→
  Speichern needed ~98% more room) and over-pads the cases that
  actually got shorter (Language→Sprache), so real translated strings
  need to be measured, not estimated from an average expansion factor.
- Rule of thumb: any fixed-width UI element sized to fit source-
  language (typically English) text must be verified against the
  ACTUAL translated strings for every shipped locale before launch —
  German alone showed real per-string expansion ranging from -28% to
  +98% in this measurement, so neither "it fit in English" nor "budget
  30% extra everywhere" is a safe substitute for measuring the real
  translated content the way this sandbox did.
- Provenance (verified/assumed): Verified first-hand — ran `run.js`
  against a real headless Chromium via Playwright, measuring 8 real
  English/German UI-label pairs with `CanvasRenderingContext2D.
  measureText`. Re-ran as two independent process invocations; output
  byte-identical both times (deterministic font rendering in this
  environment). The translations themselves are real, commonly-known
  German equivalents of common UI terms, not independently fact-
  checked against a dictionary in this session — flagged as the one
  externally-assumed (not independently re-verified) input.
- Composed: N/A
- Link: session 7195397b-63a9-5efe-a80b-2792eaa6645e (`brain train
  new-domain`, localization gap); `scratchpad/loop7/localization/
  measure.html` + `run.js`, run twice as independent process
  invocations, outputs diffed identical
- Cited-by: 2026-10-11 · projects/local__sandbox-edges.md#E53 · compatible · sandboxes/2026-10-11__canvas-label-fit-expansion-headroom-and-font-reset-on-resize.py · observed RESULT: PASS EN box 84px overflows 3 DE labels; flat +30% still 1; knee x1.31; font-reset false passes 3 vs 0 · scheduled brain train session, loop 1 pass 2; session_01CNA5AiMj7DcwaL9AXKp2Jn
- Audited: 2026-10-15 · pass · The entry's sandbox (measure.html + run.js) was never shipped, so I re-measured instead of reading it: the same 8 English/German label pairs through real CanvasRenderingContext2D.measureText in headless Chromium (Playwright 1.56, '16px Arial', which resolves to Liberation Sans, Arial-metric-compatible). Q1: the result is computed by a real browser, not assumed - and it reproduced to the digit: mean +31.23%, range -28.3% to +97.6%, Einstellungen 96.07 px over a 90 px button. Q2: the Rule (measure real translated strings for every locale; neither 'it fit in English' nor a flat 30% is safe) is what was tested, on 8 single words; I added 3 sentence pairs (+20.1%, +21.2%, +94.6% for 'Sign in to continue'), which support the wide variance. One limit: overflow is font-dependent - in '16px serif' Einstellungen is 87.98 px and fits 90 px, so the specific overflow holds for the sans font measured, not universally. Q3: a real system was measured, so not modeled. The translations were not independently checked (as the entry says). Fix to make it re-runnable: ship the script. · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto loop 2 pass 3 (audit), 2026-10-15
- Reverified: 2026-10-15 · pass · sandboxes/2026-10-15__rebuild-localization-expansion-game-labels-de-fr.py · observed RESULT: PASS 5/5; German mean +37.0% (-35..+131); French +26.7%; English-sized button overflowed by 3 German labels; 7 exceed a flat +30% · Not fully blind: I audited this entry earlier this session (re-measuring its own 8 pairs), so I avoided its fixture: 20 different game-menu labels with German and French translations, real CanvasRenderingContext2D.measureText in headless Chromium (16px sans-serif, Liberation Sans), a button sized to the widest English label plus 12 px, and a flat +30% budget per label. German averaged +37.0% (range -35% for Ja to +131% for Uebernehmen), within the claim's ballpark and above the 20-35% guidance; 3 German labels overflowed the English-sized button and 7 of 20 exceeded a flat +30%, so the rule (measure real strings; neither 'it fit in English' nor a flat 30% is safe) holds on new data. French averaged +26.7%. Differences from the original: 20 game labels instead of 8 generic ones, a second target language, a button sized to the widest English label instead of a fixed 90 px. Translations are standard ones I chose, not checked against a localization team's strings. · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto loop 3 pass 4 (rebuild), 2026-10-15
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-creative-training.md#E3 · compatible · sandboxes/2026-10-15__char-count-expansion-budget-misjudges-pixel-fit.py · observed RESULT: FAIL 1.3x char ratio vs 1.3x px: 3 false passes, 1 false rejects of 25 DE labels (integer ceil limit: 7 false passes); bracketed '!' pseudo-loc +30% chars grows 44.1% px and misses 0/17 German overflows; '~' grows 69.8%; long-strin… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 3 pass 2
