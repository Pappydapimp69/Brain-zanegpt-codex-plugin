"""Compose event-bus emit snapshot (sandbox-combined-narrative-flags/E2) with RNG isolation (brainwork/E100).
A bus has 5 listeners; each rolls one draw when it runs and adds it to its score. Listener 1 unsubscribes itself
during dispatch. Ten emits.
Prediction (before first run):
 P1 live-array iteration skips exactly listener 2 on the first emit (and never again after the unsubscribe shifts).
 P2 on a shared sequential stream a skipped roll shifts every later draw: listeners 3 and 4 and every later emit
    change vs the snapshot run (>= 3 of 5 listeners' final scores differ from the snapshot reference).
 P3 with addressed draws (hash of seed, listener, emit) only the skipped listener differs (exactly 1 of 5, by the
    one lost draw) and the others match the snapshot reference exactly.
 P4 (break) with no self-unsubscribe, live and snapshot dispatch agree under both RNG designs (0 differences)."""
import hashlib

def addr(seed, lid, emit):
    return int(hashlib.sha256(f"{seed}:{lid}:{emit}".encode()).hexdigest()[:8], 16) % 100

class Stream:
    def __init__(s, seed): s.x = seed
    def next(s):
        s.x = (s.x * 1103515245 + 12345) & 0x7FFFFFFF
        return (s.x >> 8) % 100

def run(live, rng, self_unsub=True, seed=5, emits=10):
    L = [0, 1, 2, 3, 4]
    score = {i: 0 for i in L}
    st = Stream(seed)
    ran_first = None
    for e in range(emits):
        ran = []
        it = L if live else list(L)
        i = 0
        while i < len(it):
            lid = it[i]
            ran.append(lid)
            d = st.next() if rng == "shared" else addr(seed, lid, e)
            score[lid] += d
            if self_unsub and lid == 1 and lid in L:
                L.remove(1)
                if not live:
                    pass
            i += 1
        if e == 0: ran_first = ran
    return score, ran_first

def diffs(a, b): return sum(a[i] != b[i] for i in a)
out = {}
for rng in ("shared", "addressed"):
    snap, ran_snap = run(False, rng)
    live, ran_live = run(True, rng)
    out[rng] = (snap, live, ran_snap, ran_live)
    print(rng, "first-emit ran snapshot", ran_snap, "live", ran_live, "score diffs", diffs(snap, live))
p1 = out["shared"][3] == [0, 1, 3, 4]       # listener 2 skipped on the first emit
d_shared = diffs(out["shared"][0], out["shared"][1])
d_addr = diffs(out["addressed"][0], out["addressed"][1])
# note: snapshot keeps running unsubscribed listener 1 for the first emit only; later emits both lack it
print("P1", p1, " shared diffs", d_shared, " addressed diffs", d_addr)
b_shared = diffs(run(False, "shared", False)[0], run(True, "shared", False)[0])
b_addr = diffs(run(False, "addressed", False)[0], run(True, "addressed", False)[0])
print("P4 no-unsub diffs shared", b_shared, "addressed", b_addr)
ok = p1 and d_shared >= 3 and d_addr == 1 and b_shared == 0 and b_addr == 0
print("RESULT:", "PASS" if ok else "FAIL",
      f"skipped_first_emit={out['shared'][3]} shared_diffs={d_shared}/5 addressed_diffs={d_addr}/5 nounsub_diffs={b_shared},{b_addr}")
