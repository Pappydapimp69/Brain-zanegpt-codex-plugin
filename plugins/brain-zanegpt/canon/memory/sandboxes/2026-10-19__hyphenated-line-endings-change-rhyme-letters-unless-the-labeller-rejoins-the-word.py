"""Sandbox: do hyphenated line endings (Suno pacing trick) change a two-pass rhyme labeller's output?
Deterministic, stdlib only.
Prediction (written before first run): with a naive last-token lookup the hyphenated stanza A
(to-night / beau-ti-ful / light / wonder-ful) keeps ABAB only by luck, stanza B (beau-ti-ful / pull)
gains a FALSE perfect rhyme (UH L fragment 'ful' vs 'pull'), and a rejoining labeller gives
identical letters hyphenated vs plain in every stanza. Expect >=1 naive mismatch, 0 rejoin mismatches.
"""
P = {  # word: (vowel, coda)
    "night": ("AY", "T"), "light": ("AY", "T"), "tonight": ("AY", "T"), "bright": ("AY", "T"),
    "beautiful": ("AH", "L"), "wonderful": ("AH", "L"), "pull": ("UH", "L"), "full": ("UH", "L"), "ful": ("UH", "L"),
    "fall": ("AO", "L"), "tiful": None, "day": ("EY", ""), "today": ("EY", ""), "way": ("EY", ""),
    "sound": ("AW", "ND"), "found": ("AW", "ND"), "resound": ("AW", "ND"), "ground": ("AW", "ND"),
}
STOPS = {"K", "D", "T", "P", "B", "G"}

def end_naive(line):   # last whitespace token, then last hyphen fragment (what a split-on-hyphen tokenizer sees)
    return line.split()[-1].split("-")[-1].lower()
def end_rejoin(line):  # last whitespace token with hyphens removed
    return line.split()[-1].replace("-", "").lower()

def rel(a, b):
    pa, pb = P.get(a), P.get(b)
    if not pa or not pb or pa[0] != pb[0]: return "none"
    if pa[1] == pb[1]: return "perfect"
    return "family" if pa[1][-1:] in STOPS and pb[1][-1:] in STOPS else "assonance"

def two_pass(words):
    res = [None] * len(words); n = 0
    for i, w in enumerate(words):
        for j in range(i):
            if rel(words[j], w) in ("perfect", "family"):
                if res[j] is None: res[j] = chr(65 + n); n += 1
                res[i] = res[j]; break
    m = 0
    for i, w in enumerate(words):
        if res[i] is None:
            for j in range(len(words)):
                if j != i and res[j] is None and rel(words[j], w) == "assonance":
                    res[j] = chr(97 + m); res[i] = res[j]; m += 1; break
    return "".join(r or "x" for r in res)

def scheme(lines, ext): return two_pass([ext(l) for l in lines])

stanzas = {
 "A end-words hyphenated": (["I dream of you tonight", "all things feel beautiful", "stars burn in the light", "you are wonderful"],
                           ["I dream of you to-night", "all things feel beau-ti-ful", "stars burn in the light", "you are wonder-ful"]),
 "B false-rhyme bait": (["all things feel beautiful", "no hand to pull", "stars burn in the light", "I am whole and full"],
                       ["all things feel beau-ti-ful", "no hand to pull", "stars burn in the light", "I am whole and full"]),
 "C re-sound": (["we hear it resound", "it was lost then found", "far away today", "I know the way"],
               ["we hear it re-sound", "it was lost then found", "far a-way to-day", "I know the way"]),
 "D BREAK no hyphen at line end": (["stars burn in the light", "I walk alone", "all through the night", "I am on my own"],
                                   ["stars burn in the light", "I walk alone", "all through the night", "I am on my own"]),
}
nm = rm = 0
for k, (plain, hyph) in stanzas.items():
    p = scheme(plain, end_rejoin); n = scheme(hyph, end_naive); r = scheme(hyph, end_rejoin)
    nm += n != p; rm += r != p
    print(f"{k}: plain {p} naive-hyphenated {n} rejoin-hyphenated {r}")
ok = nm >= 1 and rm == 0
print(("RESULT: PASS" if ok else "RESULT: FAIL"), f"naive mismatches {nm}/4, rejoin mismatches {rm}/4")
