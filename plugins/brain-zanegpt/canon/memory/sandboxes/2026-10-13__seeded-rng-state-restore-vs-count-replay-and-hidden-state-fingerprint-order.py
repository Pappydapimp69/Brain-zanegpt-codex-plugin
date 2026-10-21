"""Prediction (before run): (1) restoring a mulberry32 generator from its 32-bit state costs 1 step and gives the same next 5
draws as replaying count rolls, which costs count steps (1000, 20000, 200000); (2) a state hash over insertion-ordered JSON
differs for two logically identical states built in different key order, while a sorted-key canonical hash matches;
(3) BUILT TO BREAK: a generator with a cached spare gaussian has hidden state, so restoring only {state} diverges on the next
gaussian after an odd number of gaussian draws (predict diverge at odd, match at even), while count replay stays correct.
Deterministic, stdlib only."""
import json, hashlib
M = 0xFFFFFFFF

class Mulberry:
    def __init__(self, seed): self.s = seed & M; self.steps = 0; self.spare = None
    def next(self):
        self.steps += 1
        self.s = (self.s + 0x6D2B79F5) & M
        t = self.s
        t = ((t ^ (t >> 15)) * (t | 1)) & M
        t ^= (t + (((t ^ (t >> 7)) * (t | 61)) & M)) & M
        return ((t ^ (t >> 14)) & M) / 4294967296
    def gauss(self):
        if self.spare is not None:
            v, self.spare = self.spare, None; return v
        import math
        u, v = self.next() or 1e-9, self.next()
        r = math.sqrt(-2 * math.log(u)); self.spare = r * math.sin(2 * math.pi * v)
        return r * math.cos(2 * math.pi * v)

def replay(seed, count):
    g = Mulberry(seed)
    for _ in range(count): g.next()
    return g

ok = True
# 1) restore cost and equality
for n in (1000, 20000, 200000):
    live = Mulberry(7)
    for _ in range(n): live.next()
    saved = live.s
    cost_replay = replay(7, n).steps; cost_state = 1
    la = replay(7, n); lb = Mulberry(0); lb.s = saved
    same = [la.next() for _ in range(5)] == [lb.next() for _ in range(5)]
    print("restore n=%d replay_steps=%d state_steps=%d same=%s" % (n, cost_replay, cost_state, same))
    ok &= same and cost_replay == n
# 2) fingerprint order
A = {"hp": 5, "pos": {"x": 1, "y": 2}, "7": "a"}
B = {"7": "a", "pos": {"y": 2, "x": 1}, "hp": 5}
naive = lambda d: hashlib.sha256(json.dumps(d).encode()).hexdigest()[:8]
canon = lambda d: hashlib.sha256(json.dumps(d, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:8]
print("naive", naive(A), naive(B), "canonical", canon(A), canon(B))
ok &= naive(A) != naive(B) and canon(A) == canon(B)
# 3) hidden spare state
res = {}
for k in (1, 2, 3, 4):
    live2 = Mulberry(11)
    for _ in range(k): live2.gauss()
    st2 = Mulberry(0); st2.s = live2.s
    res[k] = (st2.gauss() == live2.gauss())
print("state-only restore matches next gaussian after k draws:", res)
ok &= res == {1: False, 2: True, 3: False, 4: True}
print("RESULT: %s state restore 1 step vs replay n steps with equal draws (n=1000,20000,200000); naive hash differs %s canonical %s; spare-gaussian state-only restore matches only at even draw counts %s" %
      ("PASS" if ok else "FAIL", naive(A) != naive(B), canon(A) == canon(B), res))
