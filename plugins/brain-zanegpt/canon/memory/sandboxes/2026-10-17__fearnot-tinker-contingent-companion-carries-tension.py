"""Fearnot's tinker: where scene tension comes from when the hero cannot be frightened.

The StoryTeller "Fearnot": a fearless boy hires a crafty tinker; the boy agrees to
give the tinker his money if the tinker finds something that frightens him, and the
tinker leads him to a haunted pond and then a haunted castle. Nothing scares the boy.

Model: a fixed itinerary of ever scarier places. The hero is immune (never frightened).
The guide believes a place of scariness s frightens the hero with p = s / (s + D);
D is his doubt, which grows by factor k after each failed scare. He travels on only
while his expected gain beats the trip cost: gain * p - COST * s > 0.
Scene tension = sum over characters of stake * 4p(1-p) (stake on the line times how
open the outcome is, in that character's eyes). The hero risks nothing in a scene.
Deterministic, stdlib only.
"""

ITINERARY = [2, 6, 18, 54, 162]
COST = 0.1
D0 = 2.0


def run(name, guide, purse=10.0, k=2.5, informed=False, d0=D0):
    """guide: None (hero alone), 'contingent' (paid only on a scare), 'flat' (paid up front)."""
    D = d0
    scenes = []
    for s in ITINERARY:
        if guide is None:
            # hero travels alone; he stakes nothing in the encounter
            scenes.append((s, 0.0, 0.0))
            continue
        p = 0.0 if informed else s / (s + D)
        gain = purse if guide == "contingent" else 0.0
        if gain * p - COST * s <= 0:
            break  # guide sees no profit in the next trip: the road ends
        tension = gain * 4 * p * (1 - p)  # hero term is 0: immune, nothing at stake
        scenes.append((s, round(p, 3), round(tension, 2)))
        frightened = False  # the hero is immune
        if not frightened:
            D *= k
    total = round(sum(t for _, _, t in scenes), 1)
    print(f"{name:<44} scenes={len(scenes)} total_tension={total:5.1f}  "
          + " ".join(f"[s={s} p={p} t={t}]" for s, p, t in scenes))
    return len(scenes), total


def main():
    res = {}
    res["alone"] = run("1) hero alone", None)
    res["cont"] = run("2) contingent guide purse 10 k=2.5", "contingent")
    res["fast"] = run("3) contingent guide purse 10 fast learner k=10", "contingent", k=10)
    res["flat"] = run("4) flat-fee guide (paid up front)", "flat")
    res["small"] = run("5) contingent guide small purse 0.5", "contingent", purse=0.5)
    res["brk"] = run("6) BREAK greedy guide who knows hero is immune", "contingent", informed=True)
    # 7) BREAK sweep: same contingent, uninformed guide, but a more doubtful prior
    sweep = [run(f"7) BREAK prior doubt D0={d}", "contingent", d0=d)[0] for d in (0.5, 2, 8, 32, 128)]
    print(f"   scenes by prior doubt D0 0.5/2/8/32/128: {sweep}")

    checks = [
        ("hero alone: 5 scenes, tension 0", res["alone"] == (5, 0.0)),
        ("contingent: 4 scenes, total ~38.9", res["cont"][0] == 4 and abs(res["cont"][1] - 38.9) <= 0.3),
        ("fast learner: 2 scenes, total ~17.1", res["fast"][0] == 2 and abs(res["fast"][1] - 17.1) <= 0.3),
        ("flat fee: 0 scenes", res["flat"] == (0, 0.0)),
        ("small purse: 1 scene, tension 0.5", res["small"] == (1, 0.5)),
        ("BREAK informed greedy guide: 0 scenes", res["brk"] == (0, 0.0)),
        ("BREAK prior-doubt sweep scenes 4,4,3,2,0", sweep == [4, 4, 3, 2, 0]),
    ]
    for label, ok in checks:
        print(("ok   " if ok else "MISS ") + label)
    if all(ok for _, ok in checks):
        print(f"RESULT: PASS immune hero alone gives 0 tension; contingent guide gives "
              f"{res['cont'][0]} scenes / {res['cont'][1]} tension, fast learner {res['fast'][0]} / "
              f"{res['fast'][1]}; flat fee and informed greedy guide give 0 scenes; "
              f"uninformed guide with prior doubt D0 0.5/2/8/32/128 gives {sweep} scenes")
    else:
        print("RESULT: FAIL " + "; ".join(l for l, ok in checks if not ok))


if __name__ == "__main__":
    main()
