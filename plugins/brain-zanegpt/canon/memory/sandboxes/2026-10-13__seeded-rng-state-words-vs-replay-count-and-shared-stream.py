# Prediction (before run): sfc32 saved as 4 state words restores with 0 replayed draws and the next 1000 rolls
# match an uninterrupted run; a {seed,count} save needs count draws on load (count=250000 -> 250000 draws).
# Canonical sorted-key JSON gives one hash for 24 insertion orders of a 4-key state, plain json.dumps gives 24.
# BREAK: if a cosmetic consumer (particles) draws from the same stream, two runs with different particle counts
# diverge in sim outcome (fingerprint mismatch) even with identical seeds and inputs; routing cosmetics to a
# separate stream restores a single fingerprint.
import json, itertools, hashlib
M = 0xFFFFFFFF
class Sfc32:
    def __init__(self, a, b, c, d): self.s = [a & M, b & M, c & M, d & M]; self.draws = 0
    @classmethod
    def seeded(cls, seed):
        r = cls(0, seed, seed * 2654435761 & M, 1)
        for _ in range(12): r.next()
        r.draws = 0; return r
    def next(self):
        a, b, c, d = self.s
        t = (a + b + d) & M; d = (d + 1) & M
        a = b ^ (b >> 9); b = (c + (c << 3)) & M
        c = ((c << 21 | c >> 11) & M) + t & M
        self.s = [a, b, c, d]; self.draws += 1; return t
def run_to(seed, n):
    r = Sfc32.seeded(seed)
    for _ in range(n): r.next()
    return r
N = 250000
orig = run_to(7, N)
state = list(orig.s)
loaded = Sfc32(*state)                       # O(1)
nxt_a = [orig.next() for _ in range(1000)]
nxt_b = [loaded.next() for _ in range(1000)]
replayed = Sfc32.seeded(7)
for _ in range(N): replayed.next()           # {seed,count} load
print("S1 state-words load draws 0, next-1000 equal %s; seed+count load draws %d" % (nxt_a == nxt_b, replayed.draws))
base = {"hp": 10, "5": 1, "gold": 3, "2": 9}
def h(obj, canon):
    return hashlib.sha256(json.dumps(obj, sort_keys=canon).encode()).hexdigest()[:8]
plain, canon = set(), set()
for perm in itertools.permutations(base):
    o = {k: base[k] for k in perm}
    plain.add(h(o, False)); canon.add(h(o, True))
print("S2 hashes over 24 insertion orders: plain %d canonical %d" % (len(plain), len(canon)))
def fingerprint(share, particles):
    sim = Sfc32.seeded(11); cos = sim if share else Sfc32.seeded(99)
    hp = 100
    for step in range(60):
        for _ in range(particles): cos.next()
        hp -= sim.next() % 7
    return hp
fp_shared = {fingerprint(True, p) for p in (0, 3, 10)}
fp_split = {fingerprint(False, p) for p in (0, 3, 10)}
print("S3 BREAK shared stream fingerprints over particle counts %s split %s" % (sorted(fp_shared), sorted(fp_split)))
ok = nxt_a == nxt_b and replayed.draws == N and len(plain) > 1 and len(canon) == 1 and len(fp_shared) > 1 and len(fp_split) == 1
print("RESULT: %s state-word load 0 draws vs %d for seed+count; hashes plain %d vs canonical %d; shared stream gave %d fingerprints over particle counts, split stream %d"
      % ("PASS" if ok else "FAIL", replayed.draws, len(plain), len(canon), len(fp_shared), len(fp_split)))
