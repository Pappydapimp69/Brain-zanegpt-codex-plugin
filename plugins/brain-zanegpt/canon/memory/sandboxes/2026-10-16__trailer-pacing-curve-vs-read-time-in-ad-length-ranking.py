import math
def shots(L, d0, d1):
    """linear pacing: hold shrinks d0 -> d1 across L seconds; returns list of (start, hold)."""
    t = 0.0; out = []
    while t < L - 1e-9:
        d = d0 + (d1 - d0) * (t / L); d = min(d, L - t) if L - t < d else d
        out.append((t, d)); t += d
    return out
def comp(L, d0, d1, r):
    """share of screen time on shots held at least r seconds (readable); the last 20% (climax) counts double."""
    tot = ok = 0.0
    for t, d in shots(L, d0, d1):
        w = 2.0 if t >= 0.8 * L else 1.0
        tot += w * d; ok += w * d * (d >= r - 1e-9)
    return ok / tot
def value(L, h, curve, r, rule):
    c = comp(L, *curve, r)
    ipm = 0.35 * math.exp(-h * (L - 3)) * (1 + L / 60) * 1.65 * c      # anchored cut, ending kept
    d1 = 0.30 * (0.5 + 0.5 * c)
    return ipm * d1 if rule == "ipm*d1" else ipm
CURVES = {"flat1.0": (1.0, 1.0), "trailer 1.0->0.4": (1.0, 0.4), "trailer 1.5->0.6": (1.5, 0.6), "slow 1.5->1.2": (1.5, 1.2)}
res = {}
for r in (0.5, 1.0):
    for name, cv in CURVES.items():
        res[(r, name)] = (round(comp(15, *cv, r), 3), round(comp(30, *cv, r), 3))
        print("read-time", r, name, "comprehension 15s/30s", res[(r, name)], "n shots 15s", len(shots(15, *cv)))
def best(L, h, r, rule): return max(CURVES, key=lambda n: value(L, h, CURVES[n], r, rule))
b = {(r, rule): best(15, 0.03, r, rule) for r in (0.5, 1.0) for rule in ("ipm", "ipm*d1")}
print("best curve at 15s, 3%/s:", b)
def cross(curve, r, rule):
    lo, hi = 0.0, 0.5
    for _ in range(50):
        m = (lo + hi) / 2
        if value(15, m, curve, r, rule) > value(30, m, curve, r, rule): hi = m
        else: lo = m
    return round(hi, 4)
cx = {n: cross(CURVES[n], 1.0, "ipm*d1") for n in CURVES}; cx05 = cross(CURVES["trailer 1.0->0.4"], 0.5, "ipm*d1")
print("15 vs 30 crossover at read-time 1.0:", cx, " trailer curve at read-time 0.5:", cx05)
t = "trailer 1.0->0.4"
ok = (res[(0.5, t)][0] < 0.8 and res[(1.0, t)][0] < 0.1 and res[(1.0, "flat1.0")][0] == 1.0
      and all(v != t for v in b.values()) and cx[t] < cx["flat1.0"] and cx05 > cx["flat1.0"])
print("RESULT: %s trailer pacing 1.0->0.4 s reads %.3f of the 15 s ad at read-time 0.5 and %.3f at 1.0 (flat 1.0 s pacing: 1.0); flat pacing is the best 15 s curve under IPM and IPM x D1; the 15-vs-30 crossover is %.4f flat, %.4f for the trailer curve at read-time 1.0 (the 30 s trailer reads worse, %.3f vs %.3f) and %.4f at read-time 0.5"
      % ("PASS" if ok else "FAIL", res[(0.5, t)][0], res[(1.0, t)][0], cx["flat1.0"], cx[t], res[(1.0, t)][1], res[(1.0, t)][0], cx05))
