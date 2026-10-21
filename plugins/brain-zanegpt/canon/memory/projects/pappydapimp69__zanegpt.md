# Pappydapimp69/Zanegpt — lessons

Project: Pappydapimp69/Zanegpt. Newest first.

---

## E31 — segment map stretches a hard coded film
- Date: 2026-10-17
- Project: Pappydapimp69/Zanegpt
- Tags: [film][animation][audio][timing]
- What: Lengthening a 2:56 render(t) film to 4:03 and inserting three fireside cutaways, where the
  tale half of the film is timeline-hard-coded: about forty actor tracks, shot boundaries and
  node birth times all in tale seconds.
- Why built: The owner asked for a four-minute cut with room for the narrator to explain; the
  previous cut had just been retimed twice by hand and a third pass over every literal was the
  obvious way to break sync.
- Design: Two clocks. The tale keeps its own clock ts and is untouched. A segment map
  [[filmA, filmB, taleX, taleY], ...] plays tale [X, Y] over film [A, B] linearly, so a segment can
  be stretched; between segments taleTime(t) returns the last segment's end, so the tale parks on
  its final frame during a cutaway. Cues and fire shots are written in film time, tale shots stay
  in tale time, tale-anchored sound events are converted once at start-up with the inverse map
  filmOf(ts), the pulse phase integrates the tale's rate per frame, and ambient motion (flames,
  shimmer) runs on film time so the frame stays alive while parked.
- Got right: No tale literal changed; the 28-still contact sheet matched the shot list and all 44
  captions met their reading time; the three cutaways slot in by adding map rows. The sound layer
  was converted the same way but the session had no way to listen to it, so its sync is assumed.
- Where/why it failed: The cut before this one derived the time warp from caption reading time
  alone and clamped every stretch without a caption to at most 1.4 s. That worked for a
  caption-dense cut, and would have crushed this cut's silent walks and crossings, which carry the
  story; a warp derived from text only knows about text. The inverse map also has a trap: a
  flash-forward segment at film 0 replays tale 135 to 136, so an inverse lookup that scans every
  segment resolves tale 135.5 to the cold open instead of the climax; the inverse must skip
  replayed segments.
- Fix: Replace the text-derived warp with the explicit segment map (stretch factors chosen per
  segment, cutaways as gaps) and have the inverse map skip the flash-forward row.
- Why this fix: The map keeps every table in the clock it was authored in and makes the stretch a
  per-segment decision instead of a global rule, so action and text get the time each needs;
  skipping replayed rows keeps the inverse single-valued.
- Rule of thumb: To lengthen a timeline-hard-coded film, map film time onto the story clock per
  segment (stretch, or park during cutaways) and convert story-anchored cue times once with the
  inverse map, skipping any replayed segment; a warp derived from caption reading time alone
  crushes silent action.
- Provenance (verified/assumed): verified first-hand for picture and captions, the 28-still
  contact sheet and the 44-caption sweep on the published cut. The sound layer is covered under
  Got right.
- Composed: film/E7, seven/E49, brain-film-explainer/E2
- Distinct from: film/E7 finds that a beat can be inserted by remapping T at the dispatcher and
  shifting absolute-time tables; this finds that a per-segment map can also park the story during
  cutaways and that story-anchored events are converted with the inverse map (which must skip a
  flash-forward) instead of shifting their tables.
- Link: https://claude.ai/code/session_01WkbM7ZHHguQoKwyDFf4vYn · https://claude.ai/artifact/1kFmKx74PL3QTXsPNWCAQc

## E30 — local screenshots miss the host reset
- Date: 2026-10-17
- Project: Pappydapimp69/Zanegpt
- Tags: [artifact][testing][browser]
- What: A Playwright contact-sheet harness that opens an artifact page from file://, scrubs the
  film to one time per story beat, screenshots the screen element and tiles the stills, run
  before each publish of a canvas film.
- Why built: Brain lesson film/E2 says to tile one still per beat before a long render; the film
  has 20 to 28 beats and a hand check in the browser misses framing bugs.
- Design: Load the local HTML, set the splash overlay's hidden attribute, dispatch an input event
  on the scrubber for each beat time, wait two frames, screenshot, then tile with PIL and read the
  sheet.
- Got right: The sheet caught framing and placement for every beat in seconds, and the same
  harness later carried the caption-timing sweep.
- Where/why it failed: Every still showed the splash button and its dark gradient over the
  bottom third. The page's hidden attribute relies on the publish-time skeleton's rule that
  hides [hidden] elements, which the local file does not carry, and the splash is position:fixed,
  so setting hidden did nothing from file://. The first sheet's dark lower frames were misread as
  a lighting problem in the film itself.
- Fix: The harness removes the overlay element instead of hiding it. The re-rendered wide shots
  showed the real frame, and one real lighting change (a ground glow under the throne) was made
  from that frame rather than from the false one.
- Why this fix: A test should not depend on a stylesheet the host adds at publish time; removing
  the element is equivalent for the test's purpose and holds under any host reset. Mirroring the
  host reset locally would also work but has to be kept in step with the host.
- Rule of thumb: A page that renders inside a host skeleton (resets, [hidden] rules) renders
  differently from file://: in a local screenshot harness remove overlays or mirror the host
  reset, and distrust the first sheet's lighting until you do.
- Provenance (verified/assumed): verified first-hand, the splash appeared in all 24 stills of the
  first sheet and in none after the harness switched to removing the element.
- Composed: film/E2
- Link: https://claude.ai/code/session_01WkbM7ZHHguQoKwyDFf4vYn · https://claude.ai/artifact/1kFmKx74PL3QTXsPNWCAQc

## E29 — caption window must include its fades
- Date: 2026-10-17
- Project: Pappydapimp69/Zanegpt
- Tags: [film][captions][timing]
- What: The caption timing rule of a browser-rendered film (canvas picture, captions as a DOM
  overlay) that sized every caption's on-screen window to its reading time, 0.6 s plus 15
  characters a second, while the caption also faded in and out over 0.3 s at each end.
- Why built: Brain's pacing lessons say the pacing should follow the on-screen text, and the
  owner had reported that the captions went past too fast to read; a per-caption window computed
  from the string length replaces hand retiming each time a line changes.
- Design: One film clock. Each stretch of the timeline that holds a caption is stretched at the
  dispatcher to that caption's window; the caption's opacity envelope is a smooth window that
  ramps over 0.3 s at both ends; a headless-browser sweep scrubs the published page every 0.05 s
  and counts the frames in which the caption's opacity is above 0.9.
- Got right: Pacing-follows-text as a rule removed all hand retiming, and 13 of the 20 captions
  measured as readable on the first sweep; the sweep itself is cheap (one scrub loop) and
  independent of how the window was computed.
- Where/why it failed: 7 of 20 captions measured below 85 percent of their reading time, and
  every caption, long or short, was short by the same 0.5 to 0.6 s: the two fades. The window
  started counting at the start of the fade-in, so the reading budget was spent on the ramps
  where the text is still half transparent.
- Fix: Window = 1.1 s + length / 15 (reading time plus both fades), and the sweep kept as the
  acceptance check. After the change 20 of 20 captions met their budget; the two later cuts
  measured 32 of 32 and 44 of 44.
- Why this fix: The reading budget should start when the text is legible, at full opacity, so
  the fades are overhead added to the window rather than taken from it; measuring fully visible
  time instead of window length keeps the check honest whatever envelope the captions use.
- Rule of thumb: A caption's reading budget starts at full opacity: add both fade durations to
  the window and measure visible time (opacity above 0.9), or every caption runs short by
  exactly its fades.
- Provenance (verified/assumed): verified first-hand with the Playwright sweep on the published
  page, 7 of 20 captions short before the change and 0 of 20, then 0 of 32 and 0 of 44, after it.
- Composed: brain-film-explainer/E2, brainwork/E123, hook-caption-budget/E1
- Link: https://claude.ai/code/session_01WkbM7ZHHguQoKwyDFf4vYn · https://claude.ai/artifact/1kFmKx74PL3QTXsPNWCAQc

## E28 — allegory voice carries the mapping
- Date: 2026-10-17
- Project: Pappydapimp69/Zanegpt
- Tags: [narrative][explainer][process]
- What: A four-minute allegory film explaining how the Conscience node works as a bridge, told
  through the ferryman of the Luck Child tale (Jim Henson's Storyteller), built over nine owner
  rounds in one session.
- Why built: The owner asked for the mechanism described as a bridge, in a film, and then
  steered the casting: Conscience is the ferryman, ZaneGPT the Luck Child, Brain the griffin, and
  the owner the king who ends up holding the pole.
- Design: The tale plays on a canvas (river, griffin constellation, glass ferry, throne) with a
  storyteller at a fire; captions carry dialogue and narration; the owner's casting fixed the
  ending.
- Got right: The owner's casting gave the ending its thesis, and the fairy-tale frame itself
  was accepted; the picture side (shot list, one camera move per shot, hard cuts, a cold open
  that bookends the climax) passed once added.
- Where/why it failed: Two rejections. First, with one continuous camera move and no cuts: you
  almost have a film but not quite. Second, with a voiceover that retold the tale beat for beat
  (the griffin woke, I took the feather): too literal. The narration restated what the picture
  already showed, so the owner heard a fairy tale and got no explanation of the real system.
- Fix: A shot list with one move per shot and hard cuts fixed the first. For the second, the
  tale stayed on screen with no retelling, and every narration line was rewritten to say only
  what the image cannot: what each prop is in the real system (the griffin is Brain picking
  paths every night, the feather is the controls, the pole is the watching duty, "where you were
  before you unparked it"), with three cutaways to the fire for the narrator's observation-versus-
  interpretation checks. The rewritten cut shipped; the owner's reading of it was still to come
  when this was filed.
- Why this fix: Both critiques cited rules Brain already held: storyboarding fundamentals
  (film/E9) and narrate what the image cannot show. The second is the first rule applied to
  allegory: the picture owns the tale, the voice owns the mapping to the real thing, and a voice
  that narrates the picture is redundant twice over.
- Rule of thumb: In an allegory explainer the picture carries the tale and the voice carries the
  mapping to the real thing; a voiceover that retells the on-screen tale reads as too literal even
  when the tale is right.
- Provenance (verified/assumed): verified first-hand, both owner critiques in the session, the
  shot-list fix accepted (the owner moved on to content notes), and the Brain lessons each
  critique matched.
- Composed: film/E9, film/E3, ideas:NARRATION/voiceover-restraint/narrate-what-the-image-cant-show
- Link: https://claude.ai/code/session_01WkbM7ZHHguQoKwyDFf4vYn · https://claude.ai/artifact/1kFmKx74PL3QTXsPNWCAQc

## E27 — parallel fifths fuse by shared partials
- Date: 2026-10-15
- Project: pappydapimp69/zanegpt
- Tags: [creative-arts][music][voice-leading]
- What: A check of the music-theory kernel that parallel fifths and octaves are banned because the two voices fuse
  into one, and that contrary motion keeps voices independent.
- Why built: Brain training on creative arts (current half, weakest link): the kernel cites converging sources but
  had never been put to a number, and "contrary motion keeps independence" was stated without a measure.
- Design: A harmonic model (partials 1 to 10 at 1/n, equal temperament), fusion as the share of the upper voice's
  partial energy that lands on the lower voice's, for eight intervals and for three eight-step two-voice passages.
- Got right: Fusion ranks exactly as the kernel says: octave 94 percent, fifth 22, fourth 9, thirds and sixths 0,
  and a parallel-fifths line stays fused on 8 of 8 steps while parallel thirds never fuse.
- Where/why it failed: My prediction that contrary motion fuses less on average was wrong: the contrary line fused
  27 percent on average against 22 for parallel fifths, because it passes through an octave and a unison on the way.
- Fix: Measure persistence, not the average: contrary motion was fused on no more than 1 step in a row, parallel
  fifths on every step, which is what the rule and the kernel's mechanism are actually about.
- Why this fix: A single perfect consonance reached by contrary motion is allowed in counterpoint for this reason:
  the voices touch and part; fusion only reads as one voice when it lasts across consecutive notes.
- Rule of thumb: Parallel fifths fuse every step in a row (8/8, 22 percent shared partials); contrary motion can
  fuse as much on average but never for more than a step, so judge independence by fused runs, not averages.
- Provenance (verified/assumed): Verified first-hand in the sandbox with an idealised harmonic model; listener
  perception of fusion was not measured.
- Composed: ideas:MUSIC/theory/parallel-fifths-are-banned-for-acoustic-fusion-not-tradition, ideas:MUSIC/theory/stepwise-motion-is-preferred-because-its-trackable, ideas:MUSIC/chiptune/chord-tone-triage
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__parallel-fifths-fuse-by-shared-partials.py
- Prediction: Written first: fusion ranks octave over fifth over fourth over thirds, and contrary motion fuses less
  on average than parallel fifths. The second half was refuted on run 1 and restated as persistence.
- Observed: RESULT: PASS octave 94%, fifth 22%, fourth 9%, thirds 0%; parallel fifths fused 8/8 steps running;
  contrary motion 27% average but at most 1 step running.
- Scenarios: 1) eight intervals; 2) parallel fifths; 3) parallel thirds; 4) a contrary line that crosses perfect
  consonances, built to BREAK the averaged claim
