# Rebuild: batch caps (6, 12, 16) vs lookalike and duplicate rates for 3-syllable invented names from 12 syllables.
# PREDICTION (before running): closed-form expected near-pair counts give batch 6 ~ 0.3 (15 pairs x 0.0245 -> P about 0.31),
# batch 12 ~ 0.8 (66 pairs), batch 16 ~ 0.93 (120 pairs); exact duplicates 0.9/3.7/6.7 percent (birthday over 1728).
# My own fixture: a different syllable pool, 3000 batches, and independence-based closed forms as a cross-check.
import random, itertools, math
POOL = ["fa","gu","he","ji","ko","ma","ne","po","qi","ra","su","ti"]
rng = random.Random(424242)
p_near = 3*(1/12)**2*(11/12) + (1/12)**3   # P(two random names agree in >=2 of 3 positions)
def sample(n): return [tuple(rng.choice(POOL) for _ in range(3)) for _ in range(n)]
def near(b): return any(sum(x != y for x, y in zip(a, c)) <= 1 for a, c in itertools.combinations(b, 2))
T = 3000; out = {}
for n in (6, 12, 16):
    bs = [sample(n) for _ in range(T)]
    nr = sum(map(near, bs)) / T; du = sum(len(set(b)) < len(b) for b in bs) / T
    cf_near = 1 - (1 - p_near) ** math.comb(n, 2)  # independence approximation
    cf_dup = 1 - math.prod((1728 - i) / 1728 for i in range(n))
    out[n] = (nr, du, cf_near, cf_dup)
    print("batch %2d near=%.3f (indep approx %.3f) dup=%.3f (exact %.3f)" % (n, out[n][0], out[n][2], out[n][1], out[n][3]))
# BREAK: if the screen compares only 4-syllable names, cap 6 should be nearly clean
bs4 = [[tuple(rng.choice(POOL) for _ in range(4)) for _ in range(6)] for _ in range(T)]
n4 = sum(map(near, bs4)) / T
print("BREAK 4-syllable names, batch 6: near=%.3f" % n4)
ok = (0.2 < out[6][0] < 0.4 and out[16][0] > 0.85 and out[6][0] < out[12][0] < out[16][0]
      and all(out[n][1] < 0.1 for n in out) and n4 < out[6][0])
print("RESULT: %s near 6/12/16 = %.0f/%.0f/%.0f%%, dup %.1f/%.1f/%.1f%%, 4-syllable batch 6 near %.0f%%"
      % ("PASS" if ok else "FAIL", out[6][0]*100, out[12][0]*100, out[16][0]*100, out[6][1]*100, out[12][1]*100, out[16][1]*100, n4*100))
