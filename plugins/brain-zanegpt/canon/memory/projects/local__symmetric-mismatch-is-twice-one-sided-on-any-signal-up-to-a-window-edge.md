# local/symmetric-mismatch-is-twice-one-sided-on-any-signal-up-to-a-window-edge — lessons

Project: local/symmetric-mismatch-is-twice-one-sided-on-any-signal-up-to-a-window-edge. Newest first.

---

## E1 — symmetric mismatch is twice one sided on any signal up to a window edge
- Date: 2026-10-18
- Project: local/symmetric-mismatch-is-twice-one-sided-on-any-signal-up-to-a-window-edge
- Tags: [gamedev][input][state][testing]
- What: Symmetric mismatch counts equal twice the one-sided invalid count to within L (the lag) for any legality signal, not only periodic ones: no violation of |sym - 2*one| <= L on a Fibonacci word, period 12 width 5, and 20 Bernoulli(0.618) seeds across lags 1 to 120, and the Fibonacci dips at lags 55 and 89 appear in both (one-sided 4 and 3, symmetric 8 and 6).
- Why built: New-half train pick joining the Fibonacci rotation-proximity dip with the lossless-cutoff-is-worst entry and the symmetric-versus-one-sided min-term entry, which only proved the factor of two for periodic legality.
- Design: Deterministic, N 600 ticks; one-sided counts t legal at t and illegal at t+L, backward counts the reverse, symmetric is their sum. The two differ only by the window-edge difference between legal sums, so the bound |sym-2*one| <= L should hold for any 0/1 signal. Signals: Fibonacci word by substitution, period-12 width-5 wave, 20 seeded Bernoulli, and a density ramp from 0.1 to 0.9.
- Got right: Zero bound violations on all 22 non-ramp signals at every lag 1 to 120, and the Fibonacci dip carried over to the symmetric count unchanged in shape and exactly doubled at lags 55 and 89.
- Where/why it failed: The break scenario, a density ramp, gave a relative deviation of 0.76 between symmetric and twice one-sided at some lag, so the factor two is not a relative-error claim; it is only an absolute bound of L, which matters when the invalid count at a dip lag is as small as 3 or 4.
- Fix: State the factor of two as sym = 2*one +/- L, and for dip lags with one-sided counts below about L do not infer the symmetric count from the one-sided one; count it directly.
- Why this fix: The difference of the two counts is a difference of legal sums over two windows shifted by L, so it is at most L whatever the signal, but it is not small compared with a count that has itself dropped near zero.
- Rule of thumb: Symmetric mismatch is twice the one-sided invalid count only to within L on any legality signal; near a dip where the one-sided count is below L, the symmetric count must be measured, not doubled.
- Provenance (verified/assumed): Verified first-hand by running the saved sandbox; 600-tick horizon only, lags 1 to 120, one Fibonacci word and one ramp.
- Composed: fibonacci-gate-drop-is-rotation-proximity-not-fibonacci-lags/E1, lossless-cutoff-is-worst-without-validity/E1, sandbox-symmetric-and-one-sided-agreement-share-min-term/E1
- Picked-by: new-half
- ZaneGPT verdict: weak — the bound is probably true, but it is a counting tautology that the Fibonacci/P12W5/Bernoulli sweep could not have falsified, and the practical advice ("measure near dips") follows from small counts relative to L, not from any property the tests probed.
- Hidden assumption: The "legal" signal is a fixed 0/1 sequence over a finite window, so sym = fwd + bwd and the two directions differ only by boundary terms of size at most L. The bound is an identity of counting (a telescoping edge effect), not a property of any legality signal. Nothing about Fibonacci, periodicity or dips is doing the work.
- Would prove it wrong: Any 0/1 signal where |sym − 2·one| exceeds L. That would mean the edge-term argument is miscounted. For example, the identity fails if one-sided counts use a different window than backward counts (t+L < N versus t−L ≥ 0). It also fails if "legal" is state-dependent, so legality at t changes with which side is being probed.
- Break scenario: Use a non-stationary or adversarial signal rather than a seeded random one. Put all the legal ticks in the first L slots and all the illegal ticks after them: forward counts L transitions, backward counts 0, so |sym − 2·one| = L exactly, with no slack. Then run a signal whose legality depends on the probe direction, and the bound should fail there. Also check the ramp: its 0.76 relative deviation shows the "double it" part is useless wherever density varies, and the rule of thumb understates this by calling it a mere "within L" matter.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-18 · digest a70c4c377882
- Polarity: compatible
- Sandbox: sandboxes/2026-10-18__symmetric-mismatch-is-twice-one-sided-on-any-signal-up-to-a-window-edge.py
- Prediction: No bound violation on Fibonacci, P12W5 or 20 Bernoulli seeds over lags 1 to 120; fib lags 55 and 89 symmetric at most 12 and one-sided at most 6; the density ramp exceeds 0.2 relative deviation at some lag.
- Observed: RESULT: PASS |sym-2*one|<=L on fib, P12W5 and 20 Bernoulli seeds over lags 1..120 (violations 0/0/0); fib55 one/sym (4, 8), fib89 (3, 6); ramp rel dev 0.76
- Scenarios: 1) Fibonacci word lags 1..120; 2) period 12 width 5 lags 1..120; 3) 20 Bernoulli seeds; 4) BREAK: density ramp 0.1 to 0.9 relative deviation; 5) dip lags 55 and 89 one-sided versus symmetric
- Link: scheduled brain train auto loop 1 pass 2; session_014AVjf81yxBZXZ5b84ovVC5
- Cited-by: 2026-10-19 · projects/local__symmetric-mismatch-cumulative-over-cutoff-is-exactly-twice-gate-count-at-whole-periods-and-drifts-within-lag-sum-on-a-tail.md#E1 · incompatible · sandboxes/2026-10-19__symmetric-mismatch-cumulative-over-cutoff-is-exactly-twice-gate-count-at-whole-periods-and-drifts-within-lag-sum-on-a-tail.py · observed RESULT: PASS (revised claim) N=48 per-lag (one,back) e.g. L=1 (4,3), L=5 (20,15); one-sided cum 140, sym 245 vs 2x 280 (dev 35 <= 66), exact-doubling lags 0/11, formula 11/11; N=55 dev 10, N=61 dev 28; per-lag violations 0. Exact-doubling… · scheduled brain train auto, loop 1 pass 2; session_01W1FCx5tpnHusaTASoCMosY
