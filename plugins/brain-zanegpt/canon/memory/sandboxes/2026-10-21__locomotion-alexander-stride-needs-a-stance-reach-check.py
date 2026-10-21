"""Sandbox: Alexander's stride law vs two-bone IK reach in a procedural biped.

Claim under test: driving stride length from speed with Alexander's (1976)
dynamic-similarity law, lambda/h = 2.3 * (v^2/(g h))^0.3, makes the sprint
stride longer than a hand-tuned linear stride, and what the leg must actually
reach is the STANCE length = duty * stride. With a fixed metatarsus the binding
limit is toe-off behind the hip; with the low sprint duty factor from a
Froude-keyed schedule the stance overreaches even with full heel lift, so duty
must be capped by reach / stride.

Iteration history: run 1 predicted that even full heel lift could not reach the
Alexander + Froude-duty sprint stance; that was REFUTED (heel lift reaches with
2.2 cm to spare). Run 2 (this file) tests the surviving claim: the FIXED
metatarsus is what breaks, and stance heel lift is required and sufficient.

Geometry is copied from demos/skin-test/index.html (Herrerasaurus rig).
Deterministic, stdlib only.
"""
import math

G = 9.81
H_HIP = 1.18  # Alexander's h: hip height (pelvis joint y in the rig)


def dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


# Rig points (x, y, z), z forward.
hip0 = (0.17, 1.14, 0.02)
knee0 = (0.22, 0.66, 0.22)
ankle0 = (0.20, 0.20, -0.06)
ball0 = (0.19, 0.035, 0.10)
THIGH, SHIN, META = dist(hip0, knee0), dist(knee0, ankle0), dist(ankle0, ball0)
REACH = THIGH + SHIN
ANK_FROM_BALL = tuple(a - b for a, b in zip(ankle0, ball0))  # fixed metatarsus


def lerp(a, b, t):
    return a + (b - a) * t


def demo_duty(v):
    return lerp(0.64, 0.38, min(max(v / 7.4, 0), 1))


def demo_stride(v):
    return 0.9 + 0.33 * v


def froude_duty(v, L=1.15):  # schedule filed as dlist/E2
    fr = v * v / (G * L)
    return 0.5 + 0.14 * math.tanh((0.5 - fr) / 0.25)


def alexander_stride(v, h=H_HIP):
    return 2.3 * (v * v / (G * h)) ** 0.3 * h


def alexander_speed(stride, h=H_HIP):  # sourced solved form
    return 0.25 * G ** 0.5 * stride ** 1.67 * h ** -1.17


def hip_at(v, q):
    """Hip joint in body frame at leg phase q (leg 0: stance starts at q=0)."""
    sf = min(max(v / 7.4, 0), 1)
    mf = 1.0 if v > 0.6 else max(0.0, (v - 0.05) / 0.55)
    ph = q * 2 * math.pi
    bob = -(0.012 + 0.016 * v) * mf * (0.5 + 0.5 * math.cos(2 * ph))
    return (hip0[0], hip0[1] - 0.04 * sf + bob, hip0[2])


def stance_overreach(v, duty, stride, heel_lift):
    """Worst (front, back) overreach in metres over the stance, >0 means the IK cannot reach."""
    half = 0.5 * duty * stride
    worst_front = worst_back = -9.0
    n = 400
    for i in range(n + 1):
        s = i / n  # 0 touchdown .. 1 toe-off
        q = s * duty
        dz = half - 2 * half * s
        foot = (ball0[0], ball0[1], ball0[2] + dz)
        hip = hip_at(v, q)
        if heel_lift:
            need = dist(foot, hip) - (REACH + META)
        else:
            ankle = tuple(f + a for f, a in zip(foot, ANK_FROM_BALL))
            need = dist(ankle, hip) - REACH
        if s < 0.5:
            worst_front = max(worst_front, need)
        else:
            worst_back = max(worst_back, need)
    return worst_front, worst_back


def max_duty(v, stride, heel_lift):
    lo, hi = 0.05, 0.95
    for _ in range(60):
        mid = (lo + hi) / 2
        f, b = stance_overreach(v, mid, stride, heel_lift)
        if max(f, b) <= 0:
            lo = mid
        else:
            hi = mid
    return lo


fails = []
print(f"rig: thigh={THIGH:.3f} shin={SHIN:.3f} meta={META:.3f} reach(thigh+shin)={REACH:.3f}")

