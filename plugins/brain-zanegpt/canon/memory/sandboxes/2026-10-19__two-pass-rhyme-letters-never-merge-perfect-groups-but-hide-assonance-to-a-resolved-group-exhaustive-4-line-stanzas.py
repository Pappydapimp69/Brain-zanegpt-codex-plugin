"""Prediction (before run): over ALL 6^4=1296 four-line stanzas (line = vowel in {a,e,i} x coda in {1,2}),
one-pass any-rhyme lettering gives the same letter to two lines that are NOT perfect rhymes in a
nonzero share of stanzas (>=30%), while two-pass uppercase groups equal the true perfect-rhyme groups
in 100% of stanzas. BREAK: the two-pass scheme leaves a line that is assonant with a resolved group
unlettered (shown as a fresh lowercase or dash), so in at least 5% of stanzas it hides an
assonance link that exists; the share is predicted to be between 5% and 40%."""
import itertools
lines_t = [(v, c) for v in "aei" for c in (1, 2)]
def perfect_groups(st):
    g = {}
    for i, l in enumerate(st): g.setdefault(l, []).append(i)
    return sorted(tuple(x) for x in g.values() if len(x) > 1)
def one_pass(st):
    letters, nxt, out = {}, 0, []
    for l in st:
        k = l[0]                       # any rhyme type counts: vowel match
        if k not in letters: letters[k] = chr(65 + nxt); nxt += 1
        out.append(letters[k])
    return out
def groups_of(lab):
    g = {}
    for i, x in enumerate(lab): g.setdefault(x, []).append(i)
    return sorted(tuple(x) for x in g.values() if len(x) > 1)
def two_pass(st):
    lab = [None] * len(st); nxt = 0
    for grp in perfect_groups(st):
        for i in grp: lab[i] = chr(65 + nxt)
        nxt += 1
    rest = [i for i, x in enumerate(lab) if x is None]
    by_v = {}
    for i in rest: by_v.setdefault(st[i][0], []).append(i)
    for v, idx in by_v.items():
        if len(idx) > 1:
            for i in idx: lab[i] = chr(97 + nxt)
            nxt += 1
    return lab
n = merge1 = ok2 = hidden = 0
for st in itertools.product(lines_t, repeat=4):
    n += 1
    pg = perfect_groups(st)
    o = one_pass(st); t = two_pass(st)
    # one-pass merges non-perfect lines: some group of equal letters not a union consistent with perfect rhyme
    if any(st[i] != st[j] for g in groups_of(o) for i in g for j in g): merge1 += 1
    up = sorted(tuple(i for i, x in enumerate(t) if x == L) for L in set(x for x in t if x and x.isupper()))
    ok2 += (up == pg)
    # hidden assonance: an unlettered line shares a vowel with a resolved (uppercase) line
    if any(x is None and any(t[j] and t[j].isupper() and st[j][0] == st[i][0] for j in range(4)) for i, x in enumerate(t)): hidden += 1
print(n, merge1, ok2, hidden)
p1, p2, ph = merge1 / n, ok2 / n, hidden / n
ok = n == 1296 and p1 >= .30 and p2 == 1.0 and .05 <= ph <= .40
print(("RESULT: PASS " if ok else "RESULT: FAIL ") +
      f"{n} stanzas: one-pass merges non-perfect lines in {merge1} ({p1:.1%}); two-pass uppercase groups = perfect groups in {ok2}/{n}; two-pass hides assonance to a resolved group in {hidden} ({ph:.1%})")
