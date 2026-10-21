"""Spelling rhyme judge (last 3 letters of the last token) with and without hyphenated
end words, scored against a hand-keyed phonetic truth, exhaustive over 4-line stanzas.
Stdlib only, deterministic."""
from itertools import product

# word: (hyphenated spelling, phonetic perfect-rhyme key)
LEX = {
    "freely":   ("free-ly",   "EE-lee"),
    "gladly":   ("glad-ly",   "AD-lee"),
    "sadly":    ("sad-ly",    "AD-lee"),
    "madly":    ("mad-ly",    "AD-lee"),
    "lightly":  ("light-ly",  "AIT-lee"),
    "tonight":  ("to-night",  "AIT"),
    "delight":  ("de-light",  "AIT"),
    "away":     ("a-way",     "AY"),
    "today":    ("to-day",    "AY"),
    "ocean":    ("o-cean",    "OH-shun"),
    "motion":   ("mo-tion",   "OH-shun"),
    "kite":     ("kite",      "AIT"),
}
WORDS = list(LEX)
N_LETTERS = 3

def spell(w, hyph):
    text = LEX[w][0] if hyph else LEX[w][0].replace("-", "")
    return text.split("-")[-1][-N_LETTERS:]

def partition(words, key):
    g = {}
    for i, w in enumerate(words):
        g.setdefault(key(w), []).append(i)
    return sorted(tuple(v) for v in g.values() if len(v) > 1)

truth = lambda w: LEX[w][1]
stanzas = list(product(WORDS, repeat=4))
n = len(stanzas)
wrong_plain = sum(partition(s, lambda w: spell(w, False)) != partition(s, truth) for s in stanzas)
wrong_hyph = sum(partition(s, lambda w: spell(w, True)) != partition(s, truth) for s in stanzas)
changed = sum(partition(s, lambda w: spell(w, False)) != partition(s, lambda w: spell(w, True)) for s in stanzas)
fixed = sum(partition(s, lambda w: spell(w, False)) != partition(s, truth) and partition(s, lambda w: spell(w, True)) == partition(s, truth) for s in stanzas)
broken = sum(partition(s, lambda w: spell(w, False)) == partition(s, truth) and partition(s, lambda w: spell(w, True)) != partition(s, truth) for s in stanzas)
print(f"stanzas {n}; spelling judge wrong plain {wrong_plain} ({100*wrong_plain/n:.1f}%), hyphenated {wrong_hyph} ({100*wrong_hyph/n:.1f}%)")
print(f"hyphenation changes the spelling verdict in {changed}; repairs {fixed}, breaks {broken}")
pairs = sorted({(a, b) for a in WORDS for b in WORDS if a < b and (spell(a, True) == spell(b, True)) != (spell(a, False) == spell(b, False))})
print("pairs whose spelling match flips with hyphenation:", pairs)
ok = wrong_plain > 0 and changed >= 0.05 * n and broken > fixed
print(f"RESULT: {'PASS' if ok else 'FAIL'} spelling judge wrong in {wrong_plain}/{n} plain vs {wrong_hyph}/{n} hyphenated; hyphenation changed the verdict in {changed}, repaired {fixed}, broke {broken}")
