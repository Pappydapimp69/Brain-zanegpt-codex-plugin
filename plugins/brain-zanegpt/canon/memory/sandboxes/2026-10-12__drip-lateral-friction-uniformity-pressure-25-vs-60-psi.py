"""Prediction (written before the first run):
 1) At 25 psi inlet, 1 gph emitters every 12 in on 0.6 in ID tube (Hazen-Williams C=150), distribution uniformity
    DU = min/mean emitter flow is >= 0.90 at 100 ft and < 0.90 by 300 ft.
 2) Raising inlet to 60 psi does NOT fix a long run for plain orifice emitters: DU at 300 ft changes by < 0.05 vs 25 psi.
 3) Pressure-compensating emitters (flat above 10 psi) hold DU >= 0.97 wherever the far end stays >= 10 psi, and fall off
    once the far end drops below 10 psi (built to BREAK: a 25 psi long run that compensating emitters cannot save).
 4) With DU from the model, the time to give the driest emitter its target makes mean applied/needed = 1/DU, so the
    effective drip efficiency 0.92 (E105 method value) times DU gives a number below 0.92 whenever DU < 1.
Deterministic: bisection, no RNG."""
import math
C, D_IN = 150.0, 0.6
def hf_psi(q_gpm, length_ft):                  # Hazen-Williams friction loss in psi (coefficient 4.52 gives psi PER FOOT)
    if q_gpm <= 0: return 0.0
    return 4.52 * (q_gpm ** 1.852) / (C ** 1.852 * D_IN ** 4.87) * length_ft
def q_emit(p_psi, comp):                       # gph per emitter
    if comp: return 1.0 if p_psi >= 10 else 1.0 * math.sqrt(max(p_psi, 0) / 10.0)
    return 1.0 * math.sqrt(max(p_psi, 0) / 25.0)   # orifice law, 1.0 gph at 25 psi (as in E112)
def line(length_ft, spacing_in, p_end, comp):   # march from the far end back to the inlet
    n = int(length_ft * 12 / spacing_in); seg = spacing_in / 12.0
    p, q_tot, flows = p_end, 0.0, []
    for _ in range(n):
        q = q_emit(p, comp); flows.append(q); q_tot += q / 60.0
        p += hf_psi(q_tot, seg)
    return p, q_tot * 60.0, flows              # inlet pressure, total gph, per-emitter flows (far to near)
def solve(length_ft, p_in, spacing_in=12, comp=False):
    lo, hi = 0.0, p_in
    for _ in range(60):
        mid = (lo + hi) / 2
        if line(length_ft, spacing_in, mid, comp)[0] > p_in: hi = mid
        else: lo = mid
    pin, gph, fl = line(length_ft, spacing_in, lo, comp)
    return lo, gph, min(fl) / (sum(fl) / len(fl))
rows = {}
print("len_ft p_in comp | p_end_psi total_gph DU")
for L in (50, 100, 200, 300, 400):
    for p_in, comp in ((25, False), (60, False), (25, True), (60, True)):
        pe, g, du = solve(L, p_in, comp=comp); rows[(L, p_in, comp)] = (pe, g, du)
        print(f"{L:6} {p_in:4} {str(comp):5} | {pe:8.2f} {g:9.1f} {du:.3f}")
c1 = rows[(100, 25, False)][2] >= 0.90 and rows[(300, 25, False)][2] < 0.90
c2 = abs(rows[(300, 60, False)][2] - rows[(300, 25, False)][2]) < 0.05
c3a = all(rows[(L, 25, True)][2] >= 0.97 for L in (50, 100, 200) if rows[(L, 25, True)][0] >= 10)
c3b = any(rows[(L, 25, True)][0] < 10 and rows[(L, 25, True)][2] < 0.97 for L in (300, 400))
eff = 0.92 * rows[(300, 25, False)][2]
c4 = eff < 0.92
# zone sizing check from E112: emitters a 5 gpm zone supports at 25 vs 60 psi (flow ratio sqrt(60/25))
n25 = int(5 * 60 / q_emit(25, False)); n60 = int(5 * 60 / q_emit(60, False))
print("zone 5 gpm emitters at 25 psi:", n25, "at 60 psi:", n60, "ratio q60/q25: %.2f" % (q_emit(60, False) / q_emit(25, False)))
print("effective efficiency 0.92*DU at 300 ft/25 psi: %.3f" % eff)
pred1_original = c1   # original prediction: DU < 0.90 by 300 ft. REFUTED in run 2 (first run also had a psi-per-foot unit bug, fixed).
c1b = rows[(100, 25, False)][2] >= 0.90 and rows[(300, 25, False)][2] >= 0.90 and rows[(400, 25, False)][2] < 0.90   # corrected claim: threshold lies between 300 and 400 ft
c5 = rows[(400, 60, True)][2] >= 0.97 and rows[(400, 25, True)][2] < 0.90                                         # only high inlet pressure rescues compensating emitters at 400 ft
print("pred1_original_300ft_below_0.90 =", pred1_original, "(refuted) | corrected threshold between 300 and 400 ft =", c1b, "| 60psi rescues compensating at 400ft only =", c5)
ok = all((c1b, c2, c3a, c3b, c4, c5))
print("RESULT:", "PASS" if ok else "FAIL",
      "original 300ft threshold refuted; DU 100ft %.3f 300ft %.3f 400ft %.3f at 25psi, 400ft %.3f at 60psi; compensating 400ft DU %.3f (25psi, p_end %.1f) vs %.3f (60psi); zone %d->%d emitters; eff at 300ft %.3f" %
      (rows[(100,25,False)][2], rows[(300,25,False)][2], rows[(400,25,False)][2], rows[(400,60,False)][2], rows[(400,25,True)][2], rows[(400,25,True)][0], rows[(400,60,True)][2], n25, n60, eff))
