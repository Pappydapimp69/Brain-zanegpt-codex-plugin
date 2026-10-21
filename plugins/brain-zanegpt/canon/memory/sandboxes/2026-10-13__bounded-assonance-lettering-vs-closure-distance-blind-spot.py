# Prediction (before run): toy lexicon word -> (vowel, tail). Pass 1 letters perfect rhymes (same tail) uppercase;
# pass 2 letters unresolved same-vowel lines lowercase. UNBOUNDED pass 2 puts four same-vowel/different-tail lines
# on one letter (closure distances [1,1,1]); BOUNDED pass 2 (each line joins at most one earlier unresolved line)
# gives 'aabb'. Closure distance alone cannot tell perfect AABB from assonance aabb (both [1,1]) and, after bounding,
# cannot tell assonance aabb from the 4-line mush either (also [1,1]); resolved-pair count (2 / 0 / 0) separates the
# first from the others, and only the vowel-tail diversity count (distinct tails) separates the last two.
LEX = {"night":("ai","t"),"light":("ai","t"),"line":("ai","n"),"mine":("ai","n"),"time":("ai","m"),"rhyme":("ai","m"),
       "side":("ai","d"),"pride":("ai","d"),"tide":("ai","d"),"town":("ow","n"),"cloud":("ow","d"),"found":("ow","nd"),"sound":("ow","nd"),
       "stone":("oh","n"),"home":("oh","m"),"bone":("oh","n"),"road":("oh","d")}
def letters(words, bounded):
    n = len(words); lab = [None]*n; nxt = 0; pool = "ABCDEFGH"
    for i in range(n):                      # pass 1: perfect rhyme
        if lab[i] is not None: continue
        mates = [j for j in range(i+1, n) if LEX[words[j]] == LEX[words[i]] and lab[j] is None]
        if mates:
            L = pool[nxt]; nxt += 1; lab[i] = L
            for j in mates: lab[j] = L
    unres = [i for i in range(n) if lab[i] is None]
    low = "abcdefgh"; k = 0; used = set()
    for i in unres:                         # pass 2: assonance, lowercase
        if i in used: continue
        mates = [j for j in unres if j > i and j not in used and LEX[words[j]][0] == LEX[words[i]][0]]
        if bounded: mates = mates[:1]
        L = low[k]; k += 1; lab[i] = L; used.add(i)
        for j in mates: lab[j] = L; used.add(j)
    return "".join(lab)
def closure(lab):
    out = []
    for L in sorted(set(lab)):
        idx = [i for i, c in enumerate(lab) if c == L]
        out += [b - a for a, b in zip(idx, idx[1:])]
    return sorted(out)
def report(words, bounded):
    lab = letters(words, bounded)
    resolved = sum(1 for L in set(lab) if L.isupper() and lab.count(L) > 1)
    tails = len({LEX[w][1] for w in words})
    return lab, closure(lab), resolved, tails
stanzas = {
 "perfect AABB": ["night","light","line","mine"],
 "assonance aabb": ["night","line","time","side"],    # no perfect pair; all same vowel -> still assonance
 "mush 4 same vowel": ["night","line","time","side"],
 "perfect ABAB": ["night","line","light","mine"],
 "two vowels BREAK": ["town","stone","cloud","home"],
}
rows = {}
for name, w in stanzas.items():
    for b in (False, True):
        rows[(name, b)] = report(w, b)
        print("%-18s bounded=%-5s letters %s closure %s resolved %d tails %d" % ((name, b) + rows[(name, b)]))
u = rows[("mush 4 same vowel", False)]; bd = rows[("mush 4 same vowel", True)]
p = rows[("perfect AABB", True)]
ok = u[0] == "aaaa" and bd[0] == "aabb" and p[0] == "AABB" and p[1] == bd[1] == [1, 1] and p[2] == 2 and bd[2] == 0
print("RESULT: %s unbounded mush %s closure %s; bounded mush %s closure %s equals perfect AABB closure %s; resolved pairs perfect %d vs mush %d; distinct tails %d vs %d"
      % ("PASS" if ok else "FAIL", u[0], u[1], bd[0], bd[1], p[1], p[2], bd[2], p[3], bd[3]))
