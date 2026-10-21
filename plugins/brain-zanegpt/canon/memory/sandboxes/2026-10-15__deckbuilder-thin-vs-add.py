# Deckbuilder: does removing a weak card beat adding a good one? Exact enumeration, no RNG.
# PREDICTION (before first run): from a 10-card starter (5 Strike=6, 4 Defend=5, 1 Bash=10),
# draw 5, play the best 3: removing a Defend gains more per turn than adding any card worth < ~7
# (the mean of PLAYED cards, not the deck mean 6.1); with hand >= deck size, thinning gains 0.
from itertools import combinations
from fractions import Fraction as F
KEY_AT = lambda deck: deck.index(10)   # the first 10 in the list is the Bash; added cards go after it
def turn(deck, hand=5, play=3):
    n = len(deck); h = min(hand, n); tot = F(0); k = 0; key = 0
    for c in combinations(range(n), h):
        vals = sorted((deck[i] for i in c), reverse=True); tot += sum(vals[:play]); k += 1
        key += any(i == KEY_AT(deck) for i in c)
    return tot / k, F(key, k)
START = [6]*5 + [5]*4 + [10]
base, bkey = turn(START)
cut_def, kd = turn(START[:5] + [5]*3 + [10])
cut_str, ks = turn([6]*4 + [5]*4 + [10])
print('S1 starter  per-turn %.3f  P(Bash in hand) %s' % (base, bkey))
print('   remove Defend %.3f (+%.3f) P(Bash) %s ; remove Strike %.3f (+%.3f)' % (cut_def, cut_def-base, kd, cut_str, cut_str-base))
thr = None
for v in range(5, 16):
    a, ka = turn(START + [v]); print('   add card v=%2d -> %.3f (%+.3f) P(Bash) %s' % (v, a, a-base, ka))
    if thr is None and a > cut_def: thr = v
print('S2 smallest added value that beats removing a Defend:', thr, '| deck mean %.2f' % (sum(START)/len(START)))
# S3 (built to BREAK the rule): tiny deck, hand covers the whole deck -> removal can only lose value
small = [6, 6, 5, 10, 5]; s_base, _ = turn(small); s_cut, _ = turn([6, 6, 10, 5])
print('S3 5-card deck: %.3f ; remove a Defend %.3f (gain %+.3f)' % (s_base, s_cut, s_cut - s_base))
# S4: energy 5 (play everything you draw). Predicted removal would LOSE here; first run showed it GAINS
# (+0.556): removing a below-mean card raises the mean of every draw. Kept as a refuted prediction.
e_base, _ = turn(START, play=5); e_cut, _ = turn(START[:5] + [5]*3 + [10], play=5)
print('S4 play all 5 drawn: %.3f ; remove Defend %.3f (%+.3f)' % (e_base, e_cut, e_cut - e_base))
ok = cut_def > base and thr is not None and thr > sum(START)/len(START) and s_cut <= s_base and e_cut > e_base
print('RESULT: %s remove-Defend +%.3f/turn; an added card must be worth >= %s (deck mean %.1f) to beat it; thinning gains nothing when hand covers deck (%+.2f) and still gains when you can play every card drawn (%+.3f)'
      % ('PASS' if ok else 'FAIL', cut_def-base, thr, sum(START)/len(START), s_cut-s_base, e_cut-e_base))
