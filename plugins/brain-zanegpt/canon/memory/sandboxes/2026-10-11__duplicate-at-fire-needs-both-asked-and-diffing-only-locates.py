"""Sandbox (composed): seven E24 (rescued member returns as a same-name
duplicate; player picks 1-of-2, assumed accuracy 0.80) meets the deduction
kernels question-budget (budget < cast, or diffing replaces memory) and
derived-vs-authored-tells (the fake's account = real log with ONE fact bent).

Exact model, no RNG. A day has F facts; the fake bends one uniformly. One
question covers K facts. The player's memory recalls a given fact with M
(otherwise unsure, never wrongly sure).
- Budget 1 (ask one of the two): P(correct pick).
- Budget 2 (ask both the same question): diffing LOCATES the bent fact when
  covered, memory must still say WHICH version is true.
- Break case: cast 3 with one fake and full budget: majority vote identifies
  the fake with no memory at all whenever the question covers the bent fact.
Then recompute E24 rule C pylon spend with the derived accuracy.
"""
from fractions import Fraction as Fr

F, K, M = 6, 2, Fr(8, 10)
HIT = Fr(K, F)


def acc_budget1():
    # ask a random one of the two; if it is the fake, the question hits and
    # memory recalls: caught; otherwise nothing learned -> coin
    caught = Fr(1, 2) * HIT * M
    return caught + (1 - caught) * Fr(1, 2)


def acc_budget2():
    # both asked: differ iff hit; then memory decides, else coin
    return HIT * (M + (1 - M) * Fr(1, 2)) + (1 - HIT) * Fr(1, 2)


def acc_cast3_no_memory():
    # odd one out by majority whenever covered; else 1-of-3 guess
    return HIT * 1 + (1 - HIT) * Fr(1, 3)


def rule_c_pylons(q, pylons=2):
    # first pylon on the doubted one: right with q; else second (certain)
    return q * 1 + (1 - q) * 2


def main():
    a1, a2, a3 = acc_budget1(), acc_budget2(), acc_cast3_no_memory()
    print(f"cover per question {float(HIT):.3f}, memory {float(M):.2f}")
    print(f"duplicate, budget 1: {float(a1):.3f}; budget 2: {float(a2):.3f}")
    print(f"cast 3, full budget, NO memory: {float(a3):.3f}")
    p_assumed, p_derived = rule_c_pylons(Fr(8, 10)), rule_c_pylons(a2)
    print(f"E24 rule C pylons per rescue: assumed q=0.80 -> {float(p_assumed):.3f}; derived -> {float(p_derived):.3f}")
    edge1, edge2 = a1 - Fr(1, 2), a2 - Fr(1, 2)
    checks = [
        ("budget 2 edge over a coin is exactly 2x budget 1", edge2 == 2 * edge1),
        (f"derived 1-of-2 accuracy falls short of E24's assumed 0.80 (got {float(a2):.3f})", a2 < Fr(8, 10)),
        ("duplicate with budget 2 is NOT solvable without memory (M=0 gives 0.5)",
         HIT * (0 + 1 * Fr(1, 2)) + (1 - HIT) * Fr(1, 2) == Fr(1, 2)),
        (f"break case: cast 3 is solved by diffing alone above 0.5 (got {float(a3):.3f})", a3 > Fr(1, 2)),
        (f"derived accuracy raises rule C pylon spend above 1.5 (got {float(p_derived):.3f})", p_derived > Fr(3, 2)),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)} predictions held; "
          f"budget1 {float(a1):.3f} budget2 {float(a2):.3f} cast3-no-memory {float(a3):.3f}; "
          f"rule C pylons {float(p_derived):.3f}")


if __name__ == "__main__":
    main()
