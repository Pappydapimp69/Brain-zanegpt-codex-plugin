# Discrete authoritative core (zone, hp, rolls from sfc32) + continuous float renderer position.
# Question: does "split state by determinism need" stay exact together with saving sfc32 state words?
M = 0xFFFFFFFF
class Sfc32:
    def __init__(s, a, b, c, d): s.s = [a & M, b & M, c & M, d & M]
    def next(s):
        a, b, c, d = s.s
        t = (a + b + d) & M
        d = (d + 1) & M
        a = b ^ (b >> 9)
        b = (c + (c << 3)) & M
        c = ((c << 21 | c >> 11) & M) + t & M
        s.s = [a, b, c, d]
        return t
def seeded(n):
    g = Sfc32(n, n * 7 + 1, n * 13 + 5, 1)
    for _ in range(12): g.next()
    return g

TICKS = 60  # discrete sim ticks per run (fixed), frame rate only changes how many render steps happen per tick

def run(mode, frames_per_tick, save_at=None, cosmetic_shared=False):
    g = seeded(42); cos = seeded(99)
    hp, zone, x = 100, 0, 0.0
    log = []; saved = None
    for t in range(TICKS):
        if save_at is not None and t == save_at:
            saved = (list(g.s), hp, zone, x)
            g = Sfc32(*saved[0]); hp, zone, x = saved[1], saved[2], saved[3]   # reload from state words
        for _ in range(frames_per_tick):               # continuous renderer, frame-rate dependent float drift
            x += 0.7 / frames_per_tick + 0.002 * frames_per_tick
            r = (g if cosmetic_shared else cos).next() & 7   # camera shake draw
        if mode == "coupled":
            zone = int(x // 5)                          # authoritative zone read off the float position
            hit = (g.next() % 100) < (30 if x % 5 > 2.5 else 10)   # roll threshold reads float x
        else:
            zone = t // 7                               # zone is a discrete tick fact
            hit = (g.next() % 100) < (30 if (t % 7) > 3 else 10)   # roll reads discrete state only
        if hit: hp -= 3
        log.append((zone, hp))
    return log, list(g.s)

res = {}
base, bs = run("split", 1)
res["split_fps_invariant"] = all(run("split", f)[0] == base for f in (2, 4, 7))
res["split_reload_exact"] = run("split", 1, save_at=30)[0] == base
res["coupled_fps_invariant"] = all(run("coupled", f)[0] == run("coupled", 1)[0] for f in (2, 4, 7))
res["coupled_diverging_fps"] = sum(run("coupled", f)[0] != run("coupled", 1)[0] for f in (2, 4, 7))
# BREAK: split state but cosmetic shake draws come from the SAME stream as the rolls
res["shared_cosmetic_fps_invariant"] = all(run("split", f, cosmetic_shared=True)[0] == run("split", 1, cosmetic_shared=True)[0] for f in (2, 4, 7))
res["shared_cosmetic_reload_exact"] = run("split", 3, save_at=30, cosmetic_shared=True)[0] == run("split", 3, cosmetic_shared=True)[0]
print(res)
ok = (res["split_fps_invariant"] and res["split_reload_exact"] and not res["coupled_fps_invariant"]
      and not res["shared_cosmetic_fps_invariant"] and res["shared_cosmetic_reload_exact"])
print("RESULT: %s split+separate stream invariant over fps 1/2/4/7 and exact on reload; coupled float diverged %d/3 fps; shared cosmetic stream diverged although state split (reload still exact)"
      % ("PASS" if ok else "FAIL", res["coupled_diverging_fps"]))
