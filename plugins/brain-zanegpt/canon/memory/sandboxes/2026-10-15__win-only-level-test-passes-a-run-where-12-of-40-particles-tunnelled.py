"""Train edge: demo-disc (local) E1 (particle-liquid puzzle: cap speed or liquid
tunnels through thin walls; prove each level with a stepped completability
test that plays the solution and requires a win) + brain E38 (endpoint
validation leaves the middle unchecked: assert on the trajectory wherever the
work makes a claim).
Composed claim: a win-only completability test passes levels whose physics is
broken mid-run; a trajectory invariant ('no particle is ever inside a wall')
catches them.
Own fixture, deterministic, no rng: 2-D grid-free particles (radius 3) poured
from x = 10..30 at staggered heights; a 2 px vertical wall at x = 50 separates
the pour from a side pocket; the basin is the floor region x < 50. Each frame a
particle falls under gravity and gets a sideways push toward the wall
(a 'slope'). Win = at least 70% of 40 particles end in the basin. Frame
schedules: fixed 1/60, per-frame steps at 30, 20, 12 fps (variable step).
PREDICTION (written before running): fixed 1/60 never tunnels; at 20 and 12
fps some particles tunnel through the wall yet the level is still WON (the win
test passes a broken run); the trajectory invariant flags every tunnelling run;
the win test flags none of the won-with-tunnelling runs.
"""
import sys
print("python", sys.version.split()[0])
R, WALL, WW = 3.0, 50.0, 2.0
def run(dt, frames):
    ps = [[10 + (i % 7) * 3.0, 100 + (i // 7) * 8.0, 0.0, 0.0] for i in range(40)]
    inside = tunnelled = 0
    for _ in range(frames):
        for p in ps:
            p[3] -= 900 * dt
            p[2] = min(p[2] + 400 * dt, 300.0)
            if p[1] - R <= 0: p[1], p[3] = R, 0.0
            old = p[0]
            p[0] += p[2] * dt; p[1] += p[3] * dt
            if p[1] < R: p[1] = R
            # discrete wall test only at the new position (the bug shape)
            if WALL - R < p[0] < WALL + WW + R and old < WALL - R + 1e-9:
                p[0] = WALL - R; p[2] = 0.0
            if WALL < p[0] < WALL + WW: inside += 1
            if old < WALL and p[0] > WALL + WW: tunnelled += 1
    basin = sum(1 for p in ps if p[0] < WALL)
    return basin / 40 >= 0.70, tunnelled, basin
res = {}
for nm, dt, fr in (("fixed 60", 1 / 60, 300), ("30fps", 1 / 30, 150), ("20fps", 1 / 20, 100), ("12fps", 1 / 12, 60)):
    won, tun, basin = run(dt, fr)
    res[nm] = (won, tun, basin)
    print(f"{nm:9s}: won {won!s:5s} basin {basin}/40, tunnelled {tun} -> win test {'PASS' if won else 'FAIL'}, trajectory invariant {'FAIL' if tun else 'PASS'}")
broken_won = [n for n, (w, t, b) in res.items() if w and t]
c = [res["fixed 60"][1] == 0, len(broken_won) >= 1, all(res[n][1] > 0 for n in ("20fps", "12fps"))]
print("won despite tunnelling:", broken_won)
print("checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} {sum(c)}/3; " + "; ".join(f"{n} won={w} tunnelled={t} basin={b}" for n, (w, t, b) in res.items()) + f"; win-only test passed broken runs: {broken_won}")
