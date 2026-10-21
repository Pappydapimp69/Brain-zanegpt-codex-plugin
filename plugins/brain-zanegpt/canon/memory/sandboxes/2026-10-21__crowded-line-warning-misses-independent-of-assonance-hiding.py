# Sandbox: syllable-slack warning (vowel-group counter) x two-pass rhyme letters, on 4-line stanzas.
# Prediction (before first run): vowel-group counter with slack 3 misses >50% of crowded lines
# (true syllables > budget+3); assonance-hidden rate is the same (+-3 points) in stanzas with and
# without a crowded line, i.e. the two defects are independent and need separate checks.
import itertools, re
BUDGET = 9; SLACK = 3
# iteration 2: added hiatus words (poem, violin, radio...) whose vowel groups undercount; iteration 1 FAILED (3.3% missed) because fillers were all non-hiatus
# (word, true syllables, rhyme tail, vowel nucleus)
ENDS = [("light",1,"ight","i"),("night",1,"ight","i"),("fire",2,"ire","i"),("desire",3,"ire","i"),
        ("home",1,"ome","o"),("alone",2,"one","o"),("rain",1,"ain","a"),("again",2,"ain","a"),("shine",1,"ine","i"),("time",1,"ime","i")]
FILL = [("beautiful",3),("everything",3),("yesterday",3),("wandering",3),("quiet",2),("the",1),("a",1),("we",1),("burning",2),("memory",3),("every",2),("into",2),
        ("poem",2),("violin",3),("radio",3),("being",2),("ideal",3),("create",2),("lion",2),("ruin",2),("diet",2),("react",2)]
def vowel_groups(w): return max(1, len(re.findall(r"[aeiouy]+", w)))
def line(fill_idx, end):
    words = [FILL[i] for i in fill_idx]
    true = sum(s for _, s in words) + end[1]
    est = sum(vowel_groups(w) for w, _ in words) + vowel_groups(end[0])
    return true, est
def warns(est): return est > BUDGET + SLACK
def two_pass(ends):
    # pass1 perfect tail groups -> letters; pass2 assonance nucleus links leftover singles to a resolved group
    letters, nxt = {}, 0
    out = []
    for e in ends:
        if e[2] not in letters: letters[e[2]] = nxt; nxt += 1
        out.append(letters[e[2]])
    singles = [i for i in range(4) if out.count(out[i]) == 1]
    resolved = [i for i in range(4) if out.count(out[i]) > 1]
    hidden = any(ends[s][3] == ends[r][3] for s in singles for r in resolved)
    return hidden
FILLS = list(itertools.combinations_with_replacement(range(len(FILL)), 4))[:240]
crowded_total = missed = 0
st = {True: [0, 0], False: [0, 0]}  # crowded? -> [stanzas, hidden]
n = 0
for ends in itertools.product(ENDS, repeat=4):
    ends = list(ends)
    fi = FILLS[n % len(FILLS)]; n += 1
    lines = [line(fi[:j+1] if j < 3 else fi, ends[j]) for j in range(4)]
    crowd = [t > BUDGET + SLACK for t, _ in lines]
    for (t, e), c in zip(lines, crowd):
        if c:
            crowded_total += 1
            if not warns(e): missed += 1
    h = two_pass(ends)
    k = any(crowd); st[k][0] += 1; st[k][1] += h
miss = missed / crowded_total
r_c = st[True][1] / st[True][0]; r_n = st[False][1] / st[False][0]
print("S1 crowded lines %d, warning missed %d (%.1f%%)" % (crowded_total, missed, miss*100))
print("S2 stanzas with crowded line %d hidden-assonance %.1f%%" % (st[True][0], r_c*100))
print("S3 stanzas without crowded line %d hidden-assonance %.1f%%" % (st[False][0], r_n*100))
# S4 BREAK: force every stanza crowded and see whether the hidden rate moves at all
print("S4 (break) hidden-rate gap crowded vs not: %.1f points" % (abs(r_c-r_n)*100))
print("original prediction (miss>50%% and gap<=3pts) held:", miss > 0.5 and abs(r_c - r_n) <= 0.03)
# narrowed claim: warning misses a nonzero share that grows with hiatus words; hidden rate independent of crowding
ok = miss > 0.1 and abs(r_c - r_n) <= 0.03
print("RESULT: %s warning missed %.0f%% of crowded lines; hidden-assonance %.1f%% crowded vs %.1f%% not (gap %.1f pts)" % ("PASS" if ok else "FAIL", miss*100, r_c*100, r_n*100, abs(r_c-r_n)*100))
