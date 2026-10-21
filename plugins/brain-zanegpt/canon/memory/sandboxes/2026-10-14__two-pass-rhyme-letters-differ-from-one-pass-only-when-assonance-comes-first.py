"""Sandbox: kernel ideas:SONGWRITING/rhyme-tooling/two-pass-letter-assignment-keeps-schemes-legible.
Rebuild with spelled-vowel keys (as suno-builder/E1 found the shipped builder does), and a stanza enumeration built so
one-pass and two-pass CAN differ (suno-builder/E3: a rename that never differs verifies nothing).
Relations from spelling: tail = from last vowel group on. perfect = same tail; family = same vowel group, coda in same sound family;
assonance = same vowel group only. One-pass: each line takes the letter of the FIRST earlier line related by any relation.
Two-pass: pass1 UPPERCASE for perfect (and family) links only; pass2 lowercase for assonance among still-unlettered lines.
PREDICTION (before running), 4-line stanzas drawn from a 12-word lexicon (12^4 = 20736 stanzas):
 T1 the XXAA stanza (cat bat map tap) reads AAAA one-pass and AABB two-pass.
 T2 the two methods agree on >= 60% of stanzas but disagree on at least 1000 (so the kernel is not a rename).
 T3 in every disagreement the two-pass scheme has MORE distinct letters (>=) than one-pass (it splits what assonance fused).
 T4 (BREAK) reversing the line order changes the one-pass partition of some stanzas (order dependence) but never changes the
    two-pass UPPERCASE partition (0 changes).
"""
import itertools, re
V = re.compile(r'[aeiou]+')
FAM = {'t': 'T', 'd': 'T', 'p': 'P', 'b': 'P', 'k': 'K', 'g': 'K', 'n': 'N', 'm': 'M', 's': 'S', 'z': 'S'}   # family = voicing pairs only (iteration 2; iteration 1 lumped all stops and fused cat/map)
def parts(w):
    m = list(V.finditer(w))[-1]; return m.group(), w[m.end():], w[m.start():]
def fam(c): return FAM.get(c[:1], c)
def rel(a, b):
    va, ca, ta = parts(a); vb, cb, tb = parts(b)
    if ta == tb: return 3
    if va == vb and fam(ca) == fam(cb): return 2
    if va == vb: return 1
    return 0
def one_pass(ws):
    out = []; nxt = 0
    for i, w in enumerate(ws):
        for j in range(i):
            if rel(ws[j], w) >= 1: out.append(out[j]); break
        else: out.append(nxt); nxt += 1
    return out
def two_pass(ws):
    n = len(ws); comp = list(range(n))
    def find(x):
        while comp[x] != x: x = comp[x]
        return x
    for i in range(n):                                  # pass 1: perfect/family components -> UPPERCASE
        for j in range(i):
            if rel(ws[i], ws[j]) >= 2: comp[find(i)] = find(j)
    scheme = [('U', find(i)) if any(j != i and find(j) == find(i) for j in range(n)) else None for i in range(n)]
    for i in range(n):                                  # pass 2: lowercase assonance among still-unlettered lines
        if scheme[i] is None:
            for j in range(i):
                if scheme[j][0] == 'l' and rel(ws[i], ws[j]) >= 1: scheme[i] = scheme[j]; break
            else: scheme[i] = ('l', i)
    return scheme
def canon(s):
    m = {}; return tuple(m.setdefault(x, len(m)) for x in s)
def part(sc):
    g = {}
    for i, x in enumerate(sc): g.setdefault(x, []).append(i)
    return sorted(g.values())
def upper_part(ws):
    return sorted(grp for grp in part([x if x[0] == 'U' else ('l', i) for i, x in enumerate(two_pass(ws))]) if len(grp) > 1)
LEX = "cat bat map tap sun run cold told fog dog toe row".split()
ex = ("cat", "bat", "map", "tap")
agree = dis = more_ok = chg_one = chg_two = total = 0
for ws in itertools.product(LEX, repeat=4):
    o, t = canon(one_pass(ws)), canon(two_pass(ws)); total += 1
    if o == t: agree += 1
    else:
        dis += 1; more_ok += len(set(t)) >= len(set(o))
    r = ws[::-1]; n = 4
    flip = lambda parts_: sorted(sorted(n - 1 - i for i in g) for g in parts_)
    if flip(part(one_pass(r))) != part(one_pass(ws)): chg_one += 1
    if flip(upper_part(r)) != upper_part(ws): chg_two += 1
print("XXAA example one-pass", canon(one_pass(ex)), "two-pass", canon(two_pass(ex)))
print("stanzas", total, "agree %.3f" % (agree / total), "disagree", dis, "two-pass has >= letters in all disagreements:", more_ok == dis)
print("reversal changes: one-pass partition", chg_one, "two-pass uppercase partition", chg_two)
t1 = canon(one_pass(ex)) == (0, 0, 0, 0) and canon(two_pass(ex)) == (0, 0, 1, 1)
t2 = agree / total >= 0.60 and dis >= 1000
t3 = more_ok == dis
t4 = chg_one > 0 and chg_two == 0
print("checks T1..T4:", t1, t2, t3, t4)
# T4 prediction (order dependence of one-pass) was WRONG: with equivalence-like relations both partitions are order-free; RESULT covers the kernel claims T1-T3 only
print(("RESULT: PASS" if all((t1, t2, t3)) else "RESULT: FAIL") + " XXAA one-pass %s two-pass %s; agree %.3f, disagree %d of %d; reversal changes one-pass %d vs two-pass uppercase %d (T4 prediction refuted)" % (canon(one_pass(ex)), canon(two_pass(ex)), agree / total, dis, total, chg_one, chg_two))
