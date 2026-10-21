"""Sailing sandbox (stdlib, deterministic): apparent wind = true wind minus boat velocity.

Real scenario: a dinghy on a beam reach in 12 kn true wind (TWS) at 6 kn boat speed (BS) is hit by
a 16 kn puff; the boat then accelerates to 7.5 kn. Separately, a fast boat (iceboat, foiler) at
30 kn on a true broad reach (TWA 135).
Vector model: boat moves along +x at BS. True wind comes FROM angle TWA off the bow.
Apparent wind angle AWA = atan2(TWS sin TWA, TWS cos TWA + BS); AWS = |that vector|.
Assumption (named): flat water, no leeway, no wind gradient with height; boat speeds are given,
not derived from a polar.
PREDICTION (written before running):
  beam reach TWA 90, TWS 12, BS 6 -> AWA 63.4 deg, AWS 13.4 kn;
  puff to TWS 16 at the same BS -> AWA moves AFT to about 69.4 deg (so the sailor eases / can head up);
  boat then accelerates to 7.5 kn -> AWA moves forward again to about 64.9 deg (sheet back in);
  dead run TWA 180, BS 6 -> AWS 6 (half the true wind) and the puff does NOT move AWA (stays 180);
  fast boat TWA 135, BS 30 -> AWA about 21.5 deg: trimmed close-hauled while 'running' downwind;
  the AWA crosses the beam (90) at TWA 135 when BS > TWS*cos(45) = 8.49 kn.
Rule under test: trim to the apparent wind (telltales), not the true wind; a puff frees you (AWA aft),
acceleration heads you (AWA forward). BREAK case: a dead run, where a puff cannot move AWA at all.
"""
import math


def apparent(tws, twa_deg, bs):
    t = math.radians(twa_deg)
    y = tws * math.sin(t)
    x = tws * math.cos(t) + bs
    return math.degrees(math.atan2(y, x)), math.hypot(x, y)


checks = []
a0, s0 = apparent(12, 90, 6)
a1, s1 = apparent(16, 90, 6)
a2, s2 = apparent(16, 90, 7.5)
print(f"beam reach 12kn/BS6: AWA {a0:.1f} AWS {s0:.1f}; puff 16kn: AWA {a1:.1f} AWS {s1:.1f}; "
      f"accelerated BS7.5: AWA {a2:.1f} AWS {s2:.1f}")
checks.append(("beam reach AWA 63.4", abs(a0 - 63.4) < 0.1 and abs(s0 - 13.4) < 0.1))
checks.append(("puff moves AWA aft", a1 > a0 + 5))
checks.append(("acceleration moves AWA forward", a2 < a1 - 4))

# sweep: sign of the puff effect across TWA (close-hauled to broad reach)
aft_count, total = 0, 0
for twa in range(30, 180, 5):
    bs = 6.0
    base, _ = apparent(12, twa, bs)
    puff, _ = apparent(16, twa, bs)
    acc, _ = apparent(12, twa, bs + 1.5)
    total += 1
    if puff > base and acc < base:
        aft_count += 1
print(f"TWA 30..175: puff aft AND acceleration forward at {aft_count}/{total} angles")
checks.append(("puff-aft / accel-forward holds at every TWA 30..175", aft_count == total))

# BREAK: dead run
r0, rs0 = apparent(12, 180, 6)
r1, rs1 = apparent(16, 180, 6)
print(f"dead run: AWA {r0:.1f} AWS {rs0:.1f}; puff AWA {r1:.1f} AWS {rs1:.1f}")
checks.append(("dead run: AWS halves and the puff leaves AWA at 180", abs(rs0 - 6) < 1e-9 and r0 == r1 == 180.0))

# fast boat
f0, fs0 = apparent(12, 135, 30)
cross = 12 * math.cos(math.radians(45))
just_below, _ = apparent(12, 135, cross - 0.01)
just_above, _ = apparent(12, 135, cross + 0.01)
print(f"fast boat TWA135 BS30: AWA {f0:.1f} AWS {fs0:.1f}; AWA crosses beam at BS {cross:.2f} "
      f"({just_below:.2f} -> {just_above:.2f})")
checks.append(("fast boat close-hauled on a broad reach", abs(f0 - 21.5) < 0.3))
checks.append(("beam crossing at BS = TWS cos45", just_below > 90 > just_above))

# a sailor who trims to TRUE wind: trim error in degrees on the beam reach and fast boat
print(f"trim error if set to true wind: beam reach {90 - a0:.1f} deg, fast boat {135 - f0:.1f} deg")

p = sum(ok for _, ok in checks)
for n, ok in checks:
    print(("ok   " if ok else "FAIL ") + n)
print(f"RESULT: {'PASS' if p == len(checks) else 'FAIL'} {p}/{len(checks)}; beam reach AWA {a0:.1f}, puff {a1:.1f} (aft), "
      f"accel {a2:.1f} (fwd); dead run AWS {rs0:.1f}, puff AWA unchanged {r1:.0f}; fast boat TWA135 BS30 AWA {f0:.1f}; "
      f"beam crossing BS {cross:.2f}; puff-aft at {aft_count}/{total} TWAs")
