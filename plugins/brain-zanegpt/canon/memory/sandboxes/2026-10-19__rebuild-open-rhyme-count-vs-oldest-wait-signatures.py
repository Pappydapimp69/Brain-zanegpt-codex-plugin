# Own fixture: restricted-growth strings = all set partitions of n lines (15 for n=4, 203 for n=6).
# Prediction (before run): ABAB and ABBA tie on mean open count (1.0), AABB 0.5; oldest wait
# ABBA 2 > ABAB 1 > AABB 0; >=30% of 4-line schemes share their open-count value (I expect ~80%);
# for 6 lines the triple signature (mean open, max wait, open at end) is shared by 60-85% of schemes.
from fractions import Fraction
def schemes(n):
    def rec(pre, mx):
        if len(pre) == n: yield tuple(pre); return
        for v in range(mx + 2): yield from rec(pre + [v], max(mx, v))
    yield from rec([0], 0)
def metrics(s):
    first = {}; answered = set(); counts = []; wait = 0
    for i, c in enumerate(s):
        if c not in first: first[c] = i
        elif c not in answered: answered.add(c)
        open_now = [k for k in first if k not in answered]
        counts.append(len(open_now))
        for k in open_now: wait = max(wait, i - first[k])
    return Fraction(sum(counts), len(s)), wait, counts[-1]
def name(s): return "".join("ABCDEFG"[x] for x in s)
m4 = {name(s): metrics(s) for s in schemes(4)}
for k in ("AABB", "ABAB", "ABBA"): print(k, float(m4[k][0]), m4[k][1])
def shared(vals):
    from collections import Counter
    c = Counter(vals); return sum(1 for v in vals if c[v] > 1) / len(vals)
s4 = shared([v[0] for v in m4.values()])
m6 = [metrics(s) for s in schemes(6)]
s6 = shared(m6); s6_wait_only = shared([v[1] for v in m6])
print("n4", len(m4), "n6", len(m6), "4-line share open-count", round(s4, 3), "6-line share triple", round(s6, 3))
ok = (m4["ABAB"][0] == m4["ABBA"][0] == 1 and m4["AABB"][0] == Fraction(1, 2)
      and m4["ABBA"][1] > m4["ABAB"][1] > m4["AABB"][1] and s4 >= 0.30 and 0.60 <= s6 <= 0.85 and len(m6) == 203)
print("RESULT:", "PASS" if ok else "FAIL", f"ties ok, wait order ok, 4-line share {s4:.0%}, 6-line triple share {s6:.0%} of {len(m6)}")
