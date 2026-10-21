"""Train edge: age-cutoff-lossless-threshold-exceeds-period-p12 E1 (the lossless
cutoff is the largest lag with a valid press, never derived from the period) +
sandbox-mismatch-aliasing-quasiperiodic-fibonacci-lags E1 (mismatch is blind at
a quasi-periodic world's near-period lags: Fibonacci numbers on a Fibonacci word).
Composed question: on a world with NO period, (a) does the lossless cutoff still
equal the largest valid lag, and (b) does a mismatch-based staleness gate leak
mostly at Fibonacci lags - i.e. does 'derive it from the period' fail twice?
Own fixture, deterministic: Fibonacci word of length 2,000 (1 = role B
available); hint at t says B iff available; press lands at t + L. Lag sets
F {1, 2, 34} (Fibonacci), N {1, 2, 30} (non-Fibonacci), M {3, 55, 60}.
Mismatch rate at a lag = share of t where state(t) != state(t + L).
PREDICTION (written before running): smallest lossless cutoff = largest valid
lag in all three sets; mismatch rate at Fibonacci lags 34 and 55 is under 0.10
while at 30 and 60 it is over 0.30 - so a mismatch gate passes far more stale
presses at Fibonacci lags.
"""
import sys
print("python", sys.version.split()[0])
w = "1"; prev = "0"
while len(w) < 2200: w, prev = w + prev, w
S = [c == "1" for c in w[:2200]]
T = 2000
def mismatch(L): return sum(S[t] != S[t + L] for t in range(T)) / T
def lossless(lags):
    presses = [(L, S[t] and S[t + L]) for t in range(T) for L in lags]
    base = sum(ok for _, ok in presses)
    maxv = max(L for L, ok in presses if ok)
    cut = min(c for c in range(0, 100) if sum(ok for L, ok in presses if L <= c) == base)
    return maxv, cut
res = {nm: lossless(l) for nm, l in (("F", (1, 2, 34)), ("N", (1, 2, 30)), ("M", (3, 55, 60)))}
for nm, (mv, cu) in res.items(): print(f"set {nm}: largest valid lag {mv}, smallest lossless cutoff {cu}")
mm = {L: mismatch(L) for L in (13, 21, 30, 34, 40, 55, 60, 89)}
print("mismatch rate by lag:", {L: round(v, 3) for L, v in mm.items()})
c = [all(a == b for a, b in res.values()), mm[34] < 0.10 and mm[55] < 0.10, mm[30] > 0.30 and mm[60] > 0.30]
print("checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} {sum(c)}/3; lossless cutoff = largest valid lag {[(k, v[0], v[1]) for k, v in res.items()]}; mismatch at Fibonacci lags 34 {mm[34]:.3f}, 55 {mm[55]:.3f} vs 30 {mm[30]:.3f}, 60 {mm[60]:.3f}")
