# local/gate-invalid-formula-needs-lag-mod-period-for-lags-above-period — lessons

Project: local/gate-invalid-formula-needs-lag-mod-period-for-lags-above-period. Newest first.

---

## E1 — gate invalid formula needs lag mod period for lags above period
- Date: 2026-10-18
- Project: local/gate-invalid-formula-needs-lag-mod-period-for-lags-above-period
- Tags: [gamedev][input][state][testing]
- What: The gate-only invalid count (N/P) times min(L, W, P-L, P-W) stays exact for lags above the period only if L is first reduced mod P: it matched on all 47 lags of P12 W4 and all 39 lags of P10 W3, while the unreduced formula was wrong on 35 of 47 lags, and every lag that is a multiple of P gave 0 invalid presses.
- Why built: New-half train pick joining the age-cutoff lossless threshold (lags 20 and 24 above P12) with the lossless-cutoff-is-worst entry and the per-period-constant invalid count, none of which had run the invalid formula on lags beyond P-1.
- Design: Deterministic, N 600 ticks from base 3P, legal(t) is t mod P under W; a hint issued at t-L names B iff legal then, and is invalid at use iff now illegal. Brute-force counts for lags 1 to 47 compared with the formula with and without L mod P; lossless cutoff for lag sets S1 {1,3,7,20} and S3 {5,12,24} taken as the largest lag, then gate-only invalid totals summed at that cutoff.
- Got right: Reduced formula had zero mismatches on both wave shapes; at the validity-lossless cutoffs 20 and 24 the gate-only invalid totals were 600 for S1 (50+150+200+200) and 200 for S3 (lags 12 and 24 contribute 0), exactly as predicted.
- Where/why it failed: My first sandbox run failed because I defined a valid press as legal at both issue and use, which makes lags 7 and 20 never valid and gave a lossless cutoff of 3; the established model issues A (always legal) when B is unavailable, so every lag has valid presses. The raw formula also goes negative for L above P.
- Fix: Reduce the lag mod P before applying min(L, W, P-L, P-W), and take the lossless cutoff under the same hint model the earlier entries used; for lags that are multiples of P the gate is harmless.
- Why this fix: Legality depends only on t mod P, so a lag and the same lag plus a whole period are indistinguishable to the gate; only the validity-guarded cutoff cares about the raw lag.
- Rule of thumb: The gate-only invalid count depends on the lag only through L mod P, so a lossless cutoff that exceeds the period can still admit zero invalid presses at lags that are multiples of P; apply the formula to L mod P.
- Provenance (verified/assumed): Verified first-hand by running the saved sandbox; P12 W4 and P10 W3 only, one contiguous legal window, hint model with an always-legal fallback role.
- Composed: age-cutoff-lossless-threshold-exceeds-period-p12/E1, lossless-cutoff-is-worst-without-validity/E1, gate-invalid-count-is-per-period-constant-and-cutoff-scales-it-linearly/E1
- Picked-by: new-half
- ZaneGPT verdict: weak — The mod-P reduction is sound for the strictly periodic gate and the pre-stated prediction held, but the lesson claims generality from two (P, W) pairs. It also reports the S1 and S3 totals (600, 200) without showing the formula explains them; I'd expect them to reflect the cutoff landing on specific L mod P values, not the formula.
- Hidden assumption: The formula min(L, W, P-L, P-W) with L reduced mod P is treated as a law of the lag, but it was verified only inside one hint model (deterministic legal(t)=t mod P under W, one blocked state B, N=600 from base 3P). Its exactness rests on that model's periodic gate, on W being below P/2, and on N being a multiple of P. "Depends only on L mod P" is a property of a periodic legal(t), not of lag in general.
- Would prove it wrong: A lag whose brute-force invalid count differs from the reduced formula. That could happen with a non-periodic or jittered gate, with W ≥ P/2 (the min then picks the wrong term), with N not a multiple of P (edge ticks add or drop presses), or with a base offset other than 3P. Any one of these would also show the "exact on all 47/39 lags" result is a coincidence of the chosen parameters.
- Break scenario: Take P12 with W7 (W > P/2) and N=605, so N is not a multiple of P. Run the brute-force count for lags 1 to 47 against N/P × min(L mod P, W, P−L mod P, P−W). The min term should misbehave once W exceeds P−W. The N/P factor is fractional, so the count should be off by the 5 leftover ticks. Also run a gate where legal(t) has a phase drift of one tick per period. The mod-P reduction should then fail, because lag no longer collapses to L mod P.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-18 · digest c1df35764936
- Polarity: compatible
- Sandbox: sandboxes/2026-10-18__gate-invalid-formula-needs-lag-mod-period-for-lags-above-period.py
- Prediction: Reduced formula exact on all 47 lags of P12 W4 and 39 lags of P10 W3, unreduced formula wrong on at least 30 lags, multiples of P give 0, and gate-only invalid at the lossless cutoff is 600 for S1 and 200 for S3.
- Observed: RESULT: PASS mod-reduced formula exact on 47 lags P12W4 and 39 lags P10W3; raw formula wrong on 35 lags; S1 cutoff 20 invalid 600; S3 cutoff 24 invalid 200 (first run FAILED from my wrong valid-press definition, fixed to the established hint model before the final run).
- Scenarios: 1) lags 1..47 on P12 W4 against reduced formula; 2) lags 1..39 on P10 W3; 3) BREAK: unreduced formula on lags above P; 4) lag multiples of P 12, 24, 36; 5) S1 and S3 lossless cutoffs with gate-only invalid totals
- Link: scheduled brain train auto loop 1 pass 1; session_014AVjf81yxBZXZ5b84ovVC5
- Cited-by: 2026-10-19 · projects/local__lag-mod-period-zero-at-multiples-holds-only-for-periodic-legality-fibonacci-word-has-no-zero-lags.md#E1 · compatible · sandboxes/2026-10-19__lag-mod-period-zero-at-multiples-holds-only-for-periodic-legality-fibonacci-word-has-no-zero-lags.py · observed RESULT: PASS periodic multiples of 12 invalid [0, 0, 0, 0, 0, 0]; Fibonacci-word fib lags {8: 33, 13: 21, 21: 12, 34: 8, 55: 4, 89: 3} (never 0), window median 158; nominal-P13 formula wrong on 103/120 lags · scheduled brain train auto, loop 1 pass 5; session_01W1FCx5tpnHusaTASoCMosY
