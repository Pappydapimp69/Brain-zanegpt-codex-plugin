"""Sandbox: does a grid-based smoothing validator inherit the grid's centre-sampling blind spot?

Composes (all three exercised below):
  pappydapimp69/dog/E34                      (grid built by sampling cell CENTRES misses a small obstacle;
                                             goal inside an obstacle -> fallback to straight steering)
  sandbox-path-smoothing-validation/E1       (validate a smoothed path with an independent continuous
                                             padded-geometry check, not the smoother's own abstraction)
  sandbox-dog-pathfinding/E1                 (string-pull smoothing can cut a corner through an obstacle)

PREDICTION (written before the first run), cell size 2, padded radius R=1.0, one circular obstacle,
sweep of 20x20=400 obstacle positions inside one cell period, straight start->goal line through y=9:
  P1 centre-sampled grid sees NO blocked cell at 1-pi/4 = 21.5% of positions -> 86 +/- 6 of 400.
  P2 in the centre-sampled grid the grid-lookup validator (G) reports 0 violations in all 400 layouts
     while the continuous padded check (C) reports a violation in >= 70 of them (G false-green).
  P3 with an AABB-vs-circle grid (dog/E34 fix) and dense LOS: C violations = 0 of 400, G = 0.
  P4 BREAK: AABB grid but LOS/validator sampled only every 2.0 (= one cell): C violations >= 1 of 400
     while G (same coarse sampling) = 0.  (Uncertain - may come out 0.)
  P5 goal inside the obstacle: naive fallback (steer straight at raw goal) violates C in 400/400;
     nearest-open-cell substitution violates in 0/400.
FIRST RUN (recorded, predictions left unedited above): P1 missed (95 blind, 23.8%: positions exactly
tangent at distance 1.0 on the 0.1 lattice count as free, which the 1-pi/4 estimate ignored) and P4 missed
(coarse step == cell size 2.0 gave C=0). Probe of step 3.0/6.0 gave C=19/380 with G=0, so the
REVISED claim below (R1..R4) was added AFTER run 1 and is labelled as such.
REVISED CLAIM (post-hoc): R1 centre-grid: G=0 while C>0 in >=100 layouts. R2 aabb grid, step<=cell: C=0.
R3 aabb grid, validation+LOS step > cell (3.0): C>=1 with G=0. R4 P5 holds.
"""
import heapq, math

CELL = 2.0
N = 10                      # 10x10 cells, world 0..20
R = 1.0                     # padded obstacle radius (small prop, comparable to half a cell)
START = (1.0, 9.0)
GOAL = (19.0, 9.0)
STEP_DENSE = 0.1
EPS = 1e-9


