# local/cel-shading — lessons

Project: local/cel-shading. Newest first.

---

## E10 — toon specular pow is redundant under a step
- Date: 2026-10-15
- Project: local/cel-shading
- Tags: [shaders][cel-shading][rendering][numerics]
- What: In a toon specular the Phong exponent adds no control: with a hard step, step(t, x^s) equals
  step(t^(1/s), x) on every grid point; with the widely copied smoothstep(0.005, 0.01,
  pow(N.H, g^2)) the soft edge stays at 6.3 to 7.0% of the highlight radius for glossiness 4
  to 32, so size and softness are one knob.
- Why built: Cel-shading training with external research: Roystan's toon shader tutorial computes
  pow(NdotH, Glossiness^2) then smoothstep(0.005, 0.01); artists treat glossiness and the
  smoothstep bounds as separate controls, which the maths may not support.
- Design: Exact evaluation on 20,001 values of N.H. Claim 1: compare step(t, x^s) with step(t^(1/s),
  x) for s in 2..1024 and t in 0.01..0.9. Claim 2: for glossiness 4, 8, 16, 32 compute the
  highlight radius (output 0.5) and the angular width between output 0 and 1 of
  smoothstep(0.005, 0.01, x^(g^2)).
- Got right: Claim 1 holds exactly: any exponent and threshold pair equals exponent 1 with threshold
  t^(1/s), because x^s is monotonic on [0, 1]; under a step the highlight is just a cap of
  fixed angular radius.
- Where/why it failed: The fixed smoothstep bounds lock softness to size: radius 42.6 to 5.6 degrees, edge 2.68 to
  0.39 degrees, ratio 0.063 to 0.070, much tighter than my loose 0.5x to 2x bound. A small
  highlight therefore always gets a proportionally thin edge, which on screen is a sub-pixel
  edge that aliases.
- Fix: Drop the pow in toon specular and expose two artist controls instead: cap size as a
  threshold on N.H (or its angle) and edge softness as an angular width, ideally scaled by
  screen-space derivatives (fwidth) so small highlights keep about one pixel of anti-aliasing.
- Why this fix: Exponentiation is a monotonic remap that a threshold already covers, so it only couples the
  two controls; separating size and edge restores both choices and lets the edge be sized in
  pixels, where aliasing actually happens.
- Rule of thumb: Under a step, pow on N.H is redundant (exactly a threshold); with smoothstep(0.005, 0.01)
  the edge stays about 7% of the highlight radius at any glossiness, so expose size and edge
  width separately.
- Provenance (verified/assumed): Verified first-hand by the sandbox below; shader lines quoted from
  roystan.net/articles/toon-shader (fetched 2026-10-15); the fwidth suggestion is standard
  practice, not tested here.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__toon-specular-pow-is-redundant-under-a-step.py
- Prediction: Written before running: claim 1 holds on 100% of grid points; in claim 2 edge/radius stays
  within 0.5x to 2x across glossiness 4 to 32.
- Observed: RESULT: PASS hard-step exponent redundant on all grid points: True; smoothstep(0.005,0.01):
  radius 42.6 -> 5.6 deg as glossiness 4 -> 32, edge 2.68 -> 0.39 deg, edge/radius
  0.063-0.070.
- Scenarios: 1) hard step over 20 (s, t) pairs, built to find any pair where the exponent changes the
  mask; 2) Roystan smoothstep at glossiness 4, 8, 16, 32.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

## E9 — held poses need refresh multiple of 60
- Date: 2026-10-15
- Project: local/cel-shading
- Tags: [animation][cel-shading][timing][rendering]
- What: Held poses (limited animation on twos or threes of a 60 Hz game) reach the eye unevenly on
  displays that are not a multiple of 60 Hz: on twos 144 Hz alternates 4 and 5 refreshes per
  pose (max/min 1.25), 165 Hz 5 and 6 (1.20), 50 Hz 1 and 2 (2.00); 60 and 120 Hz stay exactly
  even.
- Why built: Cel-shading training with external research: GGXrd dropped interpolation so every frame is a
  key pose held like stop motion (Motomura, GDC 2015); holding poses makes their on-screen
  timing the whole motion signal, so uneven presentation becomes visible rhythm error.
- Design: Exact rational arithmetic: pose k starts at game frame k x hold (hold 2 or 3) of a 60 Hz
  game; each pose is visible from the first display refresh at or after its start until the
  first refresh at or after the next pose starts. Displays 60, 120, 144, 165 and 50 Hz, 120
  poses each.
- Got right: Displays at a multiple of 60 Hz present every held pose for an identical time (60 and 120
  Hz, ratio 1.00 for twos and threes), which is what the limited-animation timing was authored
  against.
- Where/why it failed: Common PC refresh rates break the authored rhythm: twos at 144 Hz run 4,5,4,5 refreshes (25%
  longer every other pose), threes 7 and 8 (14%); a 50 Hz display drops to 1 or 2 refreshes on
  twos, so some poses last twice as long as their neighbours.
