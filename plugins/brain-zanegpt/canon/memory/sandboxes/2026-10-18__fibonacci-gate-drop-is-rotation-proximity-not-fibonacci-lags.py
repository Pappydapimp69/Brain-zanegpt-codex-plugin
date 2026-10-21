# Is the low gate-only invalid count at Fibonacci lags a property of the Fibonacci
# word (rotation proximity ||L*phi||) rather than of "Fibonacci lags" or of gates?
import random, math, statistics
N = 600
def fibword(n):
    s = "1"
    while len(s) < n:
        s = "".join("10" if c == "1" else "1" for c in s)
    return [int(c) for c in s[:n]]
def invalid(sig, L):  # legal now at t, illegal at t+L (one-sided stale press)
    return sum(1 for t in range(N) if sig[t] == 1 and sig[t + L] == 0)
M = N + 130
fw = fibword(M)
phi = (1 + 5 ** 0.5) / 2
def dist(L):
    x = (L * phi) % 1.0
    return min(x, 1 - x)
fib = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
lucas = [4, 7, 11, 18, 29, 47, 76, 123 - 0]
lucas = [l for l in lucas if l <= 120]
f = {L: invalid(fw, L) for L in range(1, 121)}
win = [f[L] for L in range(40, 71)]
med = statistics.median(win)
# 1) Fibonacci lags
fibs = [f[L] for L in fib]
# 2) Lucas lags (non-Fibonacci, small ||L phi||)
luc = {L: f[L] for L in lucas}
# 3) correlation of count with ||L phi||
xs = [dist(L) for L in range(1, 121)]; ys = [f[L] for L in range(1, 121)]
mx, my = statistics.mean(xs), statistics.mean(ys)
r = sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / math.sqrt(sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys))
# 4) BREAK: Bernoulli(0.618) signal with same density, lags 55 and 89 and window median
rng = random.Random(7)
meds = []; b55 = []; b89 = []
for seed in range(20):
    rng = random.Random(seed)
    bs = [1 if rng.random() < 0.618 else 0 for _ in range(M)]
    b55.append(invalid(bs, 55)); b89.append(invalid(bs, 89))
    meds.append(statistics.median(invalid(bs, L) for L in range(40, 71)))
# 5) periodic control P12 W5 (formula exact)
P, W = 12, 5
ps = [1 if t % P < W else 0 for t in range(M)]
ctrl_ok = all(invalid(ps, L) == (N // P) * min(L, W, P - L, P - W) for L in range(1, 12))
print("fib lags", fibs, "window median", med)
print("lucas lags", luc)
print("corr(count, ||L phi||) =", round(r, 3))
print("bernoulli lag55 mean", statistics.mean(b55), "lag89 mean", statistics.mean(b89), "window median mean", statistics.mean(meds))
print("periodic control exact", ctrl_ok)
ok = (f[55] <= 10 and f[89] <= 10
      and statistics.mean(luc[L] for L in (47, 76)) <= 0.25 * med
      and r > 0.8
      and statistics.mean(b55) >= 0.5 * statistics.mean(meds)
      and statistics.mean(b89) >= 0.5 * statistics.mean(meds)
      and ctrl_ok)
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
      f"fib55={f[55]} fib89={f[89]} lucas47={luc[47]} lucas76={luc[76]} median40-70={med} r={r:.2f} "
      f"bern55={statistics.mean(b55):.0f} bern89={statistics.mean(b89):.0f}")
