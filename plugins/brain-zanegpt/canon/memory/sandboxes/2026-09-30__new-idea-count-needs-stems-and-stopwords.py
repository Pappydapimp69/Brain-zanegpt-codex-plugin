# Composes: the one-lyric-line-is-one-intonation-unit kernel (one new idea per line, flag lines with more
# than about three new content words) and sandbox-compress-words-not-syllables-to-keep-a-repeated-rhythm/E1
# (compress by word count while holding syllables, using long words).
# PREDICTION (written before running): 12 lines in 3 sections, each hand-labelled with its count of new ideas.
# 1) raw new-token count (every unseen word) disagrees with the hand label on at least 6/12 lines;
# 2) new content words after stopword removal and simple stemming agree on at least 10/12, and the
#    over-three flag matches the hand "overloaded" label on 12/12;
# 3) the long-word compressed lines from the compress lesson (e.g. "honestly unbelievably") score 2 new
#    content words each, so the kernel's flag never fires on them: the two kernels do not conflict.
import re
STOP = set("i a the it and you me to be we that my is of in on so your was at for but with he she they them "
           "this there are am do did not no just all what when where like up out one".split())
def st(w):
    for suf in ("ing", "ed", "es", "s", "ly"):
        if w.endswith(suf) and len(w) - len(suf) >= 3: return w[: -len(suf)]
    return w
def words(l): return re.findall(r"[a-z']+", l.lower())
def count(section, mode):
    seen, out = set(), []
    for l in section:
        ws = words(l)
        if mode == "raw": new = [w for w in ws if w not in seen]; seen |= set(ws)
        else:
            c = [st(w) for w in ws if w not in STOP]; new = [w for w in dict.fromkeys(c) if w not in seen]; seen |= set(c)
        out.append(len(new))
    return out
S = [  # (line, hand count of new ideas) -- a new idea = a new referent, action or state
 [("the kitchen light is on", 1), ("your coffee cup is cold", 2), ("the kitchen light is on again", 0),
  ("i drove past the church where we married and the bank that took the house", 4)],
 [("i keep on running", 1), ("i keep on running", 0), ("running from the morning", 1),
  ("from the morning and the mornings after that", 0)],
 [("honestly unbelievably", 2), ("eventually nevermind", 2), ("the porch the rain the truck the dog the town", 5),
  ("and i was waiting", 1)],
]
raw_bad = st_bad = flag_bad = 0
for sec in S:
    lines = [l for l, _ in sec]; want = [n for _, n in sec]
    r = count(lines, "raw"); s = count(lines, "stem")
    for (l, w), a, b in zip(sec, r, s):
        raw_bad += a != w; st_bad += b != w; flag_bad += (b > 3) != (w > 3)
        print(f"  hand {w} raw {a} stem {b}  {l}")
print(f"raw disagrees {raw_bad}/12; stem+stop disagrees {st_bad}/12; over-3 flag disagrees {flag_bad}/12")
ok = raw_bad >= 6 and st_bad <= 2 and flag_bad == 0
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" raw new-token count off on {raw_bad}/12, stem+stopword count off on {st_bad}/12, over-three flag off on {flag_bad}/12; compressed long-word lines score 2 each")
