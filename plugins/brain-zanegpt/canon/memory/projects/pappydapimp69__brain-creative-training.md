# Pappydapimp69/brain-creative-training — lessons

Project: Pappydapimp69/brain-creative-training. Newest first.

---

## E41 — swapped name template vs lookalike name gate
- Date: 2026-10-15
- Project: pappydapimp69/brain-creative-training
- Tags: [game-ads][legal][testing][sandbox]
- What: Ran three fake-ad gates on one synthetic batch: a script-similarity check for name-swapped templates, an invented-name lookalike screen, and the kernel label audit.
- Why built: The train picker paired the one-joke-per-video kernel with the source-check lesson; the lookalike-name lesson was the untested companion.
- Design: Six invented names scored as clean and six near-copies of real titles. Six scripts that were one template with the name swapped, and six with their own joke. Script similarity was measured after stripping the game name. The name screen compared exact match, edit-style similarity at 0.85, and distinctive-word overlap. A five-pattern kernel with one renamed label was audited against its source.
- Got right: Similarity after name strip was 1.00 for the swapped template and 0.35 for own-joke scripts. Exact match caught 0 of 6 lookalikes, the edit screen caught 6 of 6 with 0 of 6 clean names flagged, and the label audit caught 1 of 5.
- Where/why it failed: Nothing failed, but the lookalikes were simple near-copies of one or two characters, so the 6 of 6 is an easy case. The existing lesson found compound lookalikes defeat character checks, and none were included here, so this does not extend that finding.
- Fix: Gate the batch on script similarity first (strip the name, reject near 1.00), then the name screen with edit similarity plus distinctive words, then the label audit, and treat name hits as review prompts, not legal clearance.
- Why this fix: Each gate sees a defect the others cannot: the similarity check ignores names, the name screen ignores scripts, and the audit sees only labels.
- Rule of thumb: In a fake-ad batch, a name swapped into one template scored 1.00 script similarity against 0.35 for per-ad jokes, and exact-match name screening caught 0 of 6 simple lookalikes where edit similarity caught 6; keep the three gates separate and do not read a pass as clearance.
- Provenance (verified/assumed): Verified first-hand by running the sandbox script; the scripts and names are synthetic and compound lookalikes were not tested.
- Composed: ideas:AI-VIDEO/every-video-gets-its-own-joke-and-script, fake-ad-kernel-source-check/E1, invented-name-check-exact-match-misses-lookalikes/E1
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__swapped-name-template-vs-lookalike-name-gate.py
- Prediction: Assumption: the three defects are independent, so no gate can stand in for another. Expected swapped similarity of at least 0.99, own-joke similarity under 0.5, exact match 0 of 6, edit screen at least 5 of 6 with 0 clean flagged, and 1 of 5 labels caught. It would be wrong if own-joke scripts scored high or the edit screen flagged clean names.
- Observed: RESULT: PASS swapped sim 1.00 own 0.35; exact 0/6 edit 6/6 on lookalikes, 0/6 on clean; labels 1/5
- Scenarios: 1) name-swapped template scripts; 2) own-joke scripts (built to BREAK the similarity claim); 3) exact-match name screen on lookalikes; 4) edit screen on lookalikes and on clean names; 5) label audit of 5 patterns
- Link: brain train auto session 2026-10-15 loop 1 pass 5; session_01RMAaQPULLrY2w6iRwP967n

## E40 — engine vary label check under trope cap
- Date: 2026-10-15
- Project: pappydapimp69/brain-creative-training
- Tags: [comedy][game-ads][testing][sandbox]
- What: Ran engine rotation, the kernel label audit and the trope-cap batch ceiling together in one deterministic fake-ad batch builder.
- Why built: The train picker paired the vary-the-comic-engine path with the source-check lesson; the batch-ceiling lesson was its untested companion.
- Design: 16 engine-skeleton slots, 6 tropes, per-trope cap of 1, 2 or 3, rotation on or off, plus a 5-pattern kernel with one renamed label audited against its source.
- Got right: Batch size was 6, 12 and 16 at caps 1, 2 and 3, so rotating engines did not move the ceiling. Max same-engine run was 1 with rotation and 2 without. The audit found exactly the one renamed label.
- Where/why it failed: Nothing failed. The break attempt (rotation off, hoping the ceiling shifts) changed only the streak length, not the batch size. Caveat: the rotate/no-rotate gap rests on a stylised builder, so the size of the gap is unproven.
- Fix: Keep engine rotation as a streak control and the trope cap as the size control. Run the label audit as a separate step, because neither of the other two sees it.
- Why this fix: The three levers act on different quantities (streaks, count, label fidelity), so none can stand in for another.
- Rule of thumb: In a fake-ad batch, rotate the engine to stop streaks, set the trope cap to set size (6 x cap, max 16), and audit kernel labels against the source separately; in this sandbox the three did not interfere.
- Provenance (verified/assumed): Verified first-hand by running the sandbox script; real-world comedy quality was not tested.
- Composed: ideas:COMEDY-CRAFT/vary-the-comic-engine-not-the-topic, fake-ad-kernel-source-check/E1, batch-ceiling-trope-cap/E1
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__engine-vary-label-check-under-trope-cap.py
- Prediction: Assumption: the engine rotation constrains order only and cannot change batch size. Expected batches of 6, 12, 16 at caps 1, 2, 3, max engine run 1 with rotation and above 1 without, and exactly 1 of 5 labels mismatched. Would be wrong if rotation shifted any ceiling.
- Observed: RESULT: PASS ceilings {1: 6, 2: 12, 3: 16} engine run rotate/no-rotate 1 2 label mismatches 1
- Scenarios: 1) cap 1 rotated; 2) cap 2 rotated; 3) cap 3 rotated; 4) cap 2 rotation off (built to BREAK the independence claim); 5) label audit of 5 kernel patterns against source
- Link: brain train auto session 2026-10-15; session_01RMAaQPULLrY2w6iRwP967n

## E39 — xrun counter hides overruns behind buffer depth
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [dsp][audio][realtime][testing]
- What: A seeded model of an audio callback with rare allocation stalls, measured four ways on the same
  10-minute trace: mean callback time, a sampling profiler that sees 1 callback in 100, a per-callback
  duration log against the period, and a device xrun counter with 1, 2 or 3 periods of buffer slack.
  A soak scenario asks how often a zero-xrun test passes a callback whose stall is 100 times rarer.
- Why built: The measure-worst-case kernel had never been applied by a lesson. It names the OS xrun counter
  as the pass/fail gate, and the hidden assumption is that the counter faithfully reports callback
  overruns. A device with more buffer slack absorbs late callbacks, so the counter could read zero on the
  test rig while the same callback glitches on a user's smaller buffer.
- Design: Stdlib, seeded. Workload from local__sandbox-kernel-dsp-realtime E1's allocation design: 128
  samples at 48 kHz (2667 us period), 900 us +-10%, allocation on 30% of blocks, 0.05% stall chance (my
  assumption: uniform 0-6 ms). Xrun model: callbacks start at their period or when the previous one ends,
  an xrun when one finishes past (k + S) periods, then the stream resyncs. Soak uses 2000 seeded trials.
- Got right: E1's tail-not-mean result reproduced on its own workload: mean 900.5 us against a 2667 us
  period, worst 6880 us, 26 callbacks over the period (E1 reported 27). The 1-in-100 sampling profiler's
  max was 990 us, so it never saw a spike. At one period of slack the xrun counter matched the log
  exactly (26), confirming the counter is a faithful gate only for that buffer setting.
- Where/why it failed: The xrun counter depends on buffer depth: the same trace read 26 at S=1, 8 at S=2
  and 0 at S=3, so a rig with three periods of slack reports a clean run while 26 callbacks overran. My
  soak prediction was wrong: a 1-hour zero-xrun test passed the 100x rarer bug 23.6% of the time, below the at
  least 30% I expected, which matches exp(-1.43) for 1.43 expected overruns per hour.
- Fix: Gate on the per-callback duration log against the single-period deadline, which does not depend on
  the device's buffer depth, and use the xrun counter only on the smallest buffer setting you ship; size
  the soak from the target rate (about 3 times the mean interval between overruns), not by habit.
- Why this fix: Slack periods let late callbacks catch up, so the counter measures the device's tolerance,
  not the callback's safety; the per-callback log measures the callback itself, and a zero-count test is
  a Poisson draw whose pass rate follows the soak length.
- Rule of thumb: Gate audio on per-callback time vs one period, not the xrun count: one trace with 26
  overruns read 26, 8 and 0 xruns at 1, 2 and 3 periods of slack; a 1-in-100 sampler saw max 990 us.
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__xrun-counter-hides-overruns-behind-buffer-depth.py
  twice with byte-identical output (md5 c40abaed...); every number above is from that run. The stall
  shape and the resync rule are model inputs I chose, standing in for a real ALSA, JACK or CoreAudio device.
- Composed: ideas:DSP/real-time-buffer/measure-worst-case-not-average/xrun-counters-and-rtsan, local__sandbox-kernel-dsp-realtime/E1
- Picked-by: current-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__xrun-counter-hides-overruns-behind-buffer-depth.py
- Prediction: Written before running. Hidden assumption: the device xrun counter equals the number of
  callback overruns. Expected mean about 900 us, 20-30 overruns (E1 saw 27), S=2 about 5-8 xruns, the
  1-in-100 sampler under the period, and the 100x rarer bug passing a zero-xrun test at least 85% of
  5-minute runs and at least 30% of 1-hour runs. Proof it is wrong: equal counts at every slack depth.
- Observed: RESULT: FAIL mean 900 us of 2667; 26 callbacks over the period; xrun counter S=1 26, S=2 8,
  S=3 0 (18 overruns hidden at S=2); 1-in-100 sampler max 990 us; rare-bug zero-xrun pass rate 5 min
  89.8%, 1 h 23.6%, 10 h 0.0%. The FAIL is only the 1-hour pass-rate criterion (23.6% vs at least 30%);
  every other check held, and the criterion was left unchanged after the run.
- Scenarios: 1) E1's allocation workload, mean vs per-callback log; 2) 1-in-100 sampling profiler; 3) built
  to BREAK the counter-as-gate assumption: the same trace with 1, 2 and 3 periods of slack; 4) soak of a
  100x rarer stall over 5-minute, 1-hour and 10-hour tests, 2000 trials each.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 1 pass 5

## E38 — vertical cutdown follow pan needs per layer dither anchor
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [game-ads][dither][narrative][viewport]
- What: Re-cutting a 1-bit fixable-fail ad from 16:9 to a 9:16 crop showed two linked failures. A
  static centre crop hid the goal the player fails just short of, so the gap was lost in all 10
  cuts, beat-anchored ones included. A follow-pan kept the goal but added camera motion the static
  master never had, and the world-anchored Bayer pattern then swam on the parallax background
  layer (0.419 of its pixels flipped per camera step) while the foreground stayed at 0.
- Why built: New-half edge. Path: anchor the Bayer pattern to world space, plus tension as a rationed
  information gap. Companion: cut fail ads by beats, not clock. All three say anchor to the content,
  not the frame. The question was whether they still hold once a vertical cut-down reframes the shot.
- Design: Hand-written model: 160x90 world, 30 fps, 50x90 vertical crop. Beat sheet hook 0-3, setup
  3-8, attempt 8-20, near-win 20-22, fail 22-26, end card 26-30, cut by truncation or by beats. Goal
  at x 152, player fails at x 145. Gap kept: fail beat 2 s or more, ending within 0.5 s of the card,
  and the goal visible in 90 percent or more of fail frames. Background scrolls at 0.5x, foreground
  at 1x. Bayer index from screen x, from x plus the foreground camera (the kernel), or from each
  layer's own scrolled x. Swim: share of bits that flip between sampled frames when the camera moves.
- Got right: The beat-anchored cut and world anchoring both held where they apply: with a follow-pan,
  beat-anchored cuts kept the gap at 10, 15, 20 and 30 s while truncation kept it only at 30 s. World
  anchoring took foreground swim from 0.853 (screen-anchored) to 0. The 4x4 matrix gave 17 coverage
  levels. The static 16:9 master swam 0 under every anchoring.
- Where/why it failed: Keeping the fail beat on screen is not enough when the reframe crops out what
  the gap is about: the centre crop failed in 0 of 10 cuts. The follow-pan that fixes this exposes the
  dither, and world space is not one space: anchoring the background to the foreground camera gave
  0.419 swim, worse than screen anchoring's 0.331 on that layer, because the index moves at the
  difference of the two scroll speeds.
- Fix: Frame vertical cut-downs so the goal stays in the crop through the fail beat (follow or reframe
  per beat, not a fixed centre crop). Then anchor the Bayer index to each layer's own scrolled
  coordinate, not to one world camera, so every parallax layer is stable. Check the cut-down rather
  than the master, since a static master hides screen-anchoring bugs.
- Why this fix: Per-layer anchoring gave swim 0.000 on both layers under the same follow-pan, and the
  follow framing kept the goal visible in every fail frame. So the content-anchored rule has to be
  applied per layer for the dither, and to what is visible for the gap, not just to when it happens.
- Rule of thumb: A 9:16 cut-down of a fail ad needs the goal kept in the crop (a centre crop lost the
  gap in 0/10 cuts) and a follow-pan then makes dither swim, so anchor Bayer per parallax layer:
  foreground-world anchoring left the 0.5x layer at 0.419 swim, per-layer at 0.
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__vertical-cutdown-follow-pan-needs-per-layer-dither-anchor.py,
  which printed RESULT: PASS with 17 Bayer levels, centre crop 0 of 10 cuts keeping the gap, follow
  beat-anchored 10/15/20/30 s kept and truncated only 30 s, master swim 0, follow-pan swim screen bg
  0.331 fg 0.853, world fg 0.000 bg 0.419, per-layer 0.000 on both.
- Composed: ideas:ART/dithering/bayer-4x4-gives-17-levels-from-two-colours/anchor-the-pattern-to-world-space, ideas:SYSTEM/narrative/tension-as-information-gap/discourse-not-content, local__fail-ad-cutdowns-keep-the-gap/E1
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__vertical-cutdown-follow-pan-needs-per-layer-dither-anchor.py
- Prediction: Written before the first run. Hidden assumption: world space is one space, and keeping
  the fail beat keeps the gap. Proven wrong if a parallax layer swims under world anchoring or a
  beat-anchored cut loses the gap. Expected: 17 levels; master static swim 0 for every anchoring and
  gap kept at 30 s; centre crop loses the gap at every length; follow-pan keeps it beat-anchored at
  10/15/20/30 s and truncated only at 30 s; screen-anchored swim above 0.2 on both layers;
  world-anchored foreground 0 but background above 0.2; per-layer 0 on both.
- Observed: RESULT: PASS centre crop keeps the gap in 0/10 cuts (goal off-frame); follow-pan
  beat-anchored keeps it at 10/15/20/30 s, truncated only at 30 s; master static swim 0 everywhere;
  follow-pan swim screen bg 0.331 fg 0.853, world-anchored fg 0.000 but parallax bg 0.419, per-layer
  bg 0.000 fg 0.000. Not predicted: world anchoring made the background worse than screen anchoring.
- Scenarios: 1) static 16:9 master under three anchorings; 2) 9:16 static centre crop at 6/10/15/20/30
  s, truncated and beat-anchored, built to break the beat-anchored rule; 3) 9:16 follow-pan at the
  same lengths; 4) follow-pan swim with screen, world and per-layer anchoring, with the 0.5x parallax
  layer under world anchoring built to break the dither kernel; 5) the 6 s cut, which neither method
  fits.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 5 pass 2

## E37 — thin rim light loses its ratio in srgb downscale but not to exposure
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [cinematography][lighting][rendering]
- What: A back/rim light set on set to a rim:background ratio r was followed through a delivery
  downscale (box filter, factor 4) that makes the rim thinner than one output pixel, averaged in
  linear light and in sRGB values. A 1-px rim at 16:1 on a dark background kept only 49% of its
  excess over the background in the sRGB downscale (contrast 2.83 instead of 4.75), while an
  unclipped exposure change of plus or minus 2 stops left either result unchanged to 4e-16.
- Why built: New-half kernel pass. Path: the two sRGB-blend lessons (50% blend reads 0.214, error
  grows with colour distance) plus the three-point-lighting kernel (back light separates the subject
  by an edge; ratio, not brightness, controls contrast). This morning's E19 covered the key-to-fill
  penumbra; the back light's job lives in a thin edge, which is exactly what a resize averages away.
- Design: Stdlib script with the exact piecewise sRGB transfer functions. A 1-D row: subject side,
  rim of k high-res px at r times the background, then background, all linear and clipped at 1.
  Box downscale by F=4 either on linear values or on sRGB-encoded values. Rim contrast = peak output
  pixel over background. Sweeps: r 4/8/16, k 1/2/4, sub-pixel phase 0-3, exposure -2..+2 stops,
  backgrounds pushed into the sRGB linear toe, a high-key bright background, and the r needed to
  compensate. The box filter, the 1-D edge and the 0.02 background are model choices standing in
  for a real scaler and a real camera; nothing was measured on footage.
- Got right: Linear downscale matched the closed form (k/F)r + (1 - k/F) at every cell, so with a
  correct pipeline the rim's surviving contrast is set only by ratio and footprint. sRGB kept 71%
  of the excess at r=4, 59% at r=8, 49% at r=16 for a 1-px rim, more for wider rims (81/72/65% at
  2 px) and 100% once the rim is one output pixel wide (difference 0). The ratio-not-brightness
  rule survived the sRGB error exactly: over the power segment the curve's 1.055 scale and 0.055
  offset cancel in any weighted average, so contrast did not move with exposure (spread 4e-16).
- Where/why it failed: Ratio stops controlling contrast in two places. Clipping: at r=16 a +2 stop
  push clips the rim at 1.0 and linear contrast falls 4.75 to 3.88. The sRGB toe: with the
  background below 0.0031 linear the curve stops being homogeneous and the same r=8 rim read 2.09
  to 2.71 instead of 2.04 (up to 33% off), so in near-black low-key the sRGB result depends on
  exposure after all. A rim straddling two output pixels (k=2 at worst phase) fell to the 1-px
  numbers (sRGB 2.83 versus 5.85 aligned). My exposure-invariance prediction expected small drift;
  it was exactly zero, which I had not foreseen.
- Fix: Resize, mip and proxy-generate footage in linear light whenever a rim or hair light is
  expected to end up under an output pixel; if the pipeline cannot be fixed, the rim needs about
  twice the ratio (r=15.1 in the sRGB pipeline matched linear r=8) and must stay below clip. Judge
  separation on the delivered size, not on set or in the full-res grade.
- Why this fix: The rim's job is an edge, and an edge thinner than a pixel is a blend, which sRGB
  averaging darkens in proportion to the colour distance; a low-key rim against a dark background is
  the largest distance in the frame, so it pays most. Linear averaging keeps the on-set ratio's
  meaning, and the exposure test shows the ratio rule itself still holds above the toe and below
  clip.
- Rule of thumb: A thin rim or hair light keeps its on-set ratio through a downscale only in linear
  light: a 1-px rim at 16:1 averaged in sRGB kept 49% of its separation (2.83 vs 4.75), and only a
  rim one output pixel wide was exact; exposure changed nothing until the rim clipped or the
  background fell into the sRGB toe.
- Provenance (verified/assumed): Verified first-hand: ran
  2026-10-15__thin-rim-light-loses-its-ratio-in-srgb-downscale-but-not-to-exposure.py twice with
  byte-identical output (md5 b8d9f466...). Observed numbers: linear 4.75 vs sRGB 2.83 at r=16 k=1,
  exposure spread 4.4e-16 at r=8, clip 4.75 to 3.88, toe deviation 33%, high-key r=1.5 kept 91%,
  compensation r=15.1.
- Composed: local__sandbox-shaders-gamma/E1, local__sandbox-shaders-pipeline/E1, ideas:CINEMATOGRAPHY/lighting/three-point-lighting-key-fill-back-have-distinct-jobs/ratio-not-brightness-controls-contrast
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__thin-rim-light-loses-its-ratio-in-srgb-downscale-but-not-to-exposure.py
- Prediction: Written before running. Hidden assumption the pick rests on: an on-set ratio is a
  property of the lights, so it survives any resize. Proof it is wrong would be a large drop in
  rim contrast under sRGB averaging that vanishes once the rim spans an output pixel. Predicted:
  P1 linear contrast equals (k/F)r + (1 - k/F) exactly; P2 sRGB keeps under half the excess for a
  1-px rim at r=16 on bg 0.02; P3 an unclipped +-2 stop sweep moves the sRGB contrast by under 10%;
  P4 (break) k=F shows zero sRGB error and a clipped +2 stop rim at r=16 loses contrast.
- Observed: RESULT: PASS 1-px rim F=4 r=16 bg .02: linear 4.75 sRGB 2.83 (keeps 49% of excess);
  exposure +-2 st unclipped spread r=8 0.0%; k=F diff 0; clip +2 st linear 4.75->3.88; high-key r1.5
  keeps 91%; sRGB needs r=15.1 to match linear r=8; toe dev 33%. P2 passed narrowly (48.9% against
  a 50% bar). The toe scenario S2b and its toe dev number were added after run 1 because the
  exactly-zero exposure spread needed an explanation; no pass criterion was changed.
- Scenarios: 1) r 4/8/16 by rim width 1/2/4 px, linear vs sRGB; 2) exposure sweep -2..+2 stops at
  r=8 and r=16; 3) BREAK of ratio-not-brightness: background pushed into the sRGB toe (33% drift)
  and rim clipped at +2 stops (4.75 to 3.88); 4) BREAK of the sRGB error: rim one output pixel
  wide (exact); 5) high-key bright background r=1.5 (91% kept); 6) compensating ratio search;
  7) worst sub-pixel phase for a 2-px rim.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 4 pass 1

## E36 — test hook fast forward batches deferred sweeps so a full view rebuild oracle misses lost credit
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [testing][state][attribution][architecture]
- What: A wizard whose commit() arms deferred, idempotent complete(step) effects that carry their
  origin was tested the way the wizard lesson recommends: a hook that routes through the real
  commit() and a diff of the full view against a fresh rebuild. When the hook fast-forwarded all
  commits and swept once, the view matched the oracle and the real final state exactly, yet the
  player's credit fell from 3 to 2, because the batched sweep coalesced the player's tone override
  with the system's autofill and kept only the first origin.
- Why built: Current-half edge pass. The wizard lesson says a delegating hook plus a full-view
  rebuild oracle catches whatever a shortcut forgot; the deferred-attribution lesson says carried
  origin survives only while the sweep keeps one item per origin, and tests must compare credit,
  not state. Nobody had checked what a fast-forward hook does to sweep timing.
- Design: Stdlib, no RNG. Steps genre, tone, ending; picking a genre autofills a default tone with
  origin auto on the same tick. A sweep applies effects, sets complete[step] and credits the
  origin, deduping identical effects by key (or, as the fix, by key plus origin). Real play sweeps
  between ticks; hooks either sweep once at the end or once per commit. Oracles: the wizard
  rebuild from final answers, a replay of the same event log, and an intent ledger counting arms
  per origin at arm time. The three-step wizard and the tick schedule are my own fixture, not code
  from either source project.
- Got right: The hook that sweeps after every commit matched real play on view and credit (3/1),
  and origin-set dedupe made even the single-sweep hook credit 3/1. The state-only force hook
  still failed the view oracle, as the wizard lesson found. On a backtrack log the single-sweep
  hook kept a matching view while losing 3 of 6 credits (2/1 against real 4/2).
- Where/why it failed: The rebuild oracle cannot hold credit at all: it replays final answers under
  its own origin, so its ledger read rebuild 2, auto 1 and would flag even correct real play if
  credit were added to the view diff. And when production itself arms the override on the same
  tick as the autofill, real play loses the credit (2/1); a replay-based credit oracle agrees with
  the bug, and only the intent ledger (player armed 3) disagrees. The loss itself is built into
  the key-dedupe definition; what the run adds is that the hook's batching creates coalescing that
  tick-by-tick play never has.
- Fix: Give hooks the production sweep cadence (one sweep per tick or per commit), dedupe deferred
  effects on key plus origin, and check credit against an intent ledger recorded at arm time,
  separate from the full-view rebuild, which stays the oracle for state and view only.
- Why this fix: A rebuild from final answers throws away who did what, so no state or view oracle
  can see attribution; a replay shares the applier's dedupe; only a ledger written at arm time is
  independent of the sweep that loses the origin.
- Rule of thumb: A test hook that routes through the real transition but batches deferred sweeps
  can pass a full-view rebuild oracle while losing credit (player 3 to 2 here); keep production
  sweep cadence in hooks and check credit against an arm-time intent ledger, since a rebuild has no
  origins and a replay shares the dedupe bug.
- Provenance (verified/assumed): Verified first-hand: ran
  2026-10-15__test-hook-fast-forward-batches-deferred-sweeps-so-a-full-view-rebuild-oracle-misses-lost-credit.py,
  which printed RESULT: PASS with single-sweep hook 2/1 against real 3/1 while view and state
  matched, per-commit sweep 3/1, origin-set 3/1, rebuild ledger rebuild 2 auto 1, same-tick real
  play 2/1 with intent ledger player 3, and a backtrack loss of 3 credits.
