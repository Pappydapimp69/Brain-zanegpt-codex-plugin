# Prediction (before run): 6 consumers (spawn, loot, crit, ai, weather, shake) each draw 5 rolls.
# Name-keyed substreams (seed = FNV1a(name) mixed with the world seed) give identical per-consumer traces under
# insert, remove and reorder: 0 changed consumers in all three. Index-keyed substreams (seed = world seed + slot)
# change every consumer after an insert (insert at slot 1 -> 5 of 6 existing consumers changed), after removal at
# slot 1 (4 of 5 remaining), and after a reorder swap of two (2 of 6). Hidden assumption: the name is stable.
# Run 1 missed the collision part (0 shared streams at 4 bits; the bucket spread was kinder than the 16-bucket guess).
# Run 2 prediction: narrowing the name hash to 1 or 2 bits makes >=1 shared stream (1 bit: >=4 of 6), 32 bits none.
# BREAK: truncating the name hash to 4 bits makes two names collide and share a stream -> some consumer pair
# traces equal (>=1 collision among 6 names, expected since 6 names in 16 buckets).
import hashlib, json
M = 0xFFFFFFFF
def fnv(s):
    h = 2166136261
    for c in s.encode(): h = ((h ^ c) * 16777619) & M
    return h
def sfc32(a, b, c, d):
    def nxt():
        nonlocal a, b, c, d
        t = (a + b + d) & M; d = (d + 1) & M
        a = b ^ (b >> 9); b = (c + (c << 3)) & M
        c = ((c << 21 | c >> 11) & M) + t & M
        return t
    for _ in range(12): nxt()
    return nxt
def stream(seed):
    return sfc32(seed & M, (seed * 2654435761 + 1) & M, (seed ^ 0x9E3779B9) & M, 1)
def roll(seed, n=5):
    g = stream(seed); return [g() % 100 for _ in range(n)]
WORLD = 12345
def named(names, bits=32):
    return {n: roll(WORLD * 31 + (fnv(n) & ((1 << bits) - 1))) for n in names}
def indexed(names):
    return {n: roll(WORLD * 31 + i) for i, n in enumerate(names)}
def fingerprint(d):  # canonical sorted-key hash as in the replay-fingerprint practice
    return hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()[:12]
base = ["spawn", "loot", "crit", "ai", "weather", "shake"]
ins = base[:1] + ["boss"] + base[1:]
rem = base[:1] + base[2:]
reo = base[:]; reo[1], reo[4] = reo[4], reo[1]
def changed(f, other):
    a, b = f(base), f(other)
    return sum(1 for n in b if n in a and a[n] != b[n])
res = {}
for label, f in (("named", named), ("indexed", indexed)):
    res[label] = (changed(f, ins), changed(f, rem), changed(f, reo))
    print(label, "insert/remove/reorder changed consumers", res[label])
print("fingerprint named base vs reordered", fingerprint(named(base)) == fingerprint(named(reo)), "indexed", fingerprint(indexed(base)) == fingerprint(indexed(reo)))
dups = {}
for bits in (32, 8, 4, 2, 1):
    c = named(base, bits); dups[bits] = len(base) - len({tuple(v) for v in c.values()})
print("shared streams by name-hash bits", dups)
ok = res["named"] == (0, 0, 0) and res["indexed"] == (5, 4, 2) and dups[32] == 0 and dups[1] >= 4 and dups[2] >= 1
print(f"RESULT: {'PASS' if ok else 'FAIL'} named changed {res['named']} indexed changed {res['indexed']}; shared streams by hash bits {dups}")
