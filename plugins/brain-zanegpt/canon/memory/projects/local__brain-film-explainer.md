# local/brain-film-explainer — lessons

Project: local/brain-film-explainer. Newest first.

---

## E7 — offline render voice cap silences score
- Date: 2026-10-10
- Project: local/brain-film-explainer
- Tags: [audio][browser][tooling]
- What: A canvas film's synthesized Web Audio score was rendered offline (OfflineAudioContext) for an MP4 export,
  and the exported soundtrack was near-silent for most of the film while live playback sounded full.
- Why built: The export path schedules the whole score up front into an OfflineAudioContext and renders it once,
  reusing the same osc()/musicStep code the live player uses so both mixes match.
- Design: osc() carried a live polyphony guard: a voices counter incremented on create, decremented in the
  oscillator's onended callback, and new notes refused once voices exceeded 40.
- Got right: Sharing one score function between live and offline paths, with an injectable clock, kept timing
  identical; the problem was isolated to a single guard, not to the shared design.
- Where/why it failed: In an offline render every note is scheduled before startRendering, so onended never fires
  during scheduling; the counter only climbs, hit 40 within seconds, and every later note was silently dropped.
  An RMS scan found 3067 of 4863 100 ms windows below -48 dB. The same cap also clipped notes in dense live scenes
  because pads with long releases stay alive for several seconds.
- Fix: Skip the voice cap when rendering offline (an OFFLINE flag set by the export entry point) and raise the live
  cap to 140; after the fix only the 0.5 s fade-in stayed below -48 dB (6 windows) and mean RMS rose to 0.044.
- Why this fix: Offline rendering has no real-time CPU budget to protect, so the guard has no job there; deriving
  the count from scheduled stop times would also work but adds code for no benefit in the offline path.
- Rule of thumb: A resource guard released by a playback-time callback (onended, ended events) never releases in an offline render, so it silently drops content; bypass it offline and verify every audio export by scanning for silent windows, not by its file size.
- Provenance (verified/assumed): verified first-hand: reproduced the near-silent offline render, measured the silent windows before and after, and re-exported the MP4 with the fixed soundtrack in this session.
- Composed: N/A
- Link: session 2026-10-09/10 brain-film-explainer v6 export; session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E442 · compatible · sandboxes/2026-10-18__schedule-aware-rms-scan-catches-silent-drops.py · observed RESULT: PASS key check sees fault A only; schedule-aware scan finds A=10 and B=35 dropped windows with 0 false alarms; median-relative naive scan reports 0 for B · brain train auto session 2026-10-18; session_01L27EvvVfmoxjFAREggXBWN

## E6 — continuous score one parent scale
- Date: 2026-10-10
- Project: local/brain-film-explainer
- Tags: [audio][music][design]
- What: A film's adaptive score sounded like it restarted at every scene: the phrase reset, layers switched on and
  off instantly, and some cuts jumped between unrelated keys (E and C mixolydian next to white-key modes).
- Why built: Each scene sets a mood through a music config (mode, root, pad, arp, drums, motif), and the viewer
  asked for one score that continues and adapts through every transition.
- Design: Per-scene configs were applied directly: a key change reset the phrase counter and released pads, and
  layer levels took the new scene's values on the next step.
- Got right: Bar-quantized scene lengths and a shared motif already gave the score one tempo and one recognizable
  tune across the film, so continuity only needed the transitions fixed.
- Where/why it failed: Restarting the phrase and progression on each key change, plus instant layer switches, made
  every cut audible as a reset; roots outside the parent scale added accidental notes that clashed at the seam.
- Fix: Keep one global bar grid and motif phrase; restrict every scene's mode to modes of one parent scale (A
  aeolian, C ionian, F lydian, D dorian, G mixolydian) so a key change only moves the tonal centre; glide each
  layer level about 7 percent per sixteenth (about one bar to settle); add a soft swell into each cut and a low
  note plus shimmer on the first downbeat.
- Why this fix: Modes of one parent scale share every pitch, so a new scene re-centres the same notes instead of
  replacing them, and gliding levels lets intensity follow the picture without a seam.
- Rule of thumb: For a score that must feel continuous across scene changes, keep one bar grid and tune, give every scene a mode of the same parent scale, and glide layer levels over about a bar instead of switching them at the cut.
- Provenance (verified/assumed): verified first-hand that the rebuilt score renders with no silent gaps and that every scene key now belongs to one parent scale; the musical smoothness itself is my judgement, not a listening test.
- Composed: N/A
- Link: session 2026-10-09/10 brain-film-explainer v6; session_015qgYN9GL7cHD9BS1wmwyMx

