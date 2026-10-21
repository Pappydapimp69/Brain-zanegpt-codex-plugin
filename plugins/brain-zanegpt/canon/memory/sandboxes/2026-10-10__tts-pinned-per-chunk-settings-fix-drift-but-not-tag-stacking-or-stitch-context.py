"""Prediction (before run): a 12-chunk document, first-call-only style leaves 11 chunks at default (drift),
pinning identical settings per chunk gives 0 drifted chunks, passing previous_text/next_text stitching context
WITHOUT pinning still leaves 11 drifted; stacking contradictory tags in one pinned chunk blends (valence 0.0 for
excited(+1)/sorrowful(-1)) and is caught by the gold diff, and style slider 0.9 gives instability flag while 0.6 does not.
HAND-WRITTEN MODEL of a TTS API (no network): output = f(request only). Modeled, not a real service."""
GOLD = {"valence": 1.0, "style": 0.6}   # human-approved reference read for this voice/style
DEFAULT = {"valence": 0.0, "style": 0.0}

def synth(text, tags, settings, stitch=None):
    """Stateless: nothing from earlier calls is visible. stitch only smooths boundary prosody."""
    s = {**DEFAULT, **settings}
    val = 0.0
    if tags:
        val = sum(tags) / len(tags)          # averaging, not alternation
    else:
        val = s.get("valence", 0.0)
    unstable = s["style"] > 0.75 or len(tags) > 3
    return {"valence": val, "style": s["style"], "prosody_smooth": stitch is not None, "unstable": unstable}

def gold_diff(out):
    return out["valence"] != GOLD["valence"] or out["style"] != GOLD["style"] or out["unstable"]

N = 12
SETTINGS = {"valence": 1.0, "style": 0.6}
def run(mode):
    outs = []
    for i in range(N):
        st = SETTINGS if (mode == "pinned" or i == 0) else {}
        stitch = ("prev", "next") if mode in ("stitch_only", "pinned") else None
        outs.append(synth("chunk%d" % i, [], st, stitch))
    return outs

res = {}
for mode in ("first_only", "stitch_only", "pinned"):
    res[mode] = sum(gold_diff(o) for o in run(mode))
# stacking inside a pinned pipeline (BREAK case for 'pinning fixes it'): chunk 5 carries excited + sorrowful tags
stack = synth("c5", [1.0, -1.0], SETTINGS, ("prev", "next"))
res["stack_valence"] = stack["valence"]; res["stack_flagged"] = gold_diff(stack)
res["style_0.9_unstable"] = synth("c", [], {"valence": 1.0, "style": 0.9})["unstable"]
res["style_0.6_unstable"] = synth("c", [], {"valence": 1.0, "style": 0.6})["unstable"]
res["stitch_flag_set"] = run("pinned")[3]["prosody_smooth"] and not run("first_only")[3]["prosody_smooth"]
print(res)
ok = (res["first_only"] == 11 and res["stitch_only"] == 11 and res["pinned"] == 0
      and res["stack_valence"] == 0.0 and res["stack_flagged"]
      and res["style_0.9_unstable"] and not res["style_0.6_unstable"] and res["stitch_flag_set"])
print("RESULT:", "PASS" if ok else "FAIL",
      "drifted first_only=%d stitch_only=%d pinned=%d; stack valence=%.1f flagged=%s; unstable@0.9=%s @0.6=%s" % (
      res["first_only"], res["stitch_only"], res["pinned"], res["stack_valence"], res["stack_flagged"],
      res["style_0.9_unstable"], res["style_0.6_unstable"]))
