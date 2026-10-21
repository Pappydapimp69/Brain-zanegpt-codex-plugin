"""Sandbox L5: which listener metric captures 'AABB stops often, ABBA stays open'?

Kernel ideas:SONGWRITING/rhyme/rhyme-scheme-shape-sets-a-songs-emotional-motion (quoted, never
declared, by sandbox-lyrical-composition E8, which measured closure distance). Listener model: a rhyme
letter is PENDING while it has appeared exactly once. Per scheme:
  L = mean pending count per line   (how much is open)
  A = max age of a pending letter   (how long the oldest open rhyme waits)
  E = pending count after the last line (open at the end)
All schemes of 4 and 6 lines are enumerated as restricted growth strings (15 and 203 schemes).
Deterministic, stdlib only.

PREDICTION (AABB/ABAB/ABBA values hand-worked first; the enumeration results were not):
  P1 L ties ABAB with ABBA (1.0 each) while AABB is 0.5, so pending count alone cannot separate
     ABBA's wistfulness from ABAB
  P2 A separates them: ABBA 2 > ABAB 1 > AABB 0
  P3 across all 4-line schemes, >= 30% share their L value with some other scheme
  P4 break: across 6-line schemes, the triple (L, A, E) still leaves >= 20% of schemes sharing a
     signature, so even three metrics under-describe scheme shape at 6 lines
"""


def rgs(n):
    out = []

    def go(prefix, mx):
        if len(prefix) == n:
            out.append(prefix)
            return
        for c in range(mx + 2):
            go(prefix + [c], max(mx, c))

    go([0], 0)
    return ["".join(chr(65 + c) for c in s) for s in out]


def metrics(s):
    count, first = {}, {}
    loads, ages = [], []
    for i, ch in enumerate(s):
        count[ch] = count.get(ch, 0) + 1
        first.setdefault(ch, i)
        pending = [c for c in count if count[c] == 1]
        loads.append(len(pending))
        ages.append(max((i - first[c] for c in pending), default=0))
    return sum(loads) / len(s), max(ages), loads[-1]


def share(schemes, key):
    sig = {}
    for s in schemes:
        sig.setdefault(key(s), []).append(s)
    shared = sum(len(v) for v in sig.values() if len(v) > 1)
    return shared / len(schemes)


four, six = rgs(4), rgs(6)
L = {s: metrics(s)[0] for s in ["AABB", "ABAB", "ABBA"]}
A = {s: metrics(s)[1] for s in ["AABB", "ABAB", "ABBA"]}
s4_L = share(four, lambda s: round(metrics(s)[0], 4))
s4_all = share(four, lambda s: tuple(round(x, 4) for x in metrics(s)))
s6_all = share(six, lambda s: tuple(round(x, 4) for x in metrics(s)))
res = [("P1 L ties ABAB/ABBA, AABB lower", L["ABAB"] == L["ABBA"] and L["AABB"] < L["ABAB"],
        f"AABB {L['AABB']:.2f} ABAB {L['ABAB']:.2f} ABBA {L['ABBA']:.2f}"),
       ("P2 A orders ABBA > ABAB > AABB", A["ABBA"] > A["ABAB"] > A["AABB"], f"{A['ABBA']} > {A['ABAB']} > {A['AABB']}"),
       ("P3 4-line L shared >= 30%", s4_L >= 0.30, f"{s4_L:.0%} of {len(four)}"),
       ("P4 break: 6-line (L,A,E) shared >= 20%", s6_all >= 0.20, f"{s6_all:.0%} of {len(six)} (4-line triple {s4_all:.0%})")]
for name, ok, d in res:
    print(f"{name}: {'PASS' if ok else 'FAIL'}  {d}")
k = sum(ok for _, ok, _ in res)
print(("RESULT: PASS " if k == 4 else "RESULT: FAIL ") +
      f"{k}/4; L AABB/ABAB/ABBA {L['AABB']:.2f}/{L['ABAB']:.2f}/{L['ABBA']:.2f}, A {A['AABB']}/{A['ABAB']}/{A['ABBA']}; "
      f"4-line L-shared {s4_L:.0%}, triple-shared {s4_all:.0%}; 6-line triple-shared {s6_all:.0%}")