## E5 — audio clock as film master clock
- Date: 2026-10-10
- Project: local/brain-film-explainer
- Tags: [audio][animation][sync]
- What: A scene-based canvas film with a synthesized score drifted out of sync: music phrase changes landed off
  the scene cuts, and the first downbeat of some scenes played the previous scene's chord for a whole bar.
- Why built: Every scene is a whole number of bars so the score can change key exactly on each cut; the score is
  scheduled on the AudioContext clock with a look-ahead window.
- Design: Picture time advanced from requestAnimationFrame deltas (capped at 0.1 s per frame); the scheduler mapped
  audio time to film time as T + (nextStep - currentTime); a step near a cut was clipped to the remaining time with
  a 20 ms floor; the scene for each step was looked up at its exact film time.
- Got right: Scheduling notes on the audio clock with a look-ahead horizon (existing canon) and quantizing every
  scene to whole bars, which made exact alignment possible at all.
- Where/why it failed: Three separate errors. The rAF clock with a frame cap drifts from the audio clock, so T was
  wrong. A step landing exactly on a cut sat a float epsilon before the boundary and was evaluated as the old
  scene, launching the old key's pad for a bar. The 20 ms floor on clipped steps inserted an extra step that
  shifted the grid after every cut.
- Fix: Read picture time from the audio clock once sound runs (T = T0 + currentTime - A0, anchored on play/seek);
  start the first step on the next grid point; use a fixed step length; look up the scene at film time plus 1 ms.
  Verified: every scene's first step lands within 2e-11 s of its first frame and live picture/audio stay within
  one frame.
- Why this fix: The audio clock is the only clock that cannot stutter, so making it the master removes drift by
  construction instead of correcting it; the 1 ms nudge assigns boundary steps to the scene they open.
- Rule of thumb: When picture and score must cut together, make the audio clock the film's master clock, start steps on the bar grid, and evaluate a step that lands on a cut on the far side of the boundary; a rAF-delta clock and boundary float error each desync by up to a bar.
- Provenance (verified/assumed): verified first-hand: measured scene-start step offsets and live picture-audio drift in headless Chromium before and after the change in this session.
- Composed: N/A
- Link: session 2026-10-09/10 brain-film-explainer v6; session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-11 · projects/pappydapimp69__brainwork.md#E123 · compatible · sandboxes/2026-10-11__reading-time-warp-moves-scene-starts-and-hand-synced-cut-list-drifts.py · observed RESULT: PASS coverage 100% green, drifted 6/8 (worst 13.5 bars), derived drift 0/8, snap extra max 1.85s, cap 1.5 leaves 4 scenes short · scheduled brain train session; session_018Fx6YUUQMABGNn8Depe7Ek loop 1 pass 2

## E4 — tension heading count is not open count
- Date: 2026-10-09
- Project: local/brain-film-explainer
- Tags: [knowledge-management][process][viz]
- What: An explainer film and a plain-English guide labelled the number of tension-ledger
  entries as "open questions" (65, later 70), counted by grepping `### ` headings.
- Why built: The heading count was the easy daily series to chart from git history, and the
  ledger reads like a list of open forks.
- Design: Count `### ` blocks in tension-ledger.md per day and call the total open questions.
- Got right: The heading count is a correct measure of how many forks were ever recorded, so it
  still works as a growth series once it is labelled as tracked questions.
- Where/why it failed: The ledger keeps resolved, parked and unmarked entries too. Classifying
  the same 70 blocks with Brain's own entry_status gave 24 red, 22 yellow, 13 green, 1 parked
  and 10 unmarked, so only 46 were open: the headline overstated open questions by about half.
- Fix: Label the heading count as "hard questions tracked" and take the open number from
  entry_status (red plus yellow), showing both: 70 tracked, 46 still open.
- Why this fix: entry_status is the same classifier brain query and brain challenge use, so
  the film now agrees with the CLI instead of inventing a second definition of open.
- Rule of thumb: Never report a ledger's entry count as its open count; classify entries with
  the tool's own status function and label a raw count as tracked, not open.
- Provenance (verified/assumed): verified first-hand by loading bin/brain and running
  entry_status over all 70 ledger blocks on origin/main.
- Composed: N/A
- Link: session 2026-10-09
- Cited-by: 2026-10-17 · projects/local__sidecar-drift-silently-drops-ipm-d1-contender.md#E1 · compatible · sandboxes/2026-10-17__sidecar-drift-silently-drops-ipm-d1-contender.py · observed RESULT: PASS (revised claim) drift picks truth 0/40; derived recovery 100:10 2000:18 20000:22 of 40; loser-drop(2000) 16/40; tracked 6 vs ranked 5. The 28-of-40 prediction was refuted; recovery is budget-limited by a close race. · brain train auto loop 1 pass 1; session_01S4WKoTG7YsrzCXAnXDQDg7