- Composed: local__2026-10-10__deferred-effect-attribution-carry-origin-vs-apply-now-coalescing-breaks-carried-origin/E1, local__sandbox-wizard-test-hook-vs-real-transition/E1
- Picked-by: current-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__test-hook-fast-forward-batches-deferred-sweeps-so-a-full-view-rebuild-oracle-misses-lost-credit.py
- Prediction: Written before running. Hidden assumption: a full-view rebuild oracle catches whatever
  a shortcut forgot; it is wrong if a delegating hook passes it while credit differs. Predicted:
  real play credits player 3 auto 1; the force hook fails the view oracle; a single-sweep
  delegating hook passes it with credit 2/1; per-commit sweeps and origin-set dedupe restore 3/1;
  a credit check against the rebuild flags real play; same-tick real play loses credit and a replay
  oracle agrees while the intent ledger does not.
- Observed: RESULT: PASS delegating one-sweep hook passes full-view rebuild oracle (state==real) but
  credits player 2/auto 1 vs real 3/1; per-commit sweep 3/1; origin-set 3/1; rebuild has no origins
  (credit {'rebuild': 2, 'auto': 1}); same-tick real play loses too (2/1) and only intent ledger
  (player arms 3) sees it; backtrack hook loses 3 credits. Every prediction held on the first run;
  the backtrack scenario's 3-credit loss was not predicted, only its matching view.
- Scenarios: 1) real play with a sweep per tick; 2) state-only force hook (control); 3) BREAK of the
  wizard rule: delegating hook with one final sweep against the full-view rebuild oracle;
  4) delegating hook with a sweep per commit; 5) origin-set dedupe; 6) credit added to the rebuild
  oracle; 7) BREAK of the replay fix: same-tick override in real play; 8) backtrack through the
  single-sweep hook.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 4 pass 2

## E35 — surreal distance dial costs the wrong cue
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [comedy][humor][structure][simulation]
- What: The escalation-needs-matching-distance model, rerun with a perceived-wrongness term from the
  premise-design kernel: surreal or AI framing that adds distance also makes the harm matter less, so
  distance is no longer a free safe cue. A second safe cue that is not distance (a competing in-world
  norm, such as a victim who respawns) is tested as the way to keep big beats both wrong and safe.
- Why built: Bridge handoff after the current-half escalation-distance lesson held. That lesson's matched
  case was identical to no gate by construction, so distance cost nothing; the dark-humor kernel itself
  says far-away harm stops mattering, and the premise kernel says a beat needs a wrong cue as well as a
  safe cue. Composing all three asks whether turning the distance dial to the ceiling is really free.
- Design: Stdlib script, no randomness. E1's model reimplemented from its stored sandbox: habituation
  exp(-0.2 X), X += 1/(1 + I/5), response I/C, ceiling 10, six beats, gate exp(-((d_safe - I/C)/0.25)^2).
  New and assumed: perceived wrongness care(d) = 1 - kappa d, beat = h (I/C) care g. A competing-norm cue
  n adds to the gate's safety but not to distance, so distance drops to max(0, I/C - n). Kappa swept 0-1.
- Got right: Kappa 0 reproduces E1 exactly (matched: flat 5.11, three 3.59, mild 1.77). Matched distance
  keeps flat-at-ceiling best up to kappa 0.7 (1.53 vs three 1.34), so E1's go-big result survives a
  moderate wrongness cost. A competing-norm cue of 0.4 lifts flat from 2.04 to 3.27 at kappa 0.6 and at
  kappa 0.9 restores flat as best (2.35 against matched-distance mild 1.13).
- Where/why it failed: My predicted flip near kappa 0.5 was wrong: flat stopped winning only at kappa 0.8
  (mild 1.21 vs flat 1.02) and scores 0.00 at kappa 1.0. My S3 check at kappa 0.6 was too weak, since flat
  was already best there; S3b at kappa 0.9 was added after the first run. The care form and its slope are
  assumptions, so only the direction and the existence of a flip are findings.
- Fix: When escalating a dark beat to the ceiling, do not buy all of its safety with surreal distance;
  carry part of it with a cue that leaves the harm mattering (an in-world rule that the victim respawns,
  deserves it or chose it) and keep mild beats close, never on full surreal framing.
- Why this fix: Distance pays for safety with wrongness, so at the ceiling it can cancel the violation it
  is protecting; a competing-norm cue adds safety without muting the violation, so both cues the premise
  kernel needs are present at the same moment.
- Rule of thumb: Surreal distance is not a free safe cue: if it mutes the harm, go-big under matched distance
  lost to mild from kappa 0.8 on, while a 0.4 competing-norm cue restored it (2.35 vs 1.13).
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__surreal-distance-dial-costs-the-wrong-cue.py
  twice with byte-identical output (md5 eb34965b...); every number above is from that run, and the
  kappa 0 row matches E1's published 5.11. The care form, its slope and the norm size are my inputs.
- Composed: ideas:COMEDY/dark-humor/severe-harm-needs-distance-mild-harm-needs-closeness/use-surreal-or-ai-framing-as-the-distance-dial, local__escalation-needs-matching-distance/E1, ideas:COMEDY/premise-design/an-absurd-premise-needs-a-wrong-cue-and-a-safe-cue/weirdness-alone-is-not-a-joke
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__surreal-distance-dial-costs-the-wrong-cue.py
- Prediction: Written before running. Hidden assumption in E1: distance makes a beat safe without making it
  matter less. Expected kappa 0 to reproduce E1 (flat 5.11), flat to stop winning near kappa 0.5, a 0.4
  norm cue to make flat best again at kappa 0.6, and mild beats on full surreal distance to keep under 0.3
  of their matched value. Proof it is wrong: flat staying best at every kappa.
- Observed: RESULT: PASS kappa=0 reproduces E1 (matched flat 5.11); flat-at-ceiling stops winning under
  matched distance at kappa=0.8 (mild 1.21 vs flat 1.02); at kappa 0.6 a competing-norm cue n=0.4 lifts
  flat 3.27 vs matched 2.04; at kappa 0.9 it restores flat as best (2.35 vs matched mild 1.13); mild on
  full surreal distance keeps 0.003 of matched. The S3b kappa 0.9 check was added after the first run.
- Scenarios: 1) kappa 0, reproducing E1; 2) built to BREAK E1's matched-distance result: kappa swept 0 to
  1; 3) competing-norm cue at kappa 0.6 and (added) 0.9; 4) mild beats on full surreal distance, the
  weirdness-alone case.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 1 pass 2

## E34 — stream tap survives redesign until schema or pause breaks it
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [voice][automation][browser][testing]
- What: A hand-written model of automating a TTS web UI compared a selector scraper with a tap on
  the page's own audio stream. A markup redesign (hashed class names, extra wrappers) took the
  scraper from 100 to 0 percent capture while the stream tap stayed at 100; a renamed stream message
  type then took the tap to 0 percent while it still reported a normal end of stream.
- Why built: Current-half kernel pass on intercept-the-stream-not-the-dom, which no lesson had applied.
  The kernel promises robustness to redesigns; the job was to reproduce that and then push the
  stream tap and the silence-based completion heuristic until they stopped holding.
- Design: 100 ms audio frames, six words with pauses between them. Stream: one message per frame,
  then 1000 ms trailing silence. Page v1 plain classes; v2 hashed CSS-module classes plus a done toast
  pre-rendered hidden; v3 keeps v2 markup but renames the audio message type and payload field. The
  tap ends a take after N ms of silence once audio began. DOM waits: a fixed 1000 ms sleep against
  six render delays (300 to 2500 ms), and insertion-based vs visibility-based waits on the toast.
- Got right: The kernel's core claim reproduced: on the redesign the selector scraper captured 0 percent
  and the stream tap 100 percent. The pocketzane E2 rule also held here: on v2 an insertion wait fired
  at 0 ms on the hidden pre-rendered toast, while a visibility wait fired at the true 1800 ms finish.
- Where/why it failed: The stream is only more stable than the DOM until the vendor changes its message
  schema: on v3 the tap kept 0 percent and returned stream-ended, which reads as success. Silence
  completion also broke: a take with one 600 ms dramatic pause kept only 50 percent of its audio at
  thresholds of 300 to 600 ms. A fixed 1000 ms sleep failed 3 of 6 renders and wasted 1050 ms.
- Fix: Make the tap strict: reject unknown message types and treat a take with zero audio frames as a
  failure, never a completion. Set the silence threshold above the longest pause the voice will
  produce (700 ms here) or prefer an explicit end-of-job message when the stream has one. Where the
  DOM must be touched, wait on a visibility change with an observer, not on node insertion or sleep.
- Why this fix: The strict tap turned the silent 0 percent into an error naming the new message type,
  which is the signal a maintainer needs. Raising the threshold to 700 ms recovered 100 percent of the
  paused take, so the cost is about 100 ms of extra end latency per take, not lost audio.
- Rule of thumb: Tapping a TTS page's stream survives a markup redesign (0 vs 100 percent capture),
  but fail loudly on unknown message types (a renamed type gave 0 percent with a normal stream end),
  and set the silence cutoff above the longest pause (a 600 ms pause cut a take to 50 percent).
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__stream-tap-survives-redesign-until-schema-or-pause-breaks-it.py,
  which printed RESULT: PASS with scraper 0 vs tap 100 percent on v2, tap 0 percent on v3 reported
  as stream-ended, strict tap erroring on audio_chunk, 50 percent kept at 400 ms, safe from 700 ms,
  sleep failing 3 of 6, insertion wait at 0 ms and visibility wait at 1800 ms.
- Composed: ideas:VOICE/automation/intercept-the-stream-not-the-dom/webui-automation-survives-redesigns, pappydapimp69__pocketzane/E2
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__stream-tap-survives-redesign-until-schema-or-pause-breaks-it.py
- Prediction: Written before the first run. Hidden assumption: the page's data stream is more stable
  than its markup. It is proven wrong if a redesign that changes the stream leaves the tap no better
  off than the scraper. Expected: v1 both 100 percent; v2 scraper 0 and tap 100; v3 tap 0 and
  reporting success unless strict; a 400 ms threshold keeps under 60 percent of a take with a 600 ms
  pause and the safe threshold is above the longest pause; a fixed 1000 ms sleep fails at least 1 of
  6 renders; an insertion wait on the hidden toast fires at 0 ms.
- Observed: RESULT: PASS redesign: scraper 0% vs stream tap 100%; schema rename: tap 0% reported
  'stream-ended' (strict: error:unknown-type:audio_chunk); silence 400 ms on a 600 ms pause keeps 50%,
  safe from 700 ms; sleep 1000 fails 3/6; hidden pre-rendered toast: insertion fires at 0 ms,
  visibility at 1800 ms. Thresholds 300 to 600 ms all kept 50 percent; 700 and 800 kept 100.
- Scenarios: 1) v1 baseline, scraper and tap both 100 percent; 2) v2 markup redesign with the stream
  unchanged; 3) v3 schema rename, built to BREAK the claim that the stream outlives the DOM; 4)
  silence-threshold sweep 300 to 800 ms on a take with a 600 ms pause, built to break the completion
  heuristic; 5) fixed sleep vs observer over six render delays; 6) insertion vs visibility wait on a
  pre-rendered hidden toast.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 5 pass 1

## E33 — squint test keeps only the value step of hue shifted shading
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [pixel-art][art][cel-shading][testing]
- What: On 16x16 sprites run through a squint test (luminance, 4x4 pooling), two poses with an
  IDENTICAL silhouette (arm across the chest versus arm hanging inside the outline) separated by
  exactly 0 under an iso-luminant hue shift, but by 0.059 to 0.167 pooled luminance under a
  hue-shifted ramp with a value step, which was more than a raised 2 px arm changed the
  silhouette (0.005 to 0.050 on mid-grey, 0/5 colours where the silhouette won).
- Why built: New-half edge pick: hue-shift shading (cool darker shadow, warm lighter highlight),
  cel-shading E5 (Gooch cool shadows cost luminance) and the companion silhouette-first kernel
  (no amount of shading fixes an unreadable shape; validate by squinting). The chain assumes the
  silhouette carries readability and shading cannot, but the squint test only sees luminance, so
  I wanted to know what part of a shading ramp survives it.
- Design: Stdlib Python. 16x16 sprites, light from the upper left: body lit on the left, one cel
  shadow step on the right, arm takes the highlight. Poses A (arm across chest), B (arm inside the
  outline, same silhouette as A), C (arm raised outside the outline). Ramps on 5 base colours:
  flat; same-hue value ramp (0.6x / 1.3x HSV value); hue-shifted (25 deg toward blue, darker,
  shadow; 25 deg toward yellow, lighter, highlight); the same hues rescaled to equal luminance;
  2-band Gooch cel with E5's paper values. Squint = WCAG relative luminance pooled 4x4; pair
  readability = max pooled difference, 0.02 as the can-tell line. Mid-grey background, plus a
  dark background and a black-fill silhouette added after run 1.
- Got right: Flat shading gave 0 between A and B, as the silhouette kernel expects, and the
  iso-luminant hue shift also gave exactly 0 under the squint although its raw RGB difference was
  0.46: the hue component of a hue-shift ramp carries nothing a squint can see. The hue-shifted
  ramp beat the same-hue value ramp on 5/5 colours (0.059 to 0.167 against 0.030 to 0.095),
  because the cool shift also lowers luminance, which is E5's mechanism working in its favour here.
- Where/why it failed: My prediction that the silhouette change (A versus C, flat) would exceed 0.1
  and beat every shading-only difference failed on run 1: it was 0.005 to 0.050 on the mid-grey
  background, because the sprite colours sat 0.019 to 0.198 from the background's luminance
  (0.186), and a 2 px limb moves a 4x4 pooled cell only a fraction of that. Added after run 1, a
  dark background raised it to 0.030 to 0.095 and a black-fill silhouette gave 0.046, still losing
  to the hue-shifted value step on 5/5 colours in both. A value-carried internal form read better
  than a thin silhouette change, so shading did fix an identical-silhouette pose.
- Fix: Treat the squint test as a luminance test of the whole sprite on its real background, not a
  silhouette-only gate: check figure-ground luminance gap first, make limbs that must read at
  least as wide as a squint cell, and when a pose lives inside the outline give it a value step
  (highlighted limb on a shadowed body), never a hue-only change.
- Why this fix: Pooled luminance is all the squint keeps, so any cue survives in proportion to its
  luminance difference times its pixel area; a silhouette is just one such cue whose contrast is
  set by the background, and a hue shift contributes only its incidental value change.
- Rule of thumb: The squint test sees only luminance: an iso-luminant hue shift separates
  identical-silhouette poses by 0, while a hue-shifted value step separates them by 0.059-0.167,
  beating a 2 px silhouette change (0.005-0.050) on 5/5 colours; give inner poses a value step.
- Provenance (verified/assumed): Verified first-hand: ran
  2026-10-15__squint-test-keeps-only-the-value-step-of-hue-shifted-shading.py and read flat A/B 0,
  iso-luminant A/B 0 with raw RGB diff 0.46, value ramp 0.030-0.095, hue-shifted 0.059-0.167 (5/5
  above value), Gooch 0.048-0.091, silhouette A/C 0.005-0.050 on mid-grey, 0.030-0.095 on dark,
  black fill 0.046, silhouette beating hue shift 0/5 on both backgrounds.
- Composed: ideas:ART/pixel-art/hue-shift-shading-scaled-to-sprite-size/shadows-cooler-highlights-warmer, local__cel-shading/E5, ideas:ART/pixel-art/silhouette-first-plus-squint-test/no-amount-of-shading-fixes-an-unreadable-shape
- Picked-by: new-half
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-15__squint-test-keeps-only-the-value-step-of-hue-shifted-shading.py
- Prediction: Written before the first run. Hidden assumption: under a squint the silhouette carries
  the shape and shading cannot; it would be proved wrong if a shading-only difference between two
  identical-silhouette poses beat a silhouette change. Expected flat A/B 0; iso-luminant A/B under
  0.005; value and hue-shifted A/B over 0.02 with hue-shifted at least value on all colours; Gooch
  over 0.02; flat silhouette A/C over 0.1 and above every shading-only A/B difference.
- Observed: RESULT: FAIL A/B squint flat 0.000, isolum max 0.0000 (raw RGB diff 0.46), value min
  0.030, hueshift min 0.059 (>= value 5/5), gooch min 0.048; silhouette A/C min 0.005 vs best
  shading 0.167; black-fill silhouette 0.046; silhouette beats hueshift mid-grey 0/5, dark bg 0/5.
  Every criterion held except the silhouette one; criteria were not changed. The dark background,
  black-fill and win-count lines were added after run 1 as extra reporting, not as criteria.
- Scenarios: 1) flat ramp, identical silhouettes A/B; 2) same-hue value ramp and hue-shifted ramp
  A/B on 5 colours; 3) iso-luminant hue shift A/B; 4) Gooch 2-band cel A/B (E5 values);
  5) BREAK: silhouette change A/C with flat colour, built to show the silhouette dominates the
  squint, on mid-grey, dark background and black fill (it did not).
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 3 pass 2

## E32 — slow delivery rescues reverb only beyond critical distance
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [speech][voice][acoustics][sandbox]
- What: In a modelled room with RT60 1.5 s, halving a speaker's syllable rate from 4 to 2 per second
  raised the syllable-envelope modulation depth from 0.355 to 0.596 for a listener well beyond the
  critical distance (direct-to-reverberant -10 dB) but only from 0.826 to 0.875 for a close one
  (+6 dB); a 10 dB louder voice changed reverb-only depth by nothing (7.8e-16), and in a dry room
  with noise at 0 dB SNR slowing did nothing either (0.500 at both rates).
- Why built: New domain, Voice and speech: the usual advice to a speaker in a live, echoing hall is
  slow down and speak up. Reverb and noise blur speech by different mechanisms, so I wanted to see
  which remedy acts on which, and how much the listener's distance decides it, with numbers.
- Design: Stdlib Python intensity-envelope model in the Houtgast and Steeneken modulation-transfer
  style. Syllables are sin squared pulses over 60% of each period with a 40% gap, at a 1 kHz
  envelope rate. The room is a direct fraction d plus an exponential tail decaying 60 dB in RT60,
  run exactly as a one-pole filter; steady noise is set by SNR against mean speech intensity.
  After 12 s warm-up, measured over the last 8 periods: modulation depth at the syllable rate
  (output over input), valley-to-peak ratio, and a single-band transmission index (apparent SNR
  clipped to plus or minus 15 dB), checked against the closed-form transfer function. The
  envelope shape, single-band TI and exponential-tail room are my modelling choices; no recorded
  speech or measured hall was used.
- Got right: Measured depth matched theory within 0.27% everywhere, and the far listener gained
  0.241 depth (TI 0.41 to 0.56) from halving the rate, the gap between syllables reopening from a
  valley-to-peak of 0.271 to 0.081. Loudness is exactly scale-invariant against reverb, and only
  helps against noise: SNR 10 to 20 dB moved depth 0.323 to 0.352, never past the reverb-only
  ceiling 0.355, while in the dry noisy room +10 dB moved it 0.500 to 0.909.
- Where/why it failed: Slowing is weak where the advice is usually given: the close listener gained
  only 0.049, and against noise in a dry room the gain was 0.000, because noise lowers depth by a
  factor that does not depend on modulation rate. Even for the far listener, keeping TI at 0.6 or
  more needed 1.5 syllables per second or slower, an unnaturally slow delivery, so slowing alone
  cannot rescue a listener deep in the reverberant field.
- Fix: Diagnose before advising: if listeners are mostly near the talker or the problem is noise,
  raise level (or the mic) and leave the pace alone; if they sit far past the critical distance in
  a live room, slow down and lengthen gaps, but mainly raise the direct share (closer seating,
  a pointed loudspeaker, absorption) since pace alone needs an unusable rate.
- Why this fix: Reverb fills the gaps between syllables, a time-domain smear that only longer gaps
  or more direct sound can undo, and it scales with the signal so level cannot touch it; noise is
  a constant floor that lowers depth equally at every rate, so only a higher SNR helps.
- Rule of thumb: Slow down for reverb, speak up for noise, and only far from the talker: at RT60 1.5
  s halving 4 to 2 syl/s lifted envelope depth 0.355 to 0.596 at D/R -10 dB but 0.049 at +6 dB,
  and 0.000 against 0 dB noise; +10 dB level does nothing to reverb.
- Provenance (verified/assumed): Verified first-hand: ran
  2026-10-15__slow-delivery-rescues-reverb-only-beyond-critical-distance.py; it printed far depth
  0.355 and 0.596, close 0.826 and 0.875, theory error at most 0.27%, loudness change 7.8e-16,
  noisy depth 0.323 to 0.352, dry SNR 0 depth 0.500 at both rates and 0.909 at +10 dB, and maximum
  rates for TI 0.6 of 1.5 far and 8.0 close.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__slow-delivery-rescues-reverb-only-beyond-critical-distance.py
- Prediction: Written before the first run. Hidden assumption: slowing down is a general
  intelligibility remedy; it would be proved wrong if slowing gave little gain close to the talker
  or none against noise. Expected measured depth within 3% of the exponential theory; far listener
  about 0.37 at 4 syl/s and about 0.6 at 2; close listener gaining under 0.1 from slowing; +10 dB
  with no noise changing depth by 0; dry room at 0 dB SNR at 0.5 for both rates.
- Observed: RESULT: PASS RT60 1.5 s far(D/R -10 dB) m 4/s 0.355 -> 2/s 0.596 (+0.241),
  close(+6 dB) +0.049; theory err max 0.27%; +10 dB voice no noise dm 7.8e-16; noisy SNR10->20 m
  0.323->0.352; dry SNR0 m 0.500/0.500 at 4/2 syl/s; TI>=0.6 max rate far 1.5 close 8.0.
- Scenarios: 1) far listener (D/R -10 dB) at 4 and 2 syl/s; 2) close listener (+6 dB) at 4 and 2
  syl/s; 3) +10 dB voice with no noise and with SNR 10 dB; 4) BREAK: dry room at 0 dB SNR, built
  to show slowing is not a general fix (no gain at all); 5) sweep of the fastest rate keeping TI
  at 0.6 or more, far and close.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 3 pass 4

## E31 — seek rederives presentation from the event log not the undo stack
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [animation][state][determinism][testing]
- What: In a replay scrubber for a session recorded as a command log with undo/redo, the
  animation re-derived on seek from the authoritative undo stack matched continuous playback
  on only 72.2% of frames, because animation is kept outside history so an undone move or cast
  still played its clip. Re-deriving from the raw command log (undone commands included)
  matched 100%, and carrying the old animation matched 15.1%.
- Why built: Current-half edge pick pairing rpg-progression E3 (presentation state lives outside
  the undo history) with edge-draft-opticon-scrub E1 (on seek, every stateful presentation
  stage must be re-derived, not carried). Together they leave open what the re-derivation
  should be computed from, and the natural answer, the authoritative state at the seek
  target, is the thing E3 deliberately made presentation independent of.
- Design: Deterministic integer-frame sandbox, 20 seeds x 600 frames, random log of move, cast,
  pull, undo, redo. Animation FSM: walk loop, attack plays once then idle, idle loop; play()
  resets only on a clip change; undo/redo never touch it (E3's fix). Every frame is a seek
  target and is compared with the continuous playback view (clip, frame index). Three seek
  rules: carry the animation from the old playhead; closed-form from the move/cast commands on
  the history stack at t; closed-form from every move/cast in the raw log up to t.
- Got right: Both source lessons hold where they claim to: with undo, log re-derivation was
  frame-exact on 12000 of 12000 frames, and with undo/redo replaced by pull (no undos) the
  stack re-derivation was also 12000 of 12000, so the stack rule is not wrong in itself.
- Where/why it failed: Undo is a seek of authoritative state but not of presentation: 190
  undos removed a move or cast from the stack while the clip it started kept playing, so
  stack-based re-derivation disagreed with playback on 3336 frames (27.8%). The scrub lesson's
  fix (snap to state derived at the target) silently assumes presentation is a function of
  authoritative state, which E3 makes false the moment undo exists.
- Fix: Derive presentation on seek from the same event stream that drove it during play, which
  is the raw command log including undone commands, or record presentation triggers as their
  own log; never from the undo stack. Also make playback count integer ticks, since a float
  accumulator makes playback itself path-dependent and no closed form can match it.
- Why this fix: E3 makes presentation a function of commands issued, not commands still in
  effect, so the re-derivation input must be the issued stream; the stack only records what is
  still in effect. Integer ticks keep playback reproducible from that stream.
- Rule of thumb: When animation lives outside undo history, a seek must rebuild it from the raw
  command log, undone commands included, not from the undo stack: stack-based re-derivation
  matched playback on 72.2% of frames, log-based 100%, carried state 15.1%.
- Provenance (verified/assumed): Verified first-hand by running
  2026-10-15__seek-rederives-presentation-from-the-event-log-not-the-undo-stack.py: log 12000
  of 12000, stack 8664 of 12000, carry 1814 of 12000 with 190 undos of move/cast; no-undo
  control stack 12000 of 12000; float-accumulator playback log 10931 of 12000.
- Composed: local__sandbox-combined-rpg-progression/E3, local__sandbox-edge-draft-opticon-scrub/E1
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__seek-rederives-presentation-from-the-event-log-not-the-undo-stack.py
- Prediction: Hidden assumption tested: the scrub fix's re-derivation can be computed from the
  authoritative state at the seek target, so the two lessons compose without conflict. Proven
  wrong if stack-based re-derivation mismatches playback once undo exists. Written before the
  first run: log rule 100% with integer ticks; stack rule below 100% (guessed 70-90%) with
  undos and exactly 100% in the no-undo control; carry under 30%; float-accumulator playback
  breaks the log rule below 100%. Pass criteria fixed before running: log == all frames,
  stack < all frames, control stack == all frames.
- Observed: RESULT: PASS log re-derivation 12000/12000, stack re-derivation 8664/12000, carry
  1814/12000; no-undo control stack 12000/12000; float-accumulator playback log 10931/12000.
  The float break cost the log rule 8.9% of frames (stack fell to 67.2%), as predicted.
- Scenarios: 1) 20 seeded sessions with undo/redo, integer ticks; 2) control, the same logs with
  undo/redo replaced by pull, where the stack and the log agree; 3) BUILT TO BREAK the log
  rule: playback advances the animation with a float dt=1/60 accumulator, where even the log
  re-derivation fails on 1069 frames because playback itself depends on rounding history.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 2 pass 2

