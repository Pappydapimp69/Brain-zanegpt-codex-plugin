# local/symmetric-mismatch-cumulative-over-cutoff-is-exactly-twice-gate-count-at-whole-periods-and-drifts-within-lag-sum-on-a-tail — lessons

Project: local/symmetric-mismatch-cumulative-over-cutoff-is-exactly-twice-gate-count-at-whole-periods-and-drifts-within-lag-sum-on-a-tail. Newest first.

---

## E1 — symmetric mismatch cumulative over cutoff is exactly twice gate count at whole periods and drifts within lag sum on a tail
- Date: 2026-10-19
- Project: local/symmetric-mismatch-cumulative-over-cutoff-is-exactly-twice-gate-count-at-whole-periods-and-drifts-within-lag-sum-on-a-tail
- Tags: [simulation][method][gate][testing]
- What: A deterministic model on period-12 width-5 legality that adds up one-sided gate-only invalid counts and symmetric mismatch counts over lags 1 to 11 at horizons 48, 55 and 61, to test whether the cumulative symmetric total is twice the cumulative one-sided total.
- Why built: Three earlier results say the gate invalid count is a per-period constant, symmetric mismatch is twice one-sided within L, and the lossless cutoff is worst; I predicted that composed, the cumulative symmetric total at whole periods would be exactly twice the cumulative one-sided total.
- Design: legal(t) is t mod 12 under 5; one-sided counts t legal at t and illegal at t+L, backward counts the reverse, symmetric is their sum, each over t below N-L. Per-lag formula (N/P)*min(L,W,P-L,P-W) is checked at N=48 and the cumulative totals over lags 1..11 are compared with twice the one-sided totals.
- Got right: The per-lag formula was exact in 11 of 11 lags at N=48, the cumulative one-sided total came to 140, and the per-lag bound |sym-2*one| <= L held with 0 violations at all three horizons.
- Where/why it failed: The prediction that symmetric would be exactly 280 at N=48 was refuted: the symmetric total was 245 and no lag had exact doubling (0 of 11). The per-lag table shows why: forward counts are 4,8,12,16,20,20,20,16,12,8,4 but backward counts are 3,6,9,12,15,15,15,12,9,6,3, because the signal starts legal at t=0 and the last illegal-to-legal edge falls past the end of the window. The deviation is 35 at N=48, 10 at N=55 and 28 at N=61, inside the sum of lags 66.
- Fix: Do not double the cumulative one-sided total to get the symmetric total even at whole periods; measure the symmetric count directly, or bound its error by the sum of the lags used in the cutoff.
- Why this fix: The per-lag bound of L is tight enough that it never broke, but summing it over a cutoff multiplies the slack, so the cumulative bound of the sum of L is the honest limit and the exact figure needs a direct count.
- Rule of thumb: On period-12 width-5 legality starting legal at t=0 the backward count was three quarters of the forward count at whole periods, so the symmetric total was 245 against the doubled 280; count the symmetric total directly or bound it by the sum of lags instead of doubling the gate-only total.
- Provenance (verified/assumed): Verified first-hand by running the saved sandbox; the first run failed my exact-doubling prediction and the saved script asserts the revised claim, PASS with deterministic output on one synthetic signal.
- Composed: lossless-cutoff-is-worst-without-validity/E1, symmetric-mismatch-is-twice-one-sided-on-any-signal-up-to-a-window-edge/E1, gate-invalid-count-is-per-period-constant-and-cutoff-scales-it-linearly/E1
- Polarity: incompatible
- Picked-by: new-half
- ZaneGPT verdict: weak — the 245 and 280 figures and the "count directly, don't double" advice are sound, but "three quarters" is stated as a pattern property when it is a (k-1)/k edge effect from one tested N, and the bound |sym-2*one| <= sum of lags was checked at only three horizons.
- Hidden assumption: The 3/4 backward-to-forward ratio is a property of the period-12 width-5 pattern. It looks like an artifact of the window edge. The window starts legal and the cut at t<N-L drops the final period's illegal-to-legal transition, so the ratio is (k-1)/k for k whole periods, and k=4 is the only case tested.
- Would prove it wrong: At N=96 or N=120 (whole periods), a backward/forward ratio of 7/8 or 9/10 instead of 3/4, so the symmetric total is 2*one minus one/k rather than 245 against 280. A phase shifted to start illegal, where backward exceeds forward, would show the same thing.
- Break scenario: Run N=96 at offset 0 (predicted: symmetric 2*280 − 70 = 490, not 3/4-based), and the same N=48 with legal(t) = (t+7) mod 12 < 5, where the window ends legal and the deficit should move from the backward count to the forward count.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-19 · digest 3306d4fb754b
- Sandbox: sandboxes/2026-10-19__symmetric-mismatch-cumulative-over-cutoff-is-exactly-twice-gate-count-at-whole-periods-and-drifts-within-lag-sum-on-a-tail.py
- Prediction: At N=48 the cumulative one-sided total is 140 and the symmetric total is exactly 280 with exact doubling in all 11 lags; at N=55 and N=61 doubling breaks for some lags while |sym-2*one| <= L holds.
- Observed: RESULT: PASS (revised claim) N=48 per-lag (one,back) e.g. L=1 (4,3), L=5 (20,15); one-sided cum 140, sym 245 vs 2x 280 (dev 35 <= 66), exact-doubling lags 0/11, formula 11/11; N=55 dev 10, N=61 dev 28; per-lag violations 0. Exact-doubling prediction refuted.
- Scenarios: 1) N=48 whole periods; 2) N=55 partial tail; 3) BREAK: N=61 partial tail with a different offset; 4) per-lag formula check at whole periods
- Link: scheduled brain train auto, loop 1 pass 2; session_01W1FCx5tpnHusaTASoCMosY

