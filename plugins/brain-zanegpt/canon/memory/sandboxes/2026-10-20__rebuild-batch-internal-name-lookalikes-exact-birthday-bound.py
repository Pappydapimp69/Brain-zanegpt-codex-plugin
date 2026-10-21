# Rebuild: invented names from a 12-syllable pool collide inside a batch of 30.
# PREDICTION (before running): exact-duplicate rate at 3 syllables ~ 22% (birthday bound over 12^3=1728 names),
# a pair one syllable apart (differ in <=1 syllable position) in >99% of batches; at 2 syllables duplicate ~95%+.
# Own fixture: syllables are letter pairs; distance is syllable-position Hamming, plus exact closed form.
import random, itertools, math
POOL = ["ka","mo","ri","tu","ze","ba","lu","pi","so","vi","da","ne"]
def batch(rng, k, n): return ["".join(rng.choice(POOL) for _ in range(k)) for _ in range(n)]
def has_dup(b): return len(set(b)) < len(b)
def near(b, k):
    s = [tuple(x[i*2:i*2+2] for i in range(k)) for x in b]
    for a, c in itertools.combinations(s, 2):
        if sum(p != q for p, q in zip(a, c)) <= 1: return True
    return False
def exact_dup(space, n): return 1 - math.prod((space - i) / space for i in range(n))
rng = random.Random(20261020)
T = 4000
res = {}
for k in (2, 3, 4):
    bs = [batch(rng, k, 30) for _ in range(T)]
    res[k] = (sum(map(has_dup, bs)) / T, sum(near(b, k) for b in bs) / T, exact_dup(12**k, 30))
    print("k=%d dup=%.3f (exact %.3f) near<=1syl=%.3f" % ((k,) + res[k][:1] + (res[k][2], res[k][1])))
# BREAK: bigger pool (60 syllables) at 3 syllables should drop near-pair rate sharply
POOL2 = ["".join(p) for p in itertools.product("kmrtzbl", "aiou")][:28] + ["ve", "ne", "se", "ho"]
POOL2 = (POOL2 + ["pa", "ju", "gi", "wo", "xe", "yu", "fa", "de"] * 3)[:60]
POOL2 = sorted(set(POOL2 + ["%s%s" % (a, b) for a in "kmrtzblpnsdfgh" for b in "aeiou"]))[:60]
big = [["".join(rng.choice(POOL2) for _ in range(3)) for _ in range(30)] for _ in range(T)]
def near2(b):
    s = [tuple(x[i*2:i*2+2] for i in range(3)) for x in b]
    return any(sum(p != q for p, q in zip(a, c)) <= 1 for a, c in itertools.combinations(s, 2))
nb = sum(map(near2, big)) / T
print("BREAK pool=%d k=3 near=%.3f" % (len(POOL2), nb))
ok = abs(res[3][0] - res[3][2]) < 0.03 and res[3][1] > 0.99 and res[2][0] > 0.9 and res[4][1] < res[3][1] and nb < res[3][1]
print("RESULT: %s k=3 dup=%.1f%% (exact %.1f%%) near=%.1f%%; k=2 dup=%.1f%%; k=4 near=%.1f%%; pool60 k=3 near=%.1f%%"
      % ("PASS" if ok else "FAIL", res[3][0]*100, res[3][2]*100, res[3][1]*100, res[2][0]*100, res[4][1]*100, nb*100))
