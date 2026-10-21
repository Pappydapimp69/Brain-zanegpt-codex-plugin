"""Kernel: crowded syllables make Suno rush a line; fix = shorter lines (4-6 words).
Applied the way a writer usually does it: SPLIT each long line at its midpoint into two
short lines (instead of cutting words). Question: what does the split do to the stanza's
rhyme letters when lettered by the two-pass method (resolved rhymes claim UPPERCASE
letters first, assonance gets lowercase among still-unlettered lines) with a phonetic
judge (companion lesson: judge, scope and pass order are separate stages)?
Split rule is mechanical (after word ceil(n/2)), so the exposed mid-line word is NOT chosen.
Phonetic fixture: hand-written (stressed vowel, tail after it) for every line-final word.
Deterministic, stdlib only.

PREDICTION (written before first run): over 6 natural stanzas, two-pass keeps the
uppercase pattern of the original line ends in 6/6; at least 2/6 split stanzas gain a
letter on an exposed mid-line word; single-pass lettering on the split stanzas changes
the original end-line pattern in at least 2/6; words/line fall from ~11 to ~5.5.
The engineered internal-rhyme stanza (S7) gets an exposed word promoted to UPPERCASE."""
import math

PH = {  # word -> (stressed vowel, tail after the vowel); only line-final words need it
 "rain":("EY","N"),"train":("EY","N"),"night":("AY","T"),"light":("AY","T"),
 "down":("AW","N"),"kept":("EH","PT"),"changes":("EY","NJAHZ"),"when":("EH","N"),
 "tin":("IH","N"),"gold":("OW","LD"),"in":("IH","N"),"cold":("OW","LD"),
 "you":("UW",""),"the":("AH",""),"i":("AY",""),"empty":("EH","MPTIY"),
 "sea":("IY",""),"door":("AO","R"),"floor":("AO","R"),"me":("IY",""),
 "road":("OW","D"),"window":("IH","NDOW"),"stay":("EY",""),"away":("EY",""),
 "ground":("AW","ND"),"sound":("AW","ND"),"sky":("AY",""),"by":("AY",""),
 "fire":("AY","ER"),"stone":("OW","N"),"higher":("AY","ER"),"alone":("OW","N"),
 "day":("EY",""),"sun":("AH","N"),"done":("AH","N"),"today":("EY",""),
 "something":("AH","MTHIHNG"),"stumbled":("AH","MBAHLD"),"shelf":("EH","LF"),
 "hard":("AA","RD"),"night_":("AY","T"),"mill":("IH","L"),"quiet":("AY","AHT"),
 "it":("IH","T"),"would":("UH","D"),"evening":("IY","VNIHNG"),"hear":("IH","R"),
 "blinking":("IH","NGKIHNG"),"doorway":("AO","RWEY"),"we":("IY",""),"itself":("EH","LF"),
 "getting":("EH","TIHNG"),"year":("IH","R"),"noticed":("OW","TAHST"),"there":("EH","R"),
 "shift":("IH","FT"),"so":("OW",""),"plane":("EY","N"),"just":("AH","ST"),"sparks":("AA","RKS"),
 "at":("AE","T"),"fountain":("AW","NTAHN"),"till":("IH","L"),"for":("AO","R"),"what":("AH","T"),
 "and":("AE","ND"),"wine":("AY","N"),"up":("AH","P"),"little":("IH","TAHL"),"on":("AA","N"),
 "came":("EY","M"),"tired":("AY","ERD"),"home":("OW","M"),"never":("EH","VER"),
 "told":("OW","LD"),"wrote":("OW","T"),"while":("AY","L"),"liked":("AY","KT"),
 "talking":("AO","KIHNG"),"like":("AY","K"),"a":("AH",""),"way":("EY",""),"asked":("AE","SKT"),"was":("AH","Z"),"single":("IH","NGGAHL"),
}
FAMILY = [set("PTK"), set("BDG"), set("MN"), {"F","S","TH","SH"}, {"V","Z","DH"}]
def resolved(a, b):
    (va, ta), (vb, tb) = PH[a], PH[b]
    if va != vb: return False
    if ta == tb: return True
    if len(ta) == 1 and len(tb) == 1:
        return any(ta in f and tb in f for f in FAMILY)
    return False
def assonant(a, b): return PH[a][0] == PH[b][0]

def two_pass(ends):
    let = [None] * len(ends); up = iter("ABCDEFGH"); lo = iter("abcdefgh")
    for i in range(len(ends)):
        if let[i] is None:
            grp = [j for j in range(i + 1, len(ends)) if let[j] is None and resolved(ends[i], ends[j])]
            if grp:
                c = next(up); let[i] = c
                for j in grp: let[j] = c
    for i in range(len(ends)):
        if let[i] is None:
            grp = [j for j in range(i + 1, len(ends)) if let[j] is None and assonant(ends[i], ends[j])]
            if grp:
                c = next(lo); let[i] = c
                for j in grp: let[j] = c
    return [c or "x" for c in let]
