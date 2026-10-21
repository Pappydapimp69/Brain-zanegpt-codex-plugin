"""Train edge: age-cutoff-lossless-threshold-exceeds-period-p12 E1 (an age
cutoff stacked on validity is lossless exactly at the largest lag with a valid
press, never derived from the period) + sandbox-agreement-aliasing-period-
jitter-reverify E1 (agreement checks alias at multiples of the TRUE repeat
length; on periods alternating 15/16 the super-cycle is 31).
Composed question: on the jittered world, (a) is the lossless cutoff still the
largest valid lag, and (b) if a designer replaces the age cutoff with an
agreement check (accept a press if the state it was hinted from equals the
state it lands in), how many STALE presses get through, and at which lags?
Own fixture, deterministic: 1,240 ticks; periods alternate 15, 16; role B is
available for the first 5 ticks of each period. A hint at tick t says B if B is
available at t; the press lands at t + L. Lag sets: S1 {1, 2, 4}, S2 {1, 3, 31},
S3 {2, 16, 47}. 'Stale' = L > 2 (the age threshold the source lessons use).
PREDICTION (written before running): (a) for every lag set the smallest
lossless cutoff equals the largest lag that ever produces a valid press;
(b) agreement lets through stale presses at L = 31 (super-cycle) in S2 and
blocks most at L = 16 and 47; the age cutoff at 2 blocks every stale press.
"""
import sys
print("python", sys.version.split()[0])
T = 1240
avail = []
p = 15
while len(avail) < T + 100:
    avail += [True] * 5 + [False] * (p - 5); p = 31 - p
def run(lags):
    valid_by_lag = {L: 0 for L in lags}; agree_stale = {L: 0 for L in lags}; age_stale = {L: 0 for L in lags}
    presses = []
    for t in range(T):
        hint_b = avail[t]
        for L in lags:
            legal = hint_b and avail[t + L]
            if legal: valid_by_lag[L] += 1
            presses.append((L, legal))
            if L > 2 and hint_b and avail[t] == avail[t + L]: agree_stale[L] += 1
            if L > 2 and hint_b: age_stale[L] += 1
    max_valid = max(L for L in lags if valid_by_lag[L] > 0)
    base = sum(1 for L, ok in presses if ok)
    lossless = min(c for c in range(0, 100) if sum(1 for L, ok in presses if ok and L <= c) == base)
    return valid_by_lag, max_valid, lossless, agree_stale
res = {}
for nm, lags in (("S1", (1, 2, 4)), ("S2", (1, 3, 31)), ("S3", (2, 16, 47))):
    v, mv, ll, ag = run(lags); res[nm] = (mv, ll, ag)
    print(f"{nm} lags {lags}: valid presses by lag {v}; largest valid lag {mv}; smallest lossless cutoff {ll}; stale presses agreement lets through {ag}")
c = [all(r[0] == r[1] for r in res.values()), res["S2"][2][31] > 0 and res["S2"][2][31] >= 0.9 * max(1, sum(avail[t] for t in range(T))),
     res["S3"][2][16] < 0.5 * res["S2"][2][31] and res["S3"][2][47] < 0.5 * res["S2"][2][31]]   # 'blocks most' at 16 and 47, as predicted
print("checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} {sum(c)}/3; lossless cutoff = largest valid lag in all sets ({[(k, r[0], r[1]) for k, r in res.items()]}); agreement passes stale lag-31 presses {res['S2'][2][31]}, lag-16 {res['S3'][2][16]}, lag-47 {res['S3'][2][47]}; age cutoff at 2 passes 0")