- Fix: For held-pose cel animation, offer a 120 Hz or 60 Hz presentation mode (or VRR locked to a
  multiple of 60) and test animation timing on 144 and 165 Hz screens; on 50 Hz output, prefer
  holds on threes or re-time for 50.
- Why this fix: Interpolated animation hides presentation jitter inside smooth motion, but held poses expose
  it because every pose change is a discrete event whose spacing is the timing the animator
  chose; only an integer refresh-per-game-frame ratio keeps that spacing.
- Rule of thumb: Held-pose animation needs refresh = n x 60 Hz: on twos 144 Hz alternates 4/5 refreshes
  (1.25x), 165 Hz 5/6, 50 Hz 1/2 (2x); 60 and 120 Hz stay even.
- Provenance (verified/assumed): Verified first-hand by the sandbox below; limited-animation practice from Motomura's GDC
  2015 slides; presentation modelled as latest-frame at refresh without frame pacing or VRR,
  which real drivers may change.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__held-poses-need-refresh-multiple-of-60.py
- Prediction: Written before running: 60 and 120 Hz ratio 1.00; 144 Hz on twos alternates 4/5 (1.25); 50
  Hz on twos 1 and 2+ refreshes (ratio >= 2).
- Observed: RESULT: PASS twos: 60Hz 1.00, 120Hz 1.00, 144Hz 1.25, 165Hz 1.20, 50Hz 2.00; threes: 144Hz
  1.14, 50Hz 1.50.
- Scenarios: 1) twos at 60/120/144/165/50 Hz; 2) threes at the same rates; 3) 50 Hz, built to break the
  even-presentation assumption hardest.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

## E8 — depth outlines no threshold spans distance
- Date: 2026-10-15
- Project: local/cel-shading
- Tags: [shaders][cel-shading][rendering][testing]
- What: Depth-based screen-space outlines have no threshold that works from 2 to 50 m: an absolute
  Roberts threshold (0.1 m) finds a 0.3 m step everywhere but draws false lines on bare floor
  from about 15 m; depth-normalised edges (grad z / z above 0.02, as in depth-normalising toon
  packages) keep the floor clean to 30 m but lose the 0.3 m step from 30 m.
- Why built: Cel-shading training with external research: the zzamjak ToonShading URP package runs
  Roberts cross over depth and normals and normalises depth edges by centre depth for constant
  line weight; GGXrd chose inverted hulls over post outlines; the trade-off of the depth
  threshold decides where post outlines fail.
- Design: Per-pixel ray cast: pinhole camera f 1000 px at 1.5 m eye height over a flat floor, a box
  face 0.3 m in front of a wall at distance z = 2 to 50 m. Roberts cross on the depth image
  across the box/wall boundary, and the floor's neighbour depth difference at the same
  distance. ABS threshold 0.1 m; NORM threshold 0.02 on grad z / z.
- Got right: Each rule works in its own band: ABS detected the 0.3 m step at every distance, and NORM
  kept the receding floor clean out to 30 m where ABS had already marked it from 15 m (floor
  depth difference grows as z squared over f h).
- Where/why it failed: No single depth rule spans the range: ABS adds false floor lines from 15 m, NORM loses real
  steps from 30 m and also hits the floor from 40 m. I predicted NORM would lose the step from
  15 to 20 m; it lasted to about 21 m because Roberts' diagonal magnitude carries a sqrt(2)
  factor (0.42 m for a 0.3 m step).
- Fix: Do not rely on depth alone for post-process cel outlines: combine depth with the normal-
  buffer edge (a floor has constant normals, a box/wall step does not), or scale the depth
  threshold by the expected slope (z squared over f h) rather than by z, and test both near
  and far.
- Why this fix: A tilted surface's depth gradient grows as z squared while a fixed geometric step stays
  constant in depth and shrinks as 1/z after normalisation, so absolute and z-normalised
  thresholds fail at opposite ends; normals separate the two cases directly.
- Rule of thumb: Depth-only post outlines cannot span 2-50 m: an absolute threshold marks receding floors
  from about 15 m, depth-normalised loses 0.3 m steps from about 21-30 m; add normal edges.
- Provenance (verified/assumed): Verified first-hand by the sandbox below; technique description from the zzamjak ToonShading
  package page on openupm; flat-floor scene and thresholds are mine, not the package's
  defaults.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__depth-outlines-no-threshold-spans-distance.py
- Prediction: Written before running: ABS detects the step at every distance but marks the floor beyond
  about 12 m; NORM keeps the floor clean to about 30 m but loses the step beyond 15 m; neither
  covers 2-50 m.
- Observed: RESULT: FAIL (NORM range) ABS finds the 0.3 m step at all distances: True, floor false edges
  from 15 m; NORM loses the step from 30 m (hit at 20), floor false edges from 40 m.
