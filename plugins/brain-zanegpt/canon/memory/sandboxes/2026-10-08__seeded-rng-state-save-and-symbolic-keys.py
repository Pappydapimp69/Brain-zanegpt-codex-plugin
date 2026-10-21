"""Deterministic sandbox: raw-state save vs count replay, shared stream coupling,
per-mechanic streams (named vs ordinal seeds), symbolic keyed draws."""
M = 2**32

class LCG:
    def __init__(self, s): self.s = s % M; self.draws = 0
    def next(self):
        self.s = (1664525 * self.s + 1013904223) % M; self.draws += 1
        return self.s >> 8
def fnv(*parts):
    h = 2166136261
    for b in "|".join(map(str, parts)).encode():
        h = ((h ^ b) * 16777619) % M
    return h
def keyed(seed, *key): return fnv(seed, *key) % 100

SEED = 12345
# S1: save/load. raw state O(1) vs replay-count O(n); both must resume exactly.
r = LCG(SEED); [r.next() for _ in range(5000)]
saved_state, saved_count = r.s, r.draws
want = [r.next() for _ in range(20)]
a = LCG(0); a.s = saved_state; got_state = [a.next() for _ in range(20)]
b = LCG(SEED); [b.next() for _ in range(saved_count)]; got_replay = [b.next() for _ in range(20)]
s1 = got_state == want and got_replay == want
print("S1 raw-state ok:", got_state == want, "replay ok:", got_replay == want, "replay cost:", saved_count, "vs 1")

# S2: shared stream; an extra consumer (a new roll) inserted before 20 loot rolls.
def loot_shared(extra):
    g = LCG(SEED); out = []
    for i in range(20):
        if extra and i % 2 == 0: g.next()   # extra consumer
        out.append(g.next() % 100)
    return out
base = loot_shared(False); ch = loot_shared(True)
s2 = sum(x != y for x, y in zip(base, ch))
print("S2 shared-stream outcomes changed:", s2, "/ 20")

# S3: per-mechanic streams seeded by NAME.
def loot_named(extra):
    streams = {"loot": LCG(fnv(SEED, "loot")), "crit": LCG(fnv(SEED, "crit"))}
    out = []
    for i in range(20):
        if extra and i % 2 == 0: streams["crit"].next()
        out.append(streams["loot"].next() % 100)
    return out
s3 = sum(x != y for x, y in zip(loot_named(False), loot_named(True)))
print("S3 named-stream changed:", s3, "/ 20")

# S4 (BREAK): streams seeded by registration ORDINAL; new mechanic registered first.
def loot_ordinal(insert_first):
    names = (["new"] if insert_first else []) + ["loot", "crit"]
    streams = {n: LCG(fnv(SEED, i)) for i, n in enumerate(names)}
    return [streams["loot"].next() % 100 for _ in range(20)]
s4 = sum(x != y for x, y in zip(loot_ordinal(False), loot_ordinal(True)))
print("S4 ordinal-seeded streams changed:", s4, "/ 20")

# S5: symbolic keys (entity id, tick, purpose); insert an extra entity & extra check.
def decisions(entities, extra_check):
    d = {}
    for e in entities:
        for t in range(10):
            d[(e, t, "move")] = keyed(SEED, e, t, "move")
            if extra_check: d[(e, t, "scan")] = keyed(SEED, e, t, "scan")
    return d
b5 = decisions(["a", "b", "c"], False); c5 = decisions(["a", "x", "b", "c"], True)
s5 = sum(c5[k] != v for k, v in b5.items())
print("S5 symbolic keys changed:", s5, "/", len(b5))

ok = s1 and s2 >= 5 and s3 == 0 and s4 >= 15 and s5 == 0
print("RESULT: %s raw-state save exact (replay costs %d draws); shared stream flips %d/20; named streams %d/20; ordinal-seeded streams flip %d/20; symbolic keys %d/30"
      % ("PASS" if ok else "FAIL", saved_count, s2, s3, s4, s5))