# S1: the sourced solved form is the inverse of the stride law.
coef = (1 / 2.3) ** (1 / 0.6)
print(f"S1 inverse coefficient (1/2.3)^(1/0.6)={coef:.4f} (sourced 0.25); exponents {1 / 0.6:.3f}, {0.5 - 1 / 0.6:.3f}")
worst_rt = 0
for v in (1.0, 2.0, 3.4, 5.0, 7.4):
    lam = alexander_stride(v)
    worst_rt = max(worst_rt, abs(alexander_speed(lam) - v) / v)
print(f"  round-trip worst error {worst_rt * 100:.2f}%")
if worst_rt > 0.01:
    fails.append("inverse mismatch")

# S2: stride and cadence, Alexander vs the demo's linear stride.
print("S2 stride / cadence")
for v in (1.0, 2.38, 3.4, 5.0, 7.4):
    la, ld = alexander_stride(v), demo_stride(v)
    print(f"  v={v:4.2f} Fr={v * v / (G * H_HIP):.2f} alexander={la:.2f} m ({v / la:.2f} Hz) demo={ld:.2f} m ({v / ld:.2f} Hz) demo/alex={ld / la:.2f}")

# S3: demo as shipped (fixed metatarsus during stance).
f, b = stance_overreach(7.4, demo_duty(7.4), demo_stride(7.4), heel_lift=False)
print(f"S3 demo sprint: duty={demo_duty(7.4):.2f} stance={demo_duty(7.4) * demo_stride(7.4):.2f} m overreach front={f:+.3f} back={b:+.3f}")
s3 = b > 0 and f < 0

# S4 (BUILT TO BREAK 'just use Alexander's stride'): Alexander stride + Froude duty.
v = 7.4
lam = alexander_stride(v)
d = froude_duty(v)
f4, b4 = stance_overreach(v, d, lam, heel_lift=False)
f5, b5 = stance_overreach(v, d, lam, heel_lift=True)
print(f"S4 BREAK: alexander stride {lam:.2f} m, froude duty {d:.3f}, stance {d * lam:.2f} m")
print(f"  fixed metatarsus overreach front={f4:+.3f} back={b4:+.3f}; full heel lift front={f5:+.3f} back={b5:+.3f}")
dmax_fixed = max_duty(v, lam, False)
dmax_lift = max_duty(v, lam, True)
print(f"  max reachable duty at 7.4 m/s: fixed meta {dmax_fixed:.3f}, heel lift {dmax_lift:.3f}")
s4 = max(f4, b4) > 0 and max(f5, b5) <= 0

# S5: the reach cap across speeds (where does it start to bind?).
print("S5 reach-capped duty along the speed range (alexander stride)")
bind = None
lift_binds = False
for i in range(10, 75):
    v = i / 10
    lam = alexander_stride(v)
    cap_fixed = max_duty(v, lam, False)
    cap_lift = max_duty(v, lam, True)
    want = froude_duty(v)
    if cap_fixed < want and bind is None:
        bind = v
    lift_binds = lift_binds or cap_lift < want
    if i in (10, 20, 24, 30, 34, 40, 50, 74):
        print(f"  v={v:4.2f} froude duty={want:.3f} cap fixed meta={cap_fixed:.3f} cap heel lift={cap_lift:.3f}")
print(f"  fixed metatarsus first binds at v={bind} m/s; heel-lift cap ever binds: {lift_binds}")
s5 = bind is not None and not lift_binds

if not fails and s3 and s4 and s5:
    print(f"RESULT: PASS stride law inverts to 0.25 coef within {worst_rt * 100:.2f}%; sprint stride alexander {alexander_stride(7.4):.2f} m vs demo {demo_stride(7.4):.2f} m (cadence {7.4 / alexander_stride(7.4):.2f} vs {7.4 / demo_stride(7.4):.2f} Hz); demo toe-off overreach {b:+.3f} m; alexander+froude duty with fixed metatarsus overreaches {b4:+.3f} m at toe-off (duty cap {dmax_fixed:.3f}, binds from {bind} m/s), with heel lift reaches (margin {-max(f5, b5):.3f} m, cap {dmax_lift:.3f})")
else:
    print(f"RESULT: FAIL fails={fails} s3={s3} s4={s4} s5={s5}")
