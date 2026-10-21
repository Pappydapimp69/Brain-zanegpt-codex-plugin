# Batch sizes allowed by the trope cap (6 / 12 / 16) against in-batch name lookalikes, plus a label-vs-source check on the trope list.
import random
SYL = 12; LEN = 3; TRIALS = 600
def batch(rng, n): return [tuple(rng.randrange(SYL) for _ in range(LEN)) for _ in range(n)]
def near(a, b): return sum(x != y for x, y in zip(a, b)) <= 1          # one syllable apart
def stats(n, seed):
    rng = random.Random(seed); dup = look = 0
    for _ in range(TRIALS):
        b = batch(rng, n)
        pairs = [(b[i], b[j]) for i in range(n) for j in range(i + 1, n)]
        dup += any(x == y for x, y in pairs); look += any(near(x, y) for x, y in pairs)
    return dup / TRIALS, look / TRIALS
res = {n: stats(n, 11) for n in (6, 12, 16)}
for n, (d, l) in res.items(): print("batch", n, "exact dup %.3f lookalike %.3f" % (d, l))
# label check: kernel trope labels against the source labels; one label paraphrased
source = {"borrowed fame", "fake reviews", "rapid reward", "gameplay mismatch", "celebrity cameo", "urgency timer"}
kernel = ["borrowed fame", "fake reviews", "rapid reward", "gameplay mismatch", "celebrity cameo", "countdown pressure"]
bad = [t for t in kernel if t not in source]
print("labels not in source:", bad)
ok = res[6][1] > 0.15 and res[12][1] > 0.5 and res[16][1] > 0.8 and res[16][0] < res[16][1] and len(bad) == 1
print("RESULT: %s lookalike %.2f/%.2f/%.2f at batch 6/12/16 vs exact dup %.2f/%.2f/%.2f; label check flagged %d of 6" % ("PASS" if ok else "FAIL", res[6][1], res[12][1], res[16][1], res[6][0], res[12][0], res[16][0], len(bad)))
