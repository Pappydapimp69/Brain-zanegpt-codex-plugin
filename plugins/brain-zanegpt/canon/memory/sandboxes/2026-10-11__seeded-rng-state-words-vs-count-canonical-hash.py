"""Sandbox: seeded RNG save by state words vs {seed,count}, plus canonical vs insertion-order hashing.
Prediction (written before run): state-words restore costs 0 rolls and matches the next 1000 rolls;
count replay costs exactly `count` rolls and matches too; insertion-order JSON hash of equal state
differs in >=1 of 3 key orders while sorted-key hash is identical in all 3."""
import json, hashlib, itertools
M = 0xFFFFFFFF
class Sfc32:
    def __init__(s, seed):
        s.a, s.b, s.c, s.d = 0x9E3779B9, 0x243F6A88, 0xB7E15162, seed & M
        s.rolls = 0
        for _ in range(12): s.next()
        s.rolls = 0
    def next(s):
        t = (s.a + s.b + s.d) & M
        s.d = (s.d + 1) & M
        s.a = s.b ^ (s.b >> 9)
        s.b = (s.c + (s.c << 3)) & M
        s.c = (((s.c << 21) | (s.c >> 11)) & M) + t & M
        s.rolls += 1
        return t
    def state(s): return [s.a, s.b, s.c, s.d]
    def load(s, w): s.a, s.b, s.c, s.d = w
ok = True
# 1) state words restore
r = Sfc32(42)
for _ in range(5000): r.next()
saved_words, saved_count = r.state(), r.rolls
cont = [r.next() for _ in range(1000)]
r2 = Sfc32(7); r2.load(saved_words); r2.rolls = 0
words_ok = [r2.next() for _ in range(1000)] == cont
words_cost = 0
# 2) count replay restore
r3 = Sfc32(42); r3.rolls = 0
for _ in range(saved_count): r3.next()
count_cost = r3.rolls
count_ok = [r3.next() for _ in range(1000)] == cont
print("words_ok", words_ok, "cost", words_cost, "| count_ok", count_ok, "cost", count_cost)
ok &= words_ok and count_ok and count_cost == 5000
# 3) BREAK: same logical state, different key insertion order
base = {"rng": saved_words, "hp": 10, "pos": [3, 4]}
hashes_raw, hashes_canon = set(), set()
for perm in itertools.permutations(base):
    d = {k: base[k] for k in perm}
    hashes_raw.add(hashlib.sha256(json.dumps(d).encode()).hexdigest())
    hashes_canon.add(hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest())
print("raw distinct hashes", len(hashes_raw), "canonical distinct", len(hashes_canon))
ok &= len(hashes_raw) > 1 and len(hashes_canon) == 1
# 4) signed vs unsigned word storage: a saved signed int32 reloaded without masking diverges
signed = [w - (1 << 32) if w >= 1 << 31 else w for w in saved_words]
r4 = Sfc32(0); r4.load(signed)
try:
    bad = [r4.next() for _ in range(5)] != cont[:5]
except Exception:
    bad = True
print("unmasked signed reload diverges:", bad, "(signed words:", sum(w < 0 for w in signed), ")")
ok &= bad
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
      f"state-words restore 0 rolls vs count replay {count_cost} rolls, both exact; raw hash {len(hashes_raw)} variants vs canonical 1; unmasked signed reload diverges")
