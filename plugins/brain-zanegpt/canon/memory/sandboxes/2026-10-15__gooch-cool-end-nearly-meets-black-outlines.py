"""Cel loop 4 - Gooch et al. 1998 (A Non-Photorealistic Lighting Model for Automatic
Technical Illustration): kcool = kblue + alpha*kd, kwarm = kyellow + beta*kd, with
kblue = (0,0,b), kyellow = (y,y,0), tone = t*kwarm + (1-t)*kcool, t = (1 + l.n)/2,
shown with b = 0.4, y = 0.4, alpha = 0.2, beta = 0.6 so shading stays in the middle
luminance range and black edge lines and white highlights stay visible.
Test on four object colours (red, green, blue, grey): the WCAG contrast ratio between
the darkest shaded value and a black edge line (and between the brightest shaded value
and a white highlight) for Lambert (kd * max(0, l.n), plus 2-band cel of the same) vs
Gooch (smooth, and 2-band cel using its two end tones at t = 0.25 / 0.75).
PREDICTION (written before running): Lambert's darkest value gives contrast < 1.2 with a
black line for every colour (line invisible on the shadow side); Gooch's darkest gives
>= 2.0 for every colour; Gooch's brightest stays >= 1.3 below white for every colour."""
def lum(c):
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    c = [min(1, max(0, v)) for v in c]
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])
ratio = lambda a, b: (max(lum(a), lum(b)) + 0.05) / (min(lum(a), lum(b)) + 0.05)
BLACK, WHITE = (0.02, 0.02, 0.02), (1, 1, 1)
b, y, al, be = 0.4, 0.4, 0.2, 0.6
COL = {"red": (0.8, 0.1, 0.1), "green": (0.15, 0.6, 0.2), "blue": (0.15, 0.25, 0.8), "grey": (0.5, 0.5, 0.5)}
def gooch(kd, ln):
    kc = (al * kd[0], al * kd[1], b + al * kd[2]); kw = (y + be * kd[0], y + be * kd[1], be * kd[2])
    t = (1 + ln) / 2
    return tuple(t * w + (1 - t) * c for w, c in zip(kw, kc))
lam = lambda kd, ln: tuple(v * max(0.0, ln) for v in kd)
lns = [i / 50 - 1 for i in range(101)]          # l.n from -1 to 1
rows = {}
for name, kd in COL.items():
    L = [lam(kd, x) for x in lns]; G = [gooch(kd, x) for x in lns]
    Lcel = [lam(kd, 1.0) if x > 0 else lam(kd, 0.0) for x in lns]        # lit = full, shade = black-ish
    Gcel = [gooch(kd, 0.5) if x > 0 else gooch(kd, -0.5) for x in lns]
    dark = lambda S: min(S, key=lum); bright = lambda S: max(S, key=lum)
    rows[name] = {k: (ratio(dark(S), BLACK), ratio(bright(S), WHITE)) for k, S in
                  (("Lambert", L), ("Lambert cel", Lcel), ("Gooch", G), ("Gooch cel", Gcel))}
    print(f"{name:5s} " + "  ".join(f"{k}: vs black {v[0]:4.2f} vs white {v[1]:4.2f}" for k, v in rows[name].items()))
p1 = all(r["Lambert"][0] < 1.2 for r in rows.values())
p2 = all(r["Gooch"][0] >= 2.0 for r in rows.values())
p3 = all(r["Gooch"][1] >= 1.3 for r in rows.values())
worst_g = min(r["Gooch"][0] for r in rows.values()); worst_w = min(r["Gooch"][1] for r in rows.values())
print(f"RESULT: {'PASS' if p1 and p2 and p3 else 'FAIL'} Lambert darkest vs black line max {max(r['Lambert'][0] for r in rows.values()):.2f}; "
      f"Gooch darkest vs black min {worst_g:.2f}; Gooch brightest vs white min {worst_w:.2f}")
