"""Sandbox: hint-vs-press mismatch count over a sweep window, as a function of window phase.
Composes (a) age-cutoff 2-lag average flat at multiples of P (window = whole cycles) with
(b) the cycle-sweep hint-lag mismatch count. Deterministic, stdlib only."""
def role(t, P, K): return ((t % P) * K) // P
def mism(s, N, P, K, L):  # presses at ticks s..s+N-1; hint shows state at t-L
    return sum(1 for t in range(s, s + N) if role(t, P, K) != role(t - L, P, K))
def spread(N, P, K, L):
    c = [mism(s, N, P, K, L) for s in range(P)]
    return min(c), max(c)
rows, flat_ok, off_varies = [], True, False
CASES = [(7, 2), (11, 3), (13, 2)]; LAGS = (1, 2, 4)
for P, K in CASES:
    for L in LAGS:
        for N in (600, P * 85 if P == 7 else P * 54 if P == 11 else P * 46):
            lo, hi = spread(N, P, K, L)
            whole = N % P == 0
            rows.append((P, K, L, N, whole, lo, hi))
            if whole and lo != hi: flat_ok = False
            if not whole and lo != hi: off_varies = True
for r in rows[:6]: print("P=%d K=%d L=%d N=%d whole=%s min=%d max=%d" % r)
# 600 is NOT a multiple of 7, 11, 13: prior sweep counts (171/341/511) depend on start tick
lo, hi = spread(600, 7, 2, 1)
print("S-break: P7 K2 L1 N600 start-phase range", lo, hi)
# whole-cycle window equals N/P * per-cycle count (conservation by cycle)
per = mism(0, 7, 7, 2, 1); print("per-cycle P7 L1:", per, " 85 cycles:", mism(3, 595, 7, 2, 1))
# lag >= P aliasing: lag P gives zero mismatch (hint period-aliased)
alias = mism(0, 70, 7, 2, 7)
print("lag==P mismatches:", alias)
ok = flat_ok and off_varies and (lo != hi) and mism(3, 595, 7, 2, 1) == 85 * per and alias == 0
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" whole-cycle windows phase-flat in all {len(rows)//2} cases; N=600 non-multiple varies {lo}-{hi} with start; lag=P aliases to 0")
