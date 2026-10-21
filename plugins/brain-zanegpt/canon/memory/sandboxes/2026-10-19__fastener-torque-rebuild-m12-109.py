# Own fixture: M12x1.75 class 10.9 (As 84.3 mm2, proof stress 830 MPa, yield 940 MPa), target 65% of proof, dry K 0.20.
# Prediction (before run): torque for 65% proof = 0.65*proof*K*d; oiled K 0.15 loads it to 86.7% of proof; heavy K 0.12 to 108.3% of proof
# (about 95.7% of yield, so under yield here, unlike the M10 8.8 case where the ratio pushed past it); scaling torque by K ratio restores 65%;
# on a K grid 0.14..0.26 step 0.01 the dry torque keeps the load inside 60-95% of proof for K in [0.14, 0.21] only (8 of 13 values).
As, proof_s, yield_s, d = 84.3e-6, 830e6, 940e6, 0.012
proof, yld = proof_s * As, yield_s * As
def torque(frac, K): return frac * proof * K * d
def load(T, K): return T / (K * d)
T = torque(0.65, 0.20)
print("proof kN", round(proof / 1e3, 1), "yield kN", round(yld / 1e3, 1), "dry torque Nm", round(T, 1))
r = {}
for name, K in (("dry", 0.20), ("oiled", 0.15), ("heavy", 0.12)):
    F = load(T, K); r[name] = (F / proof, F / yld); print(name, "K", K, "pct proof", round(100 * F / proof, 1), "pct yield", round(100 * F / yld, 1))
fixed = load(T * 0.15 / 0.20, 0.15) / proof
grid = [round(0.14 + 0.01 * i, 2) for i in range(13)]
inwin = [K for K in grid if 0.60 <= load(T, K) / proof <= 0.95]
print("scaled oiled torque pct proof", round(100 * fixed, 1), "in-window K values", len(inwin), "of", len(grid), "range", inwin[0], inwin[-1])
ok = (abs(r["oiled"][0] - 0.8667) < 0.001 and abs(r["heavy"][0] - 1.0833) < 0.001 and r["heavy"][1] < 1.0 and abs(fixed - 0.65) < 1e-9 and len(inwin) == 8)
print("RESULT:", "PASS" if ok else "FAIL",
      f"oiled {100*r['oiled'][0]:.1f}% proof, heavy {100*r['heavy'][0]:.1f}% proof but {100*r['heavy'][1]:.1f}% yield (under yield); K-ratio scaling restores {100*fixed:.1f}%; {len(inwin)}/13 K values in 60-95%")
