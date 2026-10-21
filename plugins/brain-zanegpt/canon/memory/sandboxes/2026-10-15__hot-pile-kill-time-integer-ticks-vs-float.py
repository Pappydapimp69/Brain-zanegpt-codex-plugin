# Composes weedy-material-needs-a-turned-hot-pile (seeds die after a hot spell) with the brainwork
# integer-tick rule (float time accumulation drifts at exact boundaries).
import math
KILL = 3.0
def float_kills(step, spell):            # accumulate float time while hot
    hot = 0.0
    for _ in range(round(spell/step)): hot += step
    return hot >= KILL
def round_ticks_kills(step, spell):      # integer ticks, but the spell is ROUNDED to whole ticks
    return round(spell/step) >= round(KILL/step)
def floor_ticks_kills(step, spell):      # integer ticks, completed ticks only (floor, small eps)
    return math.floor(spell/step + 1e-9) >= math.floor(KILL/step + 1e-9)
steps = [0.1, 0.05, 0.2, 0.25, 0.5, 1/3, 0.125, 0.01]
tests = [(3.0, True), (2.9, False), (2.8, False), (3.1, True)]   # (hot spell days, should kill)
res = {}
for name, fn in (("float", float_kills), ("round-ticks", round_ticks_kills), ("floor-ticks", floor_ticks_kills)):
    wrong = [(s, sp) for s in steps for sp, want in tests if fn(s, sp) != want]
    res[name] = wrong
    print(name, "wrong", len(wrong), "of", len(steps)*len(tests), wrong[:6])
whole = all(floor_ticks_kills(1.0, float(d)) == (d >= 3) for d in range(0, 7))
print("whole-day spells with floor ticks all right:", whole)
ok = len(res["floor-ticks"]) == 0 and len(res["float"]) > 0 and len(res["round-ticks"]) > 0 and whole
print(("RESULT: PASS" if ok else "RESULT: FAIL"), "wrong verdicts of 32: float %d, round-ticks %d, floor-ticks %d"%(len(res["float"]), len(res["round-ticks"]), len(res["floor-ticks"])))
