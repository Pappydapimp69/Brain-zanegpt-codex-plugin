# Edge: sRGB-space blending (gamma E1, pipeline E1) x key-to-fill ratio (high-key vs low-key kernel).
# A soft shadow edge (penumbra) is a coverage ramp c in [0,1] from the fill-only side (key occluded)
# to the key+fill side. Physically: L(c) = F + c*K in linear light. A compositor or shader that
# lerps the two ENCODED pixel values instead gives enc^-1(lerp(enc(F), enc(K+F), c)).
# Lit side is exposed to linear 0.8 so nothing clips. R is the total lighting ratio lit:shadow = (K+F):F,
# one of the readings of the kernel's "1:1 vs 8:1" figures.
def enc(x):
    return 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055
def dec(v):
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
def lstar(y):
    return 116 * y ** (1 / 3) - 16 if y > 216 / 24389 else y * 24389 / 27

LIT = 0.8
STEPS = 1000

def edge(R):
    shadow = LIT / R
    a, b = enc(shadow), enc(LIT)
    lin = [shadow + (LIT - shadow) * i / STEPS for i in range(STEPS + 1)]
    srg = [dec(a + (b - a) * i / STEPS) for i in range(STEPS + 1)]
    max_err = max(abs(x - y) for x, y in zip(lin, srg))
    max_rel = max(abs(x - y) / x for x, y in zip(lin, srg))
    mid = (shadow + LIT) / 2                       # half-light point of the edge
    def cross(curve, level):
        for i, v in enumerate(curve):
            if v >= level:
                return i / STEPS
        return 1.0
    if LIT - shadow < 1e-12:                       # 1:1 high-key: no edge exists, nothing can shift
        return dict(R=R, max_err=max_err, max_rel=max_rel, shift=0.0, pshift=0.0, dark_lin=0.0,
                    dark_srg=0.0, end_err=abs(lin[0] - srg[0]) + abs(lin[-1] - srg[-1]))
    shift = cross(srg, mid) - cross(lin, mid)      # + means the visible edge moves toward the lit side
    # perceptual mid (L* halfway): where a viewer sees "half shadow"
    lmid = (lstar(shadow) + lstar(LIT)) / 2
    lcurve = [lstar(v) for v in lin]
    lcurve_s = [lstar(v) for v in srg]
    pshift = cross(lcurve_s, lmid) - cross(lcurve, lmid)
    # how much of the penumbra width reads as "in shadow" (below the L* midpoint)
    dark_lin = sum(1 for v in lcurve if v < lmid) / (STEPS + 1)
    dark_srg = sum(1 for v in lcurve_s if v < lmid) / (STEPS + 1)
    end_err = abs(lin[0] - srg[0]) + abs(lin[-1] - srg[-1])
    return dict(R=R, max_err=max_err, max_rel=max_rel, shift=shift, pshift=pshift,
                dark_lin=dark_lin, dark_srg=dark_srg, end_err=end_err)

rows = [edge(R) for R in (1.0, 1.5, 2.0, 4.0, 8.0, 16.0)]
for r in rows:
    print("ratio %5.1f:1  max lum err %.4f (%.0f%% of lit)  rel %.0f%%  half-light edge shift %+.3f W  "
          "L*-mid shift %+.3f W  dark share lin %.2f srgb %.2f  endpoints err %.1e"
          % (r["R"], r["max_err"], 100 * r["max_err"] / LIT, 100 * r["max_rel"], r["shift"], r["pshift"],
             r["dark_lin"], r["dark_srg"], r["end_err"]))

monotonic = all(rows[i]["max_err"] <= rows[i + 1]["max_err"] + 1e-12 and rows[i]["shift"] <= rows[i + 1]["shift"]
                for i in range(len(rows) - 1))
hi = rows[0]; r2 = rows[2]; r8 = rows[4]; r16 = rows[5]
# core claim: zero at 1:1, grows monotonically with ratio, endpoints (pure lit / pure shadow) untouched
ok = (hi["max_err"] < 1e-9 and monotonic and r8["max_err"] > 0.1 * LIT and hi["end_err"] < 1e-9
      and r8["end_err"] < 1e-9 and r8["shift"] > r2["shift"] > 0)
print("prediction check: 8:1 shift > 0.15 W -> %s (%.3f); 8:1 err > 10%% of lit -> %s"
      % (r8["shift"] > 0.15, r8["shift"], r8["max_err"] > 0.1 * LIT))
print("monotonic in ratio:", monotonic)
print("RESULT: %s 1:1 err %.4f; 2:1 err %.3f shift %+.3f W; 8:1 err %.3f (%.0f%% of lit) half-light shift %+.3f W L*-mid shift %+.3f W dark share %.2f->%.2f; 16:1 shift %+.3f W; endpoints exact"
      % ("PASS" if ok else "FAIL", hi["max_err"], r2["max_err"], r2["shift"], r8["max_err"],
         100 * r8["max_err"] / LIT, r8["shift"], r8["pshift"], r8["dark_lin"], r8["dark_srg"], r16["shift"]))
