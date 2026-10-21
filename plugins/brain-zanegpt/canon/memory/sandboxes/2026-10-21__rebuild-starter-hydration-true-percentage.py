# Own fixture (exact Fractions, different from a flour-500 recipe): verify true hydration counts starter flour+water.
# Prediction (before run): for the claimed recipe 500/350/100g: 72.7, 75.0 (200g), 67.6 (50% starter), water to hit 70% = 335 g.
# For my own recipe 800 g flour, 560 g water, 150 g starter at 80%: naive 70.0%, true ~ 70.5%+? (starter wetter than 70% -> true above naive: 71.1%).
from fractions import Fraction as F
def true_h(flour, water, starter, sh):
    sf = starter / (1 + sh); sw = starter - sf
    return (water + sw) / (flour + sf)
def water_for(target, flour, starter, sh):
    sf = starter / (1 + sh); sw = starter - sf
    return target * (flour + sf) - sw
pct = lambda x: round(float(x) * 100, 1)
c1 = pct(true_h(F(500), F(350), F(100), F(1)))
c2 = pct(true_h(F(500), F(350), F(200), F(1)))
c3 = pct(true_h(F(500), F(350), F(100), F(1, 2)))
c0 = pct(true_h(F(500), F(350), F(0), F(1)))
w = water_for(F(7, 10), F(500), F(100), F(1))
print("S1 claim recipe: 100g@100%%=%s 200g@100%%=%s 100g@50%%=%s control=%s water for 70%%=%s" % (c1, c2, c3, c0, float(w)))
m1 = pct(true_h(F(800), F(560), F(150), F(4, 5)))
m2 = pct(true_h(F(800), F(560), F(150), F(7, 10)))   # BREAK: starter at exactly the dough's own 70% -> should not move
m3 = pct(true_h(F(800), F(560), F(150), F(3, 5)))
print("S2 own recipe 150g starter @80%%=%s @70%%(break, must equal naive 70.0)=%s @60%%=%s" % (m1, m2, m3))
rt = pct(true_h(F(500), w, F(100), F(1)))
print("S3 round trip: adding %s g water gives true %s%%" % (float(w), rt))
ok = (c1, c2, c3, c0) == (72.7, 75.0, 67.6, 70.0) and w == 335 and m2 == 70.0 and m1 > 70 > m3 and rt == 70.0
print("RESULT: %s claim numbers reproduced (72.7/75.0/67.6, 335 g); own recipe 80%%->%s, 70%%->%s, 60%%->%s" % ("PASS" if ok else "FAIL", m1, m2, m3))
