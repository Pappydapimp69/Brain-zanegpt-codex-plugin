# Sandbox: fixed-weight pressure cooker (regulates GAUGE pressure) at altitude. Water saturation T from Antoine
# (mmHg, C): log10 P = 8.07131 - 1730.63/(T + 233.426). Ambient from the barometric formula. Cook time scales by
# 10^((121.1 - T)/z). z is the temperature rise that cuts the time 10x; it is an ASSUMED texture constant.
# Prediction (before first run): sea level 15 psi gauge gives 121 C (+-0.5); at 3000 m the cooker reaches 115-117 C;
# with z=33 the time penalty at 3000 m is 35-50%; the popular rule (+5% per 1000 ft above 2000 ft = +39% at 3000 m)
# is inside z=25..45 at 3000 m but stays inside +-10 points of the model at 1500 m only for z<=33.
from math import log10, exp
GAUGE_KPA = 103.4   # 15 psi weight
def ambient_kpa(h): return 101.325 * exp(-h / 8434.0)   # isothermal scale height
def t_sat(p_kpa):
    p = p_kpa * 7.50062  # mmHg
    return 1730.63 / (8.07131 - log10(p)) - 233.426
def cooker_t(h): return t_sat(ambient_kpa(h) + GAUGE_KPA)
def penalty(h, z): return 10 ** ((cooker_t(0) - cooker_t(h)) / z) - 1
def rule(h): return max(0.0, (h * 3.28084 - 2000) / 1000 * 0.05)
print("S1 sea level %.1f C; open pot boils at %.1f C" % (cooker_t(0), t_sat(ambient_kpa(0))))
for h in (1500, 3000, 4500):
    print("S2 %4d m: cooker %.1f C (open pot %.1f C); penalty z=20/33/45: %s; rule %.0f%%" % (
        h, cooker_t(h), t_sat(ambient_kpa(h)), [round(100*penalty(h, z)) for z in (20, 33, 45)], 100*rule(h)))
p3 = {z: penalty(3000, z) for z in (20, 25, 33, 45)}
in3 = [z for z in (25, 33, 45) if abs(p3[z] - rule(3000)) < 0.15]
d15 = {z: abs(penalty(1500, z) - rule(1500)) for z in (20, 33, 45)}
print("S3 (break) z swept: penalty at 3000 m %s; |model-rule| at 1500 m %s" % ({z: round(v, 2) for z, v in p3.items()}, {z: round(v, 2) for z, v in d15.items()}))
pred = abs(cooker_t(0) - 121) <= .5 and 115 <= cooker_t(3000) <= 117 and .35 <= p3[33] <= .50 and 25 in in3 and 45 in in3 and d15[33] <= .10 < d15[45]
print("original prediction held:", pred)
ok = abs(cooker_t(0) - 121) <= 1.0 and cooker_t(3000) < cooker_t(0) - 3 and p3[20] > p3[45] * 1.5
print("RESULT: %s cooker %.1f C at sea level, %.1f C at 3000 m; time penalty at 3000 m is %.0f%% (z=20), %.0f%% (z=33), %.0f%% (z=45) vs rule 39%%" % (
    "PASS" if ok else "FAIL", cooker_t(0), cooker_t(3000), 100*p3[20], 100*p3[33], 100*p3[45]))
