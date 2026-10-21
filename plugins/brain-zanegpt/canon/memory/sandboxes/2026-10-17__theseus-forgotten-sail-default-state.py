"""The forgotten sail: which state should a signal show when nobody updates it?

The StoryTeller "Theseus and the Minotaur" (1991): the ship sails under a black
sail; Theseus promises to raise a white one if he lives, forgets, and Aegeus,
seeing black, kills himself.  Plutarch (Theseus 22) says the joy of success is
why both Theseus and the pilot forgot.

Model: 100 voyages, 70 succeed and 30 fail.  The sender forgets to change the
signal on 20% of the voyages where a change is needed (integer counts, no
randomness).  In some scenarios a failed voyage leaves nobody able to change
anything at all.  Three designs:
  A default-bad   : black unless someone hoists white on success (Theseus)
  B default-good  : white unless someone hoists black on failure
  C three-state   : no sail until someone hoists white (success) or black
                    (failure); "no sail" reads as "no news yet"
Costs per voyage when read: correct 0, false bad news, false good news and
"no news" each have a scenario cost.

PREDICTION (written before the first run):
  S1 Theseus (false-bad 100 irreversible, false-good 20, wait 1, sender able
     on failure): A 1400, B 120, C 20.  Default-bad is the worst design.
  S2 failure leaves nobody to act (same costs): A 1400, B 600, C 44.
  S3 BREAK costs swapped (false good 100 = no relief sent, false bad 20),
     nobody to act on failure: A 280, B 3000, C 44 -> default-bad now beats
     default-good, so "make the default mean good news" is not a rule; the
     rule is "default = the reading whose false version is cheapest".
  S4 BREAK receiver cannot wait (no-news read as worst, cost 100), S1 costs:
     A 1400, B 120, C 2000 -> the third state is the worst design.
  Added after the first run (prediction written before the second run):
  S5 BREAK checklist on success (success updates never forgotten), nobody to
     act on failure, S1 costs: A 0, B 600, C 30.  The per-voyage shortcut
     "default = cheaper false reading" picks B and is wrong; only the count-
     weighted version (how often each default is left standing) picks A.
"""

N_SUCCESS, N_FAIL = 70, 30
FORGET_NUM, FORGET_DEN = 1, 5  # 20% of needed updates are forgotten


def forgotten(n):
    return n * FORGET_NUM // FORGET_DEN


def run(design, costs, fail_incapacitated, success_checklist=False):
    """Return (total cost, counts of each reading error)."""
    false_bad = false_good = unknown = 0
    # success branch: sender alive, may forget (a checklist removes forgetting)
    s_forget = 0 if success_checklist else forgotten(N_SUCCESS)
    # failure branch: sender may be unable to act at all
    f_unable = N_FAIL if fail_incapacitated else forgotten(N_FAIL)
    if design == "A":       # default black; success must hoist white
        false_bad += s_forget            # forgotten success shows black
    elif design == "B":     # default white; failure must hoist black
        false_good += f_unable           # failure with no update shows white
    elif design == "C":     # default none; both branches must hoist
        unknown += s_forget + f_unable
    cost = (false_bad * costs["false_bad"] + false_good * costs["false_good"]
            + unknown * costs["unknown"])
    return cost, (false_bad, false_good, unknown)


def shortcut_rule(costs):
    """Per-voyage shortcut: default = reading whose false version is cheaper."""
    return "A" if costs["false_bad"] < costs["false_good"] else "B"


def best_two_state_by_rule(costs, fail_incapacitated, success_checklist=False):
    """Rule: default = reading whose false version costs least, weighted by
    how many voyages leave the default standing on the wrong branch."""
    a = (0 if success_checklist else forgotten(N_SUCCESS)) * costs["false_bad"]
    b = (N_FAIL if fail_incapacitated else forgotten(N_FAIL)) * costs["false_good"]
    return "A" if a < b else "B"


SCENARIOS = [
    ("S1 Theseus", dict(false_bad=100, false_good=20, unknown=1), False, False,
     dict(A=1400, B=120, C=20), "B"),
    ("S2 failure leaves nobody to act", dict(false_bad=100, false_good=20, unknown=1), True, False,
     dict(A=1400, B=600, C=44), "B"),
    ("S3 BREAK costs swapped", dict(false_bad=20, false_good=100, unknown=1), True, False,
     dict(A=280, B=3000, C=44), "A"),
    ("S4 BREAK receiver cannot wait", dict(false_bad=100, false_good=20, unknown=100), False, False,
     dict(A=1400, B=120, C=2000), "B"),
    ("S5 BREAK checklist on success", dict(false_bad=100, false_good=20, unknown=1), True, True,
     dict(A=0, B=600, C=30), "B"),
]

ok = True
for name, costs, incap, check, predicted, shortcut_pred in SCENARIOS:
    got = {}
    for d in "ABC":
        c, errs = run(d, costs, incap, check)
        got[d] = c
        print(f"{name:34s} design {d}: cost {c:5d}  (false-bad, false-good, no-news) = {errs}")
    rule = best_two_state_by_rule(costs, incap, check)
    actual_best2 = "A" if got["A"] < got["B"] else "B"
    best = min(got, key=got.get)
    sc = shortcut_rule(costs)
    print(f"{'':34s} best overall {best}; best two-state {actual_best2}; "
          f"weighted rule picks {rule}; per-voyage shortcut picks {sc}"
          f"{'' if sc == actual_best2 else ' (SHORTCUT WRONG)'}")
    if sc != shortcut_pred:
        ok = False
    if got != predicted:
        ok = False
        print(f"{'':34s} MISMATCH predicted {predicted}")
    if rule != actual_best2:
        ok = False
        print(f"{'':34s} RULE WRONG")

theseus_ratio = SCENARIOS and run("A", SCENARIOS[0][1], False)[0] / run("B", SCENARIOS[0][1], False)[0]
print(f"S1 default-bad costs {theseus_ratio:.1f}x default-good")
if ok:
    print("RESULT: PASS forgotten sail: default-bad 1400 vs default-good 120 vs three-state 20; "
          "swap costs and default-bad wins (280 vs 3000); three-state worst (2000) when receiver cannot wait; "
          "never-forgotten success flips it (0 vs 600) so weigh by how often the default is left standing")
else:
    print("RESULT: FAIL predictions did not match")
