"""Caffeine cutoff sandbox (deterministic, stdlib only, no RNG, no timing).

CLAIM UNDER TEST: "no coffee after 2pm" is a hidden claim about half-life and
dose. Across the cited adult half-life range the same clock cutoff leaves very
different residuals, and an hours-before-bed rule is dose-blind. A usable rule
is a residual target: cutoff = bedtime - half_life * log2(dose / target).

PREDICTION (written BEFORE the first run):
  S1 100 mg at 14:00, bed 23:00 (9 h), absorption half-life 0.25 h assumed:
     residual about 9.2 / 30.2 / 55.0 mg for half-life 2.5 / 5 / 10 h
     (ratio about 6.0, +-0.4).
  S2 half-life 5 h: 100 mg at 6 h before bed leaves LESS (about 45 mg) than
     400 mg at 12 h before bed (about 80 mg); matching 400 mg to it needs about
     16 h of lead.
  S3 target 25 mg left, 200 mg dose, bed 22:30 (wake 06:30 + 8 h): numeric
     cutoff within 0.5 h of the closed form; a 14:00 cutoff passes only when
     half-life <= about 2.8 h.
  S4 forward Euler at 1 h step on the 5 h half-life under-predicts the 9 h
     residual by about 9 %; a per-step factor of 0.8706 applied at 15-minute
     steps leaves about 0.7 % instead of about 29 %.
  S5 BREAK (two parts): (a) repeated 3 x 100 mg daily, wake-up carryover for
     half-life 10 is more than 2x that for half-life 5 and matches closed form
     within 1 %; (b) with saturable (Michaelis-Menten) elimination, ILLUSTRATIVE
     parameters tuned to a 5 h low-dose half-life, the residual FRACTION is
     dose-independent within 2 % up to 400 mg but not at 2000 mg.
"""
import math

KA = math.log(2) / 0.25   # absorption rate: ASSUMED 15 min absorption half-life


def ke_of(th):
    return math.log(2) / th


def body(dose, t, th, ka=KA):
    """Amount in body (mg) t hours after one oral dose, first-order in and out."""
    if t < 0:
        return 0.0
    ke = ke_of(th)
    return dose * ka / (ka - ke) * (math.exp(-ke * t) - math.exp(-ka * t))


def hhmm(h):
    h = h % 24
    return "%02d:%02d" % (int(h), int(round((h - int(h)) * 60)) % 60)


results = []

# ---------------- S1 same clock cutoff, three half-lives ----------------
print("S1 100 mg at 14:00, bed 23:00 (9 h)")
res = {}
for th in (2.5, 5.0, 10.0):
    res[th] = body(100, 9, th)
    print("  half-life %4.1f h -> %5.1f mg left" % (th, res[th]))
ratio = res[10.0] / res[2.5]
print("  ratio slow/fast = %.2f" % ratio)
s1 = abs(res[2.5] - 9.2) < 1 and abs(res[5.0] - 30.2) < 1.5 and abs(ratio - 6.0) < 0.4
results.append(("S1", s1))

# ---------------- S2 hours-before-bed rule is dose blind ----------------
print("S2 half-life 5 h, residual by dose and lead time")
th = 5.0
a = body(100, 6, th)
b = body(400, 12, th)
print("  100 mg @6 h: %.1f mg   400 mg @12 h: %.1f mg" % (a, b))
for lead in (0, 3, 6):
    print("  400 mg @%d h before bed: %.1f mg" % (lead, body(400, lead, th)))
lead = 24.0
while body(400, lead, th) < a:   # walk down from a long lead (absorption makes body()=0 at lead 0)
    lead -= 0.05
print("  400 mg needs %.1f h of lead to match 100 mg @6 h" % lead)
s2 = a < b and 15 <= lead <= 17 and 40 <= a <= 50 and 75 <= b <= 85
results.append(("S2", s2))

# ---------------- S3 residual-target cutoff ----------------
print("S3 target 25 mg left, dose 200 mg, wake 06:30 + 8 h sleep -> bed 22:30")
bed = 22.5
target, dose = 25.0, 200.0


def numeric_gap(th):
    lo, hi = 0.0, 200.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if body(dose, mid, th) > target:
            lo = mid
        else:
            hi = mid
    return hi


s3 = True
pass14 = []
for th in (2.5, 5.0, 10.0):
    closed = th * math.log2(dose / target)
    num = numeric_gap(th)
    cut_num = bed - num
    ok14 = body(dose, bed - 14.0, th) <= target
    pass14.append(ok14)
    print("  half-life %4.1f h: closed %.1f h before bed, numeric %.2f h -> cutoff %s%s; 14:00 passes: %s"
          % (th, closed, num, hhmm(cut_num), " (previous day)" if cut_num < 0 else "", ok14))
    s3 = s3 and abs(num - closed) < 0.5
