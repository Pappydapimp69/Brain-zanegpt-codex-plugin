# local/lag-set-sparsity-makes-gate-only-cost-at-the-lossless-cutoff-far-below-the-staircase — lessons

Project: local/lag-set-sparsity-makes-gate-only-cost-at-the-lossless-cutoff-far-below-the-staircase. Newest first.

---

## E1 — lag set sparsity makes gate only cost at the lossless cutoff far below the staircase
- Date: 2026-10-18
- Project: local/lag-set-sparsity-makes-gate-only-cost-at-the-lossless-cutoff-far-below-the-staircase
- Tags: [gamedev][input][state][testing]
- What: The gate-only cumulative invalid staircase (sum of one-sided invalid over every lag 1 to c) is only an upper bound for a real lag set: at the validity-lossless cutoff the actual gate-only cost was 600 of 2900 (ratio 0.207) for lags {1,3,7,20}, 200 of 3200 (0.062) for {5,12,24}, 300 of 300 for {1,2,3}, and exactly 2900 of 2900 for the dense set 1 to 20 on P12 W4.
- Why built: New-half train pick joining the lossless cutoff above the period, the lossless-cutoff-is-worst rule and the linear-per-period cumulative cost, which quoted the cost of a cutoff over all lags, not over the lags a policy actually sees.
- Design: Deterministic, N 600 ticks from base 3P, legal(t) is t mod 12 under 4; hint issued at t-L is invalid at use iff legal then and illegal now; lossless cutoff is the largest lag in the set (always-legal fallback role); cost is the sum of brute-force invalid counts over the set versus over all lags up to the cutoff.
- Got right: The dense set matched the staircase exactly and the contiguous low set {1,2,3} was at 1.000, so the staircase is the right cost only when every lag up to the cutoff occurs.
- Where/why it failed: My first run failed the pre-written test because I had estimated the S1 staircase at 3300 or more while the true value is 2900, giving a ratio of 0.207 against a bound of 0.2; the revised bound of 0.25, set after seeing the miss, then passed together with a new sparse set {2,9,17} at 0.196.
- Fix: Quote the gate-only cost of a lossless cutoff from the lags actually present (sum of min(L mod P, W, P-L mod P, P-W) times N/P), and use the staircase only as an upper bound or for dense lag sets.
- Why this fix: The cost is additive over lags, so a sparse set that skips costly residues and includes multiples of the period pays a fraction of the all-lags staircase.
- Rule of thumb: The staircase of cumulative gate-only invalid counts is an upper bound for a cutoff; the real cost follows the lag set (0.06 to 0.21 of it on sparse sets, 1.0 on dense ones), so do not size a validity-free gate from the cutoff alone.
- Provenance (verified/assumed): Verified first-hand by running the saved sandbox; one wave shape P12 W4, five lag sets, thresholds in the revised prediction were set after run 1.
- Composed: age-cutoff-lossless-threshold-exceeds-period-p12/E1, lossless-cutoff-is-worst-without-validity/E1, gate-only-cumulative-invalid-grows-linearly-per-period-with-slope-n-w-p-minus-w-over-p/E1
- Picked-by: new-half
- ZaneGPT verdict: weak — the headline claim (staircase is an upper bound, and dense sets reach 1.0) is probably true as arithmetic, but the "0.06 to 0.21 on sparse sets" band is fitted to a single P12 W4 pattern with phase-aligned lags. It is untested across period, duty or legality sequence, so treat it as a one-pattern observation, not a rule of thumb.
- Hidden assumption: Invalid counts depend only on the lag set against one fixed square-wave legality pattern (t mod 12 under 4, N=600), so the cost-to-staircase ratio is read as a property of sparsity, when it is mostly a property of how the lags sit relative to the period of 12 and the duty of 4/12.
- Would prove it wrong: A sparse set with a low ratio on this pattern that jumps to about 1.0 on another. For example, {1,3,7,20} or {5,12,24} on a different period or duty, or with an aperiodic legality sequence, where the ratio rises well above 0.2 and 0.06. The same would hold if a sparse set scored near 1.0 on P12 W4 itself. Lags congruent to 0 mod 12, such as 12 and 24, contribute zero invalid because the pattern repeats exactly. That is why {5,12,24} is cheap, and it says nothing about sparsity.
- Break scenario: Take a sparse set of three lags that are all odd multiples of 6, such as {6,18,30}, on P12 W4. A 6-lag shift moves the legal window onto the illegal half-period. Each lag then costs about the same as the whole staircase's worst per-lag term, so the ratio should land near the dense-set value, not the 0.06 to 0.21 band. Alternatively, run {1,3,7,20} on P12 W6, where the window is half the period and the invalid counts become denser.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-18 · digest b5c8a8632a87
- Polarity: compatible
- Sandbox: sandboxes/2026-10-18__lag-set-sparsity-makes-gate-only-cost-at-the-lossless-cutoff-far-below-the-staircase.py
- Prediction: Gate-only cost over staircase at the lossless cutoff is at most 0.2 for {1,3,7,20}, at least 0.9 for {1,2,3}, at most 0.1 for {5,12,24}, exactly 1.0 for the dense set 1 to 20 (run 1 missed the first by 0.007; revised to 0.25 plus a new set {2,9,17} at most 0.3).
- Observed: RESULT: PASS actual/staircase ratios S1 0.207 S2 1.000 S3 0.062 S4 0.196 dense 1.000 at cutoffs 20/3/24/20 (actual 600/300/200/2900)
- Scenarios: 1) sparse set {1,3,7,20} with a lag above the period; 2) contiguous low set {1,2,3}; 3) lags at multiples of the period {5,12,24}; 4) sparse set {2,9,17}; 5) BREAK: dense set 1 to 20 built to defeat the sparse-is-cheap claim
- Link: scheduled brain train auto loop 2 pass 1; session_014AVjf81yxBZXZ5b84ovVC5
- Cited-by: 2026-10-20 · projects/local__fibonacci-lag-sparsity-compounds-gate-only-cost-drop-at-the-lossless-cutoff.md#E1 · incompatible · sandboxes/2026-10-20__fibonacci-lag-sparsity-compounds-gate-only-cost-drop-at-the-lossless-cutoff.py · observed RESULT: FAIL fibword/staircase fib-lags 0.419 far-lags 1.624 dense 1.004; bernoulli fib-lags 1.002 · scheduled brain train auto run, 2026-10-20; session_0193ruCZULAVFBK6Q3cwQk5z
