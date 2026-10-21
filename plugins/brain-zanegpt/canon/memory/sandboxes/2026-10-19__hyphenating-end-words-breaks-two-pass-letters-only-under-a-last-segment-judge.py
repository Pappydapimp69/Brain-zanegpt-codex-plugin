"""Hyphenating end words to slow a vocal line vs two-pass rhyme lettering.
Judge W keys the whole word (stressed syllable to end); judge S keys only the last
hyphen segment (what a per-token judge sees once 'mo-tion' is split).
Exhaustive over all 9^4 four-line stanzas. Stdlib only, deterministic."""
from itertools import product

# word: (hyphenated segments, per-segment (vowel, coda), stressed segment index)
LEX = {
    "light":     (["light"],            [("ai", "t")], 0),
    "tonight":   (["to", "night"],      [("u", ""), ("ai", "t")], 1),
    "delight":   (["de", "light"],      [("i", ""), ("ai", "t")], 1),
    "motion":    (["mo", "tion"],       [("oh", ""), ("u", "n")], 0),
    "ocean":     (["o", "cean"],        [("oh", ""), ("u", "n")], 0),
    "emotion":   (["e", "mo", "tion"],  [("i", ""), ("oh", ""), ("u", "n")], 1),
    "nation":    (["na", "tion"],       [("ay", ""), ("u", "n")], 0),
    "beautiful": (["beau", "ti", "ful"], [("yoo", ""), ("i", ""), ("u", "l")], 0),
    "dutiful":   (["du", "ti", "ful"],  [("yoo", ""), ("i", ""), ("u", "l")], 0),
}
WORDS = list(LEX)

def key_whole(w):          # perfect-rhyme key: stressed syllable through the end
    segs, ph, st = LEX[w]
    return tuple(ph[st:])

def key_last(w):           # a judge that only sees the final hyphen segment
    return (LEX[w][1][-1],)

def vowel_whole(w):
    return LEX[w][1][LEX[w][2]][0]

def vowel_last(w):
    return LEX[w][1][-1][0]

def two_pass(words, key, vowel):
    """uppercase letters for perfect groups, lowercase for assonance among the rest."""
    n = len(words)
    out = [None] * n
    groups = {}
    for i, w in enumerate(words):
        groups.setdefault(key(w), []).append(i)
    letter = 0
    for g in groups.values():
        if len(g) > 1:
            for i in g:
                out[i] = chr(65 + letter)
            letter += 1
    rest = {}
    for i, w in enumerate(words):
        if out[i] is None:
            rest.setdefault(vowel(w), []).append(i)
    for g in rest.values():
        if len(g) > 1:
            for i in g:
                out[i] = chr(97 + letter)
            letter += 1
    return tuple(out)

def perfect_partition(words, key):
    g = {}
    for i, w in enumerate(words):
        g.setdefault(key(w), []).append(i)
    return sorted(tuple(v) for v in g.values() if len(v) > 1)

stanzas = list(product(WORDS, repeat=4))
bad_last = bad_whole = changed_whole = 0
false_merge_pairs = 0
for s in stanzas:
    truth = perfect_partition(s, key_whole)
    if perfect_partition(s, key_last) != truth:
        bad_last += 1
    if perfect_partition(s, key_whole) != truth:
        bad_whole += 1
    # judge W is a function of the unhyphenated word, so hyphenation cannot touch it
    if two_pass(s, key_whole, vowel_whole) != two_pass([w for w in s], key_whole, vowel_whole):
        changed_whole += 1

N = len(stanzas)
print(f"stanzas {N}; whole-word judge wrong {bad_whole}; last-segment judge wrong {bad_last} ({100*bad_last/N:.1f}%)")
print(f"hyphenation changes two-pass letters under whole-word judge: {changed_whole}")
pairs = [(a, b) for a in WORDS for b in WORDS if a < b and key_last(a) == key_last(b) and key_whole(a) != key_whole(b)]
print("pairs falsely merged by last-segment judge:", len(pairs), pairs[:6])
ok = bad_whole == 0 and changed_whole == 0 and bad_last >= 0.2 * N
print(f"RESULT: {'PASS' if ok else 'FAIL'} last-segment judge broke the perfect-rhyme partition in {bad_last}/{N} stanzas ({100*bad_last/N:.1f}%), "
      f"whole-word judge in {bad_whole}; {len(pairs)} falsely merged word pairs")
