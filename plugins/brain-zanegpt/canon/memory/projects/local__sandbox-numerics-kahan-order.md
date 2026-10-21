# local/sandbox-numerics-kahan-order — lessons

Project: local/sandbox-numerics-kahan-order. Newest first.

---

## E1 — kahan vs naive vs neumaier order and 2p53
- Date: 2026-10-10
- Project: local/sandbox-numerics-kahan-order
- Tags: [algorithm][determinism][floating-point][testing]
- What: Naive, Kahan and Neumaier float sums were compared with an exact Fraction sum on four cases: a million 0.1 terms, 2^53 plus a thousand ones, a mixed-magnitude set summed in four orders, and the adversarial set 1, 1e100, 1, -1e100.
- Why built: The Kahan kernel says naive summation drops small addends and compensation fixes it; the determinism entries say sum order changes results. I wanted to see whether Kahan also removes order dependence and where it fails.
- Design: Exact reference is a Fraction sum of the same float inputs. Order test uses the input, ascending, by magnitude and descending orders of a 200-term set with plus and minus 1e16 swings. math.fsum as a further check on the adversarial case.
- Got right: 0.1 x 1e6: naive error 1.33e-06, Kahan and Neumaier 5.55e-12 (about 240000x smaller). 2^53 plus 1000 ones: naive lost all 1000 (stuck at 2^53), Kahan and Neumaier recovered it exactly (error 0).
- Where/why it failed: Kahan did not make the sum order-independent: 2 distinct results over 4 orders (spread 4.65) versus 3 for naive (spread 239); only Neumaier's spread was negligible (2.8e-13). On the adversarial set plain Kahan returned 0.0 where the exact sum is 2.0, while Neumaier and math.fsum returned 2.0. My first prediction (one identical Kahan result) and second (1000x spread reduction) were both wrong and revised in the script header.
- Fix: Use Neumaier's variant (or math.fsum for a final exact total) when terms vary in magnitude or when order independence matters; plain Kahan is enough only for same-scale accumulation such as repeated small increments.
- Why this fix: Neumaier also tracks the lost low-order bits when the new term is larger than the running sum, which is exactly the case where Kahan's compensation is itself rounded away.
- Rule of thumb: Compensated summation fixes dropped small addends (a million 0.1s, ones above 2^53) but plain Kahan neither removes order dependence nor survives a large term cancelling; choose Neumaier or fsum for mixed-magnitude data, and do not claim determinism from Kahan alone.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; all numbers are from its output, on one 200-term test set and three other fixtures.
- Composed: ideas:NUMERICS/summation/naive-left-to-right-float-sum-silently-drops-small-addends, local__sandbox-kernel-system-determinism/E5, pappydapimp69__the-game-the-recursion/E21
- Polarity: compatible
- Sandbox: sandboxes/2026-10-10__kahan-vs-naive-vs-neumaier-order-and-2p53.py
- Prediction: Kahan beats naive by over 1000x on 0.1 x 1e6; Kahan recovers the ones above 2^53; sums in four orders differ for naive but Kahan gives one result (wrong, revised twice); plain Kahan fails on 1, 1e100, 1, -1e100 while Neumaier and fsum return 2.
- Observed: RESULT: PASS 0.1x1e6 naive err 1.33e-06 kahan 5.55e-12; 2^53+1000 ones naive lost 1000 kahan err 0; order results naive 3 kahan 2 neumaier 2 (spread naive 239 kahan 4.65); adversarial kahan 0.0 vs neumaier 2.0
- Scenarios: 1) million small increments; 2) ones added above 2^53; 3) four summation orders of a mixed-magnitude set; 4) adversarial large cancelling terms (built to BREAK plain Kahan)
- Link: scheduled brain train auto loop 2 pass 5 (gap); session_01PQ4jLSc8kGvXwYbpjoS24m
- Audited: 2026-10-12 · pass · Read the entry and re-ran its stored sandbox, which reproduces the recorded numbers (0.1 x 1e6 naive error 1.33e-06 against 5.55e-12 for Kahan; naive stuck at 2^53 and Kahan exact; adversarial set 0.0 for Kahan against 2.0 for Neumaier and fsum). Every figure is computed against an exact Fraction sum, nothing is assumed, and the script header openly records two failed predictions. The core Rule of thumb claims (Kahan fixes dropped small addends, does not remove order dependence, fails when a large term cancels) are covered by scenarios 1-4. One overreach: the Fix says to use Neumaier when order independence matters, but the same run shows Neumaier produced 2 distinct results over 4 orders (spread 2.8e-13, not zero), and math.fsum was only tested on the adversarial set, never across orders, so only 'Neumaier is far tighter' is shown, not 'order independent'. The order test is also one 200-term set. The claim concerns IEEE float arithmetic itself, which Python executes directly, so this is not a modeled stand-in. · scheduled brain train session; loop 2 pass 3 audit; session_01LL6VFqb8pBPKJxf8rLawar
