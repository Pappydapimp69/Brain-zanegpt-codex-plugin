# Pappydapimp69/animation — lessons

Project: Pappydapimp69/animation. Newest first.

---

## E1 — scrub while playing must pause first
- Date: 2026-07-30
- Project: Pappydapimp69/animation
- Tags: [gamedev][cutscene][ui][state]
- What: Dragging the timeline scrub bar while a cutscene is autoplaying
  appeared to do nothing — the position visibly snapped back toward wherever
  autoplay had already advanced to, instead of holding where the user
  dragged it. The `input` handler correctly called `seek(t)`, but only
  force-rendered the sought frame `if (!playing)`; while playing, the
  running `requestAnimationFrame` loop's next tick advanced `t` forward from
  the sought position on its own very next frame, overwriting the user's
  scrub before it was ever visible.
- Why built: Discovered incidentally while testing an unrelated claim (a
  geometry-verification pass on the same file) that used scripted scrub
  input without first clicking Pause — the scrubbed screenshots kept
  showing wrong/drifting timestamps until pausing first was added to the
  test script. That test workaround should have been the tell that the
  player itself had the bug, not just the test.
- Design: `el.scrub.addEventListener("input", () => { seek(t, "scrub"); if
  (!playing) frame(now, true); })` — force-render only guarded the paused
  case; nothing stopped the main loop from running afterward.
- Got right: `seek()` itself is correct — it re-resolves the marker pointer
  and clamps `t` properly regardless of direction (see the companion
  no-retroactive-fire lesson). The bug is purely in WHEN the seek is allowed
  to be overwritten, not in the seek logic itself.
- Where/why it failed: Verified first-hand (deterministic headless
  Chromium): scrubbing to t=10.0s while the page's default autoplay was
  still running left `t = 10.000s` displayed for one instant, but polling
  again 500ms later showed the SAME instant only after the fix; before the
  fix, playback had continued advancing past the scrubbed position within
  that window, so a user's drag never actually held.
- Fix: Any manual scrub takes control — pause first, unconditionally, THEN
  seek, THEN force-render: `if (playing) { playing = false;
  playButton.textContent = "Play"; } seek(t); frame(now, true);`. Matches
  standard media-player UX (grabbing the seek handle implies "I'm driving
  now") and removes the race entirely rather than tuning around it.
- Why this fix: The race existed because "should this frame render the
  sought position" and "is autoplay currently allowed to advance" were the
  same boolean (`playing`) checked at two different times (once in the
  handler, once on the next rAF tick) instead of one authoritative state
  change made before the seek. Pausing unconditionally collapses it to a
  single ordering: state change, then seek, then render — no window where
  the two can race.
- Rule of thumb: A manual scrub/seek control on a live-playing timeline
  should force playback into a paused state as part of the SAME handler
  that performs the seek, not merely skip re-rendering while already
  paused — otherwise a running update loop can win a race against the
  user's own input on its very next tick.
- Provenance (verified/assumed): Verified first-hand. Headless Chromium
  (`--enable-unsafe-swiftshader`), scripted `input` event on the real
  `<input type="range">` scrub control, polled the displayed clock
  immediately and again 500ms later; confirmed drift before the fix and
  no drift after.
- Composed: N/A
- Link: Pappydapimp69/animation, lamplighter.html; this session.
- Cited-by: 2026-09-28 · projects/local__sandbox-kernel-system-cutscene.md#E1 · compatible · sandboxes/2026-09-28__train-gap-b03.py · session 2026-09-28, brain train gap batch 3 loop 15
