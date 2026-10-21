# Sandbox: benign-violation + escalation-needs-matching-distance + rule-card-first.
# Beat is funny iff severity>=1 (violation) AND severity<=distance (benign reason)
# AND the frame/ceiling was in place before the beat. Sketch score = sum of severity of funny beats.
import itertools
BEATS = 6
def run(schedule, distance, ceiling, card_first):
    score = funny = 0
    for i, sev in enumerate(schedule):
        if ceiling is not None:
            sev = min(sev, ceiling)          # rule card clamps what the writer may write
        framed = card_first or i > 0         # late card: opener beat is unframed
        if 1 <= sev <= distance and framed:
            funny += 1; score += sev
    return score, funny
go_big = [1, 2, 3, 4, 5, 5]
mild   = [1, 1, 2, 2, 2, 2]
flat   = [3] * BEATS
scen = {}
for d in (2, 3, 4):
    scen[f"d{d}/gobig-nocard"]      = run(go_big, d, None, True)
    scen[f"d{d}/mild-nocard"]       = run(mild, d, None, True)
    scen[f"d{d}/gobig-card=d-first"] = run(go_big, d, d, True)
    scen[f"d{d}/gobig-card=d-late"]  = run(go_big, d, d, False)
# BREAK case: ceiling set one above the framing distance
    scen[f"d{d}/gobig-card=d+1"]    = run(go_big, d, d + 1, True)
for k, v in scen.items(): print(k, v)
ok = True
for d in (2, 3, 4):
    a = scen[f"d{d}/gobig-card=d-first"][0]
    ok &= a >= scen[f"d{d}/gobig-nocard"][0] and a >= scen[f"d{d}/mild-nocard"][0]
    ok &= scen[f"d{d}/gobig-card=d-late"][0] < a            # card must come first
    ok &= scen[f"d{d}/gobig-card=d+1"][1] < scen[f"d{d}/gobig-card=d-first"][1] or d >= 5
print("RESULT: %s card-at-ceiling=distance first beats no-card go-big, mild, late card and ceiling d+1 at d=2,3,4" % ("PASS" if ok else "FAIL"))
