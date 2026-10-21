"""IPM x D1 recut rank with three fidelity columns: derived-from-game link (with
read noise), hand-kept sidecar (drifts after renames), any-new-noun check.
Pick = argmax IPM * D1_estimated; scored against the true IPM * D1 best."""
import random

def sheet(rng, n=6):
    v = []
    for i in range(n):
        f = rng.choice([0.2, 0.5, 1.0])          # true fidelity to the game
        hook = rng.uniform(0.8, 1.3)
        ipm = 10 * hook * (1.6 - 0.6 * f)         # flashy = higher IPM, lower fidelity
        v.append(dict(id=i, f=f, ipm=ipm, noun=rng.random() < 0.5))
    return v

def d1(f):
    return 0.15 + 0.25 * f

def true_best(v):
    return max(v, key=lambda x: x["ipm"] * d1(x["f"]))["id"]

def pick(v, est):
    return max(v, key=lambda x: x["ipm"] * d1(est(x)))["id"]

def run(noise, drift, trials=2000, seed=7):
    rng = random.Random(seed)
    ok = dict(derived=0, sidecar=0, noun=0, ipm=0)
    for _ in range(trials):
        v = sheet(rng)
        t = true_best(v)
        # derived link: reads fidelity, but with prob `noise` returns a wrong level
        der = {x["id"]: (rng.choice([0.2, 0.5, 1.0]) if rng.random() < noise else x["f"]) for x in v}
        # sidecar: after a rename each entry is stale with prob `drift` (copies another variant's value)
        side = {x["id"]: (rng.choice(v)["f"] if rng.random() < drift else x["f"]) for x in v}
        ok["derived"] += pick(v, lambda x: der[x["id"]]) == t
        ok["sidecar"] += pick(v, lambda x: side[x["id"]]) == t
        ok["noun"] += pick(v, lambda x: 1.0 if x["noun"] else 0.5) == t   # noun flag independent of f
        ok["ipm"] += max(v, key=lambda x: x["ipm"])["id"] == t
    return {k: c / trials for k, c in ok.items()}

res = {}
for noise in (0.0, 0.2, 0.5, 0.8):
    res[noise] = run(noise, drift=0.25)
    print("noise", noise, {k: round(x, 3) for k, x in res[noise].items()})
clean = run(0.0, 0.0)
print("drift 0 clean", {k: round(x, 3) for k, x in clean.items()})
flat = None
# crossover: first noise level where derived <= sidecar at drift 0.25
cross = next((n for n in (0.0, 0.2, 0.5, 0.8) if res[n]["derived"] <= res[n]["sidecar"]), None)
ok = (res[0.0]["derived"] > res[0.0]["sidecar"] > res[0.0]["noun"]
      and clean["sidecar"] == 1.0 and res[0.8]["derived"] <= res[0.8]["sidecar"])
print("crossover noise (derived <= sidecar at drift .25):", cross)
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
      "derived@0 %.3f sidecar@.25 %.3f noun %.3f ipm %.3f; derived@.8 %.3f; crossover noise %s; drift0 sidecar %.3f"
      % (res[0.0]["derived"], res[0.0]["sidecar"], res[0.0]["noun"], res[0.0]["ipm"], res[0.8]["derived"], cross, clean["sidecar"]))
