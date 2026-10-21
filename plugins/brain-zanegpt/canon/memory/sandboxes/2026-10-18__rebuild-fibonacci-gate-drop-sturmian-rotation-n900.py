# My own fixture: Sturmian rotation word s(n)=floor((n+2)*a)-floor((n+1)*a), a=1/phi, N=900 (not substitution, N differs, offset 2).
# Prediction (written before running): one-sided invalid(L) ~ N*||L*a|| (within 40% +/- 3), so
# fib 55 <= 12, fib 89 <= 8, Lucas 47 in 30..55 and 76 in 18..40, window(40..70) median > 150,
# corr(invalid, ||L a||) over lags 1..144 > 0.9, 10 Bernoulli(0.618) seeds give mean at lag 55 and 89 within 190..235.
import random, math
a = (math.sqrt(5) - 1) / 2
N, M = 900, 150
s = [math.floor((n + 2) * a) - math.floor((n + 1) * a) for n in range(N + M)]
def inv(sig, L): return sum(1 for t in range(N) if sig[t] and not sig[t + L])
def dist(L): x = (L * a) % 1; return min(x, 1 - x)
inv_f = {L: inv(s, L) for L in range(1, 145)}
xs = [dist(L) for L in range(1, 145)]; ys = [inv_f[L] for L in range(1, 145)]
mx, my = sum(xs)/144, sum(ys)/144
corr = sum((x-mx)*(y-my) for x, y in zip(xs, ys)) / math.sqrt(sum((x-mx)**2 for x in xs) * sum((y-my)**2 for y in ys))
med = sorted(inv_f[L] for L in range(40, 71))[15]
bern = {55: [], 89: []}
for seed in range(100, 110):
    r = random.Random(seed); b = [1 if r.random() < a else 0 for _ in range(N + M)]
    for L in bern: bern[L].append(inv(b, L))
bm = {L: sum(v)/len(v) for L, v in bern.items()}
print("fib55 %d fib89 %d lucas47 %d lucas76 %d median40-70 %d corr %.3f bern %s" % (inv_f[55], inv_f[89], inv_f[47], inv_f[76], med, corr, bm))
ok = inv_f[55] <= 12 and inv_f[89] <= 8 and 30 <= inv_f[47] <= 55 and 18 <= inv_f[76] <= 40 and med > 150 and corr > 0.9 and all(190 <= v <= 235 for v in bm.values())
print("RESULT: %s fib55=%d fib89=%d lucas47=%d lucas76=%d median=%d corr=%.3f bernoulli55=%.0f bernoulli89=%.0f" % ("PASS" if ok else "FAIL", inv_f[55], inv_f[89], inv_f[47], inv_f[76], med, corr, bm[55], bm[89]))