- Scenarios: 1) absolute depth threshold at 2 to 50 m; 2) depth-normalised threshold at the same
  distances; 3) bare receding floor, built to break each rule with false edges.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

## E7 — cel vertex ndotl identical only at zero threshold
- Date: 2026-10-15
- Project: local/cel-shading
- Tags: [shaders][cel-shading][rendering][numerics]
- What: Evaluating a cel step on N.L interpolated from the vertices gives exactly the same
  terminator as per-pixel renormalised normals when the threshold is 0, but drifts once the
  threshold moves: 1.8x the per-pixel error at threshold 0.3 and 5.1x at 0.6 on a 16-segment
  sphere (6.5 vs 1.3 px at 200 px radius).
- Why built: Cel-shading training: cheap toon shaders step on per-vertex lighting (a ramp coordinate from
  N.L per vertex) while GGXrd-style shaders step per pixel with a tunable threshold; I
  expected per-vertex to be much worse at every threshold.
- Design: Latitude/longitude sphere with n = 8, 16, 32 segments; for points on the true sphere, the
  containing cell's corners are bilinearly interpolated either as N.L values (vertex) or as
  normals then renormalised (per pixel). Light 60 degrees off axis. Error = max distance in px
  from wrongly shaded points to the true threshold line, at thresholds 0, 0.3, 0.6.
- Got right: At threshold 0 both methods are identical for every tessellation (6.23, 1.75, 0.38 px), and
  both errors shrink about 4x per doubling of n, as the tessellation error should.
- Where/why it failed: My first prediction (vertex 3x worse at threshold 0) was refuted: N.L is linear in the
  normal, so interpolating N.L equals dotting the interpolated normal, and renormalising
  multiplies by a positive factor that cannot change the sign. Away from 0 the shortened
  interpolated normal matters, but at 0.3 the gap was 1.8x, under my 2x second prediction; at
  0.6 it was 5.1x.
- Fix: A per-vertex cel step is safe only for a terminator at N.L = 0; if the artist moves the
  threshold (rim bands, wide lit areas, GGXrd-style offsets) evaluate the step per pixel on
  the renormalised normal, or tessellate densely where the moved band crosses.
- Why this fix: Interpolated normals are shorter than unit length between vertices, which shrinks |N.L|
  toward 0; a threshold at 0 is immune to scaling, any other threshold is crossed in the wrong
  place by an amount that grows with the threshold and the cell size.
- Rule of thumb: Vertex-interpolated N.L and per-pixel normals give the identical cel terminator at threshold
  0; a moved threshold drifts with vertex N.L (1.8x error at 0.3, 5.1x at 0.6 on 16 segments).
- Provenance (verified/assumed): Verified first-hand by the sandbox below; quad bilinear
  interpolation stands in for two triangles; which published shaders use per-vertex ramps is left
  open here, so the lesson names none.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__cel-vertex-ndotl-identical-only-at-zero-threshold.py
- Prediction: Iteration 1, written before running: at n 16 vertex N.L deviation >= 3x per-pixel. Iteration
  2, written before its run: threshold 0 identical at all n; at threshold 0.3 n 16 vertex >=
  2x per-pixel.
- Observed: RESULT: FAIL (iteration 2's 2x) threshold 0 identical at all n: True; threshold 0.3 n16
  vertex 3.55px vs per-pixel 1.98px (1.8x); threshold 0.6 n16 6.52 vs 1.28px (5.1x).
- Scenarios: 1) threshold 0 at n 8, 16, 32 (refuted the first claim); 2) threshold 0.3; 3) threshold 0.6,
  built to break the identity found in 1.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-15 · projects/pappydapimp69__zanegpt.md#E26 · compatible · sandboxes/2026-10-15__offset-copy-terminator-is-a-stylisation.py · observed RESULT: PASS plain copy 0.790 at 20 deg, 0.841 at 90, 0.977 at 160; scaled copy at least 0.926 from 45 to 135 but 0.790 at 20; half-ellipse 1.000 everywhere. · brain train cel (current half), session 2026-10-15; session_011p52L2CkFXcsYRwjDu6tG9

## E6 — inverted hull corner and distance failures
- Date: 2026-10-15
- Project: local/cel-shading
- Tags: [shaders][cel-shading][rendering][geometry]
- What: Inverted-hull outlines have three geometric failure modes measured exactly: split (hard-
  edge) normals open a gap of w x sqrt(2) at every right-angle corner, averaged normals thin
  the line to cos(half-turn) of w (0.71w at 90 degrees, 0.26w at 30), and the usual 1/cos fix
  makes sharp corners spike (3.86w at 30 degrees).
