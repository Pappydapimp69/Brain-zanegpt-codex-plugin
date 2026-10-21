"""Sandbox: predictive foot planting and touchdown skid in a procedural gait.

The demo (demos/skin-test/index.html) swings each foot with
  foot = lerp(liftPos, land, smoothstep(s)),
  land = body + R(yaw) * (neutral + 0.5*v*duty*T forward) + fwd * v * remaining,
re-evaluated every frame. Because smoothstep has zero slope at s=1, the foot's
world velocity at touchdown equals the TARGET's world velocity. So the
v*remaining term is what makes the target stand still in the world and the foot
arrive without skidding. Claim under test: that holds on straight paths and under
acceleration, but in a turn the body-attached offset rotates, so the target moves
at omega*|offset| at touchdown unless heading is predicted as well.

Iteration history: run 1 predicted ~0 skid under acceleration; it gave 0.43 m/s,
because the stance-centring term 0.5*v*duty*T uses the CURRENT speed, so the
target creeps forward at 0.5*a*duty*T. Run 2 adds the fix (freeze that speed at
lift-off) as its own scenario.

Deterministic, stdlib only.
"""
import math

NEUTRAL = (0.19, 0.10)  # (lateral, forward) of the ball joint in the rig


def lerp(a, b, t):
    return a + (b - a) * t


def demo_duty(v):
    return lerp(0.64, 0.38, min(max(v / 7.4, 0), 1))


def demo_stride(v):
    return 0.9 + 0.33 * v


def alexander_stride(v, h=1.18):  # dlist/E3
    return 2.3 * (v * v / (9.81 * h)) ** 0.3 * h


def froude_duty(v, L=1.15):  # dlist/E2
    fr = v * v / (9.81 * L)
    return 0.5 + 0.14 * math.tanh((0.5 - fr) / 0.25)


def rot(vec, yaw):  # three.js applyAxisAngle(UP, yaw) on (x, z)
    x, z = vec
    return (x * math.cos(yaw) + z * math.sin(yaw), -x * math.sin(yaw) + z * math.cos(yaw))


def body_state(t, v0, a, omega):
    """Body position/yaw/speed with constant acceleration and yaw rate (closed form by fine sum)."""
    n = max(1, int(t / 1e-4))
    dt = t / n
    x = z = yaw = 0.0
    v = v0
    for _ in range(n):
        x += math.sin(yaw) * v * dt
        z += math.cos(yaw) * v * dt
        v += a * dt
        yaw += omega * dt
    return (x, z), yaw, v


def target(t, rem, v0, a, omega, duty, T, mode, v_center=None):
    p, yaw, v = body_state(t, v0, a, omega)
    vc = v if v_center is None else v_center
    off = (NEUTRAL[0], NEUTRAL[1] + 0.5 * vc * duty * T)
    if mode == "none":
        o = rot(off, yaw)
        return (p[0] + o[0], p[1] + o[1])
    if mode == "vel":  # the demo
        o = rot(off, yaw)
        f = (math.sin(yaw), math.cos(yaw))
        return (p[0] + o[0] + f[0] * v * rem, p[1] + o[1] + f[1] * v * rem)
    # "arc": predict where the body and its heading will be at touchdown
    q, yaw2, _ = (body_state(t + rem, v0, a, omega) if rem > 0 else (p, yaw, v))
    o = rot(off, yaw2)
    return (q[0] + o[0], q[1] + o[1])


def touchdown_speed(v0, a, omega, mode, stride_fn=demo_stride, duty_fn=demo_duty, t_lift=0.5, freeze=False):
    """World speed of the foot at touchdown = speed of the target at s=1 (smoothstep)."""
    duty = duty_fn(v0)
    f = max(v0 / stride_fn(v0), 1.1)
    T = 1 / f
    swing = (1 - duty) * T
    t_td = t_lift + swing
    h = 1e-3
    vc = body_state(t_lift, v0, a, omega)[2] if freeze else None

    def foot(t):
        s = min(1.0, (t - t_lift) / swing)
        e = s * s * (3 - 2 * s)
        rem = (1 - s) * swing
        lift = target(t_lift, swing, v0, a, omega, duty, T, mode, vc)  # where the swing started (approx)
        land = target(t, rem, v0, a, omega, duty, T, mode, vc)
        return (lift[0] + (land[0] - lift[0]) * e, lift[1] + (land[1] - lift[1]) * e)

    p1, p0 = foot(t_td), foot(t_td - h)
    return math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / h


