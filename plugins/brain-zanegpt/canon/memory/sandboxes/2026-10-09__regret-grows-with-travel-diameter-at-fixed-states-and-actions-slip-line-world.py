"""Sandbox: does regret track the DIAMETER (travel time) rather than state/action counts?
World: S states on a line, A=3 actions (left, right, stay). A move executes only on every m-th attempt made from that state
(deterministic slip counter, no RNG), so the travel diameter is D ~ m*(S-1). Reward 1 per step spent on the treasure state g.
Learner: starts in the middle, sweeps right to the end, then left to state 0, stopping as soon as it sees reward (it only
learns g by standing on it). Regret = reward of the informed optimum (knows g, walks straight there) minus the learner's,
averaged over every g in 0..S-1, horizon T.
PREDICTION (written before run 1), T=600:
 P1 at fixed S=8, A=3, regret rises roughly linearly with m: R(m=8)/R(m=1) between 6 and 10.
 P2 same state and action count, diameters differ: S=6,m=8 (D=40) has MORE regret than S=24,m=1 (D=23).
 P3 BREAK: when T is below the travel needed (T=60, S=24, m=8) both learner and optimum earn almost nothing, so regret
    SATURATES (shrinks) instead of growing with D: R(T=60) < R(T=600) for that world.
 P4 once the treasure is found nothing more is lost: doubling T 600->1200 leaves regret unchanged (+-1%) when D << T."""
def run(S, m, g, T, learner=True):
    pos = S // 2
    if not learner:                                  # informed optimum: straight to g
        reward, att = 0, {}
        target_dir = 1 if g > pos else -1
        for t in range(T):
            if pos == g: reward += 1; continue
            att[pos] = att.get(pos, 0) + 1
            if att[pos] % m == 0: pos += target_dir
        return reward
    reward, att, direction, seen_end = 0, {}, 1, False
    for t in range(T):
        if pos == g: reward += 1; continue           # found: stay
        att[pos] = att.get(pos, 0) + 1
        if att[pos] % m == 0:
            if pos + direction > S - 1 or pos + direction < 0: direction = -direction
            pos += direction
            if pos == S - 1: direction = -1
    return reward

def regret(S, m, T):
    tot = 0
    for g in range(S):
        tot += run(S, m, g, T, False) - run(S, m, g, T, True)
    return tot / S

R = {}
for m in (1, 2, 4, 8): R[("S8", m)] = regret(8, m, 600)
print("P1 S=8 regret by m:", {m: round(R[("S8", m)], 1) for m in (1, 2, 4, 8)}, "ratio m8/m1 = %.2f" % (R[("S8", 8)] / R[("S8", 1)]))
a, b = regret(6, 8, 600), regret(24, 1, 600)
print("P2 S=6,m=8 (D=40): %.1f   S=24,m=1 (D=23): %.1f" % (a, b))
c60, c600 = regret(24, 8, 60), regret(24, 8, 600)
print("P3 S=24,m=8: regret at T=60 %.1f vs T=600 %.1f" % (c60, c600))
d600, d1200 = regret(6, 2, 600), regret(6, 2, 1200)
print("P4 S=6,m=2: regret at T=600 %.2f vs T=1200 %.2f" % (d600, d1200))
ok = (6 <= R[("S8", 8)] / R[("S8", 1)] <= 10 and a > b and c60 < c600 and abs(d1200 - d600) <= 0.01 * d600)
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
      "m8/m1 regret ratio %.2f; S6 m8 %.1f > S24 m1 %.1f; T-limited regret %.1f < %.1f; T doubling %.2f -> %.2f" % (R[("S8", 8)] / R[("S8", 1)], a, b, c60, c600, d600, d1200))