- Why built: Cel-shading training with external research: GGXrd used the inverted hull, expanded along
  normals with per-vertex width control (Motomura, GDC 2015), and toon-shader docs (Delt06 URP
  toon shader wiki) recommend clip-space scaling for perspective; the hull's corner and
  distance behaviour decides where artists must intervene.
- Design: Exact 2-D geometry: a square cross-section hulled by offset w with split normals, averaged
  normals, and averaged normals scaled by 1/cos(half-turn); then a corner-angle sweep
  (interior 150, 90, 60, 30 degrees); then on-screen width of a 0.02 world-unit offset at
  depth 2 to 20 with a 1000 px pinhole camera, in world space vs offset multiplied by depth.
- Got right: Clip-space scaling keeps the outline at a constant 4.0 px from depth 2 to 20 while world-
  space width falls from 10 px to 1 px, and the 1/cos correction restores full width on gentle
  and right-angle corners.
- Where/why it failed: No single normal choice works everywhere: split normals crack the hull open at hard edges;
  averaged normals thin the line exactly where the corner is sharpest; correcting by 1/cos
  pushes the corner vertex out 3.86w at 30 degrees, a visible spike. Results are exact
  geometry, so only the size of each effect is new, not its existence.
- Fix: Bake a separate smoothed normal set for the hull (keep hard normals for shading), scale the
  offset in clip space, clamp the 1/cos correction (about 2x) and taper width toward zero at
  very sharp corners with a per-vertex width channel, as GGXrd did with vertex colours.
- Why this fix: The hull only needs a continuous offset direction, which hard shading normals cannot give; a
  clamp bounds the spike while keeping most of the width, and per-vertex width gives artists
  the last word at the corners geometry cannot fix.
- Rule of thumb: Inverted hulls: hard normals crack corners (gap 1.41w), averaged normals thin them (0.71w at
  90, 0.26w at 30 degrees), 1/cos spikes them (3.9w at 30); use smoothed hull normals, clip-
  space width, a clamped fix.
- Provenance (verified/assumed): Verified first-hand by the sandbox below (exact geometry); technique sources Motomura GDC
  2015 slides and the Delt06 urp-toon-shader wiki (Outline page); the clamp value is my
  suggestion, untested.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__inverted-hull-corner-and-distance-failures.py
- Prediction: Written before running: split-normal gap w*sqrt2 per corner; averaged width 0.707w;
  corrected width w; world width falls 10x from z 2 to 20, clip-space within 1%; (added before
  run 2) corrected spike above 3.5w at a 30-degree corner.
- Observed: RESULT: PASS split normals gap 1.414w per corner; averaged width 0.707w, corrected 1.000w;
  world width 10.0px at z2 vs 1.0px at z20, clip-scaled 4.0px constant; 30-degree corner
  averaged 0.26w, corrected spike 3.86w.
- Scenarios: 1) square with split normals; 2) averaged normals; 3) 1/cos-corrected; 4) corner sweep to 30
  degrees, built to break the correction; 5) depth sweep world vs clip space.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-creative-training.md#E10 · compatible · sandboxes/2026-10-15__inverted-hull-outline-erased-first-under-centroid-painters-sort.py · observed RESULT: FAIL A (two disjoint spheres): centroid exact at all disjoint gaps=True; B (sphere over tilted backdrop, 25 positions): outline-only erased 0, body-only 0, both 5, clean 20; pooled wrong outline 9.3% vs body 2.3%; outline frac>=bod… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 1 pass 2

## E5 — gooch cool end nearly meets black outlines
- Date: 2026-10-15
- Project: local/cel-shading
- Tags: [shaders][cel-shading][rendering][accessibility]
- What: Gooch 1998 cool-to-warm shading with the paper's values (b 0.4, y 0.4, alpha 0.2, beta 0.6)
  is meant to keep shading in the middle luminance range so black edge lines stay visible; by
  WCAG contrast its darkest tone was only 1.29 to 1.45 against a black line, because the cool
  end is saturated blue and blue carries 7% of luminance.
- Why built: Cel-shading training with external research: the Gooch paper (read from the PDF) says its
  tone model stays in the middle luminance range so black edges and white highlights read; cel
  shaders borrow the cool shadow idea, so the claim is worth checking in perceived luminance,
  not RGB values.
- Design: Four object colours (red, green, blue, grey). For N.L from -1 to 1: Lambert, 2-band Lambert
  cel, smooth Gooch, and 2-band Gooch cel (tones at t 0.25 and 0.75). Contrast ratio (WCAG
  relative luminance) of the darkest tone against a black line and of the brightest against
  white.
- Got right: Gooch does lift the shadow side above Lambert, whose unlit side is black (1.03 against a
  black line, so the outline disappears there), and it pulls the brightest tone well below
  white (2.19 to 3.55), keeping room for highlights.
