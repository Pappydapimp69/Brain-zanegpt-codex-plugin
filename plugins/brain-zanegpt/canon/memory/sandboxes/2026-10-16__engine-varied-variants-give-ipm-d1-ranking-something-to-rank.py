import random, math
# Variants of one winning concept: pool A varies the comic ENGINE, pool B varies only the TOPIC.
# Hidden assumption: engine changes true IPM*D1 materially; topic swaps barely do. Ranking by
# measured IPM*D1 then only pays when the pool has real spread. Breaker: engine effect = 0.
def trial(rng, spread, n_var=6, imps=300):
    true = [max(0.002, 0.04*math.exp(rng.gauss(0, spread))) for _ in range(n_var)]  # install rate
    d1 = [min(0.6, max(0.05, 0.30 + rng.gauss(0, spread*0.5))) for _ in range(n_var)]
    value = [t*d for t, d in zip(true, d1)]
    meas = []
    for t, d in zip(true, d1):
        inst = sum(rng.random() < t for _ in range(imps))
        ret = sum(rng.random() < d for _ in range(inst))
        meas.append((inst/imps) * (ret/inst if inst else 0))
    pick = max(range(n_var), key=lambda i: meas[i]); rand = rng.randrange(n_var)
    best = max(value)
    return value[pick]/best, value[rand]/best, pick == value.index(best)
def run(spread, seed, N=2000):
    rng = random.Random(seed); r = [trial(rng, spread) for _ in range(N)]
    return sum(x[0] for x in r)/N, sum(x[1] for x in r)/N, sum(x[2] for x in r)/N
res = {}
for name, spread in [("engine-varied", 0.50), ("topic-varied", 0.08), ("engine-no-effect", 0.0)]:
    res[name] = run(spread, 7); print(name, "ranked=%.3f random=%.3f hit-best=%.3f" % res[name])
gain = {k: v[0]-v[1] for k, v in res.items()}
print("gain over random pick:", {k: round(v, 3) for k, v in gain.items()})
ok = gain["engine-varied"] > 0.08 and gain["topic-varied"] < 0.03 and abs(gain["engine-no-effect"]) < 0.02
print("RESULT: %s engine gain %.3f vs topic %.3f vs none %.3f" % ("PASS" if ok else "FAIL", gain["engine-varied"], gain["topic-varied"], gain["engine-no-effect"]))
