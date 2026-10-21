import json, hashlib
M = 0xFFFFFFFF
class Sfc32:
    def __init__(s, a, b, c, d): s.s = [a & M, b & M, c & M, d & M]; s.calls = 0
    @classmethod
    def seeded(cls, seed):
        r = cls(0x9E3779B9, 0x243F6A88, 0xB7E15162, seed)
        for _ in range(15): r.next()
        r.calls = 0
        return r
    def next(s):
        a, b, c, d = s.s; s.calls += 1
        t = (a + b + d) & M; d = (d + 1) & M
        a = b ^ (b >> 9); b = (c + (c << 3)) & M
        c = ((c << 21 | c >> 11) & M); c = (c + t) & M
        s.s = [a, b, c, d]; return t
def draw(r, n): return [r.next() for _ in range(n)]
def canon(o): return json.dumps(o, sort_keys=True, separators=(",", ":"))
def h(o): return hashlib.sha256(canon(o).encode()).hexdigest()[:12]
res = {}
# S1: words round-trip through JSON; next 100 rolls identical, O(1) restore
r = Sfc32.seeded(42); draw(r, 5000)
saved = json.dumps({"rng": r.s}); ref = draw(Sfc32(*r.s), 100)
r2 = Sfc32(*json.loads(saved)["rng"]); c0 = r2.calls; res["s1_words"] = (draw(r2, 100) == ref, c0)
# S2: seed+count save replays count rolls (cost) and matches
cnt = 5000; r3 = Sfc32.seeded(42); draw(r3, cnt); res["s2_replay_cost"] = (draw(r3, 100) == ref, cnt)
# S3 (BREAK): words saved as signed 32-bit ints and reloaded WITHOUT re-masking (naive load).
# Swept over 200 seeds: does a negative word change the stream? (shift of a negative differs from >>>)
div = tot = 0
for sd in range(200):
    q = Sfc32.seeded(sd); draw(q, 17)
    ex = draw(Sfc32(*q.s), 50)
    sg = [x - (1 << 32) if x >= (1 << 31) else x for x in q.s]
    if all(x >= 0 for x in sg): continue
    tot += 1; w = Sfc32(0, 0, 0, 0); w.s = sg
    if draw(w, 50) != ex: div += 1
res["s3_signed_unmasked_diverges"] = (div > 0, div, tot)
res["s3_masked_ok"] = (draw(Sfc32(*[x - (1 << 32) if x >= (1 << 31) else x for x in r.s]), 100) == ref,)
n_neg = div
# S4: dropping rng from save (seed only) diverges
r6 = Sfc32.seeded(42); res["s4_seed_only_diverges"] = (draw(r6, 100) != ref,)
# S5: canonical hash vs naive insertion-order hash
a = {"rng": r.s, "hp": 7, "pos": [1, 2]}; b = {"pos": [1, 2], "hp": 7, "rng": r.s}
naive = lambda o: hashlib.sha256(json.dumps(o).encode()).hexdigest()[:12]
res["s5_canon_equal_naive_differs"] = (h(a) == h(b), naive(a) != naive(b))
print(res)
ok = (res["s1_words"][0] and res["s1_words"][1] == 0 and res["s2_replay_cost"][0] and res["s2_replay_cost"][1] == 5000
      and res["s3_signed_unmasked_diverges"][0] and res["s3_masked_ok"][0] and res["s4_seed_only_diverges"][0]
      and all(res["s5_canon_equal_naive_differs"]))
print("RESULT: %s words restore O(1) calls=0 vs replay %d; unmasked signed words diverge (%d diverged of %d states with a negative word); canonical hash order-independent"
      % ("PASS" if ok else "FAIL", cnt, div, tot))
