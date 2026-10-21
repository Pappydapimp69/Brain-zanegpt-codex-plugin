"""sfc32 seeded RNG: (a) save the 4 state words vs {seed,count} replay, (b) replay-fingerprint of a run,
(c) BREAK: one shared stream vs per-system substreams when a roll is INSERTED in the loot system.
PREDICTION (before run): saving state words restores the next 100 rolls bit-identically with 0 replayed
rolls (count replay needs N); two runs from one seed have equal fingerprints; with ONE shared stream,
inserting a single extra loot roll at tick 5 changes >= 90% of the later combat rolls and the run
fingerprint; with per-system substreams (seeded from hash(seed, name)) combat rolls and combat
fingerprint stay identical (0 changed), only loot changes."""
import hashlib
M = 0xFFFFFFFF
class Sfc32:
    def __init__(s, a, b, c, d):
        s.a, s.b, s.c, s.d = a & M, b & M, c & M, d & M; s.rolls = 0
        for _ in range(12): s.next()
        s.rolls = 0
    def next(s):
        t = (s.a + s.b + s.d) & M; s.d = (s.d + 1) & M
        s.a = s.b ^ (s.b >> 9); s.b = (s.c + (s.c << 3)) & M
        s.c = (((s.c << 21) | (s.c >> 11)) & M) + t & M
        s.rolls += 1
        return t
    def state(s): return (s.a, s.b, s.c, s.d)
    def load(s, st): s.a, s.b, s.c, s.d = st
def seeded(seed, name=""):
    h = hashlib.sha256(("%d:%s" % (seed, name)).encode()).digest()
    return Sfc32(*[int.from_bytes(h[i*4:i*4+4], "big") for i in range(4)])
def fp(seq): return hashlib.sha256(repr(seq).encode()).hexdigest()[:12]

# (a) save/load vs count replay
r = seeded(7); [r.next() for _ in range(500)]
saved, cnt = r.state(), r.rolls
after = [r.next() for _ in range(100)]
r2 = seeded(7); r2.load(saved); load_rolls = r2.rolls
same_a = [r2.next() for _ in range(100)] == after
r3 = seeded(7); [r3.next() for _ in range(cnt)]; replay_rolls = r3.rolls
same_a2 = [r3.next() for _ in range(100)] == after
# (b) replay fingerprint
def run_single(seed, insert_at=None, ticks=60):
    rng = seeded(seed); combat = []; loot = []
    for t in range(ticks):
        combat.append(rng.next() % 20)
        if t == insert_at: loot.append(rng.next() % 100)       # the inserted extra loot roll
        loot.append(rng.next() % 100)
    return combat, loot
def run_split(seed, insert_at=None, ticks=60):
    rc, rl = seeded(seed, "combat"), seeded(seed, "loot"); combat = []; loot = []
    for t in range(ticks):
        combat.append(rc.next() % 20)
        if t == insert_at: loot.append(rl.next() % 100)
        loot.append(rl.next() % 100)
    return combat, loot
b1, b2 = run_single(7), run_single(7); same_b = fp(b1) == fp(b2)
s0, s1 = run_single(7), run_single(7, insert_at=5)
changed_single = sum(1 for t in range(6, 60) if s0[0][t] != s1[0][t]) / 54
p0, p1 = run_split(7), run_split(7, insert_at=5)
changed_split = sum(1 for t in range(60) if p0[0][t] != p1[0][t])
print("(a) state-word load: %d rolls to restore, identical next-100: %s; count replay: %d rolls, identical: %s" % (load_rolls, same_a, replay_rolls, same_a2))
print("(b) fingerprint equal across two runs: %s (%s)" % (same_b, fp(b1)))
print("(c) shared stream: %.0f%% of later combat rolls changed, fingerprint %s -> %s" % (100*changed_single, fp(s0), fp(s1)))
print("    split streams: %d combat rolls changed, combat fp %s -> %s, loot changed: %s" % (changed_split, fp(p0[0]), fp(p1[0]), p0[1] != p1[1]))
ok = (same_a and same_a2 and load_rolls == 0 and replay_rolls == 500 and same_b and changed_single >= 0.9
      and fp(s0) != fp(s1) and changed_split == 0 and fp(p0[0]) == fp(p1[0]) and p0[1] != p1[1])
print("RESULT: %s state-word load 0 rolls vs 500 replayed, same next 100; shared stream %.0f%% of later combat rolls shifted by one inserted roll, split streams 0" % ("PASS" if ok else "FAIL", 100*changed_single))
