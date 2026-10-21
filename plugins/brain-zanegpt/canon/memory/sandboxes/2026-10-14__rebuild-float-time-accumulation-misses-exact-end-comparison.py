"""ITERATION 2. Iteration 1 FAILED: my analytic frame was round(d*fps), which rounds 62.5 down (banker's) and mislabelled the 25 fps x 2.5 s cell as late and
tolerance-wrong (23/24). Fixed to ceil(d*fps - 1e-9), the first frame at which elapsed truly reaches the duration; prediction unchanged.
Rebuild (own fixture: fps 24/25/30/50/60/90/120/144 x durations 1,2,2.5, plus a tolerance+snap variant).
PREDICTION (before run): sum of 1/30 thirty times is 0.9999999999999999 (<1) and exact >= stops one frame late (31 steps not 30);
across my 24 fps x duration cells at least 3 and at most 20 show a strict-'>=' completion lagging the analytic frame count by 1 or
more; the tolerance (eps=1e-9) completion lands on the analytic frame in 24/24 cells; exact == never fires in at least 1 cell where >= fires late."""
import math
FPS = (24, 25, 30, 50, 60, 90, 120, 144)
DUR = (1.0, 2.0, 2.5)

def steps_exact(fps, d, mode):
    dt, t, n = 1.0 / fps, 0.0, 0
    while n < 100000:
        t += dt; n += 1
        if mode == 'ge' and t >= d: return n
        if mode == 'eq' and t == d: return n
        if mode == 'eps' and t >= d - 1e-9: return n
        if mode == 'eq' and t > d: return None   # overshot without ever matching
    return None

s = 0.0
for _ in range(30): s += 1.0 / 30
late = eps_ok = eq_never = cells = 0
for fps in FPS:
    for d in DUR:
        analytic = math.ceil(d * fps - 1e-9); cells += 1
        ge = steps_exact(fps, d, 'ge'); eps = steps_exact(fps, d, 'eps'); eq = steps_exact(fps, d, 'eq')
        late += ge > analytic
        eps_ok += eps == analytic
        eq_never += (eq is None and ge > analytic)
        if ge > analytic: print("late", fps, d, analytic, ge)
print("sum30", repr(s), "ge30", steps_exact(30, 1.0, 'ge'))
ok = (repr(s) == '0.9999999999999999' and steps_exact(30, 1.0, 'ge') == 31 and 3 <= late <= 20 and eps_ok == cells and eq_never >= 1)
print("RESULT: %s sum30=%r; strict >= late in %d/%d cells, tolerance exact in %d/%d, == never fires in %d late cells" % ("PASS" if ok else "FAIL", s, late, cells, eps_ok, cells, eq_never))
