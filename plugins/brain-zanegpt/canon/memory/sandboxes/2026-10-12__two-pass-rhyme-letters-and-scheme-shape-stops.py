# Deterministic sandbox: one-pass vs two-pass rhyme lettering, and stopping points per scheme shape.
# Prediction (before run): one-pass labeler mislabels the XXAA stanza (reads XAAA) while the two-pass labeler returns XXAA with
# uppercase on the resolved pair; both agree on AABB/ABAB/ABBA when no stray assonance exists; stopping points (adjacent
# resolved line pairs) AABB=2, ABAB=0, ABBA=1 (middle pair only), XXAA=1; a stanza with two distinct assonance-only pairs and no
# resolved rhymes labels all lowercase in two-pass (open) but looks fully rhymed in one-pass.
# Tiny hand lexicon: word -> (nucleus, coda). Perfect: same nucleus+coda. Family: same nucleus, coda in same class.
LEX = {"night": ("ai", "t"), "light": ("ai", "t"), "mine": ("ai", "n"), "time": ("ai", "m"), "line": ("ai", "n"),
       "stone": ("o", "n"), "home": ("o", "m"), "road": ("o", "d"), "load": ("o", "d"), "cold": ("o", "ld"),
       "day": ("e", ""), "stay": ("e", ""), "rain": ("e", "n"), "grain": ("e", "n"), "sea": ("i", ""), "free": ("i", ""),
       "gone": ("o", "n"), "town": ("au", "n"), "down": ("au", "n"), "heart": ("a", "t"), "apart": ("a", "t"), "face": ("e", "s")}
NASAL = {"n", "m", "ng"}; STOP = {"t", "d", "k", "p", "b", "g"}
def cls(c): return "nas" if c in NASAL else "stop" if c in STOP else c
def rel(w1, w2):
    n1, c1 = LEX[w1]; n2, c2 = LEX[w2]
    if w1 == w2: return None
    if (n1, c1) == (n2, c2): return "perfect"
    if n1 == n2 and cls(c1) == cls(c2) and c1 and c2: return "family"
    if n1 == n2: return "assonance"
    return None
def one_pass(words):
    letters = [None] * len(words); nxt = 0
    for i in range(len(words)):
        if letters[i] is None:
            hit = [j for j in range(i + 1, len(words)) if letters[j] is None and rel(words[i], words[j])]
            if hit:
                letters[i] = chr(65 + nxt); 
                for j in hit: letters[j] = chr(65 + nxt)
                nxt += 1
    return "".join(l if l else "X" for l in letters)
def two_pass(words):
    letters = [None] * len(words); nxt = 0
    for kinds, upper in ((("perfect", "family"), True), (("assonance",), False)):
        for i in range(len(words)):
            if letters[i] is None:
                hit = [j for j in range(i + 1, len(words)) if letters[j] is None and rel(words[i], words[j]) in kinds]
                if hit:
                    ch = chr(65 + nxt) if upper else chr(97 + nxt)
                    letters[i] = ch
                    for j in hit: letters[j] = ch
                    nxt += 1
    return "".join(l if l else "X" for l in letters)
def stops(s): return sum(1 for i in range(len(s) - 1) if s[i].isupper() and s[i] != "X" and s[i] == s[i + 1])
S = {"AABB": ["night", "light", "road", "load"], "ABAB": ["night", "road", "light", "load"], "ABBA": ["night", "road", "load", "light"],
     "XXAA": ["face", "town", "road", "load"],
     "stray": ["town", "night", "mine", "line"],       # night is assonance-only with mine/line, which are a perfect pair
     "assonance_only": ["night", "road", "mine", "home"]}  # night/mine and road/home share a vowel, not a coda class
res = {}
for k, w in S.items():
    o, t = one_pass(w), two_pass(w); res[k] = (o, t); print(f"{k:15s} one-pass={o} two-pass={t} stops={stops(t)}")
ok = (res["XXAA"][1] == "XXAA" and res["AABB"][1] == "AABB" and res["ABAB"][1] == "ABAB" and res["ABBA"][1] == "ABBA"
      and stops("AABB") == 2 and stops("ABAB") == 0 and stops("ABBA") == 1 and stops("XXAA") == 1
      and res["stray"][0] == "XAAA" and res["stray"][1] == "XXAA"
      and res["assonance_only"][1].islower() and res["assonance_only"][0].isupper())
print("RESULT: %s two-pass %s XXAA=%s stray one-pass=%s two-pass=%s assonance-only one-pass=%s two-pass=%s stops AABB/ABAB/ABBA/XXAA=%d/%d/%d/%d" % (
    "PASS" if ok else "FAIL", "labels", res["XXAA"][1], res["stray"][0], res["stray"][1], res["assonance_only"][0], res["assonance_only"][1],
    stops("AABB"), stops("ABAB"), stops("ABBA"), stops("XXAA")))
