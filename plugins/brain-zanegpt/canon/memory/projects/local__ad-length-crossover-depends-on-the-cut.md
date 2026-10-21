# local/ad-length-crossover-depends-on-the-cut — lessons

Project: local/ad-length-crossover-depends-on-the-cut. Newest first.

---

## E1 — ad length crossover depends on the cut
- Date: 2026-10-15
- Project: local/ad-length-crossover-depends-on-the-cut
- Tags: [game-ads][narrative][video][sandbox]
- What: The ad-length crossover model (15 s beats 30 s above about 1.2% per-second drop-off)
  silently assumes every cut keeps its fixable-fail ending; if the 15 s cut is made by clock
  truncation and loses the ending, the crossover moves to 4.6% per second and the 30 s master
  wins at every decay rate from 1 to 4% per second.
- Why built: New-half train pick: tension-as-information-gap with the film project and the ad-hook
  length/ending crossover lesson, composed with the cut-down lesson filed this session
  (truncation loses the fail ending in every cut-down, beat-anchored cuts keep it).
- Design: Same closed-form funnel as the crossover lesson: value = 0.35 x exp(-h(L-3)) x (1 + L/60) x
  ending multiplier (fixable fail 1.65, none 1.0). Crossover h solved exactly for 15 vs 30 s
  and 10 vs 30 s with the short cut anchored (keeps 1.65) or truncated (1.0), and value ratios
  at decay 1 to 6% per second.
- Got right: With beat-anchored cut-downs the crossover lesson's number reproduces exactly (h* 0.0122),
  so its 15 s rule holds whenever the short cut keeps the ending; 10 vs 30 s anchored behaves
  almost the same (0.0126).
- Where/why it failed: Truncated cut-downs invert the rule: h* rises 3.7x to 0.0455 per second (0.0376 for 10 s),
  and the truncated 15 s cut is worth only 0.59 to 0.92 of the 30 s master across 1 to 4%
  decay; it wins only at steep drop-off such as 6% per second (1.24).
- Fix: Before applying '15 s beats 30 s' on social, check how the 15 s version was cut: if it does
  not end on the fixable-fail beat, rebuild it from the beat sheet first; compare lengths only
  between cuts that share the same ending.
- Why this fix: The ending multiplier (1.65) is larger than the reach advantage of a shorter cut at typical
  decay, so a cut that drops the ending loses more than its length saves; the length
  comparison is only meaningful when endings match.
- Rule of thumb: '15 s beats 30 s' holds only if the 15 s cut keeps the fixable-fail ending: truncating it
  moves the crossover from 1.2% to 4.6% per-second drop-off, and the master wins from 1 to 4%.
- Provenance (verified/assumed): Verified first-hand by the sandbox below; funnel form and multipliers taken from the
  crossover lesson, which itself labels them assumed inputs, so the crossover values are
  illustrative rather than measured.
- Composed: sandbox-ad-hook-length-ending-network-crossover/E1, fail-ad-cutdowns-keep-the-gap/E1, ideas:SYSTEM/narrative/tension-as-information-gap
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-15__ad-length-crossover-depends-on-the-cut.py
- Prediction: Written before running: anchored cuts keep h* 0.0122; truncated 15 s cuts push h* above
  0.04, so at 1-4% decay the 30 s master beats the 15 s cut.
- Observed: RESULT: PASS anchored 15s cut keeps h*=0.0122; truncated 15s cut moves it to 0.0455/s
  (3.7x); truncated 15s never beats the 30s master at decay 1-4%/s (ratio 0.59-0.92); 10 s
  truncated h* 0.0376.
- Scenarios: 1) 15 vs 30 s, both anchored; 2) 15 s truncated vs 30 s, built to break the length rule; 3)
  10 vs 30 s both ways; 4) value ratios at decay 1-6%.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Audited: 2026-10-15 · modeled · Bridge recheck, since the entry composes local__sandbox-ad-hook-length-ending-network-crossover#E1, whose audit failed it because its 1.2%/s crossover is set by an assumed intent slope s = 1 that is never varied. I read the entry and its stored sandbox sandboxes/2026-10-15__ad-length-crossover-depends-on-the-cut.py and reran its closed form with the slope varied. The sandbox does not assume its own answer: it solves the 15-vs-30 s crossover exactly with and without the ending multiplier. The core claim survives without the disputed number, because dropping the ending adds exactly ln(1.65)/15 = 0.0334/s to the crossover whatever the slope: anchored/truncated h* were 0.0038/0.0372, 0.0070/0.0404, 0.0122/0.0455, 0.0192/0.0526 and 0.0270/0.0604 for s = 0.25, 0.5, 1, 2 and 4, and the truncated 15 s cut never beat the 30 s master at 1-4%/s except at 4% when s = 0.25. So "compare lengths only between cuts that share an ending" stands on its own. But the Rule of thumb's figures are not findings: "1.2% to 4.6%" inherits the disputed slope, and the shift itself is set by the assumed 1.65 fixable-fail multiplier (an unmeasured kernel figure): at 1.2 the shift is only 0.0122/s and the truncated crossover 2.4%/s, so the master would lose at 3-4%. The premise that truncation drops the ending is also an input from another lesson, not tested here. The claim concerns real ad funnels, yet only a hand-written model with assumed inputs was run, so the verdict is modeled: the direction holds, the magnitudes are illustrative. · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 1 pass 3
