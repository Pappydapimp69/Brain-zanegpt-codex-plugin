"""Sandbox: which side of a turn does a theropod tail end up on?

Planar (top-down) model. The hip moves along a prescribed path (straight, then a
left turn whose yaw rate ramps in with the demo's smoothing, time constant
0.125 s); body yaw follows the path tangent. The tail is a chain of N rigid links
with point masses at link ends, joined by torsional springs and dampers (passive,
no muscle). Equations of motion with a prescribed accelerating base:

  sum_i M_ai phi_i'' = tau_a - l S(a) u'(phi_a).p0'' + l^2 sum_i S(max(a,i)) sin(phi_i-phi_a) phi_i'^2
  M_ai = l^2 S(max(a,i)) cos(phi_a - phi_i),   S(k) = sum_{j>=k} m_j

integrated with semi-implicit Euler (velocity first, then position) at dt=1e-4.

Compared against a kinematic tail that follows the hip's own path (each joint
placed on the path behind it). Then distal stiffening (the herrerasaurid
elongated distal prezygapophyses as a stiffness multiplier on distal joints) is
tested for where it moves the bending.

Deterministic, stdlib only.
"""
import math

N = 6
L_TAIL = 2.86  # demo tail length (pelvis to tail tip)
LL = L_TAIL / N
M_TAIL = 45.0  # kg, ~18% of a ~250 kg animal (assumed)
w = [N - i for i in range(N)]  # tapering masses 6..1
MASS = [M_TAIL * x / sum(w) for x in w]
S = [sum(MASS[k:]) for k in range(N)]
TAU_YAW = 0.125  # demo: yawRate = damp(yawRate, turn/dt, 8)


def solve(A, b):
    n = len(b)
    A = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(A[r][c]))
        A[c], A[p] = A[p], A[c]
        for r in range(n):
            if r != c:
                f = A[r][c] / A[c][c]
                for k in range(c, n + 1):
                    A[r][k] -= f * A[c][k]
    return [A[i][n] / A[i][i] for i in range(n)]


def inertia_from(k):
    return sum(MASS[j] * (LL * (j - k + 1)) ** 2 for j in range(k, N))


def make_gains(freq_hz, zeta, distal_mult, n_distal=3):
    ks, cs = [], []
    for i in range(N):
        I = inertia_from(i)
        k = I * (2 * math.pi * freq_hz) ** 2
        if i >= N - n_distal:
            k *= distal_mult
        ks.append(k)
        cs.append(2 * zeta * math.sqrt(k * I))
    return ks, cs


