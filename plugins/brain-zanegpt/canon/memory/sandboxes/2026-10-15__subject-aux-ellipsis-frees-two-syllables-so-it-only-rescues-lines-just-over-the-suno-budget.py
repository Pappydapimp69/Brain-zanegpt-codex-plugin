"""Sandbox: can conversational ellipsis pay for a rushed Suno line where hyphenation cannot?

suno-builder warns when a line's counted syllables exceed budget + 3 (default
budget 9, so > 12) and suggests shortening or hyphenating long words. Earlier
lesson suno-builder/E11: hyphenating never lowers the count. The ellipsis kernel
says casual speech drops a leading subject + auxiliary ("Been a while"), freeing
syllables. This sandbox ports the builder's syllable counter and hyphenator to
Python (cross-checked once against node on the real builder, outside this file)
and applies three fixes to a hand-written casual-register corpus:
  H  hyphenate the longest word (the builder's suggestion)
  EN drop a leading subject+aux pair wherever it opens a line (the kernel's linter as written)
  EG same, but only when the next word is not a determiner or pronoun (guarded)
  EG+H guarded ellipsis, then hyphenate the longest word to slow it
Deterministic, stdlib only.
"""
import re

BUDGET = 9
WARN = BUDGET + 3


def syl_part(w):
    w = re.sub(r"[^a-z']", "", w.lower())
    if not w:
        return 0
    if len(w) <= 3:
        return 1
    x = re.sub(r"(?:[^laeiouy]es|[^laeiouy]ed|[^laeiouyt]e)$", "", w)
    x = re.sub(r"^y", "", x)
    m = re.findall(r"[aeiouy]{1,3}", x)
    n = len(m) if m else 1
    if re.search(r"[^aeiouy]le$", w) and not re.search(r"[aeiouy]le$", w):
        n = max(n, 2)
    return max(1, n)


def syl_word(word):
    parts = [p for p in word.split("-") if re.sub(r"[^a-z']", "", p, flags=re.I)]
    if len(parts) > 1:
        return sum(max(1, syl_part(p)) for p in parts)
    return syl_part(word)


def line_syl(line):
    return sum(syl_word(w) for w in re.findall(r"[A-Za-z'-]+", line))


def hyphenate(word):
    clean = word.replace("-", "")
    if syl_part(clean) < 2:
        return word
    isv = lambda c: c in "aeiouyAEIOUY"
    groups, j = [], 0
    while j < len(clean):
        if isv(clean[j]):
            s = j
            while j < len(clean) and isv(clean[j]):
                j += 1
            groups.append((s, j))
        else:
            j += 1
    cuts = []
    for g in range(len(groups) - 1):
        endv, nextv = groups[g][1], groups[g + 1][0]
        cl = nextv - endv
        if cl <= 0:
            continue
        cuts.append(endv if cl == 1 else endv + cl - 1)
    if not cuts:
        return word
    out, prev = [], 0
    for c in cuts:
        out.append(clean[prev:c])
        prev = c
    out.append(clean[prev:])
    merged = []
    for ch in out:
        if not re.search(r"[aeiouy]", ch, re.I) and merged:
            merged[-1] += ch
        else:
            merged.append(ch)
    return "-".join(x for x in merged if x)


def hyph_longest(line):
    ws = line.split(" ")
    i = max(range(len(ws)), key=lambda k: (len(re.sub(r"[^A-Za-z]", "", ws[k])), -k))
    ws[i] = hyphenate(ws[i])
    return " ".join(ws)


PAIRS = [("it", "has"), ("it", "is"), ("i", "am"), ("i", "have"), ("do", "you"),
         ("are", "you"), ("i", "will"), ("have", "you")]
CONTRACTIONS = {"it's", "i'm", "i've", "i'll"}
BLOCK = {"the", "a", "an", "my", "your", "our", "his", "her", "their", "this", "that",
         "you", "me", "him", "them", "us", "i", "one"}


def elide(line, guarded):
    ws = line.split(" ")
    low = [w.lower().strip(",.?!") for w in ws]
    n = 0
    if len(low) >= 2 and (low[0], low[1]) in PAIRS:
        n = 2
    elif low and low[0] in CONTRACTIONS:
        n = 1
    if n == 0:
        return line, "none"
    nxt = low[n] if len(low) > n else ""
    if guarded and nxt in BLOCK:
        return line, "blocked"
    rest = ws[n:]
    rest[0] = rest[0][:1].upper() + rest[0][1:]
    return " ".join(rest), "elided"


