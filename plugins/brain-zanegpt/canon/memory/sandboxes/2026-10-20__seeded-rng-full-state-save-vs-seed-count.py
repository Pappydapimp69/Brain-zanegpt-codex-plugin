import json, hashlib
M = 0xFFFFFFFF
class Sfc32:
    def __init__(s, a, b, c, d): s.st = [a & M, b & M, c & M, d & M]
    @classmethod
    def seeded(cls, seed):
        r = cls(0, seed, seed * 7 + 1, 1); [r.next() for _ in range(15)]; return r
    def next(s):
        a, b, c, d = s.st
        t = (a + b + d) & M
        d = (d + 1) & M
        a = b ^ (b >> 9)
        b = (c + (c << 3)) & M
        c = (((c << 21) | (c >> 11)) & M) + t & M
        s.st = [a, b, c, d]
        return t
work = {"calls": 0}
def roll(r):
    work["calls"] += 1; return r.next()
# S1: {seed,count} vs full-state save after N rolls; compare cost and next 5 rolls
def scenario(N):
    r = Sfc32.seeded(42); [r.next() for _ in range(N)]
    saved_state = list(r.st); saved_sc = (42, N)
    want = [r.next() for _ in range(5)]
    work["calls"] = 0
    r2 = Sfc32(*saved_state); got_state = [roll(r2) for _ in range(5)]; cost_state = work["calls"] - 5
    work["calls"] = 0
    r3 = Sfc32.seeded(saved_sc[0]); [roll(r3) for _ in range(saved_sc[1])]; got_sc = [roll(r3) for _ in range(5)]; cost_sc = work["calls"] - 5
    return got_state == want, got_sc == want, cost_state, cost_sc
res = {N: scenario(N) for N in (10, 1000, 100000)}
for N, v in res.items(): print("N", N, "state-save exact", v[0], "seed+count exact", v[1], "restore rolls: state", v[2], "seed+count", v[3])
# S2: canonical hash: insertion order vs sorted keys
s1 = {"b": 1, "a": 2, "rng": [1, 2, 3, 4]}; s2 = {"rng": [1, 2, 3, 4], "a": 2, "b": 1}
h = lambda o, sk: hashlib.sha256(json.dumps(o, sort_keys=sk).encode()).hexdigest()[:8]
raw_equal = h(s1, False) == h(s2, False); canon_equal = h(s1, True) == h(s2, True)
print("S2 same logical state: raw dumps hash equal", raw_equal, "canonical equal", canon_equal)
# S3 BREAK: state saved as full words but game also keeps a call counter outside RNG state; a replay branch mismatch
r = Sfc32.seeded(7); [r.next() for _ in range(50)]; snap = list(r.st)
a = Sfc32(*snap); b = Sfc32(*snap); b.next()      # one extra roll on a client => lockstep desync
desync = [a.next() for _ in range(3)] != [b.next() for _ in range(3)]
print("S3 one extra roll on one client desyncs the stream:", desync)
ok = all(v[0] and v[1] for v in res.values()) and res[100000][2] == 0 and res[100000][3] == 100000 and not raw_equal and canon_equal and desync
print(("RESULT: PASS " if ok else "RESULT: FAIL ") + f"full-state restore 0 rolls vs seed+count {res[100000][3]} at N=100000, both exact; raw-order hash equal={raw_equal}, canonical equal={canon_equal}; one extra roll desyncs={desync}")
