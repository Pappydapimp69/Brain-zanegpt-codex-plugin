# Pappydapimp69/brain-auto-training — lessons

Project: Pappydapimp69/brain-auto-training. Newest first.

---

## E46 — reduce gonna first then hyphenate only leftover rushed lines
- Date: 2026-10-19
- Project: pappydapimp69/brain-auto-training
- Tags: [songwriting][lyrics][suno-prompting][testing]
- What: Sandbox of 48 synthetic lines at budget 9 true syllables: reducing going-to to gonna before a bare verb clears the rushed-line hint only on lines exactly one syllable over (9 of 16), none of the 16 two-over lines, so hyphenate-to-slow is still needed on the leftovers.
- Why built: Auto-train picked the hyphenate-to-slow kernel with the write-the-reduced-form kernel as untested companion; the question was whether reducing first removes the need to hyphenate.
- Design: Python stdlib; vowel-group counter plus a true-syllable table (going 2, gonna 2); guarded reducer skips going to the store; hint fires on true count over 9; whole-word end-word rhyme key letters each 4-line stanza before and after.
- Got right: Reduction never touched an end word, so rhyme letters stayed identical in 12 of 12 stanzas; the guard left all 16 going-to-noun lines unchanged.
- Where/why it failed: The reduction saves one syllable per line at most, so two-over lines stay flagged; and the vowel-group counter reads going as one syllable, so it saw no change at all (7 to 7, 10 to 10, 16 to 16).
- Fix: Key the over-budget hint off true syllables, apply the reduction first, then offer hyphenation or a cut only for lines still over.
- Why this fix: Reduction is free and keeps the sung words honest, while hyphenation slows the line but adds nothing to the syllable budget, so order them cheap to costly.
- Rule of thumb: Reduce going-to before a bare verb first, then hyphenate or cut only lines still over budget; judge by true syllables because a vowel-group counter cannot see the saving.
- Provenance: Verified first-hand by running the sandbox script; the synthetic lines are not real Suno output.
- Composed: ideas:SONGWRITING/hyphenate-words-to-slow-a-rushed-vocal-line, ideas:SONGWRITING/write-the-reduced-form-you-will-sing, two-pass-rhyme-letters-never-merge-perfect-groups-but-hide-assonance-to-a-resolved-group-exhaustive-4-line-stanzas/E1
- Picked-by: new-half
- ZaneGPT verdict: weak — the sandbox is built from 48 synthetic lines with a hand-set syllable table, so "reduce first, then hyphenate or cut the leftovers" is plausible but the 9/16 vs 0/16 result describes the generator, not real lines.
- Hidden assumption: Reduction savings are uniform across lines (one syllable per going-to), so the 9/16 and 0/16 splits generalize, when they actually come from the synthetic verb mix (carry and away counted as two syllables) and the table's gonna = 2 value.
- Would prove it wrong: Running the same reducer on a set where the bare verbs are mostly one-syllable (go, run, see), or on natural lyrics with different going-to frequency, and getting a cleared share well away from 9/16 or any two-over line cleared. Another refutation would be a rhyme letter shifting in a stanza where the reduced line ends on a different word.
- Break scenario: Two-over lines containing "going to" twice (e.g. "I'm going to try and I'm going to stay"), where reduction saves two syllables and clears a two-over line. That contradicts "none of the two-over", or "going to" followed by a vowel-initial verb, where the reduced "gonna" might elide in singing and make the true count disagree with the table.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-19 · digest 283917f35c0c
- Polarity: compatible
- Sandbox: sandboxes/2026-10-19__reduce-gonna-first-then-hyphenate-only-leftover-rushed-lines.py
- Prediction: Reduction would clear most one-over hints (about 12 of 16), none of the two-over, and leave rhyme letters unchanged in all stanzas.
- Observed: RESULT: PASS reduction cleared 9 of 16 one-over hints (= the 9 lines exactly one over), 0 of 16 two-over, noun lines untouched (0 changed), vowel-group counter saw 0 change, rhyme letters kept 12/12 stanzas. Cleared count was 9 not 12 because carry and away are two syllables.
- Scenarios: 1) one-over bare-verb lines; 2) going-to-noun lines the guard must skip; 3) BREAK: two-over bare-verb lines where reduction should not be enough
- Link: brain train auto loop 1 pass 1; session_01TymEo8Je55Sk3ydLUdwHUE

## E45 — parochial empathy gap not general empathy predicts harm in a grid model
- Date: 2026-10-19
- Project: pappydapimp69/brain-auto-training
- Tags: [empathy][bias][model][testing]
- What: In a 80-person deterministic grid model where harm depends on the gap between in-group and out-group empathy, regressing harm on in-group, out-group and trait empathy recovers +0.5, -0.5 and 0.0, raising everyone's empathy by 1 changes mean harm by 0.0, and raising only out-group empathy cuts it by 0.5; an out-group-only harm model has an in-group coefficient of 0 and a general raise cuts harm by 0.5.
- Why built: The parochial-empathy kernel was a gap with no memory applying it; I wanted to know which of its three claims (opposite-signed independent effects, trait controlled, a general raise need not cut harm) a simulation can actually separate from the alternative reading.
- Design: Python stdlib, no RNG; people on a lattice of trait 0 to 4, in-group offset -1 to 2 and out-group offset -2 to 1; ordinary least squares by Gauss-Jordan on [1, in, out, trait]; two generating rules, gap and out-group-only; interventions add +1 to all, or to out-group only.
- Got right: The in-group coefficient is the diagnostic: a positive in-group coefficient beside a negative out-group one fits the gap model (+0.5 and -0.5), while an out-group-only model gives 0 there, and only the gap model makes a general empathy raise leave harm unchanged.
- Where/why it failed: The result is partly built in, since the gap model was written to produce it, so it shows what the kernel's claims imply and tests no real data; it says nothing about the effect sizes in the paper, which the kernel itself marks as unverified.
- Fix: Read the kernel as a testable pair of predictions (in-group coefficient above 0 with trait controlled, and a null effect of general empathy training) and check the in-group coefficient before accepting a gap story.
- Why this fix: A single out-group coefficient fits both the gap and the out-group-only story, but the in-group coefficient and the general-raise effect split them, so they are the cheap discriminating checks.
- Rule of thumb: To tell parochial empathy from low empathy, look at the in-group coefficient with trait controlled and at what a general empathy boost does; in a gap world the first is positive and the second is zero.
- Provenance: Verified first-hand by running the sandbox script; it exercises the kernel's opposite-effects claim, the trait control and the general-raise claim on a generated grid, not on the Bruneau, Cikara and Saxe data.
- Composed: ideas:EMPATHY/bias/it-is-the-GAP-between-in-group-and-out-group-empathy
- Polarity: compatible
- Sandbox: sandboxes/2026-10-19__parochial-empathy-gap-not-general-empathy-predicts-harm-in-a-grid-model.py
- Prediction: Gap model gives coefficients +0.5, -0.5 and 0 and a general raise changes harm by 0.0; the out-group-only break model changes harm by -0.5 under a general raise.
- Observed: RESULT: PASS gap model: in +0.5, out -0.5, trait +0.0; general +1 raise changes harm by 0.0, out-group-only by -0.5; BREAK out-only model: general raise changes harm by -0.5
- Scenarios: 1) gap harm model regression; 2) interventions: general +1 versus out-group-only +1; 3) BREAK: out-group-only harm model where a general raise should reduce harm
- Link: brain train auto loop 2 pass 5; session_01TymEo8Je55Sk3ydLUdwHUE
- Cited-by: 2026-10-20 · projects/pappydapimp69__brainwork.md#E529 · compatible · sandboxes/2026-10-20__parochial-gap-meets-crowd-diffusion-targeted-vs-general-empathy.py · observed RESULT: PASS general empathy raise (+0.2 both) leaves crowd harm exactly unchanged only under the difference form (12/12 cells); at n=6 alpha 0.7 it changes harm by -0.026 under a ratio form and +0.031 under a saturating-product form; out-… · session_015FBsByvogibt2qnd37NTki

## E44 — exhaustive split table shows which first weighings solve the coin puzzle
- Date: 2026-10-19
- Project: pappydapimp69/brain-auto-training
- Tags: [coin-weighing][search][testing][sandbox]
- What: An exhaustive solver over (unknown, maybe-light, maybe-heavy, genuine) counts shows that for 12 coins in 3 weighings only one first weighing works, 4 v 4, so the obvious 6 v 6 half split fails; 13 coins with no spare have no working first move and with one spare genuine coin only 5 v 4 plus the spare works.
- Why built: Auto-train paired the counterfeit-coin lesson, which proved capacity, with the training loop's search and testing tags; the open question was whether the lesson also says which first move to make, not only whether a solution exists.
- Design: Memoised recursion over counts instead of coin identities, trying every left and right pan composition including known genuine coins as ballast, tilt outcomes mapping candidates to light or heavy sets; first weighings enumerated from 1 v 1 up and with a spare.
- Got right: The solver reproduced the entry's capacity numbers independently (12 solvable, 13 not without a spare, 13 solvable with one spare) and added the move-level result that exactly one first split survives out of six for 12 coins.
- Where/why it failed: My first version ignored the spare and reported 13 coins unsolvable even with a spare; the second tracked known genuine coins per state and fixed it, so a capacity claim needs the genuine-coin count in the state.
- Fix: Treat the known-genuine count as part of the search state and enumerate all first weighings, reporting the working set and not just a yes or no.
- Why this fix: Capacity alone leaves a person with a 6 v 6 first weighing that looks right and cannot succeed, while the move table makes the mistake visible.
- Rule of thumb: When a puzzle's capacity is proven by exhaustive search, also tabulate which first moves survive, because the intuitive balanced opening can be the one that fails.
- Provenance: Verified first-hand by running the sandbox script; the model is the classic one-odd-coin puzzle with a balance scale and no real weighing.
- Composed: counterfeit-coin-weighings-need-a-spare-genuine-coin-for-the-last-coin/E1
- Picked-by: current-half
- ZaneGPT verdict: weak — The 12-coin result (only 4v4 works, 13 impossible without a spare) matches known theory, but the rule of thumb is generalized from one instance and was never tested on a second one where the balanced opening might actually be correct.
- Hidden assumption: The solver's model is faithful to the puzzle: the weighing rules, the "unknown coin may be heavy or light" state, and the requirement of identifying the coin and its direction (not just the coin) are encoded correctly, and "12 coins/3 weighings" is a representative case. The rule also assumes that a first move failing at 6v6 generalizes beyond this one puzzle.
- Would prove it wrong: The same solver, run on other proven-capacity cases (for example 3 coins/2 weighings, 4 coins/2 weighings, or 39 coins/4 weighings with a spare), showing that the balanced half split is always among the working first moves (or that the working set is not narrow). Alternatively, a hand-verifiable 6v6 strategy, or a 13-coin strategy found by an independent solver.
- Break scenario: Run 12 coins/3 weighings with "identify the odd coin only, direction not required." The 13-coin and 6v6 conclusions can flip, so the lesson's boundary depends on an unstated goal definition. Also run n=4, 2 weighings with a spare genuine coin, to see whether "balanced fails" holds anywhere beyond this single case.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-19 · digest bdf4bfb7533a
- Polarity: compatible
- Sandbox: sandboxes/2026-10-19__exhaustive-split-table-shows-which-first-weighings-solve-the-coin-puzzle.py
- Prediction: Only 4 v 4 works as a first weighing for 12 coins; 13 coins without a spare have none; one spare lets 13 coins work.
- Observed: RESULT: PASS 12 coins/3 weighings: first splits that work ['4v4'] (6v6 fails); 13 coins no spare []; 13 with one spare ['5v4+spare']
- Scenarios: 1) 12 coins, all pan sizes 1 to 6; 2) BREAK: 13 coins without a spare, where no move should work; 3) 13 coins with one spare genuine coin
- Link: brain train auto loop 2 pass 2; session_01TymEo8Je55Sk3ydLUdwHUE

## E43 — effort past the floor knee buys nothing in dilution and thermostat
- Date: 2026-10-19
- Project: pappydapimp69/brain-auto-training
- Tags: [model][numerics][sandbox][thermostat-control][lab-dilution]
- What: A bounded-effort knob hits a floor in both systems: halving the thermostat band cut swing 41% at first but only 8% at the last halving (floor about 1.1 K), and dilution error at a=0.2 uL is lowest at 2 steps and rises at 4.
- Why built: Auto-train paired the serial-dilution step-count lesson with the thermostat band lesson because they share model, numerics and sandbox tags; the question was whether they share one stopping rule.
- Design: Python stdlib, 1 s steps, no RNG; on/off heater with 120 s command lag, band 2.0 to 0.125 over 7200 s; dilution worst-case percent error n * max(0.5 percent, a / sample volume) for 1000x in 1000 uL, a from 0 to 2 uL.
- Got right: Both show a knee: the tunable part falls until it equals the floor, then more effort buys little; at a=0 dilution had no knee and one step won (0.5 vs 1.0 percent at two steps).
- Where/why it failed: The guess that the last band halving would cut under 5 percent missed (7.9 percent), and the thermostat did not get worse past the knee: cycles only rose 6 to 15, unlike dilution where extra steps raised error.
- Fix: Treat the floor as the stopping rule: estimate it first (overshoot, or the per-step minimum error), tune only until the knob term matches it, and check whether extra effort also adds error (dilution) or merely flatlines (thermostat).
- Why this fix: The floor sets the best reachable value, so measuring it is cheaper than sweeping the knob and tells you whether to stop at a knee or at an optimum.
- Rule of thumb: Measure the floor before turning a precision knob; past the point where the knob term equals the floor extra effort flatlines or backfires, so stop there.
- Provenance: Verified first-hand by running the sandbox script; both are simplified models, not real instruments.
- Composed: 2026-10-13__serial-dilution-step-count-worst-case-error-crossover-with-pipette-floor/E1, thermostat-band-below-lag-overshoot-adds-cycles-not-precision/E1
- Picked-by: current-half
- ZaneGPT verdict: weak — both PASS results are baked into the models (the dilution knee is the formula and the thermostat floor is the lag), the 5% prediction missed (7.9%), and the rule's "past the knob term equals the floor" threshold was never measured in either system.
- Hidden assumption: Both systems' floors are the same kind of thing: the thermostat floor is a lag-set limit that effort can't beat, while the dilution knee comes from a modeled cost that grows with effort (n times a/sample volume), so "stop where knob term equals floor" generalizes only if every knob has this additive form.
- Would prove it wrong: A system where the best setting sits well past the point where the knob term equals the floor, such as the thermostat with a shorter command lag or a nonlinear actuator, or one where the best n is the same at a=0.2 and a=2. Either would show the stop-point depends on the cost model, not on a general rule.
- Break scenario: Rerun the thermostat with the 120 s lag cut to 0 s and 10 s. If the floor drops and the swing keeps falling at the 0.125 band (last-halving cut well above 8%), the floor was a property of that lag and not a limit on effort. Also sweep a from 0.05 to 2 uL and check that the best n moves smoothly. Scenario 3 (a=0) only tests the formula's own algebra, since n * 0.5% is increasing in n by construction.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-19 · digest bb6ba97eb0e3
- Polarity: compatible
- Sandbox: sandboxes/2026-10-19__effort-past-the-floor-knee-buys-nothing-in-dilution-and-thermostat.py
- Prediction: First band halving cuts swing at least 20 percent, the last under 5 percent; dilution gets worse two steps past its best count; at a=0 one step wins.
- Observed: RESULT: PASS thermostat swing cut 0.41 at first halving vs 0.08 at last; dilution a=0.2 best n=2 and n+2 is worse=True; a=0 one step wins=True. The under-5-percent number was wrong (7.9 percent).
- Scenarios: 1) thermostat band halvings 2.0 to 0.125; 2) dilution a=0.2 steps 2 vs 4; 3) BREAK: dilution a=0 where no knee should exist
- Link: brain train auto loop 1 pass 2; session_01TymEo8Je55Sk3ydLUdwHUE
- Audited: 2026-10-20 · modeled · Read the entry and its stored sandbox and reran it (output matched: swing cuts 0.407, 0.279, 0.134, 0.079 per band halving; dilution best n=2 at a=0.2 with error 1.26 vs 1.5 at n=3; a=0 best n=1). The thermostat half computes its result by stepping a heater with 120 s lag, so the flattening swing and rising cycle count (6 to 15) are produced by the run. The dilution half does not compute a dilution: error is the closed form n*max(0.5 percent, a/sample volume), so the optimum and the backfire past it are built into the formula and the run only reads them off; the a=0 case likewise follows from the max() term. The PASS test for the thermostat is loose (last cut under a quarter of the first and first above 20 percent), and the 5 percent guess it admits missing was never replaced by a firm threshold. The rule of thumb says to measure the floor before turning the knob, but the sandbox never measures a floor ahead of time and then checks the stopping point it predicts; it only shows the knee afterwards, and at a=2 the best n (7) sits at the edge of a nearly flat curve (3.79, 3.76, 4.0), which the rule does not describe. Both systems are hand-written models of real pipettes and thermostats, so the claim about real instruments is untested. · session_015FBsByvogibt2qnd37NTki

## E42 — rule card ceiling caps go big at frame distance
- Date: 2026-10-17
- Project: pappydapimp69/brain-auto-training
- Tags: [comedy][humor][testing]
- What: Composed a gag rule card whose harm ceiling equals the framing's distance with a go-big severity schedule, in a toy sketch where a beat is funny only if it has a violation and stays benign.
- Why built: To test whether the rule card (write the rules first) is what lets going big stay inside the distance that benign-violation requires.
- Design: Six beats, three frames (grounded 2, sitcom 4, cartoon 6); schedules flat-mild, go-big 1..6, flat-max; card clamps severity to the stated ceiling; score is summed severity of funny beats.
- Got right: Card with ceiling equal to distance took grounded go-big from 2/6 funny beats to 6/6 and score 3 to 11; sitcom went 4/6 to 6/6 and score 10 to 18; cartoon needed no card.
- Where/why it failed: Built-to-break case: a card whose ceiling ignores the frame (ceiling 6 in grounded) changed nothing, still 2/6 funny. The card also flattens the top of the arc, so grounded caps at score 11 versus 18 for sitcom.
- Fix: State the ceiling as the frame's distance, not a generic maximum, and escalate in steps up to that ceiling.
- Why this fix: The card only helps through the number it states; the distance is what makes a violation benign, so the ceiling must be that number.
- Rule of thumb: A rule card helps a go-big sketch only if its harm ceiling is set to the frame's distance; a ceiling that ignores the frame is worth nothing, and a grounded frame caps the payoff.
- Provenance (verified/assumed): Verified first-hand by running the sandbox script; the toy funny test is my own model, not human audience data.
- Composed: ideas:COMEDY-CRAFT/benign-violation, local__escalation-needs-matching-distance/E1, ideas:COMEDY-CRAFT/write-the-rules-before-the-gags
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-17__rule-card-ceiling-caps-go-big-at-frame-distance.py
- Prediction: Assumption: the card helps by itself. Expected grounded go-big 2/6 funny unclamped and 6/6 with card; a wrong-ceiling card equal to no card; would be wrong if the wrong-ceiling card also helped.
- Observed: RESULT: PASS grounded go-big funny 2/6 -> 6/6 with ceiling=distance card; wrong ceiling stays 2/6; score 3->11
- Scenarios: 1) grounded frame no card; 2) grounded with matched card; 3) sitcom and cartoon frames; 4) BREAK: card with ceiling 6 ignoring frame; 5) flat-mild and flat-max schedules
- Link: brain train auto pass 1 (scheduled run 2026-10-17); session_01MUFH1b1Lc27PXz6rjHHodQ

## E41 — publish gate mix real product ai scenes label
- Date: 2026-10-17
- Project: pappydapimp69/brain-auto-training
- Tags: [ai-video][compliance][disclosure][sandbox][model]
- What: Built a publish-gate model over an eight-shot AI product video (five scenes, two product shots, one cartoon) that applies three AI-video kernels at once: a reference image does not make an AI product shot compliant, label photoreal AI, and mixing real product footage with AI scenes.
- Why built: The kernel about reference images had no memory entry applying it; the gap was whether the three kernels combine into one checkable gate or overlap.
- Design: Five plans (all-AI with reference fidelity 0.9, all-AI with fidelity 1.0, real product plus AI scenes with and without label, real product plus cartoon scenes without label) scored on two platforms. Rules are taken from the kernels, so only the composed accounting is tested, not platform policy.
- Got right: Real product shots plus AI scenes plus a label had 0 violations on both platforms; each rule failed independently (missing label gave exactly one violation, AI product shots gave one each).
- Where/why it failed: Built-to-break case: a perfect reference image (fidelity 1.0) still left both product shots in violation, identical to 0.9, so reference fidelity buys nothing. Cartoon-only AI needs no label on YouTube but does on TikTok, so one label rule across platforms is wrong.
- Fix: Gate on product shots being real first, then the label by platform; treat the reference image as a consistency tool only.
- Why this fix: The two checks are independent and each failure has a different remedy (reshoot real footage versus flip a toggle), so one combined gate with separate reasons tells the author which to do.
- Rule of thumb: Check product-shot source and label separately; real product footage plus labelled AI scenes passed in every tested plan, while a reference image at any fidelity never cured an AI product shot.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; platform rules are encoded from the kernels, not checked against the live platform policies, so the result is a model of the composition.
- Composed: ideas:AI-VIDEO/ai-for-scenes-and-dubbing-real-footage-for-the-product-plus-the-ai-label, ideas:AI-VIDEO/label-photoreal-ai-and-skip-the-label-for-obvious-cartoons-on-youtube, ideas:TIKTOK-SHOP/compare-the-platforms-ai-video-maker-with-external-models-on-credits-modes-and-compliance-review
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-17__publish-gate-mix-real-product-ai-scenes-label.py
- Prediction: Assumption: the three kernels do not overlap. Expected mix plus label 0 violations on both platforms and all-AI with reference 2 violations at fidelity 0.9 and 1.0; would be wrong if fidelity 1.0 cleared them.
- Observed: RESULT: PASS mix+label = 0 violations on both platforms; all-AI with reference image 0.9 or 1.0 keeps 2 product violations; cartoon-only AI skips label on youtube but not tiktok
- Scenarios: 1) all-AI fidelity 0.9 with label; 2) BREAK: all-AI fidelity 1.0 with label; 3) real product plus AI scenes with label; 4) same without label; 5) real product plus cartoon scenes without label, on youtube and tiktok
- Link: brain train auto pass 5 (scheduled run 2026-10-17); session_01MUFH1b1Lc27PXz6rjHHodQ
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E433 · compatible · sandboxes/2026-10-18__i2v-drift-vs-reference-fidelity-gate.py · observed RESULT: PASS source rule never passes ref shots (3/3 fids); tolerance rule passes fid 1.0 and animate<=15s (2 hops), fails 22s+; label gate independent per platform. Key numbers: i2v violations 0,0,1,1 at 8,15,22,30 s; ref under deviation… · session_01RNshpLS3CjgyV5GRQ9SeH2

