"""Renderer-private enumeration vs content-declared enumeration, with several mods loaded in every order.
Each mod declares places (name -> meaning) and entities placed in them. Meaning of 'other' differs per mod
(a shared name with different meaning = collision); 'forest'/'river' have the same meaning everywhere."""
from itertools import permutations

MODS = {
    "M1": {"places": {"forest": "wood", "river": "water", "other": "misc-scenery"},
           "ents": [("oak", "forest"), ("eel", "river"), ("rock", "other")]},
    "M2": {"places": {"forest": "wood", "camp": "enemy-camp", "other": "camp-fallback"},
           "ents": [("pine", "forest"), ("tent", "camp"), ("spear", "other")]},
    "M3": {"places": {"river": "water", "ford": "crossing"},
           "ents": [("log", "river"), ("stone", "ford")]},
}
PRIVATE = ["forest", "river", "other"]       # written into the renderer before M2/M3 existed

def load(order, strategy):
    ents = []   # (id, label, intended_meaning)
    declared = {}
    errors = 0
    for m in order:
        mod = MODS[m]
        if strategy == "last-list-wins":
            declared = dict(mod["places"])                    # later mod replaces the whole list
        else:
            for k, v in mod["places"].items():
                key = f"{m}:{k}" if strategy == "namespaced" else k
                declared[key] = v if strategy == "namespaced" else declared.get(k, v)  # first meaning kept on union
        for e, p in mod["ents"]:
            label = f"{m}:{p}" if strategy == "namespaced" else p
            ents.append((e, label, mod["places"][p]))
    drawn, undrawn, wrong, state = 0, 0, 0, []
    for e, label, meaning in ents:
        if strategy == "private" or strategy == "validated":
            ok = label in PRIVATE
            if not ok and strategy == "validated": errors += 1; continue   # loud failure, entity rejected
        else:
            ok = label in declared
        if ok:
            drawn += 1
            # rendered meaning: private list has fixed meaning from M1; declared uses the declared meaning
            shown = {"forest": "wood", "river": "water", "other": "misc-scenery"}.get(label) if strategy in ("private",) else declared.get(label)
            if shown != meaning: wrong += 1
            state.append((e, label))
        else:
            undrawn += 1
    return dict(loaded=len(ents), drawn=drawn, undrawn=undrawn, rejected=errors, wrong=wrong, state=tuple(sorted(state)))

res = []
orders = list(permutations(MODS))
out = {}
for s in ("private", "validated", "union", "last-list-wins", "namespaced"):
    rs = [load(o, s) for o in orders]
    states = {r["state"] for r in rs}
    out[s] = dict(undrawn=max(r["undrawn"] for r in rs), rejected=max(r["rejected"] for r in rs), wrong=max(r["wrong"] for r in rs),
                  states=len(states), loaded=rs[0]["loaded"])
    print(f"{s:15s} loaded {out[s]['loaded']} | silently undrawn (max over {len(orders)} orders) {out[s]['undrawn']} | loudly rejected {out[s]['rejected']} | wrong meaning {out[s]['wrong']} | distinct end states {out[s]['states']}")
res.append(out["private"]["undrawn"] > 0 and out["private"]["rejected"] == 0)    # bug: present but undrawn, no error
res.append(out["validated"]["rejected"] > 0 and out["validated"]["undrawn"] == 0) # tell: loud
res.append(out["union"]["undrawn"] == 0 and out["union"]["states"] == 1)          # declared list: all drawn, order independent
res.append(out["union"]["wrong"] > 0)                                             # BREAK: name collision 'other' shows wrong meaning
res.append(out["last-list-wins"]["undrawn"] > 0 and out["last-list-wins"]["states"] > 1)  # declared but order dependent
res.append(out["namespaced"]["undrawn"] == 0 and out["namespaced"]["wrong"] == 0 and out["namespaced"]["states"] == 1)
print(("RESULT: PASS" if all(res) else "RESULT: FAIL") + f" checks={res}")
