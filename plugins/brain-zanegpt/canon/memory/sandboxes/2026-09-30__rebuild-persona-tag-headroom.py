# Rebuild of: a persona pre-spends the 5-8 style-tag band (5-tag persona leaves 3 free); remove a clashing persona
# tag instead of adding an opposite one. Own fixture: 5 axes, persona tags chosen by me; conflict = two values on a
# single-valued axis (mood, tempo, vocal). The band limits (5..8) are the kernel's premise and are NOT tested here.
BAND_LO, BAND_HI = 5, 8
SINGLE = {"mood", "tempo", "vocal"}
def conflicts(tags):
    by = {}
    for ax, v in tags: by.setdefault(ax, set()).add(v)
    return sum(len(v) - 1 for ax, v in by.items() if ax in SINGLE and len(v) > 1)
persona = [("vocal", "breathy female"), ("mood", "melancholic"), ("tempo", "slow"), ("genre", "indie folk"), ("inst", "acoustic guitar")]
want = [("mood", "uplifting"), ("inst", "strings"), ("genre", "dream pop"), ("inst", "piano")]
print("persona tags", len(persona), "headroom vs band top", BAND_HI - len(persona), "vs band bottom", BAND_LO - len(persona))
add = persona + want
print("ADD all wanted:", len(add), "tags, conflicts", conflicts(add), "over band top", len(add) > BAND_HI)
repl = [t for t in persona if t[0] != "mood"] + want
print("REPLACE clashing mood:", len(repl), "tags, conflicts", conflicts(repl), "within band", BAND_LO <= len(repl) <= BAND_HI)
big = persona + [("inst", "pads"), ("genre", "ambient"), ("inst", "synth")]
print("BREAK 8-tag persona+3:", len(big), "tags headroom now", BAND_HI - len(big), "; persona of 3 tags leaves", BAND_HI - 3)
ok = BAND_HI - len(persona) == 3 and conflicts(add) == 1 and conflicts(repl) == 0 and len(add) > BAND_HI and len(repl) <= BAND_HI
print("RESULT: %s 5-tag persona leaves %d free at band top (%d at band bottom); adding an opposite mood gives %d tags/%d conflict, replacing gives %d tags/%d conflicts" % (
    "PASS" if ok else "FAIL", BAND_HI - len(persona), BAND_LO - len(persona), len(add), conflicts(add), len(repl), conflicts(repl)))