## E40 — greedy knob stop rule dilution steps and solder dwell
- Date: 2026-10-17
- Project: pappydapimp69/brain-auto-training
- Tags: [lab-dilution][soldering][sandbox][numerics][model]
- What: Tested one greedy stop rule (raise the knob while the next notch gains at least 1 percent) on two systems whose lessons share a shape: dilution step count with a pipette floor, and solder dwell time with a steady-state ceiling.
- Why built: Both lessons say do not tune the knob blindly (an interior optimum in one, an unreachable steady state in the other); I wanted to know if a single cheap stop rule plus a target check handles both.
- Design: Dilution uses the stored worst-case error model for a=0, 0.2, 0.5, 1.0, 2.0 and n 1 to 8; solder uses the first-order joint model with a 350 C tip for a small pad, a ground-plane pad and a ground-plane pad on a 100 C board, dwell in 0.25 s notches, target 217 C. Constants are assumed and no randomness is used.
- Got right: The greedy rule landed within 0.007 percent of the true dilution optimum at every a tested; in solder it stopped at saturation, 185.0 C against a steady state of 187.5 C for the ground plane, and the unmet target then showed that dwell was the wrong lever, while the preheated board stopped at 223.1 C and melted.
- Where/why it failed: Built-to-break case a=2.0: greedy stopped at 5 steps while the argmin is 6, but both give 5.85 percent, so the apparent trap cost almost nothing; the stop rule alone cannot tell a plateau from a ceiling, which is why the target check is needed.
- Fix: Run the stop rule, then compare the stopped metric with the target; if the target is unmet at a saturated knob, switch to a different lever (preheat, larger tip, different pipette) instead of pushing the knob.
- Why this fix: Saturation says the knob is exhausted but not whether the goal is reached, and the two systems differ exactly there: dilution reached its best error, solder stopped short of melting.
- Rule of thumb: Stop raising a knob when a notch gains under 1 percent, then test the target: a stop with the target met is done (dilution within 0.007 percent of optimum), a stop with it unmet means change the lever (ground-plane joint 185.0 C versus 217 C).
- Provenance (verified/assumed): Verified first-hand by running the sandbox; both system models and all constants are assumed values, not measurements of a pipette or an iron.
- Composed: 2026-10-13__serial-dilution-step-count-worst-case-error-crossover-with-pipette-floor/E1, solder-joint-steady-state-decides-not-dwell-time/E1
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-17__greedy-knob-stop-rule-dilution-steps-and-solder-dwell.py
- Prediction: Assumption: a single greedy stop rule is right for both. Expected greedy equals the argmin at a=0.5 and may be trapped at a=2.0; solder stops short of 217 C on the ground plane at 350 C; would be wrong if greedy missed the optimum error by more than 0.1 percent or the ground plane stopped above 217 C.
- Observed: RESULT: PASS greedy 1 pct stop rule is within 0.007 pct of the dilution optimum at every a tested (n differs at a=2.0, 5 vs 6, a plateau); in solder it stops at saturation (ground plane 185.0 C of steady 187.5 C, target 217 C unmet)
- Scenarios: 1) dilution a=0 to 1.0 unimodal; 2) BREAK: dilution a=2.0 plateau; 3) small pad solder; 4) ground-plane solder; 5) ground plane on preheated board
- Link: brain train auto loop 2 pass 2 (scheduled run 2026-10-17); session_01MUFH1b1Lc27PXz6rjHHodQ
- Audited: 2026-10-17 · modeled · Read the entry and reran its stored sandbox. The result is computed, not built in: the greedy stop and the argmin are both derived from the same error formula and from a first-order thermal curve, and the quoted figures (greedy n=5 vs best 6 at a=2.0 with equal 5.85 percent, ground plane 185.0 C of 187.5 C steady, preheated 223.1 C) reproduce. Coverage is narrower than a general rule: the dilution part covers a only up to 2.0, and sweeping a from 0.001 to 20 uL in 0.001 steps the greedy rule's worst gap to the optimum is 0.088 percent at a=3.52 (greedy 5, best 6), about 12 times the 0.007 quoted, though still under 0.1. The entry says "at every a tested", so it stands as worded. Both systems are hand-written models with assumed constants and no pipette or iron was measured, so the verdict is modeled rather than pass. · brain train auto loop 1 pass 3, scheduled run 2026-10-17; session_01696mc4JbaRUYgcwwnaPSG1

## E39 — frame zero sound hook factor in ipm d1 ranking
- Date: 2026-10-17
- Project: pappydapimp69/brain-auto-training
- Tags: [game-ads][testing][model][sandbox]
- What: Added a frame-zero sound switch (from the film hook lesson) to the 18-variant IPM times D1 ranking and swept how much the sound lifts low-fidelity ads (K), checking which variant wins and what a recut that drops the sound costs.
- Why built: The ranking lesson assumes the hook factor is independent of fidelity; the kernel says decompose the winner and recut, so I wanted to know whether a sound-at-frame-zero hook breaks that independence.
- Design: Variants are hook 0.8, 1.0, 1.2 by fidelity 0.4, 0.7, 1.0 by sound on or off. IPM is 10 times hook times (1.6 minus 0.6 times fidelity) times a sound boost of 1 plus 0.25 times (1 plus K times (1 minus fidelity)); D1 is 0.15 plus 0.25 times fidelity. K swept over 0, 1, 2, 4, 8, 16. All constants are assumed and no randomness is used.
- Got right: With independent sound (K=0) IPM alone picks fidelity 0.4, IPM times D1 picks fidelity 1.0 with sound on and hook 1.2, and dropping the sound in the recut loses exactly 20 percent (1 minus 1 over 1.25).
- Where/why it failed: Built-to-break sweep of K: at K=1 and 2 the IPM times D1 winner moves to fidelity 0.7 and from K=4 up to fidelity 0.4, the same pick IPM alone makes, so D1 stops protecting against the over-promising ad once sound lifts low-fidelity ads enough. I did not predict the threshold; it is lower than I expected.
- Fix: Treat the sound as a factor to hold equal across variants before ranking, or rank sound-on and sound-off variants separately, so its interaction with fidelity cannot decide the pick.
- Why this fix: The flip happens through the sound boost multiplying IPM unevenly; equalising it removes that term and leaves the retention link to do its job.
- Rule of thumb: If a hook element lifts IPM more for the less faithful ads, IPM times D1 can lose its correction (winner fidelity 1.0 to 0.7 to 0.4 as K goes 0, 1, 4), so fix that element across variants before ranking, then recut.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; all functional forms and constants are assumed model values, not measured ad data.
- Composed: rank-ipm-times-d1-needs-fidelity-retention-link/E1, film/E14, ideas:GAME-ADS/concept-then-variants-ranked-on-ipm-times-early-retention
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-17__frame-zero-sound-hook-factor-in-ipm-d1-ranking.py
- Prediction: Assumption: sound is independent of fidelity. Expected at K=0 IPM-only winner fidelity 0.4, IPM times D1 winner fidelity 1.0 with sound on, recut loss 20 percent; would be wrong if sound changed the K=0 winner. The K sweep was exploratory with no threshold predicted.
- Observed: RESULT: PASS with independent sound (K=0) IPM*D1 still picks fidelity 1.0 with sound on, IPM-only picks 0.4; dropping the sound in a recut loses 20 percent; once sound lifts low-fidelity ads enough (first flip K=1.0) the IPM*D1 winner leaves fidelity 1.0
- Scenarios: 1) K=0 independent sound; 2) recut dropping the sound layer; 3) BREAK: K=1 and 2; 4) K=4, 8, 16 where the winner equals the IPM-only pick
- Link: brain train auto loop 2 pass 1 (scheduled run 2026-10-17); session_01MUFH1b1Lc27PXz6rjHHodQ

## E38 — drain slope manning scour velocity vs code table
- Date: 2026-10-17
- Project: pappydapimp69/brain-auto-training
- Tags: [plumbing][drainage][sandbox][numerics][model]
- What: Seeded a plumbing domain by computing, with Manning's equation for a part-full circular pipe, the flow velocity that the common drain-slope table (a quarter inch per foot up to 2.5 in, an eighth inch per foot for 3 to 6 in) delivers, against a 2 ft/s self-cleaning target.
- Why built: New domain with no records; advice often says steeper is not better or that the table is generous, and I wanted numbers per pipe size.
- Design: V is 1.486 over n times R to the 2/3 times S to the 1/2, with R equal to a quarter of the diameter (half-full), n 0.012 for smooth plastic and 0.015 for rougher pipe, and the 2 ft/s target is a commonly cited design figure used as an input. Diameters 1.5, 2, 3, 4 and 6 in. No randomness.
- Got right: Velocity rises monotonically with slope and the table gives 2.15 ft/s at 2 in, 2.41 at 4 in and 3.16 at 6 in, comfortably above target; the slope needed for 2 ft/s falls from 0.318 in/ft at 1.5 in to 0.050 at 6 in, so the larger pipe needs far less.
- Where/why it failed: My pre-run guess that the table clears 2 ft/s everywhere was wrong: 1.5 in gives 1.77 ft/s and 3 in gives 1.99, both just under. The built-to-break rough-pipe case (n 0.015) lowers every velocity by 20 percent to 1.42, 1.72, 1.59, 1.93 and 2.53 ft/s, leaving only 6 in above target.
- Fix: Check the table slope against Manning for the actual diameter and pipe roughness, and add slope for 1.5 in and 3 in runs or for older pipe instead of trusting one table across sizes.
- Why this fix: Velocity scales with the square root of slope and the inverse of n, so the margin differs by diameter and a single slope per size band hides which sizes have none.
- Rule of thumb: For the standard drain-slope table, the margin over a 2 ft/s scour velocity is thin at 1.5 in (1.77) and 3 in (1.99) and large at 6 in (3.16), and rougher pipe removes 20 percent of it, so lay the small and 3 in runs at or above the table slope and compute for rough pipe.
- Provenance (verified/assumed): Verified first-hand by running the sandbox: velocities and required slopes are computed from Manning's equation; the code table, n values and the 2 ft/s target are inputs recalled from common practice and no pipe was measured.
- Composed: N/A
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-17__drain-slope-manning-scour-velocity-vs-code-table.py
- Prediction: Assumption: the table gives at least 2 ft/s everywhere. Expected 1.5 in near 2 ft/s and 6 in well above; would be wrong if any size fell under 1.9 ft/s. 1.5 in came out at 1.77, so the assumption failed.
- Observed: RESULT: PASS code-table slopes give V=1.77 (1.5 in), 1.99 (3 in), 3.16 (6 in) ft/s; below 2 ft/s for D in [1.5, 3]; rough pipe n=0.015 lowers every one by 20 percent
- Scenarios: 1) five diameters at the table slope with n 0.012; 2) slope needed for 2 ft/s per diameter; 3) BREAK: rough pipe n 0.015; 4) monotonic slope sweep at 3 in
- Link: brain train auto loop 2 pass 6 (scheduled run 2026-10-17); session_01MUFH1b1Lc27PXz6rjHHodQ

## E37 — dilution step choice is dwarfed by cure dose base error
- Date: 2026-10-17
- Project: pappydapimp69/brain-auto-training
- Tags: [lab-dilution][curing][sandbox][numerics][model]
- What: Composed the serial-dilution step-count lesson with the cure-dose weight-base lesson in one error budget for a nitrite cure made from a 1000x diluted stock.
- Why built: To see which error dominates the delivered ppm, the dilution step count or the weight base the percent is applied to.
- Design: Worst-case dilution error is n steps times max(0.5 percent, a over carried volume) with final volume 1000 uL; base error is brine weight over meat weight when the percent is applied to meat plus brine; a swept over 0, 0.02, 0.2, 0.5 uL and n over 1 to 4.
- Got right: With the best step count the dilution error stayed at or under 3.2 percent (0.5, 1.0, 1.26, 1.5 for the four pipette constants) while a 10 to 25 percent base error is far larger; at a=0.02 the whole step-choice spread was only 1.0 point.
- Where/why it failed: Built-to-break case: with a coarse pipette (a=0.2 or 0.5) a single step gives 20 and 50 percent error, which exceeds the base error, so the claim that the base always dominates is false; it holds only when the step count is chosen well.
- Fix: Fix the dose base first (weigh meat at cure time), then pick the step count for the pipette constant; do not tune steps while the base is unsettled.
- Why this fix: The base error is a fixed 10 to 25 percent no step count can reduce, while a good step choice shrinks dilution error to a few percent, so ordering the fixes by size removes the larger error first.
- Rule of thumb: Settle the dose weight base before optimising dilution steps, then still pick steps for the pipette constant, since one step at a coarse pipette (20 to 50 percent) can beat the base error as the worst term.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the dilution formula is my simplified model and does not match the earlier lesson's exact percentages, and no real pipetting was done.
- Composed: local__2026-10-13__serial-dilution-step-count-worst-case-error-crossover-with-pipette-floor/E1, local__curing-dose-base-meat-weight-not-total/E1
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-17__dilution-step-choice-is-dwarfed-by-cure-dose-base-error.py
- Prediction: Assumption: the weight-base error dominates everywhere. Expected best-step dilution error under 3 percent for every a and a spread under 2 points at a=0.02; would be wrong if any best-step error exceeded the 10 percent base error.
- Observed: RESULT: PASS step-count spread at a=0.02 is 1.00 pct vs 10-25 pct base error; best-case dilution error never exceeds 1.5 pct (best n per a: 1, 2, 2, 3; one step at a=0.5 gives 50 pct)
- Scenarios: 1) a=0 pipette; 2) a=0.02; 3) a=0.2; 4) BREAK: a=0.5 with one step; 5) base 10 percent brine; 6) base 25 percent brine and trim mismatch
- Link: brain train auto pass 2 (scheduled run 2026-10-17); session_01MUFH1b1Lc27PXz6rjHHodQ
- Audited: 2026-10-17 · modeled · Read the entry and its stored sandbox. The dilution error is genuinely computed from the step count and pipette constant, and the coarse-pipette break case is real. But the comparison side is assumed: the base errors (10 and 25 percent brine, 25 percent trim mismatch) are author-chosen inputs, so the headline that base error dwarfs step choice is partly built in, and check 4 compares a constant to itself so it tests nothing. The entry text also says best-step error stays at or under 3.2 percent while the run prints a worst best-case of 1.5 percent. Both the pipette error formula and the curing dose are real-world systems tested only against a hand-written model with no real measurements, so the verdict is modeled. · brain train auto loop 2 pass 3 audit session (session_01PTu5uBJqYTUhgm91RqrjQ3)

## E36 — containment dedicated threads batch give first
- Date: 2026-10-17
- Project: pappydapimp69/brain-auto-training
- Tags: [distribution][gamedev][sandbox][model]
- What: Modelled 28 days of promoting a free browser game in three communities with different rules (thread-only 50k, ten percent self-promo ratio 200k, anti-spam spacing 20k) under four strategies, exercising the reddit containment, batch-do-not-drip and where-to-post kernels together.
- Why built: The containment kernel had no memory entry applying it; the gap was whether dedicated threads, weekly batching and give-first each matter, or one of them carries the result.
- Design: Rules are assumed inputs: thread-only removes standalone promos, the ratio community removes a promo unless promos are at most 10 percent of own contributions, the open one removes a promo within 3 days of the last, and two removals ban. Strategies: daily drip without give-first; weekly batch with 3 helpful comments a day and the dedicated thread; the same with a standalone post in the thread-only community (built to BREAK); weekly batch with threads but no give-first. Reach is surviving promos times community size. No randomness.
- Got right: Weekly batch plus give-first plus the dedicated thread survived 4 of 4 promos in every community and reached 1080k with no bans; daily drip reached 20k and was banned in all three.
- Where/why it failed: Give-first alone did not protect against the thread rule: the standalone post in the thread-only community was removed twice and banned (880k), and batching without give-first lost the ratio community entirely (280k). Each practice guards a different community, so none substitutes for another. Because the rules are my assumed inputs, much of this follows by construction; the sandbox checks that the three practices compose, not what any real subreddit enforces.
- Fix: Read each community's rule first, post only in its allowed form (thread or standalone), keep a counted record of helpful contributions before promoting, and space promos by a week.
- Why this fix: The three failures came from three different rules, so the fix needs all three behaviours, each aimed at its own rule.
- Rule of thumb: Contain promotion rather than avoid it: in this model all three of dedicated thread, give-first and weekly spacing were needed (1080k with each, 880k and 280k losing one), so check which rule each community enforces before dropping any.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the community rules, sizes and ratio are assumed model inputs and no real community was posted to.
- Composed: ideas:DISTRIBUTION/reddit-containment-not-prohibition, ideas:DISTRIBUTION/itch-devlog-cadence-discipline, ideas:DISTRIBUTION/where-to-post-a-free-browser-game
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-17__containment-dedicated-threads-batch-give-first.py
- Prediction: Assumption: each of the three practices matters on its own. Expected full practice about 4 survivors per community and no bans, drip banned in A and B by day 2, standalone in A removed even with give-first; would be wrong if dropping one practice cost nothing.
- Observed: RESULT: PASS weekly batch + give-first + dedicated thread reached 1080k with no bans versus 20k and bans in A and B for daily dripping; standalone posts in the thread-only community die even with give-first (880k), and batching without give-first loses community B entirely (280k)
- Scenarios: 1) daily drip, no give-first; 2) weekly batch, give-first, dedicated thread; 3) BREAK: same but standalone in thread-only community; 4) weekly batch with threads but no give-first
- Link: brain train auto loop 2 pass 5 (scheduled run 2026-10-17); session_01MUFH1b1Lc27PXz6rjHHodQ

## E35 — canning altitude bands lethality at band edges
- Date: 2026-10-17
- Project: pappydapimp69/brain-auto-training
- Tags: [canning][food-safety][sandbox][numerics][model]
- What: Seeded a canning domain by modelling the stepped altitude additions for boiling-water canning (bands of 1001 to 3000 ft plus 5 min, 3001 to 6000 plus 10, 6001 to 8000 plus 15, 8001 to 10000 plus 20) against a lethality model with boiling point falling 1 C per 300 m and z of 10 C.
- Why built: New domain with no records; the question was whether the stepped table holds sea-level lethality across a band or only at some point in it.
- Design: Lethality ratio is (base plus added minutes) over base times 10 to the power (boiling point minus 100) over z, enumerated every 50 ft from 0 to 10000 ft for 10 and 20 min bases. The band table is an input taken from public home-canning guidance for short processes, and z and the slope are modelling assumptions.
- Got right: The low edge of the first band reaches 1.19 of sea-level lethality, so the table is not useless; the sandbox also computes the exact equal-lethality time, 20.2 min at 3000 ft and 103.8 min at 10000 ft for a 10 min process.
- Where/why it failed: My pre-run prediction (ratio at or above 1 everywhere) was wrong, and the first run also had a bug (ratio not divided by the sea-level time), fixed before the final run. Corrected result: 165 of 180 grid altitudes fall below 1, first at 1751 ft; 0.74 at 3000 ft and 0.29 at 10000 ft; a z of 6 C (built to break the z=10 assumption) drops the worst case to 0.06.
- Fix: Treat the band table as a margin-based rule that leans on the sea-level time carrying large headroom, not as an equal-lethality calculation; if you need the latter, scale time by 10 to the (100 minus boiling point) over z.
- Why this fix: Required time grows exponentially with the boiling-point drop while the table adds linear minutes, so the gap widens with altitude and cannot be closed by a bigger step alone.
- Rule of thumb: Altitude time additions are linear patches on an exponential, so they reach equal lethality only near the bottom of a band; follow the published table for acid foods, and do not reuse its additions for a different food or temperature target without recomputing.
- Provenance (verified/assumed): Verified first-hand by running the sandbox: the lethality ratios and equal-lethality times are computed; the band table is an input recalled from public guidance, and z and the boiling-point slope are chosen model constants.
- Composed: N/A
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-17__canning-altitude-bands-lethality-at-band-edges.py
- Prediction: Assumption: the band additions preserve sea-level lethality. Expected worst ratio at or above 1.0 for 10 and 20 min bases and a ratio under 0.5 at 10000 ft with no additions; would be wrong if any band-edge ratio fell below 1. It did, so the claim was revised and retested.
- Observed: RESULT: PASS stepped additions leave lethality at 0.74 of sea level at 3000 ft and 0.29 at 10000 ft (10 min base, z 10 C); equal lethality needs 20.2 and 103.8 min; z 6 C worsens worst case to 0.06
- Scenarios: 1) 10 min base across 0 to 10000 ft; 2) 20 min base; 3) band low edges versus high edges; 4) no additions at 10000 ft; 5) BREAK: z of 6 C instead of 10 C
- Link: brain train auto pass 6 (scheduled run 2026-10-17); session_01MUFH1b1Lc27PXz6rjHHodQ

## E34 — window surface temp sets condensation rh
- Date: 2026-10-17
- Project: pappydapimp69/brain-auto-training
- Tags: [building-physics][condensation][model][testing]
- What: Seeds a new psychrometrics domain: the indoor humidity at which a window pane starts to condense is the relative humidity whose dew point equals the pane's inner surface temperature, so the glazing U-value sets a humidity ceiling.
- Why built: The domain had no records at all (queries for dewpoint, psychrometrics and humidity returned nothing); a real, checkable scenario was needed to seed it.
- Design: Magnus dew point with the Alduchov and Eskridge 1996 constants (17.625, 243.04) checked against the textbook 9.3 C at 20 C and 50 percent; inner surface temperature from U-value and ISO 6946 internal surface resistance 0.13; ceiling humidity found by inverting the dew point. Single, double and triple glazing at 20 C inside, 0 C outside, plus an outside-temperature sweep and a cold corner.
- Got right: Dew point 9.26 C matched the reference; ceilings were 37, 63 and 88 percent for single, double and triple glazing; the double-glazing ceiling fell 80, 71, 63, 56, 49 as outside went 10 to -10 C; feeding the ceiling back gave dew point equal to surface temperature.
- Where/why it failed: My single-glazing guess of about 31 percent missed (37 observed). The break case, a cold-bridge corner at an effective U of 6, dropped double glazing to 36 percent, so a pane's centre figure overstates safety where the frame bridges.
- Fix: Use the weakest surface (corner or frame) when stating a humidity ceiling, not the glass centre U-value.
- Why this fix: Condensation starts at the coldest wetted surface, so the minimum surface temperature governs.
- Rule of thumb: Keep indoor humidity below the value whose dew point equals the coldest inner surface; for 20 C inside and 0 C outside that is about 37, 63 and 88 percent for single, double and triple glazing. It is a steady-state model: still air, no ventilation or moisture storage.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the Magnus constants and the 0.13 resistance are cited from the literature, not re-measured, and no real window was tested.
- Composed: N/A
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-17__window-surface-temp-sets-condensation-rh.py
- Prediction: Assumption: centre-of-glass U-value is enough to state the ceiling. I predicted single about 31 and double about 62 percent and that a bridged corner would not change the ordering of the results; single came out 37 (missed), double 63.
- Observed: RESULT: PASS dew 20C/50% = 9.3 C; condensation RH ceiling single 37% double 63% triple 88% at 0C outside; cold corner U=6 drops double to 36%
- Scenarios: 1) single glazing; 2) double glazing; 3) triple glazing; 4) outside-temperature sweep; 5) cold-bridge corner at U 6 (built to BREAK the centre-of-glass assumption)
- Link: brain train auto pass 6, loop 1; session_01LG4GQFTi9A1QxnCzb5c6CV

## E33 — venue rules compose into a launch calendar
- Date: 2026-10-17
- Project: pappydapimp69/brain-auto-training
- Tags: [distribution][process][testing][model]
- What: Five separate venue-etiquette kernels turned into one plan linter plus a greedy scheduler show that, for a free browser game, the weekly Saturday self-promo thread sets the launch day, not the jam end.
- Why built: These kernels were never applied in memory; each is a standalone rule, so nothing showed whether a single launch plan can satisfy them all or what pins the earliest date.
- Design: Day 0 is a Monday. Rules as predicates: 9 comments before an r/gamedev promo and only in the Saturday thread, itch listing after jam end, Show HN last and once with a live playable and a plain title, no copy reused across venues, devlogs 15 days apart. A greedy scheduler builds a plan; the linter checks it. Ran jam end day 3 and day 8, a naive same-day plan, and HN placed two days early.
- Got right: Scheduler plans linted clean; Show HN landed on day 6 for jam end 3 and day 13 for jam end 8, both the day after the Saturday thread. The naive plan tripped 7 distinct rules.
- Where/why it failed: My first probe moved HN one day early and linted clean, because the same-day Saturday thread is not strictly after HN; the check was too weak, so I moved it two days early, which tripped the last-promo and live-playable rules. The linter and scheduler share my reading of the kernels, so this tests their consistency, not Reddit or HN themselves.
- Fix: Schedule Show HN as the day after the Saturday self-promo thread (and after the listing), and build the 9 give-first comments early so they never delay it.
- Why this fix: Last-promo ordering makes HN wait for the slowest earlier promo, and the Saturday-only thread is the slowest, so the calendar sets the date.
- Rule of thumb: When composing venue rules, compute the launch date from the slowest calendar-gated venue, not from the jam end: Show HN waited for Saturday on both jam dates tested. The constants (9 comments, 15 days) come from medium-confidence kernels and a toy model.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the platform norms themselves are taken from the kernels and not re-checked against the live sites.
- Composed: ideas:DISTRIBUTION/where-to-post-a-free-browser-game, ideas:DISTRIBUTION/reddit-containment-not-prohibition, ideas:DISTRIBUTION/show-hn-survival-criteria, ideas:DISTRIBUTION/never-duplicate-copy-across-venues, ideas:DISTRIBUTION/itch-devlog-cadence-discipline
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-17__venue-rules-compose-into-a-launch-calendar.py
- Prediction: Assumption: the jam end is the binding constraint on the launch date. I predicted Show HN on day 6 for jam end 3 (the Saturday thread) and day 13 for jam end 8, a clean linter result, and at least 6 rules tripped by the naive plan.
- Observed: RESULT: PASS greedy schedule lints clean (HN day 6 at jam_end 3, day 13 at jam_end 8); naive plan trips 7 rules (R1,R2b,R2c,R3a,R3b,R4,R5); HN placed before the Saturday thread trips R2c and R3a
- Scenarios: 1) jam end day 3; 2) jam end day 8 (built to BREAK the jam-binds assumption by moving the Saturday); 3) naive same-day plan with duplicate copy; 4) HN placed two days early
- Link: brain train auto pass 5, loop 1; session_01LG4GQFTi9A1QxnCzb5c6CV

