# Rebuild from the claim only. Own fixture: xorshift128 (4 x 32-bit words) plus a
# Box-Muller gaussian wrapper that caches its second value.
# Prediction (before run): bare generator: words restore (4 copies) is exact after
# 10, 777 and 20000 draws and equals replaying n rolls; gaussian wrapper: words-only
# restore diverges on the first post-load draw when the cache is non-empty (odd draw
# count) and is fine when empty (even count); saving the cache too fixes it; replay by
# GAUSSIAN-draw count also works (so the claim's seed-plus-count failure depends on
# counting raw rolls instead).
import math

M = 0xFFFFFFFF

class X128:
    def __init__(self, seed):
        s = seed & M
        self.w = []
        for _ in range(4):
            s = (s * 1664525 + 1013904223) & M
            self.w.append(s or 1)
    def next(self):
        x, y, z, w = self.w
        t = (x ^ (x << 11)) & M
        nw = (w ^ (w >> 19) ^ t ^ (t >> 8)) & M
        self.w = [y, z, w, nw]
        return nw
    def uni(self):
        return (self.next() + 0.5) / 4294967296.0

class Gauss:
    def __init__(self, seed):
        self.g = X128(seed); self.cache = None; self.raw = 0
    def draw(self):
        if self.cache is not None:
            v, self.cache = self.cache, None
            return v
        u1, u2 = self.g.uni(), self.g.uni(); self.raw += 2
        r = math.sqrt(-2 * math.log(u1))
        self.cache = r * math.sin(2 * math.pi * u2)
        return r * math.cos(2 * math.pi * u2)

# bare generator: states after identical continuations
bare_ok = True
for n in (10, 777, 20000):
    a = X128(5)
    for _ in range(n): a.next()
    b = X128(0); b.w = list(a.w)
    bare_ok &= all(a.next() == b.next() for _ in range(50))
# gaussian wrapper
def run(n, save_cache, replay=None):
    a = Gauss(11)
    for _ in range(n): a.draw()
    b = Gauss(0); b.g.w = list(a.g.w); b.cache = a.cache if save_cache else None
    return all(abs(a.draw() - b.draw()) < 1e-15 for _ in range(6))
odd_words_only = run(777, False)       # odd count -> cache full
even_words_only = run(776, False)      # even -> cache empty
odd_with_cache = run(777, True)
# replay by gaussian-draw count (seed + count) and by raw-roll count
a = Gauss(11)
for _ in range(777): a.draw()
r = Gauss(11)
for _ in range(777): r.draw()
by_draws = all(abs(a.draw() - r.draw()) < 1e-15 for _ in range(6))
a = Gauss(11)
for _ in range(777): a.draw()
raw = a.raw                                # 778 raw rolls
r = Gauss(11)
for _ in range(raw): r.g.next()            # replay raw rolls, wrapper cache lost
by_raw = all(abs(a.draw() - r.draw()) < 1e-15 for _ in range(6))
print("bare_ok=%s odd_words_only_ok=%s even_words_only_ok=%s odd_with_cache_ok=%s replay_by_draws_ok=%s replay_by_raw_ok=%s"
      % (bare_ok, odd_words_only, even_words_only, odd_with_cache, by_draws, by_raw))
ok = bare_ok and (not odd_words_only) and even_words_only and odd_with_cache and by_draws and (not by_raw)
print("RESULT: %s words restore exact for bare generator; gaussian words-only restore diverges when cache is full (odd count) and not when empty; saving cache fixes; replay by gaussian-draw count works, replay by raw-roll count diverges" % ("PASS" if ok else "FAIL"))