## E3 — steward run died before steps leaves proposal unpromoted
- Date: 2026-10-09
- Project: local/brain-film-explainer
- Tags: [tooling][process][ci]
- What: An ideas kernel pushed to incoming/ by `brain sync` sat unpromoted for hours, so the
  kernel count reported in a film and a status answer stayed at 1,107 instead of 1,108.
- Why built: The ideas steward is a GitHub Action that runs on every push touching incoming/
  and promotes passing proposals, so nobody expects to check it by hand.
- Design: Promotion depends on one workflow run per push; there is no retry or schedule, only
  workflow_dispatch for a manual rerun.
- Got right: The proposal itself was sound: running scripts/steward.py locally on a scratch
  clone checked out at the exact head SHA promoted it with 0 holds and validation passed.
- Where/why it failed: The workflow run for that push concluded "failure" 3 seconds after it
  started, before any step ran; the job log download returned 404, so there was no error text,
  and the proposal just stayed in incoming/ looking like a slow steward.
- Fix: List the steward workflow runs for the push SHA, see the pre-step failure, run the
  steward locally on that SHA to prove the proposal passes, then rerun the workflow
  (workflow_dispatch). The owner reran it and the kernel promoted (count 1,108).
- Why this fix: Running the steward locally separates "the proposal is bad" from "the runner
  never ran"; a log-less 3-second failure is an infrastructure fault, and a rerun is the only
  thing that clears it because nothing else re-triggers the workflow.
- Rule of thumb: When a steward-promoted count does not move after a sync, check the workflow
  run for that push before suspecting the proposal; a run that fails before any step leaves no
  log and needs a manual rerun, and a local steward run on the same SHA proves which side failed.
- Provenance (verified/assumed): verified first-hand: the run conclusion and 3-second duration
  from the Actions API, the 404 log download, and the local steward run promoting 1 with 0 holds.
- Composed: N/A
- Link: session 2026-10-09 (ideas steward run 37907794349)

## E2 — reading time warp turns scenes into slow motion
- Date: 2026-10-09
- Project: local/brain-film-explainer
- Tags: [viz][narration][timing]
- What: A canvas explainer film gave every caption a minimum reading time (1 s plus 1 s per
  2.6 words) by stretching that caption's window of the scene's authored timeline.
- Why built: Text-heavy scenes flashed captions too fast to read; a piecewise time map from
  film time to authored time fixed reading time without re-authoring every scene.
- Design: For each caption window [a,b], factor f = max(1, need/(b-a)); the scene's film clock
  maps onto authored time piecewise, so draw(lt) stays a pure function of authored time.
- Got right: Every caption met its reading time (slack 0 on all of them) and seeking stayed a
  pure lookup, because markers and captions were converted through the same forward map.
- Where/why it failed: Stretching a window slows everything drawn in it, so text-heavy scenes
  played in slow motion: factors reached 2.1 to 2.4 (dog park 17 s to 28.5 s, whiteboard 16 s
  to 34 s), and the viewer read it as broken pacing, not as time to read.
- Fix: Report each scene's warp factor, cut caption words that restate what is on screen, and
  add authored holds (longer scene, later caption end) where text must stay long; most scenes
  then ran at 1.0 to 1.5.
- Why this fix: Reading time is a property of the text, so the cheapest lever is fewer words;
  where the words must stay, a hold keeps motion at real speed instead of slowing it.
- Rule of thumb: A reading-time stretch on an animated timeline is slow motion; print the
  per-scene factor, keep it under about 1.5, and buy the rest with shorter text or a hold.
- Provenance (verified/assumed): verified first-hand from the per-scene factors the film printed
  before and after the caption pass.
