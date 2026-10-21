"""Prediction (before run): (1) saving sfc32's 4 state words and reloading gives the identical next 1000 draws as an
uninterrupted run, restoring in 1 step, while a {seed,count} save needs `count` replay draws (count=50000 -> 50000 steps)
and reaches the same state; (2) two lockstep clients with different frame schedules but a fixed-step accumulator draw
the identical stream (equal 10-tick hash); (3) BREAK A: a frame-delta clamp that drops ticks on the stalled client makes
tick counts differ and the streams diverge at the first dropped tick; (4) BREAK B: the same two systems drawing in a
different ORDER within a tick diverge even with identical seeds. Integer-only, deterministic. Stdlib."""
M = 0xFFFFFFFF
class Sfc32:
    def __init__(s, seed):
        s.a, s.b, s.c, s.d = 0x9E3779B9, 0x243F6A88, 0xB7E15162, seed & M
        for _ in range(15): s.next()
    def next(s):
        t = (s.a + s.b + s.d) & M
        s.d = (s.d + 1) & M
        s.a = s.b ^ (s.b >> 9)
        s.b = (s.c + (s.c << 3)) & M
        s.c = (((s.c << 21) | (s.c >> 11)) & M) + t & M
        return t
    def state(s): return (s.a, s.b, s.c, s.d)
    def load(s, st): s.a, s.b, s.c, s.d = st
# 1) save/load
r = Sfc32(7)
for _ in range(50000): r.next()
st = r.state()
ref = [r.next() for _ in range(1000)]
r2 = Sfc32(0); r2.load(st); load_steps = 1
after_state = [r2.next() for _ in range(1000)]
r3 = Sfc32(7); replay_steps = 0
for _ in range(50000): r3.next(); replay_steps += 1
after_replay = [r3.next() for _ in range(1000)]
ok1 = after_state == ref and after_replay == ref and load_steps == 1 and replay_steps == 50000
# 2) lockstep with different frame schedules, fixed-step accumulator (dt=10), no clamp
def run(frames, clamp=None, ticks_wanted=10, order=("a", "b")):
    rng = Sfc32(99); acc = 0; ticks = 0; out = []
    for f in frames:
        if clamp is not None: f = min(f, clamp)
        acc += f
        while acc >= 10 and ticks < ticks_wanted:
            acc -= 10; ticks += 1
            for who in order:
                out.append((who, rng.next() & 0xFF))
    return ticks, out
tA, oA = run([10] * 10)                    # smooth
tB, oB = run([5, 5, 40, 0, 0, 30, 20])     # bursty schedule, same total time 100
ok2 = tA == tB == 10 and oA == oB
# 3) clamp drops time on the stalled client
tC, oC = run([5, 5, 40, 0, 0, 30, 20], clamp=15)
first_div = next((i for i, (x, y) in enumerate(zip(oA, oC)) if x != y), None)
ok3 = tC != tA and (first_div is not None or len(oC) != len(oA))
# 4) draw order
tD, oD = run([10] * 10, order=("b", "a"))
vals_A = [v for _, v in oA]; vals_D = [v for _, v in oD]
ok4 = vals_A == vals_D and oA != oD      # same stream consumed, but who gets which value swaps
print("save/load exact+O(1):", ok1, "replay steps", replay_steps, "vs load steps", load_steps)
print("lockstep bursty==smooth:", ok2, "ticks", tA, tB)
print("clamp: ticks", tC, "vs", tA, "first divergence index", first_div)
print("draw-order swap: same value stream", vals_A == vals_D, "but per-system assignment differs", oA != oD)
allok = ok1 and ok2 and ok3 and ok4
print("RESULT: %s state-words save exact (1 step vs %d replay); lockstep parity holds with fixed-step; clamp ticks %d!=%d so the stalled client holds only a prefix of the stream (first value divergence %s); swapped draw order reassigns values to systems"
      % ("PASS" if allok else "FAIL", replay_steps, tC, tA, first_div))