def run(v, omega, ks, cs, t_turn=1.0, t_end=4.0, dt=1e-4, explicit=False, track=None):
    """Return a timeline of (t, tip inside offset, joint relative angles)."""
    psi = math.pi / 2  # heading north
    yaw_rate = 0.0
    px, py = 0.0, 0.0
    phi = [psi + math.pi] * N
    dphi = [0.0] * N
    out = []
    t = 0.0
    prev_vel = (v * math.cos(psi), v * math.sin(psi))
    steps = int(t_end / dt)
    for s in range(steps):
        target = omega if t >= t_turn else 0.0
        yaw_rate += (target - yaw_rate) * (1 - math.exp(-dt / TAU_YAW))
        psi_dd = (target - yaw_rate) / TAU_YAW
        psi += yaw_rate * dt
        vel = (v * math.cos(psi), v * math.sin(psi))
        acc = ((vel[0] - prev_vel[0]) / dt, (vel[1] - prev_vel[1]) / dt)
        prev_vel = vel
        px += vel[0] * dt
        py += vel[1] * dt
        base = psi + math.pi
        dbase = yaw_rate
        # spring/damper torques
        tau = [0.0] * N
        for i in range(N):
            prev = base if i == 0 else phi[i - 1]
            dprev = dbase if i == 0 else dphi[i - 1]
            tq = ks[i] * (phi[i] - prev) + cs[i] * (dphi[i] - dprev)
            tau[i] -= tq
            if i > 0:
                tau[i - 1] += tq
        Mx = [[LL * LL * S[max(a, i)] * math.cos(phi[a] - phi[i]) for i in range(N)] for a in range(N)]
        rhs = []
        for a in range(N):
            up = (-math.sin(phi[a]), math.cos(phi[a]))
            r = tau[a] - LL * S[a] * (up[0] * acc[0] + up[1] * acc[1])
            r += LL * LL * sum(S[max(a, i)] * math.sin(phi[i] - phi[a]) * dphi[i] ** 2 for i in range(N))
            rhs.append(r)
        dd = solve(Mx, rhs)
        if explicit:  # forward Euler: position from the OLD velocity
            for i in range(N):
                phi[i] += dphi[i] * dt
            for i in range(N):
                dphi[i] += dd[i] * dt
        else:
            for i in range(N):
                dphi[i] += dd[i] * dt  # semi-implicit: velocity first
            for i in range(N):
                phi[i] += dphi[i] * dt
        t += dt
        if track is not None:
            rel_now = [phi[0] - base] + [phi[i] - phi[i - 1] for i in range(1, N)]
            track[0] = max(track[0], max(abs(r) for r in rel_now))
            if not all(math.isfinite(r) for r in rel_now) or track[0] > 50:
                track[0] = float("inf")
                break
        if s % max(1, int(round(0.01 / dt))) == 0:
            tipx = px + sum(LL * math.cos(p) for p in phi)
            tipy = py + sum(LL * math.sin(p) for p in phi)
            left = (-math.sin(psi), math.cos(psi))
            inside = (tipx - px) * left[0] + (tipy - py) * left[1]  # left turn: left = inside
            rel = [phi[0] - base] + [phi[i] - phi[i - 1] for i in range(1, N)]
            out.append((t, inside, rel))
    return out


def path_follow_inside(R, Ltail):
    """Kinematic tail on the hip's own circular path: tip lateral offset toward centre."""
    return R * (1 - math.cos(Ltail / R))


fails = []
ks, cs = make_gains(1.0, 0.3, 1.0)

# S1: kinematic path-following tail, sprint and walk turn radii from the demo's maxTurn.
for v, om in ((7.4, 1.35), (1.5, 2.43)):
    R = v / om
    print(f"S1 path-following tail v={v} omega={om} R={R:.2f} m: tip inside by {path_follow_inside(R, L_TAIL):.2f} m")

# S2/S3: passive tail at sprint and at walk.
summary = {}
for name, v, om in (("sprint", 7.4, 1.35), ("walk", 1.5, 2.43)):
    tl = run(v, om, ks, cs)
    turn = [(t, x) for t, x, _ in tl if t >= 1.0]
    first = min(turn[:40], key=lambda p: -p[1])  # max inside within 0.4 s
    early_min = min(x for t, x in turn if t < 1.4)
    early_max = max(x for t, x in turn if t < 1.4)
    steady = sum(x for t, x in turn if t > 3.0) / len([1 for t, x in turn if t > 3.0])
    t_first_in = next((t for t, x in turn if x > 0.01), None)
    t_first_out = next((t for t, x in turn if x < -0.01), None)
    summary[name] = (early_max, early_min, steady, t_first_in, t_first_out)
    print(f"S2 passive {name}: first 0.4 s inside max {early_max:+.3f} m / outside max {early_min:+.3f} m; "
          f"first inside at t={t_first_in}, first outside at t={t_first_out}; steady tip {steady:+.3f} m (+ = inside)")

sp = summary["sprint"]
claim_outward_brief = sp[4] is not None and (sp[3] is None or sp[4] < sp[3]) and sp[2] > 0
print(f"  user claim 'brief OUTWARD lag then inside' reproduced at sprint: {claim_outward_brief}")
my_pred = sp[3] is not None and sp[4] is not None and sp[3] < sp[4] and sp[2] < 0
print(f"  my prediction 'brief INSIDE then steady OUTSIDE' reproduced at sprint: {my_pred}")

