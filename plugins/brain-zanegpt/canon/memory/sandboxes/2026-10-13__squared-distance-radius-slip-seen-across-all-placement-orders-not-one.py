"""Greedy point placement with per-point collision radii, over EVERY ordering (deterministic permutations, no RNG).
Predicates: correct = sqrt(d2) >= MIN + r_other ; slip = d2 >= MIN + r_other (squared distance vs linear threshold).
A placement is VALID when every placed pair satisfies the correct predicate. Compare orderings, not one order."""
from itertools import permutations
MIN = 2.0
pts = [(0.0, 0.5), (2.4, 1.5), (5.0, 0.5), (7.3, 1.0), (9.0, 0.5)]   # (x, radius), collinear
def d2(a, b): return (a[0] - b[0]) ** 2
def ok_correct(p, placed): return all(d2(p, q) ** 0.5 >= MIN + q[1] for q in placed)
def ok_slip(p, placed): return all(d2(p, q) >= MIN + q[1] for q in placed)
def place(order, ok):
    placed = []
    for p in order:
        if ok(p, placed): placed.append(p)
    return placed
def valid(placed): return all(d2(a, b) ** 0.5 >= MIN + b[1] or d2(a, b) ** 0.5 >= MIN + a[1] for i, a in enumerate(placed) for b in placed[:i])
def strict_valid(placed):   # correct predicate applied in placement order
    return all(ok_correct(p, placed[:i]) for i, p in enumerate(placed))
orders = list(permutations(pts))
stats = dict(correct_counts=set(), slip_counts=set(), slip_invalid=0, correct_invalid=0, slip_more=0, same=0)
cc, sc = [], []
for o in orders:
    a = place(o, ok_correct); b = place(o, ok_slip)
    cc.append(len(a)); sc.append(len(b))
    stats["correct_invalid"] += not strict_valid(a)
    stats["slip_invalid"] += not strict_valid(b)
    stats["slip_more"] += len(b) > len(a)
    stats["same"] += (a == b)
n = len(orders)
print(f"orders {n}: correct counts {sorted(set(cc))} (mean {sum(cc)/n:.2f}); slip counts {sorted(set(sc))} (mean {sum(sc)/n:.2f})")
print(f"slip places more than correct in {stats['slip_more']}/{n}; identical placement in {stats['same']}/{n}; slip layouts invalid {stats['slip_invalid']}/{n}; correct invalid {stats['correct_invalid']}/{n}")
first = orders[0]
print("single order (as listed):", len(place(first, ok_correct)), "correct vs", len(place(first, ok_slip)), "slip")
# BREAK: threshold scale where squared and linear agree (MIN=1): the slip should vanish
MIN = 1.0
bad = sum(strict_valid(place(o, ok_slip)) is False for o in orders)
print(f"BREAK MIN=1.0: slip invalid in {bad}/{n}")
ok = stats["slip_invalid"] > 0 and stats["correct_invalid"] == 0 and len(set(cc)) > 1
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" slip invalid {stats['slip_invalid']}/{n}, correct counts {sorted(set(cc))}, slip more in {stats['slip_more']}, MIN=1 invalid {bad}")
