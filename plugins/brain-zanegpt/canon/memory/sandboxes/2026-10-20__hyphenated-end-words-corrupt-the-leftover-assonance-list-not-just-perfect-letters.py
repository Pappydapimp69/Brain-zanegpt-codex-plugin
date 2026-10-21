"""Do hyphenated end words under a last-segment judge corrupt the LEFTOVER-ASSONANCE list
(not only perfect-rhyme letters)? Own fixture: 7 end words, exhaustive 7^4 = 2401 stanzas.
word: (segments, per-segment (vowel, coda), stressed index). Truth = whole word key
(stressed syllable through end); assonance = same stressed vowel, different key.
Judge W IS the reference (whole-word key), so it is right by construction and is not scored; judge S sees only the last hyphen segment.
PREDICTION (before run): judge S mislabels >= 30% of stanzas on
the perfect letters AND adds spurious or drops true leftover-assonance links in a further
share (>= 10%) of the stanzas whose perfect letters were still correct."""
from itertools import product
LEX = {
 "fire":   (["fi", "re"],   [("ai", ""), ("ai", "r")], 0),   # key (ai,"")+(ai,r) -> use phonetic: stressed 'ai' + 'r'
 "desire": (["de", "sire"], [("i", ""), ("ai", "r")], 1),
 "higher": (["hi", "gher"], [("ai", ""), ("u", "r")], 0),
 "river":  (["ri", "ver"],  [("i", ""), ("u", "r")], 0),
 "mother": (["mo", "ther"], [("u", ""), ("u", "r")], 0),
 "cover":  (["co", "ver"],  [("u", ""), ("u", "r")], 0),
 "light":  (["light"],      [("ai", "t")], 0),
}
KEYS = {"fire": ("ai", "r"), "desire": ("ai", "r"), "higher": ("ai", "er"), "river": ("i", "er"),
        "mother": ("u", "er"), "cover": ("u", "er"), "light": ("ai", "t")}   # whole-word truth (vowel, tail)
def whole(w): return KEYS[w]
def last(w):  # judge S: only the last segment's (vowel, coda)
    v, c = LEX[w][1][-1]; return (v, c if c else "-")
def perfect_groups(ws, key):
    g = {}
    for i, w in enumerate(ws): g.setdefault(key(w), []).append(i)
    return sorted(tuple(v) for v in g.values() if len(v) > 1)
def assonance_links(ws, key, vow):
    pg = perfect_groups(ws, key); in_pg = {i for g in pg for i in g}
    left = [i for i in range(len(ws)) if i not in in_pg]
    links = set()
    for i in left:
        for j in range(len(ws)):
            if j != i and key(ws[j]) != key(ws[i]) and vow(ws[j]) == vow(ws[i]): links.add(tuple(sorted((i, j))))
    return tuple(sorted(links))
vow_w = lambda w: whole(w)[0]
vow_s = lambda w: last(w)[0]
N = bad_perfect = bad_assoc_given_perfect_ok = perfect_ok = 0
for st in product(LEX, repeat=4):
    N += 1
    tp, ta = perfect_groups(st, whole), assonance_links(st, whole, vow_w)
    sp, sa = perfect_groups(st, last), assonance_links(st, last, vow_s)
    if sp != tp: bad_perfect += 1
    else:
        perfect_ok += 1
        if sa != ta: bad_assoc_given_perfect_ok += 1
p1 = bad_perfect / N; p2 = bad_assoc_given_perfect_ok / perfect_ok if perfect_ok else 0
print("stanzas", N, "judge S perfect-letter errors %d (%.1f%%)" % (bad_perfect, 100*p1))
print("of %d with correct perfect letters, assonance list wrong: %d (%.1f%%)" % (perfect_ok, bad_assoc_given_perfect_ok, 100*p2))
ok = p1 >= 0.30 and p2 >= 0.10
print("RESULT: %s judge S (vs whole-word reference) perfect letters wrong %.1f%% of %d, leftover-assonance list wrong in %.1f%% of the stanzas whose perfect letters were right" % ("PASS" if ok else "FAIL", 100*p1, N, 100*p2))
