# pappydapimp69/seven — lessons

Project: pappydapimp69/seven. Newest first.

---

## E109 — cricket chirp rate is an honest night clock that falls silent when it gets cold
- Date: 2026-10-15
- Project: Pappydapimp69/seven
- Tags: [audio][gamedesign][simulation]
- What: Gap with no records (brain query crickets: 0): Dolbear's law (temperature from cricket chirp rate)
  as a sound cue SEVEN could derive from a public fact, air temperature, which fits its rule that
  sound is built only from the percept and public facts.
- Why built: SEVEN's soundscape needs night cues that carry real information without leaking hidden state; a
  cricket bed that follows the night's cooling would tell the player how cold and how late it is,
  honestly.
- Design: Exact arithmetic. Dolbear 1897: T(F) = 50 + (N - 40)/4 and the 15-second shortcut T = N15 + 40; the
  Celsius form T = 10 + (N - 40)/7 against the exact conversion. An assumed night cooling from 72 F
  toward 48 F with a 4-hour time constant; crickets silent below 55 F (assumed).
- Got right: The 15-second shortcut is algebraically identical to Dolbear's law. Over the assumed night the rate
  falls from 128 to about 60 chirps per minute, then the crickets stop at hour 5, so both the slowing
  and the silence mark the night's progress; one chirp counted in 15 seconds is 1 F.
- Where/why it failed: I predicted the Celsius shortcut would be within 0.6 C of exact; it is off by up to 0.63 C at 200
  chirps per minute because its divisor is 7, not the exact 7.2. The cooling curve and the 55 F
  silence threshold are assumptions, and real chirp rates vary by species.
- Fix: Drive a cricket bed's chirp rate from the sim's air temperature with Dolbear's law and silence it
  below a threshold; use the Fahrenheit form or divisor 7.2 if the game reasons in Celsius.
- Why this fix: It gives the player a real, learnable clock of the night built from a public fact, and the moment
  the crickets stop is a natural cue that the cold part of the night has begun, without any UI.
- Rule of thumb: Cricket chirp rate is an honest night clock: by Dolbear's law (T = 50 + (N - 40)/4 F) an assumed
  cooling night slows the bed from 128 to 60 chirps a minute before it falls silent; drive it from air
  temperature, one chirp per 15 s is 1 F.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry for the arithmetic; Dolbear's law is cited from the
  standard 1897 formula; the night curve and silence threshold are assumed.
- Composed: N/A
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__cricket-chirp-rate-is-an-honest-night-clock-that-falls-silent-when-it-gets-cold.py
- Prediction: shortcut identical to Dolbear; Celsius form under 0.6 C off; rate about 128 falling to about 60 per
  minute; silence 4 to 6 h after dusk; 15 s count resolves 1 F.
- Observed: RESULT: FAIL 4/5; shortcut exact True; Celsius error 0.63 C; dusk rate 128/min, last rate before
  silence 60/min; crickets stop at hour 5.0; 15 s count resolves +-1 F
- Scenarios: 1) shortcut vs formula over 40-200 chirps a minute; 2) Celsius form (built to BREAK the 'shortcuts
  are exact' reading: 0.63 C off); 3) a 10-hour cooling night; 4) the silence threshold
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 5 pass 5 (gap: crickets), 2026-10-15

## E108 — a dying torch dims for a third of its life if incandescent and cuts out if led
- Date: 2026-10-15
- Project: Pappydapimp69/seven
- Tags: [gamedesign][rendering][survival]
- What: Gap with no records (brain query flashlight and headlamp: 0): what a real torch does as its
  batteries die, compared with the linear battery bar horror games use, for an incandescent bulb and a
  regulated LED.
- Why built: A dying light is a classic dread mechanic; whether it should dim gradually or cut out depends on the
  light, and a linear bar matches neither, which matters for how SEVEN's night tools feel.
- Design: Exact arithmetic over runtime. Incandescent flux scaled as (V / V_rated)^3.4 (standard lamp rule);
  regulated LED at full output until cells drop below a 1.0 V per cell driver cut-off. Assumed
  alkaline AA discharge: 1.50 to 1.20 V over the first 70 percent of runtime, then to 0.90 V; two
  cells, bulb rated at 1.2 V per cell.
- Got right: The incandescent torch starts 2.14 times its rated brightness, falls through rated at 70 percent of
  runtime and keeps dimming for the rest; the LED stays at full output until 90 percent of runtime,
  then cuts out in one step. A linear bar matches neither curve.
- Where/why it failed: I predicted the incandescent would fall under 25 percent of rated before the cells were spent; it
  ended at 38 percent at 0.9 V per cell, so at the usual cut-off a dying incandescent is dim, not
  dark. The discharge curve is a piecewise stand-in, not a datasheet.
- Fix: Pick the light's character on purpose: an old incandescent torch should be bright at first and dim
  over the last third of its life without ever going fully dark; an LED torch should give no warning
  and then fail at once. Show remaining charge in the light itself, not a linear bar.
- Why this fix: Players read brightness, not a bar; a gradual dim gives dread and time to act, an LED cliff gives a
  sudden blackout, and each is a different horror beat.
- Rule of thumb: A dying incandescent torch starts about 2x rated, passes rated at 70 percent of runtime and ends dim
  (38 percent), never dark; a regulated LED holds full output to about 90 percent then cuts out;
  neither looks like a linear battery bar.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry; the 3.4 flux exponent is the standard lamp rule of
  thumb and the discharge curve, rating and driver cut-off are assumed.
- Composed: N/A
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__a-dying-torch-dims-for-a-third-of-its-life-if-incandescent-and-cuts-out-if-led.py
- Prediction: incandescent over 2x rated at start, rated at about 70 percent of runtime, under 25 percent before
  the cells reach 0.9 V; LED full to about 90 percent then off.
- Observed: RESULT: FAIL 3/4; incandescent starts 2.14x rated, passes rated at 0.70 of runtime, under 25% at
  None (ends at 0.38x); LED full until 0.90 then off
- Scenarios: 1) incandescent over the discharge; 2) regulated LED over the same; 3) linear bar; 4) built to BREAK
  the 'dims to dark' reading: end of discharge at 0.9 V (still 38 percent)
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 4 pass 5 (gap: torch battery), 2026-10-15

## E107 — sevens linear fog keeps mid range clear and pops objects in at the edge
- Date: 2026-10-15
- Project: Pappydapimp69/seven
- Tags: [rendering][perception][wayfinding]
- What: Gap (brain query koschmieder: 0): SEVEN's raycaster fogs linearly with distance (fog = dist / 22
  cells, src/view.js at seven-1.18.0, read not modified), while real air attenuates contrast
  exponentially; compared the two at the same Koschmieder visual range.
- Why built: Being lost in the woods is SEVEN's core feeling, and fog shape decides how far a player can read
  landmarks and how objects appear; a linear ramp is the cheap default and its perceptual consequences
  were unmeasured.
- Design: Exact arithmetic. Linear contrast 1 - d/22; exponential exp(-sigma d) with sigma = 3.912 / V
  (Koschmieder 1924, 2 percent threshold), V matched to where linear contrast hits 2 percent (21.56
  cells). Compared contrast by distance, the half-contrast distance, the fade rate at the visual
  range, and the range above 30 percent contrast (assumed readable).
- Got right: At the same visual range, SEVEN's linear fog keeps 50 percent contrast at half range where real fog
  keeps 14 percent; contrast halves at 11 cells instead of 3.8; objects fade 12.5 times faster per
  cell at the edge (a pop-in band) and stay readable (over 30 percent) to 15.4 cells instead of 6.6,
  2.3 times farther.
- Where/why it failed: Nothing in the arithmetic failed; the limits are that the 30 percent readability line is my
  assumption and that screen contrast and gamma change perceived contrast, so the ratios are about fog
  shape, not exact perception.
- Fix: If SEVEN wants real-feeling fog, switch to exp(-sigma d) or exp2 fog with sigma = 3.912 / visual
  range: the mid-distance turns grey and landmarks emerge gradually instead of popping in at the edge.
  Keep linear if the design wants long readable sightlines; either way choose it on purpose.
- Why this fix: Exponential fog is what the eye sees in mist and costs the same per pixel, and it removes the edge
  band where objects appear abruptly, which reads as rendering rather than weather.
- Rule of thumb: Linear fog at the same visual range keeps the mid-distance far clearer than real fog (50 vs 14
  percent contrast at half range, readable 2.3x farther) and pops objects in 12x faster at the edge;
  use exp(-3.912 d / V) when fog should feel like weather.
- Provenance (verified/assumed): Verified first-hand: SEVEN's fog formula read from its source and the comparison computed by the
  sandbox in this entry; Koschmieder's law (V = 3.912/sigma at a 2 percent threshold) is the standard
  meteorological definition, cited from memory.
- Composed: N/A
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__sevens-linear-fog-keeps-mid-range-clear-and-pops-objects-in-at-the-edge.py
- Prediction: half range: linear 50 percent, real about 14 percent; real contrast halves within about 4 cells
  against 11; the edge fades about 10x faster in linear fog; readable range about 2.5x farther in
  linear fog.
- Observed: RESULT: PASS 5/5; at half range linear 0.51 vs real 0.14; halves at 11 vs 3.8 cells; edge fade x12.5
  faster; readable range x2.32
- Scenarios: 1) contrast at 2 to 21.5 cells; 2) half-contrast distance; 3) fade rate at the visual range (built
  to show the pop-in edge); 4) readable range at 30 percent
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 3 pass 5 (gap: fog), 2026-10-15

## E106 — sevens answer whistle carries no distance and leans on level for front back
- Date: 2026-10-15
- Project: Pappydapimp69/seven
- Tags: [audio][wayfinding][gamedesign]
- What: Gap with no lessons (brain query front-back and hrtf: 0): what a player can tell about where a
  companion is from SEVEN's answer whistle, read from src/audio.js and src/soundscape.js at
  seven-1.18.0 (not modified): pan = sin(bearing), gain = 0.35 + 0.25 cos(bearing), no distance term,
  no rear low-pass.
- Why built: The whistle is how a player finds companions in the woods; a stereo pan alone cannot tell front from
  back, and the question was what SEVEN's level cue adds and what is missing.
- Design: Exact arithmetic over 360 bearings. A bearing and its front/back mirror share a pan and differ only
  in level; ambiguous when that difference is under a criterion of 1 dB (side-by-side JND) or 4 dB
  (assumed, judging one whistle against memory). A 10 degree head turn (Wallach 1940: head movement
  resolves front/back) checked by the sign of each mirror's pan change. Distance information read off
  the gain formula.
- Got right: The answer whistle carries no distance information at all: its gain has no distance term (the
  hallucinated voice layer does have distance and a rear low-pass). The level cue separates front from
  back well: only 18 of 360 bearings are ambiguous at 1 dB, 74 at 4 dB (about 20 degrees around each
  ear).
- Where/why it failed: I predicted a 10 degree head turn would resolve every bearing except exactly 90 degrees; it left
  about 10 degrees around each ear unresolved (85 to 95 and 266 to 274), because a source that close
  to the ear swings through it during the turn. The 4 dB memory criterion is my assumption.
- Fix: Give the answer whistle a distance cue (level falling with distance, more reverb send farther away)
  and the voice layer's rear low-pass, so front/back does not rest on absolute level alone; encourage
  a small turn to localize, which SEVEN's first-person look already allows.
- Why this fix: Without a distance term a near companion and a far one sound the same, so the whistle tells
  direction but not how far to walk; a spectral rear cue does not depend on remembering how loud a
  whistle should be.
- Rule of thumb: SEVEN's answer whistle tells direction but not distance (gain has no distance term) and separates
  front from back only by level (74 of 360 bearings ambiguous at a 4 dB memory criterion); add
  distance falloff and a rear low-pass, and expect a 10 degree head turn to resolve all but about 10
  degrees around each ear.
- Provenance (verified/assumed): Verified first-hand: the formulas were read from SEVEN's source at seven-1.18.0 and the consequences
  computed by the sandbox in this entry; the 4 dB criterion is assumed; Wallach 1940 is cited from
  memory as the classic head-movement result.
- Composed: N/A
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__sevens-answer-whistle-carries-no-distance-and-leans-on-level-for-front-back.py
- Prediction: 0 bits of distance; at 1 dB only bearings within about 5 degrees of the side ambiguous; at 4 dB
  about a quarter of bearings; a 10 degree turn resolves all but exactly 90 degrees.
- Observed: RESULT: PASS 4/4; answer whistle carries 0 bits of distance; front/back ambiguous at 18/360 bearings
  (1 dB) and 74/360 (4 dB); 10 deg turn unresolved at 85-95 and 266-274 (wider than my 'exactly 90'
  prediction)
- Scenarios: 1) 360 bearings at a 1 dB criterion; 2) the same at 4 dB; 3) distance at 1 and 30 cells; 4) built to
  BREAK the head-turn fix: bearings near each ear (about 10 degrees stay unresolved)
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 2 pass 5 (gap: front-back localization), 2026-10-15

## E105 — green wood penalty vanishes into whole trips at camp scale
- Date: 2026-10-15
- Project: Pappydapimp69/seven
- Tags: [gamedesign][survival][balance]
- What: Applied the FIREWOOD moisture kernel (green wood: 56 percent of seasoned heat per kg but 90 percent
  per log) to a camp night fed one log per action (sevin E15's feed action) with wood gathered in
  trips, to see whether green wood costs the player feeds or carrying.
- Why built: The kernel concluded that a game counting logs should model green wood's cost as weight and
  handling, not heat. Whether that cost actually shows at camp scale (about ten logs a night) was
  untested.
- Design: Exact arithmetic. Net heat per 2 kg-dry log from the kernel's formula; a night needs 300 MJ
  (assumed); feeds = logs needed; trips either weight-limited (20 kg a trip, whole logs) or count-
  limited (one log per gather action, SEVEN 1.15.0's rule). Moisture 0.12 to 0.65.
- Got right: Feeds rose as the kernel predicts per log: green wood at 50 percent moisture needed 10 feeds against
  9 (+11 percent), and very wet wood (0.65) 11 (+22 percent). Under SEVEN's one-log-per-action rule,
  gather actions rise exactly with feeds, so green wood is nearly free.
- Where/why it failed: My continuous estimate of a 75 to 80 percent carrying penalty at 50 percent moisture did not appear:
  whole logs per 20 kg trip (8 seasoned, 5 green) still fit a 10-log night in 2 trips each, so the
  penalty was zero; at 0.65 it jumped to 2x (4 trips against 2). At camp scale whole numbers hide or
  exaggerate the moisture effect.
- Fix: If green wood should cost something, express the cost in a continuous resource (weight against
  stamina, burn time, smoke) rather than in counts of trips or feeds, or make nights need enough logs
  that the averages show through.
- Why this fix: With about ten logs a night, a 10 to 20 percent effect is one log, and trip counts move in steps of
  a whole trip; a continuous resource carries the real 60 percent weight difference every time.
- Rule of thumb: At camp scale (about 10 logs a night) green wood's penalty disappears into whole numbers: 50 percent
  moisture cost one extra feed and zero extra 20 kg trips, very wet wood jumped to 2x trips; put a
  moisture cost in a continuous resource like weight or burn time, not in counts.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry; the 300 MJ night, 2 kg dry log and 20 kg carry are
  assumptions, and SEVEN's real wood numbers were not used.
- Composed: ideas:FIREWOOD/moisture/green-wood-loses-half-the-heat-per-kilo-but-a-tenth-per-log, pappydapimp69__sevin/E15
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__green-wood-penalty-vanishes-into-whole-trips-at-camp-scale.py
- Prediction: green vs seasoned: feeds +11 percent; weight-limited trips +75-80 percent; count-limited +11
  percent; at 0.65 feeds +27 percent and weight trips about 2.6x.
- Observed: RESULT: FAIL 3/5; green(0.5) feeds +11%, weight-limited trips x1.00, count-limited +11%; m 0.65
  feeds +22%, trips x2.00
- Scenarios: 1) moisture 0.12, 0.20, 0.35, 0.50, 0.65; 2) weight-limited carry; 3) count-limited carry (SEVEN's
  rule); 4) built to BREAK the kernel's 'cost is weight' advice at game scale: a 10-log night (the
  weight cost vanished at 0.5)
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 2 pass 1 (kernel apply FIREWOOD), 2026-10-15

## E104 — windbreak value scales with cold not with how much wind it stops
- Date: 2026-10-15
- Project: Pappydapimp69/seven
- Tags: [gamedesign][survival][simulation]
- What: Gap with no records (brain query hypothermia returned nothing): what a shelter or windbreak buys in
  felt cold, using the NWS and Environment Canada 2001 wind chill formula, as the basis for SEVEN's
  'the night takes the exposed first'.
- Why built: A shelter mechanic needs a rule for how much cutting the wind helps; the obvious guess, from the
  concave wind term, is that only stopping the wind entirely matters, which would make partial shelter
  pointless.
- Design: Exact arithmetic. WCT(F) = 35.74 + 0.6215 T - 35.75 V^0.16 + 0.4275 T V^0.16, with calm counted as 3
  mph (the formula's floor). Temperatures 50, 32, 20, 0 and -10 F; wind cuts 15 mph to calm, 40 to 15,
  30 to 15 and 6 to 3.
- Got right: Halving a strong wind (30 to 15 mph) gains only 2.6 to 7.2 F across the range, less than taking a
  moderate wind to calm, and the last few mph are worth a lot (6 to 3 mph gains 2 to 5.6 F), as the
  concave term implies.
- Where/why it failed: My all-or-nothing reading was too strong: cutting a 40 mph gale to 15 gains 75 percent as much (7.1
  F at 20 F) as taking 15 mph to calm (9.5 F, not the over 10 I predicted). And every benefit scales
  with the cold: taking 15 mph to calm is worth 5.0 F at 50 F but 14.0 F at -10 F. Calm is still below
  air temperature in the formula (15.7 F at 20 F).
- Fix: Model a windbreak's warmth as proportional to how cold the night is and to the wind it removes, with
  partial shelter worth most of full shelter in a gale; make shelter matter on the coldest nights and
  barely on mild ones, rather than making it binary.
- Why this fix: It follows the formula's real shape, so a player who builds a half windbreak in a storm is rewarded
  fairly, and the coldest nights become the ones where shelter decides who is 'exposed'.
- Rule of thumb: A windbreak's value scales with cold more than with how fully it stops the wind: by the 2001 wind
  chill formula, 15 mph to calm is worth 5 F at 50 F but 14 F at -10 F, and cutting a 40 mph gale to
  15 gives about 75 percent of the calm benefit.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry using the published NWS and Environment Canada 2001
  wind chill formula (written from memory, standard form); felt temperature is not body heat loss or
  hypothermia risk, which the formula does not model.
- Composed: N/A
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__windbreak-value-scales-with-cold-not-with-how-much-wind-it-stops.py
- Prediction: at 20 F, 15 mph to calm gains over 10 F; 40 to 15 under 8 F; 30 to 15 under 6 F; at 50 F, 15 to calm
  under 5 F.
- Observed: RESULT: FAIL 2/4; at 20 F calm vs 15 mph +9.5 F, 40->15 +7.1, 30->15 +4.9; at 50 F 15->calm +5.0; at
  -10 F 15->calm +14.0
- Scenarios: 1) five temperatures from 50 to -10 F; 2) four wind cuts each; 3) built to BREAK the all-or-nothing
  reading: a gale cut to 15 mph (it kept 75 percent of the benefit); 4) mild night at 50 F
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 1 pass 5 (gap: hypothermia), 2026-10-15

## E103 — hallucinated voices barely shrink a whistles range anywhere
- Date: 2026-10-15
- Project: Pappydapimp69/seven
- Tags: [audio][gamedesign][perception]
- What: Applied the OUTDOOR-ACOUSTICS forest-propagation kernel with seven E88 (maskers add by power, +3 dB
  per doubling of voices) and seven E73 (a must-land signal needs about 6 dB over other voices) to ask
  how much a real whistle's range shrinks as hallucinated voices pile up, in dense woods against open
  ground.
- Why built: SEVEN's whistle is how companions find each other, and its sanity layer adds voices; a natural
  design idea is that voices drown out real whistles. Whether that is a large effect or a rounding
  error decides whether it can carry gameplay.
- Design: Exact arithmetic with bisection. Whistle 100 dB at 1 m, air absorption 1.3 dB per 100 m, night band
  background 20 dB, each hallucinated voice 20 dB in the band (all assumed as in the kernel); heard at
  0 dB SNR; must-land at plus 6 dB. Excess attenuation 0, 4 and 23 dB per 100 m; voices 0, 1, 2, 4, 8.
- Got right: In dense woods voices cost little: 150 m fell to 119 m with 8 voices, 4 to 6 percent per doubling,
  and the must-land margin cost 20 m. The forest term still dominates, as the kernel says.
- Where/why it failed: My prediction that open ground would lose a quarter to a third per doubling was wrong: it lost only
  7 to 11 percent (1,342 to 886 m with 8 voices), because at kilometre range the air absorption term
  (17 dB at 1.3 km) is also linear in distance and caps the range the same way the forest does. The 4
  dB woods case lost 5 to 8 percent, not 20 or more.
- Fix: Do not use voice masking alone to make whistles fail: 8 equal voices cost 20 to 34 percent of range
  anywhere. If hallucinations should drown whistles, make the voices much louder than the night bed in
  the whistle's band, or make the hallucination change what the whistle sounds like rather than
  whether it is heard.
- Why this fix: Each doubling of voices adds only 3 dB, and every term that sets range here is linear in distance,
  so 3 dB buys only tens of metres; a perceptible effect needs either a large level jump or a change
  in the signal itself.
- Rule of thumb: Hallucinated voices barely shrink a whistle's range: each doubling of equal voices (+3 dB) cost 4-6
  percent in dense woods and 7-11 percent in the open (air absorption caps long range too), so 8
  voices cost 20-34 percent; drowning a whistle needs much louder voices or a changed signal.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry; whistle level, background, voice band level and
  air absorption are assumptions carried from the kernel, not measurements.
- Composed: ideas:OUTDOOR-ACOUSTICS/forest-propagation/a-whistle-carries-a-kilometre-in-the-open-and-150-to-500-m-in-woods, pappydapimp69__seven/E88, pappydapimp69__seven/E73
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__hallucinated-voices-barely-shrink-a-whistles-range-anywhere.py
- Prediction: each doubling costs open ground a quarter to a third of range but dense woods under 10 percent; 8
  voices halve open-ground range; the 4 dB woods case loses at least 20 percent per doubling.
- Observed: RESULT: FAIL 1/4; 8 voices shrink range open 1342->886 m, woods23 150->119 m, woods4 493->363 m; per
  doubling open 0.07, woods23 0.04, woods4 0.05
- Scenarios: 1) open ground; 2) dense woods 23 dB per 100 m; 3) built to BREAK the woods-only reading: light
  woods 4 dB per 100 m; 4) 0 to 8 voices each; 5) must-land plus 6 dB margin
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 1 pass 1 (kernel apply; brain challenge masking run first), 2026-10-15
- Audited: 2026-10-17 · fail · Read the entry and its stored sandbox. The model does compute its numbers (bisection on a spreading plus absorption plus excess-attenuation level equation, no answer built in), and its per-doubling figures reproduce. But the title and Rule of thumb say voices barely shrink a whistle's range anywhere, while the sandbox fixes each voice at 20 dB, exactly equal to the 20 dB night background, and never varies that level. Recomputing with the same equations and only the voice level changed: at 30 dB eight voices cut the open range from 1342 to 514 m and the dense-woods range from 150 to 90 m; at 40 dB a single voice already cuts open ground to 483 m (64 percent lost) and woods to 87 m; at 50 dB one voice leaves 226 m open and 60 m in woods. So the benign result is a property of the one chosen voice level, not of voices in general; the Fix sentence about much louder voices is the only part the data supports and it was never tested. The claim should be scoped to voices at the background level. · session_01FKz3vbJ5KozVVes2fUyYJ8

## E102 — hallucinated voices mostly mixed and resistible not all hostile commands
- Date: 2026-10-15
- Project: Pappydapimp69/seven
- Tags: [gamedesign][audio][research]
- What: Gap on SEVEN's open list (disturbing voice content): what a hallucinated-voice layer should contain
  if it follows what voice hearers report, using the 199-person phenomenological survey of McCarthy-
  Jones et al. and bounds on which experiences co-occur.
- Why built: SEVEN's sound-first progression puts voices at the centre, and the stigma tension asks whether the
  game frames psychosis as the threat or as the person's experience; voice content and control rules
  are where that choice becomes concrete.
- Design: Read the survey's results (Schizophrenia Bulletin 40(1):231-235, PMC3885292). Only marginal
  percentages were published, so the sandbox computes Frechet bounds on co-occurrence (abusive with
  helpful, derogatory with guiding, second with third person address) and the shares of all hearers
  who get commands they can and cannot resist. Break case: a voice layer in which every line is a
  command that overrides the player's input.
- Got right: At least 6 percent and up to 45 percent of hearers have both abusive and helpful voices (16 to 49
  percent derogatory and guiding), so an all-hostile layer contradicts a large share of reports. 51
  percent of all hearers get commands they can resist and at most 16 percent commands they cannot, so
  a voice that takes control is the minority case. At least 38 percent hear both 'you' and third-
  person commentary.
- Where/why it failed: One check failed only on float rounding (second-person-only at most 0.35, computed as 0.73 - 0.38 a
  hair above 0.35). The bigger limit: without a joint table the co-occurrence is a range, not a
  number, and the sample is a clinical one (81 percent schizophrenia).
- Fix: Build SEVEN's voice layer as a mix: hostile and critical lines alongside some helpful or guiding
  ones, commentary in the third person as well as 'you', voices that sound like people the character
  knows; let commands pressure the player but never seize input, so the character resisting is the
  common case.
- Why this fix: It matches the proportions people report and keeps the person as the one experiencing the voices,
  not a puppet of them, which is the framing the stigma evidence (identification lowered social
  distance) supports.
- Rule of thumb: Most voice hearers report commands they can resist (51 percent of all, at most 16 percent cannot),
  both hostile and helpful voices often together, and third-person commentary nearly as often as
  'you'; a voice layer of all-hostile commands that seize control inverts those proportions.
- Provenance (verified/assumed): Verified first-hand: percentages read from the survey's full text on PMC; bounds and shares verified
  by the sandbox in this entry. The design recommendation is my interpretation, not tested on players.
- Composed: N/A
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__hallucinated-voices-mostly-mixed-and-resistible-not-all-hostile-commands.py
- Prediction: abusive and helpful co-occur in at least 5 percent; resistible commands about 51 percent of all,
  irresistible at most 16-17 percent; second person more common than third; second-person-only at most
  35 percent.
- Observed: RESULT: FAIL 4/5; abusive+helpful 0.06-0.45 of hearers; resistible commands 0.51, irresistible 0.16;
  both address forms >= 0.38; all-override layer 100% vs 16% (the failed check is float rounding at
  the 0.35 boundary)
- Scenarios: 1) abusive with helpful; 2) derogatory with guiding; 3) commands resistible and not; 4) address
  forms; 5) built to BREAK the horror default: an all-override command layer (100 percent against 16)
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto loop 3 pass 5 (gap: disturbing voice content), 2026-10-15

## E101 — hellblade stigma studies move social distance not the dangerous stereotype
- Date: 2026-10-15
- Project: Pappydapimp69/seven
- Tags: [gamedesign][research][accessibility]
- What: First evidence for SEVEN's open tension on psychosis as horror versus as the character's experience:
  two experiments on Hellblade, read at the source, plus a power check on what their null results can
  and cannot say.
- Why built: The tension had no evidence at all, and SEVEN's hallucination layer is the design choice it governs.
  The question was whether an experience-framed, consulted game measurably changes stigma, and whether
  its nulls rule anything out.
- Design: Read Ferchaud et al. 2020 (Frontiers in Psychology, PMC7509402: N 198 students, randomized and
  yoked, 45 minutes of Hellblade played versus watched, structural equation model) and the abstract of
  Mason and Westhead 2025 (Journal of Mental Health: n 37, pre and post). Sandbox: normal-
  approximation power at alpha .05, power .80, for both designs, and power at small effects.
- Got right: Playing rather than watching raised transportation, then identification, then lowered desire for
  social distance from people with mental illness (significant indirect path). The second study found
  attitudes to schizophrenia improved after play. Both point the same way for an experience framing.
- Where/why it failed: Neither study moved the dangerousness stereotype: Ferchaud found no effect on a stereotyping index
  that includes 'those with mental illness are dangerous', and Mason and Westhead found no change in
  social distance or empathy. Their minimum detectable effects were d 0.40 and 0.46, with power 0.29
  and 0.23 at d 0.2, so the nulls cannot rule out small effects, and neither study tested a horror
  framing at all.
- Fix: Treat the experience framing as modestly supported (less social distance through identification) and
  the dangerousness stereotype as untested; in SEVEN keep the person as the one experiencing the
  voices, not the threat, and do not claim a stigma benefit.
- Why this fix: The only measured mechanism runs through identification with the character, which a horror framing
  that makes the person the monster would remove; the evidence is too small to say more, and about 392
  players per arm would be needed to see a d of 0.2.
- Rule of thumb: Playing an experience-framed psychosis game (Hellblade) lowered social distance through
  identification (N 198) but did not move the 'dangerous' stereotype, and both studies could only
  detect d of about 0.4 or more; keep the person as the experiencer, not the threat, and claim no
  stigma benefit.
- Provenance (verified/assumed): Verified first-hand: Ferchaud et al. 2020 read on PMC (design, N, indirect path, stereotyping null,
  limitations); the power numbers are verified by the sandbox in this entry. Mason and Westhead 2025
  was read only through search summaries of its abstract.
- Composed: N/A
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__hellblade-stigma-studies-move-social-distance-not-the-dangerous-stereotype.py
- Prediction: minimum detectable d about 0.40 (Ferchaud) and 0.47 (Mason); power at d 0.2 below 0.30 in both.
- Observed: RESULT: PASS 4/4; MDD Ferchaud 0.40, Mason 0.46; power at d 0.2: 0.29 / 0.23; 392 per arm needed for
  d 0.2
- Scenarios: 1) Ferchaud two-arm design; 2) Mason paired design; 3) power at d 0.1, 0.2, 0.3, 0.5; 4) built to
  BREAK the reading that the nulls show no effect: power at d 0.2 (0.29 and 0.23, so they cannot)
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto loop 2 pass 5 (gap: stigma tension evidence), 2026-10-15

## E100 — sun compass 15 degrees per hour fails near noon
- Date: 2026-10-15
- Project: Pappydapimp69/seven
- Tags: [wayfinding][navigation][gamedesign]
- What: Applied the SUNDIALS kernel (a vertical stick is not a polar-aligned style, so its shadow geometry
  changes with season) to the two ways a lost walker actually uses the sun: the shadow-tip method for
  east-west and holding the sun at an angle corrected 15 degrees per hour, then fed the residual into
  a seven E91-style cue-following walker.
- Why built: Seven E91 made the visible sky SEVEN's navigation dial and modelled the cue as unbiased. A sun cue
  read with folk rules is biased in ways that depend on hour, season and latitude, which matters for
  how 'helpful' the sky should be in the game.
- Design: Exact spherical geometry. Sun vector in east-north-up from latitude, declination and hour angle;
  shadow tip of a unit vertical stick; shadow-tip error is the angle of the line from the first to the
  second mark (30 min apart) against due east, at latitudes 20, 40, 55, equinox and both solstices,
  four clock times. Sun azimuth rate by hour. A walker that keeps the sun at a fixed relative angle
  corrected 15 degrees per hour from 11:00 to 13:00, and an E91-style walker (cue gain 0.05) following
  that drifting bearing.
- Got right: The shadow-tip line is exactly east-west at the equinox at every hour and latitude, and exact for
  marks symmetric about noon; off the equinox it errs 7 to 43 degrees in mid-morning, worst in winter
  at high latitude (43 degrees at 55 N in December, 09:00). At lat 40 in June the azimuth moves 48
  degrees per hour at noon, so the 15 degree per hour walker turns 53.7 degrees in two hours and the
  E91 walker ends 53.6 degrees off course while still walking straight (0.964).
- Where/why it failed: I predicted the 15 degree per hour rule would be close at the equinox; it still turned the walker
  15.3 degrees in two midday hours because the azimuth rate peaks at 23 degrees per hour at noon. In
  the tropics with the sun near the zenith (lat 20, June) the midday turn was 177 degrees: the sun
  swaps sides and the rule sends the walker back the way it came.
- Fix: Treat the sun as an unbiased cue only near the equinox or for marks symmetric about noon; otherwise
  give it an error that grows with distance from the equinox, latitude and closeness to noon (for the
  hold-the-sun rule) or to morning and evening (for the shadow tip), and never use it near the zenith.
- Why this fix: A biased cue does not produce E91's loops; it produces a confident straight walk in the wrong
  direction, which is a different and more dangerous kind of lost, and is the kind a player cannot
  notice from the path shape.
- Rule of thumb: A sun compass is biased, not just noisy: the 15 degree per hour rule turned a walker 54 degrees in
  two midday June hours at 40 N (15 at the equinox, 177 near the zenith), and the shadow-tip line is
  exact only at the equinox; a biased sky cue walks people straight and wrong rather than in circles.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry from standard solar geometry; the walker is a
  model, not data on people.
- Composed: ideas:SUNDIALS/hour-lines-are-set-by-a-polar-aligned-style-not-a-vertical-stick, pappydapimp69__seven/E91
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__sun-compass-15-degrees-per-hour-fails-near-noon.py
- Prediction: equinox shadow-tip exact; June lat 40 error >= 5 deg at 09:00 and less near noon; 15 deg/h
  correction close (< 10 deg turn) at the equinox; > 25 deg turn 11:00-13:00 in June at lat 40.
- Observed: RESULT: FAIL 4/5; shadow-tip equinox exact; lat40 June error 09h 16.36, 11:45 0.00 deg; 15 deg/h
  walker 11-13h turns eq 15.3, June lat40 53.7, lat20 -176.8 deg; E91 walker final heading 53.6 deg
  straightness 0.964
- Scenarios: 1) shadow tip at three latitudes, equinox and both solstices, four times; 2) azimuth rates; 3) 15
  deg/h walker at lat 40 equinox and June; 4) built to BREAK the rule: lat 20 in June near the zenith
  (177 deg); 5) E91 walker fed the residual
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto loop 2 pass 1 (kernel apply SUNDIALS), 2026-10-15

## E99 — content warnings game wide list plus filters spoils nothing
- Date: 2026-10-15
- Project: Pappydapimp69/seven
- Tags: [accessibility][gamedesign][narrative]
- What: Gap with no lessons: content warnings for SEVEN that do not spoil. Took the 2023 meta-analysis
  finding that warnings do not reduce distress but raise anticipatory anxiety, treated a warning's job
  as an informed choice, and measured how much each warning scheme reveals about a run.
- Why built: SEVEN has disturbing content (voices, a missing member, an impostor in the party) and a design whose
  twist is that someone is not who they say. A warning that leaks timing or the twist damages the
  game; no warning removes a player's choice.
- Design: Exact information model. Six content types, each present in a run with p 0.5 and on one of 7 days.
  Schemes: one game-wide list (same every run), a per-run list, per-day warnings, and the game-wide
  list plus per-type filters. Spoil = entropy of the warning, since it is a function of the run. Break
  case: a type whose existence is the twist, with an assumed 0.2 prior that the game has it.
- Got right: A game-wide list and game-wide list plus filters reveal 0 bits about any run; a per-run list reveals
  6 bits; per-day warnings reveal 14.42 bits, the whole run's entropy, so they spoil every timing.
  Filters add control without adding information.
- Where/why it failed: The game-wide list is not spoiler-free for the twist: naming impersonation as a content type removes
  2.32 bits of premise surprise even though it says nothing about a run. An umbrella word whose prior
  is already high (deception, paranoia; prior assumed 0.8) removes 0.32. The priors are assumed, not
  measured.
- Fix: Show one game-wide list before play with per-type filters, never per-run or per-day warnings, and
  name the twist only under an umbrella word players already expect from a horror game.
- Why this fix: Warnings do not prepare people emotionally (meta-analysis), so their value is the choice to skip or
  filter, which a constant list with filters gives at zero spoil; per-day warnings buy nothing extra
  and leak everything.
- Rule of thumb: Content warnings should be one game-wide list with per-type filters (0 bits about a run); per-day
  warnings leak the whole run (14.4 of 14.4 bits), and naming the twist itself spoils the premise, so
  use an umbrella word players already expect.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry for the information arithmetic; the warning-effect
  finding is Bridgland, Jones and Bellet 2023, Clinical Psychological Science, doi
  10.1177/21677026231186625, read through its abstract and APS and PsyPost coverage; the 0.2 and 0.8
  priors are my assumptions.
- Composed: N/A
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__content-warnings-game-wide-list-plus-filters-spoils-nothing.py
- Prediction: S1 0 bits; S2 6; S3 14.4 equal to the run entropy; S4 0; naming the twist game-wide removes 2.32
  bits of premise surprise.
- Observed: RESULT: PASS S1 0, S2 6.0, S3 14.42 (= run entropy 14.42), S4 0 bits; twist named game-wide removes
  2.32 bits of premise surprise, umbrella word 0.32
- Scenarios: 1) game-wide list; 2) per-run list; 3) per-day warnings; 4) list plus filters; 5) built to BREAK the
  'game-wide list spoils nothing' claim: the twist as a named type (it broke, 2.32 bits)
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto loop 1 pass 5 (gap: content warnings), 2026-10-15

## E98 — full screen hallucination effects cost a phone 9x at dpr 3
- Date: 2026-10-15
- Project: Pappydapimp69/seven
- Tags: [performance][rendering][mobile]
- What: Gap with no lessons (brain query post-process and fillrate return nothing): what full-screen
  hallucination effects (vignette, chromatic split, 9-tap blur) cost on a phone, and which lever cuts
  the cost most, using a memory-bandwidth model of full-screen passes.
- Why built: SEVEN's later sanity stages add visual distortion on top of a canvas raycaster, and the
  owner tests on a desktop; a cost that only appears on phones would ship unnoticed.
- Design: Exact arithmetic. Pass cost = pixels x (taps + 1) x 4 bytes / bandwidth. Assumed: 390x844
  CSS px phone, 10 GB/s effective bandwidth (mid phone) and 40 GB/s (flagship), desktop 1920x1080 at
  DPR 1 and 200 GB/s, 4 ms post budget. Compared DPR 3, 2, 1, half-resolution blur, and fusing
  vignette with chroma into one pass.
- Got right: On the mid phone at DPR 3 the three effects cost 30.8 ms, nearly two whole frames;
  rendering the post chain at DPR 1 cut it exactly 9x to 3.4 ms (inside budget); a half-resolution
  blur alone cut it to 13.0 ms; fusing vignette and chroma saved only 1.2 ms. A flagship at DPR 3
  still needs 7.7 ms.
- Where/why it failed: My break-case threshold missed: the desktop came out 1.08 ms, not under 0.5,
  though still 28x cheaper than the mid phone, so the hiding effect holds while my number did not.
  Bandwidths are assumed, not measured on devices.
- Fix: Render hallucination post-effects into a DPR 1 (or lower) buffer and upscale, blur at half
  resolution, and budget them on a mid phone, not the desktop the owner tests on.
- Why this fix: Pixel count scales with DPR squared, so the buffer's DPR is the 9x lever; pass fusion
  and tap trimming are single-digit-percent wins next to it, and soft distortion effects lose little
  at low resolution.
- Rule of thumb: Full-screen hallucination effects scale with DPR squared: in a bandwidth model a blur,
  vignette and chroma split cost a mid phone at DPR 3 about 31 ms against 1 ms on a desktop; render
  them at DPR 1 (9x cheaper) and blur at half resolution before fusing passes.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry for the arithmetic;
  the bandwidth figures, viewport and budget are assumed and no real device was measured.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__full-screen-hallucination-effects-cost-a-phone-9x-at-dpr-3.py
- Prediction: mid phone DPR 3 over 8 ms; DPR 1 cuts 9x and fits 4 ms; half-res blur recovers over half;
  fusing saves less than dropping DPR; desktop under 0.5 ms.
- Observed: RESULT: FAIL mid phone DPR3 30.81 ms (budget 4), DPR1 3.42; half-res blur 13.03; fused
  29.62; flagship DPR3 7.70; desktop 1.08 ms (4 of 5 checks held; desktop threshold missed)
- Scenarios: 1) mid phone DPR 3, 2, 1; 2) flagship DPR 3; 3) half-res blur; 4) fused pass; 5) built
  to BREAK the phone-only reading: desktop DPR 1 (1.08 ms, cheap but above my threshold)
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto pass 5 (gap), 2026-10-15

## E97 — sway amplitude convention flips drift vs jitter
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [accessibility][motion][gamedesign]
- What: Auditing seven E81 (keep hallucination sway out of the 0.2-0.4 Hz sickness band) showed its
  dose model never says what is held constant when a designer moves sway to another frequency. Rebuilt
  with the ISO 2631-1 Wf weighting on weighted acceleration and three conventions: same pixel amplitude,
  same peak velocity, same peak acceleration.
- Why built: E81's 'a 0.05 Hz drift cuts less than 2 Hz jitter' and its 96 percent figure came from an
  assumed weighting applied to an unnamed amplitude. A designer who keeps the sway's pixel size and only
  changes its speed is doing something different from what the model assumed.
- Design: Exact arithmetic. Wf table entered from memory (peak about 0.16-0.2 Hz), log-interpolated;
  dose = Wf(f) x acceleration amplitude, where acceleration = (2 pi f)^2 D for fixed displacement D,
  2 pi f V for fixed velocity, A for fixed acceleration. Cut relative to 0.3 Hz for 0.05, 0.1, 1 and 2 Hz.
  Vignette: linear-area dose vs a periphery-weighted one (periphery 2x per area, assumed).
- Got right: Under fixed velocity or acceleration, 2 Hz cuts 98 to 99.8 percent, consistent with E81.
  Under fixed pixel amplitude 2 Hz still cuts 90 percent, so moving out of the band helps in every
  convention.
- Where/why it failed: The drift-versus-jitter comparison flips with the convention: at fixed pixel
  amplitude a 0.05 Hz drift cuts 99.3 percent against 89.6 for 2 Hz jitter; at fixed acceleration the
  drift cuts only 76 percent. 1 Hz at fixed pixels cuts only 61 percent. A vignette's cut depends on
  how the periphery is weighted (70 percent linear, 80 periphery-weighted).
- Fix: State sway as pixel amplitude and frequency together, and when leaving the band prefer going
  slower and larger-period over faster at the same pixel size; keep a reduce-motion switch either way.
- Why this fix: Designers tune pixels, not accelerations, and in pixel terms a slow drift is the gentler
  choice while 1 Hz is barely better than the band. The switch covers what the toy cannot.
- Rule of thumb: When moving hallucination sway out of the 0.2-0.4 Hz band, say what is held fixed: at
  the same pixel amplitude a 0.05 Hz drift cut the modeled dose 99 percent and 2 Hz jitter 90, but 1 Hz
  only 61; tune in pixels and offer reduce-motion.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry for the model; the Wf
  values are entered from memory and the periphery weight is assumed, so the numbers are a model of
  people, not measurements. Diels and Howarth 2013 (Human Factors 55(3):595-604) re-checked: peak
  0.2-0.4 Hz for fore-and-aft optical flow.
- Composed: pappydapimp69__seven/E81, ideas:ACCESSIBILITY/motion-comfort/keep-repetitive-screen-motion-out-of-the-2-to-5-second-period-band
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-12__sway-amplitude-convention-flips-drift-vs-jitter.py
- Prediction: under V and A 2 Hz cuts >= 90%; under D it does NOT reach 90%; 0.05 Hz drift cuts less
  than 2 Hz under A but more under D; vignette 70% linear, more if the periphery is weighted.
- Observed: RESULT: PASS 2Hz cut D 0.896 V 0.984 A 0.998; 0.05Hz cut D 0.993 A 0.763
- Scenarios: 1) fixed displacement; 2) fixed velocity; 3) fixed acceleration; 4) vignette linear vs
  periphery-weighted; 5) built to BREAK E81: the 0.05 Hz drift under fixed pixels (it broke)
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; review pass of SEVEN targets, gap lessons, 2026-10-12

## E96 — hue only hallucination cue vanishes for colour blind
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [accessibility][color][gamedesign]
- What: Gap with no lessons: colour-blind-safe hallucination cues. If SEVEN's visual hallucinations tint
  the woods a 'wrong' colour, does the cue survive protanopia, deuteranopia and tritanopia, and what
  makes it survive?
- Why built: The sound-first-then-sight progression puts visual cues late, and about 8 percent of men
  have a red-green deficiency; a cue that some players cannot see breaks the investigation for them.
- Design: Exact arithmetic. Foliage base sRGB (62,118,48). Cues: HUE (red-brown at matched luminance),
  LUM (35 percent darker), BY (blue shift at matched luminance), BOTH (hue shift plus darker). Simulated
  with Machado, Oliveira and Fernandes 2009 full-severity matrices in linear RGB (entered from memory),
  CIE76 delta-E in Lab; 10 taken as a glanceable cue.
- Got right: The hue-only cue lost most of its contrast for red-green deficiency: delta-E 60.7 normal,
  7.5 protan, 10.3 deutan. The luminance cue stayed 16.6 or more in all four, and the redundant cue 13.3
  or more in all four.
- Where/why it failed: My deutan prediction (under 10) missed narrowly at 10.3, and the blue-yellow
  swap kept 11.2 under tritanopia instead of falling below 10; still both lost over 80 percent of their
  normal contrast, so the threshold, not the loss, decided those checks.
- Fix: Carry every hallucination colour cue redundantly in luminance (or shape, motion or sound), never
  in hue alone, and check it through a CVD simulation of all three types.
- Why this fix: Luminance survives every dichromacy in the model, and a redundant cue keeps the full
  colour effect for typical vision while staying visible to everyone else.
- Rule of thumb: A hue-only hallucination tint loses most of its contrast for colour-blind players
  (delta-E 61 to 7.5 under protanopia, a blue swap 60 to 11 under tritanopia); carry the cue in
  luminance or another channel too and check all three CVD types.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry for the simulation;
  the Machado matrices are entered from memory and the delta-E 10 threshold is assumed, not measured on
  players.
- Composed: ideas:GAME-DESIGN/hallucination-phenomenology/sound-first-then-sight-as-sanity-falls
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__hue-only-hallucination-cue-vanishes-for-colour-blind.py
- Prediction: HUE >= 30 normal and < 10 under protan and deutan; LUM >= 10 under all; BY >= 10 under
  protan and deutan, < 10 under tritan; BOTH >= 10 under all.
- Observed: RESULT: FAIL 5/7; HUE dE normal 60.7 protan 7.5 deutan 10.3; LUM min 16.6; BY tritan 11.2;
  BOTH min 13.3
- Scenarios: 1) hue cue; 2) luminance cue; 3) blue-yellow cue; 4) redundant cue; each under normal,
  protan, deutan, tritan; 5) built to BREAK the blue-yellow fix: tritanopia (it lost 81 percent)
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; review pass of SEVEN targets, gap lessons, 2026-10-12
- Cited-by: 2026-10-15 · projects/local__heraldic-rule-of-tincture-is-a-lightness-class-not-a-contrast-threshold.md#E1 · compatible · sandboxes/2026-10-15__heraldic-rule-of-tincture-is-a-lightness-class-not-a-contrast-threshold.py · observed RESULT: PASS rule-of-tincture: 10/10 allowed pairs >=3:1, weakest allowed or/vert 3.03, strongest forbidden sable/vert 5.11 (AUC 0.955, no single threshold); CVD allowed pairs under 3:1: 1, weakest under CVD 2.64 · session_01A5ZkeepCfk7CHTSxS7qQ4k

## E95 — fade with a lasting cue keeps most rescues
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][rescue][search-theory]
- What: Blind rebuild of seven E77 (fade to silence ends hopeless searches at small rescue cost) with
  its suggested pairing tested: the call fades to silence, but a lasting non-call cue (tracks) keeps a
  call-following player searching some nights after silence.
- Why built: E77's rule said fading costs about 0.13 of rescues even on easy finds and suggested a
  lasting cue without testing it. The owner chose fade, so what the cue buys decides how to ship it.
- Design: Exact, no rng. 14 nights; call heard 1.0 nights 1-3 then falling 0.2 a night; FLOOR keeps it
  at 0.35, FADE reaches 0 by night 8, FADE+CUE keeps a 0.21 chance of going out after silence. Find
  chance per search: hopeless 0, shallow 0.5, mid 0.2, deep 0.08. Rescue probability and expected late
  search nights (night 8 on).
- Got right: Fade cut hopeless late search nights 2.45 to 0 and cost 0.126 to 0.139 on mid and deep
  rescues, matching E77's size there. Adding the lasting cue won back 59 percent of the deep loss
  (0.339 to 0.413 against 0.465 floored) and still cut hopeless late nights 40 percent (to 1.47).
- Where/why it failed: The easy case cost only 0.029, not about 0.13, so E77's 'even when easy' did not
  reproduce; the cost scales with how hard the find is. A cue strong enough to save deep rescues also
  brings back hopeless searching, so it trades one against the other rather than removing both.
- Fix: Ship the fade with a lasting physical cue whose strength is the dial between hopeless nights
  and deep rescues, and tune it on deep cases, since easy ones barely need it.
- Why this fix: It keeps the owner's fade (an ending to hopeless searches) while recovering most of
  what fade costs where it costs anything, using the world rather than a call that never ends.
- Rule of thumb: Fading a missing member's call costs little on easy finds (0.03 here) and about 0.13 on
  hard ones; a lasting non-call cue won back 59 percent of the hard-case loss while keeping hopeless
  late searching 40 percent below a floored call.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry; the schedules, the
  0.21 cue rate and find chances are my choices, and players are modeled as following every cue.
- Composed: pappydapimp69__seven/E77, pappydapimp69__seven/E27
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__fade-with-a-lasting-cue-keeps-most-rescues.py
- Prediction: hopeless late-night cut >= 70%; shallow cost <= 0.02; deep cost >= 0.10; a lasting cue
  restores most of the deep-case rescue while hopeless late nights stay well below the floor.
- Observed: RESULT: FAIL hopeless late nights 2.450->0.000; shallow cost 0.0288; deep cost 0.126;
  fade+cue deep 0.413 (floor 0.465, fade 0.339), hopeless late 1.470
- Scenarios: 1) hopeless; 2) shallow; 3) mid; 4) deep; each floor, fade, fade+cue; 5) built to BREAK
  E77: the easy case's 0.13 cost (it broke)
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; review pass of SEVEN targets, gap lessons, 2026-10-12
- Audited: 2026-10-19 · modeled · Read the entry and reran its stored sandbox (3.x, exact, no rng). The model computes its numbers (per-night heard probability times find chance, summed), nothing is built in: shallow cost 0.0288, deep cost 0.126, hopeless late nights 2.450 to 0, and from the printed fade+cue figures (deep 0.339 fade, 0.413 cue, 0.465 floor) the 59 percent win-back and 1.47 hopeless late nights (40 percent below floor) check out by hand. Scope is narrower than the Rule of thumb implies: the 59 percent depends on the cue rate (0.21, a chosen dial), and the entry's sandbox file uses 0.35*0.6 with the stated RESULT line not printing the win-back. The claim is about how real players behave when a call fades and a cue persists, but players are modeled as following every cue with fixed find chances, so only a hand-written model was tested, not player behaviour. · brain train auto pass 3 audit (loop 1), 2026-10-19; session_01TLYDN658tW4ZQFUr2wQFj7

## E94 — compensated sum is order free except exact cancellation
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [testing][floating-point][sandbox]
- What: Follow-up to seven E90 (stored sandboxes drift because sum() of floats is compensated since
  Python 3.12): is sum() therefore order-free? 40 random lists of 8 floats each summed in 200 orders by
  sum(), a plain loop and math.fsum, in three magnitude regimes.
- Why built: E90 predicted sum() in two orders is equal on 3.13. A review found a list where it is not,
  so a sandbox that relies on sum() being order-free could still flake.
- Design: Seeded random.Random. Regimes: wide magnitudes (1e-3 to 1e16, random signs), narrow (1 to 2),
  and lists holding an exactly cancelling huge pair (x and -x, x 1e15 to 1e17) plus six small values.
  Counted lists with more than one distinct total per method. Python 3.13.
- Got right: math.fsum gave one value for all 120 lists; the plain loop varied on all 120; sum() was
  order-free on all 80 wide and narrow lists.
- Where/why it failed: sum() was order-dependent on 8 of 40 lists with an exactly cancelling huge pair
  (e.g. 4.0009999999999994 against 4.001), so compensated is not exact. My first prediction (sum()
  varies on 5+ random lists) and second (10+ cancelling lists) were both refuted.
- Fix: Demonstrate order effects with a plain loop, and when a result must not depend on order use
  math.fsum, not sum().
- Why this fix: The loop shows the effect on every interpreter; fsum is the only one of the three that
  was order-free on every list, while sum() hides order effects almost always but not always.
- Rule of thumb: Python 3.12+ sum() of floats is almost order-free (0 of 80 random lists varied) but not
  exact: it still varied on 8 of 40 lists holding an exactly cancelling huge pair; use math.fsum when
  order must not matter.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry on Python 3.13.16;
  that sum() uses Neumaier compensation since 3.12 is from the Python changelog as cited in E90.
- Composed: pappydapimp69__seven/E90
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__compensated-sum-is-order-free-except-exact-cancellation.py
- Prediction: iteration 1: fsum always one value, loop varies on >= 30/40, sum() varies on >= 5/40
  wide lists; iteration 2: with a cancelling pair sum() varies on >= 10/40.
- Observed: RESULT: FAIL sum() order-dependent in wide 0/40, narrow 0/40, cancelling-pair 8/40 lists
  (loop 40/40/40, fsum 0/0/0)
- Scenarios: 1) wide magnitudes; 2) narrow magnitudes; 3) built to BREAK the order-free reading: an
  exactly cancelling huge pair (it broke on 8 of 40)
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; review pass of SEVEN targets, gap lessons, 2026-10-12

## E93 — cancel ratio between two slopes is a fixture constant
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][sanity][sandbox]
- What: Blind rebuild of seven E76 (a sanity competence penalty cancels only with recovery damping 3 to
  5 times steeper; a 0.10 penalty cannot be cancelled) in a different model, plus an audit of how the
  original's predictions were written.
- Why built: E76 gave a numeric ratio as a design rule, and its stored sandbox carried the prediction of
  an earlier rebuild (E67), with check thresholds that match its observed 3.3x and 4.7x.
- Design: Exact DP over 20 sanity levels, 60 tasks; competence p0(1 - a(1 - s)); success +1, failure -3;
  passive recovery min(1, r0(1 + b(1 - s))); breakdown at 0; outcome = expected tasks done. Least b that
  matches the no-penalty baseline, for a in 0.03 to 0.40, under two base-rate sets (p0 0.7 r0 0.15 and
  p0 0.8 r0 0.30). Iteration 1 used per-0.1-level units.
- Got right: The shape carries over: a mild penalty can be cancelled, cancelling always needs b > a,
  and the recovery cap makes large penalties impossible to cancel in both sets.
- Where/why it failed: The ratio does not: 27 to 29x in set A and 49 to 76x in set B (28x and 158x in
  iteration 1), never 3 to 5x, and a 0.10 penalty was cancellable in set A. The ratio of two slopes in
  different units is set by base rates and units, so it is a property of the fixture.
- Fix: Report such results as a shape (which side must be steeper, where a cap makes it impossible) and
  give a ratio only after showing it holds across at least two base-rate sets and unit choices.
- Why this fix: A designer reading '3 to 5x' tunes to it; in another model the needed damping was ten
  times that, so the number would mislead while the shape transfers.
- Rule of thumb: A ratio between a penalty slope and the damping that cancels it is a fixture constant
  (3-5x in one model, 27-76x in another); keep the shape (damping must be steeper, a cap makes big
  penalties uncancellable) and rerun base rates before quoting a number.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry and by re-running the
  stored E76 sandbox; both models are toys of a game, the units are my choice.
- Composed: pappydapimp69__seven/E76, pappydapimp69__seven/E67
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-12__cancel-ratio-between-two-slopes-is-a-fixture-constant.py
- Prediction: small penalties cancel and need b > a; some penalty is uncancellable at the cap; the
  ratio differs by more than 2x between the two base-rate sets.
- Observed: RESULT: FAIL shape holds but ratios 27-76x not 3-5x; 0.10 cancelled in set A (b 2.82);
  between-set difference 1.70x at a 0.03 and 2.67x at 0.06
- Scenarios: 1) set A; 2) set B; 3) iteration 1 units; 4) built to BREAK E76: a 0.10 penalty in set A
  (it was cancellable)
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; review pass of SEVEN targets, gap lessons, 2026-10-12

## E92 — barrel capture is capped by demand not tank size
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [garden][water][design]
- What: How much of a roof's yearly runoff a barrel or tank catches when it is drained only by the garden's real
  use, not emptied between storms as seven E82 and the rain-barrel kernel's best case assume.
- Why built: E82 flagged that emptying between storms inflates capture. The size of that gap decides whether a
  bigger tank is worth buying, which is the decision the kernel is used for.
- Design: Deterministic. 70 storms totalling 40 inches with exponential storm depths and 2-12 day gaps on a 1000 sq
  ft roof, 10 percent gutter loss, 12.5 gallon first flush per storm; tanks of 55, 200 and 500 gallons drained by
  2, 10 or 25 gallons a day, against the emptied-every-storm best case.
- Got right: A small barrel is barely demand-limited: 55 gallons caught 0.141 of runoff at 10 gallons a day against
  0.158 in the best case. Big tanks are: 500 gallons caught 0.792 in the best case but 0.244 at 10 gallons a day
  and 0.067 at 2 gallons a day.
- Where/why it failed: My prediction that even the 55 gallon barrel would lose 20 percent to demand missed (it lost
  11): a small barrel refills to full from most storms whatever was drawn.
- Fix: Size storage to demand times typical days between storms (for example 10 gallons a day x 5 days, about 50
  to 100 gallons), not to roof yield; past that, a bigger tank mostly holds water nobody uses, so route overflow
  to a rain garden instead.
- Why this fix: Capture is what you empty between storms, so the tank only helps up to the volume the garden draws
  down; roof yield sets the ceiling only for tanks that are emptied.
- Rule of thumb: Rain-tank capture is capped by use between storms, not tank size: a 500 gallon tank caught 79% of
  runoff if emptied every storm but 24% at 10 gal/day and 7% at 2 gal/day; size storage to demand x days between storms.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 2/3 of my predictions;
  numbers copied from the run). The storm series is a model, not local rainfall data.
- Composed: pappydapimp69__seven/E82, ideas:GARDEN/water/rain-barrel-sizing-plus-first-flush-diverter, ideas:GARDEN/water/passive-landscape-water-harvesting
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__barrel-capture-is-capped-by-demand-not-tank-size.py
- Prediction: the best case catches 15-25 percent with 55 gallons and 65-85 with 500; at 10 gallons a day a 55 gallon
  barrel catches at most 0.8x its best case; at 2 gallons a day even 500 gallons catches under 25 percent.
- Observed: RESULT: FAIL 2/3; best case 55/200/500 0.158/0.465/0.792; 55 gal at 2/10/25 gal/day 0.047/0.141/0.157;
  500 gal at 2 gal/day 0.067
- Scenarios: 1) emptied every storm; 2) demand 2, 10 and 25 gallons a day; 3) three tank sizes; built to BREAK the
  best-case reading: a big tank with low demand.
- Link: session; brain train deeper (review + follow-up of seven E82); session_01KGZvxv8BDgpDMRFTYMfJoJ

## E91 — wayfinding without a sky cue heading noise alone walks circles
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [wayfinding][gamedesign][navigation][perception]
- What: Seed lesson for a new WAYFINDING domain: a heading random walk (accumulating noise each step)
  with and without a sky cue that pulls heading back toward the intended bearing, reproducing the
  'walking in circles' finding and asking how strong the cue must be.
- Why built: SEVEN is a walk through woods with a compass that can lie and nights that hide the sky,
  and Brain had nothing on how people actually lose their way. Souman et al. 2009 is a real, directly
  usable finding: straight with the sun visible, circles without it, turning either way.
- Design: Deterministic generator, 1 metre steps, 2,000 steps, 20 seeds. Heading changes by Gaussian
  noise sigma per step (0.06 to 0.5 radians); a sky cue pulls heading back by 5 percent of its error per
  step. Measured straightness (net distance / path length) and whether the path loops (returns within 5
  metres of a point at least 100 steps earlier), and the turning direction of loops.
- Got right: Heading noise alone produces circles in both turning directions (16 of 20 seeds loop at
  sigma 0.15, 20 of 20 at 0.5), matching the paper's report that circles rarely had a systematic
  direction, while a fixed turning bias with no noise circles one way only. At moderate noise a sky cue
  removes every loop (0.889 straightness at 0.15).
- Where/why it failed: My first predictions at sigma 0.06 were refuted (straightness 0.661, no loops):
  low noise only veers, so looping needs much larger heading noise, as with a blindfold. And a fixed-
  strength sky cue does not remove loops at every noise level: at 0.3 three seeds loop and at 0.5
  eighteen do, so the cue has to scale with the noise.
- Fix: Use the sky as the navigation dial: a visible sun, moon or distant landmark lets the player hold
  a heading; overcast, fog or canopy removes it and lets drift and loops emerge on their own. Scale how
  much the world 'helps' (cue strength) against how disoriented the player is meant to be.
- Why this fix: It produces lost-ness from a real perceptual mechanism instead of a scripted maze, and
  fits SEVEN's night and hallucination layers (a lying compass on an overcast night) without new
  systems.
- Rule of thumb: Without a sky cue, heading noise alone walks people in circles in both directions (16
  of 20 paths looped at moderate noise), and a fixed-strength cue stops loops only while noise is
  moderate (18 of 20 looped at high noise); use the visible sky as the navigation dial.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 3/4 on
  the iterated predictions; iteration 1 refuted all three of its no-cue predictions, kept in the
  docstring). The walking-in-circles findings come from search summaries of Souman et al. 2009 and its
  press release; noise and cue values are my choices. This domain is new, so no existing lesson is
  composed; the kernel below is its seed.
- Composed: ideas:WAYFINDING/veering/without-a-sky-cue-heading-noise-alone-walks-people-in-circles
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__wayfinding-without-a-sky-cue-heading-noise-alone-walks-circles.py
- Prediction: (iteration 2) at sigma 0.06 the walker veers without looping; at high noise most no-cue
  walks loop; a sky cue removes loops at every noise level; noise loops turn both ways and a fixed bias
  one way.
- Observed: RESULT: FAIL 3/4; s0.06: 0.66/0 cue 0.98/0; s0.15: 0.31/16 cue 0.89/0; s0.3: 0.13/19 cue
  0.63/3; s0.5: 0.08/20 cue 0.28/18
- Scenarios: 1) sigma 0.06; 2) 0.15; 3) 0.30; 4) 0.50; each with and without the sky cue; 5) a fixed bias
  with no noise; 6) built to BREAK the claim: a sky cue at high noise (it broke).
- Link: session; brain train auto replacement pass (newdomain WAYFINDING); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-12 · pass · sandboxes/2026-10-12__rebuild-seven-e91-wayfinding-circles-without-sky-cue.py · observed RESULT: PASS no-cue loops 0 / 15 / 24 of 24; cue loops moderate 0, high 18/24; directions 5/10; bias one-way 24/0 · Own fixture: a correlated walk in TURN RATE (w = 0.9 w + N(0,s)), 0.7 m steps, 3000 steps, 24 seeds, loop = true self-crossing (original: white heading noise, 1 m steps, 20 seeds, near-return loop test). No cue: 0/24 loops at low noise, 15/24 at moderate (both directions, 5 left 10 right), 24/24 at high; a fixed cue (k 0.05) cleared moderate noise (0/24) but not high (18/24 looped); a constant bias looped one way only (24/0). So the mechanism reproduces under a different noise model and loop test; my own '>= 16/24' threshold missed by one. The numbers are toy-model numbers; the human part rests on Souman, Frissen, Sreenivasa & Ernst 2009, Current Biology 19(18):1538-1542, re-checked: circles under overcast skies, straight-ish with the sun, blindfolded circles < 20 m rarely in a systematic direction, attributed to accumulating sensorimotor noise - all as cited. · session_01P1LRA5HjMLEFnWXayE2EHx; blind review pass of SEVEN targets, 2026-10-12
- Cited-by: 2026-10-15 · projects/pappydapimp69__seven.md#E100 · compatible · sandboxes/2026-10-15__sun-compass-15-degrees-per-hour-fails-near-noon.py · observed RESULT: FAIL 4/5; shadow-tip equinox exact; lat40 June error 09h 16.36, 11:45 0.00 deg; 15 deg/h walker 11-13h turns eq 15.3, June lat40 53.7, lat20 -176.8 deg; E91 walker final heading 53.6 deg straightness 0.964 · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto loop 2 pass 1 (kernel apply SUNDIALS), 2026-10-15
- Cited-by: 2026-10-15 · projects/pappydapimp69__demo-disc.md#E7 · incompatible · sandboxes/2026-10-15__sky-cue-beats-clearing-seeking-in-woods.py · observed RESULT: PASS a sky cue lifts homing from 18/40 to 40/40, while clearing-first adds only 4/40 under drift; in earshot both 40/40, in the open both 40/40, with the sun clearing-first is only faster (median 178 s against 192 s). · Demo-disc commit "Add Veer: the ad is a draw-the-path puzzle, the game is a foggy walk you play by ear"; session_011p52L2CkFXcsYRwjDu6tG9

## E90 — stored sandboxes drift on interpreter and missing snapshots
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [testing][process][tooling][verification]
- What: A reproducibility sweep of every stored Brain sandbox: all 1,349 scripts in memory/sandboxes
  were re-run on Python 3.13 (30 seconds each, 8 in parallel) and their RESULT word compared with the
  Observed field recorded in their entries.
- Why built: Brain's confirmed tier rests on sandboxes that 'anyone can rerun', but nobody had rerun
  them. An audit this session found one that no longer reproduces, so the question was how many others
  had drifted, and why.
- Design: Parsed each entry's Sandbox and Observed fields (1,172 mapped), re-ran every script, and
  compared PASS or FAIL. Classified a sample of 40 scripts with no RESULT line by re-running them alone.
  This entry's own sandbox demonstrates the interpreter cause on the running Python.
- Got right: Reproducibility is high: of 794 comparable results, 792 matched their record. Every
  no-result script in the sample does print a RESULT line; none crashed. They were slow: 22 of 40 still
  ran past 30 seconds alone, and the rest finished when run without parallel load.
- Where/why it failed: Two flipped from PASS to FAIL, for two different reasons. One used sum() to show
  that float order matters; since Python 3.12 sum() uses compensated summation, so the effect vanishes
  (a plain loop still shows it). The other depends on a saved web page that was not shipped with the
  sandbox, so its scope check now finds 1 marker instead of 5. And about 28 percent of stored sandboxes
  (373) give no result within 30 seconds, which makes casual re-verification impractical.
- Fix: When writing a sandbox, demonstrate float effects with an explicit loop (or math.fsum versus a
  loop), never sum(); embed or ship every input file it reads beside it; print the Python version in
  the RESULT line; and keep runtime under about 30 seconds or say how long it takes. Re-run the store
  periodically and audit any flip.
- Why this fix: Each rule removes one of the observed drift causes at the point of writing, and a cheap
  periodic sweep catches the next cause before a confirmed lesson silently stops being true.
- Rule of thumb: Stored sandboxes mostly reproduce (792 of 794 here), but they drift on the interpreter
  (sum() of floats is compensated since Python 3.12) and on unshipped input files; write float-order
  demos with a plain loop, ship every input, print the Python version, and keep runs under about 30 s.
- Provenance (verified/assumed): Verified first-hand: I re-ran all 1,349 stored sandboxes on 2026-10-12
  and compared them with their recorded Observed fields; this entry's sandbox reproduces the interpreter
  cause on Python 3.13; the missing-snapshot cause was confirmed by re-running that script.
- Composed: local__sandbox-rng-determinism-not-sufficient-for-replay/E2, pappydapimp69__brain/E207, pappydapimp69__seven/E70
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__stored-sandboxes-drift-on-interpreter-and-missing-snapshots.py
- Prediction: on Python 3.13 sum() in two orders is equal, a plain loop differs, and math.fsum is equal.
- Observed: RESULT: PASS 3/3; sum equal True loop equal False fsum equal True on 3.13.16. Sweep: 794
  comparable, 792 matched, 2 flipped PASS to FAIL, 373 no result within 30 s.
- Scenarios: 1) sum() in two orders; 2) a plain loop in two orders; 3) math.fsum in two orders; plus the
  full sweep of 1,349 stored sandboxes.
- Link: session; brain train auto pass 5 (gap), 2026-10-12; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-12 · pass · sandboxes/2026-10-12__rebuild-seven-e90-stored-sandbox-reproducibility.py · observed RESULT: PASS finished reproduce 9/9 (80-sample sweep 49/49, 31 age-cutoff timeouts at 30 s); sum() compensated but NOT order-free (4.0009999999999994 vs 4.001) - my prediction refuted · Own fixture: float probe with my own values, plus a fresh sample of stored sandboxes picked by sha1 of the name, re-run with python -I in an empty temp dir and compared with the RESULT word in the entry's Observed. Sweep of 80 at 30 s, 8 parallel: 49 finished, 49/49 reproduced; 31 timed out, ALL in the age-cutoff family (so 'keep runs under 30 s' is not met by ~40% of that sample under load). The shipped sandbox runs 16 at 12 s (16 s wall) and reproduced 9/9 finished. Gap: the entry's prediction 'sum() in two orders is equal on 3.13' is not general - [1e16, 1.0, -1e16, 3.0, 1e-3] gives 4.0009999999999994 forward and 4.001 reversed with sum(); Neumaier compensation narrows but does not remove order dependence; only math.fsum is exact. The rule's advice (plain loop for demos, print the version) still holds. Timeout counts vary with machine load. · session_01P1LRA5HjMLEFnWXayE2EHx; blind review pass of SEVEN targets, 2026-10-12
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E94 · compatible · sandboxes/2026-10-12__compensated-sum-is-order-free-except-exact-cancellation.py · observed RESULT: FAIL sum() order-dependent in wide 0/40, narrow 0/40, cancelling-pair 8/40 lists (loop 40/40/40, fsum 0/0/0) · session_01P1LRA5HjMLEFnWXayE2EHx; review pass of SEVEN targets, gap lessons, 2026-10-12

## E89 — rebuilt witness list forks a fakes lie across reload
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [determinism][save][deduction][rng]
- What: Composed seven E1 (a fixed total number of draws), seven E48 (save the rng state words),
  seven E20 (facts come from state) and seven E40 (reading answers) around the fake's lie. That lie
  draws nothing from the run stream: it takes one side-stream value keyed on (seed, fake, day) and
  uses it as an INDEX into the list of facts the player witnessed that day. The test was whether
  satisfying both rng rules is enough for the lie to survive a save and reload.
- Why built: The house rule says anything that GATES an rng draw is save state, and E48 makes the
  run stream restore exactly. A witness list that only indexes a draw gates nothing, so neither rule
  requires it to be saved. If the resumed game rebuilds it, nothing flags it.
- Design: Stdlib Python over 3000 days with seeds 7001 onward. Each day has 4 to 10 facts and makes
  six run-stream draws, always. Each fact is witnessed with chance 0.7, and the first two always.
  The lie is a sha256 side-stream value. The save stores the sfc32 state words and the witness list
  is restored one of four ways: verbatim; rebuilt in a different order (by place, not time); rebuilt
  sorted by id on both sides; or rebuilt with one witnessed fact lost. Two pickers were compared:
  index into the list, and min-hash over fact ids. The player's check: ask the same question, reload,
  ask again. A real account comes from the log and never changes, so a story that changed is the fake.
- Got right: Every scenario met both rules: six draws every day, and the run stream resumed exactly
  (1.000) after a reload. A verbatim saved list kept the lie stable (0.000). Min-hash removed the
  reorder fork (0.000) and kept the drop fork near 1/n (0.208). A canonical id sort on both sides
  also removed the reorder fork (0.000).
- Where/why it failed: With every rng rule met, a reorder-rebuilt list changed the fake's bent fact
  on 0.797 of reloads, and ask, reload, ask again picked out the fake 0.899 of the time (0.5 is
  chance). Losing one witnessed fact changed the bent fact 0.395 of the time with either the index
  pick or the canonical sort (I had predicted at least 0.60). Each drop that changes the lie is still
  a free tell (identification 0.698). The canonical sort does not help with a lost fact.
- Fix: Treat the witnessed-fact list as save state, stored verbatim in a canonical order, not
  recomputed on load. Select the bent fact by min-hash over fact ids keyed on (seed, fake, day,
  fact) rather than by index into the list, so that a reorder cannot move it and a change to the set
  only moves it when the chosen fact itself is affected.
- Why this fix: Both rng rules guard the run stream, but this fork happens entirely in data that
  indexes a side-stream value. Saving the list closes the hole at its source. Min-hash ties each
  fact's selection to that fact alone, so it cannot depend on where the fact sits in the list.
- Rule of thumb: Anything that INDEXES a draw is save state too, not only what gates one: with a
  fixed draw count and an exact rng restore, a rebuilt witness list moved a fake's bent fact on
  0.797 of reloads (0.395 when one fact was lost), so ask, reload, ask again caught the fake 0.899 of
  the time. Save the list verbatim and pick the bent fact by min-hash over fact ids.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 8/10
  predictions held; numbers copied from the run). Separately, the fact counts, the 0.7 witness rate
  and the two rebuild modes are my modelling choices, not read from src/chronicle.js.
- Composed: pappydapimp69__seven/E1, pappydapimp69__seven/E48, pappydapimp69__seven/E20, pappydapimp69__seven/E40
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-12__rebuilt-witness-list-forks-a-fakes-lie-across-reload.py
- Prediction: verbatim 0.000 change; reorder-rebuilt index pick at least 0.70; drop-one at least
  0.60; min-hash reorder 0.000 and drop at most 0.25; canonical sort fixes reorder but drop stays at
  least 0.40; run stream resumes exactly and draw count constant in every case; ask-reload-ask
  identification at least 0.85 under reorder.
- Observed: RESULT: FAIL 8/10; changed verbatim 0.000 reorder 0.797 drop 0.395; minhash reorder
  0.000 drop 0.208; sorted reorder 0.000 drop 0.395; resume+draws constant True
- Scenarios: 1) verbatim save, index pick; 2) reorder rebuild, index pick; 3) drop-one rebuild,
  index pick; 4) reorder rebuild, min-hash; 5) drop-one rebuild, min-hash; 6) built to BREAK the
  claim: reorder rebuild with a canonical id sort, where the fork should vanish; 7) drop-one rebuild
  with canonical sort.
- Link: session; brain train loop round 3; session_01QGT1LfmPHPG99JEGaPhBwB

## E88 — duck must cover total masker power
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][audio][voices]
- What: The duck a must-land hallucinated voice line needs as voices are added, using the published finding
  that same-sex multi-talker masking follows total masker power, after seven E73 and E78 both modelled the
  talker penalty as 1.5 dB per doubling.
- Why built: My review of E73 found its 1.5 dB per doubling was half its own cited 4-5 dB per tripling, and E78
  re-used it. The missing fact was what real listeners do as same-sex voices are added at equal level.
- Design: Brungart, Simpson, Ericson and Scott 2001 (JASA 110:2527), read first-hand: with two or more same-sex
  maskers, performance depended almost exclusively on the overall SNR (linear, r 0.98), not the number of
  talkers, so equal voices add 10 log10(m) dB (3 dB per doubling). Deterministic: 0.60 against one equal
  masker (E73's calibration), linear slope 5/10/15 percent per dB, mono; duck needed for 80 percent.
- Got right: A 6 dB duck carries only 2 to 3 voices in mono at every slope (E73 said 6, E78 said 6 at 10
  percent per dB); 6 voices need 11.0/9.0/8.3 dB at 5/10/15 percent per dB; going from 2 to 6 voices adds
  7.0 dB at every slope, against 3.5 dB under the 1.5 dB per doubling model.
- Where/why it failed: Nothing refuted the predictions; the 7 dB growth is power arithmetic once the paper's
  finding is accepted, and the base (0.60 at 0 dB, linear slope) remains a calibration. The paper also notes
  the second interferer costs more than the first, which this model does not add, so real budgets are tighter.
- Fix: Size the duck against the summed level of all other voices: add 10 log10(number of other voices) dB to
  the duck that works against one voice, so about +7 dB from 2 to 6 voices; or keep must-land scenes to 2 or 3
  voices on phones.
- Why this fix: Listeners hear same-sex chatter as one masker whose loudness is the sum, so each added voice
  costs level whether or not it is loud on its own.
- Rule of thumb: A must-land voice's duck must cover the summed level of the other voices (+3 dB per doubling,
  Brungart 2001): a 6 dB duck carried only 2-3 voices in mono at any slope; 6 voices need 8-11 dB.
- Provenance (verified/assumed): Verified first-hand: Brungart et al. 2001 read from the paper's PDF, and the
  sandbox in this entry (RESULT PASS 4/4; numbers copied from the run). The calibration point is E73's.
- Composed: pappydapimp69__seven/E73, pappydapimp69__seven/E78, pappydapimp69__seven/E65, pappydapimp69__seven/E69
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-12__duck-must-cover-total-masker-power.py
- Prediction: 6 voices at 5 percent per dB need at least 10 dB; a 6 dB duck at 10 percent per dB carries 3 or
  fewer; 2 to 6 voices adds about 7 dB at every slope; the 1.5 dB per doubling model adds under 4.
- Observed: RESULT: PASS 4/4; 6 voices need 11.0/9.0/8.3 dB at 5/10/15%/dB; 6 dB carries 2/3/3; growth 2->6
  voices 7.0 dB vs 3.5 at 1.5/doubling
- Scenarios: 1) slopes 5, 10, 15 percent per dB; 2) 2 to 6 voices; 3) built to BREAK E73/E78: their own 1.5 dB
  per doubling against the power-sum finding.
- Link: session; brain train follow-up on E78 (missing masking data); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-15 · projects/pappydapimp69__seven.md#E103 · compatible · sandboxes/2026-10-15__hallucinated-voices-barely-shrink-a-whistles-range-anywhere.py · observed RESULT: FAIL 1/4; 8 voices shrink range open 1342->886 m, woods23 150->119 m, woods4 493->363 m; per doubling open 0.07, woods23 0.04, woods4 0.05 · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 1 pass 1 (kernel apply; brain challenge masking run first), 2026-10-15

## E87 — conditioned phantoms persist but reach a minority
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][perception][deception]
- What: Checked the conditioned-phantom budget (seven E63, E75, E79) against human data on conditioned
  hallucinations instead of a textbook learner: how fast real ones extinguish and how many people get one.
- Why built: E63 and E75 used symmetric Rescorla-Wagner, E79 showed the answer flips with the learner, and
  only human data can choose. The 2022 Psychological Medicine review of conditioning-evoked hallucinations
  (read first-hand, Table 1) reports Ellson 1942 (n 30): they persisted through extinction trials, even after
  people were told the tone was gone; and in a placebo arm (n 21, 80 trials) 29 percent reported at least one.
- Design: Deterministic. RW with acquisition 0.3 and extinction slowed by r = 1, 4, 10, 12; 60 teaching
  pairings, threshold 0.6; how many consecutive phantoms persist; all-phantom, 1:1 and 2:1 schedules over 12
  phantoms; and the share of all players reached if 29 percent are susceptible.
- Got right: Symmetric RW contradicts the data: phantoms stop after 3, 2 and 1 cue-alone trials at learning
  rates 0.2, 0.3, 0.45. Matching Ellson's persistence (20 phantoms) needs extinction 12x slower, and then an
  all-phantom schedule lands 12 of 12, so E75's two-pairings-per-phantom rule is an artefact of fast extinction.
- Where/why it failed: Nothing refuted my predictions, but the population cap is built in (29 percent susceptible
  means at most 0.29 reached), the 12x is fitted to one old study, and the paradigm is a lab tone, not a game.
- Fix: Treat a conditioned phantom as a bonus that lands for a minority (about three in ten), not as a beat
  the story depends on; never put required information in it; once taught, it can be reused freely for
  the players it reaches, so spend the design effort on the teaching, not on refresh ratios.
- Why this fix: The human data cap who perceives it at all and say it does not wear out fast, which moves
  the risk from 'running out' to 'most players never see it'.
- Rule of thumb: Real conditioned hallucinations persist through extinction (Ellson 1942) but reach a minority
  (29 percent in a placebo arm): design conditioned phantoms as optional extras, not required beats.
- Provenance (verified/assumed): Verified first-hand: the review's Table 1 read from its PDF, and the sandbox
  in this entry (RESULT PASS 4/4; numbers copied from the run). The 29 percent is one 21-person arm.
- Composed: pappydapimp69__seven/E63, pappydapimp69__seven/E75, pappydapimp69__seven/E79, pappydapimp69__seven/E55
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-12__conditioned-phantoms-persist-but-reach-a-minority.py
- Prediction: symmetric RW stops phantoms within 6 cue-alone trials; persistence through 20 needs extinction at
  least 8x slower; at that rate all-phantom lands at least 10 of 12; no schedule reaches over 0.29 of players.
- Observed: RESULT: PASS 4/4; symmetric RW stops after 3/2/1; persistence needs r>=12; fitted all-phantom
  12/12; population share max 0.290
- Scenarios: 1) symmetric RW at three learning rates; 2) slowed extinction r 4, 10, 12; 3) three schedules;
  built to BREAK E75: a learner fitted to Ellson's persistence.
- Link: session; brain train follow-up on E78/E79 (missing human data); session_01KGZvxv8BDgpDMRFTYMfJoJ

## E86 — sway sickness tracks velocity not frequency
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][accessibility][vfx]
- What: Settled the contradiction between seven E83 (replace a breathing sway with a slow 6 second swell)
  and E85 (avoid everything below 0.5 Hz; use 2 Hz jitter) by checking what the published studies vary:
  frequency, or the speed of the moving scene.
- Why built: Both entries rank sway designs by frequency alone. Chen, Bao, Zhao and So 2016 (Ergonomics 59:4,
  read first-hand) held rms velocity constant and found visually induced sickness flat from 0.05 to 0.8 Hz;
  with amplitude held constant, nausea rose with frequency to a peak that moved up as amplitude fell (0.2 Hz
  at 100 m, 0.8 at 25 m, 3.2 at 6.25 m). Diels and Howarth 2013 report 0.2 to 0.4 Hz and reject the 0.06 Hz
  proposal for purely visual motion, which E85's low-peak cells relied on.
- Design: Deterministic. Six designs (breathing sway 0.25 Hz 3 deg; swell 0.15 Hz 3 and 6 deg; jitter 2 Hz
  1 and 0.2 deg; the breath on a 30 percent edge ring), dosed under a frequency-band model (E81/E85 style,
  12 dB per octave outside 0.2-0.4 Hz) and a velocity model (rms angular velocity, Chen's flat response).
- Got right: The models disagree where it matters: the band model puts 1 deg 2 Hz jitter at 0.04 of the
  breath's dose, the velocity model at 2.67x. Under velocity a 2 Hz jitter must stay at or under 0.375 deg to
  match the breath, and the edge ring cuts 70 percent under both.
- Where/why it failed: My prediction that the slow swell at equal amplitude halves the dose missed (0.60x),
  and a swell sized to read as strongly (6 deg) doses 1.20x the breath, so E83's 'use a slow swell' only helps
  if the swell is also small. E85's '2 Hz jitter cuts 85-98 percent' holds only for jitter far smaller than the sway.
- Fix: Budget the angular speed of whole-frame motion (rms degrees per second, times the area moving), not
  its frequency: cap it below the level a playtest finds comfortable, keep jitter under about half a degree,
  move distortion to the edge, and keep the reduce-motion switch where the deep stages begin.
- Why this fix: Speed is what the controlled study found sickness follows across 0.05 to 0.8 Hz, and a speed
  budget covers slow drift, breathing sway and jitter with one number instead of three frequency rules.
- Rule of thumb: Hallucination sway sickens by speed, not period: with velocity held equal, sickness was flat
  from 0.05 to 0.8 Hz (Chen 2016), so 1 deg 2 Hz jitter doses 2.7x a 3 deg breathing sway; cap rms deg/s and area.
- Provenance (verified/assumed): Verified first-hand: Chen et al. 2016 read in full from the paper's PDF, and
  the sandbox in this entry (RESULT FAIL 3/4 of my predictions; numbers copied from the run). Chen tested
  fore-and-aft translation, not roll; the degree amplitudes are my design inputs.
- Composed: pappydapimp69__seven/E83, pappydapimp69__seven/E85, pappydapimp69__seven/E81, ideas:ACCESSIBILITY/motion-comfort/keep-repetitive-screen-motion-out-of-the-2-to-5-second-period-band
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-12__sway-sickness-tracks-velocity-not-frequency.py
- Prediction: the two models disagree on 1 deg jitter vs the breath; under velocity a same-amplitude slow
  swell halves the dose but a 6 deg swell is within 25 percent of the breath; jitter must be 0.4 deg or less;
  the edge ring cuts 70 percent in both.
- Observed: RESULT: FAIL 3/4; model B vs breath: swell 0.60x, swellbig 1.20x, jitter1deg 2.67x, microjitter
  0.53x; model A jitter 0.040 vs breath 1.000; jitter cap 0.375 deg
- Scenarios: 1) breathing sway; 2) slow swells at two amplitudes; 3) jitter at two amplitudes; 4) edge ring;
  built to BREAK the frequency rules: the same designs under the velocity model.
- Link: session; brain train follow-up on the E83/E85 sway contradiction; session_01KGZvxv8BDgpDMRFTYMfJoJ
- Audited: 2026-10-15 · modeled · Read the entry and re-ran its stored sandbox (RESULT: FAIL 3/4 reproduced). Q1: the arithmetic is computed, but every ranking follows from the dose formula chosen: model B sets dose = area x rms angular velocity, so '1 deg 2 Hz jitter doses 2.7x the breath' is just (2.0 x 1.0)/(0.25 x 3.0), not a finding about people. Q2: the Rule claims more than its source covers. Chen, Bao, Zhao & So 2016 (as the sandbox cites) found sickness flat across 0.05 to 0.8 Hz at constant rms velocity, and for fore-and-aft oscillation (metres of travel), not angular screen sway in degrees; the 2 Hz jitter the Rule ranks lies outside that tested band, so 'sickens by speed, not period' is extrapolated exactly where it is applied. The entry is right that frequency-only rankings (E81) hide the amplitude convention - my own E97 found the same flip (at constant pixel amplitude a 0.05 Hz drift beats 2 Hz jitter) - but which convention matches viewers above 0.8 Hz is untested. Q3: a claim about real viewers tested on two hand-written dose models, so modeled. To raise it: measure, or cite a study covering 1-3 Hz angular jitter. · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 5 pass 3 (audit), 2026-10-15

## E85 — sway comfort rules across published peaks and peripheral vection
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][accessibility][vfx][comfort]
- What: Re-verified seven E81's motion-comfort advice for hallucination sway (leave the sickness band, keep
  distortion off the full frame) across every published visual-only sickness peak and a periphery-weighted
  field model, composed with the sound-first curve that decides when visual sway appears in a run.
- Why built: E81 was the only source for the edge between the motion-comfort kernel and the sound-first
  curve, and it fixed the peak at 0.2-0.4 Hz and a linear area term although its own entry notes published
  peaks of 0.06, 0.1, 0.2 and 0.2-0.4 Hz.
- Design: Deterministic. Peak at 0.06, 0.1, 0.2 or 0.3 Hz; roll-off 6 or 12 dB per octave below and
  above (16 cells); dose relative to full-frame 0.3 Hz sway. Field: area-linear (E81) against
  vection drive rising with radius (periphery-weighted), for a 30 percent edge-only ring. Run exposure
  under the linear (0, 1/3, 2/3, 1) and banded (0, 0.1, 0.5, 0.9) sound-first curves.
- Got right: Fast 2 Hz jitter cuts the dose in every cell (85 to 98 percent), and an edge-only vignette
  still cuts 59 percent under periphery weighting (70 under area). The banded curve puts 60 percent of
  the run's visual exposure in the deepest band (linear 50), so comfort settings matter most late.
- Where/why it failed: A slow drift is not a safe alternative. With the peak at 0.06 or 0.1 Hz a 0.05 Hz
  drift is as bad as or worse than in-band sway in 7 of 16 cells (up to 20x). E81's '96 percent' for
  jitter needs a 12 dB per octave upper roll-off; at 6 dB it is 85. My own prediction of a sub-50 percent
  vignette cut was wrong (59).
- Fix: Treat everything below about 0.5 Hz as the risk zone, slow drift included. Make visual sway fast
  small jitter (2 Hz or above, inside the three-flashes rule) or one-off lurches, confine it to the edge,
  and put the reduce-motion switch where the deep bands begin.
- Why this fix: It holds at every published peak and roll-off tested, rather than at one assumed
  weighting, and it puts the opt-out where the sound-first curve concentrates the visual dose.
- Rule of thumb: For hallucination sway, avoid everything below about 0.5 Hz, slow drift included: at a
  0.06-0.1 Hz peak a 0.05 Hz drift dosed as much as in-band sway in 7 of 16 cells, while 2 Hz jitter cut
  85-98 percent and a 30 percent edge vignette 59-70 percent at every peak tested.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL against my
  prediction; numbers copied from the run). The peak values are the published ones E81 lists; the
  roll-off slopes and the periphery weighting are my modelling assumptions.
- Composed: pappydapimp69__seven/E81, ideas:ACCESSIBILITY/motion-comfort/keep-repetitive-screen-motion-out-of-the-2-to-5-second-period-band, ideas:GAME-DESIGN/hallucination-phenomenology/sound-first-then-sight-as-sanity-falls, pappydapimp69__seven/E66
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__sway-comfort-rules-across-published-peaks-and-peripheral-vection.py
- Prediction: 2 Hz jitter cuts at least 90 percent at every peak and slope; a 0.05 Hz drift is at least as
  bad as 0.3 Hz sway when the peak is 0.06 or 0.1 Hz; the vignette cut falls below 50 percent with
  periphery weighting; banded puts at least 55 percent of visual exposure in the deepest band.
- Observed: RESULT: FAIL jitter robust (max 0.151); slow drift as bad or worse than 0.3 Hz sway in 7/16
  cells; vignette cut 70% area vs 59% periphery-weighted; banded puts 60% of visuals in the deepest band
- Scenarios: 1) peak 0.06/0.1/0.2/0.3 Hz; 2) roll-offs 6/12 dB per octave each side; 3) area against
  periphery-weighted field; 4) linear against banded run exposure; 5) built to BREAK the claim: a slow
  drift at a low published peak.
- Link: session; brain train loop after the review of seven E63-E73; session_01QGT1LfmPHPG99JEGaPhBwB
- Reverified: 2026-10-12 · fail · sandboxes/2026-10-12__rebuild-seven-e85-velocity-model.py · observed RESULT: FAIL 3/4; model B vs breath: swell 0.60x, swellbig 1.20x, jitter1deg 2.67x, microjitter 0.53x; model A jitter 0.040 vs breath 1.000; jitter cap 0.375 deg · Rebuilt from the claim with a different dose model and checked its sources. E85's low peaks (0.06 and 0.1 Hz) come from a list E81 copied; Diels and Howarth 2013 measured purely visual fore-aft motion and found 0.2-0.4 Hz with LESS sickness lower down, explicitly rejecting the 0.06 Hz crossover proposal, and Chen et al. 2016 (read in full) found sickness flat from 0.05 to 0.8 Hz when rms velocity is held constant and rising with frequency when amplitude is held constant. So the frequency-band dose E85 sweeps is the wrong variable. Under a velocity dose (rms angular speed times area) a 1 deg 2 Hz jitter is 2.67x a 3 deg 0.25 Hz breathing sway, not the 85-98 percent cut E85 reports; the jitter only wins below about 0.375 deg. E85's 'avoid slow drift too' survives (a slow drift at equal speed is no safer), and its edge-vignette cut survives (70 percent under both models). Fail because its headline fix (2 Hz jitter) can be worse than the sway it replaces at ordinary amplitudes. · session; brain train follow-up on the E83/E85 sway contradiction; session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E86 · incompatible · sandboxes/2026-10-12__sway-sickness-tracks-velocity-not-frequency.py · observed RESULT: FAIL 3/4; model B vs breath: swell 0.60x, swellbig 1.20x, jitter1deg 2.67x, microjitter 0.53x; model A jitter 0.040 vs breath 1.000; jitter cap 0.375 deg · session; brain train follow-up on the E83/E85 sway contradiction; session_01KGZvxv8BDgpDMRFTYMfJoJ

## E84 — merging keyed sets namespace every key not just the fallback
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [state][architecture][viz][data]
- What: brain-pitch E3 (when two independently keyed collections are merged into one namespace, a
  generic fallback bucket such as 'other' collides) combined with sandbox-edges E23 (namespace a shared
  key by writer identity), testing whether renaming only the fallback bucket is enough.
- Why built: E3's natural fix is to rename the fallback. E23 says the general rule is to namespace by
  writer. If the two sources' real ids can also overlap, the narrow fix leaves the same bug in place.
- Design: Deterministic: source A has forest, river and other; source B has forest, camp and other. A merge
  keyed by id where a later write overwrites the bucket label and appends members (the bug shape in E3).
  Counted members filed under a label from the other source, for a naive merge, fallback-only
  namespacing, every key namespaced by source, and a control with no shared ids.
- Got right: Namespacing every key by its source misfiles nothing, and with no shared ids and a single
  fallback even a naive merge is clean, so the fix is needed exactly when ids can overlap.
- Where/why it failed: The narrow fix is not enough: namespacing only the fallback still misfiles 2
  members (the shared 'forest' bucket), against 4 for the naive merge. E3's rule of thumb points at the
  fallback, but the fallback is only the most visible overlapping key.
- Fix: When merging independently built keyed collections, prefix every key with its source (or keep
  separate maps per source) unless the ids are guaranteed globally unique, and test with a fixture
  where a real id appears in both sources.
- Why this fix: It applies E23's writer-identity rule to E3's case, removing the whole class of
  collision instead of the instance that happened to surface.
- Rule of thumb: When merging two independently keyed collections, namespace every key by its source,
  not just the fallback bucket: renaming only 'other' still misfiled 2 of 4 members once a real id
  appeared in both; test with a fixture that shares a real id.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 4/4
  predictions held; numbers copied from the run). The overwrite-and-append merge is the bug shape E3
  describes, modelled here, not taken from brain-pitch's code.
- Composed: pappydapimp69__brain-pitch/E3, local__sandbox-edges/E23
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__merging-keyed-sets-namespace-every-key-not-just-the-fallback.py
- Prediction: a naive merge misfiles members; fallback-only namespacing still misfiles when real ids
  overlap; full namespacing misfiles none; with no shared ids a naive merge misfiles none.
- Observed: RESULT: PASS 4/4; misfiled naive 4, fallback-only 2, full 0, no-overlap 0
- Scenarios: 1) naive merge; 2) fallback-only namespacing; 3) every key namespaced; 4) built to BREAK the
  claim: no shared ids, where namespacing should not matter.
- Link: session; brain train auto pass 2 (edge); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-12 · pass · sandboxes/2026-10-12__rebuild-seven-e84-namespace-every-key-merge.py · observed RESULT: PASS shared id: naive 6/9, fallback-only 3/9, full 0; no shared id: fallback-only 0; full namespacing splits an intended join · Own fixture: two command registries grouped by category where 'audio' means different things in each (original: two fixed sources with overwrite-label semantics). Misfiled = member grouped with the other source's members. Naive 6/9, fallback-only 3/9, full namespacing 0; with no shared real id fallback-only gives 0. Gap found (break case): when a shared id is a deliberate JOIN (both 'net' mean the same), full namespacing splits a group that should be one; an explicit join list fixes it. The rule holds for independently keyed sets, which is what it states; note the author's 'naive misfiles none with no shared ids' only holds if the fallback buckets do not both exist. · session_01P1LRA5HjMLEFnWXayE2EHx; blind review pass of SEVEN targets, 2026-10-12
- Cited-by: 2026-10-13 · projects/pappydapimp69__brainwork.md#E182 · compatible · sandboxes/2026-10-13__renderer-private-place-list-vs-content-declared-enumeration-mod-orders.py · observed RESULT: PASS checks all true; private undrawn 2 rejected 0; validated rejected 2; union undrawn 0 states 1 wrong 1; last-list-wins undrawn up to 5 states 3; namespaced undrawn 0 wrong 0 states 1. · scheduled brain train session, loop 2 pass 5; session_01Vd1XXerYpxYYjyMDy9FPmH

## E83 — breathing sway for sanity depth sits in the nausea band
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][accessibility][vfx]
- What: Composed the accessibility kernel (whole-screen motion cycling every 2.5 to 5 seconds is the most
  nauseating, worse with more screen moving) with the sound-first-then-sight kernel (visual effects arrive
  in the deep stages and strengthen with depth), for the obvious way to build 'deeper means stronger'.
- Why built: A sanity-linked visual is usually a sway or breathing effect that speeds up as the mind goes.
  Resting to panicked breathing (12 to 30 breaths a minute) is a 5 to 2 second period, which runs straight
  through the band the accessibility kernel warns against.
- Design: Deterministic sweep over the two visual stages (chest-deep, undercurrent), equal and deep-heavy
  time splits. Designs: whole-screen sway synced to breathing 12 to 30 per minute; a slow 10 to 6 second
  swell; the breathing sway on the screen edge only (area 0.15); fast 0.15 second jitter; one-off lurches.
  Exposure = moving screen area times time spent with a period in 2.5 to 5 seconds.
- Got right: The breathing sway spent 0.67 of visual-stage time in the band (0.42 of all play time when
  players linger deep). Edge-only cut exposure from 0.333 to 0.050 (85 percent), and the slow swell,
  jitter and lurches never entered the band.
- Where/why it failed: Nothing refuted the predictions, but the in-band shares are range arithmetic over
  the chosen breathing rates and periods; whether real players get sick is not modelled.
- Fix: Do not sync a whole-screen sway to a breathing rate that rises with depth. Show depth with a slow
  swell (6 seconds or longer), edge-only distortion, fast small jitter, or one-off lurches, and keep a
  reduced-motion switch.
- Why this fix: It keeps the 'stronger as you sink' progression while staying out of the period band the
  accessibility kernel names, and edge-only keeps most of the look for a fraction of the exposure.
- Rule of thumb: A breathing-synced sway that quickens as sanity falls (12 to 30 breaths a minute, 5 to 2
  seconds) spends two thirds of the visual stages in the 2.5 to 5 second nausea band; use slow swells,
  edge-only distortion or lurches instead.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 4/4; numbers
  copied from the run). Breathing rates and effect periods are assumed design inputs.
- Composed: ideas:ACCESSIBILITY/motion-comfort/keep-repetitive-screen-motion-out-of-the-2-to-5-second-period-band, ideas:GAME-DESIGN/hallucination-phenomenology/sound-first-then-sight-as-sanity-falls
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__breathing-sway-for-sanity-depth-sits-in-the-nausea-band.py
- Prediction: breathing sway keeps at least 60 percent of visual time in band; edge-only cuts exposure at
  least 80 percent; a 10 to 6 second swell never enters the band; a deep-heavy split raises the all-play share.
- Observed: RESULT: PASS 4/4; breath in-band 0.67 of visual time (all play 0.33 equal, 0.42 deep-heavy); edge
  exposure 0.050 vs 0.333; swell 0.00; jitter 0.00
- Scenarios: 1) equal time per stage; 2) deep-heavy time; 3) five effect designs; built to BREAK the claim:
  the slow swell and jitter, which should stay out of the band.
- Link: session; brain train auto pass 2 (aim edge; edge-mode pick was the saturated age-cutoff family); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E86 · incompatible · sandboxes/2026-10-12__sway-sickness-tracks-velocity-not-frequency.py · observed RESULT: FAIL 3/4; model B vs breath: swell 0.60x, swellbig 1.20x, jitter1deg 2.67x, microjitter 0.53x; model A jitter 0.040 vs breath 1.000; jitter cap 0.375 deg · session; brain train follow-up on the E83/E85 sway contradiction; session_01KGZvxv8BDgpDMRFTYMfJoJ

## E82 — rain barrel catches a sliver route overflow to a rain garden
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [garden][water][sizing]
- What: The rain-barrel sizing kernel (gallons = roof square feet x inches of rain x 0.623, with a
  first-flush diversion) re-verified and combined with the passive water-harvesting kernel (route
  runoff to a rain garden sized at drainage area / 6 to / 8) and the drip-irrigation kernel, to ask how
  much of a year's roof runoff one barrel actually catches and how far a full barrel goes.
- Why built: The kernel was never applied by a lesson. Its numbers can be checked exactly, and the
  practical question it raises (is a barrel enough, or should overflow go to a rain garden?) needs the
  two sibling kernels together.
- Design: Exact arithmetic. The 0.623 factor from cubic inches per square-foot-inch over cubic inches per
  US gallon; first flush at 0.5 litres per square metre (clean roof) and 2 mm depth (dirty) for 1,000
  square feet. An assumed temperate year of 70 storms totalling about 40 inches; 10 percent gutter loss;
  12.5 gallons first flush per storm; barrels of 55, 200 and 500 gallons emptied between storms (a best
  case); a 10-emitter, 1 gph drip bed.
- Got right: The kernel's numbers hold exactly: 144/231 = 0.6234, and the first-flush range for 1,000
  square feet is 12.3 to 49.1 gallons (kernel: 12.5 to 50). A full 55-gallon barrel runs the drip bed
  for 5.5 hours, so a barrel is a top-up, not a supply.
- Where/why it failed: My predictions about capture were too pessimistic: even in this best case a 55
  gallon barrel catches 19.5 percent of net annual runoff (not under 15), and a 500 gallon tank 76.0
  percent (not under 60), because most storms are small and fit. The best-case emptying assumption
  inflates every figure, so real capture is lower.
- Fix: Size storage for the small storms that dominate the count, and plan overflow on purpose: send
  everything a barrel cannot hold to a rain garden of about 125 to 167 square feet for a 1,000 square foot
  roof (area / 8 sandy to / 6 clay) rather than letting it spill at the foundation.
- Why this fix: It uses each kernel for what it is good at: the barrel for clean water on dry days, the
  rain garden for volume, and the drip bed's demand to show how little a barrel holds.
- Rule of thumb: One 55-gallon barrel catches about a fifth of a 1,000 square foot roof's yearly runoff
  even when emptied between storms, and runs a 10-emitter drip bed for about 5.5 hours; pair it with a
  rain garden of roof area / 8 to / 6 for the overflow.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 3/5
  predictions held; numbers copied from the run). The conversion and first-flush figures are exact
  arithmetic; the storm mix and emptying assumption are mine.
- Composed: ideas:GARDEN/water/rain-barrel-sizing-plus-first-flush-diverter, ideas:GARDEN/water/passive-landscape-water-harvesting, ideas:GARDEN/water/drip-irrigation-efficiency-plus-design-specs
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__rain-barrel-catches-a-sliver-route-overflow-to-a-rain-garden.py
- Prediction: 0.623 reproduces within 0.001; a 55 gallon barrel catches under 15 percent; a 500 gallon
  tank under 60 percent; one full barrel runs the drip bed under 6 hours.
- Observed: RESULT: FAIL 3/5; factor 0.6234; first flush 12.3/49.1 gal; caught 55 19.5% 200 46.9% 500
  76.0%; drip 5.5 h
- Scenarios: 1) the conversion factor; 2) first flush clean and dirty; 3) 55, 200 and 500 gallon storage;
  4) drip run time; 5) built to BREAK the claim: whether a single barrel is really negligible (it catches
  a fifth).
- Link: session; brain train auto pass 1 (kernel); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-12 · pass · sandboxes/2026-10-12__rebuild-seven-e82-barrel-demand-limited.py · observed RESULT: FAIL 2/3; best case 55/200/500 0.158/0.465/0.792; 55 gal at 2/10/25 gal/day 0.047/0.141/0.157; 500 gal at 2 gal/day 0.067 (the miss is mine: a small barrel refills to full from most storms, so demand barely limits it) · Rebuilt from the claim with my own storm fixture: 70 storms totalling 40 inches but with exponential storm depths (deterministic quantiles) and irregular 2-12 day gaps, E82's 10 percent gutter loss and 12.5 gallon first flush. Its best-case numbers reproduce on a different distribution: a 55 gallon barrel emptied between storms caught 0.158 of net runoff (E82: about a fifth, 0.195) and 500 gallons 0.792 (E82: 0.760). E82 states that emptying between storms is a best case; draining only by garden demand shows how much: at 10 gallons a day the 55 gallon barrel still caught 0.141, but a 500 gallon tank only 0.244, and at 2 gallons a day 0.067. So the rule's 'about a fifth' holds for a small barrel, but bigger tanks only pay off with matching demand; filed as a separate lesson. · session; brain train deeper (review + follow-up of seven E82); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E92 · compatible · sandboxes/2026-10-12__barrel-capture-is-capped-by-demand-not-tank-size.py · observed RESULT: FAIL 2/3; best case 55/200/500 0.158/0.465/0.792; 55 gal at 2/10/25 gal/day 0.047/0.141/0.157; 500 gal at 2 gal/day 0.067 · session; brain train deeper (review + follow-up of seven E82); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Reverified: 2026-10-12 · pass · sandboxes/2026-10-12__rebuild-seven-e82-rain-barrel-capture-share.py · observed RESULT: PASS barrel share temperate 0.168 arid 0.152 drizzly 0.212; K 0.6234; drip 5.5 h; 500 gal 0.791 (my <70% and drizzly >30% refuted) · Own fixture: three synthetic climates with exponential storm depths from an LCG (temperate 100 storms/42 in, arid 30/13 in, drizzly 150/43 in; original: one hand-built 70-storm mix), 0.05 in first flush, barrel emptied between storms. 144/231 = 0.6234 gal per sq ft-in (0.623 holds). One 55 gal barrel caught 0.168 / 0.152 / 0.212 - about a fifth in all three, so the rule is robust to climate (my prediction that a drizzly climate would push it past 30% was refuted). A full barrel runs 10 x 1 gph emitters 5.5 h. Not reproduced: the author's prediction that a 500 gal tank catches under 60% - here 0.77-0.79. The rain-garden /6 to /8 sizing is quoted, not tested. · session_01P1LRA5HjMLEFnWXayE2EHx; blind review pass of SEVEN targets, 2026-10-12

## E81 — hallucination sway out of the sickness band and off the full frame
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][accessibility][vfx][comfort]
- What: Motion sickness from hallucination distortion effects (screen sway, warping, field-of-view
  pulsing): which choices of frequency and screen coverage cut the sickness dose, so the visual stages
  of the owner's sound-first progression do not make players ill.
- Why built: Brain had no lesson on visually induced motion sickness, and the art style's late, visual
  stages are exactly where sway and warp would go. A related study of a commercial console game
  reported 67 percent of adults feeling motion sick (search summary), so this is not an edge case.
- Design: Exact arithmetic. Visual oscillation is most nauseating at 0.2 to 0.4 Hz (Diels and Howarth
  2013, abstract); weighting assumed flat there, -6 dB per octave below and -12 dB per octave above (the
  ISO 2631-1 shape moved to that band); dose proportional to weight x amplitude x moving field fraction
  x square root of duration. Compared full-frame sway at 0.3 Hz with a 0.05 Hz drift, 2 Hz jitter, and
  the same confined to a 30 percent vignette.
- Got right: Moving the sway out of the band to 2 Hz jitter cuts the dose 96 percent, confining it to a
  vignette cuts it 70 percent, and both together leave 0.012 of the reference; a very slow 0.05 Hz drift
  helps less (75 percent), because the weighting falls more gently below the band than above it.
- Where/why it failed: Nothing in the run refuted the predictions, but the result follows from the
  assumed weighting shape and the linear field-of-view term; published peaks for visual-only motion
  disagree (0.06, 0.1, 0.2 or 0.2 to 0.4 Hz). The opt-out check in my prediction was not run. Fast
  jitter that changes brightness must also respect the three-flashes rule (seven E57).
- Fix: Keep any repetitive hallucination sway out of roughly 0.05 to 0.5 Hz (periods of 2 to 20 seconds,
  worst about 2.5 to 5); prefer short one-off lurches, fast small jitter, or edge-only distortion; and
  provide an off switch or a slider, honouring the browser's reduced-motion preference.
- Why this fix: It follows Xbox Accessibility Guideline 117 (avoid repetitive on-screen sway or make it
  optional) and the published frequency band, while keeping the visual stages' unease.
- Rule of thumb: Keep hallucination sway out of the motion-sickness band (about 0.2 to 0.4 Hz, a 2.5 to
  5 second period) and off the full frame: in a weighted dose model 2 Hz jitter cut the dose 96 percent
  and a 30 percent vignette 70 percent; always offer a reduce-motion switch.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 3/3
  predictions held; numbers copied from the run). The Xbox guideline was read on its page; the
  frequency findings come from study abstracts; the weighting shape is my assumption.
- Composed: pappydapimp69__seven/E57, ideas:GAME-DESIGN/hallucination-phenomenology/sound-first-then-sight-as-sanity-falls
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__hallucination-sway-out-of-the-sickness-band-and-off-the-full-frame.py
- Prediction: 2 Hz instead of 0.3 Hz cuts the dose at least 90 percent; a 30 percent vignette at least 60
  percent; a 0.05 Hz drift cuts less than 2 Hz jitter.
- Observed: RESULT: PASS 3/3; relative doses full-frame sway 0.3 Hz 1.000; slow drift 0.05 Hz 0.251;
  jitter 2 Hz 0.040; vignette-only 0.300; vignette-only jitter 2 Hz 0.012
- Scenarios: 1) full-frame 0.3 Hz; 2) 0.05 Hz drift; 3) 2 Hz jitter; 4) vignette-only; 5) built to BREAK
  the claim: whether a very slow drift is as safe as fast jitter (it is not).
- Link: session; gap loop on motion sickness in hallucination effects, 2026-10-12; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E85 · compatible · sandboxes/2026-10-12__sway-comfort-rules-across-published-peaks-and-peripheral-vection.py · observed RESULT: FAIL jitter robust (max 0.151); slow drift as bad or worse than 0.3 Hz sway in 7/16 cells; vignette cut 70% area vs 59% periphery-weighted; banded puts 60% of visuals in the deepest band · session; brain train loop after the review of seven E63-E73; session_01QGT1LfmPHPG99JEGaPhBwB
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E86 · incompatible · sandboxes/2026-10-12__sway-sickness-tracks-velocity-not-frequency.py · observed RESULT: FAIL 3/4; model B vs breath: swell 0.60x, swellbig 1.20x, jitter1deg 2.67x, microjitter 0.53x; model A jitter 0.040 vs breath 1.000; jitter cap 0.375 deg · session; brain train follow-up on the E83/E85 sway contradiction; session_01KGZvxv8BDgpDMRFTYMfJoJ
- Audited: 2026-10-12 · modeled · Read the entry and its stored sandbox and re-ran it (RESULT PASS 3/3). The claim is about real players' motion sickness, but every number is set by the ASSUMED weighting: W is flat 0.2-0.4 Hz with -6/-12 dB per octave, so the 96% cut at 2 Hz and the 70% vignette cut (dose linear in moving area) follow from the inputs, not from data. Amplitude is never said to be pixels, velocity or acceleration. Sources re-checked: Diels & Howarth 2013, Human Factors 55(3):595-604 - VIMS peaks 0.2-0.4 Hz, but for FORE-AND-AFT optical flow (dot fields, 0.025-1.6 Hz), not lateral sway or warp; Xbox Accessibility Guideline 117 'Visual Distractions and Motion Settings' does ask for opt-outs of camera shake, head bob, sway and repetitive screen motion - correct. My own model (ISO 2631-1 Wf table from memory on weighted acceleration) shows the convention matters: at constant pixel amplitude 2 Hz cuts 90% but a 0.05 Hz drift cuts 99%, reversing the entry's 'drift cuts less than jitter'; filed as a new lesson. Keep the reduce-motion switch; treat the percentages as illustrative. · session_01P1LRA5HjMLEFnWXayE2EHx; blind review pass of SEVEN targets, 2026-10-12
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E97 · incompatible · sandboxes/2026-10-12__sway-amplitude-convention-flips-drift-vs-jitter.py · observed RESULT: PASS 2Hz cut D 0.896 V 0.984 A 0.998; 0.05Hz cut D 0.993 A 0.763 · session_01P1LRA5HjMLEFnWXayE2EHx; review pass of SEVEN targets, gap lessons, 2026-10-12

## E80 — voice time share is a population claim not per player
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][audio][balance]
- What: Whether 'voices dominate hallucination time' (seven E71) holds per person or only across a
  population, once the full published voice-duration and frequency mix is used.
- Why built: E71 swept voice episodes of 30 to 180 minutes only, while McCarthy-Jones 2014 reports
  that 43 percent of voice-hearers have voices lasting minutes or seconds.
- Design: Exact weighted sum over the McCarthy-Jones 2014 duration mix (seconds 12, minutes 31,
  hours 59 percent) and frequency mix (constant 48, 11-20 a week 26, daily 16, 0-5 a week 10 percent),
  with visions of 0.1 to 5 minutes at 1 to 50 a week (Waters 2014: seconds to several minutes, rare
  to frequent). Auditory share of hallucinating minutes, per person and pooled.
- Got right: Pooled over people, voices hold at least 0.888 of hallucinating time in every corner,
  above the 0.686 prevalence share, so E71's bed-and-events advice is sound for a population.
- Where/why it failed: Per person it does not hold: the lowest share is 0.002, and up to 28 percent of
  voice-hearers fall below the prevalence share when visions are long and frequent; E71's 0.766 floor
  came from cutting the short-voice half of the published durations out of its sweep.
- Fix: Keep sound as the default bed, but give SEVEN a vision-led profile too (short, sparse voices
  with frequent visions) rather than one mix for every player; sweep the full published range before
  quoting a floor.
- Why this fix: It matches the spread the sources actually report and stops the design from
  presenting a population average as everyone's experience.
- Rule of thumb: 'Voices dominate hallucination time' is a population claim: pooled it holds (at least
  0.888), but up to 28 percent of voice-hearers in the published mix are vision-led by time, so
  sweep the full duration range and allow a vision-led profile.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL; numbers
  copied from the run); the duration, frequency and prevalence figures were read on the cited papers
  on PubMed Central; treating 'constant' as half of waking time is my choice.
- Composed: pappydapimp69__seven/E71, pappydapimp69__seven/E62
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-12__voice-time-share-is-a-population-claim-not-per-player.py
- Prediction: pooled time share above prevalence in every corner; the per-person floor drops well
  below 0.75 once seconds and minutes voices are included.
- Observed: RESULT: FAIL pop share >= 0.888 everywhere; lowest person 0.002 (vision 5 min x 50/wk);
  up to 0.28 of voice-hearers below the prevalence share
- Scenarios: 1) vision 0.1/1/5 minutes; 2) vision 1/7/50 a week; 3) the full voice duration and
  frequency mix; 4) built to BREAK the claim: long frequent visions against short rare voices.
- Link: session; blind rebuild review of seven hallucination lessons E63-E73; session_01QGT1LfmPHPG99JEGaPhBwB

## E79 — phantom budget depends on the assumed learner
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][perception][pacing]
- What: Whether a conditioned-phantom schedule's budget (how many cue-alone phantoms land, and whether
  longer teaching buys more) survives a change of learning model, after seven E63 priced it on
  Rescorla-Wagner alone.
- Why built: E63's 'all-phantom lands 1 to 2 of 12 however long the teaching; budget one honest
  pairing per phantom' came from one RW point (alpha 0.3, threshold 0.6) and was never fitted to players.
- Design: Exact, no RNG. RW over alpha 0.15/0.3/0.5 and threshold 0.5/0.6/0.7, and a Beta-count
  Bayesian learner (belief = paired/(paired+unpaired)) at threshold 0.6/0.7; teaching 3/10/20; 12 later
  cues all-phantom, alternating, or one real per four.
- Got right: Under every learner a phantom needs some honest teaching first, and under RW an
  alternating schedule never does worse than all-phantom.
- Where/why it failed: The numbers and the 'however long' clause are learner artefacts: only 2 of 9
  RW cells give E63's counts, and under the Beta learner 20 pairings buy 9 to 12 all-phantom landings
  against 1 to 2 after 3, with all-phantom beating alternating.
- Fix: Do not fix a pairing-per-phantom ratio from a model; schedule phantoms adaptively from play
  data (track how often players react to a cue-alone event) and keep honest pairings as the refill.
- Why this fix: Two textbook learners disagree on the very direction of the effect of longer
  teaching, so only player data can set the ratio.
- Rule of thumb: A conditioned-phantom budget is a readout of the learner you assume: RW says long
  teaching buys nothing (1 to 2 of 12), a Bayesian count says 20 pairings buy 9 to 12; tune the
  ratio from play data, not from either model.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL; numbers
  copied from the run). Both learners are textbook models, assumed stand-ins for players.
- Composed: pappydapimp69__seven/E63
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-12__phantom-budget-depends-on-the-assumed-learner.py
- Prediction: E63's counts move under other RW rates and thresholds; under a Beta-count learner 20
  pairings buy at least 2 more all-phantom landings than 3.
- Observed: RESULT: FAIL rw cells off claim 7/9; beta thr 0.6 all-phantom 2/7/12 at teach 3/10/20,
  alternating 6/6/6
- Scenarios: 1) RW 3x3 grid; 2) Beta learner thresholds 0.6/0.7; 3) teach 3/10/20 under three
  schedules; 4) built to BREAK the claim: the Beta learner with long teaching.
- Link: session; blind rebuild review of seven hallucination lessons E63-E73; session_01QGT1LfmPHPG99JEGaPhBwB
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E87 · incompatible · sandboxes/2026-10-12__conditioned-phantoms-persist-but-reach-a-minority.py · observed RESULT: PASS 4/4; symmetric RW stops after 3/2/1; persistence needs r>=12; fitted all-phantom 12/12; population share max 0.290 · session; brain train follow-up on E78/E79 (missing human data); session_01KGZvxv8BDgpDMRFTYMfJoJ

## E78 — must land voice duck size turns on psychometric slope
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][audio][voices][mobile]
- What: How big a level duck a must-land hallucinated voice line needs, swept across the published
  range of speech-in-speech psychometric slopes (5 to 15 percent per dB) instead of E73's fixed 10.
- Why built: The review of seven E73 found its '6 dB duck, mono carries 6, headphones about 4' advice
  is the readout of an assumed 10 percent per dB slope, the one parameter the advice turns on.
- Design: Logistic and linear psychometric functions calibrated so one equal mono talker lands 0.60;
  1.5 dB per doubling of talkers; spatial release 6/9/12 dB (half beyond 3 maskers), none in mono;
  slopes 5, 10, 15 percent per dB; budgets uncapped; target 80 percent.
- Got right: Mono with no duck fits no competing voice at 80 percent at every slope and shape, so
  'never rely on an unducked must-land line on a phone' is robust.
- Where/why it failed: The duck size is not robust: at 5 percent per dB a 6 dB duck lets mono carry
  only 2 to 3 voices and 6 voices need 7.5 to 8.5 dB; headphones at low release carry 2 to 3, not 4.
- Fix: Duck must-land lines 8 to 9 dB above the other voices (the shallow-slope requirement), or
  measure the slope with a short listening test on the real lines before tuning the duck down.
- Why this fix: It holds across the whole published slope range, so the advice no longer depends on
  one assumed constant; erring loud costs only some texture voices.
- Rule of thumb: Size a must-land voice duck for the shallow end of the speech psychometric slope: at
  5 percent per dB mono needs about 8.5 dB to carry 6 voices (6 dB carries 2 to 3); 6 dB is only
  enough if the slope is 10 percent per dB or steeper.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 1/5 of the
  E73 claims held; numbers copied from the run). The slope range and masking figures are the published
  ranges given for the review; the psychometric shapes are my modelling choice.
- Composed: pappydapimp69__seven/E73, pappydapimp69__seven/E65
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-12__must-land-voice-duck-size-turns-on-psychometric-slope.py
- Prediction: at 5 percent per dB a 6 dB duck gives mono at most 3 voices at 80 percent; headphones
  at low release at most 3; at 15 percent per dB mono with 6 dB about 8.
- Observed: RESULT: FAIL 1/5 held; at 5%/dB mono+6dB carries [2, 3] (log/lin), duck for 6 voices
  [8.5, 7.5] dB; 15%/dB mono+6dB 8/9
- Scenarios: 1) logistic slopes 5/10/15; 2) linear slopes 5/10/15; 3) release 6/9/12 dB; 4) built to
  BREAK the claim: the 5 percent per dB slope.
- Link: session; blind rebuild review of seven hallucination lessons E63-E73; session_01QGT1LfmPHPG99JEGaPhBwB
- Reverified: 2026-10-12 · fail · sandboxes/2026-10-12__rebuild-seven-e78-power-sum.py · observed RESULT: PASS 4/4; 6 voices need 11.0/9.0/8.3 dB at 5/10/15%/dB; 6 dB carries 2/3/3; growth 2->6 voices 7.0 dB vs 3.5 at 1.5/doubling (my predictions held; they refute E78's numbers) · Rebuilt with the talker penalty taken from Brungart, Simpson, Ericson and Scott 2001 (JASA 110:2527, read first-hand): with two or more same-sex maskers performance depended almost exclusively on overall SNR (r 0.98), so equal voices cost 10 log10(m) dB, 3 dB per doubling. E78 kept E73's 1.5 dB per doubling, which my E73 review had already found was half E73's own cited figure. With the published penalty, E78's 'a 6 dB duck is enough if the slope is 10 percent per dB or steeper' fails: 6 dB carries 3 voices at 10 and 15 percent per dB and 2 at 5; and its '8.5 dB carries 6 voices at 5 percent per dB' becomes 11.0 dB. E78's robust half holds: mono with no duck fits no competing voice at 80 percent. Different from E78: linear-in-SNR curve (Brungart's own finding) instead of logistic and linear, power-sum penalty instead of per-doubling constant. · session; brain train follow-up on E78 (missing masking data); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E88 · incompatible · sandboxes/2026-10-12__duck-must-cover-total-masker-power.py · observed RESULT: PASS 4/4; 6 voices need 11.0/9.0/8.3 dB at 5/10/15%/dB; 6 dB carries 2/3/3; growth 2->6 voices 7.0 dB vs 3.5 at 1.5/doubling · session; brain train follow-up on E78 (missing masking data); session_01KGZvxv8BDgpDMRFTYMfJoJ

## E77 — fade to silence ends hopeless searches at small rescue cost
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][disappearance][rescue][missing]
- What: A fair test of the owner's decision to let a missing member's call fade to silence (a time
  limit) instead of flooring it (seven E27): what fading buys, and what it costs, for a player who goes
  out on every night a call is heard.
- Why built: The owner's decision had no supporting evidence after seven E28 failed review, while E27
  (the floor) was confirmed. Neither lesson measured the one thing a time limit is for: ending searches
  that can no longer succeed.
- Design: Exact computation over 12 nights. Call chance 0.9 x 0.6^n (fade) or the same floored at 0.25.
  The player searches on every night a call is heard; a search finds with 0.6 (shallow), 0.1 (deep) or
  0.02 (hopeless: the member drifted beyond reach). Measured rescue probability and expected search
  nights after night 5.
- Got right: Fading ends hopeless searches: late search nights fall from 1.647 to 0.163 (90 percent) when
  the member is beyond reach, and from 1.286 to 0.136 in the deep case, so a time limit stops the
  player sinking nights into a search the world has already lost.
- Where/why it failed: The price is higher than I predicted: fading costs about 0.13 of rescue
  probability even in the shallow case (0.814 vs 0.942), not 0.02 or less, because a player who only
  goes out on a call stops going out once the calls thin. Deep: 0.206 vs 0.337.
- Fix: If the fade is kept (the owner's choice), pair it with a cue that keeps shallow rescues alive
  without a call, such as the last bearing heard marked in the world or a companion who remembers
  where it came from, so the fade ends hopeless searches without silencing recoverable ones.
- Why this fix: It keeps what fading buys (no endless hopeless nights) and attacks its main cost (lost
  shallow rescues), instead of choosing between them.
- Rule of thumb: Letting a missing member's call fade to silence ends hopeless searches (late search
  nights 1.647 to 0.163) but costs about 0.13 of rescues even when they are easy to find, because
  call-following players stop searching; pair the fade with a lasting non-call cue.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 2/3
  predictions held; numbers copied from the run). The call-following policy and find rates are
  assumptions; the fade and floor curves are E27's.
- Composed: pappydapimp69__seven/E27, pappydapimp69__seven/E28, pappydapimp69__seven/E37
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__fade-to-silence-ends-hopeless-searches-at-small-rescue-cost.py
- Prediction: hopeless case, fade cuts late search nights by at least 70 percent; shallow case, fade
  costs at most 0.02 rescue probability; deep case, fade costs at least 0.10.
- Observed: RESULT: FAIL 2/3; shallow: rescue 0.814/0.942 late 0.034/0.205; deep: rescue 0.206/0.337
  late 0.136/1.286; hopeless: rescue 0.044/0.077 late 0.163/1.647 (fade/floor)
- Scenarios: 1) shallow; 2) deep; 3) hopeless; 4) built to BREAK the claim: the shallow case, where fade
  was predicted to be nearly free (it was not).
- Link: session; fair test of the owner's fade decision, 2026-10-12; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-12 · fail · sandboxes/2026-10-12__rebuild-seven-e77-fade-to-silence-cost.py · observed RESULT: FAIL hopeless late nights 2.450->0.000; shallow cost 0.0288; deep cost 0.126; mid 0.139; easy-case 0.13 not reproduced · Own fixture: 14 nights; call heard 1.0 for nights 1-3 then falling 0.2 a night, FLOOR at 0.35 vs FADE to 0 by night 8 (original: 0.9 x 0.6^n, floor 0.25, 12 nights); find chance per search 0 / 0.5 / 0.2 / 0.08. Fade cut hopeless late search nights 2.45 to 0 (100%), and cost 0.126-0.139 of rescues on mid and deep cases, matching the rule's ~0.13. But on the EASY case it cost 0.029, not ~0.13, so the rule's 'even when they are easy to find' did not reproduce (and the author's own shallow <= 0.02 missed narrowly too). The cost scales with how hard the find is and how fast the fade is - fade is cheaper on easy rescues than the entry says. Extra: a lasting non-call cue (searched 0.21 a night after silence) kept a 40% cut of hopeless late nights (2.45 to 1.47) and won back 59% of the deep-case loss (0.339 to 0.413 of 0.465); filed as a new lesson. · session_01P1LRA5HjMLEFnWXayE2EHx; blind review pass of SEVEN targets, 2026-10-12
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E95 · compatible · sandboxes/2026-10-12__fade-with-a-lasting-cue-keeps-most-rescues.py · observed RESULT: FAIL hopeless late nights 2.450->0.000; shallow cost 0.0288; deep cost 0.126; fade+cue deep 0.413 (floor 0.465, fade 0.339), hopeless late 1.470 · session_01P1LRA5HjMLEFnWXayE2EHx; review pass of SEVEN targets, gap lessons, 2026-10-12

## E76 — sanity penalty cancels only with damping several times steeper
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][sanity][balance][hallucination]
- What: How steep recovery damping at low sanity must be to cancel a sanity penalty on competence,
  found while blind-rebuilding seven E67 (which said easier recovery 'does not undo' the penalty).
- Why built: The rebuild of E67 failed it: on a different fixture, damping of 0.20 per lost level
  brought collapse to x1.21 of a perception-only meter and 0.30 went below it. So damping can undo
  the penalty; the open question is how much it takes.
- Design: Exact Markov chain: sanity 0 to 6 (0 = collapse), 20 encounters, fail 0.28 plus a penalty of
  0.03, 0.06 or 0.10 per lost level, recovery 0.25 rising by x per lost level (capped at 1). Found the
  smallest x (in steps of 0.01) whose collapse rate is at or below the perception-only meter.
- Got right: A mild penalty can be cancelled (0.03 per level needs recovery rising 0.10 per level) and
  so can a moderate one (0.06 needs 0.28): damping roughly 3 to 5 times as steep as the penalty.
- Where/why it failed: A 0.10 per-level penalty cannot be cancelled at all, because recovery hits its
  cap of 1 before it can outrun the failures. So damping is a fix only for mild penalties, and its
  required steepness grows faster than the penalty.
- Fix: Prefer seven E59's original fix (low sanity changes perception, not competence). If a
  competence penalty is kept, keep it mild and pair it with recovery that rises at least about 3 to 5
  times as fast per lost level; never pair damping with a steep penalty.
- Why this fix: It turns E67's blanket 'does not undo' and E59's 'never' into a measured boundary a
  designer can check, while keeping the safest option first.
- Rule of thumb: Easier recovery at low sanity cancels a competence penalty only when it rises about 3
  to 5 times as steeply (0.03 penalty needed 0.10, 0.06 needed 0.28), and a 0.10 penalty cannot be
  cancelled at all; keep competence flat, or the penalty mild and the damping steep.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 3/3;
  numbers copied from the run). The predictions were written after an exploratory probe of the same
  chain, so they are not pre-registered; fail and recovery rates are model inputs.
- Composed: pappydapimp69__seven/E59, pappydapimp69__seven/E67, ideas:GAME-DESIGN/hallucination/sanity-changes-perception-not-competence
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__sanity-penalty-cancels-only-with-damping-several-times-steeper.py
- Prediction: a 0.03 penalty can be cancelled; cancelling needs damping at least 3x the penalty slope
  (0.03 and 0.06); a 0.10 penalty cannot be cancelled with recovery capped at 1.
- Observed: RESULT: PASS 3/3; damping needed pen 0.03: 0.1; pen 0.06: 0.28; pen 0.1: None
- Scenarios: 1) penalty 0.03; 2) penalty 0.06; 3) built to BREAK the claim: penalty 0.10, where damping
  might be expected to win eventually.
- Link: session; follow-up to the blind rebuild of seven E67; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-12 · fail · sandboxes/2026-10-12__rebuild-seven-e76-sanity-penalty-damping-ratio.py · observed RESULT: FAIL shape holds but ratios 27-76x not 3-5x; 0.10 cancelled in set A (b 2.82); my >2x instability prediction held only at a=0.06 (2.67x), not 0.03 (1.70x) · Own exact-DP fixture: 20-level sanity, 60 tasks, success +1 / failure -3, competence c = p0(1 - a(1-s)), passive recovery r = min(1, r0(1 + b(1-s))), breakdown at 0; outcome = expected tasks done; two base-rate sets. The qualitative shape held (a mild penalty can be cancelled, it needs b > a, the cap makes big penalties uncancellable) but the rule's numbers did not: cancelling ratios were 27-29x (set A) and 49-76x (set B), never 3-5x, and a 0.10 penalty WAS cancellable in set A. Iteration 1 (x10 units) gave 28x and 158x. Then compared with the stored sandbox: its docstring carries the PREDICTION of the earlier E67 rebuild, not this entry's; the three checks (>= 3x, 0.10 impossible) were written to match the observed 0.10/0.03 = 3.3x and 0.28/0.06 = 4.7x, so they were not pre-registered. Its units (fail +0.06 per level on a 6-level scale) are not the claim's stated units. The 3-5x band is a constant of that fixture; keep only the shape. · session_01P1LRA5HjMLEFnWXayE2EHx; blind review pass of SEVEN targets, 2026-10-12
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E93 · incompatible · sandboxes/2026-10-12__cancel-ratio-between-two-slopes-is-a-fixture-constant.py · observed RESULT: FAIL shape holds but ratios 27-76x not 3-5x; 0.10 cancelled in set A (b 2.82); between-set difference 1.70x at a 0.03 and 2.67x at 0.06 · session_01P1LRA5HjMLEFnWXayE2EHx; review pass of SEVEN targets, gap lessons, 2026-10-12

## E75 — one to one refresh lets conditioned phantoms die
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][perception][deception]
- What: The refresh rate a conditioned phantom needs in the long run (cue shown, stimulus withheld),
  testing seven E63's fix of one honest pairing per phantom past the 12 cues E63 ran.
- Why built: E63 measured 12 cues right after a teaching burst, so its 4 to 5 landed phantoms could be
  carry-over rather than what the schedule sustains over a run.
- Design: Rescorla-Wagner (assumed model of players), learning rate 0.2/0.3/0.45, perception threshold
  0.5/0.6/0.7, 6 teaching pairings, then 60 cues at real:phantom 1:1, 2:1, 3:1; phantoms counted only in
  cues 31 to 60. Closed form for the association just before a phantom in a k:1 cycle.
- Got right: The closed form matches the run: at 1:1 the association settles at 1/(2-a) (0.588 at a 0.3),
  at 2:1 at 0.776, at 3:1 at 0.865.
- Where/why it failed: E63's fix decays to nothing at its own constants: 1:1 landed 0 of 15 late phantoms
  (0.588 < 0.6), and sustained phantoms in only 4 of 9 rate/threshold cells. 2:1 sustained them in all 9.
- Fix: Schedule at least two honest pairings per phantom across a run, and check the steady-state
  association 1 - (1-a)^k over 1 - (1-a)^(k+1) against the threshold rather than a short window after teaching.
- Why this fix: The steady state, not the teaching burst, decides a long run; a short window measures
  the carry-over and hides that the schedule is draining.
- Rule of thumb: Conditioned phantoms need about two honest pairings each over a run, not one: at 1:1 the
  learned expectation settles at 1/(2-a) (0.588 at a 0.3), under a 0.6 threshold, and landed 0 of 15.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 3/3; numbers
  copied from the run). Rescorla-Wagner stands in for players; real partial reinforcement is untested.
- Composed: pappydapimp69__seven/E63, pappydapimp69__seven/E55
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-12__one-to-one-refresh-lets-conditioned-phantoms-die.py
- Prediction: at a 0.3, threshold 0.6, 1:1 lands 0 phantoms in steady state; 1:1 sustains phantoms in fewer
  than half the cells; 2:1 sustains them wherever threshold <= 0.6.
- Observed: RESULT: PASS 3/3; E63 constants 1:1 late 0/15 (V* 0.588), 2:1 10/10; 1:1 sustains in 4/9 cells;
  2:1 in 9/9
- Scenarios: 1) ratios 1:1, 2:1, 3:1; 2) learning rates 0.2, 0.3, 0.45; 3) built to BREAK E63's fix: a 60-cue
  run read only after teaching wore off.
- Link: session; brain train round 2 on seven hallucination lessons (E63-E66); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E87 · incompatible · sandboxes/2026-10-12__conditioned-phantoms-persist-but-reach-a-minority.py · observed RESULT: PASS 4/4; symmetric RW stops after 3/2/1; persistence needs r>=12; fitted all-phantom 12/12; population share max 0.290 · session; brain train follow-up on E78/E79 (missing human data); session_01KGZvxv8BDgpDMRFTYMfJoJ

## E74 — depth readability is set by neighbour band spacing
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][balance]
- What: Which feature of a sound-to-sight curve (share of visual hallucinations per sanity band) makes
  depth readable without a HUD, testing seven E66's advice to move the chest-deep band off a 50/50 mix.
- Why built: E66 blamed the 0.5 stage for the banded curve's low readability and proposed 0.3 or 0.7.
  That was not run, and E66 named reading several episodes as untested.
- Design: Exact. Curves over four bands: linear, the owner's banded 0/0.1/0.5/0.9, banded with 0.3 or 0.7,
  a hard step and a flat control; equal time per band and a shallow-heavy split 0.4/0.3/0.2/0.1. Measured
  one-episode mutual information and band-guess accuracy (MAP) from 5 episodes.
- Got right: A flat mix still carries 0 bits, and linear reads best among gradual curves under both measures
  (0.541 bits, 0.829 accuracy with 5 episodes).
- Where/why it failed: E66's fix lowers readability: 0.3 gave 0.455 bits and 0.7 0.529, both below the
  banded 0.470/linear 0.541 or barely changed, and both cut 5-episode accuracy to 0.680. The weak point is
  shore vs wading (0 vs 0.1), nearly the same mix; 0.5 sits evenly between neighbours and is the best part.
- Fix: Space neighbouring bands' visual shares as evenly as the design allows (linear is the even case);
  if the owner wants early restraint, keep the shallow bands distinguishable through something else
  (frequency or kind of sound) rather than a near-identical modality mix.
- Why this fix: A band is read by how different it is from the band next to it; two bands with 0 and 0.1
  visual look the same however the deep bands are tuned.
- Rule of thumb: Depth reads from modality only where neighbouring bands differ: the banded 0/0.1/0.5/0.9
  curve loses on shore vs wading, not at 50/50; moving 0.5 to 0.3 or 0.7 cut 5-episode accuracy 0.718 to 0.680.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 0/3 of my
  predictions on E66's fix; numbers copied from the run). The time splits are assumptions.
- Composed: pappydapimp69__seven/E66, pappydapimp69__seven/E56
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-12__depth-readability-is-set-by-neighbour-band-spacing.py
- Prediction: moving chest-deep off 0.5 raises one-episode bits; a moved curve beats linear; with 5 episodes
  banded accuracy is within 0.05 of linear.
- Observed: RESULT: FAIL 0/3; equal-time bits/5-ep accuracy linear 0.541/0.829 banded 0.470/0.718 band0.3
  0.455/0.680 band0.7 0.529/0.680 step 1.000/0.500; shallow-heavy banded 0.373b
- Scenarios: 1) equal time per band; 2) shallow-heavy time; 3) built to BREAK E66's fix: chest-deep at 0.3 and 0.7.
- Link: session; brain train round 2 on seven hallucination lessons (E63-E66); session_01KGZvxv8BDgpDMRFTYMfJoJ

## E73 — voice budget from published masking data
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][audio][voices][mobile]
- What: The hallucinated-voice budget (how many voices can speak while one line still lands) rebuilt
  on published speech-in-speech numbers, after the review of seven E58 showed its budget was only a
  readout of an assumed masking width (seven E69), which also undercut seven E65's phone budget.
- Why built: E58, E60 and E65 rested on one invented constant. The cocktail-party literature gives the
  real levers: how threshold worsens with more talkers, how much spatial separation buys, and that mono
  playback loses all of it.
- Design: Calibrated so a line against one equal same-sex voice in mono lands 0.60 (Brungart 2001, via
  the Bronkhorst 2015 review). Each doubling of talkers costs about 1.5 dB (Bronkhorst 2015: 4 to 5 dB
  per tripling). Spatial release with speech maskers about 9 dB for 2 to 3 maskers and 4.5 dB for more
  (published ranges 6 to 12 and 3 to 6 dB; low ends also tested); mono gets none. Assumed a 10 points
  per dB psychometric slope and a duck (raising the line above the others) of 0 or 6 dB. Budget = most
  voices in the scene with the line landing 50 or 80 percent.
- Got right: In mono with no duck, a line that must land 80 percent cannot share the scene with even one
  equal voice (budget 1; 0.60 with one other). Headphones carry 4 voices at 80 percent, still 4 at the
  low end of published release. A 6 dB duck lifts mono to 6 voices at 80 percent.
- Where/why it failed: Nothing in the run refuted the predictions, but several 'budgets' hit the 13-voice
  cap of the sweep (meaning at least 13), the slope is assumed, and most source numbers come from
  review summaries and abstracts, not the full papers' tables.
- Fix: Treat level, not placement, as the main tool: any hallucinated line that must be understood is
  mixed about 6 dB above the other voices, especially on phones; spatial spread is a bonus for
  headphones. Retire E58's fixed '2 in one place or 4 to 5 spread' as a constant.
- Why this fix: It replaces an invented width with the published effect sizes, and the result holds at
  the low end of those ranges, so the advice does not depend on one guess.
- Rule of thumb: In mono a hallucinated line that must land 80 percent cannot share the scene with even
  one equal voice, headphones carry about 4; raise must-land lines about 6 dB above the other voices
  (mono then carries 6) rather than counting on spatial spread.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 4/4
  predictions held; numbers above copied from the run). The masking figures come from two review
  articles read on PubMed Central plus abstracts; the psychometric slope and the duck sizes are my
  assumptions.
- Composed: pappydapimp69__seven/E58, pappydapimp69__seven/E69, pappydapimp69__seven/E65
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__voice-budget-from-published-masking-data.py
- Prediction: mono with no duck fits no competing voice at 80 percent; headphones beat mono at the same
  duck; a 6 dB duck gives mono at least 3 voices at 80 percent; headphones still beat mono at the low
  end of published release.
- Observed: RESULT: PASS 4/4; 80% budgets mono 1 headphones 4 (low-release 4); with 6 dB duck mono 6
  headphones 13; 50% budgets mono 2 headphones 13
- Scenarios: 1) mono and headphones with 1 to 12 other voices; 2) must-land at 50 and 80 percent; 3) 0 and
  6 dB duck; 4) built to BREAK the claim: the low end of published spatial release.
- Link: session; follow-up to the 2026-10-12 review of seven E58 and E60; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-12 · fail · sandboxes/2026-10-12__rebuild-voice-budget-psychometric-slope-sweep.py · observed RESULT: FAIL 1/5 held; at 5%/dB mono+6dB carries [2, 3] (log/lin), headphones [[2,4,4],[3,4,4]], duck for 6 voices [8.5, 7.5] dB; 15%/dB mono+6dB 8/9 · Blind rebuild on the published ranges: one equal mono talker gives 0.60, 1.5 dB per doubling of talkers, spatial release 6/9/12 dB (half beyond 3 maskers), mono none. Slopes of 5, 10 and 15 %/dB, logistic and linear shapes, uncapped budgets. Robust: mono with no duck fits no competing voice at 80 percent at every slope and shape. Not robust: at 5 %/dB a 6 dB duck lets mono carry only 2 (logistic) or 3 (linear) voices, not 6, and 6 voices need an 8.5 dB duck. Headphones at the 6 dB low end of release carry 2-3 voices, not 4. At 15 %/dB headphones reach 8-9 and mono plus 6 dB reaches 8-9. E73's '6 dB, mono carries 6, headphones about 4' is the 10 %/dB readout, and the original sandbox fixes the slope at 10, the very parameter the advice turns on. Safe form: duck must-land lines by 8-9 dB, or measure the slope. · session; blind rebuild review of seven hallucination lessons E63-E73; session_01QGT1LfmPHPG99JEGaPhBwB
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E78 · incompatible · sandboxes/2026-10-12__must-land-voice-duck-size-turns-on-psychometric-slope.py · observed RESULT: FAIL 1/5 held; at 5%/dB mono+6dB carries [2, 3] (log/lin), duck for 6 voices [8.5, 7.5] dB; 15%/dB mono+6dB 8/9 · session; blind rebuild review of seven hallucination lessons E63-E73; session_01QGT1LfmPHPG99JEGaPhBwB
- Reverified: 2026-10-12 · fail · sandboxes/2026-10-12__rebuild-seven-e73-masking-per-doubling.py · observed RESULT: FAIL 3/4; mono+6dB budget at c1.5/2.5/3.2 (slope 10%) 6/3/3; slope 5% 2/2/2; headphones no duck c2.5 slope10 3 (the miss: c 2.5 at a 15 percent slope gave 4, not 3 or fewer) · Rebuilt from the claim with my own fixture: a logistic psychometric curve (E73 used linear 10 points per dB) at slopes 5/10/15 percent per dB, calibrated as E73 to 0.60 for one equal masker in mono, low-end spatial release (6 dB for 2-3 maskers, 3 dB beyond), duck 0 or 6 dB, and the per-doubling talker penalty swept. E73 has an internal arithmetic slip: it cites Bronkhorst 2015 as 4 to 5 dB per TRIPLING of talkers but models 1.5 dB per DOUBLING; 4-5 dB per tripling is 4/log2(3) to 5/log2(3) = 2.5 to 3.2 dB per doubling. With E73's 1.5 dB the rebuild reproduces its headline (mono with a 6 dB duck carries 6 at 10 percent per dB), but at the cited 2.5-3.2 dB mono with the duck carries 3 (2 at a 5 percent slope, 4 at 15 percent with 2.5 dB), so 'mono then carries 6' rests on half the cited penalty. What holds in every cell: mono with no duck cannot share an 80 percent line with any equal voice, and headphones beat mono at the same duck; the advice to raise must-land lines above the rest survives, the count does not. The Bronkhorst figure itself was not re-checked against the paper; the slip is in E73's own conversion. · session; brain train auto pass 4 (rebuild; auto's age-cutoff pick skipped as saturated); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E88 · incompatible · sandboxes/2026-10-12__duck-must-cover-total-masker-power.py · observed RESULT: PASS 4/4; 6 voices need 11.0/9.0/8.3 dB at 5/10/15%/dB; 6 dB carries 2/3/3; growth 2->6 voices 7.0 dB vs 3.5 at 1.5/doubling · session; brain train follow-up on E78 (missing masking data); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-15 · projects/pappydapimp69__seven.md#E103 · compatible · sandboxes/2026-10-15__hallucinated-voices-barely-shrink-a-whistles-range-anywhere.py · observed RESULT: FAIL 1/4; 8 voices shrink range open 1342->886 m, woods23 150->119 m, woods4 493->363 m; per doubling open 0.07, woods23 0.04, woods4 0.05 · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 1 pass 1 (kernel apply; brain challenge masking run first), 2026-10-15

## E72 — depth reads from bed density plus vision rate not one episode
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][sanity][audio]
- What: How well a player can read their sanity depth when sound is a continuous bed that thickens
  with depth and visions are brief events (seven E71), compared with judging from a single episode's
  modality (seven E66, where the owner's banded curve gave 0.470 bits).
- Why built: E66 showed one episode says little about depth, and a 50/50 stage says nothing. E71 says
  hallucinations are lived as a state (voices) with moments (visions), which gives the player two
  channels over time instead of one draw.
- Design: Exact computation over four equally likely bands (2 bits at most). Bed thickness 0 to 3
  (silence, presence, murmurs, voices), perceived correctly with probability 0.7 (or 0.5), otherwise an
  adjacent level. Visions as a Poisson count in a 2-minute window with rates 0, 0.1, 0.5, 1.5 per band.
  Mutual information between band and what the player perceives.
- Got right: The bed carries most of the depth signal (0.952 bits) and visions alone carry little
  (0.396); together they beat either alone (1.069), and even a muddy bed with visions (0.874) beats a
  single episode's modality (0.470 in E66). Depth reads from how thick the sound is, not from whether
  the latest hallucination was a voice or a sight.
- Where/why it failed: My target of 1.2 bits was refuted (1.069): adjacent bed levels blur and rare
  visions at the shallow bands add almost nothing. The comparison with E66 is loose: E66 measured one
  episode, this a 2-minute window.
- Fix: Make the bed's thickness steps clearly distinct (four levels a player can tell apart, such as
  silence, a single presence, murmur, several voices), and let visions confirm depth late rather than
  signal it early.
- Why this fix: It puts the readability where the signal is, matches the owner's shore-to-undercurrent
  progression, and removes the 50/50 problem E66 found without changing the curve.
- Rule of thumb: Let players read hallucination depth from the sound bed's thickness, not from which
  modality the last episode used: the bed alone gave 0.952 bits of 2 and bed plus visions 1.069,
  against 0.396 from visions alone; make the bed's steps clearly distinct.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 2/3
  predictions held; numbers above copied from the run). Perception accuracy, band rates and the window
  are my assumptions.
- Composed: pappydapimp69__seven/E66, pappydapimp69__seven/E71, ideas:GAME-DESIGN/hallucination-phenomenology/sound-first-then-sight-as-sanity-falls
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__depth-reads-from-bed-density-plus-vision-rate-not-one-episode.py
- Prediction: bed plus visions beats either alone; reaches at least 1.2 bits; a muddy bed plus visions
  still beats one-episode modality (0.470).
- Observed: RESULT: FAIL 2/3; bits visions 0.396 bed 0.952 both 1.069 both-muddy 0.874
- Scenarios: 1) visions only; 2) bed only; 3) both; 4) built to BREAK the claim: a muddy bed (0.5 correct).
- Link: session; brain train focused loops after the 2026-10-12 review; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-12 · fail · sandboxes/2026-10-12__rebuild-bed-vs-vision-depth-information-window-sweep.py · observed RESULT: FAIL; win 5 acc 0.7 visions 0.962 bed 0.672; win 10 visions 1.346 bed 0.672; bed acc 0.5 0.252, acc 0.4 0.129 · Blind rebuild with my own fixture. Bed errors spread to any level weighted by 1/distance (the original sends them only to adjacent levels). Bed accuracy 0.4-0.9. Own vision rates (0/0.2/0.6/1.2 per minute). Windows of 1, 2, 5 and 10 minutes. Joint at least equal to each channel holds everywhere, but that is a property of MI, not a finding. 'Read depth from the bed, not from visions' fails: at 0.7 bed accuracy visions alone out-inform the bed at 5 and 10 minute windows (0.962 and 1.346 vs 0.672). The bed alone also falls below E66's one-episode 0.470 at accuracy 0.5 or less (0.252, 0.129). The ranking is a readout of two assumptions, the 2-minute window and how well players tell bed levels apart, and neither is measured. The Fix (make bed steps clearly distinct) is the right lever, but it needs a playtest, not MI. · session; blind rebuild review of seven hallucination lessons E63-E73; session_01QGT1LfmPHPG99JEGaPhBwB

## E71 — voices dominate by time so sound is a bed and visions are events
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][audio][balance]
- What: Follow-up to the failed review of seven E62 (SEVEN's hallucination mix against real
  psychosis): the 'real auditory share' depends on what is counted, and counting the TIME a person
  spends hallucinating, rather than who ever has each kind, changes the design answer.
- Why built: E62 compared SEVEN's episode mix with a prevalence figure (about 0.55), and the review
  showed episode-rate weighting moves the reference anywhere from 0.38 to 0.71, so the target was
  unstable. Voices and visions differ most in duration, which E62 ignored.
- Design: Exact arithmetic. Prevalence auditory 0.59 and visual 0.27 (Waters 2014); voice episodes last
  hours and about half of voice-hearers hear them constantly (McCarthy-Jones 2014); psychotic visions
  last seconds to minutes (Waters 2014). Swept voice episodes 30, 60, 180 minutes, visions 0.25, 1, 5
  minutes, and visions equally or 4 times as frequent. Auditory share of hallucination time.
- Got right: By time, voices are 0.992 of hallucinating in the central case (voices an hour, visions a
  minute), above the prevalence share (0.686) in every swept case, and still 0.766 in the case most
  favourable to visuals (short voices, long frequent visions).
- Where/why it failed: Nothing in the run refuted the predictions, but the durations are ranges chosen
  inside published descriptions, not measured averages, and the comparison is per person with each
  kind, not per population. The robust part is the ordering, not the third decimal.
- Fix: Model the sound-first style as a continuous audio BED that thickens with depth (presence,
  murmurs, voices), and visuals as brief EVENTS layered on it, instead of drawing discrete episodes
  from one pool of kinds; compare SEVEN's mix by time on screen and in the ear, not by episode count.
- Why this fix: It matches how hallucinations are actually lived (voices as a state, visions as
  moments), fits the owner's shore-to-undercurrent progression directly, and gives E62's comparison a
  stable target.
- Rule of thumb: Count hallucination modality by TIME, not by who has it or how many episodes: voices
  were 0.992 of hallucinating time in the central case and at least 0.766 in every swept case, so a
  faithful style plays sound as a continuous bed and visions as brief events.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 3/3
  predictions held; numbers above copied from the run). Prevalence figures and duration descriptions
  were checked on the cited review and survey papers; the swept durations are my choices within them.
- Composed: pappydapimp69__seven/E62, ideas:GAME-DESIGN/hallucination-phenomenology/real-hallucinations-are-voice-led-and-overlay-the-real-scene, ideas:GAME-DESIGN/hallucination-phenomenology/sound-first-then-sight-as-sanity-falls
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__voices-dominate-by-time-so-sound-is-a-bed-and-visions-are-events.py
- Prediction: voices above 0.9 of time in the central case; above the prevalence share in every swept
  case; above 0.75 even in the visual-friendliest case.
- Observed: RESULT: PASS 3/3; prevalence 0.686; time share central 0.992, range 0.766..0.999
- Scenarios: 1) voice episodes 30, 60, 180 minutes; 2) visions 0.25, 1, 5 minutes; 3) equal or 4x vision
  frequency; 4) built to BREAK the claim: the visual-friendliest corner.
- Link: session; follow-up to the 2026-10-12 review of seven E62; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E72 · compatible · sandboxes/2026-10-12__depth-reads-from-bed-density-plus-vision-rate-not-one-episode.py · observed RESULT: FAIL 2/3; bits visions 0.396 bed 0.952 both 1.069 both-muddy 0.874 · session; brain train focused loops after the 2026-10-12 review; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-12 · fail · sandboxes/2026-10-12__rebuild-voice-time-share-over-published-duration-mix.py · observed RESULT: FAIL pop share >= 0.888 everywhere; but lowest person 0.002 (vision 5.0 min x 50/wk) and up to 0.28 of voice-hearers below the prevalence share · Re-checked the sources on PMC. Waters 2014 (PMC4141306): auditory 59 percent (range 25-86), visual 27 percent (range 4-65), visions last 'several seconds to several minutes'. McCarthy-Jones 2014 (PMC3885292): voices last hours for 59 percent, minutes for 31 percent and seconds for 12 percent, are constant for 48 percent, and are inside the head for 34 percent. E71 quotes these correctly but sweeps only voices of 30-180 minutes, dropping the 43 percent of hearers whose voices last minutes or seconds. Blind rebuild over the full published duration and frequency mix against visions of 0.1-5 minutes at 1-50 per week: the POPULATION time share stays above the prevalence share everywhere (at least 0.888), but per person (E71's stated scope) the lowest share is 0.002, and up to 28 percent of voice-hearers fall below 0.686. The 'at least 0.766 in every swept case' floor is an artefact of the sweep. The bed/events design advice survives at population level only. Caveat: the survey sample is self-selected voice-hearers, not a psychosis cohort. · session; blind rebuild review of seven hallucination lessons E63-E73; session_01QGT1LfmPHPG99JEGaPhBwB
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E80 · incompatible · sandboxes/2026-10-12__voice-time-share-is-a-population-claim-not-per-player.py · observed RESULT: FAIL pop share >= 0.888 everywhere; lowest person 0.002 (vision 5 min x 50/wk); up to 0.28 of voice-hearers below the prevalence share · session; blind rebuild review of seven hallucination lessons E63-E73; session_01QGT1LfmPHPG99JEGaPhBwB

## E70 — correction seven e60 e61 e63 e65 composed refs
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [process][tooling][verification]
- What: Correction of cross-references in seven E60, E61, E63 and E65 (and one tension evidence line).
  They cite seven E55 meaning the voice-budget lesson and seven E57 meaning the believable-phantom
  lesson, but the steward assigned E55 to the believable-phantom lesson, E57 to the flicker lesson and
  E58 to the voice-budget lesson. The ids were mapped from PITFALLS.md line order, not from the
  project file's headers.
- Why built: The Composed fields mint graph edges and the evidence line scores an owner decision, so
  a mis-mapped id silently links the wrong systems and scored the decision on the inner-voice lesson
  instead of the altered-object one. Canon is append-only, so the fix is this entry plus corrected
  edges below.
- Design: Checked every seven id cited in this author's session against the '## E<n> — title' headers
  of projects/pappydapimp69__seven.md. E22 to E50 were all correct. Wrong: E60 (Composed seven/E55 and
  prose 'seven E55's voice budget' mean E58), E61 (Composed seven/E57 means E55), E63 (Composed
  seven/E57 means E55), E65 (Composed seven/E55 and seven/E61 mean E58 and E60). The fidelity tension's
  evidence line cited E60 for the altered-object lesson, which is E61; that line was corrected in the
  Tension repo with a dated note.
- Got right: The error was caught by reading a reviewer's notes against the cited titles, before any
  further lesson composed on the wrong edges, and every other id from the session checks out.
- Where/why it failed: Ids were taken from the order PITFALLS.md lists index lines, which follows
  promotion order inside a batch, not the id the steward assigned; within one sync batch these can
  differ, so a batch of eight lessons came back shuffled.
- Fix: Read an entry's id from its '## E<n> — title' header in the project file (or the arrow target
  of its own index line, matched by its text), never from list position; correct edges here:
  E60 -> E58; E61 -> E55; E63 -> E55; E65 -> E58, E60.
- Why this fix: The header is the only place the id and the lesson are written together, so it cannot
  drift; list order is a side effect of promotion.
- Rule of thumb: Take a lesson's id from its own header (or its index line's arrow, matched by text),
  never from the order index lines appear; one batch of eight came back shuffled and four later
  lessons composed on the wrong edges.
- Provenance (verified/assumed): Verified first-hand by reading the '## E<n>' headers of the project
  file on 2026-10-12 against every id cited in this session's lessons and evidence lines.
- Composed: pappydapimp69__seven/E58, pappydapimp69__seven/E55, pappydapimp69__seven/E60, pappydapimp69__seven/E61, pappydapimp69__seven/E63, pappydapimp69__seven/E65
- Link: session; correction after the 2026-10-12 review of seven hallucination lessons; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E90 · compatible · sandboxes/2026-10-12__stored-sandboxes-drift-on-interpreter-and-missing-snapshots.py · observed RESULT: PASS 3/3; sum equal True loop equal False fsum equal True on 3.13.16. Sweep: 794 comparable, 792 matched, 2 flipped PASS to FAIL, 373 no result within 30 s. · session; brain train auto pass 5 (gap), 2026-10-12; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Audited: 2026-10-20 · pass · The entry has no sandbox, and none is needed: it is a documentary correction, so the check was to read the project file's own headers. They confirm the mapping it states (E55 is the believable-hallucination or learned-prior lesson, E57 the flicker window-cap lesson, E58 the more-voices-turn-words-into-texture lesson, E60 inner voices and the binaural budget, E61 misperceived real objects, E63 conditioned phantoms, E65 phone speakers) and that E60's Composed still reads E55 while its prose speaks of seven E55's voice budget, which by title is E58; E65's prose also names seven E58 and E60 as its subjects. The answer is built from headers, not assumed. One limit: for E61 and E63 the entry's claim that their Composed E57 meant E55 rests on the author's memory of the session, because neither body mentions flicker or the believable-phantom idea in so many words, so I could confirm that E57 is the wrong target by title but not that E55 is the intended one. Nothing real-world is modeled here, so modeled does not apply. · session_015FBsByvogibt2qnd37NTki
- Reverified: 2026-10-20 · pass · sandboxes/2026-10-20__rebuild-id-from-header-not-index-line-order.py · observed RESULT: PASS positional wrong 0/8 in order, 8/8 reversed, 8/8 rotated, 2/8 one swap; by-text wrong 0 · Rebuilt from the claim alone with my own fixture: eight generic titles with ids 55 to 62 taken from headers, then index lines in four orders. Taking ids by order of appearance was right only when the order matched (0 of 8 wrong), wrong for 8 of 8 when reversed or rotated and 2 of 8 with one swap, while matching by title text was right in every order. This supports the rule to take ids from the header or match by text. Differences from the original: I did not open its sandbox before running; my fixture is synthetic titles rather than the real lesson text, so it shows the mechanism, not the original incident. · brain train auto loop 1 pass 4 rebuild session_01NFn71BZX5UoPHJWMN7pDFZ

## E69 — voice budget is a readout of masking width
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][audio][voices]
- What: Whether seven E58's hallucinated-voice budget (2 voices in one place, about 4 spread, texture past
  about 6) and E60's corrected spread budget of 5 survive a different masking width and talk share.
- Why built: Both entries derive the budget from a 60 degree on/off masking cone and a 0.4 talk share,
  each picked by the author. A sound designer reading 'about 4' would take it as a property of voices.
- Design: Exact model as E58 (voices evenly spaced, a phrase lands if no masker within w talks over it),
  swept w = 30, 45, 60, 90, 120 degrees and p = 0.2, 0.4, 0.6; budget = the largest N with at least half
  the words landing. Then E60's inner-voice variant at w 45 and 90.
- Got right: Spreading helps in most cells, and a mostly-inner scene falls to the one-place budget, as
  E60 said.
- Where/why it failed: The budget is a readout of the two constants: one place 4/2/1 across p, spread
  11/7/5/3/2 across w at p 0.4, and spreading did not double it at w 120. Under even spacing nothing masks
  until 360/N reaches w, so 'about 4' is just 360/60 minus one. A third inner voices even raised the budget
  in one cell (3 to 4 at w 90, p 0.3) because fewer outer voices spread wider.
- Fix: Do not quote a voice count. Measure the masking width and talk share of the actual mix (or play-test
  intelligibility), then derive the budget; until then, duck all but the line that must land.
- Why this fix: The counts only move with the inputs, so a fixed number gives false confidence; ducking is
  the part of E58's advice that holds at any width.
- Rule of thumb: A hallucinated-voice budget is a readout of masking width and talk share, not a constant:
  spread budgets ran 11 to 2 for widths 30 to 120 degrees; measure the mix, or duck all but one line.
- Provenance (verified/assumed): Verified first-hand by the sandboxes in this entry and the E60 rebuild
  (RESULT FAIL 0/3 on E58's numbers; numbers copied from the run). The on/off cone is the original model.
- Composed: pappydapimp69__seven/E58, pappydapimp69__seven/E60
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-12__voice-budget-is-a-readout-of-masking-width.py
- Prediction: one-place budget 2 at every p; spread budget within 3 to 5 across widths; spreading at least
  doubles the one-place budget everywhere.
- Observed: RESULT: FAIL 0/3; one-place budget p0.2/0.4/0.6 4/2/1; spread at p0.4 w30..120 11/7/5/3/2;
  spread range 2-23
- Scenarios: 1) one place across p; 2) spread across w at p 0.4; 3) built to BREAK the claim: wide 120
  degree masking, where spreading should still double the budget.
- Link: session; review of seven hallucination lessons (E46, E55-E62); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E73 · compatible · sandboxes/2026-10-12__voice-budget-from-published-masking-data.py · observed RESULT: PASS 4/4; 80% budgets mono 1 headphones 4 (low-release 4); with 6 dB duck mono 6 headphones 13; 50% budgets mono 2 headphones 13 · session; follow-up to the 2026-10-12 review of seven E58 and E60; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-12 · pass · sandboxes/2026-10-12__rebuild-seven-e69-soft-masking-budget.py · observed RESULT: PASS 3/3; sigma budgets 16/14/10/7/5; talk-share budgets 16/10/7; one place 2 · Rebuilt blind with a different masking model: masking falls off smoothly with angle (exp(-a/sigma)) instead of the original on/off cone. The spread budget ran from at least 16 down to 5 as sigma went from 15 to 90 degrees (16 is the sweep cap) and from at least 16 to 7 as talk share went 0.2 to 0.6 at sigma 45, while one place stayed 2 at every sigma. So the budget is a readout of the masking model and talk share, as the entry says, under a second model shape too. A separate lesson this session (seven E73) re-grounds the budget on published masking figures. · session; blind rebuild of seven E67-E69 (written by another session), 2026-10-12; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E88 · incompatible · sandboxes/2026-10-12__duck-must-cover-total-masker-power.py · observed RESULT: PASS 4/4; 6 voices need 11.0/9.0/8.3 dB at 5/10/15%/dB; 6 dB carries 2/3/3; growth 2->6 voices 7.0 dB vs 3.5 at 1.5/doubling · session; brain train follow-up on E78 (missing masking data); session_01KGZvxv8BDgpDMRFTYMfJoJ

## E68 — sub threshold recede is decisive near a deadline
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][perception][deception]
- What: Whether a phantom target that recedes on screen below the speed-discrimination threshold can
  stop a disciplined player when the walk races a deadline (SEVEN's night clock), which seven E46 ruled out.
- Why built: E46 showed an invisible recede only delays arrival by 1/(1-j) and concluded it can never be
  both unnoticeable and unbeatable. That was computed with no deadline; SEVEN's walks race nightfall.
- Design: Exact arithmetic. Gap 60 m, walk 1.4 m/s, invisible recede f = 0.08; night falls at the base
  arrival time times (1 + slack), slack 0.02 to 0.20. Also re-ran E46's off-screen relief with the
  player still walking while looking away.
- Got right: The delay is exactly 1/(1-f) (x1.087 at 0.08), as E46 said.
- Where/why it failed: E46's conclusion does not hold under a deadline: the invisible f = 0.08 recede
  stopped a perfectly disciplined player at every slack of 0.08 or less. And E46's off-screen 'look away
  40 percent' stop point is its own assumption that a player stops walking while looking away; a
  player who keeps walking is only stopped from 0.667.
- Fix: When a receding phantom sits on a timed walk, treat any recede, even an invisible one, as a
  possible run-ender for players with slack under f/(1-f); either keep the recede off the clock-critical
  path or size f from the slack the level leaves, not from the perception threshold alone.
- Why this fix: The threshold decides whether the motion is seen; the slack decides whether it matters.
  Checking only the first lets an imperceptible effect decide a run, which is the unfair kind of dread.
- Rule of thumb: A sub-threshold on-screen recede is harmless only without a deadline: with night at
  base time +8 percent, an invisible 0.08 recede stopped a disciplined player; size it against slack.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 1/3 of my
  predictions on E46's claim; numbers copied from the run). The 0.08 threshold is a stand-in value.
- Composed: pappydapimp69__seven/E46
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-12__sub-threshold-recede-is-decisive-near-a-deadline.py
- Prediction: invisible delay equals 1/(1-j); the stop share stays 0.4 in any walking model; an invisible
  recede is never decisive for a disciplined player.
- Observed: RESULT: FAIL 1/3; delay x1.031/x1.087/x1.176; stop share walk 0.667 freeze 0.400; invisible
  f=0.08 blocks slack <= 0.08
- Scenarios: 1) thresholds 0.03, 0.08, 0.15; 2) off-screen relief with walking vs freezing players;
  3) built to BREAK E46: deadline slack 0.02 to 0.20.
- Link: session; review of seven hallucination lessons (E46, E55-E62); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Reverified: 2026-10-12 · pass · sandboxes/2026-10-12__rebuild-seven-e68-recede-vs-slack.py · observed RESULT: PASS 3/3; flipped 0.109/0.178/0.277 at j 0.05/0.08/0.12; slack>=0.2: 0.000 · Rebuilt blind with my own fixture: instead of one deadline, trips whose slack before night is spread evenly from 0 to 0.5 of the walk, and invisible recedes at stand-in thresholds 0.05, 0.08 and 0.12. A trip flips from arriving to benighted when f > s/(1+s). At 0.08 an invisible recede flips 0.178 of trips, at 0.05 0.109 and at 0.12 0.277, while no trip with 20 percent slack or more flips. That is the entry's claim: harmless without a deadline, decisive near one, sized against slack. The core is close to algebra once arrival is T/(1-f), so the pass is on the claim's logic, not on any perception data. · session; blind rebuild of seven E67-E69 (written by another session), 2026-10-12; session_01NHKVhTvCnvtvZ2NGLSPYj6

## E67 — easier recovery does not undo a sanity competence penalty
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][sanity][balance]
- What: seven E59's alternative fix for a sanity meter that lowers competence: keep the penalty but make
  recovery easier at low sanity so the feedback loop is damped.
- Why built: E59 offered that fix without testing it; a team that wants a mechanical cost will reach for
  it first, so it needed pricing before it is used as cover for keeping the penalty.
- Design: Exact Markov chain, meter 0 to 8, 25 encounters, base fail 0.25, penalty 0.08 per lost level,
  recovery rho 0.1 to 0.9; the fix raises recovery by 0.08 per lost level from rho 0.3.
- Got right: E59's rule holds and its ratios understate it: the penalty raised collapse x5.6 to x161,
  growing with recovery rate, and even 0.02 per level raised it x2.4 to x7.4.
- Where/why it failed: The damped-recovery fix barely helps: collapse stayed x10.0 of the perception-only
  meter (0.433 vs 0.043). Recovery acts only after a success, which the penalty has already made rarer.
- Fix: Treat 'easier recovery at low sanity' as a weak patch, not a fix: if low sanity must cost something,
  take it from a separate resource; otherwise keep competence flat and let sanity change perception only.
- Why this fix: The loop runs through the failure chance; damping a different term leaves it running.
- Rule of thumb: Easier recovery at low sanity does not undo a sanity penalty on competence: with recovery
  rising 0.08 per lost level, collapse stayed x10 of a perception-only meter; keep competence flat.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 2/4 of my
  predictions; numbers copied from the run). Fail and recovery rates are model inputs.
- Composed: pappydapimp69__seven/E59
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__easier-recovery-does-not-undo-a-sanity-competence-penalty.py
- Prediction: any penalty raises collapse at every rho; mild ratio at least x1.5; strong ratio within x2 to
  x6; the damped-recovery fix brings collapse within x1.3 at rho 0.3.
- Observed: RESULT: FAIL 2/4; mild ratio x2.43/x3.44/x5.34/x7.41; strong ratio x5.57/x14.35/x52.71/x160.60
  (rho 0.1/0.3/0.6/0.9); damped x10.03
- Scenarios: 1) recovery 0.1, 0.3, 0.6, 0.9; 2) mild and strong penalties; 3) built to BREAK the rule:
  the damped-recovery fix.
- Link: session; review of seven hallucination lessons (E46, E55-E62); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Reverified: 2026-10-12 · fail · sandboxes/2026-10-12__rebuild-seven-e67-damped-recovery.py · observed RESULT: FAIL 1/3; base 0.1932 penalty x3.07; damped 0.05 x2.46; damped 0.1 x1.92; damped 0.2 x1.21 (probe: 0.25 x1.04, 0.30 x0.95) · Rebuilt blind from the claim and prediction with my own chain: sanity 0 to 6, 20 encounters, fail 0.28 plus 0.06 per lost level, recovery 0.25 rising by 0.05, 0.10 or 0.20 per lost level, against a perception-only meter (flat fail and recovery). The bare penalty triples collapse (x3.07) and mild damping still leaves x2.46, which supports the entry's direction, but its rule says easier recovery 'does not undo' the penalty and that collapse 'stayed x10': here damping of 0.20 per level brings it to x1.21, 0.25 to x1.04, and 0.30 below the perception-only rate (x0.95). Whether damping undoes the penalty depends on how steep the damping is relative to the penalty, so the general claim does not survive a different fixture. Differs from the original: different scale, encounter count and rates. · session; blind rebuild of seven E67-E69 (written by another session), 2026-10-12; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E76 · compatible · sandboxes/2026-10-12__sanity-penalty-cancels-only-with-damping-several-times-steeper.py · observed RESULT: PASS 3/3; damping needed pen 0.03: 0.1; pen 0.06: 0.28; pen 0.1: None · session; follow-up to the blind rebuild of seven E67; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E93 · incompatible · sandboxes/2026-10-12__cancel-ratio-between-two-slopes-is-a-fixture-constant.py · observed RESULT: FAIL shape holds but ratios 27-76x not 3-5x; 0.10 cancelled in set A (b 2.82); between-set difference 1.70x at a 0.03 and 2.67x at 0.06 · session_01P1LRA5HjMLEFnWXayE2EHx; review pass of SEVEN targets, gap lessons, 2026-10-12

## E66 — sound to sight curve shape sets how readable depth is
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][sanity][balance]
- What: The shape of the owner's 'sound first, then sight as sanity falls' curve: how the share of
  visual hallucination episodes should rise across four sanity bands so the player can read how deep
  they are from what they experience, without a HUD.
- Why built: The owner chose the progression (shore, wading, chest-deep, undercurrent) but not its
  shape. A curve can be linear, a hard step, or banded like the owner's image, and each spends visual
  surprise and signals depth differently.
- Design: Exact computation over four equally long bands. Curves for P(visual | band): linear 0, 0.33,
  0.67, 1; hard step 0, 0, 1, 1; the owner's banded shape 0, 0.10, 0.50, 0.90; and a flat 0.45 control.
  Measured the mutual information between band and one episode's modality, P(deep | a visual episode),
  and visual episodes spent before chest-deep per 20.
- Got right: A flat mix carries no depth information at all (0 bits), so SEVEN's current flat pick
  cannot signal depth through modality. The banded shape makes a visual a strong sign of depth
  (P(deep | visual) 0.933 vs 0.833 linear) and spends only 0.50 visuals early against 1.67, keeping
  visual surprise for the deep woods (seven E56).
- Where/why it failed: My prediction that the banded shape is the most readable was refuted: per
  single episode it carries 0.470 bits, below linear (0.541) and far below a hard step (1.000),
  because a 0.50 visual share at chest-deep is the most ambiguous possible stage and 0.90 at the bottom
  still leaves sound. A hard step reads best but has no transition to feel.
- Fix: Keep the banded shape for its early restraint and its strong 'visual means deep' signal, but
  move chest-deep away from 0.50 (about 0.30 or 0.70) so that band reads, or let the band show through
  how episodes combine (frequency, overlap) rather than modality alone.
- Why this fix: It keeps the owner's gradual progression and its saved surprise while removing the one
  stage that tells the player nothing, without falling back to a hard switch.
- Rule of thumb: When hallucinations shift from sound to sight as sanity falls, avoid a 50/50 mix at
  any stage: it is the least readable point; a banded curve still makes a visual mean deep (0.933 vs
  0.833 linear) and spends a third of linear's early visuals, while a flat mix signals nothing.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 3/4
  predictions held; numbers above copied from the run). Equal time per band and single-episode
  readability are my simplifications; players also read sequences.
- Composed: ideas:GAME-DESIGN/hallucination-phenomenology/sound-first-then-sight-as-sanity-falls, pappydapimp69__seven/E56, pappydapimp69__seven/E62
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__sound-to-sight-curve-shape-sets-how-readable-depth-is.py
- Prediction: flat carries 0 bits; banded beats linear on readability; banded spends at most a third of
  linear's early visuals; a hard step is the most readable at 1 bit.
- Observed: RESULT: FAIL 3/4; bits linear 0.541 step 1.000 banded 0.470 flat 0.000; early visuals
  linear 1.67 banded 0.50
- Scenarios: 1) linear; 2) hard step; 3) the owner's banded curve; 4) flat control; 5) built to BREAK
  the claim: whether banded beats linear per episode (it did not).
- Link: session; brain train focused loops after the owner's sound-first decision (loop 1); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E72 · compatible · sandboxes/2026-10-12__depth-reads-from-bed-density-plus-vision-rate-not-one-episode.py · observed RESULT: FAIL 2/3; bits visions 0.396 bed 0.952 both 1.069 both-muddy 0.874 · session; brain train focused loops after the 2026-10-12 review; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-12 · fail · sandboxes/2026-10-12__rebuild-seven-e66-depth-readability.py · observed RESULT: FAIL 0/3; equal-time bits/5-ep accuracy linear 0.541/0.829 banded 0.470/0.718 band0.3 0.455/0.680 band0.7 0.529/0.680 step 1.000/0.500; shallow-heavy banded 0.373b · Rebuilt with unequal time per band (0.4/0.3/0.2/0.1, players linger shallow) as well as equal, and readability measured both as one-episode mutual information and as band-guess accuracy from 5 episodes, which E66 named but did not test. E66's Fix fails: moving chest-deep off 0.5 to 0.3 LOWERS one-episode bits (0.455 vs 0.470) and 0.7 barely moves them (0.529), neither beats linear (0.541), and both lower 5-episode accuracy (0.680 vs banded 0.718, linear 0.829). The diagnosis is wrong: 0.5 at chest-deep is the most informative point of the banded curve, evenly between 0.1 and 0.9; what costs readability is shore vs wading at 0 and 0.1, nearly indistinguishable. Readability is set by the spacing between neighbouring bands, which linear maximises. · session; brain train round 2 on seven hallucination lessons (E63-E66); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E74 · incompatible · sandboxes/2026-10-12__depth-readability-is-set-by-neighbour-band-spacing.py · observed RESULT: FAIL 0/3; equal-time bits/5-ep accuracy linear 0.541/0.829 banded 0.470/0.718 band0.3 0.455/0.680 band0.7 0.529/0.680 step 1.000/0.500; shallow-heavy banded 0.373b · session; brain train round 2 on seven hallucination lessons (E63-E66); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Reverified: 2026-10-12 · fail · sandboxes/2026-10-12__rebuild-modality-curve-readability-and-the-half-mix.py · observed RESULT: FAIL banded 0.470 / 0.30 -> 0.455 / 0.70 -> 0.529; worst chest-deep value 0.35; k=6 banded 1.225 vs fix0.70 1.186 · Blind rebuild: exact MI between 4 equal bands and the count of visual episodes among k = 1, 3 or 6 episodes, plus a sweep of the chest-deep value from 0.05 to 0.95 and the Fix's two variants. The arithmetic reproduces: 0.470, 0.541, 1.000 and 0 bits; P(deep|visual) 0.933 vs 0.833; early visuals 0.50 vs 1.67. The rule 'avoid 50/50 at any stage: it is the least readable point' fails. With the other bands fixed, the least readable chest-deep value is 0.35 (0.454 bits), not 0.50 (0.470). The Fix's 0.30 lowers readability to 0.455. The Fix's 0.70 helps one episode (0.529) but hurts six-episode reading (1.186 vs 1.225 for 0.50). Per-band entropy peaks at 0.5, but MI depends on how far apart neighbouring bands are. The original sandbox computed only single-episode MI on four fixed curves, so it could not see either effect. · session; blind rebuild review of seven hallucination lessons E63-E73; session_01QGT1LfmPHPG99JEGaPhBwB
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E85 · compatible · sandboxes/2026-10-12__sway-comfort-rules-across-published-peaks-and-peripheral-vection.py · observed RESULT: FAIL jitter robust (max 0.151); slow drift as bad or worse than 0.3 Hz sway in 7/16 cells; vignette cut 70% area vs 59% periphery-weighted; banded puts 60% of visuals in the deepest band · session; brain train loop after the review of seven E63-E73; session_01QGT1LfmPHPG99JEGaPhBwB

## E65 — sound first voices collapse on phone speakers
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][audio][voices][mobile]
- What: The hallucinated-voice budget (seven E55 and E61: how many voices can speak before words stop
  landing) across playback devices, because a sound-first style is played on headphones, stereo
  speakers and phone speakers, and SEVEN is played on phones.
- Why built: E55's spread-around-the-head budget assumes headphones. A phone speaker is effectively
  one place, so the binaural spread that buys extra voices does not exist there, and the owner's
  sound-first decision makes voices carry the first stages.
- Design: Exact model as E55 and E61 (each voice talks 0.4 of the time; inner voices mask everyone).
  Device = effective masking width: headphones 60 degrees, stereo speakers 150 degrees (a rough
  left/right split), phone speaker 360 degrees (everything masks). Inner-voice share 0 or 0.34 (the
  survey figure for voices inside the head). Budget = most voices with half the words landing.
- Got right: A phone speaker collapses the budget to the one-place 2, while headphones keep 5 (4 with
  a third of the voices inside the head), and stereo speakers sit at the phone end (2 all-outer), so
  any scene that must land on phones has to be written for 2 voices.
- Where/why it failed: Nothing in the run refuted the predictions, but the stereo result with inner
  voices (3, above its all-outer 2) is an artefact of rounding the inner-voice count at small numbers,
  not a real gain. The device widths are my stand-ins, not measured binaural release.
- Fix: Write every voice line that must be understood for 2 simultaneous voices, the phone budget;
  use extra voices only as texture that may collapse on speakers, and offer a headphones prompt for
  the fuller version rather than designing for it.
- Why this fix: It keeps the owner's sound-first stages working on the device most players will use,
  without giving up the richer headphone experience.
- Rule of thumb: On phone speakers a hallucinated-voice scene has the one-place budget of 2 voices
  whatever the mixing (headphones 5, or 4 with a third inner); write lines that must land for 2 and
  treat extra voices as texture.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 3/3
  predictions held; numbers above copied from the run). Device masking widths are assumptions; the
  0.34 inner share was checked on the McCarthy-Jones 2014 survey paper.
- Composed: pappydapimp69__seven/E55, pappydapimp69__seven/E61, ideas:GAME-DESIGN/hallucination-phenomenology/sound-first-then-sight-as-sanity-falls
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__sound-first-voices-collapse-on-phone-speakers.py
- Prediction: phone speaker collapses the all-outer budget to 2; headphones keep a bigger budget than a
  phone even with 34 percent inner voices; stereo speakers land between phone and headphones.
- Observed: RESULT: PASS 3/3; budgets all-outer/34%-inner headphones 5/4; stereo speakers 2/3; phone
  speaker 2/2
- Scenarios: 1) headphones; 2) stereo speakers; 3) phone speaker; each all-outer and with 34 percent
  inner voices; 4) built to BREAK the claim: stereo landing between the two.
- Link: session; brain train focused loops after the owner's sound-first decision (loop 4); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E70 · compatible · no sandbox · session; correction after the 2026-10-12 review of seven hallucination lessons; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E73 · compatible · sandboxes/2026-10-12__voice-budget-from-published-masking-data.py · observed RESULT: PASS 4/4; 80% budgets mono 1 headphones 4 (low-release 4); with 6 dB duck mono 6 headphones 13; 50% budgets mono 2 headphones 13 · session; follow-up to the 2026-10-12 review of seven E58 and E60; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-12 · fail · sandboxes/2026-10-12__rebuild-seven-e65-phone-voice-budget.py · observed RESULT: FAIL 1/3; phone budget p0.15/0.25/0.4/0.55 5/3/2/1; scripted turns 6/4/2/1; headphones w90 11/7/3/3 · Rebuilt sweeping talk share 0.15/0.25/0.4/0.55 (E65 fixed 0.4) and headphone widths 45/60/90, and modelled two mixes that act on a single speaker: scripted turn-taking and ducking. 'The one-place budget of 2 voices whatever the mixing' does not hold: the phone budget is a talk-share readout (5/3/2/1), scripted non-overlapping turns raise it (6/4/2/1), and ducking all but the lead voice makes the line that must land always land. Headphones beat the phone in every cell, so the direction (write for the phone, treat extra voices as texture) is sound; the number 2 and the 'whatever the mixing' clause are not. Same width/share dependence as seven E69. · session; brain train round 2 on seven hallucination lessons (E63-E66); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Reverified: 2026-10-12 · fail · sandboxes/2026-10-12__rebuild-phone-voice-budget-against-published-masking.py · observed RESULT: FAIL phone no-duck [3, 2, 2], phone+6dB [41, 26, 22], headphones 50% [[11,21,41],[7,13,26],[6,11,22]] at 5/10/15 %/dB · Blind rebuild of 'phone speakers have a budget of 2 voices whatever the mixing; headphones 5' on E65's own metric (half the words land), but driven by published speech-in-speech effects instead of invented masking widths: one equal mono talker gives 0.60, 1.5 dB per doubling of talkers, spatial release 6-12 dB, none in mono, a logistic at 5/10/15 %/dB, ducks 0/3/6 dB. With no duck the phone budget is 2 or 3 (3 at 5 %/dB). A 3 dB duck lifts it to 6-11, so 'whatever the mixing' is false. Headphones come out 6-41, never about 5. The 50 percent budgets get large because 1.5 dB per doubling has not been validated past a few talkers, so the exact numbers mean little, but the claim fails in every cell. This agrees with E73, which supersedes it. E65's own sandbox varies only the assumed width, so it could not see level as a lever. · session; blind rebuild review of seven hallucination lessons E63-E73; session_01QGT1LfmPHPG99JEGaPhBwB
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E78 · incompatible · sandboxes/2026-10-12__must-land-voice-duck-size-turns-on-psychometric-slope.py · observed RESULT: FAIL 1/5 held; at 5%/dB mono+6dB carries [2, 3] (log/lin), duck for 6 voices [8.5, 7.5] dB; 15%/dB mono+6dB 8/9 · session; blind rebuild review of seven hallucination lessons E63-E73; session_01QGT1LfmPHPG99JEGaPhBwB
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E88 · incompatible · sandboxes/2026-10-12__duck-must-cover-total-masker-power.py · observed RESULT: PASS 4/4; 6 voices need 11.0/9.0/8.3 dB at 5/10/15%/dB; 6 dB carries 2/3/3; growth 2->6 voices 7.0 dB vs 3.5 at 1.5/doubling · session; brain train follow-up on E78 (missing masking data); session_01KGZvxv8BDgpDMRFTYMfJoJ

## E64 — sound first hallucinations need captions that lie the same way
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][accessibility][captions]
- What: Captions for a sound-first hallucination style (the owner's decision: the first stage is all
  audio). Players who cannot hear get nothing without captions, and captions can reveal which sounds
  are hallucinated.
- Why built: The owner's progression makes the shore stage entirely sound, so captions stop being an
  extra and become the only way some players experience it. A hallucinated sound routed outside the
  caption system, or captioned in a different style, tells a caption reader it is fake.
- Design: Exact model of 10 real and 10 hallucinated shore-stage sounds. Three groups: hear without
  captions, hear with captions on, captions only; shares assumed (60/30/10 and 30/50/20). Policies: no
  captions; real sounds only; both captioned with hallucinations marked; both captioned identically,
  no speaker name for unseen voices. Measured the share of players for whom the hallucinations land
  unspoiled.
- Got right: Identical captions land the shore stage for every player (1.00 in both audiences), and
  without captions a caption-heavy audience loses only its caption-only group (0.80).
- Where/why it failed: The two most natural implementations are the worst. Captioning only real
  sounds (hallucinated audio bypassing the caption system) is worse than no captions at all (0.60 vs
  0.90; 0.30 vs 0.80), because a caption reader hears a sound with no caption and knows; marking
  hallucinations (italics, a question mark) is just as bad. My first version of this sandbox counted
  missing a hallucination as spotting it; it was rewritten with three audience groups before this
  result, and one check had a float rounding bug that was fixed.
- Fix: Send hallucinated sounds through the same caption path as real ones, in the same style, with
  the same speaker rules (no name for any unseen voice), and test it by diffing captions between a
  real and a hallucinated instance of the same sound.
- Why this fix: It gives deaf and muted players the whole first stage and keeps the lie intact for
  everyone; it is seven E10's diff test applied to captions.
- Rule of thumb: Caption hallucinated sounds exactly like real ones: captioning only real sounds is
  worse than no captions (0.30 vs 0.80 of a caption-heavy audience left unspoiled), marking them is as
  bad, and identical captions reach everyone (1.00).
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 4/4
  predictions held; numbers above copied from the run). The audience shares are assumptions, not
  measured; the ranking holds in both mixes tested.
- Composed: ideas:GAME-DESIGN/hallucination-phenomenology/sound-first-then-sight-as-sanity-falls, pappydapimp69__seven/E10, ideas:GAME-DESIGN/disappearance/call-without-a-name
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__sound-first-hallucinations-need-captions-that-lie-the-same-way.py
- Prediction: identical captions best in both audiences; real-only worse than none; tagging worst in a
  caption-heavy audience; with no captions a caption-heavy audience loses only its read-only group.
- Observed: RESULT: PASS 4/4; mostly hearing: 0.90/0.60/0.60/1.00; caption-heavy: 0.80/0.30/0.30/1.00
  (none/real-only/tagged/same)
- Scenarios: 1) mostly hearing audience; 2) caption-heavy audience; each under four caption policies;
  3) built to BREAK the claim: no captions in a caption-heavy audience.
- Link: session; brain train focused loops after the owner's sound-first decision (loop 3); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Audited: 2026-10-12 · modeled · Read the entry and its stored sandbox. The ranking is set by hand: group_effect returns leak 1.0 for real-only and tagged captions and 0.0 for identical captions, so 'identical is 1.00', 'real-only is worse than none' (it loses the both-group as well as the read-group, by construction) and 'tagging is worst' follow from the table for ANY audience shares; sweeping two share mixes cannot test them. Nothing models whether a caption reader actually notices a missing or italic caption, which is the empirical claim. The design advice (one caption path, same style, same speaker rules, diff a real and a hallucinated instance) is sound engineering, but the claim about real players is modeled, not tested. · session; brain train round 2 on seven hallucination lessons (E63-E66); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Reverified: 2026-10-12 · pass · sandboxes/2026-10-12__rebuild-caption-policy-ordering-under-imperfect-noticing.py · observed RESULT: PASS real-only < none in every mix with HC>0 at every d; same >= all; tagged > real-only in 165 cells (only when d<1) · Blind rebuild with my own fixture: all 66 audience mixes on a 0.1 grid of hear-only / hear+captions / captions-only, and a probability d (0.2, 0.5, 0.8, 1) that a caption reader notices a mismatch, where the original assumes certain noticing and only two mixes. Real-only captions are strictly worse than none in every mix with any hear+captions players at every d, and identical captions are never beaten, so the ranking does not depend on the assumed shares. Caveats: the ordering is structural (it follows once a missing caption can be noticed at all), so the sandbox confirms the logic, not player behaviour; the 0.30/0.80/1.00 figures belong to the assumed mixes; 'marking is as bad' holds only at d=1 (165 cells where d<1 put tagged above real-only), though a visible tag is close to d=1; and the 'no name for an unseen voice' rule is itself a tell (P(fake) 0.95 if 1 in 20 real voices is unseen). That tell reaches hearers too, so it is not caption-specific. · session; blind rebuild review of seven hallucination lessons E63-E73; session_01QGT1LfmPHPG99JEGaPhBwB
- Cited-by: 2026-10-14 · projects/pappydapimp69__brainwork.md#E257 · compatible · sandboxes/2026-10-14__curb-cut-reach-collapses-with-setup-friction-and-so-does-the-caption-tell.py · observed RESULT: PASS users 1000/356/50 at friction 0/0.2/0.6 (minority 50); tell-noticers 400 vs 45 (8.9x) · session_017SJAeaijx8mHKPVUZV6hJB brain train auto loop 2 pass 5

## E63 — conditioned phantom belief extinguishes unless pairings are refreshed
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][perception][pacing]
- What: The conditioned-hallucination staging kernel (teach a cue-stimulus pairing honestly, then
  present the cue alone and let the player perceive the missing half) priced over time: how many
  honest pairings it takes, and how many cue-alone phantoms that buys before the learned expectation
  wears away.
- Why built: The kernel says when to show a phantom, not how often. Every cue-alone showing is also
  evidence against the pairing, so the staging spends the very expectation it relies on.
- Design: Rescorla-Wagner learning (a standard associative-learning model, assumed here as a stand-in
  for players): association V moves 0.3 of the way to 1 on a paired event and to 0 on a cue-alone
  event; a phantom is perceived while V is at least 0.6. After 3, 6 or 10 teaching pairings, 12 later
  cues follow three schedules: all alone; alternating real and alone; one real then three alone.
- Got right: Three honest pairings are needed before the first phantom works (V 0.657). Alternating
  real and phantom cues lands 4 to 5 phantoms out of 12, against 1 to 2 when every later cue is a
  phantom.
- Where/why it failed: Teaching longer does not help a phantom-only schedule: 10 pairings still land
  only 2 phantoms, because each cue-alone event cuts V by 30 percent. My break case was also refuted: a
  sparse refresh (one real per three alone) lands no more than all-phantom (1 to 2), so the refresh has
  to be frequent to matter.
- Fix: Interleave honest pairings with phantoms at about one to one throughout, rather than teaching
  up front and then spending; treat each phantom as costing one honest pairing to replace.
- Why this fix: It turns the kernel into a budget the level designer can schedule, and keeps the
  learned expectation alive across a whole run instead of a single burst.
- Rule of thumb: A conditioned phantom (cue shown, stimulus withheld) spends the expectation that makes
  it work: after 3 honest pairings, all-phantom schedules land only 1 to 2 of 12 cues however long the
  teaching, while alternating real and phantom lands 4 to 5; budget one honest pairing per phantom.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 3/4
  predictions held; numbers above copied from the run). Rescorla-Wagner and its constants are an assumed
  model of players, not measured; the Powers et al. 2017 basis of the kernel was checked earlier via a
  published commentary.
- Composed: ideas:GAME-DESIGN/hallucination/conditioned-hallucination-staging, pappydapimp69__seven/E57, pappydapimp69__seven/E56
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__conditioned-phantom-belief-extinguishes-unless-pairings-are-refreshed.py
- Prediction: at least 3 pairings needed; with all later cues alone at most 2 phantoms land even after
  10 pairings; alternating real and alone beats all-phantom; a sparse refresh also beats all-phantom.
- Observed: RESULT: FAIL 3/4; need 3; t3: 1/4/1; t6: 2/5/2; t10: 2/5/2 (all-phantom/partial/sparse)
- Scenarios: 1) taught 3; 2) taught 6; 3) taught 10; each with all-phantom, alternating and sparse
  schedules; 4) built to BREAK the claim: the sparse refresh (it broke).
- Link: session; brain train focused loops after the owner's sound-first decision (loop 2); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E70 · compatible · no sandbox · session; correction after the 2026-10-12 review of seven hallucination lessons; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-12 · fail · sandboxes/2026-10-12__rebuild-seven-e63-phantom-steady-state.py · observed RESULT: PASS 3/3; E63 constants 1:1 late 0/15 (V* 0.588), 2:1 10/10; 1:1 sustains in 4/9 cells; 2:1 in 9/9 (my predictions held; they refute E63's Fix) · Rebuilt with Rescorla-Wagner at learning rates 0.2/0.3/0.45 and thresholds 0.5/0.6/0.7, 6 teaching pairings, and a 60-cue run (E63 used 12) counting phantoms landed only in cues 31-60, after teaching has worn off. E63's Fix (interleave about one honest pairing per phantom) fails at E63's own constants: a 1:1 cycle converges to V = 1/(2-a) = 0.588 before each phantom, below the 0.6 threshold, so it lands 0 of 15 late phantoms; the 4 to 5 of 12 E63 reported is carry-over from the teaching burst. 1:1 sustains phantoms in only 4 of 9 cells; 2:1 (V* 0.776 at a 0.3) sustains them in all 9. Note RW has no partial-reinforcement extinction effect, which in real learners slows extinction under mixed schedules; that is untested either way. · session; brain train round 2 on seven hallucination lessons (E63-E66); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E75 · incompatible · sandboxes/2026-10-12__one-to-one-refresh-lets-conditioned-phantoms-die.py · observed RESULT: PASS 3/3; E63 constants 1:1 late 0/15 (V* 0.588), 2:1 10/10; 1:1 sustains in 4/9 cells; 2:1 in 9/9 · session; brain train round 2 on seven hallucination lessons (E63-E66); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Reverified: 2026-10-12 · fail · sandboxes/2026-10-12__rebuild-phantom-extinction-across-learners.py · observed RESULT: FAIL rw cells off claim 7/9; beta learner thr 0.6: teach 3/10/20 all-phantom 2/7/12, alternating 6/6/6; thr 0.7: 1/4/9 · Blind rebuild from the claim only. Own fixture: Rescorla-Wagner over a 3x3 grid (alpha 0.15/0.3/0.5, threshold 0.5/0.6/0.7) plus a second learner, a Beta-count Bayesian, with teaching 3/10/20 and 12 later cues. The claimed numbers (all-phantom 1-2 of 12 after 10 pairings, alternating 4-5) hold in only 2 of 9 RW cells; at alpha 0.15 longer teaching does help (0, 2, 3). Under the Beta learner teaching 20 buys 9-12 all-phantom landings against 1-2 after 3, and all-phantom beats alternating, which reverses the 'one honest pairing per phantom' budget. 'However long the teaching' is a property of RW's fixed-rate forgetting, not of conditioning. RW is assumed, never fitted to players, and real extinction also shows renewal and the partial-reinforcement effect that RW lacks. The original sandbox uses the single alpha 0.3 / threshold 0.6 point, so its result is that model's readout. · session; blind rebuild review of seven hallucination lessons E63-E73; session_01QGT1LfmPHPG99JEGaPhBwB
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E79 · incompatible · sandboxes/2026-10-12__phantom-budget-depends-on-the-assumed-learner.py · observed RESULT: FAIL rw cells off claim 7/9; beta thr 0.6 all-phantom 2/7/12 at teach 3/10/20, alternating 6/6/6 · session; blind rebuild review of seven hallucination lessons E63-E73; session_01QGT1LfmPHPG99JEGaPhBwB
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E87 · incompatible · sandboxes/2026-10-12__conditioned-phantoms-persist-but-reach-a-minority.py · observed RESULT: PASS 4/4; symmetric RW stops after 3/2/1; persistence needs r>=12; fitted all-phantom 12/12; population share max 0.290 · session; brain train follow-up on E78/E79 (missing human data); session_01KGZvxv8BDgpDMRFTYMfJoJ

## E62 — seven hallucination mix is vision led unlike psychosis
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][balance][audio]
- What: The share of SEVEN's hallucination episodes that are voices, computed from its own code
  (pickHallucinationKind in src/state.js, seven-0.34: the player rolls flat over five kinds; companions
  weight by traits), against the auditory share in real psychosis.
- Why built: SEVEN's five kinds are a phantom monolith, a doubled companion, a false pylon, a wrong
  compass and a chorus of voices: one auditory kind in five. Research says real psychosis is
  voice-led, so the game's mix needed measuring before any fidelity decision.
- Design: Exact arithmetic over the five companion templates' chatty and wander traits, with
  selfCare integrated over 0 to 1; the symmetric trait jitter is ignored. Real auditory share 0.55
  (auditory 59 percent of prevalence against visual 27, tactile about 14 and olfactory about 8; Waters
  2014, McCarthy-Jones 2017). Then a reweighted mix: voices 0.55, every other kind kept reachable.
- Got right: The player's mix is 0.20 voices, under half the real share, and even the chattiest
  companion (NKEM) reaches only 0.314 (mean 0.241). A voice-led reweight keeps every kind reachable
  (each other kind 0.112).
- Where/why it failed: My break case was refuted: the reweight cuts visual episodes per 20 from 12.0 to
  6.7 (44 percent), not by half, because DOUBLED_PARTY and FALSE_ANCHOR keep their share. (An earlier
  run also flagged a miss that was a float comparison bug in my check; fixed before this result.)
- Fix: If SEVEN chooses fidelity (an open tension), weight CHORUS to about 0.55 for the player and lift
  companions' chorus weight; keep the visual kinds rarer, which also slows their wear-out (seven E56).
  If it does not, record that the mix is a deliberate screen-first choice, not an accident of the
  flat roll.
- Why this fix: It turns an unexamined default (a flat pick over kinds that happen to be mostly
  visual) into a stated design choice, and gives the fidelity option a concrete weight.
- Rule of thumb: Measure a hallucination system's modality mix from its own code before claiming
  fidelity: SEVEN's flat pick gives the player voices 0.20 of the time against about 0.55 in real
  psychosis, and even its chattiest companion reaches only 0.314.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 3/4
  predictions held; numbers above copied from the run), using SEVEN's weights read from src/state.js.
  The 0.55 real share is my reduction of the cited prevalence figures (one checked review, one
  abstract), so it is approximate.
- Composed: ideas:GAME-DESIGN/hallucination-phenomenology/real-hallucinations-are-voice-led-and-overlay-the-real-scene, pappydapimp69__seven/E56
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__seven-hallucination-mix-is-vision-led-unlike-psychosis.py
- Prediction: the player's mix under half the real share; even NKEM below the real share; the reweight
  keeps every kind at 0.05 or more; the reweight halves visual episodes per 20.
- Observed: RESULT: FAIL 3/4; player voices 0.20, companion mean 0.241, NKEM 0.314, real ~0.55;
  visuals per 20 12.0 -> 6.7
- Scenarios: 1) the player's flat mix; 2) each of the five companions; 3) built to BREAK the claim:
  whether a voice-led reweight halves the visual episodes (it cut them 44 percent).
- Link: session; brain train focused loops on hallucination phenomenology (loop 5); seven src/state.js pickHallucinationKind; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E66 · compatible · sandboxes/2026-10-12__sound-to-sight-curve-shape-sets-how-readable-depth-is.py · observed RESULT: FAIL 3/4; bits linear 0.541 step 1.000 banded 0.470 flat 0.000; early visuals linear 1.67 banded 0.50 · session; brain train focused loops after the owner's sound-first decision (loop 1); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-12 · fail · sandboxes/2026-10-12__rebuild-seven-e62-modality-mix.py · observed RESULT: FAIL 2/3; player 0.200; NKEM clamped 0.309 (no jitter 0.314); companion mean 0.241; reference auditory share 0.38..0.71 for 0.5x..2x episode rates · Re-derived from src/state.js pickHallucinationKind at seven-0.34.0 (4cc7f1a^), integrating the trait jitter WITH clamp01 (E62 ignored it). The code arithmetic holds: player CHORUS 0.200, companion mean 0.241, NKEM 0.309 (E62 0.314; the clamp at chatty 1.0 trims it). The comparison does not hold. The 0.55 'real share' divides two separate per-patient prevalences (Waters 2014: AH 59 percent, VH 27 percent; McCarthy-Jones 2017 gives tactile 9-19 and olfactory 6-10 percent as lifetime ranges, not 14 and 8), which says nothing about the share of EPISODES; with voice episodes per hearer 0.5x to 2x other modalities' the reference spans 0.38 to 0.71, and at 0.5x 'under half' fails. Two more problems: the player's CHORUS is delivered as HUD text lines plus a 0.75 s tonal blip (hud.js chorusEcho, audio.js chorus), so counting it as auditory overstates the game's voice share; and seven-1.0.0 deleted the whole hallucination-kind system, so the lesson describes code that no longer exists on main. · session; review of seven hallucination lessons (E46, E55-E62); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E71 · compatible · sandboxes/2026-10-12__voices-dominate-by-time-so-sound-is-a-bed-and-visions-are-events.py · observed RESULT: PASS 3/3; prevalence 0.686; time share central 0.992, range 0.766..0.999 · session; follow-up to the 2026-10-12 review of seven E62; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E80 · incompatible · sandboxes/2026-10-12__voice-time-share-is-a-population-claim-not-per-player.py · observed RESULT: FAIL pop share >= 0.888 everywhere; lowest person 0.002 (vision 5 min x 50/wk); up to 0.28 of voice-hearers below the prevalence share · session; blind rebuild review of seven hallucination lessons E63-E73; session_01QGT1LfmPHPG99JEGaPhBwB

## E61 — misperceived real objects outlast inserted phantoms
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][perception][deception]
- What: Which form of hallucination survives a player's reality checks longest: an inserted phantom
  (an object that is not there), an altered real object (a spent pylon that looks lit), or a felt
  presence, given the verbs the player has (touch, use, ask a companion).
- Why built: Real hallucinations mostly overlay the real scene, and early ones are minor phenomena
  (misperceived objects, presence, passage; 48, 23 and 29 percent of minor phenomena in a Parkinson's
  study). The movie image is the inserted phantom. The question for an art style is which form the
  game's own verification verbs can expose.
- Design: Exact model. Touch exposes an inserted phantom always, an altered object never (it is solid),
  a presence half the time. Use exposes inserted and altered always, presence never. Asking a lucid
  companion exposes any form with 0.8. Kits: touch only, touch and use, touch, use and ask; the player
  cycles their verbs; expected checks to exposure, capped at 12.
- Got right: An inserted phantom falls to the first touch in every kit; an altered real object survives
  touch-only checking entirely (exposure 0) and outlasts the phantom in every kit (2.00 checks vs 1.00);
  a presence lasts longest for a solo player who can only touch and use (2.97 checks).
- Where/why it failed: Nothing in the run refuted the predictions, but the result is mostly set by the
  verb table I wrote: the sandbox shows the consequence of which verb exposes which form, not new
  facts about perception. With a companion to ask, every form falls within about 2 checks, so a party
  quickly undoes any hallucination style.
- Fix: Match the hallucination form to the verbs available: when the player can touch, prefer altered
  real objects and presences (as SEVEN's FALSE_ANCHOR dead pylons and DOUBLED_PARTY already do) over
  inserted phantoms; save inserted phantoms for moments when touch is unavailable (distance, dark,
  alone).
- Why this fix: It follows the real phenomenology (overlay, minor phenomena) and keeps hallucinations
  alive against the game's own verification verbs, which is seven E10's rule of lying about state seen
  from the player's side.
- Rule of thumb: A hallucination that alters a real object survives touch checks that kill an inserted
  phantom at once (2.00 vs 1.00 checks; touch-only never exposes it), so prefer altered objects and felt
  presences where the player can touch, and match the hallucination form to the verbs they have.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 4/4
  predictions held; numbers above copied from the run). The exposure probabilities are my design
  table; the minor-phenomena proportions were checked on the cited Parkinson's paper (PMC8505047).
- Composed: pappydapimp69__seven/E10, pappydapimp69__seven/E57, ideas:GAME-DESIGN/hallucination-phenomenology/minor-phenomena-come-first
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__misperceived-real-objects-outlast-inserted-phantoms.py
- Prediction: an inserted phantom falls to the first touch in every kit; an altered object survives
  touch-only entirely; altered outlasts inserted in every kit; with a party every form falls within 3
  checks.
- Observed: RESULT: PASS 4/4; solo-touch altered survives 1.00; solo checks ins/alt/pres
  1.00/2.00/2.97; party 1.00/2.00/2.22
- Scenarios: 1) touch only; 2) touch and use; 3) touch, use and ask; 4) built to BREAK the claim: a party,
  where every form should fall fast.
- Link: session; brain train focused loops on hallucination phenomenology (loop 2); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E65 · compatible · sandboxes/2026-10-12__sound-first-voices-collapse-on-phone-speakers.py · observed RESULT: PASS 3/3; budgets all-outer/34%-inner headphones 5/4; stereo speakers 2/3; phone speaker 2/2 · session; brain train focused loops after the owner's sound-first decision (loop 4); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Audited: 2026-10-12 · modeled · Read the entry and its stored sandbox. Every result is the author's verb table restated: touch exposes inserted 1.0 and altered 0.0, so 'inserted falls to the first touch' and 'altered survives touch-only entirely' are inputs, and 2.00 vs 1.00 checks is the touch-then-use cycle order. The entry says as much. No player or perception data is involved, so the claim about which form survives real reality checks is modeled. The source is reworded: PMC8505047 (Zhong et al. 2021) gives visual illusions 48.4, passage 28.7 and presence 23.0 percent of 122 minor-hallucination EPISODES in 74 patients; 'misperceived objects' is only the object-misidentification slice (19.7 percent), the 48 percent is all illusions together. · session; review of seven hallucination lessons (E46, E55-E62); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E70 · compatible · no sandbox · session; correction after the 2026-10-12 review of seven hallucination lessons; session_01NHKVhTvCnvtvZ2NGLSPYj6

## E60 — inner voices cannot be spread so binaural budget shrinks
- Date: 2026-10-12
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][audio][voices]
- What: seven E55's voice budget (hallucinated voices stay intelligible up to a few spread around the
  head) re-tested with voices heard INSIDE the head, which have no position to spread: in a survey of
  199 voice-hearers, 34 percent heard voices inside the head, 28 percent outside and 38 percent both.
- Why built: E55 assumed every voice could be placed around the head. A faithful voice-led art style
  will put many voices inside the head, and those cannot benefit from binaural separation.
- Design: Exact model as E55 (each voice talks 0.4 of the time; outer voices spread evenly, masking
  only neighbours within 60 degrees), plus a share p of inner voices that mask and are masked by every
  voice. Swept p = 0, 0.25, 0.5, 1 and 1 to 12 voices.
- Got right: Inner voices shrink the budget fast: with half the voices inside, 4 voices land only
  0.288 of words (1.000 all outside) and the budget falls to 2, the same as putting every voice in one
  place; at a quarter inside, 4 voices land 0.504.
- Where/why it failed: My check that the all-outside case reproduces E55's budget of 4 failed: it is
  5. E55 only tested 1, 2, 3, 4, 6, 8 and 12 voices, and 5 voices spread 72 degrees apart never mask
  under its own assumption. E55's 'about 4' is an artefact of the sample, and its true budget under
  that model is 5.
- Fix: Count inner voices separately in the voice budget: keep at most 2 voices when any meaningful
  share are inside the head, and use outside voices for the spread scenes; read E55's spread budget as
  5, not 4.
- Why this fix: It keeps the voice-led style faithful (many voices are inner) while keeping the line
  that matters audible, and it corrects the upstream number instead of building on it.
- Rule of thumb: Voices heard inside the head cannot be spread, so they collapse the binaural budget:
  with half the voices inner, 4 voices landed 0.288 of words and the budget fell from 5 to 2; count
  inner voices as one-place voices.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 3/4
  predictions held; numbers above copied from the run). The inside/outside shares were checked on the
  survey paper (PMC3885292); the masking model is E55's assumption, unchanged.
- Composed: pappydapimp69__seven/E55, ideas:GAME-DESIGN/hallucination-phenomenology/real-hallucinations-are-voice-led-and-overlay-the-real-scene
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__inner-voices-cannot-be-spread-so-binaural-budget-shrinks.py
- Prediction: all-outside reproduces E55 (4 voices land 1.000, budget 4); half inner cuts 4-voice
  landing below 0.5; all inner collapses to a budget of 2; a quarter inner keeps the budget at 3 or more.
- Observed: RESULT: FAIL 3/4; 4-voice landing by inner share 1.000/0.504/0.288/0.216; budget 5/5/2/2.
  Missed: the all-outside budget is 5, not E55's 4.
- Scenarios: 1) all outside; 2) a quarter inside; 3) half inside; 4) all inside; 5) built to BREAK the
  claim: a quarter inside, where the budget should survive.
- Link: session; brain train focused loops on hallucination phenomenology (loop 3); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-12 · fail · sandboxes/2026-10-12__rebuild-seven-e60-inner-voice-budget.py · observed RESULT: FAIL 1/3; w45 p0.3 7/4/2 (one place 2); w45 p0.5 7/2/2; w90 p0.3 3/4/2; w90 p0.5 3/2/2 · Rebuilt with masking width 45 and 90 (E60 inherited E55's 60), talk share 0.3 and 0.5, and inner shares 0.34 (the survey's inside-only) and 0.72 (inside-only plus half of 'both'); outer voices spread evenly, inner voices masked by and masking everyone, budget by mean landing. The high-inner case held: at 0.72 the budget equals the one-place budget in every cell. But the Rule's general claim that inner voices collapse the budget failed in one cell (w 90, p 0.3: all outside 3, a third inner 4, because fewer outer voices spread wider), and E60's corrected 'budget 5' is again width-bound (7 at 45 degrees, 3 at 90). The 34/28/38 shares match PMC3885292 (n 197 answering of 199). · session; review of seven hallucination lessons (E46, E55-E62); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E69 · incompatible · sandboxes/2026-10-12__voice-budget-is-a-readout-of-masking-width.py · observed RESULT: FAIL 0/3; one-place budget p0.2/0.4/0.6 4/2/1; spread at p0.4 w30..120 11/7/5/3/2; spread range 2-23 · session; review of seven hallucination lessons (E46, E55-E62); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E70 · compatible · no sandbox · session; correction after the 2026-10-12 review of seven hallucination lessons; session_01NHKVhTvCnvtvZ2NGLSPYj6

## E59 — punishing sanity meter makes a death spiral
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][sanity][hallucination][balance]
- What: A sanity meter that PUNISHES (low sanity makes the player worse at the game: shakier aim,
  sluggish controls) against one that only changes PERCEPTION (low sanity changes what is shown, not
  how well the player can act), modelled as a Markov chain over sanity levels.
- Why built: Treating a broken mind as a failure state is both a design choice and a representation
  choice. The design half can be measured: a penalty that makes failure likelier, where failure lowers
  sanity, is a positive feedback loop, and nobody had priced how strong it is. Real precedent (checked
  on the pages): Eternal Darkness's sanity patent (US 6,935,954, Nintendo, expired) claims low sanity
  impairs control response; Amnesia's designer wrote that they eventually removed all challenge from
  its sanity system so it became a feature with few gameplay implications (Game Developer deep dive).
- Design: Exact Markov chain, sanity 0 to 5, start at 5, 12 encounters. A failed encounter drops sanity
  by 1, a success recovers 1 with probability 0.3; sanity 0 is collapse. Perception-only: fail chance
  0.30 at every level. Punishing: 0.30 plus 0.10 per lost level. Mild punishing: plus 0.03 per level.
- Got right: Punishment quadruples collapse (0.499 vs 0.126, x3.97) and lowers the mean end sanity
  (1.57 vs 2.90), while the perception-only meter still lets some players collapse, so dread does not
  need the death spiral to have stakes.
- Where/why it failed: My break case was refuted: even a mild penalty (0.03 per level) nearly doubles
  collapse (0.229 vs 0.126, x1.82, not within x1.3). The spiral is not a property of harsh tuning; any
  coupling of sanity to competence feeds it.
- Fix: Make low sanity change perception (what is shown, heard, believed), not competence; if a
  mechanical cost is wanted, take it from a separate resource, or make recovery easier at low sanity so
  the loop is damped rather than amplified.
- Why this fix: It keeps the art style's dread without a feedback loop that ends runs for players who
  are already struggling, and it avoids presenting a mind in distress as a player who simply gets
  worse, which the representation critique of sanity meters objects to.
- Rule of thumb: Never let a sanity meter reduce the player's competence: failures lower sanity and
  lower sanity raises failures, so even a 0.03-per-level penalty raised collapse x1.82 and a 0.10 one
  x3.97; let low sanity change perception, not skill.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 2/3
  predictions held; numbers above copied from the run). Fail and recovery rates are assumptions; the
  feedback direction is what the chain shows.
- Composed: pappydapimp69__seven/E27, local__sandbox-loot-pity/E1
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__punishing-sanity-meter-makes-a-death-spiral.py
- Prediction: punishing collapses at least 2x as often; perception-only still above 0; a mild penalty
  stays within x1.3 of perception-only.
- Observed: RESULT: FAIL 2/3; collapse perception 0.126 punish 0.499 (x3.97); mild 0.229
- Scenarios: 1) perception-only; 2) punishing 0.10 per level; 3) built to BREAK the claim: mild 0.03 per
  level (it broke the claim that mild is safe).
- Link: session; brain train loop on hallucination as an art style (loop 4); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-12 · pass · sandboxes/2026-10-12__rebuild-seven-e59-sanity-spiral-recovery.py · observed RESULT: FAIL 2/4; mild ratio x2.43/x3.44/x5.34/x7.41; strong ratio x5.57/x14.35/x52.71/x160.60 (rho 0.1/0.3/0.6/0.9); damped x10.03 (misses are magnitude and the Fix, not the rule) · Rebuilt with a 0..8 meter, 25 encounters, base fail 0.25, recovery rho 0.1/0.3/0.6/0.9 and penalties 0.02/0.08 per level (E59: 0..5, 12 encounters, rho 0.3, 0.03/0.10). The Rule of thumb holds and its numbers UNDERSTATE it: the mild penalty raised collapse x2.43 to x7.41 and the strong one x5.57 to x160.6, growing with recovery rate because the perception-only baseline vanishes faster than the punished one. So the specific ratios are tuning-bound but the direction is robust. One part of E59's Fix did not hold: making recovery easier at low sanity (rho +0.08 per level lost) left strong-penalty collapse at x10.0 of perception-only, so 'damp the loop with recovery' is not a substitute for not coupling sanity to competence. Sources: the Nintendo patent US 6,935,954 does recite impaired reactions to commands, but in dependent claims 6 and 16, not claim 1; it expired 2021. The Amnesia quote matches Grip's Game Developer deep dive word for word. · session; review of seven hallucination lessons (E46, E55-E62); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E67 · compatible · sandboxes/2026-10-12__easier-recovery-does-not-undo-a-sanity-competence-penalty.py · observed RESULT: FAIL 2/4; mild ratio x2.43/x3.44/x5.34/x7.41; strong ratio x5.57/x14.35/x52.71/x160.60 (rho 0.1/0.3/0.6/0.9); damped x10.03 · session; review of seven hallucination lessons (E46, E55-E62); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E76 · compatible · sandboxes/2026-10-12__sanity-penalty-cancels-only-with-damping-several-times-steeper.py · observed RESULT: PASS 3/3; damping needed pen 0.03: 0.1; pen 0.06: 0.28; pen 0.1: None · session; follow-up to the blind rebuild of seven E67; session_01NHKVhTvCnvtvZ2NGLSPYj6

## E58 — more hallucinated voices turn words into texture
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][audio][voices]
- What: Hallucinated voices as an art style (Hellblade's binaural 'furies' around and inside the
  player's head): how many simultaneous voices can speak before individual words stop landing, and
  how much spreading them around the head buys.
- Why built: A design that uses voices both as texture (dread) and as content (a voice that says
  something the player must hear) needs to know where one turns into the other. Voice-hearers commonly
  report several voices (81 percent in Woods et al. 2015, Lancet Psychiatry, from the paper's summary),
  so a multi-voice scene is the faithful case.
- Design: Exact model. Each voice talks 40 percent of the time, independently; a phrase lands if no
  masking voice talks over it. All voices in one place: every other voice masks. Spread evenly around
  the head: only voices within 60 degrees mask (a simplified stand-in for binaural release from
  masking). 1 to 12 voices.
- Got right: Spreading voices around the head doubles how many can speak while at least half the
  words land (4 against 2), and at 4 voices spread placement keeps every word (1.000) where one place
  keeps 0.216.
- Where/why it failed: Even spread placement does not scale: at 12 voices only 0.130 of words land, so
  past about 6 voices the scene is texture whatever the mixing. The 60-degree masking width is my
  assumption and the exact counts move with it.
- Fix: Decide per scene whether voices are content or texture. For content, keep at most 2 voices in
  one place or about 4 spread around the head, and duck the others when a line must land; for texture,
  use as many as wanted and stop expecting words to be heard.
- Why this fix: It gives sound design a budget instead of a guess, and keeps the line that matters
  audible without breaking the overlapping-voices style the art direction depends on.
- Rule of thumb: Hallucinated voices are content up to about 2 in one place or 4 spread around the
  head (words landing 0.216 vs 1.000 at 4 voices) and texture beyond about 6; duck the rest when one
  line must land.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 3/3
  predictions held; numbers above copied from the run). Hellblade's binaural recording and its
  consultation with voice-hearers were checked on a BPS article; the 81 percent figure is from a
  search summary of the paper, not read in full.
- Composed: pappydapimp69__mirage/E19
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__more-hallucinated-voices-turn-words-into-texture.py
- Prediction: with one place, 4 voices land under 0.25 of words; spreading doubles the voice count that
  stays half-intelligible; at 12 voices even spread placement drops below 0.5.
- Observed: RESULT: PASS 3/3; 4 voices one place 0.216 spread 1.000; 12 spread 0.130; max
  half-intelligible 2 vs 4
- Scenarios: 1) one place, 1 to 12 voices; 2) spread placement, 1 to 12 voices; 3) built to BREAK the
  claim: 12 voices spread, testing whether spreading scales without limit.
- Link: session; brain train loop on hallucination as an art style (loop 1); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-12 · fail · sandboxes/2026-10-12__rebuild-seven-e58-voice-budget-width.py · observed RESULT: FAIL 0/3; one-place budget p0.2/0.4/0.6 4/2/1; spread at p0.4 w30..120 11/7/5/3/2; spread range 2-23 · Rebuilt sweeping the two constants E58 picked: masking width w 30/45/60/90/120 degrees and talk share p 0.2/0.4/0.6. The budget is not a property of voices, it is a readout of those two numbers. One-place budget was 4/2/1 at p 0.2/0.4/0.6; spread budget at p 0.4 was 11/7/5/3/2 across w 30..120 (5 at E58's own 60, as E60 found, not 4), and the 'spreading doubles it' claim failed at w 120 (2 vs 2). Under even spacing the model only masks once 360/N <= w, so 'about 4 spread' is just 360/60 minus one. Real binaural release from masking is a graded few-dB effect, not a 60 degree on/off cone. Woods et al. 2015's 81 percent multiple-voices figure checks out (124 of 153). · session; review of seven hallucination lessons (E46, E55-E62); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E69 · incompatible · sandboxes/2026-10-12__voice-budget-is-a-readout-of-masking-width.py · observed RESULT: FAIL 0/3; one-place budget p0.2/0.4/0.6 4/2/1; spread at p0.4 w30..120 11/7/5/3/2; spread range 2-23 · session; review of seven hallucination lessons (E46, E55-E62); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E70 · compatible · no sandbox · session; correction after the 2026-10-12 review of seven hallucination lessons; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E73 · compatible · sandboxes/2026-10-12__voice-budget-from-published-masking-data.py · observed RESULT: PASS 4/4; 80% budgets mono 1 headphones 4 (low-release 4); with 6 dB duck mono 6 headphones 13; 50% budgets mono 2 headphones 13 · session; follow-up to the 2026-10-12 review of seven E58 and E60; session_01NHKVhTvCnvtvZ2NGLSPYj6

## E57 — hallucination flicker needs a window cap not an average rate
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][accessibility][vfx]
- What: Flickering hallucination effects (stuttering lights, a world 'glitching') against the
  photosensitive-epilepsy rule: WCAG 2.3.1 allows no more than three flashes in ANY one-second period
  unless the flashing stays below the general and red flash thresholds (checked on the W3C page).
- Why built: A glitch look wants irregular flicker, and the obvious safety check is an average rate.
  The rule is about every one-second window, and irregular timing clusters flashes, so the average was
  suspected to be the wrong check.
- Design: Flash start times from a fixed-seed generator with irregular gaps (mean 1.5, 2.0 or 2.5 per
  second, 60 seconds). Compared the raw irregular schedule, the same schedule with a sliding-window cap
  (a flash is dropped if it would make four within one second), and a perfectly regular schedule.
  Measured the worst one-second window.
- Got right: The window cap never exceeds 3 in any window at any rate, and a regular 2.5 per second
  flicker stays within 3, so the rule is easy to satisfy once it is checked in the right form.
- Where/why it failed: Irregular flicker averaging only 1.5 flashes per second still hit 7 in one
  second, and at 2.5 per second 0.258 of all one-second windows broke the rule. The cap also costs more
  flicker than I predicted: it keeps 0.75 of flashes at 2.0 per second, not 0.80.
- Fix: Enforce the three-per-second limit as a sliding-window cap in the effect scheduler (or keep the
  flashing area under the threshold, about a quarter of a 10 degree field), avoid saturated-red flashes,
  and test with a flash analyser rather than an average rate.
- Why this fix: It checks the rule as written, keeps the irregular look the art style wants, and costs
  only the clustered flashes that would have been dangerous.
- Rule of thumb: Cap hallucination flicker per sliding one-second window, never by average rate:
  irregular flicker averaging 1.5 per second still hit 7 flashes in a second, while a window cap held
  every window to 3 and kept 0.75 of the flashes.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 4/5
  predictions held; numbers above copied from the run). The three-flash rule and thresholds were checked
  on W3C's WCAG 2.3.1 page; the flash timings are a model, not measured luminance.
- Composed: pappydapimp69__seven/E45, pappydapimp69__mirage/E19
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__hallucination-flicker-needs-a-window-cap-not-an-average-rate.py
- Prediction: irregular 2.5 per second breaks the rule; irregular 1.5 per second also breaks it; the cap
  never exceeds 3; the cap keeps at least 80 percent at 2.0 per second; a regular 2.5 per second stays
  within 3.
- Observed: RESULT: FAIL 4/5; worst windows jitter 7/8/8 capped 3/3/3; cap keeps 0.75 at 2.0/s
- Scenarios: 1) irregular at 1.5, 2.0 and 2.5 per second; 2) window-capped; 3) regular; 4) built to
  BREAK the claim: a low 1.5 per second average, which still broke the rule.
- Link: session; brain train loop on hallucination as an art style (loop 5); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E61 · compatible · sandboxes/2026-10-12__misperceived-real-objects-outlast-inserted-phantoms.py · observed RESULT: PASS 4/4; solo-touch altered survives 1.00; solo checks ins/alt/pres 1.00/2.00/2.97; party 1.00/2.00/2.22 · session; brain train focused loops on hallucination phenomenology (loop 2); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E63 · compatible · sandboxes/2026-10-12__conditioned-phantom-belief-extinguishes-unless-pairings-are-refreshed.py · observed RESULT: FAIL 3/4; need 3; t3: 1/4/1; t6: 2/5/2; t10: 2/5/2 (all-phantom/partial/sparse) · session; brain train focused loops after the owner's sound-first decision (loop 2); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-12 · pass · sandboxes/2026-10-12__rebuild-seven-e57-flicker-window.py · observed RESULT: FAIL 2/3; worst raw at 1.0/s poisson 7.0 bursty 10.0; worst capped 3.0; kept at 2/s 0.74/0.80/0.76/0.56/0.56/0.58 (the miss is the kept fraction, not the claim) · Rebuilt with two different generators (Poisson and a bursty two-state Markov one), seeds 7/11/13, 120 s, mean rates 1.0/1.5/2.0, and flashes counted as WCAG defines them (a pair of opposing transitions, 80 ms each) rather than as start times. The claim holds harder than stated: even 1.0 per second irregular flicker hit 7 (Poisson) and 10 (bursty) flashes in a second, and a greedy sliding-window cap held every window to 3 counted as transition pairs. Caveats: the cap holding 3 is true by construction, so it is not evidence; and the 'keeps 0.75 of flashes' figure is generator-bound (Poisson 0.74-0.80, bursty 0.56-0.58). Sources: WCAG 2.3.1 wording and the 25 percent of a 10 degree field area threshold match the W3C page. · session; review of seven hallucination lessons (E46, E55-E62); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E81 · compatible · sandboxes/2026-10-12__hallucination-sway-out-of-the-sickness-band-and-off-the-full-frame.py · observed RESULT: PASS 3/3; relative doses full-frame sway 0.3 Hz 1.000; slow drift 0.05 Hz 0.251; jitter 2 Hz 0.040; vignette-only 0.300; vignette-only jitter 2 Hz 0.012 · session; gap loop on motion sickness in hallucination effects, 2026-10-12; session_01NHKVhTvCnvtvZ2NGLSPYj6

## E56 — fourth wall sanity effects wear out shuffle bag and variants
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][sanity][procgen]
- What: Scheduling a finite pool of authored fourth-wall hallucination effects (the Eternal Darkness
  style: a fake save wipe, a fake controller unplug) when each effect loses most of its power after
  the player has seen it once, comparing random picks, a no-repeat shuffle bag, and derived variants.
- Why built: Hallucination as an art style spends surprise, and surprise does not survive a repeat. A
  game that fires these effects at random wastes some of its best ones on the second showing, and no
  existing lesson priced how fast a pool runs dry.
- Design: Exact expected values. Pool of 8 effects; 8, 16 or 24 triggers per playthrough. An effect's
  value on its k-th showing is 0.35^k (habituation rate assumed); below 0.2 counts as a dud. Random
  picks with repeats; a shuffle bag (no repeat until the pool is used up); and derived variants whose
  similarity to earlier showings is 0.4, so value is 0.35^(0.4k).
- Got right: With as many triggers as effects, the shuffle bag delivers 8.00 against random's 6.06
  (x1.32), and derived variants keep duds at zero even at three times the pool (16.71 total vs 11.78
  for the plain shuffle bag), which matches the derived-vs-authored-tells kernel.
- Where/why it failed: My prediction that duds would already jump at twice the pool was refuted (0.00
  at 16 triggers, because a second showing still scores 0.35); they arrive at three times the pool
  (0.33). Random picks are worse than they look: 0.25 of triggers are duds at 16 triggers, with the
  pool not even exhausted.
- Fix: Fire authored fourth-wall effects from a shuffle bag, never at random; budget roughly two
  showings per effect per playthrough; past that, derive variants (change the target, the timing, the
  fake message) rather than repeating the authored effect.
- Why this fix: It spends each effect's surprise once at full strength, delays the dud wall to where
  variants can take over, and uses derivation, the same tool that keeps SEVEN's tells fresh.
- Rule of thumb: Schedule fourth-wall hallucination effects from a no-repeat shuffle bag (x1.32 the
  scare of random picks when triggers equal the pool) and switch to derived variants past about two
  showings per effect; random picks already waste a quarter of triggers by twice the pool.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 3/4
  predictions held; numbers above copied from the run). The habituation rate 0.35 and the variant
  similarity 0.4 are assumptions, so the counts are structural.
- Composed: ideas:GAME-DESIGN/deduction/derived-vs-authored-tells, pappydapimp69__mirage/E19
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__fourth-wall-sanity-effects-wear-out-shuffle-bag-and-variants.py
- Prediction: shuffle beats random by at least 25 percent at triggers equal to the pool; shuffle duds
  reach 0.5 or more at three times the pool; variants keep duds at 0 through three times the pool; at
  triggers equal to the pool variants add nothing.
- Observed: RESULT: FAIL 3/4; M=N random 6.06 shuffle 8.00; M=3N shuffle 11.78 duds 0.33 vs variants
  16.71 duds 0.00
- Scenarios: 1) 8 triggers; 2) 16 triggers; 3) 24 triggers; 4) built to BREAK the claim: triggers equal
  to the pool, where variants should add nothing.
- Link: session; brain train loop on hallucination as an art style (loop 2); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E62 · compatible · sandboxes/2026-10-12__seven-hallucination-mix-is-vision-led-unlike-psychosis.py · observed RESULT: FAIL 3/4; player voices 0.20, companion mean 0.241, NKEM 0.314, real ~0.55; visuals per 20 12.0 -> 6.7 · session; brain train focused loops on hallucination phenomenology (loop 5); seven src/state.js pickHallucinationKind; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E63 · compatible · sandboxes/2026-10-12__conditioned-phantom-belief-extinguishes-unless-pairings-are-refreshed.py · observed RESULT: FAIL 3/4; need 3; t3: 1/4/1; t6: 2/5/2; t10: 2/5/2 (all-phantom/partial/sparse) · session; brain train focused loops after the owner's sound-first decision (loop 2); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E66 · compatible · sandboxes/2026-10-12__sound-to-sight-curve-shape-sets-how-readable-depth-is.py · observed RESULT: FAIL 3/4; bits linear 0.541 step 1.000 banded 0.470 flat 0.000; early visuals linear 1.67 banded 0.50 · session; brain train focused loops after the owner's sound-first decision (loop 1); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-12 · fail · sandboxes/2026-10-12__rebuild-seven-e56-shuffle-habituation.py · observed RESULT: FAIL 1/3; ratio range x1.150-x1.421; random dud share at 2N 0.020-0.259 · Rebuilt with pools N 5 and 12, habituation r 0.2/0.5/0.65 (E56 used N 8, r 0.35), closed-form random expectation and exact binomial dud shares. The direction is a theorem and held everywhere: a shuffle bag never scores below random picks. The numbers the Rule of thumb states do not transfer: the shuffle/random ratio at M = N ran x1.150 to x1.421 (x1.32 is r = 0.35 only), and 'random picks already waste a quarter of triggers by twice the pool' held only at r = 0.2; at r 0.5 and 0.65 the dud share was 0.020 to 0.097. 'Switch to variants past about two showings' is likewise the dud threshold of the assumed r (duds start at showing 3, 4 or 5 depending on r). Keep the shuffle-bag advice; drop the numbers or state them as conditional on habituation. · session; review of seven hallucination lessons (E46, E55-E62); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E74 · incompatible · sandboxes/2026-10-12__depth-readability-is-set-by-neighbour-band-spacing.py · observed RESULT: FAIL 0/3; equal-time bits/5-ep accuracy linear 0.541/0.829 banded 0.470/0.718 band0.3 0.455/0.680 band0.7 0.529/0.680 step 1.000/0.500; shallow-heavy banded 0.373b · session; brain train round 2 on seven hallucination lessons (E63-E66); session_01KGZvxv8BDgpDMRFTYMfJoJ

## E55 — believable hallucination renders the players learned prior
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][perception][deception]
- What: Where to place a phantom (a hallucinated pylon) so the player believes it, using the
  predictive-processing account of hallucination: perception combines prior expectation with
  evidence, and hallucinations arise when learned expectations outweigh weak evidence.
- Why built: A hallucination art style can show anything; the question is what will be MISTAKEN for
  real. Powers, Mathys and Corlett (Science, 2017) induced hearing tones that were never played by
  first pairing a light with a near-threshold tone (checked via a commentary on PubMed Central), which
  suggests the most believable phantom is the one the player has been taught to expect.
- Design: Exact Bayes. Real pylons stand at path junctions with rate q (the world's regularity, which
  the player has learned) and on open stretches with rate 0.02. A phantom rendered exactly like a real
  pylon is placed at a junction (prior-shaped) or on an open stretch (random); belief = P(real | seen
  here). Also a weak visual tell (likelihood ratio 0.5).
- Got right: With q = 0.8 a junction phantom is believed 0.800 against 0.020 for a random one (x40),
  belief tracks the world's regularity (0.8, 0.5, 0.1), and a weak visual tell barely dents a
  prior-shaped phantom (0.667). When the world has no regularity (q = 0.1) the advantage shrinks to
  x5, so the effect is bought by teaching a pattern first.
- Where/why it failed: Nothing in the run refuted the predictions, but with no visual tell the
  belief simply equals the prior: the sandbox shows Bayes' rule at work rather than discovering it.
  The design content is the consequence, not the arithmetic: a random phantom is spotted almost
  every time.
- Fix: Build hallucinations from the world's own regularities: teach a pattern honestly first (where
  pylons stand, what a call sounds like), then show the phantom where the pattern predicts. This is
  the conditioning method of Powers et al. used as staging, and it fits seven E10's rule to lie about
  the state of what the player expects rather than conjure the unexpected.
- Why this fix: It turns believability into something the level teaches and the designer controls,
  and keeps phantoms legible as the world's own logic going wrong, which is the art style's point.
- Rule of thumb: A hallucination is believed in proportion to what the player has learned to expect:
  a phantom where the world taught them things appear was believed 0.800 against 0.020 at random
  (x40); teach the pattern honestly first, then break it there.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 4/4
  predictions held; numbers above copied from the run). The Powers et al. finding was checked via the
  2018 Corlett and Powers commentary; the rates q and 0.02 are my choices.
- Composed: pappydapimp69__seven/E10, pappydapimp69__mirage/E19
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__believable-hallucination-renders-the-players-learned-prior.py
- Prediction: prior-shaped phantom believed at least 10x a random one at q = 0.8; belief tracks q; at q
  = 0.1 the advantage drops below 6x; with a weak tell a prior-shaped phantom stays at 0.6 or more.
- Observed: RESULT: PASS 4/4; believed junction/open q0.8: 0.800/0.020; q0.5: 0.500/0.020; q0.1:
  0.100/0.020; weak tell 0.667
- Scenarios: 1) strong regularity q 0.8; 2) q 0.5; 3) built to BREAK the claim: no regularity, q 0.1;
  4) a weak visual tell.
- Link: session; brain train loop on hallucination as an art style (loop 3); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E60 · compatible · sandboxes/2026-10-12__inner-voices-cannot-be-spread-so-binaural-budget-shrinks.py · observed RESULT: FAIL 3/4; 4-voice landing by inner share 1.000/0.504/0.288/0.216; budget 5/5/2/2. Missed: the all-outside budget is 5, not E55's 4. · session; brain train focused loops on hallucination phenomenology (loop 3); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E65 · compatible · sandboxes/2026-10-12__sound-first-voices-collapse-on-phone-speakers.py · observed RESULT: PASS 3/3; budgets all-outer/34%-inner headphones 5/4; stereo speakers 2/3; phone speaker 2/2 · session; brain train focused loops after the owner's sound-first decision (loop 4); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Audited: 2026-10-12 · modeled · Read the entry and its stored sandbox. The answer is built in: with no visual tell, belief() returns its input, so 'believed 0.800 vs 0.020 (x40)' is q/0.02, the author's two constants, and 'x5 at q 0.1' is 0.1/0.02. The quantity is also mislabelled: q is the rate at which a REAL pylon stands at a junction, not P(real | a pylon is seen there), which needs the phantom rate too (q/(q+h)); with phantoms placed at every junction the posterior is well below q. Only the weak-tell row (0.667) is a computation, and it is Bayes' odds rule. The design idea (teach a pattern, break it there) is plausible but untested against any player. Powers, Mathys and Corlett 2017 is cited correctly (visual checkerboard paired with an at-threshold tone; tones reported that were never played); the 2018 Corlett and Powers commentary could not be located to confirm. · session; review of seven hallucination lessons (E46, E55-E62); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E70 · compatible · no sandbox · session; correction after the 2026-10-12 review of seven hallucination lessons; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E75 · incompatible · sandboxes/2026-10-12__one-to-one-refresh-lets-conditioned-phantoms-die.py · observed RESULT: PASS 3/3; E63 constants 1:1 late 0/15 (V* 0.588), 2:1 10/10; 1:1 sustains in 4/9 cells; 2:1 in 9/9 · session; brain train round 2 on seven hallucination lessons (E63-E66); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E87 · incompatible · sandboxes/2026-10-12__conditioned-phantoms-persist-but-reach-a-minority.py · observed RESULT: PASS 4/4; symmetric RW stops after 3/2/1; persistence needs r>=12; fitted all-phantom 12/12; population share max 0.290 · session; brain train follow-up on E78/E79 (missing human data); session_01KGZvxv8BDgpDMRFTYMfJoJ

## E54 — seven first person input paths tested
- Date: 2026-10-11
- Project: Pappydapimp69/Seven
- Tags: [gamedev][camera][testing][input]
- What: Closes the gaps seven/E53 named in seven/E52: mouse look, gamepad sticks, and
  followers trailing behind a walking lead are now driven by tests/view.mjs in Chromium
  at device scales 1, 1.25 and 2.
- Why built: E53 corrected E52 to keyboard-only evidence. Admitting a gap is half a
  fix; the input path behind the original PC drift (mouse under display scaling) was
  exactly the one left untested.
- Design: Mouse: fake a locked pointer and dispatch a mousemove whose movementX is 240
  device pixels divided by devicePixelRatio (what one physical sweep produces), then W.
  Pad: stub navigator.getGamepads with the left stick up at heading 0.9 rad, then the
  right stick. Trailing: hold W and steer up the bending trail 14 cells with everyone
  following, then require every follower within 4 cells AND seen in one turn round.
- Got right: One physical sweep turned 44.00 degrees at all three scales; W then
  followed the new heading within 1 degree. The pad stick walked 0.00 degrees off the
  view and the right stick turned. After the walk all five followers were 1.1-3.1 cells
  away and all five came into view.
- Where/why it failed: The first trailing test passed with followers broken: a lead
  walking straight north hit a trail bend after 4.2 cells, so companions left behind
  were still close and visible. Visibility alone does not test following.
- Fix: Steer the walk along the trail and assert distance walked (at least 8) plus
  follower distance (at most 4) as well as visibility.
- Why this fix: The negative controls now bite: dropping the DPR scale on movementX read
  44.00 / 35.20 / 22.00 degrees across scales; disabling following left companions
  11.8-15.5 cells back and only three of five in view.
- Rule of thumb: A "can I see them" test only tests following if the lead actually got
  far away; assert distance covered and follower distance, and make the walk follow the
  real route, or the scene stays small enough to pass with following switched off.
- Provenance (verified/assumed): Verified first-hand in headless Chromium, each guard
  negative-controlled with the numbers above; synthetic pointer-lock and gamepad events
  stand in for real hardware.
- Composed: seven/E52, seven/E53, mirage/E10, mirage/E6
- Link: Seven tests/view.mjs, session 2026-10-11; session_01XbmpbLd4QyYTiQBBzo2Hdw

## E53 — correction seven e52 evidence scope
- Date: 2026-10-11
- Project: Pappydapimp69/Seven
- Tags: [gamedev][camera][testing]
- What: Correction to seven/E52 (first person restored as a grid raycaster). E52 as
  promoted claims "0.00° drift at 4 headings × 3 device scales", composes mirage/E6
  and calls the visibility sweep a guard. Its evidence is narrower than that.
- Why built: The author overstated E52 and only caught it after promotion. A lesson
  that claims coverage it lacks is worse than a missing lesson: the next reader stops
  testing mouse look because Brain says drift is solved.
- Design: Re-read tests/view.mjs against each claim in E52. The drift test drives the
  keyboard only (KeyW, KeyD, ArrowRight). The 360 degree sweep places companions by
  hand around a still lead. Nothing exercises pointer-lock mouse look, a real gamepad,
  or followers walking behind a moving lead.
- Got right: Keyboard heading drift is verified at 0.00 degrees across four headings
  and device scales 1, 1.25 and 2, and negative-controlled (a 0.3 rad offset read 17.19
  degrees). The hand-placed sweep is negative-controlled (hiding one companion failed).
- Where/why it failed: E52 generalised keyboard results to all input, and cited
  mirage/E6 (followers trailing out of frame while walking) though the sweep never
  recreates that situation. The old PC drift was reported with mouse and zoom, the
  exact path left untested.
- Fix: Read E52 as covering keyboard input and a static sweep only. Treat mouse-look
  drift (movementX times devicePixelRatio under display scaling), gamepad drift, and
  trailing followers as untested until a test drives them.
- Why this fix: Narrowing the claim keeps the verified part usable and leaves the
  untested input paths visible as open work instead of silently closed.
- Rule of thumb: When filing a lesson, list each claim beside the exact input the test
  drove; a drift test that only presses keys says nothing about the mouse, and a
  hand-placed scene says nothing about a formation that forms itself.
- Provenance (verified/assumed): Verified first-hand by re-reading tests/view.mjs and
  the E52 text; the narrowing is a statement of what was tested, not a new measurement.
- Composed: seven/E52
- Link: Seven session 2026-10-11, after seven-1.6.0; session_01XbmpbLd4QyYTiQBBzo2Hdw
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E54 · compatible · no sandbox · Seven tests/view.mjs, session 2026-10-11; session_01XbmpbLd4QyYTiQBBzo2Hdw

## E52 — first person is load bearing
- Date: 2026-10-11
- Project: Pappydapimp69/Seven
- Tags: [gamedev][camera][gamedesign]
- What: A remake swapped a buggy 3D first-person view for a top-down 2D view to kill
  movement and camera bugs, and in doing so removed "out of sight", which is the
  mechanic fakes hide in. Restored first person as a grid raycaster on the same 2D
  canvas, keeping the new sim untouched.
- Why built: The owner asked what happened to first person. The design said the
  player is a member of the team with no overview; a live top-down view is a second
  honest instrument that shows everyone around you at once.
- Design: Raycaster over the existing walkability grid (forest cells are walls,
  everything else billboards, per-pixel light). Fixed horizontal FOV, canvas backing
  CSS times devicePixelRatio, mouse movementX scaled by DPR, and the stick turned into
  a world vector from yaw before the sim tick, so the sim never knew the view changed.
- Got right: The old drift was unit errors around the camera, not first person: with
  the stick-to-world conversion in one function, W walked within 0.00 degrees of the
  view at four headings and device scales 1, 1.25 and 2; a 360 degree turn saw all
  five companions.
- Where/why it failed: Choosing the view to dodge bugs treated perspective as
  presentation. It was a design mechanic: the phantom, lit-looking dead pylons and the
  unnoticed replacement all depend on what the player cannot currently see.
- Fix: Put the perspective back, cheaply: a raycaster on the grid the sim already had,
  plus browser guards for drift (heading x device scale), turning without moving, and
  a 360 degree visibility sweep, each negative-controlled (0.3 rad offset gave 17.19
  degrees; hiding one companion failed the sweep).
- Why this fix: A grid raycaster needs no WebGL, no camera rig and no zoom, so the
  classes of unit error that caused the drift have nowhere to live, and the sim and
  its tests stayed unchanged.
- Rule of thumb: Before changing a game's perspective to fix camera bugs, ask what
  the perspective hides; if a mechanic depends on things being out of sight, keep the
  perspective and fix the units, with a drift test across headings and device scales.
- Provenance (verified/assumed): Verified first-hand by tests/view.mjs in Chromium at
  three device scales, each guard negative-controlled; that players feel the restored
  out-of-sight is a playtest question, not tested here.
- Composed: mirage/E10, mirage/E6
- Link: Seven commit for seven-1.6.0, session 2026-10-11; session_01XbmpbLd4QyYTiQBBzo2Hdw
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E53 · compatible · no sandbox · Seven session 2026-10-11, after seven-1.6.0; session_01XbmpbLd4QyYTiQBBzo2Hdw
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E54 · compatible · no sandbox · Seven tests/view.mjs, session 2026-10-11; session_01XbmpbLd4QyYTiQBBzo2Hdw

## E51 — abandonment felt dismantle call
- Date: 2026-10-11
- Project: Pappydapimp69/Seven
- Tags: [gamedesign][abandonment][missing]
- What: Making abandonment-by-walking-forward FELT with no prompt. Compared, at the
  moment the lead takes camp down, what the player can know: the dawn call alone, a
  call as camp comes down (real whenever the move would abandon someone, false at
  0.3 otherwise), and that camp-down call heard from the SAME bearing as the dawn call.
- Why built: Open red tension (spatial rescue window: how is abandonment a felt choice
  with no prompt?). The remake (seven-1.0.0) abandons silently on a camp move; the
  dawn call was the only cue and nobody had measured whether it is enough.
- Design: Exact enumeration, no RNG. Three states at the move: missing in this area
  (behind, abandoned by the move), missing in the next area (ahead, safe), nobody.
  Dawn call uses the game's numbers (fades 0.15 a night, floor 0.5, false 0.3, eight
  bearings). Metrics: informed = P(cue | behind), posterior = P(behind | cue).
- Got right: Bearing agreement is what carries it. A real voice holds its bearing
  across dawn and camp-down; two false calls agree one time in eight. Posterior
  0.930 / 0.971 / 0.915 across three priors, false alarm about 0.015, and never 1.0,
  so it is evidence, not an announcement. Informed 0.775 (needs the dawn call too).
- Where/why it failed: Prediction (posterior about 0.8 for a camp-down call alone)
  was wrong: alone it reached only 0.455 at prior 0.2 and 0.690 at 0.4, because a
  0.3 false rate swamps a rare event. The dawn call alone is weaker still (0.29-0.55)
  and cannot tell behind from ahead, since both call at the same rate.
- Fix: Fire a call when camp comes down while someone is in this area's window, from
  their bearing; fire false camp-down calls at the dawn false rate from a random
  bearing. The felt signal is the camp-down voice matching this morning's bearing.
- Why this fix: It lands at the decision moment, on a reversible step (camp can go
  straight back up), and keeps the posterior below 1.0. A camp-down call that only
  fires when real (false rate 0) reaches posterior 1.000, which is a prompt in
  disguise; one that fires every time (false rate 1) carries nothing on its own.
- Rule of thumb: To make an unprompted irreversible choice felt, put a cue at the
  reversible step just before it, and make the cue's strength come from AGREEMENT with
  an earlier cue (same bearing), not from the cue firing; a lone cue with honest false
  alarms stays weak, and one with no false alarms becomes an announcement.
- Provenance (verified/assumed): Verified first-hand by the sandbox below (exact
  enumeration, five scenarios). Player perception of the cue is a separate question
  that a playtest would answer; the numbers here are the information available.
- Composed: seven/E25, seven/E30, seven/E34
- Sandbox: sandboxes/2026-10-11__abandonment-felt-dismantle-call.py
- Prediction: A camp-down call alone (false rate 0.3) would give posterior about 0.8
  and informed 1.0; dawn-only about 0.5.
- Observed: RESULT: PASS camp-down call on the dawn bearing: posterior 0.9-0.995,
  informed 0.775, in 3/3; alone it is weak (0.46-0.69); fk=0 announces; fk=1 alone
  says nothing. Numbers: C 0.930/0.971/0.915, false alarm 0.0146-0.0179; B 0.455/0.690.
- Scenarios: 1) prior 0.2, ahead 0.15; 2) prior 0.4, ahead 0.15; 3) prior 0.2,
  ahead 0.30; 4) BREAK false rate 0 (announces, posterior 1.0); 5) BREAK false rate 1
  (camp-down call alone carries nothing).
- Link: seven-1.0.0 session 2026-10-11, commit 4ecc609; session_01XbmpbLd4QyYTiQBBzo2Hdw

## E50 — search effort spreads by water filling not all on the likeliest spot
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [search-theory][gamedesign][rescue][missing][probability]
- What: Splitting a fixed night of search hours for a missing member across directions, using
  Koopman's detection law (an area searched with effort e detects a present target with probability
  1 - exp(-w e)), compared with concentrating on the likeliest sector and with seven E31's fixed
  4-sector block.
- Why built: SEARCH-THEORY had one kernel (seven E47: how a failed search updates the map). The other
  half of the theory, how to spend effort in the first place, was missing, and SEVEN's E31 tuning
  assumed a fixed block of sectors regardless of hours or noise.
- Design: Exact computation on a 24-sector ring, prior from the call bearing with noise 0.6, 1.5 or 3.25
  sectors, 1, 4 or 8 hours in quarter-hour units, detection rate 1.2 per hour. Optimal = greedy
  quarter-hour allocation by largest marginal gain. Measured find chance and how many sectors the
  optimal plan uses.
- Got right: The greedy optimum is never beaten, the area it searches grows with the hours (3, 5, 7
  sectors at noise 1.5), and with a very sharp prior and one hour concentrating is optimal (0.416 both),
  so the rule reduces to common sense exactly where common sense is right.
- Where/why it failed: Concentrating everything is badly wrong once there is time to spare: at noise
  1.5 with 8 hours it finds 0.261 against 0.782 optimal. A fixed 4-sector block is close at moderate
  noise (0.722 vs 0.782) but falls behind as the bearing gets noisier (0.416 vs 0.557 at noise 3.25,
  where the optimum spreads over 11 sectors), so E31's block search under-searches the deep woods.
- Fix: Let the searched area grow with both the hours spent and the call's noise (water-filling), rather
  than a fixed block; for a player-facing version, offer search width as the choice and let hours
  deepen it.
- Why this fix: It is the optimal allocation of a real planning field, it adds no hidden dice, and it
  gives the depth difficulty a second, readable lever (how wide you must search) on top of the noise.
- Rule of thumb: Spread a missing member's search hours by water-filling: the searched area should grow
  with the hours and the call's noise (3 to 11 sectors here); all hours on the likeliest spot found
  0.261 against 0.782, and a fixed 4-sector block lost 0.141 at high noise.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 4/4
  predictions held; numbers above copied from the run). The exponential detection law is the
  standard search-theory model; the detection rate 1.2 per hour is my choice.
- Composed: ideas:SEARCH-THEORY/bayesian-search/a-failed-search-lowers-a-cell-by-1-minus-POD-it-does-not-clear-it, pappydapimp69__seven/E31, pappydapimp69__seven/E47
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__search-effort-spreads-by-water-filling-not-all-on-the-likeliest-spot.py
- Prediction: optimal never beaten; more hours spread over more sectors at noise 1.5; concentrating
  loses at least 0.15 with 8 hours at noise 1.5; with a sharp prior and 1 hour concentrating is within
  0.01 of optimal.
- Observed: RESULT: PASS 4/4; s0.6/h1.0: c 0.416 o 0.416 n1; s1.5/h8.0: c 0.261 u 0.722 o 0.782 n7;
  s3.25/h8.0: c 0.122 u 0.416 o 0.557 n11
- Scenarios: 1) noise 0.6, 1.5, 3.25; 2) 1, 4, 8 hours; 3) built to BREAK the claim: a sharp prior with
  one hour, where concentrating should be optimal.
- Link: session; brain train auto run 2 pass 5 (gap, SEARCH-THEORY); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__brain.md#E135 · compatible · sandboxes/2026-10-11__water-filling-test-time-across-suspect-modules.py · observed RESULT: PASS searched modules grow 2->8->12 (r=.8); greedy >= others in 7/7; levelled; sharp prior tiny budget concentrate 0.181 vs greedy 0.181 · brain train auto loop 1 pass 5 (gap, kernel); session_01ScEdAr4bK7Pp21fx27MXao
- Reverified: 2026-10-12 · pass · sandboxes/2026-10-12__rebuild-seven-e50-water-filling-search-effort.py · observed RESULT: PASS never beaten; sectors 1->7 with hours; concentrate loses 0.245 at H8 noise3; sharp prior gap 0.0000; bimodal split both peaks · Own fixture: 20 sectors on a line, Laplace prior plus 5% uniform, w = 0.7/h, closed-form water filling by bisection on lambda (original: greedy 0.25 h units on a 24-ring with Gaussian prior). Water filling was never beaten by 150 random allocations per cell nor by the alternatives; sectors searched grew with hours (1 to 7 at noise 1) and with noise (3 to 11 at noise 3); concentrating lost 0.245 at H=8, noise 3; with a sharp prior and 1 h concentrating tied optimal. Break case: bimodal prior - water filling split effort across both peaks and beat the 4-block. Koopman's exponential detection law and the threshold allocation re-checked against search-theory summaries (Koopman's problem; de Guenin 1961). · session_01P1LRA5HjMLEFnWXayE2EHx; blind review pass of SEVEN targets, 2026-10-12

## E49 — time remap insert keeps cues in sync except spanning clips
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [film][animation][audio][tooling]
- What: film E7's insert-a-beat technique (remap time at the dispatcher instead of editing hard-coded
  cue times) combined with collective-reference E1 (two things that must agree should be derived
  from one source, not hand-synced), measured on a film whose visual and audio cue lists must agree.
- Why built: The remap is collective-reference E1's rule applied to time: one mapping instead of two
  hand-edited lists. What neither lesson says is what the remap does NOT cover, so the boundary was
  tested on purpose.
- Design: Exact model: 40 visual and 40 audio cues every 1.5 s, a 3 s beat inserted at 30 s. Hand edit
  shifts every later cue in both lists but misses every 7th audio cue. The dispatcher remap leaves both
  lists untouched and plays story time t at t, or t + 3 from 30 s on. Then three continuous audio clips:
  two that start before 30 s and run past it, one that ends before it.
- Got right: The dispatcher remap leaves 0 of 40 cue pairs out of sync where the hand edit left 3, and a
  cue exactly at the insert point is placed once, after the insert (a half-open boundary), so discrete
  cues are fully covered by deriving both from one mapping.
- Where/why it failed: Continuous clips that span the insert point are not covered: both spanning clips
  end exactly 3.0 s early (the inserted length), because the audio engine keeps playing in wall time
  while the story clock is held; a clip that ends before the insert is unaffected. The one-source
  rule only holds for the things that read the remapped clock.
- Fix: When inserting a beat by time remap, list every continuous media item that spans the insert
  point and pause it (or split it at the insert) through the same dispatcher, so it also reads the
  remapped clock; everything else needs no change.
- Why this fix: It extends the single source of truth to the only items that were still on a second
  clock, rather than hand-editing them and recreating the sync bug the remap removed.
- Rule of thumb: Inserting a film beat by remapping time at the dispatcher keeps discrete cues in sync
  (0 of 40 off, against 3 of 40 for hand edits), but continuous clips spanning the insert end exactly
  the insert length early; pause or split spanning clips through the same remap.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 5/5
  predictions held; numbers above copied from the run). The missed-edit pattern is a stand-in for
  human error, not a measured rate.
- Composed: local__film/E7, local__collective-reference/E1
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__time-remap-insert-keeps-cues-in-sync-except-spanning-clips.py
- Prediction: hand edits leave some cues out of sync; the remap leaves 0; a cue at the insert point is
  placed once after it; spanning clips end exactly 3 s early; a clip ending before the insert is
  unaffected.
- Observed: RESULT: PASS 5/5; hand desync 3/40; remap 0/40; spanning clips early by 3.0s and 3.0s;
  pre-T clip 0
- Scenarios: 1) hand-edited lists; 2) dispatcher remap; 3) the cue exactly at the insert point; 4)
  built to BREAK the claim: continuous clips spanning the insert; 5) a clip ending before it.
- Link: session; brain train auto run 2 pass 2 (edge); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-12 · pass · sandboxes/2026-10-12__rebuild-seven-e49-time-remap-beat-insert.py · observed RESULT: PASS hand off 6/25, remap 0; spanning clip ends 2.5 s early; end-remapped clip stretched 2.5 s instead · Own fixture: 25 seeded cue pairs over 0-120 s with one exactly at T, insert L=2.5 s at T=47 (original 40 pairs, L=3 at T=30); hand-edit failure modelled as a '>' vs '>=' boundary slip plus a missed page of audio cues (original: every 7th cue). Hand edits left 6/25 out of sync, remap 0, the cue at T fired once at T+L, the duration-scheduled spanning clip ended exactly L early, clips before/at/after T unaffected. Break case: if clips store an END time and the dispatcher remaps both ends, the spanning clip instead plays L LONGER than authored - so 'ends early' is specific to duration-scheduled clips; either way a spanning clip must be split or paused explicitly, as the rule says. · session_01P1LRA5HjMLEFnWXayE2EHx; blind review pass of SEVEN targets, 2026-10-12
- Cited-by: 2026-10-17 · projects/pappydapimp69__zanegpt.md#E31 · compatible · no sandbox · https://claude.ai/code/session_01WkbM7ZHHguQoKwyDFf4vYn · https://claude.ai/artifact/1kFmKx74PL3QTXsPNWCAQc

## E48 — save rng state words survives a miscounted draw
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [determinism][rng][save][testing]
- What: The seeded-rng kernel (save the generator's full state words rather than a seed-and-count
  pair) re-verified and declared, by running it against seven E1's hidden callback draws and the
  golden-hash rule of the-game-prologue E1, which quoted the kernel in prose only.
- Why built: The kernel was only quoted, never built against, and sandbox-edges E20 had already shown
  that a seed-and-count save breaks under hidden draws. What was untested was whether the kernel's own
  remedy is immune to that break, and what each save form costs to restore.
- Design: sfc32 implemented in the sandbox. 3000 turns, each with one counted roll and a crit callback
  that draws 0 to 2 extra times without counting them (seven E1's shape), for 6000 true draws. Restored
  three ways: the four state words; the seed plus the counted total; the seed plus the true total.
  Restore cost counted in generator steps. Then two equal game states built in different key order
  were hashed with plain JSON and with sorted keys.
- Got right: State words restore the exact next roll at a cost of 0 replay steps, regardless of how
  many draws went uncounted. A seed-and-count save is only correct with the TRUE total (6000) and then
  pays every draw again to restore; with the counted total (3000) it silently diverges.
- Where/why it failed: Nothing in the run refuted the predictions. The trap this guards against is
  real: a counted total that misses callback draws is wrong by half here, with every return value
  correct until the save is loaded. Plain JSON also gave two equal states different golden hashes.
- Fix: Save the generator's state words (and treat them as save state, per SEVEN's invariants), never
  a seed-and-count pair; hash golden states with sorted keys so key order cannot split equal states.
- Why this fix: State words remove the need to count draws at all, which is the quantity callbacks make
  impossible to count, and turn restore from O(draws) into O(1); sorted keys make the hash a function
  of the state, not of how it was built.
- Rule of thumb: Save the RNG's full state words, never a seed and a roll count: with hidden callback
  draws the counted total was 3000 of 6000 and the restore silently diverged, while state words
  restored exactly at zero replay cost; hash saved state with sorted keys.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 4/4
  predictions held; numbers above copied from the run). The sfc32 step follows the published algorithm
  as I wrote it from memory; the comparison holds for any generator with a fixed state.
- Composed: ideas:SYSTEM/determinism/seeded-rng, pappydapimp69__seven/E1, pappydapimp69__the-game-prologue/E1, local__sandbox-edges/E20
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__save-rng-state-words-survives-a-miscounted-draw.py
- Prediction: state words match with 0 replay steps; seed plus counted total diverges; seed plus true
  total matches but costs every draw; plain JSON splits equal states while sorted keys do not.
- Observed: RESULT: PASS 4/4; true 6000 counted 3000; words cost 0 match; counted diverges; true-count
  cost 6000; sorted hash stable
- Scenarios: 1) state-word restore; 2) seed plus counted total; 3) built to BREAK the claim: seed plus
  the true total, which should also be correct; 4) golden hash of two equal states.
- Link: session; brain train auto run 2 pass 1 (kernel, declare); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E89 · incompatible · sandboxes/2026-10-12__rebuilt-witness-list-forks-a-fakes-lie-across-reload.py · observed RESULT: FAIL 8/10; changed verbatim 0.000 reorder 0.797 drop 0.395; minhash reorder 0.000 drop 0.208; sorted reorder 0.000 drop 0.395; resume+draws constant True · session; brain train loop round 3; session_01QGT1LfmPHPG99JEGaPhBwB
- Reverified: 2026-10-12 · pass · sandboxes/2026-10-12__rebuild-seven-e48-save-rng-state-words.py · observed RESULT: PASS words exact 0 replay; seed+counted (250 of 632) diverged; seed+true replays 632; no-hidden seed+count exact · Own generator xoshiro128** (original sfc32), 500 turns, a hidden callback drawing 0-3 extra times keyed on the last value, save at turn 250. State words through JSON restored exactly with 0 replay; seed + counted total (250 of a true 632) diverged; seed + true total matched but replayed 632 draws; plain json.dumps split two equal dicts built in different key order, sort_keys gave one hash. Break case: with no hidden draws seed+count restores exactly - the defect needs an uncounted draw, which is the rule's stated condition. · session_01P1LRA5HjMLEFnWXayE2EHx; blind review pass of SEVEN targets, 2026-10-12
- Cited-by: 2026-10-15 · projects/local__transcendental-drift-forks-only-when-it-feeds-state.md#E1 · compatible · sandboxes/2026-10-15__transcendental-drift-forks-a-run-only-when-it-feeds-state.py · observed RESULT: PASS 8/8; plain json splits equal states, canonical one hash; NaN never equals itself; sin impls differ on 100.0% of args, branch-only sim traces agree, feedback sim differs at step 1 and is > 0.1 apart by step 75; grep guard catch… · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto loop 3 pass 1 (kernel declare SYSTEM/seeded-rng), 2026-10-15

## E47 — search theory failed search moves probability not removes it
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [search-theory][gamedesign][rescue][missing][probability]
- What: Seed lesson for a new SEARCH-THEORY domain: Bayesian search planning (a failed search lowers an
  area's probability by a factor of 1 - POD rather than clearing it) applied to SEVEN's night rescue
  search for a missing member, comparing repeating the same block, the Bayesian update, and planning
  as if every searched sector were cleared.
- Why built: SEVEN's search is multi-night and in the dark, so detection is imperfect. Without a rule
  for what a failed night means, the game (or a player-facing hint, or a bot) either repeats the same
  spot forever or treats a searched spot as cleared; search theory says which is worse.
- Design: Exact computation on a 24-sector ring, prior from the call bearing (noise 1.5 or 3.25 sectors,
  as in seven E31), 4 sectors searched per night, 3 nights, true POD 0.5, 0.8 or 0.98. Policies: repeat
  the nearest block; Bayesian update with the true POD then top-4 by p x POD; plan as if POD = 1.
- Got right: The Bayesian plan never does worse than repeating (for example 0.929 vs 0.787 at noise 1.5,
  POD 0.8), and planning as if POD = 1 loses to it at POD 0.5 under both noise levels (0.500 vs 0.737;
  0.466 vs 0.506). With a tight prior it even loses to blind repetition (0.500 vs 0.694), the shape of
  the AF447 search's early misses.
- Where/why it failed: Two predictions were refuted. Repeating the block is not near-optimal at low
  noise and POD 0.5 (0.694 vs 0.737, a 0.043 gap, not under 0.02), and overconfidence is not free even
  at POD 0.98 with a tight prior (0.980 vs 0.991). Repetition also falls badly behind once detection is
  good (0.457 vs 0.914 at noise 3.25, POD 0.98), because it never moves.
- Fix: For SEVEN's multi-night search (and any helper that suggests where to look), carry each sector's
  probability forward with the p(1 - POD) update and pick by p x POD; make night-time POD an explicit,
  modest number rather than treating a searched sector as cleared.
- Why this fix: It is the standard planning rule of a real field, it beats both naive policies in every
  cell measured, and it gives the darkness a mechanical meaning: a dark search is evidence, but weak
  evidence.
- Rule of thumb: After a failed search, lower each searched area's probability by a factor of 1 - POD
  and search next where probability times detection is highest; never treat a searched area as cleared
  when detection is poor (POD 0.5: cleared-planning found 0.500 against 0.737 Bayesian).
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 2/4
  predictions held; numbers above copied from the run). The search rule is from Bayesian search theory;
  the AF447 outcome (posterior map, wreck found within a week in 2011) was checked against the paper's
  published abstract (Stone et al., Statistical Science 29(1), 2014). The POD values are my choices.
- Composed: ideas:SEARCH-THEORY/bayesian-search/a-failed-search-lowers-a-cell-by-1-minus-POD-it-does-not-clear-it, pappydapimp69__seven/E22, pappydapimp69__seven/E31
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__search-theory-failed-search-moves-probability-not-removes-it.py
- Prediction: Bayes never worse than repeating; cleared-planning loses to Bayes at POD 0.5 at both noise
  levels; repeating within 0.02 of Bayes at noise 1.5, POD 0.5; at POD 0.98 overconfidence within 0.01.
- Observed: RESULT: FAIL 2/4; s1.5/pod0.5: rep 0.694 bay 0.737 over 0.500; s1.5/pod0.98: rep 0.794 bay
  0.991 over 0.980; s3.25/pod0.5: rep 0.400 bay 0.506 over 0.466; s3.25/pod0.98: rep 0.457 bay 0.914
  over 0.914
- Scenarios: 1) tight prior, POD 0.5/0.8/0.98; 2) wide prior, POD 0.5/0.8/0.98; 3) built to BREAK the
  claim: near-perfect detection, where overconfidence should cost nothing (it cost 0.011 with a tight
  prior).
- Link: session; brain train newdomain (SEARCH-THEORY seed); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E50 · compatible · sandboxes/2026-10-11__search-effort-spreads-by-water-filling-not-all-on-the-likeliest-spot.py · observed RESULT: PASS 4/4; s0.6/h1.0: c 0.416 o 0.416 n1; s1.5/h8.0: c 0.261 u 0.722 o 0.782 n7; s3.25/h8.0: c 0.122 u 0.416 o 0.557 n11 · session; brain train auto run 2 pass 5 (gap, SEARCH-THEORY); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__brain.md#E135 · compatible · sandboxes/2026-10-11__water-filling-test-time-across-suspect-modules.py · observed RESULT: PASS searched modules grow 2->8->12 (r=.8); greedy >= others in 7/7; levelled; sharp prior tiny budget concentrate 0.181 vs greedy 0.181 · brain train auto loop 1 pass 5 (gap, kernel); session_01ScEdAr4bK7Pp21fx27MXao
- Reverified: 2026-10-12 · pass · sandboxes/2026-10-12__rebuild-seven-e47-bayesian-search-failed-search.py · observed RESULT: PASS POD0.5 noise1.5 bayes 0.798 cleared 0.611 repeat 0.631; unequal POD p*POD 0.777 vs p-only 0.734 · Own fixture: 16-sector ring, prior = Gaussian around the bearing plus 10% uniform (call may be wrong), 3 sectors a night for 6 nights (original: 24 sectors, 3 nights), exact expectation. Bayes >= repeat and >= cleared-planning in all 9 noise x POD cells; at POD 0.5 cleared lost 0.079-0.217; at POD 0.98 cleared tied Bayes. Break case: unequal POD (thick brush near the call, 0.3) - ranking on p x POD beat ranking on p alone (0.777 vs 0.734). One author prediction did not carry over: repeating was NOT within 0.02 of Bayes at noise 1.5 POD 0.5 here (0.631 vs 0.798); the rule does not depend on it. Sources re-checked: Stone, Keller, Kratzke & Strumpfer 2014, Statistical Science 29(1):69-80 (AF447 found after one week of Bayesian-planned search) is correct. · session_01P1LRA5HjMLEFnWXayE2EHx; blind review pass of SEVEN targets, 2026-10-12

## E46 — on screen recede cannot be both invisible and unbeatable
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][hallucination][perception][deception]
- What: Tension T1's two poles for a receding phantom relief (a pylon that backs away from a far-gone
  player): move it only while the player looks away, or let it creep away on screen at a fraction of
  the player's closing speed, which T1 says cannot be beaten by discipline.
- Why built: T1 says only a human at a screen can settle it, but one half is arithmetic: whether an
  on-screen recede can be both too slow to see and strong enough to stop a disciplined player.
- Design: Exact arithmetic. Start gap 100, player speed 1. On-screen recede at fraction f closes the
  gap at 1 - f, and is noticeable when f exceeds a speed-discrimination threshold j (assumed 0.10, swept
  0.05 to 0.20). Off-screen only: the relief backs away at 1.5 while unwatched, for players who look
  away 0 to 50 percent of the time.
- Got right: Off-screen only behaves as T1 describes: a player who never looks away arrives in the base
  time, and one who looks away 40 percent of the time or more never arrives, so the effect lands on
  exactly the players who are not watching, without anything moving under the eye.
- Where/why it failed: The on-screen pole's selling point does not survive: the strongest recede below
  the threshold only delays a disciplined player by x1.053, x1.111 or x1.250 (j = 0.05, 0.10, 0.20), and
  tripling the walk needs f = 0.667, 6.7 times the 0.10 threshold. An on-screen recede can be invisible
  or unbeatable, never both; any version that stops a disciplined player is plainly visible motion.
- Fix: Keep off-screen only as the default. If an on-screen version is ever wanted, choose it as VISIBLE
  dread (the classic receding door, shown on purpose) and judge it on whether it reads as dread or as a
  bug, rather than presenting it as an imperceptible version of the same effect.
- Why this fix: It removes the false middle option from T1, so the human playtest only has to judge the
  one real question left: whether a visibly receding relief reads as dread or as a glitch.
- Rule of thumb: A phantom target that backs away on screen cannot be both unnoticeable and unbeatable:
  below a 0.10 speed-discrimination threshold it delays a disciplined player only x1.111, and tripling
  the walk needs 6.7x that threshold; make it off-screen only, or visibly recede on purpose.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 4/4
  predictions held; numbers above copied from the run). The 0.10 threshold is a stand-in for a
  speed-discrimination limit that I did not measure; the sweep from 0.05 to 0.20 shows the conclusion
  holds across that range.
- Composed: pappydapimp69__mirage/E19
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__on-screen-recede-cannot-be-both-invisible-and-unbeatable.py
- Prediction: an invisible recede adds at most 25 percent at every threshold; tripling needs at least 5x
  the 0.10 threshold; off-screen only lets a disciplined player arrive in the base time; off-screen only
  stops a player who looks away 40 percent or more.
- Observed: RESULT: PASS 4/4; invisible recede delay x1.053/x1.111/x1.250; tripling needs f=0.667;
  off-screen stops at look-away >= 0.4
- Scenarios: 1) thresholds 0.05, 0.10, 0.20; 2) the f needed to triple the walk; 3) off-screen only at
  0 to 50 percent look-away; 4) built to BREAK the claim: whether off-screen only ever stops anyone.
- Link: session; brain train auto pass 5 (gap), tension T1; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-12 · fail · sandboxes/2026-10-12__rebuild-seven-e46-recede-deadline.py · observed RESULT: FAIL 1/3; delay x1.031/x1.087/x1.176; stop share walk 0.667 freeze 0.400; invisible f=0.08 blocks slack <= 0.08 · Rebuilt from the claim only with a different fixture: gap 60 m, walk 1.4 m/s, thresholds j 0.03/0.08/0.15, an off-screen model where the player KEEPS WALKING while looking away, and a night deadline with slack s. The arithmetic of the rule holds: an invisible recede delays exactly 1/(1-j) (x1.031/x1.087/x1.176). Two parts do not survive. The 'look away 40 percent or more never arrives' figure is set by E46's own assumption that the player stops walking while looking away; if they keep walking the stop point is 0.667. And 'cannot be unbeatable' only holds with no deadline: SEVEN has a clock, and an invisible f = 0.08 recede stopped a perfectly disciplined player whenever slack was 8 percent or less, so near a deadline the sub-threshold recede is decisive and invisible at once. Fail on scope, not on arithmetic. · session; review of seven hallucination lessons (E46, E55-E62); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E68 · incompatible · sandboxes/2026-10-12__sub-threshold-recede-is-decisive-near-a-deadline.py · observed RESULT: FAIL 1/3; delay x1.031/x1.087/x1.176; stop share walk 0.667 freeze 0.400; invisible f=0.08 blocks slack <= 0.08 · session; review of seven hallucination lessons (E46, E55-E62); session_01KGZvxv8BDgpDMRFTYMfJoJ

## E45 — render pass snapshot of animated page needs frozen clock
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [browser][testing][tooling][animation]
- What: codex-visual-snapshots E1's rule (update visual snapshots only after a browser render pass)
  combined with sandbox-edges E29 (a harness that snapshots a continuously moving system must capture
  at a fixed event time), for generated pages that animate, such as Brain's own film view.
- Why built: A render pass guarantees the page has drawn, not WHEN in its animation it was captured.
  If baselines and checks are taken at different moments, the snapshot test can flake on an
  unchanged page, which E1 alone does not warn about.
- Design: Exact model, no randomness: one element moving at 30 to 240 px/s on a 600 px loop. The
  baseline and the check are each captured after a 120 ms render plus 0 to 4 frames of jitter (all 25
  pairs enumerated). The diff is the element's displacement between the two captures. Compared a live
  clock with a clock pinned to t = 0 for capture, and a static page as a control.
- Got right: A frozen clock gives zero differing pairs at every speed, and a static page needs no
  freezing (0 differing pairs), so the rule only bites where the page actually animates.
- Where/why it failed: With a live clock, 0.80 of capture pairs differ by at least 1 px at 120 px/s, and
  the worst diff grows with speed (1.92, 3.84, 7.68, 15.36 px). Sweeping speed shows the flake is
  structural, not noise, exactly as E29's sweep advice predicts: an unchanged animated page fails its
  own snapshot test most of the time.
- Fix: Before any baseline or check capture of an animated generated page, pin its clock (a fixed time
  parameter or a paused animation timeline) after the render pass; keep E1's render-pass step, and
  add a static-page control so the freeze is not applied blindly.
- Why this fix: It removes the only free variable left after the render pass (capture time), costs one
  parameter in the page, and does not loosen the diff threshold, which would hide real regressions.
- Rule of thumb: A render pass is not enough to snapshot an animated generated page: with a live clock
  0.80 of baseline and check pairs differed by 1 px or more at 120 px/s on an unchanged page; pin the
  page's clock for capture, and leave static pages alone.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 4/4
  predictions held; numbers above copied from the run). The model is a single moving element, not a
  real browser capture, so real pixel diffs will also include anti-aliasing.
- Composed: local__codex-visual-snapshots/E1, local__sandbox-edges/E29
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__render-pass-snapshot-of-animated-page-needs-frozen-clock.py
- Prediction: unfrozen, at least 0.75 of pairs differ at 120 px/s; frozen, zero at every speed; max diff
  grows with speed; a static page has zero differing pairs.
- Observed: RESULT: PASS 4/4; unfrozen flaky@120 0.80 max 7.68px; frozen 0; static 0
- Scenarios: 1) speeds 30, 60, 120, 240 px/s with a live clock; 2) the same with a frozen clock; 3)
  built to BREAK the claim: a static page, where freezing should not matter.
- Link: session; brain train auto pass 2 (edge); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E57 · compatible · sandboxes/2026-10-11__hallucination-flicker-needs-a-window-cap-not-an-average-rate.py · observed RESULT: FAIL 4/5; worst windows jitter 7/8/8 capped 3/3/3; cap keeps 0.75 at 2.0/s · session; brain train loop on hallucination as an art style (loop 5); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-12 · pass · sandboxes/2026-10-12__rebuild-seven-e45-render-pass-snapshot-frozen-clock.py · observed RESULT: PASS live@120 0.925; frozen 0 at all speeds; max px [8, 8, 24, 96]; static 0; slow marquee-only 0.000 · Own fixture: 3 elements (marquee at v px/s, a 0.5 Hz sine-offset element, static header), capture after a fixed 300 ms settle plus LCG latency jitter 0-80 ms and a 120 ms GC pause every 10th capture, 200 pairs per speed; the original used one element and an enumerated 0-4 frame jitter. Live clock at 120 px/s: 0.925 of pairs differ; frozen clock: 0 at every speed; max diff grows 8/8/24/96 px; static page 0. Caveat found: a slow marquee alone (5 px/s) differed in 0 of 200 pairs, so a live-clock harness looks clean on slow motion and the defect only shows on fast or oscillating elements. Toy of capture timing, not a real browser. · session_01P1LRA5HjMLEFnWXayE2EHx; blind review pass of SEVEN targets, 2026-10-12

## E44 — rescue near miss share falls with depth
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][rescue][missing][regret][probability]
- What: The regret kernel (regret scales with how easily the better outcome can be imagined, so near
  misses hurt more than clear misses) applied to SEVEN's spatial rescue search for a missing member,
  measuring where failed searches are near misses (the person was one sector past the searched block).
- Why built: The spatial search (seven E22, tuned in E31) gives failures a distance, which a dice roll
  never has. If near misses drive regret, the depth tuning also decides where the game's sharpest
  regret moments land, and nobody had measured that.
- Design: Exact computation on a 24-sector ring with E31's tuned settings per depth (noise 1.50, 1.50,
  2.25, 3.25 sectors; search hours 4, 2, 2, 2). For each failed search, the miss distance is the gap
  between the searched block and the person; a near miss is distance 1. Measured the near-miss share
  of failures and near misses per search.
- Got right: The share of failures that are near misses falls steadily with depth (0.397, 0.349, 0.236,
  0.157): deep failures read as bad luck in a big dark wood, shallow ones as almost having them.
- Where/why it failed: Two predictions were refuted. Shallow failures are not mostly near misses (0.397,
  not 0.50 or more). And near misses per search do NOT fall with depth: they peak in the middle (0.038,
  0.111, 0.119, 0.101), because shallow searches rarely fail at all. So by the kernel's mechanism the
  most frequent sharp-regret moments sit at mid depth, not at the edge of the woods.
- Fix: Treat mid depth as where losing someone hurts most often, and place the reveal there (the call
  heard next night from just past where you searched), rather than assuming the shallow woods carry
  the most painful losses; keep deep failures as the clear misses they already are.
- Why this fix: It uses the search model's own failure geometry to aim the emotional beat, with no new
  system, and it keeps the deep woods reading as hopeless rather than taunting.
- Rule of thumb: In a spatial rescue search, the share of failures that are near misses falls with depth
  (0.397 to 0.157), but near misses per search peak at mid depth (0.119), because shallow searches rarely
  fail; aim near-miss regret beats at mid depth.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 2/4
  predictions held; numbers above copied from the run). That near misses cause more regret is the
  kernel's research claim, taken as given here, and is not tested by this sandbox.
- Composed: ideas:REGRET/intensity/regret-scales-with-how-EASILY-the-better-outcome-can-be-imagined-not-with-the-size-of-the-loss, pappydapimp69__seven/E22, pappydapimp69__seven/E31
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__rescue-near-miss-share-falls-with-depth.py
- Prediction: shallow failures at least 0.50 near misses; deep at most 0.35; share falls monotonically;
  near misses per search also fall with depth.
- Observed: RESULT: FAIL 2/4; near-miss share 0.397/0.349/0.236/0.157; per search
  0.038/0.111/0.119/0.101
- Scenarios: 1) depth 0; 2) depth 1; 3) depth 2; 4) depth 3; 5) built to BREAK the claim: near misses
  per search rather than share (it broke).
- Link: session; brain train auto pass 1 (kernel); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-12 · pass · sandboxes/2026-10-12__rebuild-seven-e44-rescue-near-miss-share-by-depth.py · observed RESULT: PASS share 1.000->0.173 monotone; per-search peak depth 5 (0.161); widening block 0.950->0.259 (my flatten prediction refuted, the fall is robust) · Rebuilt from claim only on a LINE of sectors (not the original's ring of 24), sd = 0.6 x depth (not E31's tuned per-depth sigmas), a fixed 5-sector block, depths 1-10, exact erf. Share of failures that are near misses fell monotonically 1.000 to 0.173, and near misses per search peaked at mid depth (depth 5, 0.161), matching the rule (the author's own prediction that per-search also falls was refuted in both builds). Break case: a block that widens with depth did NOT flatten the fall (0.950 to 0.259), so the result is robust to search width. Original differs in fixture (ring, tuned sigmas, h shrinking with depth). · session_01P1LRA5HjMLEFnWXayE2EHx; blind review pass of SEVEN targets, 2026-10-12

## E43 — two observation bayes applies the prior once
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][disappearance][testing]
- What: An audit of seven E23's sandbox found its posterior after two night calls written as
  (prior x likelihood) squared for each hypothesis, which applies the prior twice. Measured how far
  that bug moves a two-observation posterior and whether it can flip a design conclusion.
- Why built: E23 concluded that cross-night consistency never makes a call proof (0.741). That number
  came from the squared prior, so the bug needed pricing as a reusable pitfall, not just a review.
- Design: Exact. Correct update p L1^2 / (p L1^2 + (1-p) L0^2) against the buggy (p L1)^2 /
  ((p L1)^2 + ((1-p) L0)^2) over priors 0.05 to 0.7 and three likelihood pairs, plus E23's own
  constants with consistency rates 0.749 and 0.293.
- Got right: The bug is invisible at a 0.5 prior (shift exactly 0) and small when the evidence is
  overwhelming (+0.007 at p 0.7), which is why it can survive a casual sanity check.
- Where/why it failed: At low priors it pulls the posterior hard toward the prior: at E23's constants
  the consistent-pair posterior is 0.942 correct vs 0.741 buggy, flipping its 0.85 proof threshold, so
  E23's refuted prediction actually held and its design conclusion was the bug's.
- Fix: Write a multi-observation update as prior times the product of likelihoods, normalised once;
  check it at a prior other than 0.5, where a doubled prior shows.
- Why this fix: The prior enters Bayes once per hypothesis regardless of the number of observations,
  and a 0.5 prior is exactly the case where the bug cancels.
- Rule of thumb: In a two-observation Bayes update apply the prior once (p L1^2, not (p L1)^2): the
  doubled prior cancels at p 0.5 but at a 0.15 prior moved seven E23's consistent-pair posterior from
  0.942 to 0.741 and flipped its proof threshold; test updates at a skewed prior.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry and by re-running
  E23's stored sandbox with only the prior line corrected (0.942); exact, numbers copied from the runs.
- Composed: pappydapimp69__seven/E23, pappydapimp69__seven/E35
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-11__two-observation-bayes-applies-the-prior-once.py
- Prediction: the bug pulls toward the prior side; moves E23's pair posterior by more than 0.15; no
  effect at p 0.5; flips a 0.85 threshold somewhere.
- Observed: RESULT: PASS 4/4 predictions held; E23 pair correct 0.942 buggy 0.741
- Scenarios: 1) priors 0.05 to 0.7 across three likelihood pairs; 2) E23's constants; 3) built to
  BREAK the claim: prior 0.5, where the bug should vanish.
- Link: session_01CGJM5fLtaFfLbkADKJ7DJt (brain train audit disappearance)
- Cited-by: 2026-10-12 · projects/pappydapimp69__sevin.md#E5 · incompatible · sandboxes/2026-10-12__day-keyed-false-whistle-leaks-on-the-second-night.py · observed RESULT: FAIL 3/5 predictions held; S1 single 0.346 pair 0.957; stable pair 0.792 off-dir 1.000; episodes pair 0.652 vs 0.500; break(4 dirs,F .5) pair 0.858; exact 0.930 vs doubled 0.732 · session; brain train loop round 2; session_01QGT1LfmPHPG99JEGaPhBwB

## E42 — target pinned to a bin centre fakes a step
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][disappearance][testing]
- What: An audit of seven E32's sandbox found the missing person pinned at sector 0, which is always
  the centre of a heard wedge at 8 directions. Measured whether that pin alone creates E32's step
  function of find chance over search hours.
- Why built: E32 reported hours 1 to 5 all finding 0.293 and called the step structural to coarse
  hearing; a target that always sits on a bin centre can only be found by searching whole bins.
- Design: Exact. 24-sector ring heard at 8 directions, discrete Gaussian noise sigma 4, search of the
  H sectors nearest the heard centre. Three fixtures: target pinned at a bin centre, pinned at a bin
  edge, and averaged over all 24 sectors.
- Got right: The pinned-centre fixture reproduces E32's numbers exactly (0.294 for H 1 to 5, 0.742 at
  H 6), confirming the audit's diagnosis rather than a reasoned guess.
- Where/why it failed: The step is the fixture: averaged over target positions, find chance rises at
  every H (0.098 to 0.536 over H 1 to 6), and pinning at a bin edge moves the plateau (0.000 at H 1,
  0.285 at H 2 and 3), so any single pinned target gives a step whose shape depends on where it sits.
- Fix: Average a perception or search test over target positions within a bin (or randomise the true
  position); never pin the target to one sector that is also a quantisation centre.
- Why this fix: The player's target lands anywhere in the wedge, so a per-position average is the
  quantity the design tunes; one pinned position measures the grid, not the mechanic.
- Rule of thumb: Never test a coarse-perception search with the target pinned to one sector: at a bin
  centre it fakes a step (0.294 flat over H 1 to 5, seven E32's numbers), averaged over positions find
  chance rises every sector (0.098 to 0.536).
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (exact; numbers copied
  from the run), which matches the stored E32 sandbox's output at noise 4.
- Composed: pappydapimp69__seven/E32, pappydapimp69__seven/E31
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-11__target-pinned-to-a-bin-centre-fakes-a-step.py
- Prediction: pinned at a centre, find chance flat for H 1 to 3; averaged, strictly rising for H 1 to
  6; pinned at an edge, H 1 below H 2.
- Observed: RESULT: PASS 3/3 predictions held; pinned H1-3 0.294/0.294/0.294; averaged 0.098->0.536
  strictly rising True; edge H1 0.000 H2 0.285
- Scenarios: 1) target pinned at a bin centre; 2) averaged over all sectors; 3) built to BREAK the
  claim: target pinned at a bin edge.
- Link: session_01CGJM5fLtaFfLbkADKJ7DJt (brain train audit disappearance)

## E41 — but therefore adjacency test is local
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [narrative][structure][testing]
- What: The but/therefore rule (adjacent beats must connect by "but" or "therefore", never "and
  then") turned into a mechanical beat checker and run on five hand-built stories, alongside a stricter
  therefore-only variant and a causal checker that adds the chronicle lesson and the Chekhov ledger's
  reach-the-ending rule.
- Why built: The owner asked for every SEVEN scene to obey a therefore-only rule. The kernel had never
  been built against, so it was unknown what an adjacent-beat check catches and what it gets wrong.
- Design: Deterministic. Beats carry planted facts, used facts, an opposition flag and a coincidence
  direction (into or out of trouble). A link reads therefore if the next beat uses something the
  previous one planted, but if it opposes, else and-then. Stories: tight causal, pure chronicle,
  cross-cut A/B plots, a dead-end subplot, an into-trouble storm plus a lucky rescue. Defects are
  hand-labelled; deletion mutations on the tight story.
- Got right: The adjacent but/therefore test catches a pure chronicle completely (6/6 links) and flags
  nothing on a tight causal story, so as a first-pass smell test it works.
- Where/why it failed: The adjacent form is local. It false-flags 5/6 links of a cross-cut story
  whose beats are caused two beats back; it misses all 3 beats of a dead-end subplot and flags the
  innocent beat where the main plot resumes; it flags luck that gets a character INTO trouble (fine
  per Pixar 19) yet passes a lucky rescue because the rescue reads as therefore; any opposition passes
  as but, so deleting the beat before a but goes unnoticed (3/5 deletions caught). Therefore-only flags
  every conflict beat of the tight story as a defect (2 false positives).
- Fix: Check causality, not adjacency: every beat must use or oppose SOME earlier beat, every planted
  fact must lie on a chain that reaches the ending, and only coincidence that removes trouble is a
  defect. That checker hit all labelled defects (dead end 3/3, rescue 1/1) with one false positive (an
  uncaused second-plot opening). Keep "but" as a valid link; do not use therefore-only.
- Why this fix: It keeps what the rule is for (no beat without a cause) while letting stories braid
  plots and use conflict, and it puts the flag on the beat that is actually wrong.
- Rule of thumb: Use but/therefore between adjacent beats only as a smell test: it catches chronicles
  but false-flags cross-cut plots, misses dead-end subplots and lucky rescues, and therefore-only
  rejects every conflict beat; check that each beat uses or opposes some earlier beat and reaches the
  ending instead.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (deterministic, numbers
  copied from the run). The stories and labels are my own constructions, not SEVEN's scenes. Two fixture
  bugs were fixed before the reported run (a mislabelled dead end, a rescue beat missing its cause).
- Composed: ideas:SYSTEM/narrative/but-therefore-spine, pappydapimp69__test/E10, 2026-10-10__chekhov-ledger-checker-unfired-spotlight-unintroduced-resolver-dead-end-and-motif-false-positive/E1
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-11__but-therefore-adjacency-test-is-local.py
- Prediction: adjacent test flags 6/6 chronicle links; therefore-only false-flags >= 2 but beats;
  cross-cut false-flagged >= 50% by adjacency and 0 by causal; a dead end passes adjacency and causal
  catches it; adjacency flags the into-trouble storm while causal flags only the rescue; every middle
  deletion caught by adjacency.
- Observed: RESULT: FAIL 3/6 predictions held; chronicle ADJ-BT hits 6/6; therefore-only false positives
  on tight 2; crosscut ADJ-BT fp 5/6 CAUSAL fp 1; deadend ADJ-BT hits 0 CAUSAL miss 0; coincidence ADJ-BT
  flags [1] CAUSAL [3]; deletions 3/5
- Scenarios: 1) tight causal story; 2) pure chronicle; 3) cross-cut A/B plots; 4) dead-end subplot;
  5) storm into trouble plus lucky rescue; 6) built to BREAK the claim: deleting each middle beat of the
  tight story.
- Link: session_01CGJM5fLtaFfLbkADKJ7DJt (brain train on narrative)

## E40 — one answer read by bayes matches asking both
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][doppelganger][deduction]
- What: Seven E26 said asking BOTH people at the fire the same question doubles the player's edge
  over asking one (0.633 vs 0.567). Rebuilt with a Bayes-optimal reader who uses every observation,
  including a match between the asked person's answer and the player's memory.
- Why built: A blind rebuild of seven E26 for review; the 0.567 single-question figure looked like it
  ignored what a matching answer tells the player.
- Design: Exact enumeration. A day has 8 binary facts of unknown true value; the fake bends one; a
  question covers 3; memory per fact recalls true 0.7 or blank; a variant adds a wrongly-sure memory
  (0.6 true, 0.1 flipped). Worlds are grouped by what the player sees and the more probable identity
  is chosen. Compared: ask one, ask both, no memory, three at the fire.
- Got right: Ask-both reproduces E26's formula exactly (1/2 + 1/2 x coverage x recall = 0.631), no
  memory gives exactly 0.5, and with three at the fire a majority answer beats a guess (0.583 vs 0.333)
  without any memory.
- Where/why it failed: Asking ONE person, read optimally, is also 0.631: the edge ratio is 1.00, not
  2.0. A match with memory is evidence the asked person is real, because the fake only matches when the
  bent fact is uncovered or forgotten. E26's doubling came from treating a match as no information.
  Asking both only helps when memory can be wrongly sure (0.594 vs 0.576 with a 0.1 false recall).
- Fix: Do not justify a two-person question budget by the doubling; with reliable memory one question
  gives the same edge. Budget a second question only if memory in SEVEN can mislead, or to make the
  scene legible (the player sees the two answers differ), and say which.
- Why this fix: It keeps the design argument on what the player can actually infer, and stops a
  question budget being spent on an edge that a careful player already has from one answer.
- Rule of thumb: In a two-suspect identity check, a single answer that matches the player's memory is
  evidence too: read optimally, asking one gives the same accuracy as asking both (0.631 each with
  memory that is never wrong); a second question only adds accuracy when memory can be wrongly sure.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (exact enumeration;
  numbers copied from the run). The fact count, coverage and recall rates are my choices.
- Composed: pappydapimp69__seven/E26, pappydapimp69__seven/E24
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-11__one-answer-read-by-bayes-matches-asking-both.py
- Prediction: ask-both = 0.631; ask-one read optimally equals ask-both; no memory 0.5; three at the fire
  above 1/3; with wrongly-sure memory ask-both within 5% of ask-one.
- Observed: RESULT: FAIL 4/5 predictions held; ask-one(optimal) 0.6312 ask-both 0.6312 edge ratio 1.00;
  wrong-sure ratio 1.23; three no-memory 0.583
- Scenarios: 1) ask one; 2) ask both; 3) no memory; 4) three at the fire; 5) built to BREAK the claim:
  wrongly-sure memory, where asking both finally helps.
- Link: session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E89 · incompatible · sandboxes/2026-10-12__rebuilt-witness-list-forks-a-fakes-lie-across-reload.py · observed RESULT: FAIL 8/10; changed verbatim 0.000 reorder 0.797 drop 0.395; minhash reorder 0.000 drop 0.208; sorted reorder 0.000 drop 0.395; resume+draws constant True · session; brain train loop round 3; session_01QGT1LfmPHPG99JEGaPhBwB

## E39 — expose first holding depends on test cap
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][doppelganger][rescue]
- What: Seven E29 found rescue-narrows holds a doppelganger at the fire fewer nights than
  expose-first. Rebuilt with expose-first allowed to keep testing by elimination after the window, on
  a longer horizon.
- Why built: A blind rebuild of seven E29 for review; a missed rescue window parks the fake to the
  horizon, while elimination testing always ends, so the ranking should depend on the test cap.
- Design: Exact. Party of 4, 3-night window, 8-night horizon, search 0.45; expose-first tests one per
  night with derived accuracies (0.4375, 0.5, 0.625, certain); rescue-narrows uses a 1-of-2 pick 0.631;
  also a 5-night horizon.
- Got right: Rescue-narrows still spends fewer pylons (1.141 vs 1.949 per disappearance), so on the
  pylon axis E29 holds.
- Where/why it failed: On holding time the ranking flips: expose-first holds the fake 1.949 nights,
  rescue-narrows 2.992 (2.493 at a 5-night horizon). Elimination exposes the fake within 4 nights,
  while a missed window (0.166) parks it to the horizon. E29's result needs expose-first's tests to stop
  at the window.
- Fix: State the comparison with the test cap explicit; if SEVEN lets the player keep testing after the
  window, pair rescue-narrows with a post-window pylon fallback (E33) before claiming it holds less.
- Why this fix: Holding time is dominated by whichever rule can leave a fake unresolved to the horizon,
  so the cap, not the ordering, decides the axis.
- Rule of thumb: Rescue-narrows only holds a doppelganger fewer nights than expose-first if exposure
  testing stops at the rescue window; with elimination testing allowed after it, expose-first held
  1.949 nights vs 2.992, though rescue-narrows still spent fewer pylons.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (exact; numbers copied
  from the run). The accuracies and rates are my choices.
- Composed: pappydapimp69__seven/E29, pappydapimp69__seven/E33
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-11__expose-first-holding-depends-on-test-cap.py
- Prediction: rescue-narrows holds fewer nights; missed window over half of its held nights; it spends
  fewer pylons; at a 5-night horizon it still holds less.
- Observed: RESULT: FAIL 1/4 predictions held; A held 1.949 B held 2.992 (h5 2.493); miss share 0.445;
  pylons A 1.949 B 1.141
- Scenarios: 1) expose-first by elimination; 2) rescue-narrows at horizon 8; 3) built to BREAK the
  claim: rescue-narrows at horizon 5.
- Link: session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)

## E38 — centred heard wedge search has no step
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][disappearance][balance]
- What: Seven E32 said that at 8 heard directions, find chance becomes a step function of search
  hours (hours 1 to 5 identical, then a jump), so a target table misses by 0.207. Rebuilt with a
  search centred on the heard direction.
- Why built: A blind rebuild of seven E32 for review; a search that grows outward from the heard
  centre should gain something with each sector, which a flat plateau contradicts.
- Design: Exact. 40 internal sectors, 5 per heard wedge, so each wedge has a centre sector. True
  sector plus discrete Gaussian noise, rounded to 8 heard directions. A search of H sectors covers the
  H sectors nearest the heard centre. Own targets 0.85, 0.65, 0.45, 0.30 with noise non-decreasing and
  a skill-gap floor of 0.20.
- Got right: Find chance rises with every added sector (0.060, 0.119, 0.179, 0.236 for H 1 to 4 at
  sigma 6.5; 0.159 to 0.958 over H 1 to 10 at sigma 2), and the target table is hit within 0.007 with
  every gap at least 0.256, so E31's tunability survives 8-direction hearing.
- Where/why it failed: E32's step function is not a property of 8-direction hearing. Both of my
  predictions that reproduced E32 (flat over H 1 to 4, table missed by more than 0.05) failed, so the
  plateau must come from how E32 maps hours onto sectors, not from the coarse hearing.
- Fix: Grow the search outward from the centre of the heard direction one sector at a time, and keep
  E31's two knobs; check any plateau in find chance against how effort is mapped to ground before
  calling it structural.
- Why this fix: It keeps every hour of search meaningful to the player and leaves the designer a
  smooth dial, which E32 said was lost.
- Rule of thumb: Coarse hearing (8 directions) does not by itself make a find chance a step function:
  a search grown outward from the heard centre gains with every sector and still hits a 0.85 to 0.30
  table within 0.007; a plateau means effort is mapped to ground badly.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (exact; numbers
  copied from the run). I did not read E32's sandbox; its plateau cause is my inference.
- Composed: pappydapimp69__seven/E32, pappydapimp69__seven/E31, pappydapimp69__seven/E25
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-11__centred-heard-wedge-search-has-no-step.py
- Prediction: (reproducing E32) flat over H 1 to 4 at sigma 6.5; target table missed by more than 0.05;
  every depth keeps a gap of at least 0.20.
- Observed: RESULT: FAIL 1/3 predictions held; sigma6.5 H1-4 0.060/0.119/0.179/0.236; worst target miss
  0.007
- Scenarios: 1) find chance by H at sigma 6.5; 2) by H at sigma 2; 3) a four-depth target table;
  4) built to BREAK the claim: E32's own predictions run on a centred search.
- Link: session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)

## E37 — call stopping point is set by history
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][disappearance][rescue]
- What: Seven E28 scored the value of answering a night call on night k with a fixed prior and a
  known k, and concluded that the fade plus false calls stop rescues at one natural point. Rebuilt with
  exact Bayes over what the player has actually heard and searched.
- Why built: A blind rebuild of seven E28 for review; the player never knows k or a fresh prior, only
  a history of calls and failed searches.
- Design: Exact. Prior 0.20 that a member went missing at night 0, real call 0.85 x 0.65^k, false calls
  0.12 per night, a night out finds with 0.85, risk 0.20. Four histories scored at night k: memoryless
  (E28 style), a call every night with failed searches, a call after silent nights following one failed
  search, and a first call after silent nights.
- Got right: All four histories agree on night 0 (0.644), so a first-night call is worth answering in
  every reading, as E28 said.
- Where/why it failed: After night 0 they split widely: the last night where answering pays is 6 for
  the memoryless formula, 2 for repeated or returning calls, and 0 for a first call after silence
  (posterior 0.159 by night 1). Max posterior gap from the memoryless formula is 0.419. The stopping
  point is set by the history, and the per-night formula overstates late value.
- Fix: Price night-call value on the player's evidence (calls heard, searches failed, silence), not on
  nights since the disappearance; tune the fade and night risk against those histories.
- Why this fix: The player acts on what they heard, so a tuning that assumes they know k sets the
  wrong stopping point; failed searches and silences are the evidence that should end rescues.
- Rule of thumb: Score a missing member's night call on the player's history, not on nights since the
  disappearance: the last night answering pays ranged from 0 to 6 across histories (gap up to 0.419),
  so fade and false calls alone do not set one natural stopping point.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (exact; numbers copied
  from the run). The rates are my choices.
- Composed: pappydapimp69__seven/E28, pappydapimp69__seven/E23, pappydapimp69__seven/E27
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-11__call-stopping-point-is-set-by-history.py
- Prediction: memoryless value negative by night 3; some history differs from memoryless by more than
  0.15; last-paying night differs between histories by at least 2 nights.
- Observed: RESULT: FAIL 2/3 predictions held; last-pays night memoryless 6, repeated 2, returning 2,
  fresh 0; max posterior gap vs memoryless 0.419
- Scenarios: 1) memoryless; 2) repeated calls with failed searches; 3) returning call after silence;
  4) built to BREAK the claim: a fresh first call after silent nights.
- Link: session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E77 · compatible · sandboxes/2026-10-12__fade-to-silence-ends-hopeless-searches-at-small-rescue-cost.py · observed RESULT: FAIL 2/3; shallow: rescue 0.814/0.942 late 0.034/0.205; deep: rescue 0.206/0.337 late 0.136/1.286; hopeless: rescue 0.044/0.077 late 0.163/1.647 (fade/floor) · session; fair test of the owner's fade decision, 2026-10-12; session_01NHKVhTvCnvtvZ2NGLSPYj6

## E36 — nearest open cell is not legal placement on dense maps
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedev][testing][procgen][pathfinding]
- What: Seven E12's fix for tests that place an agent in rock (place it on the nearest OPEN cell, via a
  helper that throws rather than returning rock) checked on denser procedural maps, where open cells
  can sit in pockets sealed off from the agent's goal.
- Why built: A rebuild of seven E12 from another session confirmed its claim, but its legal-placement
  arm fell to 0.865 at rock density 0.35, which the entry's fix did not predict.
- Design: 30x30 grid, rock density 0.05 to 0.40, 200 placed episodes per density, a BFS agent that must
  take one step toward the goal. Three placements: the computed point as-is, the nearest open cell,
  and the nearest cell inside the goal's connected open region.
- Got right: Placement inside the goal's component passes every episode at every density (1.000
  throughout), and at low density it agrees exactly with nearest-open, so the stricter helper costs
  nothing where the old one worked.
- Where/why it failed: Nearest-open placement degrades with density: 0.975 at 0.25, 0.865 at 0.35 and
  0.630 at 0.40. The cell is legal by the map's tile rules but the agent is sealed in a pocket, so the
  test again measures an agent that cannot act, which is the exact failure E12 fixed, one density up.
- Fix: Define legal placement as inside the connected region that contains the agent's goal (flood
  fill from the goal, then take the nearest cell in it), and have the helper throw when that region is
  empty, rather than accepting any open tile.
- Why this fix: It states legality in the terms the behaviour needs (can act toward its goal), not the
  terms the tile map offers (not rock), and it costs one flood fill per test setup.
- Rule of thumb: Placing a test agent on the nearest open cell is not legal placement once a
  procedural map is dense: open pockets sealed from the goal took the pass rate from 1.000 to 0.630 at
  rock density 0.40; place inside the goal's connected region instead.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 3/3
  predictions held; numbers above copied from the run). The map and agent are my own model, not
  SEVEN's generator, so the densities where it bites will differ there.
- Composed: pappydapimp69__seven/E12, pappydapimp69__seven/E13, pappydapimp69__seven/E11
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__nearest-open-cell-is-not-legal-placement-on-dense-maps.py
- Prediction: nearest-open below 0.90 at density 0.35 or more; nearest-connected 1.000 everywhere;
  the two agree at the lowest density.
- Observed: RESULT: PASS 3/3; d0.05 open 1.000 connected 1.000; d0.25 open 0.975 connected 1.000;
  d0.35 open 0.865 connected 1.000; d0.40 open 0.630 connected 1.000
- Scenarios: 1) naive placement; 2) nearest open cell; 3) nearest cell in the goal's region; 4) built
  to BREAK the claim: low density, where the two helpers should agree.
- Link: session; follow-up to the 2026-10-11 rebuild review of seven E12; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-11 · pass · sandboxes/2026-10-11__rebuild-seven-e36-placement-on-cave-maps.py · observed RESULT: FAIL 3/4 predictions held; nearest-open 0.30:1.000 0.40:1.000 0.45:0.987 0.50:0.950; goal-region 1.000 all; agree low 1.000; displacement 0.20->1.31; checks [False, True, True, True] · Rebuilt on clustered cellular-automata cave maps (40x24, 3 smoothing passes) instead of uniform rock noise, with a random requested spawn. Goal-region placement passes 1.000 at every fill (by construction) and agrees with nearest-open at low fill; nearest-open does degrade with density (1.000, 1.000, 0.987, 0.950 at fill 0.30-0.50), so the claim's direction and fix hold. Caveat: on clustered maps the drop is mild (0.950, not 0.630), my own < 0.90 prediction failed, and the stricter helper moves the spawn 6.5x further at the densest fill (0.20 to 1.31 cells), which can change what a test measures. · session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Audited: 2026-10-11 · pass · Read the entry and its stored sandbox. Pass rates are computed by BFS, but each density uses ONE map (make_map(d, 7)), so the quoted 0.865 and 0.630 are one map's pocket structure. Re-running the stored code across 40 map seeds gives a nearest-open mean of 0.453 at density 0.35 (range 0.0 to 0.97) and 0.183 at 0.40 (range 0.0 to 0.84): the claim is stronger than stated, the numbers are not representative. Goal-region placement at 1.000 is true by construction. The direction and the fix hold; quote a seed-averaged rate, not one map. · session_01CGJM5fLtaFfLbkADKJ7DJt (brain train audit disappearance)

## E35 — waiting for a second call trades rescues for safety
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][disappearance][missing][rescue][probability]
- What: Two player strategies for night calls about a missing member: go out on every call, or wait
  for a second call from a consistent direction (seven E23's tell, heard at 8 directions per E25),
  under the owner's fade-to-silence decision and false calls.
- Why built: E23 made cross-night consistency the learnable tell, but waiting a night costs fade and
  time; nobody had priced what the tell costs in rescues versus what it saves in wasted nights.
- Design: Exact enumeration of all call patterns over 6 nights. Missing world: calls at 0.9 times
  0.6 per night, real pairs consistent 1.0. Empty world: false calls 0.106, false pairs consistent
  0.375. A night out finds with 0.9. Prior 0.15 missing. Measured rescue chance, wasted nights when
  nobody is missing, and rescues per night out.
- Got right: Waiting is a real, learnable skill: it raises rescues per night out 3.49x (0.578 vs 0.166)
  and cuts wasted nights from 0.636 to 0.021. Answering the first call still rescues 0.952 despite the
  fade, so both strategies are viable and neither is dominant.
- Where/why it failed: Waiting halves the rescue chance (0.952 to 0.505, a 0.469 cut): the fading call
  often never gives a second, consistent chance. So the consistency tell, played safe, quietly costs
  half of all rescues, which is a steep price for a tell meant to help.
- Fix: Make the cost of a wasted night visible and real (the night risk), so the choice between
  answering at once and waiting for a second call is a judgement, not an obvious best play; keep the
  first-night call strong so the brave strategy stays rewarding.
- Why this fix: The two strategies trade rescue for safety in opposite directions, which is the
  tension the design wants the player to feel at night; tuning only one side would make the other
  never worth choosing.
- Rule of thumb: Waiting for a second, consistent night call before searching for a missing member
  makes each night out 3.49x more productive but halves the rescues (0.952 to 0.505) once calls fade,
  so price wasted nights with real night risk or the safe play wins or loses outright.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 4/4
  predictions held; numbers above copied from the run). Pairs are treated as independent for
  consistency, which is my simplification.
- Composed: pappydapimp69__seven/E23, pappydapimp69__seven/E25, pappydapimp69__seven/E27, pappydapimp69__seven/E28, ideas:GAME-DESIGN/disappearance/call-without-a-name
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__waiting-for-a-second-call-trades-rescues-for-safety.py
- Prediction: waiting raises rescues per night out at least 1.3x; waiting cuts rescue chance by at least
  0.20; waiting cuts wasted nights by more than half; first-call rescue stays at least 0.85.
- Observed: RESULT: PASS 4/4 predictions held; rescue first 0.952 wait 0.505; wasted first 0.636 wait
  0.021; efficiency ratio 3.49
- Scenarios: 1) answer every call; 2) wait for a consistent pair; 3) built to BREAK the claim: whether
  the fade ruins even the first-call strategy (it did not, 0.952).
- Link: session; Seven docs/IDEAS.md "Disappearance and return"; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-11 · pass · sandboxes/2026-10-11__rebuild-seven-e35-wait-for-second-call.py · observed RESULT: PASS 4/4 predictions held; rescue first 0.963 wait 0.730; wasted first 0.721 wait 0.082; eff ratio 2.36; indep-pairs wait 0.727; checks [True, True, True, True] · Rebuilt with a correlated bearing model (fixed true bearing plus sigma-25 noise heard at 8 directions, so real pairs are not always consistent), false calls in both worlds, prior 0.20, call 0.85 x 0.65^k, find 0.85, seeded Monte Carlo of 400k worlds. Waiting raises rescues per night out 2.36x and cuts wasted nights from 0.721 to 0.082, at a rescue cost of 0.963 to 0.730. Independent-pair consistency gives 0.727 vs 0.730 correlated, so the independence simplification does not matter. Caveat: the cut is about a quarter, not 'halves'; that magnitude is E35's fixture. · session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Audited: 2026-10-11 · pass · Read the entry and its stored sandbox. Exact enumeration over 2^6 call patterns and consistency masks computes rescue chance, wasted nights and efficiency, rather than assuming them. Treating pair consistency as independent is exact for uniform false calls, and real pairs are set to 1.0 consistent, generous to waiting; my rebuild with correlated bearings found independence changes the wait-rescue chance by under 0.01. Caveats: WAIT requires the consistent call on the IMMEDIATELY preceding night, which with a fading call drives the 'halves the rescues' figure (my any-earlier version cut about a quarter), and the missing world has no false calls. The claim's direction holds. · session_01CGJM5fLtaFfLbkADKJ7DJt (brain train audit disappearance)
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E43 · incompatible · sandboxes/2026-10-11__two-observation-bayes-applies-the-prior-once.py · observed RESULT: PASS 4/4 predictions held; E23 pair correct 0.942 buggy 0.741 · session_01CGJM5fLtaFfLbkADKJ7DJt (brain train audit disappearance)

## E34 — time limit usually abandons before the camp move
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][abandonment][disappearance][missing][rescue]
- What: Which abandonment route ends a missing member's rescue first once both exist: the owner's time
  limit (the call fades to silence, lost after night 6) or the sleep-measured spatial window (lost when
  the lead sleeps two areas ahead, seven E30), and whether sleeping out keeps abandonment deliberate.
- Why built: The owner accepted the time limit as a second abandonment route. Nobody knew which route
  would actually decide most losses, which changes what the player experiences as the abandoning act.
- Design: Exact enumeration of every 8-day plan of stay, scout one, scout two or move camp (65536
  plans), then again with a fifth action, sleeping out two areas ahead (390625 plans). The member is
  never found, so the plan alone decides which limit hits first.
- Got right: Neither rule ever abandons by accident (0 accidental losses in both sets), even with
  sleeping out allowed, because sleeping out is itself a deliberate dusk choice. The sleep rule from
  E30 holds up under the extra action.
- Where/why it failed: With camp moves only, the time limit abandons first in 0.534 of plans, so the
  silence, not a choice the player made, is the most common way someone is left behind. Allowing
  sleeping out flips it (space-first 0.860), which means one action changes the whole feel.
- Fix: Decide which route should be the usual one and tune to it: if the camp move should be the felt
  choice, keep the time limit longer than the typical two-move pace; if the silence should be, keep
  sleeping out rare and costly.
- Why this fix: Both routes are legitimate by the owner's decision, but the player only learns the
  one that usually happens, so the ratio between them is a design dial, not a side effect.
- Rule of thumb: When a missing member can be abandoned both by time (the call fades out) and by
  space (the camp moves on), measure which route ends most rescues: in the toy model the time limit
  came first in 0.534 of plans, and allowing sleeping out flipped it to 0.860 space-first.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 4/4
  predictions held; numbers above copied from the run). The equal weighting of plans is my choice;
  real players will not pick actions uniformly.
- Composed: pappydapimp69__seven/E30, pappydapimp69__seven/E27, ideas:GAME-DESIGN/rescue/abandonment-by-progress
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__time-limit-usually-abandons-before-the-camp-move.py
- Prediction: time-first at least 0.40 of base plans; 0 accidental in base plans; 0 accidental with
  sleeping out; sleeping out makes space-first the majority.
- Observed: RESULT: PASS 4/4 predictions held; base time-first 0.534; sleepout space-first 0.860;
  accidental 0/0
- Scenarios: 1) base action set; 2) with sleeping out; 3) built to BREAK the claim: whether sleeping
  out creates accidental abandonment (it did not).
- Link: session; Seven docs/blueprint-0.35-camp-tasks-and-time.md; owner decision 2026-10-11 on the fade; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-11 · pass · sandboxes/2026-10-11__rebuild-seven-e34-abandonment-route-weights.py · observed RESULT: PASS 3/3 predictions held; time-first by q 0.10:0.886, 0.25:0.534, 0.40:0.233, 0.60:0.041; accidental 0 · Rebuilt with 7-day plans, a time limit after night 5, the sleep-measured space rule, and i.i.d. player profiles with camp-move probability q instead of equal weights. Equal weighting (q=0.25) gives time-first 0.534, matching E34. But the share swings from 0.886 (q=0.10) to 0.041 (q=0.60), so plan weights decide which route is 'usual'; E34's 'silence is the most common way' is a uniform-weights artifact. The rule of thumb itself (measure which route dominates; it is a dial) holds and is what my rebuild shows. 0 accidental is true by construction under the sleep rule. · session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Audited: 2026-10-11 · modeled · Read the entry and its stored sandbox. It enumerates all 4^8 and 5^8 plans with equal weight and computes which limit hits first, so 0.534 time-first and 0.860 space-first with sleeping out are real outputs of that enumeration. But outcome() can only return a space loss on 'move' or 'sleepout2', so 0 accidental losses and the 'break case' cannot fail. The claim is about which abandonment players will experience, and uniformly random plans stand in for player behaviour (the entry says so); my rebuild found the time-first share runs from 0.886 to 0.041 as the camp-move rate goes from 0.10 to 0.60. A real-player claim tested on a toy: modeled. · session_01CGJM5fLtaFfLbkADKJ7DJt (brain train audit disappearance)
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E51 · compatible · sandboxes/2026-10-11__abandonment-felt-dismantle-call.py · observed RESULT: PASS camp-down call on the dawn bearing: posterior 0.9-0.995, informed 0.775, in 3/3; alone it is weak (0.46-0.69); fk=0 announces; fk=1 alone says nothing. Numbers: C 0.930/0.971/0.915, false alarm 0.0146-0.0179; B 0.455/0.690. · seven-1.0.0 session 2026-10-11, commit 4ecc609; session_01XbmpbLd4QyYTiQBBzo2Hdw

## E33 — pylon fallback after missed window competes with depth
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][doppelganger][replacement][rescue][balance]
- What: The pylon fallback seven E29 proposed (after a missed rescue window, keep testing the party
  with pylons so the doppelganger is not held to the horizon), priced against the area pylon budget
  from blueprint 0.35 (3 pylons in area 1, 2 to 4 later, each also shielding depth).
- Why built: E29 said the missed window, not the ordering, keeps a fake at the fire longest, and
  suggested a fallback. A fallback spends the same pylons the depth system needs, so it had to be priced.
- Design: Exact fractions. Rescue-narrows as in E29 (search 0.6 per night, 2-night window, 1-of-2 pick
  at 0.633). On a miss, up to K pylon tests from night 3, at 0.45 then 0.55 then certain; otherwise the
  fake stays to night 6. Measured fake-held nights and pylons per disappearance for K = 0 to 3.
- Got right: The fallback is cheap: two tests add 0.248 pylons per disappearance and the total stays
  under 1.5 (1.396). Each extra test still lowers holding time (2.040, 1.824, 1.727, 1.688).
- Where/why it failed: The fallback helps far less than I predicted: two tests cut fake-held nights by
  only 0.153, not 0.25 or more, because the miss happens in only 0.16 of disappearances. Most holding
  time is the first two nights of every case, before any rescue resolves.
- Fix: Treat one fallback test as enough, and attack the first nights instead: make the same-night
  search the strong default (E22: same-night shallow find 0.94), since the night the fake arrives is
  where most of the holding time sits.
- Why this fix: It spends pylons where they buy the most, leaves the depth budget mostly intact, and
  matches the design's existing push to go out the same night.
- Rule of thumb: A pylon fallback after a missed doppelganger rescue window is cheap (about 0.25 pylons
  per disappearance) but buys little (0.153 fewer held nights), because misses are rare; cut holding
  time by making the same-night search the strong default instead.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 3/4
  predictions held; numbers above copied from the run). Accuracies and rates come from E29 and E26;
  the night-3 start is my choice.
- Composed: pappydapimp69__seven/E29, pappydapimp69__seven/E26, pappydapimp69__seven/E22, ideas:GAME-DESIGN/doppelganger/rescue-returns-a-duplicate, ideas:GAME-DESIGN/doppelganger/the-test-must-be-inviolable
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__pylon-fallback-after-missed-window-competes-with-depth.py
- Prediction: two fallback tests cut held nights by at least 0.25; fallback under 0.25 pylons per
  disappearance; total under 1.5; a third test still lowers held nights.
- Observed: RESULT: FAIL 3/4 predictions held; held 0/2/3 tests 2.040/1.727/1.688; pylons
  1.148/1.396; cut 0.153
- Scenarios: 1) no fallback; 2) one test; 3) two tests; 4) built to BREAK the claim: a third test,
  checking for diminishing returns.
- Link: session; Seven docs/blueprint-0.35-camp-tasks-and-time.md (pylons per area); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-11 · fail · sandboxes/2026-10-11__rebuild-seven-e33-fallback-vs-miss-rate.py · observed RESULT: FAIL 3/4 predictions held; cut/miss constant 3.320; cut at search 0.35 1.403, at 0.60 0.531; checks [True, True, True, False] · Rebuilt with an 8-night horizon (not 6), fallback picks 0.40/0.55/certain from night 3, and search rate swept 0.30 to 0.75. Cut per missed window is a constant 3.32 nights, so the fallback's value is exactly proportional to the miss rate and the horizon. At E33's own search rate 0.60 the cut is 0.531 nights, not 0.153, and at search 0.35 it is 1.403, for at most 0.78 extra pylons. 'Cheap but buys little' is a product of the 6-night horizon and 0.6 search rate, not a property of the fallback; 'one test is enough' should not be generalised. · session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E39 · incompatible · sandboxes/2026-10-11__expose-first-holding-depends-on-test-cap.py · observed RESULT: FAIL 1/4 predictions held; A held 1.949 B held 2.992 (h5 2.493); miss share 0.445; pylons A 1.949 B 1.141 · session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Audited: 2026-10-11 · fail · Read the entry and its stored sandbox. The entry reports the fallback 'cuts fake-held nights by only 0.153', but the code computes cut = 1 - held2/held0, a RELATIVE cut. In nights it is 2.040 - 1.727 = 0.313, which meets the entry's own prediction of at least 0.25, so its one missed prediction, and the 'helps far less than I predicted' conclusion, come from comparing a fraction against a night count. The fallback arithmetic is otherwise computed, but tied to a 6-night horizon and 0.6 search rate; my rebuild found the absolute cut is 3.32 nights per missed window, 0.531 at an 8-night horizon. · session_01CGJM5fLtaFfLbkADKJ7DJt (brain train audit disappearance)

## E32 — find chance tuning survives 8 direction hearing
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][disappearance][rescue][balance][probability]
- What: Whether seven E31's tuning of the spatial find-chance for a missing member (targets 0.90 to
  0.35 hit within 0.017) survives when the search is aimed from the direction the player actually
  hears, rounded to 8 points as seven E25 says, instead of an exact 24-sector bearing.
- Why built: E31 settled the tuning on information the player does not have; E25 showed perceived
  direction is coarser. If the tuning breaks under real hearing, the find-chance tension is not settled.
- Design: Exact computation with a discretised normal for bearing noise. The heard direction is
  rounded to 8 centres (3 sectors each) and a search covers the H sectors nearest that centre. Same
  targets, noise cap 4, noise not falling with depth, skill gap at least 0.20.
- Got right: Skill survives: every depth keeps a gap of at least 0.25. And the break case held: E31's
  24-sector settings reused at 8 points miss their targets by more than 0.05, so the check was needed.
- Where/why it failed: The tuning does not survive: the worst target is missed by 0.207. The cause is
  structural: with 8 heard directions, search hours 1 to 5 all give the same find chance (0.293 at
  noise 4, 0.495 at 2.25) and hour 6 jumps to the next wedge (0.742, 0.954). Find chance becomes a step
  function of hours, so mid targets like 0.50 sit in a dead zone.
- Fix: Size search effort in whole heard wedges (one direction's worth of ground per step), and tune
  difficulty through noise and the number of wedges searched, not single hours; an hour that cannot
  reach the next wedge should not be offered as a choice.
- Why this fix: It matches the search to what the player can perceive, removes hours that buy nothing,
  and restores a smooth enough dial for the designer; it is the same sizing rule as mirage E19.
- Rule of thumb: Tune a missing member's find-chance on the direction the player can hear, not the
  internal bearing: at 8 heard directions search hours 1 to 5 found exactly the same and the 0.90 to
  0.35 target table missed by 0.207, so size search effort in whole heard wedges.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 3/4
  predictions held; numbers above copied from the run, plus a probe of find chance by hours at noise
  2.25, 3.0 and 4.0). The target table is my example.
- Composed: pappydapimp69__seven/E31, pappydapimp69__seven/E25, pappydapimp69__seven/E22, pappydapimp69__mirage/E19
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-11__find-chance-tuning-survives-8-direction-hearing.py
- Prediction: at 8 heard directions all targets within 0.05; every gap at least 0.20; more total search
  hours than at 24 sectors; E31's settings reused unchanged miss a target by more than 0.05.
- Observed: RESULT: FAIL 3/4 predictions held; worst miss at 8 points 0.207; total hours 24pt 10 vs 8pt
  14. Probe at noise 4: hours 1-5 all 0.293, hour 6 0.742.
- Scenarios: 1) 24-sector tuning; 2) 8-direction tuning; 3) built to BREAK the claim: E31's settings
  reused at 8 directions.
- Link: session; Seven docs/IDEAS.md "Disappearance and return"; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-11 · fail · sandboxes/2026-10-11__rebuild-seven-e32-heard-wedge-steps.py · observed RESULT: FAIL 1/3 predictions held; sigma6.5 H1-4 0.060/0.119/0.179/0.236; worst target miss 0.007; checks [False, False, True] · Rebuilt with 40 internal sectors (5 per heard wedge, so each wedge has a centre sector), noise heard at 8 directions, and a search of H sectors nearest the heard centre. There is no step function: at sigma 6.5 find chance rises 0.060/0.119/0.179/0.236 over H=1..4 and smoothly after, and at sigma 2 it climbs 0.159 to 0.958 over H=1..10. My own table 0.85/0.65/0.45/0.30 is hit within 0.007 with gaps of at least 0.256. E32's 'hours 1-5 identical, then a jump' is therefore not structural to 8-direction hearing; it comes from how its search maps hours to sectors around the heard centre. E32's refutation of E31 does not stand. · session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E38 · incompatible · sandboxes/2026-10-11__centred-heard-wedge-search-has-no-step.py · observed RESULT: FAIL 1/3 predictions held; sigma6.5 H1-4 0.060/0.119/0.179/0.236; worst target miss 0.007 · session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Audited: 2026-10-11 · fail · Read the entry and its stored sandbox. The step function is a fixture artifact: the missing person is fixed at sector 0, which is always a wedge centre at 8 points (step 3), and the heard direction is round(off/3)*3, so the person is always a multiple of 3 sectors from the searched centre. Covering the 1 or 2 sectors around the heard centre can never contain sector 0, so hours 1 to 5 must give identical find chances. With the true bearing spread across the wedge (my rebuild: 40 sectors, every true sector averaged), find chance rises with every sector and an independent target table is hit within 0.007. E32's refutation of E31 does not stand. · session_01CGJM5fLtaFfLbkADKJ7DJt (brain train audit disappearance)
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E42 · incompatible · sandboxes/2026-10-11__target-pinned-to-a-bin-centre-fakes-a-step.py · observed RESULT: PASS 3/3 predictions held; pinned H1-3 0.294/0.294/0.294; averaged 0.098->0.536 strictly rising True; edge H1 0.000 H2 0.285 · session_01CGJM5fLtaFfLbkADKJ7DJt (brain train audit disappearance)

## E31 — spatial find chance is tunable per depth
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][disappearance][rescue][probability][balance]
- What: Whether the spatial find-chance model for a missing member (seven E22: hidden position plus a
  noisy call bearing) can be tuned to a designer's target find rate per depth while keeping a visible
  skill gap, which the find-chance tension listed as its main cost.
- Why built: The tension's case for a weighted roll was that it is simple and tunable; if the spatial
  model can hit a target table with two knobs, that argument goes away.
- Design: Exact, using a discretised normal for bearing noise. Ring of 24 sectors; knobs are bearing
  noise (1 to 4 sectors, capped per seven E22) and search hours (1 to 12). Targets 0.90, 0.70, 0.50,
  0.35 for depths 0 to 3; noise may not fall with depth; skill gap at least 0.20.
- Got right: All four targets are hit within 0.017 (0.904, 0.683, 0.495, 0.356), every depth keeps a
  large skill gap (0.738 down to 0.272), and difficulty rises through noise (1.50, 1.50, 2.25, 3.25)
  with search hours fixed at 2 from depth 1 on.
- Where/why it failed: My first run reported the opposite (noise stuck at 4 everywhere, a target
  missed by 0.057). That was a sandbox bug, not a finding: its tie-break preferred the noisiest
  setting. After fixing the selection rule, all four predictions held, so the earlier failure is
  recorded here, not as evidence.
- Fix: Tune the spatial model with two knobs, noise rising with depth under the cap and hours set
  once, and check every new target against the skill-gap floor. Choose the least noise that hits the
  target, never the most.
- Why this fix: It keeps the feel of skill at every depth while giving the designer the same direct
  control a weighted roll offers, so the tension's cost argument for dice does not hold here.
- Rule of thumb: A spatial find-chance for a missing member is as tunable as a weighted roll: two
  knobs (bearing noise rising with depth under a cap, search hours) hit a 0.90 to 0.35 target table
  within 0.017 with a skill gap of at least 0.27; tune for the least noise that hits each target.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 4/4
  predictions held after a selection-bug fix described above; numbers copied from the fixed run). The
  target table is my example, not SEVEN's.
- Composed: pappydapimp69__seven/E22, pappydapimp69__seven/E25, ideas:GAME-DESIGN/disappearance/call-without-a-name
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__spatial-find-chance-is-tunable-per-depth.py
- Prediction: all four targets within 0.05; skill gap at least 0.20 everywhere; noise rises with depth;
  the deepest target needs fewer search hours than depth 0.
- Observed: RESULT: PASS 4/4 predictions held; d0 s1.50 h4 p0.904 gap0.738; d1 s1.50 h2 p0.683
  gap0.599; d2 s2.25 h2 p0.495 gap0.412; d3 s3.25 h2 p0.356 gap0.272
- Scenarios: 1) depth 0 target 0.90; 2) depth 1 target 0.70; 3) depth 2 target 0.50; 4) built to BREAK
  the claim: depth 3 target 0.35 under the noise cap with the gap floor.
- Link: session; Seven docs/IDEAS.md "Disappearance and return"; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E32 · incompatible · sandboxes/2026-10-11__find-chance-tuning-survives-8-direction-hearing.py · observed RESULT: FAIL 3/4 predictions held; worst miss at 8 points 0.207; total hours 24pt 10 vs 8pt 14. Probe at noise 4: hours 1-5 all 0.293, hour 6 0.742. · session; Seven docs/IDEAS.md "Disappearance and return"; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-11 · pass · sandboxes/2026-10-11__rebuild-seven-e31-tunable-on-grid.py · observed RESULT: PASS 3/3 predictions held; t0.85 s5 K12 p0.852; t0.6 s10 K14 p0.622; t0.4 s10 K8 p0.389; t0.25 s10 K6 p0.298; checks [True, True, True] · Rebuilt on a different map shape (17x17 grid, bearing-only call with no distance) with my own targets 0.85/0.60/0.40/0.25, sigma 5-60 deg under a 60 deg cap, search effort 2-40 cells, and E31's least-noise selection. All targets hit within 0.05 (0.852, 0.622, 0.389, 0.298; the last at 0.048) with gaps of at least 0.276. Caveat: difficulty came almost entirely from search effort (12 to 6 cells) with noise only 5 to 10 deg, so E31's 'difficulty rises through noise, hours fixed' is a property of its ring, not the tunability claim itself. · session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E38 · incompatible · sandboxes/2026-10-11__centred-heard-wedge-search-has-no-step.py · observed RESULT: FAIL 1/3 predictions held; sigma6.5 H1-4 0.060/0.119/0.179/0.236; worst target miss 0.007 · session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Audited: 2026-10-11 · pass · Read the entry and its stored sandbox. Find chance is computed exactly from a discretised normal over a 24-sector ring with the person at sector 0, skilled search ordered by distance to the heard sector, naive H/24. The selection rule (least error rounded to 0.01, then least noise, then larger gap) is stated and its earlier bug is disclosed. Targets, gaps and noise rising are all outputs, not inputs. The model is coarse (one ring, person fixed), but my rebuild on a 2D grid also hit an independent target table within 0.05, so the tunability claim is supported. Caveat: on the grid, difficulty came mostly from search effort, not noise. · session_01CGJM5fLtaFfLbkADKJ7DJt (brain train audit disappearance)
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E42 · incompatible · sandboxes/2026-10-11__target-pinned-to-a-bin-centre-fakes-a-step.py · observed RESULT: PASS 3/3 predictions held; pinned H1-3 0.294/0.294/0.294; averaged 0.098->0.536 strictly rising True; edge H1 0.000 H2 0.285 · session_01CGJM5fLtaFfLbkADKJ7DJt (brain train audit disappearance)
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E44 · compatible · sandboxes/2026-10-11__rescue-near-miss-share-falls-with-depth.py · observed RESULT: FAIL 2/4; near-miss share 0.397/0.349/0.236/0.157; per search 0.038/0.111/0.119/0.101 · session; brain train auto pass 1 (kernel); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E47 · compatible · sandboxes/2026-10-11__search-theory-failed-search-moves-probability-not-removes-it.py · observed RESULT: FAIL 2/4; s1.5/pod0.5: rep 0.694 bay 0.737 over 0.500; s1.5/pod0.98: rep 0.794 bay 0.991 over 0.980; s3.25/pod0.5: rep 0.400 bay 0.506 over 0.466; s3.25/pod0.98: rep 0.457 bay 0.914 over 0.914 · session; brain train newdomain (SEARCH-THEORY seed); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E50 · compatible · sandboxes/2026-10-11__search-effort-spreads-by-water-filling-not-all-on-the-likeliest-spot.py · observed RESULT: PASS 4/4; s0.6/h1.0: c 0.416 o 0.416 n1; s1.5/h8.0: c 0.261 u 0.722 o 0.782 n7; s3.25/h8.0: c 0.122 u 0.416 o 0.557 n11 · session; brain train auto run 2 pass 5 (gap, SEARCH-THEORY); session_01NHKVhTvCnvtvZ2NGLSPYj6

## E30 — rescue window on feet abandons by accident
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][abandonment][rescue][missing][disappearance]
- What: Where a spatial rescue window for a missing member is measured from: the CAMP (only a camp move
  can abandon), the player's FEET (walking two areas ahead abandons), or where the lead SLEEPS. Tested
  over every four-day plan of stay, scout one area, scout two areas, or move camp.
- Why built: The open tension on the rescue window asks how abandonment becomes a felt choice with no
  prompt. Following the feet seemed more visceral; following the camp seemed fairer but like admin.
- Design: Exact enumeration of all 256 four-day plans, equally weighted. The missing member is in the
  camp's area; at two areas ahead they are lost. An abandonment on a camp-move day counts as
  deliberate, on any other day as accidental.
- Got right: The camp rule abandons only on deliberate moves (0 accidental, at least 2 camp moves
  before any loss), and the sleep rule, as long as the lead never sleeps out, gives exactly the same
  result, so the window can be stated diegetically as where you sleep.
- Where/why it failed: The feet rule abandons in 225 of 256 plans, and 0.844 of those losses happen on
  a scouting day, not a move. Almost every abandonment under it is an accident the player made while
  looking ahead, which is the opposite of a felt choice.
- Fix: Measure the window from where the lead sleeps (the camp, unless they sleep out). Scouting ahead
  stays free; the abandoning act is the dawn camp move, which in blueprint 0.35 is already a
  deliberate, costly, hour-taking decision.
- Why this fix: A choice can only be felt if the player made it, and the camp move is the one action
  the design already makes heavy (dismantle, carry, rebuild). It keeps no prompt and no accident.
- Rule of thumb: Measure a spatial rescue window for a missing member from where the lead sleeps, not
  where their feet go: in the toy model 0.844 of feet-rule abandonments happened while scouting, while
  the camp or sleep rule abandoned only on deliberate camp moves.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 5/5
  predictions held; numbers above copied from the run). The four day options and the two-area
  window are my reading of the design note.
- Composed: pappydapimp69__seven/E27, ideas:GAME-DESIGN/rescue/abandonment-by-progress, ideas:GAME-DESIGN/disappearance/call-without-a-name
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__rescue-window-on-feet-abandons-by-accident.py
- Prediction: feet-rule accidental share at least 0.40; camp rule 0; camp rule needs at least 2 moves;
  feet rule abandons in more plans; sleep rule equals camp rule.
- Observed: RESULT: PASS 5/5 predictions held; feet lost 225/256 accidental 0.844; camp lost 67/256
  accidental 0
- Scenarios: 1) camp rule; 2) feet rule; 3) built to BREAK the claim: sleep rule, which would differ
  from the camp rule if the reasoning were wrong.
- Link: session; Seven docs/IDEAS.md "Disappearance and return"; docs/blueprint-0.35-camp-tasks-and-time.md; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E34 · compatible · sandboxes/2026-10-11__time-limit-usually-abandons-before-the-camp-move.py · observed RESULT: PASS 4/4 predictions held; base time-first 0.534; sleepout space-first 0.860; accidental 0/0 · session; Seven docs/blueprint-0.35-camp-tasks-and-time.md; owner decision 2026-10-11 on the fade; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-11 · pass · sandboxes/2026-10-11__rebuild-seven-e30-window-plan-weights.py · observed RESULT: PASS 3/3 predictions held; feet accidental share uniform 0.965, cautious 0.980, explorer 0.982, mover 0.476; camp accidental 0 in all · Rebuilt with 6-day plans, five actions (stay, scout 1/2/3, move), a 3-area loss distance, and four non-uniform player profiles (uniform, cautious, explorer, mover) instead of equal plan weights. Camp/sleep rule: 0 accidental losses under every profile (true by construction, since only a move changes the camp). Feet rule: accidental share 0.965 / 0.980 / 0.982, and 0.476 for a mover who rarely scouts far; it also loses more plans in every profile. Plan weights change the size (0.476 to 0.98) but not the conclusion. · session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Audited: 2026-10-11 · pass · Read the entry and its stored sandbox. The feet-rule accidental share (0.844) is genuinely computed by exact enumeration of 256 plans. Two checks cannot fail by construction: the camp rule's 0 accidental losses (only a move changes the camp) and its 'break case' that the sleep rule equals the camp rule (sleeping out is not in the action set, so the two rules are the same code path). Plans are equally weighted; my rebuild with four non-uniform player profiles found the feet rule's accidental share stays at least 0.476, so the conclusion survives the weighting. Pass on the computed claim, but the break case does not test anything. · session_01CGJM5fLtaFfLbkADKJ7DJt (brain train audit disappearance)
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E51 · compatible · sandboxes/2026-10-11__abandonment-felt-dismantle-call.py · observed RESULT: PASS camp-down call on the dawn bearing: posterior 0.9-0.995, informed 0.775, in 3/3; alone it is weak (0.46-0.69); fk=0 announces; fk=1 alone says nothing. Numbers: C 0.930/0.971/0.915, false alarm 0.0146-0.0179; B 0.455/0.690. · seven-1.0.0 session 2026-10-11, commit 4ecc609; session_01XbmpbLd4QyYTiQBBzo2Hdw

## E29 — expose first holds the fake longer
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][doppelganger][replacement][rescue][disappearance]
- What: Expose-first versus rescue-narrows (the rescued member returns beside the doppelganger) scored
  on how long the fake stays at the fire, because SEVEN's rule says holding a fake raises the chance of
  losing another member.
- Why built: The rescue-ordering tension leaned to the duplicate rule on real-back rate alone; holding
  time is the cost that compounds, so it is the second axis the fork needed.
- Design: Exact fractions. Two-night window, six-night horizon, an unresolved fake is held to the
  horizon. Expose-first: one pylon test per night, accuracy 0.45 then 0.55. Rescue-narrows: search
  finds with 0.6 per night, the 1-of-2 pick uses seven E26's derived 0.633 and a wrong pick is fixed by
  the second pylon. Each fake-held night adds 0.10 chance of another loss.
- Got right: Rescue-narrows holds the fake less (2.040 vs 2.540 nights), causes fewer knock-on losses
  (0.204 vs 0.254) and spends fewer pylons (1.148 vs 1.550), so it wins on every axis measured.
- Where/why it failed: The margin is smaller than I predicted: 1.245x, not 1.3x or more. Both rules
  hold a fake over 2 nights on average because a missed window parks the fake until the horizon, so
  the window miss, not the ordering, dominates holding time.
- Fix: Keep rescue-narrows, and attack holding time at the window miss: after the window closes,
  expose-by-pylon must still be available as a fallback so an abandoned member's fake is not held for
  the rest of the run by default.
- Why this fix: The ordering decision is settled by all three axes; the remaining cost sits in a case
  neither ordering touches, so the fallback is where the next pylon should go.
- Rule of thumb: For doppelganger rescue ordering, let the rescue narrow the question rather than
  gating it on exposure, and keep a pylon fallback after a missed window: in the toy model the missed
  window, not the ordering, is what keeps a fake at the fire longest.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 3/4
  predictions held; numbers above copied from the run). The accuracies, window, horizon and knock-on
  rate are my design choices.
- Composed: pappydapimp69__seven/E24, pappydapimp69__seven/E26, ideas:GAME-DESIGN/doppelganger/rescue-returns-a-duplicate, ideas:GAME-DESIGN/deduction/question-budget
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__expose-first-holds-the-fake-longer.py
- Prediction: expose-first holds the fake at least 1.3x longer; more knock-on losses; more pylons; the
  duplicate rule still holds a fake over 1.5 nights.
- Observed: RESULT: FAIL 3/4 predictions held; held A 2.540 B 2.040 ratio 1.245; pylons A 1.550 B 1.148
- Scenarios: 1) expose-first; 2) rescue-narrows; 3) built to BREAK the claim: whether rescue-narrows
  still holds the fake over 1.5 nights (it does, 2.040).
- Link: session; Seven docs/IDEAS.md "Acting on a conclusion"; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E33 · compatible · sandboxes/2026-10-11__pylon-fallback-after-missed-window-competes-with-depth.py · observed RESULT: FAIL 3/4 predictions held; held 0/2/3 tests 2.040/1.727/1.688; pylons 1.148/1.396; cut 0.153 · session; Seven docs/blueprint-0.35-camp-tasks-and-time.md (pylons per area); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-11 · fail · sandboxes/2026-10-11__rebuild-seven-e29-holding-time.py · observed RESULT: FAIL 1/4 predictions held; A held 1.949 B held 2.992 (h5 2.493); miss share 0.445; pylons A 1.949 B 1.141 · Rebuilt with a party of 4, 3-night window, 8-night horizon, search 0.45, derived accuracies, and expose-first allowed to keep testing by elimination after the window (one pylon per night until exposed). The ranking flips: expose-first holds the fake 1.949 nights vs 2.992 for rescue-narrows (2.493 even at a 5-night horizon), because elimination guarantees exposure within 4 nights while a missed rescue window parks the fake to the horizon (missed-window share 0.445). Rescue-narrows still spends fewer pylons (1.141 vs 1.949). E29's ranking on holding time depends on capping expose-first's tests at the window; on the pylon axis it holds. · session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E39 · incompatible · sandboxes/2026-10-11__expose-first-holding-depends-on-test-cap.py · observed RESULT: FAIL 1/4 predictions held; A held 1.949 B held 2.992 (h5 2.493); miss share 0.445; pylons A 1.949 B 1.141 · session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Audited: 2026-10-11 · fail · Read the entry and its stored sandbox. The ranking is built into an asymmetric setup: expose-first (A) gets exactly two pylon tests (0.45, then 0.55) and is then held to the 6-night horizon, while rescue-narrows (B) uses the same 6-night tail only after a missed window. A is not allowed to keep testing by elimination after the window, which is what decides holding time: my rebuild with elimination allowed found A holds 1.949 nights vs B's 2.992. The arithmetic is correct for the setup it states, but the conclusion that rescue-narrows holds the fake less comes from the two-test cap, which the rule does not mention. Pylons do favour B, as computed. · session_01CGJM5fLtaFfLbkADKJ7DJt (brain train audit disappearance)

## E28 — answering a fading call stops paying by itself
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][disappearance][missing][rescue][probability]
- What: Whether going out after an unnamed night call is worth it, once the woods make false calls
  (seven E23) and, by the owner's decision, the real call fades to silence with no floor (seven E27).
- Why built: The night-call tension's open worry was that false calls might teach players to stop
  answering calls at all; the owner's fade decision changes how fast real calls become rare.
- Design: Exact arithmetic. Value of answering = P(real given a call) times find chance 0.9 minus the
  risk of the night out (0.15 or 0.30 member-equivalents). Missing prior 0.15, false-call rate 0.106
  (posterior 0.6 on the first night), real call 0.9 times 0.6 per night missing.
- Got right: A first-night call is clearly worth answering even at high risk (+0.240 at 0.30), and the
  value runs out on its own: positive through night 3 at risk 0.15 and through night 2 at 0.30, with
  the posterior down to 0.163 by night 4. The fade plus false calls ends rescue attempts at a natural
  point, which matches the owner's choice of a time limit.
- Where/why it failed: Nothing in the run refuted the predictions, but the stopping point is entirely
  set by the night risk, which SEVEN has not numbered yet (blueprint 0.35 lists it as open). At a
  higher risk the window in which answering pays shrinks to two nights.
- Fix: Treat the night risk number as the knob for how long players keep answering calls, and set it
  together with the fade, not separately. Keep the first night clearly worth answering.
- Why this fix: The player's rational stopping point becomes a property of two visible pressures
  (calls getting rarer, nights being dangerous), so stopping feels like their judgement, not a rule.
- Rule of thumb: With false calls and a fading real call, answering a missing member's night call
  pays on the first nights and stops paying on its own (night 3 at risk 0.15 in the toy model), so
  tune the night risk together with the fade; it alone sets when players give up the rescue.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 4/4
  predictions held; numbers above copied from the run). The risk values and prior are my design
  choices; the false-call rate and fade come from seven E23 and E27.
- Composed: pappydapimp69__seven/E23, pappydapimp69__seven/E27, pappydapimp69__seven/E22, ideas:GAME-DESIGN/disappearance/call-without-a-name
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__answering-a-fading-call-stops-paying-by-itself.py
- Prediction: night 0 worth answering at risk 0.30; at risk 0.15 still worth it through night 2 and not
  by night 4; posterior under 0.25 by night 4.
- Observed: RESULT: PASS 4/4 predictions held; posterior n0 0.600 n2 0.350 n4 0.163; last worth
  answering at risk 0.15: night 3, at 0.30: night 2
- Scenarios: 1) risk 0.15 over 7 nights; 2) risk 0.30 over 7 nights; 3) built to BREAK the claim:
  whether answering stops paying before night 4 at low risk.
- Link: session; Seven docs/blueprint-0.35-camp-tasks-and-time.md (night risk numbers open); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E35 · compatible · sandboxes/2026-10-11__waiting-for-a-second-call-trades-rescues-for-safety.py · observed RESULT: PASS 4/4 predictions held; rescue first 0.952 wait 0.505; wasted first 0.636 wait 0.021; efficiency ratio 3.49 · session; Seven docs/IDEAS.md "Disappearance and return"; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-11 · fail · sandboxes/2026-10-11__rebuild-seven-e28-fading-call-history.py · observed RESULT: FAIL 2/3 predictions held; last-pays night memoryless 6, repeated 2, returning 2, fresh 0; max posterior gap vs memoryless 0.419 · Rebuilt with prior 0.20, call 0.85 x 0.65^k, false calls 0.12, find 0.85, risk 0.20, and exact Bayes over the player's actual HISTORY instead of E28's fixed prior with a known night k (the player knows neither). The stopping night swings with history: memoryless E28-style math pays through night 6 here, a player who heard a call every night and failed each search stops after night 2, a returning call after silence stops after night 2, and a first call after silent nights pays only on night 0 (posterior 0.159 by night 1). Max posterior gap vs memoryless 0.419. So the fade plus false calls do not set one natural stopping point; the history does, and E28's per-night formula overstates late-night value. My own P1 (memoryless negative by night 3) failed in this fixture because calls here union with false calls. · session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E37 · incompatible · sandboxes/2026-10-11__call-stopping-point-is-set-by-history.py · observed RESULT: FAIL 2/3 predictions held; last-pays night memoryless 6, repeated 2, returning 2, fresh 0; max posterior gap vs memoryless 0.419 · session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Audited: 2026-10-11 · fail · Read the entry and its stored sandbox. It is a 40-line closed form: post(n) = c_n M / (c_n M + F(1-M)) with c_n = 0.9 x 0.6^n. That conditions on the player knowing n (nights since an unannounced disappearance) and re-uses the fixed 0.15 prior every night, ignoring calls already heard, failed searches and silences. The 'stops paying by itself at a natural point' conclusion is therefore built in by the decaying c_n, not tested. My rebuild with exact Bayes over histories found the last night that pays ranges from 0 to 6 depending on what the player has heard. The rule overclaims what this model covers. · session_01CGJM5fLtaFfLbkADKJ7DJt (brain train audit disappearance)
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E77 · compatible · sandboxes/2026-10-12__fade-to-silence-ends-hopeless-searches-at-small-rescue-cost.py · observed RESULT: FAIL 2/3; shallow: rescue 0.814/0.942 late 0.034/0.205; deep: rescue 0.206/0.337 late 0.136/1.286; hopeless: rescue 0.044/0.077 late 0.163/1.647 (fade/floor) · session; fair test of the owner's fade decision, 2026-10-12; session_01NHKVhTvCnvtvZ2NGLSPYj6

## E27 — fading rescue call decay needs a floor and constant draws
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][disappearance][rescue][determinism][missing]
- What: The fading night call that seven E22 prescribes for a missing member (the call weakens each night
  missing so delay costs information) combined with the loot-pity decay lesson and the constant roll
  count rule, to check what a per-night multiplier and its night step do to rescue and to seed purity.
- Why built: E22 said the call must fade, but did not say how. A plain multiplier is the obvious code,
  and loot-pity E1 says uniform multiplicative decay with no floor converges to zero; the waiting-city
  E17 lesson says a forced branch that skips a roll desyncs everything drawn after it.
- Design: Call chance 0.9 times 0.6 per night missing, with and without a floor of 0.25; the chance of
  hearing at least one call over a 2-night window is computed exactly. A scripted counting generator
  counts draws in a naive night step (roll drift, call and bearing only when someone is missing and
  not found) against one that always draws three.
- Got right: The floor keeps the call alive (0.438 chance of hearing it over two nights, at any night),
  and the always-three night step draws 3/3/3 across nobody missing, someone missing and someone found,
  so a resumed run cannot fork on who happens to be out on the map.
- Where/why it failed: Unfloored, the call falls below 0.05 by night 6 (0.042), and the two-night hear
  chance drops to 0.066: the missing member goes silent from time alone, which quietly adds a TIME
  rescue window on top of the spatial one the design asked for. The naive night step draws 0/3/0, so
  the seed stream depends on whether anyone is missing, the exact desync shape of waiting-city E17.
- Fix: Floor the fading call (here 0.25) so it fades but never ends while the person is inside the
  spatial window; end it only when the window closes. Draw drift, call and bearing every night for
  every slot unconditionally and use the values conditionally.
- Why this fix: The floor keeps one abandonment rule (space) instead of two (space plus a hidden
  clock), and the constant draws keep the run a pure function of its seed, which SEVEN's save
  discipline depends on; both cost nothing in feel.
- Rule of thumb: A rescue call that fades by a per-night multiplier for a missing member needs a floor,
  or it decays to silence and adds a hidden time window on top of the spatial one; and its night step
  must draw drift, call and bearing for every slot every night, or who is missing decides the seed stream.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 5/5
  predictions held; numbers above copied from the run). The 0.9, 0.6 and 0.25 values are my design
  choices; the decay and draw-count structure is what the run shows.
- Composed: pappydapimp69__seven/E22, local__sandbox-loot-pity/E1, pappydapimp69__the-game-the-waiting-city/E17, ideas:GAME-DESIGN/rescue/abandonment-by-progress
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__fading-rescue-call-decay-needs-a-floor-and-constant-draws.py
- Prediction: unfloored call below 0.05 by night 6; floored call never under the floor; floored
  two-night hear chance at least 0.40 forever; naive draw counts vary; constant draws do not.
- Observed: RESULT: PASS 5/5 predictions held; unfloored silent at night 6; floored night-6 hear 0.438;
  naive draws [0, 3, 0] vs constant [3, 3, 3]
- Scenarios: 1) unfloored decay over 10 nights; 2) floored decay over 10 nights; 3) draw counts for
  nobody missing, someone missing, someone found; 4) built to BREAK the claim: whether the floor still
  leaves a hearable call (0.438) or merely delays silence.
- Link: session; Seven docs/IDEAS.md "Disappearance and return"; brain train pass on disappearance; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E28 · compatible · sandboxes/2026-10-11__answering-a-fading-call-stops-paying-by-itself.py · observed RESULT: PASS 4/4 predictions held; posterior n0 0.600 n2 0.350 n4 0.163; last worth answering at risk 0.15: night 3, at 0.30: night 2 · session; Seven docs/blueprint-0.35-camp-tasks-and-time.md (night risk numbers open); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E30 · compatible · sandboxes/2026-10-11__rescue-window-on-feet-abandons-by-accident.py · observed RESULT: PASS 5/5 predictions held; feet lost 225/256 accidental 0.844; camp lost 67/256 accidental 0 · session; Seven docs/IDEAS.md "Disappearance and return"; docs/blueprint-0.35-camp-tasks-and-time.md; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E34 · compatible · sandboxes/2026-10-11__time-limit-usually-abandons-before-the-camp-move.py · observed RESULT: PASS 4/4 predictions held; base time-first 0.534; sleepout space-first 0.860; accidental 0/0 · session; Seven docs/blueprint-0.35-camp-tasks-and-time.md; owner decision 2026-10-11 on the fade; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E35 · compatible · sandboxes/2026-10-11__waiting-for-a-second-call-trades-rescues-for-safety.py · observed RESULT: PASS 4/4 predictions held; rescue first 0.952 wait 0.505; wasted first 0.636 wait 0.021; efficiency ratio 3.49 · session; Seven docs/IDEAS.md "Disappearance and return"; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-11 · pass · sandboxes/2026-10-11__rebuild-seven-e27-fade-floor-and-draws.py · observed RESULT: PASS 4/4 predictions held; unfloored n8 0.0461 hear3 0.098; floored min hear3 0.488; conditional desync True; constant in sync True · Rebuilt with call 0.8 x 0.7^n, floor 0.2, a 3-night hearing window, and a real PRNG stream: two runs from one seed that differ only in a member missing nights 2-4, comparing a downstream weather stream. Unfloored call is 0.046 by night 8 with a 3-night hear chance of 0.098 (a hidden time window), the floored hear chance never drops below 0.488, conditional draws desync the weather stream and unconditional draws keep it identical. Arithmetic is simple, but both halves hold on a different fixture. Note the owner later chose fade-to-silence, so the floor is a design option, not a defect fix. · session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E37 · incompatible · sandboxes/2026-10-11__call-stopping-point-is-set-by-history.py · observed RESULT: FAIL 2/3 predictions held; last-pays night memoryless 6, repeated 2, returning 2, fresh 0; max posterior gap vs memoryless 0.419 · session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Audited: 2026-10-11 · pass · Read the entry and its stored sandbox. The decay half is direct arithmetic on the stated multiplier and floor, computed rather than assumed. The draw-count half uses a counting LCG on two hand-written night steps; the naive step skipping draws is by construction, but a varying draw count IS the mechanism the rule names, so the check is fair rather than circular. It never shows a downstream stream actually diverging; my rebuild did (a seeded weather stream forks when a member is missing under conditional draws and stays identical under constant draws). Scope matches the rule. · session_01CGJM5fLtaFfLbkADKJ7DJt (brain train audit disappearance)
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E59 · compatible · sandboxes/2026-10-11__punishing-sanity-meter-makes-a-death-spiral.py · observed RESULT: FAIL 2/3; collapse perception 0.126 punish 0.499 (x3.97); mild 0.229 · session; brain train loop on hallucination as an art style (loop 4); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E77 · compatible · sandboxes/2026-10-12__fade-to-silence-ends-hopeless-searches-at-small-rescue-cost.py · observed RESULT: FAIL 2/3; shallow: rescue 0.814/0.942 late 0.034/0.205; deep: rescue 0.206/0.337 late 0.136/1.286; hopeless: rescue 0.044/0.077 late 0.163/1.647 (fade/floor) · session; fair test of the owner's fade decision, 2026-10-12; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__sevin.md#E7 · compatible · no sandbox · Sevin commit f813ed7; session_0125c7UeqZXhwxqnu8spbVdh
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E95 · compatible · sandboxes/2026-10-12__fade-with-a-lasting-cue-keeps-most-rescues.py · observed RESULT: FAIL hopeless late nights 2.450->0.000; shallow cost 0.0288; deep cost 0.126; fade+cue deep 0.413 (floor 0.465, fade 0.339), hopeless late 1.470 · session_01P1LRA5HjMLEFnWXayE2EHx; review pass of SEVEN targets, gap lessons, 2026-10-12

## E26 — duplicate at fire needs both asked and diffing only locates
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][doppelganger][replacement][deduction][rescue]
- What: Seven E24's duplicate-at-the-fire rule (the rescued member comes back while the doppelganger is
  still there, and the player picks 1-of-2, assumed 0.80 accurate) checked against the two deduction
  kernels: question-budget (fewer questions than suspects, or comparing answers replaces memory) and
  derived-vs-authored-tells (the fake's account is the real log with one fact bent).
- Why built: E24's 0.80 accuracy was assumed, not derived, and the question-budget kernel seemed to say
  a two-person scene with two questions would collapse into mechanical diffing.
- Design: Exact fractions. A day has 6 facts; the fake bends one; a question covers 2; memory recalls a
  fact with 0.8 and is never wrongly sure. Budget 1 asks one of the two; budget 2 asks both the same
  question. Break case: three at the fire with one fake and full budget, solved by majority with no
  memory at all. Rule C pylon spend recomputed with the derived accuracy.
- Got right: With two at the fire, comparing answers only LOCATES the bent fact; it never says which
  version is true, so memory stays the evidence (with no memory, budget 2 is exactly 0.5). Asking both
  doubles the edge over a coin (0.633 vs 0.567). With three, comparison alone beats a guess (0.556 vs
  0.333), which is the case the question-budget kernel actually guards.
- Where/why it failed: E24's assumed 0.80 is too high: derived accuracy is 0.633, so the duplicate scene
  is closer to a coin than claimed and pylon spend rises from 1.200 to 1.367 per rescue. My prediction
  that it would pass 1.5 was refuted: rule C stays affordable, but less than E24 suggested.
- Fix: Give the duplicate scene a budget of two (ask both the same question) and raise coverage, not
  the budget: questions about the shared hours just before the disappearance, when the fake's bent fact
  is most likely to sit. Scope the question-budget rule to casts of three or more.
- Why this fix: It keeps the scene about memory, which is the design's only evidence, while giving the
  player enough signal that the pylon choice is not a coin-flip; and it stops a two-person scene being
  starved by a rule that only matters when a majority exists.
- Rule of thumb: When a rescued member returns beside their doppelganger, let the player ask both the
  same question: with two, comparing answers only locates the bent fact and memory still decides (the
  question-budget rule matters only from three suspects, where a majority answers without memory).
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 4/5
  predictions held; numbers above copied from the run). Facts per day, coverage and memory recall are
  my design choices; the 2x edge and the M=0 result are exact properties of the model.
- Composed: pappydapimp69__seven/E24, ideas:GAME-DESIGN/deduction/question-budget, ideas:GAME-DESIGN/deduction/derived-vs-authored-tells, ideas:GAME-DESIGN/doppelganger/rescue-returns-a-duplicate
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__duplicate-at-fire-needs-both-asked-and-diffing-only-locates.py
- Prediction: budget 2 edge exactly twice budget 1; derived accuracy under 0.80; no memory gives 0.5 at
  budget 2; three at the fire solved above 0.5 by comparison alone; rule C pylons rise above 1.5.
- Observed: RESULT: FAIL 4/5 predictions held; budget1 0.567 budget2 0.633 cast3-no-memory 0.556; rule
  C pylons 1.367. Missed: pylon spend stayed under 1.5.
- Scenarios: 1) two at the fire, one question; 2) two at the fire, both asked; 3) memory set to zero;
  4) built to BREAK the claim: three at the fire, full budget, no memory.
- Link: session; Seven docs/IDEAS.md "Investigation" and "Acting on a conclusion"; brain train pass on disappearance; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E29 · compatible · sandboxes/2026-10-11__expose-first-holds-the-fake-longer.py · observed RESULT: FAIL 3/4 predictions held; held A 2.540 B 2.040 ratio 1.245; pylons A 1.550 B 1.148 · session; Seven docs/IDEAS.md "Acting on a conclusion"; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E33 · compatible · sandboxes/2026-10-11__pylon-fallback-after-missed-window-competes-with-depth.py · observed RESULT: FAIL 3/4 predictions held; held 0/2/3 tests 2.040/1.727/1.688; pylons 1.148/1.396; cut 0.153 · session; Seven docs/blueprint-0.35-camp-tasks-and-time.md (pylons per area); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-11 · fail · sandboxes/2026-10-11__rebuild-seven-e26-duplicate-question-budget.py · observed RESULT: FAIL 4/5 predictions held; ask-one(optimal) 0.6312 ask-both 0.6312 edge ratio 1.00; wrong-sure ratio 1.23; three no-memory 0.583 · Rebuilt with 8 binary facts of unknown true value, 3 covered per question, recall 0.7, and a Bayes-optimal player who uses EVERYTHING observed. Ask-both reproduces E26's formula exactly (0.631). But asking ONE person, read optimally, is also 0.631: when the asked answer matches memory, that match is evidence the asked one is real (the fake only matches when the bent fact is uncovered or forgotten), so the edge ratio is 1.00, not 2.0. E26's 'asking both doubles the edge' comes from discarding the evidence in a match. Asking both helps only when memory can be wrongly sure (w=0.1: 0.594 vs 0.576). The no-memory 0.5 and the 3-at-fire majority (0.583 > 1/3) hold. My first run had a fixture bug (all true values 0, so an answer alone revealed the fake); fixed before reading results as evidence. · session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E40 · incompatible · sandboxes/2026-10-11__one-answer-read-by-bayes-matches-asking-both.py · observed RESULT: FAIL 4/5 predictions held; ask-one(optimal) 0.6312 ask-both 0.6312 edge ratio 1.00; wrong-sure ratio 1.23; three no-memory 0.583 · session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Audited: 2026-10-11 · fail · Read the entry and its stored sandbox. The headline (asking both doubles the edge over asking one) is built into hand-written formulas, not computed from a model of what the player observes. acc_budget1 says 'otherwise nothing learned -> coin': when the asked person's answer matches memory, the code throws that evidence away. With the same constants (6 facts, 2 covered, recall 0.8, never wrongly sure), reading a match as evidence gives budget 1 = 0.633, equal to budget 2, so the check 'edge exactly 2x' only holds because of the discarded evidence. The no-memory 0.5 and the three-at-fire majority are computed correctly; the rule's 'let the player ask both' is not supported by this sandbox. · session_01CGJM5fLtaFfLbkADKJ7DJt (brain train audit disappearance)

## E25 — call bearing tell must be sized to perceivable resolution
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][disappearance][missing][rescue][probability]
- What: Seven E23's learnable tell (two night calls from a consistent bearing mean a real missing member,
  not a false call) checked against how the player actually hears direction, using mirage E19 (size a
  tell to the resolution of what shows it) and missing-laughter E1 (silence is only evidence against an
  established baseline) for what the end of the calls means for abandonment.
- Why built: E23 measured consistency on 24 internal sectors, but a player hears a voice as roughly one
  of 8 directions at best. And the abandonment fork needs silence to mean something, which the
  missing-laughter lesson says depends on the call rate the player has learned.
- Design: Exact enumeration with fractions. Real second calls are offset from the first by a fixed
  kernel of 0 to 3 sectors; false calls are two uniform bearings. Consistency is same or adjacent
  perceived direction (same only for 4 quadrants). Silence: a missing member inside the window calls at
  0.9 or 0.3 per night, outside the window never; posterior of abandonment after 1 to 3 silent nights.
- Got right: Heard at 8 directions, the tell weakens as predicted: false pairs look consistent 0.375
  of the time and the likelihood ratio drops from 5.00 to 2.67. Silence works as a signal only with a
  strong call: at 0.9, one silent night is 0.909 sure the person is beyond reach.
- Where/why it failed: My prediction that coarser hearing always weakens the tell was REFUTED: 4
  quadrants with a same-direction rule gave a ratio of 3.17, better than 8 points with an adjacent rule.
  What sets the strength is the WIDTH of the consistency rule on the circle, not the resolution. And with
  a weak or floored call (0.3), three silent nights only reach 0.745, so silence cannot announce
  abandonment once the call is allowed to fade.
- Fix: Define the consistency tell in units the player hears (8 directions at most), and keep its
  window narrow, same direction or one step at most. Do not use silence alone as the abandonment signal
  with a fading call; give the closing window a world cue as well (the camp move itself, the last
  call heard from behind the camp).
- Why this fix: It keeps the tell readable without a HUD, and it stops the design depending on a
  silence the player cannot distinguish from a quiet night once calls are weak.
- Rule of thumb: A direction tell for a missing member's call must be sized in the units the player can
  hear (8 directions at most) and kept narrow, since rule width not resolution sets its strength; and
  silence only signals abandonment when the call was strong, so a fading rescue call needs a second cue.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 4/5
  predictions held; numbers above copied from the run). The offset kernel and call rates are my design
  choices; the exact fractions are what the enumeration gives.
- Composed: pappydapimp69__seven/E23, pappydapimp69__mirage/E19, local__sandbox-missing-laughter-needs-the-response-window/E1, ideas:GAME-DESIGN/disappearance/call-without-a-name
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__call-bearing-tell-must-be-sized-to-perceivable-resolution.py
- Prediction: the ratio falls from 24 sectors to 8 points; false pairs look consistent at least 0.35 at
  8 points; at 4 quadrants the ratio is under 1.5; at call rate 0.9 one silent night is at least 0.85
  sure; at 0.3 three silent nights stay under 0.80.
- Observed: RESULT: FAIL 4/5 predictions held; LR 24=5.00 8=2.67 4=3.17; silence c0.9 k1=0.909, c0.3
  k3=0.745. Missed: the 4-quadrant ratio was 3.17, not under 1.5.
- Scenarios: 1) 24-sector hearing; 2) 8-direction hearing; 3) built to BREAK the claim: 4-quadrant
  hearing with a stricter rule (it broke it); 4) silence at call rate 0.9; 5) silence at call rate 0.3.
- Link: session; Seven docs/IDEAS.md "Disappearance and return"; brain train pass on disappearance; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E31 · compatible · sandboxes/2026-10-11__spatial-find-chance-is-tunable-per-depth.py · observed RESULT: PASS 4/4 predictions held; d0 s1.50 h4 p0.904 gap0.738; d1 s1.50 h2 p0.683 gap0.599; d2 s2.25 h2 p0.495 gap0.412; d3 s3.25 h2 p0.356 gap0.272 · session; Seven docs/IDEAS.md "Disappearance and return"; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E32 · incompatible · sandboxes/2026-10-11__find-chance-tuning-survives-8-direction-hearing.py · observed RESULT: FAIL 3/4 predictions held; worst miss at 8 points 0.207; total hours 24pt 10 vs 8pt 14. Probe at noise 4: hours 1-5 all 0.293, hour 6 0.742. · session; Seven docs/IDEAS.md "Disappearance and return"; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E35 · compatible · sandboxes/2026-10-11__waiting-for-a-second-call-trades-rescues-for-safety.py · observed RESULT: PASS 4/4 predictions held; rescue first 0.952 wait 0.505; wasted first 0.636 wait 0.021; efficiency ratio 3.49 · session; Seven docs/IDEAS.md "Disappearance and return"; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-11 · pass · sandboxes/2026-10-11__rebuild-seven-e25-rule-width-vs-resolution.py · observed RESULT: PASS 4/4 predictions held; equal-f LR spread 0.000 (f=3/8) 0.110 (f=1/8); R8 k0 5.37 vs k1 2.67; silence c0.9 n2 0.977, c0.3 n3 0.555 · Rebuilt with 72 internal sectors, a triangular +-40 deg offset kernel, heard resolutions 24/12/8/6/4 and rule widths k, and a 0.3 (not 0.5) prior for silence. At equal false-consistency rate the LR is identical across resolutions (2.67 at f=3/8 for 24/k4 and 8/k1) or within 11% (f=1/8: 5.96 vs 5.37), and narrowing the rule at 8 points doubles the LR (5.37 vs 2.67), so width, not resolution, sets strength. Silence: c=0.9 two silent nights give 0.977, c=0.3 three nights only 0.555. Caveat: one silent night at c=0.9 gives only 0.811 at prior 0.3, so E25's 0.909 is prior-bound. · session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E38 · incompatible · sandboxes/2026-10-11__centred-heard-wedge-search-has-no-step.py · observed RESULT: FAIL 1/3 predictions held; sigma6.5 H1-4 0.060/0.119/0.179/0.236; worst target miss 0.007 · session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Audited: 2026-10-11 · pass · Read the entry and its stored sandbox. It computes everything by exact enumeration: consistency rates for real pairs (fixed offset kernel) and uniform false pairs at 24, 8 and 4 heard directions, and silence posteriors by Bayes. The surprise result (4 quadrants with a same-direction rule beats 8 points with an adjacent rule) is genuinely computed, and it supports the rule's 'width, not resolution' claim, which my independent rebuild confirmed at equal false-consistency rates. Caveats: the silence numbers use a hard-coded 0.5 prior (at 0.3 one silent night at c=0.9 gives 0.811, not 0.909), and perceive() floors to a bin edge rather than rounding to a centre, which does not change the conclusion. · session_01CGJM5fLtaFfLbkADKJ7DJt (brain train audit disappearance)
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E51 · compatible · sandboxes/2026-10-11__abandonment-felt-dismantle-call.py · observed RESULT: PASS camp-down call on the dawn bearing: posterior 0.9-0.995, informed 0.775, in 3/3; alone it is weak (0.46-0.69); fk=0 announces; fk=1 alone says nothing. Numbers: C 0.930/0.971/0.915, false alarm 0.0146-0.0179; B 0.455/0.690. · seven-1.0.0 session 2026-10-11, commit 4ecc609; session_01XbmpbLd4QyYTiQBBzo2Hdw

## E24 — rescue exposes the fake two at the fire
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][disappearance][replacement][doppelganger][rescue]
- What: Ordering of exposure and rescue when a missing member has been replaced by a same-name,
  same-skill doppelganger: (A) expose the fake by pylon before a search is possible, (B) a successful
  rescue makes the fake vanish for free, (C) a rescue brings a SECOND person with the same name to the
  fire, and the player must still pick which one to test.
- Why built: SEVEN's open fork asks whether the fake must be exposed before the real person can be
  rescued. Rule A gates rescue on a 1-of-N deduction; rule B lets rescue skip the investigation layer
  entirely; both looked plausible on paper.
- Design: Toy model: party of 4 at the fire, 2-night spatial window, search finds with 0.6 per night, a
  pylon test costs a day of the window, 2 pylons, deduction accuracy 0.45 for 1-of-4 and 0.80 for 1-of-2.
  Measured real-back rate, pylons spent, and deduction share (resolved cases decided by a player choice).
  Game references (secondary research, not checked first-hand): The Thing (2002) blood tests,
  That's Not My Neighbor's cleaning protocol cost on a false positive.
- Got right: Rule C keeps rescue as strong as rule B (0.844 vs 0.841 real back) while every resolution
  still runs through a player deduction (share 1.0 vs 0.0 for B), and spends about one pylon per rescue
  (1.014), so the rescue becomes the best evidence the player can earn rather than a bypass.
- Where/why it failed: Rule A collapses: only 0.274 of missing members come back while burning 1.546
  pylons, because a 1-of-4 deduction eats the window that the search needed. Rule B is generous but
  turns rescue into a free identity oracle, so the investigation verb stops mattering whenever the
  player can search.
- Fix: Use rule C (two at the fire): rescue never requires exposure first, and rescue never resolves
  identity by itself; it narrows the question from 1-of-N to 1-of-2 and the pylon still decides it.
- Why this fix: It keeps all three costs the design depends on (night hours to search, a pylon to act,
  memory to choose) while removing the dead-end where a wrong early guess also kills the rescue window.
  It also produces the strongest scene available to the genre: two people with the same name at the fire.
- Rule of thumb: In doppelganger or replacement mechanics, never gate rescue of the missing person on
  first exposing the fake (the 1-of-N deduction eats the rescue window), and never let rescue expose the
  fake for free (it bypasses the investigation); bring the real one back as a duplicate so rescue turns
  the question into a cheaper 1-of-2 choice the player still has to pay for.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT PASS 5/5
  predictions held; numbers above copied from the run). The accuracies, window and search rate are my
  design choices, so the ranking is structural and the exact rates are not tuned for SEVEN.
- Composed: N/A
- Sandbox: sandboxes/2026-10-11__rescue-exposes-the-fake-two-at-the-fire.py
- Prediction: A lowest real-back rate; B deduction share under 0.30; C real-back within 0.05 of B; C
  deduction share at least 0.50; C spends under 1.5 pylons on average.
- Observed: RESULT: PASS 5/5 predictions held; A back=0.274 pylons=1.546 ded=1.000; B back=0.841
  pylons=0.000 ded=0.000; C back=0.844 pylons=1.014 ded=1.000
- Scenarios: 1) rule A expose-first; 2) rule B rescue-exposes; 3) rule C two-at-fire; 4) built to BREAK
  the claim: C's pylon drain, checked against a 1.5 per-rescue ceiling.
- Link: session; Seven docs/IDEAS.md "Acting on a conclusion"; docs/blueprint-0.35-camp-tasks-and-time.md; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E26 · compatible · sandboxes/2026-10-11__duplicate-at-fire-needs-both-asked-and-diffing-only-locates.py · observed RESULT: FAIL 4/5 predictions held; budget1 0.567 budget2 0.633 cast3-no-memory 0.556; rule C pylons 1.367. Missed: pylon spend stayed under 1.5. · session; Seven docs/IDEAS.md "Investigation" and "Acting on a conclusion"; brain train pass on disappearance; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E29 · compatible · sandboxes/2026-10-11__expose-first-holds-the-fake-longer.py · observed RESULT: FAIL 3/4 predictions held; held A 2.540 B 2.040 ratio 1.245; pylons A 1.550 B 1.148 · session; Seven docs/IDEAS.md "Acting on a conclusion"; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-11 · pass · sandboxes/2026-10-11__rebuild-seven-e24-rescue-ordering.py · observed RESULT: PASS 5/5 predictions held; A back 0.398 B/C back 0.875; C pylons/rescue 1.369; A pylons 2.311; A dusk-test back 0.875 · Rebuilt with a party of 5, a 3-night window, search 0.5, and DERIVED pick accuracies (1-of-n from a skill formula, 1-of-2 from a fact/memory model: 0.631, not the assumed 0.80). Expose-first collapses (0.398 back, 2.311 pylons), two-at-the-fire equals rescue-exposes on real-back (0.875) and spends 1.369 pylons per rescue. Caveats: C's real-back equal to B and its deduction share of 1.0 are true by construction, and the break arm shows the collapse of A is entirely the time cost of a test: with a dusk test that does not use the night, A's real-back is 0.875 too. So the rule holds only where exposure spends rescue time, which its parenthetical already states. · session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E40 · incompatible · sandboxes/2026-10-11__one-answer-read-by-bayes-matches-asking-both.py · observed RESULT: FAIL 4/5 predictions held; ask-one(optimal) 0.6312 ask-both 0.6312 edge ratio 1.00; wrong-sure ratio 1.23; three no-memory 0.583 · session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Audited: 2026-10-11 · modeled · Read the entry and its stored sandbox. Only one of its findings is computed: rule A's collapse (0.274 back), which comes from each pylon test using up a window night. The rest is built in: rule C runs the identical search loop as B so their real-back rates match by construction, B's deduction share is hard-coded 0 and C's 1, and C's pylon spend under 1.5 follows from the ASSUMED 1-of-2 accuracy of 0.80 (q + 2(1-q) < 1.5 iff q > 0.5). The claim is about how players experience doppelganger mechanics, tested on a hand-built toy with authored accuracies, so the honest verdict is modeled; the rebuild showed the A collapse disappears if a test does not cost a night. · session_01CGJM5fLtaFfLbkADKJ7DJt (brain train audit disappearance)
- Cited-by: 2026-10-12 · projects/pappydapimp69__sevin.md#E13 · compatible · no sandbox · Sevin commits 2bd39d4, 4567c72; session_0125c7UeqZXhwxqnu8spbVdh

## E23 — night call is an announcement unless false calls exist
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][disappearance][missing][deception][probability]
- What: An unnamed night call from a missing party member, meant to guide a rescue search without saying
  who is calling, checked for how much it leaks: whether hearing a call already announces that a
  disappearance happened and that a replacement sits at the fire.
- Why built: SEVEN's disappearance is unannounced; the tell is supposed to be that nobody at the fire
  finds anything strange. But if only the missing ever call, a call at night is a notification with
  extra steps, and the count of calls tells the player how many fakes there are.
- Design: Prior 0.15 that someone is missing on a given night; a missing member calls with 0.9; the
  woods also make false calls at rate F. Posterior P(missing | call) and wasted search nights per real
  one were computed for F = 0 to 0.25. A skill path was simulated: real calls come from a stable bearing,
  false ones from a random bearing, and two calls on consecutive nights within 3 of 24 sectors count as
  consistent. Folklore and game references (secondary research, not checked first-hand): voices in the
  woods that must not be answered; Lethal Company's mimic voices exist only in mods.
- Got right: Calls only stay ambiguous if false calls exist: at F = 0.10 one call gives a posterior of
  0.614 and at F = 0.15 it gives 0.514. Consistency across nights is a real, learnable tell: real pairs
  look consistent 0.749 of the time against 0.293 for false pairs, lifting the posterior to 0.741.
- Where/why it failed: With F = 0 a call is certain proof (posterior 1.000), so the unannounced design
  leaks through the rescue cue. Ambiguity is not free: holding the posterior near 0.6 needs F of at least
  0.106, which costs about 0.63 wasted search nights per real rescue, and my prediction that consistency
  would lift the posterior to 0.85 was refuted (0.741), so a call never becomes proof on its own.
- Fix: Run a baseline of false calls in the woods that does not depend on anyone being missing (scaled by
  depth, like the hallucination), make real calls come from a stable bearing that drifts slowly, and let
  bearing consistency across nights be the tell the player learns. Never put a name in the call.
- Why this fix: It keeps the call useful for the search and keeps the disappearance unannounced; the
  price is wasted night hours, which is the currency the design already wants the player to spend
  outside, so the cost lands on the right axis.
- Rule of thumb: An unnamed call from a missing person still announces the disappearance if only the
  missing ever call; add false calls that do not depend on anyone missing (about 0.1 per night at a 0.15
  missing prior keeps a call near 0.6 sure) and make cross-night bearing consistency, never the voice or
  a name, the learnable tell.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 4/5
  predictions held; numbers above copied from the run). The call, missing and drift rates are my
  design choices, so the posteriors are structural and not tuned for SEVEN.
- Composed: N/A
- Sandbox: sandboxes/2026-10-11__night-call-is-an-announcement-unless-false-calls-exist.py
- Prediction: F = 0 gives posterior 1.0; F needed for a posterior at or below 0.6 is at least 0.10; at that
  F, wasted searches per real at least 0.6; a consistent pair lifts the F = 0.15 posterior to at least 0.85;
  false pairs look consistent under 0.35 of the time.
- Observed: RESULT: FAIL 4/5 predictions held; F for 0.6 = 0.106; one call 0.514, consistent pair 0.741.
- Scenarios: 1) F swept 0, 0.05, 0.10, 0.15, 0.25; 2) consistent-pair rates for real vs false calls;
  3) built to BREAK the claim: whether consistency turns a call into proof (it did not, 0.741).
- Link: session; Seven docs/IDEAS.md "Disappearance and return"; docs/blueprint-0.35-camp-tasks-and-time.md; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E25 · compatible · sandboxes/2026-10-11__call-bearing-tell-must-be-sized-to-perceivable-resolution.py · observed RESULT: FAIL 4/5 predictions held; LR 24=5.00 8=2.67 4=3.17; silence c0.9 k1=0.909, c0.3 k3=0.745. Missed: the 4-quadrant ratio was 3.17, not under 1.5. · session; Seven docs/IDEAS.md "Disappearance and return"; brain train pass on disappearance; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E28 · compatible · sandboxes/2026-10-11__answering-a-fading-call-stops-paying-by-itself.py · observed RESULT: PASS 4/4 predictions held; posterior n0 0.600 n2 0.350 n4 0.163; last worth answering at risk 0.15: night 3, at 0.30: night 2 · session; Seven docs/blueprint-0.35-camp-tasks-and-time.md (night risk numbers open); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E35 · compatible · sandboxes/2026-10-11__waiting-for-a-second-call-trades-rescues-for-safety.py · observed RESULT: PASS 4/4 predictions held; rescue first 0.952 wait 0.505; wasted first 0.636 wait 0.021; efficiency ratio 3.49 · session; Seven docs/IDEAS.md "Disappearance and return"; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-11 · fail · sandboxes/2026-10-11__rebuild-seven-e23-false-calls-and-consistency.py · observed RESULT: FAIL 4/5 predictions held; F* 0.156; pair post 0.943; real pair 0.927 vs false 0.375; 3-night LR true 6.20 vs indep 6.11 · Rebuilt with prior 0.25, call rate 0.7, 8 heard directions and a stable true bearing plus per-call Gaussian noise (so pairs share a bearing and are correlated, unlike E23's drifting bearing and 3-of-24 window). The false-call half holds exactly: F=0 gives proof, and the F that holds a call at 0.6 follows prior*c*(1/0.6-1)/(1-prior), here 0.156, so 'about 0.1' only holds at E23's 0.15 prior. The consistency half breaks: real pairs are consistent 0.927 vs 0.375 for false, and a consistent pair lifts the posterior to 0.943, so consistency DOES make a call near-proof with a stable bearing; E23's 0.741 depended on its drift and window. Treating pairs as independent barely matters (3-night LR 6.20 correlated vs 6.11 independent). · session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E37 · incompatible · sandboxes/2026-10-11__call-stopping-point-is-set-by-history.py · observed RESULT: FAIL 2/3 predictions held; last-pays night memoryless 6, repeated 2, returning 2, fresh 0; max posterior gap vs memoryless 0.419 · session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Audited: 2026-10-11 · fail · Read the entry and its stored sandbox. The posterior after a consistent pair is computed with the prior SQUARED: prior_pair_real = (C*M)**2 and prior_pair_false = (F*(1-M))**2, i.e. M^2 C^2 vs (1-M)^2 F^2, when two calls on one hypothesis are M C^2 vs (1-M) F^2. Re-running the stored code with only that line corrected (same seed, real-consistent 0.749, false 0.293) gives two calls 0.864 and a consistent pair 0.942, not 0.741. So the entry's 'refuted' prediction (consistency lifts the posterior to at least 0.85) actually HELD, and its 'a call never becomes proof on its own' conclusion is an artifact of the bug. The single-call false-rate part (F about 0.106 for 0.6) is computed correctly. · session_01CGJM5fLtaFfLbkADKJ7DJt (brain train audit disappearance)
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E43 · incompatible · sandboxes/2026-10-11__two-observation-bayes-applies-the-prior-once.py · observed RESULT: PASS 4/4 predictions held; E23 pair correct 0.942 buggy 0.741 · session_01CGJM5fLtaFfLbkADKJ7DJt (brain train audit disappearance)
- Cited-by: 2026-10-12 · projects/pappydapimp69__sevin.md#E5 · incompatible · sandboxes/2026-10-12__day-keyed-false-whistle-leaks-on-the-second-night.py · observed RESULT: FAIL 3/5 predictions held; S1 single 0.346 pair 0.957; stable pair 0.792 off-dir 1.000; episodes pair 0.652 vs 0.500; break(4 dirs,F .5) pair 0.858; exact 0.930 vs doubled 0.732 · session; brain train loop round 2; session_01QGT1LfmPHPG99JEGaPhBwB

## E22 — disappearance search chance from hidden position not dice
- Date: 2026-10-11
- Project: Pappydapimp69/seven
- Tags: [gamedesign][disappearance][rescue][missing][probability]
- What: Rescue search for a missing party member (disappearance mechanic) modelled two ways: a dice roll
  p(nights out, depth, same night) versus a hidden position on the map plus a noisy, unnamed night-call
  bearing that the player searches toward for a fixed number of hours.
- Why built: SEVEN's design says the find-chance is weighted by things the player controlled (nights out,
  depth, same-night search). An independent roll makes those weights invisible: the player only ever sees
  success or failure, which reads as a coin-flip (secondary research: Sid Meier's GDC 2010 talk on players
  rejecting displayed odds; Frostpunk players reloading over scout deaths).
- Design: Ring of 24 sectors; the missing person drifts by a random walk each night out; the call bearing
  carries Gaussian noise that grows with depth; a search covers 4 sectors. Skilled policy searches nearest
  the heard bearing, naive policy searches at random. Dice model uses the same factors as multipliers.
  Metric: skill gap = find rate skilled minus naive.
- Got right: The spatial model gives a large, readable skill gap where the call is clear (0.767 same-night
  at shallow depth: 0.938 skilled vs 0.171 naive), while the dice model's gap is exactly 0 everywhere, so
  only the spatial version can ever read as skill. Depth weighting falls out of call noise for free.
- Where/why it failed: Two things broke. (1) My prediction that find rate falls with nights out was
  REFUTED: 0.94/0.93/0.93/0.93 over 0-3 nights, because each night's call reports where the person is NOW,
  so drift is cancelled by fresh information. (2) Depth noise collapses skill fast: the gap is 0.230 at
  depth 1, 0.070 at depth 2 and 0.015 at depth 3, i.e. a coin-flip in the deep woods.
- Fix: Put the nights-out penalty INTO the call, not the position: the call gets fainter or rarer each
  night out (or stops), so delay costs information instead of a hidden multiplier. Cap bearing noise at
  about 4 of 24 sectors so even the deepest search keeps a visible skill gap, and push the remaining
  depth difficulty into search time (fewer sectors per night) rather than into pure noise.
- Why this fix: The weights the design wants (delay hurts, depth hurts, same-night is best) survive, but
  each one now acts on something the player perceives and can act on, so a failed search has a cause the
  player can name. A multiplier on a roll gives the same averages with no learnable cause.
- Rule of thumb: For disappearance and rescue searches, derive find-chance from a hidden position plus an
  unnamed but informative cue (a call bearing), never from a dice roll: the cue must degrade with delay
  (fainter calls each night missing) because a fresh cue erases drift, and its noise must be capped or
  deep searches silently become coin-flips.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (RESULT FAIL 4/5
  predictions held; numbers above copied from the run). The constants (24 sectors, 4 hours, noise per
  depth) are my design choices, so the result is about structure, not tuning.
- Composed: N/A
- Sandbox: sandboxes/2026-10-11__disappearance-search-chance-from-hidden-position-not-dice.py
- Prediction: dice skill gap 0; spatial gap at least 0.30 at night 0 depth 0; skilled find rate falls
  with nights out; deepest noise drops the gap below 0.10; same-night shallow skilled at least 0.75.
- Observed: RESULT: FAIL 4/5 predictions held; spatial gap n0d0=0.767, n0d3=0.015; dice gap 0. Missed:
  nights-out decline (0.94/0.93/0.93/0.93).
- Scenarios: 1) dice vs spatial at 16 nights-by-depth cells; 2) skilled vs naive policy; 3) built to BREAK
  the claim: depth 3 call noise, where skill collapses to 0.015.
- Link: session; Seven docs/IDEAS.md "Disappearance and return"; docs/blueprint-0.35-camp-tasks-and-time.md; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E27 · compatible · sandboxes/2026-10-11__fading-rescue-call-decay-needs-a-floor-and-constant-draws.py · observed RESULT: PASS 5/5 predictions held; unfloored silent at night 6; floored night-6 hear 0.438; naive draws [0, 3, 0] vs constant [3, 3, 3] · session; Seven docs/IDEAS.md "Disappearance and return"; brain train pass on disappearance; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E28 · compatible · sandboxes/2026-10-11__answering-a-fading-call-stops-paying-by-itself.py · observed RESULT: PASS 4/4 predictions held; posterior n0 0.600 n2 0.350 n4 0.163; last worth answering at risk 0.15: night 3, at 0.30: night 2 · session; Seven docs/blueprint-0.35-camp-tasks-and-time.md (night risk numbers open); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E31 · compatible · sandboxes/2026-10-11__spatial-find-chance-is-tunable-per-depth.py · observed RESULT: PASS 4/4 predictions held; d0 s1.50 h4 p0.904 gap0.738; d1 s1.50 h2 p0.683 gap0.599; d2 s2.25 h2 p0.495 gap0.412; d3 s3.25 h2 p0.356 gap0.272 · session; Seven docs/IDEAS.md "Disappearance and return"; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E32 · incompatible · sandboxes/2026-10-11__find-chance-tuning-survives-8-direction-hearing.py · observed RESULT: FAIL 3/4 predictions held; worst miss at 8 points 0.207; total hours 24pt 10 vs 8pt 14. Probe at noise 4: hours 1-5 all 0.293, hour 6 0.742. · session; Seven docs/IDEAS.md "Disappearance and return"; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E33 · compatible · sandboxes/2026-10-11__pylon-fallback-after-missed-window-competes-with-depth.py · observed RESULT: FAIL 3/4 predictions held; held 0/2/3 tests 2.040/1.727/1.688; pylons 1.148/1.396; cut 0.153 · session; Seven docs/blueprint-0.35-camp-tasks-and-time.md (pylons per area); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Audited: 2026-10-11 · fail · Read the entry and its stored sandbox. (1) The headline contrast is built in, not computed: the dice model ignores the policy argument by construction, so its skill gap of exactly 0 is an assumption restated as a result; the spatial gap is genuinely computed from a random-walk position and noisy bearing. (2) The Rule of thumb claims the cue must degrade with delay and that noise must be capped near 4 of 24 sectors, but the sandbox never runs a fainter-with-delay cue or any noise cap; it only shows that a fresh cue cancels drift and that sigma 10 collapses the gap, so the prescriptive half of the rule is untested. It also never tries a dice model whose odds depend on player choices, so never use a dice roll is broader than what was shown. (3) The motivation, that players read dice as coin-flips, rests on cited talks, not on anything modeled. The spatial numbers (gap 0.767 at n0 d0, 0.015 at n0 d3) look sound as a toy result, so the entry should be narrowed rather than discarded. · brain train auto loop 1 pass 3 (audit); session_012QzNKQEGhirAziWZ2Cg9Tj
- Reverified: 2026-10-11 · fail · sandboxes/2026-10-11__rebuild-seven-e22-grid-search-chance.py · observed RESULT: FAIL 4/5 predictions held; gap s10 0.573 s60 0.065 s120 0.011; nights 0.631->0.623; heavy-tail gap 0.399; checks [True, True, False, True, True] · Rebuilt from the claim only on a different map shape (17x17 grid, bearing-only call with no distance, so the searched set is a wedge, not ring sectors) and a second noise model (30% echo calls from a random bearing). The structure survives: skill gap 0.573 at sigma 10 deg, a fresh call cancels four nights of random-walk drift (0.631 to 0.623), and heavy-tailed noise still leaves a 0.399 gap. But the prescriptive half fails: the rule's cap of about 4 of 24 sectors (60 deg) leaves a gap of only 0.065 on a 2D map, already a coin-flip by the rule's own standard. The cap value is a property of the ring model, not of the mechanic, so the rule should say: find the cap on the real map, do not reuse 4/24. · session_01CGJM5fLtaFfLbkADKJ7DJt (blind rebuild of seven E22-E36)
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E44 · compatible · sandboxes/2026-10-11__rescue-near-miss-share-falls-with-depth.py · observed RESULT: FAIL 2/4; near-miss share 0.397/0.349/0.236/0.157; per search 0.038/0.111/0.119/0.101 · session; brain train auto pass 1 (kernel); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E47 · compatible · sandboxes/2026-10-11__search-theory-failed-search-moves-probability-not-removes-it.py · observed RESULT: FAIL 2/4; s1.5/pod0.5: rep 0.694 bay 0.737 over 0.500; s1.5/pod0.98: rep 0.794 bay 0.991 over 0.980; s3.25/pod0.5: rep 0.400 bay 0.506 over 0.466; s3.25/pod0.98: rep 0.457 bay 0.914 over 0.914 · session; brain train newdomain (SEARCH-THEORY seed); session_01NHKVhTvCnvtvZ2NGLSPYj6

## E21 — tutorial props must not be spendable
- Date: 2026-10-10
- Project: Pappydapimp69/Seven
- Tags: [gamedev][onboarding][softlock]
- What: In the walk-in tutorial the player picks up a flare and a tether, crafts them into an ember, then hands it to a named person. Pressing use on any carried item spent the only thing the next step needed, and the lesson could not finish.
- Why built: Each tutorial step pins to a specific object so progress means a real demonstration. The side effect is that the objects are also ordinary game items with ordinary verbs, so every verb that consumes them is a way out of the lesson.
- Design: While the ground, craft and hands steps are active, use and drop are refused with a short hold-on line, and give is refused until the hands step, where it is also refused for anyone but the step's named person. The guard sits at the top of the single action handler so it reads as one list.
- Got right: One guard at the dispatch point covers touch buttons, keys and pad alike. The browser tutorial test now tries use, drop, give and the wrong recipient and asserts the inventory is unchanged.
- Where/why it failed: Completion gates were checked for starvation by the earlier tutorial design, but nothing checked that the items could be destroyed. The soft lock only appeared when a real player pressed the use key on a prop.
- Fix: Refuse the consuming verbs while a prop is load-bearing, with feedback, rather than letting them run and trying to repair the lesson afterwards by respawning items.
- Why this fix: Respawning props needs a second code path per step and teaches the wrong thing; refusing the verb removes the failure class and the message tells the player what to do instead.
- Rule of thumb: In a guided tutorial, list every verb that can consume, drop or give away the object a later step needs, and refuse those verbs until that step is done.
- Provenance (verified/assumed): First-hand. Reproduced the consumption in a browser probe with the guard disabled (the flare vanished), restored it (all three verbs left the item in hand), and confirmed the full seven-step walkthrough still completes.
- Link: Seven commits b45a527 and fb6c602 (branch ccr-77663fb4-3d4vnd); session_01XbmpbLd4QyYTiQBBzo2Hdw
- Cited-by: 2026-10-17 · projects/pappydapimp69__demo-disc.md#E51 · compatible · no sandbox · https://claude.ai/code/session_0189x5cwDWHdyFUT5WmrVCJq, Demo-disc commit 9859c0a

## E20 — fact from state not from indistinguishable event
- Date: 2026-10-10
- Project: Pappydapimp69/Seven
- Tags: [gamedev][history][deception]
- What: Seven records a structured history of the day (who did what, who was close by, who answered a call) that a fake later lies about. The call verb emits an event, and the first plan was to write the "answered" fact from that event.
- Why built: The whole investigation rests on a truthful history existing for a fake to bend by one fact. Facts therefore have to be true even when the player-facing event is built to be uninformative.
- Design: The call event is emitted with identical text whether or not the companion answers, on purpose, so the sound and line are never a tell. The fact is instead read off the world at record time: only a companion whose summon-by is the caller and whose summon-until is still in the future answered.
- Got right: Recording from world state kept the player-facing event indistinguishable while the history stayed true. A browser probe showed one call fact for the summoned companion and none for a ignored call, and a test pins that nearby and camp facts read real positions.
- Where/why it failed: Recording from the event would have written an "answered" fact for every call, including calls nobody heard, so the history would contain true-looking lies and a real fake could be caught or missed by accident.
- Fix: In the event handler, look the companion up and check the summon fields before recording; record nothing otherwise. Neighbours and camp stayers likewise come from positions, via small pure helpers that are tested without a browser.
- Why this fix: An event that is deliberately the same in every branch carries no information, so any fact derived from it is only as true as the guess. World state is the single source that already encodes what really happened.
- Rule of thumb: When a verb's event is built to look identical across outcomes, never derive history from the event; derive it from the state the outcome changed.
- Provenance (verified/assumed): First-hand. Verified in a headless browser run (call fact present for the summoned companion, camp facts written at nightfall) and in pure tests; the account-text test fails when the neighbour field is dropped from the stored fact.
- Link: Seven commit 6f46388 (branch ccr-77663fb4-3d4vnd); session_01XbmpbLd4QyYTiQBBzo2Hdw
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E89 · incompatible · sandboxes/2026-10-12__rebuilt-witness-list-forks-a-fakes-lie-across-reload.py · observed RESULT: FAIL 8/10; changed verbatim 0.000 reorder 0.797 drop 0.395; minhash reorder 0.000 drop 0.208; sorted reorder 0.000 drop 0.395; resume+draws constant True · session; brain train loop round 3; session_01QGT1LfmPHPG99JEGaPhBwB

## E19 — diagnostic ratio of same unit is always one
- Date: 2026-10-10
- Project: Pappydapimp69/Seven
- Tags: [gamedev][debugging][display]
- What: A player reported that walking forward leaned about 18 degrees and the picture looked stretched. The sim and camera agreed exactly in every test, so a Tab-key readout was added to print raw input, walked direction against view, canvas sizes, pixel ratio and zoom.
- Why built: Reading code and running headless checks could not show what the player's machine was reporting, and arguing from the model had already failed twice. A readout turns the report into numbers the player can photograph.
- Design: The overlay prints the raw input lean, the yaw, the direction actually walked relative to the camera, raw pad axes, css and buffer canvas sizes, aspect ratios, the device pixel ratio and window sizes. It reads input and display facts only, never any hidden meter.
- Got right: The first photo of the readout showed input lean 0 and walked-versus-view 0, which cleanly separated the game from the display. It also exposed an unexpected 2.05 pixel ratio and a 1280 by 800 screen.
- Where/why it failed: The first version estimated browser zoom as outer window width over inner window width. Both are in css pixels, so the ratio is about one hundred percent whatever the zoom, and it told the player zoom was off when it was on.
- Fix: Replace the estimate with screen width times pixel ratio, printed beside the note that it should equal the real resolution; a larger number means zoom is on.
- Why this fix: A real zoom signal needs two quantities in different units. Comparing a css size with a device-pixel size is the only version that can differ from one.
- Rule of thumb: Before shipping a diagnostic ratio, check the two quantities are in different units; a ratio of two values in the same unit prints a constant and misleads the person reading it.
- Provenance (verified/assumed): First-hand. The player's photo of the corrected readout agreed with the stated screen size, and the headless run of the new line printed the expected product; the faulty line was the one I wrote and replaced.
- Link: Seven commits 51f90a6 and 725a3a5 (branch ccr-77663fb4-3d4vnd); session_01XbmpbLd4QyYTiQBBzo2Hdw

## E18 — instructions name the button in hand
- Date: 2026-09-25
- Project: Pappydapimp69/Seven
- Tags: [ui][input][tutorial][testing]
- What: A game with keyboard, gamepad and touch schemes had a scheme-aware bottom legend, but tutorial briefs named no keys ("Pick IREN out on the roster, then hand it to her"), the legend's verb had no object ("LB/RB select"), and the action prompt's key was a CSS `::after { content: "[E]" }` constant shown on every controller. Reported from a real playtest on a pad projected on a wall.
- Why built: The legend was the only scheme-aware text, so every other instruction was either keyboard-only or key-less, and a tutorial is exactly where the player has no other way to learn a binding.
- Design: One pure table of button NAMES per scheme (keys.js), separate from the bindings in input.js. Instructions carry {tokens} filled at DISPLAY time; the raw text is kept so a controller change repaints the banner. The action prompt key comes from a data attribute via `attr(data-key)`. Legend verbs say what they act on ("pick a teammate on the roster").
- Got right: A test that parses input.js and checks each name in the table is actually bound to the action the instruction claims, so a rebinding cannot leave a brief naming the old button; and a control where one name is `undefined`, which exposed that `t in table` passed while the screen would print the word "undefined".
- Where/why it failed: Two older tutorial guards read the RAW brief strings; after tokenising they needed to check the text as shown per scheme. The legend was scheme-aware and still failed the player, because it listed a verb with no object.
- Fix: Tokenised briefs, a names table, repaint on scheme change, per-scheme checks in both the pure tier and a fake-pad browser test (negative-controlled by pinning substitution to keyboard: both assertions failed).
- Why this fix: Resolving at display time is the only point that knows the current scheme; resolving at authoring time freezes whichever controller the player started on.
- Rule of thumb: Every instruction that says "press" must name the button in the player's CURRENT hand and what it acts on — test the names against the real bindings, and grep CSS for key glyphs, because a hard-coded [E] in `content:` escapes every JS audit.
- Provenance (verified/assumed): Verified first-hand in SEVEN 0.26.1: pure tests/keys.mjs (5 guards, 7 negative controls, each read for its reason), tests/gamepad.mjs with a fake pad showed the banner switch from "Q/R ... B" to "LB/RB ... D-pad Right" and the prompt key from E to A. Open, and outside what this entry claims: whether players read the longer briefs; only the one playtest report motivates it.
- Composed: N/A
- Link: Pappydapimp69/Seven main, seven-0.26.1

## E17 — webgl readback needs the loops camera
- Date: 2026-09-25
- Project: Pappydapimp69/Seven
- Tags: [testing][rendering][browser][verification]
- What: A browser test that reads a WebGL frame back to judge whether something is VISIBLE (five weathers must look different on screen). It calls `renderer.render(scene, camera)` then `gl.readPixels` inside one `page.evaluate`, which returns the real frame without `preserveDrawingBuffer`.
- Why built: A look table and a source-text check can both be green while the scene draws the same thing for every value; only pixels say whether the player can tell the values apart.
- Design: Move the player, wait two rAFs so the page's own loop runs its per-frame update (camera rig, fog, uniforms), then render and read back in one evaluate. Signature = mean colour in three horizontal bands plus the mean absolute difference between two samples 400ms apart (motion). Every pair must differ by a threshold.
- Got right: Reading back inside the same task as the render call; comparing a signature that includes motion, because wind and rain are movement and a single still frame undersells them.
- Where/why it failed: The first probe moved the player and rendered immediately, in the same evaluate. `render()` draws with whatever pose the loop's LAST `update()` left on the camera, so all five weathers returned the same uniform brown frame from the stale pose — which reads exactly like "the weather does not draw". Separately, inserting the rAF wait in the middle of a section timed off the wall clock (a nightfall overlay) let the overlay run out and broke three unrelated assertions downstream.
- Fix: Await two rAFs between changing state and sampling, so the loop applies the state to the camera and scene first. Put any rAF-waiting scene read AFTER sections that depend on wall-clock timing, not inside them.
- Why this fix: The loop's `update()` is the only writer of the camera and per-frame scene state; calling it by hand from the test would duplicate its argument plumbing (percept, view, viewport) and test a path the player never runs.
- Rule of thumb: A readback judges the frame the LOOP last composed, not the state you just set — let the loop draw before you read, and never let a wait for frames sit inside a timed sequence.
- Provenance (verified/assumed): Verified first-hand in SEVEN's tests/woods-play.mjs under headless Chromium with SwiftShader: stale-pose probe gave identical frames for all five weathers; after the rAF wait, pairwise distances were 28-69 in mean RGB; unbinding the weather in render.js drove all ten pairs to 0.0. The overlay breakage was reproduced once and fixed by moving the block. Open, and outside what this entry claims: whether the same holds on hardware GL, where readback timing differs.
- Composed: N/A
- Link: Pappydapimp69/Seven branch claude/brain-install-vohzag, seven-0.26.0

## E16 — negative controls live in the test file
- Date: 2026-09-25
- Project: Pappydapimp69/Seven
- Tags: [testing][verification][process]
- What: A readability guard per perturbation kind (six kinds a false account can bend), where each guard is a function that takes the thing it watches as an argument, and the same file feeds every guard a copy broken the way that axis was or would be broken, requiring it to fail.
- Why built: mirage#E16 says to negative-control every guard, but a control done once by hand is unmeasured the moment the guard is edited; and a control can itself be wrong in a way that makes a live guard look inert.
- Design: Guards return a list of problems, not a boolean. Real inputs are one object; each control spreads it and overrides one field (the look table with drizzle aliased to clear, a render source with the binding removed, a work function whose emit drops the actor's name). Controls are named after the historical defect ("four identical cairns", "drawn, never depicted").
- Got right: Printing each control's problem list once and reading it — every one of 18 failed for the INTENDED reason. A control that fails for an unrelated reason (a thrown error, a missing import) passes the "guard is not inert" assertion while measuring nothing.
- Where/why it failed: Nothing failed in the shipped form. The risk this addresses was observed in the same project earlier: a hand-run control that did not reproduce the defect the way it had actually occurred made a live guard read as inert.
- Fix: Make controls data, run them every suite run, and inspect their failure messages when first written.
- Why this fix: Keeps the control coupled to the guard's current code; costs milliseconds in the pure tier.
- Rule of thumb: Put the negative control in the test file as a broken INPUT to the guard, not a one-off revert — and read what it failed on, because failing for the wrong reason is indistinguishable from a working guard.
- Provenance (verified/assumed): Verified first-hand: tests/readability.mjs, 6 guards, 18 controls, each control's problem text inspected. Browser-tier guards were controlled the manual way (unbinding the weather and emptying the marks pool in render.js gave 19 failures of the expected shape). Open, and outside what this entry claims: source-text checks remain weaker than pixel checks and can be satisfied by a binding that is present but unreachable.
- Composed: mirage/E16
- Link: Pappydapimp69/Seven branch claude/brain-install-vohzag, seven-0.26.0

## E15 — a filmic curve is the wrong reach for a scene that is all shadow
- Date: 2026-09-18
- Project: Pappydapimp69/seven
- Tags: [gamedev][rendering][process]
- What: Reaching for ACES tone mapping to give a very dark 3D scene more tonal range made it measurably flatter, because a filmic curve's toe DARKENS shadows as the price of compressing highlights — and a scene with no highlights pays that price for nothing. The range the scene was missing was in the content, which was authored near-black, not in the transfer curve.
- Why built: A first-person basin at dusk read as flat cutouts rather than terrain: a stand of rock spires rendered as one silhouette with no facets, no near/far separation, and no edge between adjacent shapes.
- Design: Three.js r160, `NoToneMapping` by default with `SRGBColorSpace` output. Rock spires were `MeshStandardMaterial` at `color: 0x1b212b`, `roughness: 1`, `flatShading: true`, lit by a 1.05 hemisphere and a 0.55 directional. The obvious fix, and the one every engine defaults to, is a filmic tone curve.
- Got right: Captured screenshots on both sides of the change from a harness that fixes seed, position, yaw and sim time, so the two frames differed in nothing but the edit. Without that the change would have been judged from memory of the previous session's screenshot, which is what "looks better" usually means and is not evidence.
- Where/why it failed: ACES made it worse and the comparison said so immediately. The plain sRGB transfer function is roughly a gamma-1/2.2 lift, which raises dark values aggressively; ACES replaces that with a filmic S-curve whose toe pulls the bottom of the range DOWN before the shoulder rolls the top off. A dusk scene lives entirely in the toe. There were no highlights to buy the trade with, so it spent contrast the scene could not spare. Two separate errors compounded it: the material's `roughness: 1` means a perfectly diffuse surface with no directional response, so a rim light added at the same time had nothing to catch; and `computeVertexNormals` on a gentle heightfield gives every ground triangle nearly the same normal, so the floor lit as one tone no matter how much relief it had.
- Fix: Revert the tone curve. Lift the rock's base colour off the floor (0x1b212b to 0x39424f — same hue, same darkness register, far enough up to HAVE a lit side), drop roughness to 0.92 so an edge can exist, add a weak opposite-side rim purely for silhouette separation, give the spires per-instance colour and a few degrees of tilt from their existing cell hash, and switch the ground to flat shading so its triangles catch light differently.
- Why this fix: A tone curve redistributes the range a scene HAS; it cannot invent range a scene never generated. When every surface returns almost nothing to every light, the output is dark and flat before any curve sees it. The per-instance variation matters for the same reason at a different level — one mass in one colour reads as a repeated stamp however many instances it has, and the cheapest cure is a deterministic hash the geometry already computes for its own placement, which costs no rng draw in a sim that counts them.
- Rule of thumb: Before reaching for a tone curve, ask which part of the output range the scene actually occupies. A filmic curve trades shadow depth for highlight headroom, so it helps a scene with bright sources and hurts one that is uniformly dark — the default that every engine ships is tuned for the first. And when a render looks flat, check the three places range dies before the curve: a base colour near the floor, a roughness at exactly 1, and smooth normals over a low-relief surface. Any of the three makes lighting changes invisible, which reads as "the lighting is not working" and sends you tuning lights that were never the problem.
- Provenance (verified/assumed): Verified first-hand. ACES was implemented, shot, compared against the baseline frame, and reverted in the same session; the comment in `render.js` records the refutation so it is not re-proposed. The subsequent changes were shot the same way after each step. The full suite including the browser tier was run. Open, and outside what this entry claims: whether the result is better to a PLAYER rather than merely higher-contrast — tension T11 says the automated tier cannot answer that, and the screenshots go to a human.
- Composed: N/A
- Link: seven, src/render.js, tools/shoot.mjs, tension T11
- Cited-by: 2026-10-10 · projects/local__sandbox-kernel-cinematography-lighting-ratio.md#E1 · compatible · sandboxes/2026-10-10__lighting-ratio-stops-vs-lux-and-bounce-floor.py · observed RESULT: PASS 19/19 checks held, 1 prediction miss (P7b). Spread 0.000 L*; frozen exposure shifts 11.2 (+-1 st) and 23.2 (+-3 st); 8 stops 68.2 L* with code 5, 23.5 L* from lux reading; key:fill vs total 1.8 L*; cheek 3.39:1, azimuth range… · session_01YFLLRpDsfZpRstb2KT2MQy
- Cited-by: 2026-10-16 · projects/pappydapimp69__brainwork.md#E347 · incompatible · sandboxes/2026-10-16__filmic-toe-collapses-bayer-shadow-levels.py · observed RESULT: FAIL identity dark=5 toe dark=6 (naive passes toe=False, region passes toe=True) dark-scene levels=6 · brain train auto pass 5; session_01RbNqhLnCALyxxvjiR2t3TU

## E14 — a spacing assertion is not a distinguishability assertion
- Date: 2026-09-14
- Project: Pappydapimp69/seven
- Tags: [gamedev][gamedesign][testing][feedback]
- What: A module documented that its four locations must be distinguishable, then discharged that requirement with a test that only checked they were far APART. The renderer drew all four identically, so a whole falsification axis — one of six ways the game lies to the player about what happened — was correct in the data and invisible on screen for the entire life of the feature.
- Why built: The game asks the player to catch a false account of a day they watched. A false account can swap the PLACE a beat happened at, which only works as a test of memory if the places are things a person can tell apart.
- Design: Four authored sites, each with an id and a label, spread to four quarters of the map. `tests/woods.mjs` asserted each is open ground, reachable from spawn, and more than four site-radii from every other. The renderer's `makeSite()` took no argument: one cairn, one pole, one lamp, for all four.
- Got right: The requirement was WRITTEN DOWN, in the module that owns the sites, in the exact words that later made the gap obvious ("a wrong-place claim is only evidence if the places are distinguishable"). Without that sentence the defect would have read as a missing feature rather than an unmet stated contract. The spacing test was also genuinely necessary — it is half the contract, not a wrong idea.
- Where/why it failed: The comment named a property (distinguishable) and the test asserted a PROXY for it (far apart), and nobody re-read the two together. Spacing is necessary and not sufficient: two identical cairns eighty metres apart are still two identical cairns, and position is exactly the cue a player's memory of a busy day does not retain. The failure is invisible from either side alone — the data layer is correct (four distinct ids, four distinct labels, a working perturbation), the test layer is green, and only the rendered result is empty. Nothing in the pure tier can see a look.
- Fix: Give each site a body that depicts what its label names, keeping the shared pole-and-lamp as the separate ACTIVE-beat indicator so identity and state stay on different channels. Then assert in two tiers: the pure test holds the contract (every id has a form, no two labels collide) by reading the renderer as text, and the browser test holds the result by walking the live scene and comparing per-site geometry signatures.
- Why this fix: The two-tier split is the point. A text-level check catches the case that actually breaks silently later — someone adds a fifth site and it falls back to the generic shape — while being honest in its own comment that it proves nothing about pixels. The scene-graph check is what proves the pixels, and it is cheap: geometry type plus vertex count per child is stable across material and colour changes, so it does not become a snapshot test that fails on every tweak.
- Rule of thumb: When a comment states a required property and a test asserts a measurable proxy for it, write down which one the test is actually checking — a proxy that is necessary-but-not-sufficient will read as full coverage forever. And for anything the player must TELL APART, the assertion belongs in the tier that can see what is drawn: distinctness in the data model is not distinctness to a person, and a mechanism that discriminates correctly on a cue nobody can perceive is indistinguishable from one that does not run.
- Provenance (verified/assumed): Verified first-hand. Read `makeSite()` and confirmed it takes no argument and branches on nothing; confirmed `place` is one of six entries in `chronicle.js`'s KINDS and that `pickPerturbation` emits place swaps against real visited places. All three new guards were negative-controlled and each failed for its own reason: collapsing the factory to one shape fails the browser check naming all four as identical; deleting one body fails the contract check naming the site that would fall back; giving two sites one label fails the label check. Full suite green including the browser tier. Open, and outside what this entry claims: whether the new forms are legible to a player at speed, which needs a human at the controls rather than a geometry signature.
- Composed: N/A
- Link: seven 20d0282 (seven-0.23.0), docs/blueprint-0.23-four-places-that-look-like-places.md, src/render.js SITE_BODIES, tests/woods.mjs, tests/woods-play.mjs
- Reverified: 2026-10-11 · pass · sandboxes/2026-10-11__rebuild-seven-e14-spacing-vs-distinguishability.py · observed RESULT: PASS 4/4; spacing pass, catch same 0.000 half 0.667 distinct 1.000 · Own four sites with positions and a rendered form; a wrong-place lie is catchable only if the remembered site and the named one look different. The spacing test passes under every rendering, while the wrong-place catch rate is 0.000 with identical forms, 1.000 with four distinct forms and 0.667 with two shared forms, so a spacing proxy reads as full coverage while the distinguishability requirement can be fully unmet. Differs from the original: no renderer, a form table. · session; brain train rebuild pass on Seven-relevant Games lessons, 2026-10-11; session_01NHKVhTvCnvtvZ2NGLSPYj6

## E13 — more density bought fewer obstacles
- Date: 2026-09-12
- Project: Pappydapimp69/seven
- Tags: [procgen][gamedesign][balance]
- What: Turning up a generator's density pass produced FEWER obstacles, not more — the knob that made the map denser was consuming the raw material the obstacle-placement pass needed. It ALSO appeared to break an unrelated NPC behaviour assertion three modules away, and that second half turned out to be a broken test rather than a real interaction; both halves are kept here because the false one is the more instructive.
- Why built: A density pass was added so that a deadfall across a route would cost something to walk around. The obvious next move was to turn it up.
- Design: Density runs as N rounds of "fill a random slice of open cells, keep the round only if every feature is still inside the distance budget". Deadfalls are placed AFTER it, each needing an open three-cell run at least 8 cells from camp, 8 from any other deadfall, 2 clear of any feature, and accepted only if the map stays connected without clearing it.
- Got right: The two passes were measured separately rather than together, which is the only reason the second effect was attributable at all — running the suite with density off and deadfalls on proved deadfalls innocent of the drift regression in one run.
- Where/why it failed: Sweeping rounds at 14 / 8 / 5 (fill 0.12) landed the basin at 63% walkable and produced 3.25 deadfalls per world; 2 rounds landed at 70% and produced 3.95. More fill meant fewer open three-cell runs for the placement pass to find, so the denser map hosted FEWER obstacles — the knob bought less of exactly what it was turned up for. Separately, the density appeared to break a companion-drift assertion in a different subsystem, monotonically: a lucid-dark companion drifted 8 units from where they broke on 24 of 24 seeds with density off, 7 of 12 at one round, 5 of 12 at two. The obvious reading was that rock stops them, and it was wrong. The test positioned the companion at a computed bearing and radius WITHOUT checking the ground; inside rock there is no start cell for the pathfinder, the path is emptied and never refilled, and the character stands still scoring 0.0u. That fires at the rate a random point lands in rock, which rises with density and mimics a real map effect exactly. Corrected numbers with the spawn checked: 9 of 12 on dense ground against 11 on the open basin, bar 8.
- Fix: For the real half, nothing — the fewer-obstacles result is a measurement, and the response was to pick the round count from the sweep rather than assume more is better. For the false half, fix the harness: place on the nearest OPEN cell via a helper that throws rather than silently relocating, and add a check that runs the same episode on dense ground while asserting the ground it received is actually dense. The density pass was made opt-in while the drift claim stood; that reason is now withdrawn and the default is an open decision rather than a forced one.
- Why this fix: A sweep is cheap and the monotonicity assumption is what cost the time — the 2-round setting was found by measuring downstream, not by reasoning about fill. And a harness that silently relocates an illegal spawn would have hidden the next version of the same bug, so the helper throws.
- Rule of thumb: A generator knob that creates terrain also DESTROYS the raw material every later placement pass consumes, so measure the downstream passes across the sweep instead of assuming the effect is monotonic. And the inverse of what this entry originally concluded: when a terrain knob appears to regress a test in an unrelated subsystem, check the test's coupling to that knob BEFORE believing the interaction. A harness that places an agent at a computed point fails at a rate set by how much of the map is illegal ground, which is precisely the quantity the knob moves — so a harness bug and a real physical interaction produce the same monotonic curve. "The test is usually right" was the reasoning that filed a tension, made a generator feature opt-in, and was wrong on all counts.
- Provenance (verified/assumed): Verified first-hand, in both directions. Sweeps at 0.22/6, 0.12/14, 0.08/24 and 0.05/40 fill-per-round all land at 62-64% walkable; deadfall counts were measured at each. The drift claim was measured, believed, filed as a tension, acted on, and then REFUTED the same day by instrumenting the frozen companions directly — one goal held for 1400 ticks, path empty every tick, victim standing on a blocked cell. The corrected 9-of-12 and 11-of-12 figures come from the real suite, not a probe; an earlier probe of my own diverged from the test and its numbers were discarded rather than reported. The harness fix is negative-controlled: restore the blind spawn and the dense check fails at 5 of 12, reproducing the original "regression" exactly. Still unexplained: two dense seeds where the companion is on OPEN ground, holds one invented goal for the whole episode and travels under a unit.
- Composed: N/A
- Link: seven 6d2bfb4 (seven-0.22.0), src/world.js DENSITY_ROUNDS, tests/deadfall.mjs "the density pass spends the budget, and only when asked"
- Reverified: 2026-10-11 · pass · sandboxes/2026-10-11__rebuild-seven-e13-density-consumes-placement.py · observed RESULT: PASS 3/3; sites 625/444/291/15/15/14/8; share 1.000->0.571 · Own 25x25 grid with 2x2 wall clusters per density round; a later deadfall pass may only use open cells that are not articulation points (a deadfall must not cut the map), counted with Tarjan's algorithm rather than assumed. Legal sites fall from 625 to 8 as density rounds go 0 to 24, and the share of reachable open ground that can host a deadfall falls from 1.000 to 0.571, so the terrain knob consumes the placement pass's raw material faster than it consumes open ground. That is the claim's real half. Differs from the original: a cut-vertex rule stands in for whatever the deadfall pass consumes in SEVEN, so it shows the mechanism, not SEVEN's numbers. · session; brain train rebuild pass on Seven-relevant Games lessons, 2026-10-11; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E36 · compatible · sandboxes/2026-10-11__nearest-open-cell-is-not-legal-placement-on-dense-maps.py · observed RESULT: PASS 3/3; d0.05 open 1.000 connected 1.000; d0.25 open 0.975 connected 1.000; d0.35 open 0.865 connected 1.000; d0.40 open 0.630 connected 1.000 · session; follow-up to the 2026-10-11 rebuild review of seven E12; session_01NHKVhTvCnvtvZ2NGLSPYj6

## E12 — a test that places an agent must assert the placement is legal
- Date: 2026-09-12
- Project: Pappydapimp69/seven
- Tags: [testing][gamedev][procgen][method]
- What: A behaviour test positioned an NPC at a computed point on a procedural map without checking the point was walkable. Inside rock the pathfinder has no start cell, the path is set to the empty array and never refilled, and the character stands still — so the suite measured an agent's INABILITY TO EXIST and reported it as behaviour. Because the failure rate is just the rate at which a random point lands in rock, it scaled with map density and was misdiagnosed as a map regression that nearly cost a generator feature its default.
- Why built: The test drops one companion into a hallucinating state at a fixed distance and bearing from the lead and watches whether they wander off. A bearing and a radius is the obvious way to place them, and it reads as deterministic and harmless.
- Design: `victim.x = cos(bearing) * startDist; victim.z = sin(bearing) * startDist`, then run 70 simulated seconds and score displacement from the break point. Three separate checks read that same episode.
- Got right: The suite did have a guard on the underlying behaviour, and the guard's threshold was the thing that eventually surfaced the problem — a density pass moved the pass count from 24/24 to 7/12 to 5/12 and that drop is what got investigated. Also: the pathfinder itself was correct, and already carried the `null` means not-computed / `[]` means computed-and-none distinction that a previous lesson bought.
- Where/why it failed: Invisibly, and in the direction that hides it. A walled-in companion scores 0.0u of drift, which makes the "stays where it can be witnessed" check pass TRIVIALLY, deflates the "stays in the neighbourhood" median with zeros, and counts against the "does wander off" tally. One defect weakened three assertions and failed none of them. Then the misdiagnosis: at 78% walkable it fires on ~2 seeds in 12 and the suite's bar absorbed it; at 63% walkable it fires on ~5, the bar broke, and the obvious reading was "dense ground pens companions in". A tension was filed saying exactly that, a generator pass was made opt-in to protect the assertion, and all of it was wrong. Corrected numbers: 9 of 12 on dense ground against 11 on open, bar 8 — density costs two seeds.
- Fix: Place on the nearest OPEN cell via a helper that throws rather than silently returning rock; add a sibling check that runs the same episode on dense ground AND asserts the ground it received is actually dense; raise the departure bar from 8 to 10, which the old harness could not have met.
- Why this fix: Throwing rather than snapping-silently matters — a helper that quietly relocates would hide the next version of this. Asserting the density inside the dense-ground check matters for the same reason: swapping its flag to `false` left the check green, so the flag was doing nothing an assertion could see. Both were caught by negative control, not by review.
- Rule of thumb: Any test that PLACES an agent at a computed position must assert the position is legal in the world's own terms, or it will eventually measure an agent that cannot act and score that as a choice. Two corollaries. A defect in shared test SETUP weakens every assertion reading that setup, in the same direction, so a setup bug looks like a consistent behavioural finding rather than noise. And when a behavioural pass rate moves with a WORLD-GENERATION parameter, suspect the harness's coupling to that parameter before concluding the world changed the behaviour — the rate at which a blind placement lands somewhere illegal is a function of the map, and it mimics a real effect perfectly.
- Provenance (verified/assumed): Verified first-hand. The frozen companions were instrumented directly (one goal held for 1400 ticks, path empty on every tick, victim confirmed standing on a blocked cell). The corrected pass rates come from the real suite, not a probe — an earlier probe of my own diverged from the test and its numbers were discarded rather than reported. Both new guards were negative-controlled: restore the blind spawn and the dense check fails at 5 of 12, reproducing the original "regression" exactly; hand it an open basin and it fails on walkability. A peak-displacement variant was tried and REVERTED because with the spawn fixed it changed no verdict — recorded so it is not re-proposed. Open, and deliberately left that way: why two dense seeds still freeze on open ground holding one goal. It is asserted against in the suite rather than explained away, and it is the residue this entry does NOT claim to cover.
- Composed: N/A
- Link: seven 090d703 correcting 6d2bfb4, tests/hallucination.test.mjs, Tension 1b23110 (the withdrawn fork)
- Reverified: 2026-10-11 · pass · sandboxes/2026-10-11__rebuild-seven-e12-placement-legality.py · observed RESULT: FAIL 2/3 on my own predictions (missed: nearest-open placement 0.865 at density 0.35); naive 0.975/0.850/0.740/0.615; legal 1.000/1.000/0.975/0.865. · Own 30x30 map with rock density 0.05 to 0.35 and 200 placed episodes per density; the behaviour under test is taking one step toward a goal. With naive placement the pass rate falls with density (0.975, 0.850, 0.740, 0.615) and tracks the open fraction within 0.08, so a setup defect reads as a consistent behavioural trend, as claimed. One gap the entry's fix does not cover: placing on the nearest OPEN cell still fails 13.5 percent of episodes at density 0.35, because the nearest open cell can sit in a pocket cut off from the goal; legal in the world's own terms has to include connectivity once the map is dense. Verdict pass on the claim; the gap is noted for the next lesson. Differs from the original: no NPC code, a BFS agent. · session; brain train rebuild pass on Seven-relevant Games lessons, 2026-10-11; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E36 · compatible · sandboxes/2026-10-11__nearest-open-cell-is-not-legal-placement-on-dense-maps.py · observed RESULT: PASS 3/3; d0.05 open 1.000 connected 1.000; d0.25 open 0.975 connected 1.000; d0.35 open 0.865 connected 1.000; d0.40 open 0.630 connected 1.000 · session; follow-up to the 2026-10-11 rebuild review of seven E12; session_01NHKVhTvCnvtvZ2NGLSPYj6

## E11 — binary reachability has no stopping rule
- Date: 2026-09-12
- Project: Pappydapimp69/seven
- Tags: [procgen][gamedesign][algorithm]
- What: A procedural map generator whose connectivity contract is binary — every feature REACHABLE, enforced by a repair pass that carves corridors to anything a flood fill misses — cannot host any pass that makes ground expensive to cross, because "reachable" has no stopping rule. Replacing the flood fill with a distance field and reporting a budget (reachable within N steps) alongside the unchanged boolean is what made a density pass possible at all.
- Why built: The traverse design needs a cut path through dense forest: "a fallen tree across the path needs cutting" is only a decision when leaving the path is worse than clearing it. Obstacles were being placed on a basin the generator kept 78% walkable.
- Design: `distanceField(blocked, cx, cz)` is the same BFS as the existing flood fill, storing step counts instead of a reachability bit; `-1` is unreachable. `validate()` runs it instead of the flood fill and returns `worstDistance`, `worstId`, `overBudget`, `withinBudget` and `budget` ALONGSIDE the original `ok`, which still means exactly what it meant. Reachable is `distance !== -1`, so the old contract is a special case of the new one and every existing caller keeps working. The density pass then has a keep/reject test it never had: fill a slice of open cells, re-derive the field, keep the slice only if every feature is still inside the budget, and roll the slice back WHOLE on refusal.
- Got right: Reported the budget rather than enforcing it. A world where a marker is a very long walk is HARD, not BROKEN, and folding the two into one boolean is how a difficulty question turns into a crash. Also: rolling back a rejected round whole rather than cell by cell, because a partially reverted round leaves the map in a state no measurement was ever taken of.
- Where/why it failed: Three obstacle experiments failed before this, all measuring the same wall. Deadfalls placed at random cleared a 6-cell-detour bar on 0.2 worlds in 1; laid on a carved 3-wide path with dense sides, 0.03; with the rock band deepened from 4 to 10 cells, 0.00 — and the open-cell count only fell 1517 to 1397, because the repair pass carved back through the very ground that was meant to make the path worth following. The binary contract could not tell "everything is a stroll" from "everything is a long hard walk": both pass identically, so there was no signal to stop filling against and no way to notice the repair pass undoing the work.
- Fix: Weaken the contract to a distance budget (3x the grid's side = 138 cells; the worst walk on the open basin measures 54-71, so nothing existing is near the bar). Add the density pass that spends it.
- Why this fix: A weaker contract that reports a number beats a stronger one that reports a bit, when what you need to build is a pass that trades against the thing being measured. The binary version was not wrong — it is why this generator ships without hand inspection — it was just unfalsifiable as a quality measure. Result: 78% to 63% walkable, and deadfalls clearing the detour bar went from 0.2 per world to 3.40 with a median detour of 10 cells.
- Rule of thumb: If a generator guarantees a property with a boolean and you need a pass that spends against that property, the boolean has no stopping rule — re-derive it as a quantity and report it beside the boolean rather than replacing it. And when weakening a contract, make the strong case fail the weak one explicitly: unreachable must be reported as INFINITE distance, or a caller that reads only `withinBudget` gets told a walled-in feature is affordable. A weaker contract still has to hold wherever the stronger one does.
- Provenance (verified/assumed): Verified first-hand. The three failed experiments were measured across 20-40 seeds each before the budget existed; the 54-71 worst-walk range and the 0-of-40-over-budget figure were measured after. All four new guards were negative-controlled: stop counting steps and the cost check fails, drop the infinite-distance push and subsumption fails, ignore the dense flag and the density check fails at 80% walkable, remove the detour gate and 69 free deadfalls appear. Full suite green including the browser tier.
- Composed: N/A
- Link: seven 6d2bfb4 (seven-0.22.0), src/world.js, tests/deadfall.mjs
- Reverified: 2026-10-11 · pass · sandboxes/2026-10-11__rebuild-seven-e11-binary-reachability.py · observed RESULT: FAIL 4/5 on my own predictions (missed: boolean walk 18, not over 42); wall counts boolean 167/260/348 vs budget 144/176/176; worst walk budget 32 of 42; sentinel -1 passes, inf fails. The claim itself (no stopping rule; the pass cannot make ground expensive under the boolean) holds. · Own 21x21 grid with an LCG wall pass, six markers, a boolean contract enforced by carving an L corridor to any unreachable marker, against a distance budget that rolls back a whole round. My own sub-prediction was wrong: I expected the boolean version's worst walk to blow past the budget, but the repair carves shortest corridors so the walk returns to 18. What it shows instead is the entry's actual claim: under the boolean the wall pass never stops (167, 260, 348 walls at 10/20/40 rounds) and cannot make ground expensive (walk back to the base 18), while the budget stops at 176 walls with a worst walk of 32, inside 42. The sentinel half also holds: a -1 for unreachable passes a dist <= budget check, infinity fails it. Differs from the original: different grid, repair shape and budget. · session; brain train rebuild pass on Seven-relevant Games lessons, 2026-10-11; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E36 · compatible · sandboxes/2026-10-11__nearest-open-cell-is-not-legal-placement-on-dense-maps.py · observed RESULT: PASS 3/3; d0.05 open 1.000 connected 1.000; d0.25 open 0.975 connected 1.000; d0.35 open 0.865 connected 1.000; d0.40 open 0.630 connected 1.000 · session; follow-up to the 2026-10-11 rebuild review of seven E12; session_01NHKVhTvCnvtvZ2NGLSPYj6

## E10 — conjured affordance is a readout
- Date: 2026-09-09
- Project: pappydapimp69/seven
- Tags: [gamedesign][ui]
- What: A deception layer in a game whose entire difficulty is that the player cannot tell whether their own senses are lying. One module derives what the player is SHOWN from what is true, and a single prompt line offers whichever verb is available where they stand.
- Why built: A new mechanic — a campfire that must be fed — was to be lied about: below a certain lucidity band, a mind sees a fire burning normally when there is none, keeps feeding it, and the wood really leaves.
- Design: Fabricate a fire for a far-gone mind and show it exactly as a real one, burning down on the same schedule so it asks to be fed on the same cadence. The consistency was the point: a lie that behaves wrongly is a bug the player can see.
- Got right: The behavioural fidelity, and putting the fabrication in the perception module rather than the simulation. The sim never learns anyone is hallucinating; it takes the wood and banks fuel only if a fire is really there.
- Where/why it failed: Fabricating the fire FROM NOTHING meant the prompt line grew a "Feed the fire" offer on empty ground the instant the lead went under. That is a perfect lucidity readout — the player learns their own hidden state by watching an affordance appear. The existing browser test caught it, because the same rule had already been written for a different verb: the strike prompt is deliberately offered to a gone mind who cannot use it, since its ABSENCE would be the tell. Both are the same rule from opposite sides, and the new mechanic broke it by adding rather than altering.
- Fix: Narrow the lie to a thing that exists. A far-gone mind sees its OWN DEAD fire as live, never a fire where it never built one. The affordance is then present for both states — you can always feed a fire you built — and only its EFFECT differs.
- Why this fix: The deception layer already had this shape and it had been stated in the design note: a far-gone mind sees dead pylons as live. Dead pylons, not imaginary ones. Altering the state of a real object leaves the interface identical; conjuring an object changes what the interface offers, and the interface is the one channel that must read the same to everyone.
- Rule of thumb: A hidden-state game may lie about the STATE of something the player can see, but must not conjure the thing itself — an affordance that only appears while deceived is a readout of the deception. Test it as a diff, not a snapshot: assert the prompt/UI is IDENTICAL before and after the hidden state flips, because a check that only looks at the deceived case cannot see what the honest case was missing.
- Provenance (verified/assumed): Verified — the browser smoke test failed with the prompt changing from the strike offer to "Feed the fire" when the lead went under, and passed once the fabrication was restricted to an already-built fire. The narrowed rule is asserted by a new test that a fire is never shown where none was built. Assumed — that no other prompt rung currently has this defect; only the rung added today was audited.
- Composed: The starvation half of the same day's work is the sibling failure: the build verb was first added to a craft resolver that returns the first match, which made an existing recipe unreachable — the same "a new verb silently eats an old one" shape, one level below the prompt ladder.
- Link: seven 66e1e04 "Fire in play — and the lie narrowed to what a lie may touch"
- Reverified: 2026-10-11 · pass · sandboxes/2026-10-11__rebuild-seven-e10-conjured-affordance.py · observed RESULT: PASS 4/4; conjure differs at ['none', 'dead'], narrowed differs at [] · Rebuilt from the rule alone with my own model: fire none/dead/live crossed with deceived or not, comparing a version that conjures a fire whenever the mind is deceived with one that only changes how a built fire looks. The obvious snapshot test (deceived shows a fire prompt) passes both versions; the diff test (prompt identical before and after the hidden flip) fails the conjuring version at none and dead and passes the narrowed one, and the conjuring prompt leaks the hidden state in 2 of 3 world states. That is exactly the claim. Differs from the original: no game code, a pure truth table. · session; brain train rebuild pass on Seven-relevant Games lessons, 2026-10-11; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E55 · compatible · sandboxes/2026-10-11__believable-hallucination-renders-the-players-learned-prior.py · observed RESULT: PASS 4/4; believed junction/open q0.8: 0.800/0.020; q0.5: 0.500/0.020; q0.1: 0.100/0.020; weak tell 0.667 · session; brain train loop on hallucination as an art style (loop 3); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E61 · compatible · sandboxes/2026-10-12__misperceived-real-objects-outlast-inserted-phantoms.py · observed RESULT: PASS 4/4; solo-touch altered survives 1.00; solo checks ins/alt/pres 1.00/2.00/2.97; party 1.00/2.00/2.22 · session; brain train focused loops on hallucination phenomenology (loop 2); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E64 · compatible · sandboxes/2026-10-12__sound-first-hallucinations-need-captions-that-lie-the-same-way.py · observed RESULT: PASS 4/4; mostly hearing: 0.90/0.60/0.60/1.00; caption-heavy: 0.80/0.30/0.30/1.00 (none/real-only/tagged/same) · session; brain train focused loops after the owner's sound-first decision (loop 3); session_01NHKVhTvCnvtvZ2NGLSPYj6

## E9 — player only guard
- Date: 2026-09-09
- Project: pappydapimp69/seven
- Tags: [state][save]
- What: `applyCharacter()` in a save system for a party game where the PLAYER and the five AI companions are the same kind of object, restored by the same function, which ends in an `if (!c.isPlayer) { ... }` block for the fields only a companion has.
- Why built: Companions carry AI state the lead genuinely does not — wander goals, path caches, chatter cooldowns, personality traits. Restoring those onto the lead would be meaningless at best.
- Design: One shared restore for everything both have, then a guarded tail for companion-only fields. The guard is correct and the split is real.
- Got right: The split itself. Most of what is inside that guard belongs there.
- Where/why it failed: Three times now, a field has been put inside the guard because it LOOKS like party-AI state and is not. `goalKind`/`goal` went in because they are how a companion picks somewhere to walk — but a hallucinating LEAD is driven by the same lost-drift code, so a resumed lead re-entered that branch and drew three fresh rng values the original had spent. `lostSince` went in for the same reason and produced `sim.time - undefined` = NaN, and NaN < x is false, so the resumed mind skipped its whole dwell. This time it was `phantomWood`, the count of wood cut while hallucinating — the lead is the ONLY mind whose count is on screen, and it came back undefined, making the displayed total NaN. Each one is invisible: no throw, no failed round-trip, because both sides agree on the same missing field.
- Fix: Move the field above the guard. The test that caught it asserted on the PLAYER's restored value specifically, not on a companion's.
- Why this fix: The guard's real predicate is not "is this character AI" — it is "does the lead have this state". Anything touched by the hallucination system fails that test, because the lead hallucinates too.
- Rule of thumb: In a party game where the player is one character among several, an `if (!isPlayer)` block in the save path is a magnet for fields that belong outside it. Before adding one, ask whether the mechanic can happen TO THE PLAYER — if it can, the field is shared. And write the round-trip assertion against the player's own value: a test that only checks a companion cannot see this class of bug at all, which is why it survived three times.
- Provenance (verified/assumed): Verified — the third instance was caught live by a new test asserting `back.party.find(c => c.isPlayer).phantomWood`, which failed with `undefined` until the line moved above the guard. The two earlier instances are recorded in the file's own comments at the fields concerned. Assumed — that no fourth field is currently misplaced; only the three found so far were audited.
- Composed: N/A
- Link: seven 8fb721a "Blueprint 0.19: the fire, and the count that lies about feeding it"

## E8 — the frame timestamp is not the clock
- Title: a rAF timestamp is not "now", and under throttling it is behind it
- Date: 2026-08-30
- Project: pappydapimp69/seven
- Tags: [browser][animation][timing][testing]
- What: A timed screen effect — a four-second blackout covering a scene transition — measured its own elapsed time as `rafTimestamp - startedAt`, where `startedAt` came from `performance.now()` at the moment the effect began. Both are the same clock, so this looks correct. It is not: the timestamp `requestAnimationFrame` hands its callback is the time the FRAME was scheduled for, and in a throttled page that is delivered behind the current clock — measured here at a persistent ~200ms in the past. The effect's elapsed time came out NEGATIVE on every frame and the blackout never ended. The page was not frozen, the loop was running, nothing threw.
- Why built: the transition needed real duration, and it had to pause with the game rather than run without it — which rules out `setTimeout` (a hidden tab throttles timers to roughly once a minute, so a multi-second sequence built from nested timeouts can stall for as long as the player is looking elsewhere and come back mid-effect).
- Design: keep driving it from the frame loop, but read `performance.now()` INSIDE the update rather than trusting the timestamp the loop was handed.
- Got right: refusing `setTimeout`. Driving presentation from the frame loop is correct — it stops cleanly when the loop stops and resumes where it was.
- Where/why it failed: "the argument rAF gives me is the current time" is an assumption that holds at 60fps and stops holding exactly when frames get scarce, which is also exactly when a several-second effect matters most. It also cannot be caught by reading the code, because the two clocks genuinely are the same clock.
- Fix: `const t = (performance.now() - startedAt) / 1000;`
- Why this fix: `performance.now()` read at call time is monotonic and can never be behind a value sampled earlier. The frame timestamp remains the right input for simulation DELTAS (frames are meant to be simulated at their scheduled time); it is the wrong input for "how long has this been on screen".
- A second lesson from the same bug: the same loop capped its per-frame delta at 0.1s so a slow frame cannot teleport the simulation. Accumulating that capped delta for a UI effect is also wrong — under throttling it runs at a fraction of real time and a four-second fade stretches to fifteen. Simulation time and presentation time are different clocks and want different rules.
- Rule of thumb: `requestAnimationFrame(t => ...)` gives you the frame's scheduled time, not the current time, and the gap opens under throttling — read `performance.now()` yourself for anything measuring wall-clock duration. And never build a UI duration out of a CAPPED simulation delta: the cap exists to protect the simulation and it distorts the effect.
- Provenance (verified/assumed): VERIFIED first-hand — instrumented in a headless page and observed `now` 205ms behind `startedAt` persistently, with elapsed time negative on every frame; fixed and confirmed.
- Link: session; src/main.js updateNightfall / frame
- Cited-by: 2026-09-28 · projects/local__sandbox-kernel-motion-animation-loop.md#E1 · compatible · sandboxes/2026-09-28__train-gap-b01.py · session 2026-09-28, brain train gap batch 1 loop 1
- Cited-by: 2026-09-29 · projects/local__sandbox-lockstep-delta-cap-trades-tunneling-for-sim-lag.md#E1 · compatible · no sandbox · session_01AJo9NVvaQuzD3JbJDk6P3B

## E7 — source window with an expiry date
- Title: a source window measured in characters is a guard with an expiry date
- Date: 2026-08-30
- Project: pappydapimp69/seven
- Tags: [testing][process][tooling]
- What: Two separate tests read a source file and sliced a fixed number of characters forward from an anchor — `src.slice(indexOf("function paintPrompt"), +3000)` and `html.slice(indexOf('id="howto"'), +4000)` — then asserted on what they found inside that window. Both were correct when written. Adding a block to the TOP of each subject pushed the content each check was actually about out of the window, and both failed with a message about the wrong thing: one reported "the parse broke — only found 0 verbs", the other reported "a bound verb with no explanation" about a paragraph sitting untouched in the file. Neither the code nor the property being asserted had changed.
- Why built: Both are legitimate source-reading tests. One holds a UI priority ladder against the real resolver so re-ordering it fails in the test rather than silently starving a tutorial step; the other holds "every bound verb is explained somewhere the player reads". Reading the source is the right technique — the window was the mistake.
- Design: Slice to a STRUCTURAL boundary instead: the next sibling function at the same indentation, or the element's own closing tag. Both are one line and neither has a magic number in it.
- Got right: Nothing about the assertions themselves. The properties were right and the anchors were right.
- Where/why it failed: A character count is a proxy for "the rest of this construct", and it is a proxy that decays monotonically as the construct grows. Worse, it fails in the direction that produces a CONFUSING message rather than a silent pass — the test reports a defect in the subject when the defect is in its own reach. That cost two rounds of looking at innocent code.
- Fix: `hud.slice(from, from + 1 + rest.search(/\n  function /))` and `html.slice(from, html.indexOf("</div>", from))`.
- Why this fix: The boundary now moves with the construct, so growing either subject cannot shrink the window. Negative-controlled both after the change: deleting the word the help check looks for still fails it, and re-ordering the resolver still fails the ladder check.
- Rule of thumb: When a test reads source, bound it by something the language or markup already delimits — the next declaration, the closing tag, a blank line — never by a character count. A numeric window is a guard that silently narrows every time the file it watches grows, and the failure it eventually produces blames the subject rather than the window.
- Provenance (verified/assumed): VERIFIED first-hand — both windows failed in this session on unmodified subject code after unrelated additions; both were re-anchored and negative-controlled afterwards.
- Link: session; tests/tutorial.mjs resolver-ladder check; tests/logic.test.mjs help-panel check

## E6 — sentinel nobody routed
- Title: a sentinel that nothing routes regenerates as valid-but-wrong
- Date: 2026-08-30
- Project: pappydapimp69/seven
- Tags: [save][state][worldgen][testing]
- What: The save system rebuilds a run by regenerating the world from `sim.seed`, which is exact for every procedurally generated map. One map is AUTHORED, and it was given a reserved negative seed (`CAMP_SEED = -1`) so the loader could recognise it. Nothing ever wrote the recognising branch. A run saved on the authored map therefore resumed by handing `-1` to the procedural generator, which produced a perfectly valid, fully reachable, completely different map — and then pasted the saved character positions onto it. No exception, no warning, no failed assertion, at any layer. The camp's own source file documented the sentinel and why it was chosen; the consumer that was supposed to read it did not exist.
- Why built: THE WOODS autosaves and must resume, so this was reached immediately. It had been live and unnoticed in the parent project's tutorial, which also autosaves every five seconds.
- Design: The routing is one line — `const world = data.seed === CAMP_SEED ? buildCamp() : null` — passed into the real constructor's existing world-injection point, so the authored map goes through exactly the same construction path a generated one does.
- Got right: The seed WAS the right routing key. It is already in every save payload at every schema version, so no migration is needed and an old save routes correctly the first time it is read. A separate `isCamp` boolean would have needed one.
- Where/why it failed: Every save test used a generated map. That is not laziness — a generated map is the normal case and the tests were written against the normal case. The authored map is a second kind of world that shares one field with the first and differs in the only property the save path depends on: whether the field reconstructs it. Nothing about "seed" says "reconstructs", so nothing about the tests suggested asking.
- Fix: Route the sentinel, and assert the resumed world CELL-BY-CELL against the authored one rather than asserting that a world came back. Reloading and finding a valid world is exactly what the bug did.
- Why this fix: The failure is not "no world" but "a different world", so any assertion weaker than identity passes on the defect. Confirmed by negative control: removing the routing line fails the cell comparison; removing only the sites-attachment fails a narrower one.
- Rule of thumb: If a reserved value means "this one is special", grep for the branch that reads it before trusting that it is handled — a sentinel with no consumer is a comment. And when one code path reconstructs its subject from a key, any subject that is NOT reconstructable from that key is a second case that needs its own test, however much it shares the same shape.
- Provenance (verified/assumed): VERIFIED first-hand — reproduced by serialising a camp run and comparing the restored `blocked` grid, which differed; fixed; negative-controlled by reverting the routing line and watching the new guard fail.
- Link: session; src/save.js deserializeRun; src/camp.js CAMP_SEED; tests/save.test.mjs "a run saved on the camp resumes ON THE CAMP"
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E13 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E19 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E42 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E5 — one account one origin
- Title: two projects on one GitHub Pages account share ONE localStorage
- Date: 2026-08-30
- Project: pappydapimp69/seven
- Tags: [browser][state][deploy][save]
- What: A game was forked into a second repository and deployed alongside the original — `owner.github.io/mirage/` and `owner.github.io/Seven/`. Both inherited the same localStorage key names. GitHub Pages serves every project of one account from ONE origin (`owner.github.io`); the project name is a PATH, and localStorage is scoped to the origin, not the path. So the two games shared a single save slot and a single settings blob: each would read the other's payload, find a schema version it refuses, discard it, and tell a player who had a save that they had none — and then overwrite it. Neither of the two lines of work developing the fork had noticed.
- Why built: The fork needed to resume runs, which is what made anyone look at the save path at all.
- Design: Rename the keys to the fork's own namespace. Nothing else needs to change; the schema-version guard was already doing the right thing with a foreign payload, which is exactly why the collision was invisible — the failure presented as "no save", which looks like a first run.
- Got right: Having a schema version at all, and discarding rather than half-applying an unrecognised payload. Without it this would have been a partially-applied cross-game snapshot instead of a lost save.
- Where/why it failed: The mental model was "different site, different storage", which is true for a project on its own domain and false for a project path on a shared user domain. Path-scoped deployment feels like isolation and is not.
- Fix: `seven:run` / `seven:settings` instead of the inherited `mirage:*`. Also worth knowing: tutorial progress rode inside the settings blob, so it was colliding too.
- Why this fix: Namespacing at the key is the only lever available — the origin cannot be changed without a custom domain per project.
- Rule of thumb: Anything scoped to an ORIGIN — localStorage, sessionStorage, IndexedDB, cookies without a path, service workers, permissions — is shared by every project deployed under one `*.github.io` account (and by every app on any shared host domain). Namespace storage keys per project from the first commit, and treat a fork as a new project for this purpose even though its code says otherwise. And note the failure presents as "no save", not as an error, so it will be reported as data loss rather than as a collision.
- Provenance (verified/assumed): VERIFIED — both sites are live under one `pappydapimp69.github.io` origin with the same key names, and the schema versions differ (3 vs 4), which is the discard path. The keys were namespaced before the fork's first player-facing release.
- Link: session; src/save.js SAVE_KEY/SETTINGS_KEY; docs/adr/0003-two-alphas.md
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-dog-seven-project-namespace-does-not-fix-slot-leak.md#E1 · compatible · no sandbox · session https://claude.ai/code/session_01VDpEDT2ry2U1WXLUnGqdYD
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E23 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-10-09 · projects/pappydapimp69__brain.md#E107 · compatible · sandboxes/2026-10-09__hidden-menu-row-focus-grid-shared-origin-save-and-start-key.py · observed RESULT: PASS naive grid dead-press=['DEAD:resume']; identity survives reshape, index does not; bare shared key lets a sibling reshape the menu, namespaced does not; any-key start fires on Ctrl; own-style filter misses hidden-ancestor row,… · brain train auto pass 5, session 01EzGMQhUbptmRNUnqW1q9k1

## E4 — a verifier pinned to its own name
- Title: a verifier pinned to the project's own name cannot fail after a fork
- Date: 2026-08-30
- Project: pappydapimp69/seven
- Tags: [tooling][deploy][testing][process]
- What: A deploy verifier walks the LIVE site's module graph and asserts that every module carries the current cache-bust token. It found the token with a regex that hard-coded the project's name — `/\?v=(mirage-[\d.]+)/`. The project was forked and renamed. On the fork the regex matched nothing, so the token set came back empty, the "more than one token is live" check could never fire, and the tool printed its success line — "every module the browser loads carries the current token" — over a graph in which it had verified exactly zero tokens. It reported OK on every run.
- Why built: This tool exists specifically because three consecutive correct fixes were shipped and none reached the player: ES module imports resolve against the module's PATH, so a query string on the entry script is not inherited by its imports, and every other module kept being served from cache. The tool is the guard against exactly that, on the live site.
- Design: Match any project's prefix (`/\?v=([a-z]+-[\d.]+)/`), and treat an EMPTY token set as a failure rather than a pass. A graph with no tokens in it has been walked, not verified.
- Got right: Walking the LIVE graph by following the exact urls the browser follows, rather than curling the changed file. That part is the whole value and was correct.
- Where/why it failed: The identity the tool matched on was the project's NAME, which is the one thing about a project that is expected to change. Every other input — the entry path, the BUILD constant, the import syntax — was derived from the document at run time; only this one was frozen at authoring time. And the failure mode is silent by construction: the checks that would have complained are all conditioned on having found something.
- Fix: Derive the prefix from the shape rather than the value, and add an explicit "nothing was checked" failure so a zero-result run is loud.
- Why this fix: The "more than one token" check and the per-import check both degrade to no-ops on an empty match set, so the ONLY way to notice is to assert on the set being non-empty. Confirmed by running the fixed tool against both projects: it now prints the live token, and it fails if the graph carries none.
- Rule of thumb: When a tool identifies its subject by a literal that names the project, ask what happens after a rename or a fork — and make "found nothing" a failure rather than a vacuous pass. Any check written as "for each X found, assert P" is silently satisfied by an empty X; the guard needs a companion assertion that X was non-empty.
- Provenance (verified/assumed): VERIFIED first-hand — the tool printed "tokens live: (none)" alongside "OK" on the fork; after the fix it prints the real token on both projects.
- Link: session; tools/verify-deploy.mjs in pappydapimp69/seven and pappydapimp69/mirage
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E18 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E24 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E34 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E3 — a known red test in the middle
- Title: a known-red test under `set -e` silently deletes the rest of the suite
- Date: 2026-08-30
- Project: pappydapimp69/seven
- Tags: [testing][process][tooling]
- What: A shell test runner with `set -e` ran its checks in file order. One of them — a balance simulation whose assertion encodes a difficulty decision nobody had made — had been failing for some time and was known to be failing, and was accepted as such. It sat in the middle of the file. Everything after it therefore never ran: the entire browser tier, eleven Playwright suites covering the 3D layer, the gamepad, split-screen, save resume, menu navigation, display scaling, field of view and a full tutorial playthrough. For as long as the red test had been red, "run the suite" had been exercising only the pure-logic half, and nothing said so — the runner just stopped, having printed a failure that everyone already expected to see.
- Why built: The red test is legitimately red and legitimately kept. The intent — "the suite exits non-zero if anything fails" — is also right.
- Design: Move the accepted-red check to the END, capture its status rather than letting `set -e` act on it, and carry that status to the exit. Everything else keeps failing fast.
- Got right: Not deleting or weakening the failing assertion. It encodes a real open question and the tuning that would make it pass would be a lie about the game's difficulty.
- Where/why it failed: `set -e` makes ORDER significant in a file where order looks incidental. Nobody re-reads a runner script when a test they already knew about fails; the expected failure message is indistinguishable from the expected failure message, and the missing eleven suites produce no output at all — absence of output is the one thing a human skimming a terminal will not notice.
- Fix: `set +e; node tests/balance.mjs; BALANCE=$?; set -e`, at the bottom, with an explicit final branch that exits non-zero and names the reason.
- Why this fix: It keeps the suite honest (still non-zero overall) while making the tolerated failure cost nothing else. The alternative — deleting the test or relaxing its threshold — trades a visible open question for an invisible one.
- Rule of thumb: An accepted-failing check must be the LAST thing a fail-fast runner does, and its status must be captured rather than thrown. Any tolerated red under `set -e` is not one failing test, it is every test below it, and the loss is silent because a suite that stops early looks exactly like a suite that ran.
- Provenance (verified/assumed): VERIFIED first-hand — the browser tier produced no output at all until the reorder, then eleven suites ran and passed.
- Link: session; tests/run-all.sh in pappydapimp69/seven and pappydapimp69/mirage
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E2 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E40 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E2 — a context per mount
- Title: one WebGL context per mount, and the browser discards the oldest
- Date: 2026-08-30
- Project: pappydapimp69/seven
- Tags: [browser][webgl][gamedev][performance]
- What: Mounting a run built a fresh scene, a fresh geometry set and a fresh WebGL context on the same canvas, and nothing released the previous one. One code path (moving level to level) disposed correctly; the other — title to run, and every tutorial or new-game start — did not, and had not for the life of the project. It was survivable only because a session historically mounted two or three runs in total. Adding a "play again" button beside the end-of-run screen changed that overnight: six runs in a sitting is six live contexts on one canvas. Browsers hard-cap live WebGL contexts (16 is typical in Chromium) and, on hitting the cap, force-lose the OLDEST rather than refusing the newest — so the failure is a black screen on a canvas whose context was silently taken away, with nothing thrown and nothing in the console.
- Why built: the fork put a fresh run one keypress from the end of the previous one, deliberately, because the design question it is testing is whether the game survives repetition.
- Design: `run?.renderer?.dispose?.()` as the first statement of the mount, before the new renderer is constructed. The dispose already existed and already traversed the scene freeing geometries and materials; only the call site was missing.
- Got right: having a real `dispose()` at all, and having ONE code path that used it — which is what made the missing call obvious once anyone looked.
- Where/why it failed: two mount paths, one of them added later, and the newer one was written by copying the shape of a fresh start rather than the shape of a transition. Nothing in the type system, the tests or the console distinguishes them. And the symptom appears far from the cause, several runs later, as the game not drawing.
- Fix: dispose at the top of the shared mount, not in each caller, so a third mount path cannot reintroduce it.
- Why this fix: putting it in the callers is what produced the bug. The invariant is "at most one live renderer", and the only place that can enforce it is the thing that creates them.
- How it surfaced: a headless browser test wedged so completely it could not navigate to `about:blank` — three mounted runs under software rasterisation. The leak was not what the test was for; it was found while working out why the harness had stopped responding.
- Rule of thumb: a graphics context, an audio context, a worker, a socket — anything the browser caps and reclaims by evicting the OLDEST — must be released by the function that ACQUIRES it, at the top, not by each caller that happens to remember. And the tell for this class is not an exception: it is the oldest thing quietly going dark while the newest works fine.
- Provenance (verified/assumed): VERIFIED first-hand — reproduced as a wedged headless page after three mounts, fixed with a one-line dispose at the head of the mount, browser suites green afterwards in both the fork and the parent project (the parent had the same missing call).
- Link: session; src/main.js mountRun; src/render.js dispose()
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E44 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E7 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-09-28 · projects/pappydapimp69__brain.md#E51 · compatible · no sandbox · session 2026-09-28, Canon and Frontier animation; hasWebGL removal

## E1 — a callback that draws
- Title: a callback that draws makes a constant-roll-count function variable
- Date: 2026-08-30
- Project: pappydapimp69/seven
- Tags: [rng][determinism][api-design][testing]
- What: A selection function was written to the codebase's constant-roll-count rule: two draws from the caller's generator, always, whatever it returns. It took a CALLBACK for one of its inputs — "give me an almost-right version of this name" — and called it once per distinct actor while walking its candidate list. The callback drew. So the function's real cost was `2 + (however many distinct people did something that day)`, which moved with the shape of the data, and two runs on the same seed with days of different lengths consumed different amounts of the caller's stream. The function's own two draws were scrupulously unconditional and that fact was irrelevant.
- Why built: The rule exists because a variable draw count silently forks a resumed run — everything looks identical at the moment of the resume and diverges minutes later.
- Design: Replace the callback with a PREPARED MAP. The caller draws one value per party member, in a fixed sorted order, whether or not that member appears in the data, and passes the finished table in. The cost is fixed before the function is entered.
- Got right: Having a draw-count test at all. It was the only thing that could have found this — the return values are correct in every case, and the divergence is invisible until a save is resumed.
- Where/why it failed: The draw-count test held the DATA SHAPE constant while sweeping the seed, so the candidate list was always the same length and the per-candidate cost was always the same number. It passed on the defect. Sweeping the shape as well as the seed found it immediately. This is the same failure as a guard that has never been observed to fail: the test was written from the same mental model as the function, and that model had "the days are all the same length" quietly baked in.
- Fix: `pickPerturbation(rng, chron, nearMisses)` where `nearMisses` is a plain object, and the caller does `for (const id of Object.keys(roster).sort()) nearMisses[id] = nearMiss(prng, ...)`.
- Why this fix: It moves the variable-length work OUT of the stream-consuming function and makes it fixed-length at the same time, rather than trying to make a data-driven walk cost a constant amount.
- Rule of thumb: The constant-roll-count rule is about the FUNCTION'S TOTAL, not about its own visible draws. Any callback, iterator or helper it invokes that can touch the generator inherits the obligation, and if it is invoked a data-dependent number of times the obligation cannot be met — hoist those draws to the caller and pass a finished table. And sweep the DATA SHAPE, not just the seed, when measuring a draw count: holding the shape fixed is exactly what hides this.
- Provenance (verified/assumed): VERIFIED first-hand — the draw-count sweep printed a single constant while the defect was live, and printed `4,5,6,7,3` the moment the day length was swept; after the fix it prints one value, and re-injecting a per-candidate draw fails it.
- Link: session; src/chronicle.js pickPerturbation; src/woods.js fallNight; tests/chronicle.mjs "picking a perturbation costs a fixed number of draws"
- Cited-by: 2026-09-29 · projects/local__sandbox-dbz-combat-seven-hoisted-crit-table-loot-stream.md#E1 · compatible · no sandbox · session_01AJo9NVvaQuzD3JbJDk6P3B
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E20 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E48 · compatible · sandboxes/2026-10-11__save-rng-state-words-survives-a-miscounted-draw.py · observed RESULT: PASS 4/4; true 6000 counted 3000; words cost 0 match; counted diverges; true-count cost 6000; sorted hash stable · session; brain train auto run 2 pass 1 (kernel, declare); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E89 · incompatible · sandboxes/2026-10-12__rebuilt-witness-list-forks-a-fakes-lie-across-reload.py · observed RESULT: FAIL 8/10; changed verbatim 0.000 reorder 0.797 drop 0.395; minhash reorder 0.000 drop 0.208; sorted reorder 0.000 drop 0.395; resume+draws constant True · session; brain train loop round 3; session_01QGT1LfmPHPG99JEGaPhBwB