- Link: brain train creative arts (current half), session 2026-10-15; session_011p52L2CkFXcsYRwjDu6tG9

## E26 — offset copy terminator is a stylisation
- Date: 2026-10-15
- Project: pappydapimp69/zanegpt
- Tags: [creative-arts][cel-shading][canvas]
- What: A check of the canvas cel-shading recipe in the composite-modes kernel: fill the lit tone, clip to the
  shape, and fill an offset copy of the shape in the shadow tone to get a hard terminator.
- Why built: Brain training on cel (current half, weakest link): ten cel lessons cover 3D shaders, but the 2D
  recipe used for ads and games on canvas had never been compared with a real terminator.
- Design: A sphere drawn as a disc, its true shadow from N.L under 0, against the recipe's shadow at the best
  offset, with a second variant that may also scale the copy and a half-ellipse terminator, over light angles
  from 20 to 160 degrees from the viewer.
- Got right: The recipe is a fair stylisation once the light is well behind the subject (IoU 0.977 at 160
  degrees), and the half-ellipse terminator (ctx.ellipse with semi-minor axis cos of the light angle) is exact at
  every angle tested.
- Where/why it failed: My prediction that side light fits best was wrong: at 90 degrees the true terminator is
  a straight line and the copy's edge is a curve (IoU 0.841), and near frontal light the thin crescent reaches
  only 0.790; scaling the copy lifts 45 to 135 degrees to at least 0.926 but not the frontal crescent.
- Fix: Draw the terminator as a half-ellipse whose minor axis is the cosine of the light's angle from the viewer,
  and keep the offset copy only as a deliberate stylised crescent.
- Why this fix: The ellipse is the true projection of the great circle where N.L is zero, costs one ellipse call,
  and needs no tuning per angle, while the offset copy needs a different offset at every angle and still misses.
- Rule of thumb: A canvas offset-copy shadow is a stylisation (IoU 0.79 to 0.84 frontal to side light); for a
  correct cel terminator draw a half-ellipse with minor axis cos(light angle).
- Provenance (verified/assumed): Verified first-hand by grid IoU in the sandbox for a sphere; other shapes
  were not tested.
- Composed: ideas:VFX/canvas-recipes/composite-modes-are-the-style, cel-shading/E7, ideas:PAINTING/shadows/edges
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__offset-copy-terminator-is-a-stylisation.py
- Prediction: Written first: the offset copy fits the true terminator best at side light (IoU over 0.97 at 90
  degrees). Refuted on run 1 (0.841); the claim was restated from what three runs showed.
- Observed: RESULT: PASS plain copy 0.790 at 20 deg, 0.841 at 90, 0.977 at 160; scaled copy at least 0.926 from
  45 to 135 but 0.790 at 20; half-ellipse 1.000 everywhere.
- Scenarios: 1) near frontal 20 deg; 2) 45 and 70 deg; 3) side light 90 deg, built to BREAK the recipe; 4) 110 to
  160 deg backlight
- Link: brain train cel (current half), session 2026-10-15; session_011p52L2CkFXcsYRwjDu6tG9

## E25 — cool cel shadows need a luminance floor
- Date: 2026-10-15
- Project: pappydapimp69/zanegpt
- Tags: [creative-arts][cel-shading][color]
- What: The new half's cel path, hue-shift shading (shadows cooler, highlights warmer) with the cel lesson that
  cool shadow tones lose contrast against a dark outline, run with selective outlining as the companion.
- Why built: Pixel-art and cel guides both say to shade cooler, and the outline guidance assumes the shadow
  still separates from the line; nobody had measured how much the cool shift costs or how to keep both.
- Design: Six base colours, a cel shadow at the same HSV value (x 0.65) made three ways: plain darkening, a
  20-degree hue shift toward blue, and the same shift with its luminance held to plain darkening's; WCAG
  contrast of each against a #1a1a2a outline and against the lit tone.
- Got right: Cooler shadows did separate more from the lit tone (gold 3.41 against 2.26, sky 3.21 against
  2.15), which is the readability the hue-shift kernel promises.
- Where/why it failed: At equal HSV value the cool shift lost contrast against the outline in 5 of 6 colours
  (mean 18 percent, gold 4.25 to 2.83, sky 3.29 to 2.20), because hue toward blue drops luminance even when
  HSV value stays the same.
- Fix: Shift the hue, then raise the shadow's value until its luminance matches plain darkening; that restored
  outline contrast in all six colours while keeping the cooler hue.
- Why this fix: HSV value is not perceived brightness, so equal value hides a luminance drop; holding luminance
  makes hue and contrast independent, which is what lets both rules apply at once.
- Rule of thumb: Shade cel shadows cooler but hold their luminance: a 20-degree blue shift at equal HSV value cut
  outline contrast 18 percent on average (5/6 colours); a luminance floor restores it.
- Provenance (verified/assumed): Verified first-hand by WCAG contrast arithmetic in the sandbox; perceived
  readability on screen was not tested with viewers.
- Composed: ideas:ART/pixel-art/hue-shift-shading-scaled-to-sprite-size, cel-shading/E5, ideas:ART/pixel-art/selective-outlining-not-uniform-black
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-15__cool-cel-shadows-need-a-luminance-floor.py
- Prediction: The cool shift at equal HSV value loses outline contrast in at least 4 of 6 colours, and holding
  luminance restores it in all.
- Observed: RESULT: PASS lost in 5/6 (mean 18%); restored in 6/6; lit-to-shadow separation rose with the cool shift.
- Scenarios: 1) warm colours (skin, gold); 2) greens and reds; 3) a colour already near blue (sky), built to
  BREAK the claim that a small shift is harmless; 4) purple
- Link: brain train cel (new half), session 2026-10-15; session_011p52L2CkFXcsYRwjDu6tG9

## E24 — shorten from the front keeps two pass case
- Date: 2026-10-15
- Project: pappydapimp69/zanegpt
- Tags: [creative-arts][songwriting][rhyme]
- What: The new half's strongest songwriting path, two-pass rhyme lettering with rhyme-scheme shape, run with its
  companion, shortening rushed Suno lines from the front so the rhyme word survives.
- Why built: The companion showed front-shortening keeps a stanza's shape, but two-pass lettering also carries
  meaning in its case (uppercase resolved, lowercase open); nobody had checked that the case survives too.
- Design: Four rushed stanzas, one per shape (AABB, ABAB, XXAA, ABBA), each with an assonance distractor, a small
  phonetic lexicon, two-pass and one-pass lettering, and two shortening methods to six words.
- Got right: Front-shortening kept the exact two-pass letters, case included, in 4 of 4 shapes, so the
  resolved-versus-open reading the songwriter relies on is untouched.
- Where/why it failed: Cutting the end of each line to six words kept 0 of 4 shapes (every rhyme word went),
  and after front-shortening one-pass lettering still misread XXAA as XAAA because the fire/night assonance
  steals a letter: shortening does not remove the need for the second pass.
- Fix: Shorten rushed lines from the front, then letter with two passes; never trim from the end, and never
  trust a one-pass scheme readout on a stanza with assonance in it.
- Why this fix: The rhyme word is the only thing lettering reads, so any cut that keeps it is safe for both
  shape and case, while the one-pass failure is independent of length.
- Rule of thumb: Shortening from the front keeps two-pass letters exactly, case included (4/4), end-trimming
  keeps 0/4, and one-pass still misreads XXAA after shortening.
- Provenance (verified/assumed): Verified first-hand in the sandbox; the lexicon's rhyme keys are hand-coded,
  so real pronunciation judges were not exercised.
- Composed: ideas:SONGWRITING/rhyme-tooling/two-pass-letter-assignment-keeps-schemes-legible, ideas:SONGWRITING/rhyme/rhyme-scheme-shape-sets-a-songs-emotional-motion, sandbox-shorten-rushed-lines-keep-the-rhyme-word/E1
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-15__shorten-from-the-front-keeps-two-pass-case.py
- Prediction: Front-shortening keeps exact two-pass letters in 4/4; end-trimming keeps at most 1/4; one-pass still
  misreads XXAA.
- Observed: RESULT: PASS 4/4 kept with case; end-trimming 0/4; one-pass misread XXAA as XAAA.
- Scenarios: 1) AABB; 2) ABAB; 3) XXAA with an assonance distractor, built to BREAK one-pass lettering; 4) ABBA
- Link: brain train (creative arts, loop 1, new half), session 2026-10-15; session_011p52L2CkFXcsYRwjDu6tG9
- Audited: 2026-10-16 · modeled · Read the entry and its stored sandbox and reran it (RESULT PASS, 4/4, 0/4, XXAA misread). The 4/4 "front-shortening keeps exact two-pass letters, case included" result is true by construction: letters() reads only each line's final word, and the front() cut always keeps the final word, so the letter input is identical before and after the cut; the model assumes its answer rather than computing it. The end-truncation 0/4 and the one-pass XXAA misread are computed from the lexicon and do test something. The claim is about how a real Suno vocal line and real rhyme perception behave, but only a 19-word hand-coded lexicon and orthographic stanza text were run, and the entry itself says pronunciation judges were not exercised, so it is a hand-written model of a real system, not a test of it. · brain train auto audit, session 2026-10-16; session_013uRvb55pYWRMwoocxRqQ3a

## E23 — penumbra grows linearly only far from the light
- Date: 2026-10-15
- Project: pappydapimp69/zanegpt
- Tags: [creative-arts][painting][rendering]
- What: A check of the painting kernel that a cast shadow is sharp at contact and blurs with distance, with
  penumbra width given as light radius times occluder-to-receiver distance over light-to-occluder distance.
- Why built: Brain training on creative arts (current half, weakest link): the kernel had never been tested,
  calls the relation linear, and lists its sunlight figure of about a centimetre per metre as unverified.
- Design: Brute-force 2D ray casting: a disk light seen edge-on, a knife-edge occluder at heights from 0 to
  2.7 m under a 0.5 m light at 3 m, ground points lit by the fraction of light samples that clear the edge.
- Got right: The kernel's formula held: zero penumbra at contact and the raycast width matched
  r h / (H - h) within 1 percent at every height; sunlight (0.53 degree disc) gives 0.93 cm per metre.
- Where/why it failed: "Linear" only holds while the object is short compared with its distance to the light:
  at 0.3 m the straight-line estimate was 10 percent low, at 2 m it was a third of the true blur (0.67 against
  2.0 m), and at 2.7 m a tenth (0.9 against 9 m), because the denominator shrinks as the edge nears the light.
- Fix: Use width = light size x gap / (light distance - gap) for near lights such as a window or a lamp, and
  keep the straight-line centimetre-per-metre rule for the sun, where the light is effectively infinitely far.
- Why this fix: The two cases differ only in whether the light distance is large against the object's
  height; one formula covers both, and the sun case reduces to the simple rule painters can carry.
- Rule of thumb: Shadow blur is zero at contact and grows 0.93 cm per metre under the sun, but under a near
  light it grows faster than linear (a 2 m object under a lamp at 3 m blurs 3x the straight-line estimate).
- Provenance (verified/assumed): Verified first-hand by ray casting in the sandbox; the sun's 0.53 degree
  angular diameter is a standard astronomical value used as input.
- Composed: ideas:PAINTING/shadows/edges, ideas:PAINTING/shadows/grounding, ideas:PHOTOGRAPHY/lighting/golden-hour
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__penumbra-grows-linearly-only-far-from-the-light.py
- Prediction: Raycast matches the formula within 1 percent, zero at contact, near-linear when the gap is small,
  far off near the light, and sunlight gives between 0.8 and 1.0 cm per metre.
- Observed: RESULT: PASS within 1% at all heights; 0.111 against 0.100 m at 0.3 m; 8.98 against 0.90 m at
  2.7 m; sunlight 0.93 cm per metre.