## E32 — harm ceiling card matched to distance
- Date: 2026-10-17
- Project: pappydapimp69/brain-auto-training
- Tags: [comedy][humor][testing]
- What: Sandbox composing a gag rule card that states a harm ceiling with a go-big severity schedule and a framing distance; asks whether the ceiling lets a sketch escalate safely to the framing's distance.
- Why built: Open tension asked whether a harm-ceiling rule card makes escalation safe; benign-violation, matched-distance escalation and rules-before-gags were each tested alone but never together.
- Design: Eight-beat go-big schedule (severity 1..8); a beat is ok if severity is at most the distance d, scoring its severity, else it scores 0 and counts as a violation. The card clamps severity to its ceiling. Swept d from 1 to 8 over four cards: none, ceiling equal to d, ceiling d+2 (built to break), ceiling d-2.
- Got right: Ceiling equal to d gave 0 violations and the plateau-at-d score at all 8 distances; no card leaked at 7 of 8 distances; a fixed d=1 with no card gave 7 violations and score 1.
- Where/why it failed: The d+2 ceiling leaked at 6 of 8 distances, so stating a ceiling is not protective, only a matched one is. First run reported FAIL from my own scoring bug (oracle ignored that clamped beats repeat the ceiling); fixed the oracle, not the claim.
- Fix: Derive the card's ceiling from the framing distance instead of writing it independently; the d-2 ceiling stays safe but lost score at 7 of 8 distances, so do not undershoot either.
- Why this fix: Safety and score both depend on ceiling matching distance; the card is only the carrier of that number.
- Rule of thumb: A harm ceiling on the gag rule card makes escalation safe only when it equals the framing's distance: over-stated ceilings leak like no card, under-stated ones are safe but forfeit score. Caveat: severity and distance are one-number toys, so this checks the composition logic, not real comedy.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the toy severity-versus-distance model itself is assumed, not measured on real sketches.
- Composed: ideas:COMEDY-CRAFT/benign-violation, escalation-needs-matching-distance/E1, ideas:COMEDY-CRAFT/write-the-rules-before-the-gags
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-17__harm-ceiling-card-matched-to-distance.py
- Prediction: Assumption: a stated ceiling protects regardless of its value. I predicted the matched card gives 0 violations at every d, and the d+2 card leaks (assumption broken) at least 5 of 8 distances.
- Observed: RESULT: PASS matched ceiling: 0 violations and full score at all 8 distances; no card leaks at 7/8, over-ceiling leaks at 6, under-ceiling loses at 7
- Scenarios: 1) no card; 2) ceiling equals d; 3) ceiling d+2 (built to BREAK the stated-ceiling-protects assumption); 4) ceiling d-2; each swept over d=1..8
- Link: brain train auto pass 1, loop 1; session_01LG4GQFTi9A1QxnCzb5c6CV

## E31 — dough water temp formula vs heat balance
- Date: 2026-10-17
- Project: pappydapimp69/brain-auto-training
- Tags: [baking][thermal][model][testing]
- What: Seeds a BAKING domain: the baker's three-factor water temperature rule (3 times desired dough temperature minus flour, room and friction) is exact only when the three thermal masses are close to equal, and a heat balance gives the water temperature that hits the target every time.
- Why built: The domain had no records; the rule is a cited real practice (Hamelman, Bread) and its equal-weight assumption can be checked by computation.
- Design: Heat balance with thermal masses relative to water (flour 0.40, preferment 0.70, water 1.0, all assumed), mixer rise 6 C so friction factor 18, target 24 C. Swept preferment share 0, 0.5 and 1.0, hydration 55, 75 and 85 percent, and four flour and room temperature pairs.
- Got right: Worst rule error was 12.5 C (no preferment, 85 percent hydration, 30 C flour and room); at preferment 1.0 and hydration 55 percent the worst case was 0.9 C. The heat-balance water temperature hit the target to 0e+00.
- Where/why it failed: My first version used friction as the raw 6 C rise instead of the friction factor (3 times the rise) and showed a false 6 C miss; the flour-and-water-only version also did not match the rule's setting since the rule has a third term. Both fixed before the reported run.
- Fix: When flour, water and a preferment differ much in thermal mass or the kitchen is hot, compute water temperature from a heat balance; the rule asked for -6 C water in a 30 C kitchen, which really means use ice.
- Why this fix: The rule gives each of its three temperatures equal weight, which is right only when their thermal masses match, so error grows as they diverge.
- Rule of thumb: Treat the three-factor dough water rule as an approximation valid near equal thermal masses (error at most 0.9 C there, up to 12.5 C without a preferment at high hydration); otherwise solve the heat balance. Specific heats and preferment mass here are assumed, not measured on dough.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the rule is taken from a cited book and the thermal masses are my assumed values, with no real dough measured.
- Composed: N/A
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-17__dough-water-temp-formula-vs-heat-balance.py
- Prediction: Assumption: the rule is accurate for ordinary conditions regardless of preferment. I predicted a worst error above 3 C, near 1 C when the masses are nearly equal, and a negative water temperature in a hot kitchen; all three held.
- Observed: RESULT: PASS rule misses the dough temperature by up to 12.5 C (0.9 C at near-equal thermal masses, 12.5 C with no preferment at 85% hydration); heat-balance water hits it exactly (0e+00); hot-kitchen rule asks for -6 C water
- Scenarios: 1) preferment 0 at three hydrations; 2) preferment 0.5; 3) preferment 1.0 (near-equal masses); 4) hot 30 C flour and room (built to BREAK the rule); 5) cold 10 and 18 C inputs
- Link: brain train auto loop 2 pass 6; session_01LG4GQFTi9A1QxnCzb5c6CV

## E30 — beat recut keeps the gap clock recut spoils it
- Date: 2026-10-17
- Project: pappydapimp69/brain-auto-training
- Tags: [game-ads][film][testing][model]
- What: When a winning 25 second ad is recut shorter, cutting by beats keeps the information-gap reveal intact down to 10 seconds, while trimming the tail or scaling every beat by the clock breaks it much earlier.
- Why built: The ad-iteration kernel says to decompose a winner and recut it, the earlier ranking lesson showed a clock recut losing 23 percent, and the film lesson says to time a reveal from the line that opens its gap; none had been tested together.
- Design: Seven beats (hook 3, open 3, filler 4, build 6, filler 3, reveal 4, cta 2). Three recuts to 20, 15, 10 and 8 seconds: keep the first T seconds, scale every beat by T/25, and drop filler then shrink the rest toward per-role minimums. Pass needs hook of 2 s or more, reveal of 2 s or more, a CTA, and a gap (reveal start minus end of the opening beat) of 3 s or more.
- Got right: Beat recut passed at 20, 15 and 10 seconds; scaling passed only at 20; tail trim passed at none, because the reveal starts at 19 s and was cut to 1 s or removed.
- Where/why it failed: The 8 second target failed for every method (minimums sum to 10), so the beat recut has a floor. I also expected tail trim to pass at 20 s; its reveal is only 1 s there, so it failed.
- Fix: Recut by dropping filler beats first and shrinking the rest down to role minimums, and treat the sum of the minimums as the shortest legal cut.
- Why this fix: The gap and the reveal are defined by beat order and spacing, which uniform scaling distorts (hook falls under 2 s at 15 s) and tail trimming removes.
- Rule of thumb: Recut a winning ad by beat, not by clock: in this one fixture the beat recut kept the gap at 20, 15 and 10 s while the clock recuts held at best 20 s. The numeric minimums are my assumptions, not viewer data.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the role minimums and the 3 s gap threshold are assumed, and no real ad or retention data was used.
- Composed: ideas:GAME-ADS/concept-then-variants-ranked-on-ipm-times-early-retention, rank-ipm-times-d1-needs-fidelity-retention-link/E1, film/E19
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-17__beat-recut-keeps-the-gap-clock-recut-spoils-it.py
- Prediction: Assumption: a clock recut is roughly as safe as a beat recut for a reveal-driven ad. I predicted the beat recut would pass down to 10 s, scaling would fail at 15 s or below, and tail trim would pass at 20 s; the last was wrong (it failed).
- Observed: RESULT: PASS beat recut keeps the gap down to 10s (passes [20, 15, 10]), tail trim passes only [], uniform squeeze passes [20]; below 10s nothing works (8s fails)
- Scenarios: 1) target 20 s; 2) target 15 s; 3) target 10 s; 4) target 8 s (built to BREAK the beat recut below the minimums), each across the three recut methods
- Link: brain train auto loop 2 pass 1; session_01LG4GQFTi9A1QxnCzb5c6CV

## E29 — ai video shot list lint composes three rules
- Date: 2026-10-17
- Project: pappydapimp69/brain-auto-training
- Tags: [ai-video][compliance][testing][model]
- What: Three unapplied AI-VIDEO kernels (real product footage, platform-dependent AI label, verbatim character bible) can be enforced together as one shot-list lint, and the label rule differs by platform for the same cartoon video.
- Why built: The kernels were each stated in prose and never exercised; a single checkable shot list shows whether they conflict and where the platform split bites.
- Design: Each shot has a source (real or AI), product and character flags, a realistic flag and a prompt. Rules: product shots must be real; label needed if any realistic AI on YouTube, or any AI on TikTok with the label on by default; every AI shot with the character must contain the fixed descriptor string. Six cases over two platforms.
- Got right: The compliant list linted clean when labelled; the same list unlabelled tripped only the label rule on TikTok; a reference-image-only AI product shot tripped the product rule; a paraphrased character line tripped the bible rule.
- Where/why it failed: Nothing broke in the model, but the rules are my hand encoding of the kernels, so the run shows they can be checked mechanically and do not conflict, not that the platforms enforce them that way. The kernels themselves say TikTok's current page did not render, so the TikTok default is unverified.
- Fix: Keep the lint as a pre-publish step with a per-platform label rule rather than one global label rule, and keep the real or AI column on every shot.
- Why this fix: A single global rule either over-labels cartoons on YouTube or under-labels them on TikTok, so the platform must be an input.
- Rule of thumb: Check an AI product video as a shot list with a real or AI column, a verbatim bible string and a platform-specific label rule; the same unlabelled cartoon passed on YouTube and failed on TikTok. Encoded from the kernels, not from the platforms' live rules.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the platform rules are assumed from the kernels as written and were not re-read from the sources.
- Composed: ideas:AI-VIDEO/ai-for-scenes-and-dubbing-real-footage-for-the-product-plus-the-ai-label, ideas:AI-VIDEO/label-photoreal-ai-and-skip-the-label-for-obvious-cartoons-on-youtube, ideas:AI-VIDEO/locked-character-bible-pasted-verbatim-into-every-shot
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-17__ai-video-shot-list-lint-composes-three-rules.py
- Prediction: Assumption: one global label rule is enough for both platforms. I predicted an unlabelled cartoon-plus-real list would pass on YouTube and fail on TikTok, and that each of the other three rules would trip exactly once on its own broken case.
- Observed: RESULT: PASS 6 shot-list cases: compliant list clean; unlabelled realistic AI trips K2; reference-image-only product shot trips K1; paraphrased character block trips K3; unlabelled cartoon passes on YouTube but not TikTok
- Scenarios: 1) compliant list labelled on YouTube; 2) same list unlabelled on TikTok; 3) AI product shot with reference image only (built to BREAK the reference-image-is-enough assumption); 4) paraphrased character descriptor; 5) cartoon list unlabelled on YouTube; 6) cartoon list unlabelled on TikTok
- Link: brain train auto loop 2 pass 5; session_01LG4GQFTi9A1QxnCzb5c6CV

## E28 — age cutoff threshold shifts with jitter
- Date: 2026-10-17
- Project: pappydapimp69/brain-auto-training
- Tags: [ui][input][state][gamedev][testing]
- What: Sandbox composing the age-cutoff lossless threshold (largest valid-press lag) with the jitter amplitude sweep, asking where the lossless cutoff sits once observed lag is shifted by jitter.
- Why built: One entry says the cutoff is lossless at the max valid lag, the other (disputed) says it lost 0 at max lag across J=0..8; they look contradictory if jitter can delay a press.
- Design: Valid lags V=[4,8,12,20] (period 12); every lag meets every jitter offset in -J..+J, J=0..8; a cutoff drops presses whose observed lag exceeds it. Compared cutoffs at max lag, max+J, max+J-1 and the period, plus an early-only jitter case (offsets -J..0).
- Got right: Cutoff max+J lost 0 at all nine J; one below lost 1 at every J; the period cutoff lost 1 to 28 as J grew.
- Where/why it failed: The max-lag cutoff lost J presses for J=1..8 (0 only at J=0), so the lossless-at-max-lag rule does not survive late jitter. A first run with a short fixed jitter cycle missed offsets and falsely failed; the full cross product fixed it.
- Fix: Set the cutoff to max valid lag plus the largest late jitter, not the max lag alone; with only early jitter the max lag stays lossless (0 lost at all nine J).
- Why this fix: Observed lag is true lag plus jitter, so the worst case valid press is the max lag with maximum delay; the cutoff must cover it exactly, no more.
- Rule of thumb: Lossless age cutoff over a validity gate equals the largest valid lag plus the largest late jitter; the max-lag-only version holds just when jitter cannot delay. This reconciles the two entries rather than refuting either. Tested on one lag set, so treat the constant as the model's, not general.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the lag set and the uniform jitter model are assumed choices, not measured input traces.
- Composed: age-cutoff-lossless-threshold-exceeds-period-p12/E1, validity-cutoff-jitter-amplitude-sweep-sixth-angle/E1
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-17__age-cutoff-threshold-shifts-with-jitter.py
- Prediction: Assumption: the max-valid-lag threshold is independent of jitter. I predicted it would break, with max lag losing about J presses and max+J losing 0 for every J, while early-only jitter keeps max lag lossless.
- Observed: RESULT: PASS lossless threshold = max valid lag + J (0 lost at all J=0..8); max-only lost J for J=1..8; one below lost 1 each; period12 lost 1..28; early-only 0 lost at max
- Scenarios: 1) cutoff at max lag; 2) cutoff at max+J; 3) cutoff at max+J-1; 4) period cutoff; 5) early-only jitter with cutoff at max lag (built to BREAK the claim that late jitter is what shifts it)
- Link: brain train auto pass 2, loop 1; session_01LG4GQFTi9A1QxnCzb5c6CV
- Audited: 2026-10-17 · pass · Read the entry and ran its stored sandbox (RESULT: PASS reproduced). The model computes the dropped-press counts by enumerating every true lag against every jitter offset and comparing observed lag to each cutoff, so the loss numbers (0 at max+J, J at max-only, 1 one below) are counted, not stated. The result is close to arithmetic once observed lag is lag plus offset, but it is the claim's own definition, and the early-only scenario genuinely could have failed it. Scope matches the rule of thumb, which already says it is tested on one lag set and treats the constant as the model's; no real system is claimed, so modeled does not apply. · brain train auto loop 1 pass 3, session_01Jftxp3Xz4k4dPRx9kG19YD

## E27 — single peak vs stack flips with the score metric
- Date: 2026-10-15
- Project: pappydapimp69/brain-auto-training
- Tags: [comedy][humor][timing][sandbox]
- What: In a six-beat comic-arc model with a distance gate and habituation, 'one peak after a held pause' beats 'six stacked beats' only because the stack was given no pause: with a 3 s pause before only the peak, the single peak won on both total and peak response at all three distances (d 0.3, 0.6, 0.9), but when the stack also got a 3 s pause before every beat its total response was 1.364 versus 0.295 at d 0.3 (2.636 vs 0.540 at 0.6, 4.013 vs 0.789 at 0.9) and its peak only tied the single peak.
- Why built: New-half train pick: the premise checklist (wrong cue plus safe cue), the matched-distance escalation gate and the single-peak-with-a-held-pause kernel had never been run together; I wanted to know whether the single peak wins as a structure or because of the pause it is given.
- Design: Response per beat = (I/10) * exp(-0.2 X) * gate(d, I) * pause(p) with the gate and habituation copied from the escalation entry and pause(p) = 1 - exp(-p/1.5) as my own assumed shape; schedules SINGLE (five calm beats then one peak after a 3 s pause), STACK unpaused (0.2 s baseline), and STACK paused (3 s before each beat), intensity grid 0.5 to 10, scored by total and by largest single beat.
- Got right: The habituated, unpaused stack does lose to the single peak at 3 of 3 distances on both metrics, and the best intensity moves up with distance (I 4.0, 6.5, 9.5 at d 0.3, 0.6, 0.9), consistent with the matched-distance entry.
- Where/why it failed: I predicted the unpaused stack would win on total response and that the best single intensity at d 0.3 would be 3.0; the stack lost (0 of 3) and the best intensity was 4.0, because the pause term multiplies each beat by 0.13 when unpaused. My first scenario compared unlike things (pause vs no pause), and when a bug in the paused-stack scenario made it copy the single arc I caught that by its identical numbers and fixed it before filing.
- Fix: Compare the single peak with a stack that gets the same pause per beat or the same total runtime, and score both total and peak; do not credit the single-peak structure with an advantage that belongs to the pause.
- Why this fix: The pause term is a per-beat multiplier in this model, so any schedule without it is handicapped; only an equal-pause or equal-runtime comparison separates structure from pause, and equal runtime is what a 30 s short actually has (18 s of stillness for six paused beats is not available).
- Rule of thumb: Do not claim one peak beats stacking until the stack gets the same pause: here the single peak won 3 of 3 against an unpaused stack but lost on total response (0.295 vs 1.364 at d 0.3) and only tied on peak against a stack paused before every beat, at 18 s of stillness against 3 s.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the pause shape, the 0.2 s baseline, the gate width and the response product are my assumed model, and the kernel's single-peak claim is correlational, so only the dependence on the pause term is a finding, not any comedy outcome.
- Composed: ideas:COMEDY/premise-design/an-absurd-premise-needs-a-wrong-cue-and-a-safe-cue, escalation-needs-matching-distance/E1, ideas:COMEDY/timing/one-peak-violation-with-a-held-pause
- Picked-by: new-half
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-15__single-peak-vs-stack-flips-with-the-score-metric.py
- Prediction: The stack wins on total response and the single peak wins on peak response at every distance, and the best single intensity at d 0.3 is 3.0; assumption: the two metrics agree on the winner; the equal-pause stack was added after the first run showed the unpaused stack handicapped.
- Observed: RESULT: FAIL unpaused stack wins by sum at 0/3 distances, single wins by peak at 3/3; stack with a pause before every beat wins by sum at 3/3 (costs 18 s of stillness vs 3 s); single d=0.3 p=1.5 best I=4.0 score 0.215
- Scenarios: 1) SINGLE peak after a 3 s pause at d 0.3, 0.6, 0.9; 2) STACK unpaused at the same distances; 3) STACK with a 3 s pause before every beat (BREAK: removes the pause advantage); 4) SINGLE with a 1.5 s pause at d 0.3
- Link: brain train auto loop 2 pass 2; session_01USEQKxFedmHB9RNfo9RMD6

## E26 — magic square three constructions by n mod 4
- Date: 2026-10-15
- Project: pappydapimp69/brain-auto-training
- Tags: [magic-squares][algorithm][testing][sandbox]
- What: Seeded the MAGIC-SQUARES domain: a magic-square generator has to pick its construction by n mod 4. In a stdlib check that tested every row, column, both diagonals and the 1..n^2 set, the Siamese method was valid for 8 of 8 odd n (3 to 17) and 0 of 6 even n (4 to 14), the complement-the-diagonals method was valid for 3 of 3 multiples of 4 (4, 8, 12), and Strachey's method for n = 2 mod 4 was valid for 3 of 3 (6, 10, 14) but 0 of 3 with its swap step removed.
- Why built: New-domain training pass: a domain with no records cannot be gap-checked, so it is seeded from a concrete task (a generator that must emit a valid square at any size) whose claim a script can fully verify.
- Design: One validator (sum, column, diagonal and permutation checks) run against four builders; the even-n Siamese run is real, not skipped (my first draft hardcoded that row to False, which would have passed by construction, and I fixed it before filing); the no-swap Strachey run is built to BREAK the idea that the swap is cosmetic.
- Got right: Every prediction held, including that the swap is load-bearing (0 of 3 valid without it) and that Siamese fails on all six even sizes tried.
- Where/why it failed: Nothing in the sandbox failed; the gap is scope, since only n up to 17 was tested, only one Strachey layout was checked, and n = 2 (no magic square exists) was not run.
- Fix: Dispatch on n mod 4 (odd, 0, 2) and run the validator on every emitted square rather than trusting the method for the size.
- Why this fix: The three constructions rest on different structure (a carry rule, a diagonal complement, a quadrant swap), so one method cannot cover all n, and a validator is cheap against a silent invalid square.
- Rule of thumb: Choose the magic-square construction by n mod 4 and validate the output: Siamese covered 8 of 8 odd sizes but 0 of 6 even ones, and Strachey for n = 2 mod 4 fails 3 of 3 sizes without its swap step.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; sizes beyond n = 17 and the n = 2 edge were not run.
- Composed: N/A
- Picked-by: new-domain
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__magic-square-three-constructions-by-n-mod-4.py
- Prediction: Siamese valid for 8 of 8 odd n and 0 of 6 even n, doubly-even 3 of 3, Strachey 3 of 3 and 0 of 3 without the swap; assumption: one method fits all n, wrong if Siamese is valid for any even n or the no-swap Strachey for any n.
- Observed: RESULT: PASS siamese odd 8/8, siamese even 0/6, doubly-even 3/3, strachey 3/3, strachey without swap 0/3
- Scenarios: 1) Siamese odd n 3 to 17; 2) Siamese on even n 4 to 14; 3) doubly-even n 4, 8, 12; 4) Strachey n 6, 10, 14; 5) Strachey without the swap (BREAK: swap is cosmetic)
- Link: brain train auto loop 1 pass 6 (newdomain); session_01USEQKxFedmHB9RNfo9RMD6

