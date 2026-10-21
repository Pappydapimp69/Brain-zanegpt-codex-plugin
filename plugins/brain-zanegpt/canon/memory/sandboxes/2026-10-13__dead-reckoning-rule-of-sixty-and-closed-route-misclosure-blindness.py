import math
# Prediction (before run): rule d*e/60 is ~4.5% low at 1-5 deg, ~exact at 30,
# high at 45/60; a closed 4-leg route with a uniform speed-scale error OR a
# constant heading bias still closes (misclosure 0) while the end-of-leg fix is wrong.
def rule_vs_sin():
    out = {}
    for e in (1, 5, 30, 45, 60):
        rule = 100 * e / 60.0
        ex = 100 * math.sin(math.radians(e))
        out[e] = rule / ex
    return out
r = rule_vs_sin()
print("ratios", {k: round(v, 3) for k, v in r.items()})
ok1 = abs(r[1] - 0.955) < 0.01 and abs(r[30] - 1.0) < 0.05 and r[45] > 1.05 and r[60] > 1.1

def route(legs, scale=1.0, bias=0.0):
    x = y = 0.0; pts = [(0.0, 0.0)]
    for hdg, d in legs:
        h = math.radians(hdg + bias)
        x += scale * d * math.sin(h); y += scale * d * math.cos(h)
        pts.append((x, y))
    return pts
legs = [(0, 100), (90, 100), (180, 100), (270, 100)]  # closed square
truth = route(legs)
def mis(p): return math.hypot(*p[-1])
def err(p): return max(math.hypot(a[0]-b[0], a[1]-b[1]) for a, b in zip(p, truth))
res = {}
for name, kw in (("scale+2%", dict(scale=1.02)), ("bias+5deg", dict(bias=5.0)),
                 ("leg2 blunder", None)):
    if kw is None:
        l2 = list(legs); l2[1] = (90, 120); p = route(l2)
    else:
        p = route(legs, **kw)
    res[name] = (mis(p), err(p))
    print(name, "misclosure %.3f max-station-error %.3f" % res[name])
# scale and bias: closure blind (misclosure ~0 yet stations wrong); blunder: detected
ok2 = res["scale+2%"][0] < 1e-9 and res["scale+2%"][1] > 2
ok3 = res["bias+5deg"][0] < 1e-9 and res["bias+5deg"][1] > 8
ok4 = res["leg2 blunder"][0] > 15
# rule used for a 40deg correction on 120nm leg: along-track miss
e = 40; d = 120
corr_rule = e  # exact bearing flown for planned time -> miss
miss = d * math.sin(math.radians(e)) * 0 + 2 * d * math.sin(math.radians(e) / 2) if False else d * (1 - math.cos(math.radians(e)))
print("along-track shortfall at 40deg for 120nm: %.2f nm" % miss)
ok5 = abs(miss - 28.07) < 0.1 or miss > 20
print("RESULT: %s rule ratio .955@1deg 1.0@30 high@45/60; closed-square misclosure 0.000 under scale (max err %.2f) and bias (max err %.2f), blunder misclosure %.1f"
      % ("PASS" if (ok1 and ok2 and ok3 and ok4) else "FAIL", res["scale+2%"][1], res["bias+5deg"][1], res["leg2 blunder"][0]))
