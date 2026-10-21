"""Sandbox: an ACTIVELY controlled theropod tail in a turn -- which side, how far, when.

Planar (top-down) multibody model with a 3D-lite roll check:
  * body (all but the tail): 205 kg, CoM 0.33 m ahead of the hip at 1.10 m height,
    yaw inertia 75 kg m^2 about its CoM; its path and yaw are prescribed (the demo's
    speed, max turn rate lerp(2.7, 1.35, v/7.4) and yaw smoothing tau = 0.125 s);
  * tail: the loop-4 chain (6 links, 2.86 m, 45 kg tapering 6:5:4:3:2:1); the BASE joint
    is driven by a PD servo (3 Hz, zeta 0.9) toward the strategy's target angle; the
    other joints are passive springs (2 Hz, zeta 0.5) with the distal three 5x stiffer,
    so bending sits at the base.
Equations of motion as in loop 4, semi-implicit Euler, dt = 2e-4 s.

Scored per strategy:
  * roll moment about the support line under the body CoM (N m, + tips outward):
      sum m_i * a_inward_i * z_i  -  sum m_i * g * y_inward_i
  * yaw torque the legs must supply to the body:
      tau_legs = I_b * psi'' + tau_hip  -  M(hip force from tail about body CoM)
  * settling: time after turn entry / exit until roll moment and leg torque stay
    within 5% of their final values (band floor 20 N m).

Iteration history: run 1 fed step commands straight into the PD servo; the step
derivative made impulsive torques (peaks of 1e5..1e7 N m) that swamped every
comparison. Run 2 passes every command through a critically damped 2nd-order
filter (3 Hz) first, as a real muscle-driven tail would be rate-limited.

Deterministic, stdlib only. Mass split, body inertia, gains are ASSUMED (stated).
"""
import math

G = 9.81
N = 6
L_TAIL = 2.86
LL = L_TAIL / N
M_TAIL = 45.0
w = [N - i for i in range(N)]
MASS = [M_TAIL * x / sum(w) for x in w]
S = [sum(MASS[k:]) for k in range(N)]
Z_TAIL = [1.17 - 0.31 * (j + 1) / N for j in range(N)]
M_BODY, H_BODY, C_BODY, I_BODY = 205.0, 1.10, 0.33, 75.0
M_ALL = M_BODY + M_TAIL
D_TAIL = sum(MASS[j] * LL * (j + 1) for j in range(N)) / M_TAIL
TAU_YAW = 0.125
DT = 2e-4


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


def gains(f_mid=2.0, z_mid=0.5, distal=5.0, f_base=3.0, z_base=0.9):
    ks, cs = [], []
    for i in range(N):
        I = inertia_from(i)
        f, z = (f_base, z_base) if i == 0 else (f_mid, z_mid)
        k = I * (2 * math.pi * f) ** 2
        if i >= N - 3:
            k *= distal
        ks.append(k)
        cs.append(2 * z * math.sqrt(k * I))
    return ks, cs


def max_turn(v):
    return 2.7 + (1.35 - 2.7) * min(v / 7.4, 1.0)


def hold_angle(v, omega_f, phi_max):
    """Roll-balancing inside angle: m_t g d sin(phi) = m v omega h, capped at phi_max."""
    need = M_ALL * H_BODY * v * abs(omega_f) / (M_TAIL * G * D_TAIL)
    return math.asin(min(math.sin(phi_max), need))


