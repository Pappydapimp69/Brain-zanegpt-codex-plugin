"""Theater blocking: count audience seats that lose sight of an actor behind another.
Seats on an arc facing a stage; actors are discs (radius 0.25 m). Deterministic, stdlib only."""
import math
R = 0.25
seats = [(10 * math.sin(math.radians(a)), -8 - 4 * (1 - math.cos(math.radians(a))))
         for a in range(-50, 51, 5)] + [(x, -14.0) for x in range(-8, 9)]
def blocked(seat, tgt, other):
    sx, sy = seat; tx, ty = tgt; ox, oy = other
    dx, dy = tx - sx, ty - sy; L2 = dx * dx + dy * dy
    u = ((ox - sx) * dx + (oy - sy) * dy) / L2
    if u <= 0 or u >= 1: return False
    px, py = sx + u * dx, sy + u * dy
    return math.hypot(ox - px, oy - py) < 2 * R   # discs overlap in the line of sight
def score(actors):
    return sum(any(blocked(s, a, b) for b in actors if b is not a) for s in seats for a in actors)
forms = {
    "depth line (all at x=0, 1m apart upstage)": [(0, 0), (0, 1), (0, 2)],
    "flat row across (1m apart)":              [(-1, 0), (0, 0), (1, 0)],
    "stagger (0.75m lateral, 1m depth)":        [(-0.75, 0), (0, 1), (0.75, 2)],
    "stagger too tight (0.25m lateral)":        [(-0.25, 0), (0, 1), (0.25, 2)],   # BREAK case
}
res = {k: score(v) for k, v in forms.items()}
for k, v in res.items(): print(f"{k:45s} occluded seat-actor pairs: {v} / {len(seats)*3}")
d, st, tight = res["depth line (all at x=0, 1m apart upstage)"], res["stagger (0.75m lateral, 1m depth)"], res["stagger too tight (0.25m lateral)"]
ok = st <= d * 0.5 and tight > st
print(f"RESULT: {'PASS' if ok else 'FAIL'} stagger {st} vs depth line {d} vs tight stagger {tight}")