- Where/why it failed: The paper's mid-range claim fails in perceived luminance: the darkest smooth Gooch tone is
  pure-ish blue (b 0.4 plus 0.2 kd), contrast 1.29 to 1.45 against black, under my 2.0
  prediction. A 2-band Gooch cel that never uses the cool extreme (t 0.25) does better, 1.70
  to 2.12.
- Fix: When using cool shadows in cel or Gooch shading, check the shadow tone's luminance against
  the outline colour, not its RGB value: raise the cool end's lightness (add some kd or
  lighten kblue), or avoid the extreme cool end by placing the shade band at t 0.25 or above.
- Why this fix: Edge visibility depends on luminance contrast, and a cool hue shift lowers luminance much
  faster than its RGB values suggest because blue contributes only 0.0722 of it; lifting the
  cool end or keeping the band off the extreme restores contrast without losing the hue cue.
- Rule of thumb: Cool shadows cost luminance: Gooch's own blue end sat at 1.29 to 1.45 contrast against a
  black outline; check shadow tones against the line colour and keep the shade band off the
  cool extreme.
- Provenance (verified/assumed): Verified first-hand by the sandbox below; formula and parameters from Gooch, Gooch, Shirley
  and Cohen 1998 (PDF, users.cs.northwestern.edu); my reading takes the warm end as facing the
  light; WCAG luminance stands in for perceived lightness.
- Composed: ideas:ART/pixel-art/hue-shift-shading-scaled-to-sprite-size
- Sandbox: sandboxes/2026-10-15__gooch-cool-end-nearly-meets-black-outlines.py
- Prediction: Written before running: Lambert darkest vs black < 1.2 for every colour; Gooch darkest >=
  2.0 for every colour; Gooch brightest >= 1.3 below white for every colour.
- Observed: RESULT: FAIL Lambert darkest vs black line max 1.03; Gooch darkest vs black min 1.29 (1.29
  to 1.45); Gooch brightest vs white min 2.19; Gooch cel at t 0.25 1.70 to 2.12.
- Scenarios: 1) Lambert; 2) 2-band Lambert cel; 3) smooth Gooch with the paper's values, built to test
  its mid-range claim; 4) 2-band Gooch cel; each on red, green, blue and grey.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-15 · projects/pappydapimp69__zanegpt.md#E25 · compatible · sandboxes/2026-10-15__cool-cel-shadows-need-a-luminance-floor.py · observed RESULT: PASS lost in 5/6 (mean 18%); restored in 6/6; lit-to-shadow separation rose with the cool shift. · brain train cel (new half), session 2026-10-15; session_011p52L2CkFXcsYRwjDu6tG9
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-creative-training.md#E9 · compatible · sandboxes/2026-10-15__hue-shifted-deep-shadow-swallows-selective-black-outline.py · observed RESULT: PASS 32px deep-shadow step loses >=40% of shadow-side black-outline pairs on 4/5 bases for same-hue AND hue-shifted ramps (16px: 0%); hue shift drops darkest-tone contrast 9.2% mean on non-blue (blue drop 18.8%, red drop -2.6% i.e.… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 5 pass 1
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-creative-training.md#E33 · incompatible · sandboxes/2026-10-15__squint-test-keeps-only-the-value-step-of-hue-shifted-shading.py · observed RESULT: FAIL A/B squint flat 0.000, isolum max 0.0000 (raw RGB diff 0.46), value min 0.030, hueshift min 0.059 (>= value 5/5), gooch min 0.048; silhouette A/C min 0.005 vs best shading 0.167; black-fill silhouette 0.046; silhouette beats h… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 3 pass 2

## E4 — cel step noise blotches on flat closeups
- Date: 2026-10-15
- Project: local/cel-shading
- Tags: [shaders][cel-shading][rendering][testing]
- What: A cel shader's step on N.L turns normal noise that changes Lambert brightness by only 1.5%
  into flipped shading on 1.13% of a close-up of a gently curved cheek and 6 detached shadow
  islands, against 0.15% and no islands on the whole head.
- Why built: Cel-shading training with external research. Motomura's GGXrd GDC 2015 slides say every
  little noise in the normals becomes a huge blotch under cel shading and that the team hand-
  edited normals on every major feature; this measures how big and where.
- Design: 128x128 view of a sphere of radius 56 px (whole head) or 400 px (close-up, centred on the
  terminator). Normal = analytic plus a deterministic sum-of-sines tilt of amplitude eps. Step
  threshold 0 on N.L, light from the upper left. Counted flipped pixels against the clean
  normals, 8-connected detached shadow islands inside the disc, and the max Lambert change.
- Got right: Clean (proxy) normals gave no islands and no flips in either view, which is why transferring
  normals from a smooth proxy shape removes blotches; on the whole head the same noise only
  wiggled the terminator (0.15% flipped, no islands).
- Where/why it failed: Iterations 1 to 3 measured islands on the whole head and found none once pixel artefacts at
  the crescent tips were excluded; the damage only showed on the flat close-up, where N.L
  changes slowly across pixels, so a small normal error moves the terminator far: 7.8x the
  flipped area and 6 islands at eps 0.01, 13 at 0.02.
