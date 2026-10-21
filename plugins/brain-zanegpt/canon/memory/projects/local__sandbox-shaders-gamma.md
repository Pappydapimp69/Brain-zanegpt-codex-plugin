# local/sandbox-shaders-gamma — lessons

Project: local/sandbox-shaders-gamma. Newest first.

---

## E1 — srgb space alpha blend is too dark
- Date: 2026-07-20
- Project: local/sandbox-shaders-gamma
- Tags: [rendering][algorithm]
- What: Alpha-blending two colors by linearly interpolating their gamma-
  encoded (sRGB) byte/float values directly — the extremely common
  shortcut (`result = c1*(1-a) + c2*a` applied to raw 0-255 or 0-1
  sRGB channel values) — produces a visibly too-dark midpoint compared
  to the physically correct result: converting both colors to LINEAR
  light, blending there, then converting back to sRGB.
- Why built: `brain train new-domain`, seeding SHADERS as a genuine gap
  (`brain query` returned only adjacent-but-distinct ART/accessibility
  dithering entries, nothing on gamma-correct blending specifically).
  This is a standard, well-documented graphics fact (the sRGB transfer
  function, IEC 61966-2-1 / the W3C sRGB color space spec).
- Design: `sandbox.py` — exact deterministic sRGB<->linear conversion
  formulas (the standard piecewise sRGB transfer function, zero RNG).
  Blended pure white (1,1,1) and pure black (0,0,0) at alpha=0.5 two
  ways: `naive_srgb_blend` (lerp the sRGB values directly) and
  `correct_linear_blend` (convert both to linear, lerp, convert the
  result back to sRGB). Compared each result's relative luminance
  (computed correctly, in linear space, via Rec. 709 coefficients)
  against the TRUE physical halfway-light luminance (0.5, exactly
  halfway between black at luminance 0 and white at luminance 1 in
  real light).
- Got right: used the SAME correct luminance-computation function (itself
  converting to linear first) to judge BOTH blend methods' results, so
  the comparison isn't circular — the naive blend's own sRGB output is
  independently re-measured for its true physical brightness.
- Where/why it failed: the naive sRGB-space blend of white+black at
  alpha=0.5 yields an sRGB value of exactly 0.5 (looks like a plausible
  "middle gray" by the numbers) but its TRUE linear luminance is only
  0.214 — a 0.286 absolute error versus the true 0.5 halfway point,
  because sRGB encoding is a nonlinear (gamma ~2.2) curve, and
  interpolating along that curve does not interpolate the underlying
  light linearly. The linear-space blend's luminance came out at
  exactly 0.500, a 0.0000 error against the true value.
- Fix: for any alpha blend where the result should represent physically
  mixed light (fog, translucency, additive VFX, lighting accumulation),
  convert both source colors from sRGB to linear light, blend there,
  then convert the result back to sRGB for display/storage — never
  interpolate gamma-encoded values directly.
- Why this fix: sRGB encoding exists to allocate more numeric precision
  to darker tones (matching human perceptual sensitivity), not to
  represent light linearly — any arithmetic meant to model how light
  actually combines (blending, averaging, mip-mapping/downsampling)
  must operate on the LINEAR representation, and re-encode only at the
  final display step.
- Rule of thumb: before blending, averaging, or otherwise arithmetically
  combining color values meant to represent physical light mixing, ask
  whether those values are gamma-encoded (sRGB, the default for
  textures/canvas/most color pickers) — if so, convert to linear space
  first. The error is not subtle: a 50% blend that should be exactly
  halfway in brightness comes out looking notably darker than expected
  when done naively, and the same class of error affects mip-mapping,
  texture filtering, and any other operation that averages sRGB texel
  values directly.
- Provenance (verified/assumed): Verified first-hand — ran `sandbox.py`
  (exact deterministic sRGB<->linear formulas, zero RNG), confirmed the
  naive blend's true luminance (0.214) vs. the correct blend's (0.500,
  exact match to the true halfway point). Re-ran as two independent
  process invocations; output byte-identical both times. Externally
  grounded in the standard sRGB transfer function (IEC 61966-2-1).
- Composed: N/A
- Link: session 7195397b-63a9-5efe-a80b-2792eaa6645e (`brain train
  new-domain`, shaders/gamma gap); sandbox
  `scratchpad/loop7/shaders/sandbox.py`, run twice as independent
  process invocations, outputs diffed identical
- Cited-by: 2026-10-10 · projects/local__sandbox-shaders-pipeline.md#E1 · compatible · sandboxes/2026-10-10__srgb-blend-normal-pipeline.py · observed RESULT: PASS; luminance 0.214 vs 0.5; error 0.00012 at 0.02 and 0.286 at 1.0; dot 0.0 vs -3.638; uniform scale diff 0.0. · scheduled brain train auto loop 1 pass 1; session_01PQ4jLSc8kGvXwYbpjoS24m
- Cited-by: 2026-10-11 · projects/pappydapimp69__brain.md#E133 · compatible · sandboxes/2026-10-11__orm-packed-texture-linear-not-srgb.py · observed RESULT: PASS linear err 0.0020; sRGB misflag err 0.284 (endpoints immune); swap wrong 5/6; bilinear 0.50 vs 0.32. (First run FAILed only because my check expected 4 swapped materials; the miscount was mine, the sandbox logic was unchanged.) · brain train auto loop 1 pass 1 (kernel); session_01ScEdAr4bK7Pp21fx27MXao
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-creative-training.md#E19 · compatible · sandboxes/2026-10-15__srgb-penumbra-shifts-shadow-edge-only-in-low-key.py · observed RESULT: PASS 1:1 err 0.0000; 2:1 err 0.020 shift +0.050 W; 8:1 err 0.098 (12% of lit) half-light shift +0.133 W L*-mid shift +0.139 W dark share 0.34->0.48; 16:1 shift +0.161 W; endpoints exact. The shift-above-0.15 W part of the predictio… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 2 pass 2
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-creative-training.md#E37 · compatible · sandboxes/2026-10-15__thin-rim-light-loses-its-ratio-in-srgb-downscale-but-not-to-exposure.py · observed RESULT: PASS 1-px rim F=4 r=16 bg .02: linear 4.75 sRGB 2.83 (keeps 49% of excess); exposure +-2 st unclipped spread r=8 0.0%; k=F diff 0; clip +2 st linear 4.75->3.88; high-key r1.5 keeps 91%; sRGB needs r=15.1 to match linear r=8; toe de… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 4 pass 1
