# Pappydapimp69/Shadow — lessons

Project: Pappydapimp69/Shadow. Newest first.

---

## E4 — zero loop tail when repeat off
- Date: 2026-07-01
- Project: Pappydapimp69/Shadow
- Tags: [audio][state]
- What: A tone "sequence" type that can either loop or play once; each step is followed by a `loopDelay` gap before the next.
- Why built: The loop delay spaces repeats of a looping sequence.
- Design: After the final step, the same `loopDelay` was applied before deciding whether to repeat.
- Got right: Looping sequences spaced correctly.
- Where/why it failed: A NON-looping (one-shot) sequence stayed in the "playing" state for ~2 extra seconds because its final step still added the trailing `loopDelay` even though nothing repeats. It was invisible until one-shots played inline (on the same screen) instead of on a separate player screen, where the lingering "playing" state became obvious.
- Fix: Zero the tail delay when `repeat` is off — the last step of a one-shot has no gap after it.
- Why this fix: A between-repeats delay is only meaningful between repeats; when there is no next iteration, the trailing gap is dead time that keeps transient state alive. The state duration should equal the actual audible duration.
- Rule of thumb: A "between-items" delay must be dropped on the final item when there's no repeat — otherwise a one-shot lingers in a transient (playing/busy) state for the length of a gap that never precedes anything. Watch for it when the same code path serves both looping and one-shot modes.
- Provenance (verified/assumed): REPORTED by the Shadow project (OVERVIEW); NOT verified first-hand here.
- Link: session 01KxkbJUq8YajH8GokSZYYHy; source at Pappydapimp69/ideas @ claude/shattered-realm-architecture-lv3lb4 reference/shadow/

## E3 — touch action pan y tiles
- Date: 2026-07-01
- Project: Pappydapimp69/Shadow
- Tags: [input][browser][touch]
- What: A grid of tappable tiles / menu rows on a mobile web page that also needs to scroll vertically.
- Why built: Tiles are the primary tap targets on the home screen.
- Design: Tiles handle pointer/touch for tapping.
- Got right: Taps worked.
- Where/why it failed: The tiles "ate" scroll drags — a finger starting on a tile couldn't scroll the page, because the elements captured the touch gesture as a tap/press instead of letting the browser pan.
- Fix: Set `touch-action: pan-y` on the tiles and menu rows so vertical panning is handed back to the browser while taps still register (and trim the default home to few enough cards to reduce the need to scroll over tiles).
- Why this fix: `touch-action` tells the browser which gestures it may handle natively; `pan-y` reserves vertical scrolling for the browser while leaving tap/click to the element. Without it, interactive elements can swallow the scroll.
- Rule of thumb: On mobile, interactive tiles/rows over a scrollable area need `touch-action: pan-y` (or `pan-x`) so they don't eat scroll drags — declare the axes the browser should still own. (Note the flip side: a full-screen game canvas wants `touch-action: none` to own ALL gestures — pick per element.)
- Provenance (verified/assumed): REPORTED by the Shadow project (OVERVIEW) and mined cross-project; NOT verified first-hand here. The `touch-action` mechanism is standard CSS behavior.
- Link: session 01KxkbJUq8YajH8GokSZYYHy; source at Pappydapimp69/ideas @ claude/shattered-realm-architecture-lv3lb4 reference/shadow/
- Cited-by: 2026-08-21 · projects/local__sandbox-touch-cancel-signature.md#E1 · compatible · no sandbox · local sandbox, this session (Pappydapimp69/Tension branch claude/animated-interactive-story-znhhve build of Ephemeral, where the touch-action failure was first hit live on a real deploy)

## E2 — no reliable output detection api
- Date: 2026-07-01
- Project: Pappydapimp69/Shadow
- Tags: [audio][browser][process]
- What: Trying to detect the audio output situation in a browser — is it a Bluetooth speaker? mono or stereo? — to auto-pick a playback mode.
- Why built: The app behaves differently on one speaker (beacon) vs two separated speakers (directional), so it wanted to auto-configure.
- Design: Read `AudioContext.destination.maxChannelCount` and `navigator.mediaDevices.enumerateDevices()` to infer channels/device.
- Got right: Recognizing early that output geometry changes correctness.
- Where/why it failed: No web API reliably reports this. `maxChannelCount` almost always returns 2 even for a mono Bluetooth speaker (the OS down-mixes); `enumerateDevices()` hides output labels until microphone permission is granted and returns little/nothing on iOS Safari; no API exposes the transport type (BT vs wired). Any auto-detection built on these is confidently wrong.
- Fix: Treat API reads as best-effort *display only* ("Output: Bluetooth detected" with a visible "tap to test"), and make the real decision a one-time FUNCTIONAL test: play a hard-left cue, pause, hard-right cue, and ask the user "did the sound move from one side to the other?" — Yes → directional, No → beacon. Re-runnable from settings.
- Why this fix: When introspection is unreliable, the only trustworthy signal is the observed effect. A functional test sidesteps every platform quirk because it measures the actual outcome the user experiences.
- Rule of thumb: Don't trust `maxChannelCount`/`enumerateDevices` to tell you mono-vs-stereo or Bluetooth — they lie or are permission-gated (esp. iOS). Gate correctness on a one-time user-confirmed functional test, and use the APIs only for informational display.
- Provenance (verified/assumed): REPORTED by the Shadow project (OVERVIEW + design-plan) and mined cross-project; NOT verified first-hand here.
- Link: session 01KxkbJUq8YajH8GokSZYYHy; source at Pappydapimp69/ideas @ claude/shattered-realm-architecture-lv3lb4 reference/shadow/

## E1 — audio clock scheduler not settimeout
- Date: 2026-07-01
- Project: Pappydapimp69/Shadow
- Tags: [audio][process][browser]
- What: A web soundboard that plays rhythmic tone loops to guide a blind dog, originally sequencing tones with per-tone `setTimeout(scheduleNext, …)`.
- Why built: setTimeout recursion is the obvious way to space out sounds over time.
- Design: Each tone scheduled the next via setTimeout based on wall-clock delay.
- Got right: Simple and worked while the app was foregrounded.
- Where/why it failed: JS timers drift and are throttled/suspended when the tab is backgrounded or the phone is pocketed/locked — exactly when a dog-guiding loop must keep perfect rhythm. Rhythm wandered or stalled.
- Fix: Drive timing off the `AudioContext` clock with a look-ahead scheduler — a short repeating timer (~25 ms) that schedules every tone due within a small horizon (~150 ms) at an absolute `audioCtx.currentTime + offset`; plus a Screen Wake Lock while looping so the screen/CPU don't sleep. Degrade gracefully where Wake Lock is unsupported (iOS is limited; document the caveat).
- Why this fix: The audio hardware clock is monotonic and unaffected by JS timer throttling; scheduling ahead of time on that clock makes rhythm immune to main-thread jitter. The coarse timer only needs to run often enough to top up the horizon.
- Rule of thumb: For anything rhythmic in Web Audio, schedule on the AudioContext clock with a look-ahead window — never chain per-note setTimeout, which drifts and dies when backgrounded. Add a Wake Lock for playback that must survive a locked screen.
- Provenance (verified/assumed): REPORTED by the Shadow project (its OVERVIEW + design-plan) and mined cross-project this session; NOT independently verified first-hand here. The look-ahead-scheduler pattern is well-established Web Audio guidance.
- Link: session 01KxkbJUq8YajH8GokSZYYHy; source at Pappydapimp69/ideas @ claude/shattered-realm-architecture-lv3lb4 reference/shadow/ (OVERVIEW.md, design-plan.md)

