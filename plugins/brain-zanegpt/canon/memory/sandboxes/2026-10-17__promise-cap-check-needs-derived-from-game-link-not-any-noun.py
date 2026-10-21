import itertools
# Cold-open variant: (mech, deco). mech = game mechanics shown (some beyond what is delivered), deco = decorative nouns (props, logos).
# Game delivers DELIVERED mechanics. True retention D1 falls with real over-promise = max(0, mech - DELIVERED).
# IPM rises with mech and (weakly) with deco. Rule under test: cap promise at delivery, using a check column that counts promise.
DELIVERED = 2
def ipm(m, d, hook): return 10*hook*(1 + .35*m + .08*d)
def d1(m, pen): return max(.05, .30 - pen*max(0, m-DELIVERED))
def best(variants, key): return max(variants, key=key)
def run(pen, deco_pool, label):
    V = [(m, d, h) for m in range(0, 6) for d in deco_pool for h in (1.0, 1.2)]
    truth = lambda v: ipm(v[0], v[1], v[2]) * d1(v[0], pen)
    t = best(V, truth)
    # check column estimates promise; cap = promise <= DELIVERED, then rank by IPM among the survivors
    naive = lambda v: v[0] + v[1]       # any new noun counts as promise
    derived = lambda v: v[0]            # only nouns linked to a game mechanic
    out = {}
    for name, col in (("naive", naive), ("derived", derived)):
        S = [v for v in V if col(v) <= DELIVERED] or V
        p = best(S, lambda v: ipm(*v))
        out[name] = (p, truth(p) / truth(t))
    return t, out
rows = {}
for label, pen, deco in (("flat-no-deco", 0.0, (0,)), ("linear+deco", .06, (0, 1, 2, 3)), ("steep+deco", .12, (0, 1, 2, 3)), ("cliff+deco BREAK", .25, (0, 2, 4))):
    t, o = run(pen, deco, label); rows[label] = (t, o)
    print(f"{label:18s} truth={t[:2]} naive pick={o['naive'][0][:2]} ratio={o['naive'][1]:.3f} | derived pick={o['derived'][0][:2]} ratio={o['derived'][1]:.3f}")
deco_rows = [k for k in rows if "deco" in k and k != "flat-no-deco"]
nv = [rows[k][1]["naive"][1] for k in deco_rows]; dv = [rows[k][1]["derived"][1] for k in deco_rows]
ok = all(x < 0.97 for x in nv) and all(x >= 0.97 for x in dv) and rows["flat-no-deco"][1]["naive"][0] == rows["flat-no-deco"][1]["derived"][0]
print("RESULT: %s promise cap on any-noun column keeps %s of the true-best value vs %s for derived-from-game column on decorated sheets; identical with no decoration" % ("PASS" if ok else "FAIL", "/".join(f"{x:.2f}" for x in nv), "/".join(f"{x:.2f}" for x in dv)))
