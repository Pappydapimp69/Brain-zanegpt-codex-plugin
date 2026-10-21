"""Compose brainwork/E40 (ending is a classifier over live state; replay exhaustively) with
smallmouth/E2 (a mechanic whose threshold the system's own dynamics cannot reach, though
unit tests with hand-built inputs pass).
Model: state (water, trust, hope) clamped 0..10, start (6,6,6); K choice points each with 3
options (deterministic delta table below); classifier endings by predicate on final state.
Prediction (before the first run): hand-built-state tests reach all 4 endings (4/4 pass) while
exhaustive replay of the real choice paths reaches fewer than 4 at K=3 and all 4 at K=6;
the rare ending ('lost') gets under 1 percent of paths at K=6; flipping the start to (3,3,3)
lifts its share; and raising a single predicate threshold by one makes an ending unreachable
even at K=6."""
from itertools import product
DELTAS = [  # per choice point: three options of (water, trust, hope)
    [(-2, 1, 0), (1, -1, 1), (0, 2, -1)],
    [(-1, -1, 2), (2, 0, -1), (-2, 1, 1)],
    [(-3, 0, 0), (0, 2, 1), (1, -2, -1)],
    [(-1, 2, -2), (-2, -2, 1), (2, 1, 0)],
    [(0, -3, 1), (1, 1, 1), (-2, 0, -2)],
    [(-2, -1, -1), (2, 2, -1), (-1, 0, 2)],
]
def clamp(v): return max(0, min(10, v))
def classify(s, lost_t=2, dead_t=3):
    w, t, h = s
    if w <= lost_t and t <= lost_t and h <= lost_t: return "lost"
    if w <= dead_t: return "dead"
    if t >= 7 and h >= 7: return "holding"
    return "drifting"
def replay(K, start, **kw):
    counts = {}
    for path in product(range(3), repeat=K):
        s = start
        for k, o in enumerate(path):
            d = DELTAS[k][o]
            s = tuple(clamp(a + b) for a, b in zip(s, d))
        e = classify(s, **kw)
        counts[e] = counts.get(e, 0) + 1
    return counts, 3 ** K
# 1) hand-built-state unit test: assign a state directly per ending, assert classifier
hand = {"lost": (1, 1, 1), "dead": (2, 5, 5), "holding": (8, 8, 8), "drifting": (6, 5, 5)}
hand_pass = sum(classify(s) == e for e, s in hand.items())
print(f"1) hand-built states reach {hand_pass}/4 endings")
res = {}
for K in (3, 6):
    c, n = replay(K, (6, 6, 6)); res[K] = (c, n)
    print(f"2) K={K} start (6,6,6): {len(c)}/4 endings; shares", {e: round(v / n, 4) for e, v in sorted(c.items())})
c3, n3 = replay(6, (3, 3, 3))
print("3) K=6 start (3,3,3): shares", {e: round(v / n3, 4) for e, v in sorted(c3.items())})
c4, n4 = replay(6, (6, 6, 6), lost_t=1)
print("4) lost threshold 2 -> 1 at K=6: endings", sorted(c4), "lost", c4.get("lost", 0))
share_lost6 = res[6][0].get("lost", 0) / res[6][1]
ok = (hand_pass == 4 and len(res[3][0]) < 4 and len(res[6][0]) == 4 and share_lost6 < 0.01
      and c3.get("lost", 0) / n3 > share_lost6 and c4.get("lost", 0) == 0)
print(f"RESULT: {'PASS' if ok else 'FAIL'} hand-built {hand_pass}/4; K3 {len(res[3][0])}/4, K6 {len(res[6][0])}/4; lost share K6 {share_lost6:.4f}, start(3,3,3) {c3.get('lost',0)/n3:.4f}; lost at threshold 1: {c4.get('lost',0)}")
