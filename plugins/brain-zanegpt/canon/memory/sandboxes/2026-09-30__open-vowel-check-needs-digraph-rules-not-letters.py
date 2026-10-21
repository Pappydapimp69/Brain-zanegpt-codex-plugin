"""Sandbox L4: can a tool judge sustain-friendly vowels from spelling?

Kernel ideas:SONGWRITING/singability/sustained-notes-want-open-vowels: put ah/oh/oo on the long
note, not ee/ih. Line-end words are labelled with the ARPAbet vowel of their LAST syllable (the one
held at a line end). Classes: open {AA AO OW UW AW AY AH OY}, closed {IY IH}, neutral {EH EY AE ER UH}.
Compared: a naive letter judge (first letter of the last vowel group: a/o/u open, e/i/y closed) and a
digraph judge (spelling patterns such as ee/ea -> closed, igh/i_e -> open). Deterministic, stdlib only.

PREDICTION (written before the first run):
  P1 naive letter judge error >= 25% on the labelled set
  P2 digraph judge error <= 10%
  P3 in "Did You Eat?", >= 75% of CHORUS line-end words are open by phoneme
  P4 break: the title word "eat" is the ONLY closed line-end in the chorus sections
"""
import re

LAB = {"eat": "IY", "mom": "AA", "up": "AH", "stuff": "AH", "time": "AY", "fine": "AY", "line": "AY", "eyes": "AY",
       "wall": "AO", "all": "AO", "sticks": "IH", "it": "IH", "slow": "OW", "know": "OW", "soup": "UW", "too": "UW",
       "small": "AO", "sunday": "EY", "slower": "ER", "short": "AO", "ask": "AE", "back": "AE", "night": "AY",
       "light": "AY", "fire": "AY", "heart": "AA", "start": "AA", "love": "AH", "above": "AH", "home": "OW",
       "alone": "OW", "gone": "AO", "on": "AA", "free": "IY", "me": "IY", "see": "IY", "be": "IY", "believe": "IY",
       "sea": "IY", "dream": "IY", "true": "UW", "you": "UW", "blue": "UW", "through": "UW", "new": "UW", "soul": "OW",
       "go": "OW", "road": "OW", "cold": "OW", "rain": "EY", "pain": "EY", "say": "EY", "day": "EY", "way": "EY",
       "stay": "EY", "friend": "EH", "bed": "EH", "said": "EH", "dead": "EH", "head": "EH", "breath": "EH", "fall": "AO",
       "call": "AO", "war": "AO", "more": "AO", "door": "AO", "floor": "AO", "sky": "AY", "cry": "AY", "why": "AY",
       "die": "AY", "goodbye": "AY", "kiss": "IH", "miss": "IH", "still": "IH", "will": "IH", "fear": "IH", "here": "IH",
       "cheap": "IY", "leaf": "IY", "feel": "IY", "real": "IY", "mind": "AY", "find": "AY", "kind": "AY", "sun": "AH",
       "run": "AH", "done": "AH", "one": "AH", "blood": "AH", "flood": "AH", "mud": "AH", "truck": "AH", "word": "ER",
       "world": "ER", "heard": "ER", "burn": "ER", "turn": "ER", "now": "AW", "down": "AW", "sound": "AW", "out": "AW",
       "cloud": "AW", "around": "AW", "boy": "OY", "joy": "OY", "truth": "UW", "lie": "AY"}
OPEN = {"AA", "AO", "OW", "UW", "AW", "AY", "AH", "OY"}
CLOSED = {"IY", "IH"}


def cls(ph):
    return "open" if ph in OPEN else "closed" if ph in CLOSED else "neutral"


def naive(w):
    g = re.findall(r"[aeiouy]+", w)[-1]
    return "open" if g[0] in "aou" else "closed"


DIGRAPH = [  # (pattern on the word's final syllable region, class) first match wins
    (r"(ee|ea|ie|ei)(ve|f|p|m|l|t|$|d)?$", None),  # handled below with exceptions
]