fails = []
res = {}
cases = [
    ("S1 sprint straight", 7.4, 0.0, 0.0),
    ("S2 walk straight", 1.5, 0.0, 0.0),
    ("S3 accelerating 3 m/s^2 at 4 m/s", 4.0, 3.0, 0.0),
    ("S4 BREAK sprint turn 1.35 rad/s", 7.4, 0.0, 1.35),
    ("S5 walk turn 2.43 rad/s", 1.5, 0.0, 2.43),
]
for name, v, a, om in cases:
    row = {m: touchdown_speed(v, a, om, m) for m in ("none", "vel", "arc")}
    res[name] = row
    print(f"{name}: touchdown foot speed  no-prediction {row['none']:.2f}  velocity-only (demo) {row['vel']:.3f}  heading-predicted {row['arc']:.3f} m/s")

# S3b: the fix for S3 -- freeze the stance-centring speed at lift-off.
c3b = {m: touchdown_speed(4.0, 3.0, 0.0, m, freeze=True) for m in ("vel", "arc")}
print(f"S3b accelerating, centring speed frozen at lift-off: velocity-only {c3b['vel']:.3f}  heading-predicted {c3b['arc']:.3f} m/s (unfrozen drift 0.5*a*duty*T = {0.5 * 3.0 * demo_duty(4.0) / max(4.0 / demo_stride(4.0), 1.1):.3f})")

# S6: compose with dlist/E2 + dlist/E3 (longer Froude/Alexander stance offset) in the sprint turn.
row6 = {m: touchdown_speed(7.4, 0.0, 1.35, m, alexander_stride, froude_duty) for m in ("vel", "arc")}
half_demo = 0.5 * demo_duty(7.4) * demo_stride(7.4)
half_alex = 0.5 * froude_duty(7.4) * alexander_stride(7.4)
print(f"S6 sprint turn with alexander stride + froude duty: velocity-only {row6['vel']:.3f} m/s, heading-predicted {row6['arc']:.3f} m/s (half stance {half_alex:.2f} m vs demo {half_demo:.2f} m)")
pred_turn = 1.35 * math.hypot(NEUTRAL[0], NEUTRAL[1] + half_demo)
print(f"  omega*|offset| prediction for the demo sprint turn: {pred_turn:.3f} m/s")

c1 = res["S1 sprint straight"]
c3 = res["S3 accelerating 3 m/s^2 at 4 m/s"]
c4 = res["S4 BREAK sprint turn 1.35 rad/s"]
c5 = res["S5 walk turn 2.43 rad/s"]
if not (c1["none"] > 6.5 and c1["vel"] < 0.05):
    fails.append("straight sprint")
if not (c3["vel"] > 0.3 and c3b["vel"] < 0.05):
    fails.append("acceleration")
if not (c4["vel"] > 0.5 and c4["arc"] < 0.05 and c5["vel"] > 0.5 and c5["arc"] < 0.05):
    fails.append("turn")
if not abs(c4["vel"] - pred_turn) < 0.05:
    fails.append("omega*offset")
if not row6["vel"] > c4["vel"]:
    fails.append("longer stance should skid more")
if not fails:
    print(f"RESULT: PASS no prediction skids at {c1['none']:.2f} m/s at sprint touchdown, velocity prediction {c1['vel']:.3f}; accel skids {c3['vel']:.3f} until the centring speed is frozen at lift-off ({c3b['vel']:.3f}); in turns velocity-only still skids {c4['vel']:.2f} m/s sprint / {c5['vel']:.2f} walk (= omega*|offset|), {row6['vel']:.2f} with E2/E3 stance; heading prediction {c4['arc']:.3f}/{c5['arc']:.3f}")
else:
    print(f"RESULT: FAIL {fails}")
