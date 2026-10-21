# Variants have true install rate p (IPM proxy) and true D1 retention r; score = p*r. Test: does a larger batch
# (6, 12, 16 variants - the trope-cap ceilings) keep the same pick accuracy at fixed impressions per variant?
# Seeded, stdlib only. Binomial draws by summing Bernoulli trials (n small).
import random
def pick_correct(k, n, seed, trials=400):
    rng = random.Random(seed); hit = 0; regret = 0.0
    for _ in range(trials):
        v = [(rng.uniform(.04, .12), rng.uniform(.25, .45)) for _ in range(k)]
        true = [p*r for p, r in v]
        est = []
        for p, r in v:
            inst = sum(rng.random() < p for _ in range(n))
            ret = sum(rng.random() < r for _ in range(inst))
            est.append(ret / n)  # retained installs per impression
        w = est.index(max(est)); hit += w == true.index(max(true)); regret += max(true) - true[w]
    return hit/trials, regret/trials
out = {}
for k in (6, 12, 16):
    for n in (300, 1000, 3000):
        out[(k, n)] = pick_correct(k, n, k*7+n)
        print("k=%2d n=%4d best picked %.2f mean regret %.4f" % ((k, n)+out[(k, n)]))
ok = out[(6, 300)][0] > out[(16, 300)][0] and out[(16, 3000)][0] > out[(16, 300)][0]
need = min((n for n in (300, 1000, 3000) if out[(16, n)][0] >= out[(6, 300)][0]), default=None)
print("RESULT: %s at 300 impressions best picked k6 %.2f k12 %.2f k16 %.2f; k16 at 3000 %.2f; k16 matches k6@300 first at n=%s; regret k16@300 %.4f vs k6@300 %.4f" % (
    "PASS" if ok else "FAIL", out[(6,300)][0], out[(12,300)][0], out[(16,300)][0], out[(16,3000)][0], need, out[(16,300)][1], out[(6,300)][1]))
