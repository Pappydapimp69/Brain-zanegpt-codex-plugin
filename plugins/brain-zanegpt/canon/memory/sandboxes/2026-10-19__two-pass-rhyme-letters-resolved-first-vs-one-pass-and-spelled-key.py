"""Sandbox: two-pass rhyme-letter assignment vs one-pass vs spelling-keyed labeller.
Deterministic, stdlib only. Hand-coded phoneme table (vowel, coda) -- no dictionary, no RNG.
Prediction (written before first run): on the fixture sky/tone/mine/line one-pass reports ABAA
and two-pass reports xxAA-shape (lines 3,4 uppercase, 1,2 unlettered); on truck/mud/blood/flood
merge-in gives AAAA, distinct-letter gives BAAA, spelling-keyed gives AABB; exhaustive 4-line
stanzas from a 10-word pool: one-pass lets an assonance-only line share a letter with a
resolved pair in a clear majority-minus-zero (>0) of stanzas where two-pass never does.
"""
import itertools

W = {  # word: (vowel, coda, spelled_vowel_group)
    "sky": ("AY", "", "y"), "tone": ("OW", "N", "o"), "mine": ("AY", "N", "i"), "line": ("AY", "N", "i"),
    "truck": ("AH", "K", "u"), "mud": ("AH", "D", "u"), "blood": ("AH", "D", "oo"), "flood": ("AH", "D", "oo"),
    "cat": ("AE", "T", "a"), "bad": ("AE", "D", "a"), "hat": ("AE", "T", "a"), "time": ("AY", "M", "i"),
}
STOPS = {"K", "D", "T", "P", "B", "G"}

def rel(a, b):
    va, ca, _ = W[a]; vb, cb, _ = W[b]
    if va != vb: return "none"
    if ca == cb: return "perfect"
    if ca in STOPS and cb in STOPS: return "family"
    return "assonance"

def one_pass(words):  # any rhyme type counts, merge
    letters, out = [], []
    for i, w in enumerate(words):
        hit = next((out[j] for j in range(i) if rel(words[j], w) != "none"), None)
        out.append(hit or chr(65 + len(set(out))))
    return "".join(out)

def two_pass(words, distinct_family=False):
    res = [None] * len(words); n = 0
    strong = ("perfect",) if distinct_family else ("perfect", "family")
    for i, w in enumerate(words):
        for j in range(i):
            if rel(words[j], w) in strong:
                if res[j] is None: res[j] = chr(65 + n); n += 1
                res[i] = res[j]; break
    if distinct_family:  # family word gets its own uppercase letter (E1's rule)
        for i, w in enumerate(words):
            if res[i] is None and any(rel(words[j], w) == "family" for j in range(len(words)) if j != i):
                res[i] = chr(65 + n); n += 1
    m = 0
    for i, w in enumerate(words):
        if res[i] is None:
            for j in range(len(words)):
                if j != i and res[j] is None and rel(words[j], w) == "assonance":
                    res[j] = res[j] or chr(97 + m); res[i] = res[j]; m += 1; break
    return "".join(r or "x" for r in res)

def spelled(words):  # E3: key on spelled vowel group + coda family
    out, keys = [], {}
    for w in words:
        k = (W[w][2], "stop" if W[w][1] in STOPS else W[w][1])
        keys.setdefault(k, chr(65 + len(keys))); out.append(keys[k])
    return "".join(out)

ok = True
def check(name, got, want):
    global ok
    good = got == want; ok &= good
    print(f"{name}: got {got} want {want} {'ok' if good else 'MISMATCH'}")

fx = ["sky", "tone", "mine", "line"]
check("S1 one-pass stray assonance", one_pass(fx), "ABAA")
check("S1 two-pass", two_pass(fx), "xxAA")
tm = ["truck", "mud", "blood", "flood"]
check("S2 merge-in(one-pass)", one_pass(tm), "AAAA")
check("S2 two-pass family uppercase", two_pass(tm), "AAAA")
check("S2 distinct-family (E1 rule)", two_pass(tm, True), "BAAA")
check("S2 spelled-key (E3 builder-like)", spelled(tm), "AABB")

# S3 exhaustive: stanzas of 4 from pool; stray = a line with only assonance ties lettered same as a resolved pair
pool = ["sky", "tone", "mine", "line", "cat", "bad", "hat", "time"]
bad1 = bad2 = tot = 0
for st in itertools.product(pool, repeat=4):
    tot += 1
    a, b = one_pass(list(st)), two_pass(list(st))
    for i in range(4):
        for j in range(i):
            r = rel(st[i], st[j])
            if r == "assonance":
                resolved_i = any(rel(st[i], st[k]) in ("perfect", "family") for k in range(4) if k != i)
                resolved_j = any(rel(st[j], st[k]) in ("perfect", "family") for k in range(4) if k != j)
                if resolved_i != resolved_j:  # one resolved, one not: must NOT share a symbol
                    if a[i] == a[j]: bad1 += 1; break
                    if b[i].upper() == b[j].upper() and b[i] != "x" and b[i] == b[j]: bad2 += 1; break
        else: continue
        break
print(f"S3 exhaustive {tot} stanzas: one-pass stray-shares {bad1}, two-pass {bad2}")
ok &= bad1 > 0 and bad2 == 0
# S4 BREAK: all-assonance stanza has no resolved rhyme: two-pass must still report a scheme
check("S4 BREAK interleaved family pair + assonance pair (cat sky bad time)", two_pass(["cat", "sky", "bad", "time"]), "AaAa")
print(("RESULT: PASS" if ok else "RESULT: FAIL"), f"one-pass stray {bad1}/{tot}, two-pass {bad2}/{tot}")
