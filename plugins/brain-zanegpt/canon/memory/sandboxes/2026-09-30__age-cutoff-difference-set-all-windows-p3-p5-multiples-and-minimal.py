# Sandbox: difference-set validity rule on ALL nonempty windows (subsets of ticks) at P3,P4,P5,P10 sampled.
# Oracle: press at lag L valid iff exists active tick t with t-L also active (brute force over 3 periods).
import itertools
def valid_bf(P, win, L):
    return any((t % P) in win and ((t - L) % P) in win for t in range(L, L + 3 * P))
def diffset(P, win):
    return {(a - b) % P for a in win for b in win}
def cutoff(valid, lags):
    v = [L for L in lags if valid(L)]
    return max(v) if v else 0
mis = 0; n = 0; fullP = 0; fullN = 0; dropP0 = 0; dropPN = 0; multi_raise = 0; multi_N = 0
for P in (3, 4, 5, 6):
    for mask in range(1, 2 ** P):
        win = {i for i in range(P) if mask >> i & 1}
        D = diffset(P, win)
        for lags in (list(range(1, P + 1)), [L for L in range(1, P + 1) if L != P], list(range(1, 3 * P + 1))):
            n += 1
            b = cutoff(lambda L: valid_bf(P, win, L), lags)
            c = cutoff(lambda L: (L % P) in D, lags)
            mis += b != c
        # minimal: lags 1..P -> P always (0 in difference set)
        fullN += 1; fullP += cutoff(lambda L: valid_bf(P, win, L), list(range(1, P + 1))) == P
        # drop P -> 0 iff window singleton
        dp = cutoff(lambda L: valid_bf(P, win, L), [L for L in range(1, P)])
        dropPN += 1; dropP0 += ((dp == 0) == (len(win) == 1 or D == {0}))
        # multiples: with lags up to 3P, cutoff is 3P (0 in D) -> always above P
        multi_N += 1; multi_raise += cutoff(lambda L: valid_bf(P, win, L), list(range(1, 3 * P + 1))) == 3 * P
ok = mis == 0 and fullP == fullN and dropP0 == dropPN and multi_raise == multi_N
print(f"n={n} mismatches={mis} full1..P->P {fullP}/{fullN} dropP->0 iff singleton {dropP0}/{dropPN} 3P-lags->3P {multi_raise}/{multi_N}")
print(f"RESULT: {'PASS' if ok else 'FAIL'} n={n} mismatches={mis} full={fullP}/{fullN} dropP={dropP0}/{dropPN} mult={multi_raise}/{multi_N}")