def simulate(v, strategy, phi_max=0.5, schedule=None, gk=None, t_end=5.0, f_ref=3.0):
    ks, cs = gk or gains()
    schedule = schedule or (lambda t: (max_turn(v) if 1.0 <= t < 3.0 else 0.0))
    psi, yaw_rate = 0.0, 0.0
    px = py = 0.0
    phi = [psi + math.pi] * N
    dphi = [0.0] * N
    ref_f, ref_fd = 0.0, 0.0  # critically damped reference filter (no step commands)
    wr = 2 * math.pi * f_ref
    entry_psi, side, flick_t0, last_target = None, 1.0, None, 0.0
    rec = []
    steps = int(t_end / DT)
    for s in range(steps):
        t = s * DT
        target = schedule(t)
        if target != 0.0 and (last_target == 0.0 or math.copysign(1, target) != math.copysign(1, last_target)):
            entry_psi, side, flick_t0 = psi, math.copysign(1, target), t
        last_target = target
        a_f = 1 - math.exp(-DT / TAU_YAW)
        yaw_new = yaw_rate + (target - yaw_rate) * a_f
        psi_dd = (yaw_new - yaw_rate) / DT
        yaw_rate = yaw_new
        u = (math.cos(psi), math.sin(psi))
        up = (-math.sin(psi), math.cos(psi))
        # hip kinematics (body CoM moves at v along heading; hip is C_BODY behind it)
        hip = (px - C_BODY * u[0], py - C_BODY * u[1])
        hip_dd = (v * yaw_rate * up[0] - C_BODY * psi_dd * up[0] + C_BODY * yaw_rate ** 2 * u[0],
                  v * yaw_rate * up[1] - C_BODY * psi_dd * up[1] + C_BODY * yaw_rate ** 2 * u[1])
        # strategy -> inside angle (+ toward the side of the current/last turn)
        hold = hold_angle(v, yaw_rate, phi_max)
        if strategy == "inside":
            th = hold
        elif strategy == "outside":
            th = -hold
        elif strategy == "straight":
            th = 0.0
        elif strategy == "flick-in-hold-out":
            th = phi_max if (flick_t0 is not None and t - flick_t0 < 0.25 and target != 0) else -hold
        elif strategy == "flick-out-hold-in":
            th = -phi_max if (flick_t0 is not None and t - flick_t0 < 0.25 and target != 0) else hold
        elif strategy == "inside-lag":  # tail keeps its world heading until the hold angle is reached
            if target != 0.0 and entry_psi is not None:
                th = min(hold, abs(psi - entry_psi))
            else:
                th = hold
        else:
            raise ValueError(strategy)
        cmd = -side * th  # relative angle: inside (toward +side) is a negative rotation
        ref_fd += (wr * wr * (cmd - ref_f) - 2 * wr * ref_fd) * DT
        ref_f += ref_fd * DT
        ref, ref_rate = ref_f, ref_fd
        base, dbase = psi + math.pi, yaw_rate
        tau = [0.0] * N
        tau_hip = 0.0
        for i in range(N):
            prev = base if i == 0 else phi[i - 1]
            dprev = dbase if i == 0 else dphi[i - 1]
            rel, drel = phi[i] - prev, dphi[i] - dprev
            if i == 0:
                tq = ks[0] * (rel - ref) + cs[0] * (drel - ref_rate)
                tau_hip = -tq  # torque the hip applies to the tail
            else:
                tq = ks[i] * rel + cs[i] * drel
            tau[i] -= tq
            if i > 0:
                tau[i - 1] += tq
        Mx = [[LL * LL * S[max(a, i)] * math.cos(phi[a] - phi[i]) for i in range(N)] for a in range(N)]
        rhs = []
        for a in range(N):
            ua = (-math.sin(phi[a]), math.cos(phi[a]))
            r = tau[a] - LL * S[a] * (ua[0] * hip_dd[0] + ua[1] * hip_dd[1])
            r += LL * LL * sum(S[max(a, i)] * math.sin(phi[i] - phi[a]) * dphi[i] ** 2 for i in range(N))
            rhs.append(r)
        dd = solve(Mx, rhs)
        # tail mass accelerations and positions (before stepping)
        acc = list(hip_dd)
        pos = list(hip)
        F = [0.0, 0.0]
        roll = 0.0
        inward = (up[0] * side, up[1] * side)
        for j in range(N):
            uj = (math.cos(phi[j]), math.sin(phi[j]))
            upj = (-math.sin(phi[j]), math.cos(phi[j]))
            acc[0] += LL * (dd[j] * upj[0] - dphi[j] ** 2 * uj[0])
            acc[1] += LL * (dd[j] * upj[1] - dphi[j] ** 2 * uj[1])
            pos[0] += LL * uj[0]
            pos[1] += LL * uj[1]
            F[0] += MASS[j] * acc[0]
            F[1] += MASS[j] * acc[1]
            a_in = acc[0] * inward[0] + acc[1] * inward[1]
            y_in = (pos[0] - px) * inward[0] + (pos[1] - py) * inward[1]
            roll += MASS[j] * (a_in * Z_TAIL[j] - G * y_in)
        a_body_in = v * yaw_rate * side
        roll += M_BODY * a_body_in * H_BODY
        r_h = (-C_BODY * u[0], -C_BODY * u[1])
        Fb = (-F[0], -F[1])
        m_hip = r_h[0] * Fb[1] - r_h[1] * Fb[0]
        tau_legs = I_BODY * psi_dd + tau_hip - m_hip
        rel_all = [phi[0] - base] + [phi[i] - phi[i - 1] for i in range(1, N)]
        if s % 25 == 0:
            rec.append((t, roll, tau_legs, rel_all, -side * (phi[0] - base)))
        for i in range(N):
            dphi[i] += dd[i] * DT
        for i in range(N):
            phi[i] += dphi[i] * DT
        psi += yaw_rate * DT
        px += v * math.cos(psi) * DT
        py += v * math.sin(psi) * DT
    return rec


