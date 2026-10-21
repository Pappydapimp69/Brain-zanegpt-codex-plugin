"""Prediction (written before run): with cover tests built from frozenset.issuperset, ChainMap membership and an
OrderedDict-based first-cover (structurally unlike the dict/bitmask paths), at base 2207 the 2-lag period-average
shadow total for P=5..7 is flat exactly at every multiple of P up to 3P (N=P-1..3P+1), all three implementations agree
with each other, an 'any' cover rule gives different averages, and a base-0 control differs at N=P. Break case: the
any-rule and base-0 control. Same landing/shadow model as the family's other sandboxes. Stdlib, deterministic."""
from collections import ChainMap, OrderedDict
from fractions import Fraction as F

def lands(P, T, w, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

def count(P, T, N, impl):
    sh = 0
    for w in range(1, P):
        ev = {L: lands(P, T, w, L) for L in range(1, N + 1)}
        fs = {L: frozenset(ev[L]) for L in ev}
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                if impl == "issuperset":
                    covered = fs[a].issuperset(fs[b])
                elif impl == "chainmap":
                    cm = ChainMap({x: 1 for x in ev[a]})
                    covered = all(x in cm for x in ev[b])
                elif impl == "ordereddict":
                    od = OrderedDict((x, a) for x in ev[a])
                    new = [x for x in ev[b] if x not in od]
                    covered = not new
                else:  # any-for-all bug
                    covered = any(x in fs[a] for x in ev[b])
                cut = a if (covered and ev[a]) else (b if ev[b] else 0)
                last = b if ev[b] else (a if ev[a] else 0)
                sh += (last != cut)
    return sh

def avg(P, base, N, impl):
    return F(sum(count(P, base + r, N, impl) for r in range(P)), P)

ok = True; out = []
for P in (5, 6, 7):
    Ns = list(range(P - 1, 3 * P + 2))
    A = {impl: {N: avg(P, 2207, N, impl) for N in Ns} for impl in ("issuperset", "chainmap", "ordereddict")}
    agree = A["issuperset"] == A["chainmap"] == A["ordereddict"]
    flats = [N for N in Ns[1:] if A["issuperset"][N] == A["issuperset"][N - 1]]
    anyv = avg(P, 2207, P, "any"); ctrl = avg(P, 0, P, "issuperset")
    d = anyv != A["issuperset"][P]; c = ctrl != A["issuperset"][P]
    print(P, flats, agree, "any", anyv, "vs", A["issuperset"][P], "ctrl_differs", c, flush=True)
    ok = ok and agree and flats == [P, 2 * P, 3 * P] and d and c
    out.append(f"P{P} flats={flats} agree={agree} any={anyv} true={A['issuperset'][P]} ctrl_differs={c}")
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
