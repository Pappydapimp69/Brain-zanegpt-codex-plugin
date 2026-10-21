"""Sandbox: reduced sung forms (kernel: write-the-reduced-form), hyphenation (hyphenate-to-slow),
and two-pass rhyme lettering together on all 4-line stanzas over a small end-word lexicon.
Judge = stressed-vowel + coda tail from a hand phoneme table. Deterministic, stdlib only."""
from itertools import product

# word -> (stressed vowel, tail after vowel)
PH = {
 "to": ("UW", ""), "you": ("UW", ""), "through": ("UW", ""),
 "gonna": ("AO", "N AH"), "wanna": ("AA", "N AH"), "donna": ("AA", "N AH"),
 "of": ("AH", "V"), "love": ("AH", "V"), "kinda": ("AY", "N D AH"), "finder": ("AY", "N D ER"),
 "them": ("EH", "M"), "'em": ("EH", "M"), "gem": ("EH", "M"),
 "because": ("AH", "Z"), "'cause": ("AO", "Z"), "does": ("AH", "Z"),
}
# lexicon slots: each entry = (full form, reduced form)
SLOTS = [("to", "gonna"), ("to", "wanna"), ("of", "kinda"), ("them", "'em"),
         ("because", "'cause"), ("you", "you"), ("love", "love"), ("gem", "gem")]
HY = {"gonna": "gon-na", "wanna": "wan-na", "kinda": "kin-da"}   # hyphenated forms

def judge_whole(w):
    w = w.replace("-", "")
    return PH[w]

def judge_last_segment(w):
    # a naive judge keying only the text after the last hyphen: maps segment to a tail by spelling
    seg = w.split("-")[-1]
    return ("SEG", seg)

def rel(a, b):
    if a == b: return "perfect"
    if a[0] == b[0] and a[0] != "SEG": return "assonance"
    return None

def letters(words, judge, strict_same_word=True):
    keys = [judge(w) for w in words]
    out = [None] * len(words); nxt = 0
    for i in range(len(words)):                       # pass 1: resolved rhymes, uppercase
        if out[i]: continue
        grp = [j for j in range(i, len(words)) if not out[j] and rel(keys[i], keys[j]) == "perfect"
               and (j == i or words[j] != words[i] or not strict_same_word)]
        if len(grp) > 1:
            for j in grp: out[j] = chr(65 + nxt)
            nxt += 1
    low = 0
    for i in range(len(words)):                       # pass 2: assonance among unlettered, lowercase
        if out[i]: continue
        grp = [j for j in range(i, len(words)) if not out[j] and rel(keys[i], keys[j]) in ("perfect", "assonance")]
        if len(grp) > 1:
            for j in grp: out[j] = chr(97 + low)
            low += 1
    return "".join(c if c else "X" for c in out)

def norm(s):
    # canonical relabel (uppercase/lowercase kept) so XAXA == XBXB
    m = {}; r = []
    for c in s:
        if c == "X": r.append("X"); continue
        if c not in m: m[c] = chr((65 if c.isupper() else 97) + sum(1 for k in m if k.isupper() == c.isupper()))
        r.append(m[c])
    return "".join(r)

n = 0; changed = 0; changed_by_slot = {}; hy_wrong = 0; hy_changed_vs_reduced = 0
by_item = {i: 0 for i in range(len(SLOTS))}
for combo in product(range(len(SLOTS)), repeat=4):
    n += 1
    full = [SLOTS[i][0] for i in combo]; red = [SLOTS[i][1] for i in combo]
    lf = norm(letters(full, judge_whole)); lr = norm(letters(red, judge_whole))
    if lf != lr:
        changed += 1
        for i in set(combo): by_item[i] += 1
    hy = [HY.get(w, w) for w in red]
    lh_whole = norm(letters(hy, judge_whole)); lh_seg = norm(letters(hy, judge_last_segment))
    if lh_whole != lr: hy_changed_vs_reduced += 1
    if lh_seg != lr: hy_wrong += 1
print("stanzas:", n)
print("full vs reduced letters differ: %d (%.1f%%)" % (changed, 100 * changed / n))
for i, c in by_item.items():
    print("  slot %-14s appears in %d changed stanzas" % ("%s>%s" % SLOTS[i], c))
print("whole-word judge on hyphenated reduced forms differs from unhyphenated: %d" % hy_changed_vs_reduced)
print("last-segment judge on hyphenated reduced forms differs from unhyphenated: %d (%.1f%%)" % (hy_wrong, 100 * hy_wrong / n))
em_slot = 3
ok = changed > 0 and hy_changed_vs_reduced == 0 and hy_wrong > 0
print("RESULT: %s reduced end words change two-pass letters in %d/%d stanzas (%.1f%%), hyphenating them is safe under a whole-word judge (%d changes) but a last-segment judge mislabels %d/%d (%.1f%%)"
      % ("PASS" if ok else "FAIL", changed, n, 100 * changed / n, hy_changed_vs_reduced, hy_wrong, n, 100 * hy_wrong / n))
