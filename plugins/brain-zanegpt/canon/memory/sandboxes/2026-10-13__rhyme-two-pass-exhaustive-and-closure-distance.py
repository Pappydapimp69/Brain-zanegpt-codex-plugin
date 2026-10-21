# Prediction (before run): over ALL 6^4=1296 four-line stanzas from 6 end-sounds (vowel a/i x coda t/n/k):
# (1) two-pass uppercase letters reproduce the perfect-rhyme scheme in 1296/1296 (by construction of pass 1);
# (2) one-pass any-match (assonance counts) mislabels the perfect-rhyme scheme in >=200 stanzas;
# (3) every line gets exactly one letter in both approaches; (4) closure distance (lines since same-letter partner):
# AABB max 1, ABBA max 3, AAAA max 1 -- and the two-pass scheme keeps AABB/ABBA distinguishable where one-pass merges them.
from itertools import product
SOUNDS = [(v, c) for v in "ai" for c in "tnk"]
def pattern(keys):
    seen = {}; out = []
    for k in keys:
        seen.setdefault(k, len(seen)); out.append(seen[k])
    return tuple(out)
def one_pass(st):  # any shared vowel counts as a rhyme -> letter keyed by vowel only
    return pattern([v for v, c in st])
def two_pass(st):
    perfect = pattern([s for s in st])             # pass 1: resolved rhymes (vowel+coda) -> uppercase
    counts = {}
    for s in st: counts[s] = counts.get(s, 0) + 1
    lower = {}
    letters = []
    for i, s in enumerate(st):
        if counts[s] > 1: letters.append(("U", perfect[i]))
        else: letters.append(None)
    # pass 2: assonance pairs among still-unlettered lines -> lowercase
    free = [i for i, l in enumerate(letters) if l is None]
    byv = {}
    for i in free: byv.setdefault(st[i][0], []).append(i)
    n = 100
    for v, idx in byv.items():
        if len(idx) > 1:
            for i in idx: letters[i] = ("l", n)
            n += 1
    for i in range(4):
        if letters[i] is None: letters[i] = ("x", i)
    return letters
def uppercase_pattern(letters):
    return pattern([l[1] if l[0] == "U" else ("-", i) for i, l in enumerate(letters)])
def closure(p):
    last = {}; ds = []
    for i, k in enumerate(p):
        if k in last: ds.append(i - last[k])
        last[k] = i
    return max(ds) if ds else 0
total = bad1 = bad2 = nolabel = merged = 0
for st in product(SOUNDS, repeat=4):
    total += 1
    truth = pattern(list(st))
    l1 = one_pass(st); l2 = two_pass(st)
    if len(l1) != 4 or len(l2) != 4: nolabel += 1
    if l1 != truth: bad1 += 1
    # two-pass: uppercase letters equal truth wherever truth has a repeat
    up = uppercase_pattern(l2)
    exp = pattern([s if truth.count(truth[i]) > 1 else ("-", i) for i, s in enumerate(st)])
    if up != exp: bad2 += 1
# distinguishability: AABB vs ABBA built with distinct codas but same vowel (stray assonance everywhere)
A, B = ("a", "t"), ("a", "n")
aabb = (A, A, B, B); abba = (A, B, B, A); aaaa = (A, A, A, A)
merged = one_pass(aabb) == one_pass(abba)
sep2 = uppercase_pattern(two_pass(aabb)) != uppercase_pattern(two_pass(abba))
cd = (closure(pattern(list(aabb))), closure(pattern(list(abba))), closure(pattern(list(aaaa))))
ok = bad2 == 0 and bad1 >= 200 and nolabel == 0 and cd == (1, 3, 1) and merged and sep2
print("RESULT:", "PASS" if ok else "FAIL",
      f"stanzas={total} onepass_wrong={bad1} twopass_wrong={bad2} unlabeled={nolabel} "
      f"closure(AABB,ABBA,AAAA)={cd} onepass_merges_AABB_ABBA={merged} twopass_separates={sep2}")