## E25 — fake ad batch invented names need lookalike gate
- Date: 2026-10-15
- Project: pappydapimp69/brain-auto-training
- Tags: [game-ads][comedy][legal][sandbox]
- What: A fake-ad batch of 8 built from distinct slot-machine cells passes the label check (2 of 8 axis labels non-verbatim before the fix, 0 after) and the not-templated check (mean pair similarity 0.143 vs 1.0 for a name-swap-only batch), but invented names drawn from a syllable pool did NOT pass the invent-every-name check by construction: 1 of 8 ('Gardloscape') sat within edit distance 3 of a real game (Gardenscapes).
- Why built: New-half train pick: the 'every video gets its own joke' kernel plus the kernel source-check lesson, with the 'parody the genre, not the brand' kernel as the companion never tested alongside them; the question was whether the three gates can be run as one batch pipeline and whether passing one implies the others.
- Design: Deterministic stdlib script: 6 tropes x 5 axes with the Penn State labels verbatim, 8 distinct cells, names from a syllable pool checked against a 20-name real-game list (exact, edit distance <=3, shared distinctive word), pair similarity as the share of 6 content fields that match, plus a reject-and-redraw rerun.
- Got right: The label fix changed no cell identity (6 of 6 cell checks kept), the composed batch stayed far below the name-swap-only 1.0 similarity, and reject-and-redraw cleared the name flag (0 of 8) without moving similarity (0.143 before and after).
- Where/why it failed: I predicted all three gates pass together with independent generators. The name gate failed: made-up syllable names are not automatically distinct from real brands, so 'invented' is a claim about the process while the gate is about the result.
- Fix: Run the lookalike screen (edit distance plus distinctive-word overlap) on every generated name and redraw hits before the name enters the batch, independent of the label and similarity checks.
- Why this fix: The three gates fail for different reasons and a pass on labels or similarity says nothing about names; redrawing changed only the name field, so it costs no joke variety.
- Rule of thumb: Passing the label and not-templated gates does not clear the names: syllable-pool names hit a lookalike in 1 of 8 here, so screen every generated name against real titles and redraw hits (not legal clearance).
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the real-game list has only 20 names and the 1-in-8 rate is for this pool and seed, so it is not a population estimate.
- Composed: fake-ad-kernel-source-check/E1, ideas:AI-VIDEO/every-video-gets-its-own-joke-and-script, ideas:LEGAL/parody/parody-the-genre-not-the-brand
- Picked-by: new-half
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-15__fake-ad-batch-three-gates.py
- Prediction: All three gates pass together on 8 distinct cells: 0 bad labels after fix, 0 lookalike names, mean pair similarity under 0.50; assumption: the gates are independent so one passing says nothing of the others, and it breaks if the name pool flags any name.
- Observed: RESULT: FAIL label 2->0, wide names flagged 1/8 (redraw 0/8), narrow 1/8, sim composed 0.143 vs name-swap 1.0
- Scenarios: 1) kernel label vs source label; 2) wide name pool; 3) narrow name pool, built to BREAK the invented-name claim; 4) distinct-cell batch similarity; 5) name-swap-only batch; 6) cell identity after label fix; 7) redraw flagged names
- Link: brain train auto loop 1 pass 1; session_01USEQKxFedmHB9RNfo9RMD6

## E24 — engine trope breadth binds the batch ceiling
- Date: 2026-10-15
- Project: pappydapimp69/brain-auto-training
- Tags: [comedy][game-ads][testing][sandbox]
- What: The fake-ad batch ceiling of min(16, 6R) holds while every engine can reach at least 2 tropes, but if each engine is tied to a single trope the ceiling at a trope cap of 3 is 14, not 16 (6, 12, 14, 16 for caps 1 to 4), because tropes 0 and 1 then own 4 engine-skeleton slots while tropes 2 to 5 own only 2; windows of 6, 3 and 2 tropes per engine all gave 6, 12, 16, 16.
- Why built: New-half train pick: the batch-ceiling entry named one untested case, an engine restricted to whole tropes, and the per-video-joke rule and the closed-label rule decide whether such a restriction is real and checkable.
- Design: My own fixture, not the max-flow script: 8 engines x 2 skeletons = 16 slots, each slot allowed a cyclic window of w tropes out of 6, each trope capped at R videos, ceiling computed by augmenting-path b-matching, windows 6, 3, 2 and 1, caps 1 to 4, no randomness.
- Got right: The open case reproduces the earlier entry exactly (6, 12, 16, 16), and the hand-derived w=1 prediction (14 at R=3, from 2+2+2+2+3+3 slot limits) matched the run.
- Where/why it failed: Nothing failed; the limit is that the cyclic window with 8 engines over 6 tropes is a deliberately uneven assignment, so the 14 is specific to that 4-4-2-2-2-2 slot split, and a window that spreads engines evenly would not bind.
- Fix: When engines are tied to tropes, count the slots each trope can actually draw before choosing the trope cap: the ceiling is the sum over tropes of min(R, slots that can reach it), and add a second engine or skeleton to the thinnest trope instead of raising the cap.
- Why this fix: The binding limit moved from the cap to the thinnest trope's slot count, so only adding slots there relaxes it; raising R past that point adds nothing.
- Rule of thumb: The 6R batch ceiling assumes engines can reach 2 or more tropes: with each engine tied to one trope the ceiling at cap 3 fell from 16 to 14 (slots per trope 4,4,2,2,2,2), so count slots per trope before raising the cap.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the cyclic engine-to-trope windows and the 8 engines, 2 skeletons and 6 tropes are assumed or carried from the earlier entries, and no real batch was built.
- Composed: ideas:AI-VIDEO/monetization-policy/every-video-gets-its-own-joke-and-script, fake-ad-kernel-source-check/E1, batch-ceiling-trope-cap/E1
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__engine-trope-breadth-binds-the-batch-ceiling.py
- Prediction: Windows of 6, 3 and 2 tropes give 6, 12, 16, 16; one trope per engine gives 6, 12, 14, 16 so a cap of 3 no longer reaches 16; assumption: the ceiling depends on the trope cap only, wrong if the one-trope case gives 16 at cap 3.
- Observed: RESULT: PASS open [6, 12, 16, 16], w=2 [6, 12, 16, 16], w=1 [6, 12, 14, 16] (R=3 gives 14, not 16)
- Scenarios: 1) open engines (w=6); 2) three-trope windows; 3) two-trope windows; 4) one trope per engine (BREAK: the cap-3 advice); each at caps 1 to 4
- Link: brain train auto loop 2 pass 5; session_01USEQKxFedmHB9RNfo9RMD6

## E23 — engine cap check needs verbatim engine labels
- Date: 2026-10-15
- Project: pappydapimp69/brain-auto-training
- Tags: [comedy][game-ads][testing][sandbox]
- What: A label-count check of the engine-repeat cap (ceil(k/8)) silently stops working when ideas paraphrase their engine: in 2000 simulated 16-idea batches that truly repeat one engine 3 times (cap 2), a free-text label counter missed the breach 48.4% of the time at a 0.2 paraphrase rate, 76.8% at 0.4 and 90.0% at 0.6, versus 0.0% at rate 0; a closed engine vocabulary that bounces unknown labels missed none but sent back 20% to 60% of the ideas.
- Why built: New-half train pick: the vary-the-engine kernel says to check a batch for repeated engines, the source-check lesson says paraphrased labels break lookups, and the engine-repeat lesson says a repeat past 8 ideas is forced; I wanted to know whether the repeat check itself depends on verbatim labels.
- Design: Stdlib simulation with a fixed seed: 8 engines, 16 ideas per batch with one engine planted 3 times, each idea paraphrased with probability 0, 0.2, 0.4 or 0.6 from a synonym table, then compared a plain label counter against a closed-vocabulary check that bounces unknown labels for relabelling.
- Got right: At paraphrase rate 0 the two checks agree exactly (0 misses), so the miss rate is caused by paraphrase and not by the counter; the prediction of at least 30% misses at rate 0.4 held (got 76.8%).
- Where/why it failed: The closed-vocabulary result of 0 misses is by construction, because the bounced idea is relabelled with its true engine; real authors may relabel wrongly, so that 0 is an upper bound on the benefit and the bounce cost (about equal to the paraphrase rate) is the real price.
- Fix: Keep the engine list as a closed vocabulary with verbatim names, store the engine on each idea as one of those names, and bounce any idea whose label is outside the list before running the repeat count.
- Why this fix: The count is exact only over identical strings, so the vocabulary makes the check exact at the one place paraphrase enters; the cost is relabelling work, not lost jokes.
- Rule of thumb: Run the engine-repeat cap on a closed list of verbatim engine names: with free-text labels a 16-idea batch that really repeats an engine 3 times slipped past the counter in 48% to 90% of runs once 20% to 60% of ideas paraphrased their engine.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the paraphrase rates, the synonym table and the planted 3-repeat batch are my assumed model, not measured author behaviour.
- Composed: ideas:COMEDY-CRAFT/ideation/vary-the-comic-engine-not-the-topic, fake-ad-kernel-source-check/E1, engine-repeat-above-eight-needs-new-skeleton-not-new-topic/E1
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__engine-cap-check-needs-verbatim-engine-labels.py
- Prediction: At a 0.4 paraphrase rate the free-text counter misses at least 30% of true cap breaches at k=16 while the closed vocabulary misses 0%; at rate 0 both miss 0% (built to BREAK the claim that the checker is the cause). Assumption: the check counts label strings.
- Observed: RESULT: PASS free-text miss at 0.4 = 0.768 (at 0.0 = 0.000), closed-vocab miss = 0.000, bounced 0.401
- Scenarios: 1) paraphrase rate 0 (BREAK: no paraphrase, both checks agree); 2) rate 0.2; 3) rate 0.4; 4) rate 0.6
- Link: brain train auto loop 1 pass 2; session_01USEQKxFedmHB9RNfo9RMD6

## E22 — domino tiling colour count decides removed squares
- Date: 2026-10-15
- Project: pappydapimp69/brain-auto-training
- Tags: [tiling][algorithm][testing][sandbox]
- What: For a domino-tiling board generator, the checkerboard colour count of the cells left decided tileability in every case an exhaustive count tried: the opposite-corner board had 0 tilings at 4x4, 6x6 and 8x8, none of the 56 same-colour pairs on 4x4 or 306 on 6x6 tiled, all 64 and 324 mixed-colour pairs did tile, and on 5x5 and 7x7 with one square removed exactly the majority-colour squares tiled (13 and 25).
- Why built: New-domain training pass: TILING had no records, so it is seeded from a concrete task (a puzzle generator that must only emit tileable boards) whose claim a script can verify exhaustively instead of by quoting the classic argument.
- Design: A memoised bitmask count of domino tilings with removed cells, checked first on full boards (36, 6728, 12,988,816), then on the opposite-corner boards, every pair of removed squares on 4x4 and 6x6 split by colour, and every single removal on 5x5 and 7x7; no randomness.
- Got right: The full-board counts matched the known values and no colour-balanced pair on 4x4 or 6x6 failed to tile, so the colour count was a sufficient and necessary pre-check on these sizes.
- Where/why it failed: Two of my own errors: my first counter let a vertical domino overlap a removed cell below, which wrongly reported 26 same-colour 4x4 pairs and 206 on 6x6 as tileable (the impossible result exposed it), and my prediction that no odd-side single removal tiles was wrong because 5x5 minus one square has 24 cells, even area, so majority-colour removals do tile (13 of 25 and 25 of 49).
- Fix: Run the colour count first and the search only when counts are equal; on odd sides accept a single removal only on the majority colour; treat a counter that finds a tiling the colour argument forbids as a bug in the counter.
- Why this fix: The colour test is O(cells) and exact on every size tried, while the counting search is exponential, so the cheap necessary test should gate the expensive one; the impossible result is also a free correctness check on the counter.
- Rule of thumb: Before searching for a domino tiling, compare the two checkerboard colour counts: here equal counts tiled in 388 of 388 pairs on 4x4 and 6x6, unequal counts tiled in 0 of 362, and an odd board minus one square tiled only on the majority colour (13 of 25, 25 of 49).
- Provenance (verified/assumed): Verified first-hand by running the sandbox; sizes above 8 and boards with more than two removed squares were not run, and I corrected the counter and the odd-side prediction after the first runs.
- Composed: N/A
- Picked-by: new-domain
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__domino-tiling-colour-count-decides-removed-squares.py
- Prediction: Opposite corners untileable at 4, 6, 8; every mixed-colour pair tiles on 4x4 and 6x6; full counts 36, 6728, 12988816; an odd side with one removal tiles in 0 cases (wrong: it tiles on the majority colour, 13 and 25); assumption: colour balance is necessary but maybe not sufficient.
- Observed: RESULT: PASS full [36, 6728, 12988816], opposite corners [0, 0, 0], 4x4 mixed-colour pairs untileable 0/64 and same-colour tileable 0, 6x6 untileable 0/324 and same-colour tileable 0, odd sides tileable single removals [13, 25] (all and only the majority-colour squares: True; my prediction of 0 was wrong, n*n-1 is even)
- Scenarios: 1) full boards 4, 6, 8; 2) opposite-corner boards 4, 6, 8; 3) every same-colour and mixed-colour pair on 4x4 and 6x6; 4) every single removal on 5x5 and 7x7 (BREAK: the odd-area prediction)
- Link: brain train auto loop 2 pass 6 (newdomain); session_01USEQKxFedmHB9RNfo9RMD6

## E21 — axis swap position sets same trope similarity
- Date: 2026-10-15
- Project: pappydapimp69/brain-auto-training
- Tags: [comedy][game-ads][testing][sandbox]
- What: Two slot-machine cells on the same trope with different axes are not the one-beat variant of each other: in the toy similarity model each differs from the base skeleton by one beat (0.60, or 0.78 when the swap lands on beat 0), but against each other they differ by two beats and scored a mean 0.433 (min 0.333, max 0.600), with only 1 of 10 axis pairs reaching the 0.6 flag; a 7-idea batch of distinct cells forced to repeat one trope peaked at 0.455 versus 0.067 for 6 ideas, one per trope.
- Why built: New-half train pick: the slot-machine kernel, the source-check lesson and the engine-repeat lesson, where a one-beat variant sat on the flag line at 0.60; I wanted to know whether rotating cells without replacement inherits that borderline score when a trope has to repeat past 6 ideas.
- Design: Same assumed model as the engine-repeat entry (Jaccard over beat bigrams plus voice, layout, endpoint, length; flag at 0.6), with each of the five verbatim axes mapped to one swapped beat of a 5-beat trope skeleton; scored the swap beat 0 to 4 against the base, all 10 same-trope axis pairs, a 6-cell and a 7-cell batch, and the kernel's 'borrowed fame' label against the verbatim map.
- Got right: A trope repeat is cheaper than the earlier 0.60 suggested, so a batch of 7 distinct cells stays well under the flag (0.455), and the 'borrowed fame' label cannot be mapped to a swap beat at all (1 of 5 axes unresolved), which confirms the source-check lesson reaches the generator.
- Where/why it failed: I predicted a repeat-trope cell would score about 0.6 or more and that edge swaps score 0.78; the max pair was 0.600 and only beat 0 scored 0.778, because a swap at beat 4 also moves the endpoint (0.600), and the repeat pair differs in two beats rather than one.
- Fix: Judge a same-trope repeat by the pair of cells (both swapped beats), not by one cell against the base, and prefer axes that swap different beats; treat a hook-beat (beat 0) axis as the one most likely to look templated against the base.
- Why this fix: Similarity here is computed between ads in a batch, so the base skeleton is never an ad; the pair score is what the check would compare, and it drops with each extra differing beat.
- Rule of thumb: In the toy model a same-trope repeat with a different axis scored a mean 0.43 (1 of 10 pairs at the 0.6 flag), well below the 0.60 one-beat-variant figure, so the 7th idea of a rotated batch is not the template risk that figure implies; score pairs of cells, not cell versus base.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the feature set, the axis-to-beat map and the 0.6 flag are my assumed model, carried over from the earlier entry, not a platform detector or viewer data.
- Composed: ideas:COMEDY/fake-mobile-ad/premise-slot-machine-from-the-five-misleading-ad-patterns, fake-ad-kernel-source-check/E1, engine-repeat-above-eight-needs-new-skeleton-not-new-topic/E1
- Picked-by: new-half
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-15__axis-swap-position-sets-same-trope-similarity.py
- Prediction: A repeat-trope distinct cell scores about 0.6 or more against its sibling (flagged), edge swaps score about 0.78 and middle swaps 0.60; assumption: the swap beat is a free choice and siblings differ by one beat; wrong if the pair max stays under 0.5.
- Observed: RESULT: FAIL edge-swap mean 0.689 vs middle-swap 0.600; k=6 max 0.067, k=7 max 0.455; unresolved kernel labels 1
- Scenarios: 1) one-beat variant vs base for swap beat 0 to 4; 2) all 10 same-trope axis pairs (BREAK: sibling cells, not cell vs base); 3) 6 cells one per trope; 4) 7 distinct cells with one trope repeated; 5) kernel label 'borrowed fame' against the verbatim axis map
- Link: brain train auto loop 1 pass 5; session_01USEQKxFedmHB9RNfo9RMD6

## E20 — written commitment premium closes only a temptation band and a partial recap redirects retreat
- Date: 2026-10-15
- Project: Pappydapimp69/brain-auto-training
- Tags: [negotiation][model][sandbox]
- What: A deterministic threshold model of the written-vs-verbal commitment kernel composed with the BATNA kernel:
  the counterparty walks back when a new alternative beats the deal by more than its walk-back cost
  (verbal 1, written 2). Writing cut reneging from 0.177 to 0.033 under moderate shocks, but only
  0.984 to 0.889 under large ones, and a recap email that covered 2 of 3 terms put 73% of retreats
  on the unwritten term.
- Why built: The kernel says to turn every verbal agreement into a written recap at once because writing
  strengthens commitment, and it has never been applied by a lesson. Its hidden premise is that
  the written premium matters regardless of how much better the other side's alternative becomes,
  which the BATNA kernel suggests is false: a strong enough walk-away option should beat any
  fixed consistency cost.
- Design: Stdlib, no random draws: the temptation gain from the counterparty's new alternative is taken from
  an exact 2000-point lognormal quantile grid (sigma 0.75) at a chosen median. Renege when gain
  exceeds the walk-back cost. Costs verbal 1 and written 2 are ASSUMED units, not from a study; the
  kernel itself names no effect size. Partial recap: 3 terms, each with its own temptation (one
  third of a rotated gain), terms A and B written, C verbal. Sweep of medians 0.25 to 13.
- Got right: The kernel's direction holds in its zone: with modest alternatives writing cut reneging by 82%
  relative (0.177 to 0.033) and at median 1.5 by 0.355 absolute, the peak. Writing every term
  cut total retreats from 1065 (none written) to 195; writing 2 of 3 still left 485.
- Where/why it failed: The premium is a band, not a constant. Past the written cost it fades: at median 5 the cut is
  only 10% relative (0.095 absolute) and from median 8 under 0.05 absolute (0.029), because a
  strong enough alternative clears any fixed consistency cost. Below the verbal cost it is also
  small (0.030 at median 0.25) since nobody walks anyway. A partial recap did not just weaken the
  deal; it steered 355 of 485 retreats (0.73) onto the one unwritten term.
- Fix: Write the recap when the other side's alternatives are improving modestly, and write every term,
  not the headline ones, since the gaps draw the reopening. When their alternative is improving a
  lot, do not rely on the paper: work on your offer or your own BATNA, which is what moves the
  outcome there.
- Why this fix: In the model the commitment premium only bites for temptations between the verbal and written
  costs, so its value depends on where the counterparty's outside options sit; and per-term
  costs mean an omitted term is the cheapest place to retreat, so coverage matters as much as
  the act of writing.
- Rule of thumb: A written recap only blocks walk-backs whose gain falls between the verbal and written cost: it
  cut reneging 82% for small outside offers but 10% for large ones (under 0.05 absolute past 8x
  the verbal cost), and a recap missing one of 3 terms drew 73% of retreats onto that term.
- Provenance (verified/assumed): Verified first-hand: the sandbox 2026-10-15__written-commitment-premium-closes-only-a-temptation-band-and-a-partial-recap-redirects-retreat.py
  printed every number above (0.177 to 0.033, 0.984 to 0.889, 355 of 485, peak 0.355 at median
  1.5, fade below 0.05 from median 8). The cost values and lognormal shocks are model inputs
  named in Design.
- Composed: ideas:NEGOTIATION/commitment/written-vs-verbal/a-written-commitment-is-harder-to-walk-back-than-a-spoken-one, ideas:NEGOTIATION/batna/walk-away-power/power-comes-from-your-walk-away-alternative-not-willpower
- Picked-by: current-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__written-commitment-premium-closes-only-a-temptation-band-and-a-partial-recap-redirects-retreat.py
- Prediction: Written before the first run. Hidden assumption under test: the written premium is useful
  whatever the counterparty's alternative is worth. Expected: moderate shocks (median 0.5) cut
  reneging by more than 50% relative; large shocks (median 5) by under 20% relative and under 0.10
  absolute; a recap covering 2 of 3 terms puts over 70% of retreats on the unwritten one; and a
  sweep finds a median past the peak where the absolute premium drops under 0.05. It would be
  wrong if the large-shock relative cut stayed above 20%.
- Observed: RESULT: PASS moderate rel cut 0.82 (0.177->0.033), large rel cut 0.10 abs 0.095, partial recap 0.73
  of retreats on the unwritten term, premium <0.05 from median 8. Sweep abs premium 0.030, 0.145,
  0.323, 0.355, 0.323, 0.223, 0.095, 0.029, 0.006 at medians 0.25 to 13. Total retreats 1065 none
  written, 485 two written, 195 all written. The 0.73 share was close to the 0.70 line.
- Scenarios: 1) moderate outside offers, median 0.5; 2) large outside offers, median 5, built to BREAK the
  kernel's always-write advice; 3) recap email covering 2 of 3 terms; 4) sweep of offer size 0.25
  to 13 to find where the premium fades on both sides
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 5 pass 1

## E19 — vei from dre instead of bulk tephra drops boundary eruptions a class
- Date: 2026-10-15
- Project: Pappydapimp69/brain-auto-training
- Tags: [volcanology][measurement][classification][sandbox]
- What: The Volcanic Explosivity Index bins bulk tephra volume by decade (VEI 1 spans two). Feeding it the
  dense-rock-equivalent (DRE) volume instead, which is 2 to 5 times smaller, dropped Mount St. Helens
  1980, Pinatubo 1991 and Tambora 1815 one class each (5 to 4, 6 to 5, 7 to 6) while bulk volume
  reproduced all 5 listed classes. Over log-uniform eruptions a factor of 2.5 moves 39.8% of them.
- Why built: New domain seed (volcanology was empty in Brain: volcano, volcanic, eruption and tephra all
  returned 0 memory). Papers and summaries quote both bulk and DRE volumes for the same eruption, often
  side by side, and the VEI table only says 'volume', so a classifier or a game or teaching tool that
  takes whichever number is handy can silently mislabel the eruptions people most often cite.
- Design: Stdlib. VEI table per Newhall and Self 1982 (under 1e4 m3 is 0, 1e4 to 1e6 is 1, then one class per
  decade to 8 at 1e12 or more), checked at 11 boundary values. Magnitude per Pyle, M = log10(mass in
  kg) - 7, using deposit density 1000 for bulk and magma density 2500 for DRE (assumed typical
  values). Eruption volumes are values I recalled, NOT fetched this session: St. Helens bulk 1.1 /
  DRE 0.25 km3, Pinatubo bulk 10.4 or 8.4 / DRE 5.3 or 3.7, Tambora 150 / 30, Krakatau 20 / 10,
  Eyjafjallajokull 0.27 / 0.12. A 60,000-point log-uniform sweep from 1e6 to 1e12 m3.
- Got right: Bulk volume gave the listed VEI for 5 of 5 eruptions, and DRE dropped exactly the 3 I predicted
  (St. Helens, Pinatubo, Tambora) while Krakatau and Eyjafjallajokull stayed put. The population
  share that shifts equals log10(f): 0.301 at f=2, 0.398 at 2.5, 0.602 at 4.
- Where/why it failed: My magnitude prediction missed by a hair: I expected the bulk and DRE routes to agree within 0.3
  for all eruptions and Tambora gave exactly 0.30 (7.18 vs 6.88), because its recalled bulk/DRE ratio
  is 5, not the 2.5 the densities imply, so the inputs are not mutually consistent. Also Pinatubo's own
  class is on a knife edge: the low bulk estimate 8.4 km3 gives VEI 5, the high 10.4 gives 6.
- Fix: Classify VEI only from bulk tephra volume and label which volume a number is before using it; for
  an eruption whose bulk estimate lies within the uncertainty factor of a decade boundary, report the
  VEI as a range (Pinatubo 5-6); and compare sizes on the mass-based magnitude, which moved at most
  0.30 between routes while VEI moved a full class.