- Fix: Clean normals hardest where the surface is flattest relative to the view (cheeks, foreheads,
  close-ups), by transferring them from a smooth proxy or editing them by hand, and judge
  noise under the step shader at close-up framing, not under smooth lighting.
- Why this fix: The terminator moves by roughly the normal error divided by how fast N.L changes per pixel,
  so the same eps costs little on tight curvature and a lot on gentle curvature or when zoomed
  in; smooth Lambert hides it because it changes brightness by only eps.
- Rule of thumb: Under a cel step, normal noise moves the terminator by error over the N.L gradient: 1.5%
  Lambert noise flipped 7.8x more area and made 6 islands on a flat close-up; clean normals
  there.
- Provenance (verified/assumed): Verified first-hand by the sandbox below; source claim from Motomura's GGXrd GDC 2015 slides
  (ggxrd.com PDF, read as text); the noise pattern and radii are my model, not GGXrd assets.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__cel-step-noise-blotches-on-flat-closeups.py
- Prediction: Written before the final run: with under 3% Lambert change, flipped area on the close-up is
  at least 5x the whole-head share, the close-up shows detached islands, proxy normals show
  none.
- Observed: RESULT: PASS eps 0.01 (Lambert change 0.015): close-up flipped 1.13% vs whole head 0.15%
  (7.8x); close-up islands 6 (13 at eps 0.02); proxy normals 0/0.
- Scenarios: 1) whole head, eps 0, 0.01, 0.02; 2) close-up R 400, same eps; 3) clean proxy normals in
  both, built to break the claim that blotches come from the normals rather than the shape.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

## E3 — cel key light belongs to the character
- Date: 2026-10-15
- Project: local/cel-shading
- Tags: [shaders][cel-shading][rendering][gamedev]
- What: Under cel shading a scene point light changed up to 44.8% of a character's authored
  lit/shade pattern as it walked across the stage, and a scene sun that matched the authored
  look changed 41.0% the moment the fighter switched sides; a light defined in the character's
  own frame changed nothing.
- Why built: Cel-shading training with external research: GGXrd gave every character a dedicated light
  vector that lights its idle pose best, with no global lighting on characters (Motomura, GDC
  2015). The test sizes what a scene light would do to an authored cel design in a fighting
  game.
- Design: Front hemisphere of a head-sized sphere (600 normals), authored look = step shading under an
  upper-front-left light in the character's frame. Walk 0 to 1200 px, then mirror on x for the
  side switch. Lights: scene point light at (600, 900, 400) px; scene sun equal to the
  authored light at the start; per-character light that mirrors with the body.
- Got right: The scene sun is harmless while walking (0% change, translation does not alter directions)
  and the per-character light keeps the design through both walking and side switches, which
  is the property GGXrd needed for 2D-looking characters.
- Where/why it failed: The per-character result is 0% by construction (the light moves with the body), so the
  informative numbers are the scene lights: the point light's direction swings with stage
  position (44.8% worst), and mirroring puts the sun's lit side on the other half of the face
  (41.0%), so an authored cel design cannot survive either.
- Fix: For cel-shaded characters define the key light in the character's local frame and mirror it
  with the body; keep scene lights for environment and effects, or blend them in only as
  colour, never into the step decision.
- Why this fix: A step shader turns any change of light direction relative to the body into a hard pattern
  change, and fighting games mirror characters constantly; a body-relative light makes the
  pattern a property of the character art, which is what the artist authored.
- Rule of thumb: In cel shading keep the key light in the character's frame: a scene point light altered
  44.8% of the authored pattern on a walk and a matched scene sun 41.0% on a side switch.
- Provenance (verified/assumed): Verified first-hand by the sandbox below; GGXrd practice from Motomura's GDC 2015 slides;
  sphere stand-in for a head and my light placements, not GGXrd data.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__cel-key-light-belongs-to-the-character.py
- Prediction: Written before running: point light differs >= 15% somewhere on the walk; sun 0% on the walk
  and >= 15% after the side switch; per-character light 0% throughout.
- Observed: RESULT: PASS point light walk 44.8%, sun walk 0.0% / side switch 41.0%, per-character light
  0.0% / 0.0%.
- Scenarios: 1) walk under a scene point light; 2) walk under a matched scene sun; 3) side switch under
  the sun, built to break the idea that a matched global light is enough; 4) per-character
  light through both.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

## E2 — cel inner lines as axis aligned uv beams
- Date: 2026-10-15
- Project: local/cel-shading
- Tags: [shaders][cel-shading][rendering][texturing]
- What: GGXrd's inner-line trick (axis-aligned beams in the texture, UVs rotated to follow them)
  kept a 30-degree cel line edge within the half-pixel scan limit at 24x magnification,
  against 2.8 px for an anti-aliased diagonal painted in the texture and 10.6 px for a hard-
  painted one; the line width follows the UV scale across the beam exactly.
