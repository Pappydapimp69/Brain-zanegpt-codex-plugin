"""Sandbox: does a reference-image anchor make an AI product shot compliant?
Deterministic. Shot = (kind, shows_product, ref_images, attrs_changed).
Policy model from tiktok-shop/E14: product shots must show the real item; AI must
not alter size/color/material/quantity/features/performance; significantly-AI
video must be labelled; AI dubbing is permitted.
Drift model (deterministic, parameterised): an AI-rendered product shot alters
attribute i iff (i*7 + shot_seed) % (2 + ref_images*DAMP) == 0 -> more refs, fewer
alterations, but never a guarantee. A real shot alters nothing.
"""
import itertools, sys
ATTRS = ["size", "color", "material", "quantity", "features", "performance"]
DAMP = 3

def altered(kind, ref_images, seed):
    if kind != "ai_product":
        return []
    mod = 2 + ref_images * DAMP
    return [a for i, a in enumerate(ATTRS) if (i * 7 + seed) % mod == 0]

def violates(video):
    """ground truth: any product shot AI-made with alterations, or fabricated, or unlabelled significant AI."""
    prod_ai = [s for s in video["shots"] if s["kind"] == "ai_product"]
    if prod_ai:  # policy: AI must not replace/fabricate product displays at all
        return True
    ai_share = sum(s["kind"] in ("ai_scene", "ai_product") for s in video["shots"]) / len(video["shots"])
    if ai_share > video["label_threshold"] and not video["label"]:
        return True
    return False

def gate_shotlist(video):  # column check: real product only in product shots + label if AI-heavy
    return violates(video)

def gate_visual_only(video):  # "reference image keeps it consistent" check: no attribute drift seen
    return any(altered(s["kind"], s["ref"], s["seed"]) for s in video["shots"])

def build():
    vids = []
    for n_prod_ai, n_scene_ai, label, ref, seed, thr in itertools.product(
            [0, 1], [0, 2, 5], [False, True], [0, 1, 3], range(0, 6), [0.3, 0.5]):
        shots = [{"kind": "real", "ref": 0, "seed": 0}] * 2
        shots += [{"kind": "ai_scene", "ref": 0, "seed": 0}] * n_scene_ai
        shots += [{"kind": "ai_product", "ref": ref, "seed": seed}] * n_prod_ai
        vids.append({"shots": shots, "label": label, "label_threshold": thr})
    return vids

vids = build()
viol = [v for v in vids if violates(v)]
# Scenario 1: reference-anchored AI product shots (the claim): visual-only gate vs truth
anchored = [v for v in vids if any(s["kind"] == "ai_product" and s["ref"] > 0 for s in v["shots"])]
passes_visual = [v for v in anchored if not gate_visual_only(v)]
still_violate = [v for v in passes_visual if violates(v)]
# Scenario 2: shot-list gate equals truth (by construction) -- check it flags every anchored AI product shot
caught = [v for v in anchored if gate_shotlist(v)]
# Scenario 3 (BREAK): more refs lowers drift but never reaches zero across all seeds
drift = {r: sum(len(altered("ai_product", r, sd)) for sd in range(0, 60)) for r in (0, 1, 3, 9)}
# Scenario 4: dubbing-only video (real footage + AI dubbing) must be compliant even with no label
dub = {"shots": [{"kind": "real", "ref": 0, "seed": 0}] * 4, "label": False, "label_threshold": 0.3}
# Scenario 5: AI-heavy scenes, real product, unlabelled -> violation via label only
lbl = {"shots": [{"kind": "real", "ref": 0, "seed": 0}] * 2 + [{"kind": "ai_scene", "ref": 0, "seed": 0}] * 5,
       "label": False, "label_threshold": 0.3}
print(f"videos={len(vids)} violating={len(viol)} anchored_ai_product={len(anchored)}")
print(f"anchored shots passing visual-drift gate={len(passes_visual)}; of those still violating policy={len(still_violate)}")
print(f"shot-list gate catches {len(caught)}/{len(anchored)} anchored")
print("alteration counts over 60 seeds by ref_images:", drift)
print(f"dubbing-only violates={violates(dub)}; unlabelled AI-heavy scenes violates={violates(lbl)}")
ok = (len(still_violate) > 0 and len(caught) == len(anchored) and drift[0] > drift[1] > drift[3] > drift[9] > 0
      and not violates(dub) and violates(lbl))
print("RESULT: %s anchored AI product shots that pass the visual-drift check still violate in %d/%d cases; refs cut alterations %d->%d->%d->%d (never 0); shot-list gate catches %d/%d"
      % ("PASS" if ok else "FAIL", len(still_violate), len(passes_visual), drift[0], drift[1], drift[3], drift[9], len(caught), len(anchored)))
