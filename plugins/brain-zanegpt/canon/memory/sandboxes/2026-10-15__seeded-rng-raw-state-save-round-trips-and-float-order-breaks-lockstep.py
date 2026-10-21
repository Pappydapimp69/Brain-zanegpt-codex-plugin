"""Sandbox: seeded-rng kernel + split-state kernel + the-game-prologue/E1.
Deterministic, stdlib only, no ambient RNG, no timing."""
import json, hashlib, functools, operator

M = 0xFFFFFFFF
class SFC32:
    def __init__(s, a, b, c, d): s.st = [a & M, b & M, c & M, d & M]
    def next(s):
        a, b, c, d = s.st
        t = (a + b + d) & M
        d = (d + 1) & M
        a = b ^ (b >> 9)
        b = (c + (c << 3)) & M
        c = ((c << 21) | (c >> 11)) & M
        c = (c + t) & M
        s.st = [a, b, c, d]
        return t
    @classmethod
    def seeded(cls, seed):
        r = cls(0, seed, 0, 1)
        for _ in range(12): r.next()
        return r

def sim(rng, state, steps, ambient=None):
    for _ in range(steps):
        roll = rng.next() if ambient is None else ambient()
        state["hp"] -= roll % 7
        state["log"].append(roll % 100)
    return state

ok = True
# S1: raw-state save round-trips exactly; count-replay costs O(count)
r = SFC32.seeded(42); st = {"hp": 10**6, "log": []}
sim(r, st, 5000)
save = json.dumps({"rng": r.st, "state": st})
calls = [0]
def replay_load(seed, count):
    x = SFC32.seeded(seed)
    for _ in range(count): x.next(); calls[0] += 1
    return x
a = SFC32(*json.loads(save)["rng"]); b = replay_load(42, 5000); c = r
nxt = [(a.next(), b.next(), c.next()) for _ in range(100)]
s1 = all(x == y == z for x, y, z in nxt)
print(f"S1 raw-state load equal={s1} raw_load_calls=0 replay_load_calls={calls[0]}")
ok &= s1 and calls[0] == 5000

# S2: lockstep - two clients same seed same stream
c1, c2 = SFC32.seeded(7), SFC32.seeded(7)
s2a = sim(c1, {"hp": 10**6, "log": []}, 2000); s2b = sim(c2, {"hp": 10**6, "log": []}, 2000)
s2 = s2a == s2b
print(f"S2 lockstep clients identical={s2}")
ok &= s2

# S3 (BREAK): ambient source inside sim - stand-in for Math.random: a per-client
# source that is deterministic per client but not shared (models two machines)
def ambient_for(k):
    x = SFC32.seeded(1000 + k); return x.next
d1 = sim(SFC32.seeded(7), {"hp": 10**6, "log": []}, 2000, ambient_for(1))
d2 = sim(SFC32.seeded(7), {"hp": 10**6, "log": []}, 2000, ambient_for(2))
first_div = next((i for i, (p, q) in enumerate(zip(d1["log"], d2["log"])) if p != q), None)
print(f"S3 ambient rolls diverge at step {first_div}, hp {d1['hp']} vs {d2['hp']}")
ok &= first_div is not None

# S4 (BREAK): authoritative outcome fed by float sum order (two clients summing
# the same movement deltas in different order) - split-state kernel's tell
deltas = [0.1] * 10 + [1e16, -1e16]
# naive left fold (what a JS game loop does); Python 3.12 sum() is compensated
fold = lambda xs: functools.reduce(operator.add, xs, 0.0)
x_fwd = fold(deltas); x_rev = fold(list(reversed(deltas)))
hit_fwd = x_fwd >= 0.5; hit_rev = x_rev >= 0.5  # e.g. "reached the trigger"
print(f"S4 float position fwd={x_fwd!r} rev={x_rev!r} hit {hit_fwd} vs {hit_rev}")
ok &= hit_fwd != hit_rev
# fix: authoritative fact is discrete (zone index from integer steps)
zone_fwd = sum(int(d * 10) for d in deltas[:10]); zone_rev = sum(int(d * 10) for d in reversed(deltas[:10]))
print(f"S4b discrete zone fwd={zone_fwd} rev={zone_rev} equal={zone_fwd == zone_rev}")
ok &= zone_fwd == zone_rev

# S5: hashing state for golden tests needs canonical key order (E1)
sa = {"hp": 3, "zone": 2, "flags": {"b": 1, "a": 0}}
sb = {"zone": 2, "flags": {"a": 0, "b": 1}, "hp": 3}
h = lambda o, k: hashlib.sha256(json.dumps(o, sort_keys=k).encode()).hexdigest()[:12]
raw_eq = h(sa, False) == h(sb, False); canon_eq = h(sa, True) == h(sb, True)
print(f"S5 equal states hash-equal raw={raw_eq} sorted={canon_eq}")
ok &= (not raw_eq) and canon_eq

print(("RESULT: PASS" if ok else "RESULT: FAIL") +
      f" raw-state load O(1) matches 100/100 rolls vs 5000-call replay; lockstep equal; ambient diverges at step {first_div}; float order flips a hit ({hit_fwd}/{hit_rev}) while discrete zone holds; sorted-key hash needed (raw {raw_eq}, sorted {canon_eq})")
