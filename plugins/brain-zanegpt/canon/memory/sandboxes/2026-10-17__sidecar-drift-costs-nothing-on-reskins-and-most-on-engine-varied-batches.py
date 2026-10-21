# Composes: collective-reference (a hand-kept sidecar drifts silently; derive from the source),
# rank-ipm-times-d1-needs-fidelity-retention-link (rank on IPM x D1 with a fidelity column) and the kernel
# vary-the-comic-engine-not-the-topic (a batch of reskins of one engine versus a batch of different engines).
# Batch of 6 recuts. RESKIN: all share one engine fidelity f0 (only hook quality differs). VARIED: each has its
# own fidelity from {0.2,0.5,1.0}. Sidecar: with probability `drift` an entry holds another variant's fidelity.
# Derived column reads the true fidelity. Score = fraction of 2000 batches where the pick is the true IPM x D1 best.
# PREDICTION (before run): at drift 0.25 the sidecar picks the true best in 100% of RESKIN batches (stale entries
# copy an equal value) and in about 65% of VARIED batches (nearly the earlier 66.7%); the derived column is 100%
# in both; a MIXED batch (3 reskins of one strong engine plus 3 varied) lands between (80% to 95%).
import random
def batch(rng, kind, n=6):
    f0 = rng.choice([0.2, 0.5, 1.0]); v = []
    for i in range(n):
        if kind == "reskin": f = f0
        elif kind == "varied": f = rng.choice([0.2, 0.5, 1.0])
        else: f = f0 if i < 3 else rng.choice([0.2, 0.5, 1.0])
        v.append(dict(id=i, f=f, ipm=10 * rng.uniform(0.8, 1.3) * (1.6 - 0.6 * f)))
    return v
d1 = lambda f: 0.15 + 0.25 * f
def best(v, key): return max(v, key=lambda x: x["ipm"] * d1(key(x)))["id"]
def run(kind, drift, trials=2000, seed=11):
    rng = random.Random(seed); hit = dict(derived=0, sidecar=0); gap = 0.0
    for _ in range(trials):
        v = batch(rng, kind); t = best(v, lambda x: x["f"])
        side = {x["id"]: (rng.choice(v)["f"] if rng.random() < drift else x["f"]) for x in v}
        hit["derived"] += best(v, lambda x: x["f"]) == t
        p = best(v, lambda x: side[x["id"]]); hit["sidecar"] += p == t
        tv = {x["id"]: x for x in v}
        gap += tv[t]["ipm"] * d1(tv[t]["f"]) - tv[p]["ipm"] * d1(tv[p]["f"])
    return {k: round(c / trials, 3) for k, c in hit.items()}, round(gap / trials, 3)
out = {}
for kind in ("reskin", "mixed", "varied"):
    out[kind] = run(kind, 0.25); print(kind, "drift .25", out[kind])
for dr in (0.1, 0.5):
    print("varied drift", dr, run("varied", dr))
ok = (out["reskin"][0]["sidecar"] == 1.0 and out["varied"][0]["derived"] == 1.0
      and 0.55 <= out["varied"][0]["sidecar"] <= 0.75 and 0.8 <= out["mixed"][0]["sidecar"] <= 0.95)
print(f"RESULT: {'PASS' if ok else 'FAIL'} sidecar exact at drift 0.25: reskin {out['reskin'][0]['sidecar']}, mixed {out['mixed'][0]['sidecar']}, varied {out['varied'][0]['sidecar']}; derived varied {out['varied'][0]['derived']}; mean value lost reskin {out['reskin'][1]}, varied {out['varied'][1]}")