- Why this fix: The VEI is a step function of log volume, so a constant factor of f shifts a log10(f) share of
  all eruptions by a class; magnitude is continuous and carries density explicitly, so mixing bulk
  and DRE costs only the density mismatch, a fraction of one unit.
- Rule of thumb: Compute VEI from bulk tephra volume, never DRE: DRE (2-5x smaller) dropped St. Helens, Pinatubo and
  Tambora a full class and would shift 40% of eruptions at f=2.5; give a VEI range when the bulk
  estimate straddles a decade (Pinatubo 8.4 to 10.4 km3 is VEI 5-6).
- Provenance (verified/assumed): Verified first-hand: the sandbox 2026-10-15__vei-from-dre-instead-of-bulk-tephra-drops-boundary-eruptions-a-class.py
  printed bulk 5/5 matches, 3 DRE drops, shifted shares 0.301, 0.398, 0.602, magnitude gap 0.30 and
  Pinatubo 5/6. The eruption volumes and densities are recalled inputs named in Design.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__vei-from-dre-instead-of-bulk-tephra-drops-boundary-eruptions-a-class.py
- Prediction: Written before the first run. Hidden assumption: bulk and DRE are interchangeable 'eruption volume'
  for classification. Expected: bulk reproduces 5/5 listed VEI; DRE drops exactly 3 (St. Helens,
  Pinatubo, Tambora); magnitude by the two routes agrees within 0.3 for every eruption; log-uniform
  share shifted at f=2.5 equals log10(2.5) = 0.398 within 0.01. Wrong if DRE dropped none.
- Observed: RESULT: FAIL bulk volume reproduces listed VEI 5/5; DRE drops 3 (Mount St. Helens 1980, Pinatubo 1991
  (high bulk est.), Tambora 1815); magnitude bulk-vs-DRE gap max 0.30; log-uniform fraction shifted by
  DRE at f=2.5: 0.398; Pinatubo low/high bulk VEI 5/6. The FAIL is only the magnitude line (Tambora
  0.30, not under 0.3); every VEI expectation held. Criterion left unchanged.
- Scenarios: 1) five real eruptions classified from bulk; 2) the same from DRE; 3) magnitude by both routes,
  built to BREAK the claim that magnitude is route-proof (Tambora 0.30 dented it); 4) log-uniform
  population at f = 2, 2.5, 4; 5) VEI 1 spanning two decades and Pinatubo's two bulk estimates
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 5 pass 4

## E18 — thrashing cache one slot short makes mid life garbage that generational gc promotes
- Date: 2026-10-15
- Project: Pappydapimp69/brain-auto-training
- Tags: [performance][caching][memory][sandbox]
- What: Ran a loop-sized LRU cache under a generational garbage-collector model. A 59-slot cache on a 60-item
  loop got 0 hits, promoted 5980 entries to the old generation and forced 33 major collections, for 19,188
  units of GC work. The 60-slot cache did 120 units with 0 majors, and so did 61 slots. A 4-slot cache on a
  5-item loop also got 0 hits but caused 0 majors, because its entries died young.
- Why built: Bridge from the current-half cache-size-sweep lesson, which held. local__gc-cost-vs-loop-sized-cache
  E1 priced GC as a pause linear in live slots and left generational collection out. The GC kernel says
  generational GC relies on objects dying young and does badly when they outlive promotion and then die.
  That is exactly what the entries of a thrashing cache do. This gap was not yet tested.
- Design: Stdlib. An LRU OrderedDict cache, and 6000 accesses cycling a loop. Each access allocates 4
  temporaries that die at once; a miss allocates an entry and evicts one, which dies at that moment. The
  young generation collects every Y=100 allocations and copies survivors at cost 1 each, and objects that
  survive T=2 minors are promoted. The old generation runs a major collection at 200 objects, costing old
  objects scanned. All of these constants are assumed. Cases: 60/60, 60/59, 5/4, 60/59 with Y=400, and
  60/61. A sweep runs thrashing caches with loop = size+1 from size 5 to 59.
- Got right: The cache kernel and E1 held: 59 slots on a 60-loop got 0 hits and 60 slots got 5940. Sizing to the
  loop also fixed the GC: 0 majors and 120 units of work against 33 majors and 19,188. A 4x young
  generation removed the majors (0 promoted, 4425 work) but raised peak heap from 319 to 459 and worsened
  promptness from 25.3 to 39.5 accesses. That is the kernel's footprint and promptness tradeoff, shown
  directly.
- Where/why it failed: The assumption that a cache's GC cost scales with how many entries it holds is false. GC cost
  depends on entry lifetime relative to the promotion age. The same zero-hit thrash cost 0 majors at sizes 5
  to 20 and 7, 15, then 33 majors at sizes 25, 30 and 40 and above. The cliff sits where an entry's lifetime
  (cache size divided by miss rate, in accesses) passes about T minor periods. All costs are model units,
  and no real JVM, V8 or CPython collector was measured.
- Fix: For a GC'd runtime, size a looping cache to the loop. A cache one slot short is worse than no cache,
  because it turns every miss into old-generation garbage. If the loop length is unknown or too big, keep
  the cache small enough that entries die young, or store entries off-heap or in a preallocated array. A
  bigger young generation also works, but it costs footprint and promptness.
- Why this fix: A hitting cache allocates nothing after warm-up, so its 60 entries are promoted once and never die. A
  thrashing cache allocates on every access, and an entry that lives longer than about T minor periods is
  copied twice, promoted, and dies in the old generation, which only major collections reclaim.
- Rule of thumb: A looping cache one slot too small costs GC as well as hits: 59 slots on a 60-loop promoted 5980
  entries and forced 33 majors (19,188 work against 120). The same thrash at 4 slots cost 0 majors because
  entries died young, so lifetime against promotion age sets the GC bill, not cache size.
- Provenance (verified/assumed): Verified first-hand: the sandbox printed RESULT: PASS 5/5. It gave 0 majors and 120 work at
  60/60, 33 majors, 5980 promoted and 19,188 work at 60/59, 0 majors at 5/4, 0 majors at Y=400 with peak 459
  vs 319 and promptness 39.5 vs 25.3, and the cliff first at size 25 in the sweep.
- Composed: ideas:CACHE-EVICTION/replacement-policy/lru-beats-fifo-on-a-hot-set-but-both-score-zero-on-a-loop-one-slot-too-big/size-the-cache-to-the-loop-not-the-policy, local__sandbox-cache-size-sweep-loop-cliff-and-ram-ceiling/E1, ideas:PERFORMANCE/memory/garbage-collection/gc-tuning-is-a-tradeoff-between-four-competing-goals
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__thrashing-cache-one-slot-short-makes-mid-life-garbage-that-generational-gc-promotes.py
- Prediction: Hidden assumption: a cache's GC cost scales with how many entries it holds, so a smaller cache is
  cheaper for the GC. Written before running, I expected 0 majors at 60/60, at least 20 majors at 60/59, and
  0 majors at 5/4 even though it also gets 0 hits. I expected Y=400 to give 0 majors with a higher peak heap
  and worse promptness, and 60/61 to give 0 majors. A 59-slot thrash with no more majors than the 4-slot one
  would have kept the assumption.
- Observed: RESULT: PASS 5/5; loop60: cache60 majors 0 work 120, cache59 majors 33 promoted 5980 work 19188;
  loop5/cache4 majors 0; Y400 majors 0 peak 459 vs 319 promptness 39.5 vs 25.3; thrash GC cliff first at
  size 25. The sweep gave 0 majors at sizes 5-20 and 7/15/33/33/33 at 25/30/40/50/59. Max pause was 219 at
  60/59 against 40 at 60/60.
- Scenarios: 1) loop 60 with cache 60, which fits; 2) BREAK: loop 60 with cache 59, one short; 3) loop 5 with cache
  4, one short and tiny; 4) cache 59 with a 4x young generation; 5) cache 61; 6) a thrash sweep from size 5
  to 59.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 1 pass 5

## E17 — subject aux ellipsis frees two syllables so it only rescues lines just over the suno budget
- Date: 2026-10-15
- Project: Pappydapimp69/brain-auto-training
- Tags: [songwriting][suno-prompting][testing][tooling]
- What: Dropping a leading subject and auxiliary ("It has been a long time" to "Been a long time")
  is a real but small cut for suno-builder's over-budget warning. On 19 casual-register lines over
  the warning (more than 12 counted syllables at the default budget of 9), it freed 1 or 2
  syllables per line and cleared only 2 lines. Hyphenating the longest word cleared 0, lowered no
  line and raised 3. Elision followed by hyphenation also cleared 2. Applied as the ellipsis
  kernel's linter is written, eliding any line that opens with a droppable pair, it rewrote 4 of 4
  copular lines into fragments with a different meaning ("I am the reason" to "The reason").
- Why built: New-half gap pick. suno-builder/E11 found that the builder's hyphenate fix can never
  lower the count that raised the warning, so a real fix has to cut words. The ellipsis kernel
  offers a principled cut that keeps the image word and the rhyme word. I wanted to know how much
  that cut actually buys against the warning, and whether the kernel's suggested linter is safe to
  run as a one-click fix.
- Design: The sandbox ports suno-builder's syllablesInPart, syllablesInWord, lineSyllables and
  hyphenate to Python. A one-off check, outside the sandbox, ran the real builder in node and matched
  the port on all 157 words and 60 lines used. The corpus is 20 hand-written lines: 10 that open with
  a droppable pair before a verb or participle, 4 that open with one before a noun phrase or pronoun
  (my own meaning-change labels, unverified by any listener), and 6 with no droppable opener. The
  fixes are: hyphenate the longest word; naive elision; guarded elision, which refuses when the next
  word is a determiner or pronoun; and guarded elision then hyphenation.
- Got right: The guard separates the two kinds of opener cleanly: it blocked 4 of 4
  meaning-changing lines and wrongly blocked 0 of 10 safe ones, and every elision kept the line's
  last (rhyme) word. Unlike hyphenation, elision always moves the warning's metric the right way:
  a full subject and auxiliary freed 2 syllables and a contraction ("I've", "It's", "I'm") freed 1.
- Where/why it failed: My prediction that elision would clear about half of the elidable
  over-budget lines was wrong: it cleared 2 of 9. The other 7 sat at 14 to 17 counted
  syllables, 2 to 5 over the warning, and a contraction frees only 1. The 6 lines with no droppable
  opener (narrative lines like "The highway hums...") cannot use the fix at all. The kernel's
  linter as written ("flag lines that open with a droppable pair") mangles copular lines.
- Fix: Offer elision as the first, cheapest cut only when a line is at most 2 counted syllables over
  the warning and opens with a full subject and auxiliary pair (1 over for a contraction).
  Refuse it when the next word is a determiner or pronoun. For longer overruns, show the size of
  the overrun and ask for a real cut of a clause or modifier, not a rewording.
- Why this fix: The amount a fix can save has to match the size of the overrun: elision's ceiling
  is 2 syllables, hyphenation's is 0, and 13 of the 19 warned lines here were 3 or more over. The
  guard costs nothing on the safe lines and prevents every meaning change seen in this corpus.
- Rule of thumb: Subject-and-auxiliary ellipsis frees at most 2 counted syllables (a contraction
  frees 1), so it rescues a rushed Suno line only when the line is 1 or 2 over the warning; guard it
  against a following determiner or pronoun, and cut a clause for anything longer.
- Provenance (verified/assumed): Verified first-hand: sandbox
  2026-10-15__subject-aux-ellipsis-frees-two-syllables-so-it-only-rescues-lines-just-over-the-suno-budget.py
  printed 19 of 20 lines over 12; hyphenation cleared 0, lowered 0 and raised 3; guarded elision
  cleared 2 and freed 1 to 2 syllables per line; elision plus hyphenation cleared 2; the naive
  linter elided 4 of 4 copular lines; the guard blocked 4 of 4 of those and 0 of 10 safe lines;
  7 of 9 elidable warned lines stayed over. The port matched the real builder in node on 157 words.
- Composed: ideas:SONGWRITING/suno-prompting/hyphenate-words-to-slow-a-rushed-vocal-line/crowded-syllables-make-suno-rush-the-delivery, pappydapimp69__suno-builder/E11, ideas:CONVERSATION/ellipsis/casual-speech-drops-the-subject-and-auxiliary/been-a-while-sounds-spoken-it-has-been-a-while-sounds-written
- Picked-by: new-half
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-15__subject-aux-ellipsis-frees-two-syllables-so-it-only-rescues-lines-just-over-the-suno-budget.py
- Prediction: Hidden assumption: ellipsis frees enough syllables to pay for a line that trips the
  rushed-line warning, so it can replace the hyphen fix that suno-builder/E11 showed cannot work.
  It is wrong if most elidable warned lines stay over after elision. Expected before the run:
  hyphenation clears 0; guarded elision clears about half of the elidable warned lines; the naive
  linter elides 4 of 4 copular lines and the guard blocks them with 0 wrong blocks. The scenario
  built to break the assumption is the lines that run 3 or more syllables over.
- Observed: RESULT: PASS of 19 over-budget lines hyphenation cleared 0, guarded ellipsis 2 (freed
  1-2 syl), ellipsis then hyphenation 2; naive linter mangled 4/4 copular lines, guard 0 wrong
  blocks; 7/9 elidable warned lines still over. The PASS covers the sandbox's six checks. The
  composed claim, that ellipsis pays for a rushed line, was refuted at 2 of 9 against my predicted
  half, hence Polarity incompatible. The corpus came out heavier than I aimed for (19 of 20 lines
  over, where I meant most to sit at 13 to 16).
- Scenarios: 1) 10 lines with a droppable opener before a verb, elided naive and guarded; 2) 4
  copular lines with a droppable opener before a noun phrase or pronoun, built to break the
  kernel's linter; 3) 6 lines with no droppable opener; 4) BREAK for the hidden assumption: warned
  lines 3 to 5 syllables over, where a 2-syllable cut cannot reach the threshold; 5) hyphenation alone
  and after elision on every line.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 2 pass 5

## E16 — stray assonance corpus flips run both ways xaax reads as wistful abba
- Date: 2026-10-15
- Project: Pappydapimp69/brain-auto-training
- Tags: [songwriting][rhyme][testing]
- What: Exhaustive corpus check of every 4-line stanza over a toy tail inventory (3 vowels x 6 codas,
  104976 stanzas) lettered three ways: one-pass any-rhyme, two-pass read case-blind, and two-pass
  uppercase-only (the resolved truth). Stray assonance flips the open/stable verdict mostly toward
  stable (44352), but 1728 stanzas flip the other way, and every one of them is XAAX read as ABBA:
  the two unrhymed outer lines share a vowel and become a wistful envelope.
- Why built: The one-stray-merge entry counts flips per collapse type (7 of 19) and the shape kernel
  plus the suno-builder entries only show open stanzas closing (XXAA to AABB), which invites the
  belief that stray assonance can only over-close a stanza. A corpus rate and a direction count
  were missing, and the fixtures so far were hand-built.
- Design: Tails are (vowel, coda) with coda manners stop/fricative/nasal; resolved means same vowel
  and same manner (perfect or family), assonance means same vowel only. Lettering is first-match
  grouping, singletons become X. The open rule is the companion's own (max closure distance 3 or
  more, or nothing closes before line 4). Uniform sampling over tails is my modelling choice, not
  a real lyric distribution, so the percentages are toy-corpus rates. Scenario 2 swaps to 5 vowels
  x 4 codas; scenario 3 is a fixed bat/bone/foam/class XAAX stanza.
- Got right: Direction is lopsided as expected: one-pass flips 46080 of 104976 (43.9 percent), 44352
  open to stable and 1728 stable to open. Two-pass read case-blind still flips 35424 (33.7 percent),
  and over the 11520 stanzas whose truth is one of Pattison's four shapes it cuts flips from 5760
  to 2016. More vowels cut the one-pass flip rate to 29.6 percent (scenario 2).
- Where/why it failed: The claim that stray assonance only ever closes a stanza is false: XAAX (stable,
  closes at line 3) reads as ABBA (open, wistful) whenever lines 1 and 4 share only a vowel. And the
  two-pass labeller read case-blind does WORSE on this direction (2016 stable-to-open against
  1728 for one-pass), because when line 1 is also assonant with the A pair one-pass swallows it
  into AAAA while two-pass leaves 1 and 4 as a lowercase pair that folds into an envelope.
- Fix: Read shape only from uppercase letters, treating lowercase as X, and when a tool shows an ABBA
  verdict, check that the outer pair is uppercase before calling the stanza wistful; test any
  shape readout on an XAAX stanza with assonant outer lines, not just XXAA.
- Why this fix: The uppercase-only read is the only one of the three with zero flips in both
  directions; the case-blind read inherits exactly the X-with-X merges two-pass leaves behind,
  and those are the merges that create the reverse flip.
- Rule of thumb: Stray assonance does not only over-close a stanza: 1728 of 104976 toy stanzas flip
  stable to open, all XAAX read as ABBA via assonant outer lines, and case-blind two-pass makes it
  worse (2016), so read shape from uppercase letters only and test an XAAX fixture.
- Provenance (verified/assumed): Verified first-hand by running
  2026-10-15__stray-assonance-corpus-flips-run-both-ways-xaax-reads-as-wistful-abba.py: S1 one-pass
  46080/104976 flips (44352 open to stable, 1728 stable to open, all 1728 XAAX to ABBA), case-blind
  two-pass 35424 flips (2016 stable to open), S2 29.6 percent, S3 fixed stanza XAAX to ABBA.
- Composed: ideas:SONGWRITING/rhyme-tooling/two-pass-letter-assignment-keeps-schemes-legible/resolved-rhymes-claim-letters-before-assonance-does, ideas:SONGWRITING/rhyme/rhyme-scheme-shape-sets-a-songs-emotional-motion/aabb-stops-often-abba-stays-open-and-wistful, local__sandbox-one-stray-merge-flips-open-verdicts/E1
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__stray-assonance-corpus-flips-run-both-ways-xaax-reads-as-wistful-abba.py
- Prediction: Written before the first run. Hidden assumption under the pick: stray assonance only
  ever pushes a stanza toward stable, so flips are one-directional. Expected: one-pass flips 30 to
  50 percent of the toy corpus, open-to-stable outnumbering stable-to-open, but stable-to-open is
  nonzero via XAAX to ABBA (this would be proved wrong by a zero count); case-blind two-pass flips
  fewer than one-pass but still keeps some stable-to-open; 5 vowels lowers the one-pass rate.
- Observed: RESULT: PASS S1 one-pass flips 46080/104976 (43.9%: 44352 open->stable, 1728
  stable->open); case-blind two-pass flips 35424 (2016 stable->open); S2 5-vowel one-pass 29.6%;
  XAAX->ABBA fixed case flips stable->open=True. Not predicted: case-blind two-pass had MORE
  reverse flips than one-pass (2016 vs 1728). Pass criteria unchanged after the run; the first run
  crashed on a grouping bug (for/else) before printing anything, fixed before any numbers existed.
- Scenarios: 1) 3 vowels x 6 codas, all 104976 stanzas; 2) 5 vowels x 4 codas, all 160000 stanzas;
  3) fixed XAAX stanza bat/bone/foam/class, built to BREAK the one-directional assumption.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 3 pass 1

## E15 — single trope series of one swap fake ads stays over half identical until four kit assets rotate
- Date: 2026-10-15
- Project: Pappydapimp69/brain-auto-training
- Tags: [game-ads][comedy][sandbox]
- What: A themed series of fake ads that all use one trope (say eight pin-pull ads) and follow the
  kernel's one-swap rule stays 0.767 identical per pair with a fixed kit, and 0.691 at the most
  swaps that keep the trope readable (2 of 4). The 3-rotated-kit fix from the template-similarity
  lesson only brings it to 0.534; it took 4 rotated kit assets to reach 0.482.
- Why built: Kernel pick: the premise slot machine says pick one trope and swap one thing, the template
  similarity lesson says a fixed kit keeps a batch over half identical and rotating 3 kit assets
  fixes it, and the source-check lesson says the axis labels need checking. A channel running a
  one-trope series is the natural use of the kernel, so this tests whether the E1 fix carries over.
- Design: 16 slots per video as in the template-similarity lesson: 10 kit assets, 4 trope-unique
  features, 1 joke, 1 script (joke and script always new). A swap replaces a trope feature with one
  of 20 absurd values; readable means at least 2 of 4 trope features untouched (the threshold is
  taken from brain-creative-training E6, not re-derived). Rotated kit assets draw from 6 variants.
  8 videos per batch, 3000 seeded batches. Axis labels are drawn from the kernel's list and compared
  with the source list transcribed in the source-check lesson. The 0.5 line is an assumption.
- Got right: Rotating the trope across the six tropes plus 3 rotated kit assets gets under the line
  (0.480), so the E1 fix holds for a mixed batch; and the label check reproduces the source-check
  finding, 4 of 5 axis labels traceable and about 20% of generated premises carrying the renamed one.
- Where/why it failed: Swaps cannot buy distance in a one-trope series: each swap frees one of 4 trope slots, so
  even an unreadable 3-swap batch was 0.648. With 2 swaps and 3 rotated kit assets the series was
  still 0.534, so the E1 fix of rotating 3 kit assets is calibrated for mixed tropes and is not
  enough once every video shares a trope.
- Fix: For a one-trope series rotate at least 4 kit assets per video and use the readable maximum of
  2 swaps (0.482), or break the series up by trope; do not try to get distance by adding swaps,
  which costs readability before it costs similarity.
- Why this fix: Kit rotation moves up to 10 of 16 slots while swaps can move at most 2 of 4 trope slots
  before the trope stops reading, so the kit is the only lever big enough; the trope is the part
  the series exists to repeat, so keep it and spend the variation on kit assets instead.
- Rule of thumb: A one-trope fake-ad series cannot swap its way out of looking templated: 1 swap 0.767, 2
  swaps 0.691, 3 rotated kit 0.534; rotate 4+ kit assets (0.482) or vary the trope instead.
- Provenance (verified/assumed): Verified first-hand by running the sandbox
  2026-10-15__single-trope-series-of-one-swap-fake-ads-stays-over-half-identical-until-four-kit-assets-rotate.py
  (seeded, 8 scenarios, 3000 batches each): 0.767, 0.691, 0.534, 0.482, 0.480 and 4/5 labels traceable.
- Composed: ideas:COMEDY/fake-mobile-ad/premise-slot-machine-from-the-five-misleading-ad-patterns/pick-one-trope-then-swap-one-thing-absurd, local__fake-ad-kernel-source-check/E1, local__fake-ad-kit-template-similarity/E1, pappydapimp69__brain-creative-training/E6
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-15__single-trope-series-of-one-swap-fake-ads-stays-over-half-identical-until-four-kit-assets-rotate.py
- Prediction: Written before running; hidden assumption: the template-similarity fix (rotate 3 kit assets)
  is general, i.e. it works whatever the premise mix. Expected single-trope 1 swap 0.72-0.80, 2 swaps
  0.65-0.72, the E1 fix applied to a one-trope series to stay over 0.5, trope-rotated plus 3 kit under
  0.5, 3 swaps unreadable, labels 4/5 traceable. The assumption would be proved wrong if S3 went under 0.5.
- Observed: RESULT: PASS 6/6 checks; single-trope 1 swap 0.767, 2 swaps 0.691, +3 kit rotated 0.534, +4
  rotated 0.482; trope rotated+3 kit 0.480. Also: single trope 1 swap 4 rotated 0.558, trope rotated
  kit fixed 0.636, 3 swaps 0.648 and unreadable; untraceable labels about 0.20 in every scenario.
- Scenarios: 1) single trope, kit fixed, 1 swap; 2) single trope, kit fixed, 2 swaps; 3) BREAK for the E1
  fix: single trope, 2 swaps, 3 kit rotated; 4) single trope, 2 swaps, 4 rotated; 5) single trope, 1
  swap, 4 rotated; 6) trope rotated, kit fixed; 7) trope rotated, 3 rotated; 8) 3 swaps, over the cap
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 4 pass 1