- Scenarios: 1) contact; 2) small gaps 0.1 and 0.3 m; 3) mid gaps 0.6 and 1 m; 4) an edge 0.3 m from the
  light, built to BREAK the linear claim; 5) the sun
- Link: brain train (creative arts, loop 1, current half), session 2026-10-15; session_011p52L2CkFXcsYRwjDu6tG9

## E22 — hyphenated rhyme words need the joined word
- Date: 2026-10-15
- Project: pappydapimp69/zanegpt
- Tags: [creative-arts][songwriting][suno]
- What: The new half's second songwriting path, hyphenating words to slow a rushed Suno line, run with the Suno
  builder and its companion lesson that two-pass lettering needs a phonetic judge and a scoped search.
- Why built: Hyphenation changes exactly the words a rhyme judge reads ("to-night", "for-ev-er"), and a lyric
  tool that letters schemes after the singer's edits would see the hyphenated spelling.
- Design: Four stanzas whose rhyme words are the long words songwriters hyphenate, a phonetic lexicon, and three
  ways to read a hyphenated word: rejoin it, look the token up as written, or take the first fragment.
- Got right: Rejoining the word before the lookup kept every stanza's letters (4 of 4), so hyphenating for timing
  is safe for the scheme as long as the judge sees the whole word.
- Where/why it failed: The two other readings lost every scheme (0 of 4 each): the hyphenated token is not in
  the lexicon and the first fragment ("for", "to") has the wrong vowel, so all 13 rhyme words went unrhymed.
- Fix: Strip hyphens (and any other timing marks) before the rhyme lookup, while sending the hyphenated text to
  the singer; keep the timing edit and the rhyme analysis on separate copies of the line.
- Why this fix: The hyphens are delivery instructions, not spelling; analysis that reads them as spelling is the
  same scoping failure the companion lesson found, moved from search scope to token scope.
- Rule of thumb: After hyphenating a lyric for timing, rejoin words before lettering rhymes: rejoined kept 4/4
  schemes, the raw token or first fragment kept 0/4.
- Provenance (verified/assumed): Verified first-hand in the sandbox; how Suno itself treats hyphens is taken from
  the kernel's single community source and was not tested here.
- Composed: ideas:SONGWRITING/suno-prompting/hyphenate-words-to-slow-a-rushed-vocal-line, suno-builder/E1, sandbox-two-pass-lettering-needs-scope-and-phonetic-judge/E1
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-15__hyphenated-rhyme-words-need-the-joined-word.py
- Prediction: Rejoining keeps 4/4 schemes; the raw token and the first fragment each keep fewer than 4.
- Observed: RESULT: PASS 13 rhyme words hyphenated; rejoined 4/4, raw token 0/4, first fragment 0/4.
- Scenarios: 1) rejoin before lookup; 2) raw hyphenated token; 3) first fragment, the common split bug built to
  BREAK it; each over AABB, ABAB, XXAA and ABBA stanzas
- Link: brain train (creative arts, loop 2, new half), session 2026-10-15; session_011p52L2CkFXcsYRwjDu6tG9

## E21 — drop the fifth because the root already sings it
- Date: 2026-10-15
- Project: pappydapimp69/zanegpt
- Tags: [creative-arts][music][chiptune]
- What: A check of the chiptune kernel that, short of voices, you drop a chord's fifth before its third,
  because the third carries major or minor and the fifth is largely redundant.
- Why built: Brain training on creative arts (current half, weakest link): the kernel rests on one community
  source and says "largely redundant" without saying what supplies the missing fifth.
- Design: A harmonic model of a voice (partials 1 to 10 at 1/n, and an odd-only square-ish version), measuring
  the energy the root alone puts on the fifth, the major third and the minor third pitch classes, and how far
  apart major and minor stay with root plus third versus root plus fifth.
- Got right: The kernel holds in both timbres: root plus fifth cannot tell major from minor at all (difference
  0.00 against 0.50 for root plus third), so the third is the tone that must stay.
- Where/why it failed: My first metric asked whether the fifth's own overtones were already in the root,
  found 0 percent for square waves and looked like an exception; that measured the wrong thing. The redundancy
  is the root's 3rd harmonic sounding the fifth's pitch class, which square waves keep.
- Fix: State the mechanism: the root's own overtones sound the fifth 2.8 times as strongly as the major third
  and never sound the minor third, so drop the fifth first and never drop a minor third.
- Why this fix: It gives the reason a number and adds the case the kernel leaves out: a dropped major third is
  faintly implied by the root's 5th harmonic, a dropped minor third is implied by nothing.
- Rule of thumb: Drop the fifth first because the root's 3rd harmonic already sounds it (2.8x the major third,
  in sine-rich and square voices alike); a minor third is the one chord tone nothing else supplies.
- Provenance (verified/assumed): Verified first-hand in the sandbox with an idealised 1/n harmonic model; real
  chip channels' exact partial levels were not measured.
- Composed: ideas:MUSIC/chiptune/chord-tone-triage, ideas:MUSIC/chiptune/arpeggiation-phantom-chord, ideas:MUSIC/theory/tonic-subdominant-dominant-is-the-tension-engine
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__drop-the-fifth-because-the-root-already-sings-it.py
- Prediction: The root implies the fifth at least twice as strongly as the major third and the minor third not
  at all, in both timbres; root plus fifth loses major against minor.
- Observed: RESULT: PASS fifth 0.139 against major third 0.050 and minor third 0 (square 0.111, 0.040, 0);
  major against minor 0.50 with the third, 0.00 with the fifth.
- Scenarios: 1) full harmonic voice; 2) odd-only square-ish voice, the timbre built to BREAK the redundancy claim;
  3) major against minor with each reduced voicing
- Link: brain train (creative arts, loop 2, current half), session 2026-10-15; session_011p52L2CkFXcsYRwjDu6tG9

## E20 — theater stagger beats depth line
- Date: 2026-10-15
- Project: pappydapimp69/zanegpt
- Tags: [creative-arts][theater]
- What: Stage blocking for three actors and how many audience seats lose sight of an
  actor behind another, comparing a depth line, a flat row and two staggers.
- Why built: Seeding the creative-arts domain. Directors stagger actors on instinct, but
  how much lateral offset a stagger needs to work is rarely stated as a number.
- Design: Seats on an arc plus a back row; actors modelled as 0.25 m radius discs; a
  seat-actor pair counts as occluded when another actor's disc crosses the sightline.
- Got right: A stagger of 0.75 m sideways per 1 m of depth cut occluded pairs from 62 of
  114 (straight depth line) to 27, more than half, while keeping stage depth.
- Where/why it failed: A tight stagger of 0.25 m sideways barely helped (53 of 114), and
  no stagger reached zero; only a flat row across the stage did, and it throws away all
  depth, so stagger alone does not clear every seat.
- Fix: Offset each upstage actor sideways by at least about three body radii from the
  actor in front, and use cheating out or moving to rotate which seats are blocked
  instead of chasing zero with static positions.
- Why this fix: Occlusion is set by the sideways gap compared to body width, not by depth,
  so a small nudge reads as a stagger to the director but blocks nearly as much as a line.
- Rule of thumb: A stagger only clears sightlines when the sideways offset is about three
  body radii or more; a small nudge blocks almost as much as a straight depth line.
- Provenance (verified/assumed): Verified first-hand with a deterministic geometry
  sandbox on one seating layout. Other house shapes such as thrust or in-the-round
  were not tested, and the three-radii figure is from this layout only.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__theater-stagger-beats-depth-line.py
- Prediction: Stagger at 0.75 m cuts occluded pairs to half or less of the depth line;
  a 0.25 m stagger stays worse than the 0.75 m one.
- Observed: RESULT: PASS stagger 27 vs depth line 62 vs tight stagger 53 (flat row 0,
  all out of 114 seat-actor pairs).
- Scenarios: 1) depth line; 2) flat row; 3) 0.75 m stagger; 4) 0.25 m stagger, built to
  BREAK the claim that any stagger helps
- Link: brain train newdomain creative-arts, session 2026-10-15; session_011p52L2CkFXcsYRwjDu6tG9

## E19 — ceramics shrink divide not multiply
- Date: 2026-10-15
- Project: pappydapimp69/zanegpt
- Tags: [creative-arts][ceramics]
- What: Sizing wet clay so a pot fires to a target size, given the clay body's total
  shrinkage percentage (wet to fired).
- Why built: Seeding the creative-arts domain with a real craft calculation that potters
  get wrong. A lid, a set of mugs or a tile that must fit a frame needs the fired size exact.
- Design: Model the clay as fired = wet * (1 - s), then compare two ways of sizing the
  wet piece: wet = target * (1 + s) (the common shortcut) and wet = target / (1 - s).
- Got right: Dividing by (1 - s) hits the target exactly at every shrink rate tested,
  because it is the true inverse of the shrink, not an approximation of it.
- Where/why it failed: The multiply shortcut always fires short, and the shortfall is
  exactly s squared: 0.36% at 6%, 1.44% at 12%, 2.25% at 15%. On a 100 mm lid that is
  1.4 to 2.3 mm, enough that a lid no longer seats on its gallery.
- Fix: Size every wet dimension as target / (1 - s), or build a shrink ruler whose marks
  are spaced 1 / (1 - s) apart, so the potter reads fired size directly off the wet clay.
- Why this fix: It is the exact inverse of how clay shrinks, it costs no extra effort,
  and the error from the shortcut grows with the square of shrinkage, so high-shrink
  porcelain is exactly where the shortcut hurts most.
- Rule of thumb: To undo a percentage shrink, divide by (1 - s); multiplying by (1 + s)
  undershoots by s squared, which matters for fitted parts like lids and tiles.
- Provenance (verified/assumed): Verified first-hand with a deterministic sandbox at
  0, 6, 12 and 15 percent shrink. The 10-15 percent range for stoneware and porcelain is
  typical published clay-body data, taken from general craft knowledge.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__ceramics-shrink-divide-not-multiply.py
- Prediction: Divide hits 100.00 mm exactly; multiply fires short by s^2, i.e. 1.44% at
  12% and 2.25% at 15%, and no difference at 0%.
- Observed: RESULT: PASS naive multiply fires short by exactly s^2 (1.44% at 12%, 2.25%
  at 15%); divide hits target. Naive results 99.64, 98.56, 97.75 mm.
- Scenarios: 1) 0% shrink, built to BREAK it (no difference expected); 2) 6%; 3) 12%; 4) 15%
- Link: brain train newdomain creative-arts, session 2026-10-15; session_011p52L2CkFXcsYRwjDu6tG9

## E18 — calligraphy nib angle stroke contrast
- Date: 2026-10-15
- Project: pappydapimp69/zanegpt
- Tags: [creative-arts][calligraphy]
- What: How a broad-edge pen's held angle sets which strokes come out thick and which
  come out thin, for lettering by hand or a procedural calligraphy brush.
- Why built: Seeding the creative-arts domain. Pen angle is the one setting that decides
  a whole script's thick/thin pattern, and it is usually taught by feel, not by number.
- Design: Model stroke width as nib width times |sin(stroke direction - nib angle)| and
  sweep nib angles of 0, 30 and 45 degrees over every stroke direction.
- Got right: The model reproduces the known script behaviour: a 30 degree nib gives
  verticals about 1.73 times as thick as horizontals, and a 0 degree nib makes
  horizontals pure hairlines.
- Where/why it failed: A 45 degree nib, often suggested as a safe default, removes the
  vertical vs horizontal contrast entirely (ratio 1.00): the contrast moves to the
  diagonals instead, so upright letters look flat and even-weighted.
- Fix: Choose the nib angle from the contrast the script needs: about 30 degrees for
  foundational hand, 45 degrees only for italic where diagonals carry the weight, and
  hold it constant across every letter.
- Why this fix: The thickest stroke always falls at nib angle plus 90 degrees, so angle
  is a direct, predictable dial, and holding it constant is what makes a script cohesive.
- Rule of thumb: The thickest broad-nib stroke runs at nib angle + 90 degrees; 30 degrees
  makes verticals heavy, 45 degrees evens verticals and horizontals out.
- Provenance (verified/assumed): Verified first-hand with a deterministic sandbox at nib
  angles 0, 30 and 45. Which scripts use which angle comes from general calligraphy
  teaching and was not measured here.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__calligraphy-nib-angle-stroke-contrast.py