## E30 — safe area insets in css px break integer scale at fractional dpr and unsettle world dither
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [rendering][dither][viewport][mobile]
- What: A 320x180 pixel-art frame with a world-anchored Bayer 4x4 reveal was fitted inside each
  device's safe-area rect three ways: an integer scale in CSS px (the usual web layout unit), an
  integer scale in device px, and a fractional contain fit. The CSS-integer scale became 3.75 device
  px on a 125% Windows laptop with a 1280x720 panel and 2.625 on a DPR 2.625 portrait phone, giving
  column widths 1.33x and 1.50x apart and a reveal whose beats differed by up to 1.78x; the
  device-integer scale was exact (1.00 / 1.00 / 0 shimmer) on all 10 devices.
- Why built: New-half gap pass. Path: Bayer dither anchored to world space plus one-grid integer
  scale; companion: borrow broadcast safe zones, whose web analogue is safe-area-inset on notched
  screens. This morning's E16 showed a 90% shrink makes the reveal uneven and left devicePixelRatio
  out of its model; here the safe area and the integer are both in CSS px while the nearest-neighbour
  blit lands in device px.
- Design: Exact rational model. Device column width for source column x at device scale s and
  origin o = count of pixel centres in [s x + o, s (x+1) + o). Clue patch 8x8 source px, Bayer level
  1..16, camera 0..7 source px. Metrics: max/min column width, max/min newly lit area per level,
  tone shimmer across camera offsets, and the image's share of the safe rect. Origin = CSS inset
  plus centring times DPR, so it can fall between device pixels. Devices: DPR 1, 1.25, 1.5, 2,
  2.625 and 3, landscape and portrait; the viewport sizes and inset values are stand-ins for real
  hardware, and browser smoothing is outside the model.
- Got right: CSS-integer was exact at DPR 1, 2 and 3. Device-integer was exact everywhere,
  including 4 devices whose safe-area inset put the origin on a fractional device pixel: at an
  integer scale a half-open span of s pixels always holds exactly s centres, so a fractional
  origin shifts the grid but never splits a column. It also filled more of the safe rect than
  CSS-integer on the 125% 1536x864 laptop (1.00 against 0.69), retina @2 (0.90 against 0.71) and
  portrait 2.625 (0.22 against 0.17).
- Where/why it failed: My prediction that CSS-integer breaks on the 125% 1536x864 laptop missed:
  CSS floor 4 times 1.25 is the integer 5, as it is on a 1600x900 panel. At 125% a CSS scale is only
  safe when it is a multiple of 4; the 1280x720 panel (CSS scale 3, device 3.75) was added after
  the miss and broke it. Device-integer is not free: on the 2.625 landscape phone it filled 0.61
  against 0.68. Contain fit hid its mixels from the patch at 5.99 (beat 1.00 with width ratio 1.20)
  but not on phones (portrait 1.31 to 1.36). Portrait phones filled only 17 to 29% of the safe rect
  under any policy.
- Fix: Compute the integer in device pixels, floor(safe-rect size times devicePixelRatio over
  native size), then set the canvas CSS size to native times that integer divided by DPR; take the
  safe-area insets in CSS px only to define the rect. Never trust an integer computed in CSS px
  unless that integer times DPR is itself whole.
- Why this fix: Nearest-neighbour happens on the glass, so only the device-pixel scale decides
  whether every art pixel and every dither cell is the same size; the safe zone is a layout rule,
  and converting it into device units before flooring keeps both promises at once.
- Rule of thumb: Floor the pixel-art scale in device pixels, not CSS pixels: a CSS-integer fit
  inside the safe area became 3.75 at 125% (beats 1.78x apart) and 2.625 on a phone (columns 1.50x
  apart), while the device-integer scale stayed exact on 10 devices even when the inset put the
  origin between device pixels.
- Provenance (verified/assumed): Verified first-hand: ran
  2026-10-15__safe-area-insets-in-css-px-break-integer-scale-at-fractional-dpr-and-unsettle-world-dither.py
  twice with identical output (md5 8dc320a5...). Observed numbers: 125% 1280x720 panel A scale
  3.75, width 1.33, beat 1.78, shimmer 0.0356; portrait 2.625 A width 1.50 beat 1.44; device-integer
  1.00 / 1.00 / 0 on 10 devices; fills 0.69 against 1.00 and 0.68 against 0.61.
- Composed: ideas:ART/dithering/bayer-4x4-gives-17-levels-from-two-colours/anchor-the-pattern-to-world-space, ideas:ART/pixel-art/one-grid-integer-scale-no-mixels/render-low-res-then-nearest-neighbour-blit, ideas:MOTION/camera/safe-title-and-action-margins-90-93-percent/borrow-broadcast-safe-zones-for-any-cropped-or-letterboxed-viewport
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__safe-area-insets-in-css-px-break-integer-scale-at-fractional-dpr-and-unsettle-world-dither.py
- Prediction: Written before running. Hidden assumption: an integer scale computed in layout (CSS)
  units is an integer on the glass; mixels under the CSS-integer policy at a fractional DPR would
  prove it wrong. P1 CSS-integer exact at DPR 1, 2, 3; P2 CSS-integer at 125% (1536x864) width
  ratio at least 1.2 with shimmer, and at DPR 2.625 too; P3 device-integer exact everywhere,
  including a fractional device origin from the inset (built to break it); P4 device-integer fills
  the same as CSS-integer on the portrait iPhone and at least as much at 125%.
- Observed: RESULT: FAIL CSS-integer at DPR1/2/3 exact; 125%: A s5.00 width 1.00 beat 1.00 shimmer
  0.0000 fill 0.69 vs B s6 exact fill 1.00; android 2.625 land A width 1.20 shimmer 0.0249; B exact on
  all 10 devices incl 4 with fractional device origin; portrait 2.625 B fill 0.22 vs A 0.17; 125%
  1280x720 panel A s3.75 width 1.33 beat 1.78 shimmer 0.0356. FAIL is P2's 125% 1536x864 clause
  (scale came out integer); P1, P3, P4 and P2's 2.625 clause held. The 1600x900 (run 2) and 1280x720
  (run 3) 125% devices were added after the miss to find where 125% does break; criteria unchanged.
- Scenarios: 1) DPR 1, 2 and 3 controls; 2) 125% laptops at 1536x864, 1280x720 and 1024x576 CSS;
  3) 150% laptop; 4) DPR 2.625 phone landscape and portrait; 5) BREAK of the fix: safe-area insets
  that put the device-integer image on a fractional device origin; 6) contain fit for comparison;
  7) portrait (vertical) fill share of the safe rect.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 4 pass 5
- Cited-by: 2026-10-16 · projects/pappydapimp69__brainwork.md#E332 · compatible · sandboxes/2026-10-16__device-integer-scale-in-safe-box-fill-cost.py · observed RESULT: FAIL css-floor non-integer on 2 of 6, device-floor on 0 of 6, overflow 0/0 (the FAIL is the original count of 3; device-floor fill 65.8% vs 98.8% on the 1.5 phone) · brain train auto loop 2 pass 2, session 2026-10-16; session_01GUMySc86keAL33RndEKSzH

## E29 — perfect copy parody turn must beat ad skip
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [comedy][structure][simulation]
- What: A deterministic viewer-funnel model of the "copy the ad format exactly, then let it turn on
  itself" parody. Fidelity is the number of trope-unique features on screen; the payoff of the turn
  depends on whether the viewer recognised the format, and viewers who recognise it as a real ad skip
  faster. The run measures when a perfect copy beats a loose one and when that stops holding.
- Why built: The copy-then-turn kernel had never been applied by a lesson. Its evidence is self-reported
  campaign numbers, so the run asks what the shape actually depends on: a perfect copy only pays if the
  viewer is still there when the turn arrives, and a perfect copy is also exactly what ad-averse viewers
  skip, so the two pull against each other.
- Design: Stdlib script, no randomness. Recognition rates R(k) are taken from brain-creative-training E6's
  reader (0 unique features left 0/6, 1 left 15/51, 2 left 45/54, 3 left 9/9); recognition completes at
  2 s. Skip hazards are my assumptions: 0.10/s before recognition, then 0.25/s for recognisers (they
  think it is a real ad) and 0.15/s for the confused; payoff 1 for a recogniser at the turn, 0.1 for a
  non-recogniser (weirdness alone). Scenarios sweep turn time and ad-skip hazard.
- Got right: At a 3 s turn the kernel holds and fidelity is monotone: k=3 scores 0.638, k=2 0.543, k=1
  0.237, k=0 0.070, so the perfect copy beats a loose one 2.69x. A turn at 1 s, before recognition, gives
  k=3 and k=1 the same 0.090: fidelity buys nothing if the turn lands before the format is read. The
  faithful-beats-loose crossover matched the closed form T = 2 + ln(1/w)/(h_ad - h_c) to within 0.1 s.
- Where/why it failed: The claim breaks under heavy ad aversion: with recognisers skipping at 0.8/s the
  loose copy wins from a 5.6 s turn (k=3 0.0334 vs k=1 0.0415 at 6 s), at 1.2/s from 4.2 s. The peak at
  exactly the 2 s recognition point is partly built in, because the hazard rises right after
  recognition; all hazards and the 0.1 weirdness payoff are assumptions, so only the shape is a finding.
- Fix: Place the turn just after the format has been recognised (in the model, the 2 s recognition
  point), never before it and never deep into the ad; when the audience is known to skip real ads fast,
  either turn earlier or loosen the copy, because a perfect copy is exactly what they skip.
- Why this fix: Fidelity multiplies the turn's payoff only for viewers who are still watching, and the
  faithful copy wins over the loose one only while recogniser survival to the turn stays above the
  weirdness-to-turn payoff ratio, which the closed form makes a timing budget, not a style choice.
- Rule of thumb: Copy the ad exactly only if the turn lands right after recognition: a perfect copy beat a
  loose one 2.69x at a 3 s turn, gained nothing at 1 s, and under heavy ad-skipping lost from 5.6 s on.
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__perfect-copy-parody-turn-must-beat-ad-skip.py
  twice with byte-identical output (md5 8dcff892...); every number above is from that run. The
  recognition rates come from canon entry E6, and the hazards and payoffs are model inputs I chose.
- Composed: ideas:COMEDY/fake-mobile-ad/copy-the-ad-format-exactly-then-let-it-turn-on-itself/the-best-measured-parodies-subverted-a-perfect-copy, pappydapimp69__brain-creative-training/E6
- Picked-by: current-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__perfect-copy-parody-turn-must-beat-ad-skip.py
- Prediction: Written before running. Hidden assumption: the turn's payoff grows with copy fidelity and the
  viewer is still there when it lands. Expected k=3 > k=2 > k=1 > k=0 at a 3 s turn; k=3 equal to k=1 for
  a turn before recognition; faithful wins iff (h_ad - h_c)(T - 2) < ln 10, so at h_ad 0.8 a 6 s turn
  loses to the loose copy. Proof it is wrong: a loose copy winning at an early turn under moderate skip.
- Observed: RESULT: PASS perfect copy (k=3) beats loose (k=1) 2.69x at a 3 s turn; peak at the recognition
  point T=2 s (0.819), below half by T=5.0 s; a turn before recognition gives fidelity nothing; heavy
  ad-skipping (h_ad=0.8) flips it to loose-wins from T=5.6 s. Crossovers 8.6 s (h_ad 0.5), 4.2 s (1.2).
- Scenarios: 1) fidelity k=0..3 at a 3 s turn; 2) turn-time sweep 0 to 15 s for the perfect copy, incl. a
  turn before recognition; 3) built to BREAK the claim: ad-skip hazard 0.25 to 1.2/s, where the loose
  copy overtakes; 4) equal hazards, faithful never loses.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 1 pass 1

## E28 — mystery alibis solve by elimination before the pointing clue
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [writing][mystery][narrative][testing]
- What: A model of a six-suspect fair-play mystery checked when it really becomes solvable. The author
  placed the decisive pointing clue in chapter 10, but alibis plus two attribute clues ruled out every
  innocent by chapter 7. Keeping one shadow suspect who fits every clue except the pointing one held
  the solve to chapter 10. A plot that withheld the decisive clue until the reveal scored the most
  curiosity of all three.
- Why built: New-domain pass in writing and storytelling. Mystery writers judge fairness by when the
  decisive clue appears. Readers can also solve by ruling suspects out, and nobody had checked whether
  the scattered alibis and trait clues do the decisive clue's job earlier than the author meant.
- Design: Six suspects with hand, key, alibi end and a watch trait; culprit Vera; twelve chapters,
  reveal in 12. Clues are facts about the culprit; a suspect who contradicts one is out. Plots: naive
  (left-handed clue in ch 7 removes the last innocent), shadow (ch 7 clue spares Fay, who fits
  everything but the watch), unfair (watch clue only in ch 12). Readers hold every clue, or only the
  last K. Deduction point is the first chapter with one suspect left. Curiosity per chapter uses
  Kang et al.'s fitted curve with P = 1 over suspects left, an unverified transfer from trivia.
- Got right: Counting suspects left per chapter exposed the gap between intended and actual solve: the
  naive plot went 6, 5, 5, 4, 2, 2, 1 and was solved in chapter 7, three chapters before its pointing
  clue. The shadow suspect kept two candidates through chapter 9 and moved the solve to 10 as
  intended, raising the curiosity sum over chapters 1 to 11 from 8.20 to 12.36 (+51 percent).
- Where/why it failed: My break case did not break it: I expected a forgetful reader holding only the
  last 3 clues to miss the early solve, but the key and left-handed clues alone pin Vera, so readers
  holding 2 to 5 clues all solved at chapter 7 and only a 1-clue reader waited to 10. The curiosity
  curve also misleads on its own: the unfair plot scored highest (15.14) because it never closes the
  gap before the reveal.
- Fix: Before drafting, tabulate suspects left per chapter under every clue, alibis included, and find
  the first chapter with one left. If it is earlier than the pointing clue, keep a shadow suspect who
  matches every clue but the decisive one. Gate the plot on being solvable before the reveal first,
  and only then compare curiosity scores.
- Why this fix: The shadow suspect is the one change that moved the solve to the planned chapter, and
  it held for every reader memory tested. A curiosity score alone ranked the unfair plot first, so it
  has to be checked after the fair-play test, not used in its place.
- Rule of thumb: Find a mystery's deduction point by counting suspects left per chapter, alibis
  included: trait clues and alibis solved a plot at ch 7 though its pointing clue came at ch 10; one
  shadow suspect held it to 10 (+51 percent curiosity), and test fair play before scoring curiosity.
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__mystery-alibis-solve-by-elimination-before-the-pointing-clue.py,
  which printed RESULT: PASS with naive solve ch 7, shadow ch 10, unfair ch 12 and curiosity 15.14,
  memory sweep 1:10 2:7 3:7 4:7 5:7, curiosity shadow 12.36 vs naive 8.20 (+51 percent). Run 1
  printed FAIL on the last-3 reader prediction, reported below.
- Composed: ideas:ORAL-STORYTELLING/suspense/information-gap/curiosity-peaks-at-about-fifty-percent-confidence
- Sandbox: sandboxes/2026-10-15__mystery-alibis-solve-by-elimination-before-the-pointing-clue.py
- Prediction: Written before the first run. Hidden assumption: readers solve only when the decisive
  clue appears. Proven wrong if the scattered alibis and trait clues leave one suspect earlier.
  Expected: naive plot solved at ch 7; shadow at 10; unfair at 12; a reader holding only the last 3
  clues solves the naive plot at 10 (the break case); curiosity sum chapters 1 to 11 at least 20
  percent higher for shadow than naive.
- Observed: Run 1: RESULT: FAIL because the last-3 reader also solved at ch 7. The pass criterion
  was then changed after seeing that run: the last-3 check was replaced by a memory sweep (reported,
  not gated), and a check that the unfair plot scores the most curiosity was added. Run 2: RESULT: PASS
  naive plot solvable by elimination at ch 7 (pointing clue ch 10); shadow suspect holds it to ch 10;
  unfair plot ch 12 (= reveal) yet scores the most curiosity (15.14); last-3-clue reader on the naive
  plot still solves at ch 7; memory sweep {1: 10, 2: 7, 3: 7, 4: 7, 5: 7}; curiosity ch1-11 shadow
  12.36 vs naive 8.20 (+51%).
- Scenarios: 1) naive plot, ideal reader; 2) shadow-suspect plot; 3) unfair plot with the decisive
  clue only at the reveal; 4) a reader holding the last 3 clues, built to BREAK the early-solve claim
  (it did not); 5) a reader-memory sweep from 1 to 5 clues; 6) curiosity sums for all three plots.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 5 pass 4

## E27 — leading line contrast decides guide or distract in gaze model
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [photography][composition][perception][simulation]
- What: A gaze model I wrote by hand (not eye-tracking data) tested the leading-lines kernel. A line of
  mid saliency (0.4) running to a strong subject (0.8) did not speed up finding it: mean
  time-to-first-fixation went from 3.94 to 4.06 fixations. A faint subject (0.3) was found faster,
  7.25 to 6.25. The kernel's qualifier, that the effect is bigger with a prominent subject, held in
  only 3 of 9 settings. In each of those 3 the line was far dimmer than the subject (0.2 vs 0.8).
- Why built: Current-half gap pass on a kernel no lesson had applied. The kernel cites an eye-tracking
  study and says the line's power comes from a prominent subject at its end. This model's hidden
  assumption is that gaze is saliency times proximity plus a pull along the line, and the question
  was whether those rules alone reproduce the claim.
- Design: 48x32 frame, background saliency 0.05-0.15 from an integer hash, subject disc of radius 2 at
  (38, 8), line from (4, 30). Next fixation is the argmax of saliency x exp(-d/12) x (1 + beta x
  forward cosine while on the line), with inhibition of return over the last 4 fixations. 16 start
  points, 10 fixations each. Metrics: TTFF (11 if never), dwell near the subject, dwell at the line's
  end. Sweep: line saliency 0.2, 0.4 and 0.6 against beta 1, 2 and 8.
- Got right: Two parts of the kernel came out of the model. A line into an empty corner made the
  strong subject slower to find (3.94 to 5.38) and drew only 0.031 dwell at its own empty end. A
  line ending at the subject raised subject dwell (0.288 to 0.325 strong, 0.156 to 0.188 faint), in
  line with the longer viewing the study reports.
- Where/why it failed: My prediction of at least a 20 percent TTFF cut for a strong subject at line
  saliency 0.4 failed (-3 percent), and the qualifier came out reversed (strong -3, faint +14). The
  sweep shows line contrast relative to the subject decides it: strong-subject cut +19 percent at
  0.2, -3 at 0.4, -35 at 0.6. Beta barely mattered (-3 percent at both 1 and 8), so in this model a
  line guides by being a trail of moderate saliency, not by its direction.
- Fix: Treat the line as an edge to rank below the subject. Keep it clearly lower in contrast than
  the focal point, so it brings the eye near the subject without competing. Do not judge a leading
  line by whether it exists. Before trusting the kernel's claim that a prominent subject strengthens
  the effect, check the line-to-subject contrast ratio.
- Why this fix: In every setting where the line was well below the subject (0.2 vs 0.8) the
  strong-subject TTFF cut was positive (+19 to +21 percent). At 0.6 the same line cost 35 percent, the
  same ranking the edge-control kernel gives for hard edges and the focal point.
- Rule of thumb: In a saliency gaze model a leading line helps only when it is well below the subject
  in contrast: TTFF to a strong subject +19 percent at line saliency 0.2, -3 at 0.4, -35 at 0.6, and
  a faint subject gained more (+14) than a strong one (-3) at 0.4, the reverse of the kernel's
  qualifier.
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__leading-line-contrast-decides-guide-or-distract-in-gaze-model.py,
  which printed RESULT: FAIL with TTFF strong none 3.94, to subject 4.06, to empty 5.38, faint 7.25
  to 6.25, bright line 5.75, sweep +19/-3/-35 percent strong and +10/+14/+19 faint, and the qualifier
  holding in 3 of 9 settings. The gaze rules are my own model; the Design names them.
- Composed: ideas:PHOTOGRAPHY/composition/leading-lines/leading-lines-genuinely-redirect-gaze-eye-tracking-confirms-it, ideas:PAINTING/depth/edge-control/rank-edges-and-spend-hard-ones-at-the-focal-point
- Picked-by: current-half
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-15__leading-line-contrast-decides-guide-or-distract-in-gaze-model.py
- Prediction: Written before the first run. Hidden assumption: a line pulls the eye toward its end
  whatever its own contrast, and does more when the subject is prominent. Proven wrong if a line to a
  strong subject does not cut search time or if a faint subject gains more. Expected at saliency 0.4,
  beta 2: strong-subject TTFF cut of at least 20 percent; a line to an empty corner gives no cut; the
  cut is larger for strong than faint; a line brighter than the subject (1.0) raises TTFF above the
  0.4 line.
- Observed: RESULT: FAIL base l=0.4: TTFF strong none 3.94 ->subj 4.06 ->empty 5.38; faint none 7.25
  ->subj 6.25; cut strong -3% faint +14%; bright line strong 5.75; sweep: strong cut l0.2 +19% l0.4
  -3% l0.6 -35%, faint cut +10%/+14%/+19%; qualifier holds in 3/9 settings; beta 1 vs 8 at l0.4
  strong -3% vs -3%. The sweep was added after run 1 and is reported, not gated; the pass criterion
  is unchanged.
- Scenarios: 1) strong subject, no line; 2) line ending at a strong subject; 3) line into an empty
  corner; 4) faint subject with and without a line; 5) line ending where no subject is; 6) line
  brighter than the subject (1.0), built to BREAK the claim; 7) sweep of line saliency 0.2 to 0.6 and
  beta 1 to 8.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 5 pass 5

## E26 — late ideas are rarer only when the crowd shares one association ladder
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [ideation][creativity][simulation]
- What: In a model of group brainstorming, submitting each person's last three of ten ideas
  instead of their first three raised mean rarity by only 0.64 bits, while cross-striking (drop
  any idea another group member also listed, then submit) raised it by 1.78 bits over first-3.
  Both gains exist only when people share one association ladder; with idiosyncratic
  associations or a flat idea pool they shrink to 0.20 bits or less.
- Why built: New-domain pick for Ideation and originality, which held only an idea slot machine
  and a rarity-count scoring lesson. Common advice says push past your first ideas because late
  ideas are more original (the serial-order effect); I wanted to know how much that buys
  against a cheap group-side alternative, and what it rests on.
- Design: Logic model, not human data. 300 ideas with population accessibility 1/rank^s; each
  person scales it by a lognormal factor exp(sigma*z) and generates 10 ideas by sampling
  without replacement in proportion (Plackett-Luce). Rarity is -log2 of the share of a
  3000-person reference crowd listing the idea, so it averages rarity per idea as the existing
  scoring lesson advises. 200 groups of 8, three ideas submitted per person under first-3,
  last-3, or cross-strike. Four scenarios vary s (1 Zipf or 0 flat) and sigma (0.5, 1.5, 4).
- Got right: The serial-order curve is monotone on a shared ladder (3.15 bits at position 1 to
  3.93 at position 10), and cross-strike reached 100% unique-in-group ideas at 5.03 bits mean
  rarity, against 64.8% and 3.25 bits for first-3, at no extra generation cost.
- Where/why it failed: My predicted size for the late-idea gain was wrong: I expected at least
  1 bit and got 0.64 (0.61 at sigma 1.5), because ten ideas only walk a few rungs down a
  300-idea ladder; the rarest ideas in a group are the ones nobody else said, which a person
  cannot know from their own list. With a flat pool, neither rule changed rarity at all (gap
  0.00), and cross-strike there only removed duplicates without finding rarer ideas.
- Fix: When a group wants original ideas, have everyone write privately, compare lists, and
  strike anything two people wrote before choosing; use push-past-the-first-ideas as a smaller
  second lever, and first check that the prompt has an obvious shared answer ladder, since
  both levers are worth nothing when it does not.
- Why this fix: Rarity is a property of the crowd, not of one person's order; the group's own
  overlap is a direct, free sample of what the crowd finds obvious, while serial position is
  only a noisy personal proxy for it, so the group-side check measures the target directly.
- Rule of thumb: For rarer group ideas cross-strike any idea two members listed rather than just
  dropping each person's first ideas: late ideas gained 0.64 bits, striking 1.78; both fall to
  0.20 or less when associations are idiosyncratic or the pool is flat.
