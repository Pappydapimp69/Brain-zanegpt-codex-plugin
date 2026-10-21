"""Sandbox: The StoryTeller, "The True Bride" (1988) -- three nights bought with three gifts.

Claim under test: in a rule-of-three beat, the third try only teaches the audience
WHY it worked when (a) the first two fail for the same stated reason and (b) the
third changes exactly one visible thing. Otherwise the success has zero or several
candidate causes, or the single candidate is wrong.

Observer model: looks only at VISIBLE variables. A variable is a candidate cause when
every failed attempt shares one value for it and the successful attempt has a
different value. The candidate is checked by a counterfactual: replay the winning
attempt with that variable set back to its failed value, using the real outcome rule.

Deterministic, stdlib only. Prediction written before the first run:
  S1 1 candidate, confirmed; S2 2 candidates; S3 0; S4 0; S5 BREAK 1 candidate but wrong.
  Attributable in exactly 1 of 5.
"""


def outcome_as_told(att, history):
    # Anja wakes him only if she is in the room and he did not drink the sleeping drink.
    return att["present"] == 1 and att["drugged"] == 0


def outcome_accumulating(att, history):
    # BREAK: hidden state -- the spell gives way on the third visit whatever he drank.
    visits_before = sum(1 for h in history if h["present"] == 1)
    return att["present"] == 1 and (att["drugged"] == 0 or visits_before >= 2)


def analyse(name, nights, visible, rule):
    results = []
    for i, att in enumerate(nights):
        results.append(rule(att, nights[:i]))
    fails = [n for n, r in zip(nights, results) if not r]
    wins = [i for i, r in enumerate(results) if r]
    print(f"\n{name}")
    print("  outcomes:", ["wake" if r else "sleep" for r in results])
    if not wins:
        print("  no success")
        return {"candidates": [], "correct": False, "success": False}
    w = wins[0]
    win = nights[w]
    cands = []
    for v in visible:
        fail_vals = {f[v] for f in fails}
        if len(fail_vals) == 1 and win[v] not in fail_vals:
            cands.append(v)
    correct = False
    if len(cands) == 1:
        v = cands[0]
        replay = dict(win)
        replay[v] = next(iter({f[v] for f in fails}))
        still = rule(replay, nights[:w])
        correct = not still
        print(f"  counterfactual: set {v} back -> {'still wakes' if still else 'sleeps'}")
    print(f"  visible={visible} candidates={cands} attribution_correct={correct}")
    return {"candidates": cands, "correct": correct, "success": True}


# warned = he overheard the prisoners (upstream cause of avoiding the drink); the
# outcome rule reads only present and drugged.
told = [
    {"present": 1, "drugged": 1, "warned": 0, "helper": 0},
    {"present": 1, "drugged": 1, "warned": 0, "helper": 0},
    {"present": 1, "drugged": 0, "warned": 1, "helper": 0},
]
two_changes = [dict(n) for n in told]
two_changes[2]["helper"] = 1
different_reasons = [
    {"present": 1, "drugged": 1, "warned": 0, "helper": 0},
    {"present": 0, "drugged": 0, "warned": 0, "helper": 0},  # barred from the room
    {"present": 1, "drugged": 0, "warned": 0, "helper": 0},
]

r = {}
r["S1"] = analyse("S1 as told: drugged twice, avoids the drink on night 3", told,
                  ["present", "drugged", "helper"], outcome_as_told)
r["S2"] = analyse("S2 night 3 changes two visible things (drink avoided + helper)", two_changes,
                  ["present", "drugged", "helper"], outcome_as_told)
r["S3"] = analyse("S3 drugging and warning kept off-screen", told,
                  ["present", "helper"], outcome_as_told)
r["S4"] = analyse("S4 the two failures have different causes", different_reasons,
                  ["present", "drugged", "helper"], outcome_as_told)
r["S5"] = analyse("S5 BREAK hidden accumulation: spell gives way on any third visit", told,
                  ["present", "drugged", "helper"], outcome_accumulating)

# extra: a fourth night in the accumulating world with the drink taken shows the hidden cause
extra = told + [{"present": 1, "drugged": 1, "warned": 0, "helper": 0}]
print("\nS5b BREAK check: accumulating world, night 4 with the drink taken ->",
      "wake" if outcome_accumulating(extra[3], extra[:3]) else "sleep")

attributable = [k for k, v in r.items() if len(v["candidates"]) == 1 and v["correct"]]
print("\nattributable scenarios:", attributable)
ok = (
    r["S1"]["candidates"] == ["drugged"] and r["S1"]["correct"]
    and len(r["S2"]["candidates"]) == 2
    and r["S3"]["candidates"] == []
    and r["S4"]["candidates"] == []
    and r["S5"]["candidates"] == ["drugged"] and not r["S5"]["correct"]
    and attributable == ["S1"]
)
if ok:
    print("RESULT: PASS only the as-told three nights (same stated blocker twice, one visible change) give 1 correct cause; "
          "two changes give 2, hidden or mixed blockers give 0, and hidden accumulation (BREAK) gives 1 wrong cause")
else:
    print("RESULT: FAIL prediction not met: " + str({k: (v['candidates'], v['correct']) for k, v in r.items()}))
