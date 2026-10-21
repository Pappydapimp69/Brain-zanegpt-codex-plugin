"""Prediction (before run): with sfc32 (four 32-bit state words) as the only random source:
(1) saving the 4 state words and restoring gives the identical next 10,000 rolls (0 mismatches) in O(1) work (4 words),
    while a {seed,count} save needs `count` rolls of replay (I predict exactly count generator calls, 50,000 for count=50,000);
(2) two lockstep clients fed the same seed and the same command list stay byte-identical after 5,000 ticks;
(3) BUILT TO BREAK: if ONE client makes an extra roll in its render path (e.g. a particle effect) the streams diverge from the
    first tick after it and never reconverge (I predict >= 99 percent of later rolls differ); the same extra roll taken from a
    SECOND private generator leaves the authoritative stream identical;
(4) canonical (sorted-key) serialization gives the same hash for equal state regardless of key insertion order, plain
    insertion-order serialization gives different hashes for the same state (the-game-prologue/E1).
Deterministic, stdlib only, integer arithmetic only."""
import hashlib, json
M = 0xFFFFFFFF
class Sfc32:
    def __init__(self, a, b, c, d):
        self.s = [a & M, b & M, c & M, d & M]; self.calls = 0
        for _ in range(12): self.next()
        self.calls = 0
    def next(self):
        a, b, c, d = self.s; self.calls += 1
        t = (a + b) & M
        a = b ^ (b >> 9)
        b = (c + ((c << 3) & M)) & M
        c = (((c << 21) & M) | (c >> 11))
        d = (d + 1) & M
        t = (t + d) & M
        c = (c + t) & M
        self.s = [a, b, c, d]
        return t
    def state(self): return list(self.s)
    def load(self, s): self.s = list(s)
def seeded(seed): return Sfc32(0x9E3779B9, 0x243F6A88, 0xB7E15162, seed)
ok = True
# 1 save/restore
g = seeded(42)
for _ in range(50000): g.next()
saved = g.state(); want = [g.next() for _ in range(10000)]
h = seeded(7); h.load(saved); got = [h.next() for _ in range(10000)]
mism = sum(a != b for a, b in zip(want, got))
r = seeded(42); r.calls = 0
for _ in range(50000): r.next()
replay_calls = r.calls
rr = [r.next() for _ in range(10000)]
print("state-word load mismatches", mism, "| words stored", len(saved), "| replay calls for count=50000:", replay_calls, "| replay path matches:", rr == want)
ok &= mism == 0 and replay_calls == 50000 and rr == want
# 2 lockstep
A, B = seeded(99), seeded(99); cmds = [(i * 7919) % 5 for i in range(5000)]
sa = [A.next() % 100 + c for c in cmds]; sb = [B.next() % 100 + c for c in cmds]
print("lockstep identical", sa == sb); ok &= sa == sb
# 3 break: extra roll in one client's render path
A, B = seeded(99), seeded(99); da = db = 0; diverged = None; later = same = 0
for t in range(5000):
    if t == 1000: B.next()                   # render-side roll taken from the SHARED stream
    x, y = A.next(), B.next()
    if x != y and diverged is None: diverged = t
    if t > 1000: later += 1; same += (x == y)
print("shared-stream extra roll: first divergence tick", diverged, "| later ticks still equal", same, "of", later)
ok &= diverged == 1000 and same / later < 0.01
A, B, priv = seeded(99), seeded(99), seeded(5); eq = True
for t in range(5000):
    if t == 1000: priv.next()                # render roll from a private generator
    eq &= A.next() == B.next()
print("private render generator keeps authoritative streams equal:", eq); ok &= eq
# 4 canonical serialization
s1 = {"hp": 10, "pos": [1, 2], "rng": saved}; s2 = {"rng": saved, "pos": [1, 2], "hp": 10}
h = lambda d, sk: hashlib.sha256(json.dumps(d, sort_keys=sk, separators=(",", ":")).encode()).hexdigest()[:12]
print("canonical hashes equal", h(s1, True) == h(s2, True), "| insertion-order hashes equal", h(s1, False) == h(s2, False))
ok &= h(s1, True) == h(s2, True) and h(s1, False) != h(s2, False)
print("RESULT: %s restore mismatches %d with %d words vs %d replay calls; extra shared roll diverges at tick %s with %d of %d later ticks equal; private generator keeps streams equal; canonical hash stable" %
      ("PASS" if ok else "FAIL", mism, len(saved), replay_calls, diverged, same, later))