- Provenance (verified/assumed): Verified first-hand by running
  2026-10-15__late-ideas-are-rarer-only-when-the-crowd-shares-one-association-ladder.py: gap
  last-3 minus first-3 was 0.64 bits (shared ladder, sigma 0.5), 0.61 (sigma 1.5), 0.20
  (sigma 4), 0.00 (flat pool); cross-strike 5.03 bits against first-3 3.25 and last-3 3.89.
  These numbers are the printed output of the model run.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__late-ideas-are-rarer-only-when-the-crowd-shares-one-association-ladder.py
- Prediction: Hidden assumption tested: late ideas are rarer because everyone shares one
  ladder of obvious-to-unusual associations, so serial position stands in for crowd rarity.
  Proven wrong if the gap stays large when people are idiosyncratic or the pool is flat.
  Written before the first run: last-3 beats first-3 by at least 1 bit on the shared ladder;
  under 0.1 bit on a flat pool; under half the shared-ladder gap at sigma 4. All three were
  the pass criteria.
- Observed: RESULT: FAIL last3-first3 rarity gap: shared ladder 0.64 bits (sigma 1.5: 0.61),
  idiosyncratic sigma 4: 0.20, flat pool: -0.00; strike minus last3 on shared ladder 1.14
  bits. The two scope criteria held; only my 1-bit size guess failed. Criteria were not
  changed after the run; the cross-strike comparison was in the sandbox from the start.
- Scenarios: 1) shared ladder s=1, sigma 0.5; 2) shared ladder s=1, sigma 1.5; 3) BUILT TO
  BREAK the assumption: idiosyncratic associations, sigma 4, gap falls to 0.20 and strike
  adds 0.09; 4) BUILT TO BREAK: flat pool s=0, every rule at 4.90 bits.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 2 pass 4

## E25 — hold for the laugh resume on the decay not a fixed pause and second swells break it
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [humor][comedy][timing][simulation]
- What: A masking model of holding for a laugh: the laugh rises after the punchline and decays, and
  the next line's first second (its setup words) is scored by an SII-style audibility from the
  voice-to-laugh ratio. A fixed 1.0 s pause gave first-second audibility 0.99 after a small laugh
  but 0.79 after a medium and 0.43 after a big one; resuming when the laugh had fallen 10 dB under
  the voice gave 0.99, 0.98 and 0.97 and still came in 0.5 to 1.4 s before waiting for silence.
- Why built: New-domain pass in Comedy and humor. Existing lessons cover callbacks in clips, fake
  ads, escalation distance, laughter latency as evidence of a failed joke and the syllable budget
  of a punchline; none says when to come back in after a laugh, which is where stepped-on lines
  and dead air both come from, on stage and in a clip edit.
- Design: Stdlib, 10 ms steps, no RNG. Laugh starts 0.3 s after the punchline, rises 0.3 s to a
  peak, then falls linearly in dB to a 35 dB floor over D: small 68 dB D 1.0 s, medium 73 dB D 2.0 s,
  big 78 dB D 3.5 s; voice 65 dB. Audibility per instant clamp((SNR + 15) / 30, 0, 1), averaged
  over the first second after resuming. Policies: fixed 1.0 s pause; ride the laugh (resume when the
  laugh is X dB under the voice, X swept 0 to 20); wait for silence (within 3 dB of floor for
  0.5 s); ride plus a 0.5 s still-falling guard. Every level and decay time is my stand-in, not a
  measured audience; the audibility mapping is the SII band-audibility form as I recall it, applied
  to the whole band.
- Got right: Riding the laugh at 10 dB under the voice kept the first second at least 0.965
  audible for all three sizes, resuming at 1.00 / 1.55 / 2.48 s against 1.51 / 2.45 / 3.86 s for
  silence. The threshold sweep showed the trade: 0 dB under gave a worst case of 0.70, 5 dB 0.86,
  10 dB 0.97, 15 dB and above 1.00 at a cost of 0.4 s more hold per 5 dB on the big laugh.
- Where/why it failed: Run 1 used an exponential decay (2.7 to 7 dB/s) that kept the big laugh
  audible for 15 s; I judged that implausible and switched to the decay-time form, so the numbers
  above are run 2. My prediction that the fixed pause would waste over 0.5 s after a small laugh
  missed: the small laugh was 0.9 audible from 0.73 s, only 0.27 s before the pause ended, so the
  fixed pause errs mainly by stepping on bigger laughs. The break held: a second swell on the big
  laugh's tail (72 dB, starting at 60% of D) dropped the ride-the-laugh line to 0.62.
- Fix: Come back in on the laugh's decay, once it is about 10 dB under your voice, not after a set
  pause and not in silence; then hold the first words for half a second more and only go if the
  laugh is still falling. The 0.5 s still-falling guard caught the second swell (resumed 4.20 s,
  audibility 1.00) at a cost of 0.5 s on a plain laugh (2.98 s, 1.00).
- Why this fix: Masking depends on the laugh's level at the moment the setup words land, and that
  level is set by the size of the laugh, which no fixed pause knows. A level threshold adapts to
  the size; the falling check is needed because a laugh is not guaranteed to decay monotonically.
- Rule of thumb: Hold for a laugh by its level, not a clock: in this model a fixed 1.0 s pause left
  a big laugh's next line 0.43 audible, while resuming 10 dB under the voice kept 0.97 or better and
  beat waiting for silence by up to 1.4 s; add a 0.5 s still-falling check, because a second swell
  cut the ride-the-laugh line to 0.62.
- Provenance (verified/assumed): Verified first-hand: ran
  2026-10-15__hold-for-the-laugh-resume-on-the-decay-not-a-fixed-pause-and-second-swells-break-it.py
  twice with identical output (md5 54047a46...). Observed numbers: fixed pause 0.987 / 0.788 /
  0.433, ride 0.987 / 0.977 / 0.965, sweep worst cases 0.70 / 0.86 / 0.97 / 1.00, swell 0.62 and
  guard 1.00.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__hold-for-the-laugh-resume-on-the-decay-not-a-fixed-pause-and-second-swells-break-it.py
- Prediction: Written before running. Hidden assumption: a laugh decays monotonically after its
  peak, so the level when you resume predicts the masking of the next line; a re-swelling laugh
  that steps on a decay-timed line would prove it wrong. P1 a fixed 1.0 s pause leaves the big
  laugh's next line under 0.5 audible and wastes over 0.5 s after a small laugh; P2 resuming 10 dB
  under the voice keeps 0.9 or better for all sizes and resumes at least 1.0 s before silence on
  the big laugh; P3 (break) a second swell drops the ride-the-laugh line below 0.7.
- Observed: RESULT: FAIL fixed 1.0 s pause: big aud 0.43, small could start 0.27 s earlier; ride
  -10 dB aud small/med/big 0.99/0.98/0.97 at 1.00/1.55/2.48 s vs silence 1.51/2.45/3.86 s; second
  swell drops ride to 0.62 (guard 1.00). FAIL is P1's small-laugh half (0.27 s, not over 0.5 s); P1's
  big-laugh half, P2 and P3 held. Run 1 (exponential decay) also printed FAIL, with ride at 0.877 on
  the big laugh and the swell dying before any resume; the decay form and the swell onset were
  changed after run 1, the pass criteria were not.
- Scenarios: 1) small, medium and big laughs under a fixed 1.0 s pause; 2) ride-the-laugh at 10 dB
  under the voice; 3) wait for silence; 4) threshold sweep 0 to 20 dB; 5) BREAK: a second swell on
  the big laugh's tail against the monotonic-decay assumption; 6) the 0.5 s still-falling guard
  with and without the swell.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 4 pass 4

## E24 — geomyth majority retelling reaches millennia only with independent errors
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [narrative][research][sandbox]
- What: A transmission model for one strange, checkable story detail (a shoreline further seaward)
  shows a single retelling chain at 3% loss per teller lasts 569 years (half-life), inside the
  folklorists' 500-800 year ceiling, while strict-majority correction among 5 tellers at the same
  3% lasts 67158 years; but a shared rationalisation of 0.5% per generation caps even 9 tellers
  at 3455 years, under the 7250-year youngest dated coastal tradition.
- Why built: Current-half kernel pick: the geomythology kernel says Aboriginal coastal stories
  appear to be 7250-13070 years old and that the transmission mechanism, not the content, is the
  question, because Bartlett's serial-reproduction kernel says retelling strips the strange part
  first. I wanted numbers for what a mechanism must achieve for the dating to be possible.
- Design: Stdlib Python, exact binomial arithmetic plus a seeded Monte Carlo cross-check. Each
  generation N tellers learn from the previous consensus; each independently loses the detail
  with probability eps; the detail survives the generation if a strict majority kept it; loss is
  absorbing (rationalised versions are stable, per Bartlett); a common shock c per generation
  removes it for everyone. 25 years per generation; target 7250 years (290 generations). The
  25-year generation and the eps values are my assumptions, not data from the papers.
- Got right: The single chain lands where folklorists put the ceiling (569 years at eps 0.03), and
  independent cross-checking among tellers multiplies survival by orders of magnitude: N=5
  tolerates up to 6.4% loss per teller and N=9 up to 12.4% while still reaching 7250 years, so the
  kernel's dating is reachable without any teller being unusually accurate. The Monte Carlo
  median (252 generations) matched the analytic 262 within 3.8%.
- Where/why it failed: The rescue depends entirely on errors being independent. A common shock,
  the same rationalisation hitting every teller at once, is not corrected by any majority:
  c=0.005 gave 3288 years at N=5 and 3455 at N=9, and the ceiling for 7250 years is c at most
  0.00239 per generation, one shared rationalisation per 419 generations. Also N=3 fell just short
  (6540 years at eps 0.03; its limit is eps 0.0285), so small groups are marginal.
- Fix: When judging a claim that an oral tradition is millennia old, ask what made its tellers'
  errors independent and what shielded the strange detail from shared rationalisation (ritual
  constraint, a fixed formula, a landscape feature that keeps contradicting the drift), rather
  than asking whether individual tellers were accurate. When designing retelling chains in
  fiction or games, add parallel tellers with majority correction to model durable lore.
- Why this fix: In the model the per-teller error rate stops mattering once a majority corrects it,
  but a correlated error passes straight through any vote; so the only quantity that limits
  survival at the kernel's time scale is the rate of shared drift, which is what the evidence for
  a tradition should be tested on.
- Rule of thumb: A strange detail survives millennia of retelling only if tellers' errors are
  independent: majority-of-5 at 3% loss lasts 67158 years against 569 for one chain, but 0.5% shared
  rationalisation per generation caps any group at about 3455 years.
- Provenance (verified/assumed): Verified first-hand: ran
  2026-10-15__geomyth-majority-retelling-reaches-millennia-only-with-independent-errors.py, which
  printed single chain 569 years, N=3 6540, N=5 67158, N=7 657392, eps limits 0.0285, 0.0641,
  0.0965 and 0.1239 for N 3, 5, 7 and 9, common shock 0.005 giving 3288 and 3455 years, ceiling
  0.00239 per generation, and Monte Carlo 252 against 262 generations.
- Composed: ideas:ORAL-STORYTELLING/folklore-testimony/geomythology/coastal-traditions-appear-to-encode-events-millennia-old, ideas:ORAL-STORYTELLING/transmission/serial-reproduction/retelling-rationalises-away-the-strange-part-first
- Picked-by: current-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__geomyth-majority-retelling-reaches-millennia-only-with-independent-errors.py
- Prediction: Written before the first run. Hidden assumption: the kernel's millennia figure needs
  only accurate tellers; it would be proved wrong if a modest per-teller error rate under
  majority correction still fell short of 7250 years, or if correlated drift did not cap it.
  Expected single chain eps 0.03 half-life about 570 years (inside 500-800); N=3 about 6400 years,
  failing 7250; N=5 over 2000 generations; common shock 0.005 caps every N at 139 generations
  or fewer; Monte Carlo within 10% of analytic.
- Observed: RESULT: PASS single eps.03 569 yr; majority N3 6540 yr, N5 67158 yr; eps_max N5 0.064;
  common shock .005 caps N9 at 3455 yr; MC rel diff 0.038. All pass criteria were set before the
  run and none were changed.
- Scenarios: 1) single chain at eps 0.02, 0.03 and 0.04 (calibration to the 500-800 year
  consensus); 2) majority correction N 3, 5, 7 at eps 0.03 and the eps limit for 7250 years at N
  3 to 9; 3) BREAK: common-shock rationalisation c 0.001, 0.0024 and 0.005 at N 5 and 9, built to
  show majority correction cannot carry correlated drift; 4) Monte Carlo check of the N=3 analytic
  half-life.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 3 pass 1

## E23 — face normal extrusion gaps or doubles corners cage must match order
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [3d-modeling][texture][rendering][sandbox]
- What: In a 2D high-to-low normal bake on a hard-edged square, pushing ray origins out along the
  split FACE normals never baked the corners right: a rounded sculpt got 12.5 deg of detail
  doubled across each corner (37.6 deg once the ray distance reached every point) and a boxy
  sculpt got a 5.27 deg wedge baked by no texel, whatever the distance. A cage with the same vertex
  order gave 100% hits and a 0.45 deg worst gap on both; the same cage with its vertex list rotated
  by one sent 100% of texels to the wrong place.
- Why built: Current-half kernel pick: the baking kernel says rays go from the low poly inward, so
  a low poly that does not enclose the sculpt needs a wider ray origin (extrusion or max ray
  distance) or a cage object with identical topology to avoid hard-edge artifacts. It names both
  remedies as alternatives; I wanted to see whether extrusion alone fixes a hard edge and how
  strict identical topology is. brainwork E179 (cage must sit above every bump) is exercised too.
- Design: Stdlib Python. Low poly: square of half-size 1, four faces with split normals, 256
  texels each. Sculpts as star-shaped implicit curves: S1 rounded (r = 1.12 + 0.03 sin 12 theta,
  inside the low poly at corners, outside at mid-faces); S2 boxy (superellipse n 20, a 1.10, small
  bumps; outside the low poly everywhere). Setups: no extrusion (max 0.5); face-normal extrusion
  0.3 with max distance 0.6, and 1.0 added after run 1; explicit cage of corners scaled by 1.3 with
  rays toward the matching low-poly point; the same cage rotated by one vertex; cage offsets 0.02
  to 0.12 on S2. Hit = first outside-to-inside crossing, bisection refined. Metrics: hit rate,
  worst angular gap, per-corner overlap or gap of adjacent faces' hit intervals, wrong hits
  over 0.5 from the texel, ray skew.
- Got right: Without extrusion S1 hit 50.8% and S2 0.0%, because the texel starts inside the
  sculpt wherever the sculpt pokes out, which is the kernel's reason for a wider origin. The matched
  cage fixed both sculpts at once (100% hits, worst gap 0.45 deg, corner seams at texel spacing)
  by fanning rays up to 44.9 deg off the face normal at corners. Cage offset reproduced E179: 0.0%,
  0.0% and 3.9% hits at 0.02, 0.05 and 0.08 against a 0.10 protrusion, 100% at 0.12.
- Where/why it failed: My prediction that face-normal extrusion would hit over 99% failed: at
  max distance 0.6 S1 hit 87.9%, because near its corners the sculpt sits 0.5 inside the low poly
  along the face normal. With max 1.0 it hit 100%, but the doubled band grew from 12.5 to 37.6 deg
  per corner and 0.8% of texels hit wrong; S2's 5.27 deg missed wedge did not change at all. Parallel
  rays from two faces must double a sculpt that is rounder than the corner and miss one that is
  sharper, so extrusion and distance fix hit rate, never the hard-edge seam.
- Fix: For any low poly with hard edges, bake through an explicit cage (or averaged ray
  directions), not a face-normal extrusion; build the cage by offsetting a duplicate of the low
  poly so vertex count and order match, check that its vertex list was not reordered, and set
  the offset above the largest protrusion of the sculpt.
- Why this fix: The seam error comes from ray direction, not ray length: split normals give each
  face its own parallel set of rays, so the corner wedge is double-sampled or unsampled by geometry.
  A matched cage interpolates origins across the corner so directions turn continuously, and its
  correspondence is purely by index, which is why a one-vertex rotation sends every ray across the
  mesh.
- Rule of thumb: Face-normal extrusion cannot bake a hard corner: it doubled 12.5-37.6 deg or
  missed 5.27 deg per corner at any reach, while a same-order cage left 0.45 deg worst gap; rotate
  the cage's vertex list by one and 100% of texels bake the wrong spot.
- Provenance (verified/assumed): Verified first-hand: ran
  2026-10-15__face-normal-extrusion-gaps-or-doubles-corners-cage-must-match-order.py, which
  printed no-extrusion hits 50.8% (S1) and 0.0% (S2), extrusion S1 87.9% at max 0.6 and 100% at
  1.0 with 12.5 and 37.6 deg doubled, S2 5.27 deg missed at both, matched cage 100% and 0.45 deg on
  both at 44.9 deg skew, rotated cage 100% wrong on both, and cage offsets 0.02 to 0.12 at 0.0,
  0.0, 3.9 and 100.0% hits.
- Composed: ideas:3D-MODELING/baking/high-to-low-poly-normal-bake-casts-rays-from-low-poly-inward/cage-object-controls-ray-origin-when-the-low-poly-doesnt-enclose-the-sculpt, pappydapimp69__brainwork/E179
- Picked-by: current-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__face-normal-extrusion-gaps-or-doubles-corners-cage-must-match-order.py
- Prediction: Written before the first run. Hidden assumption: the kernel's two remedies (wider
  ray origin or a cage) are interchangeable at a hard edge; it would be proved wrong if face-normal
  extrusion left a corner gap or doubling that the cage does not. Expected no-extrusion hits near
  50% on S1; extrusion hits over 99% on both but S1 corners doubled and S2 corners missed by over
  5 deg; matched cage 100% hits with worst gap under 1 deg; rotated cage over 50% wrong; cage
  offset 0.02 under 100% hits.
- Observed: RESULT: FAIL none S1 50.8% hits; face-normal extrude S1 corners doubled 12.5..12.5
  deg, S2 corners missed 5.3..5.3 deg (max gap 5.27); S1 extrude hits 87.9% at max 0.6, 100.0% at
  max 1.0 with corners doubled 37.6 deg; matched cage S1/S2 max gap 0.45/0.45 deg at skew 44.9 deg;
  rotated cage wrong 100%/100%; S2 cage c=0.02/0.05/0.08/0.12 hits 0.0/0.0/3.9/100.0%. The FAIL is
  one criterion of mine (extrusion hit rate over 99% on S1 at max 0.6), kept unchanged; every
  other criterion held. The max 1.0 extrusion was added after run 1 as a scenario, not a criterion.
  The kernel's claim reproduced, so polarity is compatible.
- Scenarios: 1) no extrusion on S1 and S2; 2) face-normal extrusion at max 0.6 and 1.0;
  3) matched-order cage; 4) BREAK: cage with its vertex list rotated by one, built to test whether
  identical topology must also mean identical order (100% wrong); 5) cage offset sweep 0.02 to 0.12
  against a 0.10 protrusion (E179's claim).
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 3 pass 5

## E22 — elongation marks break a dictionary rhyme judge that spelling survives
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [songwriting][rhyme][suno-prompting][testing]
- What: Sung-timing marks that stretch a vowel (lo-o-ove, niiight, seeee, fe-e-el) defeat a
  phonetic dictionary rhyme judge that only strips hyphens: it lost the rhyme in 3 of 3
  elongated stanzas that a crude last-two-letters spelling judge lettered right 2 of 3 times.
  Trying each repeated-letter run at one or two letters fixes them, but goood and shooot each
  have two dictionary readings (god/good, shot/shoot) and must be flagged, not guessed.
- Why built: Half-new train pick: the hyphenate-to-slow kernel says writers mark timing inside
  words, the suno-builder judge reads rhyme from spelling, and the companion lesson says the
  cure is a phonetic judge plus two-pass letters. Nobody had checked whether the phonetic
  cure survives the timing marks that the hyphen kernel itself tells writers to type.
- Design: Hand-written toy phoneme fixture of 31 words (last stressed vowel plus coda, not
  CMUdict) and 9 four-line stanzas: 3 clean, 1 hyphen-only (to-night, a-lone), 3 with vowel
  elongations, 2 with ambiguous elongations. Six keyings feed two-pass letters (same letter
  only for perfect rhyme): spelling last-2 after stripping hyphens; phonetic after stripping
  hyphens; collapse every letter run to one; first dictionary hit over 1-or-2 letter runs;
  same with a context tie-break; and flag-when-ambiguous. One row reruns the tie-break with
  single-pass letters. Truth is two-pass lettering of the words the writer intended.
- Got right: Run-candidate expansion (each repeated letter run tried at length 1 and 2, keep
  dictionary hits) recovered every unambiguous elongation (love, night, see, moon, feel,
  alone), and flagging tokens with two hits gave 0 wrong stanzas out of 9 with 2 flagged.
  Hyphen-only timing marks were harmless to every judge (H1 right in all six columns).
- Where/why it failed: Swapping spelling for a dictionary judge is not a strict upgrade on
  lyrics: rejoin-only phonetic was wrong on 4 of 9 and every elongation fell out as unrhymed,
  while spelling still got E1 and E2 right because elongation keeps the word ending. The
  obvious normaliser, collapse runs to one letter, was the worst (6 of 9 wrong) because it
  also wrecks real doubled letters (blood to blod, see to se, moon to mon, good to god). The
  context tie-break looked best (8 of 9) but invented a rhyme in B2, reading goood/shooot as
  god/shot to match nod/hot, and single-pass letters there collapsed it further to AAAA.
- Fix: Before the phonetic lookup, strip hyphens, expand each repeated-letter run to length 1
  and 2, and keep the readings found in the dictionary; when exactly one survives use it, and
  when two survive show the word to the writer as ambiguous instead of picking one. Then run
  the phonetic judge and two-pass lettering as the companion lesson says.
- Why this fix: Elongation is the writer's timing instruction, not the word, so normalising it
  is a stage that sits before the judge; the companion showed lettering order cannot repair a
  bad judge, and here a good judge cannot repair a bad normaliser. Ambiguity is real (goood
  could be good or god), so any silent rule, fixed or context-driven, can manufacture a rhyme.
- Rule of thumb: Before a phonetic rhyme judge reads sung lyrics, un-stretch elongated vowels by
  trying each letter run at one and two letters and flag words with two dictionary readings;
  hyphen stripping alone lost all 3 elongated stanzas and collapse-to-one broke blood/see/moon.
- Provenance (verified/assumed): Verified first-hand by running
  2026-10-15__elongation-marks-break-a-dictionary-rhyme-judge-that-spelling-survives.py: of 9
  stanzas wrong, spelling 5, rejoin-only 4, collapse-to-one 6, first candidate 2, context
  tie-break 1, flag-ambiguous 0 with 2 stanzas and 4 tokens flagged. Counts apply to the toy
  31-word fixture.
- Composed: ideas:SONGWRITING/suno-prompting/hyphenate-words-to-slow-a-rushed-vocal-line/crowded-syllables-make-suno-rush-the-delivery, pappydapimp69__suno-builder/E4, local__sandbox-two-pass-letters-cannot-rescue-a-spelling-rhyme-judge/E1
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-15__elongation-marks-break-a-dictionary-rhyme-judge-that-spelling-survives.py
- Prediction: Hidden assumption tested: the companion implies a phonetic judge strictly beats a
  spelling judge, so timing marks are cosmetic once hyphens are stripped. Proven wrong if the
  rejoin-only phonetic judge loses stanzas the spelling judge keeps. Written before the first
  run: spelling wrong on at least 2 stanzas (eye-rhymes), rejoin-only phonetic wrong on at
  least 3 (every elongated stanza, predicted 5 counting both ambiguous ones), collapse-to-one
  wrong on E2 and E3, context tie-break wrong on at least 1 (B2), flag-ambiguous wrong on 0
  with 2 stanzas and 4 tokens flagged. Pass needs all four of those inequalities.
- Observed: RESULT: PASS of 9 stanzas wrong: spelling 5, phonetic rejoin-only 4, collapse-to-1
  6, first-candidate 2, context tie-break 1, flag-ambiguous 0 (flagged 2 stanzas, 4 tokens).
  Rejoin-only was 4 not my predicted 5 because in B2 finding no word at all happens to equal
  the true ABCD; spelling was 5 not 4 because it also fakes ABAB in B2 (od/ot endings).
  Collapse-to-one failed more widely than predicted (C2, C3 and B1 too, via blood and good).
- Scenarios: 1) clean stanzas with eye-rhymes and mud/blood, where spelling fails and every
  phonetic run-expanding judge is right; 2) hyphen-only timing (to-night, a-lone), harmless to
  all; 3) three vowel-elongation stanzas, where rejoin-only phonetic fails all three;
  4) BUILT TO BREAK the rule: goood/shooot with partners nod/hot, where the context tie-break
  manufactures ABAB against a true ABCD and only flagging stays correct; 5) goood/shooot with
  partners stood/root, where the tie-break is right but flagging still has to ask.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 2 pass 1

## E21 — cluster coda fork flips the shape verdict by position
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [songwriting][rhyme][tension][testing]
- What: The open question whether a cluster-coda rhyme (ask/back, last/that) is resolved or open
  decides the rhyme-scheme shape verdict in 16 of 26 typed four-line configurations that
  contain such a pair. Which way it goes depends on the pair's position: as the stanza's first
  closure (AABB lines 1-2, ABAB lines 1-3) counting it open turns STABLE into OPEN, but as
  ABBA's outer pair counting it open turns OPEN into STABLE (ask/rain/again/back).
