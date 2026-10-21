"""Sandbox: one-pass vs two-pass rhyme-scheme letter assignment, scored against INTENDED schemes (the stanza is
generated from a designed scheme, so truth is not defined by either labeller's own predicate).
Word = (vowel, coda). Relation: perfect = same vowel and coda; family = same vowel, coda in the same stop family
(voiced/unvoiced pair: t~d, k~g, p~b); assonance = same vowel only; none otherwise.
Stanza = 4 lines; designed scheme given as letters; each letter 'A','B' is a rhyme class (all lines of the class are
perfect or family rhymes of each other); 'X' lines are fillers that must NOT rhyme with anything in the resolved sense
(no perfect/family relation) but MAY share a vowel (assonance) with another line -> the kernel's stray-assonance trap.
Labellers (case-insensitive scheme letters compared, then case checked separately):
  one-pass : line i gets the letter of the first earlier line it rhymes with in ANY way, else a new letter.
  two-pass : pass 1 uppercase letters for resolved (perfect/family) rhymes; pass 2 lowercase letters for assonance
             pairs among still-unlettered lines; rest X.
PREDICTION (before run): two-pass recovers the designed scheme (X for fillers) on 100% of the generated stanzas; one-pass
fails on >= 10% of XXAA stanzas and on none of AABB/ABAB/ABBA built without stray assonance; BREAK: a designed scheme
that deliberately uses an assonance-only pair (AB with 'a' assonance) is labelled lowercase by two-pass (so case, not
letter, carries the open/closed information) and one-pass cannot tell it from a perfect pair.
"""
import itertools
FAM = {"t": "T", "d": "T", "k": "K", "g": "K", "p": "P", "b": "P"}
POOL = [("ai", "t"), ("ai", "d"), ("ai", "n"), ("ai", "k"), ("ee", "t"), ("ee", "k"), ("ee", "n"), ("oh", "d"), ("oh", "g"), ("oh", "n"), ("oo", "p"), ("oo", "b")]
def rel(a, b):
    if a == b: return "perfect"
    if a[0] != b[0]: return "none"
    if a[1] in FAM and b[1] in FAM and FAM[a[1]] == FAM[b[1]]: return "family"
    return "assonance"
def one_pass(ws):
    out = []; nxt = iter("abcd")
    for i, w in enumerate(ws):
        for j in range(i):
            if rel(ws[j], w) != "none": out.append(out[j]); break
        else: out.append(next(nxt))
    return out
def two_pass(ws):
    out = [None] * len(ws); up = iter("ABCD"); lo = iter("abcd")
    for i in range(len(ws)):
        if out[i]: continue
        grp = [j for j in range(i, len(ws)) if out[j] is None and (j == i or rel(ws[i], ws[j]) in ("perfect", "family"))]
        if len(grp) > 1:
            L = next(up)
            for j in grp: out[j] = L
    for i in range(len(ws)):
        if out[i]: continue
        grp = [j for j in range(i, len(ws)) if out[j] is None and (j == i or rel(ws[i], ws[j]) == "assonance")]
        if len(grp) > 1:
            L = next(lo)
            for j in grp: out[j] = L
    return [o or "X" for o in out]
def norm(lbl):  # canonical shape: first-seen order, singles -> X
    m = {}; res = []
    for c in lbl:
        if c == "X" or lbl.count(c) == 1: res.append("X"); continue
        key = c.upper(); m.setdefault(key, "ABCD"[len(m)]); res.append(m[key])
    return "".join(res)
def resolved(lbl):  # scheme from UPPERCASE letters only (what two-pass calls resolved); lowercase and singles -> X
    m = {}; res = []
    for c in lbl:
        if c == "X" or not c.isupper(): res.append("X"); continue
        m.setdefault(c, "ABCD"[len(m)]); res.append(m[c])
    return "".join(res)
def stanzas(design):
    letters = sorted(set(design) - {"X"})
    for rhyme_words in itertools.product(POOL, repeat=sum(design.count(l) for l in letters)):
        pass
    # choose a rhyme class word-pair per letter (words within a class perfect/family rhymes), fillers any word
    classes = [(a, b) for a in POOL for b in POOL if rel(a, b) in ("perfect", "family")]
    for combo in itertools.product(classes, repeat=len(letters)):
        for fill in itertools.product(POOL, repeat=design.count("X")):
            ws = []; fi = iter(fill); used = {l: iter(c) for l, c in zip(letters, combo)}
            for ch in design: ws.append(next(fi) if ch == "X" else next(used[ch]))
            # fillers must not rhyme (perfect/family) with any other line; classes must be distinct classes (non-resolved to each other)
            good = True
            for i, j in itertools.combinations(range(4), 2):
                same = design[i] == design[j] != "X"
                r = rel(ws[i], ws[j])
                if same and r not in ("perfect", "family"): good = False
                if not same and r in ("perfect", "family"): good = False
            if good: yield ws
rows = {}
for design in ("XXAA", "AABB", "ABAB", "ABBA", "AAXX"):
    n = ok1 = ok2 = ok2r = 0
    for ws in stanzas(design):
        n += 1
        ok1 += norm(one_pass(ws)) == design
        ok2 += norm(two_pass(ws)) == design
        ok2r += resolved(two_pass(ws)) == design
    rows[design] = (n, ok1, ok2r, ok2)
    print(f"{design}: stanzas={n} one-pass correct={ok1} ({ok1/n:.1%})  two-pass resolved-scheme correct={ok2r} ({ok2r/n:.1%})  two-pass incl. lowercase fillers as rhymes={ok2} ({ok2/n:.1%})")
# stray assonance subsets: designs where NO filler/class pair shares a vowel
def has_stray(ws, design):
    return any(rel(ws[i], ws[j]) == "assonance" for i, j in itertools.combinations(range(4), 2))
clean1 = clean_n = 0
for d in ("AABB", "ABAB", "ABBA"):
    for ws in stanzas(d):
        if not has_stray(ws, d): clean_n += 1; clean1 += norm(one_pass(ws)) == d
# BREAK: assonance-only intended pair (A perfect + B assonance-only)
pair = [("ai", "t"), ("oh", "n"), ("ai", "t"), ("oh", "d")]   # lines 2,4 share vowel only? oh-n vs oh-d -> assonance
tp, op = two_pass(pair), one_pass(pair)
print("assonance-pair stanza two-pass:", "".join(tp), " one-pass:", "".join(op))
xx = rows["XXAA"]
# filler-filler assonance: in XXAA stanzas where the two X lines share a vowel, two-pass lowercases them (open rhyme) by design
fill_ass = sum(1 for ws in stanzas("XXAA") if rel(ws[0], ws[1]) == "assonance")
two_res = sum(r[2] for r in rows.values()); tot = sum(r[0] for r in rows.values())
ok = (two_res == tot and xx[1] < xx[0] * 0.9 and clean1 == clean_n and tp[1] == tp[3] == "a" and tp[0] == "A")
print("RESULT: %s two-pass resolved scheme matches the design in %d of %d stanzas (lowercase marks %d XXAA filler pairs that share a vowel); one-pass is wrong on %d of %d XXAA stanzas and %d of %d stanzas with no stray assonance; assonance-only pair comes out %s"
      % ("PASS" if ok else "FAIL", two_res, tot, fill_ass, xx[0] - xx[1], xx[0], clean_n - clean1, clean_n, "".join(tp)))
