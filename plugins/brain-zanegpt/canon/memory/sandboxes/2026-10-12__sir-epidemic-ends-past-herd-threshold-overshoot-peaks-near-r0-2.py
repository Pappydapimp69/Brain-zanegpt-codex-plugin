"""Sandbox: does an SIR epidemic stop at the herd-immunity threshold 1-1/R0?

Claim under test: HIT = 1 - 1/R0 is where prevalence PEAKS (S = 1/R0), not where
the epidemic ends. Final size z solves z = 1 - exp(-R0 z) (Wikipedia, Compartmental
models in epidemiology, s_inf = s0 exp(-R0 (r_inf - r0))), and z - HIT is the
"overshoot" (Wikipedia, Herd immunity). Deterministic, stdlib only.
"""
import math

def final_size(R0, tol=1e-15):
    # root in (0,1) of f(z) = z - 1 + exp(-R0 z); bisection, exact to tol
    if R0 <= 1:
        return 0.0
    lo, hi = 1e-12, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if mid - 1 + math.exp(-R0 * mid) < 0:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return (lo + hi) / 2

def sir_rk4(R0, i0=1e-6, gamma=1.0, dt=0.01, tmax=400.0):
    beta = R0 * gamma
    s, i, r = 1 - i0, i0, 0.0
    def f(s, i):
        return -beta * s * i, beta * s * i - gamma * i
    peak_i, cum_at_peak = i, 1 - s
    t = 0.0
    while t < tmax:
        k1 = f(s, i)
        k2 = f(s + dt/2*k1[0], i + dt/2*k1[1])
        k3 = f(s + dt/2*k2[0], i + dt/2*k2[1])
        k4 = f(s + dt*k3[0], i + dt*k3[1])
        s += dt/6*(k1[0]+2*k2[0]+2*k3[0]+k4[0])
        i += dt/6*(k1[1]+2*k2[1]+2*k3[1]+k4[1])
        t += dt
        if i > peak_i:
            peak_i, cum_at_peak = i, 1 - s
    return 1 - s, cum_at_peak, peak_i  # final attack (incl. i0), cumulative at peak

ok = True
def check(name, cond):
    global ok
    print(("  ok   " if cond else "  FAIL ") + name)
    ok = ok and cond

print("Scenario 1: final size vs HIT for typical R0, and ODE agreement")
for R0, want in [(1.5, 0.583), (2.0, 0.797), (3.0, 0.940)]:
    hit = 1 - 1/R0
    z = final_size(R0)
    zode, cpk, pk = sir_rk4(R0)
    print(f" R0={R0}: HIT={hit:.4f} z={z:.4f} overshoot={z-hit:.4f} "
          f"ODE final={zode:.4f} cum@peak={cpk:.4f} peak I={pk:.4f}")
    check(f"R0={R0} z within 0.005 of predicted {want}", abs(z - want) < 0.005)
    check(f"R0={R0} ODE final matches root within 1e-3", abs(zode - z) < 1e-3)
    check(f"R0={R0} cumulative at I-peak equals HIT within 1e-3", abs(cpk - hit) < 1e-3)
    check(f"R0={R0} epidemic ends PAST the HIT", z > hit)

print("Scenario 2: sweep R0 in [1.01, 10], where is overshoot largest?")
best = (0, 0)
for k in range(101, 1001):
    R0 = k / 100
    ov = final_size(R0) - (1 - 1/R0)
    if ov > best[0]:
        best = (ov, R0)
    if ov <= 0:
        check(f"overshoot positive at R0={R0}", False)
print(f" max overshoot={best[0]:.4f} at R0={best[1]:.2f}")
check("max overshoot ~0.30 (0.28..0.32)", 0.28 <= best[0] <= 0.32)
check("argmax R0 in [2.0, 2.5]", 2.0 <= best[1] <= 2.5)

print("Scenario 3 (BREAK): extremes where 'ends at HIT' is most / least wrong")
R0 = 1.1
z, hit = final_size(R0), 1 - 1/R0
print(f" R0=1.1: HIT={hit:.4f} z={z:.4f} ratio z/HIT={z/hit:.3f}")
check("near threshold the epidemic infects ~2x the HIT (ratio 1.8..2.0)", 1.8 <= z/hit <= 2.0)
R0 = 10.0
z, hit = final_size(R0), 1 - 1/R0
print(f" R0=10: HIT={hit:.4f} z={z:.6f} overshoot={z-hit:.4f} ratio={z/hit:.3f}")
check("at R0=10 the ratio shrinks toward 1 (<1.12) though overshoot ~0.1", z/hit < 1.12)
zode, cpk, _ = sir_rk4(1.1, tmax=2000.0)
print(f" R0=1.1 ODE: final={zode:.4f} cum@peak={cpk:.4f}")
check("R0=1.1 ODE cum@peak equals HIT within 2e-3", abs(cpk - (1-1/1.1)) < 2e-3)

if ok:
    print(f"RESULT: PASS SIR ends past HIT: R0=2 z=0.797 vs HIT 0.5; overshoot max "
          f"{best[0]:.3f} at R0={best[1]:.2f}; cum@peak==HIT; R0=1.1 z/HIT~1.9")
else:
    print("RESULT: FAIL see failed checks above")
