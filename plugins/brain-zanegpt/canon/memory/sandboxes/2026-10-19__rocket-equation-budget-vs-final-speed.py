# Sandbox: Tsiolkovsky delta-v = ve*ln(m0/mf) as a budget; numerical burn vs closed form; staging; gravity loss on a vertical burn.
import math
ve = 4500.0; g = 9.81
# 1) propellant fraction for delta-v 9700 m/s (Wikipedia worked example: 88.4%)
frac = 1 - math.exp(-9700 / ve)
print("propellant fraction for 9700 m/s: %.3f" % frac)
# 2) numeric burn (explicit steps, no gravity) vs closed form
def burn(m0, mf, mdot, gravity, dt=0.001):
    v = 0.0; m = m0; t = 0.0
    while m > mf + 1e-12:
        dm = min(mdot * dt, m - mf)
        a = ve * (dm / dt) / m - (g if gravity else 0.0)
        v += a * dt; m -= dm; t += dt
    return v, t
m0, mf = 10.0, 2.0
closed = ve * math.log(m0 / mf)
for mdot in (0.4, 0.8, 1.6):                       # burn times 20, 10, 5 s (mass units per second)
    v0, t = burn(m0, mf, mdot, False)
    v1, _ = burn(m0, mf, mdot, True)
    print("mdot %.1f burn %.1f s: no-gravity v %.1f (closed %.1f) | with gravity %.1f (loss %.1f = g*t %.1f)" % (mdot, t, v0, closed, v1, v0 - v1, g * t))
v_slow, t_slow = burn(m0, mf, 0.4, True); v_fast, t_fast = burn(m0, mf, 1.6, True)
# 3) staging: wikipedia example mass fractions 80% fuel, 10% dry, 10% rest -> ve*ln5 ; three stages 3x
one = ve * math.log(1 / (1 - 0.8)); print("example stage dv/ve = %.2f; three stages %.2f" % (one / ve, 3 * one / ve))
# single stage with the same total propellant fraction 0.8**? : one stage carrying all propellant of three stages' sum?
single = ve * math.log(1 / (1 - 0.8))   # one stage at 80% propellant fraction
print("single stage at 80%% propellant: dv/ve = %.2f vs three-stage %.2f" % (single / ve, 3 * one / ve))
nog_ok = abs(burn(m0, mf, 0.8, False)[0] - closed) < 5
ok = abs(frac - 0.884) < 0.001 and nog_ok and v_fast > v_slow and abs((closed - v_slow) - g * t_slow) < 10 and abs(3 * one / ve - 4.83) < 0.01
print("RESULT: %s numeric burn matches the equation (%.0f m/s) with error under 5 m/s, 88.4%% propellant for 9700 m/s, three stages give %.2f ve; a vertical burn loses g*t (%.0f m/s over %.0f s vs %.0f m/s over %.0f s) so delta-v is a budget, not a final speed"
      % ("PASS" if ok else "FAIL", closed, 3 * one / ve, closed - v_slow, t_slow, closed - v_fast, t_fast))
