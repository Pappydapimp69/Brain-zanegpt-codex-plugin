# New domain FASTENER-TORQUE. Real scenario: an M10x1.5 class 8.8 bolt (stress area
# 58 mm^2, proof strength 580 MPa, yield about 640 MPa) tightened by torque wrench.
# Short form T = K * d * F (K = nut factor). A dry-steel torque is quoted for K = 0.20
# and a 75 percent of proof preload target.
# Prediction (before run): dry torque for 75 percent proof is about 50 N*m (published
# tables give 45-50); using that same torque with a lightly oiled bolt (K 0.15) lifts
# the preload to 100 percent of proof (33.6 kN); with a heavily lubricated bolt (K 0.12)
# it exceeds yield (>37 kN); scaling the torque by K_lube/K_dry restores the 75 percent
# target at every K tested (BREAK: K scatter of +-25 percent around 0.20 at the DRY
# torque still keeps preload within 60-95 percent of proof only for part of the range).
A, SP, SY, D = 58.0, 580.0, 640.0, 0.010
proof = A * SP            # N
yld = A * SY
target = 0.75 * proof
T_dry = 0.20 * D * target
print("proof %.1f kN yield %.1f kN target %.1f kN dry torque %.1f N*m" % (proof/1e3, yld/1e3, target/1e3, T_dry))
rows = {}
for name, K in (("dry", 0.20), ("oiled", 0.15), ("heavy", 0.12), ("plated", 0.17)):
    F = T_dry / (K * D)
    Ts = 0.20 * D * target * K / 0.20   # scaled torque = K*D*target
    F2 = Ts / (K * D)
    rows[name] = (F / proof, F / yld, F2 / proof)
    print("%-7s K=%.2f  spec-torque preload %.2f of proof (%.2f of yield)  scaled-torque %.2f of proof"
          % (name, K, F / proof, F / yld, F2 / proof))
scatter = [T_dry / (K * D) / proof for K in (0.15, 0.175, 0.20, 0.225, 0.25)]
inside = [0.60 <= x <= 0.95 for x in scatter]
print("dry-spec torque under K scatter 0.15..0.25 -> %s inside 60-95%%: %s" % (["%.2f" % x for x in scatter], inside))
ok = (abs(T_dry - 50.5) < 1.0 and abs(rows["oiled"][0] - 1.0) < 1e-9 and rows["heavy"][1] > 1.0
      and all(abs(v[2] - 0.75) < 1e-9 for v in rows.values()) and 0 < sum(inside) < len(inside))
print("RESULT: %s dry torque %.1f N*m; oiled bolt at dry torque reaches %.2f of proof, heavy lube %.2f of yield; scaled torque restores 0.75; K scatter keeps %d of 5 inside window"
      % ("PASS" if ok else "FAIL", T_dry, rows["oiled"][0], rows["heavy"][1], sum(inside)))
