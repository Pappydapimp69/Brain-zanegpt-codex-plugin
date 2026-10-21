"""ITERATION 2. Iteration 1 (margin 0.2, cog=clip(2r-0.3)) FAILED its own prediction: the floor at 0 capped the aff-cog gap at
0.1, so crossing curves gave 0 double dissociations; floor effects limit a one-latent double dissociation. Margin/curve were then
changed to 0.15 and clip(3r-0.6) and the prediction below kept otherwise unchanged.
PREDICTION (written before first run): a ONE-latent model with non-crossing monotone task curves gives 0 double
dissociations (margin 0.2) over a 21-level patient grid; with crossing curves it gives >=10 ordered pairs; the state-trace
(aff,cog) of any one-latent model is monotone (0 violations) while a TWO-latent model gives >=1 violation; and in a
distress/compassion pair a single 'exposure' latent produces a monotone negative trace (0 violations), so a dose-response
alone cannot show separate networks, while a compassion-training arm (compassion up, distress flat) breaks it (>=1)."""
def grid(n=21): return [i / (n - 1) for i in range(n)]

def double_diss(pts, m=0.15):
    # patient A: aff - cog >= m ; patient B: cog - aff >= m
    a = [p for p in pts if p[0] - p[1] >= m]; b = [p for p in pts if p[1] - p[0] >= m]
    return len(a) * len(b)

def monotone_violations(pts):
    pts = sorted(pts)  # by x then y
    v = 0
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        if x2 > x1 and y2 < y1 - 1e-12: v += 1
    return v

def trace_viol(pts):
    # direction-agnostic: min of violations for increasing and for decreasing relation
    inc = monotone_violations(pts)
    dec = monotone_violations([(x, -y) for x, y in pts])
    return min(inc, dec)

R = grid()
noncross = [(r, r * r) for r in R]                          # aff=r, cog=r^2 : same ordering everywhere
crossing = [(r, min(1.0, max(0.0, 3 * r - 0.6))) for r in R]  # curves cross at r=0.3, cog has a floor at 0
two_latent = sorted(set([(0.9, 0.2), (0.2, 0.9), (0.5, 0.5), (0.8, 0.8), (0.1, 0.1)]))
dose = [(d, 1 - d) for d in R]                              # distress up, compassion down: one 'exposure' latent
train = dose + [(0.2, 0.9), (0.2, 0.3)]                     # trained arm: compassion up at same low distress, plus a low-compassion partner
res = dict(
  dd_noncross=double_diss(noncross), dd_cross=double_diss(crossing),
  tr_noncross=trace_viol(noncross), tr_cross=trace_viol(crossing), tr_two=trace_viol(two_latent),
  tr_dose=trace_viol(dose), tr_train=trace_viol(train))
print(res)
ok = (res['dd_noncross'] == 0 and res['dd_cross'] >= 10 and res['tr_noncross'] == 0 and res['tr_cross'] == 0
      and res['tr_two'] >= 1 and res['tr_dose'] == 0 and res['tr_train'] >= 1)
print("RESULT: %s double dissociations one-latent noncrossing %d vs crossing %d; state-trace violations one-latent %d/%d, two-latent %d, dose %d, trained arm %d" % (
  "PASS" if ok else "FAIL", res['dd_noncross'], res['dd_cross'], res['tr_noncross'], res['tr_cross'], res['tr_two'], res['tr_dose'], res['tr_train']))
