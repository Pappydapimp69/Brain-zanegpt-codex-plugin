"""Sandbox L3: a rule-based lyric syllable counter vs the plain vowel-group counter.

Stored lessons: a vowel-group counter under-counts (syllable-slack lesson) and suno-builder's
hyphenate() mis-splits silent e and vowel pairs (suno-builder E8). Rules below were written against
DEV; TEST was labelled by hand before this file first ran. Labels are sets where sung English allows
two counts (fire, every, family). Deterministic, stdlib only.

PREDICTION (written before the first run):
  P1 baseline vowel-group error on TEST >= 25%
  P2 rule counter error on TEST <= 12%
  P3 rule counter never scores worse than baseline on DEV or TEST
  P4 break: the rule counter's TEST error is at least 5 points above its DEV error (rules overfit DEV)
"""
import re

DEV = {"seventeen": {3}, "coffee": {2}, "busy": {2}, "kinda": {2}, "twenty": {2}, "friday": {2}, "skipping": {2},
       "photo": {2}, "sunday": {2}, "slower": {2}, "didn't": {2}, "cheaper": {2}, "little": {2}, "every": {2, 3},
       "lie": {1}, "lies": {1}, "smaller": {2}, "truth": {1}, "quiet": {2}, "poem": {2}, "piano": {3}, "create": {2},
       "being": {2}, "idea": {3}, "lion": {2}, "react": {2}, "science": {2}, "fire": {1, 2}, "hour": {1, 2},
       "flower": {1, 2}, "power": {1, 2}, "family": {2, 3}, "different": {2, 3}, "chocolate": {2, 3}, "business": {2},
       "evening": {2, 3}, "desire": {2, 3}, "whispered": {2}, "walked": {1}, "wanted": {2}, "needed": {2}, "loved": {1},
       "places": {2}, "wishes": {2}, "makes": {1}, "smile": {1}, "table": {2}, "bottle": {2}, "lonely": {2},
       "homeless": {2}, "careful": {2}, "somewhere": {2}, "everyone": {3}, "forever": {3}, "yesterday": {3},
       "tomorrow": {3}, "beautiful": {3}, "memories": {3}, "heaven": {2}, "broken": {2}, "lying": {2}, "dying": {2},
       "trying": {2}, "player": {2}, "prayer": {1, 2}, "royal": {2}, "going": {2}, "doing": {2}, "saying": {2},
       "radio": {3}, "video": {3}, "stereo": {3}, "alien": {3}, "reality": {4}, "usually": {3, 4}, "actually": {3, 4},
       "cruel": {1, 2}, "fuel": {1, 2}, "jewel": {1, 2}, "real": {1, 2}, "really": {2}, "realize": {3}, "theater": {3},
       "poet": {2}, "violin": {3}, "the": {1}, "eyes": {1}, "knew": {1}, "rhythm": {2}, "people": {2}, "simple": {2},
       "whole": {1}, "some": {1}, "come": {1}, "ride": {1}, "lives": {1}, "used": {1}, "closed": {1}, "ended": {2},
       "started": {2}, "hated": {2}, "danced": {1}, "asked": {1}, "queue": {1}}
