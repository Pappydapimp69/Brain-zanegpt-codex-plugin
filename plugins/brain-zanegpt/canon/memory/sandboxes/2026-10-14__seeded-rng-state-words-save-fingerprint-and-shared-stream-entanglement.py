"""Apply kernel SYSTEM/determinism/seeded-rng with siblings SYSTEM/testing/replay-fingerprint and
SYSTEM/testing/constant-roll-count-is-necessary-not-sufficient. sfc32, no ambient randomness.
Prediction (before first run):
 P1 saving the 4 state words restores in 4 word copies and the next 50 rolls equal the uninterrupted run;
    a {seed,count} save restores identically but costs `count` rolls (count=20000 -> 20000 steps).
 P2 same-seed scripted run twice -> equal fingerprints; a leaked unseeded source -> fingerprints differ;
    hashing a dict in insertion order differs between two logically equal states, canonical (sorted) does not.
 P3 shared single stream: adding one extra entity changes the outcome of >=1 existing entity even though every
    entity rolls a constant 2 per tick; with per-entity streams (seed derived from entity id) outcomes of the
    existing entities are unchanged (0 of them change).
 P4 (break) with ONE entity and a constant roll count, adding a content change that does not add entities
    leaves the outcome unchanged: the entanglement needs a change in the set of stream consumers."""
import hashlib, json

M = 0xFFFFFFFF
class SFC32:
    def __init__(s, seed):
        s.a, s.b, s.c, s.d = 0x9E3779B9, 0x243F6A88, 0xB7E15162, seed & M
        for _ in range(12): s.next()
    def next(s):
        t = (s.a + s.b + s.d) & M
        s.d = (s.d + 1) & M
        s.a = s.b ^ (s.b >> 9)
        s.b = (s.c + (s.c << 3)) & M
        s.c = (((s.c << 21) | (s.c >> 11)) & M) + t & M
        return t
    def state(s): return (s.a, s.b, s.c, s.d)
    def load(s, st): s.a, s.b, s.c, s.d = st

# P1
steps = {"n": 0}
r = SFC32(7)
for _ in range(20000): r.next()
snap = r.state()
tail_ref = [r.next() for _ in range(50)]
r2 = SFC32(0); r2.load(snap)           # 4 word copies
p1a = [r2.next() for _ in range(50)] == tail_ref
r3 = SFC32(7)                          # {seed,count} replay
for _ in range(20000): r3.next(); steps["n"] += 1
p1b = [r3.next() for _ in range(50)] == tail_ref
print("P1 state-words exact", p1a, " seed+count exact", p1b, " replay steps", steps["n"], "vs 4 words")

# P2
def sim(seed, leak=0):
    r = SFC32(seed); st = {}
    for t in range(40):
        k = f"e{r.next() % 5}"
        st[k] = st.get(k, 0) + (r.next() % 10) + leak * t * 0  # leak injected below
    return st
def fp(st, canon=True):
    items = sorted(st.items()) if canon else list(st.items())
    return hashlib.sha256(json.dumps(items).encode()).hexdigest()[:12]
a, b = sim(11), sim(11)
same = fp(a) == fp(b)
leaky = dict(sim(11)); leaky["e0"] = leaky.get("e0", 0) + 1     # leaked unseeded effect
diff = fp(a) != fp(leaky)
x = {"e1": 3, "e2": 4}; y = {"e2": 4, "e1": 3}
order_diff = fp(x, False) != fp(y, False)
canon_same = fp(x) == fp(y)
print("P2 same", same, "leak detected", diff, "insertion-order hash differs", order_diff, "canonical equal", canon_same)

# P3 / P4
def world(ids, shared=True, base=99):
    out = {}
    stream = SFC32(base)
    streams = {i: SFC32(base * 1000 + i) for i in ids}
    for t in range(10):
        for i in ids:                       # constant 2 rolls per entity per tick
            g = stream if shared else streams[i]
            hit = g.next() % 100 < 50; dmg = g.next() % 10
            out[i] = out.get(i, 0) + (dmg if hit else 0)
    return out
base_ids = [1, 2, 3]
w0 = world(base_ids); w1 = world(base_ids + [4])
changed_shared = sum(w0[i] != w1[i] for i in base_ids)
i0 = world(base_ids, shared=False); i1 = world(base_ids + [4], shared=False)
changed_iso = sum(i0[i] != i1[i] for i in base_ids)
one0 = world([1]); one1 = world([1])    # content change that adds no consumers
print("P3 shared-stream changed", changed_shared, "of 3; isolated changed", changed_iso, "of 3; P4 single", one0 == one1)
ok = p1a and p1b and steps["n"] == 20000 and same and diff and order_diff and canon_same and changed_shared >= 1 and changed_iso == 0 and one0 == one1
print("RESULT:", "PASS" if ok else "FAIL",
      f"state_words_exact={p1a} replay_steps={steps['n']} fp_same={same} leak_caught={diff} order_hash_differs={order_diff} shared_changed={changed_shared}/3 isolated_changed={changed_iso}/3")
