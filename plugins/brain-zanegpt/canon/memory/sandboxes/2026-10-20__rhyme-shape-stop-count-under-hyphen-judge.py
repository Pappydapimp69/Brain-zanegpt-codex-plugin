from itertools import product
# word: (segments, whole-word key, vowel)
LEX = {
 "borrow":  (("bor","row"), "orrow", "o"), "tomorrow": (("to","mor","row"), "orrow", "o"),
 "below":   (("be","low"),  "ow", "o"),    "glow":     (("glow",), "ow", "o"),
 "today":   (("to","day"),  "ay", "a"),    "stay":     (("stay",), "ay", "a"),
 "daylight":(("day","light"),"ight","i"),  "night":    (("night",), "ight", "i"),
}
W = list(LEX)
def kw(w): return LEX[w][1]
def kl(w):
    seg = LEX[w][0][-1]
    return {"row": "ow", "low": "ow", "day": "ay"}.get(seg, LEX[w][1]) if seg in ("row","low","day") else LEX[w][1]
def shape(st, keyf):
    ks = [keyf(w) for w in st]; m = {}; return "".join(m.setdefault(k, chr(65+len(m))) for k in ks)
def stops(sh):            # a "stopping point": a line that rhymes with the line immediately before it
    return sum(sh[i] == sh[i-1] for i in range(1, 4))
def gap(sh):              # mean distance back to the nearest earlier rhyme partner (open = larger)
    g = [i - max(j for j in range(i) if sh[j] == sh[i]) for i in range(4) if sh[i] in sh[:i]]
    return sum(g) / len(g) if g else 0
# S1: kernel shapes under the whole-word judge
base = {"AABB": ("borrow","tomorrow","glow","below"), "ABAB": ("glow","stay","below","today"),
        "ABBA": ("glow","stay","today","below"), "XXAA": ("glow","stay","night","daylight")}
print("shape stops mean-gap (whole judge)")
tab = {}
for name, st in base.items():
    sh = shape(st, kw); tab[sh] = (stops(sh), gap(sh)); print(" ", name, sh, stops(sh), round(gap(sh), 2))
# S2: all stanzas: how often does the last-segment judge change the stop count / shape class
n = shape_chg = stop_chg = 0; stop_chg_nofem = tot_nofem = 0
NOFEM = [w for w in W if w not in ("borrow", "tomorrow")]
for st in product(W, repeat=4):
    a, b = shape(st, kw), shape(st, kl); n += 1
    if a != b: shape_chg += 1
    if stops(a) != stops(b): stop_chg += 1
for st in product(NOFEM, repeat=4):
    tot_nofem += 1; stop_chg_nofem += stops(shape(st, kw)) != stops(shape(st, kl))
print(f"stanzas {n}: shape differs {shape_chg}, stop count differs {stop_chg}; without feminine words {stop_chg_nofem}/{tot_nofem}")
# S3 BREAK: kernel ordering of openness: does mean-gap order ABAB > AABB hold, and ABBA vs ABAB?
order_ok = tab["AABB"][0] > tab["ABAB"][0] and tab["AABB"][1] < tab["ABAB"][1]
abba_open = tab["ABBA"][1] > tab["AABB"][1]
print("AABB more stops than ABAB and smaller gap:", order_ok, "; ABBA gap larger than AABB:", abba_open, "; ABBA vs ABAB gap", tab["ABBA"][1], tab["ABAB"][1])
ok = order_ok and abba_open and stop_chg > 0 and stop_chg_nofem == 0
print(("RESULT: PASS " if ok else "RESULT: FAIL ") + f"last-segment judge changes the stop count of {stop_chg}/{n} stanzas, 0 without feminine words; AABB stops {tab['AABB'][0]} vs ABAB {tab['ABAB'][0]}; ABBA gap {tab['ABBA'][1]} vs ABAB {tab['ABAB'][1]}")
