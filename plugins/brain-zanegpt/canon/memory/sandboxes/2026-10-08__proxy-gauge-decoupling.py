# Deterministic sandbox: does a proxy metric (object count) predict true cost (draw calls)
# when a view-window cull sits between them? No RNG, no timing.
def scene(n=200):  # objects at x=0..n-1, material = x % 4
    return [(x, x % 4) for x in range(n)]

def cost(objs, lo, hi, batch=1):
    """true cost = draw calls: culled to [lo,hi), then grouped by material in chunks of `batch`."""
    vis = [o for o in objs if lo <= o[0] < hi]
    if batch == 1:
        return len(vis)
    by = {}
    for _, m in vis:
        by[m] = by.get(m, 0) + 1
    return sum(-(-c // batch) for c in by.values())

def prune(objs, keep):  # deterministic prune: keep objects whose x passes predicate
    return [o for o in objs if keep(o[0])]

W = (0, 5)  # window sees 5 objects
base = scene()
checks = []

# S1 no cull (window = everything): proxy tracks truth
p0, t0 = len(base), cost(base, 0, 200)
half = prune(base, lambda x: x % 2 == 0)
p1, t1 = len(half), cost(half, 0, 200)
print("S1 no-cull: proxy %d->%d truth %d->%d" % (p0, p1, t0, t1))
checks.append(p1 < p0 and t1 < t0 and (p0 - p1) == (t0 - t1))

# S2 window cull: prune out-of-view objects -> proxy drops, truth flat
out = prune(base, lambda x: x < 5 or x % 2 == 0)  # keeps all in-view
p2, t2 = len(out), cost(out, *W)
print("S2 cull, prune off-screen: proxy %d->%d truth %d->%d" % (p0, p2, cost(base, *W), t2))
checks.append(p2 < p0 and t2 == cost(base, *W))

# S3 BREAK: prune the IN-VIEW objects -> same proxy-drop magnitude but truth moves
inv = prune(base, lambda x: not (x < 3))  # remove 3 in-view objects, proxy -3 only
print("S3 prune in-view: proxy %d->%d truth %d->%d" % (p0, len(inv), cost(base, *W), cost(inv, *W)))
checks.append(cost(inv, *W) < cost(base, *W))

# S4 same proxy delta (-3), different truth delta (0 vs -3): proxy cannot rank the two edits
off3 = prune(base, lambda x: x not in (100, 101, 102))
checks.append(len(off3) == len(inv) and cost(off3, *W) != cost(inv, *W))
print("S4 equal proxy (%d) truth %d vs %d" % (len(off3), cost(off3, *W), cost(inv, *W)))

# S5 camera pan: scene untouched (proxy constant), truth changes with window width
widths = [cost(base, 0, w) for w in (5, 20, 80)]
print("S5 pan/zoom: proxy const %d truth %s" % (len(base), widths))
checks.append(len(set(widths)) == 3)

# S6 batching in-view only: truth 5 -> 2 (4 materials, 5 objs); batching the culled-away set does nothing
tb = cost(base, *W, batch=8)
print("S6 batch=8 in view: truth %d->%d" % (cost(base, *W), tb))
checks.append(tb < cost(base, *W))

# S7 gauge: true-cost readout beside proxy flags decoupling (|dproxy|>=3 but dtruth==0)
def gauge(before, after, w):
    dp = len(before) - len(after); dt = cost(before, *w) - cost(after, *w)
    return "DECOUPLED" if dp >= 3 and dt == 0 else ("TRACKING" if dp == dt else "PARTIAL")
g = (gauge(base, off3, W), gauge(base, inv, W))
print("S7 gauge:", g)
checks.append(g == ("DECOUPLED", "TRACKING"))

print("RESULT: %s proxy-vs-truth: decoupled only for off-view edits; in-view edits track 1:1; window/pan alone moves truth (%s)"
      % ("PASS" if all(checks) else "FAIL", checks))
