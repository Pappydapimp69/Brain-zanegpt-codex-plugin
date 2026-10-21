# Sandbox: two-pass letters report "hidden assonance links" (a lowercase line whose vowel matches a resolved uppercase group).
# Does a last-segment judge on hyphenated end words corrupt that report, not just the letters?
import itertools
LEX = {  # word: (perfect key, vowel key, last-segment (perfect, vowel)); one-segment words keep their own keys
    "tide":    ("IDE", "I", ("IDE", "I")),
    "bride":   ("IDE", "I", ("IDE", "I")),
    "river":   ("IVER", "I", ("ER", "E")),
    "tiger":   ("IGER", "I", ("ER", "E")),
    "silver":  ("ILVER", "I", ("ER", "E")),
    "mother":  ("UTHER", "U", ("ER", "E")),
    "other":   ("UTHER", "U", ("ER", "E")),
    "shine":   ("INE", "I", ("INE", "I")),
}
def keys(w, mode): return (LEX[w][0], LEX[w][1]) if mode == "whole" else LEX[w][2]

def two_pass(ws, mode):
    ks = [keys(w, mode) for w in ws]
    out = [None]*4; pl = {}; n = 0
    for i, (p, v) in enumerate(ks):
        if sum(1 for k in ks if k[0] == p) > 1:
            if p not in pl: pl[p] = chr(65+n); n += 1
            out[i] = pl[p]
    vl = {}
    for i, (p, v) in enumerate(ks):
        if out[i] is None:
            if sum(1 for k in ks if k[1] == v) > 1:
                if v not in vl: vl[v] = chr(97+n); n += 1
                out[i] = vl[v]
            else:
                out[i] = chr(97+n); n += 1
    return out, ks

def hidden_links(ws, mode):
    """lowercase lines whose vowel key equals the vowel key of some uppercase-resolved line (assonance hidden behind a resolved group)"""
    out, ks = two_pass(ws, mode)
    resolved_vowels = {ks[i][1] for i, c in enumerate(out) if c.isupper()}
    return {i for i, c in enumerate(out) if c.islower() and ks[i][1] in resolved_vowels}

total = diff_report = fewer = more = same_letters_diff_report = 0
has_hidden_whole = 0
for st in itertools.product(LEX, repeat=4):
    total += 1
    hw, hl = hidden_links(st, "whole"), hidden_links(st, "last")
    if hw: has_hidden_whole += 1
    if hw != hl:
        diff_report += 1
        fewer += len(hl) < len(hw); more += len(hl) > len(hw)
        a, _ = two_pass(st, "whole"); b, _ = two_pass(st, "last")
        # letters are the same shape yet the report changed?
        if [c.isupper() for c in a] == [c.isupper() for c in b]: same_letters_diff_report += 1
# BREAK: stanzas of one-segment words only (nothing is hyphenated, judge cannot differ)
ONE = ["tide", "bride", "shine"]
break_diff = sum(1 for st in itertools.product(ONE, repeat=4) if hidden_links(st, "whole") != hidden_links(st, "last"))
print("stanzas", total, "| with a hidden link (whole-word judge)", has_hidden_whole, "(%.1f%%)" % (100*has_hidden_whole/total))
print("report differs under last-segment judge:", diff_report, "(%.1f%%) | fewer links %d, more links %d" % (100*diff_report/total, fewer, more))
print("case pattern identical but report differs:", same_letters_diff_report)
print("one-segment-only stanzas (81) with a difference:", break_diff)
ok = diff_report > 0 and fewer > more and break_diff == 0
print("RESULT: %s last-segment judge changed the hidden-assonance report in %d of %d stanzas (%d with fewer links, %d with more); one-segment words 0 differences"
      % ("PASS" if ok else "FAIL", diff_report, total, fewer, more))
