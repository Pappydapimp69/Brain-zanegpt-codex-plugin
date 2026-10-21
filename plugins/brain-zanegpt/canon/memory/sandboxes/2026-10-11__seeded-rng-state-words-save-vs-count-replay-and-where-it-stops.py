"""sfc32 seeded RNG, full-state save vs {seed,count} save, plus the boundaries.
Sim: N entities; each tick every entity draws one roll to move; world = positions.
S1 state-word save/load: next 1000 rolls identical, 0 rolls spent on load.
S2 {seed,count}: identical but load costs `count` rolls.
S3 break: replay consumes rolls in a different ORDER (entities iterated sorted vs
   insertion) -> identical stream, different world.
S4 break: float accumulation order differs -> sums differ in low bits though rolls equal.
S5 break (seed-vs-replay lesson): restore ONLY the RNG words into a fresh world
   (world is derived by playback) -> next rolls match but world state does not."""
M = 0xFFFFFFFF
class Sfc32:
    def __init__(s, seed):
        s.a, s.b, s.c, s.d = 0x9E3779B9, 0x243F6A88, 0xB7E15162, seed & M
        s.n = 0
        for _ in range(15): s.next()
        s.n = 0
    def next(s):
        t = (s.a + s.b + s.d) & M
        s.d = (s.d + 1) & M
        s.a = s.b ^ (s.b >> 9)
        s.b = (s.c + (s.c << 3)) & M
        s.c = (((s.c << 21) | (s.c >> 11)) & M) + t & M
        s.n += 1
        return t / 4294967296.0
    def state(s): return (s.a, s.b, s.c, s.d)
    def load(s, st): s.a, s.b, s.c, s.d = st
def run(rng, world, ticks, order):
    ids = list(world)
    if order == "sorted": ids = sorted(ids, key=lambda k: world[k])
    for _ in range(ticks):
        for k in ids:
            world[k] += int(rng.next() * 7) - 3
    return world
def fresh(): return {i: 100 - i * 3 for i in range(8)}
res = {}
live = Sfc32(42); w = fresh(); run(live, w, 50, "insert")
saved = live.state(); count = live.n
cont = [live.next() for _ in range(1000)]
# S1
r1 = Sfc32(0); r1.load(saved); res["S1_identical"] = [r1.next() for _ in range(1000)] == cont; res["S1_load_rolls"] = 0
# S2
r2 = Sfc32(42); 
for _ in range(count): r2.next()
res["S2_identical"] = [r2.next() for _ in range(1000)] == cont; res["S2_load_rolls"] = count
# S3 order break: same stream, different world
a = Sfc32(7); wa = run(a, fresh(), 50, "insert"); b = Sfc32(7); wb = run(b, fresh(), 50, "sorted")
res["S3_streams_equal"] = a.state() == b.state() and a.n == b.n; res["S3_worlds_equal"] = wa == wb
# S4 float order
xs = [Sfc32(9).next() for _ in range(1)]
g = Sfc32(9); vals = [g.next() * 10 ** (i % 7 - 3) for i in range(5000)]
res["S4_float_sum_equal"] = sum(vals) == sum(reversed(vals))
# S5 RNG words only into a fresh world
w_true = fresh(); lv = Sfc32(5); run(lv, w_true, 30, "insert"); st = lv.state()
w_loaded = fresh(); rl = Sfc32(0); rl.load(st)
nxt_true = run(lv, w_true, 5, "insert"); nxt_loaded = run(rl, w_loaded, 5, "insert")
res["S5_rolls_match_world_differs"] = lv.state() == rl.state() and nxt_true != nxt_loaded
for k, v in res.items(): print(k, v)
ok = (res["S1_identical"] and res["S2_identical"] and res["S2_load_rolls"] == 400
      and res["S3_streams_equal"] and not res["S3_worlds_equal"]
      and not res["S4_float_sum_equal"] and res["S5_rolls_match_world_differs"])
print("RESULT:", "PASS" if ok else "FAIL",
      f"state-words load 0 rolls vs {count} for seed+count, both exact; same stream gave different world on order change, float sum order, and RNG-only restore")