- Why built: Cel-shading training with external research: Motomura's GDC 2015 slides describe drawing all
  inner lines as axis-aligned beams with the UV lined up alongside so close-ups never show
  jaggies, and controlling thickness by UV overlap.
- Design: 32x32 texture, line 2 texels wide at 30 degrees on the surface, rendered at 24 screen px per
  texel with bilinear sampling then threshold 0.5. A: diagonal painted with 4x4 coverage anti-
  aliasing; A2: diagonal hard-painted; B: horizontal beam on texel rows with UVs rotated 30
  degrees. Edge error = max distance of edge pixels from the ideal edges; width of B measured
  across the beam for UV scales 0.5, 1, 2.
- Got right: The beam's edge is exactly straight after any UV rotation (0.50 px, the scan's own half-
  pixel quantisation), because a bilinear field that is constant along u has no texel steps
  along the line; width doubled and halved exactly with the UV scale (4.0, 2.0, 1.0 texels).
- Where/why it failed: I predicted the anti-aliased diagonal at 0.25 texel or worse; it was 0.12 texel (2.8 px), so
  careful coverage painting removes half the staircase, though it still grows with
  magnification. Hard painting is far worse (0.44 texel, 10.6 px).
- Fix: For cel inner lines that must hold up in close-ups, paint lines as axis-aligned beams and
  route the UVs along them; control thickness by how much the UV strip spans the beam, and
  accept the distorted UVs since the texture carries no other detail.
- Why this fix: The staircase comes from a diagonal crossing texel rows; aligning the line with texel rows
  moves all variation to the across-line axis, where bilinear interpolation is exact, so
  magnification only scales a straight edge.
- Rule of thumb: Paint cel inner lines as axis-aligned beams and rotate UVs onto them: straight to half a
  pixel at 24x, vs 2.8 px anti-aliased diagonal and 10.6 px hard diagonal.
- Provenance (verified/assumed): Verified first-hand by the sandbox below; technique from Motomura's GDC 2015 slides; one
  angle (30 degrees), one magnification, bilinear only (no mipmaps or anisotropic filtering).
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__cel-inner-lines-as-axis-aligned-uv-beams.py
- Prediction: Written before running: A's edge error >= 0.25 texel (6 px), B's < 0.5 px; B's width grows
  linearly with UV overlap.
- Observed: RESULT: FAIL (A's size) diagonal edge error 2.8px (0.12 texel) vs beam 0.50px at 24x; hard-
  painted diagonal 10.58px (0.44 texel); beam width 4.0/2.0/1.0 texels for UV scale 0.5/1/2.
- Scenarios: 1) anti-aliased diagonal in the texture; 2) hard-painted diagonal; 3) axis-aligned beam with
  rotated UVs; 4) beam width vs UV scale; scenario 1 was built to break the claim by painting
  the diagonal as well as possible.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Audited: 2026-10-15 · pass · Read the entry and its stored sandbox sandboxes/2026-10-15__cel-inner-lines-as-axis-aligned-uv-beams.py and reran it (same RESULT: FAIL on the predicted size of A only: anti-aliased diagonal 2.80 px / 0.12 texel, hard diagonal 10.58 px / 0.44 texel, beam 0.50 px, widths 4.0/2.0/1.0 for UV scale 0.5/1/2). The model does not assume its answer: both textures go through the same hand bilinear sampler, the same 0.5 threshold and the same edge scan, and the beam's straightness falls out of the sampled field being constant along u, which is the mechanism the rule names. An ad-hoc probe that reuses the stored code at angles 10, 30, 45 and 60 degrees and magnifications 8 and 24 found the beam edge exact at every angle; its measured error is only the row scan's floor of sin(angle) x 1 px (0.17 px at 10, 0.50 at 30, 0.67 at 45, 0.87 at 60 degrees), so "half a pixel" is specific to the 30-degree test and is a measurement floor, not a property of the beam. The diagonal's disadvantage holds across angles (anti-aliased 0.06 to 0.20 texel, hard 0.15 to 0.49 texel) and its pixel error does grow with magnification (10 degrees: 0.97 px at 8x, 2.91 px at 24x), which the entry asserted without measuring. Scope notes: the 10.6 px hard-diagonal figure is angle-dependent (only 3.58 px at 45 degrees); the width test varies UV scale only, the unused offset parameter means partial overlap of the strip is not exercised; mipmaps and anisotropic filtering are out of scope, as the entry's own Provenance says. The claim is about the bilinear filter's maths, which the hand sampler implements exactly at mip 0, so pass rather than modeled. · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 5 pass 3