- Prediction: Thickest stroke at nib + 90 for each angle; V/H ratio sqrt(3) = 1.73 at 30
  degrees, 1.00 at 45 degrees, horizontal width 0 at 0 degrees.
- Observed: RESULT: PASS thickest stroke = nib+90; 30deg nib gives V/H 1.73, 45deg gives
  1.00, 0deg makes horizontals hairlines.
- Scenarios: 1) nib 0; 2) nib 30; 3) nib 45, built to BREAK the claim that verticals are
  always heavier
- Link: brain train newdomain creative-arts, session 2026-10-15; session_011p52L2CkFXcsYRwjDu6tG9

## E17 — sundial style tilt error grows with the hour and vanishes at noon
- Date: 2026-10-15
- Project: Pappydapimp69/Zanegpt
- Tags: [sundial][geometry][simulation][testing]
- What: Build tolerance for the SUNDIALS kernel: how many minutes a horizontal
  dial reads wrong when its style is tilted off the latitude angle (a common
  build or levelling error), computed by exact shadow projection and read back
  through the printed hour-line formula.
- Why built: brain train auto pass 5 (gap mode) listed the SUNDIALS kernel as
  unapplied. Its own sandbox proved the formula for a perfect style; the
  practical question for anyone building one is how precise the style must be.
- Design: Sun vector at latitude L, declination -23.44 to +23.44, hour angles 0
  to 5 h either side of noon; style tip tilted to L + tilt; shadow of the tip
  projected onto the dial; the angle read back to hours with the kernel's
  formula; worst error in minutes. Latitudes 25, 40, 55 then unseen 30, 50, 60.
- Got right: Noon is exact at every tilt. Worst error is about 3.6 min per degree
  at latitude 40 (1/2/5 deg give 3.59/7.15/17.61 min) and follows
  2.3 x tilt / sin(latitude) minutes within 6.8% at latitudes 30, 50 and 60.
- Where/why it failed: My first prediction said the error keeps growing away from
  noon; it peaks 3 to 4 hours from noon and falls by 5 hours. My second check
  (peak always at 3 h, 2.5 to 5 min per degree) failed at latitudes 25 and 55;
  the 1/sin(latitude) scaling came from reading those failures.
- Fix: Budget a style angle tolerance from the accuracy you need: tolerance in
  degrees = allowed minutes x sin(latitude) / 2.3. At latitude 40, a 2-minute
  dial needs the style within about 0.6 degrees; check it mid-morning, not at
  noon, because noon hides the error.
- Why this fix: A tilted style moves the shadow plane off Earth's axis, so the
  error depends on the hour and vanishes on the meridian; the printed lines are
  only exact for the polar-aligned style the kernel assumes.
- Rule of thumb: A horizontal sundial with its style tilted off the latitude
  angle reads wrong by up to about 2.3 x tilt / sin(latitude) minutes, worst 3
  to 4 hours from noon and exact at noon, so check a new dial mid-morning, not
  at noon (3.6 min per degree at latitude 40).
- Provenance (verified/assumed): verified first-hand by the sandbox in three
  iterations; the dial geometry is exact, the 2.3 constant is fitted on three
  latitudes and confirmed on three unseen ones (within 6.8%).
- Composed: ideas:SUNDIALS/horizontal-dial/hour-lines-are-set-by-a-polar-aligned-style-not-a-vertical-stick
- Sandbox: sandboxes/2026-10-15__sundial-style-tilt-error-grows-with-the-hour-and-vanishes-at-noon.py
- Prediction: iteration 1 (before any run): 0 error at tilt 0, exact at noon,
  under 4 min at 1 degree, over 10 min at 5 degrees, growing with the hour.
  Iteration 3 (before its run): worst error within 12% of 2.3 x tilt / sin(L),
  peaking 3 or 4 h from noon, at unseen latitudes 30, 50, 60.
- Observed: iteration 1 RESULT: FAIL (peak at 3 h, not growing); iteration 2
  RESULT: FAIL (peak 4 h at L=55, 5.44 min/deg at L=25); iteration 3 RESULT:
  PASS worst error = 2.3 x tilt / sin(latitude) within 6.8%, peaking 3-4 h from
  noon, exact at noon (latitudes 30/50/60, tilt 1 and 3 deg).
- Scenarios: 1) tilt 0, the control; 2) tilt 1, 2, 5 deg at latitude 40;
  3) latitudes 25, 40, 55 at 1 deg; 4) unseen latitudes 30, 50, 60 at 1 and
  3 deg, built to break the fitted 1/sin(latitude) rule.
- Link: https://claude.ai/code/session_01TQvFfNiYzpWZZDPgWeMoBC (brain train auto pass 5)

## E16 — pin puzzle speed cap only stops tunneling under a fixed step accumulator
- Date: 2026-10-15
- Project: Pappydapimp69/Zanegpt
- Tags: [gamedev][physics][simulation][determinism][testing]
- What: Extended particle-speed-cap-per-tick-fixed-step#E1 (a per-tick speed
  cap guards only a fixed step) on the pin-puzzle cap it actually came from,
  pappydapimp69__demo-disc#E38, to measure two things that entry left open: how often a
  frame-time step tunnels across start phases and hitch positions, and whether
  the fixed-step accumulator is enough on its own without the cap.
- Why built: brain train auto pass 2 (edge mode) offered demo-disc + brain as
  untested. The pair was already composed, but against the wrong demo-disc entry
  (the step-hook lesson, not the pin puzzle) and from one start phase and one
  hitch position, so it showed tunnelling can happen, not how often.
- Design: A particle centre falls at constant speed onto a 10 px wall with a
  discrete end-of-step push-out; 100 start phases (0.1 px apart) per case; frame
  schedules: fixed 60 Hz, raw 30 fps, a 1/20 s hitch in a 60 Hz cycle (swept over
  all 10 positions), the same schedules through a 60 Hz accumulator, and an
  uncapped 900 px/s ball through the accumulator.
- Got right: The cap holds at fixed 60 Hz (0/100) and through a 60 Hz
  accumulator for 30 fps rendering (0/100) and for hitches (0/1000).
- Where/why it failed: Stepped by frame time, the same 400 px/s cap tunnels 33/100
  phases at 30 fps and 167/1000 phase-and-position pairs with one 1/20 s hitch
  per 10 frames; my first hitch run showed 0 only because the hitch fell after
  the crossing. The accumulator alone does not hold either: uncapped 900 px/s
  tunnels 50/100 through it.
- Fix: Keep both halves: cap speed below wall thickness per FIXED tick and step
  physics through a fixed-dt accumulator, so a slow frame becomes several small
  steps; test with a hitch swept across the crossing, not one fixed schedule.
- Why this fix: The cap is a per-tick distance bound expressed as a speed; only
  a fixed tick turns the speed back into the distance it was derived from.
- Rule of thumb: The pin-puzzle speed cap and the fixed-step accumulator are
  both required: frame-time steps tunnel 33% of start phases at 30 fps and 17%
  with one hitch, and the accumulator without the cap tunnels 50% at 900 px/s;
  sweep the hitch across the wall crossing when testing.
- Provenance (verified/assumed): verified first-hand by the sandbox (two
  iterations); the 1D constant-speed model is a simplification of the 2D liquid.
- Composed: local__particle-speed-cap-per-tick-fixed-step/E1, pappydapimp69__demo-disc/E38, pappydapimp69__brain/E119
- Sandbox: sandboxes/2026-10-15__pin-puzzle-speed-cap-only-stops-tunneling-under-a-fixed-step-accumulator.py
- Prediction: fixed 60 Hz 0%; raw 30 fps at least 20%; 30 fps through the
  accumulator 0%; one hitch per 10 frames tunnels on some phases; uncapped
  900 px/s tunnels even through the accumulator.
- Observed: iteration 1 RESULT: FAIL (hitch 0/100: it fell after the crossing).
  Iteration 2 RESULT: PASS cap holds at fixed 60 Hz (0) and under the accumulator
  (0, 0) but raw 30 fps tunnels 33/100 and one 1/20 s hitch 167/1000 when swept
  over its position (0/1000 with the accumulator); uncapped 900 px/s tunnels
  50/100 even with the accumulator.
- Scenarios: 1) fixed 60 Hz; 2) raw 30 fps; 3) hitch swept over 10 positions,
  raw; 4) 30 fps into a 60 Hz accumulator; 5) hitch into the accumulator;
  6) uncapped 900 px/s into the accumulator, built to break "the accumulator is
  enough".
- Link: https://claude.ai/code/session_01TQvFfNiYzpWZZDPgWeMoBC (brain train auto pass 2)

## E15 — firewood dry basis in the wet formula is small when seasoned and catastrophic when green
- Date: 2026-10-15
- Project: Pappydapimp69/Zanegpt
- Tags: [firewood][units][simulation][testing]
- What: Tested the unit trap the FIREWOOD kernel names but never checked: feeding
  the wet-basis heat formula q = 19(1-m) - 2.443m a dry-basis moisture figure
  u = water/dry mass, as wood meters and forestry tables often report it.
- Why built: brain train auto pass 1 (kernel mode) offered the FIREWOOD kernel;
  its own sandbox already covered per-kg vs per-log heat, so re-running that would
  duplicate it. The untested claim was the unit warning.
- Design: Deterministic sweep of dry-basis u from 0.10 to 2.00, converting to wet
  basis m = u/(1+u) for the right value and plugging u straight in for the wrong
  one; per-kg and per-log (2 kg dry matter) views; zero point of each.
- Got right: Seasoned wood barely notices the mistake: u 0.10 to 0.25 gives
  1.1% to 7.3% low. Green wood breaks: u 1.00 (50% wet) gives -2.44 MJ/kg
  instead of 8.28, and a 2 kg-dry log gives -9.8 MJ instead of 33.1.
- Where/why it failed: The error is not proportional, so a spot check on seasoned
  wood passes and hides the bug; the wrong formula reaches zero heat at dry-basis
  u 0.886 (47% wet), while the right one only does at 88.6% wet.
- Fix: Convert dry-basis moisture to wet basis (m = u/(1+u)) before the formula,
  and test the calculator on green wood (u 1.0), where the mistake shows as a
  negative heat value, not on seasoned wood, where it hides inside 7%.
- Why this fix: The two bases agree near zero moisture and diverge fast, so only
  a wet-wood test case separates a correct implementation from a wrong one.
- Rule of thumb: Firewood heat from a dry-basis meter reading must be converted
  to wet basis first; the mistake costs under 8% on seasoned wood but turns green
  wood negative (-2.4 instead of 8.3 MJ/kg), so test on green wood, not seasoned.
- Provenance (verified/assumed): verified first-hand by the sandbox run; the
  formula and constants are the kernel's (FAO and Secure-Bio-Supply sources).
- Composed: ideas:FIREWOOD/moisture/green-wood-loses-half-the-heat-per-kilo-but-a-tenth-per-log
- Sandbox: sandboxes/2026-10-15__firewood-dry-basis-in-the-wet-formula-is-small-when-seasoned-and-catastrophic-when-green.py
- Prediction: written into the script's pass condition before the first run:
  seasoned wood (u up to 0.25) errs by under 10%, and green wood (u 1.0 and
  above) comes out zero or negative.
- Observed: RESULT: PASS seasoned (u<=0.25) error -7.3% to -1.1%; green (u>=1.0)
  wrong value -2.44 MJ/kg, i.e. zero or negative heat. Middle: u 0.43 -22%,
  u 0.67 -55%.
- Scenarios: 1) seasoned u 0.10-0.25; 2) middle u 0.43-0.67; 3) green u 1.0-2.0,
  built to break the "small error" reading; 4) per-log view at u 0.25 and 1.0.
- Link: https://claude.ai/code/session_01TQvFfNiYzpWZZDPgWeMoBC (brain train auto pass 1)

## E14 — generator parity caps reachable orderings for bell touches and faro shuffles
- Date: 2026-10-15
- Project: Pappydapimp69/Zanegpt
- Tags: [change-ringing][card-magic][permutation][parity][sandbox]
- What: Checked whether the change-ringing parity limit (plain and bob lead ends are even permutations, so a bobs-only Plain Bob Minor
  touch is stuck in 360 of 720 rows) is a general rule for any set of reorderings, using faro shuffles (zanegpt/E11) as the second
  domain. It is as an upper bound, not as a prediction: when every generator is even, no odd ordering is ever reached, but faros reach far
  fewer orderings than the even half.
- Why built: Train gap pass on the unapplied change-ringing kernel; the faro entry is also a fixed set of permutations applied over and
  over, so the bell kernel's parity argument predicts which faro decks are confined to even orderings.
