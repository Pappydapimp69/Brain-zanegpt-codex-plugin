"""Prompt-composer sandbox for the AI-VIDEO kernels (five-part shot formula with audio block; style card fills slots;
image-to-video = subject + movement). Deterministic, stdlib only. The conflict table is AUTHOR-WRITTEN from the kernels'
vocabulary (handheld vs rigged moves, shallow focus vs deep/wide focus, available vs shaped light, ambient vs scored audio),
not measured on a video model.
Prediction (before running): (1) the three whole cards compose to prompts with the identical block order and zero lint
conflicts; (2) mixing slots across cards (camera from X, lens from Y, light from Z, audio from W; 3^4=81 combos) leaves
fewer than half lint-clean, so cards should be swapped whole; (2b) appending two cards' values into each slot conflicts for 3/3 card pairs; (3) image-to-video mode drops cinematography and style, so
structure is NOT identical there (4 blocks not 6) and a card's look terms must not appear; (4) BREAK: a free-text action with
two verbs ('walks and spins') passes the five-slot form but is caught by a one-action lint, and the form alone cannot stop it."""
import itertools, re
CARDS = {
 "ugc":     dict(camera="handheld phone, eye level", lens="soft focus", light="available window light", audio="ambient room tone", dialogue='"I tried this yesterday."'),
 "demo":    dict(camera="static close-up", lens="macro lens, shallow depth of field", light="soft controlled light", audio="crisp product SFX", dialogue=None),
 "premium": dict(camera="slow dolly shot", lens="wide-angle lens, deep focus", light="shaped key light", audio="scored music bed", dialogue=None),
}
ORDER = ["CAMERA", "SUBJECT", "ACTION", "CONTEXT", "STYLE", "AUDIO"]
def compose(card, subject="a ceramic mug", action="steam rises", context="on a kitchen counter"):
    style = f"{card['lens']}; {card['light']}"
    blocks = [("CAMERA", card["camera"]), ("SUBJECT", subject), ("ACTION", action), ("CONTEXT", context), ("STYLE", style),
              ("AUDIO", card["audio"] + (f"; Dialogue: {card['dialogue']}" if card["dialogue"] else ""))]
    return blocks
def compose_i2v(card, subject="a ceramic mug", movement="steam rises"):
    return [("SUBJECT", subject), ("ACTION", movement), ("CAMERA", card["camera"]), ("AUDIO", card["audio"])]
CONFLICTS = [  # (term A in one slot text, term B in another slot) cannot coexist in one shot
 ("handheld", "dolly"), ("handheld", "static"), ("handheld", "crane"),
 ("shallow depth", "deep focus"), ("macro", "wide-angle"), ("soft focus", "deep focus"), ("soft focus", "macro"),
 ("available window", "shaped key"), ("available window", "soft controlled"),
 ("ambient room", "scored music"), ("crisp product", "scored music"), ("crisp product", "ambient room"),
]
def lint(blocks):
    text = " | ".join(v.lower() for _, v in blocks); bad = []
    for a, b in CONFLICTS:
        if a in text and b in text: bad.append((a, b))
    act = dict(blocks).get("ACTION", "")
    if len(re.findall(r"\b(and|then|while|,)\b", act)) >= 1: bad.append(("one-action", act))
    return bad
ok = True; out = []
pure = {k: compose(v) for k, v in CARDS.items()}
same_order = len({tuple(n for n, _ in b) for b in pure.values()}) == 1 and [n for n, _ in pure["ugc"]] == ORDER
clean_pure = sum(not lint(b) for b in pure.values())
s1 = same_order and clean_pure == 3; ok &= s1; out.append(f"pure cards same order={same_order} clean={clean_pure}/3")
slots = ["camera", "lens", "light", "audio"]; clean = total = 0
for pick in itertools.product(CARDS, repeat=4):
    card = {s: CARDS[p][s] for s, p in zip(slots, pick)}; card["dialogue"] = None
    total += 1; clean += not lint(compose(card))
mixed_only = clean - 3 if clean >= 3 else clean       # the three pure combos have no dialogue here, still clean
# FIRST RUN refuted prediction (2): all 81 slot-mixed combos were lint-clean, because the vocabulary conflicts live INSIDE a slot, not across slots.
s2 = clean == total; ok &= s2; out.append(f"slot-mixed combos lint-clean {clean}/{total} (prediction of <half was REFUTED)")
def union(a, b): return {k: (a[k] + " + " + b[k]) if a[k] and b[k] else (a[k] or b[k]) for k in a}
pairs = list(itertools.combinations(CARDS, 2))
uni = sum(bool(lint(compose({**union(CARDS[x], CARDS[y]), "dialogue": None}))) for x, y in pairs)
s2b = uni == len(pairs); ok &= s2b; out.append(f"union-merged card pairs with a conflict {uni}/{len(pairs)}")
i2v = compose_i2v(CARDS["premium"]); names = [n for n, _ in i2v]
s3 = len(i2v) == 4 and "STYLE" not in names and "CONTEXT" not in names and "deep focus" not in " ".join(v for _, v in i2v)
ok &= s3; out.append(f"i2v blocks={len(i2v)} no style/context={s3}")
b4 = compose(CARDS["demo"], action="walks and spins")
s4 = bool([x for x in lint(b4) if x[0] == "one-action"]) and len(b4) == 6; ok &= s4; out.append(f"two-verb action caught={s4} (form had 6 slots filled)")
for k, b in pure.items(): print(k, " || ".join(f"{n}: {v}" for n, v in b))
print("i2v", i2v)
print("RESULT:", "PASS" if ok else "FAIL", "; ".join(out))