# corpus: (group, line). A = droppable opener before a verb/participle (elision keeps meaning);
# B = droppable opener before a noun phrase/pronoun (elision changes meaning; my labels);
# C = no droppable opener.
CORPUS = [
    ("A", "It has been a long time since I drove down this highway"),
    ("A", "I have been waiting by the window every single evening"),
    ("A", "Do you remember the motel with the broken neon sign"),
    ("A", "I am getting tired of the radio and the rain"),
    ("A", "It is getting harder to remember how your laughter sounded"),
    ("A", "I've been driving all night with the windows rolled down low"),
    ("A", "It's been a while since anybody called me by my name"),
    ("A", "Are you still awake and thinking of the summer by the river"),
    ("A", "I will be leaving in the morning when the station opens"),
    ("A", "I'm still holding on to every letter that you never sent"),
    ("B", "I am the reason that you never answered when I called you"),
    ("B", "It is the silence after midnight that I can't forgive"),
    ("B", "I'm the one who kept the porch light on for you all winter"),
    ("B", "It's you I think of every time the jukebox plays our song"),
    ("C", "The highway hums beneath the tires like a lullaby gone wrong"),
    ("C", "Your mother's photographs are fading on the refrigerator door"),
    ("C", "Every streetlight in this city knows the color of my coat"),
    ("C", "Somewhere down in Tennessee a radio is playing our song"),
    ("C", "Yesterday the morning paper said the factory would close"),
    ("C", "Maybe we were never meant to make it past the borderline"),
]

rows = []
for g, line in CORPUS:
    s0 = line_syl(line)
    h = hyph_longest(line)
    en, en_st = elide(line, guarded=False)
    eg, eg_st = elide(line, guarded=True)
    egh = hyph_longest(eg)
    rows.append(dict(g=g, line=line, s0=s0, sh=line_syl(h), sen=line_syl(en), en_st=en_st,
                     seg=line_syl(eg), eg_st=eg_st, segh=line_syl(egh), last_kept=eg.split()[-1] == line.split()[-1],
                     eg=eg))
    print(f"{g} {s0:2d} H{line_syl(h):3d} EN{line_syl(en):3d}({en_st:7s}) EG{line_syl(eg):3d}({eg_st:7s}) EG+H{line_syl(egh):3d} | {eg}")

warned = [r for r in rows if r["s0"] > WARN]
print(f"lines over the warning (> {WARN}): {len(warned)}/{len(rows)}; by group "
      + ", ".join(f"{g}:{sum(1 for r in warned if r['g']==g)}" for g in 'ABC'))
clr = lambda key: sum(1 for r in warned if r[key] <= WARN)
h_lower = sum(1 for r in rows if r["sh"] < r["s0"])
h_raise = sum(1 for r in rows if r["sh"] > r["s0"])
freed = [r["s0"] - r["seg"] for r in rows if r["eg_st"] == "elided"]
print(f"H: cleared {clr('sh')}/{len(warned)}; lowered {h_lower}/{len(rows)} lines, raised {h_raise}")
print(f"EG: cleared {clr('seg')}/{len(warned)}; syllables freed per elided line {sorted(freed)}")
print(f"EG+H: cleared {clr('segh')}/{len(warned)}")
wrongB = sum(1 for r in rows if r["g"] == "B" and r["en_st"] == "elided")
blockedA = sum(1 for r in rows if r["g"] == "A" and r["eg_st"] == "blocked")
blockedB = sum(1 for r in rows if r["g"] == "B" and r["eg_st"] == "blocked")
print(f"naive linter elides {wrongB}/4 meaning-changing B lines; guard blocks B {blockedB}/4, wrongly blocks A {blockedA}/10")
c_cleared = sum(1 for r in warned if r["g"] == "C" and r["seg"] <= WARN)
a_warned = [r for r in warned if r["g"] == "A"]
a_left = [r for r in a_warned if r["seg"] > WARN]
print(f"group C warned lines cleared by ellipsis: {c_cleared}; group A warned still over after EG: {len(a_left)}/{len(a_warned)} "
      f"(counts {[r['s0'] for r in a_left]})")
print(f"rhyme (last) word kept by EG on all lines: {all(r['last_kept'] for r in rows)}")

checks = [
    ("H never lowers a line count", h_lower == 0),
    ("EG clears more warned lines than H", clr('seg') > clr('sh')),
    ("naive linter elides the meaning-changing lines", wrongB == 4),
    ("guard blocks all B, no A", blockedB == 4 and blockedA == 0),
    ("ellipsis cannot clear no-opener lines", c_cleared == 0),
    ("rhyme word kept", all(r['last_kept'] for r in rows)),
]
for name, ok in checks:
    print(f"  check {name}: {ok}")
allok = all(ok for _, ok in checks)
print(f"RESULT: {'PASS' if allok else 'FAIL'} of {len(warned)} over-budget lines hyphenation cleared {clr('sh')}, "
      f"guarded ellipsis {clr('seg')} (freed {min(freed)}-{max(freed)} syl), ellipsis then hyphenation {clr('segh')}; "
      f"naive linter mangled {wrongB}/4 copular lines, guard 0 wrong blocks; {len(a_left)}/{len(a_warned)} elidable warned lines still over")
