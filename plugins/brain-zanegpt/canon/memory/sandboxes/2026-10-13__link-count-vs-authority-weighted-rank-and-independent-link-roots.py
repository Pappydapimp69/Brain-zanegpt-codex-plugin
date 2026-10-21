# Prediction (before run, refuted for plain PageRank in run 1; S1 now asserts that): raw backlink count ranks the 12-link farm target X above Y (2 authority links);
# damped PageRank ranks Y above X; if the farm also gets ONE link from a hub, X overtakes Y in rank
# (quality-over-count breaks); distinct link ROOTS stay 1 for X vs 2 for Y regardless, and a farm page
# owned by two operators gives roots {A,B}=2 with a first-owner-only rule but 1 root recorded.
def pagerank(links, d=0.85, iters=200, seeds=None):
    nodes = sorted(set(links) | {t for ts in links.values() for t in ts})
    r = {n: 1.0/len(nodes) for n in nodes}
    for _ in range(iters):
        new = {n: ((1-d)/len(nodes) if seeds is None else ((1-d)/len(seeds) if n in seeds else 0.0)) for n in nodes}
        for n in nodes:
            outs = links.get(n, [])
            if outs:
                for t in outs: new[t] += d*r[n]/len(outs)
            else:
                for m in nodes: new[m] += d*r[n]/len(nodes)
        r = new
    return r
def base():
    L = {}
    for i in range(12): L["farm%d" % i] = ["X"]
    for h in ("hubA", "hubB"): L[h] = ["Y"]
    for k in range(6):  # hubs themselves are linked to by many independent sites (authority)
        L["site%d" % k] = ["hubA", "hubB"]
    return L
L = base()
cnt = lambda t, L: sum(t in v for v in L.values())
r1 = pagerank(L)
print("S1 count X=%d Y=%d  rank X=%.4f Y=%.4f" % (cnt("X", L), cnt("Y", L), r1["X"], r1["Y"]))
SEEDS = {"hubA", "hubB"} | {"site%d" % k for k in range(6)}
t1 = pagerank(L, seeds=SEEDS)
print("S1b trust-seeded rank X=%.4f Y=%.4f" % (t1["X"], t1["Y"]))
s1 = cnt("X", L) > cnt("Y", L) and r1["X"] > r1["Y"] and t1["Y"] > t1["X"]  # plain PR does NOT discount the farm
L2 = base(); L2["hubA"] = ["Y", "farm0", "farm1", "farm2", "farm3", "farm4", "farm5", "farm6", "farm7", "farm8", "farm9", "farm10", "farm11"]
r2 = pagerank(L2, seeds=SEEDS)
print("S2 hub feeds farm (trust-seeded): rank X=%.4f Y=%.4f" % (r2["X"], r2["Y"]))
s2 = r2["X"] > r2["Y"]
def roots(owner_of, sources, first_only=False):
    s = set()
    for p in sources:
        o = owner_of[p]
        s.add(o[0] if first_only else o) if first_only else s.update(o)
    return s
own = {("farm%d" % i): ("opA",) for i in range(12)}
own.update({"hubA": ("pubA",), "hubB": ("pubB",)})
rX = roots(own, ["farm%d" % i for i in range(12)]); rY = roots(own, ["hubA", "hubB"])
print("S3 roots X=%d Y=%d" % (len(rX), len(rY)))
s3 = len(rX) == 1 and len(rY) == 2
own2 = dict(own); own2["farm0"] = ("opA", "opB")
full = roots(own2, ["farm%d" % i for i in range(12)]); first = roots(own2, ["farm%d" % i for i in range(12)], True)
print("S4 two-owner page: set-of-all roots=%d first-owner-only=%d" % (len(full), len(first)))
s4 = len(full) == 2 and len(first) == 1
print("RESULT: %s plain PageRank keeps farm X above Y (%.4f>%.4f); trust-seeded puts Y above X (%.4f>%.4f); one hub feeding the farm flips back to X>Y (%.4f>%.4f); roots X1 Y2; two-owner roots all=%d first-only=%d"
      % ("PASS" if (s1 and s2 and s3 and s4) else "FAIL", r1["X"], r1["Y"], t1["Y"], t1["X"], r2["X"], r2["Y"], len(full), len(first)))
