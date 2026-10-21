"""Sandbox: enumerate every cribbage hand (4 cards) with every starter card (all 2,598,960 five-card sets x 5
choices of which card is the starter) and score it by the standard rules: fifteens (any subset summing to 15,
face cards 10, ace 1), pairs (2/6/12 for two/three/four of a kind), runs (3+ consecutive ranks, multiplied
by duplicates), flush (4 in hand same suit = 4, +1 if starter matches; the crib rule is not used), and
nobs (jack in hand matching the starter's suit = 1).
Prediction (written before first run): the scores that cannot occur are exactly {19, 25, 26, 27}; the maximum
is 29 and it occurs for exactly 4 (hand, starter) combinations (5-5-5-J in hand with the 5 of the jack's suit
as starter, one per suit); the modal score is 4. Assumption: the scoring
function is right; BREAK: cross-check the engine on known hands (29, 28, 24 for 7-7-8-8-9, 0 for a no-score hand)."""
from itertools import combinations
from collections import Counter
RANKS = range(1, 14)
VAL = {r: min(r, 10) for r in RANKS}
cache = {}
def base(hand_ranks, start):
    key = (hand_ranks, start)
    if key in cache: return cache[key]
    cards = list(hand_ranks) + [start]
    pts = 0
    vals = [VAL[r] for r in cards]
    for n in range(2, 6):
        for sub in combinations(vals, n):
            if sum(sub) == 15: pts += 2
    c = Counter(cards)
    for r, k in c.items():
        pts += {2: 2, 3: 6, 4: 12}.get(k, 0)
    present = sorted(c)
    best = 0
    # runs: longest consecutive stretch of distinct ranks, length>=3, times product of multiplicities
    i = 0
    while i < len(present):
        j = i
        while j + 1 < len(present) and present[j + 1] == present[j] + 1: j += 1
        L = j - i + 1
        if L >= 3:
            m = 1
            for r in present[i:j + 1]: m *= c[r]
            pts += L * m
        i = j + 1
    cache[key] = pts
    return pts
def score(hand, start):                # hand: 4 (rank, suit); start: (rank, suit)
    hr = tuple(sorted(r for r, _ in hand))
    p = base(hr, start[0])
    suits = {s for _, s in hand}
    if len(suits) == 1: p += 4 + (1 if start[1] in suits else 0)
    if any(r == 11 and s == start[1] for r, s in hand): p += 1
    return p
DECK = [(r, s) for r in RANKS for s in range(4)]
hist = Counter(); top = []
for five in combinations(DECK, 5):
    for k in range(5):
        start = five[k]; hand = five[:k] + five[k + 1:]
        sc = score(hand, start)
        hist[sc] += 1
        if sc >= 29: top.append((hand, start))
impossible = sorted(set(range(0, 30)) - set(hist))
print("total hand-starter combinations:", sum(hist.values()))
print("impossible scores 0..29:", impossible, "; max:", max(hist), "occurs", hist[max(hist)], "times")
print("modal score:", hist.most_common(1)[0], "; score 0 count:", hist[0])
chk = {
 "29 hand": score(((5, 0), (5, 1), (5, 2), (11, 3)), (5, 3)),
 "7-7-8-8-9 with 8 in hand": score(((7, 0), (7, 1), (8, 2), (8, 3)), (9, 0)),
 "no-score hand": score(((2, 0), (4, 1), (6, 2), (8, 3)), (13, 0)),
}
print("engine cross-checks (known: 29, 24, 0):", chk)
ok = (impossible == [19, 25, 26, 27] and max(hist) == 29 and hist[29] == 4 and chk["29 hand"] == 29
      and chk["7-7-8-8-9 with 8 in hand"] == 24 and chk["no-score hand"] == 0)
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" impossible scores {impossible}; 29 occurs {hist[29]} times; modal score {hist.most_common(1)[0][0]} ({hist.most_common(1)[0][1]}x) over {sum(hist.values())} combinations")