- Why built: Half-new gap pick: two-pass lettering gives UPPERCASE to resolved pairs and the
  shape kernel reads AABB as stopping and ABBA as wistful and open; the companion lesson says
  the rhyme judge is its own stage. The judge has one open fork in the tension ledger, cluster
  codas, and nobody had measured what that fork does to the shape readout downstream.
- Design: Two-pass letters (uppercase for resolved pairs first, then lowercase assonance among
  unlettered lines) feed a shape verdict where only uppercase letters close a line: OPEN if
  the longest closure span is 3 or more, the first close is line 4, or nothing closes. Part A
  enumerates all 15 partitions of four lines with each rhyming block typed perfect, cluster
  or assonance (61 configurations) under policy R (cluster resolved) and O (cluster open).
  Part B runs 7 real-word stanzas through a hand-written 20-word phoneme fixture.
- Got right: The fork is real and position-bound, not noise: inner or late cluster pairs never
  flipped (ABBA lines 2-3, ABAB lines 2-4, AABB lines 3-4, XXAA lines 3-4), and the real-word
  stanzas matched Part A exactly, flipping in the same 3 of 7 positions with the control at
  OPEN under both policies.
- Where/why it failed: My predictions were wrong twice. I expected AABB to be immune, but with
  its first couplet as a cluster pair the open policy leaves only lines 3-4 closing, so the
  first close is line 4 and the verdict reads OPEN (3 of 7 named shapes flipped, not 2). And
  the overall flip share was 61.5%, above my 60% ceiling. The direction I expected to be
  surprising did occur, but only once in 16 flips (ABBA outer pair).
- Fix: Until the cluster-coda tension is resolved, a shape tool should compute the verdict under
  both policies and, when they disagree, print the verdict as depending on that pair, naming
  the words; a single hard-coded policy silently picks the stanza's emotional reading.
- Why this fix: The judge stage owns the cluster decision, yet the shape stage inherits it
  without seeing it, as the companion's stage split predicts; showing both readings keeps the
  writer's choice explicit instead of letting an unresolved fork decide wistful or settled.
- Rule of thumb: When a rhyme judge has an unresolved pair class like cluster codas (ask/back),
  run the shape verdict both ways: it flipped in 16 of 26 four-line cases, toward OPEN when the
  pair is the first closure and toward STABLE when it is ABBA's outer pair.
- Provenance (verified/assumed): Verified first-hand by running
  2026-10-15__cluster-coda-fork-flips-the-shape-verdict-by-position.py: flips 16/26 typed
  configurations (15 toward OPEN when cluster counts as open, 1 toward STABLE), named shapes
  3/7, real-word stanzas 3/7. The phoneme fixture is hand-written, not CMUdict.
- Composed: ideas:SONGWRITING/rhyme-tooling/two-pass-letter-assignment-keeps-schemes-legible/resolved-rhymes-claim-letters-before-assonance-does, ideas:SONGWRITING/rhyme/rhyme-scheme-shape-sets-a-songs-emotional-motion/aabb-stops-often-abba-stays-open-and-wistful, local__sandbox-two-pass-lettering-needs-scope-and-phonetic-judge/E1
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-15__cluster-coda-fork-flips-the-shape-verdict-by-position.py
- Prediction: Hidden assumption tested: the open cluster-coda question is a fine phonetic detail
  that a shape verdict can ignore, and if it matters, counting a pair open can only make a
  stanza read more open. Proven wrong if verdicts flip often, or if any flip goes toward
  STABLE. Written before the first run: of the 7 named shapes with one cluster pair exactly 2
  flip (ABAB first pair toward OPEN, ABBA outer pair toward STABLE); 20% to 60% of
  cluster-containing configurations flip. Both were the pass criteria.
- Observed: RESULT: FAIL cluster-coda policy flips the shape verdict in 16/26 typed
  configurations (1 toward open when cluster counts as resolved, 15 the other way); named
  shapes with one cluster pair flip 3/7; real-word stanzas flip 3/7. Both criteria missed (AABB
  first couplet also flips; 61.5% exceeds 60%); the hidden assumption is refuted in both
  parts. Run 1 had a fixture bug in Part B only: my cluster test matched suffix codas but not
  prefix ones, so list/this and mist/kiss lettered as assonance; I fixed the test and re-ran.
  Part A and the RESULT line were the same in both runs; criteria were not changed.
- Scenarios: 1) exhaustive 61 typed four-line configurations; 2) the four named shapes with one
  cluster pair in each position; 3) real-word stanzas (ask/back, last/that, mist/kiss,
  list/this) plus a no-cluster ABBA control; 4) BUILT TO BREAK the open-means-more-open
  intuition: ABBA with a cluster outer pair (ask/rain/again/back), which reads STABLE when the
  cluster counts as open.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 2 pass 5

## E20 — style rules as framebuffer lint localize pipeline bugs
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [art][pixel-art][rendering][testing]
- What: Wrote the Game Boy style from the style catalog as three checks on the final screen image
  (R1 only the 4 shades, R2 every art pixel an identical uniform block, R3 a camera pan shifts the
  image by exactly pan times scale) and ran it over five pipelines built from the dither and
  integer-scale recipes: the correct order and four plausible order mistakes, including the
  pixel-art kernel's own Shovel Knight example at 4.5x.
- Why built: New-half gap pass. The two path kernels give a pipeline (native resolution, world-
  anchored Bayer, nearest-neighbour integer blit) and the companion says a style is a short list
  of rules, not a vibe. The question was whether those rules, made executable, catch pipeline
  mistakes and point to the step that caused each one.
- Design: Pure-python 48x24 native scene (sky gradient plus a dark crate) in world coordinates,
  4-shade ordered dither with the 4x4 Bayer matrix. Pipelines: P0 native world-anchored dither then
  nearest x4; P1 same with a bilinear blit; P2 upscale first, dither per screen pixel; P3 native
  dither anchored to the screen; P4 correct order at nearest x4.5. R3 pans the camera 2 art
  pixels (4 at x4.5) and compares interior pixels. Extra: pans of 1 and 4 art pixels; Bayer
  2-colour level count.
- Got right: The correct pipeline passed all three rules, and each order mistake tripped a rule
  tied to its step: bilinear gave 51 values (R1) and 918 smeared art pixels (R2); screen-resolution
  dither left 1080 non-uniform art pixels (R2 only); screen-anchored dither changed 13.5% of pixels
  on a 2-pixel pan (R3 only). The x4.5 blit failed R2 alone with art pixels 4 and 5 screen pixels
  wide, so the integer-scale rule flags the kernel's own Shovel Knight example. Bayer gave 17 levels.
- Where/why it failed: R3 is blind when the pan is a multiple of the Bayer period: screen-anchored
  dither changed 50.9% of pixels on a 1-pixel pan, 13.5% on 2 and 0.000 on 4. Screen-resolution
  dither at x4 never swims at all under whole-pixel pans (0.000), because 4 screen pixels is one
  Bayer period, so only R2 sees that bug. My first run flagged R1 on every frame (I rounded to 6
  decimals then compared with 1e-9) and R3 on bilinear at 1.1% from edge clamping; both were bugs
  in my checks, now fixed.
- Fix: Turn each style rule into a framebuffer check and run the set on every build: shade count
  against the palette, block uniformity and equal widths per art pixel, and a pan test; make the
  pan test move by 1 and by 2 art pixels (never only by a multiple of the dither period); when
  shipping a non-integer scale on purpose (as Shovel Knight did), record it as a deliberate
  exception to the rule rather than deleting the rule.
- Why this fix: Each rule reads a different property (palette, grid, world anchoring), so a
  failing rule names the step that broke it, which a visual check of the whole frame does not;
  the measured period blindness shows a pan test can pass a swimming pattern unless its step is
  coprime with the matrix size.
- Rule of thumb: Run a style's rules as framebuffer checks: each Game Boy order bug tripped its own
  rule (bilinear 51 shades, screen-res dither 1080 bad blocks, x4.5 widths 4/5), but the pan test
  saw screen-anchored Bayer change 50.9% at 1 px and 0% at 4 px, so pan by 1 px.
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__style-rules-as-framebuffer-lint-localize-pipeline-bugs.py,
  which printed the counts above and RESULT: FAIL (the FAIL is three of my predictions, about which
  rules bilinear and screen-res dither trip and the size of the 2-pixel swim). Shovel Knight's 4.5x
  scale is taken from the kernel's cited source; no real engine or GPU sampler was run.
- Composed: ideas:ART/dithering/bayer-4x4-gives-17-levels-from-two-colours/anchor-the-pattern-to-world-space, ideas:ART/pixel-art/one-grid-integer-scale-no-mixels/render-low-res-then-nearest-neighbour-blit, ideas:ART/style-catalog/pick-a-named-style-and-copy-its-defining-constraints/every-style-is-a-short-list-of-rules-not-a-vibe
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__style-rules-as-framebuffer-lint-localize-pipeline-bugs.py
- Prediction: Written before the first run: P0 passes all rules; P1 bilinear fails R1 only; P2
  screen-resolution dither fails R2 and R3; P3 screen-anchored dither fails R3 only with over 30%
  of pixels changed on the pan; P4 at x4.5 fails R2 only with widths 4 and 5; Bayer gives 17 levels.
- Observed: RESULT: FAIL P0 fails none; P1 fails ['R1', 'R2']; P2 fails ['R2']; P3 fails ['R3']; P4
  fails ['R2']; bilinear 51 values, screen-anchored pan changed 0.135, x4.5 widths [4, 5]; pan of 4
  art px hides swim (0.000); Bayer 17 levels. Pan of 1 art px: screen-anchored 0.509, screen-res
  dither 0.000. P2 did not fail R3 as I predicted (my check only asserted R2), P1 also failed R2.
- Scenarios: 1) correct pipeline; 2) bilinear blit; 3) dither after upscaling; 4) screen-anchored
  dither; 5) BREAK: the kernel's own Shovel Knight 4.5x scale, built to break the integer-scale
  rule with a shipped game; 6) pan sizes 1, 2 and 4 art pixels (added after the first run);
  7) two-colour Bayer level count.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 3 pass 5

## E19 — srgb penumbra shifts shadow edge only in low key
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [cinematography][lighting][rendering]
- What: A soft shadow edge (penumbra) modelled as a coverage ramp from the fill-only side to the key-plus-fill
  side, rendered two ways: correct linear-light mixing and the common shortcut of lerping the two sRGB pixel
  values. Swept over total lighting ratios 1:1 to 16:1 to see where the gamma error lands across high-key and
  low-key looks.
- Why built: New-half edge pass joining the sRGB blend lessons (gamma E1: 50% blend reads 0.214 not 0.5;
  pipeline E1: error grows with colour distance) with the key-to-fill ratio kernel. The prediction was that
  ratio sets the colour distance across a shadow edge, so a gamma-wrong soft edge should be harmless in
  comedy high-key and visible in noir low-key.
- Design: Stdlib script with the exact sRGB transfer functions and CIE L*. Lit side fixed at 0.8 linear so
  nothing clips, shadow side 0.8/R. For each ratio it measures the max luminance error along the ramp, how far
  the half-light point and the L* midpoint move (in penumbra widths W), how much of the edge reads darker than
  its L* midpoint, and the error at the two endpoints.
- Got right: Error is 0 at 1:1 (no edge exists) and grows monotonically: 1.5:1 1% of the lit level, 2:1 3%,
  4:1 7%, 8:1 12% (0.098 absolute, 26% relative), 16:1 17%. The half-light point moves toward the lit side by
  0.030 W at 1.5:1, 0.050 W at 2:1, 0.133 W at 8:1 and 0.161 W at 16:1. Endpoints are exact (error ~1e-16), so
  the measured key-to-fill ratio is untouched and only the edge transition is wrong.
- Where/why it failed: My predicted shift above 0.15 W at 8:1 missed (0.133 W); it only passes 0.15 W at 16:1.
  A side finding: the sRGB-lerped edge reads half dark (0.47 to 0.50 of its width below the L* midpoint) at
  every ratio, while the physically right edge reads dark over only 0.34 W at 8:1 and 0.30 W at 16:1, so the
  shortcut makes low-key shadows look about 14% of a penumbra width bigger than the light really casts them.
- Fix: Mix soft-shadow coverage, light wraps and comp blurs across a shadow edge in linear light whenever the
  ratio is above about 2:1; below that the error is 3% of the lit level or less and the shortcut is harmless.
  Check a lighting setup by its edge profile, not only by lit and shadow patch readings, which stay exact.
- Why this fix: The endpoints are immune, so a ratio meter or a two-patch check never sees the error; it only
  exists inside the transition, and its size is set by the ratio the scene is lit at.
- Rule of thumb: A gamma-wrong soft shadow edge costs nothing in high-key (0 at 1:1, 3% at 2:1) but in low-key
  pulls the edge toward the light (0.133 W at 8:1, 0.161 W at 16:1) and widens the dark part of the edge by 0.14 W at 8:1,
  while lit and shadow patch levels, and so the measured ratio, stay exact; inspect the edge, not the patches.
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__srgb-penumbra-shifts-shadow-edge-only-in-low-key.py,
  output byte-identical over two runs, every number above copied from it. The linear coverage ramp and the
  0.8 lit level are model choices; it is pure math standing in for a real renderer or camera.
- Composed: sandbox-shaders-gamma/E1, sandbox-shaders-pipeline/E1, ideas:CINEMATOGRAPHY/lighting/key-to-fill-ratio-defines-high-key-vs-low-key/near-1-to-1-comedy-8-to-1-plus-noir-and-horror
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__srgb-penumbra-shifts-shadow-edge-only-in-low-key.py
- Prediction: sRGB-lerp penumbra error 0 at 1:1 and growing with ratio; at 8:1 the half-light point of the
  edge shifts more than 0.15 W toward the lit side and the max error exceeds 10% of the lit level.
- Observed: RESULT: PASS 1:1 err 0.0000; 2:1 err 0.020 shift +0.050 W; 8:1 err 0.098 (12% of lit) half-light
  shift +0.133 W L*-mid shift +0.139 W dark share 0.34->0.48; 16:1 shift +0.161 W; endpoints exact. The
  shift-above-0.15 W part of the prediction missed at 8:1.
- Scenarios: 1) 1:1 high-key with no edge (built to BREAK the claim that sRGB blending is wrong); 2) 1.5:1 and
  2:1 near-flat comedy looks; 3) 4:1 middle; 4) 8:1 noir; 5) 16:1 extreme low-key; 6) endpoint check at every
  ratio.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 2 pass 2

## E18 — split rushed line exposes midline word to two pass lettering
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [songwriting][rhyme][suno-prompting][testing]
- What: Applied the crowded-syllables kernel's shorter-lines fix the way writers usually do it,
  by splitting each 11-word line at its midpoint into two short lines, and re-lettered seven
  stanzas with a two-pass phonetic letterer. The split halves words per line (11.2 to 5.6)
  but turns every mid-line word into a line end that the letterer now judges.
- Why built: New-half pick: the hyphenate/shorter-lines kernel with suno-builder as path and the
  two-pass-lettering-needs-scope-and-phonetic-judge lesson as companion. Earlier lessons tested
  hyphenation and front-cuts; none tested splitting, which changes the number of line ends.
- Design: Hand phonetic fixture (stressed vowel plus tail) for every line-final word, family
  coda classes, two-pass letterer (resolved uppercase first, assonance lowercase among the
  still-unlettered) and a single-pass baseline. Split rule is mechanical, after word ceil(n/2),
  so the exposed word is not chosen. Six natural stanzas (AABB x2, ABAB x2, ABBA, XXAA) plus one
  stanza written with a deliberate mid-line internal rhyme (train today / far away).
- Got right: Uppercase letters were untouched on natural stanzas: 0 of 6 gained an uppercase letter
  on an exposed word, so a shape readout taken from resolved letters only (suno-builder/E9) still
  reports the written AABB/ABAB/ABBA/XXAA after the split, and words per line fell 11.2 to 5.6.
- Where/why it failed: Lowercase noise appeared in 3 of 6 natural stanzas (kept/when, wrote/liked,
  shift/it). In the XXAA stanza the exposed IH words recruited the deliberately unrhymed line
  window into an assonance group, so the line-end pattern read xaAA, not xxAA (end pattern kept
  5/6). My prediction that single-pass would break 2+ stanzas missed: it kept 5/6 too, because
  these line ends rarely share a vowel. The internal-rhyme stanza promoted today to UPPERCASE A.
- Fix: After splitting a rushed line, re-letter the whole stanza and read the shape from uppercase
  letters on the original line-end positions only; choose a split point whose last word shares no
  stressed vowel with an unrhymed line end, and treat an internal rhyme at the split as a new
  resolved stop the stanza did not have before.
- Why this fix: A split does not move the original rhyme words, so their resolved letters survive,
  but it adds new line ends; the two-pass rule only protects resolved pairs, so the added ends land
  in the assonance pass where they can pair with the open lines that give XXAA its motion.
- Rule of thumb: Splitting a rushed line at its midpoint halves words per line (11.2 to 5.6) and kept
  every resolved letter, but the exposed mid-line word took an assonance letter in 3 of 6 stanzas,
  turned XXAA's open line into xaAA, and an internal rhyme became an uppercase stop; re-letter after.
- Provenance (verified/assumed): Verified first-hand: ran the sandbox 2026-10-15__split-rushed-line-exposes-midline-word-to-two-pass-lettering.py;
  it printed words/line 11.2->5.6, two-pass end pattern kept 5/6, exposed words lettered 3/6 with 0
  uppercase, break stanza 1 uppercase promotion. Phonetics are a hand fixture; the real suno-builder
  code and Suno's sung delivery are outside this test.
- Composed: ideas:SONGWRITING/suno-prompting/hyphenate-words-to-slow-a-rushed-vocal-line/crowded-syllables-make-suno-rush-the-delivery, pappydapimp69__suno-builder/E9, local__sandbox-two-pass-lettering-needs-scope-and-phonetic-judge/E1
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__split-rushed-line-exposes-midline-word-to-two-pass-lettering.py
- Prediction: Written before the first run: two-pass keeps the original end-line uppercase pattern in
  6/6; at least 2/6 split stanzas gain a letter on an exposed word; single-pass changes the end
  pattern in at least 2/6; words/line about 11 to 5.5; the internal-rhyme stanza gets an UPPERCASE
  exposed word.
- Observed: RESULT: FAIL split at midpoint: words/line 11.2->5.6; two-pass kept end pattern 5/6,
  single-pass kept 5/6; exposed mid-line words lettered in 3/6 natural stanzas (0 uppercase);
  internal-rhyme break stanza: 1 exposed word(s) promoted to UPPERCASE, end pattern kept=True
  (the FAIL is the 6/6 and single-pass parts of my prediction; XXAA read xaAA after the split).
- Scenarios: 1) AABB stanzas S1 and S5; 2) ABAB stanzas S2 and S6; 3) ABBA S3; 4) open XXAA S4;
  5) single-pass baseline on every split; 6) BREAK: S7 written with a mid-line rhyme at the split
  point (today vs way), built to break the claim that splitting leaves resolved letters alone.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 1 pass 1

## E17 — sentence length variance is not rhythm variety
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [storytelling][prose][testing][measurement]
- What: Checked how a prose-rhythm checker should score "vary your sentence length". Spread alone
  (coefficient of variation of sentence lengths) ranked a mechanical short/long alternation as the
  most varied of four paragraphs (CV 0.74 vs 0.63 for a genuinely varied one). The obvious repair, an
  autocorrelation periodicity test, flagged all four paragraphs at paragraph size, including the
  near-monotone one (r = 1.00 at lag 4) and the varied one (0.71).
- Why built: New-domain pass for Writing and storytelling; brain query showed nothing on sentence
  rhythm, echo words or prose cadence. Style tools and editors turn "vary sentence length" into a
  spread number, and the question was whether spread measures variety at all.
- Design: Four storm paragraphs written for the sandbox with labels by construction: monotone (5-6
  words each), alternating (2-3 / 15-17), a three-sentence short-medium-long cycle, and varied.
  Metrics: CV; lag-1 autocorrelation; max |autocorrelation| over lags 1-4 at threshold 0.7. False
  positives measured on 2000 seeded random paragraphs of independent 4-28 word sentences at 6 to 48
  sentences. Added after run 1: a CV gate (below 0.2 = monotone) plus an exact-period check on
  coarse bins (short up to 6, medium 7-12, long 13+) matching on at least 80 percent of pairs at p 2 or 3.
- Got right: CV correctly put the monotone paragraph last (0.075) and lag-1 correlation caught the
  alternation at -0.99 while missing the three-cycle (-0.38), as predicted. The CV gate plus binned
  period check labelled all four paragraphs correctly (monotone, period 2, period 3, ok).
- Where/why it failed: Normalised autocorrelation divides by the variance, so on 8 near-constant
  sentences tiny 5-vs-6 word wobbles become r = 1.00, and with few pairs at long lags any paragraph
  looks periodic: random paragraphs false-flagged 36 percent at 8 sentences and 9 percent at 12, and
  stayed under 5 percent only from 16. The binned fix still false-flagged 22 percent at 8 and 9
  percent at 12, so no periodicity test is reliable on a single paragraph.
- Fix: Score rhythm in two steps: gate monotony with spread (CV below about 0.2), then test for
  mechanical patterns on coarse length bins, and run periodicity only over a scene-sized window of
  16 or more sentences; on a single paragraph show it as a hint for the writer, not a verdict.
- Why this fix: Spread answers whether lengths differ, not whether they surprise, so it rewards a
  metronome of short-long pairs; a pattern test answers the second question but needs enough
  sentences for chance repeats to be rare, which the false-positive sweep located at about 16.
- Rule of thumb: Sentence-length spread is not rhythm variety: CV ranked a mechanical short/long
  alternation above a varied paragraph (0.74 vs 0.63); check periodicity on binned lengths, and only
  over 16+ sentences (random 8-sentence paragraphs false-flag 22-36 percent).
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__sentence-length-variance-is-not-rhythm-variety.py,
  which printed RESULT: PASS with CV ranks alternating, varied, three-cycle, monotone; max-lag flags
  4/4; binned verdicts monotone, periodic2, periodic3, ok; random false positives 0.361/0.091/0.001 at
  8/12/32 for max-lag and 0.218/0.086 at 8/12 for the binned check. The paragraphs are my own and
  how readers perceive these rhythms was outside the test.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__sentence-length-variance-is-not-rhythm-variety.py
- Prediction: Written before running: CV order alternating > varied > three-cycle > monotone; lag-1
  about -1 for alternating and about -0.5 for the three-cycle (missed at 0.7); max |r| over lags 1-4
  catches both without flagging the varied paragraph; random false positives above 20 percent at 8
  sentences and under 5 percent at 32. The max-lag part was refuted: it flagged varied and monotone.
- Observed: RESULT: PASS max-lag autocorr fix refuted on paragraphs (4/4 flagged incl. monotone
  r=1.00, varied 0.71); CV gate+binned period verdicts ['monotone', 'periodic2', 'periodic3', 'ok'],
  iid FP n8 0.218 n12 0.086; CV ranks ['alternating', 'varied', 'three_cycle', 'monotone']
  (alternating CV 0.74 > varied 0.63); r1 alternating -0.99, three-cycle -0.38; iid false positives
  n8 0.361 n12 0.091 n32 0.001; <5% from n=16. Run 1 printed FAIL on the refuted max-lag prediction.
- Scenarios: 1) monotone paragraph; 2) short/long alternation, built to break CV as a variety score;
  3) three-sentence cycle, built to slip past a lag-1 test; 4) varied paragraph; 5) BREAK: random
  paragraphs at 6 to 48 sentences against both periodicity tests.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 4 pass 4

## E16 — safe zone shrink makes world dither reveal uneven
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [rendering][dither][narrative][viewport]
- What: A world-anchored Bayer 4x4 reveal of a clue, scheduled as 16 equal information beats, was
  upscaled from 320x180 to several screens. At integer scale 6 every beat lit the same screen area
  and nothing shimmered; shrinking the canvas to the 90 percent title-safe box (scale 5.4) made the
  largest beat 1.21x the smallest and the clue's tone shift by 0.0119 (about a fifth of a level) as
  the camera scrolled, even though the pattern stayed anchored to the world.
- Why built: New-half edge. Path: dithering anchored to world space plus tension as rationed
  information (a reveal paced by level changes). Companion: borrow broadcast safe zones for a
  letterboxed viewport. The cheapest way to honour a safe zone is to scale the whole frame to 90
  percent, and the question was what that does to a reveal that relies on even, stable beats.
- Design: Exact rational nearest-neighbour model: source pixel x covers the screen columns whose
  centres fall in [s x + ox, s (x+1) + ox). Clue patch 8x8 source px; level k lights the cells with
  Bayer value below k. Per camera offset 0..7 source px: beat sizes (screen px newly lit per level),
  tone error vs k/16, shimmer (spread of tone at one level across offsets) and swim (source-space
  pattern change for a 1 px scroll). Screens: 1920x1080 at 6, at 5.4 (90 percent safe shrink), at 5
  (integer floor inside the safe box), 1366x768 at 768/180, 390x844 portrait at 1.21875 and x0.9.
