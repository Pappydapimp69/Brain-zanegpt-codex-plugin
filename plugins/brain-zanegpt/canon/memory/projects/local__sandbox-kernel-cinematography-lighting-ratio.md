# local/sandbox-kernel-cinematography-lighting-ratio — lessons

Project: local/sandbox-kernel-cinematography-lighting-ratio. Newest first.

---

## E1 — lighting ratio stops vs lux and bounce floor
- Date: 2026-10-10
- Project: local/sandbox-kernel-cinematography-lighting-ratio
- Tags: [cinematography][lighting][simulation][testing]
- What: A two-light Lambertian face model (key, fill, ambient floor, exposure gain, clip, tone curve, 8-bit
  quantise, display L*) was used to test two kernels: key-to-fill ratio defines high-key vs low-key, and ratio
  (not brightness) controls contrast in three-point lighting. The ratio does set contrast, but only after
  exposure is normalised to the lit side, only if the label is read in the same unit the author meant, only
  for a fixed key angle, and only while ambient light scales with the key.
- Why built: The train pass flagged both kernels as untested by any memory entry. They also disagree on
  numbers (near 1:1 high-key and 8:1 noir in one, 1.5:1 flat and 2:1 dramatic in the other) and never say
  whether 8:1 is lux, stops, key:fill or (key+fill):fill.
- Design: Stdlib script. Cast-shadow site (lit side K+F+A, key-occluded side F+A) gives the textbook total
  ratio; two cheek sites on a sphere with Lambert cosines give a geometric ratio; exposure either pins the lit
  patch to 0.4 scene-linear or is frozen; tone curves sRGB, power 2.2 and an S curve; contrast metric is
  delta L* of the displayed 8-bit codes. Scenarios built to break the claim: frozen exposure, four readings of
  one label, key-azimuth sweep at constant nominal ratio, fixed vs key-proportional ambient.
- Got right: With the lit patch pinned, delta L* is brightness-independent (0.000 spread over a 6-stop sweep)
  and strictly monotonic in ratio. The kernels' arithmetic holds (2 stops = 4:1, 3 stops = 8:1). Reading 8:1 as
  key:fill (total 9:1, 44.7 L*) or as total (8:1, 43.0 L*) differs by only 1.8 L*. Zero fill is still capped
  by the floor: (K+A)/A. Summing in linear light then encoding was the right order (see the P9 gap below).
- Where/why it failed: (1) Frozen exposure at a constant 8:1: +-1 stop moves delta L* by up to 11.2, +-3 stops
  by 23.2 (44.7 -> 21.6 dark, 33.8 bright, 12.6 at +4 as the lit side clips), so brightness does control
  contrast once the display is not re-exposed. (2) Reading 8 stops as 256:1 gives 68.2 L* with the shadow at
  code 5 (crushed), 23.5 L* from the lux reading; reading 3 stops as 3:1 gives 31.8 L*, 13.0 L* away.
  (3) Geometry: nominal 8:1 key:fill on a 45/45 rig gives a cheek ratio of 3.39:1 (1.76 stops); key azimuth
  alone spreads the cheek ratio 1.42 to 7.54 at the same nominal 8:1 (5.3x). (4) Ambient: A = K/8 turns a
  9:1 total into 5:1 (-0.85 stop), A = K/4 into 3.67:1 (-1.30 stops); with ambient fixed in lux and fill tied
  to the key, the total ratio runs 1.89 to 8.11 over +-3 stops of key brightness (4.3x), while key-proportional
  bounce holds 5.00 flat. (5) Curves keep the ordering but reshape it: the S-curve toe gives 11.1 L* at 2:1
  against 17.6 for sRGB (6.5 spread) and the shoulder gives 58.5 against 51.6 at 16:1 (7.2 spread). My
  guess that the curves would differ by more than 5 L* at 8:1 missed (0.4 spread, coincidence of the
  crossover). (6) Fading the key to half by averaging encoded codes reads 3.83:1 against 5.00:1 in linear
  light, 0.39 stop low. Also, 1.5:1 to 2:1 adds only 6.6 L* while 2:1 to 8:1 adds 25.4 and 8:1 to 16:1 adds
  8.6, so the 'flat vs dramatic' boundary between the two kernels is far below the noir threshold.