- Design: Python stdlib, deterministic. Bells: place notation to change permutations, plain courses for Minimus, Doubles and Minor
  counted as distinct rows (brainwork/E216's counts), lead-end parity, and every row reachable from rounds by any sequence of plain and
  bob leads, then with singles too. Faros: parity of out and in faros for even decks of 4 to 52 cards, and the full set of orderings
  reachable by any mix of out and in faros, by search capped at 3 million.
- Got right: E216's counts reproduced (Minimus 24 of 24, Doubles 40 of 120, Minor plain course 60 of 720); lead ends 12 and 14 are
  even and 1234 is odd; plain and bob leads reach exactly 360 of 720 rows and adding the single reaches all 720. Decks of 8, 16 and 24
  cards, where both faros are even, never produced an odd ordering, while every deck with an odd faro did.
- Where/why it failed: Parity alone did not predict how much can be reached. For bells the bound is tight (360 is exactly half), but 8
  cards under out and in faros reach only 24 of the 20,160 even orderings, and 16 cards only 64, so a parity check says what is
  impossible, not what is possible. The 20 and 24 card searches hit the 3 million cap, so the 24 card result rests on the generators
  both being even.
- Fix: Before searching a permutation space for a target (a true extent, a stack order, a puzzle state), compute the parity of each
  move; if all are even, drop every odd target at once. Then measure the reachable set itself, by search or group order, before
  assuming the even half is all reachable.
- Why this fix: The parity check costs one cycle count per generator and rules out half the space for certain, which is what made the
  bobs-only 360 limit easy to explain; but the faro numbers show the real reachable set can be smaller than that half by a factor of a
  thousand, so it cannot replace the search.
- Rule of thumb: If every move in a permutation puzzle is even, no odd ordering is reachable (bells: plain and bob reach 360 of 720,
  the odd single reaches 720; 8, 16 and 24 card faros never go odd), but even moves can reach far less than half (8-card faros reach 24 of
  20,160), so use parity to rule out targets, never to promise them.
- Provenance (verified/assumed): Verified first-hand by running the shipped sandbox (RESULT: PASS); 52-card faro reachability was not
  enumerated (only its parities, both odd), and bell results cover Plain Bob on 4 to 6 bells only.
- Composed: ideas:CHANGE-RINGING/method-composition, brainwork/E216, zanegpt/E11
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__generator-parity-caps-reachable-orderings-for-bell-touches-and-faro-shuffles.py
- Prediction: Plain courses 24/24, 40/120 and 60/720; plain+bob reach 360 and adding the single reaches 720; faro decks whose out and in
  are both even reach no odd ordering, and their reachable count is well under half of n!.
- Observed: RESULT: PASS bells: minimus 24/24, doubles 40/120, minor plain 60/720; bob and plain lead ends even so plain+bob reach
  360/720, single (odd) reaches 720; faros: decks whose out and in are both even [8, 16, 24] never reach an odd ordering, but 8 cards
  reach only 24 of 20160 even orderings (bound not tight); 52 cards out/in parity (1, 1).
- Scenarios: 1) plain-course row counts on 4, 5 and 6 bells; 2) plain+bob vs plus single on 6 bells; 3) faro parity and reachability
  for 4 to 24 cards; 4) built to BREAK the cross-domain rule: tightness of the parity bound for faros (it broke: 24 of 20,160)
- Link: brain train auto run 2 pass 5 (gap); session_01Hecxxt7Wfrejc8A3YVX1ht

## E13 — rhyme letter scope per section type keeps chorus repeats linked without cross verse false links
- Date: 2026-10-15
- Project: Pappydapimp69/Zanegpt
- Tags: [lyrical-composition][rhyme-tooling][state][algorithm]
- What: Tested which scope a rhyme-letter table should have in a verse-chorus-verse-chorus song. One global table (the single shared key
  of draft/E4) kept both chorus repeats linked but made 6 false links, including a verse-2 line tied to the chorus by its end sound
  (the section-blind bug of sandbox-lyrical-composition/E7). Resetting per section instance removed those but lost all 8 chorus-repeat
  links. Scoping by section type (chorus repeats share one table, each verse owns one) gave 0 false and 0 missed links.
- Why built: Train edge pass on the strong untested pair lyrical-composition plus draft. draft/E4 says to drive two consumers from one
  shared counter so they cannot disagree, at the cost of silent retirement, and lyrical E7 says a scope-blind assigner conflates
  sections; the two pull in opposite directions on how wide a shared key should be.
- Design: Python stdlib, deterministic. A 16-line song with hand-set rhyme classes: verse 1 ABAB, chorus AABB, verse 2 with one line
  sharing the chorus sound, chorus repeated. Intended links are same class within a section instance, or the same chorus line across
  repeats. Three scopes (global, per instance, per section type) assign letters; the run counts false links, missed links, and pairs that
  print the same letter while being in different tables.
- Got right: The prediction held on all three scopes: global 6 false and 0 missed, per instance 0 false and 8 missed, per section type 0
  and 0. The per-type scheme is the shared-key idea of draft/E4 applied at the right width: things that must agree (chorus repeats)
  share a key, and things that only look alike (verse lines) do not.
- Where/why it failed: Even the correct scope printed the same bare letter for unlinked lines 34 times (verse A and chorus A are
  different rhymes), so a plain ABAB display still invites a reader to link them; per-instance reset made it worse at 42.
- Fix: Key the rhyme table by section type for repeating sections and by section instance otherwise, and print letters qualified by that
  scope (vA, cA) or restart the alphabet visibly per section so a shared letter never implies a link across scopes.
- Why this fix: The scope decides which lines can be linked and the display decides which lines a reader thinks are linked; the run
  shows the first fixed with 0 errors while the second still produced 34 look-alike pairs.
- Rule of thumb: Give a shared key the width of what must agree, not wider: one global rhyme table made 6 false cross-section links,
  per-section reset lost 8 chorus-repeat links, and a per-section-type table made 0 of each; then label letters by scope.
- Provenance (verified/assumed): Verified first-hand by running the shipped sandbox (RESULT: PASS); one hand-built 16-line song with
  rhyme classes set by hand, not real lyrics or a phonetic matcher, and only the draft/E4 shared-key principle (not its game code) was used.
- Composed: draft/E4, sandbox-lyrical-composition/E7
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__rhyme-letter-scope-per-section-type-keeps-chorus-repeats-linked-without-cross-verse-false-links.py
- Prediction: Global table has false links and no missed links; per-instance reset has no false links but misses the chorus-repeat links;
  per-section-type scope has 0 false and 0 missed.
- Observed: RESULT: PASS global table false links 6 (missed 0); per-instance reset missed 8 chorus links and 42 printed look-alikes;
  per-section-type scope 0 false / 0 missed (look-alikes 34).
- Scenarios: 1) one global table, built to BREAK on the verse-2 line sharing the chorus sound; 2) reset per section instance, built to
  BREAK chorus-repeat links; 3) scope per section type; 4) printed-letter look-alikes for all three
- Link: brain train auto run 2 pass 2 (edge); session_01Hecxxt7Wfrejc8A3YVX1ht

## E12 — torn read of rng state words lands on no real state and a one bit buffer flip fixes it
- Date: 2026-10-15
- Project: Pappydapimp69/Zanegpt
- Tags: [determinism][state][concurrency][sandbox]
- What: Applied the Gray-code torn-read kernel to saving a seeded PRNG's state words while the simulation keeps stepping. Copying sfc32's
  four words one at a time can mix old and new words; across 8 seeds that gave 112 distinct torn snapshots, none equal to any real state
  in the next 2000 steps, and all 112 produced a roll stream matching neither the old nor the new one.
- Why built: Train kernel pass on the unapplied GRAY-CODES kernel. The seeded-rng kernel and sandbox-seeded-rng-state-words/E1 say to
  save the raw state words, but neither asks what happens when that copy races the generator, which is the multi-bit torn read the
  Gray kernel is about.
- Design: Python stdlib, no RNG beyond sfc32 itself. Scenario 1 re-checks the kernel exhaustively (every transition, every old-or-new mix
  of changing bits, decoded to a count). Scenario 2 steps sfc32 500 times per seed, then forms every old-or-new mix of the four words,
  checks it against the next 2000 real states and compares 20 rolls. Scenario 3 is a double buffer whose active slot is a 1-bit index
  flipped after the inactive buffer is written. Scenario 4 compares a binary and a Gray 2-bit index for a 4-slot ring.
- Got right: The kernel reproduced exactly: binary worst torn error 3, 7, 31, 127 for 3, 4, 6, 8 bits and 0 for Gray; the first-ten
  mod-10 Gray counter wraps with 3 bits and error 6, the middle slice (codes 3 to 12) wraps with 1 bit and error 0. The 1-bit index
  read 0 torn snapshots in 16 reads, and the 4-slot ring index had torn error 1 slot in binary and 0 in Gray.
- Where/why it failed: A word-by-word state copy is the failure the save advice leaves open: every torn snapshot is a state the
  generator never visits, so a save taken during a step silently loads into a different stream. The Gray fix itself does not transfer:
  all four sfc32 words change on every step, so no encoding of the state makes the copy one-bit.
- Fix: Never copy the live state words; have the generator write each new state into the inactive one of two buffers and then flip a
  1-bit index, and have the saver read the index first. With more than two slots, step the slot index in Gray order.
- Why this fix: The Gray property needs exactly one changing bit per step; that cannot be had for the state, but it can for the pointer
  to the state, and a 1-bit pointer read old or new always names a complete buffer. Scenario 3 is correct by construction given one write
  per read, so the evidence is scenarios 2 and 4.
- Rule of thumb: A save that copies PRNG state words while the sim steps can load a state the generator never visits (112 of 112 torn
  snapshots off-stream); put the state in a double buffer and flip a 1-bit index, using a Gray-coded index for more than two slots.
- Provenance (verified/assumed): Verified first-hand by running the shipped sandbox (RESULT: PASS); concurrency is modelled as every
  old-or-new word mix, not real threads, and memory ordering and multiple writes during one read were not tested.
- Composed: ideas:GRAY-CODES/asynchronous-counters, sandbox-seeded-rng-state-words/E1, ideas:SYSTEM/determinism/seeded-rng
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__torn-read-of-rng-state-words-lands-on-no-real-state-and-a-one-bit-buffer-flip-fixes-it.py
- Prediction: Kernel numbers reproduce (binary 3/7/31/127, Gray 0, mod-10 wrap error 6 fixed by the middle slice); most torn 4-word
  snapshots are not real states and diverge from both streams; a 1-bit index gives 0 torn reads; a binary 4-slot ring index can point
  at a slot that is neither old nor new.
- Observed: RESULT: PASS kernel reproduced (binary worst 3/7/31/127, gray 0, mod10 slice fixes wrap 6->0); 112 torn sfc32 snapshots, 0
  real, 112 diverge; 1-bit double-buffer index 0 torn; 4-slot ring index needs gray (binary err 1).
- Scenarios: 1) Gray kernel re-check over widths 3, 4, 6, 8 and the mod-10 slices; 2) word-by-word sfc32 state copy racing one step,
  built to BREAK the state-word save; 3) double buffer with a 1-bit index; 4) 4-slot ring index, binary vs Gray
- Link: brain train auto run 2 pass 1 (kernel); session_01Hecxxt7Wfrejc8A3YVX1ht
- Cited-by: 2026-10-15 · projects/local__double-buffered-save-writer-laps-reader.md#E1 · compatible · sandboxes/2026-10-15__double-buffered-rng-save-tears-once-the-writer-laps-the-reader.py · observed RESULT: PASS 6/6; single k1 torn 70/126; double k1 0, k2 1540/3003; ring4 k3 0, k4 13290/53130; seqlock torn 0, retries k1-3 [922, 18561, 134592] · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto loop 2 pass 2 (edge brainwork + zanegpt), 2026-10-15

## E11 — faro shuffle order is the order of 2 and two jokers turn 8 out faros into 52
- Date: 2026-10-15
- Project: Pappydapimp69/Zanegpt
- Tags: [card-magic][permutation][sandbox][exhaustive]
- What: Seeded a CARD-MAGIC domain with the perfect faro shuffle: cut exactly in half and interleave one card at a time. Out-faros keep the
  top card on top and restore a 52-card deck after 8; in-faros move it to second and need 52. The count is the multiplicative order of 2
  mod n-1 (out) or n+1 (in), so it jumps with deck size: two jokers (54 cards) need 52 out-faros, 50 cards need 21.
