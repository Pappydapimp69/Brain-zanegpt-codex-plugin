"""Sandbox L6: casual ellipsis as a syllable-budget tool (CONVERSATION x SONGWRITING).

Kernels: ideas:CONVERSATION/ellipsis/casual-speech-drops-the-subject-and-auxiliary and
ideas:SONGWRITING/diction/write-the-reduced-form-you-will-sing, measured against the rushed-line
budget behind ideas:SONGWRITING/suno-prompting/hyphenate-words-to-slow-a-rushed-vocal-line.
Lines: the conversational lines of "Did You Eat?" as written (elliptical) and the same content in full
written form. Budget: 9 syllables per one-bar line (8 eighth notes + 1 pickup) at the song's tempo.
Syllables: the rule counter from loop 3 (13.8% held-out word error). Deterministic, stdlib only.

PREDICTION (written before the first run):
  P1 full forms exceed the budget on >= 40% of lines
  P2 elliptical forms exceed it on <= 20%
  P3 mean saving >= 1.5 syllables per line
  P4 break: at least one elliptical line is still over budget (ellipsis alone does not fix density)
"""
import re

V = "aeiouy"


def syl(word):
    w = re.sub(r"[^a-z']", "", word.lower())
    nt = 1 if re.search(r"[^aeiou]n't$", w) else 0
    w = w.replace("'", "")
    w = re.sub(r"qu", "q", w)
    if not w:
        return 0
    groups = list(re.finditer(r"[aeiouy]+", w))
    n = len(groups)
    if n == 0:
        return 1 + nt
    for g in groups:
        s, e, t = g.start(), g.end(), g.group()
        after = w[e:e + 2]
        for pair in ("ia", "io", "iu", "eo", "ua", "uo"):
            n += t.count(pair)
        if "ie" in t and after[:1] in ("t", "n") and not w.endswith("nd"):
            n += 1
        if "oe" in t and after[:1] in ("m", "t"):
            n += 1
        if len(t) >= 2 and t.endswith("i") and after == "ng":
            n += 1
        if re.search(r"[aeiou]y[aeiou]", t) or (t.startswith("y") and len(t) > 1 and s > 0):
            n += 1
    if re.search(r"ea$", w) or re.search(r"eate$", w):
        n += 1
    if re.match(r"^rea(c|li)", w) or re.match(r"^thea", w):
        n += 1
    if w.endswith("e") and len(w) > 1 and not re.search(r"[^aeiouy]le$", w) and w[-2] not in V:
        n -= 1
    elif re.search(r"[aeiouy][^aeiouy]le$", w) and not re.search(r"[^aeiouy][^aeiouy]le$", w):
        n -= 1
    if re.search(r"[^aeiouy]es$", w) and not re.search(r"(s|x|z|ch|sh|g|c)es$", w):
        n -= 1
    if re.search(r"[^aeiou]ed$", w) and not re.search(r"(t|d)ed$", w):
        n -= 1
    n -= len(re.findall(r"[^aeiouy]e(ly|ful|less|ness|ment|where)", w))
    return max(1, n) + nt


def line_syl(line):
    return sum(syl(t) for t in re.split(r"[\s\-]+", line) if re.search(r"[a-zA-Z]", t))


PAIRS = [
    ("Six-fifteen and my phone lights up", "It's six-fifteen and my phone lights up"),
    ("Same old bubble, same old stuff", "It's the same old bubble, the same old stuff"),
    ("Wear a coat. Is the bus on time?", "You should wear a coat. Is the bus on time?"),
    ("Mom, I'm seventeen, I'm fine", "Mom, I am seventeen, I am fine"),
    ("Twenty-three in a room where the door sticks", "I'm twenty-three in a room where the door sticks"),
    ("Rent's due Friday, so I'm skipping lunch for it", "Rent is due on Friday, so I am skipping lunch for it"),
    ("Phone lights up and I type it slow", "My phone lights up and I type it slowly"),
    ("Kinda. Had a coffee. Busy. You know.", "Kind of. I had a coffee. I'm busy. You know."),
    ("Said I'd come home Sunday", "I said that I would come home on Sunday"),
    ("Then I said next Sunday", "Then I said I'd come next Sunday"),
    ("Says there's a bowl with my name on it too", "She says there is a bowl with my name on it too"),
    ("Six-fifteen, my turn to ask", "It's six-fifteen, and it's my turn to ask"),
]
BUDGET = 9
rows = [(e, f, line_syl(e), line_syl(f)) for e, f in PAIRS]
over_f = [r for r in rows if r[3] > BUDGET]
over_e = [r for r in rows if r[2] > BUDGET]
saving = sum(r[3] - r[2] for r in rows) / len(rows)
for e, f, se, sf in rows:
    print(f"{se:>2} vs {sf:>2}  {e}")
res = [("P1 full over budget >= 40%", len(over_f) / len(rows) >= 0.40, f"{len(over_f)}/{len(rows)}"),
       ("P2 elliptical over budget <= 20%", len(over_e) / len(rows) <= 0.20, f"{len(over_e)}/{len(rows)}"),
       ("P3 mean saving >= 1.5", saving >= 1.5, f"{saving:.2f} syllables/line"),
       ("P4 break: an elliptical line still over", len(over_e) >= 1, "; ".join(r[0] for r in over_e) or "none")]
for name, ok, d in res:
    print(f"{name}: {'PASS' if ok else 'FAIL'}  {d}")
k = sum(ok for _, ok, _ in res)
print(("RESULT: PASS " if k == 4 else "RESULT: FAIL ") +
      f"{k}/4; over budget {BUDGET}: full {len(over_f)}/{len(rows)}, elliptical {len(over_e)}/{len(rows)}; "
      f"mean saving {saving:.2f}; still over: {len(over_e)}")
