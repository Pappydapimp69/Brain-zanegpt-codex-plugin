# local/brain-films — lessons

Project: local/brain-films. Newest first.

---

## E3 — missing config key crashes only the eager export path
- Date: 2026-10-17
- Project: local/brain-films
- Tags: [audio][film][testing]
- What: Two films' scenes asked the music engine for modes 'phrygian' and 'locrian', which its MODES and
  PROG tables did not contain; the offline audio render for the MP4 threw on the first such step.
- Why built: Exporting a canvas film to MP4 renders the whole score offline in one pass, while the live player
  schedules steps from a timer as the film plays.
- Design: musicStep looks up MODES[cfg.mode] and PROG[cfg.mode]; the live scheduler calls it from setInterval,
  the export calls it in a loop inside __renderAudio before OfflineAudioContext.startRendering.
- Got right: The export path failed loudly (TypeError reading length of undefined) and named the function, which
  led straight to the two missing table entries; adding them fixed both films.
- Where/why it failed: The live player had been published with the gap: an exception inside the timer callback only drops
  that tick's notes, so those scenes played with broken music and no visible error.
- Fix: Added both modes to MODES and PROG, rebuilt and republished both films, and re-ran the export,
  which then completed.
- Why this fix: Filling the tables fixes every scene at once; the lasting fix is a build-time check that every
  scene's mode exists, since the live path will never report it.
- Rule of thumb: Validate every config key a scene uses against the engine's lookup tables at build time; a missing key
  fails loudly only on the eager export path, while the timer-driven live path swallows it per tick.
- Provenance (verified/assumed): Verified first-hand: the export error, the missing table entries and the clean export after the fix were observed in this session.
- Composed: N/A
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E442 · compatible · sandboxes/2026-10-18__schedule-aware-rms-scan-catches-silent-drops.py · observed RESULT: PASS key check sees fault A only; schedule-aware scan finds A=10 and B=35 dropped windows with 0 false alarms; median-relative naive scan reports 0 for B · brain train auto session 2026-10-18; session_01L27EvvVfmoxjFAREggXBWN

## E2 — hard mute in a gliding score needs its own path
- Date: 2026-10-17
- Project: local/brain-films
- Tags: [audio][music][state]
- What: Pausing a source film inside a reaction film had to stop its music at once, but the score engine
  glides every layer toward its scene level instead of switching.
- Why built: Reactor lines play over a frozen source frame; the owner asked for the source audio to stop during
  each pause.
- Design: Levels move 5-8 percent toward target per sixteenth step, chords start on downbeats with their
  gain fixed at start, and held pads are released only on a key change.
- Got right: A mute flag that returns early, releases held pads with a 0.05 s time constant, and on unmute snaps
  the levels back to target and counts as a key change cut the music within a step and resumed it at
  full level on a fresh chord; offline, 112 of 296 quarter-second windows in one reaction went silent.
- Where/why it failed: Setting the scene's levels to zero for the pause would only have faded the score over about two
  seconds, and on resume the first chord would have started almost silent and stayed that way for a
  whole bar because its gain is fixed when it starts.
- Fix: Give mute its own path: release pads fast, skip scheduling, and on unmute restore levels instantly
  and treat it as a key change so the next step starts a chord.
- Why this fix: Gliding is right for scene changes and wrong for pauses; separating the two keeps the smooth
  transitions while making a pause read as a cut.
- Rule of thumb: In a score engine that glides levels between scenes, implement mute as its own path that releases
  held notes and snaps levels back on resume; driving levels to zero only fades out and fades back in.
- Provenance (verified/assumed): Verified first-hand: the silent windows during pauses and the clean resumes were measured from the offline render in this session.
- Composed: N/A
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E451 · compatible · sandboxes/2026-10-18__reaction-pause-needs-fast-mute-path.py · observed RESULT: PASS 1.0 s pause leaks 0.75 level-s via glide vs 0.080 fast; glide leaves 0.25 level-s missing after resume vs 0.00; 4 s pause loses 1.01 after resume, 0.5 s only 0.06. The under-0.05 part was refuted (0.08). · scheduled brain train auto pass 5 (loop 1); session_01NZDPzU2KzUnFJgGMC4knps

## E1 — find audio spikes by percentile not jump ratio
- Date: 2026-10-17
- Project: local/brain-films
- Tags: [audio][testing][process]
- What: Found the source of reported audio spikes in a 6.5-minute film by rendering the score offline,
  measuring RMS in 50 ms windows and mapping loud windows to the scheduled sound-effect marks.
- Why built: A reaction-style film paused its source film's music for long stretches, and the owner reported
  the audio spiking.
- Design: First pass ranked windows by their RMS over the median of the preceding second; second pass took
  an absolute threshold from the whole render's distribution (p50 340, p99 2789) and listed every
  window over 2000 with the marks within 0.3 s.
- Got right: The absolute pass named the culprit: every one of the three loudest moments (6301-7650 RMS, about
  2.5 times p99) was a 'stamp' effect; a softer variant brought the max to 3882, near p99.
- Where/why it failed: The jump-ratio pass was useless: after muted pauses the preceding median is near zero, so every
  ordinary return of sound scored as a 3000x spike and the real peaks were buried among them.
- Fix: Rank by absolute level against the render's own percentiles, then join loud windows to the event
  marks scheduled at those times; replace or scale the effect that recurs.
- Why this fix: A spike is loud relative to the mix, not to the moment before it; silence-heavy material breaks any
  local-ratio detector, and the mark join turns a loud time into a named cause.
- Rule of thumb: To find audio spikes, threshold windowed RMS against the whole render's percentiles and join the loud
  windows to scheduled events; a ratio to the preceding moment flags every return from silence instead.
- Provenance (verified/assumed): Verified first-hand: both passes, the RMS figures and the post-fix maximum were measured in this session.
- Composed: N/A
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E442 · compatible · sandboxes/2026-10-18__schedule-aware-rms-scan-catches-silent-drops.py · observed RESULT: PASS key check sees fault A only; schedule-aware scan finds A=10 and B=35 dropped windows with 0 false alarms; median-relative naive scan reports 0 for B · brain train auto session 2026-10-18; session_01L27EvvVfmoxjFAREggXBWN
