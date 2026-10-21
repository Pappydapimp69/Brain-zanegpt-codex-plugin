"""Prediction (before run): on period-12 width-5 legality every lag that is a multiple of 12
(12,24,36,48) gives exactly 0 gate-only invalid presses. On the Fibonacci-word signal there is
no period, so for the lags 13,21,34,55,89 (near-integer multiples of phi) the count dips well
below the window median but is NOT zero (>=3 each), and the mod-P reduction with a nominal
P=13 predicts the wrong count for at least 80 of lags 1..120. The lag 89 count (3) is
below lag 13 (a Fibonacci-lag dip) so the dip, not lag mod P, sets the ordering."""
N = 600
def fibword(n):
    a, b = "1", "10"
    while len(b) < n: a, b = b, b + a
    return [int(c) for c in b[:n]]
fw = fibword(N + 130)
per = [1 if (t % 12) < 5 else 0 for t in range(N + 130)]
def inv(sig, L): return sum(1 for t in range(N) if sig[t] and not sig[t + L])
zero_per = {L: inv(per, L) for L in (12, 24, 36, 48, 60, 120)}
fib = {L: inv(fw, L) for L in (8, 13, 21, 34, 55, 89)}
import statistics
med = statistics.median(inv(fw, L) for L in range(40, 71))
# nominal-period formula on the aperiodic word, W = count of ones in first 13 symbols
P = 13; W = sum(fw[:P])
formula = lambda L: (N // P) * min(L % P, W, P - L % P, P - W)
wrong = sum(1 for L in range(1, 121) if abs(formula(L) - inv(fw, L)) > 0.1 * max(1, inv(fw, L)))
print(zero_per, fib, med, wrong, W)
ok = (all(v == 0 for v in zero_per.values())
      and all(fib[L] >= 3 for L in fib) and fib[89] < fib[13] and fib[55] < med / 5 and wrong >= 80)
print(("RESULT: PASS " if ok else "RESULT: FAIL ") +
      f"periodic multiples of 12 invalid {list(zero_per.values())}; Fibonacci-word fib lags {fib} (never 0), window median {med}; nominal-P13 formula wrong on {wrong}/120 lags")
