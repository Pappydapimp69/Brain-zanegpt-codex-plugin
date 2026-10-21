# Deterministic sandbox: dbz-combat#E4 (resource cost must BIND) x brain-builder#E4 (instrument binding rate).
# PREDICTION (before run): pool = 100*L at level L, horizon H=20 wants of a power move, costing C.
# Flat C=8: affordable uses = floor(100L/8) = 12,25,37,50 at L=1..4 -> denied wants 8,0,0,0
# -> binding rate 0.40,0,0,0 (binds only at L=1; endgame = spam). Scaled C=8L: uses = 12 at every L
# -> denied 8 at every L, rate 0.40 at all levels. Boundary checks: C=5 (=100/20) rate 0.0, C=6 rate>0,
# C=101 rate 1.0 (unwinnable; 0 uses), and rate exactly 0 is UNINFORMATIVE about the cost.
H = 20

def binding_rate(pool, cost, wants=H):
    denied = 0
    for _ in range(wants):
        if pool >= cost:
            pool -= cost
        else:
            denied += 1
    return denied / wants

flat = [binding_rate(100 * L, 8) for L in (1, 2, 3, 4)]
scaled = [binding_rate(100 * L, 8 * L) for L in (1, 2, 3, 4)]
print("flat  ", flat)
print("scaled", scaled)
assert flat == [0.4, 0.0, 0.0, 0.0]
assert all(abs(r - 0.4) < 1e-9 for r in scaled)
# breaker: sweep cost at L=1
assert binding_rate(100, 5) == 0.0
assert binding_rate(100, 6) > 0.0
assert binding_rate(100, 101) == 1.0
ok = flat[0] > 0 and flat[3] == 0 and min(scaled) == max(scaled)
print("RESULT:", "PASS" if ok else "FAIL", "flat", flat, "scaled", scaled)
