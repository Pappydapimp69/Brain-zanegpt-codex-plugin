# local/sandbox-kernel-performance-algorithms — lessons

Project: local/sandbox-kernel-performance-algorithms. Newest first.

---

## E1 — timsorts small n threshold is set by moves not comparisons
- Date: 2026-09-28
- Project: local/sandbox-kernel-performance-algorithms
- Tags: [performance][algorithm][sorting][measurement]
- What: Applied the ideas kernel that CPython's sort deliberately uses O(n^2) binary insertion sort for small inputs because comparisons, not data moves, dominate. The threshold and its mechanism reproduced from real comparison counts, and binary insertion never lost on comparisons at any size tested; data moves are what rule it out.
- Why built: brain train gap listed the kernel as unapplied. The kernel left the exact threshold unverified against a shipped CPython.
- Design: Counted comparisons made by CPython 3.11.15's own sorted() through a counting comparator, over 200 random permutations per size (40 at 1024), beside binary insertion sort (comparisons and element moves), top-down merge sort and linear insertion sort, for n from 8 to 1024. Then checked, for 100 random lists per size, whether CPython's count exactly equals one count_run pass plus binary insertion of the rest.
- Got right: Counting moves beside comparisons. On comparisons alone binary insertion looks best at every size, which cannot explain why CPython stops using it.
- Where/why it failed: CPython's count matched count_run plus binary insertion in 100 of 100 lists at n=10, 30 and 63 and in only 9 or 10 of 100 at n=64, 65 and 100, placing the switch at 64 in 3.11. Binary insertion used the fewest comparisons at every size, 293 vs 299 for merge sort at 63 and 8826 vs 8948 at 1024, while its element moves grew quadratically: 955 vs 377 at 63 (2.5x) and 261437 vs 10240 at 1024 (25x). Linear insertion made about 3.5x the comparisons of binary insertion at 63.
- Fix: When choosing a small-n cutoff for a hybrid algorithm, count both comparisons and moves at the sizes you have, and set the cutoff where moves, the quadratic term, start to outweigh the comparisons saved.
- Why this fix: Binary insertion minimises comparisons at every size; what makes it lose at large n is quadratic movement, cheap per element (a memmove) but growing without bound.
- Rule of thumb: CPython 3.11 sorts lists under 64 by binary insertion (its comparison count matched exactly in 100/100 lists below 64, about 10/100 at 64 and above), and binary insertion never loses on comparisons (8826 vs 8948 for merge sort at n=1024); what caps it is quadratic element movement (955 vs 377 moves at 63, 261437 vs 10240 at 1024).
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b09.py loop 42 in Pappydapimp69/Brain against CPython 3.11.15's real list sort, deterministic seeded permutations. Observed: the comparison and move table for n=8..1024 and the exact-match counts 100/100/100/9/9/10 at n=10/30/63/64/65/100. Other CPython versions compute minrun differently and were not run.
- Composed: ideas:PERFORMANCE/algorithms/asymptotic-complexity/timsort-uses-quadratic-sort-below-a-threshold-on-purpose
- Link: session 2026-09-28, brain train gap batch 9 loop 42
- Sandbox: sandboxes/2026-09-28__train-gap-b09.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)
- Cited-by: 2026-10-09 · projects/local__sandbox-kernel-sorting-comparator.md#E1 · incompatible · sandboxes/2026-10-09__sorting-invalid-comparator-order-dependent-outputs.py · observed Python 3.13 RESULT: FAIL py3.13 original predictions refuted: P2 rps cycle, P7 fixes, P8 scale, P9 timsort model (rps=24 distinct, n=96 185/200, model n=40 114/200). On 3.11 and 3.12 the RESULT line is FAIL with P7 and P8 refuted (rps=12 d… · brain train gap pass 5 (sandbox run in this session); session_01YFLLRpDsfZpRstb2KT2MQy
