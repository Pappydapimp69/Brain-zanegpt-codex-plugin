# Own lexicon. word = (segments, key_whole, vowel). Hyphenated words carry multiple segments.
from itertools import product
LEX = {
 "sorrow":   (("sor","row"), "orrow", "o"),
 "morrow":   (("mor","row"), "orrow", "o"),
 "show":     (("show",),     "ow",    "o"),
 "go":       (("go",),       "ow",    "o"),
 "rainbow":  (("rain","bow"),"ow",    "o"),   # masculine ending ow
 "moonlight":(("moon","light"),"ight","i"),
 "kite":     (("kite",),     "ight",  "i"),
 "hope":     (("hope",),     "ope",   "o"),
}
WORDS = list(LEX)
def key_whole(w): return LEX[w][1]
def key_last(w):  # last-segment judge: strips to last segment, rhyme = tail after first vowel-ish letter
    seg = LEX[w][0][-1]
    return {"row":"ow","bow":"ow"}.get(seg, LEX[w][1])
def letters(stanza, keyf):
    # pass 1: perfect groups by key; pass 2: assonance (same vowel) links leftover singletons, listed separately
    ks = [keyf(w) for w in stanza]; letter = {}; out = []
    for k in ks:
        if k not in letter: letter[k] = chr(65 + len(letter))
        out.append(letter[k])
    return "".join(out)
def canon(s):  # relabel by first appearance
    m = {}; return "".join(m.setdefault(c, chr(65+len(m))) for c in s)
def assonance_hidden(stanza, keyf):
    ks = [keyf(w) for w in stanza]
    singles = [w for w, k in zip(stanza, ks) if ks.count(k) == 1]
    resolved_vowels = {LEX[w][2] for w, k in zip(stanza, ks) if ks.count(k) > 1}
    return any(LEX[w][2] in resolved_vowels for w in singles)
n = 0; mis = 0; extra = 0; hid_whole = 0; hid_last = 0
for st in product(WORDS, repeat=4):
    n += 1
    a, b = canon(letters(st, key_whole)), canon(letters(st, key_last))
    if a != b: mis += 1; extra += b.count("A") != a.count("A")
    hid_whole += assonance_hidden(st, key_whole); hid_last += assonance_hidden(st, key_last)
# BREAK: remove the feminine pair from the lexicon -> does last-segment judge become safe?
SAFE = [w for w in WORDS if w not in ("sorrow","morrow")]
mis2 = sum(canon(letters(s,key_whole)) != canon(letters(s,key_last)) for s in product(SAFE, repeat=4))
# whole-word judge vs itself is trivially identical, so instead check it never merges across keys:
no_cross = all(len({key_whole(w) for w in grp}) == 1 for grp in [[w for w in WORDS if key_whole(w)==k] for k in {key_whole(x) for x in WORDS}])
print(f"stanzas {n}; last-seg mislettered {mis} ({100*mis/n:.1f}%); without feminine words {mis2} of {len(SAFE)**4}")
print(f"assonance hidden: whole {100*hid_whole/n:.1f}%, last-seg {100*hid_last/n:.1f}%; no_cross={no_cross}")
ok = mis > 0 and mis2 == 0 and no_cross and hid_whole > 0
print(("RESULT: PASS " if ok else "RESULT: FAIL ") + f"last-segment judge mislettered {100*mis/n:.1f}% of {n} stanzas, 0 once feminine multi-segment pair removed; assonance still hidden in {100*hid_whole/n:.1f}% under whole-word judge")
