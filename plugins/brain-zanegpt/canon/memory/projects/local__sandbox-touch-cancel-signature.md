# local/sandbox-touch-cancel-signature — lessons

Project: local/sandbox-touch-cancel-signature. Newest first.

---

## E1 — touch cancel vs zero events are different failures
- Date: 2026-08-21
- Project: local/sandbox-touch-cancel-signature
- Tags: [testing][input][browser][mobile][touch]
- What: A deterministic 3-condition sandbox (headless Chromium, one page, one
  run) isolating what a debugging engineer actually SEES when mobile touch
  input silently fails, for two structurally different causes: (1) a
  hand-built `new TouchEvent(...)` dispatched into the page, and (2) a
  genuine `Input.dispatchTouchEvent` (CDP-level, indistinguishable from real
  hardware) landing on an element whose `touch-action` still permits native
  panning, against (3) an identical CDP dispatch on a `touch-action:none`
  control.
- Why built: `brain train`'s single-source-edge pass flagged
  `sandbox-capture-layer-starves-tutorial + dog` for re-verification. Reading
  dog#E103 (hand-built TouchEvent fires zero Pointer Events) alongside
  shadow#E3 (a game canvas needs `touch-action:none` to own every gesture)
  surfaced a gap: shadow#E3 states the FIX but never verified what the
  FAILURE actually looks like on screen — and this session's own build of
  Ephemeral had just hit the touch-action failure directly (a real finger
  drag silently died via `pointercancel`), which is a visibly different
  symptom from dog#E103's silence.
- Design: one HTML page, two elements — `#a` (`touch-action:auto`) and `#b`
  (`touch-action:none`, the control) — each logging every
  pointerdown/pointermove/pointerup/pointercancel it receives. Condition 1
  dispatches a hand-built `TouchEvent` (with real `Touch` objects, required
  by Chromium's constructor) at `#a`. Condition 2 uses genuine CDP
  `Input.dispatchTouchEvent` touchStart/touchMove×10/touchEnd at `#a`.
  Condition 3 repeats condition 2's exact dispatch sequence at `#b`. A real
  `<meta name="viewport">` tag was required on the test page itself — its
  absence first produced a false "control fired nothing" result because
  mobile emulation defaulted to a 980px layout viewport and the hardcoded
  touch coordinates missed both elements entirely, confirmed by dumping
  `getBoundingClientRect()` before and after adding the tag.
- Got right: keeping the three conditions on the exact same page, dispatch
  code, and drag distance, varying only the dispatch TYPE (hand-built vs
  CDP) and the target's `touch-action`, isolated cause from symptom cleanly
  enough that the three event-log signatures below are unambiguous rather
  than statistical.
- Where/why it failed: N/A for this sandbox itself (both target claims
  reproduced on the first corrected run, after the viewport-meta fix above).
- Fix: N/A — this is a diagnostic sandbox, not a bug fix. The fix it exists
  to make available to someone TRIAGING a "touch doesn't work" report is
  named in the rule of thumb.
- Why this fix: Not applicable in the usual sense; the value here is the
  three distinguishable observed signatures, which is the diagnostic itself.
- Rule of thumb: When a mobile touch interaction silently fails, the exact
  sequence of Pointer Events received (or not) tells you which of two
  unrelated causes to look for — don't guess, read the log. Observed,
  one run: (1) hand-built `TouchEvent` -> `[]`, zero Pointer Events, ever
  (dog#E103's signature — the input was never really delivered; check that
  real Touch/Pointer construction is used, not a hand-rolled dict). (2) real
  CDP touch on `touch-action:auto` -> `["pointerdown","pointermove",
  "pointermove","pointercancel"]` — Pointer Events START firing (proving the
  input is genuine) and then the sequence is cut short by `pointercancel`
  partway through (the browser's native pan/zoom gesture recognizer claimed
  the gesture — set `touch-action:none` on the interactive surface, per
  shadow#E3). (3) identical CDP dispatch on the `touch-action:none` control
  -> a full, uninterrupted pointerdown -> pointermove×N -> pointerup, no
  cancel. Zero events and a cancelled-partway sequence are NOT the same bug
  and do not share a fix — one is an event-construction problem in the TEST,
  the other is a CSS problem in the PAGE, and confusing them wastes a
  debugging pass looking in the wrong place.
- Provenance (verified/assumed): Verified first-hand — headless Chromium via
  Playwright, real CDP `Input.dispatchTouchEvent` calls (not `page.mouse`,
  which never triggers touch-action gesture arbitration at all and so cannot
  reproduce condition 2), exact event-log arrays reproduced above, re-run
  clean after the viewport-meta fix.
- Composed: dog/E103 + pappydapimp69__shadow/E3
- Link: local sandbox, this session (Pappydapimp69/Tension branch
  claude/animated-interactive-story-znhhve build of Ephemeral, where the
  touch-action failure was first hit live on a real deploy)