def settle(rec, t0, t1, key, band):
    seg = [r for r in rec if t0 <= r[0] < t1]
    final = sum(r[key] for r in seg[-40:]) / 40
    last_bad = t0
    for r in seg:
        if abs(r[key] - final) > band:
            last_bad = r[0]
    return last_bad - t0, final


def score(rec, v):
    band = 0.05 * M_ALL * v * max_turn(v) * H_BODY  # 5% of the no-tail roll load, same for all strategies
    turn = [r for r in rec if r[0] >= 1.0]
    peak_roll = max(abs(r[1]) for r in turn)
    peak_yaw = max(abs(r[2]) for r in turn)
    st_e_roll, roll_ss = settle(rec, 1.0, 3.0, 1, band)
    st_e_yaw, yaw_ss = settle(rec, 1.0, 3.0, 2, band)
    st_x_roll, _ = settle(rec, 3.0, 5.0, 1, band)
    st_x_yaw, _ = settle(rec, 3.0, 5.0, 2, band)
    base = sum(abs(r[3][0]) for r in turn)
    tot = sum(sum(abs(x) for x in r[3]) for r in turn)
    return dict(peak_roll=peak_roll, roll_ss=roll_ss, peak_yaw=peak_yaw, yaw_ss=yaw_ss,
                settle=max(st_e_roll, st_e_yaw, st_x_roll, st_x_yaw), settle_in=max(st_e_roll, st_e_yaw),
                settle_out=max(st_x_roll, st_x_yaw), base_share=base / tot)


STRATS = ["inside", "inside-lag", "outside", "flick-in-hold-out", "flick-out-hold-in", "straight"]
results = {}
print(f"tail CoM {D_TAIL:.2f} m behind hip; tail yaw inertia about hip {inertia_from(0):.1f} kg m^2; body I {I_BODY}")
for v in (1.5, 3.4, 7.4):
    om = max_turn(v)
    print(f"\nv={v} m/s, yaw rate {om:.2f} rad/s, R={v / om:.2f} m, centripetal {v * om:.2f} m/s^2, no-tail roll load m*a*h={M_ALL * v * om * H_BODY:.0f} N m")
    print("  strategy            peakRoll  steadyRoll  peakLegYaw  steadyLegYaw  settle in/out  baseBend")
    for st in STRATS:
        sc = score(simulate(v, st), v)
        results[(v, st)] = sc
        print(f"  {st:19s} {sc['peak_roll']:8.0f}  {sc['roll_ss']:10.0f}  {sc['peak_yaw']:10.0f}  {sc['yaw_ss']:12.0f}  {sc['settle_in']:4.2f}/{sc['settle_out']:4.2f}s  {sc['base_share']:.2f}")

# sensitivity of the winner to phi_max at sprint
print("\nS-sens inside-lag at 7.4 m/s vs phi_max")
for pm in (0.3, 0.5, 0.7):
    sc = score(simulate(7.4, "inside-lag", phi_max=pm), 7.4)
    print(f"  phi_max={pm}: peakRoll {sc['peak_roll']:.0f} steadyRoll {sc['roll_ss']:.0f} peakLegYaw {sc['peak_yaw']:.0f} settle {sc['settle']:.2f}s")

