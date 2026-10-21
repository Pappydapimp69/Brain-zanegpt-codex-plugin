"""Sandbox: does the in/out-group empathy GAP, not the LEVEL, drive passive-harm endorsement?
Deterministic grid, no RNG. Agent has affective resonance toward in-group (e_in) and out-group (e_out),
plus a cognitive channel (understanding, independent of resonance).
Endorse passive harm to out-group iff  e_in*BENEFIT > e_out*HARM + FIXED_COST_OF_ACTING.
Helper-distress: distress = resonance * suffering; compassion motive = warmth (not depleted).
"""
B, H = 1.0, 1.0
def endorse(e_in, e_out, fixed=0.0):  # kernel: parochial gap
    return e_in * B > e_out * H + fixed
grid = [round(0.1 * i, 1) for i in range(1, 10)]
def rate(pairs, fixed=0.0):
    return sum(endorse(a, b, fixed) for a, b in pairs) / len(pairs)

# S1: same MEAN empathy (0.5), vary the split. Gap predicts endorsement.
s1 = {g: endorse(0.5 + g, 0.5 - g) for g in (-0.3, -0.1, 0.0, 0.1, 0.3)}
print("S1 endorse by gap(in-out)/2:", s1)
ok1 = [g for g, v in s1.items() if v] == [0.1, 0.3]

# S2: raise general empathy by scaling both channels; ratio fixed -> decision unchanged
base = [(a, b) for a in grid for b in grid]
r_lo = rate([(a * 0.5, b * 0.5) for a, b in base])
r_hi = rate([(a * 1.0, b * 1.0) for a, b in base])
r_x = rate([(a * 2.0, b * 2.0) for a, b in base])
print("S2 rate at scale .5/1/2:", r_lo, r_hi, r_x)
ok2 = r_lo == r_hi == r_x

# S3 (BREAK): add a fixed cost of acting; now general level matters (higher level beats the cost)
fixed = 0.2
pairs = [(0.6, 0.4), (0.5, 0.4), (0.7, 0.5)]
lo = rate([(a * 0.5, b * 0.5) for a, b in pairs], fixed)
hi = rate([(a * 2.0, b * 2.0) for a, b in pairs], fixed)
print("S3 fixed-cost endorse rate low/high general empathy:", lo, hi)
ok3 = lo < hi  # scale-invariance FAILS: raising level changed outcome (and raised endorsement here)

# S4: helper burnout: distress ~ resonance*suffering, compassion ~ warmth. Distress-only vs compassion shift.
def helper(res, warmth, suffering=1.0, rounds=5):
    cap, helped = 1.0, 0
    for _ in range(rounds):
        cap -= 0.15 * res * suffering  # distress depletes
        if cap > 0 and warmth > 0.3: helped += 1
        cap += 0.05 * warmth           # compassion restores
    return round(cap, 2), helped
print("S4 distress(res=1,warm=.2):", helper(1.0, 0.2), " less caring(res=.3,warm=.2):", helper(0.3, 0.2),
      " compassion(res=.3,warm=1):", helper(0.3, 1.0))
ok4 = helper(0.3, 1.0)[1] > helper(1.0, 0.2)[1] and helper(0.3, 1.0)[1] > helper(0.3, 0.2)[1]

# S5: double dissociation affective vs cognitive
def agent(aff, cog, suffering=1.0):
    return {"distress": aff * suffering, "reads_state": cog >= 0.5}
a_les, c_les = agent(0.0, 1.0), agent(1.0, 0.0)
print("S5 affective lesion:", a_les, " cognitive lesion:", c_les)
ok5 = a_les["distress"] == 0 and a_les["reads_state"] and c_les["distress"] > 0 and not c_les["reads_state"]

allok = all([ok1, ok2, ok3, ok4, ok5])
print("RESULT: %s gap-not-level holds in S1,S2,S4,S5; breaks (level matters) when a fixed action cost exists in S3 %s"
      % ("PASS" if allok else "FAIL", [ok1, ok2, ok3, ok4, ok5]))
