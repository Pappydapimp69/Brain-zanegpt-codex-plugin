# Domain: bread baking formulas (baker's percentages). Real scenario: a country loaf written as
# "75% hydration" with the levain kept separate.
# Prediction (before run): total hydration = (1-p)*Hd + p*Hl where p is the pre-fermented flour share of
# total flour, Hd the dough-only hydration, Hl the levain hydration. With Hd=0.75:
#   Hl=1.00: p=0.10 -> 77.5%, p=0.20 -> 80.0%, p=0.30 -> 82.5%
#   BREAK stiff levain Hl=0.50: p=0.20 -> 70.0% (the error flips sign).
# Fix check: to hit total 75% with p=0.20, Hl=1.0 the dough water must be Hd=0.6875.
def total_h(p, hd, hl): return (1 - p) * hd + p * hl
def hd_for(target, p, hl): return (target - p * hl) / (1 - p)
FLOUR = 1000.0
def grams(p, hd, hl):
    ff = FLOUR * p; fd = FLOUR - ff
    return fd * hd + ff * hl   # total water
obs = {}
for hl in (1.0, 0.5):
    for p in (0.10, 0.20, 0.30):
        t = total_h(p, 0.75, hl); w = grams(p, 0.75, hl)
        assert abs(w / FLOUR - t) < 1e-12
        obs[(hl, p)] = round(t * 100, 1); print("levain H", hl, "p", p, "total hydration %", obs[(hl, p)], "water g", round(w))
hd = hd_for(0.75, 0.20, 1.0); print("dough hydration needed for 75% total, p=.2, Hl=1:", round(hd, 4),
      "check total", round(total_h(0.20, hd, 1.0), 4))
ok = (obs[(1.0, .1)], obs[(1.0, .2)], obs[(1.0, .3)], obs[(0.5, .2)]) == (77.5, 80.0, 82.5, 70.0) and abs(hd - 0.6875) < 1e-9
print("RESULT:", "PASS" if ok else "FAIL", f"total hydration {obs[(1.0,.1)]}/{obs[(1.0,.2)]}/{obs[(1.0,.3)]}% for 10/20/30% 100%-levain, stiff levain {obs[(0.5,.2)]}%, needed dough hydration {hd:.4f}")