# robustness: soft loop-4 mid joints (1 Hz, zeta 0.3)
print("\nS-soft mid joints 1 Hz zeta 0.3 at 7.4 m/s")
soft = {}
for st in ("inside-lag", "outside", "straight"):
    sc = score(simulate(7.4, st, gk=gains(f_mid=1.0, z_mid=0.3)), 7.4)
    soft[st] = sc
    print(f"  {st:12s} peakRoll {sc['peak_roll']:.0f} steadyRoll {sc['roll_ss']:.0f} peakLegYaw {sc['peak_yaw']:.0f} baseBend {sc['base_share']:.2f}")


# BREAK: sprint slalom, yaw target flips every 0.5 s (4 flips) -- the winner must cross sides each time.
def slalom(t):
    if t < 1.0 or t >= 3.0:
        return 0.0
    k = int((t - 1.0) / 0.5)
    return 1.35 if k % 2 == 0 else -1.35


print("\nS-BREAK sprint slalom (yaw target +/-1.35 rad/s flipping every 0.5 s)")
sl = {}
for st in ("inside-lag", "inside", "straight", "outside"):
    rec = simulate(7.4, st, schedule=slalom)
    turn = [r for r in rec if 1.0 <= r[0] < 3.5]
    sl[st] = (max(abs(r[1]) for r in turn), max(abs(r[2]) for r in turn))
    print(f"  {st:12s} peakRoll {sl[st][0]:.0f} peakLegYaw {sl[st][1]:.0f}")


def rank_key(sc):
    return (sc["peak_roll"], sc["peak_yaw"])


ok = True
notes = []
for v in (1.5, 3.4, 7.4):
    best_roll = min(STRATS, key=lambda s: results[(v, s)]["roll_ss"])
    best_peak_yaw = min(STRATS, key=lambda s: results[(v, s)]["peak_yaw"])
    notes.append(f"v{v}: steady-roll best {best_roll}, peak-yaw best {best_peak_yaw}")
print("\n" + "; ".join(notes))
W = "inside-lag"
for v in (1.5, 3.4, 7.4):
    r = results[(v, W)]
    if r["roll_ss"] > 1.03 * min(results[(v, s)]["roll_ss"] for s in STRATS):
        ok = False; notes.append(f"steady roll not within 3% of best at {v}")
    if r["peak_yaw"] > results[(v, "straight")]["peak_yaw"] or r["peak_yaw"] > results[(v, "outside")]["peak_yaw"]:
        ok = False; notes.append(f"peak yaw above straight/outside at {v}")
    if r["base_share"] < 0.5:
        ok = False; notes.append(f"base share low at {v}")
slalom_broke = sl[W][1] > sl["straight"][1]
plain_inside_broke = sl["inside"][1] > sl["straight"][1]
print(f"slalom: plain inside hold breaks on leg yaw: {plain_inside_broke}; lag-timed winner breaks: {slalom_broke}")
ok = ok and not slalom_broke
s74 = results[(7.4, W)]
s74s = results[(7.4, "straight")]
s74o = results[(7.4, "outside")]
s15 = results[(1.5, W)]
s15s = results[(1.5, "straight")]
if ok:
    print(f"RESULT: PASS active tail wins INSIDE entered by lag: sprint steady roll {s74['roll_ss']:.0f} vs straight {s74s['roll_ss']:.0f} vs outside {s74o['roll_ss']:.0f} N m, peak leg yaw {s74['peak_yaw']:.0f} vs straight {s74s['peak_yaw']:.0f} vs outside {s74o['peak_yaw']:.0f}; walk steady roll {s15['roll_ss']:.0f} vs {s15s['roll_ss']:.0f}; base bend share {s74['base_share']:.2f}; slalom break holds for lag timing (peak leg yaw {sl[W][1]:.0f} vs straight {sl['straight'][1]:.0f}) but breaks a plain inside hold ({sl['inside'][1]:.0f}); settle in/out {s74['settle_in']:.2f}/{s74['settle_out']:.2f} s")
else:
    print(f"RESULT: FAIL winner checks failed; {'; '.join(notes)}")