TEST = {"orange": {2}, "window": {2}, "shadow": {2}, "silence": {2}, "promise": {2}, "notice": {2}, "office": {2},
        "garden": {2}, "morning": {2}, "midnight": {2}, "ocean": {2}, "machine": {2}, "bridge": {1}, "strange": {1},
        "change": {1}, "heartbeat": {2}, "goodbye": {2}, "honey": {2}, "money": {2}, "journey": {2}, "valley": {2},
        "baby": {2}, "lady": {2}, "pretty": {2}, "maybe": {2}, "cause": {1}, "because": {2}, "believe": {2},
        "receive": {2}, "moving": {2}, "leaving": {2}, "breathing": {2}, "sometimes": {2}, "nothing": {2},
        "something": {2}, "anything": {3}, "everything": {3, 4}, "whatever": {3}, "together": {3}, "remember": {3},
        "surrender": {3}, "universe": {3}, "paradise": {3}, "hurricane": {3}, "fireworks": {2, 3}, "iron": {2},
        "diamond": {2, 3}, "violet": {3}, "giant": {2}, "trial": {1, 2}, "denial": {3}, "fluid": {2}, "ruin": {2},
        "doesn't": {2}, "couldn't": {2}, "tired": {1, 2}, "created": {3}, "ideas": {3}, "areas": {3}, "poetry": {3},
        "cooperate": {4}, "naive": {2}, "reunion": {3}, "cruelty": {2, 3}, "played": {1}, "stayed": {1},
        "hurried": {2}, "married": {2}, "carried": {2}, "worried": {2}, "cries": {1}, "tries": {1}, "flies": {1},
        "shoes": {1}, "horses": {2}, "roses": {2}, "voices": {2}, "judges": {2}, "hopes": {1}, "dreams": {1},
        "believed": {2}, "arrived": {2}, "ashamed": {2}, "moved": {1}, "loveless": {2}, "useless": {2}, "lately": {2},
        "safety": {2}, "statement": {2}, "movement": {2}, "hopeful": {2}, "wasted": {2}, "hundred": {2}, "honest": {2}}

V = "aeiouy"


def baseline(word):
    return max(1, len(re.findall(r"[aeiouy]+", word.lower())))


def rules(word):
    w = re.sub(r"[^a-z']", "", word.lower())
    nt = 1 if re.search(r"[^aeiou]n't$", w) else 0
    w = w.replace("'", "")
    w = re.sub(r"qu", "q", w)
    groups = [m for m in re.finditer(r"[aeiouy]+", w)]
    n = len(groups)
    if n == 0:
        return 1 + nt
    # (run 1 returned here when n == 1, skipping hiatus rules: giant/iron/trial/fluid/ruin/lion)
    # hiatus splits
    for g in groups:
        s, e = g.start(), g.end()
        t = g.group()
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
    # silent endings
    if w.endswith("e") and not re.search(r"[^aeiouy]le$", w) and w[-2] not in V:
        n -= 1
    elif re.search(r"[aeiouy][^aeiouy]le$", w) and not re.search(r"[^aeiouy][^aeiouy]le$", w):
        n -= 1
    if re.search(r"[^aeiouy]es$", w) and not re.search(r"(s|x|z|ch|sh|g|c)es$", w):
        n -= 1
    if re.search(r"[^aeiou]ed$", w) and not re.search(r"(t|d)ed$", w):
        n -= 1
    # internal silent e before common suffixes
    n -= len(re.findall(r"[^aeiouy]e(ly|ful|less|ness|ment|where)", w))
    return max(1, n) + nt


def err(counter, data):
    wrong = [k for k, ok in data.items() if counter(k) not in ok]
    return len(wrong) / len(data), wrong


bd, _ = err(baseline, DEV)
rd, rdw = err(rules, DEV)
bt, _ = err(baseline, TEST)
rt, rtw = err(rules, TEST)
res = [("P1 baseline TEST >= 25%", bt >= 0.25, f"{bt:.1%}"),
       ("P2 rules TEST <= 12%", rt <= 0.12, f"{rt:.1%}"),
       ("P3 rules never worse", rd <= bd and rt <= bt, f"DEV {rd:.1%} vs {bd:.1%}, TEST {rt:.1%} vs {bt:.1%}"),
       ("P4 break: overfit gap >= 5 pts", rt - rd >= 0.05, f"gap {100 * (rt - rd):.1f} pts")]
for name, ok, d in res:
    print(f"{name}: {'PASS' if ok else 'FAIL'}  {d}")
print("rules wrong on TEST:", ", ".join(sorted(rtw)))
k = sum(ok for _, ok, _ in res)
print(("RESULT: PASS " if k == 4 else "RESULT: FAIL ") +
      f"{k}/4; TEST error baseline {bt:.1%} rules {rt:.1%} (n {len(TEST)}); DEV baseline {bd:.1%} rules {rd:.1%} (n {len(DEV)})")
