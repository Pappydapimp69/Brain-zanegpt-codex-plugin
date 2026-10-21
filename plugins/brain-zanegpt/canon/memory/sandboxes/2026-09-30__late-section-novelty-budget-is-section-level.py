"""Sandbox L8: section-level novelty against the payoff-slot budget, current vs revised song.

Kernels: ideas:SONGWRITING/outline-tooling/payoff-slot-budget (late sections can afford almost no new
emphasis) and the new-idea-count lesson (sandbox-new-idea-count-needs-stems-and-stopwords E1: a
more-than-three new-content-word line flag matched hand labels 12/12). Novelty of a section = share of
its content-word tokens whose stem was not heard earlier in the song. Revised version applies loops
1, 2 and 4: final chorus verbatim with "Did you eat, Mom?", new lines moved to the outro, outro pays
the coat setup. Deterministic, stdlib only.

PREDICTION (written before the first run):
  P1 current final chorus novelty <= 25%
  P2 revised final chorus novelty <= 10%
  P3 revised outro novelty >= current final chorus novelty (material moved, not deleted)
  P4 break: no single line of the current final chorus trips the >3-new-words line flag, i.e. the
     line-level flag cannot see a section-level budget overrun
"""
import re

STOP = set("a an the and or but so of to in on at for with by from is are was were be been am i me my you your "
           "we our it its this that he she her his they them there here what who how when where can will would "
           "could just all as if up down out into over than then not no yes oh yeah do did does don't didn't i'm "
           "it's that's there's i'd she's".split())


def stem(w):
    for suf in ("ing", "ed", "es", "s", "er", "ly"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[: -len(suf)]
    return w


def content(line):
    toks = re.findall(r"[a-z']+", line.lower().replace("-", " "))
    return [stem(t) for t in toks if t not in STOP]


BASE = [
    ("intro", ["Did you eat?", "Yeah, Mom!"]),
    ("verse1", ["Six-fifteen and my phone lights up", "Same old bubble, same old stuff",
                "Wear a coat. Is the bus on time?", "Mom, I'm seventeen, I'm fine"]),
    ("pre1", ["And every night, the same last line", "Right before I close my eyes"]),
    ("chorus1", ["Did you eat? Yeah, Mom", "Did you eat? Yeah, Mom", "Every night like a clock on the wall",
                 "Two words back, that's all", "Did you eat? Yeah, Mom"]),
    ("verse2", ["Twenty-three in a room where the door sticks", "Rent's due Friday, so I'm skipping lunch for it",
                "Phone lights up and I type it slow", "Kinda. Had a coffee. Busy. You know."]),
    ("pre2", ["She sends a heart and a photo of soup", "Says there's a bowl with my name on it too"]),
    ("chorus2", ["Did you eat? Yeah, Mom", "Did you eat? Yeah, Mom", "Two little words and a lie that's small",
                 "Cheaper than the truth, that's all", "Did you eat? Yeah, Mom"]),
    ("bridge", ["Said I'd come home Sunday", "Then I said next Sunday", "Then her texts came slower",
                "Then they came short", "Then they didn't"]),
]
CURRENT = BASE + [
    ("final", ["Did you eat?", "Did you eat?", "Six-fifteen, my turn to ask", "Two words out, and nothing back", "Did you eat?"]),
    ("outro", ["Did you eat?"]),
]
REVISED = BASE + [
    ("final", ["Did you eat, Mom?", "Did you eat, Mom?", "Every night like a clock on the wall",
               "Two words back, that's all", "Did you eat, Mom?"]),
    ("outro", ["Six-fifteen, my turn to ask", "Wear a coat. Did you eat, Mom?"]),
]


def novelty(song):
    seen, out, lines = set(), {}, {}
    for name, ls in song:
        toks, new, per_line = 0, 0, []
        for ln in ls:
            c = content(ln)
            n_new = sum(1 for t in c if t not in seen)
            per_line.append(len({t for t in c if t not in seen}))
            toks += len(c)
            new += n_new
            seen.update(c)
        out[name] = new / toks if toks else 0.0
        lines[name] = per_line
    return out, lines


cur, cur_lines = novelty(CURRENT)
rev, _ = novelty(REVISED)
res = [("P1 current final <= 25%", cur["final"] <= 0.25, f"{cur['final']:.0%}"),
       ("P2 revised final <= 10%", rev["final"] <= 0.10, f"{rev['final']:.0%}"),
       ("P3 revised outro >= current final", rev["outro"] >= cur["final"], f"outro {rev['outro']:.0%} vs {cur['final']:.0%}"),
       ("P4 break: no final line trips >3 flag", max(cur_lines["final"]) <= 3, f"max new per line {max(cur_lines['final'])}")]
print("current novelty:", ", ".join(f"{k} {v:.0%}" for k, v in cur.items()))
print("revised novelty:", ", ".join(f"{k} {v:.0%}" for k, v in rev.items() if k in ("final", "outro")))
for name, ok, d in res:
    print(f"{name}: {'PASS' if ok else 'FAIL'}  {d}")
k = sum(ok for _, ok, _ in res)
print(("RESULT: PASS " if k == 4 else "RESULT: FAIL ") +
      f"{k}/4; final novelty current {cur['final']:.0%} revised {rev['final']:.0%}; revised outro {rev['outro']:.0%}; "
      f"bridge {cur['bridge']:.0%}; verse1 {cur['verse1']:.0%} verse2 {cur['verse2']:.0%}; max new/line in final {max(cur_lines['final'])}")
