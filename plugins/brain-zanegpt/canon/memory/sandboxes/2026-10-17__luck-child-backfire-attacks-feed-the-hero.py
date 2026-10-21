"""Sandbox: an antagonist whose failed attacks become the hero's next step
(The StoryTeller's "The Luck Child": thrown off a cliff -> raised by a couple;
death order -> forged into a marriage order; impossible task -> feather and
treasure; the king's own greed -> the ferryman's curse).

Toy model. The hero has a position P (0 = foundling, GOAL = 10). The hero makes
no moves of his own; only the king acts, up to MAX_ATTACKS times.
  king's attack force a = motive(P)
  backfire chain: a failed attack is converted into hero position, P += a
  plain failure: the attack just fails, P unchanged
Audience response to an attack = a * 0.5**r, where r counts earlier attacks of
equal or greater force (habituation: a repeat that does not top the last one
lands half as hard each time). Deterministic, stdlib only.

PREDICTION (written before the first run):
  1) backfire + motive that grows with the threat (a = 1 + P): forces 1, 2, 4, 8,
     goal reached on attack 4 (P = 15), total response 15.
  2) plain failure, same king: P stays 0 after 6 attacks, all forces 1,
     total response under 2.
  3) backfire + flat motive (a = 1): P = 6 after 6 attacks, goal never reached,
     total response under 2 (same as plain failure).
  BREAK) backfire + a king deterred by a strong hero (a = max(0, 3 - P)):
     one attack of 3, then the king stops; P stalls at 3, goal never reached.

PREDICTION for 5-7 (added after the first run, before running them):
  5) half conversion (P += a/2) with motive 1 + P: forces still rise every
     attack, goal reached on attack 6, response above 15 (no habituation).
  6) flat strong king (a = 4), full conversion: goal on attack 3 but response
     only 7 (4 + 2 + 1), so total force, not growth, reaches the goal; growth
     is what buys the response.
  7) sublinear motive 1 + 0.1P: goal missed in 6 attacks (P under 8).
"""

GOAL, MAX_ATTACKS = 10, 6


def run(motive, backfire, conv=1.0):
    P, forces, resp, reached = 0, [], 0.0, None
    for t in range(1, MAX_ATTACKS + 1):
        a = motive(P)
        if a <= 0:
            break
        r = sum(1 for f in forces if f >= a)
        resp += a * 0.5 ** r
        forces.append(a)
        if backfire:
            P += a * conv
        if reached is None and P >= GOAL:
            reached = t
            break
    return P, forces, resp, reached


cases = {
    "1 backfire, motive grows with threat": (lambda P: 1 + P, True),
    "2 plain failure, same king": (lambda P: 1 + P, False),
    "3 backfire, flat motive": (lambda P: 1, True),
    "BREAK backfire, king deterred by strength": (lambda P: max(0, 3 - P), True),
}
out = {}
for name, (m, b) in cases.items():
    P, forces, resp, reached = run(m, b)
    out[name[:1] if name[0].isdigit() else "B"] = (P, forces, resp, reached)
    print(f"{name}: P={P} forces={forces} response={resp:.2f} goal_on_attack={reached}")

extra = {}
for name, m, conv in (("5 half conversion, motive grows", lambda P: 1 + P, 0.5),
                      ("6 flat strong king a=4", lambda P: 4, 1.0),
                      ("7 sublinear motive 1+0.1P", lambda P: 1 + 0.1 * P, 1.0)):
    P, forces, resp, reached = run(m, True, conv)
    extra[name[0]] = (P, forces, resp, reached)
    print(f"{name}: P={P:.2f} forces={[round(x, 2) for x in forces]} response={resp:.2f} goal_on_attack={reached}")

ok = True
P, f, r, g = extra["5"]; ok &= g == 6 and r > 15
P, f, r, g = extra["6"]; ok &= g == 3 and abs(r - 7) < 1e-9
P, f, r, g = extra["7"]; ok &= g is None and P < 8
P, f, r, g = out["1"]; ok &= f == [1, 2, 4, 8] and g == 4 and P == 15 and abs(r - 15) < 1e-9
P, f, r, g = out["2"]; ok &= P == 0 and f == [1] * 6 and r < 2 and g is None
P, f, r, g = out["3"]; ok &= P == 6 and g is None and r < 2
P, f, r, g = out["B"]; ok &= f == [3] and P == 3 and g is None

r1, r2, r3 = out["1"][2], out["2"][2], out["3"][2]
print(("RESULT: PASS" if ok else "RESULT: FAIL") +
      f" threat-driven backfire reaches the goal in 4 attacks (forces 1,2,4,8, response {r1:.2f});"
      f" plain failure stays at 0 (response {r2:.2f}); flat-motive backfire only P=6 in 6 (response {r3:.2f});"
      f" deterred king stalls the hero at P=3; flat strong king also reaches the goal (attack 3) but"
      f" response {extra['6'][2]:.2f}; half conversion still escalates (goal attack {extra['5'][3]},"
      f" response {extra['5'][2]:.2f}); sublinear motive misses (P={extra['7'][0]:.2f})")
