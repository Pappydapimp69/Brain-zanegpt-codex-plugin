"""Sandbox: seeded-rng kernel - save state words vs {seed,count}, replay, and the cost of ONE shared stream.

PREDICTION (written before the first run):
  P1. sfc32 saved as 4 state words, restored mid-run, continues identically for 1000 rolls (0 mismatches),
      at a restore cost of 0 extra rolls; {seed,count} restore also matches but costs exactly `count` rolls
      (100000 rolls at count=100000).
  P2. Replaying the whole session from the seed reproduces every roll (0 mismatches over 5000).
  P3. (break) With ONE shared stream, inserting a single cosmetic roll before turn 10 changes the gameplay
      outcome on at least 90% of later turns. Giving each subsystem its own stream derived from the seed
      leaves gameplay unchanged (0 mismatches) when the cosmetic roll is added.
  P4. (break) If the saved state words are not masked to 32 bits (a signed-int round trip), the restored stream diverges
      within 10 rolls.
"""
M = 0xFFFFFFFF

class SFC32:
    def __init__(self, a, b, c, d):
        self.s = [a & M, b & M, c & M, d & M]
        self.calls = 0
    @classmethod
    def seeded(cls, seed):
        r = cls(0, seed & M, (seed * 2654435761) & M, 1)
        for _ in range(12):
            r.next()
        r.calls = 0
        return r
    def next(self):
        a, b, c, d = self.s
        t = (a + b + d) & M
        d = (d + 1) & M
        a = b ^ (b >> 9)
        b = (c + (c << 3)) & M
        c = ((c << 21 | c >> 11) & M)
        c = (c + t) & M
        self.s = [a, b, c, d]
        self.calls += 1
        return t
    def save(self):
        return list(self.s)

def to_signed(x):
    return x - (1 << 32) if x >= (1 << 31) else x

res = []
SEED = 20261009

# S1 save/restore
r = SFC32.seeded(SEED)
COUNT = 100000
for _ in range(COUNT):
    r.next()
saved_words = r.save()
ref = [r.next() for _ in range(1000)]
w = SFC32(*saved_words)
got_w = [w.next() for _ in range(1000)]
c = SFC32.seeded(SEED)
for _ in range(COUNT):
    c.next()
replay_cost = c.calls
got_c = [c.next() for _ in range(1000)]
mm_w = sum(a != b for a, b in zip(ref, got_w))
mm_c = sum(a != b for a, b in zip(ref, got_c))
print("S1 state words: mismatches=%d restore rolls=0 | seed+count: mismatches=%d restore rolls=%d" % (mm_w, mm_c, replay_cost))
res.append(mm_w == 0 and mm_c == 0 and replay_cost == COUNT)

# S2 replay from seed
a = SFC32.seeded(SEED); b = SFC32.seeded(SEED)
mm = sum(a.next() != b.next() for _ in range(5000))
print("S2 replay from seed mismatches over 5000:", mm)
res.append(mm == 0)

# S3 shared stream coupling
def session(extra_cosmetic, separate):
    gp = SFC32.seeded(SEED)
    cos = SFC32.seeded(SEED ^ 0xABCDEF) if separate else gp
    out = []
    for turn in range(100):
        if extra_cosmetic and turn == 10:
            cos.next()            # one added particle roll
        cos.next()                # one existing cosmetic roll every turn
        out.append(gp.next() % 20)   # gameplay roll
    return out
base_shared = session(False, False); mod_shared = session(True, False)
base_sep = session(False, True); mod_sep = session(True, True)
later = range(10, 100)
diff_shared = sum(base_shared[i] != mod_shared[i] for i in later) / 90
diff_sep = sum(base_sep[i] != mod_sep[i] for i in range(100))
print("S3 shared stream: %.0f%% of later gameplay rolls changed; separate streams: %d changed" % (100 * diff_shared, diff_sep))
res.append(diff_shared >= 0.9 and diff_sep == 0)

# S4 signed round trip
bad = SFC32.__new__(SFC32)
bad.s = [to_signed(x) for x in saved_words]   # unmasked: arithmetic now sees negative ints
bad.calls = 0
def next_unmasked(o):
    a, b, c, d = o.s
    t = (a + b + d)
    d = d + 1
    a = b ^ (b >> 9)
    b = (c + (c << 3))
    c = (c << 21 | c >> 11)
    c = c + t
    o.s = [a, b, c, d]
    return t & M
first_div = None
for i in range(1000):
    if next_unmasked(bad) != ref[i]:
        first_div = i; break
print("S4 signed/unmasked restore first divergence at roll:", first_div)
res.append(first_div is not None and first_div < 10)

print("RESULT: %s state-word restore cost 0 rolls vs %d for seed+count, both bit-exact; one extra cosmetic roll changed %.0f%% of later gameplay rolls on a shared stream and 0 on split streams; unmasked words diverged at roll %s"
      % ("PASS" if all(res) else "FAIL", replay_cost, 100 * diff_shared, first_div))
