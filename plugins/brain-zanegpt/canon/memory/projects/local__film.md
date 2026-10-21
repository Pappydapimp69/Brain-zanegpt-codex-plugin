# local/film — lessons

Project: local/film. Newest first.

---

## E21 — style recipes dither and integer scale
- Date: 2026-10-15
- Project: local/film
- Tags: [rendering][canvas][art]
- What: Checked two procedural visual-style recipes from the style research numerically before filing them
  as kernels: Bayer 4x4 ordered dithering and integer nearest-neighbour upscaling for pixel art.
- Why built: The user asked Brain to learn visual styles; the canvas recipes were my synthesis from sourced
  traits, so they needed a sandbox rather than being filed on reasoning alone.
- Design: Stdlib sandbox: count distinct 4x4 dither coverages over 1001 luminance steps; for a 16-pixel art
  row, measure how many screen pixels each art pixel gets under x3, x2.5, and x3 with a 1.5 px offset.
- Got right: Bayer gives exactly 17 levels (0..16 of 16 pixels on); integer x3 gives every art pixel exactly
  3 screen pixels; x2.5 gives a mix of 2 and 3, which is the mixel defect pixel artists warn about.
- Where/why it failed: My break case was wrong: I predicted a half-pixel offset at integer scale would also
  mix pixel sizes, but it stayed uniform at 3, so offset alone is not a mixel source in a nearest blit.
- Fix: Narrowed the rule to what reproduced: mixels come from the SCALE factor (non-integer or per-sprite
  scaling), so fix the scale to an integer and keep sprites unscaled; positions only need integer rounding
  for sharp edges inside the low-res buffer, not to avoid mixels.
- Why this fix: Filing the offset claim would have sent future work chasing rounding bugs that cannot cause
  mixels, while the real cause (fractional scale) stays unguarded.
- Rule of thumb: In pixel-art canvas rendering, guard the upscale factor (integer, smoothing off) because a
  fractional scale is what mixes pixel sizes; Bayer 4x4 gives 17 tones from two colours.
- Provenance (verified/assumed): verified first-hand by running the sandbox; 3 scenarios, numbers below.
- Composed: ideas:ART/pixel-art/one-grid-integer-scale-no-mixels, ideas:ART/dithering/bayer-4x4-gives-17-levels-from-two-colours
- Sandbox: sandboxes/2026-10-15__style-recipes-dither-and-integer-scale.py
- Prediction: 17 dither levels; x3 uniform 3; x2.5 mixed 2 and 3; x3 with a 1.5 px offset mixed (break case).
- Observed: RESULT: PASS bayer 17 levels=True; integer scale uniform [3]; 2.5x mixed [2, 3]; offset x3 [3]
- Scenarios: 1) integer x3 scale; 2) fractional x2.5 scale; 3) integer x3 with 1.5 px offset (built to BREAK
  the claim; it did not, which narrowed the rule to scale only).
- Link: film session 2026-10-15, style research; session_0169rjPqYDYawkbeTUEzoNKo
- Cited-by: 2026-10-15 · projects/pappydapimp69__demo-disc.md#E16 · compatible · no sandbox · Demo-disc commit "The Last Note: readable text and a how-to card before every funeral"; session_011p52L2CkFXcsYRwjDu6tG9
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-creative-training.md#E16 · compatible · sandboxes/2026-10-15__safe-zone-shrink-makes-world-dither-reveal-uneven.py · observed RESULT: PASS integer s6 beats 1.00/err 0/swim 0 (screen-anchor swim 64); 90% safe-shrink s5.4 beats 1.21x err 0.0147 swim 0 shimmer 0.0119; floor s5 1.00x; phone s1.22 beats 4.00x err 0.1325. Also 1366x768 at 4.27: 1.56x, shimmer 0.0311; p… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 4 pass 2

## E20 — idle wall exponential cost
- Date: 2026-10-15
- Project: local/film
- Tags: [gamedesign][economy][sandbox]
- What: Checked the idle-game pricing claim from the genre research (cost = base x growth^n, production
  linear in owned count) by simulating purchase wait times, before filing it as a design kernel.
- Why built: The user asked Brain to learn game genres; idle/tycoon economics was a sourced formula, but the
  "it creates a wall and prestige pushes it back" consequence was my inference and needed a model.
- Design: Stdlib sandbox buying 150 generators greedily; wait = (cost - money) / production; scenarios with
  growth 1.07, flat cost 1.00, and growth 1.07 with a x10 prestige multiplier; wall = first wait over 60 s.
- Got right: At growth 1.07 waits go 0.79 s (buy 10), 2.36 s (50), 34.7 s (100), 682 s (150), first over
  60 s at buy 109; flat cost never walls (waits shrink to 0.03 s); x10 prestige moves the wall to buy 147.
- Where/why it failed: Nothing broke, but the x10 multiplier bought only 38 more purchases because exponential
  cost eats a constant multiplier in log(10)/log(1.07) = 34 steps, so prestige is a short reprieve, not a fix.
- Fix: Filed the rule with the log relation: a prestige multiplier m delays the wall by about log(m)/log(growth)
  purchases, so designers size prestige bonuses against the growth factor, not as a flat feel-good number.
- Why this fix: It turns the qualitative wall into a tunable number a designer can set before playtests.
- Rule of thumb: With cost growth g, a prestige multiplier m pushes the progress wall back about log(m)/log(g)
  purchases (x10 at g 1.07 gave 38, predicted 34); flat costs never wall.
- Provenance (verified/assumed): verified first-hand by running the sandbox; numbers below.
- Composed: ideas:GAME-DESIGN/idle-math/exponential-cost-over-linear-production-makes-the-wall
- Sandbox: sandboxes/2026-10-15__idle-wall-exponential-cost.py
- Prediction: growth 1.07 walls within 150 buys; flat cost never walls; x10 prestige delays the wall by
  roughly 30-40 buys.
- Observed: RESULT: PASS wall at buy 109 (1.07), none with flat cost, prestige x10 moves it to buy 147
- Scenarios: 1) growth 1.07; 2) flat cost 1.00 (built to BREAK the wall claim; no wall, as the model says);
  3) growth 1.07 with x10 prestige.
- Link: film session 2026-10-15, genre research; session_0169rjPqYDYawkbeTUEzoNKo

## E19 — reveal timing sidecar spoils info gaps
- Date: 2026-10-15
- Project: local/film
- Tags: [narrative][tooling][testing]
- What: On a real six-scene film script, reveals timed in a hand-kept sidecar of absolute
  times fired before the line that opens their gap in 14 of 20 single-line rewrites (+8
  words), spoiling 29 reveals; reveals anchored to their setup line spoiled none.
- Why built: New-half train pick: tension-as-information-gap (tension comes from the order
  and rationing of information) on the film project, with the collective-reference lesson
  (a hand-maintained sidecar drifts silently) as companion: reveal timing is that sidecar.
- Design: Parsed the Five Days script: narration lines with hold times and reveal marks
  anchored as line-start plus offset. Caption time per line = max(hold, 1 + words/2.6), as
  the engine sizes captions. Froze absolute reveal times from the original, then
  lengthened or shortened each line by 8 words in turn and compared.
- Got right: Anchoring each reveal to the line that sets up its gap keeps the order under
  any rewrite; the engine already does this, which is why caption edits across this
  session never spoiled a beat.
- Where/why it failed: The sidecar fails silently and asymmetrically: longer lines spoil
  reveals (gap closed before it is opened, 29 reveals); shorter lines never spoil but leave
  24 reveals over 0.5 s late, holding a gap after the narration already resolved it. The
  derived 0 is safe by construction, so the sidecar counts are the informative result.
- Fix: Store every reveal as an offset from the narration beat that opens its gap, never
  as an absolute time, and derive scene length from the captions so edits cannot reorder
  what the audience learns.
- Why this fix: Tension lives in the order of information, so the order is the thing to
  store; absolute times only encode it indirectly and any rewrite breaks the encoding
  without an error.
