from itertools import product
from collections import defaultdict
def rod(h, e):
    """h heavenly beads worth 5, e earthly beads worth 1; a state is (heavenly down, earthly up)."""
    by = defaultdict(list)
    for a, b in product(range(h + 1), range(e + 1)):
        by[5 * a + b].append((a, b))
    return by
def report(h, e):
    by = rod(h, e)
    states = sum(len(v) for v in by.values())
    red = sorted(v for v, s in by.items() if len(s) > 1)
    return states, len(by), red
res = {(h, e): report(h, e) for h in range(0, 4) for e in range(0, 7)}
sor, sua = res[(1, 4)], res[(2, 5)]
print("soroban 1+4", sor, "suanpan 2+5", sua)
# state equality vs value equality on every pair of suanpan states
by = rod(2, 5)
allst = [s for v in by.values() for s in v]
wrong = sum(1 for x in allst for y in allst if (x == y) != (5*x[0]+x[1] == 5*y[0]+y[1]))
print("suanpan ordered pairs where state-equality disagrees with value-equality:", wrong)
# redundancy iff earthly beads >= 5 (a second heavenly worth) and heavenly >= 1... check every layout
pred_ok = all((bool(r[2])) == (h >= 1 and e >= 5) for (h, e), r in res.items() if h or e)
print("redundant layouts match (h>=1 and e>=5):", pred_ok)
ok = sor == (10, 10, []) and sua == (18, 16, [5, 10]) and wrong == 4 and pred_ok
print("RESULT: %s soroban %s suanpan %s state/value disagreements %d" % ("PASS" if ok else "FAIL", sor, sua, wrong))
