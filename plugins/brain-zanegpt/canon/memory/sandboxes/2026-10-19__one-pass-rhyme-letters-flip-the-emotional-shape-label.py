# Exhaustive 4-line stanzas over 6 end words; compare the shape label (and the emotion it implies) from
# one-pass letters (any shared vowel rhymes) with two-pass letters (perfect rhymes get the main letters).
import itertools
W = {"cat": ("a","t"), "hat": ("a","t"), "cap": ("a","p"), "bed": ("e","d"), "red": ("e","d"), "bell": ("e","l")}
names = list(W)
def norm(letters):
    m = {}; return "".join(m.setdefault(c, "ABCD"[len(m)]) for c in letters)
def one_pass(st):
    # a line joins the first earlier line sharing its vowel (any rhyme type counts)
    g = []; out = []
    for w in st:
        for i, x in enumerate(g):
            if W[x][0] == W[w][0]: out.append(i); break
        else: g.append(w); out.append(len(g)-1)
    return norm(out)
def two_pass(st):
    # pass 1: perfect rhymes (same vowel+coda) share a letter; lines with no perfect partner are unlabelled X
    out = []
    for i, w in enumerate(st):
        out.append(W[w] if sum(W[v] == W[w] for v in st) > 1 else ("X", i))
    return norm(out)
def shape_to_emotion(s):
    # kernel: AABB stable stopping, ABAB stable flowing, ABBA open/wistful, XXAA-like open, else unrhymed
    if s == "AABB": return "stable"
    if s == "ABAB": return "stable"
    if s == "ABBA": return "open"
    if s == "ABCC": return "open"      # unrhymed first couplet, resolved end (XXAA)
    return "other"
tot = diff_shape = diff_emo = 0; ex = None
for st in itertools.product(names, repeat=4):
    a, b = one_pass(st), two_pass(st); tot += 1
    if a != b:
        diff_shape += 1
        if shape_to_emotion(a) != shape_to_emotion(b):
            diff_emo += 1; ex = ex or (st, a, b)
print("stanzas", tot, "shape label differs", diff_shape, "emotion class differs", diff_emo, "example", ex)
# break case: with only perfect-rhyme words in the vocabulary the two methods must agree
pure = [s for s in itertools.product(["cat","hat","bed","red"], repeat=4)]
agree = sum(one_pass(s) == two_pass(s) for s in pure)
# not exactly: one-pass treats cat/hat (perfect) and bed/red alike, but singletons are lettered; count anyway
print("perfect-only vocab agree", agree, "of", len(pure))
ok = diff_shape / tot >= 0.5 and diff_emo / tot >= 0.3
print(f"RESULT: {'PASS' if ok else 'FAIL'} one-pass vs two-pass shape differs {diff_shape}/{tot} ({100*diff_shape/tot:.1f}%), emotion class differs {diff_emo}/{tot} ({100*diff_emo/tot:.1f}%); perfect-only vocab agree {agree}/{len(pure)}")