- Rule of thumb: Time a reveal from the line that opens its gap, not from the clock; an
  absolute-time cue list spoils reveals on lengthened lines and leaves dead air on cut ones.
- Provenance (verified/assumed): verified first-hand by the sandbox below on the real
  script (snapshot shipped beside it as a fixture); the caption timing formula is the
  engine's; the 8-word edit size is my choice.
- Composed: ideas:SYSTEM/narrative/tension-as-information-gap, film/E1, collective-reference/E1
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-15__reveal-timing-sidecar-spoils-info-gaps.py
- Prediction: Written before running: derived spoils 0 reveals for any edit; sidecar spoils
  at least one reveal for most single-line +8-word edits.
- Observed: RESULT: PASS derived 0 spoils; sidecar spoiled at least one reveal in 14/20
  single-line edits (29 reveals); -8-word edits: 0 spoiled, 24 late by over 0.5 s.
- Scenarios: 1) +8 words on each line, derived anchors; 2) +8 words, frozen sidecar;
  3) -8 words, frozen sidecar (built to break the spoil claim: it cannot spoil, only lag).
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-15 · projects/local__fail-ad-cutdowns-keep-the-gap.md#E1 · compatible · sandboxes/2026-10-15__fail-ad-cutdowns-keep-the-gap.py · observed RESULT: PASS clock truncation keeps the fixable-fail ending in 0/4 cut-downs; beat-anchored keeps it in 3/4 (10, 15, 20); 6 s lost by both. · https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-15 · projects/local__hook-caption-budget.md#E1 · compatible · sandboxes/2026-10-15__hook-proposition-word-budget.py · observed RESULT: FAIL (readable count) by 3 s: BBC 8-9 words, Netflix ~10, film engine 5; kernel's 10 w/s is 3.3x BBC's fastest; propositions readable by 3 s (BBC fast): 4/6. · https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-auto-training.md#E7 · compatible · sandboxes/2026-10-15__ending-check-on-a-cut-down-passes-cuts-that-dropped-the-gap-opening-beat.py · observed RESULT: PASS 167/488 cut-downs that end on the reveal lost the gap at HMIN=3 (0.342 even at HMIN=0), so their h* is 0.0455 not 0.0122; rescaled cue list mistimed 210/321 gap-keeping cuts (early 0, late 210). Both mechanism guesses were wro… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 2 pass 2
- Cited-by: 2026-10-17 · projects/pappydapimp69__brain-auto-training.md#E30 · compatible · sandboxes/2026-10-17__beat-recut-keeps-the-gap-clock-recut-spoils-it.py · observed RESULT: PASS beat recut keeps the gap down to 10s (passes [20, 15, 10]), tail trim passes only [], uniform squeeze passes [20]; below 10s nothing works (8s fails) · brain train auto loop 2 pass 1; session_01LG4GQFTi9A1QxnCzb5c6CV

## E18 — comedy rubric retrodicts verdicts
- Date: 2026-10-15
- Project: local/film
- Tags: [comedy][narrative][process][testing]
- What: After the user called a merge-to-evolve parody "stupid", five comedy-craft kernels were researched (game of
  the scene, Jones's rule card, hack-premise check, benign violation, Carroll's sight-gag types). Features drawn from
  them were scored on six shorts made this session and compared with the user's own verdicts (liked: PLEASE HOLD,
  SAFE MODE 90, ONLY 1% v2; mixed: ONLY 1% v1; disliked: PRIMORDIAL PAIRS; one short without a verdict).
- Why built: The obvious diagnosis ("the premise was a cliché") needed checking before it became the rule, because two
  well-received shorts also started from stock premises (Death on hold, the overprotective AI).
- Design: Binary features per short (A visible character agency, B physical or sight-gag payoff, C non-stock premise,
  D single game, E benign violation at the payoff), scored and tested one at a time and together for whether every
  disliked short scores below every liked one, plus pairwise rank concordance.
- Got right: The full rubric separated cleanly (liked minimum 4, disliked 1, concordance 0.86), and so did agency
  alone, physical payoff alone and benign violation alone (0.79 each). The failed short was the only one with no lead
  character and a payoff carried by a label ("MEETING!") and wordplay.
- Where/why it failed: The intuitive fix, avoiding cliché, did not separate them at all (concordance 0.50, equal to
  chance): both liked films had stock premises rescued by a character acting physically. "One game only" did not
  separate them either (0.64), because the failed short did hold one game. The coding is post hoc by the author, who
  knew the verdicts, with five rated pieces, so this is a consistency check of the rubric.
- Fix: Before scripting a short, require a lead with a visible want who acts on the world, a payoff that is an action
  or a named sight gag rather than a caption or label, and a payoff that is a violation read as benign at the same
  moment. Run the hack-premise check as secondary polish, not as the main gate.
- Why this fix: The features that separated the verdicts are the ones a no-voice vertical short can actually show,
  while "is it original?" is the one the work kept failing to predict and the easiest to over-weight after a miss.
- Rule of thumb: For a no-dialogue comedy short, check for a lead with agency, a physical or sight-gag payoff, and a
  benign violation at the payoff before worrying about originality. In this session's six shorts those three each
  separated liked from disliked, and the cliché check alone scored at chance.
- Provenance (verified/assumed): Verified first-hand: the sandbox was run and printed the RESULT line quoted below,
  with the prediction written down before the run.
- Composed: film/E3, film/E12, ideas:SYSTEM/narrative/tension-as-information-gap
- Sandbox: sandboxes/2026-10-15__comedy-rubric-retrodicts-verdicts.py
- Prediction: written before the run: agency (A) and physical payoff (B) would each separate the disliked short from
  the liked ones, and the hack-premise check (C) alone would fail to separate them, because two liked shorts used stock
  premises.
- Observed: RESULT: PASS agency and physical payoff each separate liked from disliked (concordance 0.79/0.79);
  hack-premise check alone does not (concordance 0.50); n=5 rated, post hoc coding. Full rubric 0.86; benign
  violation alone 0.79 and separates; one-game alone 0.64 and does not.
- Scenarios: 1) full rubric A-E; 2) agency only; 3) physical payoff only; 4) hack-premise check only (built to BREAK
  the avoid-cliches claim); 5) one game only; 6) benign violation only.
- Link: session https://claude.ai/code/session_0169rjPqYDYawkbeTUEzoNKo (film11.html critique, SCRIPT1-11)
- Audited: 2026-10-15 · fail · Read the entry and re-ran its stored sandbox (RESULT PASS reproduced). The arithmetic is computed, but the answer is built in by the fixture: only ONE short is disliked, and features A (agency), B (physical payoff) and E (benign violation) are coded 1 on all five other shorts and 0 on that one, so they are the same column. Any feature the author coded 0 on the dud 'separates' liked from disliked and scores the same 0.79 concordance; the test cannot tell A, B and E apart and cannot fail for a feature coded that way. The coding is post hoc by the author who knew the verdicts (the entry says so). The Rule of thumb claims each of the three features separated liked from disliked as a check to apply to future shorts; what was tested is n=1 disliked against 3 liked, which supports 'the dud lacked all three' and no more. The hack-check-at-chance result is real but also n=1. To test it: code features blind to verdicts, or predict verdicts on new shorts before the user rates them. · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto pass 3 (audit), 2026-10-15

## E17 — progression board spoils the top
- Date: 2026-10-15
- Project: local/film
- Tags: [narrative][comedy][gamedesign]
- What: A merge-to-evolve parody built its gag on an evolution chain whose top is hidden as "???" (cell, fish, frog,
  monkey, caveman, office worker, manager, then the meeting). The choreography needed spare office workers on the
  board as merge partners, so three were placed there from frame 0. In the beat stills, the top-tier character was
  visible before the chain had earned it, spoiling the progression and hinting at the office ending in the hook.
- Why built: A scripted merge sequence needs every partner tile to exist on the board when its merge fires, and the
  simplest layout puts them all in the initial grid.
