"""Train edge: local 2026-10-13 seeded-rng E1 (restore from full state, and save
any cached value - a spare Box-Muller gaussian lives outside the state word;
check restores at odd and even draw counts) + sandbox-seam-replan-save E1
(two subsystems saving in separate non-atomic steps corrupt silently, and the
check that would catch it may be gone).
Composed claim: a seeded run's save has two independent failure axes -
MISSING state (the cached spare) and TORN state (rng and sim saved a tick
apart) - and a load-time cross-check (both halves record the tick) catches the
torn axis but not the missing one; only an atomic, complete snapshot fixes both.
Own fixture, deterministic: mulberry32 with a Box-Muller gaussian() that caches
its spare; a sim of 1,000 ticks where each tick draws one gaussian and moves a
walker. Save at every tick 100..899; resume; compare the next 50 positions.
Modes: A atomic + spare; B atomic, no spare; C rng saved one tick before sim
(+spare); D C and no spare. Cross-check: rng half and sim half each store tick.
PREDICTION (written before running): A diverges at 0 save points; B at about
half (whenever a spare is pending - odd gaussian count); C at all 800; D at all
800; the tick cross-check flags 100% of C and D and 0% of B.
"""
import math, sys
print("python", sys.version.split()[0])
M = 0xffffffff
class G:
    def __init__(s, seed): s.a = seed & M; s.spare = None
    def u(s):
        s.a = (s.a + 0x6D2B79F5) & M; t = s.a
        t = ((t ^ (t >> 15)) * (t | 1)) & M; t ^= (t + (((t ^ (t >> 7)) * (t | 61)) & M)) & M
        return ((t ^ (t >> 14)) & M) / 4294967296.0
    def gauss(s):
        if s.spare is not None: v, s.spare = s.spare, None; return v
        u1, u2 = max(s.u(), 1e-12), s.u(); r = math.sqrt(-2 * math.log(u1))
        s.spare = r * math.sin(2 * math.pi * u2); return r * math.cos(2 * math.pi * u2)
def tick(g, x): return x + g.gauss()
def full(seed=7, n=1000):
    g = G(seed); x = 0.0; xs = []; snaps = []
    for t in range(n):
        snaps.append((g.a, g.spare, x, t))   # state BEFORE tick t
        x = tick(g, x); xs.append(x)
    return xs, snaps
xs, snaps = full()
res = {}
for mode in "ABCD":
    div = flagged = 0
    for t in range(100, 900):
        if mode in "AB": a, sp, _, rt = snaps[t]; _, _, x, st = snaps[t]
        else: a, sp, _, rt = snaps[t]; _, _, x, st = snaps[t + 1]   # rng saved at t, sim at t+1
        g = G(0); g.a = a; g.spare = sp if mode in "AC" else None
        flagged += rt != st
        ys = []; y = x
        for _ in range(50): y = tick(g, y); ys.append(y)
        start = st
        div += any(abs(p - q) > 1e-12 for p, q in zip(ys, xs[start:start + 50]))
    res[mode] = (div, flagged)
    print(f"mode {mode}: diverged {div}/800, cross-check flagged {flagged}/800")
c = [res["A"][0] == 0, 300 <= res["B"][0] <= 500, res["C"][0] == 800, res["D"][0] == 800,
     res["C"][1] == 800 and res["D"][1] == 800 and res["B"][1] == 0]
print("checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} {sum(c)}/5; diverged A {res['A'][0]}, B {res['B'][0]}, C {res['C'][0]}, D {res['D'][0]} of 800; tick cross-check flags B {res['B'][1]}, C {res['C'][1]}, D {res['D'][1]}")
