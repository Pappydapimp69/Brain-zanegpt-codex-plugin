"""Sandbox: front-cut a rushed line to a SYLLABLE budget. Does it keep two-pass
rhyme letters, and does it matter whether the cut may split the end word?
Toy lexicon, exhaustive 4-line stanzas, no RNG."""
import itertools

# word -> (syllables, stressed_index, vowel_of_stressed_syllable)
LEX = {
    "cat": (["cat"], 0, "a"), "tap": (["tap"], 0, "a"), "lake": (["lake"], 0, "e"),
    "bake": (["bake"], 0, "e"),
    "tomorrow": (["to", "mor", "row"], 1, "o"), "sorrow": (["sor", "row"], 0, "o"),
    "hollow": (["hol", "low"], 0, "o"), "follow": (["fol", "low"], 0, "o"),
}
ENDS = ["cat", "tap", "lake", "tomorrow", "sorrow", "hollow", "follow"]
FILLER = [("i", 1), ("walk", 1), ("down", 1), ("the", 1), ("road", 1)]  # 5 filler words, 1 syll each

def key_of(sylls, stress, vowel, cut_syl):
    """rhyme key from what survives. cut_syl = number of leading end-word syllables lost."""
    if cut_syl > stress:                     # stressed syllable lost: vowel unknown
        return ("?", "".join(sylls[cut_syl:]))
    return (vowel, "".join(sylls[stress:]))

def letters(items):
    """two-pass: pass1 uppercase for identical keys; pass2 lowercase for same-vowel leftovers."""
    n = len(items); out = [None] * n; nxt = [0]
    def newl():
        c = chr(ord("a") + nxt[0]); nxt[0] += 1; return c
    for i in range(n):
        if out[i]: continue
        grp = [j for j in range(n) if items[j] == items[i] and items[j][0] != "?"]
        if len(grp) > 1:
            c = newl().upper()
            for j in grp: out[j] = c
    for i in range(n):
        if out[i]: continue
        grp = [j for j in range(n) if out[j] is None and items[j][0] == items[i][0] and items[i][0] != "?"]
        if len(grp) > 1:
            c = newl()
            for j in grp: out[j] = c
        else:
            out[i] = "x"
    return "".join(out)

def line_items(end, budget, mode):
    sylls, stress, vowel = LEX[end]
    total = len(sylls) + len(FILLER)
    drop = max(0, total - budget)             # syllables to drop from the front
    if mode == "word":                        # never split the end word
        end_drop = 0
    else:                                     # naive: front cut may eat into end word
        end_drop = max(0, drop - len(FILLER))
    return key_of(sylls, stress, vowel, end_drop)

def run(budget, mode, ends_pool=ENDS):
    kept = total = 0; bad = []
    for st in itertools.product(ends_pool, repeat=4):
        full = letters([key_of(*LEX[e][0:1], LEX[e][1], LEX[e][2], 0) if False else key_of(LEX[e][0], LEX[e][1], LEX[e][2], 0) for e in st])
        cut = letters([line_items(e, budget, mode) for e in st])
        total += 1
        if full == cut: kept += 1
        elif len(bad) < 1: bad.append((st, full, cut))
    return kept, total, bad

res = {}
for b in (4, 3, 2, 1):
    res[("word", b)] = run(b, "word")
    res[("naive", b)] = run(b, "naive")
    print("budget", b, "word-boundary", res[("word", b)][:2], "naive", res[("naive", b)][:2])
print("example naive break:", res[("naive", 1)][2])
# BREAK scenario: pool of only single-syllable ends, naive == word (nothing to split)
mono = ["cat", "tap", "lake", "bake"]
mk, mt, _ = run(1, "naive", mono); wk, wt, _ = run(1, "word", mono)
print("mono pool budget 1 naive", (mk, mt), "word", (wk, wt))

def tail(e): return len(LEX[e][0]) - LEX[e][1]
safe_ok = True; unsafe = unsafe_lost = 0
for b in (4, 3, 2, 1):
    for st in itertools.product(ENDS, repeat=4):
        full = letters([key_of(LEX[e][0], LEX[e][1], LEX[e][2], 0) for e in st])
        cut = letters([line_items(e, b, "naive") for e in st])
        if all(tail(e) <= b for e in st):
            safe_ok &= (full == cut)
        else:
            unsafe += 1; unsafe_lost += (full != cut)
print("naive loses only when an end word's stressed tail exceeds the budget:", safe_ok,
      "| stanzas with such a word:", unsafe, "of which letters changed:", unsafe_lost)
word_all = all(res[("word", b)][0] == res[("word", b)][1] for b in (4, 3, 2, 1))
mono_tie = mk == wk == mt
print("RESULT: %s word-boundary cut kept letters in all %d stanzas at budgets 4..1; naive syllable cut kept all at budget 2 (%d/%d) and lost them only at budget 1 (%d/%d), every loss in stanzas with an end word whose stressed tail exceeds the budget (%d of %d such stanzas changed); single-syllable ends tie (%d/%d)"
      % ("PASS" if (word_all and safe_ok and unsafe_lost > 0 and mono_tie and res[("naive",1)][0] < res[("naive",1)][1]) else "FAIL",
         res[("word", 1)][1], res[("naive", 2)][0], res[("naive", 2)][1],
         res[("naive", 1)][0], res[("naive", 1)][1], unsafe_lost, unsafe, mk, mt))
