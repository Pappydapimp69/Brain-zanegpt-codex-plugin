"""Toy model: a game-of-the-scene check column whose verdict is shown as an on-screen caption.
Verdict correctness (naive new-noun check vs derived-from-game check) and caption visibility
(safe-margin policy x 4 vertical viewports) are independent; a beat counts only if BOTH hold.
Deterministic, no RNG. Frame 1080x1920."""
H = 1920
# bottom UI band (px) in four viewports; top band; strictest per film/E11: top 240, bottom 660
VIEWPORTS = {"a": (120, 250), "b": (180, 400), "c": (200, 530), "d": (240, 660)}  # (top, bottom) px hidden
CAP_H = 90
# beats: (name, true_X, introduces_new_noun, derived_from_game)
BEATS = [("b1",1,1,1),("b2",1,0,1),("b3",0,1,0),("b4",0,0,0),("b5",0,1,0),("b6",1,1,1),("b7",1,0,1),("b8",0,1,0)]  # true_X == derived_from_game (E1 ground truth)
# truth: X = beat is derived from the game. new-noun is the naive proxy.
def naive(b): return b[2]
def derived(b): return b[3]
def visible(y_top, vp):
    top, bot = VIEWPORTS[vp]
    return y_top >= top and y_top + CAP_H <= H - bot
POL = {
  "broadcast90": H*0.05 + 0,                       # title-safe 90%: caption top at 5% from top edge region
  "strict_edges": 240,                             # strictest top margin, top-anchored band
  "mid_band": H*0.25,                              # y .25-.75 band start
  "bottom90": H*0.95 - CAP_H,                      # caption at broadcast-safe bottom
}
def score(checker, pol):
    ok_verdict = sum(1 for b in BEATS if checker(b) == b[1])
    vis = sum(visible(POL[pol], vp) for vp in VIEWPORTS)
    allvis = vis == len(VIEWPORTS)
    both = sum(1 for b in BEATS if checker(b) == b[1]) if allvis else 0
    return ok_verdict, vis, both
res = {}
for cname, c in (("naive", naive), ("derived", derived)):
    for pol in POL:
        v, vis, both = score(c, pol)
        res[(cname, pol)] = (v, vis, both)
        print(f"{cname:8s} {pol:12s} verdict {v}/8, caption visible in {vis}/4 viewports, usable beats {both}/8")
ok = (res[("naive","mid_band")][2] < res[("derived","mid_band")][2]          # correct check matters
      and res[("derived","bottom90")][2] == 0 and res[("derived","broadcast90")][2] == 0  # broadcast-safe fails
      and res[("derived","strict_edges")][2] == 8)                           # BREAK: strict top band + derived passes all
print("RESULT: PASS" if ok else "RESULT: FAIL",
      f"derived+bottom90 {res[('derived','bottom90')][2]}/8, derived+strict_edges {res[('derived','strict_edges')][2]}/8, naive+mid_band {res[('naive','mid_band')][2]}/8")
