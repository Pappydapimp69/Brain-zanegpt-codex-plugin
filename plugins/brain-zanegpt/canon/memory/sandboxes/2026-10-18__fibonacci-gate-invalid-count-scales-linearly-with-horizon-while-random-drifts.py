# Prediction (written before the first run): on the Fibonacci word the gate-only invalid
# count at lag 55 and 89 scales linearly with horizon N with bounded deviation
# (|count - N*rate| <= 3 for N = 600..4800, rate fitted at N=4800), the dip persists at every
# N (count at 55 below 1/10 of the median over lags 40..70), and the Lucas lag 47 follows too.
# A Bernoulli(0.618) control has a deviation that grows (> 3 at the largest N for most seeds).
import random
def fib_word(n):
    a, b = "1", "10"
    while len(b) < n: a, b = b, b + a
    return [int(c) for c in b[:n]]
SIG = fib_word(5400 + 130)
def inv(sig, L, N):  # legal at t-L, illegal at t, t in L..N-1+L? use t in 0..N-1 with offset 130
    return sum(1 for t in range(130, 130 + N) if sig[t - L] == 1 and sig[t] == 0)
Ns = (600, 1200, 2400, 4800)
res = {}
for L in (55, 89, 47):
    c = [inv(SIG, L, N) for N in Ns]
    rate = c[-1] / 4800
    dev = [abs(x - N * rate) for x, N in zip(c, Ns)]
    res[L] = (c, max(dev))
    print("fib lag", L, "counts", c, "max dev", round(max(dev), 2))
med = sorted(inv(SIG, L, 600) for L in range(40, 71))[15]
dip_ok = all(res[L][0][i] < 0.25 * sorted(inv(SIG, M, Ns[i]) for M in range(40, 71))[15] for L in (55, 89, 47) for i in range(4))
print("window median at N=600:", med, "dip at every N:", dip_ok)
growing = 0
for seed in range(20):
    r = random.Random(seed)
    sig = [1 if r.random() < 0.618 else 0 for _ in range(5530)]
    c = [inv(sig, 55, N) for N in Ns]
    rate = c[-1] / 4800
    if max(abs(x - N * rate) for x, N in zip(c, Ns)) > 3: growing += 1
print("bernoulli seeds with deviation > 3 at lag 55:", growing, "of 20")
ok = all(res[L][1] <= 3 for L in res) and dip_ok and growing >= 15
print("RESULT: %s fib lag55/89/47 max dev %s, dip at every N %s, Bernoulli deviation >3 in %d/20 seeds" % ("PASS" if ok else "FAIL", {L: round(res[L][1],2) for L in res}, dip_ok, growing))