- Fix: State every lighting ratio with its unit and its sites: 'K:F in lux at the subject', or 'total lit
  side : shadow side in stops', and say whether ambient is included. Measure the shadow side with all
  lights on except the key (that includes the bounce), keep exposure normalised to the lit side when
  comparing looks, and treat key angle and ambient type (key-proportional bounce vs fixed practical or
  window) as part of the spec.
- Why this fix: Contrast on screen is the log gap between lit and shadow sites after exposure and the
  tone curve. A label that omits unit, sites, angle or ambient fixes only one of those four terms. The
  measured gaps (23 L* for stops-vs-lux, 0.85 stop for a modest bounce, 5.3x for angle) are larger than the
  difference between the kernels' 'dramatic' and 'flat' bands.
- Rule of thumb: Write a lighting ratio as 'unit + sites + ambient + angle' (for example '3 stops total, key
  45 degrees, bounce included'), because 8:1 read as stops is 256:1 (crushed, 68 L*) and a bounce at one
  eighth of the key already cuts a 3-stop setup to 2.3 stops; compare looks only at matched exposure.
- Provenance (verified/assumed): Verified first-hand: every number above came from the saved script, which
  ran deterministically and printed RESULT: PASS 19/19 with 1 logged prediction miss. The model is Lambert on
  a sphere with a sandbox-chosen tone pipeline, so values transfer as structure and sensitivities. Real skin,
  specular and subsurface terms, falloff distance, and human viewing judgments are outside the model and
  stay open; the kernels' source figures (1.5:1, 2:1, 8:1) were taken as given.
- Composed: ideas:CINEMATOGRAPHY/lighting/key-to-fill-ratio-defines-high-key-vs-low-key, ideas:CINEMATOGRAPHY/lighting/three-point-lighting-key-fill-back-have-distinct-jobs, ideas:SHADERS/color-blending/convert-to-linear-before-blending-physical-light, seven/E15, sandbox-shaders-pipeline/E1
- Polarity: compatible
- Sandbox: sandboxes/2026-10-10__lighting-ratio-stops-vs-lux-and-bounce-floor.py
- Prediction: Normalised exposure makes delta L* depend on ratio only (spread under 1.5 L* over 6 stops); at
  frozen exposure and 8:1, +-1 stop moves it under 12 L* and +-3 stops over 20; '8 stops' reads over 20 L*
  from the lux reading with shadow code under 8, while key:fill vs total readings differ under 3 L*; 8:1
  key:fill on a 45/45 rig gives cheek ratio 3.0 to 3.8 and key azimuth alone spreads it over 3x; A = K/8 cuts
  the 9:1 total to 5:1 and A = K/4 to 3.67:1; fixed ambient moves total ratio over 3x across +-3 stops while
  bounce keeps it flat; tone curves differ by over 5 L* at 8:1; encoded-space fade reads about 0.36 stop low.
- Observed: RESULT: PASS 19/19 checks held, 1 prediction miss (P7b). Spread 0.000 L*; frozen exposure
  shifts 11.2 (+-1 st) and 23.2 (+-3 st); 8 stops 68.2 L* with code 5, 23.5 L* from lux reading; key:fill vs
  total 1.8 L*; cheek 3.39:1, azimuth range 1.42 to 7.54 (5.3x); ambient 9:1 -> 5.00:1 and 3.67:1; fixed
  ambient 1.89 to 8.11 (4.3x), bounce 1.0000x; curves differ 0.4 L* at 8:1 (miss) but 6.5 at 2:1 and 7.2 at
  16:1; encoded fade 3.83:1 vs 5.00:1 (0.39 st).
- Scenarios: 1) normalised exposure brightness sweep and ratio ladder; 2) frozen exposure at constant 8:1
  (built to BREAK the ratio-only claim); 3) four readings of one 8:1 label (lux key:fill, total, 8 stops, 3
  as ratio); 4) key azimuth sweep at constant nominal ratio (BREAK); 5) ambient A = 0, K/8, K/4 and F = 0 cap;
  6) fixed vs key-proportional ambient over +-3 stops (BREAK); 7) three tone curves; 8) lit-patch vs
  face-mean exposure metering; 9) encoded-space vs linear mixing.
- Link: session_01YFLLRpDsfZpRstb2KT2MQy