## E14 — searchable phrase card loses its hashtag to a pasted footer and its overlay to the three second hook
- Date: 2026-10-15
- Project: Pappydapimp69/brain-auto-training
- Tags: [tiktok][youtube][search][captions][sandbox]
- What: The search packaging card (one phrase in voiceover, overlay and caption plus 2-3 hashtags) breaks in
  two places once real upload habits are added. On YouTube, under the kernel's own rules, a channel
  footer pasted above the card fills the 3 hashtags shown above the title, so the phrase tag is
  never shown; a hashtag dump that brings the video to 61 tags hides all of them (60 still keep
  them). On screen, adding the 4-word phrase to the 3-second hook overlay cut the propositions that
  fit from 5 of 6 to 3 of 6 at 180 wpm and to 1 of 6 at 160 wpm.
- Why built: Gap pick: no lesson had applied this kernel. Its claims are rules about position and count, so
  the test is to put the card into the workflows people actually use (pasted footers, cross-posted
  TikTok hashtag blocks) and to combine its overlay advice with the hook-caption-budget lesson,
  which caps a sound-off proposition at 8 to 9 words in 3 s.
- Design: YouTube's display rule is coded exactly as the kernel states it (first 3 description hashtags
  shown, more than 60 means all ignored). This is an unverified input: the support page could not be
  fetched from this sandbox (DNS failure), and whether duplicates count toward 60 is not stated, so
  both conventions are run. Six descriptions: card first, card then footer, footer first, 60 and 61
  tags, 31 unique tags written twice. Overlay: six hook propositions I wrote (2 to 11 words), word cap
  3 s x 160 or 180 wpm (8 or 9 words, the rates from hook-caption-budget E1), phrase length swept 2-6.
- Got right: The card as written works and survives a footer placed after it (phrase tag shown in both),
  and stays intact right up to 60 hashtags; merging the phrase into the proposition ('Only 1% beat
  this fake mobile game ad', 8 words) fits even the 160 wpm cap.
- Where/why it failed: The shown three are positional, not relevance-ranked, so a footer template pasted above the
  card hides the phrase tag (shown: shorts, comedy, channelname). The 61st tag removes every tag,
  phrase included. A 31-tag list written twice is 62 or 31 depending on the unknown duplicate rule,
  so it shows nothing or everything. And the overlay cannot carry a separate phrase beside most
  hooks: I predicted 2 of 6 would still fit at 160 wpm, only 1 did.
- Fix: Put the card's hashtags first in the description and keep footers below it; keep the total far
  from 60 and never paste TikTok hashtag blocks into YouTube; write the searchable phrase into the
  hook proposition itself rather than as a second line of overlay text.
- Why this fix: Both failures come from fixed budgets the card shares with other content (3 shown slots, 60
  tags, 8-9 words in 3 s); keeping the card first and merging the phrase into the hook spends each
  budget once instead of letting a template or a second caption take it.
- Rule of thumb: A searchable-phrase card loses to fixed budgets: a footer above it takes YouTube's 3 shown
  hashtags, a 61st tag hides all, and a separate 4-word phrase left 1-3 of 6 hooks readable in 3 s;
  put tags first and write the phrase into the hook.
- Provenance (verified/assumed): Verified first-hand by running the sandbox
  2026-10-15__searchable-phrase-card-loses-its-hashtag-to-a-pasted-footer-and-its-overlay-to-the-three-second-hook.py:
  footer-first hides the tag, 61 tags hide all and 60 keep, overlay 5/6 alone, 3/6 and 1/6 with phrase.
- Composed: ideas:TIKTOK/search/put-one-searchable-phrase-in-caption-overlay-and-voiceover/youtube-shows-the-top-three-hashtags-and-ignores-all-past-sixty, local__hook-caption-budget/E1
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__searchable-phrase-card-loses-its-hashtag-to-a-pasted-footer-and-its-overlay-to-the-three-second-hook.py
- Prediction: Written before running; hidden assumption: the card's three placements are free, i.e. nothing
  else competes for the shown hashtags or the overlay. Expected the phrase tag shown for card-first and
  footer-after, hidden for footer-first and at 61 tags, kept at 60, and with the phrase added 3 of 6
  propositions fitting at 180 wpm and 2 of 6 at 160. Wrong if footer-first still showed the phrase.
- Observed: RESULT: FAIL 5/6; footer-first hides the phrase tag, 61 tags hide all (60 keep); overlay fits alone
  5/6 at 180 wpm, with phrase 3/6 (160 wpm 1/6); W6 dupes decide: False vs True. The miss is my 160 wpm
  count (1 not 2); phrase-length sweep at 180 wpm: 2 words 5, 3-4 words 3, 5-6 words 1.
- Scenarios: 1) card first; 2) caption, card, footer after; 3) BREAK: footer pasted above the card; 4) 61
  tags; 5) 60 tags; 6) 31 tags written twice under both duplicate rules; 7) overlay budget at 160 and
  180 wpm with a 2 to 6 word phrase; 8) phrase merged into the proposition
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 4 pass 5

## E13 — roof faces unfold with a gap at hips and an overlap at valleys though area stays exact
- Date: 2026-10-15
- Project: Pappydapimp69/brain-auto-training
- Tags: [roofing][origami][geometry][sandbox]
- What: Composed the roofing pitch-multiplier lesson with the origami single-vertex lesson by reading a
  roof as a folded sheet: at each roof vertex the sloped sector angles were summed (a sheet folds to it
  only if they close to 360) and Kawasaki's alternating sums checked. Area stays exact under the
  multiplier, but the angles do not close: a hip apex is short by 6.03 degrees at 4/12 and 38.94 at
  12/12, and a valley junction is over by exactly the same amounts.
- Why built: The roofing entry shows one scalar (the multiplier) makes every face's area exact, which
  tempts the reading that a roof is just its plan stretched uniformly and could be cut or folded from one
  flat sheet. The origami entry gives the exact test for whether a vertex comes from a flat sheet, so
  the two together say where the stretched-plan picture stops holding.
- Design: 30 x 40 ft house at 4, 6, 9 and 12 in 12. Hip roof with ridge (15,15)-(25,15); gable on the
  same house; an equal-width, equal-pitch cross gable meeting a main gable, giving a 6-crease junction
  of two ridges and two valleys. Sector angles from 3D vectors, compared with the same vertex in plan;
  hip face areas by cross products against plan x multiplier. Float angles with 1e-9 tolerance, since
  they are irrational here (the origami entry's exact-arithmetic advice cannot apply directly).
- Got right: Hip area from 3D faces matched plan x multiplier at every pitch (1264.9111 at 4/12, 1697.0563
  at 12/12), plan angles closed to 360 at every vertex, and the gable ridge point summed to exactly 360
  with Kawasaki true, so a gable is genuinely one sheet bent along its ridge.
- Where/why it failed: The stretched-plan picture fails for angles: sloped hip-apex sectors were 133.49/86.98/
  133.49 at 4/12 (sum 353.966) and 125.26/70.53/125.26 at 12/12 (sum 321.058), so a flat pattern leaves a
  wedge gap there; the valley junction summed 366.034 to 398.942, so a flat pattern must overlap. I did
  not predict that the valley excess would equal the hip deficit at every pitch.
- Fix: Use the multiplier for area and material counts only; for any one-piece flat layout (a sheet-metal
  cap, a paper or card model, a cut pattern) compute sloped sector angles from 3D and budget a cut gap
  at hip apexes and a lap or extra seam at valley junctions, growing with pitch.
- Why this fix: The multiplier is the secant of one slope and scales lengths only across the fall line,
  so areas scale by one factor but angles between hips and ridges do not; the angle sum is the
  quantity the origami test reads, and it is the one the multiplier says nothing about.
- Rule of thumb: The pitch multiplier keeps roof area exact but not the angles: on a 30x40 hip roof the
  apex sectors fall short of 360 by 6.03 deg at 4/12 and 38.94 at 12/12, a valley junction overshoots by
  the same, so only gable ridges unfold flat; lay out flat patterns from 3D angles.
- Provenance (verified/assumed): Verified first-hand by running
  2026-10-15__roof-faces-unfold-with-a-gap-at-hips-and-an-overlap-at-valleys-though-area-stays-exact.py:
  hip deficits 6.034, 12.759, 25.361, 38.942 deg at 4, 6, 9, 12 in 12; valley excesses equal to those;
  gable ridge 360.000 with Kawasaki true; hip area 3D equal to plan x multiplier at all four pitches.
- Composed: local__2026-10-13__origami-single-vertex-kawasaki-equals-reflection-composition-identity/E1, local__roofing-pitch-multiplier-vs-surface-area-sum/E1
- Picked-by: current-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__roof-faces-unfold-with-a-gap-at-hips-and-an-overlap-at-valleys-though-area-stays-exact.py
- Prediction: Written before the first run. Hidden assumption under the pick: since one multiplier makes
  every face's area exact, the sloped roof is the plan stretched uniformly, so sloped angles around each
  vertex still sum to 360 like the plan. That is proved wrong if the hip apex sum differs from 360.
  Expected: area exact at all pitches; gable ridge 360 and Kawasaki true; hip apex below 360, deficit
  under 10 deg at 4/12 and over 30 deg at 12/12, growing with pitch; valley junction above 360.
- Observed: RESULT: PASS area = plan x multiplier exact at all 4 pitches, but sloped angles do not close:
  hip apex gap 6.03 deg at 4/12 to 38.94 at 12/12, valley junction overlap 6.03 to 38.94 deg; only the
  gable ridge (360, Kawasaki true) unfolds flat. Pass criteria unchanged; first run.
- Scenarios: 1) gable ridge interior point at 4 pitches (control, degree 2); 2) hip apex at 4 pitches,
  built to BREAK the stretched-plan assumption; 3) cross-gable valley junction (degree 6) at 4 pitches;
  4) hip face areas vs plan x multiplier at 4 pitches.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 3 pass 2

## E12 — replay fingerprint across frame rates must drop continuous state rounding it only moves the flake
- Date: 2026-10-15
- Project: Pappydapimp69/brain-auto-training
- Tags: [determinism][testing][state][gamedev][sandbox]
- What: A 20 Hz fixed-step sim (integer lattice plus sfc32 state words) under a per-frame camera follow at
  30, 50, 60 and 144 fps, fingerprinted six ways over 40 seeds. Hashing the camera float raised a false
  alarm on 40/40 seeds, and rounding it did not help (3 decimals 40, 1 decimal 40, whole units 36),
  because the camera ended up to 2.26 units apart between frame rates. Discrete facts plus state words
  gave 0 false alarms and caught a frame-count leak 40/40, which a run-twice test at one fps missed.
- Why built: The replay-fingerprint kernel says run a scripted playthrough twice from one seed and compare a
  hash; the split-state kernel says keep continuous detail out of authority; the seeded-rng kernel
  puts the generator state in the saved state. The hidden assumption in a common shortcut is that
  rounding presentation floats before hashing makes a full-state fingerprint tolerant across frame
  rates, and that run-twice at a fixed frame rate covers frame-rate nondeterminism.
- Design: Stdlib. Integer-microsecond accumulator runs 200 sim ticks in 10 s at every frame rate; per tick a
  lattice step, a combat roll and, on a zone change, one spawn roll; per frame cam += (pos - cam) *
  0.15. Fingerprint = sha256 of sorted-key JSON (NaN rejected) of: discrete facts, state words and cam
  raw / rounded to 3, 1, 0 decimals; discrete plus words; discrete only. A leak variant draws one roll
  from the sim stream on frames where the camera lags by more than 0.5. A break variant derives the
  zone from the camera float instead of the lattice position.
- Got right: Every kernel held where its rule is followed: discrete facts plus state words matched across all 4
  frame rates on 40/40 seeds, run-twice at 60 fps was stable, and when presentation drew from the sim
  stream the cross-fps fingerprint failed 40/40, as did deriving the zone from the camera float
  (40/40), so the hash flags exactly the split-state violations.
- Where/why it failed: Two shortcuts fail. Rounding the float only moves the flake: the camera's spread across frame rates
  (up to 2.26 units) exceeds every grid tried, so whole-unit rounding still mismatched 36/40, and a grid
  coarse enough to pass would hash nothing useful. And the kernel's run-twice test at one frame rate
  reported 0/40 mismatches for a leak whose draw count depends on frame count, since both runs had the
  same frames.
- Fix: Hash only authoritative discrete facts plus the RNG state words, leave every presentation float out
  of the golden entirely, and run the determinism test at two or more frame schedules (for example 30
  and 144 fps) instead of twice at one, so frame-count-dependent draws show up.
- Why this fix: Excluding the float removed all 40 false alarms without losing detection: the leak and the
  float-derived zone both still failed 40/40 because they change the state words or a discrete fact,
  which is where any real authority leak must surface.
- Rule of thumb: Leave presentation floats out of a replay fingerprint rather than rounding them (whole-unit rounding
  still mismatched 36/40 seeds across 30-144 fps) and run the test at two frame rates, not twice at one:
  run-twice at 60 fps missed a frame-count leak that cross-fps caught 40/40.
- Provenance (verified/assumed): Verified first-hand: the sandbox 2026-10-15__replay-fingerprint-across-frame-rates-must-drop-continuous-state-rounding-it-only-moves-the-flake.py
  printed false alarms raw 40, round3 40, round1 40, round0 36, discrete+words 0 of 40; camera spread
  2.2553; run-twice leak 0/40; cross-fps leak 40/40; zone-from-float 40/40. The 0.15 follow factor and
  the frame rates are model choices.
- Composed: ideas:SYSTEM/determinism/seeded-rng/save-replay-coop-from-one-stream, ideas:SYSTEM/testing/replay-fingerprint/determinism-regression-guard, ideas:SYSTEM/determinism/split-state-by-determinism-need/discrete-vs-continuous
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__replay-fingerprint-across-frame-rates-must-drop-continuous-state-rounding-it-only-moves-the-flake.py
- Prediction: Written before the first run. Hidden assumption under test: rounding presentation floats makes a
  full-state fingerprint frame-rate tolerant. Expected: raw cam at least 36/40 false alarms; 1-decimal
  rounding still above 0; discrete plus words 0/40; run-twice at 60 fps 0/40 on the leak; cross-fps
  leak at least 36/40; zone-from-float at least 20/40. Wrong if 1-decimal rounding gave 0 false alarms.
- Observed: RESULT: PASS across 4 fps x 40 seeds false alarms raw 40, round3 40, round1 40, round0 36,
  discrete+words 0; leak missed by run-twice-at-60 (0) but caught across fps 40/40 (discrete only 40);
  zone-from-float caught 40. Max camera spread across frame rates 2.2553 units.
- Scenarios: 1) clean build across 4 frame rates with six fingerprint scopes, built to BREAK the
  rounding-tolerates-floats shortcut; 2) presentation leak on the sim stream, run twice at 60 fps;
  3) the same leak compared across frame rates; 4) zone derived from the camera float, built to break
  the discrete fingerprint's stability
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 5 pass 5

## E11 — playable budget is encoded bytes raw asset ceiling is three quarters of the cap
- Date: 2026-10-15
- Project: Pappydapimp69/brain-auto-training
- Tags: [gamedev][web][ads][sandbox]
- What: Built single-file playable-ad HTML with every asset inlined as base64 and checked it against
  the 5 MB (AppLovin, Unity) and 2 MB (Meta) caps. The raw-asset ceiling came out at 0.747 of the cap.
  A 3.9 MB raw bundle produced a 5,220,000-byte file that fails 5,000,000 but passes 5 MiB. The test
  also ran a first-tap guard and per-network CTA builds.
- Why built: The playables kernel had never been applied. Its spec list says 5 MB with assets inlined, but
  a team budgets by summing raw asset sizes, and brainwork E179 measured base64 at 1.333x for glTF.
  The question was how much raw budget is actually left, and which parts of the spec are unclear.
- Design: Stdlib Python. Incompressible random bytes stand in for PNG and OGG assets. A fixed 20,000-byte
  HTML/JS shell is assumed. Builds are measured at the computed ceiling and 3,000 bytes past it. One file
  is checked against both 5e6 and 5 MiB. gzip level 9 is applied to raw and base64 bytes, using both
  incompressible and text-like data. A tap state machine (tutorial, play, end card) runs against a naive
  canvas-wide store listener on 500 seeded tap sequences. The Meta and AppLovin builds are grepped for
  mraid and for their CTA calls.
- Got right: The 4/3 cost reproduced exactly (ratio 1.3333). The ceiling build is 5,000,000 bytes, and
  3,000 more raw bytes makes it 5,004,000. A guarded tap handler redirected on the first tap 0 times
  in 500 sequences while the naive handler did 500 of 500, and 164 guarded runs still reached the CTA.
  The Meta build had no mraid string and used FbPlayableAd.onCTAClick.
- Where/why it failed: The kernel's single number is unclear in two ways. First, between 3,735,000 and 3,917,160
  raw bytes (182,160 bytes wide) a file passes 5 MiB but fails 5 MB decimal. Second, the cost depends on
  where size is measured. gzip of base64 is only 1.010x raw on incompressible data, so a cap measured
  on transfer size hides the base64 cost that a cap measured on file size charges in full. My first run
  printed FAIL on the ceiling check because my fixture's closing tags added 14 bytes to the shell. That
  was an accounting bug in the fixture, not the claim.
- Fix: Budget raw assets at 3/4 of (cap minus shell): about 3.73 MB for a 5 MB network and 1.48 MB for
  Meta's 2 MB. Treat MB as decimal 10^6 unless the network says otherwise. Run a CI size check on the
  built HTML file itself, not on the asset folder. Bind the store open only to the end-card CTA, and
  build each network's CTA adapter separately so no mraid reference reaches Meta.
- Why this fix: Base64 is a fixed 4/3 expansion on file bytes, so it costs the same whatever is in the asset.
  Using the decimal cap is the conservative reading of the ambiguity. A shared build would have shipped
  mraid to Meta, and a canvas-wide listener redirects on tap 1 every time.
- Rule of thumb: Check a playable against the built HTML, not raw assets: base64 leaves 0.747 of a 5 MB cap
  for assets (3.73 MB). A 3.9 MB bundle became 5.22 MB, failing 5e6 but passing 5 MiB, so budget to
  decimal MB.
- Provenance (verified/assumed): Verified first-hand: the sandbox printed RESULT: PASS 8/8 with ceiling 3,735,000 bytes,
  the 3.9 MB build at 5,220,000 bytes, gzip(b64)/raw 1.010, and first-tap redirects 500/500 naive and
  0 guarded.
- Composed: ideas:GAME-ADS/playables/single-file-html-under-5mb-no-network-first-tap-never-redirects/network-specs-differ-on-mraid, pappydapimp69__brainwork/E179, ideas:GAME-ADS/structure/hook-in-three-seconds-sound-off
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__playable-budget-is-encoded-bytes-raw-asset-ceiling-is-three-quarters-of-the-cap.py
- Prediction: Hidden assumption: "under 5 MB" can be budgeted from raw asset sizes. Written before running,
  I expected the raw ceiling to be about 3.73 MB for 5 MB and about 1.48 MB for 2 MB, and a 3.9 MB raw
  bundle to fail 5e6 but pass 5 MiB. I expected gzip of base64 random data to stay within 1.05x of raw,
  the naive handler to redirect on tap 1 in all 500 sequences and the guarded one in none, and the Meta
  build to be mraid-free. Proof the assumption is wrong would be a 3.9 MB raw bundle that fits 5e6.
- Observed: RESULT: PASS 8/8; raw ceiling 3735000 B for 5MB (0.747), 1485000 B for Meta 2MB; 3.9MB raw
  -> 5220000 B file fails 5e6 but passes 5MiB; gzip(b64)/raw 1.010 on incompressible; naive first-tap
  redirects 500/500, guarded 0. The first run printed FAIL 7/8 because the ceiling build was 5,000,014
  bytes: the fixture's closing tags sat outside the 20,000-byte shell. I fixed the fixture's byte
  accounting and left the criterion unchanged.
- Scenarios: 1) ceiling build and +3,000 bytes; 2) BREAK: naive 3.9 MB raw budget, checked against both MB
  and MiB; 3) gzip of incompressible and text-like assets; 4) 500 tap sequences, naive against guarded;
  5) per-network builds (Meta with no mraid, AppLovin with mraid.open, and a shared build that leaks
  mraid).
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 1 pass 1

## E10 — late safe cue costs only the jumps so set the frame before the first beat
- Date: 2026-10-15
- Project: Pappydapimp69/brain-auto-training
- Tags: [comedy][humor][narrative][sandbox]
- What: Delayed the safe cue (the framing distance) by one or two beats relative to the violation in the
  distance-gated escalation model. Each beat loses value in proportion to the severity jump it makes.
  Flat-at-ceiling lost only its opening beat (5.11 to 4.11) and none at all when the frame was set
  before beat 1. Escalating schedules lost 32-38 percent at lag 1 and 53-66 percent at lag 2.
- Why built: Bridge from the current-half lesson escalation-needs-matching-distance E1, which held. Its matched
  dial assumes the distance arrives on the same beat as the violation, and the benign-violation
  kernel says that simultaneity is the condition. Real framing, such as a reveal that the victim is a
  cartoon, often lands late. The premise kernel adds that distance with no violation is not a joke.
- Design: Stdlib. The escalation model and gate are copied from E1: habituation exp(-0.2 X),
  X += 1/(1+I/5), ceiling 10, six beats, and g = exp(-((d - I/C)/0.25)^2). Five schedules: flat,
  linear, geometric, rule-of-three, mild. Lag condition: d_t = W_(t-L), with grounded d = 0.3 before
  the frame is set. Frame-first variant: d is set to beat 1's severity before beat 1. Lead condition:
  d_t = W_(t+1), run with both the symmetric gate and a one-sided gate where surplus distance is free.
  A per-beat both-at-once count marks beats with gate at least 0.5. One weirdness-only track has
  violation 0 and distance 1.
- Got right: Lag 0 reproduced E1 exactly (flat 5.11, three 3.59, linear 2.53). At lag 1, flat lost 0.20 and
  stayed best. Rule-of-three lost 0.35, linear 0.32 and geometric 0.38, and mild lost only 0.03. With
  the frame set before beat 1, flat lost 0.00 at both lag 1 and lag 2. Under the one-sided gate, a
  lead cost every schedule 0.00. The weirdness-only track scored 0.00.
- Where/why it failed: Frame-first saves only a schedule with no jumps. For linear, geometric and three it changed
  the loss by 0.01 or less (lag 2 linear even went 0.66 to 0.68), because each later jump lags again.
  My prediction that a symmetric lead hurts rule-of-three as much as lag was wrong: it cost 0.18
  against 0.35. The gate's width and symmetry are assumptions taken from E1, so only the direction and
  the ordering are findings.
- Fix: When the reason-it-is-ok comes after the violation (a later reveal, a framing that catches up),
  set the frame before the first beat. Then either hold severity flat at the level the frame covers, or
  escalate in steps smaller than the gate width. Avoid big jumps such as a rule-of-three 2-6-10 unless
  the safe cue for each jump lands on that same beat.
- Why this fix: A lagging dial is exactly right whenever severity stays the same from one beat to the next. The
  mismatch at beat t equals the jump from t-L to t, so the loss sits on the jumps and on an opening
  beat with no frame. Removing jumps or pre-setting the frame removes the mismatch.
- Rule of thumb: A safe cue that lands late costs only the severity jumps: flat-at-ceiling lost just its unframed
  opening beat (5.11 to 4.11, and 0 with the frame set first), while escalating schedules lost 32-38
  percent at one beat of lag.
- Provenance (verified/assumed): Verified first-hand: the sandbox printed RESULT: FAIL 6/7. The one miss was my symmetric-lead
  prediction (rule-of-three lost 0.18, not over 0.30). Every lag, frame-first, one-sided-lead and
  weirdness-alone number in this entry comes from that run.