- Why built: brain train newdomain pass; no faro or riffle knowledge existed (both queries returned 0), and the shuffle family only covers
  Fisher-Yates fairness, not the deterministic shuffles magicians use for memorised-deck and position control.
- Design: Python stdlib, no RNG. A faro function interleaves the two halves in out or in order; restore counts are found by repeating it
  until the deck returns, compared against the order of 2 mod n-1 and n+1 for every even n from 4 to 80; Elmsley's binary control moves
  the top card to position p with in-faro for 1 and out-faro for 0, most significant bit first, checked for all 52 positions.
- Got right: 8 out-faros and 52 in-faros restore 52 cards; the order-of-2 rule matched the simulated count for all 39 even deck sizes from
  4 to 80 with no mismatch; the binary in and out sequence placed the top card exactly at all 52 positions (13 is IIOI).
- Where/why it failed: The common belief that eight perfect shuffles restore a deck is specific to 52 cards and out-faros; adding two
  jokers raises it to 52, and removing two cards raises it to 21, because the count depends on number theory of n-1, not on deck size.
- Fix: Before relying on a faro stack, compute the restore count for the exact deck in hand (order of 2 mod n-1 for out, n+1 for in), and
  remove jokers or extra cards when an eight-shuffle cycle is needed.
- Why this fix: Card i of an out-faro moves to 2i mod n-1, so the cycle length is set by the order of 2 in that modulus; a single card
  added or removed changes the modulus and can change the cycle by a factor of six or more.
- Rule of thumb: Eight perfect out-faros restore exactly a 52-card deck; for any other even size use the order of 2 mod n-1 (54 cards need
  52, 50 need 21), and to send the top card to position p do in-faros for the 1 bits of p and out-faros for the 0 bits.
- Provenance (verified/assumed): Verified first-hand by running the shipped sandbox (RESULT: PASS); perfect cuts and interleaves are
  modelled, while the hand skill to perform a perfect faro was not tested.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__faro-shuffle-order-is-the-order-of-2-and-two-jokers-turn-8-out-faros-into-52.py
- Prediction: 52 cards restore after 8 out-faros and 52 in-faros; 54 cards need 52 out-faros and 50 need 21; the order-of-2 rule matches
  every even size simulated; the binary control reaches all 52 positions.
- Observed: RESULT: PASS 52 cards restore after 8 out-faros vs 52 in-faros; out = ord of 2 mod n-1 and in = ord of 2 mod n+1 for all even n
  4..80; two jokers (54) need 52 out-faros; binary I/O control places the top card at all 52 positions.
- Scenarios: 1) 52-card out and in restore counts; 2) order-of-2 rule over every even size 4 to 80; 3) 50 and 54 cards, built to BREAK
  the eight-shuffle belief; 4) binary in and out control to every position
- Link: brain train auto pass 6 (newdomain); session_01Hecxxt7Wfrejc8A3YVX1ht
- Cited-by: 2026-10-15 · projects/pappydapimp69__zanegpt.md#E14 · compatible · sandboxes/2026-10-15__generator-parity-caps-reachable-orderings-for-bell-touches-and-faro-shuffles.py · observed RESULT: PASS bells: minimus 24/24, doubles 40/120, minor plain 60/720; bob and plain lead ends even so plain+bob reach 360/720, single (odd) reaches 720; faros: decks whose out and in are both even [8, 16, 24] never reach an odd ordering,… · brain train auto run 2 pass 5 (gap); session_01Hecxxt7Wfrejc8A3YVX1ht
- Cited-by: 2026-10-15 · projects/local__one-faro-slip-only-disturbs-cards-below-it.md#E1 · compatible · sandboxes/2026-10-15__one-faro-slip-only-disturbs-cards-below-it.py · observed RESULT: FAIL one slip leaves 50.9% of cards home after the 8-faro restore; Elmsley survives 81.1% (by target band 93%, 86%, 79%, 73%); late double drops 95.4% home. · https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-15 · projects/pappydapimp69__demo-disc.md#E9 · compatible · sandboxes/2026-10-15__elmsley-binary-is-also-shortest.py · observed RESULT: PASS correct and shortest at every position for n = 8, 16, 32, 52, 54; worst case back to the top 3, 4, 5, 6, 6 faros. · Demo-disc commit "Add Faro: the ad is a find-the-ace casino, the game is a perfect-shuffle puzzle"; session_011p52L2CkFXcsYRwjDu6tG9
- Cited-by: 2026-10-17 · projects/pappydapimp69__demo-disc.md#E39 · compatible · sandboxes/2026-10-17__faro-two-card-goals-mostly-unreachable.py · observed RESULT: PASS two-card faro goals: 16 cards reach only 32/240 joint positions, 52 cards 2600/2652; top and bottom always mirror (sum n-1). The prediction was refuted for power-of-two decks. · games/faro/game.js planMulti; session_011p52L2CkFXcsYRwjDu6tG9

## E10 — tuning circle closure is blind to octave stretch and even tempering smears one bad fifth
- Date: 2026-10-15
- Project: Pappydapimp69/Zanegpt
- Tags: [tuning-systems][closure][sandbox][error]
- What: Treated a 12-note circle of fifths as a closed traverse (misclosure = sum of the twelve fifths minus seven octaves) and checked
  whether the surveying closure lessons of brainwork/E184 carry over: a closed circle can still be uniformly wrong, and spreading the
  misclosure evenly smears one badly tuned fifth onto all the good ones. Also re-ran every number in the Pythagorean comma kernel.
- Why built: Train gap pass; the pythagorean-comma kernel had no memory entry built on it, and tempering a circle is the same operation as
  a compass adjustment (spread a closure error over the legs), so the surveying kernel's two failure modes were a direct prediction.
- Design: Python stdlib with Fraction and log2, no RNG. Scenario 1 recomputes the comma, the Pythagorean and quarter-comma meantone
  wolves, the 12-TET third error and the closure error of n stacked pure fifths for n up to 59. Scenario 2 is a stretched tuning with
  every fifth at 700.7 and the octave at 1201.2. Scenario 3 has eleven fifths at 700 and one at 710, then spreads the 10-cent misclosure
  evenly, and compares with locating the outlier against the median and re-tuning it.
- Got right: The kernel's numbers all reproduced (comma 23.46, wolves 678.49 and 737.64, meantone fifth 696.58, ET third 13.69 sharp,
  and n=53 the only stack under 60 closing within 5 cents at 3.62). The stretched circle closed with 0.000 misclosure while its octave was
  1.2 cents off and every fifth 0.7 off, and the median check found the bad fifth (index 5) and closed the circle after re-tuning it.
- Where/why it failed: Even tempering was the failure the surveying kernel predicts: exact fifths went from 11 of 12 to 0 of 12, the worst
  fifth only improved from 10.00 to 9.17 cents, and major thirds off 12-TET went from 4 of 12 (max 10.00) to 12 of 12 (max 6.67), so
  one bad interval spread into every key.
- Fix: Read each fifth's deviation from its target first; when one stands out against the median, re-tune that fifth and only spread
  what is left as true temperament. Check the octave against a reference separately, because closure cannot see a uniform stretch.
- Why this fix: A circle is a sum, and a sum cannot tell one large error from many small ones or see a change that scales every step
  together; per-interval residuals can, exactly as per-leg checks find the bad leg in a traverse.
- Rule of thumb: A closed circle of fifths says nothing about octave stretch (0.000 cents misclosure with a 1.2-cent stretch), and
  spreading the misclosure evenly turns one 10-cent bad fifth into 12 of 12 wrong thirds; find the outlying fifth before tempering.
- Provenance (verified/assumed): Verified first-hand by running the shipped sandbox (RESULT: PASS); tuning is modelled in cents only, no
  audio was rendered and no real tuning procedure or piano inharmonicity was tested.
- Composed: ideas:TUNING-SYSTEMS/temperament/pythagorean-comma, ideas:SURVEYING/traverse/closure-error-is-blind-to-scale-and-bowditch-smears-blunders, brainwork/E184
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__tuning-circle-closure-is-blind-to-octave-stretch-and-even-tempering-smears-one-bad-fifth.py
- Prediction: Kernel numbers reproduce to two decimals; the stretched circle closes with zero misclosure; evenly spreading a 10-cent blunder
  leaves no exact fifth and moves eleven correct fifths by 0.83 cents each, with every third now off.
- Observed: RESULT: PASS comma 23.46, only n=53 closes within 5 cents (3.62); a stretched circle closes at 0.000 with octaves 1.2 off; even
  tempering of one 10-cent blunder leaves 0/12 exact fifths (was 11/12) and 12/12 thirds off (was 4/12).
- Scenarios: 1) kernel numbers (comma, wolves, ET third, n-fifth closure); 2) stretched octave and fifths, built to BREAK closure as a
  validator; 3) one 10-cent bad fifth spread evenly, built to BREAK even tempering; 3b) locate the outlier by median and re-tune
- Link: brain train auto pass 5 (gap); session_01Hecxxt7Wfrejc8A3YVX1ht

## E9 — seeded rng raw state save round trips and float order breaks lockstep
- Date: 2026-10-15
- Project: Pappydapimp69/Zanegpt
- Tags: [gamedev][state][determinism][testing]
- What: Re-verified the seeded-rng kernel, the split-state-by-determinism-need kernel and the-game-prologue/E1 together in one sfc32 sandbox: saving
  the four raw state words restores the next 100 rolls exactly with no replay, a seed-plus-count load needs 5000 generator calls for the
  same result, two lockstep clients on one seed stay identical over 2000 steps, and per-client ambient rolls diverge at step 0.
- Why built: The seeded-rng kernel was only quoted in prose by the-game-prologue/E1, never declared, so the link and its three claimed
  payoffs (exact saves, replay, lockstep) had not been run together, and the float tell in the split-state kernel had no repro.
- Design: Python stdlib, no RNG and no timing. sfc32 on 32-bit masks; a toy sim drains hp by roll mod 7. Load paths: raw words vs replay
  from seed with a call counter. The float case sums the same movement deltas (ten 0.1 steps plus 1e16 and -1e16) forward and reversed
  with a plain left fold and compares a trigger test at 0.5; the fix keeps the authoritative fact as an integer zone count. State
  hashing compares json.dumps with and without sort_keys on two equal dicts built in different key orders.
- Got right: All five scenarios matched the kernels: raw-state load equal on 100 of 100 rolls with 0 replay calls, lockstep equal, the
  ambient source diverged immediately, the float position came out 0.0 vs 0.9999999999999999 and flipped the trigger, the integer zone
  stayed 10 vs 10, and equal states hashed equal only with sorted keys.
- Where/why it failed: The first float run showed no divergence because Python 3.12's built-in sum() uses compensated summation and
  returned 1.0 for both orders, which hid exactly the order dependence a JavaScript game loop has; the first trigger threshold of 1.0
  was also on the wrong side of both values.
- Fix: Model the game loop's accumulation with functools.reduce(operator.add) rather than sum(), and place the trigger between the two
  observed positions; keep the authoritative zone as integer steps so its value cannot depend on summation order.
- Why this fix: A sandbox that checks float order sensitivity must use the same naive accumulation the real engine uses; a compensated
  sum is a different algorithm and silently proves determinism that the engine does not have.
- Rule of thumb: Save a seeded PRNG's raw state words, keep every authoritative outcome off float accumulators, and hash state with
  sorted keys; when testing float order effects in Python 3.12 or later, accumulate with reduce(operator.add), because sum() is
  compensated and hides the drift.
- Provenance (verified/assumed): Verified first-hand by running the shipped sandbox (RESULT: PASS); the per-client ambient source is a
  deterministic stand-in for two machines' Math.random, and real cross-platform float differences were not run.
- Composed: ideas:SYSTEM/determinism/seeded-rng, ideas:SYSTEM/determinism/split-state-by-determinism-need, the-game-prologue/E1
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__seeded-rng-raw-state-save-round-trips-and-float-order-breaks-lockstep.py
- Prediction: Raw-state load matches all 100 next rolls with 0 replay calls vs 5000 for seed-plus-count; lockstep identical; ambient rolls
  diverge within 10 steps; forward vs reversed float sums of the same deltas differ and flip a threshold; unsorted hashes of equal
  states differ while sorted ones match.
- Observed: RESULT: PASS raw-state load O(1) matches 100/100 rolls vs 5000-call replay; lockstep equal; ambient diverges at step 0; float
  order flips a hit (False/True) while discrete zone holds; sorted-key hash needed (raw False, sorted True).
