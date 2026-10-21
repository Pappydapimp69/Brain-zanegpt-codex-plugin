"""Deterministic sandbox: does a compass tell below one display increment vanish?
Kernel claim (ideas:gamedev/feedback/rate-a-tell-in-the-units-its-display-quantises-to):
 - an error < one display increment (2pi/8) is 'invisible'; and
 - a release during player motion is masked; gate on rest (feet AND head).
Sibling (rate-a-perceptual-tell-by-its-observed-rate): measure OBSERVED rate = nominal * gates.
"""
import math
INC = 2 * math.pi / 8
def label(a): return int(round((a % (2*math.pi)) / INC)) % 8

# Prediction (written before run): a sub-increment error is NOT always invisible; over
# uniformly spaced headings the visible fraction ~= err/INC (e.g. 0.5*INC -> ~0.50), so the
# 'below one increment = invisible' rule is only a worst-case-for-the-designer bound.
def visible_fraction(err, n=8000):
    vis = sum(label(2*math.pi*i/n) != label(2*math.pi*i/n + err) for i in range(n))
    return vis / n

res = {}
for frac in (0.1, 0.25, 0.5, 0.99, 1.0, 1.5):
    res[frac] = visible_fraction(frac * INC)
    print(f"S1 err={frac:>4}*INC visible_fraction={res[frac]:.3f}")
ok1 = abs(res[0.5]-0.5) < 0.01 and abs(res[0.1]-0.1) < 0.01 and res[1.0] > 0.999 and 0 < res[0.99] < 1

# S2 masking: player timeline of 100 ticks; yaw rotates in ticks 0-59 (look-around), rest 60-99.
# A release at any tick with err=1.0*INC: perceived as a 'tell' only if display changes while
# the player does nothing. Count releases whose change lands at rest vs during motion.
moving = [t < 60 for t in range(100)]
def perceived(t, gate):
    if gate and moving[t]: return False       # gated: not released
    return (not moving[t])                    # anomaly seen as anomaly only when nothing moves
ungated = sum(perceived(t, False) for t in range(100))
gated = sum(perceived(t, True) for t in range(100))
fired_ungated = 100; fired_gated = sum(not m for m in moving)
print(f"S2 ungated: fired={fired_ungated} perceived={ungated} ({ungated/fired_ungated:.2f}); "
      f"gated: fired={fired_gated} perceived={gated} ({gated/fired_gated:.2f})")
ok2 = ungated/fired_ungated == 0.40 and gated/fired_gated == 1.0

# S3 observed rate (sibling kernel): nominal p per tick, release only at rest, visible
# fraction v for the error size. observed = p * rest_share * v  (product, not nominal p).
p, rest_share = 0.05, 0.40
for v_name, v in (("1.0*INC", res[1.0]), ("0.5*INC", res[0.5])):
    obs = p * rest_share * v
    print(f"S3 {v_name}: nominal={p} observed={obs:.4f} ratio={obs/p:.2f}")
ok3 = abs(p*rest_share*res[0.5] - 0.01) < 5e-4

# S4 BREAK: accumulating drift. Tiny per-tick drift 0.05*INC never exceeds one increment per
# event, yet after 20 ticks of accumulation the display has changed by >=1 label: a
# slow tell is visible even though every step is sub-increment.
a0 = 0.3 * INC; lab0 = label(a0); changed_at = None
for t in range(1, 40):
    if label(a0 + 0.05*INC*t) != lab0: changed_at = t; break
print(f"S4 per-step 0.05*INC drift: display flips at tick {changed_at}")
ok4 = changed_at is not None and changed_at <= 5
print("RESULT: " + ("PASS" if ok1 and ok2 and ok3 and ok4 else "FAIL") +
      f" sub-increment visible_fraction~err/INC (0.5->{res[0.5]:.3f}), gating lifts perceived 0.40->1.00, "
      f"observed rate 0.05->{p*rest_share*res[0.5]:.3f}, slow drift flips display at tick {changed_at}")
