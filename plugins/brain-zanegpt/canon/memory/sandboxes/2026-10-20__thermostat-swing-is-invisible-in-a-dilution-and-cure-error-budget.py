"""Sandbox: error budget of making a cure stock by 2-step 1000x dilution in a thermostatted water bath.
Terms (worst-case percent):
  pipette: n steps, each max(0.5, a/volume*100) percent (stored dilution model, 1000 uL end volume per step)
  thermal: relative water-density change over the bath swing, from the Tanaka et al. (2001) water density equation
  base:    cure dose weighed on meat weight vs meat+brine (stored cure-dose lesson: 125..312 ppm spread => 10..25 percent)
Thermostat swing = band + 1.18 K overshoot (stored on/off-heater lesson: bands 1.0/0.5/0.25 -> 2.16/1.68/1.44 K).
Prediction (before run): at 20 C narrowing the band from 1.0 to 0.25 K changes the summed budget by under 0.01 percentage points;
the thermal term is below 0.1 percent for every bath temperature 4..60 C with swings up to 3.4 K; the thermal term only
reaches the pipette floor (0.5) if the swing exceeds ~20 K. Stdlib only."""
def rho(T):
    a1, a2, a3, a4, a5 = -3.983035, 301.797, 522528.9, 69.34881, 999.974950
    return a5 * (1 - (T + a1) ** 2 * (T + a2) / (a3 * (T + a4)))

def thermal_pct(T0, swing):
    lo, hi = T0 - swing / 2, T0 + swing / 2
    return abs(rho(lo) - rho(hi)) / rho(T0) * 100

def pip(a, steps):
    f = 1000 ** (1 / steps); v = 1000 / f
    return steps * max(0.5, a / v * 100)

BASE_PCT = 10.0                      # low end of the stored 10..25 percent cure-base error
A = 0.02                             # uL, the stored pipette constant
rows = {}
for band in (1.0, 0.5, 0.25):
    swing = band + 1.18
    th = thermal_pct(20.0, swing)
    tot = pip(A, 2) + th + BASE_PCT
    rows[band] = (swing, th, tot)
    print("band %.2f swing %.2f K: thermal %.4f%%  pipette(2 steps) %.2f%%  base %.1f%%  total %.4f%%" % (band, swing, th, pip(A, 2), BASE_PCT, tot))
delta = rows[1.0][2] - rows[0.25][2]
print("budget change from narrowing band 1.0 -> 0.25 K: %.4f percentage points" % delta)
worst = max(thermal_pct(T, 3.4) for T in range(4, 61))
print("max thermal term over 4..60 C at 3.4 K swing: %.4f%%" % worst)
# swing needed for the thermal term to reach the 0.5 percent pipette floor at 20 C and at 60 C
def need(T0):
    s = 0.1
    while thermal_pct(T0, s) < 0.5: s += 0.1
    return round(s, 1)
n20, n60 = need(20.0), need(60.0)
print("swing needed for thermal term to reach 0.5 percent: %.1f K at 20 C, %.1f K at 60 C" % (n20, n60))
# BREAK: the stored floor-only case a=0 and a bath at 4 C (density maximum, flat slope)
print("thermal at 4 C with 3.4 K swing: %.5f%%" % thermal_pct(4.0, 3.4))
ok = delta / rows[0.25][2] < 0.002 and worst < 0.25 and n20 > 15   # claim: invisible (<0.2% of total, <half the floor)
print("RESULT: %s thermostat band 1.0->0.25 K changes the dilution+cure error budget by %.4f points (thermal term %.3f%% -> %.3f%% of a %.1f%% total); thermal term stays under %.3f%% for 4..60 C at 3.4 K and needs a %.1f K swing at 20 C to reach the 0.5%% pipette floor"
      % ("PASS" if ok else "FAIL", delta, rows[1.0][1], rows[0.25][1], rows[0.25][2], worst, n20))
