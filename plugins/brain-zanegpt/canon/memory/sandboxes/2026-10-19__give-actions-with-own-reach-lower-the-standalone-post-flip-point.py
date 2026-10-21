# Prediction (before run): R=9, thread reach Y=1. With give actions earning g=0 reach the
# flip is 5.5 (prior E1: between 5.4 and 5.6); with g=0.2 it drops to 3.7; with g=0.6 to 0.1
# (standalone then wins at any reach), i.e. the flip is (R+2)/2 - R*g/Y.
R, Y = 9, 1.0
def flip(g, R=R):
    x = 0.0
    while x < 20:
        if (x + R * g) / (R + 2) > Y / 2: return round(x, 1)
        x = round(x + 0.1, 1)
    return None
def ana(g, R=R): return (R + 2) / 2 * Y - R * g
res = {}
for g in (0.0, 0.2, 0.6):
    res[g] = flip(g); print("g", g, "flip scan", res[g], "analytic", round(ana(g), 2))
# BREAK scenario: give actions reach decays (only first 3 gives earn), R=9
def flip_cap(g, cap=3):
    x = 0.0
    while x < 20:
        if (x + min(R, cap) * g) / (R + 2) > Y / 2: return round(x, 1)
        x = round(x + 0.1, 1)
r4 = flip_cap(0.2); print("capped gives g=0.2 cap=3 flip", r4, "analytic", round(5.5 - 0.6, 2))
# run 1 used exact-equality bounds and FAILED by one 0.1 grid step (scan finds first x strictly above
# the analytic boundary); check now allows 0 < scan-analytic <= 0.15
ok = all(0 < d <= 0.15 for d in (res[0.0]-5.5, res[0.2]-3.7, res[0.6]-0.1, r4-4.9))
print("RESULT:", "PASS" if ok else "FAIL", f"flips g0={res[0.0]} g.2={res[0.2]} g.6={res[0.6]} capped={r4}")