- Composed: ideas:COMEDY/premise-design/an-absurd-premise-needs-a-wrong-cue-and-a-safe-cue/weirdness-alone-is-not-a-joke, local__escalation-needs-matching-distance/E1, ideas:COMEDY-CRAFT/theory/benign-violation/each-beat-needs-a-violation-and-a-reason-it-is-ok-perceived-at-the-same-moment
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__late-safe-cue-costs-only-the-jumps-so-set-the-frame-before-the-first-beat.py
- Prediction: Hidden assumption: E1's matched dial lands on the same beat as the violation. Written before
  running, I expected lag 0 to reproduce flat 5.11. At lag 1 without frame-first, I expected flat to lose
  about 20 percent but stay best and rule-of-three to lose over 30 percent. I expected frame-first to
  make flat lag-immune at lags 1 and 2, a symmetric lead to cost three as much as lag, a one-sided lead
  to cost 0, and weirdness alone to score 0.00. Proof the assumption is wrong would be lag costing
  nothing on the escalating schedules.
- Observed: RESULT: FAIL 6/7; flat lag0 5.11 lag1 4.11 lag1+ff 5.11; three lag0 3.59 lag1 2.35 (loss
  0.35); geometric lag1+ff loss 0.37; weird-alone 0.00. The one failed check is the symmetric lead on
  three: it lost 0.18, not over 0.30. I left the criterion unchanged. At lag 2 the losses were flat
  0.38, linear 0.66, geometric 0.62, three 0.53 and mild 0.07.
- Scenarios: 1) lag 0, reproducing E1; 2) BREAK: lag 1 and lag 2 with a grounded opening; 3) the same lags
  with the frame set first; 4) one-beat lead under symmetric and one-sided gates; 5) weirdness alone,
  with violation 0 and distance 1.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 1 pass 2

## E9 — gag rule card precision comes from two rules and yield collapses when over tightened
- Date: 2026-10-15
- Project: Pappydapimp69/brain-auto-training
- Tags: [comedy][narrative][process][testing]
- What: A Road-Runner-style rule card applied to a 1,280-beat cross product of gag candidates
  (5 harm sources x 8 tools x 4 places x 4 outcomes x dialogue on/off) raised the share of beats a
  benign-violation audience model scores funny from 0.300 to 1.000 and still left 32 distinct
  tool-and-place setups, so it does work as a gag machine. But the precision came from only two of
  its five rules (never wins, humiliated not harmed); the titular "who can hurt whom" rule added
  0 precision once "humiliated not harmed" was on the card and cut the funny yield from 160 to 96.
- Why built: The kernel claims a short rule card about who can hurt whom turns a premise into a
  gag machine and that any gag breaking a rule should be cut. That mixes two jobs (filter weak
  beats, generate many beats) and never says which rules do which job or when the card gets so
  tight that it stops producing enough distinct gags for a short.
- Design: Every candidate beat is a tuple of harm source, ACME tool, place, outcome and whether
  it carries dialogue. The audience model is the benign-violation kernel written as code: a beat is
  funny when the lead's attempt at the want visibly fails (violation) and it reads as harmless at
  the same moment (humiliated, or maimed only by a long-shot gravity fall, the distance route).
  The card is five predicates: R1 only own tool, ineptitude or gravity can hurt; R2 never quits;
  R3 never wins; R4 no dialogue; R5 humiliated, not maimed. Measures: yield, funny count,
  precision, and distinct (tool, place) setups among funny beats, for the full card, each
  one-rule ablation, each rule alone, a no-want lead, and a ladder of narrower worlds. The
  12-setups-per-short floor is an assumed working figure, not a measured Jones short count, and
  the audience model is hand-written, not audience data.
- Got right: The full card reached precision 1.000 with 96 surviving beats and 32 distinct setups,
  well above the 12-setup floor, so the "gag machine" half of the claim held in this model. The
  ablations separated the rules cleanly: dropping R2 or R3 halved precision to 0.500, dropping R5
  cut it to 0.667, dropping R4 left it at 1.000 and dropping R1 left it at 1.000.
- Where/why it failed: The "who can hurt whom" rule is not a funniness filter once the
  humiliated-not-harmed rule is present: R3+R5 gave 0.500 and adding R1 gave 0.500, while removing
  R1 from the full card raised the funny count from 96 to 160 (outside forces and the target
  striking back also produce harmless humiliations). R1 only earned precision when R5 was absent
  (R2+R3 0.600 to 0.667 with R1), by keeping maimings on the distance route. Two breaks: with no want
  for the lead the full card still yielded 96 beats but 0 were funny, and narrowing the world to
  gravity only with 3 tools in 2 places left 6 setups, under the 12 floor.
- Fix: Label each rule on the card by its job before writing gags. Rules that encode the violation
  (the lead never wins, never quits) and the benign reading (humiliated, not harmed) are the filter
  and must stay. Rules about who may hurt the lead and format rules like no dialogue are
  world-consistency or medium choices: keep them for voice, but do not count them as quality checks,
  and re-open them first when the card stops producing enough distinct setups. Write the lead's
  want on the card's first line.
- Why this fix: The ablation showed the filter value sits in R2, R3 and R5, while R1 and R4 only
  trade yield for consistency. Naming the job stops a writer from cutting a good harmless
  humiliation just because an outside force caused it, and the no-want break shows the card is
  inert without the want it is meant to collide with.
- Rule of thumb: On a gag rule card, the never-wins and humiliated-not-harmed rules do the quality
  filtering; who-can-hurt-whom and no-dialogue only cut yield for consistency, so loosen those
  first when setups run short, and always write the lead's want first or the card yields 0 funny beats.
- Provenance (verified/assumed): Verified first-hand: sandbox
  2026-10-15__gag-rule-card-precision-comes-from-two-rules-and-yield-collapses-when-over-tightened.py
  ran with no card 1,280 candidates at precision 0.300; full card 96 beats, precision 1.000, 32
  setups; R3+R5 0.500 and with R1 0.500; R2+R3 0.600 and with R1 0.667; no want 0 of 96 funny;
  over-tightened ladder 32, 32, 12, 6, 1 setups.
- Composed: ideas:COMEDY-CRAFT/gag-world/write-the-rules-before-the-gags/a-short-rule-card-about-who-can-hurt-whom-turns-a-premise-into-a-gag-machine, ideas:COMEDY-CRAFT/theory/benign-violation/each-beat-needs-a-violation-and-a-reason-it-is-ok-perceived-at-the-same-moment
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__gag-rule-card-precision-comes-from-two-rules-and-yield-collapses-when-over-tightened.py
- Prediction: Hidden assumption: every rule on the card earns its place as a filter of weak gags.
  Expected before the run: base precision under 0.20, full card precision 1.000 with yield 96 and
  32 setups, R4 adding 0 precision, and a no-want lead giving 0 funny beats. The assumption is wrong
  if some rule can be dropped without any loss in precision; the scenario built to break it is the
  one-rule ablation, with R1 as the target.
- Observed: RESULT: PASS card precision 0.300->1.000 with 32 setups; precision comes from R3+R5
  (R1 adds 0 once R5 holds, R4 adds 0); no want -> 0/96 funny; starves (<12 setups) first at
  'gravity, 3 tools, 2 places'. The base-rate prediction missed (0.300, not under 0.20); the other
  predicted numbers matched. The ablation refuted the hidden assumption for R1 and R4.
- Scenarios: 1) no card, all 1,280 candidates; 2) full five-rule card; 3) each rule dropped
  in turn and each rule alone; 4) BREAK: R1 tested for added precision with and without R5 (built
  to break "every rule filters"); 5) BREAK: lead with no want under the full card; 6) over-tightening
  ladder from 5 sources, 8 tools and 4 places down to 1 of each.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 2 pass 1
- Cited-by: 2026-10-16 · projects/pappydapimp69__brainwork.md#E329 · compatible · sandboxes/2026-10-16__rule-card-sets-distance-for-escalation.py · observed RESULT: PASS fixed d=2: go-big 2 vs mild 10 funny; card-matched: go-big 19, harm 0 in 3/3 schedules; callback break leaves 2 harm beats. · brain train auto session 2026-10-16; session_013uRvb55pYWRMwoocxRqQ3a

## E8 — exact threshold angles let a cosmetic sin branch fork a shared rng stream across runtimes
- Date: 2026-10-15
- Project: Pappydapimp69/brain-auto-training
- Tags: [determinism][gamedev][state][testing][sandbox]
- What: A cosmetic sparkle that fires when sin(spinner angle) >= 0.5 and draws one jitter roll from the shared
  seeded stream forked gameplay across two sin() implementations on 8/8 seeds when the spinner moved
  30 degrees per tick, because sin(30 deg) is exactly the threshold and the two libraries round it to
  opposite sides (173 of 3600 ticks decided differently, first at 870 deg). The same branch on
  generic angles flipped 0 times in 28,800 ticks, and a split cosmetic stream forked 0/8.
- Why built: transcendental-drift E1 found a branch-only sim never forked in 100,000 steps and concluded the
  transcendental ban matters where results feed state. That test drew generic arguments. The hidden
  assumption is that a branch rarely sits within one ulp of its threshold; designer angles (30, 45,
  60 deg) put sin, cos and tan exactly on round thresholds every period, and a cosmetic branch can
  feed state indirectly by changing how many draws the shared stream gives.
- Design: Stdlib sfc32 with state words; per tick a cosmetic check sin(radians(30 t)) >= 0.5 that draws one
  roll when true, then one d20 combat roll that can damage an enemy (kills, hp). Runtime A uses
  math.sin; runtime B a fmod range reduction plus 12-term Taylor series, standing in for another
  engine's libm (real browsers were not compared). 8 seeds, 3600 ticks. Scenarios: designer angles
  shared stream, designer angles split cosmetic stream, generic angles (t times 1.2345678901 rad)
  shared stream, the threshold on libm alone, and a state-word save at tick 1000 on A loaded on B.
- Got right: The state-words entry held: a same-runtime reload from the four saved words was exact, and once
  one runtime took an extra draw the shared stream shifted and gameplay forked 8/8. Its split-stream
  fix held here too (0/8), and so did the transcendental entry's generic-argument result (0 flips in
  28,800 ticks). A fingerprint that hashes the state words saw the cross-runtime fork at the flip
  tick (1013); an hp/kills-only fingerprint lagged by 0 to 3 ticks.
- Where/why it failed: The rule 'ban transcendentals only where they feed state' misses this route. The sin value never
  entered state, yet it decided a draw count on the shared stream, and on round designer angles the
  result lands exactly on the threshold, so two correct libraries disagree 4.8% of ticks. Even one
  library is inconsistent with itself: libm says sin(30 deg) < 0.5 but sin(390 deg) = 0.5 and
  sin(870 deg) = 0.5, so the sparkle does not repeat every 12 ticks.
- Fix: Give every cosmetic consumer its own seeded stream (state words saved for it separately), and never
  let a transcendental gate a draw on the authoritative stream. Where a periodic effect must branch,
  index an integer angle (degrees mod 360) into a shipped table or compare integers, not sin() of a
  float angle against a round constant.
- Why this fix: The split stream removed the fork 8/8 to 0/8 without touching the sin() difference, so it fixes
  the coupling, not the maths; the integer index also removes the same-runtime period break the
  split stream leaves in the visuals.
- Rule of thumb: A cosmetic sin() branch forks a shared seeded stream across runtimes when it gates a draw: on
  30-degree steps two sin()s split 0.5 on 173/3600 ticks and forked 8/8 seeds, generic angles 0/28800,
  so give effects their own stream and branch on integer angles.
- Provenance (verified/assumed): Verified first-hand: the sandbox 2026-10-15__exact-threshold-angles-let-a-cosmetic-sin-branch-fork-a-shared-rng-stream-across-runtimes.py
  printed 8/8 forked, 173 of 3600 differing ticks, first flip tick 29 (870 deg), split 0/8, generic
  0/8 with 0 flips, reload exact, fingerprint fork at 1013 and hp-only lags [0, 2, 0, 3, 0, 0, 0, 1].
  The Taylor sine is my stand-in for a second engine, named in Design.
- Composed: ideas:SYSTEM/determinism/seeded-rng/save-replay-coop-from-one-stream, local__sandbox-seeded-rng-state-words/E1, local__transcendental-drift-forks-only-when-it-feeds-state/E1
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__exact-threshold-angles-let-a-cosmetic-sin-branch-fork-a-shared-rng-stream-across-runtimes.py
- Prediction: Written before the first full run, after a one-line probe showed the two sines disagree on the
  0.5 test at 870 deg. Hidden assumption under test: a branch-only use of sin() cannot fork a run
  (transcendental E1). Expected: designer-angle branch on the shared stream forks at least 7/8 seeds;
  split stream 0/8; generic angles 0/8; same-runtime state-word reload exact; a fingerprint holding
  the state words sees the fork no later than an hp/kills-only one. Wrong if designer angles also
  gave 0/8.
- Observed: RESULT: PASS designer-angle cosmetic branch forked gameplay 8/8 via shared stream (split 0/8, generic
  angles 0/8); state-word reload exact True, cross-runtime fork seen by state-word fingerprint at tick
  1013 vs hp-only at 1013. Per-seed hp-only lag 0, 2, 0, 3, 0, 0, 0, 1 ticks (added after the first
  run as a report line; the pass criterion was not changed). libm alone: 30 deg False, 390 True, 750
  False, 870 True, 1110 False.
- Scenarios: 1) designer 30-degree angles, shared stream, built to BREAK the branch-only-is-safe claim; 2) same
  with a split cosmetic stream; 3) generic irrational angles, shared stream; 4) the threshold test on
  one runtime across periods; 5) state-word save on runtime A loaded on runtime B with two
  fingerprint scopes
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 5 pass 2

## E7 — ending check on a cut down passes cuts that dropped the gap opening beat
- Date: 2026-10-15
- Project: Pappydapimp69/brain-auto-training
- Tags: [game-ads][narrative][video][sandbox]
- What: The ad-length crossover lesson's check ("does the 15 s cut end on the fixable-fail beat?")
  tests content, not structure. Across all 810 integer-second 15 s cut-downs of a five-beat 30 s
  ad, 488 end on a reveal of at least 2 s, but 167 of those (0.342) dropped the setup beat that
  opens the gap, so the reveal pays off a question the cut never asked. Under the lesson's own
  funnel those cuts sit at the truncated crossover (0.0455 per second), not the anchored one
  (0.0122), and lose to the 30 s master at every decay rate from 1 to 4% per second.
- Why built: New-half pick: the information-gap kernel says tension comes from how the same
  material is ordered and rationed, film E19 says time a reveal from the line that opens its gap,
  and the ad-length companion turns "the cut keeps its ending" into a 1.65 value multiplier. I
  wanted to know whether a cut that keeps the ending is enough, or whether the gap-opening beat
  has to survive too.
- Design: Master beats: hook 3 s, setup 5 s (asks "will he make it?"), escalation 12 s, fail 6 s,
  reveal 4 s. Every 15 s cut keeps each beat trimmed to 0..full whole seconds, in order (810
  cuts). Content check: the reveal is kept for at least 2 s. Discourse check: setup and reveal are
  both kept for at least 2 s and the gap is held at least HMIN seconds between them (HMIN 3, swept
  0 to 8). The 1.65 multiplier, the funnel form and the 2 s minimums are assumed inputs carried
  from the companion lesson or chosen here, not measured ad data. The reveal caption is timed two
  ways: anchored to the reveal beat (film E19) or the master's absolute cue list rescaled by 15/30.
- Got right: The content check is never stricter than the gap: 0 cuts failed it while keeping the
  gap, so it catches clock truncation, as the companion says. The companion's closed form
  reproduced exactly (h* 0.0122 with the gap kept, 0.0455 without), and the length rule holds
  for the 321 cuts that pass both checks.
- Where/why it failed: Ending on the payoff is not the same as keeping the gap. All 167 false
  passes came from a cut that dropped the setup; the hold length did not bind until HMIN 4 (171
  false passes) and rose to 222 at HMIN 6 and 355 at HMIN 8. A gap-lost cut is worth only 0.587,
  0.682, 0.792 and 0.920 of the master at 1, 2, 3 and 4% per second. The rescaled cue list put
  the reveal caption more than 0.5 s late on 210 of the 321 gap-keeping cuts and never early,
  because in this fixture the reveal always ends the cut.
- Fix: Before comparing a cut-down against the master, check two beats, not one: the beat that
  opens the gap (the setup question) and the beat that closes it, in that order, with some hold
  between them. Cut seconds from the escalation first, never from the setup, and time the reveal
  caption from the reveal beat inside the cut, not from a rescaled master cue list.
- Why this fix: The multiplier the length lesson relies on is a tension effect, and the kernel
  says tension lives in the order of information, so the check has to test order (question then
  answer), not just whether the answer is still on screen. Escalation is the only beat whose loss
  shortens the cut without closing or skipping the gap.
- Rule of thumb: A 15 s cut-down that ends on the fixable-fail payoff can still have lost its gap:
  a third of such cuts here dropped the setup question, which puts them back at the truncated
  crossover; check that the gap-opening beat survives, and trim escalation first.
- Provenance (verified/assumed): Verified first-hand: sandbox
  2026-10-15__ending-check-on-a-cut-down-passes-cuts-that-dropped-the-gap-opening-beat.py
  enumerated 810 cuts, 488 passing the ending check, 167 of them without a setup (0.342 at HMIN
  0 to 3, 0.350 at 4, 0.727 at 8); h* 0.0122 versus 0.0455; value ratios 0.587 to 0.920; rescaled
  cue list late on 210 of 321 gap-keeping cuts, early on 0.
- Composed: ideas:SYSTEM/narrative/tension-as-information-gap/discourse-not-content, local__film/E19, local__ad-length-crossover-depends-on-the-cut/E1
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-15__ending-check-on-a-cut-down-passes-cuts-that-dropped-the-gap-opening-beat.py
- Prediction: Hidden assumption: the companion's "ends on the fixable-fail beat" check is
  equivalent to "the cut keeps the information gap". It is wrong if some cuts that pass the
  ending check lose the gap. Expected before the run, as a direction without a fixed number: some
  ending-passing cuts lose the gap, mostly through holds that are too short, and the rescaled cue
  list spoils reveals by firing early. The scenario built to break it is HMIN 0, where only a
  missing setup can cause a false pass.
- Observed: RESULT: PASS 167/488 cut-downs that end on the reveal lost the gap at HMIN=3 (0.342
  even at HMIN=0), so their h* is 0.0455 not 0.0122; rescaled cue list mistimed 210/321
  gap-keeping cuts (early 0, late 210). Both mechanism guesses were wrong: the false passes all came
  from a missing setup, not short holds, and the cue errors were all late, not early. The
  reordered-reveal case (hold 7 s down to 0 s with the same beats) is a stated illustration, not a
  measured result.
- Scenarios: 1) all 810 cuts under the ending check; 2) the same cuts under the gap check at HMIN 3;
  3) BREAK: HMIN swept 0 to 8, with HMIN 0 built to remove the hold condition and leave only a
  missing setup; 4) crossover and value ratios at 1 to 4% per second for a gap-lost cut; 5)
  reveal caption anchored versus rescaled cue list on the gap-keeping cuts; 6) search for cuts the
  ending check would wrongly reject (found 0).
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 2 pass 2

## E6 — drywall integer foot rooms make exact fit offcuts so a saw kerf adds sheets far more often than random cut lists
- Date: 2026-10-15
- Project: Pappydapimp69/brain-auto-training
- Tags: [drywall][estimating][packing][kerf][sandbox]
- What: Putting the cut-list kerf rule (charge k-1 kerfs per board) into the drywall run-length layout: a
  1/8 in saw kerf changed the sheet count in 26 of 91 integer-foot rooms (+40 sheets in total), where
  the woodworking cut-list lesson found kerf changed the board count in only 5 of 1500 random lists.
  Rooms measured to the inch dropped to 3 of 91. Best-fit decreasing matched the exact optimum in all
  182 rooms, so the sort order is not where drywall counts go wrong.
- Why built: Edge pick: the drywall lesson packs run remainders into offcuts with no kerf, and the cut-list
  lesson says kerf is a validity check that rarely changes a count. Both are packing rules; this tests
  whether the woodworking conclusion transfers to drywall, where room sizes are whole feet.
- Design: Exact integer units (eighths of an inch), 12 ft sheets, two courses per wall, 91 rooms 8 to 20 ft
  as in the drywall lesson. Remainders packed best-fit decreasing and by an exact subset DP; kerf
  charged as k-1 cuts per sheet as in the cut-list lesson. Control: 91 rooms with sides 96 to 240 in
  from a fixed LCG. Assumption, not checked with a crew: a saw (not score and snap, which has no kerf)
  makes the cuts; the 1/4 in fitting gap hangers leave is not modelled.
- Got right: The longest-first plus best-fit layout from the drywall lesson is optimal on every room tried
  (0 of 91 integer, 0 of 91 inch rooms above the DP optimum), because each room's remainders come in
  four copies of two lengths; and the 12x14 room still needs 9 sheets with or without kerf.
- Where/why it failed: The cut-list lesson's conclusion that kerf rarely matters does not transfer: whole-foot room
  sizes produce remainders that fill a 12 ft sheet exactly (49 of 91 rooms have such a subset, e.g. 2
  plus 10 or three 4s), and any kerf breaks an exact fill, so 26 rooms (28.6%) gain sheets. My control
  prediction also missed: inch-measured rooms changed in 3 of 91 (3.3%), not under 2%.
- Fix: When drywall pieces are saw-cut, run the layout with the k-1 kerf charge and treat exact-fill offcut
  pairs as not fitting; when they are scored and snapped, the kerf-free count stands, so record which
  cutting method the estimate assumes.
- Why this fix: The kerf matters only at exact fills, and whole-foot rooms make exact fills common, so the
  error is concentrated in a predictable set of rooms rather than spread thinly as in random lists.
- Rule of thumb: A kerf that changes under 1% of random cut lists changed 26 of 91 whole-foot drywall rooms
  (+40 sheets) because round sizes fill sheets exactly; charge k-1 kerfs whenever pieces are saw-cut.
- Provenance (verified/assumed): Verified first-hand by running the sandbox
  2026-10-15__drywall-integer-foot-rooms-make-exact-fit-offcuts-so-a-saw-kerf-adds-sheets-far-more-often-than-random-cut-lists.py:
  26/91 integer rooms changed (+40), 3/91 inch rooms (+4), FFD above optimum 0 and 0, 12x14 9 to 9.
- Composed: local__drywall-sheet-count-layout-vs-area-estimate/E1, pappydapimp69__brainwork/E178
- Polarity: incompatible
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__drywall-integer-foot-rooms-make-exact-fit-offcuts-so-a-saw-kerf-adds-sheets-far-more-often-than-random-cut-lists.py
- Prediction: Written before running; hidden assumption of the cut-list lesson: lengths are effectively random so
  exact fills are rare. Expected best-fit decreasing to equal the optimum in all integer rooms, kerf to
  change the count in over 10% of integer rooms, under 2% of inch-measured rooms, and 12x14 to stay 9.
  It would be proved wrong if integer rooms changed as rarely as random cut lists.
- Observed: RESULT: FAIL 3/4; kerf adds sheets in 26/91 integer-foot rooms vs 3/91 inch-measured; ffd>opt 0 and
  0; 12x14 9->9. The one miss is my control band (3.3% against under 2%). After the first run I widened
  only the diagnostic line from exact-fill pairs (19 rooms) to exact-fill subsets (49 rooms) to explain
  the 26; no pass criterion was changed.
- Scenarios: 1) integer-foot rooms, best-fit decreasing against the exact DP; 2) BREAK for the cut-list
  lesson: integer-foot rooms with a 1/8 in k-1 kerf; 3) inch-measured control rooms with the same kerf;
  4) the 12x14 reference room
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 4 pass 2

## E5 — clock fixed sun compass matches a great circle only at some departure hours even in the arctic
- Date: 2026-10-15
- Project: Pappydapimp69/brain-auto-training
- Tags: [ornithology][migration][navigation][sandbox]
- What: Seeds an ornithology domain. A migrant that orients by a time-compensated sun compass but never
  resets its internal clock while crossing longitudes is often said to fly a near great-circle route
  at high latitude. Geometry test: an arctic route's miss distance swings from 23 to 1289 km with the
  home-clock hour of departure, so latitude alone does not make the sun-compass route a great circle.
