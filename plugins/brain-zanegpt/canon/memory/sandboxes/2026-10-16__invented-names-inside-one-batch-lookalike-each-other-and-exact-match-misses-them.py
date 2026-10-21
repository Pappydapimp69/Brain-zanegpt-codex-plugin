# Every video invents its own game name (syllable generator). Check the names AGAINST EACH OTHER in one batch:
# exact duplicates vs edit distance <= 1 and <= 2. Seeded, stdlib only.
import random, itertools
SYL = ["ba","ko","mi","ru","ta","ne","so","li","pu","ze","fa","do"]
def name(rng, n): return "".join(rng.choice(SYL) for _ in range(n))
def lev(a, b):
    p = list(range(len(b)+1))
    for i, x in enumerate(a, 1):
        c = [i]
        for j, y in enumerate(b, 1): c.append(min(p[j]+1, c[-1]+1, p[j-1]+(x != y)))
        p = c
    return p[-1]
def trial(rng, k, syl):
    ns = [name(rng, syl) for _ in range(k)]
    ex = sum(a == b for a, b in itertools.combinations(ns, 2))
    d1 = sum(0 < lev(a, b) <= 1 for a, b in itertools.combinations(ns, 2))
    d2 = sum(0 < lev(a, b) <= 2 for a, b in itertools.combinations(ns, 2))
    return ex > 0, d1 > 0, d2 > 0
N = 600; out = {}
for k, syl in ((8, 3), (16, 3), (30, 3), (30, 2), (30, 4)):
    rng = random.Random(k*10+syl); r = [trial(rng, k, syl) for _ in range(N)]
    out[(k, syl)] = tuple(sum(x[i] for x in r)/N for i in range(3))
    print("k=%d syllables=%d batches with exact dup %.2f, edit<=1 %.2f, edit<=2 %.2f" % ((k, syl)+out[(k, syl)]))
a = out[(30, 3)]; b = out[(30, 4)]
ok = a[0] < a[2] and a[2] > 0.5 and b[2] < a[2]
print("RESULT: %s at 30 videos x 3 syllables exact dup %.2f vs edit<=2 lookalike %.2f; 4 syllables edit<=2 %.2f; 2 syllables exact %.2f" % (
    "PASS" if ok else "FAIL", a[0], a[2], b[2], out[(30, 2)][0]))