def single_pass(ends):
    let = [None] * len(ends); nxt = iter("ABCDEFGH")
    for i, w in enumerate(ends):
        for j in range(i):
            if resolved(ends[j], w) or assonant(ends[j], w):
                let[i] = let[j]; break
        if let[i] is None: let[i] = next(nxt)
    # unshared letters are unrhymed
    return [c if let.count(c) > 1 else "x" for c in let]
def canon(lets):
    """relabel letters in order of appearance, preserving case, x stays x"""
    m = {}; out = []
    for c in lets:
        if c == "x": out.append("x"); continue
        if c not in m:
            n = sum(1 for k in m if k.isupper() == c.isupper())
            m[c] = ("ABCDEFGH" if c.isupper() else "abcdefgh")[n]
        out.append(m[c])
    return "".join(out)

STANZAS = {
 "S1 AABB": ["we drove the empty highway down past the farms in rain",
             "and every mile that we kept counting felt like a train",
             "you said that nothing ever changes in the dead of night",
             "but your hand was shaking when you reached to dim the light"],
 "S2 ABAB": ["I kept the letters that you wrote me in a box of tin",
             "the paper yellowed slowly while the summer turned to gold",
             "I never read them but I liked the way they kept me in",
             "and now the box is empty and the house is getting cold"],
 "S3 ABBA": ["the radio was playing something softer than the sea",
             "we danced across the kitchen till we stumbled at the door",
             "the glasses rattled on the shelf and wine ran on the floor",
             "and you were laughing so hard you could barely look at me"],
 "S4 XXAA": ["my father worked the night shift at the mill beside the road",
             "he came home tired and quiet and he sat beside the window",
             "he never told us what it cost him just to stay",
             "he only asked that we would never move away"],
 "S5 AABB": ["the snow came down all evening and it covered up the ground",
             "the street was so still you could hear the softest sound",
             "a single plane went blinking slowly through the empty sky",
             "and I stood in the doorway just to watch it passing by"],
 "S6 ABAB": ["we built a little shelter and we sat around the fire",
             "the river kept on talking to itself against the stone",
             "the sparks went up like questions getting smaller climbing higher",
             "and for the first time in a year I did not feel alone"],
}
BREAK = {"S7 AABB internal": ["I took the early train today and walked the whole way",
             "the city never noticed I had come so far away",
             "I sat beside the fountain in the middle of the sun",
             "and waited there for hours till the waiting was all done"]}
def words(l): return l.lower().split()
def split(lines):
    out = []
    for l in lines:
        w = words(l); k = math.ceil(len(w) / 2)
        out += [" ".join(w[:k]), " ".join(w[k:])]
    return out
def run(name, lines):
    ends = [words(l)[-1] for l in lines]
    sp = split(lines); sends = [words(l)[-1] for l in sp]
    o2 = canon(two_pass(ends)); s2 = canon(two_pass(sends))
    s1 = canon(single_pass(sends)); o1 = canon(single_pass(ends))
    keep2 = canon(list(s2[1::2])) == o2
    keep1 = canon(list(s1[1::2])) == o1
    exposed = [c for c in s2[0::2] if c != "x"]
    up_exp = sum(c.isupper() for c in exposed)
    wpl0 = sum(len(words(l)) for l in lines) / len(lines); wpl1 = sum(len(words(l)) for l in sp) / len(sp)
    print(f"{name:18s} orig {o2}  split2pass {s2}  split1pass {s1}  exposed={[w for w in sends[0::2]]} "
          f"lettered={len(exposed)} (UPPER {up_exp})  ends-kept 2pass={keep2} 1pass={keep1}  w/line {wpl0:.1f}->{wpl1:.1f}")
    return dict(keep2=keep2, keep1=keep1, lettered=len(exposed) > 0, up=up_exp, w0=wpl0, w1=wpl1)

R = {n: run(n, l) for n, l in STANZAS.items()}
B = {n: run(n, l) for n, l in BREAK.items()}
n = len(R)
k2 = sum(r["keep2"] for r in R.values()); k1 = sum(r["keep1"] for r in R.values())
lett = sum(r["lettered"] for r in R.values()); upn = sum(r["up"] > 0 for r in R.values())
w0 = sum(r["w0"] for r in R.values()) / n; w1 = sum(r["w1"] for r in R.values()) / n
b = list(B.values())[0]
ok = k2 == n and lett >= 2 and (n - k1) >= 2 and b["up"] > 0
print(f"RESULT: {'PASS' if ok else 'FAIL'} split at midpoint: words/line {w0:.1f}->{w1:.1f}; two-pass kept end pattern {k2}/{n}, "
      f"single-pass kept {k1}/{n}; exposed mid-line words lettered in {lett}/{n} natural stanzas ({upn} uppercase); "
      f"internal-rhyme break stanza: {b['up']} exposed word(s) promoted to UPPERCASE, end pattern kept={b['keep2']}")