- Scenarios: 1) raw-state save vs seed-plus-count replay; 2) two lockstep clients on one seed; 3) ambient per-client rolls, built to
  BREAK lockstep; 4) float summation order feeding a trigger, built to BREAK it, plus the integer-zone fix; 5) state hash with and
  without sorted keys
- Link: brain train auto pass 1 (kernel); session_01Hecxxt7Wfrejc8A3YVX1ht

## E8 — rhyme assigner no match sentinel merges orphan lines into a fake rhyme
- Date: 2026-10-15
- Project: Pappydapimp69/Zanegpt
- Tags: [lyrical-composition][rhyme-tooling][testing][state]
- What: The no-winner sentinel bug from combat option audits (sandbox-dbz-combat/E3) reappears in a rhyme-scheme letter assigner
  (sandbox-lyrical-composition/E7): a line whose word has no known rhyme class returns None, and a naive assigner keys letters on that
  None like any class, so every orphan line shares one letter and is reported as rhyming with every other orphan.
- Why built: Train edge pass on the untested strong pair dbz-combat plus lyrical-composition (4 shared tags); E3 claims the sentinel
  turns a nothing-found case into apparent coverage, and the letter assigner has exactly that shape of per-line best-match lookup.
- Design: Python stdlib, deterministic. A six-word rhyme-class table; unknown words map to None. A naive assigner keys letters by class
  including None; a guarded one gives each orphan its own fresh letter. Metrics: share of lines that rhyme with another line, and
  maximum closure distance from sandbox-lyrical-composition/E8. Four stanzas: AABB couplets, all-orphan free verse, ABAC, and
  an orphan-wrapped couplet.
- Got right: The fully rhymed AABB stanza was identical under both assigners, so the bug is invisible on the test case people write
  first; the guarded assigner gave ABCD, ABAC and ABBC with rhymed shares 0.00, 0.50 and 0.50.
- Where/why it failed: The naive assigner turned free verse into AAAA (rhymed share 0.00 to 1.00), ABAC into ABAB (0.50 to 1.00), and
  the orphan-wrapped couplet into ABBA, which also moved closure distance from 1 to 3 and so changed the stanza's apparent emotional
  motion as E8 measures it.
- Fix: Treat the no-match result as its own category: give each orphan line a unique letter that can never be shared, and report an
  orphan count beside the scheme instead of folding it into any rhyme metric.
- Why this fix: The orphan is the key finding of the scan (lines with nothing to rhyme with), so it needs to be visible rather than
  coerced into a class; one None check costs nothing and keeps downstream metrics such as closure distance honest.
- Rule of thumb: In any best-match grouper (rhyme letters, option winners, cluster ids), never let the no-match value act as a group
  key; a None key merges every unmatched item into one fake group, and a fully matched test case will never show it.
- Provenance (verified/assumed): Verified first-hand by running the shipped sandbox (RESULT: PASS); the rhyme table is a six-word toy, so
  real phonetic lookups and their own miss rate were not run.
- Composed: sandbox-dbz-combat/E3, sandbox-lyrical-composition/E7, sandbox-lyrical-composition/E8
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__rhyme-assigner-no-match-sentinel-merges-orphan-lines-into-a-fake-rhyme.py
- Prediction: AABB identical under both assigners; all-orphan free verse reads AAAA with rhymed share 1.00 under the naive assigner and
  ABCD with 0.00 under the guarded one; mixed stanzas inflate rhymed share and can change closure distance.
- Observed: RESULT: PASS no-match sentinel turns free verse ABCD into AAAA (rhymed share 0.00 -> 1.00), ABAC into ABAB (0.50 -> 1.00),
  and an orphan-wrapped couplet ABBC into ABBA (closure 1 -> 3); fully rhymed AABB unaffected.
- Scenarios: 1) AABB couplets; 2) all-orphan free verse, built to BREAK the naive assigner; 3) ABAC with two orphans; 4) orphans
  wrapped around a couplet, checked on closure distance
- Link: brain train auto pass 2 (edge); session_01Hecxxt7Wfrejc8A3YVX1ht
- Audited: 2026-10-16 · modeled · Read the entry and its stored sandbox. The sandbox computes its outputs rather than hard-coding them, but the naive assigner is written to key letters on the None value, so the merge of orphan lines follows from that choice by construction; the run shows the consequence, not that real assigners do this. The guarded fix and metrics (rhymed share, closure distance) are computed correctly, and the scope stays within the Rule of thumb's code-pattern claim, with a free-verse case built to break it. But the cited real assigner (lyrical-composition/E7) and a real phonetic lookup were never run, only a six-word toy table, as the entry admits. Hence modeled, not pass. · brain train auto pass 3 (audit), scheduled run 2026-10-16; session_01BotpwZYRVuevNi8Z2gkH2d

## E7 — sweep assumptions before filing a sim lesson
- Date: 2026-10-15
- Project: Pappydapimp69/Zanegpt
- Tags: [simulation][testing][method]
- What: Two toy sandboxes were built for short-form video training: a loop/rewatch
  retention model and a heavy-tailed views model asking how many posts it takes to
  judge a hit-or-miss format. Both ran on invented parameters (swipe rate, hazard,
  lognormal spread), not platform data.
- Why built: To give Brain quantified kernels on retention and format testing
  before any real channel analytics existed.
- Design: Loop model: 35% swipe in 2 s, constant 6%/s hazard, finishers rewatch
  with prob r. Hits model: lognormal views, same median, the weird format with a
  wider sigma; 3,000-4,000 simulated channels per cell, count how often the better
  format fails to show more 30x-median hits after N posts.
- Got right: The hits sweep across 6 sigma settings showed one claim that survives
  every setting: at 10 posts the truly better hit-or-miss format fails to show more
  hits 47-93% of the time.
- Where/why it failed: The loop result (loops add ~7 pts APV at 15 s but ~2 at 30 s)
  followed arithmetically from the assumed constant hazard, so it restated the
  inputs rather than discovering anything. The first hits run also gave a single
  "30-60 posts needed" figure that the sweep showed swings from 7% to 63% wrong at
  60 posts depending on the guessed spread.
- Fix: Dropped the loop sandbox, re-ran the hits model as a sweep over 6 spread
  settings, and kept only the claim that held in all of them (10 posts cannot judge
  the format); the post count needed was not kept as a number.
- Why this fix: A sandbox built on guessed parameters is only evidence for claims
  that hold across the plausible parameter range; a single-setting number inherits
  the guess and would be filed as if it were measured.
- Rule of thumb: Before filing a sandbox result that rests on guessed parameters,
  sweep each guess over its plausible range and file only the claim that holds in
  every setting; if the result is implied by the model's own assumption, it is not
  a lesson.
- Provenance (verified/assumed): verified first-hand in this session by running both
  sandboxes and the 6-setting sweep; the lognormal view model itself is an assumption.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__sweep-assumptions-before-filing-a-sim-lesson.py
- Prediction: at 10 posts the better weird format would fail to show more hits at
  least 30% of the time in every one of the 6 spread settings.
- Observed: RESULT: PASS at 10 posts the better hit-or-miss format fails to show more
  hits 47-93% of the time across 6 spread settings; at 60 posts the range was 7-63%.
- Scenarios: 1) sigma 1.0 vs 1.4; 2) 1.0 vs 1.8; 3) 1.4 vs 1.8; 4) 1.4 vs 2.2;
  5) 1.8 vs 2.2; 6) 1.8 vs 2.6 (widest gap, built to break the claim; still 47%).
- Link: https://claude.ai/code/session_01TQvFfNiYzpWZZDPgWeMoBC
- Audited: 2026-10-15 · modeled · Read the entry and its stored sandbox. The sandbox computes its result: a seeded Monte Carlo of lognormal view counts, 3000 channels per cell, counting how often the wider-spread format shows no more 30x-median hits than the narrow one after N posts, so the answer is not built in, and the 47-93% range at 10 posts is what the run produces. Coverage is narrower than the rule of thumb states. The rule says to sweep each guessed parameter over its plausible range, but only sigma was swept; the 30x hit threshold, the shared median, and the hit-count definition were fixed. Ties are counted as failures (hb <= ha), and at these sigmas a 30x hit is rare, so many channels show zero hits for both formats at 10 posts; the high end of the range is therefore driven by zero-versus-zero ties, not by the narrow format winning. The claim concerns real short-form video platforms but was only tested against an invented lognormal model with no platform data, so the verdict is modeled, not pass. · brain train auto loop 1 pass 3 audit; session_01Kx9Pq1H5qpcbvZJ9u2DPKR

## E6 — sms backup voice mining
- Date: 2026-10-02
- Project: Pappydapimp69/Zanegpt
- Tags: [ai][data-integrity][privacy]
- What: Mining a person's texting voice and personality profile from an SMS Backup & Restore
  XML export (27,689 records, 17 MB) to feed a persona skill (ZaneGPT).
- Why built: The persona needed the user's real voice, not a guessed one, and a multi-year
  phone backup is the densest first-person corpus the user had on hand.
- Design: Stream the file with ElementTree iterparse, keep only the owner's own outbound
  messages (sms type="2"; mms msg_box="2" with text taken from part ct="text/plain"), then
  compute style rates (capitalization, terminal punctuation, laugh tokens, emoji, profanity),
  top trigrams and an hour histogram, and read a random sample of 220 longer texts for tone.
- Got right: Sent-only filtering kept every other person's words, names and numbers out of the
  profile, and trigram counts surfaced real signature phrasing ("I was like", "blah blah blah")
  that a skim would have missed.
- Where/why it failed: Two silent distortions. The epoch `date` field is UTC, and a cloud
  container's local zone is UTC too, so the first hour histogram was shifted seven hours and
  wrongly labelled the user a night owl. Separately, 92% of texts end in a trailing space and
  98% start capitalized, which reads as personal style but is the phone keyboard's
  auto-space/auto-capitalize behaviour leaking into the corpus.
- Fix: Derive the UTC offset by comparing `date` against the export's `readable_date` on one
  record (here UTC-7) and bucket hours in that zone; treat any near-100% formatting rate as a
  device artifact and exclude it from the voice rules unless it differs from the keyboard default.
- Why this fix: readable_date was rendered on the phone in its own zone, so it is ground truth for
  the offset without guessing the user's location; and a persona that copies keyboard artifacts
  sounds robotic while missing the habits the person actually chooses.
- Rule of thumb: When profiling a person from exported messages, keep only their outbound rows,
  re-zone timestamps using the export's own human-readable date, and discard near-universal
  formatting rates as device artifacts before calling anything a personal habit.
- Provenance (verified/assumed): verified first-hand in this session: counts, the sent filter,
  and the UTC-7 offset from record one. The keyboard origin of the trailing space is an inference
  from its near-universal rate.
- Composed: N/A
- Link: session https://claude.ai/code/session_01NfcX6Rb6Fjz7TMmo21Zgoc

