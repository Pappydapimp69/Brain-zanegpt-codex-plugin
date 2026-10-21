# local/pixel-outline-must-follow-background-value — lessons

Project: local/pixel-outline-must-follow-background-value. Newest first.

---

## E1 — pixel outline must follow background value
- Date: 2026-10-15
- Project: local/pixel-outline-must-follow-background-value
- Tags: [pixel-art][art][rendering][testing]
- What: Tested selective outlining, uniform black outlining and no outline on one 16x16
  hue-shift-shaded sprite against night, grass and sky backgrounds, with a computed
  contrast-ratio separation score and a 4x box-shrink squint test. No outline style wins
  everywhere; the right one depends on the background's value.
- Why built: Pixel-art training request. Three kernels (selective outline, silhouette squint
  test, hue-shift shading at 16x16) give rules with no stated background, and canon had no
  lesson applying any of them.
- Design: ASCII 16x16 character mask, 3-step hue-shifted ramp (cool shadow, red base, warm
  highlight) lit from the top left. Outline ring: none, black, or selective (warm tint on
  the lit side, near-black on the shadow side). Separation = share of boundary pixels with
  contrast ratio 1.5 or more against the background; squint = IoU after a 4x box shrink.
- Got right: Selective and black outlines fully separated the sprite on the light sky
  background (100% vs 26% with no outline, where the warm highlights melt into the sky),
  so outlining earns its place where body and background are close in value.
- Where/why it failed: On night, black separated 0% and selective 50% while no outline
  scored 100%: a dark outline against a dark background hides the edge. On grass the
  selective lit-side tint separated only 50% (similar value to grass). Squint failed on
  grass for every outline (IoU 0.00 to 0.17): the body's value matched the background.
- Fix: Pick the outline per background value: no or light outline on dark scenes, dark
  outline on light ones, and check the lit-side tint against mid-value backgrounds. When
  the squint test fails across all outlines, change the body's overall value, not the outline.
- Why this fix: Separation and squint both run on luminance contrast, which an outline can
  only add where it differs in value from the background; hue shift alone does not survive
  a squint.
- Rule of thumb: An outline only separates a sprite where it differs in value from the
  background: black failed on night (0%), a light lit-side tint failed on grass (50%); squint
  on every background you ship.
- Provenance (verified/assumed): verified first-hand by the sandbox below; one sprite, one
  ramp, three flat backgrounds; the 1.5 ratio and 0.08 squint thresholds are my choices.
- Composed: ideas:ART/pixel-art/selective-outlining-not-uniform-black, ideas:ART/pixel-art/silhouette-first-plus-squint-test, ideas:ART/pixel-art/hue-shift-shading-scaled-to-sprite-size
- Sandbox: sandboxes/2026-10-15__pixel-outline-must-follow-background-value.py
- Prediction: Written before running: on grass and sky selective >= black > none for
  separation; on night both dark outlines separate under 50%.
- Observed: RESULT: FAIL night none 100% / black 0% / selective 50%; grass none 100% /
  black 100% / selective 50%; sky none 26% / black 100% / selective 100%; squint on grass
  0.00 to 0.17 for all.
- Scenarios: 1) dark night background, built to break dark-against-background outlining;
  2) mid-value grass; 3) light sky; each with none, black and selective outlines.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Audited: 2026-10-15 · fail · Read the entry and its stored sandbox sandboxes/2026-10-15__pixel-outline-must-follow-background-value.py and reran it (same RESULT: FAIL, night none 100% / black 0% / selective 50%, grass none 100% / black 100% / selective 50%, sky none 26% / black 100% / selective 100%). The headline numbers are computed, but for any outlined sprite the separation metric compares ONLY the outline pixel against the background, so "an outline only separates where it differs in value from the background" is true by definition of the score rather than tested; the body-to-outline contrast, which is the edge a viewer actually reads, is never measured. The sandbox's own squint test contradicts the night verdict: squint IoU on night is 0.75 for both no outline and black outline, i.e. the silhouette survives the black outline unchanged. An ad-hoc probe that reuses the stored render and counts a ring pixel as separating when outline-vs-background, body-vs-outline or body-vs-background reaches the same 1.5 ratio gives night 100/100/100%, grass 100/100/100% and sky 33/100/100% (none/black/selective): the "black failed on night (0%)" and "selective 50% on grass" failures disappear, and only the sky no-outline weakness remains. Rule claims about readability therefore rest on a metric that assumes its answer; the sky result (outline helps where body and background are close in value) is the only part the model supports. Not a real-system claim, so not modeled. · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 1 pass 3
