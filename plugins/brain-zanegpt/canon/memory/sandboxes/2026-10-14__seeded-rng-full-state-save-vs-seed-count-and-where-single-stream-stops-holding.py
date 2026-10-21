"""Sandbox: ideas:SYSTEM/determinism/seeded-rng claims, deterministic, stdlib only.
Prediction (written before first run):
 S1 full-state restore continues identically to uninterrupted run, cost 4 words;
    {seed,count} restore matches too but replays `count` rolls (10000 for count=10000).
 S2 one leaked ambient roll makes the same seed produce different worlds 3/3 times
    when the ambient source differs; persisting only outputs (bits) loses the seed.
 S3 (BREAK) a frame-count seed at a player-triggered roll lets a brute-force delay
    pick ALL 6 outcomes: a single seeded stream does not stop manipulation.
 S4 (BREAK) two lockstep clients on the same seed diverge once they consume rolls
    in a different ORDER (cosmetic roll before gameplay roll): same stream is not enough.
"""
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
    def roll(s, n): return s.next() % n

def run_world(rng, n=50): return [rng.roll(6) for _ in range(n)]
ok = True

# S1: save/load
r = Sfc32(42); pre = run_world(r, 10000); saved = r.state(); cont_ref = run_world(r, 100)
r2 = Sfc32(0); r2.load(saved); full_ok = run_world(r2, 100) == cont_ref
r3 = Sfc32(42); replay_cost = 0
for _ in range(10000): r3.next(); replay_cost += 1
seedcount_ok = run_world(r3, 100) == cont_ref
print(f"S1 full-state-restore identical={full_ok} cost=4 words; seed+count identical={seedcount_ok} cost={replay_cost} rolls")
ok &= full_ok and seedcount_ok and replay_cost == 10000

# S2: ambient leak
def world_with_leak(seed, ambient):
    g = Sfc32(seed); w = run_world(g, 20)
    w[7] = ambient % 6                      # one leaked non-seeded roll
    return w
clean = [run_world(Sfc32(7), 20) for _ in range(3)]
leaky = [world_with_leak(7, a) for a in (11, 12, 14)]
clean_same = all(c == clean[0] for c in clean)
leak_distinct = len({tuple(w) for w in leaky})
print(f"S2 clean same-seed worlds identical={clean_same}; leaky same-seed worlds distinct={leak_distinct}/3")
ok &= clean_same and leak_distinct == 3

# S3 BREAK: frame-count seeding is manipulable
reach = {}
for delay in range(2000):
    o = Sfc32(delay).roll(6)
    reach.setdefault(o, delay)
print(f"S3 outcomes selectable by frame delay: {len(reach)}/6 (first delays {dict(sorted(reach.items()))})")
ok &= len(reach) == 6

# S4 BREAK: lockstep order sensitivity
def client(order_cosmetic_first):
    g = Sfc32(99); out = []
    for _ in range(30):
        if order_cosmetic_first: g.next()            # particle jitter roll
        out.append(g.roll(20))                       # gameplay damage roll
        if not order_cosmetic_first: g.next()
    return out
a, b = client(False), client(True)
diff = sum(x != y for x, y in zip(a, b))
print(f"S4 same seed, different consumption order: gameplay rolls differ {diff}/30")
ok &= diff >= 20

print(("RESULT: PASS" if ok else "RESULT: FAIL") +
      f" full-state {full_ok} cost 4 vs {replay_cost}; leak distinct {leak_distinct}/3; frame-seed manipulable {len(reach)}/6; order divergence {diff}/30")