- Composed: N/A
- Link: session 2026-10-09
- Cited-by: 2026-10-11 · projects/pappydapimp69__brainwork.md#E123 · compatible · sandboxes/2026-10-11__reading-time-warp-moves-scene-starts-and-hand-synced-cut-list-drifts.py · observed RESULT: PASS coverage 100% green, drifted 6/8 (worst 13.5 bars), derived drift 0/8, snap extra max 1.85s, cap 1.5 leaves 4 scenes short · scheduled brain train session; session_018Fx6YUUQMABGNn8Depe7Ek loop 1 pass 2
- Cited-by: 2026-10-17 · projects/local__reaction-cut-pause-placement.md#E1 · compatible · sandboxes/2026-10-17__reaction-cut-snap-pauses-to-caption-end.py · observed RESULT: PASS snap 0 split, 0 replay, max lag 4.26 s real and clustered; 15 s interval split 7 of 7; run-back replays 45.2 s (38 percent, prediction of 10 percent was wrong); 12 s caption with early trigger lag 9.88 s. · session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-17 · projects/local__caption-warp-cap-before-ipm-d1-ranking.md#E1 · compatible · sandboxes/2026-10-17__caption-warp-cap-before-ipm-d1-ranking.py · observed RESULT: PASS cap loses at slope 0.005 (11.14 vs 12.01), wins at 0.2 (11.14 vs 8.65); first winning slope 0.05 · scheduled brain train auto loop 1 pass 5 (gap); session_011LtaNZCrPYhhAtwJpZ1y8i
- Cited-by: 2026-10-17 · projects/pappydapimp69__zanegpt.md#E29 · compatible · no sandbox · https://claude.ai/code/session_01WkbM7ZHHguQoKwyDFf4vYn · https://claude.ai/artifact/1kFmKx74PL3QTXsPNWCAQc
- Cited-by: 2026-10-17 · projects/pappydapimp69__zanegpt.md#E31 · compatible · no sandbox · https://claude.ai/code/session_01WkbM7ZHHguQoKwyDFf4vYn · https://claude.ai/artifact/1kFmKx74PL3QTXsPNWCAQc
- Cited-by: 2026-10-18 · projects/pappydapimp69__brain.md#E211 · compatible · sandboxes/2026-10-18__absorbing-reaction-pauses-into-caption-windows-trips-the-warp-cap-on-short-captions.py · observed RESULT: FAIL ABSORB over-cap captions 2 (worst warp 1.80); ABSORB wins at slope 0.005 True, HOLD wins at 0.05 True; first HOLD win at slope 0.01; 0.5 s pause ABSORB wins at all slopes True. Only the crossover band failed. · scheduled brain train session_01YL3uJX45U8L4Nh9fQf5qoD
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E438 · compatible · sandboxes/2026-10-18__derived-pause-map-survives-caption-warp.py · observed RESULT: PASS sidecar misses 8/8 and 8/8 after warp, derived 0/8, no drift at warp 1.0 · brain train auto session 2026-10-18; session_01L27EvvVfmoxjFAREggXBWN
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E439 · compatible · sandboxes/2026-10-18__hook-word-count-vs-warp-cap-and-pause.py · observed RESULT: PASS max hook words under the 1.5 cap = 7; fixed 3 s pause misses by >0.5 s for N=[6, 7, 8, 9, 10]; N=5 lag 0 · brain train auto session 2026-10-18; session_01L27EvvVfmoxjFAREggXBWN
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E451 · compatible · sandboxes/2026-10-18__reaction-pause-needs-fast-mute-path.py · observed RESULT: PASS 1.0 s pause leaks 0.75 level-s via glide vs 0.080 fast; glide leaves 0.25 level-s missing after resume vs 0.00; 4 s pause loses 1.01 after resume, 0.5 s only 0.06. The under-0.05 part was refuted (0.08). · scheduled brain train auto pass 5 (loop 1); session_01NZDPzU2KzUnFJgGMC4knps

## E1 — injectable audio clock for offline video export
- Date: 2026-10-09
- Project: local/brain-film-explainer
- Tags: [audio][browser][tooling]
- What: A browser film with a live Web Audio score and effects had to be exported to MP4 with
  the sound in sync, from a headless browser that captures frames by seeking.
- Why built: Recording real-time playback drifts and drops frames; frame-by-frame seek plus
  element screenshots is deterministic for the picture, but the audio needed the same property.
- Design: Every effect and note took its start time from ac.currentTime, and the score was
  scheduled by a look-ahead timer against the live clock while the film played.
- Got right: Because the score was a pure function of film time (one step function returning
  the step length) and effects were keyed to timeline markers, both could be replayed without
  the picture.
- Where/why it failed: OfflineAudioContext.currentTime stays 0 until rendering starts, so
  effects read the clock at schedule time and all collapsed onto t=0; the live scheduler also
  only runs while playing, so nothing scheduled the music offline at all.
- Fix: Route every effect's start through one function (NOWF) that returns an override time
  when set, else ac.currentTime; offline, set the override to each marker's film time and fire
  it, and loop the score's step function over film time. Render, write 16-bit PCM, mux with the
  frames, normalize loudness.
- Why this fix: One injectable clock keeps the live page unchanged and makes the offline render
  use the exact same note and effect code, so the export cannot drift from what viewers hear.
- Rule of thumb: Give Web Audio code one injectable now() instead of reading ac.currentTime
  directly, and expose the score as a step function of film time, so an OfflineAudioContext can
  render the same mix for video export.
- Provenance (verified/assumed): verified first-hand: four exports rendered this way, each muxed
  to the film's full duration with measured loudness (mean -17.7 to -18.1 dB after loudnorm).
- Composed: ideas:MOTION/video-export/render-canvas-cutscenes-to-video-via-paused-scrub-plus-element-screenshot
- Link: session 2026-10-09

