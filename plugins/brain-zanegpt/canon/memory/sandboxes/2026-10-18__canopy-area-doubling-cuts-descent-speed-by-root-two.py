# Sandbox: parachute descent under quadratic drag, m=80 kg, Cd=1.5, rho=1.225, g=9.81, semi-implicit stepping dt=0.001 s.
# Analytic reference: vt = sqrt(2 m g / (rho Cd A)), v(t) = vt*tanh(g t / vt).
# Prediction (before first run): doubling canopy area 25 -> 50 -> 100 m2 scales steady descent speed by 1/sqrt(2) (ratio 1.414,
# within 0.5%), not by 1/2; simulated speed after 3 s is within 0.5% of vt. BREAK: a linear-drag model (F = k v, k matched at 50 m2
# area proportional) would predict ratio 2.0; the quadratic sim must NOT show 2.0.
import math
M, CD, RHO, G = 80.0, 1.5, 1.225, 9.81
def vt(a): return math.sqrt(2 * M * G / (RHO * CD * a))
def sim(a, t_end, dt=0.001):
    v = 0.0; n = int(round(t_end / dt))
    for _ in range(n):
        v += (G - 0.5 * RHO * CD * a * v * abs(v) / M) * dt
    return v
res = {a: sim(a, 3.0) for a in (25, 50, 100)}
for a, v in res.items():
    print("A=%3d m2 analytic vt=%.3f sim(3s)=%.3f err=%.3f%% analytic v(3s)=%.3f" % (a, vt(a), v, 100 * abs(v - vt(a)) / vt(a), vt(a) * math.tanh(G * 3 / vt(a))))
r1, r2 = res[25] / res[50], res[50] / res[100]
linear = 2.0
print("sim ratios 25/50=%.3f 50/100=%.3f; linear-drag model would give %.1f" % (r1, r2, linear))
ok = all(abs(r - math.sqrt(2)) / math.sqrt(2) < 0.005 for r in (r1, r2)) and all(abs(res[a] - vt(a)) / vt(a) < 0.005 for a in res)
print("RESULT: %s doubling canopy area cut sim descent speed by %.3f and %.3f (sqrt2=1.414), not the linear-drag 2.0" % ("PASS" if ok else "FAIL", r1, r2))
