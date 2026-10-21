# Sandbox: hyphenating hiatus words x vowel-group syllable warning x two-pass rhyme letters, 4-line stanzas.
# Prediction (before first run): hyphenating every word drops the vowel-group warning's miss rate on crowded
# lines from ~36% to under 5%; with a whole-word rhyme judge letters stay 0% wrong, with a last-segment
# judge 15-35% of stanzas get a wrong letter; the two judges differ in letters only, not in the warning.
import itertools, re
BUDGET, SLACK = 9, 3
# words as syllable segments (true syllables = number of segments)
FILL = [["beau","ti","ful"],["ev","ery","thing"],["wan","der","ing"],["qui","et"],["the"],["a"],["we"],["burn","ing"],
        ["po","em"],["vi","o","lin"],["ra","di","o"],["be","ing"],["i","de","al"],["cre","ate"],["li","on"],["di","et"],["re","act"]]
ENDS = [["light"],["night"],["de","sire"],["fire"],["ra","di","o"],["vi","de","o"],["pi","a","no"],["i","de","a"],["li","on"],["be","gin"]]
vg = lambda s: max(1, len(re.findall(r"[aeiouy]+", s)))
def est_plain(w): return vg("".join(w))
def est_hyph(w): return sum(vg(s) for s in w)
def key(w, judge):
    s = w[-1] if judge == "last" else "".join(w)
    return s[-3:]
def letters(ends, judge):
    seen, out = {}, []
    for e in ends:
        k = key(e, judge); seen.setdefault(k, len(seen)); out.append(seen[k])
    return out
def partition(l): return sorted(tuple(i for i in range(4) if l[i] == v) for v in set(l))
FILLS = list(itertools.combinations_with_replacement(range(len(FILL)), 4))
n = 0; crowded = 0; miss = {"plain": 0, "hyph": 0}; wrong = {"whole": 0, "last": 0}; stanzas = 0
for ends in itertools.product(ENDS, repeat=4):
    fi = FILLS[(n * 7) % len(FILLS)]; n += 1
    stanzas += 1
    for j in range(4):
        words = [FILL[i] for i in fi[:j+1]] + [ends[j]]
        true = sum(len(w) for w in words)
        if true > BUDGET + SLACK:
            crowded += 1
            if sum(est_plain(w) for w in words) <= BUDGET + SLACK: miss["plain"] += 1
            if sum(est_hyph(w) for w in words) <= BUDGET + SLACK: miss["hyph"] += 1
    truth = partition(letters(ends, "whole"))
    for judge in ("whole", "last"):
        if partition(letters(ends, judge)) != truth: wrong[judge] += 1
mp, mh = miss["plain"]/crowded, miss["hyph"]/crowded
ww, wl = wrong["whole"]/stanzas, wrong["last"]/stanzas
print("S1 crowded lines %d; warning miss plain %.1f%%" % (crowded, mp*100))
print("S2 same lines, all words hyphenated: miss %.1f%%" % (mh*100))
print("S3 whole-word judge mislettered stanzas %.1f%% of %d" % (ww*100, stanzas))
print("S4 (break) last-segment judge mislettered stanzas %.1f%%" % (wl*100))
print("original prediction held:", mp > 0.2 and mh < 0.05 and ww == 0 and 0.15 <= wl <= 0.35)
ok = mh < mp and mh < 0.05 and ww == 0 and wl > 0.05
print("RESULT: %s hyphenating cut the warning miss %.0f%%->%.0f%% but a last-segment judge mislettered %.1f%% of stanzas (whole-word %.1f%%)" % ("PASS" if ok else "FAIL", mp*100, mh*100, wl*100, ww*100))
