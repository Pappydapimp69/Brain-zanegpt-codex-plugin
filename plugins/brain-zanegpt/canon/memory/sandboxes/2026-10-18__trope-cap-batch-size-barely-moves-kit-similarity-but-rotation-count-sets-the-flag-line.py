# Path: batch-ceiling-trope-cap (batch <= min(16, 6*per-trope cap)) + fake-ad-kernel-source-check (kernel's kit of 10 assets).
# Companion: fake-ad-kit-template-similarity (10 fixed kit slots + 6 variable = 16; fresh-script batch 0.625; rotate 3 -> 0.48; flag line 0.5 assumed).
# Question: does the largest batch the trope cap allows (6, 12, 16 videos) keep similarity under the 0.5 line at the same rotation count?
from itertools import combinations
KIT, VAR = 10, 6                       # 10 kit slots, 6 variable slots (game name, joke, script, voiceover, layout, trope)
def video(i, r, ntrope=6):
    kit = []
    for k in range(KIT):
        # rotated assets cycle through a pool of 6 variants with a per-asset stride; fixed assets stay variant 0
        kit.append((i * (k % 5 + 1)) % 6 if k < r else 0)
    var = [("fresh", i)] * 5 + [("trope", i % ntrope)]   # 5 unique-per-video slots, 1 trope slot
    var = [(n, v if n == "fresh" else v) for n, v in var]
    return kit, [(("fresh", k, i)) for k in range(5)] + [("trope", i % ntrope)]
def sim(a, b):
    same = sum(x == y for x, y in zip(a[0], b[0])) + sum(x == y for x, y in zip(a[1], b[1]))
    return same / (KIT + VAR)
def batch_score(B, r, ntrope=6):
    vs = [video(i, r, ntrope) for i in range(B)]
    ps = [sim(a, b) for a, b in combinations(vs, 2)]
    return sum(ps) / len(ps)
print("B  r=0   r=3   r=4   r=6")
tab = {}
for B in (6, 12, 16):
    tab[B] = {r: batch_score(B, r) for r in (0, 3, 4, 6)}
    print(B, "  ".join("%.3f" % tab[B][r] for r in (0, 3, 4, 6)))
# companion's number: B=8 fresh-script batch r=0, r=3, r=6
c = [batch_score(8, r) for r in (0, 3, 6)]
print("companion B=8:", ["%.3f" % x for x in c])
# BREAK: trope-free comparison (every video its own trope) at B=16 to see how much the trope slot adds
nt = batch_score(16, 3, ntrope=16)
print("B=16 r=3 with 16 distinct tropes: %.3f vs %.3f" % (nt, tab[16][3]))
ok = (abs(c[0] - 0.625) < 0.03 and tab[6][3] < 0.5 and tab[16][3] < 0.5 and
      0 < tab[16][3] - nt < 0.02 and tab[16][0] > tab[6][0] - 0.02)
print("RESULT: %s fresh-script similarity %.3f/%.3f/%.3f at B=6/12/16, r=3 %.3f/%.3f/%.3f; trope sharing adds %.3f; companion B=8 %.3f/%.3f/%.3f"
      % ("PASS" if ok else "FAIL", tab[6][0], tab[12][0], tab[16][0], tab[6][3], tab[12][3], tab[16][3], tab[16][3] - nt, *c))
