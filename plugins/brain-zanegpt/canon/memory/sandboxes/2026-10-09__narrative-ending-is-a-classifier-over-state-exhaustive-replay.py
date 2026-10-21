"""Prediction (before run): 6 choice points x 3 options = 729 paths. (1) a classifier over the final state vector (water, trust, hope; each clamped 0..10)
yields exactly one ending for all 729 replays, with all 3 endings reachable, so authored content is 3 endings not 729 branches; (2) a handler-flag variant
(ending set by the last choice handler) is NOT a function of state: at least one pair of paths with identical final state gets different endings, while the
classifier has 0 such pairs; (3) BREAK (same six deltas applied in every order; first iteration wrongly permuted option indices across points): clamping makes state order-dependent, so at least one reordering of the same choice multiset lands in a different
ending (the readout is a function of state, not of the choice set); (4) with an overlapping specific ending (dead = water 0 and hope 0) the staged rule
most-specific-first then fixed order never returns two endings and 'dead' is reachable. Deterministic, stdlib only."""
from itertools import product, permutations
from collections import defaultdict

CHOICES = [  # per choice point: 3 options, each a (water, trust, hope) delta
    [(-3, 2, 1), (2, -1, 0), (0, 0, -2)], [(-2, 3, 0), (3, -2, 1), (-1, 0, -3)], [(1, 1, -1), (-4, 1, 2), (2, -3, 0)],
    [(-2, -1, 3), (0, 2, -1), (3, 0, -2)], [(-3, 0, 2), (1, 3, -3), (2, -2, 1)], [(0, 1, 1), (-4, 2, 0), (2, 0, -4)]]
START = (6, 5, 5)
def clamp(v): return max(0, min(10, v))
def run(path):
    s = START
    for pt, opt in enumerate(path):
        d = CHOICES[pt][opt]; s = tuple(clamp(a + b) for a, b in zip(s, d))
    return s
def classify(s):  # staged: most specific predicate first, then fixed order
    w, t, h = s
    if w == 0 and h == 0: return "lost"           # specific, overlaps dead
    if w == 0 or h == 0: return "dead"
    if t >= 6 and h >= 5: return "holding"
    return "drifting"
ALL = list(product(range(3), repeat=6))
ends = {p: classify(run(p)) for p in ALL}
cnt = defaultdict(int)
for e in ends.values(): cnt[e] += 1
print("endings", dict(cnt), "paths", len(ALL))
ok1 = len(ALL) == 729 and len(cnt) >= 3 and "lost" in cnt and sum(cnt.values()) == 729
# (2) handler-flag variant: ending set by the last handler (flag from last option index), ignoring state
flag = {p: ("holding", "drifting", "dead")[p[-1]] for p in ALL}
def same_state_conflicts(endmap):
    by = defaultdict(set)
    for p in ALL: by[run(p)].add(endmap[p])
    return sum(len(v) > 1 for v in by.values())
c_flag, c_cls = same_state_conflicts(flag), same_state_conflicts(ends)
print("same-state conflicts: handler-flag", c_flag, "classifier", c_cls)
ok2 = c_flag > 0 and c_cls == 0
# (3) order dependence via clamping: same multiset of options (one per point can't be permuted across points, so permute which point each option lands on)
reorder = 0; checked = 0
for p in ALL[:81]:
    seen = set()
    for q in set(permutations([CHOICES[i][o] for i, o in enumerate(p)])):
        st = START
        for d in q: st = tuple(clamp(a + b) for a, b in zip(st, d))
        seen.add(classify(st)); checked += 1
    reorder += len(seen) > 1
print("choice multisets (first 81 paths) whose reordering changes the ending:", reorder, "of 81; permutations run", checked)
ok3 = reorder > 0
# (4) overlap staged rule: every state maps to exactly one ending, deterministic
states = list(product(range(11), repeat=3)); out = {s: classify(s) for s in states}
ok4 = len(out) == 1331 and all(out[s] == classify(s) for s in states) and out[(0, 5, 0)] == "lost" and out[(0, 5, 5)] == "dead"
ok = ok1 and ok2 and ok3 and ok4
print("RESULT: %s 729 paths -> %d endings %s; handler-flag same-state conflicts %d vs classifier %d; reorder changes ending for %d/81 multisets; staged overlap rule exact over 1331 states"
      % ("PASS" if ok else "FAIL", len(cnt), dict(cnt), c_flag, c_cls, reorder))
