# Sandbox: two-pass letters -> closure-based shape verdict, with hyphenated end words judged by whole word vs last segment.
import itertools

# word: (perfect key, vowel key, hyphenated segments)
LEX = {
    "today":   ("AY",  "A", ["to", "day"]),
    "away":    ("AY",  "A", ["a", "way"]),
    "delight": ("ITE", "I", ["de", "light"]),
    "tonight": ("ITE", "I", ["to", "night"]),
    "river":   ("IVER", "I", ["ri", "ver"]),
    "tiger":   ("IGER", "I", ["ti", "ger"]),
    "mother":  ("UTHER", "U", ["moth", "er"]),
    "other":   ("UTHER", "U", ["o", "ther"]),
}
# toy keys for a segment: only the trailing segment's own sound (no context from earlier segments)
SEGKEY = {"day": ("AY", "A"), "way": ("AY", "A"), "light": ("ITE", "I"), "night": ("ITE", "I"),
          "ver": ("ER", "E"), "ger": ("ER", "E"), "er": ("ER", "E"), "ther": ("ER", "E")}

def keys(word, mode):
    perfect, vowel, segs = LEX[word]
    if mode == "whole":
        return perfect, vowel
    return SEGKEY[segs[-1]]          # last-segment judge on hyphenated word

def letters(words, mode):
    ks = [keys(w, mode) for w in words]
    out, nxt, perfect_letter = [None]*len(ks), 0, {}
    for i, (p, v) in enumerate(ks):                      # pass 1: perfect groups, uppercase
        if any(ks[j][0] == p for j in range(len(ks)) if j != i):
            if p not in perfect_letter:
                perfect_letter[p] = chr(65 + nxt); nxt += 1
            out[i] = perfect_letter[p]
    vowel_letter = {}
    for i, (p, v) in enumerate(ks):                      # pass 2: assonance for the unresolved, lowercase
        if out[i] is None:
            if any(ks[j][1] == v for j in range(len(ks)) if j != i):
                if v not in vowel_letter:
                    vowel_letter[v] = chr(97 + nxt); nxt += 1
                out[i] = vowel_letter[v]
            else:
                out[i] = chr(97 + nxt); nxt += 1
    return "".join(out)

def verdict(scheme):
    """stable = every line closes within 1 line on uppercase-resolved letters; else open"""
    last, worst = {}, 0
    for i, c in enumerate(scheme):
        if c.isupper():
            if c in last: worst = max(worst, i - last[c])
            last[c] = i
    unresolved = sum(1 for c in scheme if c.islower())
    return "stable" if worst <= 1 and unresolved == 0 else "open"

total = bad_letter = bad_verdict = stable_to_open = open_to_stable = 0
shapes_hit = set()
for st in itertools.product(LEX, repeat=4):
    a, b = letters(st, "whole"), letters(st, "last")
    # compare as partitions-with-case: normalise letters by first appearance, keep case
    def norm(s):
        m, o = {}, []
        for c in s:
            m.setdefault(c, len(m)); o.append(("U" if c.isupper() else "l") + str(m[c]))
        return o
    total += 1
    if norm(a) != norm(b): bad_letter += 1
    va, vb = verdict(a), verdict(b)
    if va != vb:
        bad_verdict += 1
        if va == "stable": stable_to_open += 1
        else: open_to_stable += 1
        shapes_hit.add((a, b))

# BREAK scenario: only words whose last segment carries the whole rhyme (today/away/delight/tonight)
SAFE = ["today", "away", "delight", "tonight"]
safe_bad = sum(1 for st in itertools.product(SAFE, repeat=4)
               if verdict(letters(st, "whole")) != verdict(letters(st, "last")) or letters(st, "whole") != letters(st, "last"))
print("stanzas", total, "| mislettered by last-segment judge", bad_letter, "(%.1f%%)" % (100*bad_letter/total))
print("shape verdict wrong", bad_verdict, "(%.1f%%): stable->open %d, open->stable %d" % (100*bad_verdict/total, stable_to_open, open_to_stable))
print("safe-word stanzas (256) with any difference:", safe_bad)
print("examples whole->last:", sorted(shapes_hit)[:3])
ok = 0 < bad_verdict < bad_letter and stable_to_open == 0 and open_to_stable > 0 and safe_bad == 0
print("RESULT: %s last-segment judge mislettered %d/%d stanzas but flipped the shape verdict in only %d, all open->stable (false closure); safe-ending words 0 differences"
      % ("PASS" if ok else "FAIL", bad_letter, total, bad_verdict))
