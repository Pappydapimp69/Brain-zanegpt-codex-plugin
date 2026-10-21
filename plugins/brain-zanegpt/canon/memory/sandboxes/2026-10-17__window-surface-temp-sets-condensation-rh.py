# Sandbox: indoor RH ceiling before a window pane condenses.
# Magnus dew point (Alduchov & Eskridge 1996: a=17.625, b=243.04 C); inner surface temp from
# U-value and ISO 6946 internal surface resistance Rsi=0.13 m2K/W: Ts = Ti - U*Rsi*(Ti-To).
from math import log, exp
A, B = 17.625, 243.04
def dew(t, rh):
    g = log(rh / 100) + A * t / (B + t)
    return B * g / (A - g)
def rh_at_dew(t, td):
    return 100 * exp(A * td / (B + td) - A * t / (B + t))
def surf(ti, to, u, rsi=0.13): return ti - u * rsi * (ti - to)
d = dew(20, 50)
print("dew point 20C/50%%: %.2f C (reference 9.3 C)" % d)
ceil = {}
for name, u in (("single", 5.8), ("double", 2.8), ("triple", 0.8)):
    ts = surf(20, 0, u)
    ceil[name] = rh_at_dew(20, ts)
    print("%s U=%.1f Ts=%.1f C condenses above RH %.0f%% (at 20C in, 0C out)" % (name, u, ts, ceil[name]))
# colder outside lowers every ceiling: sweep and check monotonic
sweep = [rh_at_dew(20, surf(20, to, 2.8)) for to in (10, 5, 0, -5, -10)]
mono = all(a > b for a, b in zip(sweep, sweep[1:]))
print("double-glazed ceilings at outside 10,5,0,-5,-10C:", [round(x) for x in sweep])
# round trip: at the ceiling RH the dew point equals the surface temperature
rt = abs(dew(20, ceil["double"]) - surf(20, 0, 2.8)) < 1e-9
# BREAK: a cold-bridge corner at U_eff 6 on double glazing is worse than the single pane centre
corner = rh_at_dew(20, surf(20, 0, 6.0))
ok = (abs(d - 9.3) < 0.1 and 35 <= ceil["single"] <= 40 and 60 <= ceil["double"] <= 66 and mono and rt
      and corner < ceil["double"] and ceil["triple"] > 85)
print("RESULT: %s dew 20C/50%% = %.1f C; condensation RH ceiling single %.0f%% double %.0f%% triple %.0f%% at 0C outside; cold corner U=6 drops double to %.0f%%" % ("PASS" if ok else "FAIL", d, ceil["single"], ceil["double"], ceil["triple"], corner))
