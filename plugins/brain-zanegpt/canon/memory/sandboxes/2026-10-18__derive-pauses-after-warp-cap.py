# Sandbox: pause derivation order relative to the 1.5 caption-warp cap.
# Prediction (before first run): when raw per-scene warp exceeds the 1.5 cap (2.4 and 1.8),
# pauses derived BEFORE the cap miss >=4 of 8 post-cap caption ends by >0.5s; derived AFTER the cap miss 0.
# BREAK case: raw warp already <=1.5 so the cap is a no-op and both orders agree (0 misses).
caps = [(0,4),(4,9),(9,12),(12,18),(18,22),(22,30),(30,33),(33,40)]
scene = [0,0,0,0,1,1,1,1]
CAP = 1.5

def warp(factors):
    out, t = [], 0.0
    for (s, e), sc in zip(caps, scene):
        d = (e - s) * factors[sc]; out.append((t, t + d)); t += d
    return out

def run(raw):
    before = [e for _, e in warp(raw)]                         # derived from uncapped warp
    capped = warp([min(f, CAP) for f in raw])                  # what the film actually uses
    after = [e for _, e in capped]
    miss = lambda p: sum(1 for a, (_, e) in zip(p, capped) if abs(a - e) > 0.5)
    return miss(before), miss(after)

scen = {"raw 2.4/1.8": (2.4, 1.8), "raw 1.9/2.4": (1.9, 2.4), "raw 1.3/1.5 (BREAK, cap no-op)": (1.3, 1.5)}
res = {}
for n, f in scen.items():
    res[n] = run(f); print(n, "before_cap_miss=%d after_cap_miss=%d" % res[n])
k = list(scen)
ok = (res[k[0]][0] >= 4 and res[k[1]][0] >= 4 and all(v[1] == 0 for v in res.values()) and res[k[2]][0] == 0)
print("RESULT: %s derive-before-cap misses %d/8 and %d/8, derive-after-cap 0/8, cap no-op case 0/8"
      % ("PASS" if ok else "FAIL", res[k[0]][0], res[k[1]][0]))