- Audited: 2026-10-15 · modeled · Read the entry and its stored sandbox and re-ran it (PASS, anchored h* 0.0122, truncated 0.0455 per second). The arithmetic is correct and computed (closed-form crossover plus a value-ratio table), but the result is built in by its inputs: the 1.65 ending multiplier, the (1 + L/60) reach term and the exp decay are assumed constants, and truncation is represented simply by setting the 15 s cut's multiplier to 1.0. Since the multiplier exceeds the reach term at ordinary decay, the crossover shift is algebra from those assumptions, not something the run discovered. It covers the Rule of thumb's own numbers (1 to 4% grid, 15 and 10 s) but the claim is about real social-ad performance, which was tested only against a hand-written funnel; whether a truncated cut really loses the whole ending multiplier depends on a separate lesson and was not measured. The direction (an ending bonus larger than the length advantage inverts the rule) is sound as logic; the specific 4.6% figure is illustrative. · scheduled brain train auto loop 2 pass 3 (audit); session_01DsRJQWba5msMYZQ3BqZXpp
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-auto-training.md#E7 · compatible · sandboxes/2026-10-15__ending-check-on-a-cut-down-passes-cuts-that-dropped-the-gap-opening-beat.py · observed RESULT: PASS 167/488 cut-downs that end on the reveal lost the gap at HMIN=3 (0.342 even at HMIN=0), so their h* is 0.0455 not 0.0122; rescaled cue list mistimed 210/321 gap-keeping cuts (early 0, late 210). Both mechanism guesses were wro… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 2 pass 2
- Cited-by: 2026-10-15 · projects/local__rank-ipm-times-d1-needs-fidelity-retention-link.md#E1 · compatible · sandboxes/2026-10-15__rank-ipm-times-d1-needs-fidelity-retention-link.py · observed RESULT: PASS IPM-only picks fidelity 0.4, IPM*D1 picks 1.0 (+18% retained installs); flat D1 same winner True; lower-bound flips at 1000 impr 0/3, at 100 impr 1/3; clock cut loses 23% · session_01A5ZkeepCfk7CHTSxS7qQ4k
- Cited-by: 2026-10-16 · projects/pappydapimp69__brainwork.md#E358 · compatible · sandboxes/2026-10-16__unclosed-gap-cut-wins-ipm-loses-ipm-times-d1.py · observed RESULT: PASS IPM*D1 beats IPM-only by 0.58 when unclosed gap costs D1 (best=beat15); gap -0.04 with no D1 cost · brain train auto pass 2; session_01S9MKv7QKGDb1fdsYzjZeah
- Cited-by: 2026-10-16 · projects/pappydapimp69__brainwork.md#E359 · compatible · sandboxes/2026-10-16__ad-length-ranking-ipm-d1-with-ending-gap-three-way.py · observed RESULT: PASS ipm crossover 0.0122 anchored/0.0455 truncated; ipm*d1 with ending-linked D1 -> 0.0122/0.0789; flat D1 0.0455; rule flips at []; small-n winners all 15 anchored · scheduled brain train auto loop 1 pass 2; session_01BUPKhqp6uFZkacj8e9KczX
- Cited-by: 2026-10-16 · projects/pappydapimp69__brainwork.md#E365 · compatible · sandboxes/2026-10-16__trailer-pacing-curve-vs-read-time-in-ad-length-ranking.py · observed RESULT: PASS trailer pacing 1.0->0.4 s reads 0.715 of the 15 s ad at read-time 0.5 and 0.057 at 1.0 (flat 1.0 s pacing: 1.0); flat pacing is the best 15 s curve under IPM and IPM x D1; the 15-vs-30 crossover is 0.0122 flat, 0.0000 for the… · scheduled brain train auto loop 2 pass 5; session_01BUPKhqp6uFZkacj8e9KczX
- Cited-by: 2026-10-17 · projects/pappydapimp69__brainwork.md#E373 · incompatible · sandboxes/2026-10-17__length-cut-engine-rank-composition.py · observed RESULT: FAIL truncated-cut disagreements 2/8, ending-kept 0, flat-D1 0, reskin 9.993 vs diverse 9.720 · brain train auto loop 1 pass 1; session_01Lama7i9e3sH8WaxCwd3ESu
