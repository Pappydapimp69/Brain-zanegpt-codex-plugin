"""Sandbox: walk/run switch for a procedural biped gait.

Claim under test: a two-legged gait has an aerial phase exactly when duty
factor < 0.5, and a rigid-leg (inverted pendulum) walk cannot exist above a
Froude number Fr = v^2/(g L) of 1 at midstance; once the stance arc has a real
half-angle th0 the leg force goes negative first at the ENDS of stance, so the
real ceiling is lower, Fr_mid <= 3cos(th0) - 2. A duty-factor schedule written
as a fraction of the game's top speed therefore lets the character "walk"
(duty > 0.5) at speeds no pendulum walk can reach.

Deterministic, stdlib only, no RNG, no real timing.
"""
import math

G = 9.81


def support_fractions(duty, n=20000):
    """Sweep one gait cycle for two legs offset by half a cycle."""
    aerial = double = 0
    for i in range(n):
        q = i / n
        a = q % 1.0 < duty
        b = (q + 0.5) % 1.0 < duty
        k = a + b
        aerial += k == 0
        double += k == 2
    return aerial / n, double / n


def vault_min_leg_force(v_mid, L, th0, steps=4000):
    """Point mass vaulting over a rigid massless leg of length L from -th0 to +th0.

    Energy conservation sets the speed at each leg angle; the leg force per unit
    mass along the leg is g*cos(th) - v(th)^2 / L. Returns its minimum over the
    stance and the angle where it occurs.
    """
    worst = (float("inf"), 0.0)
    for i in range(steps + 1):
        th = -th0 + 2 * th0 * i / steps
        v2 = v_mid ** 2 + 2 * G * L * (1 - math.cos(th))
        f = G * math.cos(th) - v2 / L
        if f < worst[0]:
            worst = (f, th)
    return worst


def ceiling_fr(L, th0):
    """Largest midstance Froude number with leg force >= 0 everywhere (bisection)."""
    lo, hi = 0.0, math.sqrt(2 * G * L)
    for _ in range(80):
        mid = (lo + hi) / 2
        if vault_min_leg_force(mid, L, th0)[0] >= 0:
            lo = mid
        else:
            hi = mid
    return lo ** 2 / (G * L)


def lerp(a, b, t):
    return a + (b - a) * t


# Demo schedule (demos/skin-test/index.html): duty = lerp(0.64, 0.38, v/7.4),
# stride = 0.9 + 0.33 v, hip 1.18 m with foot 0.035 m -> leg L ~ 1.15 m.
def demo_duty(v):
    return lerp(0.64, 0.38, min(max(v / 7.4, 0), 1))


def demo_stride(v):
    return 0.9 + 0.33 * v


fails = []

# Scenario 1: support pattern vs duty factor.
print("S1 support pattern (two legs, half-cycle offset)")
for duty in (0.70, 0.55, 0.50, 0.45, 0.38):
    a, d = support_fractions(duty)
    exp_a, exp_d = max(0, 1 - 2 * duty), max(0, 2 * duty - 1)
    print(f"  duty={duty:.2f} aerial={a:.3f} (pred {exp_a:.3f}) double={d:.3f} (pred {exp_d:.3f})")
    if abs(a - exp_a) > 1e-3 or abs(d - exp_d) > 1e-3:
        fails.append(f"support duty {duty}")

# Scenario 2: Froude-1 ceiling at midstance (vanishing stance angle).
L = 1.15
fr0 = ceiling_fr(L, 1e-4)
print(f"S2 rigid-leg ceiling, tiny stance arc: Fr={fr0:.3f} v={math.sqrt(fr0 * G * L):.2f} m/s")
if abs(fr0 - 1.0) > 0.01:
    fails.append("Fr ceiling not 1 at th0->0")

# Scenario 3 (BUILT TO BREAK the 'Fr = 1 is the walking ceiling' rule):
# a real stance arc. If the simple rule held, the ceiling would stay at 1.
print("S3 BREAK: finite stance half-angle")
for deg in (10, 20, 27, 30, 35):
    th0 = math.radians(deg)
    fr = ceiling_fr(L, th0)
    pred = 3 * math.cos(th0) - 2
    print(f"  th0={deg:2d} deg ceiling Fr_mid={fr:.3f} (3cos-2={pred:.3f}) v_mid={math.sqrt(max(fr, 0) * G * L):.2f} m/s")
    if abs(fr - pred) > 0.01:
        fails.append(f"ceiling formula at {deg}")

# Scenario 4: the demo schedule against both ceilings.
print("S4 demo schedule")
v_cross = 7.4 * (0.64 - 0.5) / (0.64 - 0.38)
print(f"  duty hits 0.5 at v={v_cross:.2f} m/s -> Fr={v_cross ** 2 / (G * L):.2f}")
v_froude_half = math.sqrt(0.5 * G * L)
print(f"  Froude-0.5 transition for L={L}: v={v_froude_half:.2f} m/s; human L=0.90: v={math.sqrt(0.5 * G * 0.9):.2f} m/s")
impossible = []
for i in range(0, 741):
    v = i / 100
    duty = demo_duty(v)
    if duty <= 0.5 or v < 0.5:
        continue
    stance_len = duty * demo_stride(v)
    th0 = math.asin(min(1.0, stance_len / 2 / L))
    fr_mid = v ** 2 / (G * L)  # treat mean speed as midstance speed (generous)
    if fr_mid > 3 * math.cos(th0) - 2:
        impossible.append(v)
if impossible:
    print(f"  demo 'walks' (duty>0.5) with negative leg force for v in [{impossible[0]:.2f}, {impossible[-1]:.2f}] m/s")
v_walk_top = 3.4
d = demo_duty(v_walk_top)
th0 = math.asin(d * demo_stride(v_walk_top) / 2 / L)
print(f"  non-sprint top 3.4 m/s: duty={d:.3f} th0={math.degrees(th0):.1f} deg Fr={v_walk_top ** 2 / (G * L):.2f} ceiling={3 * math.cos(th0) - 2:.2f}")

# Froude-driven schedule: duty passes 0.5 at Fr 0.5 for ANY leg length.
def froude_duty(v, L):
    fr = v * v / (G * L)
    return 0.5 + 0.14 * math.tanh((0.5 - fr) / 0.25)  # 0.64 slow, 0.36 fast

for leg in (0.25, 0.9, 1.15):
    vx = math.sqrt(0.5 * G * leg)
    print(f"  froude schedule L={leg}: duty at Fr0.5 (v={vx:.2f}) = {froude_duty(vx, leg):.3f}")
    if abs(froude_duty(vx, leg) - 0.5) > 1e-9:
        fails.append("froude schedule")

ok = not fails and impossible and v_cross ** 2 / (G * L) > 1.0
if ok:
    print(f"RESULT: PASS aerial phase iff duty<0.5; ceiling Fr=1 only at zero arc, 3cos(th0)-2 otherwise (0.60 at 30 deg); demo duty crosses 0.5 at {v_cross:.2f} m/s = Fr {v_cross ** 2 / (G * L):.2f}, walking-impossible band {impossible[0]:.2f}-{impossible[-1]:.2f} m/s; Froude-0.5 switch is {v_froude_half:.2f} m/s")
else:
    print(f"RESULT: FAIL {fails}")
