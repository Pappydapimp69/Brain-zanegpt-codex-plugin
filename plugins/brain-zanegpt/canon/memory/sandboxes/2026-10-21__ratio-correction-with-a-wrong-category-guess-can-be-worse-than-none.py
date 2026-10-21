# Sandbox: ratio correction (scale by estimated/quoted constant) when the constant is GUESSED from a category.
# Prediction (before first run): for torque (K: dry .20, plated .17, oiled .15, heavy .12) a guessed K beats
# applying the dry value in 6 of 9 (true != dry, guess != dry) cases and loses in the other 3, the losses all
# being guesses further from truth than dry is (e.g. true plated, guess heavy: 29% vs 17.6%). For the cure base
# {meat 1000, meat+brine 1250, trimmed 800} guessing beats the nominal 1000-base in <=3 of 4 off-nominal cases.
K = {"dry": .20, "plated": .17, "oiled": .15, "heavy": .12}
def torque_cases():
    res = []
    for t, kt in K.items():
        if t == "dry": continue
        for g, kg in K.items():
            if g == "dry": continue
            guess_err = abs(kg / kt - 1); none_err = abs(K["dry"] / kt - 1)
            res.append((t, g, guess_err, none_err))
    return res
tc = torque_cases()
wins = [r for r in tc if r[2] < r[3]]; losses = [r for r in tc if r[2] >= r[3]]
print("S1 torque: guess beats dry in %d/%d; losses %s" % (len(wins), len(tc), [(r[0], r[1], round(r[2]*100, 1), round(r[3]*100, 1)) for r in losses]))
B = {"meat": 1000.0, "meat+brine": 1250.0, "trimmed": 800.0}
cc = []
for t, bt in B.items():
    if t == "meat": continue
    for g, bg in B.items():
        if g == "meat": continue
        cc.append((t, g, abs(bg / bt - 1), abs(B["meat"] / bt - 1)))
cw = [r for r in cc if r[2] < r[3]]
print("S2 cure base: guess beats nominal in %d/%d; cases %s" % (len(cw), len(cc), [(r[0], r[1], round(r[2]*100, 1), round(r[3]*100, 1)) for r in cc]))
# S3 BREAK: guess exactly right (diagonal) must always win
diag = all(abs(kt / kt - 1) < abs(K["dry"] / kt - 1) for t, kt in K.items() if t != "dry")
print("S3 (break) exact category guess always beats dry:", diag)

# S4 dilution (companion): plan picked from a GUESSED pipette constant a vs doing nothing (single 1000x step)
FLOOR, FINAL = 0.005, 1000.0
def e(V, a): return max(FLOOR, a / V)
def plan_error(fs, a):
    t = 0.0
    for f in fs:
        V = FINAL / f; t += e(V, a) + e(FINAL - V, a) * (1 - 1 / f)
    return t
PL = {"1x1000": [1000], "2x(10,100)": [10, 100], "2x32": [31.6227766] * 2, "3x10": [10] * 3}
AS = [0.0, 0.02, 0.05, 0.1, 0.2]
dw = dl = 0
for at in AS:
    for ag in AS:
        pick = min(PL, key=lambda k: plan_error(PL[k], ag))
        if plan_error(PL[pick], at) < plan_error(PL["1x1000"], at) - 1e-12: dw += 1
        elif plan_error(PL[pick], at) > plan_error(PL["1x1000"], at) + 1e-12: dl += 1
print("S4 dilution guessed-a plan beats single step in %d/25, worse in %d/25" % (dw, dl))
print("original prediction held:", len(wins) == 6 and len(losses) == 3 and len(cw) <= 3)
ok = dl >= 1 and len(losses) >= 1 and len(wins) > len(losses) and len(cw) < len(cc) and diag
print("RESULT: %s a category-guessed ratio beat doing nothing in %d/%d torque, %d/%d cure and %d/25 dilution cases; worse in %d torque and %d dilution cases" % ("PASS" if ok else "FAIL", len(wins), len(tc), len(cw), len(cc), dw, len(losses), dl))
