"""FIRST RUN (recorded): my pass-2 assigner never let a later assonant line join an earlier lowercase letter (a bug: the
assonance-only stanza printed aXbX), and P4 mistakenly said the single-pass assigner reports 3 pairs on the stray stanza
(ABBB has 2). The pass-2 code was fixed; the P4 count in this docstring is left as first written.
Prediction (written before the first run), mini lexicon with vowel + coda, rhyme families nasals {m,n}, stops {t,d},
sibilants {z,s}:
 P1 on AABB with perfect rhymes and AABB with assonance-only rhymes, the closure-distance metric (index gap to the most
    recent same-letter partner) is IDENTICAL (mean 1.0, 2 pairs), so it cannot tell a landing stanza from an open one.
 P2 the two-pass letters differ by case: 'AABB' vs 'aabb', and the count of uppercase (resolved) pairs is 2 vs 0.
 P3 ABBA keeps its outer pair at distance 3 under two-pass letters ('ABBA', pairs at distance 1 and 3).
 P4 (built to BREAK the single-pass assigner): on a stanza with genuine pairs only on lines 3 and 4 plus a stray assonance
    between line 2 and line 3, a single-pass vowel-only assigner reports 3 pairs; two-pass reports exactly 1 resolved pair
    at distance 1, letters 'XXAA'.
 P5 mixed stanza 'AAbb': two-pass gives resolved pairs 1 and open pairs 1; a closure-distance-only metric gives 2 pairs."""
LEX = {
 "day": ("EY", ""), "way": ("EY", ""), "play": ("EY", ""), "say": ("EY", ""),
 "gaze": ("EY", "z"), "name": ("EY", "m"), "rain": ("EY", "n"), "pain": ("EY", "n"),
 "light": ("AY", "t"), "night": ("AY", "t"), "time": ("AY", "m"), "mine": ("AY", "n"),
 "stone": ("OW", "n"), "alone": ("OW", "n"), "road": ("OW", "d"), "home": ("OW", "m"),
}
FAM = {"m": "N", "n": "N", "t": "S", "d": "S", "z": "Z", "s": "Z"}
def fam(c): return FAM.get(c, c)

def resolved(w1, w2):
    (v1, c1), (v2, c2) = LEX[w1], LEX[w2]
    return v1 == v2 and (c1 == c2 or (c1 and c2 and fam(c1) == fam(c2)))
def assonant(w1, w2):
    return LEX[w1][0] == LEX[w2][0]

def two_pass(words):
    n = len(words); lab = [None] * n; k = 0
    for i in range(n):                      # pass 1: resolved rhymes, UPPERCASE
        for j in range(i):
            if lab[j] and lab[j].isupper() and lab[j] != "X" and resolved(words[i], words[j]):
                lab[i] = lab[j]; break
        else:
            if lab[i] is None and any(resolved(words[i], words[m]) for m in range(i + 1, n)):
                lab[i] = chr(ord("A") + k); k += 1
    for i in range(n):                      # pass 2: assonance among unlettered, lowercase
        if lab[i] is not None: continue
        earlier = [j for j in range(i) if lab[j] and lab[j].islower() and assonant(words[i], words[j])]
        if earlier: lab[i] = lab[earlier[-1]]
        elif any(lab[m] is None and assonant(words[i], words[m]) for m in range(i + 1, n)):
            lab[i] = chr(ord("a") + k); k += 1
    return "".join(l if l else "X" for l in lab)

def single_pass(words):
    lab = []; k = 0
    for i, w in enumerate(words):
        for j in range(i):
            if assonant(w, words[j]): lab.append(lab[j]); break
        else:
            lab.append(chr(ord("A") + k)); k += 1
    return "".join(lab)

def pairs(scheme):
    out = []
    for i, c in enumerate(scheme):
        if c == "X": continue
        prev = [j for j in range(i) if scheme[j] == c]
        if prev: out.append((prev[-1], i, i - prev[-1], c.isupper()))
    return out
def metric(scheme):
    p = pairs(scheme)
    return {"pairs": len(p), "mean_dist": (sum(x[2] for x in p) / len(p)) if p else 0, "resolved": sum(x[3] for x in p), "dists": [x[2] for x in p]}

S = {
 "aabb_perfect": ["day", "way", "night", "light"],
 "aabb_assonance": ["day", "gaze", "light", "time"],
 "abba": ["light", "rain", "pain", "night"],
 "stray": ["night", "name", "day", "way"],
 "mixed": ["day", "way", "gaze", "name"],
}
R = {}
for k, w in S.items():
    tp, sp = two_pass(w), single_pass(w)
    R[k] = (tp, sp, metric(tp), metric(sp))
    print(f"{k:15s} two-pass={tp} single-pass={sp} tp_metric={R[k][2]} sp_pairs={R[k][3]['pairs']}")
dist_only = lambda k: (metric(R[k][1].replace(R[k][1], R[k][1]))["pairs"], round(metric(R[k][1])["mean_dist"], 3))
held = {
 "P1": metric(R["aabb_perfect"][0].upper())["mean_dist"] == metric(R["aabb_assonance"][0].upper())["mean_dist"] == 1.0
       and metric(R["aabb_perfect"][0].upper())["pairs"] == metric(R["aabb_assonance"][0].upper())["pairs"] == 2,
 "P2": R["aabb_perfect"][0] == "AABB" and R["aabb_assonance"][0] == "aabb"
       and R["aabb_perfect"][2]["resolved"] == 2 and R["aabb_assonance"][2]["resolved"] == 0,
 "P3": R["abba"][0] == "ABBA" and sorted(R["abba"][2]["dists"]) == [1, 3],
 "P4": R["stray"][0] == "XXAA" and R["stray"][2]["resolved"] == 1 and R["stray"][2]["pairs"] == 1 and R["stray"][3]["pairs"] == 3,
 "P5": R["mixed"][0] == "AAbb" and R["mixed"][2]["resolved"] == 1 and metric(R["mixed"][0].upper())["pairs"] == 2,
}
print("predictions:", ", ".join(f"{k}={'held' if v else 'MISSED'}" for k, v in held.items()))
n = sum(held.values())
print("RESULT:", "PASS" if n == len(held) else "FAIL",
      f"{n}/{len(held)} predictions held; aabb perfect {R['aabb_perfect'][0]} vs assonance {R['aabb_assonance'][0]} (distance-only both mean 1.0); "
      f"abba {R['abba'][0]} dists {R['abba'][2]['dists']}; stray two-pass {R['stray'][0]} pairs {R['stray'][2]['pairs']} vs single-pass {R['stray'][1]} pairs {R['stray'][3]['pairs']}; mixed {R['mixed'][0]}")
