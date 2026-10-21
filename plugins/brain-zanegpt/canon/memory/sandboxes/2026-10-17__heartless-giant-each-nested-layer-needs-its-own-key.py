"""The Heartless Giant (The StoryTeller, a variant of the Norwegian 'The Giant Who Had No Heart in His Body').
Deterministic, stdlib. The heart sits in nested layers, outermost first; each layer names the solvers that can open it
(a tuple means any one of them will do). Layers in the Norwegian tale: the wolf carries the hero over the lake,
the raven fetches the church keys, the hero coaxes the duck (which drops the egg into the well),
the salmon fetches the egg up from the well, and the hero squeezes it (order as in Dasent's translation).
A layer is a NEW beat if the solver used on it has not been used before; otherwise it is padding (more distance, no
new obstacle). Retrieval walks inward and stops at the first layer no helper the hero has can open."""
TALE = [("lake", ("wolf",)), ("church", ("raven",)), ("duck", ("hero",)), ("well", ("salmon",)), ("egg", ("hero-squeeze",))]
ALL = {"wolf", "raven", "salmon", "hero", "hero-squeeze", "rope"}
def walk(layers, helpers):
    used, beats, padding, cleared = set(), 0, 0, []
    for name, solvers in layers:
        able = [s for s in solvers if s in helpers]
        if not able:
            return dict(layers=len(layers), beats=beats, padding=padding, cleared=cleared, reached=False, stuck=name)
        s = able[0]
        beats, padding = (beats + 1, padding) if s not in used else (beats, padding + 1)
        used.add(s); cleared.append(name)
    return dict(layers=len(layers), beats=beats, padding=padding, cleared=cleared, reached=True, stuck=None)
tale = walk(TALE, ALL)
padded = walk(TALE[:2] + [(f"box{i}", ("raven",)) for i in (1, 2, 3)] + TALE[2:], ALL)
no_salmon = walk(TALE, ALL - {"salmon"})
or_route = walk([(n, ("salmon", "rope") if n == "well" else s) for n, s in TALE], ALL - {"salmon"})
one_helper = walk([(n, ("wish",)) for n, _ in TALE], {"wish"})
print(f"1) tale nesting: {tale['layers']} layers, {tale['beats']} new beats, {tale['padding']} padding, heart reached {tale['reached']}")
print(f"2) padded with 3 raven-key boxes: {padded['layers']} layers, {padded['beats']} beats, {padded['padding']} padding")
print(f"3) salmon never helped: stuck at the {no_salmon['stuck']} after clearing {len(no_salmon['cleared'])} layers, reached {no_salmon['reached']}")
print(f"4) well opens to salmon OR rope, salmon missing: reached {or_route['reached']}, beats {or_route['beats']}")
print(f"BREAK one helper opens every layer: {one_helper['layers']} layers, {one_helper['beats']} beat(s)")
ok = (tale["beats"], tale["padding"], tale["reached"]) == (5, 0, True) and (padded["layers"], padded["beats"], padded["padding"]) == (8, 5, 3) \
     and (no_salmon["stuck"], len(no_salmon["cleared"]), no_salmon["reached"]) == ("well", 3, False) and or_route["reached"] \
     and (one_helper["layers"], one_helper["beats"]) == (5, 1)
print(("RESULT: PASS " if ok else "RESULT: FAIL ") + f"the tale's {tale['layers']} layers give {tale['beats']} new beats because each needs a different solver; "
      f"3 extra key-locked boxes add {padded['padding']} padding and 0 beats; one missing helper stops the quest at the {no_salmon['stuck']} "
      f"unless that layer has an OR route; a single helper that opens everything turns 5 layers into {one_helper['beats']} beat")
