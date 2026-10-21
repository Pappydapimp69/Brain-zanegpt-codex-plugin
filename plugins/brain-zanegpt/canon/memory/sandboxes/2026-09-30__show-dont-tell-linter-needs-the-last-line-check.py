# Composes: the sense-bound-detail kernel (flag a verse whose emotion words outnumber its sensory nouns)
# and the resist-explaining-the-resolution kernel (cut the line that states the meaning outright).
# PREDICTION (written before running): 8 hand-labelled verses (3 show, 2 tell, 2 show-then-explain,
# 1 show with a colour word that doubles as an emotion word).
# 1) the ratio linter alone passes both show-then-explain verses (they are image-heavy) -> 2 misses;
# 2) adding a last-line check (an emotion word or a stating phrase like "i realize", "that's when i knew",
#    "which means" in the final line) catches both, with no new false flags on the 3 show verses;
# 3) the lexicon counts "blue" in "the blue truck" as an emotion word; the verdict flips on that verse
#    only if emotion words then outnumber sensory nouns — predicted: it does not flip (1 emotion vs 3+ nouns).
# ADDED AFTER THE FIRST RUN (8/8, PASS): a break probe -- a show verse whose LAST line holds the colour
# word blue. Predicted before this second run: the last-line check falsely flags it.
import re
EMO = {"lonely", "sad", "broken", "heartbroken", "blue", "happy", "angry", "hurt", "love", "miss", "empty", "afraid", "lost", "regret"}
SENS = {"mug", "rack", "phone", "table", "coffee", "truck", "gravel", "porch", "light", "rain", "smoke", "sheets",
        "keys", "radio", "dust", "window", "boots", "screen", "sink", "dog", "door", "bed", "coat"}
STATE = r"\b(i realize|i realized|that's when i knew|which means|now i know|i finally see|and that's how i knew)\b"
V = [  # (lines, label) label True = tell / should be flagged
 (["your mug still in the rack", "the phone face-down on the table", "i let the coffee go cold", "the porch light on till two"], False),
 (["gravel in the truck bed", "your boots by the door", "the radio still on your station", "dust on the window"], False),
 (["the blue truck in the rain", "smoke on the porch", "keys in the sink", "the dog waits by the door"], False),
 (["i'm so lonely without you", "my heart is broken", "i miss you every day", "i'm lost and afraid"], True),
 (["i feel empty and sad", "the rain", "i regret it all", "love was never enough"], True),
 (["your mug still in the rack", "the phone face-down on the table", "the porch light on till two", "that's when i knew i was alone"], True),
 (["gravel in the truck bed", "your coat on the bed", "the keys in the door", "i realize i miss you"], True),
 (["the sheets still smell like smoke", "the radio on low", "your boots by the door", "i'm so lonely"], True),
]
def ratio_flag(lines):
    ws = re.findall(r"[a-z']+", " ".join(lines).lower())
    return sum(w in EMO for w in ws) > sum(w in SENS for w in ws)
def last_flag(lines):
    last = lines[-1].lower(); return bool(re.search(STATE, last)) or any(w in EMO for w in re.findall(r"[a-z']+", last))
r_ok = sum(ratio_flag(l) == t for l, t in V); c_ok = sum((ratio_flag(l) or last_flag(l)) == t for l, t in V)
explain_missed_by_ratio = sum(not ratio_flag(l) for l, _ in V[5:8])
show_false = sum(ratio_flag(l) or last_flag(l) for l, _ in V[:3])
for l, t in V: print(f"  tell={t!s:5} ratio {ratio_flag(l)!s:5} last-line {last_flag(l)!s:5}  / {l[-1]}")
print(f"ratio alone {r_ok}/8 (misses {explain_missed_by_ratio}/3 image-then-explain verses); ratio + last line {c_ok}/8; show verses falsely flagged {show_false}/3")
ok = explain_missed_by_ratio >= 2 and c_ok == 8 and show_false == 0
probe = ["smoke on the porch", "keys in the sink", "the dog waits by the door", "the blue truck in the rain"]
probe_flag = ratio_flag(probe) or last_flag(probe)
print(f"break probe (show verse ending on 'blue truck'): flagged {probe_flag}")
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" ratio alone {r_ok}/8 and passes {explain_missed_by_ratio}/3 image-then-explain verses; ratio + last-line check {c_ok}/8 with {show_false}/3 false flags; blue-truck verse not flipped mid-verse, but a show verse ending on it is falsely flagged: {probe_flag}")
