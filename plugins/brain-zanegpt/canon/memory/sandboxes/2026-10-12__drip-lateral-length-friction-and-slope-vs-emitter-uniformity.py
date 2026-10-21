"""Gap sandbox for the drip kernel (regulate to 20-25 psi, 0.5-1.0 gph emitters at 12-18 in) plus brainwork E112 (60 psi lifts flow x1.55)
and E137 (4 gpm supply ceiling). Question: how long may the lateral be before end emitters
fall under 90% of the first emitter's flow, and does the kernel's regulator advice protect against it?
Prediction (before run): 1 gph @12 in, 1/2 in tube (0.6 in ID), 25 psi inlet, flat: 100 ft keeps end/first >=95%; 400 ft drops
below 90%; a 60 psi inlet gives first emitter x1.55 of the 25 psi flow but a SMALLER relative end drop; a 10 ft rise over 100 ft
at 25 psi drops the end emitter below 92%; 0.5 gph @18 in lasts much longer than 1 gph @12 in.
Model: emitter q=q0*sqrt(P/25) (non pressure compensating), Hazen-Williams C=150, ID 0.6 in, deterministic bisection."""
import math
C, D_IN = 150.0, 0.6
def hw(q_gph, length_ft):
    qg = q_gph / 60.0
    return 4.52 * qg ** 1.85 / (C ** 1.85 * D_IN ** 4.87) * length_ft   # psi per ft of length_ft already scaled below
def friction_psi(q_gph, seg_ft):
    return 4.52 * (q_gph / 60.0) ** 1.85 / (C ** 1.85 * D_IN ** 4.87) * seg_ft
def lateral(q0, spacing_in, length_ft, pin, rise_ft=0.0):
    n = int(length_ft * 12 / spacing_in); seg = spacing_in / 12.0
    def inlet_for(pend):
        p = pend; flows = []
        # sweep from the end to the inlet
        cum = 0.0; ps = [0.0] * n
        for i in range(n - 1, -1, -1):
            ps[i] = p
            qe = q0 * math.sqrt(max(p, 0.01) / 25.0); cum += qe
            p += friction_psi(cum, seg) + 0.433 * rise_ft / n     # head to supply next emitter upstream
        return p, ps
    lo, hi = 0.0, pin * 2
    for _ in range(80):
        mid = (lo + hi) / 2
        pi, _ = inlet_for(mid)
        if pi > pin: hi = mid
        else: lo = mid
    pi, ps = inlet_for(lo)
    flows = [q0 * math.sqrt(max(p, 0.01) / 25.0) for p in ps]
    return flows[0], flows[-1], sum(flows)
rows = {}
def show(tag, q0, sp, L, pin, rise=0.0):
    f0, fe, tot = lateral(q0, sp, L, pin, rise)
    rows[tag] = (f0, fe, fe / f0, tot)
    print(f"{tag:28s} first {f0:.3f} end {fe:.3f} gph  end/first {fe/f0*100:5.1f}%  total {tot:.0f} gph ({tot/60:.2f} gpm)")
show("1gph@12 25psi 100ft", 1.0, 12, 100, 25)
show("1gph@12 25psi 400ft", 1.0, 12, 400, 25)
show("1gph@12 60psi 100ft", 1.0, 12, 100, 60)
show("1gph@12 60psi 400ft", 1.0, 12, 400, 60)
show("1gph@12 25psi 100ft rise10", 1.0, 12, 100, 25, 10.0)
show("0.5gph@18 25psi 400ft", 0.5, 18, 400, 25)
a = rows["1gph@12 25psi 100ft"]; b = rows["1gph@12 25psi 400ft"]; c = rows["1gph@12 60psi 100ft"]; d = rows["1gph@12 60psi 400ft"]
e = rows["1gph@12 25psi 100ft rise10"]; f = rows["0.5gph@18 25psi 400ft"]
checks = {"100ft>=95": a[2] >= .95, "400ft<90": b[2] < .90, "60psi first x1.5-1.6": 1.5 <= c[0] / a[0] <= 1.6,
          "60psi relative drop smaller": d[2] > b[2], "rise<92": e[2] < .92, "half-gph@18 longer": f[2] > b[2]}
for k, v in checks.items(): print(("ok   " if v else "FAIL ") + k)
ratio = c[0] / a[0]
print("RESULT:", "PASS" if all(checks.values()) else "FAIL", f"end/first 100ft {a[2]*100:.1f}% 400ft {b[2]*100:.1f}% 60psi400ft {d[2]*100:.1f}% rise10 {e[2]*100:.1f}% half-gph400ft {f[2]*100:.1f}% flow60/25 {ratio:.2f}")
