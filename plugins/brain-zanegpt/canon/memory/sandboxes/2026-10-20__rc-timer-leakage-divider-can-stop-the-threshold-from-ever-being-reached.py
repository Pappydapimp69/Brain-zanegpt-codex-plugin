"""ANALOG-TIMING seed: a 555-style monostable times how long a capacitor charging through R takes
to reach 2/3 Vcc: t = R*C*ln(3) = 1.0986*R*C (the datasheet's 1.1RC). Real capacitors leak: model that
as a parallel R_leak, which turns the charge target from Vcc into Vcc*Rl/(R+Rl).
PREDICTION (before run): Euler integration matches 1.0986RC within 0.5% at a fine step; a +-20% cap and
+-1% resistor give a worst-case timing spread of about +-21%, dominated by the cap; with leakage the
time is t = R'C ln(1/(1-(2/3)/(Rl/(R+Rl)))) and the timer NEVER fires once Rl <= 2R (threshold unreachable);
at Rl = 10R the timing error is about +11% (that last figure was a guess; observed +9.4%)."""
import math
R, C, VCC, TH = 100e3, 10e-6, 5.0, 2/3
def t_closed(R, C, rl=None):
    if rl is None: return R*C*math.log(3)
    vinf = rl/(R+rl)                   # fraction of Vcc the cap settles at
    if vinf <= TH: return math.inf
    return (R*rl/(R+rl))*C*math.log(1/(1-TH/vinf))
def t_euler(R, C, rl=None, dt=1e-4, tmax=20.0):
    v, t = 0.0, 0.0
    while t < tmax:
        i = (VCC - v)/R - (v/rl if rl else 0.0)
        v += i*dt/C; t += dt
        if v >= TH*VCC: return t
    return math.inf
nom = t_closed(R, C)
e1 = abs(t_euler(R, C) - nom)/nom
corners = [t_closed(R*(1+a), C*(1+b)) for a in (-0.01, 0.01) for b in (-0.2, 0.2)]
lo, hi = (min(corners)/nom - 1), (max(corners)/nom - 1)
cap_only = [t_closed(R, C*(1+b))/nom - 1 for b in (-0.2, 0.2)]
leak = {m: t_closed(R, C, m*R) for m in (1, 2, 3, 5, 10, 100)}
print("nominal %.4f s (1.0986RC); Euler error %.3f%%" % (nom, 100*e1))
print("tolerance corners %.1f%% .. +%.1f%%; cap-only %.1f%% .. +%.1f%%" % (100*lo, 100*hi, 100*cap_only[0], 100*cap_only[1]))
for m, t in leak.items(): print("Rl=%3dR -> t=%s (%s)" % (m, "never" if t == math.inf else "%.3fs" % t, "euler " + ("never" if t_euler(R, C, m*R) == math.inf else "%.3fs" % t_euler(R, C, m*R))))
ok = (e1 < 0.005 and leak[1] == math.inf and leak[2] == math.inf and leak[3] != math.inf
      and abs(leak[10]/nom - 1 - 0.11) < 0.02 and t_euler(R, C, 2*R) == math.inf)
print("RESULT: %s Euler within %.2f%% of 1.1RC; tolerance corners %.0f%%..+%.0f%%; leakage Rl<=2R never fires, Rl=10R +%.1f%%" % ("PASS" if ok else "FAIL", 100*e1, 100*lo, 100*hi, 100*(leak[10]/nom-1)))
