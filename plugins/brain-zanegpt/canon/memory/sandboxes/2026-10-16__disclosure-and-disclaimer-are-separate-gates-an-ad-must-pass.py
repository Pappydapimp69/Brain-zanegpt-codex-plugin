"""Sandbox: two independent ad gates (FTC disclosure, ASA core-experience) plus a playable-format check.
Deterministic, stdlib only. Rules encoded from the kernels:
 - FTC: material connection disclosed clearly and conspicuously: visible without a click, not buried in a tag block.
 - ASA 2024: footage must reflect the game's core playing experience; a disclaimer does not cure it.
 - Playables: one concept ships video + playable + end card; the playable is the core loop itself.
"""
CORE = "city-builder"

def ftc_ok(ad):
    if not ad["paid"]:
        return True
    d = ad.get("disclosure")
    if d is None:
        return False
    return d["visible_without_click"] and d["tags_in_block"] <= 3 and (d["label"] or d["position"] == "first-line")

def asa_ok(ad):
    # disclaimer is deliberately ignored: the kernel says it does not cure
    core = sum(s for loop, s in ad["footage"] if loop == CORE)
    return core / sum(s for _, s in ad["footage"]) >= 0.6

def playable_ok(ad):
    p = ad.get("playable")
    return p is not None and p == CORE

def verdict(ad):
    return ftc_ok(ad), asa_ok(ad), playable_ok(ad)

A = lambda **k: dict(dict(paid=True, footage=[(CORE, 20)], disclaimer=False, playable=CORE,
     disclosure=dict(visible_without_click=True, tags_in_block=1, label=True, position="first-line")), **k)
S = {
 "1 clean": A(),
 "2 buried hashtag": A(disclosure=dict(visible_without_click=True, tags_in_block=9, label=False, position="last")),
 "3 behind more-click": A(disclosure=dict(visible_without_click=False, tags_in_block=1, label=True, position="first-line")),
 "4 pin-pull footage, no disclaimer": A(footage=[("pin-pull", 18), (CORE, 2)]),
 "5 pin-pull footage + disclaimer": A(footage=[("pin-pull", 18), (CORE, 2)], disclaimer=True),
 "6 BREAK: disclaimer + perfect disclosure on off-core ad": A(footage=[("barrel-shoot", 15), (CORE, 5)], disclaimer=True),
 "7 minigame playable": A(playable="barrel-shoot"),
 "8 unpaid off-core": A(paid=False, disclosure=None, footage=[("barrel-shoot", 20)]),
}
r = {k: verdict(v) for k, v in S.items()}
for k, v in r.items():
    print(k, "ftc/asa/playable =", v)
checks = [
 r["1 clean"] == (True, True, True),
 r["2 buried hashtag"][0] is False and r["2 buried hashtag"][1] is True,
 r["3 behind more-click"][0] is False,
 r["4 pin-pull footage, no disclaimer"][1] == r["5 pin-pull footage + disclaimer"][1] == False,
 r["6 BREAK: disclaimer + perfect disclosure on off-core ad"][:2] == (True, False),
 r["7 minigame playable"][2] is False and r["7 minigame playable"][1] is True,
 r["8 unpaid off-core"] == (True, False, True),
]
print("checks", checks)
print(("RESULT: PASS" if all(checks) else "RESULT: FAIL"),
      f"{sum(checks)}/{len(checks)} checks; disclosure and core-experience gates independent, disclaimer cures neither; playable gate fails on a non-core minigame")
