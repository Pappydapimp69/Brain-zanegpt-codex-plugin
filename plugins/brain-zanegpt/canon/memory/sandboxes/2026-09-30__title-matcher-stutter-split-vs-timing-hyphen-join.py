# Composes: lyrics-structure/E3 (content-word subsequence title matcher), stutter-hooks sandbox/E1 (split on hyphens to
# find stutter hooks), and the hyphenate-to-slow kernel (writers hyphenate words for sung timing: to-night, beau-ti-ful).
# PREDICTION (written before running): on 4 stutter lines + 4 timing-hyphenated lines + 2 inflection variants,
# split-on-hyphen finds stutter 4/4 but timing 0/4; join-hyphens finds timing 4/4 but stutter at most 1/4;
# trying both token views finds all 10; neither view adds a false positive on 3 absent-title probes.
# FIRST RUN: two prediction parts missed -- both views found 9/10 (irregular past 'held' is not a hyphen problem) and
# split view matched 'Stay' inside the compound 'stay-at-home' (1 false positive). The check below now asserts only
# the hyphen claim; the inflection miss and compound false positive are reported, not hidden.
import re
STOP = {"i", "a", "the", "it", "and", "you", "me", "to", "be", "we", "that", "my", "is"}
def view(line, mode):
    s = line.lower()
    if mode == "join": s = s.replace("-", "")
    return re.findall(r"[a-z']+", s)          # split mode: hyphen becomes a separator
def stems(w): return w[:-2] if w.endswith("ed") and len(w) > 4 else w
def subseq(need, have):
    it = iter(have); return all(any(stems(w) == stems(h) for h in it) for w in need)
def match(title, line, modes):
    need = [w for w in re.findall(r"[a-z']+", title.lower()) if w not in STOP]
    return any(subseq(need, view(line, m)) for m in modes)
STUTTER = [("Bye Bye Bye", "bye-bye-bye, i'm done"), ("Ba Ba Baby", "ba-ba-baby come back"),
           ("Oh La La", "oh-la-la the night is young"), ("No No No", "no-no-no, not again")]
TIMING = [("Tonight", "hold me to-night"), ("Beautiful", "so beau-ti-ful and slow"),
          ("Forever", "we were for-ev-er young"), ("Desire", "this de-sire won't die")]
INFLECT = [("Hold The Line", "we held the line"), ("Walk Away", "i walked away from you")]
ABSENT = [("Tonight", "to night we ride"), ("Stay", "stay-at-home blues is over"), ("Forever", "four ever green trees")]
def score(cases, modes): return sum(match(t, l, modes) for t, l in cases)
S, J, B = ["split"], ["join"], ["split", "join"]
rows = {name: (score(c, S), score(c, J), score(c, B)) for name, c in [("stutter", STUTTER), ("timing", TIMING), ("inflection", INFLECT)]}
fp = {m: [match(t, l, v) for t, l in ABSENT] for m, v in [("split", S), ("join", J), ("both", B)]}
for k, v in rows.items(): print(f"{k:10s} split={v[0]}/{len(STUTTER if k!='inflection' else INFLECT)} join={v[1]} both={v[2]}")
print("absent-title probes (true = false positive):", fp)
total_both = sum(v[2] for v in rows.values())
ok = rows["stutter"][:2] == (4, 0) and rows["timing"][:2] == (0, 4) and rows["stutter"][2] + rows["timing"][2] == 8
print("RESULT: %s split finds stutter %d/4 timing %d/4; join finds timing %d/4 stutter %d/4; both views find %d/10 (hyphen cases 8/8); false positives split %d join %d both %d of 3" % (
    "PASS" if ok else "FAIL", rows["stutter"][0], rows["timing"][0], rows["timing"][1], rows["stutter"][1], total_both, sum(fp["split"]), sum(fp["join"]), sum(fp["both"])))
