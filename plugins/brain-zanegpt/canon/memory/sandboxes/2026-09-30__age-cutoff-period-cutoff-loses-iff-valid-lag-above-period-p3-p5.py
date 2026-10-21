# Sandbox: age cutoff over validity. Claim: minimal lossless cutoff = max VALID lag; a cutoff equal to the period P
# is lossless iff no valid lag exceeds P (multiples of P always valid, so any lag 2P/3P in set breaks it).
# Oracle: stream of presses, one per (tick in 3 periods, lag in set); valid iff both ticks active. Count presses lost
# when an age gate (drop if lag > cutoff) sits on top of validity. Exhaustive windows at P3,P4,P5; lag sets:
# all subsets of {1..2P} of size<=3 (deterministic enumeration).
import itertools
def presses(P, win, lags):
    out = []
    for t in range(2 * P, 5 * P):            # steady-state ticks
        for L in lags:
            if (t % P) in win and ((t - L) % P) in win:
                out.append(L)
    return out
n = bad_min = bad_period = 0
for P in (3, 4, 5):
    for mask in range(1, 2 ** P):
        win = {i for i in range(P) if mask >> i & 1}
        for k in (1, 2, 3):
            for lags in itertools.combinations(range(1, 2 * P + 1), k):
                pr = presses(P, win, lags)
                if not pr: continue
                n += 1
                mx = max(pr)
                lost = lambda c: sum(1 for L in pr if L > c)
                bad_min += not (lost(mx) == 0 and lost(mx - 1) > 0)           # mx minimal lossless
                bad_period += (lost(P) == 0) != (mx <= P)                       # period cutoff lossless iff mx<=P
print(f"n={n} minimal_claim_violations={bad_min} period_claim_violations={bad_period}")
print(f"RESULT: {'PASS' if bad_min == 0 and bad_period == 0 else 'FAIL'} n={n} min_viol={bad_min} period_viol={bad_period}")
