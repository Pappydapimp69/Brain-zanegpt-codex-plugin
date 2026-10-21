"""Prediction (before run): facts L0 (3, context), L1 (6, containers), L2 (20, code). Novice needs all 3 L0 facts, expert
needs 4 specific L2 facts (plus L0). Reader has effort budget B; reading a fact costs 1, opening an expander costs C.
(a) novice, B=10: flat-code-first fails, flat-context-first and layered succeed; (b) expert, B=12: flat-context-first fails
(L2 facts sit at positions 10-29), layered succeeds with reachable expanders at C=2; (c) BREAK: layered with depth omitted
entirely ('defer') makes the expert fail at any B; (d) BREAK: raising click cost C makes layered lose for the expert at a
threshold I will report (predicted between C=3 and C=6). Assumed constants; modeled, not people. Stdlib, deterministic."""
L0 = [f"c{i}" for i in range(3)]; L1 = [f"k{i}" for i in range(6)]; L2 = [f"x{i}" for i in range(20)]
EXPERT_NEEDS = {"x3", "x7", "x12", "x18"}
def flat(order, B, needs):
    got = set()
    for i, f in enumerate(order):
        if i >= B: break
        got.add(f)
    return needs <= got
def layered(B, needs, C, reachable=True):
    # sees L0 (3 facts) free of clicks, then may open L1 (cost C) and L2 (cost C), reading only the needed facts via an index
    spent = 0; got = set()
    for f in L0:
        spent += 1; got.add(f)
    if spent > B: return False
    want_deep = needs & set(L2)
    if want_deep:
        if not reachable: return needs <= got
        spent += C                      # open L2 expander (index lets the reader read just what they need)
        for f in sorted(want_deep):
            spent += 1
            if spent <= B: got.add(f)
    return needs <= got
novice = set(L0); expert = set(L0) | EXPERT_NEEDS
code_first = L2 + L1 + L0; ctx_first = L0 + L1 + L2
a = (flat(code_first, 10, novice), flat(ctx_first, 10, novice), layered(10, novice, 2))
b = (flat(ctx_first, 12, expert), layered(12, expert, 2))
c = [layered(B, expert, 2, reachable=False) for B in (12, 30, 60)]
thr = [C for C in range(0, 12) if not layered(12, expert, C)]
print("novice B=10 (flat code-first, flat ctx-first, layered):", a)
print("expert B=12 (flat ctx-first, layered C=2):", b)
print("expert, depth omitted, B=12/30/60:", c)
print("click costs C at which layered fails the expert (B=12):", thr)
ok = a == (False, True, True) and b == (False, True) and not any(c) and thr and 3 <= min(thr) <= 6
print("RESULT: %s novice=%s expert=%s depth_omitted_expert=%s layered_fails_expert_from_C=%s"
      % ("PASS" if ok else "FAIL", a, b, c, min(thr) if thr else None))
