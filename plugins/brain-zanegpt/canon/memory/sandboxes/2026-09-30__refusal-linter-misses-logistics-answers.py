# Composes: the preference-organization kernel (a refusal comes delayed, prefaced and accounted; flag a
# refusal with none of those), the um-announces-a-longer-delay kernel (um marks a longer delay than uh) and
# the practical-language subtext kernel (a logistics line answers the refused question).
# PREDICTION (written before running): 14 hand-labelled reply turns (6 padded refusals, 2 bare refusals,
# 2 logistics refusals, 2 plain acceptances, 2 hesitant acceptances).
# 1) a marker-count classifier (pause, well/uh/um, token agreement, account) calls a turn a refusal
#    when it has 2+ markers: finds the 6 padded refusals, and falsely calls both hesitant acceptances refusals;
# 2) it misses the 2 bare refusals and both logistics refusals (0/4);
# 3) adding a polarity check (an explicit no/can't/won't, or yes/sure/okay) fixes the hesitant acceptances
#    and the bare refusals but still misses both logistics refusals: those need the question they answer;
# FIRST RUN note: the RESULT summary text was hard-coded to 0/2 and is now computed from the run.
# 4) delay scoring with um = 2, uh = 1 ranks every um-prefaced refusal above every uh-prefaced one.
import re
MARK = {"pause": r"^\.\.\.|\.\.\.", "preface": r"\b(well|uh|um|i mean)\b", "token": r"\b(yeah|sure|i'd love to)\b,? (but|it's just)",
        "account": r"\b(because|it's just|i've got|i have to|work)\b"}
NEG = r"\b(no|can't|cannot|won't|not really|i don't think)\b"; POS = r"\b(yes|sure thing|okay|ok|absolutely|i'd love to)\b(?!,? but)"
T = [  # (reply, label) labels: R refusal, A acceptance
 ("... well, i'd love to, but i've got work early", "R"), ("um... i mean, i don't think i can, it's just been a long week", "R"),
 ("uh, yeah, but i have to be up at five", "R"), ("well... no, not really, because of the kids", "R"),
 ("um, i can't, work", "R"), ("uh... i mean, i'd love to, but not tonight", "R"),
 ("no.", "R"), ("i won't.", "R"),
 ("i'll need the car back by six.", "R"), ("the dishes won't wash themselves.", "R"),
 ("yes!", "A"), ("sure thing.", "A"),
 ("um... well, okay, i mean, yes", "A"), ("uh, yeah, it's just a surprise, okay", "A")]
def markers(t): return sum(bool(re.search(p, t)) for p in MARK.values())
def marker_cls(t): return "R" if markers(t) >= 2 else "A"
def polarity_cls(t):
    if re.search(NEG, t): return "R"
    if re.search(POS, t): return "A"
    return marker_cls(t)
m_ok = sum(marker_cls(t) == l for t, l in T); p_ok = sum(polarity_cls(t) == l for t, l in T)
def grp(i): return "padded" if i < 6 else "bare" if i < 8 else "logistics" if i < 10 else "plain-yes" if i < 12 else "hesitant-yes"
for i, (t, l) in enumerate(T): print(f"  {grp(i):12} {l} markers {markers(t)} marker->{marker_cls(t)} polarity->{polarity_cls(t)}  {t}")
miss_log_marker = sum(marker_cls(t) != "R" for t, _ in T[8:10]); miss_log_pol = sum(polarity_cls(t) != "R" for t, _ in T[8:10])
def delay(t): return 2 * len(re.findall(r"\bum\b", t)) + len(re.findall(r"\buh\b", t)) + 2 * t.count("...")
um_r = [delay(t) for t, l in T[:6] if "um" in t.split(",")[0]]; uh_r = [delay(t) for t, l in T[:6] if t.startswith("uh")]
print(f"marker classifier {m_ok}/14; polarity+marker {p_ok}/14; logistics refusals missed marker {miss_log_marker}/2 polarity {miss_log_pol}/2")
print(f"delay scores um-prefaced {um_r} uh-prefaced {uh_r}")
ok = miss_log_marker == 2 and miss_log_pol == 2 and p_ok == 12 and min(um_r) > max(uh_r)
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" markers alone {m_ok}/14, with polarity {p_ok}/14, logistics refusals caught {2-miss_log_marker}/2 by markers and {2-miss_log_pol}/2 with polarity (the polarity hit is the word won't about dishes, not a refusal cue); um-prefaced delay {um_r} vs uh {uh_r}")