def cell_of(p):
    return (min(N - 1, max(0, int(p[0] // CELL))), min(N - 1, max(0, int(p[1] // CELL))))


def center(c):
    return ((c[0] + 0.5) * CELL, (c[1] + 0.5) * CELL)


def build_grid(o, mode):
    blocked = set()
    for cx in range(N):
        for cy in range(N):
            if mode == "centre":
                px, py = center((cx, cy))
            else:  # "aabb": closest point of the cell square to the obstacle centre
                px = min(max(o[0], cx * CELL), (cx + 1) * CELL)
                py = min(max(o[1], cy * CELL), (cy + 1) * CELL)
            if math.hypot(px - o[0], py - o[1]) < R - EPS:
                blocked.add((cx, cy))
    return blocked


def astar(blocked, s, g):
    if s in blocked or g in blocked:
        return None
    openq = [(0.0, 0.0, 0, s)]
    best = {s: 0.0}
    prev = {}
    cnt = 0
    while openq:
        _, _, _, cur = heapq.heappop(openq)
        if cur == g:
            path = [cur]
            while cur in prev:
                cur = prev[cur]
                path.append(cur)
            return path[::-1]
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = cur[0] + dx, cur[1] + dy
                if not (0 <= nx < N and 0 <= ny < N) or (nx, ny) in blocked:
                    continue
                if dx and dy and ((cur[0] + dx, cur[1]) in blocked or (cur[0], cur[1] + dy) in blocked):
                    continue  # no corner cutting
                ng = best[cur] + math.hypot(dx, dy)
                if ng < best.get((nx, ny), 1e18):
                    best[(nx, ny)] = ng
                    prev[(nx, ny)] = cur
                    ddx, ddy = abs(g[0] - nx), abs(g[1] - ny)
                    h = (ddx + ddy) + (math.sqrt(2) - 2) * min(ddx, ddy)
                    cnt += 1
                    heapq.heappush(openq, (ng + h, h, cnt, (nx, ny)))
    return None


def grid_los(blocked, a, b, step):
    d = math.hypot(b[0] - a[0], b[1] - a[1])
    n = max(1, int(math.ceil(d / step)))
    for i in range(n + 1):
        t = i / n
        if cell_of((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)) in blocked:
            return False
    return True


def smooth(blocked, pts, step):
    out = [pts[0]]
    i = 0
    while i < len(pts) - 1:
        j = len(pts) - 1
        while j > i + 1 and not grid_los(blocked, pts[i], pts[j], step):
            j -= 1
        out.append(pts[j])
        i = j
    return out


def seg_dist(p, a, b):
    vx, vy = b[0] - a[0], b[1] - a[1]
    L2 = vx * vx + vy * vy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / L2))
    return math.hypot(p[0] - (a[0] + t * vx), p[1] - (a[1] + t * vy))


def c_violation(o, pts):          # independent ground truth: continuous segment vs padded disc
    return any(seg_dist(o, pts[i], pts[i + 1]) < R - EPS for i in range(len(pts) - 1))


def g_violation(blocked, pts, step):   # same abstraction as the planner/smoother
    return any(not grid_los(blocked, pts[i], pts[i + 1], step) for i in range(len(pts) - 1))


def vtx_violation(blocked, pts):
    return any(cell_of(p) in blocked for p in pts)


def positions():
    return [(8.0 + 0.1 * i, 8.0 + 0.1 * j) for i in range(20) for j in range(20)]


def run_plan(mode, los_step, val_step):
    r = dict(total=0, blind=0, raw_c=0, c=0, g=0, vtx=0, false_green=0, nopath=0)
    for o in positions():
        o = (round(o[0], 6), round(o[1], 6))
        blocked = build_grid(o, mode)
        r["total"] += 1
        r["blind"] += (len(blocked) == 0)
        cells = astar(blocked, cell_of(START), cell_of(GOAL))
        if cells is None:
            r["nopath"] += 1
            continue
        raw = [center(c) for c in cells]
        raw[0], raw[-1] = START, GOAL
        sm = smooth(blocked, raw, los_step)
        r["raw_c"] += c_violation(o, raw)
        cv = c_violation(o, sm)
        gv = g_violation(blocked, sm, val_step)
        r["c"] += cv
        r["g"] += gv
        r["vtx"] += vtx_violation(blocked, sm)
        r["false_green"] += (cv and not gv)
    return r


def run_goal_inside():
    naive_v = fix_v = 0
    tot = 0
    for o in positions():
        o = (round(o[0], 6), round(o[1], 6))
        blocked = build_grid(o, "aabb")
        g = o                          # destination sits at the obstacle centre
        tot += 1
        gc = cell_of(g)
        s = cell_of(START)
        # naive: no path to a blocked goal -> fall back to steering straight at the raw goal
        if astar(blocked, s, gc) is None:
            naive_v += c_violation(o, [START, g])
        # fix: nearest open cell in an expanding ring (cap 6), path there, smooth
        goal_cell = None
        for ring in range(0, 7):
            cands = [(gc[0] + dx, gc[1] + dy) for dx in range(-ring, ring + 1) for dy in range(-ring, ring + 1)
                     if max(abs(dx), abs(dy)) == ring and 0 <= gc[0] + dx < N and 0 <= gc[1] + dy < N
                     and (gc[0] + dx, gc[1] + dy) not in blocked]
            if cands:
                goal_cell = min(cands, key=lambda c: (math.hypot(center(c)[0] - o[0], center(c)[1] - o[1]), c))
                break
        cells = astar(blocked, s, goal_cell)
        raw = [center(c) for c in cells]
        raw[0] = START
        fix_v += c_violation(o, smooth(blocked, raw, STEP_DENSE))
    return tot, naive_v, fix_v


def main():
    s1 = run_plan("centre", STEP_DENSE, STEP_DENSE)
    s2 = run_plan("aabb", STEP_DENSE, STEP_DENSE)
    s3 = run_plan("aabb", CELL, CELL)
    s3b = run_plan("aabb", 3.0, 3.0)
    s3c = run_plan("aabb", 6.0, 6.0)
    tot, nv, fv = run_goal_inside()
    for name, r in (("1 centre-grid dense", s1), ("2 aabb-grid dense", s2), ("3 BREAK aabb-grid coarse-step", s3)):
        print("S%s: %s" % (name, " ".join("%s=%d" % kv for kv in r.items())))
    print("S3b BREAK(post-hoc) aabb step 3.0: C=%d G=%d false_green=%d" % (s3b["c"], s3b["g"], s3b["false_green"]))
    print("S3c BREAK(post-hoc) aabb step 6.0: C=%d G=%d false_green=%d" % (s3c["c"], s3c["g"], s3c["false_green"]))
    print("S4 goal-inside-obstacle: total=%d naive_fallback_C=%d nearest_open_cell_C=%d" % (tot, nv, fv))
    frac = s1["blind"] / s1["total"]
    p1 = 80 <= s1["blind"] <= 92
    p2 = s1["g"] == 0 and s1["false_green"] >= 70
    p3 = s2["c"] == 0 and s2["g"] == 0
    p4 = s3["c"] >= 1 and s3["g"] == 0
    p5 = nv == tot and fv == 0
    print("P1 blind=%d (%.1f%%, predicted 86+/-6) %s" % (s1["blind"], 100 * frac, p1))
    print("P2 G=%d false_green=%d (pred G=0, FG>=70) %s" % (s1["g"], s1["false_green"], p2))
    print("P3 aabb C=%d G=%d (pred 0,0) %s" % (s2["c"], s2["g"], p3))
    print("P4 break coarse C=%d G=%d (pred C>=1,G=0) %s" % (s3["c"], s3["g"], p4))
    print("P5 goal-inside naive=%d/%d fix=%d (pred 400/400, 0) %s" % (nv, tot, fv, p5))
    r1 = s1["g"] == 0 and s1["false_green"] >= 100
    r2 = s2["c"] == 0 and s3["c"] == 0
    r3 = s3b["c"] >= 1 and s3b["g"] == 0 and s3c["c"] >= 1 and s3c["g"] == 0
    orig = "".join("1" if x else "0" for x in (p1, p2, p3, p4, p5))
    ok = r1 and r2 and r3 and p5
    print("RESULT: %s centre-grid blind=%d/400 G=0 false-green=%d; aabb step<=cell C=0; aabb step3.0 C=%d step6.0 C=%d (G=0); goal-inside naive=%d fix=%d; original predictions P1-P5=%s (P1,P4 missed)"
          % ("PASS" if ok else "FAIL", s1["blind"], s1["false_green"], s3b["c"], s3c["c"], nv, fv, orig))


main()
