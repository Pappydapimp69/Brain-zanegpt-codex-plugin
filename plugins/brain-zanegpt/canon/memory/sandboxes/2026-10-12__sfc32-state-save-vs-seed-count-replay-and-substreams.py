"""Sandbox: ideas:SYSTEM/seeded-rng (save sfc32 state words, not {seed,count}) + the-game-prologue/E1 (canonical state hash, no
transcendentals) + ideas:SYSTEM/a-shared-rng-stream-is-an-ordinal-space (population change flips unrelated rolls; named substreams fix it).
Prediction (before run):
 S1 state-words save/restore reproduces the next 1000 draws exactly and costs 0 replay draws; {seed,count} also reproduces them but costs `count` draws (here 50000).
 S2 a {seed,count} save is WRONG (diverges) if any draw happened outside the counter (one uncounted draw).  State words stay right.
 S3 insertion-ordered JSON hash of the same logical state differs for two key orders; the canonical (sorted keys) hash is equal.
 S4 removing one entity from a shared stream flips >0 of 8 downstream combat rolls; per-concern named substreams keep all 8 identical.
 S5 (BREAK) substreams keyed by position/index rather than stable name flip again when an entity is removed."""
import json
M = 0xFFFFFFFF
class Sfc32:
    def __init__(self, a, b, c, d): self.s = [a & M, b & M, c & M, d & M]
    @classmethod
    def seeded(cls, seed):
        r = cls(0, seed, seed, 1)
        for _ in range(12): r.next()
        return r
    def next(self):
        a, b, c, d = self.s
        t = (a + b + d) & M
        d = (d + 1) & M
        a = b ^ (b >> 9)
        b = (c + (c << 3)) & M
        c = ((c << 21 | c >> 11) & M) + t & M
        self.s = [a, b, c, d]
        return t
def draws(r, n): return [r.next() for _ in range(n)]
checks = []
def check(name, ok, info=""):
    checks.append(ok); print(("ok   " if ok else "FAIL ") + name + " " + info)
# S1
r = Sfc32.seeded(7); draws(r, 50000)
saved_words = list(r.s); saved_count = (7, 50000)
want = draws(r, 1000)
r2 = Sfc32(*saved_words); got_words = draws(r2, 1000)
r3 = Sfc32.seeded(saved_count[0]); replay_cost = len(draws(r3, saved_count[1])); got_count = draws(r3, 1000)
check("S1 words exact, cost 0", got_words == want)
check("S1 seed+count exact but replay cost 50000", got_count == want and replay_cost == 50000, f"cost={replay_cost}")
# S2 one uncounted draw
r = Sfc32.seeded(7); draws(r, 49999); r.next()  # uncounted draw: counter says 49999 happened
saved_words = list(r.s); want = draws(r, 100)
r3 = Sfc32.seeded(7); draws(r3, 49999); got_count_bad = draws(r3, 100)
r2 = Sfc32(*saved_words)
check("S2 seed+count diverges after uncounted draw", got_count_bad != want)
check("S2 state words still exact", draws(r2, 100) == want)
# S3 canonical hash
def fnv(s):
    h = 2166136261
    for ch in s.encode(): h = ((h ^ ch) * 16777619) & M
    return h
def canon(o):
    if isinstance(o, dict): return "{" + ",".join(json.dumps(k) + ":" + canon(o[k]) for k in sorted(o)) + "}"
    if isinstance(o, list): return "[" + ",".join(canon(x) for x in o) + "]"
    if isinstance(o, float) and (o != o or o in (float("inf"), float("-inf"))): raise ValueError("non-finite")
    return json.dumps(o)
A = {"hp": 5, "pos": {"x": 1, "y": 2}, "rng": [1, 2, 3, 4]}
B = {"rng": [1, 2, 3, 4], "pos": {"y": 2, "x": 1}, "hp": 5}
check("S3 insertion-order JSON hashes differ", fnv(json.dumps(A)) != fnv(json.dumps(B)))
check("S3 canonical hashes equal", fnv(canon(A)) == fnv(canon(B)))
try: canon({"x": float("nan")}); loud = False
except ValueError: loud = True
check("S3 NaN throws loudly", loud)
# S4 shared stream vs substreams
def fight(entities, shared=True, keyed="name"):
    base = Sfc32.seeded(99)
    rolls = {}
    subs = {}
    for i, e in enumerate(entities):
        key = e if keyed == "name" else i
        subs[e] = Sfc32.seeded(1000 + (sum(map(ord, key)) if keyed == "name" else key))
    for e in entities:   # each entity consumes 3 draws for its spawn
        (base if shared else subs[e]).next(); (base if shared else subs[e]).next(); (base if shared else subs[e]).next()
    combat = Sfc32.seeded(5) if not shared else base
    return [combat.next() % 20 for _ in range(8)]
pop = ["wolf", "bat", "slime", "rat"]; less = ["wolf", "slime", "rat"]
flipped = sum(a != b for a, b in zip(fight(pop), fight(less)))
check("S4 shared stream: removal flips combat rolls", flipped > 0, f"flipped={flipped}/8")
check("S4 named substreams: identical", fight(pop, False) == fight(less, False))
# S5 break: index-keyed
# stronger break: per-entity roll tables keyed by index vs name
def entity_rolls(entities, keyed):
    out = {}
    for i, e in enumerate(entities):
        key = e if keyed == "name" else str(i)
        r = Sfc32.seeded(sum(map(ord, key)) + 1000); out[e] = r.next() % 100
    return out
n1, n2 = entity_rolls(pop, "name"), entity_rolls(less, "name")
i1, i2 = entity_rolls(pop, "index"), entity_rolls(less, "index")
name_stable = all(n1[e] == n2[e] for e in less); idx_stable = all(i1[e] == i2[e] for e in less)
check("S5 name-keyed per-entity rolls survive removal", name_stable)
check("S5 (BREAK) index-keyed per-entity rolls shift after removal", not idx_stable, f"stable={idx_stable}")
print("RESULT:", "PASS" if all(checks) else "FAIL", f"{sum(checks)}/{len(checks)} checks held; replay cost {replay_cost} vs 0; shared-stream flips {flipped}/8; name-keyed stable={name_stable} index-keyed stable={idx_stable}")