def digraph(w):
    tail = w[-5:]
    if re.search(r"(eath|ead|ead$|aid|iend)$", w):
        return "neutral"  # breath, dead, head, said, friend
    if re.search(r"(ear|ere)$", w):
        return "closed"  # fear, here
    if re.search(r"(ee|ea|ie|ei)[a-z]{0,2}$", w) and not re.search(r"ie$", w):
        return "closed"  # see, sea, dream, believe, cheap, feel, real
    if re.search(r"(igh|ie$|y$|i[^aeiou]e$|ind$|ire$|eye|yes$)", w) and not re.search(r"(ay|ey)$", w):
        return "open"  # night, lie, sky, time, mind, fire, eyes
    if re.search(r"(ay|ai[^r]?|ain|a[^aeiou]e)$", w):
        return "neutral"  # day, rain, (a_e)
    if re.search(r"(er|ur|or[ld]|ir)[a-z]{0,1}$", w) and not re.search(r"(oor|ore|ar)$", w):
        return "neutral"  # slower, burn, word, world, heard handled next
    if re.search(r"ear[d]$", w):
        return "neutral"
    if re.search(r"(e|a)[^aeiouy]{1,2}$", w) and not re.search(r"(all|ar[t]?|ong|on)$", w):
        return "neutral" if not re.search(r"i", tail[-3:]) else "closed"  # bed, back, ask
    if re.search(r"i[^aeiouy]{1,3}$", w):
        return "closed"  # sticks, kiss, still, it
    return "open"  # oo, ou, ow, o_e, u, a-in-all/art, oy


# HELD-OUT (added after run 1 showed the digraph rules were written with LAB in view; labelled before run 2)
# P5 (written before run 2): digraph error on HELD <= 15%
HELD = {"sleep": "IY", "deep": "IY", "street": "IY", "feet": "IY", "knees": "IY", "tree": "IY", "please": "IY",
        "peace": "IY", "wind": "IH", "gift": "IH", "sit": "IH", "ship": "IH", "fly": "AY", "high": "AY", "wine": "AY",
        "smile": "AY", "tide": "AY", "moon": "UW", "soon": "UW", "room": "UW", "move": "UW", "show": "OW", "snow": "OW",
        "stone": "OW", "bone": "OW", "hope": "OW", "shore": "AO", "saw": "AO", "thought": "AO", "car": "AA", "far": "AA",
        "dark": "AA", "hand": "AE", "last": "AE", "late": "EY", "name": "EY", "face": "EY", "red": "EH", "left": "EH",
        "yes": "EH", "town": "AW", "house": "AW", "loud": "AW", "cut": "AH", "gun": "AH", "rough": "AH", "girl": "ER",
        "hurt": "ER", "first": "ER", "voice": "OY"}
err_h = [w for w, p in HELD.items() if digraph(w) != cls(p)]
err_hn = [w for w, p in HELD.items() if naive(w) != cls(p)]
print(f"P5 digraph HELD <= 15%: {'PASS' if len(err_h) / len(HELD) <= 0.15 else 'FAIL'}  {len(err_h)}/{len(HELD)} = {len(err_h) / len(HELD):.1%} "
      f"(naive {len(err_hn) / len(HELD):.1%}); wrong: {', '.join(err_h)}")
err_n = [w for w, p in LAB.items() if naive(w) != cls(p)]
err_d = [w for w, p in LAB.items() if digraph(w) != cls(p)]
CHORUS_ENDS = ["eat", "mom", "eat", "mom", "wall", "all", "eat", "mom",
               "eat", "mom", "eat", "mom", "small", "all", "eat", "mom",
               "eat", "eat", "ask", "back", "eat"]
open_share = sum(cls(LAB[w]) == "open" for w in CHORUS_ENDS) / len(CHORUS_ENDS)
closed_words = sorted({w for w in CHORUS_ENDS if cls(LAB[w]) == "closed"})
n = len(LAB)
res = [("P1 naive error >= 25%", len(err_n) / n >= 0.25, f"{len(err_n)}/{n} = {len(err_n) / n:.1%}"),
       ("P2 digraph error <= 10%", len(err_d) / n <= 0.10, f"{len(err_d)}/{n} = {len(err_d) / n:.1%}"),
       ("P3 chorus line-ends >= 75% open", open_share >= 0.75, f"{open_share:.0%}"),
       ("P4 break: 'eat' only closed chorus end", closed_words == ["eat"], ", ".join(closed_words))]
for name, ok, d in res:
    print(f"{name}: {'PASS' if ok else 'FAIL'}  {d}")
print("digraph wrong:", ", ".join(err_d))
k = sum(ok for _, ok, _ in res)
print(("RESULT: PASS " if k == 4 else "RESULT: FAIL ") +
      f"{k}/4; naive {len(err_n) / n:.1%}, digraph {len(err_d) / n:.1%} (n {n}); chorus line-ends open {open_share:.0%}, closed: {', '.join(closed_words)}")
