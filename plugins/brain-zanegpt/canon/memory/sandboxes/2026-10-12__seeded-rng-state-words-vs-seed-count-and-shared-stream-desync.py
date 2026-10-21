"""Seeded RNG kernel check: sfc32 (stdlib only, 32-bit ints, no floats).
1) save 4 state words mid-run -> restore gives identical next rolls; {seed,count} restore costs count draws.
2) replay fingerprint: same seed + script twice -> same hash; one leaked ambient-order change -> different hash.
3) BREAK: ONE shared stream means a cosmetic roll on one lockstep client desyncs the sim; a separate cosmetic stream keeps sim identical.
4) canonical-hash: JSON with insertion-ordered keys hashes differently for equal states unless keys are sorted."""
import json, hashlib
M = 0xFFFFFFFF
class Sfc32:
    draws = 0
    def __init__(s, a, b, c, d): s.st = [a & M, b & M, c & M, d & M]
    @classmethod
    def seeded(cls, seed):
        r = cls(0x9E3779B9, 0x243F6A88, 0xB7E15162, seed)
        for _ in range(15): r.next()
        r.reset_count(); return r
    def reset_count(s): s.draws = 0
    def next(s):
        a, b, c, d = s.st
        t = (a + b + d) & M
        d = (d + 1) & M
        a = b ^ (b >> 9); b = (c + (c << 3)) & M
        c = ((c << 21 | c >> 11) & M); c = (c + t) & M
        s.st = [a, b, c, d]; s.draws += 1
        return t
    def roll(s, n): return s.next() % n

def sim(rng, steps, cosmetic=None):
    pos, log = 0, []
    for i in range(steps):
        if cosmetic is not None and i % 5 == 0: cosmetic.next()      # particle effect
        pos += rng.roll(7) - 3; log.append(pos)
    return pos, log
def fp(obj): return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:12]

# 1) state-word save/restore vs seed+count replay
r = Sfc32.seeded(2024); sim(r, 500)
saved = list(r.st); count = r.draws
cont = [r.roll(1000) for _ in range(1000)]
r2 = Sfc32(*saved); same_state = [r2.roll(1000) for _ in range(1000)] == cont
r3 = Sfc32.seeded(2024); r3.reset_count()
for _ in range(count): r3.next()
replay_cost = r3.draws
same_replay = [r3.roll(1000) for _ in range(1000)] == cont
print("1) state-words identical:", same_state, "restore cost 0 draws; seed+count replay identical:", same_replay, "cost", replay_cost)
s1 = same_state and same_replay and replay_cost == count == 500

# 2) replay fingerprint
a = fp(sim(Sfc32.seeded(7), 300)); b = fp(sim(Sfc32.seeded(7), 300)); c = fp(sim(Sfc32.seeded(8), 300))
class Leaky(Sfc32):
    def roll(s, n):
        return (super().roll(n) + (1 if s.draws == 150 else 0)) % n   # a leaked ambient source at one step
d = fp(sim(Leaky.seeded(7), 300))
print("2) same-seed equal:", a == b, "other seed differs:", a != c, "leak differs:", a != d)
s2 = a == b and a != c and a != d

# 3) BREAK: shared stream vs split streams under a cosmetic roll on one client
def client(shared, with_fx):
    sim_rng = Sfc32.seeded(11)
    fx = sim_rng if shared else Sfc32.seeded(99)
    return sim(sim_rng, 200, cosmetic=fx if with_fx else None)[0]
shared_desync = client(True, False) != client(True, True)
split_ok = client(False, False) == client(False, True)
print("3) shared stream desync with cosmetic roll:", shared_desync, "| split streams stay in sync:", split_ok)
s3 = shared_desync and split_ok

# 4) canonical hash
s_a = {"b": 1, "a": 2}; s_b = {"a": 2, "b": 1}
naive_diff = hashlib.sha256(json.dumps(s_a).encode()).hexdigest() != hashlib.sha256(json.dumps(s_b).encode()).hexdigest()
canon_same = fp(s_a) == fp(s_b)
print("4) insertion-order hash differs:", naive_diff, "| sorted-key hash equal:", canon_same)
s4 = naive_diff and canon_same
ok = s1 and s2 and s3 and s4
print("RESULT: %s state-word restore 0 draws vs replay %d, fingerprint catches leak, shared stream desyncs on 1 cosmetic roll (split streams fix), sorted-key hash needed" % ("PASS" if ok else "FAIL", replay_cost))
