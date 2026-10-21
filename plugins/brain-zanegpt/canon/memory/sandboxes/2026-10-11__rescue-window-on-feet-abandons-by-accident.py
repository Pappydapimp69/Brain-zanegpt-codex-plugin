"""Sandbox: spatial rescue window -- does it follow the CAMP or the player's FEET?
Exact enumeration, no RNG. A member goes missing in area m (the camp's area).
Window: findable while the reference area is <= m+1; at m+2 they are lost.
Each day the lead picks one of: stay, scout1 (walk to camp+1 and back),
scout2 (camp+2 and back), move (camp moves +1, a dawn decision).
Rules: CAMP (reference = camp area), FEET (reference = furthest area walked that
day), SLEEP (reference = where you sleep; equals CAMP unless you sleep out --
here you never sleep out, so it should match CAMP).
All 4^4 = 256 four-day plans weighted equally. An abandonment is DELIBERATE if it
happens on a move day, ACCIDENTAL otherwise.
"""
from itertools import product

ACTS = ("stay", "scout1", "scout2", "move")


def run(plan, rule):
    camp = 0
    for day, a in enumerate(plan):
        if a == "move":
            camp += 1
        far = camp + (1 if a == "scout1" else 2 if a == "scout2" else 0)
        ref = far if rule == "feet" else camp
        if ref >= 2:
            return day, a
    return None


def main():
    res = {}
    for rule in ("camp", "feet", "sleep"):
        lost = acc = 0
        moves_before = []
        for plan in product(ACTS, repeat=4):
            r = run(plan, rule)
            if r:
                lost += 1
                day, a = r
                acc += a != "move"
                moves_before.append(sum(x == "move" for x in plan[:day + 1]))
        share = acc / lost if lost else 0
        res[rule] = (lost, acc, share, min(moves_before) if moves_before else 0)
        print(f"{rule:5s}: abandoned in {lost}/256 plans, accidental {acc} ({share:.3f}), "
              f"min deliberate moves before loss {res[rule][3]}")
    checks = [
        ("feet rule: accidental share >= 0.40", res["feet"][2] >= 0.40),
        ("camp rule: accidental share is 0", res["camp"][1] == 0),
        ("camp rule: loss needs >= 2 deliberate camp moves", res["camp"][3] >= 2),
        ("feet rule abandons in more plans than camp rule", res["feet"][0] > res["camp"][0]),
        ("break case: sleep rule (no sleeping out) equals camp rule", res["sleep"] == res["camp"]),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)} predictions held; "
          f"feet lost {res['feet'][0]}/256 accidental {res['feet'][2]:.3f}; camp lost {res['camp'][0]}/256 accidental 0")


if __name__ == "__main__":
    main()
