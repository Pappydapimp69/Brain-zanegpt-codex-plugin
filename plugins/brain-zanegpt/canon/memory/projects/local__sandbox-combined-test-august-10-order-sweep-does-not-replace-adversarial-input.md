# local/sandbox-combined-test-august-10-order-sweep-does-not-replace-adversarial-input — lessons

Project: local/sandbox-combined-test-august-10-order-sweep-does-not-replace-adversarial-input. Newest first.

---

## E1 — sandbox combined test august 10 order sweep does not replace adversarial input
- Date: 2026-08-29
- Project: local/sandbox-combined-test-august-10-order-sweep-does-not-replace-adversarial-input
- Tags: [testing][method][harness][algorithm]
- What: A deterministic sandbox (LCG-generated permutations, no library RNG, no wall-clock) benchmarking a dependency-aware scheduling heuristic against a naive baseline, scored two ways: august-10#E4's swept-many-decorrelated-orders aggregate over 200 permutations, and test#E8's deliberately baseline-adversarial single input.
- Why built: august-10#E4 prescribes sweeping several decorrelated orders and publishing their agreement, because one deterministic run of an order-dependent algorithm is one witness. test#E8 separately warns that a comparative benchmark gives a false tie unless the input is adversarial to the baseline. Both are about trusting a comparative result — this tests whether E4's sweep, being the more statistically rigorous-looking procedure, actually subsumes E8's adversarial construction or silently defeats it.
- Design: A 5-task set where one task has 4 dependents and the rest have none, so scheduling the high-leverage task early is the entire heuristic. The baseline runs tasks in arrival order; the heuristic sorts by dependent count. 200 LCG permutations supply the swept population; two hand-constructed orders supply the adversarial case (high-leverage task last) and the lucky case (high-leverage task already first).
- Got right: Constructing the heuristic to be order-insensitive by design meant the swept variation came purely from the baseline's exposure to input order, isolating exactly the effect test#E8 names rather than confounding it with heuristic instability.
- Where/why it failed: The 200-order sweep reports a mean advantage of 24.280 against the adversarial case's 60 — under half the true worst-case value — and 70 of 200 orders (35%) report an outright TIE, which is precisely the lucky-ordering false tie test#E8 describes. august-10#E4's own "publish only their agreement" criterion also fails here: agreement is False because a third of the population ties, so a sweep reported by agreement would decline to claim the heuristic wins at all, despite it never once losing (0 losses in 200).
- Fix: Report a sweep's DISTRIBUTION and its worst-case-for-baseline tail, not its mean or its unanimity — and keep test#E8's adversarial construction as a separate mandatory case, since a heuristic whose value is realized only on inputs the baseline handles worst is systematically understated by any aggregate computed over a population dominated by benign inputs.
- Why this fix: The two disciplines answer different questions that look similar. august-10#E4 asks "is this claim order-robust," and its aggregate is the right instrument for that. test#E8 asks "is this claim measurable at all," which requires deliberately selecting the regime where the difference exists. Averaging over a population where 35% of members are ties is a correct answer to E4's question and a misleading answer to E8's, so the more rigorous-looking procedure is the one that hides the effect.
- Rule of thumb: august-10#E4's multi-order sweep does not replace test#E8's baseline-adversarial input — sandbox-confirmed the sweep's mean advantage (24.280) is under half the adversarial case's (60) with 35% of orders tying outright, so report the distribution and the baseline-worst tail alongside a purpose-built adversarial case, never a mean or a unanimity check alone.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/sb9/s.py) and confirmed 200 decorrelated orders yield 130 wins / 70 ties / 0 losses, mean advantage 24.280, agreement False, against an adversarial-order advantage of 60 (baseline 80 vs heuristic 20) and a lucky-order advantage of 0. test#E8 and august-10#E4 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__test/E8, pappydapimp69__august-10/E4
- Link: session_014mRpopK9xnhvk35tT8ozkX

