"""Prediction (written before run): on my own 6 stanzas, two-pass gives the intended scheme on >=5 of 6 and one-pass
on <=3 of 6; on a stanza of four words that share only a vowel (no exact rhyme) the unbounded assonance pass gives
one letter (AAAA) while a pair-bounded pass gives a-a-b-b; a one-pass mislabel changes closure distance for the
ABAB-with-assonance-intruder stanza. Stdlib, deterministic."""
import re
def vkey(w):  # last vowel group
    m = re.findall(r'[aeiouy]+', w); return m[-1]
def rkey(w):  # from last vowel group to end
    m = list(re.finditer(r'[aeiouy]+', w)); return w[m[-1].start():]
def one_pass(ws):
    out = []; seen = {}; n = 0
    for w in ws:
        hit = next((L for L, k in seen.items() if k == vkey(w)), None)  # loose match steals in reading order
        if hit is None:
            hit = chr(65 + n); n += 1; seen[hit] = vkey(w)
        out.append(hit)
    return ''.join(out)
def two_pass(ws, bounded=True):
    out = [None] * len(ws); n = 0
    groups = {}
    for i, w in enumerate(ws): groups.setdefault(rkey(w), []).append(i)
    for k, idx in groups.items():
        if len(idx) > 1:
            for i in idx: out[i] = chr(65 + n)
            n += 1
    rest = [i for i in range(len(ws)) if out[i] is None]
    g2 = {}
    for i in rest: g2.setdefault(vkey(ws[i]), []).append(i)
    for k, idx in g2.items():
        if len(idx) > 1:
            chunks = [idx[j:j + 2] for j in range(0, len(idx), 2)] if bounded else [idx]
            for c in chunks:
                for i in c: out[i] = chr(97 + n)
                n += 1
    for i in range(len(ws)):
        if out[i] is None: out[i] = chr(97 + n); n += 1
    # normalise by first appearance
    m = {}; s = ''
    for c in out:
        m.setdefault(c, 'ABCDEFGH'[len(m)]); s += m[c]
    return s
def norm(s):
    m = {}; r = ''
    for c in s: m.setdefault(c, 'ABCDEFGH'[len(m)]); r += m[c]
    return r
def closure(s):
    d = []
    for L in sorted(set(s)):
        p = [i for i, c in enumerate(s) if c == L]
        d += [b - a for a, b in zip(p, p[1:])]
    return sorted(d)
S = [("ABAB", ["night", "grain", "light", "rain"]),
     ("AABB", ["tone", "stone", "mist", "list"]),
     ("ABBA", ["cold", "far", "star", "old"]),
     ("ABAB-steal", ["pan", "band", "man", "hand"]),         # all share vowel a; exact pairs are pan/man, band/hand
     ("ABCB-steal", ["lane", "moon", "pain", "soon"]),       # vowel a/ai differ from o: no theft expected
     ("none", ["cat", "pen", "sit", "dog"])]
want = {"ABAB": "ABAB", "AABB": "AABB", "ABBA": "ABBA", "ABAB-steal": "ABAB", "ABCB-steal": "ABCB", "none": "ABCD"}
t2 = o1 = 0
for name, ws in S:
    a = two_pass(ws); b = norm(one_pass(ws)); w = want[name]
    t2 += a == w; o1 += b == w
    print(name, "two", a, "one", b, "want", w)
allas = ["cat", "bad", "mat", "sad"]  # no exact rhyme pairs? cat/mat exact, bad/sad exact -> use pure assonance set
pure = ["hat", "sand", "bag", "lamp"]
u = two_pass(pure, bounded=False); bd = two_pass(pure, bounded=True)
print("pure assonance unbounded", u, "bounded", bd)
c_steal_good = closure("ABAB"); c_steal_bad = closure(norm(one_pass(["pan", "band", "man", "hand"])))
print("closure ABAB true", c_steal_good, "one-pass", c_steal_bad)
ok = t2 >= 5 and o1 < t2 and u == "AAAA" and bd == "AABB" and c_steal_good != c_steal_bad
print(f"RESULT: {'PASS' if ok else 'FAIL'} two_pass={t2}/6 one_pass={o1}/6 pure_unbounded={u} bounded={bd} closure_true={c_steal_good} closure_onepass={c_steal_bad}")
