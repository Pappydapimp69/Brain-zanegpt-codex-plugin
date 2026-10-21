"""Gap/new: two-pass lettering (resolved rhymes claim UPPERCASE letters first, assonance gets
lowercase among the rest) + rhyme-scheme shape (AABB stable, ABAB flowing, ABBA wistful, XXAA
open then resolved) + companion lesson 'shorten a rushed line from the front so the rhyme WORD
survives' (keep-last-5 kept 4/4 shapes, with one-word rhymes and a spelling key).
Question: when the rhyme is MOSAIC (spans two words: lose it / choose it, know it / poet,
hold her / older), how short can a front-cut go before the shape read from uppercase letters
changes? Phonetic judge on a hand fixture (ARPAbet-style, stress digits): the rhyme key runs
from the LAST STRESSED vowel in the kept tail to the end; reduced vowels AH0/IH0 -> '@'.
A resolved rhyme needs both keys to start on a stressed vowel and match; a tail with no
stressed vowel can only take part in assonance (same first vowel). Deterministic, stdlib.

PREDICTION (written before first run): keep-last-1 (just the final word) preserves the
uppercase shape only in the stanza with no mosaic rhyme (1/5); keep-last-2 preserves 5/5;
at keep-last-1 at least 2 stanzas move to a more open shape (resolved pair demoted to
lowercase or x). Break/control: single-word feminine rhymes (playing/staying) survive at k=1."""
PH = {"lose":"L UW1 Z","it":"IH0 T","choose":"CH UW1 Z","playing":"P L EY1 IH0 NG","staying":"S T EY1 IH0 NG",
      "show":"SH OW1","fire":"F AY1 ER0","poet":"P OW1 AH0 T","higher":"HH AY1 ER0","hold":"HH OW1 L D",
      "her":"ER0","older":"OW1 L D ER0","ocean":"OW1 SH AH0 N","emotion":"IH0 M OW1 SH AH0 N",
      "away":"AH0 W EY1","know":"N OW1","today":"T AH0 D EY1","road":"R OW1 D","window":"W IH1 N D OW0",
      "stay":"S T EY1","really":"R IH1 L IY0","the":"DH AH0","you":"Y UW1","a":"AH0","fade":"F EY1 D",
      "carry":"K EH1 R IY0","me":"M IY0","move":"M UW1 V","beside":"B IH0 S AY1 D"}
VOW = ("AA","AE","AH","AO","AW","AY","EH","ER","EY","IH","IY","OW","OY","UH","UW")
def key(line, k):
    ws = line.lower().split()[-k:]
    ph = []
    for w in ws: ph += PH[w].split() if w in PH else ["?" + w]
    idx = [i for i, p in enumerate(ph) if p[:-1] in VOW and p[-1] == "1"]
    stressed = bool(idx)
    if not stressed:
        idx = [i for i, p in enumerate(ph) if p[:-1] in VOW]
        if not idx: return (False, ())
    tail = ph[idx[-1]:]
    if any(p.startswith("?") for p in tail): raise KeyError(f"fixture missing for tail of {ws}")
    norm = tuple("@" if p in ("AH0", "IH0") else (p[:-1] if p[-1].isdigit() else p) for p in tail)
    return (stressed, norm)
def two_pass(keys):
    let = [None] * len(keys); up = iter("ABCD"); lo = iter("abcd")
    res = lambda a, b: a[0] and b[0] and a[1] == b[1]
    asn = lambda a, b: bool(a[1]) and bool(b[1]) and a[1][0] == b[1][0]
    for test, it in ((res, up), (asn, lo)):
        for i in range(len(keys)):
            if let[i] is None:
                g = [j for j in range(i + 1, len(keys)) if let[j] is None and test(keys[i], keys[j])]
                if g:
                    c = next(it); let[i] = c
                    for j in g: let[j] = c
    return [c or "x" for c in let]
def shape(lets):
    """uppercase-only shape, relabelled in order: AABB/ABAB/ABBA/xxAA..."""
    m = {}; out = ""
    for c in lets:
        if c.isupper():
            m.setdefault(c, "ABCD"[len(m)]); out += m[c]
        else: out += "x"
    return out
ST = {
 "M1 AABB mosaic+fem": ["I held the only copy and I swore I'd never lose it",
                        "you told me it was mine to keep and mine alone to choose it",
                        "the night was cold and endless and the radio was playing",
                        "a song about the river and the reasons for not staying"],
 "M2 ABAB mosaic":     ["you kept the kind of sadness that you'd never really show it",
                        "and all the things you burned that winter fed a little fire",
                        "you scribbled on the napkins like a broke and hungry poet",
                        "and every word you crossed out only climbed a little higher"],
 "M3 AABB mosaic":     ["I never learned the proper way to hold her",
                        "and now the photographs are getting older",
                        "we drove out to the coast to see the ocean",
                        "and stood there in the wind without emotion"],
 "M4 ABBA mosaic":     ["I watched the morning trains go by and fade away",
                        "the kind of love that hurts before you know it",
                        "is not the kind you ever learn to show it",
                        "so I just let the evening carry me today"],
 "M5 XXAA one-word":   ["my father worked the night shift down beside the road",
                        "he came home tired and quiet and he sat beside the window",
                        "he never told us what it cost him just to stay",
                        "he only asked that we would never move away"],
}
KS = (1, 2, 3, 5)
kept = {k: 0 for k in KS}; opened = 0; fem_ok = True
for name, lines in ST.items():
    full = shape(two_pass([key(l, 6) for l in lines]))
    row = []
    for k in KS:
        lets = two_pass([key(l, k) for l in lines]); s = shape(lets)
        kept[k] += s == full; row.append(f"k={k}: {''.join(lets)} -> {s}")
        if k == 1 and s != full and s.count("x") > full.count("x"): opened += 1
        if k == 1 and name.startswith("M1"): fem_ok = lets[2] == lets[3] and lets[2].isupper()
    print(f"{name:20s} full {full}  " + "  ".join(row) + f"   words/line full {sum(len(l.split()) for l in lines)/4:.1f}")
n = len(ST)
ok = kept[1] == 1 and kept[2] == n and opened >= 2 and fem_ok
print(f"RESULT: {'PASS' if ok else 'FAIL'} uppercase shape kept: k=1 {kept[1]}/{n}, k=2 {kept[2]}/{n}, k=3 {kept[3]}/{n}, "
      f"k=5 {kept[5]}/{n}; stanzas opened (resolved pair lost) at k=1: {opened}; one-word feminine pair survives k=1: {fem_ok}")