- Design: Partners for the low tiers (fish, frog, monkey, caveman) sat on the starting board, which is normal for the
  format. The same was done for the high tier without considering what it revealed.
- Got right: Hiding the final tier behind "???" in the chain bar, and revealing it only at the end, kept the payoff
  intact. The leak was only on the board.
- Where/why it failed: A board is part of the information the viewer reads in the first second, so any item placed
  there is a spoiler for its tier. Low-tier partners are fine, but a partner from the destination tier answers the
  question the hook asks.
- Fix: Keep destination-tier partners off the starting board and introduce them as an in-world reward (they drop
  into empty slots with "NEW!" right after the first worker evolves), so they appear only once the chain has earned
  them.
- Why this fix: The reward drop is a native mechanic of the format, so it costs no explanation, keeps the because chain
  (making a worker unlocks workers), and preserves the information gap that powers the reveal.
- Rule of thumb: In a progression gag, audit the opening frame for anything above the tier the story has reached.
  Partners or props from later tiers spoil the climb, so bring them in as in-world rewards at the moment they're
  earned.
- Provenance (verified/assumed): verified first-hand: the stills showed three office workers on the board at t=0.3,
  and after the change none appeared before the 4.3 s reward drop. Audience impact is untested.
- Composed: ideas:SYSTEM/narrative/tension-as-information-gap
- Link: session https://claude.ai/code/session_0169rjPqYDYawkbeTUEzoNKo (film11.html)

## E16 — overshoot ease negative radius
- Date: 2026-10-15
- Project: local/film
- Tags: [film][animation][canvas]
- What: A 600-frame canvas render died at frame 504 (t=21.0, the first frame of the end card) with
  "IndexSizeError: The radius provided (-2.34035e-15) is negative". A pop-in scale used an overshoot ("back") ease,
  and back(0) evaluates to 1 + 2.7*(-1) + 1.7*1, which is about -2e-15 in floating point instead of exactly 0. That
  scale fed a stick figure's head radius.
- Why built: Pop-in animations everywhere in the short (stars, buttons, cards, characters) use one overshoot ease for
  a springy entrance, multiplied into sizes.
- Design: Sizes are computed as base times ease(progress), and progress is clamped to [0, 1], so the author assumed
  the result could never go below zero.
- Got right: The clamp on progress was correct. Only the polynomial's evaluation at exactly 0 misbehaves, and only
  canvas arc() rejects negatives (rects and lines silently accept them), which is why it surfaced on a single frame
  so late.
- Where/why it failed: Canvas arc() throws on any negative radius, including -0-ish float noise, and the first frame of
  each pop-in sits exactly at progress 0. Earlier pop-ins happened to land just past 0 on the 24 fps grid, which hid
  the bug until the end-card timing aligned exactly.
- Fix: Clamp at the drawing primitive (the radius passed to arc is max(0, r)), so every caller is covered, plus
  re-rendering. Clamping only the one end-card call would leave the next pop-in exposed.
- Why this fix: The fault is a frame-grid coincidence, so a per-callsite fix would recur wherever a pop-in starts on
  an exact frame. One guard in the primitive costs nothing and is total.
- Rule of thumb: An overshoot or back ease can return about -1e-15 at exactly t=0, and canvas arc() throws on any
  negative radius. Clamp radius to max(0, r) inside the circle helper rather than trusting a clamped progress value,
  because the failure only appears when a pop-in starts on an exact frame.
- Provenance (verified/assumed): verified first-hand: the render log shows the exception at frame 504 with the value
  quoted, and after the clamp in the helper the same frames and the full 600-frame render completed cleanly.
- Composed: N/A
- Link: session https://claude.ai/code/session_0169rjPqYDYawkbeTUEzoNKo (film10.html)

## E15 — invented name check store
- Date: 2026-10-15
- Project: local/film
- Tags: [process][research][legal]
- What: A fake crowd-runner game for a parody short was first named "Crowd Clash", which felt invented. A quick search
  for the real format showed an existing app store title "Count Master: Crowd Clash Run", so the "invented" name was
  a near-copy of a real product in the same genre. It was renamed STICK SWARM 3D before any rendering.
- Why built: The channel rule is to invent every game name and logo so parodies never imitate a real product.
- Design: Names were generated from the genre's vocabulary (crowd, clash, count, run), the same vocabulary real titles
  in that genre are built from, so collisions are likely by construction.
- Got right: The format research done before scripting was what surfaced the collision, at zero cost, before the name
  was baked into frames and an end card.
- Where/why it failed: "Sounds made up to me" is not a check. Genre-vocabulary names converge on real titles because
  real titles in the genre come from the same words.
- Fix: Search the candidate name plus the genre in the app stores and on the web before using it, and prefer names
  that leave the genre's stock words (here STICK SWARM 3D instead of CROWD CLASH).
- Why this fix: A renamed end card is one string before rendering and a full re-render after, and a collision with a
  real product undermines the channel's own no-real-names rule.
- Rule of thumb: An invented game name built from its genre's stock words often already exists (Crowd Clash matched a
  real Count Master title). Search the name in the app stores before use, and prefer names outside the genre
  vocabulary.
- Provenance (verified/assumed): verified first-hand: the web search this session returned the App Store listing
  "Count Master: Crowd Clash Run", and the replacement name was used throughout. A trademark search was not done.
- Composed: N/A
- Link: session https://claude.ai/code/session_0169rjPqYDYawkbeTUEzoNKo (SCRIPT10.md)

## E14 — hook needs sound at frame zero
- Date: 2026-10-15
- Project: local/film
- Tags: [audio][film][video]
- What: A 25 s vertical short designed its hook on three layers (visual, caption, audio). The audio layer was a giant's
  stomp synced to the picture's bob, sin(3t), whose first impact lands at t=pi/3, about 1.05 s. A per-second RMS scan
  showed the first second at 0.001, so the hook was silent for its most important second, and the music starts at 1.2 s.
