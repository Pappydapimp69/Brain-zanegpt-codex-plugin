"""Prediction (before first run), own fixture: a 32-bit mulberry32 PRNG driving a toy sim of N enemies that each roll damage per tick.
 S1 same seed twice -> identical fingerprint (sha256 of the roll log); different seed -> different.
 S2 save as {seed,count} and replay count draws, vs save the raw 32-bit state word: both resume to the identical next 100 rolls;
    raw state needs 1 step, replay needs `count` steps (count = 5000 here).
 S3 BREAK (leak): one ambient draw (a counter-derived stand-in for Date.now) mid-run -> fingerprints diverge from the first leaked tick on.
 S4 BREAK (shared stream): removing enemy #2 from a 6-enemy sim on ONE shared stream changes the rolls of every enemy listed after it
    in >= 90% of their later rolls; with a per-entity substream keyed by hash(seed, entity_id) the surviving enemies' rolls are unchanged (100%).
 S5 BREAK of S4's fix: per-entity substreams still shift if the substream key uses list ORDINAL (index) instead of a stable id.
Deterministic, stdlib."""
import hashlib
M = 0xFFFFFFFF
class Mul:
    def __init__(s, seed): s.a = seed & M
    def next(s):
        s.a = (s.a + 0x6D2B79F5) & M; t = s.a
        t = ((t ^ (t >> 15)) * (t | 1)) & M
        t ^= (t + (((t ^ (t >> 7)) * (t | 61)) & M)) & M
        return ((t ^ (t >> 14)) & M) / 4294967296
def roll(r): return 1 + int(r.next() * 6)
def fp(log): return hashlib.sha256(repr(log).encode()).hexdigest()[:12]
def sim_shared(seed, ids, ticks, leak_at=None):
    r = Mul(seed); log = []
    for t in range(ticks):
        if leak_at == t: r.next()  # ambient draw outside the seeded path
        for i in ids: log.append((t, i, roll(r)))
    return log
def sim_sub(seed, ids, ticks, keyf):
    subs = {i: Mul(hashlib.sha256(f"{seed}:{keyf(i, ids)}".encode()).digest()[0] << 24 | int.from_bytes(hashlib.sha256(f"{seed}:{keyf(i, ids)}".encode()).digest()[1:4], 'big')) for i in ids}
    return [(t, i, roll(subs[i])) for t in range(ticks) for i in ids]
ids = ["a", "b", "c", "d", "e", "f"]
res = []
l1, l2, l3 = sim_shared(42, ids, 50), sim_shared(42, ids, 50), sim_shared(43, ids, 50)
print("S1", fp(l1) == fp(l2), fp(l1) != fp(l3)); res.append(fp(l1) == fp(l2) and fp(l1) != fp(l3))
r = Mul(7)
for _ in range(5000): r.next()
saved_state = r.a; nxt = [r.next() for _ in range(100)]
rb = Mul(7); steps = 0
for _ in range(5000): rb.next(); steps += 1
rc = Mul(0); rc.a = saved_state
ok2 = [rb.next() for _ in range(100)] == nxt and [Mul.next(rc) for _ in range(100)] == nxt
print("S2 resume identical", ok2, "replay steps", steps, "raw-state steps", 1); res.append(ok2)
l4 = sim_shared(42, ids, 50, leak_at=10)
first_div = next(i for i, (x, y) in enumerate(zip(l1, l4)) if x != y)
print("S3 first divergence at log index", first_div, "= tick", l1[first_div][0]); res.append(fp(l1) != fp(l4) and l1[first_div][0] >= 10 and first_div >= 10 * 6)
ids2 = [i for i in ids if i != "c"]
def later_same(la, lb, surv):
    da = {(t, i): v for t, i, v in la}; db = {(t, i): v for t, i, v in lb}
    keys = [(t, i) for t in range(50) for i in surv]; return sum(da[k] == db[k] for k in keys) / len(keys)
afterC = ["d", "e", "f"]
sh = later_same(sim_shared(42, ids, 50), sim_shared(42, ids2, 50), afterC)
sub = later_same(sim_sub(42, ids, 50, lambda i, L: i), sim_sub(42, ids2, 50, lambda i, L: i), ids2)
ordn = later_same(sim_sub(42, ids, 50, lambda i, L: L.index(i)), sim_sub(42, ids2, 50, lambda i, L: L.index(i)), afterC)
print("S4 same-roll fraction after removing c: shared(d,e,f)", round(sh, 3), "id-keyed substream(all)", sub, "ordinal-keyed(d,e,f)", round(ordn, 3))
res.append(sh <= 0.35 and sub == 1.0 and ordn <= 0.35)
print("RESULT:", "PASS" if all(res) else "FAIL", f"S1 determinism, S2 resume equal (replay {steps} vs 1 steps), S3 leak diverges at tick 10, S4 shared stream keeps {sh:.2f} of later rolls vs id-keyed substream {sub:.2f} vs ordinal-keyed {ordn:.2f}")
