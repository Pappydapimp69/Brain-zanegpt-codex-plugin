"""Blind rebuild of seven E47 (a failed search lowers p by (1-POD), never clears).
Own fixture: 16 sectors on a ring; prior from a noisy call bearing:
p_i proportional to exp(-d_i^2 / (2 noise^2)), d_i = ring distance from sector 0,
plus 10% spread uniformly (the call might be wrong). Each night search K=3
sectors with detection POD. 6 nights. Exact expectation over the true sector
(no rng). Policies: REPEAT the top-3 prior block nightly; BAYES (multiply
searched p by 1-POD, renormalise, search top-3 of p*POD); CLEARED (set searched
to 0, i.e. assume POD=1 when planning, but the real POD applies).
PREDICTION (before running): Bayes >= repeat and >= cleared everywhere; cleared
loses >= 0.05 to Bayes at POD 0.5; at POD 0.98 cleared within 0.01 of Bayes;
repeat loses a lot to Bayes when noise is wide (it never leaves 3 sectors).
Break scenario: unequal POD by sector (dense brush near the call, POD 0.3 there,
0.9 elsewhere) - greedy on p alone vs on p*POD; Bayes using p*POD should still
win. Also check a greedy-Bayes failure: none expected for equal-cost sectors.
"""
import math, sys
print("python", sys.version.split()[0])
N, K, T = 16, 3, 6
def prior(noise):
    w = [math.exp(-min(i, N-i)**2/(2*noise**2)) for i in range(N)]
    s = sum(w); return [0.9*x/s + 0.1/N for x in w]
def plan(p0, pod, policy):
    """returns list of nightly sector sets (plan is deterministic given failures)."""
    belief = p0[:]; nights = []
    top0 = sorted(range(N), key=lambda i: -p0[i]*pod[i])[:K]
    for t in range(T):
        if policy == "repeat": S = top0
        else: S = sorted(range(N), key=lambda i: (-belief[i]*pod[i], i))[:K]
        nights.append(S)
        for i in S:
            belief[i] *= (1-pod[i]) if policy == "bayes" else 0.0
        s = sum(belief)
        if s == 0: belief = [1.0/N]*N
        else: belief = [x/s for x in belief]
    return nights
def pfind(p0, pod, nights):
    tot = 0.0
    for i in range(N):
        miss = 1.0
        for S in nights:
            if i in S: miss *= 1-pod[i]
        tot += p0[i]*(1-miss)
    return tot
ok = True; out = {}
for noise in (0.8, 1.5, 3.0):
    for P in (0.5, 0.8, 0.98):
        p0 = prior(noise); pod = [P]*N
        r = {k: pfind(p0, pod, plan(p0, pod, k)) for k in ("repeat", "bayes", "cleared")}
        out[(noise, P)] = r
        print(f"noise {noise} POD {P}: repeat {r['repeat']:.3f} bayes {r['bayes']:.3f} cleared {r['cleared']:.3f}")
        ok &= r['bayes'] >= r['repeat']-1e-12 and r['bayes'] >= r['cleared']-1e-12
c_half = all(out[(n, 0.5)]['bayes']-out[(n, 0.5)]['cleared'] >= 0.05 for n in (0.8, 1.5, 3.0))
c_98 = all(out[(n, 0.98)]['bayes']-out[(n, 0.98)]['cleared'] <= 0.01 for n in (0.8, 1.5, 3.0))
print("bayes>=others:", ok, "| cleared loses>=0.05 at POD0.5:", c_half, "| within 0.01 at 0.98:", c_98)
# break: unequal POD
p0 = prior(1.5); pod = [0.3 if min(i, N-i) <= 1 else 0.9 for i in range(N)]
b = pfind(p0, pod, plan(p0, pod, "bayes"))
# naive Bayes that ranks on p only
belief = p0[:]; nights = []
for t in range(T):
    S = sorted(range(N), key=lambda i: (-belief[i], i))[:K]; nights.append(S)
    for i in S: belief[i] *= 1-pod[i]
    s = sum(belief); belief = [x/s for x in belief]
bp = pfind(p0, pod, nights)
cl = pfind(p0, pod, plan(p0, pod, "cleared"))
print(f"break unequal POD: bayes(p*POD) {b:.3f} bayes(p only) {bp:.3f} cleared {cl:.3f}")
ok = ok and c_half and c_98 and b >= bp
print(f"RESULT: {'PASS' if ok else 'FAIL'} POD0.5 noise1.5 bayes {out[(1.5,0.5)]['bayes']:.3f} cleared {out[(1.5,0.5)]['cleared']:.3f} repeat {out[(1.5,0.5)]['repeat']:.3f}; unequal POD p*POD {b:.3f} vs p-only {bp:.3f}")
