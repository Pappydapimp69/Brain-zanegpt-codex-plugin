"""Sandbox: own-the-four-comparisons kernel. Deterministic, stdlib only.
Truth = point-in-rect on shared logical coords. 'Pipeline' = framework path that
maps device px -> world via zoom, device-pixel-ratio and integer rounding at a
stage. 'Owned' = registry of rects + four comparisons."""
from fractions import Fraction as F

def inside(r, x, y):  # the four comparisons
    return r[0] <= x < r[0] + r[2] and r[1] <= y < r[1] + r[3]

def pipeline_hit(r, dx, dy, zoom, dpr):
    # device px -> css px (round to int, as many input paths do) -> world
    cx, cy = round(dx / dpr), round(dy / dpr)
    return inside(r, F(cx) / zoom, F(cy) / zoom)

def owned_hit(r, dx, dy, zoom, dpr):
    return inside(r, F(dx) / dpr / zoom, F(dy) / dpr / zoom)

RECT = (10, 10, 20, 20)
devices = [(F(1), F(1)), (F(3, 2), F(1)), (F(1), F(5, 2)), (F(7, 4), F(3, 2)), (F(2), F(3))]

# S1: sweep device pixels for each device; count disagreement with exact truth
bad_p = bad_o = total = 0
for zoom, dpr in devices:
    for dx in range(0, 120):
        for dy in range(0, 120):
            t = inside(RECT, F(dx) / dpr / zoom, F(dy) / dpr / zoom)
            total += 1
            bad_p += pipeline_hit(RECT, dx, dy, zoom, dpr) != t
            bad_o += owned_hit(RECT, dx, dy, zoom, dpr) != t
print(f"S1 sweep: total={total} pipeline_wrong={bad_p} owned_wrong={bad_o}")

# S2: overlap priority by draw order (registry, last-drawn wins)
reg = [("back", (0, 0, 50, 50)), ("front", (20, 20, 10, 10))]
def top(reg, x, y):
    for n, r in reversed(reg):
        if inside(r, x, y): return n
s2 = (top(reg, 25, 25), top(reg, 5, 5), top(reg, 60, 60))
print("S2 priority:", s2)

# S3: press/release pairing; handler fires only if release hits the armed rect
def run(events, slot_per_key):
    fired, armed, pend = [], None, []
    for kind, x, y in events:
        if kind == "down":
            n = top(reg, x, y)
            if slot_per_key: pend = [n]       # one pending slot (august-10/E18 shape)
            else: pend.append(n)
        else:
            for n in (pend if not slot_per_key else pend[-1:]):
                if n and n == top(reg, x, y): fired.append(n)
            pend = []
    return fired
ev_drag = [("down", 25, 25), ("up", 5, 5)]                       # press front, release elsewhere
ev_dbl = [("down", 25, 25), ("down", 5, 5), ("up", 25, 25)]      # two presses same frame, one release
print("S3 drag-off fires:", run(ev_drag, False), "| same-frame pair list:", run(ev_dbl, False), "slot:", run(ev_dbl, True))

# S4 BREAK: owned arithmetic is only right if the INPUT SPACE is owned too.
# Letterboxed canvas: device origin offset by (ox,oy). Owned comparisons that skip the offset are wrong.
ox, oy = 8, 6
wrong = sum(inside(RECT, F(dx), F(dy)) != inside(RECT, F(dx - ox), F(dy - oy))
            for dx in range(0, 60) for dy in range(0, 60))
print("S4 owned-without-owned-coordinate-mapping wrong:", wrong, "of 3600")

# S5 BREAK: framework handler left live beside owned one -> double fire
fw_fired = owned_fired = 0
for dx, dy in [(15, 15), (16, 16), (29, 29)]:
    if inside(RECT, dx, dy): owned_fired += 1
    if pipeline_hit(RECT, dx, dy, F(1), F(1)): fw_fired += 1
print("S5 both paths live: owned", owned_fired, "framework", fw_fired, "handler fires", owned_fired + fw_fired, "for 3 taps")

ok = bad_o == 0 and bad_p > 0 and s2 == ("front", "back", None) and run(ev_drag, False) == [] \
     and len(run(ev_dbl, False)) > len(run(ev_dbl, True)) and wrong > 0 and owned_fired + fw_fired == 2 * owned_fired
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
      f"owned_wrong={bad_o} pipeline_wrong={bad_p}/{total}; coord-mapping break={wrong}; dual-path doubles fires")