- Why built: Sound synced to motion (stomps on the bob's floor contacts) is the right default, and it put every stomp
  on the right frame except that it created none at t=0.
- Design: Event times were derived from the animation's phase (k*pi/3 for k from 1). Nothing asserted coverage of the
  opening window, and the music cue was placed after the run starts.
- Got right: Phase-derived event times kept every later stomp exactly on the visible impact, with no manual
  alignment.
- Where/why it failed: Deriving sound from motion phase silently inherits the motion's starting phase, so if the
  animation begins mid-cycle the first sound event can land a second late. A whole-file or 2 s-window scan averages
  over it, and only a 1 s window exposed the gap.
- Fix: Add an explicit frame-0 hit (a stomp plus a short sting) independent of the phase grid, and scan RMS per second
  so the opening second is measured on its own (0.001 before, 0.20 after).
- Why this fix: Short-form viewers decide in the first seconds, and a hook layer that arrives at 1 s is missing for
  most of that window. A deliberate t=0 cue is one line and does not disturb the phase-synced stomps that follow.
- Rule of thumb: For a short-form hook, put a sound on frame 0 explicitly. Don't rely on motion-phase-derived events,
  whose first hit lands wherever the cycle starts. Check the opening with a 1 s RMS window, not a coarser one.
- Provenance (verified/assumed): verified first-hand: the per-second RMS read 0.001 for 0-1 s before the fix and 0.202
  after. That a silent first second costs retention is from the hook research gathered this session, not measured here.
- Composed: N/A
- Link: session https://claude.ai/code/session_0169rjPqYDYawkbeTUEzoNKo (audio10.py)
- Cited-by: 2026-10-17 · projects/pappydapimp69__brain-auto-training.md#E39 · compatible · sandboxes/2026-10-17__frame-zero-sound-hook-factor-in-ipm-d1-ranking.py · observed RESULT: PASS with independent sound (K=0) IPM*D1 still picks fidelity 1.0 with sound on, IPM-only picks 0.4; dropping the sound in a recut loses 20 percent; once sound lifts low-fidelity ads enough (first flip K=1.0) the IPM*D1 winner leav… · brain train auto loop 2 pass 1 (scheduled run 2026-10-17); session_01MUFH1b1Lc27PXz6rjHHodQ
- Cited-by: 2026-10-17 · projects/local__hook-frame0-audio-vs-promise-cap-recut-rank.md#E1 · compatible · sandboxes/2026-10-17__hook-frame0-audio-vs-promise-cap-recut-rank.py · observed RESULT: PASS IPM*D1 picked promise 0.5 in 3/3 scenarios; IPM alone picked [1.0, 1.0, 0.6] · brain train auto loop 1 pass 1; session_01696mc4JbaRUYgcwwnaPSG1

## E13 — removing an audio layer exposes dead air
- Date: 2026-10-15
- Project: local/film
- Tags: [audio][film][process]
- What: A vertical comedy short deliberately cut its music when the character turned to talk to camera, with
  pitched voice blips carrying the scene. When the user asked to keep the speech bubbles but remove the voice blips,
  the same 10 s talk scene became near-total silence (windowed RMS 0.003 against 0.05-0.19 elsewhere).
- Why built: The music cut was a designed silence beat (the reveal lands in the quiet), and it worked only because
  another layer (the voices) still filled the scene.
- Design: The score was built in layers on one clock (music, sound effects, voices), and each layer was judged on
  its own. The silence beat was authored as "music off", not as "this many seconds of quiet".
- Got right: The windowed RMS scan that runs after every audio build flagged the 10 s gap immediately, before the
  mux, with no listening needed.
- Where/why it failed: Removing one layer silently changed what another layer's choice meant. "Music off" turned
  from a short beat under dialogue into 10 s of dead air, which is fatal on a short-form feed. Nothing in the music
  code changed, so a review of that code could never catch it.
- Fix: Keep the silence beat short (0.7 s after the cut), then fill the rest with low, diegetic ambience (lava
  bubbles, drips, a low hum, about 0.05 RMS) so the scene is quiet but alive.
- Why this fix: The joke needs contrast with the jingle, not literal silence, and ambience keeps that contrast while
  holding attention. Restoring the blips was not an option because the user removed them on purpose.
- Rule of thumb: After removing any audio layer, rescan the mix for silent windows, because another layer's
  intentional gap may now be dead air. Author silence beats as a duration (under about 1 s), then a low ambient bed.
- Provenance (verified/assumed): verified first-hand: the windowed RMS read 0.003 across 10-20 s after the blips were
  removed and 0.044-0.051 after the ambience bed. How viewers perceive it is untested.
- Composed: N/A
- Link: session https://claude.ai/code/session_0169rjPqYDYawkbeTUEzoNKo (audio9.py)

## E12 — parody stays inside the fiction
- Date: 2026-10-15
- Project: local/film
- Tags: [narrative][comedy][structure]
- What: A fake mobile-game ad parody had its character name the format ("Everyone can. That's the ad.") and closed on a
  winking disclaimer ("*Gameplay not representative."). The user's note: the ad should not reference that it is an
  ad. The replacement kept every gag inside the game's own physics: a third lever, a drain, a gold fountain, and the
  cursor's habit of pulling the lava pin.
- Why built: The first draft aimed the joke at the ad business model, which ZaneGPT had picked over "the player is
  dumb", and it delivered that by saying it out loud.
- Design: v2 makes the cursor's behaviour the antagonist and lets the format's rules play out in-world. It fails on
  purpose, the knight takes control, and the moment he lets go to claim his reward the cursor goes straight back to
  the lava.
- Got right: The target (the format's fixed outcome) survived intact, and the ending got stronger because the success
  is real on screen (gold covers the floor) before it is destroyed, a bigger reversal than any spoken line.
- Where/why it failed: A line that names the format explains the joke, breaks the parody's surface (it must be
  indistinguishable from the real thing at a glance in a feed), and dates the piece to one meta observation.
- Fix: Remove every reference to the format itself (dialogue, disclaimers, labels), and express the satire through
  in-world cause and effect. Give the character a motive line ("...Fine. I'll do it.") instead of commentary.
- Why this fix: Parody works when it copies the format exactly and the absurdity comes from inside the rules. The
  user identified this, and it matches the channel note to copy the ad format exactly and then flip it.
- Rule of thumb: In a format parody, never let a character or caption name the format. Copy the surface exactly and
  deliver the satire through in-world cause and effect, so a real success destroyed by the format's own habit beats
  any line that explains the joke.
- Provenance (verified/assumed): verified first-hand: the user's note on v1, and v2 rendered with zero format
  references (dialogue, captions and end card were checked in stills). Audience response is untested.
- Composed: N/A
- Link: session https://claude.ai/code/session_0169rjPqYDYawkbeTUEzoNKo (film8.html to film9.html, SCRIPT8.md v2)
- Cited-by: 2026-10-15 · projects/local__film.md#E18 · compatible · sandboxes/2026-10-15__comedy-rubric-retrodicts-verdicts.py · observed RESULT: PASS agency and physical payoff each separate liked from disliked (concordance 0.79/0.79); hack-premise check alone does not (concordance 0.50); n=5 rated, post hoc coding. Full rubric 0.86; benign violation alone 0.79 and separate… · session https://claude.ai/code/session_0169rjPqYDYawkbeTUEzoNKo (film11.html critique, SCRIPT1-11)
- Cited-by: 2026-10-15 · projects/local__sandbox-ad-hook-length-ending-network-crossover.md#E1 · compatible · sandboxes/2026-10-15__sandbox-ad-hook-length-ending-network-crossover.py · observed RESULT: PASS 15s wins at h=.04, 45s wins at h=.005, crossover h*=0.0122, ending flips by network (1.65/1.33), frame0 x1.75, naming x0.50 · brain train auto, scheduled run; session_01DvSHWZUgPrcaEhdbqtMZR2

## E11 — vertical safe zone no official spec
- Date: 2026-10-15
- Project: local/film
- Tags: [film][video][research]
- What: Laying out a 9:16 short for TikTok and Shorts needed a caption and button safe zone. Research found that TikTok
  publishes no single pixel spec (it ties the zone to ad format and caption length and ships overlay files), and the
  third-party figures for a 1080x1920 canvas disagree widely: top 100-240 px, bottom 250-660 px, sides 100-120 px.
- Why built: The fake-ad parody puts all story content (caption, puzzle, character, end-card button) on screen in a
  short vertical frame, so content under the app's UI is lost.
- Design: Take the most conservative value from each source per edge (120 px sides, 240 top, 660 bottom at 1080x1920,
  which is 80, 160 and 440 at a 720x1280 render) and keep every story element inside y 160-840 of 1280, using the band
  below only for background.
- Got right: Every caption, bubble, puzzle and the INSTALL NOW button fit inside the conservative zone with room to
  spare, and the beat contact sheet confirmed it frame by frame.
- Where/why it failed: Taking any single tool's numbers at face value can leave key content under the caption block
  because the tools disagree by up to 410 px at the bottom edge, and none states it is official.
- Fix: Use the strictest margin per edge across sources, and treat the platform's own overlay file or a preview with
  captions on as the final check before publishing.
- Why this fix: The cost of an over-conservative margin is a slightly smaller stage, while the cost of an
  under-conservative one is an unreadable punchline. Short-form content is centered anyway.
- Rule of thumb: For TikTok and Shorts layouts, there is no official pixel safe zone, and third-party numbers disagree
  (bottom 250-660 px at 1920). Use the strictest margin per edge (120 sides, 240 top, 660 bottom), then confirm with
  the platform overlay or a captions-on preview.
- Provenance (verified/assumed): verified first-hand from a web search this session (Affroom, House of Marketers,
  Poster.ly, Socialync, AI Carousels pages), and the layout was verified to sit inside that zone in rendered stills.
  The platform overlay check is still pending.
- Composed: ideas:MOTION/camera/safe-title-and-action-margins-90-93-percent
- Link: session https://claude.ai/code/session_0169rjPqYDYawkbeTUEzoNKo (SCRIPT8.md, film8.html)
- Cited-by: 2026-10-16 · projects/pappydapimp69__brainwork.md#E330 · compatible · sandboxes/2026-10-16__bayer-reveal-beats-need-sixteen-divisible-and-world-anchor.py · observed RESULT: PASS densities=17 six-beat steps=[3, 2, 3, 3, 2, 3] offset285 diff=384 px · brain train auto loop 2 pass 1, session 2026-10-16; session_01GUMySc86keAL33RndEKSzH
- Cited-by: 2026-10-16 · projects/pappydapimp69__brainwork.md#E331 · compatible · sandboxes/2026-10-16__check-column-captions-need-per-edge-safe-box.py · observed RESULT: PASS overlay-clear 90%=0 93%=0 strict=6 wide=0; strict all-crop=3/6 · brain train auto pass 1, session 2026-10-16; session_01GUMySc86keAL33RndEKSzH
- Cited-by: 2026-10-16 · projects/pappydapimp69__brainwork.md#E337 · compatible · sandboxes/2026-10-16__bayer-levels-check-column-scale.py · observed RESULT: PASS integer scales worst-phase 17/17, 1.5x worst-phase 10/17, 2.5x keeps 5/17 · brain train auto pass 5 (loop 1); session_01GnLNLCEidq8XM63uFxhmgu
- Cited-by: 2026-10-16 · projects/pappydapimp69__brainwork.md#E342 · compatible · sandboxes/2026-10-16__safe-band-check-column-captions.py · observed RESULT: PASS derived+bottom90 0/8, derived+strict_edges 8/8, naive+mid_band 3/8 · brain train auto pass 2 (loop 1); session_01GnLNLCEidq8XM63uFxhmgu

## E10 — tween clamp parks idle props
- Date: 2026-10-15
- Project: local/film
- Tags: [film][animation][canvas]
- What: In a vertical fake-ad short, a hand cursor animated by a keyframe tween sat visible at its first keyframe
  (bottom-right, y 1060-1100 of 1280) for up to 10 s before each of its entrances, including through a dialogue scene.
  That spot is inside TikTok's bottom UI band, so the prop would sit under the platform's caption and buttons, and
  it read as a stray, frozen cursor.
- Why built: Each attempt in the gag re-uses one tween per prop with keyframes only for its active span, which keeps
  the timeline readable.
- Design: tween(t, keys) clamps to the first value before the first key and the last value after the last key, so
  the "start" position doubles as the idle position for every moment the prop is not animating.
- Got right: Clamping is the right default for props that should hold a pose. The pull, swerve and exit motions all
  read correctly once moving.
- Where/why it failed: A start position chosen as "just off the action" (inside the frame, near the edge) becomes
  a parked, visible prop whenever the clock is outside that prop's keyframe span, and nothing errors. It was found only
  on a beat contact sheet (4 of 24 stills showed the idle cursor).
- Fix: Start and park every entering prop fully outside the frame (here y 1400 on a 1280 canvas), and cull it from
  drawing when its position is off-canvas, so the clamped idle state can never be on screen.
- Why this fix: Per-prop visibility windows duplicate the timing in a second place and drift out of sync. Parking
  offscreen makes the tween's own clamp do the hiding, so the timing lives in one table.
- Rule of thumb: With a clamping keyframe tween, a prop's first keyframe is also where it idles between entrances.
  Put entering props' first and last keys fully off-canvas and cull off-canvas draws, then confirm on stills taken
  between entrances, not only during them.
- Provenance (verified/assumed): verified first-hand: the parked cursor was visible in 4 of 24 beat stills (t=0.5,
  4.5, 12, 15) and gone in the re-rendered stills after moving the start keys to y 1400 with an off-canvas cull.
- Composed: N/A
- Link: session https://claude.ai/code/session_0169rjPqYDYawkbeTUEzoNKo (film8.html)

## E9 — research story fundamentals before scripting
- Date: 2026-10-15
- Project: local/film
- Tags: [narrative][process][research]
- What: Over six dark-comedy shorts, both of the largest story corrections came from the user after a finished
  render. One was the "because/therefore, never and-then" beat test (3 of 9 links failed in film 3). The other was a
  continuity gap after a "DAY 1" reset card (3 gaps: counter reset while the character kept his state, an unplanted
  eviction rule, a missing "chooses to stay" beat). Both are standard storyboarding craft, documented publicly long
  before this session (the Parker/Stone therefore-but rule, setup before payoff, continuity of state).
- Why built: The workflow was premise pressure-test, then script, then render, then user critique. Craft rules
  entered only when the user named them, so each one arrived after a render, and the user, not research, was
  supplying textbook fundamentals.
- Design: The pre-script step checked the joke's target, hidden assumptions and competing endings, and queried
  Brain by keyword. It had no structural checklist and no external research step, and Brain held none of those
  rules until they were filed mid-session.
- Got right: Once a rule was named, it was applied immediately, checked as an explicit beat chain, filed into Brain,
  and reused unprompted on the next films (films 4 to 6 passed the chain test before rendering).
- Where/why it failed: A keyword query returns only what Brain already holds, so an empty result for a fundamental
  read as permission to proceed rather than as a gap to research. Treating the user's critique as the source of
  craft also made the AI dependent on the user for knowledge it could have looked up.
- Fix: Before scripting, run a fundamentals pass built from external research: causal beat chain, setup before
  payoff, continuity of character state across time jumps, who owns any on-screen counter or narrator, and staging
  for the target frame. When a query for a fundamental returns nothing, research it, test it on a small piece, and
  file it.
- Why this fix: Each missed fundamental cost a full render cycle plus a user correction, while a checklist costs
  minutes before any frame exists. Researching up front also fills Brain with rules that transfer to every later
  piece, instead of rules that arrive one critique at a time.
- Rule of thumb: Before scripting a short, research and check the story fundamentals (causal chain, setup and
  payoff, continuity of state, counter or narrator ownership, staging) instead of waiting for critique. A user note
  that cites a known craft rule marks a skipped research step, so file the rule itself, not just the fix.
- Provenance (verified/assumed): verified first-hand: both corrections arrived after full renders (films 3 and 6),
  each matched a publicly documented storyboarding rule, and the user confirmed they were teaching fundamentals,
  which they stated directly. The time cost per missed rule is from this session's render logs.
- Composed: ideas:SYSTEM/narrative/tension-as-information-gap
- Link: session https://claude.ai/code/session_0169rjPqYDYawkbeTUEzoNKo (SCRIPT3.md section 8, SCRIPT7.md)
- Cited-by: 2026-10-17 · projects/pappydapimp69__zanegpt.md#E28 · compatible · no sandbox · https://claude.ai/code/session_01WkbM7ZHHguQoKwyDFf4vYn · https://claude.ai/artifact/1kFmKx74PL3QTXsPNWCAQc

## E8 — reset card needs an owner
- Date: 2026-10-10
- Project: local/film
- Tags: [narrative][structure][comedy]
- What: A dark-comedy short ended Act One on a smash-cut "DAY 1" card (the hero relapses and the ordeal restarts),
  then continued with Act Two. The user flagged a disconnect after the card. Diagnosis found three gaps with one
  root: the counter reset but the hero kept his beard, fitness and knowledge; the eviction rule Act Two relied on
  was never planted; and the second ten-day count passed its end with no beat explaining why he stayed away.
- Why built: The loop card was the strongest button in the film, so it had to survive the extension instead of
  being cut.
- Design: The fix makes the count diegetic. The day cards after the reset become Home's "SAFETY PLAN · DAY n" in
  the antagonist's interface style. The rule is planted as a highlighted clause in the Terms the hero signs
  without reading, and one 10.5 s beat is inserted where the plan completes and the hero chooses to stay.
- Got right: No new mechanic was needed. The plant reused the existing Terms device, and the new beat reused the
  existing drone and campers, so the fix cost about 15 s of screen time and every Act Two link gained a cause.
- Where/why it failed: Act One's cards were narrator-owned, while Act Two silently treated them as a world-owned
  counter, so the reset read as a time loop the visuals contradicted. Also, the first version of the plant scrolled
  by at about 10 px, illegible, and the planted clause reused a section number that was already on screen.
- Fix: Give the reset card an owner (styled as the system's UI, so the count changes hands at the cut), plant the
  rule on screen before the payoff with a scroll-freeze and a push-in to readable size, renumber the clause to the
  row it covers, and add the missing "chooses to stay" beat.
- Why this fix: A literal time loop would have erased the character growth Act Two runs on, and dropping the card
  would kill the best button. Making the counter belong to someone keeps the button and explains why the body
  carries over (only the plan reset).
- Rule of thumb: When a "DAY 1" reset card continues into more story, decide who owns the count. If the character
  keeps his state, the reset belongs to someone in the world, so style the card as theirs and plant the rule that
  triggers it, legibly, before the payoff.
- Provenance (verified/assumed): verified first-hand: all three gaps were traced in the cut, the plant was illegible
  in the first still (about 10 px) and readable after the push-in, and the because/therefore chain across the seam
  now has no "and then" link. Audience reception is not tested.
- Composed: ideas:SYSTEM/narrative/tension-as-information-gap, narrative-design/causality
- Link: session https://claude.ai/code/session_0169rjPqYDYawkbeTUEzoNKo (SCRIPT7.md, film7.html)

## E7 — insert beat by time remap
- Date: 2026-10-10
- Project: local/film
- Tags: [film][animation][audio][tooling]
- What: A 10.5 s scene had to be inserted at 156.5 s into a finished 213 s deterministic canvas film whose later
  scenes, dialogue table, card list, fade list and score were all keyed to hard-coded absolute times. Editing
  every downstream number by hand would have touched dozens of literals across picture and audio.
- Why built: The story fix needed one new beat mid-film, while everything after it was already blocked, verified
  on contact sheets, and mixed.
- Design: The picture dispatcher maps time once: T at or past the insert end gets T minus 10.5 before any later
  scene function sees it, so those scenes keep their original clocks. Only tables drawn in absolute time (dialogue
  lines, cards, fades) were shifted, by a regex pass over entries at or past the insert point.
- Got right: Every downstream scene rendered unchanged on its old clock. The audio reused the old part-two
  synthesis by un-shifting the parsed dialogue back to the old clock, rendering, then splicing: buffer[:insert]
  plus the new beat plus buffer[insert:], so sound effects stayed aligned with no re-timing.
- Where/why it failed: Helpers that read absolute time internally (speaker-position lookups with thresholds like
  T > 191) silently used the wrong clock until the same remap was applied inside them. They draw in the right
  place for the old film and the wrong place for the new one, with no error.
- Fix: Apply the remap at every entry point that takes absolute T (the scene dispatch and the bubble-position
  lookup), and shift only the absolute-time tables. Verify with stills on both sides of the seam.
- Why this fix: One remap at the boundary keeps the change local and reversible, while hand-editing about 40
  literals risks one missed number shifting a single gag by 10 s. Splicing the audio the same way guarantees the
  picture and sound use one time map.
- Rule of thumb: To insert a beat into a timeline-hard-coded film, remap time at the dispatcher (T minus the insert
  length past the seam), shift only absolute-time tables, apply the same remap inside every helper that branches
  on absolute T, and splice audio with the same map.
- Provenance (verified/assumed): verified first-hand: inserted at 156.5 s for 10.5 s. Stills either side of the seam
  (157, 161.5, 165, 168, 196, 211.5) placed every bubble and scene correctly after the helper remap, and the output
  WAV measured exactly 223.5 s with balanced windowed RMS.
- Composed: N/A
- Link: session https://claude.ai/code/session_0169rjPqYDYawkbeTUEzoNKo (film7.html part2, audio7.py)
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E49 · compatible · sandboxes/2026-10-11__time-remap-insert-keeps-cues-in-sync-except-spanning-clips.py · observed RESULT: PASS 5/5; hand desync 3/40; remap 0/40; spanning clips early by 3.0s and 3.0s; pre-T clip 0 · session; brain train auto run 2 pass 2 (edge); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-16 · projects/pappydapimp69__brainwork.md#E338 · compatible · sandboxes/2026-10-16__beat-sheet-sidecar-drift.py · observed RESULT: PASS derived 0 wrong on all 4 edits; index sidecar wrong 5 after an insert and 4 after a reorder; name sidecar 0 on delete/reorder but 1 missing on every added beat · brain train auto pass 5 (loop 2); session_01GnLNLCEidq8XM63uFxhmgu
- Cited-by: 2026-10-17 · projects/local__hand-edited-cue-tables-skew-recut-ranking-remap-does-not.md#E1 · compatible · sandboxes/2026-10-17__hand-edited-cue-tables-skew-recut-ranking-remap-does-not.py · observed RESULT: FAIL remap 0 off cues; hand edits 9 off cues over 4 variants; IPM*D1 winner same=False; IPM winner changed=False · brain train auto loop 2 pass 2, scheduled run 2026-10-17; session_01696mc4JbaRUYgcwwnaPSG1
- Cited-by: 2026-10-17 · projects/pappydapimp69__zanegpt.md#E31 · compatible · no sandbox · https://claude.ai/code/session_01WkbM7ZHHguQoKwyDFf4vYn · https://claude.ai/artifact/1kFmKx74PL3QTXsPNWCAQc

## E6 — mirrored text in flipped character
- Date: 2026-10-10
- Project: local/film
- Tags: [film][rendering][canvas]
- What: Characters face left or right through one cx.scale(dir, 1) at the top of their draw function, so a
  single drawing serves both facings. A prop label drawn inside that function (PIZZA on a box held by a left-facing
  character, passed in as a hold() callback) rendered mirrored, because fillText inherits the flip like every
  other shape.
- Why built: One draw function per character with a facing flag halves the drawing code, and a hold callback lets
  each scene attach props (a fishing rod, a roasting stick, a pizza box) to the hand without editing the character.
- Design: The callback receives hand coordinates in the character's local, already-flipped space and draws there.
  Shapes are symmetric enough that the flip never mattered for them.
- Got right: Every geometric prop (rod, stick, fish, box) attached correctly in both facings with no per-direction
  code. Only glyphs are direction-sensitive.
- Where/why it failed: Text is the one primitive whose mirror image is visibly wrong. The callback had no way to
  know the outer transform was flipped, and code review cannot catch it because the call looks correct. It was
  seen only on a rendered still of a left-facing character.
- Fix: Draw the label in its own save/translate/scale(-1,1)/restore around a centered fillText, which undoes the
  outer flip locally, so it reads correctly. Hand-drawn shapes stay in the flipped space.
- Why this fix: Drawing the label outside the character after the fact would need the hand position in world
  space, which the callback design avoids. A local counter-scale keeps the prop self-contained and costs one
  save/restore.
- Rule of thumb: If a canvas character is mirrored with scale(-1,1) for facing, any text drawn inside its
  transform, including props passed in as callbacks, will be mirrored too. Counter-scale glyphs locally
  (translate, scale(-1,1), centered fillText) or pass the facing into the callback.
- Provenance (verified/assumed): verified first-hand: the mirrored PIZZA label was seen in the rendered still at
  t=201 and read correctly after the local counter-scale in the re-rendered still.
- Composed: N/A
- Link: session https://claude.ai/code/session_0169rjPqYDYawkbeTUEzoNKo (film6.html gateDay90)

## E5 — splice mix loudness match
- Date: 2026-10-10
- Project: local/film
- Tags: [audio][film][tooling]
- What: An expanded 135 s cut reused a finished 61 s film as its first act. The picture was tightened with a
  piecewise time map (a cut beat removed), and the old film's finished, peak-normalized mix was spliced into the
  new score with the same map. After the new mix was peak-normalized as a whole, the spliced act came out about 3x
  quieter (RMS 0.012-0.022 against 0.04-0.06 for the new material).
- Why built: Re-synthesizing the first act's score would have duplicated a whole audio script and risked drifting
  from the shipped version. Splicing the shipped mix with the picture's own time map keeps sound and picture cut
  at the same points.
- Design: One function f4(T) maps new film time to old film time (two segments with a short crossfade at the
  splice). The picture renders through it, and the audio script cuts the old WAV with the same breakpoints.
- Got right: Sharing one time map for picture and sound kept every Day 1 sound effect frame-aligned across the cut
  with no re-timing, and the 50 ms fades hid the splice.
- Where/why it failed: The old mix was already normalized to its own peak, and the new material held a few hotter
  transients (a smash-cut hit, a bear roar). Normalizing the combined track to its single loudest peak pushed the
  dense but peak-limited spliced act down, so loudness was decided by one transient, not by the program.
- Fix: Scale the spliced region so its RMS matches the new material (rms(new) / rms(spliced)), then replace peak
  normalization with a soft limiter (tanh against the 99.5th-percentile level). An RMS scan in 5 s windows
  confirmed both acts land at 0.10-0.20.
- Why this fix: Peak normalization is the wrong tool once a track mixes material with different crest factors.
  Matching program loudness first and taming rare peaks with a limiter keeps the transients' punch without
  letting them set the level of everything else.
- Rule of thumb: When splicing a finished, peak-normalized mix into a new score, match RMS before mixing and
  soft-limit instead of peak-normalizing the result, or one hot transient in the new material silently drops the
  spliced section's level. Check with a windowed RMS scan.
- Provenance (verified/assumed): verified first-hand: windowed RMS before the fix read 0.012-0.022 for the spliced
  act against 0.04-0.06 elsewhere, and after the fix 0.105-0.175 against 0.07-0.21. Listening balance is assumed
  from the meter only.
- Composed: N/A
- Link: session https://claude.ai/code/session_0169rjPqYDYawkbeTUEzoNKo (audio5.py, film5.html)
- Cited-by: 2026-10-15 · projects/pappydapimp69__brainwork.md#E291 · compatible · sandboxes/2026-10-15__film-peak-normalize-level-set-by-filter-switch-transient-df2t-vs-svf.py · observed RESULT: PASS (direction criterion of 3 dB, loosened after the first run showed 5.11, 9.17 and 4.14 dB). The 6 dB magnitude prediction was met only in the 9.17 dB case. Q10 7-sample DF2T diverged. · brain train auto loop 1 pass 2; session_01Kx9Pq1H5qpcbvZJ9u2DPKR

## E4 — numpy synth length mismatch
- Date: 2026-10-10
- Project: local/film
- Tags: [audio][dsp][tooling]
- What: A numpy offline synth for short-film scores crashed with a broadcast error each time two separately
  generated signals were summed: tone(f, d) plus noise(d2), or a fundamental plus an overtone whose durations
  were computed as different float products (int(.95*x*SR) vs int(.9*x*SR)). The same crash recurred in three
  separate score scripts in one session, and a related one came from an envelope whose attack plus release
  exceeded a 15 ms click.
- Why built: Each film's score and SFX are generated from code on the same clock as the canvas render, so they
  stay in sync with the picture. Layering signals (a thud plus a noise burst, a chord plus an octave) is the most
  common operation.
- Design: Small helpers return raw arrays sized int(d * SR), and an add(sig, t) mixes into one master buffer.
  Layering was done inline with plain + between helper outputs.
- Got right: Mixing into the master buffer through add() already clipped to the buffer's end, so writes past
  the end were never a problem. The bug was only in pre-summing layers before add().
- Where/why it failed: Any two layers with different durations, or the same nominal duration reached through
  different float math, produce arrays a few samples apart, and numpy refuses to broadcast them. Envelopes had
  the same flaw: fixed attack and release sample counts larger than a very short signal overflowed the slice.
- Fix: A pad(*xs) helper zero-pads every layer to the longest before summing, and env() caps attack and release
  at n//2. Layers are combined only through pad(), never a bare +.
- Why this fix: Rounding durations identically does not cover deliberately different lengths (a 0.4 s thud under
  a 0.25 s noise tail). Padding to the longest keeps each layer's own length and makes layering associative, so
  the call site never has to reason about sample counts.
- Rule of thumb: In an array-based synth, layer signals through a pad-to-longest helper instead of a bare +,
  and cap envelope attack and release at half the signal length, because separately computed durations differ
  by a few samples.
- Provenance (verified/assumed): verified first-hand: the broadcast error was reproduced in three score scripts
  (shapes 17640 vs 11025, and 116916 vs 110762), and each ran clean after switching to pad(), confirmed by an
  RMS scan of the rendered WAV.
- Composed: N/A
- Link: session https://claude.ai/code/session_0169rjPqYDYawkbeTUEzoNKo (audio2.py, audio4.py)

## E3 — therefore test on short beats
- Date: 2026-10-10
- Project: local/film
- Tags: [narrative][comedy][structure]
- What: The beat list of a 60-second dark-comedy short ("No Filter") was checked against the rule that adjacent
  beats may be joined only by "because" or "therefore", never "and then". Three of nine links failed: the
  reshoot attempt, the memorial livestream, and the mom's cat post each just happened next.
- Why built: The user asked that every beat be caused by the one before it. The draft read fine aloud, but
  the three weak links were exactly the beats where a viewer would ask "why are we here now".
- Design: Write the beats as a numbered chain where each line begins with "because X" or ends with "therefore Y".
  Any line that can only be joined with "and then" is a broken link.
- Got right: The fix needed no new scenes. Each broken link was repaired by making the motive visible in under
  three seconds of screen time: one line of dialogue ("TWELVE?! ...Reshoot.", "Fine. Memorials always trend.",
  "Off my pillow. ...BOO.") or one on-screen caption that names the previous beat's outcome ("Nobody came to
  her stream." in the mom's post).
- Where/why it failed: In a short with no narrator, the writer knows the motive, so the jump feels caused, but on
  screen nothing states it, and the beat lands as a non sequitur. Comedy shorts are vulnerable because each
  gag is written as its own set piece.
- Fix: For every "and then" link, add the smallest on-screen motive that ties the beat to the previous
  outcome, preferably carried by the character (a line) or by an in-world artifact (a caption, a counter).
- Why this fix: Restructuring scenes would cost runtime the short cannot spare. A motive line costs about 2 seconds
  and turns each set piece into a consequence, which also sharpens the joke because the audience sees the
  intent fail.
- Rule of thumb: Test a short's beats by chaining them with only "because" or "therefore". Each "and then"
  link gets one on-screen motive (a character line or an in-world caption naming the previous outcome), not a
  new scene.
- Provenance (verified/assumed): verified first-hand: the chain was written out, three links failed, and each was
  fixed with one line or caption. The final cut is 60 seconds with the same scene count. Audience response is
  not tested.
- Composed: ideas:SYSTEM/narrative/tension-as-information-gap
- Link: session https://claude.ai/code/session_0169rjPqYDYawkbeTUEzoNKo (SCRIPT3.md section 8)
- Cited-by: 2026-10-15 · projects/local__film.md#E18 · compatible · sandboxes/2026-10-15__comedy-rubric-retrodicts-verdicts.py · observed RESULT: PASS agency and physical payoff each separate liked from disliked (concordance 0.79/0.79); hack-premise check alone does not (concordance 0.50); n=5 rated, post hoc coding. Full rubric 0.86; benign violation alone 0.79 and separate… · session https://claude.ai/code/session_0169rjPqYDYawkbeTUEzoNKo (film11.html critique, SCRIPT1-11)
- Cited-by: 2026-10-15 · projects/local__sandbox-gap-lag-wall-from-exponential-hold-cost.md#E1 · compatible · sandboxes/2026-10-15__sandbox-gap-lag-wall-from-exponential-hold-cost.py · observed RESULT: PASS best gap lag is the affordable hold count minus 1 ([7, 3, 2, 1]), one lag past it collapses to [0, 0, 0, 0], and-then baseline 40, bigger budget moves best lag 3 to 6 · brain train auto, scheduled run; session_01DvSHWZUgPrcaEhdbqtMZR2
- Cited-by: 2026-10-15 · projects/local__sandbox-reveal-caption-safe-band-in-vertical-video.md#E1 · compatible · sandboxes/2026-10-15__sandbox-reveal-caption-safe-band-in-vertical-video.py · observed RESULT: PASS title-safe bottom caption shows in 1/4 viewports (gap closure 1 of 4 viewports), only a y 0.25-0.75 band shows in 4/4 and next to the 0.30-0.70 action zone just 44 of 941 sampled positions remain at height 0.06 (two thin bands… · brain train auto, scheduled run; session_01DvSHWZUgPrcaEhdbqtMZR2
- Cited-by: 2026-10-16 · projects/pappydapimp69__brain.md#E195 · compatible · sandboxes/2026-10-16__gap-survives-only-on-derived-causal-beats.py · observed RESULT: PASS gap beat-units early=1 withheld+chained=8 and-then=3 nonderived=4; content metric difference 0 · brain train auto pass 5; session_01BotpwZYRVuevNi8Z2gkH2d
- Cited-by: 2026-10-17 · projects/pappydapimp69__zanegpt.md#E28 · compatible · no sandbox · https://claude.ai/code/session_01WkbM7ZHHguQoKwyDFf4vYn · https://claude.ai/artifact/1kFmKx74PL3QTXsPNWCAQc

## E2 — contact sheet before full render
- Date: 2026-10-10
- Project: local/film
- Tags: [film][rendering][process][testing]
- What: Three deterministic canvas shorts (render(t) scrubbed by Playwright, about 1400-1700 frames each, several
  minutes per full render) were checked by rendering 12 timestamps at story beats into a single 3x4 ffmpeg
  xstack contact sheet BEFORE committing to the full render.
- Why built: A full frame render plus mux takes minutes, and layout bugs in hand-placed vector characters only
  appear at specific beats (a pose, a fall, an insert overlay), so watching the final MP4 is a slow loop.
- Design: Pick one still per dialogue line or blocking change, render only those via the same render(t) path
  used for export, and tile them into one image that can be reviewed in a single look.
- Got right: Across the three films the sheet caught about eight real bugs in seconds, none of them visible in code
  review: guests hidden behind a couch showed legs below it, a cake was drawn over a face, a selfie stick was
  never drawn in the hand, a photo helper overflowed, a phone inset covered the character holding it, and
  overlapping like-counters and comments.
- Where/why it failed: Hiding a character behind furniture by shifting them DOWN does not hide them; the body
  moves into the gap under the furniture. Overlays placed by absolute coordinates collide with characters
  placed by other coordinates. Neither shows up in the code, only in pixels at a specific t.
- Fix: Sheet-first loop: stills at the beats, read the sheet, patch, re-render only the changed stills, and then
  start the full render. A character hidden behind an occluder is clipped to the occluder's top edge
  (clipY = occluderTop - y), not just offset.
- Why this fix: Each sheet costs about 10 seconds against minutes for a full render, and it uses the exact export
  path, so what passes the sheet is what ships. Clipping to the occluder works for any offset, including the
  pop-up animation.
- Rule of thumb: For a deterministic render(t) film, tile one still per story beat into a contact sheet and fix
  it before the full render. Hide characters behind furniture by clipping at the occluder's edge, not by
  shifting them down.
- Provenance (verified/assumed): verified first-hand on three films this session: each listed bug was seen on a sheet
  and confirmed fixed in the re-rendered still before the full render.
- Composed: ideas:MOTION/video-export/render-canvas-cutscenes-to-video-via-paused-scrub-plus-element-screenshot
- Link: session https://claude.ai/code/session_0169rjPqYDYawkbeTUEzoNKo (render.mjs, film2.html, film3.html)
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain.md#E184 · compatible · sandboxes/2026-10-15__bayer-reveal-quantises-an-information-gap-schedule-to-17-steps.py · observed RESULT: PASS linear levels 17, anchored breaks 0/47, screen-anchored breaks 43/47, cubic dead frames at 0: 15 · https://claude.ai/code/session_01MwzyRZN1HRxgk5hnQqG5R4
- Cited-by: 2026-10-17 · projects/pappydapimp69__zanegpt.md#E30 · compatible · no sandbox · https://claude.ai/code/session_01WkbM7ZHHguQoKwyDFf4vYn · https://claude.ai/artifact/1kFmKx74PL3QTXsPNWCAQc

## E1 — canvas helper clip own bounds
- Date: 2026-10-10
- Project: local/film
- Tags: [film][rendering][canvas]
- What: A reusable canvas draw helper (sunsetPic, a "photo" drawn at w x h) was reused inside a phone-screen
  insert. Two of its fillRect calls used height h starting at 0.72h, so they painted down to 1.72h and spilled
  dark ground over the like-counter and caption below the photo inside the phone UI.
- Why built: The short film "No Filter" draws the same sunset selfie in four places (post, memorial frame,
  wall posters, phone feed). One parameterized helper keeps the image consistent across scenes.
- Design: Helpers draw in a local coordinate frame (translate to the slot's origin, pass w and h) and the
  caller composes them inside larger UI (a phone frame that already clips to the screen rect, not to the slot).
- Got right: The phone frame clipped its own screen, so the overflow never left the phone. That hid the bug
  in full-scene views, where the photo filled the screen or sat over a dark background anyway.
- Where/why it failed: The outer clip was the phone screen, not the photo slot. Overflow from a sloppy fillRect
  is invisible wherever the helper is the last or bottom-most thing drawn, and only shows when the helper is
  placed above other UI in the same clip region. It was only caught on a contact sheet of stills.
- Fix: The helper now clips to its own rect (save, rect(0,0,w,h), clip ... restore), so any fillRect sloppiness
  inside it can never paint outside the slot, whoever calls it.
- Why this fix: Fixing the two fillRect heights would fix today's symptom but not the next sloppy shape.
  Self-clipping makes containment a property of the helper rather than of every caller's layout, and it costs
  one save/restore per call.
- Rule of thumb: A canvas draw helper that renders into a w x h slot should clip itself to that slot. A caller's
  outer clip only hides overflow until the helper is reused above other UI in the same region.
- Provenance (verified/assumed): verified first-hand: the overflow was seen in the rendered still at t=13.8 (the like
  counter sat on dark fill) and was gone after adding the self-clip, in the same still re-rendered.
- Composed: N/A
- Link: session https://claude.ai/code/session_0169rjPqYDYawkbeTUEzoNKo (film3.html)
- Cited-by: 2026-10-15 · projects/local__film.md#E19 · compatible · sandboxes/2026-10-15__reveal-timing-sidecar-spoils-info-gaps.py · observed RESULT: PASS derived 0 spoils; sidecar spoiled at least one reveal in 14/20 single-line edits (29 reveals); -8-word edits: 0 spoiled, 24 late by over 0.5 s. · https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-17 · projects/pappydapimp69__brainwork.md#E370 · compatible · sandboxes/2026-10-17__gap-order-ipm-d1-film-cut.py · observed RESULT: FAIL n=2000 IPM->B 1.00, IPM*D1->A 0.82; n=300 0.90/0.75; free-bait ->B 0.97; late-close ->A 0.88 · brain train auto loop 1 pass 5; session_01Lama7i9e3sH8WaxCwd3ESu

- Cited-by: 2026-10-17 · projects/pappydapimp69__brainwork.md#E397 · compatible · sandboxes/2026-10-17__variant-gate-before-ipm-d1-rank-needs-derived-link.py · observed RESULT: PASS IPM-only: none 0.374 naive-gate 0.603 fixed-gate 0.997; once D1 is in the rank the gate adds 0.000 · brain train auto loop 2 pass 1; session_01Jftxp3Xz4k4dPRx9kG19YD
