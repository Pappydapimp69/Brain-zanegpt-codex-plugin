"""Heartless Giant: custody of the critical item decides, not the holder's intent.

Model. Leo's plan is a list of steps. After each prefix of the plan the heart
is in one state: 'hidden' (in Leo's pack or closed hand, nobody else can take
it), 'exposed' (shown, held out, or set down where a brother can reach it) or
'giant' (back inside the giant, out of anyone's reach). A brother gets ONE
action, which can land at any point in Leo's plan (positions 0..len(plan), the
single-preemption schedules). If he lands while the heart is exposed and his
motive is to kill, he grabs and squeezes: the giant dies. Otherwise his action
does nothing and Leo's plan completes. We enumerate every schedule and count
the ones where the giant dies (a count of interleavings, not a probability).

Claim: Leo's choice to give the heart back decides the ending only when no
schedule leaves the heart reachable by an actor with a different motive; the
number of deadly schedules equals the number of exposed states in the plan.

PREDICTION (written before the first run):
  1 tale (shown on arrival, a speech, then given):        2 of 4 schedules kill
  2 long bargain (shown, three steps of talk, given):     4 of 6 kill
  3 hidden until a hand-to-hand give:                     0 of 5 kill
  4 same exposure as the tale, brother wants him spared:  0 of 4 kill
  5 BREAK kept hidden all the way, but handed over by
    setting it down for the giant to pick up:             1 of 5 kill
    (breaks 'carry it yourself and you are safe'; the claim predicts it)
Added after the first run (prediction written before the second run): the
brother stands `reach` steps away; he sees the heart at position p and his
grab lands at p+reach, and kills only if it is exposed at both.
  6 tale, brother 1 step away:                            1 of 4 kill
  7 tale, brother 2 steps away:                           0 of 4 kill
  8 long bargain, brother 2 steps away:                   2 of 6 kill
Added after the check (prediction written before the third run): what counts
is each unbroken run of exposure against the reach, not the total exposed.
  9  split: shown, hidden, shown, then given; brother at 0: 2 of 6 kill
  10 same split, brother 1 step away:                     0 of 6 kill
     (2 exposed states, like the tale, but the tale kills 1 of 4 at reach 1)
  11 set-down handoff, brother 2 steps away:              0 of 5 kill
  12 same split, brother 2 steps away:                    1 of 6 kill
     (he sees it at the first showing and arrives at the second, so a
     run-length rule, which says 0, is expected to miss this one)
"""

PLANS = {
    "tale": ["arrive_showing", "speak", "give"],
    "long_bargain": ["arrive_showing", "speak", "speak", "speak", "give"],
    "hidden_handoff": ["arrive_hidden", "speak", "speak", "give_hand_to_hand"],
    "set_down_handoff": ["arrive_hidden", "speak", "set_down", "giant_takes"],
    "split": ["arrive_showing", "hide", "show", "speak_hidden", "give"],
}

def states(plan):
    """Heart state after each prefix of the plan (len(plan)+1 entries)."""
    s = "hidden"
    out = [s]
    for step in plan:
        if step == "arrive_showing":
            s = "exposed"
        elif step == "arrive_hidden":
            s = "hidden"
        elif step in ("set_down", "show"):
            s = "exposed"
        elif step in ("hide", "speak_hidden"):
            s = "hidden"
        elif step in ("give", "give_hand_to_hand", "giant_takes"):
            s = "giant"
        # 'speak' leaves the state as it was
        out.append(s)
    return out

def run(plan, brother_motive, reach=0):
    st = states(plan)
    deaths = 0
    for pos in range(len(st)):          # brother sees the heart after `pos` steps
        land = pos + reach              # his grab lands `reach` steps later
        if land >= len(st):
            continue
        if st[pos] == "exposed" and st[land] == "exposed" and brother_motive == "kill":
            deaths += 1
    exposed = sum(1 for s in st if s == "exposed")
    return deaths, len(st), exposed

SCEN = [
    ("1 tale", "tale", "kill", 2),
    ("2 long bargain", "long_bargain", "kill", 4),
    ("3 hidden hand-to-hand give", "hidden_handoff", "kill", 0),
    ("4 tale, brother would spare", "tale", "spare", 0),
    ("5 BREAK set-down handoff", "set_down_handoff", "kill", 1),
    ("6 tale, brother 1 step away", "tale", "kill", 1, 1),
    ("7 tale, brother 2 steps away", "tale", "kill", 0, 2),
    ("8 long bargain, 2 steps away", "long_bargain", "kill", 2, 2),
    ("9 split exposure, at hand", "split", "kill", 2, 0),
    ("10 split exposure, 1 step away", "split", "kill", 0, 1),
    ("11 set-down, 2 steps away", "set_down_handoff", "kill", 0, 2),
    ("12 split exposure, 2 steps away", "split", "kill", 1, 2, "run rule misses"),
]

def runs(st):
    out, cur = [], 0
    for x in st:
        if x == "exposed":
            cur += 1
        elif cur:
            out.append(cur)
            cur = 0
    if cur:
        out.append(cur)
    return out

ok = True
for row in SCEN:
    name, plan, motive, predicted = row[:4]
    reach = row[4] if len(row) > 4 else 0
    d, n, e = run(PLANS[plan], motive, reach)
    match = d == predicted
    # the claim: deadly schedules == sum over unbroken exposure runs of
    # (run length - reach), 0 if motives agree
    rs = runs(states(PLANS[plan]))
    rule = sum(max(0, r - reach) for r in rs) if motive == "kill" else 0
    expect_miss = len(row) > 5
    claim = (d == rule) != expect_miss
    ok = ok and match and claim
    print(f"{name:32s} deadly {d} of {n}  exposed states {e}  run rule {rule}  predicted {predicted}  "
          f"{'ok' if match and claim else 'MISMATCH'}{'  (run rule misses, as predicted)' if expect_miss and claim else ''}")

if ok:
    print("RESULT: PASS deadly schedules follow the exposure runs minus the rival's reach except when a re-showing meets his arrival: tale 2/4, long bargain 4/6, "
          "hidden hand-to-hand 0/5, aligned brother 0/4; BREAK set-down handoff still 1/5 "
          "though Leo carried it hidden all the way; "
          "a brother 2 steps away kills in 0/4 of the tale and 2/6 of the long bargain; "
          "split exposure kills 2/6 at hand, 0/6 one step away, but 1/6 two steps away, "
          "where the rival who saw the first showing arrives at the second")
else:
    print("RESULT: FAIL a scenario did not match the prediction or the exposure count")
