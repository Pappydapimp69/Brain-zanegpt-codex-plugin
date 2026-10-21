# Deterministic sandbox: sfc32 RNG saved as state words vs {seed,count} replay; ambient-random break; fingerprint guard.
# Prediction (before run): state-word restore costs 4 ints and 0 replayed rolls; {seed,count} restore replays exactly count rolls
# (count=200000 -> 200000 steps); both give identical next 5 rolls; a sim using an ambient source (a hidden counter-clock)
# diverges after load within the first 5 rolls; a golden fingerprint over 1000 rolls catches the ambient version but passes the seeded one;
# a sim that rolls sorted-vs-insertion dict order fingerprints differently unless keys are sorted.
import hashlib, json
M = 0xFFFFFFFF
class Sfc32:
    def __init__(s, a, b, c, d): s.st = [a & M, b & M, c & M, d & M]
    @classmethod
    def seeded(cls, seed):
        r = cls(0, seed, seed * 7 + 1, 1); r.steps = 0
        for _ in range(12): r.next()
        r.steps = 0; return r
    steps = 0
    def next(s):
        a, b, c, d = s.st
        t = (a + b + d) & M
        d = (d + 1) & M
        a = b ^ (b >> 9)
        b = (c + (c << 3)) & M
        c = (((c << 21) | (c >> 11)) & M) + t & M
        s.st = [a, b, c, d]; s.steps += 1
        return t / 4294967296.0
def state_restore(words): return Sfc32(*words)
def count_restore(seed, count):
    r = Sfc32.seeded(seed)
    for _ in range(count): r.next()
    return r
N = 200000
live = Sfc32.seeded(42)
for _ in range(N): live.next()
saved_words = list(live.st)
a = state_restore(saved_words); b = count_restore(42, N)
nxt_live = [live.next() for _ in range(5)]
nxt_a = [a.next() for _ in range(5)]; nxt_b = [b.next() for _ in range(5)]
print("state-word restore replayed rolls: 0 ; count restore replayed", b.steps - 5)
print("next5 equal:", nxt_live == nxt_a == nxt_b)
# coop lockstep: two clients, same inputs
c1, c2 = Sfc32.seeded(7), Sfc32.seeded(7)
lock = all(c1.next() == c2.next() for _ in range(10000)); print("lockstep 10000:", lock)
# BREAK 1: ambient source (module-level counter clock) mixed in -> save/load diverges
tick = [0]
def ambient(): tick[0] += 1; return (tick[0] * 0.6180339887) % 1.0
def sim_roll(r, ambient_on): return (r.next() + (ambient() if ambient_on else 0)) % 1.0
def run_sim(ambient_on, restore_at=500):
    tick[0] = 0; r = Sfc32.seeded(9); out = []
    for i in range(1000):
        if i == restore_at:
            r = state_restore(list(r.st)); tick[0] += 37  # process restart/clock skew
        out.append(round(sim_roll(r, ambient_on), 9))
    return out
def ref(ambient_on):
    tick[0] = 0; r = Sfc32.seeded(9); out = []
    for i in range(1000): out.append(round(sim_roll(r, ambient_on), 9))
    return out
clean_ok = run_sim(False) == ref(False); amb_ok = run_sim(True) == ref(True)
fp = lambda xs: hashlib.sha256(json.dumps(xs).encode()).hexdigest()[:12]
print("seeded roundtrip identical:", clean_ok, "| ambient roundtrip identical:", amb_ok, "| fp seeded", fp(run_sim(False)) == fp(ref(False)), "fp ambient", fp(run_sim(True)) == fp(ref(True)))
# BREAK 2: state hashed with insertion-order keys (integer-like keys reorder in JS; here emulate by two insertion orders)
s1 = {"b": 1, "a": 2}; s2 = {"a": 2, "b": 1}
raw = json.dumps(s1) == json.dumps(s2); canon = json.dumps(s1, sort_keys=True) == json.dumps(s2, sort_keys=True)
print("raw serializer equal:", raw, "canonical equal:", canon)
ok = (nxt_live == nxt_a == nxt_b and b.steps - 5 == N and lock and clean_ok and not amb_ok and not raw and canon)
print("RESULT: %s restore words=4 ints/0 rolls vs count=%d rolls, next5 equal, lockstep 10000, seeded roundtrip %s vs ambient %s, raw-key-order hash equal=%s canonical=%s" % ("PASS" if ok else "FAIL", N, clean_ok, amb_ok, raw, canon))