## E1 — cel closeup edges need continuous fields
- Date: 2026-10-15
- Project: local/cel-shading
- Tags: [shaders][cel-shading][rendering][testing]
- What: GGXrd stored cel shade-threshold offsets in vertex colours because textures are resolution
  dependent; at equal sample budget a bilinear texture holding a continuous signed distance
  stayed as sharp at 32x zoom as the vertex version (1.8 vs 2.0 px off the intended edge),
  while painted on/off masks drifted 16 to 21 px.
- Why built: Cel-shading training with external research: Motomura's GDC 2015 slides justify vertex
  properties over textures by close-up resolution; the claim mixes two variables, where the
  data lives (vertex or texture) and what it encodes (a continuous value or a painted mask).
- Design: 17x17 samples over a patch storing an intended circular shade zone four ways: vertex grid
  with signed distance interpolated on triangles; texture with signed distance, bilinear;
  texture with a binary mask, nearest; binary mask, bilinear then threshold 0.5. Measured the
  max distance from classified boundary pixels to the true circle at zoom 2, 8 and 32 screen
  px per sample.
- Got right: Storing a continuous field and thresholding after interpolation is close-up proof: both the
  vertex and the bilinear texture version stayed within about 2 px of the true edge at every
  zoom (A and B within 25% of each other), confirming the mechanism GGXrd relied on.
- Where/why it failed: Texture storage was not the problem: the error came from painted binary masks, whose edge
  error scales with zoom (nearest about 0.67 of a sample spacing, 21 px at 32x; bilinear-
  thresholded 0.49 of a spacing, 16 px). I predicted the bilinear mask at 0.15 to 0.45 of a
  spacing; it was 0.49 to 0.96.
- Fix: Store cel shade zones, occlusion offsets and line masks as continuous fields (signed
  distance or a smooth offset) and threshold after interpolation; that works in vertex colours
  or in bilinear textures. Avoid painted 0/1 masks for anything seen up close.
- Why this fix: Interpolating a continuous field and then stepping places the edge with sub-sample precision
  at any zoom, while a binary mask only knows which sample is in or out, so its edge error is
  a fixed fraction of a sample spacing and grows with magnification.
- Rule of thumb: For close-up cel edges, store a continuous field and threshold after interpolation (vertex
  or bilinear texture both held about 2 px at 32x); painted 0/1 masks drifted 16 to 21 px.
- Provenance (verified/assumed): Verified first-hand by the sandbox below; GGXrd's reasoning from Motomura's GDC 2015 slides
  (read as text); one shape (circle) at one budget; GPU filtering details (mip levels,
  anisotropy) not modelled.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__cel-closeup-edges-need-continuous-fields.py
- Prediction: Written before running: vertex and texture signed distance within 25% at every zoom; mask
  nearest about 0.7 Z px; mask bilinear about 0.3 Z px.
- Observed: RESULT: FAIL (mask bilinear part) zoom 32: vertex SDF 1.99px, texture SDF 1.80px, mask
  nearest 21.3px, mask bilinear 15.7px; A~B True; per spacing C 0.72/0.68/0.67, D
  0.96/0.58/0.49.
- Scenarios: 1) vertex signed distance; 2) texture signed distance bilinear, built to break the vertex-
  only claim; 3) mask nearest; 4) mask bilinear threshold; each at zoom 2, 8, 32.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Audited: 2026-10-15 · modeled · Read E1 and its stored sandbox sandboxes/2026-10-15__cel-closeup-edges-need-continuous-fields.py and reran it unchanged (same RESULT: FAIL, zoom 32 vertex SDF 1.99 px, texture SDF 1.80 px, mask nearest 21.3 px, mask bilinear 15.7 px). The sandbox does test the claim rather than assume it: all four storage schemes are classified independently and scored against the analytic circle, and its own failed prediction (mask bilinear 0.49 to 0.96 of a spacing, not 0.15 to 0.45) is reported honestly. Two scope limits matter for the Rule of thumb. First, the continuous-field error is not zoom-independent, it grows more slowly: a probe that only adds zoom 128 (scan step widened to keep it tractable) gave vertex SDF 6.26 px, texture SDF 4.20 px, mask nearest 84.6 px, mask bilinear 59.9 px, so "about 2 px" is a zoom-32 figure, not a close-up guarantee. Second, the 8x gap depends on the smooth circle: swapping only the shape to an axis-aligned square (Chebyshev distance, half-width 0.27) gave at zoom 32 vertex SDF 5.24 px, texture SDF 4.24 px, mask nearest 6.76 px, mask bilinear 5.76 px, so continuous fields barely beat masks where the edge has corners. The claim itself is about GPU vertex interpolation and texture filtering in a shipped game (GGXrd), and only a hand-written Python model of those interpolators on one circle at one 17x17 budget was tested, so the verdict is modeled: sound mechanism, numbers valid for smooth curved edges at zoom up to 32. · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 4 pass 3
