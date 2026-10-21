# Prediction (before run): exhaustive enumeration over a restricted deck (ranks A-8, 32 cards,
# 201,376 five-card sets x 5 starter choices) keeps 19,25,26,27 impossible (superset rule) and
# also makes 28 and 29 impossible; max score <= 24, and 19 stays impossible.
# Assumption: removing cards can only remove reachable totals. Break case: the full-deck
# known gaps checked against a deck with ranks A-K but one suit only (flush-heavy) -> a total
# that was impossible in the full deck must not become possible.
from itertools import combinations
def val(r): return min(r, 10)
def score(hand, start, crib=False):
    cards = hand + [start]; pts = 0
    for n in range(2, 6):
        for c in combinations(cards, n):
            if sum(val(x[0]) for x in c) == 15: pts += 2
    for a, b in combinations(cards, 2):
        if a[0] == b[0]: pts += 2
    rs = sorted(x[0] for x in cards)
    best = 0
    for n in (5, 4, 3):
        runs = 0
        for c in combinations(cards, n):
            s = sorted(x[0] for x in c)
            if len(set(s)) == n and s[-1] - s[0] == n - 1: runs += 1
        if runs: best = n * runs; break
    pts += best
    if len({x[1] for x in hand}) == 1:
        pts += 4 + (1 if start[1] == hand[0][1] else 0)
    if any(x[0] == 11 and x[1] == start[1] for x in hand): pts += 1
    return pts
def space(ranks, suits):
    deck = [(r, s) for r in ranks for s in suits]
    seen = set()
    for five in combinations(deck, 5):
        for i in range(5):
            seen.add(score(list(five[:i] + five[i+1:]), five[i]))
    return seen
# cross-check scorer on known hands first
assert score([(5,0),(5,1),(5,2),(11,3)], (5,3)) == 29
assert score([(2,0),(4,1),(8,2),(12,3)], (13,0)) == 0
sub = space(range(1, 9), range(4))
one = space(range(1, 14), [0])
print('one-suit deck impossible', sorted(set(range(30)) - one))
full_gaps = {19, 25, 26, 27}
poss = set(range(30))
imp = sorted(poss - sub)
print("achievable max", max(sub), "impossible", imp)
ok = full_gaps <= set(imp) and {28, 29} <= set(imp) and full_gaps.isdisjoint(one)
print(f"RESULT: {'PASS' if ok else 'FAIL'} subdeck A-8 impossible={imp} max={max(sub)}")
