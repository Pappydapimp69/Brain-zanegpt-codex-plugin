# Prediction (written before first run): for ANY 0/1 legality signal, over t in 0..N-1,
# sym(L) - 2*one(L) is bounded by |sum legal(t-L over window) - sum legal(t over window)| <= L, so
# (a) |sym-2*one| <= L at every lag 1..120 on Fibonacci word, 20 Bernoulli(0.618) seeds, and P12W5;
# (b) on the Fibonacci word the symmetric count dips at the same lags as one-sided (fib 55/89 sym <= 12, one-sided <= 6);
# (c) BREAK: a density ramp (legal prob 0.1 -> 0.9) violates the bound's ratio: |sym-2*one| exceeds 0.2*one at some lag.
import random
N = 600
def fibword(n):
    s = "1"
    while len(s) < n:
        s = "".join("10" if c == "1" else "1" for c in s)
    return [int(c) for c in s[:n]]
def counts(sig, L):
    one = sum(1 for t in range(N) if sig[t] and not sig[t+L])   # legal at t, illegal at t+L
    back = sum(1 for t in range(N) if not sig[t] and sig[t+L])
    return one, one + back
M = 130
fib = fibword(N + M)
per = [1 if t % 12 < 5 else 0 for t in range(N + M)]
viol = {}
def check(name, sig):
    worst = 0
    for L in range(1, 121):
        one, sym = counts(sig, L)
        d = abs(sym - 2*one)
        if d > L: worst += 1
    viol[name] = worst
check("fib", fib); check("per", per)
bern = 0
for seed in range(20):
    r = random.Random(seed)
    sig = [1 if r.random() < 0.618 else 0 for _ in range(N + M)]
    check("b%d" % seed, sig)
bviol = sum(v for k, v in viol.items() if k.startswith("b"))
dips = {L: counts(fib, L) for L in (55, 89)}
ramp_r = random.Random(7)
ramp = [1 if ramp_r.random() < 0.1 + 0.8 * t / (N + M) else 0 for t in range(N + M)]
ramp_dev = max(abs(counts(ramp, L)[1] - 2*counts(ramp, L)[0]) / max(1, counts(ramp, L)[0]) for L in range(1, 121))
print("violations fib/per/bernoulli-total:", viol["fib"], viol["per"], bviol)
print("fib dips (one,sym):", dips)
print("ramp worst relative deviation: %.2f" % ramp_dev)
ok = viol["fib"] == 0 and viol["per"] == 0 and bviol == 0 and all(s <= 12 and o <= 6 for o, s in dips.values()) and ramp_dev > 0.2
print("RESULT: %s |sym-2*one|<=L on fib, P12W5 and 20 Bernoulli seeds over lags 1..120 (violations %d/%d/%d); fib55 one/sym %s, fib89 %s; ramp rel dev %.2f" % ("PASS" if ok else "FAIL", viol["fib"], viol["per"], bviol, dips[55], dips[89], ramp_dev))
