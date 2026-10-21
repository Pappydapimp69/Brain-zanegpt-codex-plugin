# local/learned-cutoff-on-fibonacci-word-gate-only-invalid-follows-outlier-lag-not-cutoff — lessons

Project: local/learned-cutoff-on-fibonacci-word-gate-only-invalid-follows-outlier-lag-not-cutoff. Newest first.

---

## E1 — learned cutoff on fibonacci word gate only invalid follows outlier lag not cutoff
- Date: 2026-10-18
- Project: local/learned-cutoff-on-fibonacci-word-gate-only-invalid-follows-outlier-lag-not-cutoff
- Tags: [gamedev][input][state][testing]
- What: Ran a learned running-maximum cutoff gate-only on a Fibonacci-word legality signal and found the gate's total invalid rate does not drop when the outlier lag is a Fibonacci number: 22.8 percent at outlier lags 55 and 89 against 24.0 percent at 60 and 70, because small base lags carry about 110 of the roughly 112 to 132 invalid presses.
- Why built: Train pick: the Fibonacci lesson says gate-only invalid is near zero at Fibonacci lags and the learned-cutoff lesson says the cutoff is set by one late outlier; nobody had asked whether the outlier's lag being Fibonacci makes the learned gate safe.
- Design: Fibonacci word of length 4000 (1 to 10, 0 to 1, legal means 1); 500 presses at t = 3i + 1 with lag 1 + i mod 5 and every seventh press carrying the outlier lag 55, 89, 34, 60 or 70; valid iff legal at issue and at use; learned cutoff is the max valid lag in the first 140 presses; gate-only executes all presses at or under the cutoff.
- Got right: Per outlier press the Fibonacci near-recovery is real: invalid outlier presses were 0 at lag 55, 2 at 89 and 2 at 34 against 8 at lag 60 and 20 at lag 70 (of 71); at non-Fibonacci outliers the learned cutoff stayed 5 and lost 28 and 16 valid presses.
- Where/why it failed: The prediction that the total gate-only invalid rate would be under 10 percent at Fibonacci outliers and over 20 percent at the others was refuted: both sit near 23 to 24 percent, since the five base lags dominate the count (about 110 invalid presses of 500 regardless of the outlier).
- Fix: Do not read a low per-lag invalid count at one outlier lag as a safe gate; budget the whole stream, where the frequent small lags set the floor, and treat the outlier lag as a second-order term worth 0 to 20 presses here.
- Why this fix: The gate's cost is a sum over every admitted press, so a rare lag with near recovery cannot offset the common lags that have none; measuring it per lag hides this.
- Rule of thumb: A near-recovery lag lowers the gate-only invalid count only for the presses that carry that lag; with frequent small-lag presses the total is set by them, so cost the whole stream before trusting a Fibonacci-lag cutoff.
- Provenance (verified/assumed): Verified first-hand by running the sandbox below; one signal family (Fibonacci word), one press schedule, five outlier lags; no jitter or other signals tried.
- Composed: fibonacci-lag-cutoff-makes-the-gate-only-invalid-count-small-not-worst/E1, lossless-cutoff-is-worst-without-validity/E1, learned-cutoff-is-lossless-only-after-the-max-valid-lag-outlier-is-seen/E1
- Picked-by: new-half
- ZaneGPT verdict: weak — the finding that the total is set by the small base lags is supported (outlier-press invalid 0–20 against ~110 of ~120 total), but the rule is stated for "near-recovery lags" in general, yet it rests on one stream, one 140-press learning window, five outliers and no variance estimate, so the 0.228 vs 0.240 comparison and the cutoff behaviour are not shown to be anything more than a coincidence of that window.
- Hidden assumption: Fibonacci-ness of the outlier lag is the causal variable. That treats a lag's Fibonacci status as the thing driving legality at use, when the data show small base lags dominate the invalid count (~110 of 112–132), and the 55/89 vs 60/70 contrast is confounded by the learned cutoff collapsing to 5 only for the non-Fibonacci cases.
- Would prove it wrong: Hold the base lags and outlier lag fixed, vary only the 140-press learning window or its start offset, and find that cutoff = outlier lag for some non-Fibonacci outliers (e.g., 60) or that 55/89 fall to 5 for some windows. Equally, a total invalid rate that stays at about 23–24% whatever the outlier lag, Fibonacci or not, and across window changes, would show the lag type is not what drives the total. The 22.8 vs 24.0 gap needs a seed or offset spread to show it exceeds noise.
- Break scenario: Drop the base lags to {1} (or raise them to Fibonacci values like 1, 2, 3, 5, 8 and compare against 4, 6, 7, 9, 10) with the outlier fixed at 55. If total invalid rate is still ~23% while outlier-press invalid stays 0, the total is set entirely by the base-lag mix, and "near-recovery lag" was never the variable. Also run a Fibonacci outlier with a window that includes an unlucky press, such as 144 or 233, to see whether the cutoff stays lossless.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-18 · digest 3d3f1066fa50
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-18__learned-cutoff-on-fibonacci-word-gate-only-invalid-follows-outlier-lag-not-cutoff.py
- Prediction: Written before the first run: total gate-only invalid rate under 10 percent when the outlier lag is 55 or 89 and over 20 percent when it is 60 or 70, and the learned cutoff equals the outlier lag when it is Fibonacci.
- Observed: RESULT: FAIL fib rate 0.228 vs nonfib 0.240; outlier-press-only invalid 0, 2, 8, 20, 2 for lags 55, 89, 60, 70, 34; learned cutoffs 55, 89, 5, 5, 34; valid loss at the learned cutoff 0, 0, 28, 16, 0.
- Scenarios: 1) outlier 55; 2) outlier 89; 3) outlier 34; 4) outlier 60, built to break the claim that only Fibonacci outliers keep the learned cutoff lossless; 5) outlier 70.
- Link: https://claude.ai/code/session_01MRoVc2AE75bu8wwdpoV7jJ