# S4 (BUILT TO BREAK 'a passive tail ends outside'): very stiff tail (4 Hz) at walk.
ks4, cs4 = make_gains(4.0, 0.3, 1.0)
tl = run(1.5, 2.43, ks4, cs4)
steady4 = [x for t, x, _ in tl if t > 3.0]
st4 = sum(steady4) / len(steady4)
print(f"S4 BREAK: stiff 4 Hz tail at walk turn: steady tip {st4:+.4f} m (tiny either way = body-aligned)")

# S5: distal stiffening shifts bending toward the base.
def base_share(mult):
    k5, c5 = make_gains(1.0, 0.3, mult)
    tl5 = run(7.4, 1.35, k5, c5)
    tot = [0.0] * N
    for t, x, rel in tl5:
        if t > 1.0:
            for i in range(N):
                tot[i] += abs(rel[i])
    return sum(tot[:2]) / sum(tot), tot


sh1, _ = base_share(1.0)
sh5, _ = base_share(5.0)
print(f"S5 share of bending in the 2 base joints: uniform {sh1:.3f}, distal x5 {sh5:.3f} (+{(sh5 - sh1) * 100:.1f} points)")

# S6: kernel MOTION/physics critically-damped-spring -- per-joint critical damping in a coupled chain.
k6, c6 = make_gains(1.0, 1.0, 1.0)
tl6 = run(7.4, 1.35, k6, c6)
turn6 = [(t, x) for t, x, _ in tl6 if t >= 1.0]
st6 = sum(x for t, x in turn6 if t > 3.0) / len([1 for t, x in turn6 if t > 3.0])
peak_out = min(x for t, x in turn6)
overshoot6 = (st6 - peak_out) / abs(st6)
in6 = max(x for t, x in turn6 if t < 1.4)
print(f"S6 per-joint zeta=1 at sprint: early inside {in6:+.3f} m, steady {st6:+.3f} m, overshoot past steady {overshoot6 * 100:.1f}%")

# S7: kernel PHYSICS/integration semi-implicit Euler vs explicit Euler, undamped tail, coarse dt.
k7, c7 = make_gains(1.0, 0.0, 1.0)
res = {}
for name, ex in (("semi-implicit", False), ("explicit", True)):
    tr = [0.0]
    run(7.4, 1.35, k7, c7, t_end=12.0, dt=2e-3, explicit=ex, track=tr)
    res[name] = tr[0]
    print(f"S7 undamped tail, dt=2 ms, 12 s, {name}: max joint angle {tr[0]:.3f} rad")
tr = [0.0]
run(7.4, 1.35, k7, c7, t_end=12.0, dt=1e-4, track=tr)
res["reference dt=0.1ms"] = tr[0]
print(f"S7 reference semi-implicit at dt=0.1 ms: max joint angle {tr[0]:.3f} rad")
ok_int = math.isfinite(res["semi-implicit"]) and not math.isfinite(res["explicit"])

ok_geom = path_follow_inside(7.4 / 1.35, L_TAIL) > 0.5
ok_stiff = sh5 - sh1 >= 0.15
if my_pred and ok_geom and ok_stiff and ok_int:
    print(f"RESULT: PASS path-following tail sits {path_follow_inside(7.4 / 1.35, L_TAIL):.2f} m inside at sprint R; passive tail lags INSIDE first (t={sp[3]:.2f}s) then settles OUTSIDE {sp[2]:+.3f} m, so the 'brief outward lag' is the wrong sign; walk steady {summary['walk'][2]:+.3f} m; distal x5 stiffening moves base-joint bend share {sh1:.2f}->{sh5:.2f}; per-joint critical damping still overshoots {overshoot6 * 100:.0f}%; explicit Euler {res['explicit']:.2f} vs semi-implicit {res['semi-implicit']:.2f} rad")
else:
    print(f"RESULT: FAIL int={res} my_pred={my_pred} user_claim={claim_outward_brief} geom={ok_geom} stiff={ok_stiff} shares {sh1:.3f}->{sh5:.3f} sprint={sp}")
