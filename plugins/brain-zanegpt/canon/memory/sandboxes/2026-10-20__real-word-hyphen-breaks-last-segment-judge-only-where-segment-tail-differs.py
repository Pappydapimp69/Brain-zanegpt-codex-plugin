"""Sandbox: real-word end words, hyphenated at syllable breaks, judged by whole word vs by last segment (read as its own word),
then lettered with two-pass (uppercase resolved, lowercase assonance). All 16^4 stanzas over a 16-word pool. No RNG.
Prediction (before run): fewer than 10 percent of stanzas change letters under the last-segment judge (real words keep their
final syllable's rhyme: night, day, way, low, fore, on, out), every change involves a word whose segment tail differs
(someone, anywhere, beautiful), and most changes are case flips (a resolved rhyme dropping to assonance or none)."""
from itertools import product
# word: (hyphenated form, whole-word tail from stressed vowel, tail of the last segment read as its own word)
W = {
 "tonight":  ("to-night",   ("AY", "T"),       ("AY", "T")),
 "today":    ("to-day",     ("EY", ""),        ("EY", "")),
 "away":     ("a-way",      ("EY", ""),        ("EY", "")),
 "below":    ("be-low",     ("OW", ""),        ("OW", "")),
 "before":   ("be-fore",    ("AO", "R"),       ("AO", "R")),
 "upon":     ("u-pon",      ("AA", "N"),       ("AA", "N")),
 "without":  ("with-out",   ("AW", "T"),       ("AW", "T")),
 "someone":  ("some-one",   ("AH", "M W AH N"), ("AH", "N")),
 "anywhere": ("an-y-where", ("EH", "N IY W EH R"), ("EH", "R")),
 "beautiful": ("beau-ti-ful", ("UW", "T AH F AH L"), ("UH", "L")),
 "light":    ("light",      ("AY", "T"),       ("AY", "T")),
 "say":      ("say",        ("EY", ""),        ("EY", "")),
 "sun":      ("sun",        ("AH", "N"),       ("AH", "N")),
 "there":    ("there",      ("EH", "R"),       ("EH", "R")),
 "door":     ("door",       ("AO", "R"),       ("AO", "R")),
 "sound":    ("sound",      ("AW", "N D"),     ("AW", "N D")),
}
NAMES = list(W)

def rel(a, b):
    if a == b: return "perfect"
    if a[0] == b[0]: return "assonance"
    return None

def letters(words, which):
    keys = [W[w][1 if which == "whole" else 2] for w in words]
    out = [None] * 4; nxt = 0
    for i in range(4):
        if out[i]: continue
        grp = [j for j in range(i, 4) if not out[j] and rel(keys[i], keys[j]) == "perfect" and (j == i or words[j] != words[i])]
        if len(grp) > 1:
            for j in grp: out[j] = chr(65 + nxt)
            nxt += 1
    low = 0
    for i in range(4):
        if out[i]: continue
        grp = [j for j in range(i, 4) if not out[j] and rel(keys[i], keys[j]) in ("perfect", "assonance")]
        if len(grp) > 1:
            for j in grp: out[j] = chr(97 + low)
            low += 1
    s = "".join(c or "X" for c in out)
    m = {}; r = []
    for c in s:
        if c == "X": r.append("X"); continue
        if c not in m: m[c] = chr((65 if c.isupper() else 97) + sum(1 for k in m if k.isupper() == c.isupper()))
        r.append(m[c])
    return "".join(r)

def case_profile(s): return "".join("U" if c.isupper() and c != "X" else "l" if c.islower() else "x" for c in s)

n = changed = case_changed = 0; risky_in_all = True; changed_by_word = {w: 0 for w in NAMES}
for combo in product(NAMES, repeat=4):
    n += 1
    a = letters(combo, "whole"); b = letters(combo, "segment")
    if a != b:
        changed += 1
        if case_profile(a) != case_profile(b): case_changed += 1
        bad = [w for w in combo if W[w][1] != W[w][2]]
        if not bad: risky_in_all = False
        for w in set(combo): changed_by_word[w] += 1
print("stanzas %d, letters change under last-segment judge: %d (%.2f%%)" % (n, changed, 100 * changed / n))
print("of those, resolved/assonance case profile changes: %d (%.1f%%)" % (case_changed, 100 * case_changed / max(1, changed)))
print("every changed stanza contains a word with differing segment tail:", risky_in_all)
print("changed stanzas containing each word:", {w: c for w, c in changed_by_word.items() if c})
ok = changed / n < 0.10 and risky_in_all and case_changed / max(1, changed) > 0.5
print("RESULT: %s last-segment judging on real hyphenated words changes two-pass letters in %d/%d stanzas (%.2f%%), all containing a word whose last segment rhymes differently (someone, anywhere, beautiful); %d of %d changes (%.1f%%) alter the resolved/assonance case profile"
      % ("PASS" if ok else "FAIL", changed, n, 100 * changed / n, case_changed, changed, 100 * case_changed / max(1, changed)))
