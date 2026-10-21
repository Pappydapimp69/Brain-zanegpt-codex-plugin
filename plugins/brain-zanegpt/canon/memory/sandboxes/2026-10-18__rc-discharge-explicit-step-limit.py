# Sandbox: RC capacitor discharge dV/dt = -V/(R*C), V(0)=1, simulated over 10 time constants.
# Real source: closed form V(t)=exp(-t/tau); exact checkpoints 36.8% at 1 tau, 0.67% at 5 tau.
# Run 1 prediction (partly missed: h=2.5 is only 4 steps in 10 tau so growth is 1.5^4=5.06 not 1e3, and implicit ends 6.7e-3 not <1e-3): explicit Euler multiplies V by (1-h) per step, h=dt/tau.
#   h=0.1 decays monotonically; h=1.0 reaches 0 in one step (wrong, exact is 0.368);
#   h=2.0 never decays (|V| stays 1.0, sign flips); h=2.5 grows past 1.0 (>=1e3 within 10 tau).
#   BREAK: backward Euler (divide by 1+h) stays stable and positive at h=2.5, so the limit is the method, not the circuit.
# Run 2 prediction (after run 1): h=2.5 max|V| = 1.5^4 = 5.06 (>1); implicit h=2.5 ends (1/3.5)^4 = 6.7e-3, positive and <1.
import math
def sim(h, method):
    n = int(round(10 / h)); v = 1.0; mx = 1.0
    for _ in range(n):
        v = v * (1 - h) if method == "explicit" else v / (1 + h)
        mx = max(mx, abs(v))
    return v, mx
cases = [("explicit", 0.1), ("explicit", 1.0), ("explicit", 2.0), ("explicit", 2.5), ("implicit (BREAK)", 2.5)]
r = {}
for m, h in cases:
    v, mx = sim(h, "explicit" if m == "explicit" else "implicit"); r[(m, h)] = (v, mx)
    print("%s h=%.1f final=%.3e max|V|=%.3e (exact final %.3e)" % (m, h, v, mx, math.exp(-10)))
ok = (r[("explicit", 0.1)][1] == 1.0 and abs(r[("explicit", 0.1)][0]) < 0.01
      and abs(r[("explicit", 1.0)][0]) < 1e-12
      and abs(r[("explicit", 2.0)][1] - 1.0) < 1e-9 and abs(r[("explicit", 2.0)][0]) > 0.99
      and abs(r[("explicit", 2.5)][1] - 5.0625) < 1e-3
      and abs(r[("implicit (BREAK)", 2.5)][0] - (1/3.5)**4) < 1e-9)
print("RESULT: %s explicit Euler stable only for dt<2*RC: h=2.0 holds |V|=1, h=2.5 reaches %.2e; implicit at h=2.5 ends %.1e"
      % ("PASS" if ok else "FAIL", r[("explicit", 2.5)][1], r[("implicit (BREAK)", 2.5)][0]))
