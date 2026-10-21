# local/josephus-recurrence-matches-simulation-and-binary-rotation-is-k2-only — lessons

Project: local/josephus-recurrence-matches-simulation-and-binary-rotation-is-k2-only. Newest first.

---

## E1 — josephus recurrence matches simulation and binary rotation is k2 only
- Date: 2026-10-18
- Project: local/josephus-recurrence-matches-simulation-and-binary-rotation-is-k2-only
- Tags: [josephus][testing][algorithm]
- What: For the Josephus circle (n people, every k-th eliminated) the O(n) recurrence J(n) = (J(n-1) + k) mod n matched a direct list simulation in all 600 cells for k 2 to 7 and n 1 to 100, and the k = 2 closed form of rotating the leading bit of n to the end matched on all 300 n, but the same rotation applied to k = 3 was wrong on 95 of 99 values of n.
- Why built: New domain seed from a real classic, the Josephus problem as told by Flavius Josephus, to fix which of the two well-known shortcuts generalizes before anyone reuses the elegant bit trick for another step size.
- Design: Deterministic, no RNG. Simulation pops the (i + k - 1) mod len-th person from a list until one remains; the recurrence runs 0-based; the bit rotation is (n minus its top bit) shifted left plus 1 and compared to the 1-based simulation; an off-by-one variant counting k + 1 was run to see how a counting slip shows up.
- Got right: The recurrence agreed with simulation everywhere tested, so it is the safe general tool, and the bit rotation was exact for k = 2 at every n up to 300.
- Where/why it failed: Applying the k = 2 bit trick to k = 3 failed on 95 of 99 values of n, and an off-by-one in counting (stepping k instead of k - 1 from the current index) disagreed with the recurrence on 95 of 99 values of n for k = 2, so the two slips look alike and both fail quietly.
- Fix: Use the recurrence for any k, check it against a small simulation at the start, and keep the bit rotation only as a k = 2 shortcut; make the counting convention (first person counted is number one) explicit in the test.
- Why this fix: The recurrence follows from relabeling the circle after each elimination, which holds for every k, whereas the bit rotation follows from halving the circle, which needs k = 2.
- Rule of thumb: Verify a Josephus-style closed form against a brute-force simulation for each step size you use; the leading-bit rotation is k = 2 only and an off-by-one in counting wrecks most n without crashing.
- Provenance (verified/assumed): Verified first-hand by running the saved sandbox; n up to 300, k 2 to 7; the recurrence itself is textbook, and being checked against a simulation rather than proved.
- Composed: N/A
- Polarity: compatible
- Sandbox: sandboxes/2026-10-18__josephus-recurrence-matches-simulation-and-binary-rotation-is-k2-only.py
- Prediction: Recurrence equals simulation in all 600 cells, bit rotation equals simulation for k = 2 on all n to 300, bit rotation wrong on over half of n for k = 3, and the off-by-one variant differs from the recurrence at some n.
- Observed: RESULT: PASS recurrence matches simulation on 600 cells (k 2..7, n 1..100); k=2 bit-rotation exact on 300 n; same rule wrong for k=3 on 95 of 99 n; off-by-one counting wrong on 95 of 99 n
- Scenarios: 1) recurrence versus simulation for k 2 to 7; 2) k = 2 bit rotation to n 300; 3) BREAK: the bit rotation applied to k = 3; 4) off-by-one counting variant
- Link: scheduled brain train auto loop 2 pass 6; session_014AVjf81yxBZXZ5b84ovVC5

