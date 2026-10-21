import math
END = {"fix": 1.65, "none": 1.0}
def ipm(L, h, e): return 0.35 * math.exp(-h * (L - 3)) * (1 + L / 60) * END[e]
def d1(e, k): return 0.30 * (1 + k * (END[e] - 1))   # k = how much the withheld-outcome ending lifts retention
V = {"15 anchored": (15, "fix"), "15 truncated": (15, "none"), "30 master": (30, "fix")}
def score(name, h, k, rule):
    L, e = V[name]; i = ipm(L, h, e)
    return i if rule == "ipm" else i * d1(e, k)
def winner(h, k, rule): return max(V, key=lambda n: score(n, h, k, rule))
def crossover(a, b, k, rule):
    lo, hi = 0.0, 0.5
    for _ in range(60):
        m = (lo + hi) / 2
        if score(a, m, k, rule) > score(b, m, k, rule): hi = m
        else: lo = m
    return round(hi, 4)
out = {}
# S1 reproduce prior: ipm-only crossover anchored vs truncated
out["ipm_anch"] = crossover("15 anchored", "30 master", 0, "ipm")
out["ipm_trunc"] = crossover("15 truncated", "30 master", 0, "ipm")
# S2 ipm*d1 with ending-linked retention (k=1): crossover shifts?
out["d1_anch"] = crossover("15 anchored", "30 master", 1, "ipm*d1")
out["d1_trunc"] = crossover("15 truncated", "30 master", 1, "ipm*d1")
# S3 BREAK: flat D1 (k=0) must collapse to ipm-only
out["flat_trunc"] = crossover("15 truncated", "30 master", 0, "ipm*d1")
# S4 does ranking differ between rules anywhere on 1..8%/s grid, with truncated vs master
flips = [h / 100 for h in range(1, 9) if winner(h / 100, 1, "ipm") != winner(h / 100, 1, "ipm*d1")]
out["rule_flips"] = flips
# S5 sample-size quantization: install counts floored at n impressions, rank by whole installs*d1
def sampled(n, h, k):
    sc = {}
    for nm in V:
        L, e = V[nm]; inst = math.floor(ipm(L, h, e) * n / 10); sc[nm] = inst * d1(e, k)
    return max(sc, key=sc.get)
out["flip_by_n"] = {n: sampled(n, 0.03, 1) for n in (30, 100, 300, 1000)}
print(out)
ok = (abs(out["ipm_anch"] - 0.0122) < 0.001 and abs(out["ipm_trunc"] - 0.0455) < 0.002
      and out["flat_trunc"] == out["ipm_trunc"] and out["d1_trunc"] > out["ipm_trunc"] and abs(out["d1_anch"] - out["ipm_anch"]) < 0.001)
print("RESULT: %s ipm crossover %.4f anchored/%.4f truncated; ipm*d1 with ending-linked D1 -> %.4f/%.4f; flat D1 %.4f; rule flips at %s; small-n winners %s"
      % ("PASS" if ok else "FAIL", out["ipm_anch"], out["ipm_trunc"], out["d1_anch"], out["d1_trunc"], out["flat_trunc"], flips, out["flip_by_n"]))
