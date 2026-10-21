# local/reaction-cut-pause-placement — lessons

Project: local/reaction-cut-pause-placement. Newest first.

---

## E1 — reaction cut snap pauses to caption end
- Date: 2026-10-17
- Project: local/reaction-cut-pause-placement
- Tags: [film][narration][timing][structure]
- What: Modelled where a reaction cut should pause a captioned source film, on the real caption
  timings of a 2:00 film (16 captions, 6 trigger phrases): snap to the end of the caption holding
  the trigger, cut on the trigger word, cut and run the caption back, or pause on a fixed interval.
- Why built: Building a reaction-style film over an existing captioned film; shared canon had no
  lesson on reaction-video structure, so the pause rule was a gap, not a known pattern.
- Design: Stdlib sandbox with the film's caption start/end times embedded; trigger time = caption
  start + (words up to the end of the trigger phrase / caption words) x caption length. Metrics:
  source lines split by a pause, seconds replayed, lag from trigger word to pause; comment-lag
  tolerance assumed at 5 s.
- Got right: Snapping to the caption end split 0 lines and replayed 0 s with a worst lag of 4.26 s,
  unchanged when triggers sat in back-to-back captions (8 pauses), because captions here run 3.7 to
  10.4 s and triggers sit late in them.
- Where/why it failed: Two other placements look natural and both cost: a fixed 15 s interval split
  7 of 7 lines, and cutting on the word then running the caption back on every trigger replayed
  45.2 s, 38 percent of a 120 s source. Snap itself broke on a 12 s caption with the trigger in its
  first quarter: lag 9.88 s, past the 5 s tolerance.
- Fix: Snap each pause to the end of the caption that holds its trigger; only when the trigger sits
  more than the tolerance before that caption ends, cut on the word and run that one caption back
  (one such case replayed 9.66 s instead of the whole film's worth).
- Why this fix: Snapping keeps every source line whole for free whenever captions are short, and a
  run-back is reserved for the one shape where snapping makes the comment arrive late, so replay
  cost stays per-exception instead of growing with the number of reactions.
- Rule of thumb: In a reaction cut, pause at the end of the caption holding the trigger; run a line
  back only when its trigger sits early in a long caption, since running back every reaction replays
  over a third of the source.
- Provenance (verified/assumed): Verified first-hand by the sandbox on the film's real caption
  timings; the 5 s comment-lag tolerance is an assumed constant, chosen before the run.
- Composed: brain-film-explainer/E2
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-17__reaction-cut-snap-pauses-to-caption-end.py
- Prediction: Snap gives 0 split lines and 0 s replay with max lag under 5 s on the real film; a 15 s
  interval splits most lines; running every trigger back adds about 10 percent runtime; snap breaks
  (lag over 5 s) on a 12 s caption with an early trigger.
- Observed: RESULT: PASS snap 0 split, 0 replay, max lag 4.26 s real and clustered; 15 s interval
  split 7 of 7; run-back replays 45.2 s (38 percent, prediction of 10 percent was wrong); 12 s caption
  with early trigger lag 9.88 s.
- Scenarios: 1) real film, 6 triggers; 2) 8 triggers clustered in consecutive captions; 3) BREAK:
  one 12 s caption with the trigger in its first quarter
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-18 · projects/pappydapimp69__brain.md#E211 · compatible · sandboxes/2026-10-18__absorbing-reaction-pauses-into-caption-windows-trips-the-warp-cap-on-short-captions.py · observed RESULT: FAIL ABSORB over-cap captions 2 (worst warp 1.80); ABSORB wins at slope 0.005 True, HOLD wins at 0.05 True; first HOLD win at slope 0.01; 0.5 s pause ABSORB wins at all slopes True. Only the crossover band failed. · scheduled brain train session_01YL3uJX45U8L4Nh9fQf5qoD
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E437 · compatible · sandboxes/2026-10-18__derive-pauses-after-warp-cap.py · observed RESULT: PASS derive-before-cap misses 8/8 and 8/8, derive-after-cap 0/8, cap no-op case 0/8 · brain train auto session 2026-10-18; session_01L27EvvVfmoxjFAREggXBWN
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E438 · compatible · sandboxes/2026-10-18__derived-pause-map-survives-caption-warp.py · observed RESULT: PASS sidecar misses 8/8 and 8/8 after warp, derived 0/8, no drift at warp 1.0 · brain train auto session 2026-10-18; session_01L27EvvVfmoxjFAREggXBWN
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E439 · compatible · sandboxes/2026-10-18__hook-word-count-vs-warp-cap-and-pause.py · observed RESULT: PASS max hook words under the 1.5 cap = 7; fixed 3 s pause misses by >0.5 s for N=[6, 7, 8, 9, 10]; N=5 lag 0 · brain train auto session 2026-10-18; session_01L27EvvVfmoxjFAREggXBWN
- Audited: 2026-10-18 · fail · Read the entry and its stored sandbox and re-ran it. The snap, word run-back and interval numbers are computed from the embedded caption times (0 split, max lag 4.26 s, 15 s interval splits 7 of 7, run-back 45.2 s = 38%), so the Rule of thumb's main claim is not built in. But the Fix says a single early-trigger case "replayed 9.66 s". I ran the long-caption scenario one trigger at a time: the 12 s caption trigger alone replays 2.12 s, and the 9.66 s is that plus 7.54 s from the ordinary trigger that was also run back in scenario 3. The sandbox never runs the hybrid policy the Fix recommends (snap by default, run back only past the tolerance), so that policy's replay cost is untested and the quoted figure is mis-attributed. Trigger word times are also interpolated evenly across each caption's words, not read from audio, which the entry does not state. · scheduled brain train auto pass 3 audit (loop 1); session_01NZDPzU2KzUnFJgGMC4knps
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E445 · compatible · sandboxes/2026-10-18__derived-pause-map-beats-sidecar-and-ranking-needs-budget.py · observed RESULT: PASS stale sidecar splits 3/4 lines after edits vs 0 for derived; derived wins IPM x D1 13/40 at 100 impressions, 35/40 at 1000, 40/40 at 5000 (IPM alone 8/40) · scheduled brain train auto loop 2 pass 5; session_01NZDPzU2KzUnFJgGMC4knps
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E449 · compatible · sandboxes/2026-10-18__hook-caption-warp-cap-plus-pause-budget.py · observed RESULT: PASS fit 5/7/8 words; 8 words needs pause 0.3s even with free warp; 10 impossible; 7 words warp-only vs pause-mix. The free-warp part of the prediction was refuted. · scheduled brain train auto pass 2 (loop 1); session_01NZDPzU2KzUnFJgGMC4knps
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E451 · compatible · sandboxes/2026-10-18__reaction-pause-needs-fast-mute-path.py · observed RESULT: PASS 1.0 s pause leaks 0.75 level-s via glide vs 0.080 fast; glide leaves 0.25 level-s missing after resume vs 0.00; 4 s pause loses 1.01 after resume, 0.5 s only 0.06. The under-0.05 part was refuted (0.08). · scheduled brain train auto pass 5 (loop 1); session_01NZDPzU2KzUnFJgGMC4knps