- Got right: World anchoring removed swim at every scale (0 source px changed vs 64 for a screen-
  anchored matrix at scale 6), and integer scales (6 and the floor 5 that fits inside the safe box)
  gave beat ratio 1.00, tone error 0 and shimmer 0, so the reveal stays one equal beat per level.
- Where/why it failed: World anchoring does not protect against a fractional scale: nearest-neighbour
  gives some source columns 5 screen px and others 6, so a beat whose new cells land on wide columns
  reveals more. Scale 5.4 gave beats 1.21x and shimmer 0.0119; 1366x768 (4.27) 1.56x and 0.0311; a
  portrait phone fit (1.22) 4.00x with tone error 0.1325 and shimmer 0.12, about two Bayer levels.
  My first swim metric was counted in source pixels and could not see this; shimmer was added after
  run 1.
- Fix: Apply the safe zone as a layout rule, not a frame scale: keep the integer scale (floor it
  if needed: 5 fits the 90 percent box on 1080p) and place the clue and text inside the title-safe
  rectangle; on screens where only a fractional fit exists, dither at screen resolution after the
  scale or use a smooth alpha ramp for the reveal instead of an upscaled Bayer pattern.
- Why this fix: An information gap paced in 16 beats only reads as even pacing if every beat adds
  the same visible area at the same tone on every device; integer scale is the condition that makes
  each source pixel the same screen size, and world anchoring alone only fixes motion.
- Rule of thumb: Do not meet a safe zone by shrinking a pixel-art frame to 90 percent: scale 5.4
  made a world-anchored Bayer reveal's beats uneven (1.21x) and its tone shimmer as the camera moved
  (phone fit 4.00x); floor to an integer scale inside the safe box (1.00x, 0 shimmer).
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__safe-zone-shrink-makes-world-dither-reveal-uneven.py,
  which printed RESULT: PASS with integer 6 at 1.00/0/0, screen-anchor swim 64, safe-shrink 5.4 at
  1.21x error 0.0147 shimmer 0.0119, floor 5 at 1.00x and phone 4.00x error 0.1325. Browser canvas
  smoothing settings and display scaling (devicePixelRatio) are outside this model.
- Composed: ideas:ART/dithering/bayer-4x4-gives-17-levels-from-two-colours/anchor-the-pattern-to-world-space, ideas:SYSTEM/narrative/tension-as-information-gap/discourse-not-content, ideas:MOTION/camera/safe-title-and-action-margins-90-93-percent/borrow-broadcast-safe-zones-for-any-cropped-or-letterboxed-viewport, pappydapimp69__brain/E184, local__film/E21
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__safe-zone-shrink-makes-world-dither-reveal-uneven.py
- Prediction: Written before running: integer scale 6 gives beat ratio 1.00, tone error 0 and swim 0
  world-anchored (screen-anchored swim above 0); the 90 percent shrink to 5.4 gives beat ratio above
  1.2 and tone error above 0.01 and swim above 0 even world-anchored; floor 5 restores 1.00/0/0;
  phone fit beat ratio at least 2. The swim part was wrong (0 at 5.4, see Observed).
- Observed: RESULT: PASS integer s6 beats 1.00/err 0/swim 0 (screen-anchor swim 64); 90% safe-shrink
  s5.4 beats 1.21x err 0.0147 swim 0 shimmer 0.0119; floor s5 1.00x; phone s1.22 beats 4.00x err
  0.1325. Also 1366x768 at 4.27: 1.56x, shimmer 0.0311; phone x0.9: 2.25x, shimmer 0.0617.
- Scenarios: 1) integer scale 6 world-anchored; 2) integer scale 6 screen-anchored (swim baseline);
  3) BREAK: 90 percent safe shrink to 5.4, built to break the world-anchor no-swim guarantee;
  4) integer floor 5 inside the safe box; 5) 1366x768 fit; 6) portrait phone fit and its 90 percent.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 4 pass 2
- Cited-by: 2026-10-16 · projects/pappydapimp69__brainwork.md#E337 · compatible · sandboxes/2026-10-16__bayer-levels-check-column-scale.py · observed RESULT: PASS integer scales worst-phase 17/17, 1.5x worst-phase 10/17, 2.5x keeps 5/17 · brain train auto pass 5 (loop 1); session_01GnLNLCEidq8XM63uFxhmgu

## E15 — render t callback verbatim only on frame grid
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [film][animation][audio][determinism]
- What: A model of the code-rendered short-film pipeline (one render(t), one dialogue table, one clock):
  frames are hashed tuples of draw parameters for a 230 s short at 24 fps (5,520 frames), audio offsets come
  from the same table at 48 kHz, and the run tests order independence, A/V quantisation, a container frame
  rate mismatch and whether a repeated callback line re-renders verbatim.
- Why built: The render-every-frame-from-code kernel had never been applied by a lesson. It promises
  identical characters, cuts on an exact frame and callbacks repeated verbatim; the run pushes each promise
  until it stops holding.
- Design: Stdlib script. A pure render(t) against a stateful renderer that integrates position by dt (an rAF
  loop habit), both rendered in order and in a seeded shuffle; A/V offset with round() and int() frame
  quantisation; frames made for 24 fps muxed as 24000/1001; the callback line placed once on the frame grid
  (40.000 s) and once 10 ms off it (61.010 s), compared frame by frame with its first use at 4.250 s.
- Got right: Pure render(t) gave 0 of 5,520 mismatches under shuffle, matching the full seek-sweep check from
  test E13; the stateful renderer mismatched 5,520 of 5,520. Round() kept A/V within 16.7 ms (bound 20.8),
  int() 25.0 ms (bound 41.7). The frame-aligned callback reproduced its first use exactly, 38 of 38 frames.
- Where/why it failed: The callback started 10 ms off the frame grid matched only 4 of 38 frames: the blip
  envelope and mouth shape are sampled at a different phase of local line time, so a verbatim line is not a
  verbatim performance. Muxing 24 fps frames as 23.976 makes audio lead by 1 ms per second: past 45 ms at
  45.0 s and 239.6 ms at 222.9 s (drift plus 16.7 ms quantisation; I predicted about 223 ms).
- Fix: Snap every dialogue table start to the frame grid (round(start*fps)/fps) before anything reads it, so
  frames and audio sample offsets come from the same snapped time; pass the exact render rate to the muxer
  (-r 24, never a default 23.976); keep render(t) free of state carried between calls.
- Why this fix: Snapping removes both the quantisation choice and the phase difference in one place, which is
  what makes a callback identical, and the rate mismatch is invisible in the first 45 s, so it survives any
  spot check of the opening and only shows near the end of a three-minute short.
- Rule of thumb: In a code-rendered film a repeated line is only a verbatim callback if its start is on the
  frame grid: 10 ms off it changed 34 of 38 frames; snap table times to whole frames, keep render(t)
  stateless (stateful 5,520/5,520 frames wrong under seek), and mux at the exact render rate (23.976 drifts
  45 ms by 45 s).
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__render-t-callback-verbatim-only-on-frame-grid.py,
  output byte-identical over two runs, every count above from it. Frames are hashed parameter tuples standing
  in for real canvas PNGs from Playwright; the 45 ms audio-lead figure is the commonly cited detectability limit,
  taken as given.
- Composed: ideas:FILM/pipeline/render-every-frame-from-code-not-from-a-video-generator/one-render-t-function-one-dialogue-table-one-clock, pappydapimp69__test/E13
- Picked-by: current-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__render-t-callback-verbatim-only-on-frame-grid.py
- Prediction: Pure render 0 mismatches under shuffle and stateful most mismatched; round() max A/V error 20.8
  ms and int() 41.7 ms; 24 vs 24000/1001 mux crosses 45 ms audio lead at about 45 s and reaches about 223 ms
  at 223 s; a callback at a non-frame-aligned start does not reproduce its first occurrence.
- Observed: RESULT: PASS pure shuffle mismatch 0/5520, stateful 5520/5520; A/V round 16.7 ms int 25.0 ms;
  23.976 mux lead 240 ms at 223 s (45 ms at 45 s); callback aligned 38/38 off-grid 4/38. The quantisation
  errors came in under the bounds I predicted because the table times only hit some phases.
- Scenarios: 1) pure render(t) in shuffled order; 2) stateful dt renderer in shuffled order (built to BREAK
  order independence); 3) one-clock A/V offset with round() and int(); 4) 24 fps muxed as 23.976 (built to
  BREAK one clock); 5) callback on the frame grid; 6) callback 10 ms off the grid (built to BREAK verbatim).
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 2 pass 5

## E14 — rarity count originality scores fluency not originality
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [ideation][creativity][evaluation][testing]
- What: Scoring originality by statistical infrequency, the Torrance-style count of a person's
  ideas that 5% or fewer of the pool also gave, mostly measures how many ideas they produced:
  in simulated pools where fluency and a hidden originality trait were independent, the count
  correlated r +0.82 with fluency and only +0.36 with originality (mean of 10 pools of 200).
  Mean rarity per idea reversed that (+0.14 fluency, +0.57 originality).
- Why built: New-domain pass in Ideation and originality. Novelty scoring is how idea sessions,
  divergent-thinking tests and idea tools rank "most original"; brain had nothing on how the
  scoring rule itself behaves, only on brainstorming formats and idea quantity.
- Design: Stdlib Python, seeded random.Random. 300 idea categories with Zipf weights (s 1.1);
  each respondent has fluency F (2 to 25 distinct ideas) and a hidden trait theta that flattens
  their draw toward rare categories (weights p to the power 1 - 0.8 theta). Scores from the
  pool's own frequencies: count of ideas at 5% or below, mean per-idea rarity (1 - share), and
  mean rarity of the two rarest ideas. Pearson r with F and with theta over 10 pools of 200 and
  10 of 20; the same 20 people ranked inside their own 20-pool and inside the 200-pool; a break
  set where theta and fluency correlate at 0.5.
- Got right: Mean per-idea rarity is close to fluency-free (+0.14 at n 200, +0.06 at n 20) and
  tracks the hidden trait (+0.57 and +0.55), and its ranking of the same 20 people moved less
  between a 20-pool and a 200-pool (Spearman 0.84) than the count's did (0.75).
- Where/why it failed: Every extra idea is another draw that can land in the rare tail, so a count
  of rare ideas rises with fluency whatever the person's originality; in 20-person pools the 5%
  cut equals "nobody else said it" and the count's link to originality fell to +0.13. The
  top-two-rarest score, meant to dodge this, was also fluency-led (+0.44 vs +0.19). My
  prediction of r 0.6 or more for mean rarity missed (0.57). When fluency and originality
  correlate (break set) the count looks valid (+0.62), which is how the confound hides.
- Fix: Rank originality by mean rarity per idea (or rate a fixed number of each person's ideas),
  report fluency beside it as its own number, and score against a reference pool of 200 or more
  rather than the session's own handful of people.
- Why this fix: Averaging divides out the number of draws, so a prolific but conventional person
  no longer outranks a sparse but unusual one, and a larger reference pool turns the 5% cut back
  into a rarity estimate instead of a uniqueness test that two people saying the same thing flips.
- Rule of thumb: Do not rank ideas or people by a count of rare ideas: it tracked fluency r +0.82 and
  originality only +0.36 (top-2 rarest +0.44/+0.19); mean rarity per idea gave +0.14/+0.57, so
  average rarity and report fluency separately.
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__rarity-count-originality-scores-fluency-not-originality.py;
  it printed the correlations above (10 seeds per condition), 20-pool vs 200-pool Spearman 0.75
  for the count and 0.84 for mean rarity, and break-set count r(originality) +0.62. The Zipf
  universe and the theta mechanism are my model of an idea pool, not data from a real test.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__rarity-count-originality-scores-fluency-not-originality.py
- Prediction: Written before the first run: rarity count r(fluency) 0.6 or more and above its
  r(originality); mean rarity r(originality) 0.6 or more with |r(fluency)| 0.2 or less; 20-pool
  vs 200-pool count Spearman under 0.8; break set count r(originality) 0.5 or more. Run 1 (one
  seed) failed only on mean rarity 0.54; added before run 2, thresholds unchanged: average all
  correlations over 10 seeds per condition.
- Observed: RESULT: FAIL n=200 mean of 10 seeds: rarity count r(fluency) +0.82 vs r(originality)
  +0.36; mean rarity r(fluency) +0.14 vs r(originality) +0.57; top2 +0.44/+0.19; 20-pool vs
  200-pool count ranking spearman 0.75 (mean rarity 0.84); n=20 pools mean rarity r(originality)
  +0.55; break corr 0.5: count r(originality) +0.62. The FAIL is only my 0.6 bar for mean rarity.
- Scenarios: 1) 10 pools of 200, fluency independent of originality; 2) 10 pools of 20; 3) the
  same 20 people scored in their own pool vs the 200 pool; 4) BREAK: fluency and originality
  correlated 0.5, built to make the count look valid (it did, +0.62).
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 5 pass 4

## E13 — mip derived albedo and f0 not basecolor and metalness
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [3d-modeling][materials][rendering]
- What: Mip-mapped (2x2 averaged) a glTF metallic-roughness footprint that mixes a gold metal texel
  with a dark blue painted dielectric, three ways: average baseColor in sRGB, average baseColor in
  linear light (the convert-to-linear kernel), or average the derived linear diffuse albedo and F0.
  Each was shaded once with Cook-Torrance and compared with the average of the two shaded texels.
- Why built: New-half kernel pass: the sRGB-lerp-is-too-dark kernel and sandbox-shaders-pipeline/E1
  say linearize before averaging colour; the companion metallic-roughness kernel stores metalness
  and roughness as separate channels beside baseColor. The question was whether linearizing
  baseColor is enough once the shader multiplies baseColor by metalness after the average.
- Design: Pure-python Cook-Torrance (Lambert, GGX D, Schlick F, Smith-Schlick G), one light, a
  diffuse-dominant view and the mirror (specular-peak) view. Per texel: diffuse = base*(1-metal),
  F0 = mix(0.04, base, metal). Four footprints: gold|paint at equal roughness 0.5; one paint at
  roughness 0.2|0.8; two near dielectrics 0.02 apart (break case); two metals with far colours.
  Error is the max relative RGB error of the mipped radiance against the supersampled truth.
- Got right: Averaging derived diffuse albedo and F0 was exact (2.6e-16) for the metal|paint
  footprint at both views, and linear baseColor was exact (0.00%) when both texels share the same
  metalness (two metals), where sRGB averaging still erred 24.45%. Near dielectrics 0.02 apart
  erred at most 0.092% under every method, as sandbox-shaders-pipeline/E1 predicts for close colours.
- Where/why it failed: Linearizing baseColor alone left 18.50% error at the diffuse view and 38.68%
  at the specular peak for the metal|paint footprint (sRGB averaging: 41.81% and 68.91%). The
  averaged metalness 0.5 times the averaged base leaks gold into the diffuse term (red albedo 0.251
  versus true 0.002) and halves the metal's F0 (red 0.271 versus 0.52). No input-space average fixes
  roughness: paint at 0.2|0.8 was still 94.98% off at the peak even with derived albedo and F0.
- Fix: When a footprint can mix metal and dielectric texels, generate mips (and filter) on the
  derived linear quantities, diffuse albedo and F0, or keep metalness binary per mip by choosing a
  dominant texel; decode baseColor to linear in all cases; treat roughness separately (widen it or
  store a variance term) because it enters the lobe nonlinearly.
- Why this fix: Shaded radiance is linear in diffuse albedo and F0 at fixed roughness, so averaging
  them equals averaging the light; baseColor and metalness are multiplied together in the shader,
  so averaging each first is the same mistake as averaging sRGB, one stage later.
- Rule of thumb: Linear-light baseColor is not enough for a metal/dielectric mip: averaging base and
  metalness separately leaked gold into diffuse (red 0.251 vs 0.002) and left 18.5% error, while
  averaging derived albedo and F0 was exact; roughness mips stayed 95% off at the highlight.
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__mip-derived-albedo-and-f0-not-basecolor-and-metalness.py,
  which printed RESULT: PASS with sRGB-base 41.8%, linear-base 18.5% and derived 2.6e-16 errors at
  the diffuse view, 95% roughness error at the peak and 0.092% for near dielectrics. The BRDF is a
  textbook model in python; no real engine or GPU mip generator was run.
- Composed: ideas:SHADERS/color-blending/convert-to-linear-before-blending-physical-light/srgb-space-lerp-is-measurably-too-dark, local__sandbox-shaders-pipeline/E1, ideas:3D-MODELING/materials/metallic-roughness-pbr-has-three-core-inputs/basecolor-plus-metalness-blue-and-roughness-green-packed-in-one-texture
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__mip-derived-albedo-and-f0-not-basecolor-and-metalness.py
- Prediction: Written before the first run: for gold|paint at equal roughness, sRGB-base error above
  linear-base error, linear-base error above 10% at the diffuse view, derived albedo+F0 exact below
  1e-9 at both views, linear-base F0 red low by over 20%; roughness 0.2|0.8 over 50% off at the
  peak; near dielectrics within 0.1% for all methods; two metals give linear-base equal to derived.
- Observed: RESULT: PASS metal|paint mip: sRGB-base err 41.8%, linear-base err 18.5% (diffuse view),
  derived albedo+F0 err 2.6e-16; roughness 0.2|0.8 mip still 95% off at peak; near dielectrics max
  0.092%. Specular peak: 68.91% / 38.68% / 0.0%. Diffuse albedo red 0.251 vs 0.002, F0 red 0.271 vs 0.52.
- Scenarios: 1) gold metal | blue paint at equal roughness; 2) same paint at roughness 0.2 | 0.8;
  3) BREAK: two near dielectrics 0.02 apart, built to show the error vanishing for all methods;
  4) two metals with far colours (equal metalness, linear base suffices); each at a diffuse view
  and the specular-peak view.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 3 pass 1

## E12 — line splitting for suno pace flips abab open under closure distance
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [songwriting][rhyme][suno-prompting][testing]
- What: Ran the two-metric openness rule (open if max closure distance is 3 or more, or nothing
  closes before the last line) on stanzas after the rushed-line kernel's shorter-lines fix.
  Splitting long lines in half doubles every gap, so both ABAB stanzas read open (max 4 when
  every line was split, 3 to 4 when only lines over 8 words were) against the scheme-shape
  kernel's stable verdict; hyphenation, which keeps the lines, changed 0 of 8 verdicts.
- Why built: New-half gap pick: the rhyme-scheme-shape and hyphenate/shorter-lines kernels as path,
  closure-distance-calls-xxaa-closed E1 as companion. E1's rule uses an absolute threshold in
  lines, and the shorter-lines fix is the one Suno remedy that changes the number of lines, so
  the threshold was the part most likely to break.
- Design: Stdlib Python. Eight 4-line stanzas (AABB, ABAB, ABBA, XXAA, two each, one with all lines
  over 8 words and one mixing long and short lines), each line given a word count, an end rhyme
  letter and a mid-line word letter (unrhymed). Modes: original; hyphenated (lines unchanged);
  split every line after its midpoint word; split only lines over 8 words; and two repairs:
  halve every distance (split factor 2), or score only the original line-end words at their
  source-line indices. Plus a break stanza: XXAA whose two opening mid-line words rhyme.
- Got right: Hyphenation is verdict-safe (0/8 wrong), AABB stayed stable after any split (max 2),
  and ABBA and XXAA stayed open (ABBA max 5 to 6; XXAA's first close moved to the last line, so the
  first-close clause still fired). Scoring original line-end words at source-line indices gave
  0/8 wrong for both full and partial splits.
- Where/why it failed: The threshold of 3 is in printed lines, and a split inserts an unrhymed
  half-line between every rhyme pair, so ABAB's 2 becomes 4 and crosses it: 2/8 wrong, both ABAB.
  Halving distances fixed the full split (0/8) but not the realistic partial one, where it called
  a mixed ABBA stable (max 2.5): 1/8 wrong. In the break stanza the exposed internal rhyme closed
  on line 3 of 8 and the raw rule called XXAA stable.
- Fix: Compute closure distances on the stanza's source lines: map each printed line back to the
  line it was split from and score only the original line-end words; separately check whether
  any split exposes a mid-line word that rhymes, since that adds a real early stop the
  source-line score deliberately ignores.
- Why this fix: The scheme-shape kernel describes how rhyme pairs sit in the written lines; splitting
  for Suno pacing changes typography and timing, not which words close which lines, so the
  metric must be indexed by source line, and a constant factor cannot undo a split applied only
  to the long lines.
- Rule of thumb: After splitting rushed lines for Suno, score rhyme openness on source lines: raw
  closure distance doubled and turned 2/2 ABAB stanzas open (max 4), halving fixed full splits but
  not partial ones (ABBA read stable), and source-line end words gave 0/8 wrong.
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__line-splitting-for-suno-pace-flips-abab-open-under-closure-distance.py;
  it printed wrong verdicts out of 8: hyphenate 0, split-all raw 2 (ABAB#2, ABAB#3), partial raw 2,
  halve-distances 0 full / 1 partial (ABBA#5), source-line-end 0/0, break XXAA raw stable vs
  source-line open. Rhyme letters are a hand fixture; how listeners or Suno phrase the split
  halves is the kernels' claim and lies outside this sandbox.
- Composed: ideas:SONGWRITING/rhyme/rhyme-scheme-shape-sets-a-songs-emotional-motion/aabb-stops-often-abba-stays-open-and-wistful, ideas:SONGWRITING/suno-prompting/hyphenate-words-to-slow-a-rushed-vocal-line/crowded-syllables-make-suno-rush-the-delivery, local__sandbox-closure-distance-calls-xxaa-closed/E1
- Picked-by: new-half
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-15__line-splitting-for-suno-pace-flips-abab-open-under-closure-distance.py
- Prediction: Written before the first run: hyphenation 0 flips; splitting every line flips exactly
  the ABAB stanzas (max 4) while AABB stays at 2 and ABBA/XXAA stay open; partial split at least
  1 flip; halving distances repairs the full split but leaves at least 1 flip on partial;
  source-line end words 0 flips; break XXAA with rhyming mid-line words reads stable raw and
  open under the source-line score.
- Observed: RESULT: PASS wrong verdicts out of 8: hyphenate 0, split-all raw 2 ['ABAB#2',
  'ABAB#3'], partial split raw 2 ['ABAB#2', 'ABAB#3'], halve-distances fix 0 all / 1 partial,
  source-line-end fix 0/0; break XXAA raw stable vs fixC open.
- Scenarios: 1) original and hyphenated stanzas; 2) every line split; 3) only lines over 8 words
  split; 4) halve-distances repair on 2 and 3; 5) source-line repair on 2 and 3; 6) BREAK: XXAA
  whose opening mid-line words rhyme, built to break the source-line repair (it keeps calling the
  stanza open though the split exposed a real early close on line 3).
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 5 pass 5

## E11 — lighter trail clear clips static neon hue
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [vfx][canvas][rendering][color]
- What: Modelled the canvas 2D neon recipe ('lighter' strokes plus a translucent black clear at
  alpha 0.2 for trails) and the ink recipe ('multiply' onto warm paper) in 8-bit per-channel maths.
  Both style claims reproduce, but a neon stroke that stays on the same pixels converges to 5x its
  colour and clips: an orange (255,128,26) stroke held still reads (255,230,47) on frame 2 and
  settles at (255,255,121), a hue shift from 27 to 60 degrees (orange becomes yellow-white).
- Why built: Current-half pass on the composite-modes kernel, which no lesson had applied. The
  kernel gives a concrete recipe (lighter, alpha 0.2 clear, near-white core) and the push was to
  find where that exact recipe stops producing the colour the artist picked.
- Design: Per-channel 8-bit model: lighter = min(255, d + s); black clear = round(d x (1 - a));
  multiply with alpha a = round(d x (1 - a) + a x d x s / 255). 1) two crossing 128 strokes, lighter
  vs source-over; teal and pink riso inks multiplied on paper (245,238,220). 2) 3 strokes in all 6
  draw orders per mode. 3) orange stroke with dwell 1 to 12 frames under the 0.2 clear, and the
  dwell needed for a 20 degree hue drift at clear alpha 0.1/0.2/0.3/0.5. 4) residual after 200
  fade frames. 5) fix: persistent trail kept with 'lighten' (max), current frame added with lighter.
- Got right: Lighter crossings brighten (0,255,255) where source-over stays (0,128,128); the riso
  overprint is a true third colour (teal 189 deg, pink 331 deg, overprint (0,40,113) at 219 deg,
  darker than both); lighter is draw-order free (1 result over 6 orders) and multiply is too in
  exact maths, while source-over at alpha 0.6 gave 6 different results.
- Where/why it failed: The trail clear and lighter together form a leaky accumulator whose steady
  state is s / a, so any channel above a x 255 clips: at a 0.2 a still orange drifts more than 20
  degrees by frame 2 and no tested alpha avoids it (dwell 2 frames at 0.1/0.2/0.3, 3 at 0.5).
  Only a stroke that moves past its own width each frame (dwell 1) keeps its hue (drift 0.0). The
  8-bit fade also never reaches black: residual (2,2,2) at a 0.2 and (5,5,5) at a 0.1. My draw-order
  prediction was refuted for 8-bit multiply (5 distinct of 6, spread 1 level, rounding only).
