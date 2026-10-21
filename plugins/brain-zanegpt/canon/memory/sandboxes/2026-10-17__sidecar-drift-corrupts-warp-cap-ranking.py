"""Sandbox: variant->warp mapping kept in a hand-maintained sidecar (drifts when a variant is
renamed/dropped) vs derived from the render source, feeding a warp cap before IPM*D1 ranking.
Deterministic: variants enumerated, no RNG. D1 = base_d1 - slope*max(0, warp-1).
Cap: warp is clipped to CAP before the (retention) penalty is applied... i.e. capped variants are
re-cut at warp<=CAP so their penalty uses min(warp,CAP). Ranking score = IPM*D1.
Sidecar drift: after K renames, the sidecar looks up warp by the old name -> returns the warp of
a different variant (shift by one) or default 1.0 when missing.
"""
import itertools
CAP = 1.5
# (name, ipm, base_d1, true_warp)
V = [("v0", 10.0, 0.40, 1.0), ("v1", 12.0, 0.34, 1.9), ("v2", 11.0, 0.37, 1.6),
     ("v3", 9.0, 0.42, 1.1), ("v4", 13.0, 0.30, 2.2), ("v5", 10.5, 0.38, 1.4)]
def penalty(slope, warp): return slope * max(0.0, warp - 1.0)
def pick(slope, warp_of):
    best, bs = None, -1
    for n, ipm, d1, w in V:
        ww = warp_of(n)                    # what the pipeline BELIEVES
        believed = min(ww, CAP)            # cap applied to believed warp
        d1_real = max(0.0, d1 - penalty(slope, min(w, CAP)))   # real outcome after cap on TRUE warp
        # the cap is only applied (footage actually re-cut) if believed warp exceeds CAP
        recut = ww > CAP
        d1_eff = max(0.0, d1 - penalty(slope, min(w, CAP) if recut else w))
        s = ipm * d1_eff
        if s > bs: best, bs = n, s
    return best
def truth_score(slope):  # best by true post-cap outcome
    return max(V, key=lambda t: t[1] * max(0.0, t[2] - penalty(slope, min(t[3], CAP))))[0]
names = [v[0] for v in V]
true_map = {v[0]: v[3] for v in V}
derived = lambda n: true_map[n]
def sidecar(shift, missing):
    m = {}
    for i, n in enumerate(names):
        m[n] = true_map[names[(i + shift) % len(names)]] if shift else true_map[n]
    for n in missing: m.pop(n, None)
    return lambda n: m.get(n, 1.0)
def truth_value(slope, n):
    t = [v for v in V if v[0] == n][0]
    return t[1] * max(0.0, t[2] - penalty(slope, min(t[3], CAP)))
rows = []
for slope in (0.0, 0.001, 0.003, 0.005, 0.008, 0.01, 0.015, 0.02, 0.03, 0.05, 0.1, 0.2):
    t = truth_score(slope)
    d = pick(slope, derived)
    s1 = pick(slope, sidecar(1, []))
    s2 = pick(slope, sidecar(0, ["v4", "v1"]))
    s3 = pick(slope, sidecar(2, ["v5"]))
    loss = lambda p: round(truth_value(slope, t) - truth_value(slope, p), 3)
    rows.append((slope, t, d, s1, s2, s3, loss(d), loss(s1), loss(s2), loss(s3)))
    print(f"slope={slope}: truth={t} derived={d} sidecar_shift1={s1}(loss {loss(s1)}) sidecar_missing={s2}(loss {loss(s2)}) sidecar_shift2+missing={s3}(loss {loss(s3)})")
derived_ok = all(r[1] == r[2] for r in rows)
bad = [r for r in rows if r[7] > 0 or r[8] > 0 or r[9] > 0]
flat_ok = all(r[7] == r[8] == r[9] == 0 for r in rows if r[0] == 0.0)
print("derived map matches truth at every slope:", derived_ok)
print("slopes where a drifted sidecar costs value:", [r[0] for r in bad])
ok = derived_ok and flat_ok and len(bad) >= 1
print("RESULT: %s derived map = truth at all 12 slopes; drifted sidecar loses value at slopes %s and costs nothing at slope 0.0"
      % ("PASS" if ok else "FAIL", [r[0] for r in bad]))