- Why built: Arctic shorebirds and waders cross 60 to 90 degrees of longitude, and the claim that a
  clock-shifted sun compass gives a cheap great-circle route is a classic explanation for their paths;
  I wanted to know whether it is a property of latitude or of something else before relying on it.
- Design: Spherical earth, 2 km steps. The bird fixes alpha = great-circle initial course minus sun
  azimuth at departure, then holds heading = sun azimuth at its current position at the unreset home
  time + alpha. Azimuth from declination and hour angle, no 15 deg per hour shortcut. Departures every
  2 home-clock hours, kept only if the sun is up along the whole route. The hypothesis and its usual
  attribution (Alerstam) are from my memory of the literature, not checked against a source here.
- Got right: The loxodrome cost is real at high latitude: 4.1 percent longer than the great circle on
  72N 140E to 66N 160W and 9.6 percent on 70N 100W to 64N 170E, against 0.8 percent at 22 to 25N, so a
  route that does approximate the great circle is worth a lot in the Arctic. Some departure hours do
  track it closely: 23 and 36 km misses at 04 and 06h on the eastward arctic route.
- Where/why it failed: My prediction (every arctic daylight departure within 300 km, low latitude always
  worse) was refuted: eastward 72N misses ran 23 to 365 km, westward 70N 334 to 1289 km, while the
  25N route missed only 24 km at 06h. Even at 80N under midnight sun (decl 20) misses ran 8 to 341 km
  on a 1907 km route. The sun's azimuth rate is not uniform through the day off the pole, so the turn
  the compass induces matches the great-circle turn only at some hours.
- Fix: When modelling or explaining a migrant's route with a clock-fixed sun compass, state the departure
  hour and declination, sweep them, and compare against the great circle; do not quote the
  approximation from latitude alone, and expect midday departures to drift most.
- Why this fix: The heading change over a flight is the azimuth difference between two local solar
  times, which depends on where in the day those times fall; the great-circle turn depends only on
  latitude and longitude change, so the two agree only where the azimuth rate happens to match.
- Rule of thumb: A clock-fixed sun-compass route approximates a great circle by departure hour, not by
  latitude: arctic daylight misses ran 23 to 1289 km across hours and 8 to 341 km even under midnight
  sun at 80N, so sweep departure hour before claiming the shortcut.
- Provenance (verified/assumed): Verified first-hand by running
  2026-10-15__clock-fixed-sun-compass-matches-a-great-circle-only-at-some-departure-hours-even-in-the-arctic.py:
  arctic misses 23 to 1289 km over 10 daylight departures, 25N 24 to 6257 km over 5, 80N midnight sun
  8 to 341 km over 12, loxodrome plus 4.1 and 9.6 percent on the arctic routes.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__clock-fixed-sun-compass-matches-a-great-circle-only-at-some-departure-hours-even-in-the-arctic.py
- Prediction: Written before the first run. Hidden assumption: latitude decides whether the clock-fixed
  sun compass tracks a great circle. Expected: on both arctic routes the bird lands within 300 km of
  the target and flies within 2 percent of the great circle, while at 22 to 25N it misses by more than
  1000 km. A small low-latitude miss or a large arctic miss proves the assumption wrong.
- Observed: RESULT: FAIL latitude-only claim refuted=True: arctic daylight misses run 23-1289 km by
  departure hour, low latitude 24-6257 km; loxodrome +4.1%/+9.6% longer than GC on the arctic routes;
  midnight-sun 80N max miss 341 km over 12 hours. Run 1 used fixed 06h and 18h departures and already
  refuted it (S3 missed 24 km at 06h, S2 334 km at 18h); after that I added the daylight sweep and the
  sun-up filter and, after run 2, the S4 midnight-sun case, reported outside the pass criterion. Two
  low-latitude midday runs never reached the target meridian and stopped at the 3x great-circle cap.
- Scenarios: 1) 72N 140E to 66N 160W eastward, daylight hours; 2) 70N 100W to 64N 170E westward;
  3) 25N 20E to 22N 80E, low latitude, built to break the claim from the other side; 4) 80N 60E to 76N
  150E under midnight sun, the regime the hypothesis is usually stated for.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 3 pass 4

## E4 — bookbinding spine grain flips with each fold so folio and octavo need short grain and quarto long
- Date: 2026-10-15
- Project: Pappydapimp69/brain-auto-training
- Tags: [bookbinding][paper][folding][sandbox]
- What: Seeds a bookbinding domain. A fold simulator that tracks every panel of a flat sheet through
  right-angle folds shows the spine (the last fold) swaps between the sheet's two axes with each
  fold, so for grain parallel to the spine folio, octavo and 32mo signatures need short-grain sheets
  and quarto and 16mo need long-grain sheets. Practical case: long-grain A4 folded once to A5 is
  cross-grain, while long-grain A3 folded twice to the same A5 page is correct.
- Why built: Grain running across the spine makes pages cockle and the book resist opening flat, and the
  usual hobby move is to fold copier paper in half; this checks which fold counts are safe from
  which sheet instead of trusting a remembered rule, and checks the imposition the same simulator
  produces against the printers' octavo layout.
- Design: The sheet is a grid of 2^n panels; each fold halves the current longer side and mirrors the
  moving half onto the stack (position, layer depth and which face is up are tracked). The top
  layer is leaf 1, so every panel gets a page number on each face. Grain is judged against the axis
  the last fold line runs along. Unverified inputs, from memory and not re-checked: the octavo outer
  forme 1, 4, 5, 8, 9, 12, 13, 16 and the claim that copier paper is usually long grain.
- Got right: The simulator puts every page 1 to N exactly once for 1 to 5 folds, conjugate pages across
  the spine sum to N+1 on both faces (2 to 32 conjugate pairs checked per size), and the octavo side
  holding page 1 comes out as 1, 4, 5, 8, 9, 12, 13, 16, matching the standard printers' layout.
- Where/why it failed: The odd/even rule rests on the folds alternating direction, which holds only while the
  sheet's aspect ratio is under 2. A 4:1 strip folded twice keeps both folds the same way and its
  quarto needs the folio's short grain; at exactly 2:1 the halved sheet is square and the second
  fold can go either way, so the rule is undefined there (1.9:1 alternated, 2.0:1 did not).
- Fix: Decide grain from the fold count and the sheet: count the right-angle folds, and if the sheet's
  long side is under twice its short side, use short-grain stock for odd counts and long-grain for
  even; for strips or square sheets trace the folds instead of using the parity rule.
- Why this fix: The spine is always the last fold and each right-angle fold turns the fold line through 90
  degrees, so grain parity follows fold parity exactly when every fold halves the other side; the
  ratio check is the one condition under which that alternation fails.
- Rule of thumb: Grain must run along the last fold: folio, octavo and 32mo need short-grain sheets,
  quarto and 16mo long-grain, so long-grain A4 folded once is cross-grain while A3 folded twice is
  right; the parity rule fails on sheets 2:1 or longer.
- Provenance (verified/assumed): Verified first-hand by running the sandbox
  2026-10-15__bookbinding-spine-grain-flips-with-each-fold-so-folio-and-octavo-need-short-grain-and-quarto-long.py:
  RESULT PASS 5/5, octavo outer forme 1, 4, 5, 8, 9, 12, 13, 16, spine axis y/x/y/x/y for 1 to 5 folds.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__bookbinding-spine-grain-flips-with-each-fold-so-folio-and-octavo-need-short-grain-and-quarto-long.py
- Prediction: Written before running; hidden assumption: every fold changes direction. Expected each page once,
  conjugate pairs summing to N+1, the octavo outer forme 1, 4, 5, 8, 9, 12, 13, 16, odd fold counts
  needing short grain and even long, and a 4:1 strip folded twice to keep the folio's parity (the
  case built to break the alternation). Wrong if the strip had alternated like the A-series sheet.
- Observed: RESULT: PASS 5/5; folio/octavo/32mo short grain, quarto/16mo long grain; octavo outer forme [1, 4,
  5, 8, 9, 12, 13, 16]; 4:1 strip quarto spine parallel to y. A follow-up probe outside the pass
  criteria: 1.9:1 sheet folded twice gives folds x,y, 2.0:1 gives x,x.
- Scenarios: 1) imposition for folio to 32mo, every page once; 2) conjugate pages sum to N+1; 3) octavo outer
  forme against the printers' layout; 4) spine axis against grain for 1 to 5 folds; 5) BREAK: a 4:1
  strip folded twice; 6) long-grain A4 once against long-grain A3 twice
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 4 pass 4

## E3 — avalanche beacon lowest reading is a wide plateau and drifts off a tilted deep burial
- Date: 2026-10-15
- Project: Pappydapimp69/brain-auto-training
- Tags: [avalanche-safety][search][physics][sandbox]
- What: In a dipole-field model of an avalanche transceiver fine search, the lowest distance
  reading on the snow surface does not pin the burial. For a flat beacon at 2 m depth, a 0.1 m display
  shows its minimum over a stretch +/-0.91 m wide (+/-0.57 m at 1 m, +/-1.20 m at 3 m). Bracketing (the
  midpoint of the two points that read min + 0.3 m) is exact for flat or upright beacons, but a
  45-degree tilted beacon moves the field peak 0.16, 0.32 and 0.48 m off and the bracket midpoint
  0.21, 0.39 and 0.54 m off at 1, 2 and 3 m depth.
- Why built: New domain seed (avalanche safety, confirmed uncovered by brain query: 0 hits for
  avalanche). The real decision in a companion rescue is where to start the probe spiral once the
  transceiver reading stops falling, and the common shorthand is "probe where the reading is
  lowest". I wanted to know how far that spot can sit from the burial, and whether bracketing fixes it.
- Design: The buried transmitter is a magnetic dipole at depth d below flat snow, with its axis
  tilted 0 to 90 degrees from horizontal in the plane of the search line. The receiver reads field
  magnitude sqrt(1 + 3 cos^2 theta) / r^3 and shows an equivalent distance rounded to 0.1 m,
  calibrated on the dipole's broadside. The surface is sampled every 1 mm over +/-6 m. Assumed, not
  checked against a manufacturer: that receivers read total field magnitude, the broadside
  calibration, the 0.1 m display step, the min + 0.3 m bracket level and the 25 cm probe spacing
  (a commonly taught figure, from memory). Real three-antenna transceivers apply their own
  corrections, so the numbers model the field, not any one device.
- Got right: The model reproduces what the field's symmetry predicts. For a flat or upright beacon
  the bracket midpoint lands within 1 mm of the point directly above at every depth tried, and a
  flat beacon's minimum reading equals its depth (1.0, 2.0, 3.0 m). The tilt offset grows linearly
  with depth: about 0.16 x depth at 45 degrees and about 0.21 x depth at 30 degrees, the worst tilt
  tried.
- Where/why it failed: "Probe at the lowest reading" fails twice. For flat burials the lowest
  reading is a plateau whose half-width (0.91 m at 2 m) is far wider than a probe spacing, because
  along the dipole axis the field magnitude falls off only with the fourth power of the offset.
  For tilted burials the field peak itself is off the burial, and bracketing does not correct it:
  the midpoint error (0.39 m at 2 m, 45 degrees; 0.47 m at 30 degrees) is larger than the peak offset.
  An upright beacon also reads 1.6 m at 2 m depth under this calibration, which understates the depth.
- Fix: Treat the lowest reading as the centre of a search disc, not the spot. Bracket on two
  perpendicular lines to centre the disc, then probe a spiral at about 25 cm spacing out to a
  radius of at least a quarter of the indicated depth plus one spacing (0.75 m at 2 m: 29
  probes on a 25 cm grid), and widen it if the first ring finds nothing on a deep burial.
- Why this fix: Bracketing removes the plateau error, which comes from symmetry and is the larger
  error for flat burials. Only probing covers the tilt error, which bracketing cannot see because
  the surface field is still smooth and single-peaked. The tilt error scales with depth (0.47 m at
  2 m, 0.70 m at 3 m in the worst case tried), so a probe radius tied to the indicated depth covers
  it. Probing the whole flat-burial plateau instead would take 45 probes at 2 m and 69 at 3 m.
- Rule of thumb: The lowest transceiver reading is a zone, not a point: bracket to centre it, then
  probe-spiral a radius of about a quarter of the burial depth plus one spacing, because a tilted deep
  beacon puts both the reading minimum and the bracket midpoint off the victim by about 0.2 x depth.
- Provenance (verified/assumed): Verified first-hand: sandbox
  2026-10-15__avalanche-beacon-lowest-reading-is-a-wide-plateau-and-drifts-off-a-tilted-deep-burial.py
  printed plateau half-widths 0.570/0.907/1.200 m for flat burials at 1/2/3 m; 45-degree peak
  offsets 0.160/0.320/0.480 m and bracket offsets 0.213/0.390/0.544 m; worst bracket error 0.221/
  0.470/0.696 m; probe counts 21/45/69 for the plateau versus 9/25/45 for error plus 0.25 m; the
  depth/4 plus 0.25 m radius (0.50/0.75/1.00 m, 13/29/49 probes) covered the worst bracket error at
  every depth.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__avalanche-beacon-lowest-reading-is-a-wide-plateau-and-drifts-off-a-tilted-deep-burial.py
- Prediction: Hidden assumption: the lowest distance reading, or at least the bracket midpoint,
  sits directly over the buried beacon. It is wrong if a geometry exists where the bracket
  midpoint is off by more than a probe spacing. Expected before the run: flat-burial plateau
  half-width 0.6 to 0.9 m at 2 m depth, exact bracket midpoint for symmetric beacons, and a
  45-degree tilt at 2 m moving the peak 0.2 to 0.8 m. The tilted deep burial is the scenario built
  to break it.
- Observed: RESULT: PASS at 2 m a flat beacon shows its minimum over +/-0.91 m (vertical +/-0.51
  m); bracket midpoint exact when symmetric, but a 45-degree tilt puts the field peak 0.16/0.32/0.48
  m off at 1/2/3 m and the bracket midpoint 0.21/0.39/0.54 m off. The plateau at 2 m (0.907) came out
  just above the predicted band; the tilt offset (0.32) was inside it. The depth/4 plus one
  spacing radius was chosen after seeing the first run and then added as a check (it held at
  1, 2 and 3 m). It still holds with the under-read indicated depth: at 2 m and 30 degrees the
  reading is 1.8 m, giving 0.70 m against a 0.47 m error.
- Scenarios: 1) flat beacon at 1, 2 and 3 m (symmetric, bracketing exact); 2) upright beacon at the
  same depths (symmetric, narrower plateau, under-read depth); 3) BREAK: tilts of 30, 45 and 60 degrees
  at each depth, built to move the minimum and the bracket midpoint off the burial; 4) probe-count
  cost of covering the plateau versus the bracket error.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 2 pass 4

## E2 — apparent wind puff moves aft acceleration moves it forward trim to the telltales
- Date: 2026-10-15
- Project: Pappydapimp69/brain-auto-training
- Tags: [sailing][physics][sandbox]
- What: Computed apparent wind as true wind minus boat velocity across sailing angles. A beam reach in
  12 kn at 6 kn of boat speed has the apparent wind at 63.4 degrees. A 16 kn puff moves it aft to 69.4,
  and accelerating to 7.5 kn moves it forward again to 64.9. A 30 kn boat on a true broad reach (135)
  sees the wind at 21.5 degrees, which is close-hauled.
- Why built: This seeds the sailing domain, which Brain did not have (queries for sailing, apparent wind,
  sail and trim all returned 0 records). The real scenario is a dinghy on a beam reach hit by a puff,
  and the common belief tested is that sails are trimmed to the true wind direction the sailor feels
  on shore or reads on a wind report.
- Design: Stdlib vector model. The boat moves along +x, and the true wind comes from angle TWA off the bow.
  AWA = atan2(TWS sin TWA, TWS cos TWA + BS), and AWS is the vector's length. Runs: the beam-reach puff and
  acceleration case, a sweep of TWA from 30 to 175 in 5-degree steps with a puff (12 to 16 kn) and an
  acceleration (+1.5 kn), a dead run at 180, and a fast boat at TWA 135 with BS 30 plus the boat speed
  where the apparent wind crosses the beam. Flat water, no leeway and no wind gradient are assumed, and
  boat speeds are given rather than taken from a polar.
- Got right: Every predicted number reproduced. At all 30 angles from 30 to 175, a puff moved the apparent wind
  aft and acceleration moved it forward. On a dead run the apparent wind fell to 6 kn, half the true
  wind. The beam crossing at TWA 135 happened at exactly TWS cos 45 = 8.49 kn of boat speed. Trimming to
  the true wind would be 26.6 degrees off on the beam reach and 113.5 degrees off on the fast boat.
- Where/why it failed: The puff-frees-you rule fails on a dead run: the puff raised the apparent wind speed from 6 to
  10 kn but left the angle at 180. There it changes only pressure, not trim angle. The model also leaves
  out leeway, current and wind shear with height (twist), so real telltales will read a few degrees
  away from these numbers.
- Fix: Trim to the apparent wind, which is what telltales and the masthead fly show, never to the true wind.
  When a puff hits on any point of sail other than a dead run, ease or head up, because the wind went aft.
  As the boat picks up speed, sheet back in or bear away, because the wind came forward. On a dead run,
  treat a puff as pressure only.
- Why this fix: Apparent wind is the vector difference, so any change in true wind speed or boat speed rotates it
  except when the two are collinear. Boat speed always adds a component from dead ahead, so speed pulls
  the wind forward and a stronger true wind pulls it back toward the true direction.
- Rule of thumb: Trim to apparent wind, not true wind: on a 12 kn beam reach at 6 kn it sits at 63 degrees. A puff
  moves it aft (69) and the following acceleration moves it back forward (65), at every angle from 30 to
  175. Only on a dead run does a puff leave the angle unchanged.
- Provenance (verified/assumed): Verified first-hand: the sandbox printed RESULT: PASS 7/7. It gave AWA 63.4, 69.4 and 64.9 on the
  beam reach, puff-aft at 30/30 angles, dead-run AWS 6.0 with AWA unchanged at 180, AWA 21.5 for the
  fast boat, and the beam crossing at BS 8.49.
- Composed: N/A
- Sandbox: sandboxes/2026-10-15__apparent-wind-puff-moves-aft-acceleration-moves-it-forward-trim-to-the-telltales.py
- Prediction: Hidden assumption: a sailor can trim to the true wind and a puff always means ease. Written before
  running, I expected an AWA of 63.4 at 13.4 kn on the beam reach, a puff moving it aft to about 69.4,
  and acceleration to 7.5 kn bringing it forward to about 64.9. I expected a dead run to halve the
  apparent wind speed with the puff leaving AWA at 180, a fast boat at TWA 135 and 30 kn to see about
  21.5, and the beam crossing at 8.49 kn. A puff that moves AWA forward anywhere from 30 to 175 would
  refute the rule.
- Observed: RESULT: PASS 7/7; beam reach AWA 63.4, puff 69.4 (aft), accel 64.9 (fwd); dead run AWS 6.0, puff AWA
  unchanged 180; fast boat TWA135 BS30 AWA 21.5; beam crossing BS 8.49; puff-aft at 30/30 TWAs.
- Scenarios: 1) a beam-reach puff, then acceleration; 2) a sweep of TWA 30 to 175, checking puff and
  acceleration; 3) BREAK: a dead run, where the puff cannot rotate the apparent wind; 4) a fast boat on a
  true broad reach and its beam-crossing speed.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 1 pass 4

## E1 — ai output copyright is a per element claim and training fair use is split not silent
- Date: 2026-10-15
- Project: Pappydapimp69/brain-auto-training
- Tags: [legal][copyright][sandbox][model]
- What: First lesson to apply the AI-copyright kernel. A rule model of its two questions reproduced the
  claim (US: pure AI output not registrable, human edits and human selection or arrangement are; the
  training question gets no definite answer) and was pushed until it stopped holding: under a UK
  computer-generated-works model pure AI output is protectable, and "unsettled" on training now means
  district rulings that split on identical facts, not an absence of rulings. Not legal advice.
- Why built: The kernel had never been exercised, and its practical value is the separation of two
  questions people merge; a tool or a person answering one from the other gives a confident wrong
  answer, and the kernel's own scope (US only, as of 2023 guidance) was unstated.
- Design: Part A enumerates 162 works of four elements tagged human, AI or AI-with-human-edits, with or
  without human arrangement, and compares the per-element claim with two whole-work binary rules.
  Part B answers the training question with the kernel and with a tool that infers it from output
  registrability. Unverified inputs, from my memory and not fetched in this pass: UK CDPA 1988 s.9(3)
  computer-generated works, and three district rulings on training (Thomson Reuters v. Ross, not fair
  use; Bartz v. Anthropic on bought books and Kadrey v. Meta, fair use), all copying whole works.
- Got right: Pure AI output came out unregistrable in the US model (0 of the unarranged all-AI work),
  the training answer was "unsettled" in 4 of 4 fact patterns and never varied with the output answer,
  and human arrangement of all-AI elements gave a claim limited to the arrangement, as the kernel's
  quoted guidance says.
- Where/why it failed: Two whole-work shortcuts both misstate scope: "any AI taints" denied 159 of the 161
  registrable works and "any human involvement protects all" claimed AI elements in 159. The kernel
  itself stops holding at two edges: in the UK model pure AI output is protectable, and an amount-only
  fair-use bright line fits at best 2 of the 3 recorded rulings, since all copied 100 percent and
  outcomes split. My model treats any human arrangement as sufficiently creative, which overstates it.
- Fix: Answer copyrightability per element and per jurisdiction (human parts, human edits, human
  arrangement; disclaim the AI material), answer training fair use separately with the four factors,
  and say "district courts split, no appellate ruling recorded" rather than "unsettled" or "no rulings".
- Why this fix: The kernel's settled half is a US Copyright Office position, so it is jurisdiction-bound;
  its unsettled half is now unsettled because rulings disagree on the same amount copied, which is the
  fair-use kernel's point that no amount threshold decides the case.
- Rule of thumb: Treat AI-output copyright as a per-element, per-country claim (UK protects computer-
  generated works; whole-work rules misstated 159 of 161 registrable mixes) and training fair use as a
  separate question where whole-work copying split 2 to 1 in district courts.
- Provenance (verified/assumed): Verified first-hand by running
  2026-10-15__ai-output-copyright-is-a-per-element-claim-and-training-fair-use-is-split-not-silent.py:
  161 of 162 works registrable, taint rule denies 159, any-human rule overclaims in 159, conflating
  tool definite on 2 of 4 patterns vs kernel 0, UK model True, amount-only fit 2 of 3.
- Composed: ideas:LEGAL/copyright/ai-and-copyright/pure-ai-output-cant-be-copyrighted-training-data-fair-use-is-still-unsettled, ideas:LEGAL/copyright/fair-use/fair-use-has-no-safe-duration-or-credit-line-only-a-case-by-case-test
- Picked-by: current-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__ai-output-copyright-is-a-per-element-claim-and-training-fair-use-is-split-not-silent.py
- Prediction: Written before the first run. Hidden assumption: the kernel's settled answer is universal and
  "unsettled" means courts have not ruled. Expected: both binary rules wrong on most mixed works; the
  conflating tool definite on 2 of 4 patterns and kernel on 0; pure AI output unprotectable in the US
  model but protectable in the UK model (the scenario built to break the kernel); no amount-only
  threshold fits all 3 recorded rulings (best 2 of 3).
- Observed: RESULT: PASS US per-element rule: 161/162 works registrable, taint rule denies 159, any-human
  rule overclaims AI elements in 159; pure AI 0 except human-arranged; conflating tool answers training
  2/4 definitely vs kernel 0; claim stops holding in UK model (pure AI protectable) and 'unsettled'
  means split district rulings (amount-only fit 2/3). The 159 counts follow from uniform enumeration
  over a toy work space and mostly restate the rules' definitions; Parts C and D carry the finding.
- Scenarios: 1) 162 enumerated mixed works, per-element vs two binary rules; 2) four output by training
  fact patterns, kernel vs conflating tool; 3) UK computer-generated-works model, built to BREAK the
  kernel's settled half; 4) three recorded training rulings against amount-only thresholds 0.1 to 1.0.
- Link: https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 3 pass 5