- Fix: Keep the persistent trail with 'lighten' (per-channel max) over the faded buffer and add only
  the current frame's strokes with 'lighter' on top; the static orange then stays (255,128,26) with
  0.0 degree drift while a crossing still reaches (0,255,255). Clear fully every N frames or snap
  values under the ghost floor to 0 to remove the residual.
- Why this fix: Max-accumulation has steady state equal to the stroke colour, so persistence cannot
  over-brighten, while the additive part is limited to overlaps inside one frame, which is the
  phosphor-crossing look the recipe wants; the leak was in summing the same stroke over many frames.
- Rule of thumb: Lighter plus an alpha-a black trail clear is a leaky sum that settles at colour/a
  (5x at 0.2): any held or slow neon stroke clips within 2 frames and mixed hues shift (orange 27 to
  60 deg); keep the trail with lighten (max) and add only this frame's strokes with lighter.
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__lighter-trail-clear-clips-static-neon-hue.py,
  which printed RESULT: PASS with crossing 255 vs 128, overprint hue 219, static orange to (255,255,121)
  at frame 2 drift 26.1 deg, dwell-1 drift 0.0, ghost (2,2,2), fix drift 0.0. The canvas maths is
  a per-channel model of the compositing formulas; browser premultiplied storage and colour
  management are outside the test.
- Composed: ideas:VFX/canvas-recipes/composite-modes-are-the-style/lighter-for-neon-multiply-for-ink-and-print, pappydapimp69__brainwork/E388
- Picked-by: current-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__lighter-trail-clear-clips-static-neon-hue.py
- Prediction: Written before running: crossing 255 vs 128 and a darker third riso colour; lighter and
  multiply each 1 distinct result over 6 orders, source-over more; a static orange under the 0.2
  clear drifts more than 20 deg within 3 frames while dwell 1 keeps its hue; an 8-bit ghost floor
  above 0 at a 0.2; the max-trail fix gives drift 0 and crossing 255.
- Observed: RESULT: PASS lighter crossing 255 vs over 128; riso overprint third colour True;
  order-free lighter 1 multiply 8-bit 5 (spread 1, float 1) over 6; static orange under clear 0.2
  drifts >20deg at frame 2 to (255, 255, 121) (hue 27->60), dwell-1 drift 0.0; ghost floor
  (2, 2, 2) at a0.2, (5, 5, 5) at a0.1; max-trail fix drift 0.0. Run 1 printed FAIL only because
  8-bit multiply gave 5 orders; the gate was changed to float-exact plus spread after that run.
- Scenarios: 1) lighter vs source-over crossing and riso overprint (reproduce); 2) 6 draw orders for
  lighter, multiply, source-over (ki-blast order claim); 3) BREAK: static and slow strokes under the
  trail clear at alpha 0.1/0.2/0.3/0.5; 4) BREAK: 8-bit ghost after 200 fades; 5) max-trail fix.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 4 pass 1

## E10 — inverted hull outline erased first under centroid painters sort
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [shaders][cel-shading][visibility][rendering]
- What: Rendered an inverted-hull cel outline (back-face-only shell of radius r+w drawn behind
  the body) without a depth buffer, ordering every triangle by centroid depth, and compared it
  with a per-pixel z-buffer. Over a large tilted backdrop the sort erased 31 to 68 percent of the
  outline ring at three sphere positions while the body there lost 1 pixel.
- Why built: Current-half edge between cel-shading/E6 (the hull's geometry) and the painter's
  centroid-sort lesson (count wrong pixels against a depth test at your own views). The hull
  only works because its back faces sit behind the body, which is a depth-test assumption.
- Design: Barycentric rasterizer, 128x128, orthographic, larger z nearer. UV spheres r=0.6,
  outline w=0.06, body front faces kept, hull front faces culled. Scenario A: two disjoint
  spheres overlapping on screen, depth gap 0.5 to 2.5. Scenario B: one outlined sphere held
  1.0 in front of a two-triangle backdrop z=y, swept over a 5x5 grid of positions. Orders:
  global centroid sort, and per-object sort (objects by centre z, hull before body).
- Got right: A lone outlined sphere sorts exactly (0 of 2180 px wrong), because every hull back
  face has a centroid behind every body front face; per-object sort was 0 wrong at all disjoint
  gaps in A and all 25 positions in B; where errors occurred the outline's wrong fraction was at
  least the body's at every position (pooled 9.3 percent vs 2.3 percent).
- Where/why it failed: My first prediction was wrong: two disjoint spheres sort exactly under the
  centroid order at every gap (0 px), so sphere-on-sphere is not where outlines break. The damage
  came from big backdrop triangles whose centroid lands between the hull rim depth and the body:
  at y=-0.5 the outline lost 238/352, 194/384 and 118/384 px with 1/1796 body px wrong; at y=-1.0
  both failed (162/320 outline, 745/1796 body). My outline-only counter scored those 1 px body
  errors as both, so the RESULT reads FAIL. Interpenetrating spheres (gap 0.5) broke per-object
  sort (80 px wrong vs 7 for the centroid order).
- Fix: With no depth buffer, draw each outlined object as one unit (hull pass then body pass)
  in a back-to-front object order and split large background triangles so no single centroid
  spans the character's depth; where objects interpenetrate, keep the depth test on for the hull.
- Why this fix: Hull back faces sort up to r+w deeper than the body front faces they frame, so any
  foreign triangle whose centroid falls in that band is drawn between them and paints over the
  rim; grouping per object removes the band, and finer backdrop triangles move their centroids
  back to where they actually are.
- Rule of thumb: Without a depth buffer an inverted-hull outline dies before its body: big backdrop
  triangles under a centroid sort erased 31 to 68 percent of the outline ring at 3 of 25 positions
  while the body lost 1 px; sort per object, hull then body (0 wrong), unless objects interpenetrate.
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__inverted-hull-outline-erased-first-under-centroid-painters-sort.py,
  which printed single sphere 0 wrong, centroid exact at all disjoint gaps, B pooled outline 9.3% vs
  body 2.3%, per-object max wrong 0, interpenetrating gap per-object 80 px. Orthographic, spheres
  and one planar backdrop only; GPU rasterization rules and perspective are outside the test.
- Composed: local__cel-shading/E6, local__painters-centroid-sort-vs-zbuffer-yaw-sweep-bbox-overlap-not-sufficient/E1
- Picked-by: current-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__inverted-hull-outline-erased-first-under-centroid-painters-sort.py
- Prediction: Written before the first run: single sphere 0 wrong; two disjoint spheres under the
  centroid sort lose outline pixels at a larger gap than body pixels; per-object 0 wrong when
  disjoint, failing when interpenetrating. After run 1 refuted the two-sphere part, before
  scenario B first ran: outline wrong fraction >= body at every erring position, more positions
  outline-only than body-only, per-object 0 wrong.
- Observed: RESULT: FAIL A (two disjoint spheres): centroid exact at all disjoint gaps=True; B
  (sphere over tilted backdrop, 25 positions): outline-only erased 0, body-only 0, both 5, clean
  20; pooled wrong outline 9.3% vs body 2.3%; outline frac>=body at every failing position True;
  per-object max wrong 0 (the 3 y=-0.5 positions lost 31-68% outline with 1 body px each).
- Scenarios: 1) single outlined sphere; 2) two disjoint spheres at gaps 0.9 to 2.5; 3) BREAK:
  interpenetrating spheres at gap 0.5, built to break per-object sorting; 4) sphere over a tilted
  two-triangle backdrop at 25 screen positions; 5) per-object sort on every case.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 1 pass 2

## E9 — hue shifted deep shadow swallows selective black outline
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [pixel-art][art][cel-shading][accessibility][testing]
- What: Ran the hue-shift ramp kernel and the selective-outline kernel together on banded disc
  sprites and measured the shadow-side black outline against the body pixels it borders, the
  place cel-shading E5 warned that cool shadows lose luminance. The outline was lost (WCAG
  contrast under 2.0) on 44.8% of shadow-side pairs at 32 px on 4 of 5 base hues, for the
  same-hue ramp AND the hue-shifted ramp alike, and on 0% at 16 px.
- Why built: New-half pick: hue-shift-shading-scaled-to-sprite-size and selective-outlining as the
  path, local__cel-shading as companion. E5 showed a cool shade end nearly meets a black line
  in a 3-D cel shader; selective outlining puts the black line exactly on the shadow side, so the
  question was whether hue-shifting the shadows is what drowns it in a pixel sprite.
- Design: Stdlib Python. Disc sprite at 16 px (shadow, base, highlight) and 32 px (deep shadow L
  0.20, shadow, base, highlight), banded on N.L from an upper-left light. Five base hues (red 0,
  skin 20, orange 30, green 120, blue 210), S 0.6. Ramps: same hue; hue-shifted 15 degrees per
  step toward 270 in shadow and 60 in light at the same HSL L; hue-shifted at matched relative
  luminance; hue-shifted with the darkest tone floored at contrast 2.0 against black. Outline
  black on rim pixels facing away from the light. Lost pair = contrast under 2.0 (also 1.5).
- Got right: E5's direction transfers: the hue shift lowered darkest-tone contrast against black on
  4 of 5 bases at 32 px (orange 1.84 to 1.48, blue 1.62 to 1.32, skin 1.68 to 1.48), and at the
  1.5 threshold it lost the line on 3 of 5 bases where same hue kept it. A luminance-matched shift
  kept a 30-degree hue offset with exactly the same-hue loss, and a contrast-2.0 floor on the deep
  shadow gave 0% lost with 4 distinct tones on every base.
- Where/why it failed: My prediction blamed the hue shift; the sprite-size step did the damage.
  The extra deep-shadow tone that 32 px makes room for sits at contrast 1.47 to 2.24 against
  black even without any hue shift, so lost share was 35.9% mean for both ramps, while the
  16 px two-step ramp stayed at 2.24 to 5.02 and lost nothing. Non-blue mean drop from hue shift
  was 9.2%, not 15%; blue fell most (18.8%, heading through pure blue) and red rose 2.6%
  (toward magenta adds blue light), the opposite of my blue break case.
- Fix: When a 32 px or larger sprite gets a deep-shadow step and a selective black outline,
  floor the deepest tone at contrast 2.0 against the outline colour (relative luminance 0.05
  for black) or lighten the shadow-side outline; check the floor after hue-shifting, since a
  shift toward pure blue costs up to 19% more and a shift toward magenta can repay it.
- Why this fix: The shadow-side outline exists to separate silhouette from background, and it
  only shows if it differs in luminance from the rim tone it touches; the longer ramp a bigger
  sprite affords pushes that rim tone toward black, and hue shifting only nudges it, so the
  floor targets the step that actually carries the loss.
- Rule of thumb: A 32 px deep-shadow step, not the hue shift, drowns a selective black outline:
  shadow-side pairs under contrast 2.0 were 44.8% on 4/5 hues for same-hue and hue-shifted ramps
  alike, 0% at 16 px; floor the deepest tone at 2.0 vs the outline after shifting.
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__hue-shifted-deep-shadow-swallows-selective-black-outline.py;
  it printed lost share 32 px 35.9% mean for same and shifted ramps (44.8% on red, skin, orange,
  blue), 16 px 0%, non-blue darkest-tone drop 9.2%, blue 18.8%, red rose 2.6%, floor fix 0% lost.
  WCAG luminance stands in for perceived value; the disc, ramp L values and the 2.0 line
  threshold are my model choices.
- Composed: ideas:ART/pixel-art/hue-shift-shading-scaled-to-sprite-size/shadows-cooler-highlights-warmer, ideas:ART/pixel-art/selective-outlining-not-uniform-black/dark-against-background-light-against-self, local__cel-shading/E5
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__hue-shifted-deep-shadow-swallows-selective-black-outline.py
- Prediction: Written before the first run: hue shift lowers darkest-tone contrast on 4+ of 5
  bases with mean drop 15%+; 32 px lost share 50%+ hue-shifted vs 25% or less same-hue; 16 px
  under 10% for both; luminance-matched shift equals same hue; blue base (210 toward 270) does
  not lose contrast. Run 1 failed; added before run 2: 32 px loses 40%+ on 4/5 bases for both
  ramps, 16 px 0%, a 2.0 floor gives 0% with 4 tones, threshold 1.5 shows hue-shift losses on 2+.
- Observed: RESULT: PASS 32px deep-shadow step loses >=40% of shadow-side black-outline pairs on
  4/5 bases for same-hue AND hue-shifted ramps (16px: 0%); hue shift drops darkest-tone contrast
  9.2% mean on non-blue (blue drop 18.8%, red drop -2.6% i.e. rose) and loses extra lines at
  threshold 1.5 on 3/5; luminance floor 2.0 -> 0.0% lost with 4 distinct tones. The run-1
  prediction failed (original prediction holds: False).
- Scenarios: 1) same-hue ramp at 16 and 32 px on five hues; 2) hue-shifted ramp at the same HSL
  L; 3) luminance-matched hue shift; 4) contrast-2.0 floor on the deep shadow; 5) threshold 1.5
  instead of 2.0; 6) BREAK: blue base 210, built to show a cool shift toward 270 cannot cost
  luminance (it cost 18.8%; red was the base that gained).
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 5 pass 1

## E8 — genre swap must spare the recognition cues
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [storytelling][comedy][structure][ai-video]
- What: A cue-evidence model of four micro-film genres (selfie vlog, nature documentary, talk show,
  pharma ad) tested the "genre template plus one absurd swap" format. Swapping the content slot (host,
  animal, guest) left the genre readable by 1.0 s in the vlog, documentary and talk show, leaving
  5.9-6.5 s of an 8 s clip for the peak. The pharma ad was not readable in one second even played
  straight (1.5 s), and swapping its product slot pushed recognition to 4.0 s, leaving 2.5 s.
- Why built: Current-half gap pass on the micro-film swap kernel, which no lesson had applied. The
  kernel says the template does the setup in about a second; the one-peak-violation kernel needs a
  held pause plus a single peak inside the clip, and the wrong-cue/safe-cue kernel needs the
  template to stay intact as the safe cue. The question was which swaps keep both conditions.
- Design: Each genre is an authored list of cues (onset s, evidence weight, format or content).
  Recognition is the first onset where intact cue weight reaches 5; a swapped cue adds nothing. Safe
  cue: intact weight at least 60 percent of the template. Payoff room = clip - recognition - 1.0 s
  pause - 0.5 s hold. Cases: straight, content-slot swap, heaviest-format-cue swap, every 2-swap pair,
  and a robustness sweep perturbing every weight by -1/0/+1 (all 3^n combinations).
- Got right: Content-slot swaps kept the safe cue in 4/4 genres and recognition by 1.0 s in 3/4,
  and that held in 89 to 96 percent of weight perturbations for vlog, documentary and talk show.
  Swapping the heaviest format cue delayed recognition to 2.0 s in the documentary (hushed narrator)
  and the talk show (desk set), so the format cues, not the subject, are what the swap must spare.
- Where/why it failed: The kernel's one-second claim fails for ad genres: the pharma ad builds its
  identity from the product super (1.5 s) and the fast side-effects voice-over (4.0 s), so its
  content slot is also a recognition cue, and robustness for a 1 s read there was 0.00. The vlog was
  redundant (swapping the selfie framing still read at 0.3 s). My guess that two swaps break at least
  half of pairs was wrong: 19 of 41 pairs failed (46 percent), 6/6 in the ad, 3/15 in the vlog.
- Fix: Before writing the swap, list the template's recognition cues with their onset and keep
  every cue that lands before 1 s intact; swap only a slot that carries no recognition weight. For
  ad formats, keep the product super and voice-over grammar straight and make the product absurd
  inside them, or budget a 15 s clip (9.5 s room) rather than one 8 s generation (2.5 s).
- Why this fix: The format works because recognition is nearly free; a swap that removes a
  recognition cue spends the clip on setup again and leaves no room for the paused single peak, and
  removing too much template removes the safe cue that makes the violation read as a joke.
- Rule of thumb: Swap the content slot, never a cue that carries genre recognition: subject swaps
  kept vlog, documentary and talk show readable by 1 s (5.9-6.5 s left of 8 s), but a pharma ad's
  product is itself a cue (recognition 1.5 to 4.0 s, 2.5 s left), so give ad parodies 15 s.
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__genre-swap-must-spare-the-recognition-cues.py,
  which printed RESULT: PASS with content swap at or under 1.0 s in 3/4, format swap late in 2/4,
  pharma straight 1.5 s and slot swap 4.0 s, 2-swap failures 19/41, robustness 0.89/0.89/0.96/0.00.
  The cue lists, onsets, weights and the threshold of 5 are my own estimates; the sweep tests the
  weights only, and viewer recognition times were not measured.
- Composed: ideas:STORYTELLING/micro-film/familiar-genre-template-plus-one-absurd-swap/vlog-documentary-ad-or-talk-show-with-a-monster-in-it, ideas:COMEDY/timing/one-peak-violation-with-a-held-pause/not-constant-randomness, ideas:COMEDY/premise-design/an-absurd-premise-needs-a-wrong-cue-and-a-safe-cue/weirdness-alone-is-not-a-joke
- Picked-by: current-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__genre-swap-must-spare-the-recognition-cues.py
- Prediction: Written before running: content-slot swap readable by 1.0 s in all 4 genres; heaviest
  format-cue swap late in at least 3 of 4; pharma ad not readable in 1 s even straight; two swaps
  break the safe floor or recognition in at least half of pairs; content-swap robustness at least
  0.8 for vlog, documentary and talk show. The all-4, 3-of-4 and half-of-pairs parts were wrong.
- Observed: RESULT: PASS content-slot swap recognised <=1.0s in 3/4 genres, heaviest format-cue swap
  late in 2/4; pharma ad straight recog 1.5s (one-second claim fails), its product slot swap delays
  to 4.0s (room8 2.5s); 2-swap pairs failing 19/41; robustness vlog 0.89 doc 0.89 talk 0.96 pharma
  0.00. Run 1 printed FAIL on the 2-swap guess; the gate was then changed to the kernel's claims.
- Scenarios: 1) straight templates; 2) content-slot swap per genre; 3) heaviest format-cue swap;
  4) BREAK: pharma ad, built to break the one-second recognition claim; 5) all 2-swap pairs;
  6) weight perturbation sweep -1/0/+1.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 4 pass 5

## E7 — front cut must keep the whole mosaic rhyme span
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [songwriting][rhyme][suno-prompting][testing]
- What: Cut rushed lines from the front down to their last k words (k = 1, 2, 3, 5) on five
  stanzas whose rhymes span two words (lose it / choose it, show it / poet, hold her / older)
  and read the shape from two-pass uppercase letters. Keeping only the final word changed the
  shape in 4 of 5 stanzas; keeping the last two words kept 5 of 5.
- Why built: New-half gap pick: the two-pass lettering kernel and the rhyme-shape kernel with the
  shorten-rushed-lines-keep-the-rhyme-word lesson as companion. That lesson kept 4/4 shapes with
  one-word rhymes and a spelling key; a mosaic rhyme puts the stressed vowel in the second-last
  word, so keeping the rhyme WORD may not keep the rhyme.
- Design: Hand ARPAbet fixture with stress digits; rhyme key runs from the last stressed vowel in
  the kept tail to the end, reduced AH0/IH0 folded to a schwa. Resolved rhyme needs both keys to
  start on a stressed vowel and match; a tail with no stressed vowel can only join an assonance
  (lowercase) pair. Stanzas: AABB with a mosaic and a one-word feminine couplet, ABAB mosaic,
  AABB double mosaic, ABBA mosaic, and an XXAA one-word control.
- Got right: Keeping two words restored every mosaic key (5/5 shapes at k=2, 3 and 5), and the
  one-word feminine couplet playing / staying stayed uppercase at k=1 because its stressed vowel
  sits inside the final word; the one-word XXAA control kept its shape at every k.
- Where/why it failed: At k=1 the unstressed tails it and her cannot resolve: AABB read xxAA (the
  stable stanza became the open-then-resolved shape), ABAB read xAxA, ABBA read AxxA, and the
  double mosaic AABB read xxAA; 4 of 5 stanzas moved to a more open shape. The companion's
  keep-the-rhyme-word wording is exactly the cut that breaks here.
- Fix: When cutting a rushed line from the front, keep the rhyme SPAN: everything from the last
  stressed vowel of the rhyme to the end of the line, which for a mosaic or pronoun-tail rhyme
  is the last two words or more; then re-letter with a stress-aware judge before trusting the shape.
- Why this fix: A rhyme lands on its stressed vowel; an unstressed tail like it or her carries no
  stress for a resolved match, so cutting the stressed word demotes the pair to assonance or
  nothing and the uppercase-only shape reading loses the stop the writer put there.
- Rule of thumb: A front-cut that keeps only the last word broke 4 of 5 mosaic-rhyme stanzas (AABB
  read xxAA, ABAB xAxA, ABBA AxxA) while keeping the last two words held 5 of 5; keep from the
  rhyme's stressed vowel to the end, not just the rhyme word.
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__front-cut-must-keep-the-whole-mosaic-rhyme-span.py,
  which printed uppercase shape kept k=1 1/5, k=2 5/5, k=3 5/5, k=5 5/5, 4 stanzas opened at k=1,
  feminine one-word pair survived k=1. The fixture is hand-made (her is entered in its reduced
  sung form); real CMUdict lookups and Suno delivery are outside this test.
- Composed: ideas:SONGWRITING/rhyme-tooling/two-pass-letter-assignment-keeps-schemes-legible/resolved-rhymes-claim-letters-before-assonance-does, ideas:SONGWRITING/rhyme/rhyme-scheme-shape-sets-a-songs-emotional-motion/aabb-stops-often-abba-stays-open-and-wistful, local__sandbox-shorten-rushed-lines-keep-the-rhyme-word/E1
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__front-cut-must-keep-the-whole-mosaic-rhyme-span.py
- Prediction: Written before the first run: keep-last-1 preserves the uppercase shape only in the
  stanza with no mosaic rhyme (1/5); keep-last-2 preserves 5/5; at keep-last-1 at least 2
  stanzas move to a more open shape; the one-word feminine pair survives k=1.
- Observed: RESULT: PASS uppercase shape kept: k=1 1/5, k=2 5/5, k=3 5/5, k=5 5/5; stanzas opened
  (resolved pair lost) at k=1: 4; one-word feminine pair survives k=1: True
- Scenarios: 1) AABB with a mosaic couplet and a one-word feminine couplet; 2) ABAB mosaic;
  3) AABB double mosaic with a pronoun tail; 4) ABBA mosaic; 5) XXAA one-word control; 6) BREAK:
  the one-word feminine couplet playing / staying, built to break the claim that multi-syllable
  rhymes need two words (it survived at k=1); each at k = 1, 2, 3, 5.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 1 pass 5
- Audited: 2026-10-15 · modeled · Read the entry and its stored sandbox (front-cut-must-keep-the-whole-mosaic-rhyme-span.py). The result is computed, not hard-coded: shapes come from the two-pass letter assignment run over a stressed-vowel rhyme key, and the printed 1/5, 5/5, 5/5, 5/5 follow from the fixture. But the k=1 failure is largely built in: the judge defines a resolved rhyme as needing a stressed vowel in the kept tail, and "it" and "her" are entered with no stress, so they cannot resolve by construction. The claim is about real rhymes and sung delivery, yet only a hand-typed ARPAbet fixture (about 30 words, "her" entered in its reduced sung form) was tested, with no real pronunciation lookup. Scope is also thinner than the Rule of thumb: k=2, 3 and 5 are indistinguishable on these five stanzas, so "keep from the stressed vowel to the end" is never separated from "keep the last two words", and no rhyme needing three or more kept words (a longer mosaic) was tried. The direction (a tail with no stress cannot carry a rhyme) is sound, so I rate it modeled, not fail. · session_01A5ZkeepCfk7CHTSxS7qQ4k

## E6 — fake ad premise keep two trope unique features visible
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [comedy][structure][simulation]
- What: A deterministic trope reader for the fake-mobile-ad premise slot machine (pick one trope, swap one
  thing absurd). Six tropes are feature lists (signature, payload and shared grammar-kit features); the
  reader scores visible features by inverse frequency across tropes and counts a premise as readable when
  the true trope wins and keeps at least half its unswapped score. Every 1, 2 and 3 feature swap is tried.
- Why built: The premise-slot-machine kernel had never been applied by a lesson. It says one swap, and its
  example swaps the payload (pins hold back paperwork instead of lava); the run asks whether the number of
  swaps or the slot you swap decides whether the viewer still recognises the ad being parodied.
- Design: Stdlib script, no randomness. Tropes: pull-the-pin, incompetent player, number gates, save the sad
  man, merge evolution, live-action skit; kit features (finger cursor, FAIL stamp, help text, level counter,
  store card, play button) are shared, so they weigh little. Scenarios: payload, signature and kit single
  swaps; all k-swap combinations; a sparse first-second hook frame showing only three features.
- Got right: One swap is safe in every case: 35 of 35 single swaps and even 87 of 87 double swaps stay
  readable at full view, so the kernel's one-swap rule has slack. Three swaps drop to 69 of 120 (58%), and
  what decides it is how many trope-unique features stay on screen: 0 left 0/6, 1 left 15/51, 2 left 45/54,
  3 left 9/9. The grammar kit carries almost no identity (weights 0.85 to 1.25 against 1.95 for unique ones).
