# Prediction (before run): ranking recuts on IPM x predicted-D1, where predicted D1 uses a
# fidelity check column. Naive "any new noun = faithful" check picks a non-delivering recut in
# >=3 of 6 sheets; derived-from-game link check picks the true best in 6/6.
# Assumption: new nouns correlate with fidelity. Break case: sheet 6, all recuts derived -> tie.
import random
def sheet(seed, kind):
    r = random.Random(seed)
    out = []
    for i in range(6):
        if kind == "all_derived":
            derived = True
        else:
            derived = r.random() < 0.5
        new_noun = (not derived) if kind == "flashy" else r.random() < 0.5
        stock = kind == "stock" and r.random() < 0.5
        ipm = r.uniform(4, 8) + (2.5 if not derived else 0)   # flashy undelivering hooks convert better
        d1 = 0.40 if derived else 0.20                          # but retain worse
        out.append(dict(derived=derived, noun=new_noun, stock=stock, ipm=ipm, d1=d1))
    return out
def true_val(v): return v["ipm"] * v["d1"]
def pick(vs, check):
    def est(v):
        faithful = check(v)
        return v["ipm"] * (0.40 if faithful else 0.20)
    return max(vs, key=est)
naive = lambda v: v["noun"]
link = lambda v: v["derived"] and not v["stock"]
scen = [("flashy",1),("flashy",2),("mixed",3),("mixed",4),("stock",5),("all_derived",6)]
nw = lw = 0
for kind, seed in scen:
    vs = sheet(seed, kind); best = max(vs, key=true_val)
    pn, pl = pick(vs, naive), pick(vs, link)
    nw += pn is best; lw += pl is best
    print(kind, seed, "naive_ok", pn is best, "link_ok", pl is best)
print(f"RESULT: {'PASS' if lw>nw else 'FAIL'} naive exact {nw}/6, link-check exact {lw}/6")
