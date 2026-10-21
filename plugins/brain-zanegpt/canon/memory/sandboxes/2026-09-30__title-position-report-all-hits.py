# Composes: the title-power-positions kernel (title in first/last chorus line), sandbox-lyrics-structure/E3
# (content-word subsequence title matcher) and sandbox-title-matcher-stutter-split-vs-timing-hyphen-join/E1
# (try both hyphen-split and hyphen-joined views).
# PREDICTION (written before running): 8 choruses, each hand-labelled with the line(s) that carry the title drop.
# 1) exact-substring position check finds the labelled power-position drop in at most 4/8 choruses;
# 2) content-word matcher with both hyphen views finds it in 8/8;
# 3) reporting only the FIRST line that matches mislabels at least 2 choruses whose short title word
#    also appears earlier in a middle line; reporting every hit and checking first/last fixes both.
import re
STOP = {"i", "a", "the", "it", "and", "you", "me", "to", "be", "we", "that", "my", "is", "of", "in", "on", "so", "your"}
def toks(line, mode):
    s = line.lower()
    if mode == "join": s = s.replace("-", "")
    return re.findall(r"[a-z']+", s)
def st(w): return w[:-2] if w.endswith("ed") and len(w) > 4 else (w[:-1] if w.endswith("s") and len(w) > 3 else w)
def subseq(need, have):
    it = iter(have); return all(any(st(w) == st(h) for h in it) for w in need)
def cw(title): return [w for w in re.findall(r"[a-z']+", title.lower()) if w not in STOP]
def hit_sub(title, line): return title.lower() in line.lower()
def hit_cw(title, line): return any(subseq(cw(title), toks(line, m)) for m in ("split", "join"))
def pos(i, n): return "first" if i == 0 else "last" if i == n - 1 else "middle"
C = [  # (title, chorus lines, labelled drop positions)
 ("Hold The Line", ["we held the line", "through the fire and the rain", "nothing's gonna break us", "so hold the line"], {"first", "last"}),
 ("Bye Bye Bye", ["bye-bye-bye, i'm done", "don't want to be your fool", "no more calling me", "it ain't no lie, bye-bye-bye"], {"first", "last"}),
 ("Tonight", ["hold me close to-night", "the city's burning bright", "don't let it end", "we got to-night"], {"first", "last"}),
 ("Stay", ["stay", "i know you want to stay", "just one more hour", "please don't go"], {"first"}),
 ("Home", ["take me down the road", "where the porch light's on", "back to where it's warm", "take me home"], {"last"}),
 ("Run", ["run, run, run away", "leave it all behind", "don't look back tonight", "i can see you run"], {"first", "last"}),
 ("Walk Away", ["i walked away from you", "and never turned around", "the door is still open", "watch me walk away"], {"first", "last"}),
 ("Rain", ["i don't mind the rain", "the rain can have the town", "let it wash us clean", "dancing in the rain"], {"first", "last"}),
]
sub_ok = cw_ok = first_only_ok = all_hits_ok = 0
for title, lines, want in C:
    n = len(lines)
    sub_hits = {pos(i, n) for i, l in enumerate(lines) if hit_sub(title, l)} - {"middle"}
    cw_hits_all = [pos(i, n) for i, l in enumerate(lines) if hit_cw(title, l)]
    cw_hits = set(cw_hits_all) - {"middle"}
    sub_ok += sub_hits == want; cw_ok += cw_hits == want
    first = cw_hits_all[0] if cw_hits_all else None
    first_only_ok += (first in want and len(want) == 1) or (want == {"first", "last"} and first == "first" and False)
    all_hits_ok += cw_hits == want
    print(f"{title:13} want {sorted(want)} substring {sorted(sub_hits)} content-word {cw_hits_all}")
# first-only reporter: a single position per chorus (the first matching line)
first_only_ok = 0
for title, lines, want in C:
    n = len(lines); hits = [pos(i, n) for i, l in enumerate(lines) if hit_cw(title, l)]
    first_only_ok += bool(hits) and {hits[0]} == want
middle_extra = sum(any(pos(i, len(l)) == "middle" and hit_cw(t, x) for i, x in enumerate(l)) for t, l, _ in C)
print(f"substring exact {sub_ok}/8; content-word both views {cw_ok}/8; first-hit-only {first_only_ok}/8; choruses with extra middle hits {middle_extra}/8")
ok = sub_ok <= 4 and cw_ok == 8 and first_only_ok <= 6
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" substring {sub_ok}/8, content-word both views {cw_ok}/8, first-hit-only {first_only_ok}/8, middle hits in {middle_extra}/8")