- Where/why it failed: My prediction that swapping the signature feature would break recognition (3 or fewer
  of 6) was wrong at full view: 6 of 6 survived, because every trope keeps a second unique feature. Slot role
  only mattered in the sparse hook frame, and there only for pull-the-pin (1 of 6), whose remaining payload
  (lava) is shared with the incompetent-player trope, not because signature slots are special.
- Fix: Write the swap, then count the trope-unique features still visible in the opening frame and keep at
  least two; never count kit items (cursor, FAIL stamp, help text) toward that, and avoid leaving a payload
  that another trope also uses as the only identifier after the swap.
- Why this fix: The reader's recognition tracks unique features left, monotonically and almost cleanly, while
  the slot role and the swap count only matter through that number, so it is the one thing to check.
- Rule of thumb: A fake-ad parody stays recognisable while at least two features unique to the parodied trope
  remain on screen (2 left: 83%, 1 left: 29%, 0 left: 0% in the reader model); the shared ad-grammar kit does
  not count, and which slot you swap matters only when it leaves fewer than two.
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__fake-ad-premise-keep-two-trope-unique-features-visible.py,
  output byte-identical over two runs; all counts above are from that run. The feature lists, inverse
  frequency weights and the 50% recognition bar are model inputs I chose, standing in for real viewers.
- Composed: ideas:COMEDY/fake-mobile-ad/premise-slot-machine-from-the-five-misleading-ad-patterns/pick-one-trope-then-swap-one-thing-absurd, ideas:COMEDY/fake-mobile-ad/reusable-fake-ad-grammar-kit/finger-cursor-red-fail-stamp-99-percent-text-cheap-jingle-fake-store-card
- Picked-by: current-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__fake-ad-premise-keep-two-trope-unique-features-visible.py
- Prediction: A single payload swap keeps the trope recognised in at least 5 of 6 tropes; a single swap of
  the most distinctive signature feature keeps it in 3 or fewer of 6; three swaps keep under half readable.
- Observed: RESULT: PASS full view any single swap 35/35, 2-swap 87/87, 3-swap 69/120; signature swap 6/6 =
  payload 6/6 at full view; sparse hook frame signature swap loses 1/6 vs payload 0/6; 3-swaps by unique left
  {0: '0/6', 1: '15/51', 2: '45/54', 3: '9/9'}. Payload prediction held, signature prediction missed, three
  swaps came in at 58%, not under half.
- Scenarios: 1) single payload swap per trope; 2) single signature swap (built to BREAK the one-swap rule);
  3) single kit swap; 4) all 1, 2 and 3 swap combinations (3 swaps built to BREAK it); 5) sparse hook frame
  with only three features visible; 6) two swaps with the signature intact.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 2 pass 1
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-creative-training.md#E29 · compatible · sandboxes/2026-10-15__perfect-copy-parody-turn-must-beat-ad-skip.py · observed RESULT: PASS perfect copy (k=3) beats loose (k=1) 2.69x at a 3 s turn; peak at the recognition point T=2 s (0.819), below half by T=5.0 s; a turn before recognition gives fidelity nothing; heavy ad-skipping (h_ad=0.8) flips it to loose-win… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 1 pass 1
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-auto-training.md#E15 · compatible · sandboxes/2026-10-15__single-trope-series-of-one-swap-fake-ads-stays-over-half-identical-until-four-kit-assets-rotate.py · observed RESULT: PASS 6/6 checks; single-trope 1 swap 0.767, 2 swaps 0.691, +3 kit rotated 0.534, +4 rotated 0.482; trope rotated+3 kit 0.480. Also: single trope 1 swap 4 rotated 0.558, trope rotated kit fixed 0.636, 3 swaps 0.648 and unreadable; u… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 4 pass 1

## E5 — de esser key on hf share not hf level
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [audio][speech][dsp][voice]
- What: A de-esser's sibilance detector tested two ways on synthetic speech recorded at different mic
  distances: keyed on the absolute level of the high band (above 4 kHz), as a fixed threshold de-esser does,
  or keyed on the high band's share of total frame energy. Both were calibrated on one 0 dB take and then run
  on takes at +6, -6, -12 and -18 dB, plus breathy and whispered vowels.
- Why built: New-domain pass for Voice & speech; brain query for sibilance, plosive and intelligibility
  returned nothing. Voice-over and dialogue editors set a de-esser threshold once by ear, yet a talker who
  leans back or forward changes level by 6 to 12 dB inside one session.
- Design: Stdlib script at 16 kHz, 10 ms frames. Vowels are a 140 Hz harmonic stack to 3.5 kHz with faint
  aspiration; "s" is LCG white noise through two 4.5 kHz high-pass biquads; breathy vowels add strong
  broadband noise; whispered vowels are noise only. The side chain is a 4 kHz double high-pass. Detector
  thresholds sit midway between the sibilant and vowel distributions of the 0 dB take.
- Got right: The share detector hit 100% of sibilant frames at every take from +6 to -18 dB (spread 0.0
  points) with 0% false fires on plain and breathy vowels. The level detector hit 100% at +6 and 0 dB but
  76% at -12 dB and 0% at -18 dB, and up close it fired on 100% of breathy-vowel and whisper frames.
- Where/why it failed: The share detector fired on 50% of whispered-vowel frames: unvoiced noise has an HF
  share (median 0.424) sitting on the 0.422 threshold, between voiced vowels (0.0001) and "s" (0.905). My
  prediction that the level detector would drop under 20% at -12 dB missed (76%; it only collapsed at -18 dB),
  and my prediction that breathy vowels would trip the share detector was wrong (0%, median share 0.101).
- Fix: Key the de-esser on the high band's share of the full-band energy (or a split-band ratio), not on a
  fixed high-band level, so one setting survives distance changes; for whispered or unvoiced passages bypass
  it or raise the share threshold, because whisper looks like weak sibilance to a share detector.
- Why this fix: A share is level-invariant by construction, so the 18 dB distance range that took the level
  detector from 100% to 0% did not move it at all; its one blind spot is a sound that is all noise, which a
  voicing check or a higher threshold separates from the much brighter "s" (0.905 against 0.424).
- Rule of thumb: Set a de-esser to key on the HF share of the signal, not its HF level: a level threshold set
  on one take lost 24% of esses at -12 dB and all of them at -18 dB and fired on every breathy frame up close,
  while the share key held 100% at every distance; bypass it on whispered lines, where it fires half the time.
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__de-esser-key-on-hf-share-not-hf-level.py,
  output byte-identical over two runs, every percentage above from that run. The speech is synthetic (harmonic
  vowels, filtered noise for "s"), standing in for real recorded voice and a real de-esser plugin.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__de-esser-key-on-hf-share-not-hf-level.py
- Prediction: Level detector calibrated at 0 dB catches over 90% of sibilant frames at 0 dB and under 20% at
  -12 dB; share detector hit rate stays within 5 points across takes; share detector false-fires on a breathy
  vowel in over 50% of its frames.
- Observed: RESULT: PASS abs-level s hit +6/0/-12/-18 dB 100/100/76/0%, breathy FA at 0 dB 100%; share s hit
  spread 0.0 pts, breathy FA 0%, whisper FA 50% (abs-level whisper FA at 0 dB 100%). HF share medians: s
  0.905, vowel 0.0001, breathy 0.101, whisper 0.424 against threshold 0.422. The whisper pass bar in the
  script was loosened from over 50% to at least 25% after the first run read exactly 50%.
- Scenarios: 1) take at 0 dB (calibration); 2) takes at -6, -12, -18 dB, talker leaning back; 3) +6 dB, talker
  leaning in; 4) breathy vowel; 5) whispered vowel, noise only (built to BREAK the share detector).
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 2 pass 4

## E4 — constrained idea slot machine oversamples picky options
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [ideation][sampling][testing]
- What: A morphological-box idea generator (one option each for genre, setting, protagonist,
  twist, 4x4x4x4 = 256 combos) with a ban list of pairs that do not go together. Picking the
  columns in order, each uniformly among still-compatible options, served the valid ideas very
  unequally: the most likely combo came up 16x as often as the least likely one.
- Why built: New-domain pass in Ideation and originality, where brain query showed no memory on
  morphological boxes or prompt slot machines. Writers and tools add ban rules to keep random
  idea prompts sensible, and nobody checks what the bans do to which ideas get served.
- Design: Exact probabilities by enumeration with Fractions, no RNG. Sequential picker with
  restart on a dead end, renormalised over completed walks, compared with uniform-over-valid
  (draw a full combo, reject if banned). Measures: max/min probability ratio, total variation
  distance from uniform, and the share of draws passing through a picky option (an option
  banned with 3 or more partners). Ban lists: none, irregular (10 bans), regular (12 bans, each
  option bans exactly one partner in the next column).
- Got right: Irregular bans left 121 of 256 combos valid; the sequential picker gave max/min 16.00,
  TV 0.387, and sent 59.4% of draws through picky options that hold 20.7% of valid combos. Top
  combo noir / monastery / child / it was a dream came up 7.56x uniform, because once monastery
  is picked only child survives and then only one twist does.
- Where/why it failed: Bans alone do not cause the skew: the regular ban list (108 valid) was
  exactly uniform (ratio 1.00, TV 0.000), because every partial pick keeps the same number of
  continuations. The skew is caused by unequal branching, so a tool can pass a uniformity check
  on a tidy test ban list and still skew heavily on a real, lopsided one.
- Fix: Sample a valid combination uniformly (enumerate or reject whole combos), or weight each
  sequential choice by the number of valid completions below it; then check the served
  distribution on your real ban list, not a symmetric one.
- Why this fix: Choosing uniformly at each step gives each branch equal mass regardless of how many
  ideas live under it, so ideas under narrow branches get the mass that wide branches split many
  ways; weighting by completion count or whole-combo sampling restores equal mass per idea.
- Rule of thumb: An idea slot machine that picks columns in order among still-allowed options
  over-serves ideas that pass through heavily banned options (16x max/min, 59% of draws on 21% of
  ideas); a regular ban list stays uniform, so test the skew on your real, lopsided ban list.
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__constrained-idea-slot-machine-oversamples-picky-options.py,
  which printed no bans ratio 1.00, irregular max/min 16.00 TV 0.387 picky share 0.594 vs 0.207,
  regular bans ratio 1.00 TV 0.000. Whether over-serving the narrow options helps or hurts a
  writer's originality is a judgement this sandbox makes no claim about.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__constrained-idea-slot-machine-oversamples-picky-options.py
- Prediction: Written before the first run: irregular bans give max/min >= 3 and TV >= 0.15 with
  picky-path combos over-served; no bans and regular bans both exactly uniform.
- Observed: RESULT: PASS sequential picker: no bans ratio 1.00; irregular bans max/min 16.00, TV
  0.387, picky-path share 0.594 vs uniform 0.207; regular bans ratio 1.00 TV 0.000
- Scenarios: 1) no bans control; 2) irregular 10-pair ban list; 3) BREAK: regular ban list where
  every option bans exactly one next-column partner, built to break the claim that any ban list
  skews the picker (it did not: ratio 1.00).
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 1 pass 4

## E3 — char count expansion budget misjudges pixel fit
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [localization][typography][rendering]
- What: Composed German UI-label expansion with the average-character-width lesson by checking a
  localization budget written in characters (translation at most 1.3x the English character
  count, or pseudo-localization that pads English with 30% more characters) against the pixel
  budget it stands for (translated width at most 1.3x the English width in the same font).
- Why built: Current-half edge pass. localization-expansion/E1 says measure the real translated
  strings; typography-measure/E1 says character counts do not predict width in a proportional
  font. Translators and pseudo-localization tools still receive length limits in characters, so
  the question was how often a character budget gives the wrong verdict on real label pairs.
- Design: Python model with Helvetica AFM advance widths (Arial and Liberation Sans are
  metric-compatible), anchored to the earlier Chromium measurement: Einstellungen at 16px computes
  96.05 px against 96.07 px measured. 25 common English/German UI label pairs. Character rule as
  an exact 1.3 ratio and as the integer max-length ceil(1.3*len) a string table carries.
  Pseudo-localization wraps the English in brackets and pads 30% more characters of '!', '~' or
  'W'; a second pseudo case pads long English sentences with '!' and no brackets. Monospace font
  as the break case.
- Got right: With the exact 1.3 ratio the character rule disagreed with the pixel rule on 4 of 25
  labels: Loeschen, Anmelden and Abmelden passed on characters yet overflowed in pixels (Sign in
  and Log out are narrow English: spaces and i, l, t), and Oeffnen failed on characters yet fit.
  The integer max-length was worse, 7 false passes (it adds Zurueck, Drucken, Weiter, Senden).
  The monospace break case gave 0 disagreements, so the gap is glyph width, not arithmetic.
- Where/why it failed: My pseudo-localization prediction was wrong. On short labels the bracket
  pair plus ceil padding inflated width by 44.1% ('!'), 69.8% ('~') and 99.9% ('W'), flagging 25 of
  25 labels where real German overflowed 17, so it missed none and over-flagged 8. Only on long
  sentences did '!' padding undershoot, adding 17.1% to 20.0% px for 30% more characters. I also
  predicted at least 2 false rejects and saw 1. German averaged +48.5% characters and +48.3% px
  on this set, wider than the +31% of the original 8 pairs.
- Fix: Give translators and layout checks a pixel budget measured with the shipping font (or the
  string's measured width plus the layout's real headroom), not a character max-length; if a
  character limit is unavoidable, use it only as a pre-filter and still measure each translated
  string; size pseudo-localization padding by width (wide fillers) on long strings, and do not read
  its short-label results as the real German overflow count.
- Why this fix: Character count and width diverge per string in exactly the way typography-measure
  showed (Hilfe 32.0 px and Konto 41.8 px are both 5 characters), so a character budget is a
  second estimate of width and inherits its errors; the monospace case confirms the error vanishes
  only when every glyph has the same width.
- Rule of thumb: A 1.3x character budget is not a 1.3x width budget: on 25 German UI labels it gave
  3 false passes and 1 false reject (7 false passes as an integer max-length), and '!'-padded
  pseudo-loc grew long strings only 17-20% px; give translators a measured pixel limit.
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__char-count-expansion-budget-misjudges-pixel-fit.py,
  which printed the counts above and RESULT: FAIL (the FAIL is three of my own predictions, about
  false rejects and pseudo-localization). The width table is the Helvetica AFM set typed from
  memory and checked only against the one stored Chromium measurement; the German translations
  are common ones I chose and were not reviewed by a translator.
- Composed: local__sandbox-localization-expansion/E1, local__sandbox-typography-measure/E1
- Picked-by: current-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__char-count-expansion-budget-misjudges-pixel-fit.py
- Prediction: Written before the first run: the character budget gives at least 2 false passes and
  at least 2 false rejects of 25 labels; '!'-padded pseudo-localization grows width under 20% and
  misses at least one German overflow; a monospace font gives 0 disagreements.
- Observed: RESULT: FAIL 1.3x char ratio vs 1.3x px: 3 false passes, 1 false rejects of 25 DE labels
  (integer ceil limit: 7 false passes); bracketed '!' pseudo-loc +30% chars grows 44.1% px and
  misses 0/17 German overflows; '~' grows 69.8%; long-string '!' growth 17.1-20.0%; monospace 0/0.
  The first run used the integer limit for the monospace case too and showed 5 false passes; that
  was rounding slack, so the break case now uses the exact ratio and the integer limit is reported
  separately (S1b and S2b were added after the first run).
- Scenarios: 1) exact 1.3x character ratio versus 1.3x pixel width on 25 label pairs; 1b) integer
  max-length ceil(1.3*len); 2) bracketed pseudo-localization with '!', '~' and 'W' fillers;
  2b) long sentences padded with '!' only; 3) BREAK: monospace font, built to make character and
  pixel budgets agree; 4) equal-length strings with different widths (Hilfe versus Konto).
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 3 pass 2

## E2 — capped drain delays lfsr restore into permanent phase slip
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [audio][dsp][realtime][determinism][state][testing]
- What: Composed the per-callback drain cap (combined-audio-realtime E1/E3) with the persisted
  LFSR register resume and the peak-meter blindness (combined-lfsr-peak-meter E1) in one
  resume path. When the live-register RESTORE message rides the same capped FIFO behind a
  2048-message repair burst, it applies on callback 32 and the voice then runs from the
  suspend-time register 4096 samples late: a permanent phase slip, 49.8% of noise bits wrong
  for the rest of the render, while the peak meter reads 1.000 like the reference.
- Why built: Current-half edge pick: combined-audio-realtime E3 says persist live state and cap
  the drain, and treats the two as orthogonal, to be verified separately; combined-lfsr-peak-meter
  E1 says a peak meter cannot see a wrong-register resume. Neither tested what the cap does to
  the timing of the state-restore message itself.
- Design: Stdlib Python. 16-bit Galois LFSR noise plus a driven, clipped 220 Hz carrier, 48 kHz,
  128-sample callbacks, 384 samples before suspend and 64 callbacks after resume; generator
  rebuilt from DEFAULT_SEED on reload. Queue = 2048 repair messages plus one RESTORE carrying the
  saved register, 9 us per message, cap 64, budget 2800 us. Policies: capped FIFO with RESTORE
  last; same but RESTORE advances the register by the samples elapsed; priority slot (RESTORE
  applied before the capped drain); uncapped FIFO; capped FIFO with RESTORE enqueued first.
  Compared against a continuous render by sample mismatch, noise-bit mismatch, peak, a 32-bin
  DFT magnitude delta and a CRC.
- Got right: Both source lessons hold inside the composition: the cap kept every capped policy at
  576 to 585 us against 18441 us uncapped, and the peak meter read 1.000 for every policy
  including the broken one, while the DFT delta (404.9) and CRC caught it. Applying the restore
  ahead of the drain (priority slot or RESTORE-first) gave 0 mismatches at 576 to 585 us.
- Where/why it failed: Verifying continuity and budget separately, as E3 advises, passes this bug:
  continuity was proven with an immediate restore and budget with a capped drain, but together
  the cap moves the restore 32 callbacks late, and a late restore of the suspend-time register is
  not a short glitch but a lasting slip (14.2% of later samples audibly wrong, 49.8% of noise
  bits). My 40%-audible prediction missed because only 22.0% of samples escape the clip.
- Fix: Apply generator state-restore messages outside the capped drain (a priority slot read
  before the drain, or the head of the queue), and keep the cap for bulk repair only; if the
  restore can arrive late, advance the saved register by the samples rendered since resume
  (that gave 0% after the restore, though 624 samples before it stayed wrong).
- Why this fix: The drain cap protects the callback by deferring work, which is safe for work
  whose effect does not depend on when it lands; a state restore is time-indexed, so deferring
  it changes the stream from then on, and only ordering it first or time-correcting it keeps
  the restore valid under the cap.
- Rule of thumb: A drain cap must not defer a generator-state restore: queued behind a 2048-message
  burst at cap 64 it landed 32 callbacks late and left 49.8% of LFSR bits wrong for good with peak
  still 1.000; restore ahead of the capped drain.
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__capped-drain-delays-lfsr-restore-into-permanent-phase-slip.py;
  it printed restore on callback 32, 14.2% audible and 49.8% noise-bit mismatch after it, peak
  1.000 equal to the reference, DFT delta 404.9, priority slot 0% at 585 us, uncapped 0% at
  18441 us, RESTORE-first 0% at 576 us. Message costs reuse E3's 9 us figure; the voice is my
  model, not the original Node sandboxes.
- Composed: sandbox-combined-audio-realtime/E3, sandbox-combined-audio-realtime/E1, sandbox-combined-lfsr-peak-meter/E1
- Picked-by: current-half
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-15__capped-drain-delays-lfsr-restore-into-permanent-phase-slip.py
- Prediction: Written before the first run: capped FIFO applies RESTORE on callback 32 and 40% or
  more of post-resume samples mismatch for good; peak 1.0 for both; DFT delta above 0; priority
  slot 0 mismatches within 2800 us; uncapped 0 mismatches over budget; RESTORE-first FIFO 0
  mismatches. Run 1 failed only on the 40%. Added before run 2: noise-bit mismatch after
  restore 40% or more; audible share at most the unclipped share; advance-on-restore 0% after.
- Observed: RESULT: PASS capped FIFO applies the live-register restore on callback 32 and stays
  wrong after it (14.2% of later samples, 14.8% overall) with peak 1.000 = ref, dft delta 404.9,
  crc differs; priority slot 0% at 585 us worst; uncapped 0% at 18441 us; restore-first FIFO
  0.0% at 576 us; noise bits wrong 49.8% after restore (only 22.0% of samples unclipped);
  advance-on-restore 0% after, 624 wrong samples before.
- Scenarios: 1) capped FIFO with RESTORE behind the burst; 2) same with time-advanced restore;
  3) priority slot; 4) uncapped FIFO; 5) BREAK: capped FIFO with RESTORE enqueued first, built to
  show the cap alone is not the cause (0% mismatch at 576 us: ordering is).
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 5 pass 2

## E1 — callback gap must fit the clip or become a runner
- Date: 2026-10-15
- Project: Pappydapimp69/brain-creative-training
- Tags: [humor][comedy][structure][simulation]
- What: Modelled what happens to stand-up callbacks when a set is cut into short social clips.
  A callback only lands in a clip if the antecedent joke, an earlier runner mention, or a premise
  reminder is inside the same clip; the gap between antecedent and callback therefore decides
  whether the payoff survives clipping, independent of how well it played in the room.
- Why built: New-domain pass in Comedy and humor. brain query on callback, standup, clip, tag and
  rule-of-three returned no comedy lessons on callbacks or on clipping a set for short video; the
  existing humor lessons cover style typology, timing pauses and localization.
- Design: Deterministic exhaustive model: a 1200 s set with each callback at 600 s and its
  antecedent at 600 minus a gap of 30, 60, 120, 240, 360 or 480 s. Clips of 30, 60 and 90 s at
  every integer start (uniform clipping), or chosen to end 3 s after the callback (the creator
  clips the biggest laugh as the closer). Variants: a runner mentioned every 60 s across the same
  240 s span, and a one-line premise reminder 5 s before the callback. Checked against the
  analytic land fraction max(0, L-g)/L.
- Got right: Uniform 60 s clips: a 30 s gap landed 0.508 (analytic 0.5), every gap of 60 s or more
  landed at most 0.016, mean over six callbacks 0.087. Closer clips landed 1 of 6 at 60 s and 2 of
  6 at 90 s. A runner every 60 s landed in a 90 s closer clip where a single 240 s callback did
  not, and the 5 s reminder lifted the 60 s mean to 0.918 (6 of 6 in closer clips).
- Where/why it failed: My first run put every callback at 590 s of a 600 s set, so clips were
  pinned against the set end and a 30 s gap read 1.0 instead of 0.5; that was an edge artifact of
  my layout, fixed by centring the callback. A runner does not beat the clip, it only shortens the
  effective gap to its spacing (uniform 90 s clips: 0.341, the same as a 60 s callback). The model
  says nothing about whether a reminder deflates the callback live, and uses no audience data.
- Fix: When a set will be clipped, write two kinds of callback: short-gap ones that fit inside
  the clip length (gap under about L minus the tail after the laugh) and long-gap ones meant only
  for the room; for any long-gap callback that must work in a clip, either turn it into a runner
  with mentions spaced under the clip length, or add a one-line premise reminder just before it.
- Why this fix: The land fraction is set by geometry, (L-g)/L, so no amount of performance moves a
  callback whose antecedent is outside the clip; spacing or a reminder is the only lever, and the
  break case (full set uploaded, or live) shows the problem disappears when nothing is cut.
- Rule of thumb: A callback survives a short clip only if its antecedent is inside it: in 60 s clips
  a 30 s gap landed 51% and gaps of 60 s or more about 0%, so for clip-bound sets keep callback
  gaps under the clip length or add a 5 s premise reminder (lifted 0.087 to 0.918).
- Provenance (verified/assumed): Verified first-hand: ran 2026-10-15__callback-gap-must-fit-the-clip-or-become-a-runner.py,
  which printed RESULT: PASS with the land fractions above and matched the analytic (L-g)/L within
  0.016. That clips are cut around the biggest laugh, and that a callback without its antecedent
  does not land for a viewer, are craft assumptions; no audience response was measured.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__callback-gap-must-fit-the-clip-or-become-a-runner.py
- Prediction: Written before the first run: uniform 60 s clips land a 30 s gap at about 0.5 and
  gaps of 60 s or more at 0, mean about 0.083; closer clips land 1 of 6 at 60 s and 2 of 6 at
  90 s; a runner every 60 s lands in a 90 s closer clip where a single 240 s gap does not; a 5 s
  reminder lifts the uniform 60 s mean to at least 0.90; the full-set clip lands 6 of 6.
- Observed: RESULT: PASS 60 s clips: callback gap 30 s lands 0.51, >=60 s lands 0 (mean 0.087);
  closer clips land 1/6 at 60 s, 2/6 at 90 s; runner every 60 s lands in 90 s closer, single 240 s
  gap does not; 5 s reminder lifts mean to 0.918; full set 6/6. The first run (callback at 590 s
  of 600) printed FAIL with a 30 s gap at 1.0 and mean 0.182, an edge artifact.
- Scenarios: 1) uniform clips of 30, 60 and 90 s over six gaps; 2) creator clips ending 3 s after
  the callback; 3) a runner every 60 s over 240 s against a single 240 s callback; 4) a premise
  reminder 5 s before each callback; 5) BREAK: the full set as the clip (or a live room), built to
  show every callback landing when nothing is cut.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 3 pass 4

