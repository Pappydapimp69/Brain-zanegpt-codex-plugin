# Sandbox: wrong percentage base vs tighter thermostat band vs hidden water in a hydration base.
# Prediction (before first run): wrong cure base moves dose 25-60%; band 1.0->0.25 K moves
# cure-time error <6% (base error >=5x larger); hidden starter water moves hydration >3% in BOTH starter cases.
MEAT, BRINE = 1000.0, 250.0
def nitrite_ppm(pct, base): return pct/100*base*0.0625/MEAT*1e6   # 6.25% nitrite in cure salt
tgt = nitrite_ppm(0.25, MEAT)
bases = {"meat": MEAT, "meat+brine": MEAT+BRINE, "trimmed meat 800": 800.0}
errs = {k: abs(nitrite_ppm(0.25, v)-tgt)/tgt for k, v in bases.items()}
print("S1 cure base ppm", {k: round(nitrite_ppm(0.25, v), 1) for k, v in bases.items()})
def swing(band): return band + 1.18            # lag overshoot floor ~1.18 K (companion lesson)
def time_err(band): return 2**(swing(band)/2/10) - 1   # Q10=2, mean temp error = swing/2
t = {b: time_err(b) for b in (1.0, 0.5, 0.25)}
gain = t[1.0] - t[0.25]
print("S2 cure-time err by band", {b: round(v, 4) for b, v in t.items()}, "gain", round(gain, 4))
def hyd(starter_g, starter_hyd, flour=500.0, water=300.0):
    sf = starter_g/(1+starter_hyd); sw = starter_g-sf
    return (water+sw)/(flour+sf)
naive = 300/500
h100, h50 = hyd(100, 1.0), hyd(100, 0.5)
e100, e50 = abs(h100-naive)/naive, abs(h50-naive)/naive
print("S3 100%% starter hydration true %.3f naive %.3f err %.1f%%" % (h100, naive, e100*100))
print("S4 (break) 50%% starter hydration true %.3f err %.1f%%" % (h50, e50*100))
base_err = max(errs.values())
pred_ok = 0.25 <= base_err <= 0.6 and gain < 0.06 and base_err >= 5*gain and e100 > 0.03 and e50 > 0.03
narrow_ok = base_err >= 5*gain and e100 > 0.03 and e50 < e100
print("prediction fully held:", pred_ok)
print("RESULT: %s base err %.0f%% vs band gain %.1f%% (%.1fx); hidden water err %.1f%% (100%% starter) but only %.1f%% (50%% starter)" % (
    "PASS" if narrow_ok else "FAIL", base_err*100, gain*100, base_err/gain, e100*100, e50*100))
