# Deterministic sandbox: (A) fennel allelopathy radius vs bed layout, (B) marigold dose by coverage (E104-style),
# (C) claim grader ranking by independent trial roots, not page count (E130-style).
# Tomato slots: 8 plants, 1 ft apart along y=1.
# Prediction (before run): fennel at 3 ft radius clears a 4x8 bed placed 4 ft away but 10 ft radius hits all 8 tomato slots;
# marigold interplant at 10% coverage leaves >50% of nematodes vs <5% at 95%; grader puts basil (12 pages, 0 trials) last
# and a grader sorting by pages puts it first. Assumed constants: linear distance falloff, nematode_rel=exp(-3.2*cov^1.0 ... see code).
import math
def inhibited(d, R): return max(0.0, 1.0 - d / R)
slots = [(x + 0.5, 1.0) for x in range(8)]
def hit(fx, fy, R): return sum(1 for (x, y) in slots if inhibited(math.hypot(x - fx, y - fy), R) > 0)
# fennel placed 4 ft off the bed's long edge, centered
f = (4.0, -4.0 - 1.0)  # bed spans y 0..2; slot row at y=1 -> distance ~5 to 6.4 ft from fennel
res = {R: hit(*f, R) for R in (3, 5, 10)}
print("fennel hits by radius", res)
# separation needed so 10 ft radius hits nothing: farthest-first
need = next(s for s in range(0, 40) if hit(4.0, 1.0 - s, 10) == 0)
print("separation to clear 10ft radius", need, "ft from slot row")
def nem_rel(cov): return math.exp(-5.0 * cov ** 1.2) if cov > 0 else 1.0
n10, n95 = nem_rel(0.10), nem_rel(0.95)
print("marigold nematode fraction 10%%=%.2f 95%%=%.4f" % (n10, n95))
claims = [("basil-hornworm", 12, 0), ("marigold-nematode", 3, 2), ("allium-aphid", 4, 2), ("fennel-allelopathy", 3, 2), ("marigold-aphid", 6, 0)]
by_pages = [c[0] for c in sorted(claims, key=lambda c: -c[1])]
by_roots = [c[0] for c in sorted(claims, key=lambda c: (-c[2], -c[1]))]
print("by pages first:", by_pages[0], "| by roots last two:", by_roots[-2:])
ok = (res[3] == 0 and res[10] == 8 and need >= 9 and n10 > 0.5 and n95 < 0.05
      and by_pages[0] == "basil-hornworm" and set(by_roots[-2:]) == {"marigold-aphid", "basil-hornworm"})
print("RESULT: %s fennel hits R3/5/10=%s clear-distance=%dft marigold 10%%=%.2f 95%%=%.4f basil page-rank 1st, root-rank %d/5" % ("PASS" if ok else "FAIL", list(res.values()), need, n10, n95, by_roots.index("basil-hornworm") + 1))
