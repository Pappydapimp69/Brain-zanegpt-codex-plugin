"""Sandbox: ideas:SYSTEM/determinism/seeded-rng/save-replay-coop-from-one-stream.
sfc32 PRNG (32-bit, stdlib only). No ambient randomness. Seeds are fixed integers 1..8.
PREDICTION (written before run 1), 8 seeds:
 P1 restoring from 4 saved state words reproduces the next 100 rolls in 8/8 seeds at a cost of 4 word copies,
    while a count-replay load costs `count` rolls (50000 here) and also reproduces them 8/8 when every roll is counted.
 P2 one UNCOUNTED draw (a roll made through a path that does not bump the counter) makes the count-replay load
    diverge in 8/8 seeds, while the state-word load stays exact 8/8.
 P3 one extra roll inserted before a combat roll in a SINGLE shared stream changes that combat roll in >= 7/8 seeds
    and shifts every later roll by one position (8/8 seeds).
 P4 with per-subsystem streams (seed mixed with a subsystem name) the same insertion in the spawn stream changes the
    combat roll in 0/8 seeds.
 P5 (BREAK) inserting the extra roll into the COMBAT stream itself still changes the combat roll in >= 7/8 seeds:
    splitting isolates subsystems, it does not make a stream order-insensitive.
"""
import hashlib
M = 0xFFFFFFFF
class Sfc32:
    def __init__(self, a, b, c, d):
        self.s = [a & M, b & M, c & M, d & M]; self.counter = 1; self.count = 0
    @classmethod
    def seeded(cls, seed, name=""):
        h = hashlib.sha256(("%d:%s" % (seed, name)).encode()).digest()
        w = [int.from_bytes(h[i:i + 4], "big") for i in (0, 4, 8, 12)]
        r = cls(w[0], w[1], w[2], 1)
        r.counter = 1
        for _ in range(12): r.u32(count=False)
        return r
    def u32(self, count=True):
        a, b, c, d = self.s
        t = (a + b + d) & M
        self.s = [b ^ (b >> 9), (c + (c << 3)) & M, ((c << 21 | c >> 11) + t) & M, (d + 1) & M]
        if count: self.count += 1
        return t
    def state(self): return tuple(self.s)
    def load(self, st): self.s = list(st)

ok = True
SEEDS = range(1, 9)
# S1 + S2
s1 = s2 = 0; replay_cost = 0
for sd in SEEDS:
    r = Sfc32.seeded(sd)
    for _ in range(50000 - 1): r.u32()
    r.u32(count=False)              # one uncounted draw (leaked helper): count says 49999, state is 50000 deep
    saved_state, saved_count = r.state(), r.count
    want = [r.u32() for _ in range(100)]
    a = Sfc32.seeded(sd); a.load(saved_state); got_state = [a.u32() for _ in range(100)]
    b = Sfc32.seeded(sd)
    for _ in range(saved_count): b.u32()
    got_count = [b.u32() for _ in range(100)]
    s1 += got_state == want; s2 += got_count != want; replay_cost = saved_count
print("S1/S2 state-word load exact %d/8 ; count-replay load diverges %d/8 with one uncounted draw (replay cost %d rolls vs 4 words)" % (s1, s2, replay_cost))
# counted-only control: count replay is exact when every roll is counted
ctrl = 0
for sd in SEEDS:
    r = Sfc32.seeded(sd)
    for _ in range(5000): r.u32()
    st, cn = r.state(), r.count
    want = [r.u32() for _ in range(50)]
    b = Sfc32.seeded(sd)
    for _ in range(cn): b.u32()
    ctrl += [b.u32() for _ in range(50)] == want
print("S1 control: count replay exact when every roll counted: %d/8" % ctrl)
ok &= s1 == 8 and s2 == 8 and ctrl == 8
# S3 shared stream insertion
def run_shared(sd, extra):
    r = Sfc32.seeded(sd)
    pre = [r.u32() for _ in range(5)]
    if extra: r.u32()                     # quest accepted -> a spawn roll that the other timeline never makes
    return [r.u32() for _ in range(6)]    # combat rolls
ch = sh = 0
for sd in SEEDS:
    base, alt = run_shared(sd, False), run_shared(sd, True)
    ch += base[0] != alt[0]; sh += base[1:] == alt[:-1]
print("S3 shared stream: combat roll changed %d/8 ; later rolls exactly shifted by one %d/8" % (ch, sh))
ok &= ch >= 7 and sh == 8
# S4 split streams
def run_split(sd, extra, into):
    spawn, combat = Sfc32.seeded(sd, "spawn"), Sfc32.seeded(sd, "combat")
    for _ in range(5): spawn.u32()
    if extra: (spawn if into == "spawn" else combat).u32()
    return [combat.u32() for _ in range(6)]
c4 = c5 = 0
for sd in SEEDS:
    c4 += run_split(sd, False, "spawn")[0] != run_split(sd, True, "spawn")[0]
    c5 += run_split(sd, False, "combat")[0] != run_split(sd, True, "combat")[0]
print("S4 split streams, extra roll in spawn stream: combat roll changed %d/8 ; S5 extra roll in the combat stream itself: %d/8" % (c4, c5))
ok &= c4 == 0 and c5 >= 7
print("RESULT: %s state words reload exact 8/8 in O(1) and survive an uncounted draw (count replay broke 8/8); shared stream perturbed %d/8, split streams 0/8, but a roll inside the same stream still shifts it %d/8" % ("PASS" if ok else "FAIL", ch, c5))