edge = max(x / 10 for x in range(10, 120) if body(dose, bed - 14.0, x / 10) <= target)
print("  largest half-life that passes a 14:00 cutoff = %.1f h" % edge)
s3 = s3 and pass14 == [True, False, False] and 2.5 <= edge <= 3.0
results.append(("S3", s3))

# ---------------- S4 step-size trap ----------------
print("S4 simulating decay with steps")
exact = 100 * 2 ** (-9 / 5.0)
k = ke_of(5.0)
e1 = 100 * (1 - k * 1.0) ** 9
print("  exact (no absorption) 9 h residual %.2f mg; Euler dt=1 h %.2f mg (%.1f%%)" % (exact, e1, 100 * (e1 / exact - 1)))
f = 2 ** (-1 / 5.0)
n = int(9 / 0.25)
fixed = 100 * f ** n
eff_th = 0.25 * math.log(2) / -math.log(f)
print("  fixed per-step factor %.4f at 15 min steps: %.2f mg left, effective half-life %.2f h" % (f, fixed, eff_th))
e_fine = 100 * (1 - k * 0.01) ** 900
print("  Euler dt=0.01 h: %.2f mg (%.2f%%)" % (e_fine, 100 * (e_fine / exact - 1)))
s4 = abs(100 * (e1 / exact - 1) + 9) < 1.0 and fixed < 1.0 and abs(eff_th - 1.25) < 0.01 and abs(e_fine / exact - 1) < 0.01
results.append(("S4", s4))

# ---------------- S5a repeated daily dosing, wake-up carryover ----------------
print("S5a 3 x 100 mg at 08:00/12:00/16:00 daily, 14 days, residual at 06:30 on day 15")
carry = {}
ok5a = True
for th in (5.0, 10.0):
    times = [d * 24 + h for d in range(14) for h in (8, 12, 16)]
    t_end = 14 * 24 + 6.5
    sim = sum(body(100, t_end - t, th) for t in times)
    # closed form: sum of geometric series over days, per-dose body() at day-15 offsets
    cf = sum(body(100, 14 * 24 + 6.5 - (d * 24 + h), th) for d in range(14) for h in (8, 12, 16))
    carry[th] = sim
    print("  half-life %4.1f h: %.1f mg at wake-up (recomputed %.1f)" % (th, sim, cf))
    ok5a = ok5a and abs(sim - cf) / cf < 0.01
print("  carryover ratio slow/typical = %.2f" % (carry[10.0] / carry[5.0]))
ok5a = ok5a and carry[10.0] / carry[5.0] > 2.0
results.append(("S5a", ok5a))

# ---------------- S5b BREAK: saturable elimination (ILLUSTRATIVE parameters) ----------------
print("S5b saturable elimination, illustrative Km=1000 mg, low-dose half-life 5 h")
KM = 1000.0
VMAX = ke_of(5.0) * KM


def mm_fraction(d0, km=None, hours=9.0, dt=0.002):
    km = KM if km is None else km
    vmax = ke_of(5.0) * km
    a = d0
    for _ in range(int(hours / dt)):
        a -= vmax * a / (km + a) * dt
    return a / d0


fr = {d: mm_fraction(d) for d in (100, 400, 2000, 9000)}
lin = 2 ** (-9 / 5.0)
for d, v in fr.items():
    print("  dose %5d mg: residual fraction %.3f (linear model %.3f)" % (d, v, lin))
dev400 = {}
for km in (1000.0, 10000.0, 100000.0):
    dev400[km] = mm_fraction(400, km) / mm_fraction(100, km) - 1
    print("  Km %8.0f mg: 400 mg fraction is %.1f%% above the 100 mg fraction" % (km, 100 * dev400[km]))
print("  (prediction b said <2%% at 400 mg with Km=1000: it is %.0f%%, so the dietary-range linearity depends on an unmeasured Km)" % (100 * dev400[1000.0]))
s5b = ((fr[2000] - fr[100]) / fr[100] > 0.1 and dev400[1000.0] > dev400[10000.0] > dev400[100000.0]
       and dev400[100000.0] < 0.02)
results.append(("S5b", s5b))

ok = all(v for _, v in results)
print("scenarios:", ", ".join("%s=%s" % (n, "ok" if v else "FAIL") for n, v in results))
print("RESULT: %s caffeine cutoff as residual target: 9 h residual spans %.1fx across half-life 2.5-10 h, hours-before-bed rule dose-blind (400 mg@12 h %.0f mg > 100 mg@6 h %.0f mg), 14:00 cutoff passes only half-life <= %.1f h, linear scaling breaks at 2000 mg (fraction %.2f vs %.2f at 100 mg)"
      % ("PASS" if ok else "FAIL", ratio, b, a, edge, fr[2000], fr[100]))