## E5 — two load paths one takes effect now
- Date: 2026-09-14
- Project: Pappydapimp69/Zanegpt
- Tags: [tooling][process][agent]
- What: I told the operator that an installed Claude Code plugin could not take effect until the next session, because plugins load at startup. That was wrong for the other install path: a skill dropped into the personal skills directory was live in the same session, invocable on the next turn.
- Why built: Installing the ZaneGPT behaviour so the running agent could actually use it.
- Design: Two independent mechanisms deliver the same skill — a marketplace plugin (`claude plugin install`, resolved at session start) and a skills directory (`~/.claude/skills/<name>/SKILL.md`, scanned per turn). Same content, different load clock.
- Got right: The plugin install itself was correct and idempotent, and project-scope settings do make a fresh clone carry the plugin from its first turn.
- Where/why it failed: I generalised one path's timing to the whole capability and stated it as a mechanism, confidently, without testing the other path. The operator was told to wait for a restart that was never needed. The claim was not a guess presented as a guess — it was delivered as how the system works.
- Fix: Copy the SKILL.md into the personal skills dir as well; it loaded immediately and the skill was invocable in the same session. Then verify by invoking, not by reasoning.
- Why this fix: The two paths are not redundant, they are differently-timed. Choosing between them is a decision about WHEN, and that only becomes visible once you stop treating "installed" as one state.
- Rule of thumb: When a capability has two install paths, their load clocks are a property to be tested per path, not inferred once — and an agent's confident account of its own runtime is exactly the claim least likely to have been checked.
- Provenance (verified/assumed): Verified firsthand. Stated the restart claim; later copied SKILL.md to `~/.claude/skills/zanegpt/` and invoked the skill successfully in the same session, disproving my own statement. Project-scope settings verified by reading the generated `.claude/settings.json`; their effect on a fresh clone is assumed, not yet observed.
- Composed: N/A
- Link: session 2026-09-14, branch claude/brain-install-link-bj2e8t
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E41 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E4 — vacuous test under a conjunctive rule
- Date: 2026-09-09
- Project: Pappydapimp69/Zanegpt
- Tags: [testing][gamedesign][verification][method]
- What: An invariant suite written to protect a conjunctive game rule (hazard fires iff `lit AND heat >= GATE`), plus a mutation audit that breaks each invariant on purpose and requires a named test to go red.
- Why built: The build's whole premise is that the player must be able to form and refute a hypothesis about a hidden rule, so the rule's terms and their visible signal are the load-bearing parts — they were written and tested before any second mechanic.
- Design: Integer-only authoritative state behind a serializer that raises; per-tick replay fingerprints; ambient heat channel hard-banded at 6 strictly inside a gate of 10 with the player-driven channel uncapped; one avatar glyph computed from the same `is_lit`/`heat` functions the rule calls.
- Got right: Running the mutation audit at all, and treating a mutation the script could not APPLY as exit code 3 rather than a silent pass. Both weak assertions below were invisible in a fully green 14-test suite and took one mutation run to surface.
- Where/why it failed: TWO assertions were vacuous, in different ways, and neither could be seen by reading the green suite. (1) The ramp test asserted `first.armed_ticks > core.ARM_TICKS` — an assertion written against the constant it checks, which holds for every value including zero, so mutating `ARM_TICKS = 3` to `0` (removing the player's entire warning window) left the suite green. (2) The band test — the one guarding `AMBIENT_CAP < HEAT_GATE`, the tuning property the whole design rests on — exercised a run in the DARK. Under a conjunction, the other term being false makes the assertion true for every possible cap; it would have passed with the ambient channel set to 10x the gate. The second is the more dangerous shape: it does not restate the implementation, it looks like a genuine end-to-end property test, and it names the right invariant in its own docstring.
- Fix: (1) Assert the outer effect against a literal floor — count the ticks on which the ARMED glyph was actually visible before the strike, require >= 3. (2) Move the band test to where the band binds: construct a state ON a lit cell with the firsthand channel pinned to zero and the ambient channel saturated, assert the rule still does not fire, plus a separate long-run check that the cap holds over time. Then re-run every mutation to prove each new assertion actually goes red.
- Why this fix: A test of one term of a conjunction must be sited where the other terms are TRUE, or the conjunction itself supplies the pass. This is the test-side mirror of the display-side rule that drawing one term of a conjunctive rule is worse than drawing nothing — in both cases the conjunction masks the term you meant to exercise, and in both cases everything looks correct.
- Rule of thumb: When testing one term of a conjunctive rule, pin every OTHER term true first — otherwise the conjunction, not your code, is what makes the assertion pass, and the test stays green for every value of the parameter it claims to protect. A vacuous green is indistinguishable from a real one by reading, so the only way to find it is to mutate the constant and require a named test to fail; and count a mutation the harness failed to apply as a harness error, never as a catch.
- Provenance (verified/assumed): Verified first-hand — 5 mutations run against a green 14-test suite; `ARM_TICKS 3→0` and `AMBIENT_CAP 6→12` both initially SURVIVED, with the band mutation caught only by the literal-pin test and not by the property test that existed to protect it; after the two rewrites, all 5 mutations are caught by the named tests and the suite is 15/15 green. Open, and outside what this entry claims: whether the same vacuity shape appears in the existing suites of the other builds in this canon.
- Composed: opticon/E41, dog/E101, dog/E50
- Link: session https://claude.ai/code/session_01HEhYc3p6SBh1KP1VhxmjPs — commit f570d34 (hidden-rule-hazard)
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E22 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E3 — injected pointer hardcodes default path
- Date: 2026-09-09
- Project: Pappydapimp69/Zanegpt
- Tags: [tooling][documentation][process][architecture]
- What: The `brain link` pointer block that is injected into a linked project's CLAUDE.md hardcodes `$HOME/.brain/Brain/bin/brain` as the "if `brain` is not found" fallback.
- Why built: The pointer exists so any agent opening a linked project can invoke the CLI without being told a path, including when PATH is not set up in that shell.
- Design: `POINTER` is a module-level string constant in `bin/brain`; `_inject_pointer` writes it verbatim between HTML comment markers stamped with `POINTER_VERSION`, so a pointer change propagates on the next `link` or `sync`.
- Got right: The versioned marker block is the correct mechanism — it makes a stale pointer detectable without diffing prose, and it re-propagates automatically. The generated-doc-instead-of-hand-written-doc choice is right.
- Where/why it failed: The CLI explicitly supports a non-default cache — `brain link --cache DIR`, the `BRAIN_CACHE` env var, and a per-project `cache` recorded in `.brain/config.json`, with the CLI's own help recommending `~/Documents/.brain` when the home root is sandbox-blocked. `_resolve_cache()` honours all three. But `POINTER` is a static string interpolated with nothing, so every project linked with a non-default cache receives a CLAUDE.md instructing the agent to fall back to a path that does not exist on that machine. The failure is invisible at link time: the pointer is generated, correct-looking, and only wrong on the branch nobody takes until PATH is broken — the exact moment the fallback is the last resort. The tool already knows the right answer (it just wrote it into `config.json`) and declines to use it.
- Fix: Interpolate the resolved cache into the pointer at injection time — `POINTER.format(cache=CACHE)` — so the fallback line names the path this project actually resolved, and bump `POINTER_VERSION` so existing linked projects get the corrected block on their next `link` or `sync`.
- Why this fix: Generating the fallback from the same resolution the CLI performs makes the two structurally impossible to drift; documenting the caveat instead ("note: if you used --cache, adjust this path") leaves a human step in the one path that only executes when tooling is already broken. Naming a cost is not reducing it.
- Rule of thumb: When a tool generates documentation that tells a reader how to invoke it, generate every path in that documentation from the tool's own resolved configuration — never from the default the tool merely usually has. A hardcoded default inside generated output is a silent lie for exactly the configurations the tool advertises as supported, and it fails on the fallback branch, where there is no working alternative left to mask it.
- Provenance (verified/assumed): Verified first-hand — read `POINTER` (a static tuple of string literals, no format placeholders) and its single call site, which concatenates it with no substitution; confirmed `_resolve_cache()` reads `--cache` / `BRAIN_CACHE` / `.brain/config.json`; confirmed the injected CLAUDE.md in this repo carries the literal `$HOME/.brain/Brain/bin/brain`. Open, and outside what this entry claims: whether any project in the wild is currently linked with a non-default cache.
- Composed: N/A
- Link: session https://claude.ai/code/session_01HEhYc3p6SBh1KP1VhxmjPs
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E49 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E2 — missing control resource read as empty
- Date: 2026-09-12
- Project: Pappydapimp69/Zanegpt
- Tags: [security][state][tooling]
- What: The ZaneGPT runtime loaded its defensive protocols, hacker-flag rules and post-turn-5 behavior through a reader that returns `""` for a file that does not exist, so a runtime with NO control resources on disk booted and ran as if it had them.
- Why built: `ZaneStorage.read_text()` was written as a convenience so an optional resource could be absent without special-casing every call site: `return path.read_text() if path.exists() else ""`.
- Design: `load_resources()` calls that reader for six files under `knowledge/` and `persistence/` and hands the dict to `build_runtime_context()`, which interpolates them into the prompt block the LLM sees and then states the control order (Defensive Protocols → Hacker Flag → Trait Engines → Post-Turn-5).
- Got right: the layered control order and the decision to build the context block mechanically rather than have the model narrate its own state — that part is what made the gap visible once the resources were named in the block.
- Where/why it failed: the repo's files sat flat at the root while the code (and README) expected `knowledge/`, `persistence/` and `runtime/` subdirectories, so every control resource resolved to a missing path. Absent and empty are indistinguishable to the caller: the context block still announced the control order, so the prompt asserted protocols were in force while their text was the empty string. It failed OPEN and silently — the only reason it surfaced at all is that `load_session()` read its schema WITHOUT the same fallback and crashed with `FileNotFoundError`. Had that one call been equally forgiving, the runtime would have started clean with no protocol at all.
- Fix: `read_text()` records every missing path on `storage.missing` before returning `""`; `main()` prints a stderr WARNING naming them; `build_runtime_context()` gained a `CONTROL RESOURCES ABSENT: ...` line plus an explicit instruction not to act as though an absent resource is in force; `load_session()` raises a `FileNotFoundError` naming the expected layout. The files were moved into the `persistence/` and `runtime/` layout the README already documented.
- Why this fix: the absent resources could not simply be created — two `knowledge/` files genuinely do not exist yet and fabricating canonical behavior is exactly what this repo's README forbids. So the correct move was to make absence representable and visible at every layer that consumes it, including inside the prompt itself, rather than to paper over it with a default. A default value for a control resource is a silent grant of permission.
- Rule of thumb: a missing security or control resource must never share a representation with an empty one — `exists() ? read : ""` is a fail-open default. Track absence explicitly and propagate it into every surface that claims the control is active, the model's own context block included.
- Provenance (verified/assumed): verified first-hand — `python3 zanegpt_runtime.py --repo .` crashed on the session-state schema before the fix; after the layout move and patch it boots and prints `CONTROL RESOURCES ABSENT: knowledge/user_behavior_database.md, knowledge/user_behavior_runtime.md` in the rendered context block on a real turn. The counterfactual (that it would have run protocol-less had `load_session` been equally forgiving) is read from the code, not executed.
- Composed: N/A
- Link: session 2026-09-12, Pappydapimp69/Zanegpt branch claude/brain-install-ylaun7

## E1 — home anchored cache in remote container
- Date: 2026-09-09
- Project: Pappydapimp69/Zanegpt
- Tags: [tooling][process][deployment][verification]
- What: Bootstrapping the `brain` CLI inside a Claude Code remote container, where the session's repo checkouts live under `/home/user` but the process `$HOME` is `/root`.
- Why built: The container had the five node repos cloned but no CLI on PATH; `brain install` + `brain link` had to be run from scratch.
- Design: Follow `install.sh`'s documented layout — clone the node repos into the per-machine cache, then run `python3 bin/brain install` from the cache copy so the PATH symlink points at the cache, not at a feature-branch checkout.
- Got right: Installing from the cache copy rather than the working checkout, so the PATH entry does not point into a branch that later moves. Reading `_resolve_cache()` before creating anything, which is what made the failure legible in one step instead of several.
- Where/why it failed: I inferred the cache root from the session's primary working directory (`/home/user`) and cloned all four node repos into `/home/user/.brain`. `brain install` then reported success — `✓ installed → /root/.local/bin/brain` — and `brain status` still said "not linked". The symlink was created correctly and the clones were intact; nothing errored. The CLI resolves its cache as `os.path.expanduser("~/.brain")`, which is `/root/.brain` in that container, so it was reading an empty path while a complete, correct cache sat 4 directories away. The success message names the symlink it wrote, not the cache it will read, so the two halves of the install can disagree silently.
- Fix: `mv /home/user/.brain /root/.brain` and re-run `python3 bin/brain install` from the moved copy, so the PATH symlink resolves to `/root/.brain/Brain/bin/brain`.
- Why this fix: The alternative — keeping the cache at `/home/user/.brain` and passing `--cache` at link time — works for the linked project but leaves the injected CLAUDE.md pointer's `$HOME/.brain/...` fallback pointing at nothing (see the sibling proposal). Moving the cache to the real `$HOME` makes the tool's own default correct and needs no per-project flag.
- Rule of thumb: In an ephemeral/remote container, `$HOME` is not the parent of the repo checkouts and is not the working directory — echo `$HOME` before creating any `~`-anchored cache, config or credential store. A tool whose install step reports where it wrote the binary while silently resolving its data root elsewhere can report success with the two halves pointing at different filesystems; verify with the tool's own status command, not the install message.
- Provenance (verified/assumed): Verified first-hand — `HOME=/root` while the primary working directory was `/home/user`; the misplaced cache produced `✗ not linked` with an intact install; the move + reinstall produced `✓ linked` and a working `brain query`. The claim that other `~`-anchored tools behave the same way in this environment is a generalization, not separately tested.
- Composed: N/A
- Link: session https://claude.ai/code/session_01HEhYc3p6SBh1KP1VhxmjPs

