# local/lossless-cutoff-worst-gate-only-holds-on-golden-rotation-with-continuous-formula — lessons

Project: local/lossless-cutoff-worst-gate-only-holds-on-golden-rotation-with-continuous-formula. Newest first.

---

## E1 — lossless cutoff worst gate only holds on golden rotation with continuous formula
- Date: 2026-10-18
- Project: local/lossless-cutoff-worst-gate-only-holds-on-golden-rotation-with-continuous-formula
- Tags: [gamedev][input][state][testing]
- What: Ran the lossless-cutoff-is-worst rule and the one-sided gate formula on a quasiperiodic rotation signal; the per-lag formula generalises to N times min(w, distance of lag times alpha to nearest integer, 1-w), while the cutoff-as-peak part is only partly supported (the silver case broke it).
- Why built: Train pick: the two periodic-wave lessons never met the quasiperiodic near-recovery lesson on one signal, so it was untested whether the lossless cutoff is still the worst gate-only cutoff when no exact period exists.
- Design: legal(t) = frac(0.13 + t*alpha) < w, N 1000 uses per lag, lags 1 to 144, hint invalid iff legal at issue and illegal at use. Golden alpha with w 0.3 and 0.5, plus a silver alpha (sqrt2 - 1) w 0.3 built to break the claim; cutoff c admits all lags up to c.
- Got right: On golden rotation every lag up to 144 has valid hints, so the lossless cutoff is 144; gate-only cumulative invalid is monotone and maximal there (30145 at w 0.3); the continuous formula matched every lag within 0.11 percent of N; invalid fell to 8 at lag 55 and 5 at lag 89 against a 262 median at lags 40 to 70.
- Where/why it failed: On the silver rotation the lossless cutoff was 143, not the scan limit, because lag 144 has no valid hint; cumulative invalid there was 30191 but 30492 at cutoff 144, so cutoffs past the lossless one are strictly worse, and the lossless cutoff is the knee not the peak.
- Fix: Do not treat the lossless cutoff as the peak or as a fixed number on quasiperiodic state; compute per-lag invalid from the continuous formula and choose the cutoff from that table, preferring near-recovery lags.
- Why this fix: Valid presses stop growing at the lossless cutoff while invalid ones keep growing in every lag admitted, so the gate-only cost is a non-decreasing sum whose last useful step is the lossless cutoff.
- Rule of thumb: On quasiperiodic state the gate-only invalid count per lag is N x min(w, |lag x alpha|, 1-w) (error 0.1 percent), so predict it instead of assuming a period; the lossless cutoff then depends on the scan limit and phase, and any larger cutoff only adds invalid presses.
- Provenance (verified/assumed): Verified first-hand by running the sandbox below; one fixture size N 1000 and two rotation numbers; one-sided legality only, model of an input buffer, not an engine.
- Composed: lossless-cutoff-is-worst-without-validity/E1, sandbox-one-sided-formula-explains-gate-invalid-counts/E1, sandbox-quasiperiodic-near-recovery-at-fibonacci-lags/E1
- Picked-by: new-half
- ZaneGPT verdict: weak — The per-lag formula is well supported (error about 0.1 percent), but it is nearly a restatement of the measure of a rotation-interval overlap, while the cutoff-as-peak half was contradicted by your own silver case and the "any larger cutoff only adds invalid presses" wording overstates it.
- Hidden assumption: Gate-only invalid count is a stationary property of the rotation, so min(w, |lag·α|, 1-w) measured at one phase (0.13) and N=1000 uses carries over to other phases, scan limits and cutoff behavior, while "lossless cutoff = peak" is treated as a structural fact when it is only where the scan stopped.
- Would prove it wrong: Rerunning with a different phase offset or scan limit (say 233 or 89) moves the lossless cutoff and the cumulative maximum to different lags, or a silver or other badly approximable alpha shows a cumulative maximum well before the lossless cutoff; the silver run (lossless 143, 30191 at it versus 30492 at 144) already shows the peak sitting past the lossless point.
- Break scenario: Silver alpha (sqrt2 - 1) with w 0.3, phase swept across 20 values and scan limits 89, 144 and 233, checking whether the argmax of cumulative invalid ever differs from the lossless cutoff and whether per-lag error stays under 2 percent at lags near convergent denominators (29, 70, 169) where |lag·α| is tiny.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-18 · digest 0dd157af959a
- Polarity: compatible
- Sandbox: sandboxes/2026-10-18__lossless-cutoff-worst-gate-only-holds-on-golden-rotation-with-continuous-formula.py
- Prediction: Written before the first run: golden lossless cutoff equals the scan limit 144, cumulative gate-only invalid is monotone with its maximum at that cutoff, the continuous formula is within 2 percent of N at every lag, invalid at lags 55 and 89 is at most 10; the silver rotation was expected to behave the same.
- Observed: RESULT: PASS lossless=144/144, monotone, formula error 0.0011 golden and 0.0010 silver, inv55=8 inv89=5; the silver case broke the expectation: lossless 143, cumulative 30191 at it versus 30492 at 144.
- Scenarios: 1) golden w 0.3 cutoff scan; 2) golden w 0.5; 3) silver rotation w 0.3, built to break the claim that the lossless cutoff holds the maximum; 4) per-lag formula check over lags 1 to 144 for all three.
- Link: https://claude.ai/code/session_01MRoVc2AE75bu8wwdpoV7jJ
- Audited: 2026-10-19 · pass · Read the entry and its stored sandbox. The model computes invalid and valid counts by brute-force simulation of the rotation signal and compares them with the closed form N*min(w,|L*alpha|,1-w), so the formula result (error about 0.001 of N) is not built in. Two weaker points: the monotone-cumulative check is true by construction (invalid counts are non-negative), and the Rule of thumb says the lossless cutoff depends on phase, but the sandbox used a single phase offset 0.13. I reran it with offsets 0.0, 0.13, 0.37, 0.61 and 0.9: lossless cutoff stayed 144 for golden and 143 for silver at every offset and formula error stayed under 0.002, so the phase wording is untested in the original and in my rerun the cutoff did not move with phase. The claim is about an abstract signal, not a real engine, so pass holds for the formula and the silver break, with the phase dependence unsupported. · brain train auto pass 3, session_01VhAwkB8mF1QZBzEKkezmN5
