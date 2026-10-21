# Sandbox: reaction-cut pauses derived from captions vs a hand-kept sidecar, after caption warp.
# Prediction (written before first run): with per-scene warp 1.0-1.5, a sidecar of pause times
# frozen before the warp misses >=5 of 8 trigger-caption ends by >0.5s; the derived map misses 0.
# With warp 1.0 (break case) both agree, so the drift is caused by the warp, not by the sidecar form.
caps = [(0,4),(4,9),(9,12),(12,18),(18,22),(22,30),(30,33),(33,40)]  # (start,end) seconds, 8 lines
scene = [0,0,0,0,1,1,1,1]

def warp(caps, factors):
    out, t = [], 0.0
    for (s, e), sc in zip(caps, scene):
        d = (e - s) * factors[sc]
        out.append((t, t + d)); t += d
    return out

def run(factors):
    sidecar = [e for _, e in caps]                      # frozen pause list (hand-maintained)
    new = warp(caps, factors)
    derived = [e for _, e in new]                       # recomputed from the real caption source
    miss_side = sum(1 for p, (_, e) in zip(sidecar, new) if abs(p - e) > 0.5)
    miss_der = sum(1 for p, (_, e) in zip(derived, new) if abs(p - e) > 0.5)
    return miss_side, miss_der

scen = {"warp 1.5/1.3": (1.5, 1.3), "warp 1.2/1.4": (1.2, 1.4), "warp 1.0/1.0 (BREAK)": (1.0, 1.0)}
res = {}
for name, f in scen.items():
    res[name] = run(f); print(name, "sidecar_miss=%d derived_miss=%d" % res[name])
ok = (res["warp 1.5/1.3"][0] >= 5 and res["warp 1.2/1.4"][0] >= 5
      and all(v[1] == 0 for v in res.values()) and res["warp 1.0/1.0 (BREAK)"][0] == 0)
print("RESULT: %s sidecar misses %d/8 and %d/8 after warp, derived 0/8, no drift at warp 1.0"
      % ("PASS" if ok else "FAIL", res["warp 1.5/1.3"][0], res["warp 1.2/1.4"][0]))
