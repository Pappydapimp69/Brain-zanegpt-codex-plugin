"""Fleeing from where the threat WAS: avoidance that routes back to the outcome.

The StoryTeller "Perseus and the Gorgon" (1991): told he will die by his
grandson's hand, Acrisius sets Danae and the baby adrift in a chest; years
later a discus thrown by Perseus at games kills him anyway.  In Apollodorus
(2.4.4) Acrisius, hearing Perseus is coming, leaves Argos for the Pelasgian
land, and the games where the discus kills him are held at Larissa.

Model: a line of places 0..20.  The avoider starts at 8.  The threat starts at
5 and walks 2 places a turn toward its own destination (it is not chasing).
"Contact" = a turn ending with the two within 1 place.  Policies:
  STAY  : avoider stays put
  STALE : avoider steps 1 place a turn away from the threat's position at
          turn 0 (the only sighting it has), stopping at the edge
  LIVE  : avoider steps 1 place away from the threat's current position
          (tie: toward the farther edge)
Anything that has left its last-known spot is moving away from that spot, so
"away from the sighting" can be the same direction the threat is travelling.

PREDICTION (written before the first run), 15 turns unless stated:
  S1 threat settles near home (destination 7): STAY 15 contacts, STALE 0.
  S2 threat departs toward the avoider's side (destination 20, the games):
     STAY 2, STALE 8 (fleeing quadruples contact and ends at the threat's
     destination), LIVE 2.
  S3 BREAK threat departs the other way (destination 0): STAY 0, STALE 0 --
     stale flight costs nothing, so the harm needs the threat to leave toward
     the avoider's side.
  S4 BREAK threat no faster than the avoider (speed 1, destination 20):
     15 turns STAY 3, STALE 2 (flight looks better); 30 turns STAY 3,
     STALE 17 (the flight ends where the threat ends).
  Added after the separate check asked whether the wall made the result
  (prediction written before the second run): S5 line 0..40, avoider starts
  mid-line at 20, threat from 17 at speed 2, 30 turns.
     S5a destination 30 (not the edge): STAY 2, STALE 6 (3 running alongside,
         3 passing through the destination, then it runs on past).
     S5b destination 40 (the edge): STAY 2, STALE 15.
  So running alongside raises contact on its own; the long dwell needs the
  threat's destination to sit at the end of the flight.
"""

LO, HI = 0, 20


def clamp(x):
    return max(LO, min(HI, x))


def set_line(hi):
    global HI
    HI = hi


def step_toward(pos, dest, speed):
    if pos < dest:
        return min(dest, pos + speed)
    if pos > dest:
        return max(dest, pos - speed)
    return pos


def away(a, ref):
    if a > ref:
        return clamp(a + 1)
    if a < ref:
        return clamp(a - 1)
    # tie: head for the farther edge
    return clamp(a - 1) if (a - LO) > (HI - a) else clamp(a + 1)


def simulate(policy, dest, speed=2, turns=15, a0=8, t0=5, hi=20):
    set_line(hi)
    a, t = a0, t0
    sighting = t0
    contacts = 0
    for _ in range(turns):
        t_now = t
        if policy == "STAY":
            na = a
        elif policy == "STALE":
            na = away(a, sighting)
        elif policy == "LIVE":
            na = away(a, t_now)
        t = step_toward(t, dest, speed)
        a = na
        if abs(a - t) <= 1:
            contacts += 1
    return contacts, a, t


CASES = [
    # (label, policy, dest, speed, turns, predicted contacts[, a0, t0, hi])
    ("S1 settles near home", "STAY", 7, 2, 15, 15),
    ("S1 settles near home", "STALE", 7, 2, 15, 0),
    ("S2 departs toward (games)", "STAY", 20, 2, 15, 2),
    ("S2 departs toward (games)", "STALE", 20, 2, 15, 8),
    ("S2 departs toward (games)", "LIVE", 20, 2, 15, 2),
    ("S3 BREAK departs away", "STAY", 0, 2, 15, 0),
    ("S3 BREAK departs away", "STALE", 0, 2, 15, 0),
    ("S4 BREAK equal speed 15t", "STAY", 20, 1, 15, 3),
    ("S4 BREAK equal speed 15t", "STALE", 20, 1, 15, 2),
    ("S4 BREAK equal speed 30t", "STAY", 20, 1, 30, 3),
    ("S4 BREAK equal speed 30t", "STALE", 20, 1, 30, 17),
    ("S5a long line, dest mid", "STAY", 30, 2, 30, 2, 20, 17, 40),
    ("S5a long line, dest mid", "STALE", 30, 2, 30, 6, 20, 17, 40),
    ("S5b long line, dest edge", "STAY", 40, 2, 30, 2, 20, 17, 40),
    ("S5b long line, dest edge", "STALE", 40, 2, 30, 15, 20, 17, 40),
]

ok = True
res = {}
for case in CASES:
    label, pol, dest, spd, turns, pred = case[:6]
    a0, t0, hi = case[6:] if len(case) > 6 else (8, 5, 20)
    c, a, t = simulate(pol, dest, spd, turns, a0, t0, hi)
    res[(label, pol)] = c
    flag = "" if c == pred else f"  MISMATCH (predicted {pred})"
    print(f"{label:28s} {pol:5s} contacts {c:2d}  avoider ends {a:2d}, threat ends {t:2d}{flag}")
    if c != pred:
        ok = False

stale_hurts = res[("S2 departs toward (games)", "STALE")] > res[("S2 departs toward (games)", "STAY")]
stale_helps_home = res[("S1 settles near home", "STALE")] < res[("S1 settles near home", "STAY")]
neutral_away = res[("S3 BREAK departs away", "STALE")] == res[("S3 BREAK departs away", "STAY")]
print(f"stale flight hurts when threat departs toward: {stale_hurts}; helps when threat stays home: "
      f"{stale_helps_home}; neutral when it departs away: {neutral_away}")
mid_hurts = res[("S5a long line, dest mid", "STALE")] > res[("S5a long line, dest mid", "STAY")]
print(f"stale flight still hurts on a 41-place line with the destination off the edge: {mid_hurts}")
ok = ok and stale_hurts and stale_helps_home and neutral_away and mid_hurts
if ok:
    print("RESULT: PASS fleeing a stale sighting: 8 contacts vs 2 for staying when the threat departs "
          "toward the avoider (live tracking 2); 0 vs 15 when it stays home; no effect when it departs away; "
          "at equal speed 2 vs 3 at 15 turns becomes 17 vs 3 at 30; on a 41-place line 6 vs 2 with the "
          "destination mid-line, 15 vs 2 when it sits at the end of the flight")
else:
    print("RESULT: FAIL predictions did not match")
