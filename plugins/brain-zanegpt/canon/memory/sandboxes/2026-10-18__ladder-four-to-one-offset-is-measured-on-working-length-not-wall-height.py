# Seed: LADDER-SAFETY. Claim: the 1-in-4 setback is taken on the ladder's WORKING length (foot to the support point),
# not on the wall height reached and not on the full rail length; the three readings give different angles.
import math
def ang(base, hyp): return math.degrees(math.acos(base / hyp))
L = 24.0                 # full rail length ft, rails extend 3 ft above the landing => support point at working length 21
EXT = 3.0
W = L - EXT              # working length (foot to landing edge along the rail)
# Reading A: base = W/4 (working length)
bA = W / 4; hA = math.sqrt(W**2 - bA**2); aA = ang(bA, W)
# Reading B: base = full rail length / 4 (rail length misread as working length)
bB = L / 4; aB = ang(bB, W) if bB < W else float("nan")
hB = math.sqrt(W**2 - bB**2)
# Reading C: base = wall height / 4, solved so base = H/4 and sqrt(base^2+H^2) = W  => H = 4b, W^2 = 17 b^2
bC = W / math.sqrt(17); hC = 4 * bC; aC = ang(bC, W)
print(f"A base=W/4: base {bA:.2f} ft height {hA:.2f} ft angle {aA:.2f}")
print(f"B base=L/4: base {bB:.2f} ft height {hB:.2f} ft angle {aB:.2f}")
print(f"C base=H/4: base {bC:.2f} ft height {hC:.2f} ft angle {aC:.2f}")
# BREAK: same-angle claim for every length? angle must be length-independent for A, depend on EXT for B
angs = {l: (ang((l - EXT) / 4, l - EXT), ang(l / 4, l - EXT)) for l in (12, 16, 20, 24, 32, 40)}
for l, (a, b) in angs.items(): print(f"L={l}: A {a:.2f}  B {b:.2f}")
A_const = max(a for a, _ in angs.values()) - min(a for a, _ in angs.values()) < 1e-9
B_spread = max(b for _, b in angs.values()) - min(b for _, b in angs.values())
# sensitivity: 1 ft base error on the 24 ft ladder
d = ang(bA - 1, W) - aA, ang(bA + 1, W) - aA
print("1 ft base error shifts angle by %.2f / %.2f deg" % d)
# run 1 FAIL: I predicted the rail-length base over-steepens; it adds base so it flattens the ladder (sign fixed in run 2)
ok = abs(aA - 75.52) < 0.01 and abs(aC - 75.96) < 0.01 and A_const and B_spread > 2 and aB < aA - 2 and abs(d[0]) > 1.5
print("RESULT: %s A angle %.2f const across 6 lengths; B (rail-length base) %.2f..%.2f varies %.1f deg and sits shallower by %.1f; C (height/4) %.2f; 1ft base error %.1f deg"
      % ("PASS" if ok else "FAIL", aA, min(b for _, b in angs.values()), max(b for _, b in angs.values()), B_spread, aA - aB, aC, abs(d[0])))
