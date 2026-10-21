# Sandbox: a cure dose prepared by serial dilution. Two error sources compose:
#  (a) pipette floor error per step, max(0.5%, a/volume) (worst case, steps multiply)
#  (b) the quoted percent's hidden base (meat vs meat+brine), like a torque spec's hidden friction factor.
# Fix for (b) mirrors the torque lesson: scale the spec by assumed/actual ratio.
TOTAL_X = 1000.0        # total dilution factor
V_PICK  = 100.0         # uL transferred in each step (volume the floor divides by)
A_FLOOR = 0.02          # uL absolute pipette error
MEAT_G, BRINE_G = 1000.0, 250.0
NITRITE_PPM_OF_MEAT = 156.25  # 0.25 % cure, 6.25 % nitrite in cure -> ppm of MEAT mass
TOL = 0.10

def step_err(v): return max(0.005, A_FLOOR / v)
def dilution_worst(n, vol=V_PICK):
    # worst-case relative error of n balanced steps; per-step transfer volume shrinks with a smaller step ratio
    r = TOTAL_X ** (1.0 / n)
    v = max(vol / r if n > 1 else 1.0, 0.2)   # n=1 needs a 1 uL pick of a 1000x split; n>1 picks vol/r... 
    # use pick volume = V_PICK*(1/r)*r: keep pick = bulk/r with bulk 1000 uL
    pick = 1000.0 / r
    e = step_err(pick)
    return (1 + e) ** n - 1, pick

def dose_ppm(base_used, true_base):
    # dose computed as pct of base_used but ppm judged on meat mass
    return NITRITE_PPM_OF_MEAT * base_used / true_base * (MEAT_G / MEAT_G)

cases = {}
for n in (1, 2, 3):
    w, pick = dilution_worst(n)
    cases[n] = w
    print(f"steps={n} pick={pick:.1f}uL worst pipette error={w*100:.2f}%")

# hidden base: spec quoted on meat+brine (1250 g) but applied to meat (1000 g), or the reverse
over  = (MEAT_G + BRINE_G) / MEAT_G - 1       # +25 % if dose computed on total but ppm judged on meat
under = MEAT_G / (MEAT_G + BRINE_G) - 1       # -20 %
print(f"base mismatch over={over*100:.1f}% under={under*100:.1f}%")

best_dil = min(cases.values()); worst_dil = max(cases.values())
rows = []
for label, base_err, corrected in (("right base", 0.0, False), ("wrong base, uncorrected", over, False), ("wrong base, ratio-scaled", over, True)):
    resid = 0.0 if corrected else base_err
    for n in (1, 2):
        tot = abs(resid) + cases[n]
        rows.append((label, n, tot, tot <= TOL))
        print(f"{label:26s} steps={n} total worst error={tot*100:.2f}% within {int(TOL*100)}%: {tot<=TOL}")

spread_dil = worst_dil - best_dil
base_shift = abs(over)
ok_dominates = base_shift > 5 * min(cases[1], cases[2])
# can the best dilution choice rescue a wrong base?
rescue = any(r[3] for r in rows if r[0]=="wrong base, uncorrected")
corrected_ok = all(r[3] for r in rows if r[0]=="wrong base, ratio-scaled")
# BREAK scenario: a tight tolerance (1.5%) where pipette error matters after the base is corrected
tight = [(n, cases[n] <= 0.015) for n in (1, 2, 3)]
print("break (1.5% tol after ratio-scaling):", tight)
res = ok_dominates and (not rescue) and corrected_ok
print(("RESULT: PASS" if res else "RESULT: FAIL"),
 f"base mismatch {base_shift*100:.0f}% vs pipette {cases[1]*100:.2f}/{cases[2]*100:.2f}% (1/2 steps); wrong base rescued by step choice: {rescue}; ratio-scaled within tol: {corrected_ok}; at 1.5% tol only {[n for n,o in tight if o]} steps pass")
