# local/sandbox-refusal-linter-misses-logistics-answers — lessons

Project: local/sandbox-refusal-linter-misses-logistics-answers. Newest first.

---

## E1 — refusal linter misses logistics answers
- Date: 2026-09-30
- Project: local/sandbox-refusal-linter-misses-logistics-answers
- Tags: [dialogue][speech][testing]
- What: A refusal-shape linter built from the preference-organization kernel needs a polarity check as well as markers (markers alone 8 of 14, with polarity 13 of 14), and neither can reliably catch a logistics answer that refuses indirectly; the one it caught was caught by accident.
- Why built: Compose the dispreferred-response kernel with the um-versus-uh delay kernel and the practical-language subtext kernel, to see what a linter for refusal shape can and cannot detect.
- Design: Fourteen hand-labelled reply turns: 6 padded refusals, 2 bare refusals, 2 logistics refusals, 2 plain acceptances and 2 hesitant acceptances. A marker classifier (pause, well/uh/um preface, token agreement, account; 2 or more means refusal), a polarity-first classifier, and a delay score with um 2, uh 1 and a pause 2.
- Got right: Markers found all 6 padded refusals; adding polarity (no, can't, won't, or yes, okay) fixed both hesitant acceptances and both bare refusals, reaching 13 of 14.
- Where/why it failed: Markers alone called both hesitant acceptances refusals and missed both bare and both logistics refusals. With polarity, the dishes won't wash themselves counted as a refusal only because of the word won't about dishes, and I'll need the car back by six was missed. The delay score did not rank um above uh (4, 2 against 1, 3) because a written pause outweighed the filler.
- Fix: Classify polarity first and use markers only when there is no explicit yes or no; flag logistics answers from the question they follow (a request answered with a schedule or a chore), not from their words.
- Why this fix: The markers show how a reply is delivered, not what it answers; polarity words settle most cases, and a logistics refusal is only a refusal relative to the request, so only the question-answer pair can reveal it.
- Rule of thumb: Detect refusals by polarity first and delivery markers second (markers alone 8 of 14, with polarity 13 of 14); an indirect logistics refusal needs the request it answers, since word cues caught it only by accident.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; counts are copied from its output. The turns and their labels are hand-written, and the delay weights are my own choice.
- Composed: ideas:CONVERSATION/preference-organization/a-no-arrives-late-and-padded-a-yes-arrives-fast-and-bare, ideas:SPEECH-DISFLUENCY/filled-pauses/delay-signalling/um-announces-a-longer-delay-than-uh, ideas:SONGWRITING/subtext/practical-language
- Polarity: compatible
- Sandbox: sandboxes/2026-09-30__refusal-linter-misses-logistics-answers.py
- Prediction: markers find 6/6 padded refusals and falsely flag both hesitant acceptances; miss bare and logistics refusals 0/4; polarity fixes hesitant and bare but misses both logistics; um-prefaced delays all rank above uh-prefaced.
- Observed: RESULT: FAIL markers alone 8/14, with polarity 13/14, logistics refusals caught 0/2 by markers and 1/2 with polarity (the polarity hit is the word won't about dishes, not a refusal cue); um-prefaced delay [4, 2] vs uh [1, 3]
- Scenarios: 1) padded refusals; 2) bare refusals; 3) logistics refusals, built to break every word-based check; 4) plain acceptances; 5) hesitant acceptances with fillers, built to break the marker classifier.
- Link: https://claude.ai/code/session_01FPKwCG4xnKWiiLWPC1nvdo
- Cited-by: 2026-10-14 · projects/pappydapimp69__brainwork.md#E261 · compatible · sandboxes/2026-10-14__two-weak-cues-gain-only-when-errors-are-independent-and-weighted-by-strength.py · observed RESULT: PASS single 0.759 pair rho0 0.843 rho.9 0.766 rho-.5 0.923; strong 0.9822 equal 0.9501 weighted 0.9820 (weighted-minus-strong prediction missed by 0.0002) · session_017SJAeaijx8mHKPVUZV6hJB brain train auto loop 2 pass 2
