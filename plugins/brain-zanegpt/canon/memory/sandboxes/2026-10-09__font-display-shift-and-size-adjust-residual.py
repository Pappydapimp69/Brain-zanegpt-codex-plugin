"""Deterministic font-display timeline model. No RNG, no real timing.
Prediction (written before first run): only `optional` yields 0 shift for EVERY
load time; swap/fallback/block shift whenever the font lands after the block
period (and fallback only inside its 3000ms swap window); a single size-adjust
factor tuned on average width leaves a nonzero per-string residual (both signs).
"""
INF = float("inf")
# (block_ms, swap_ms) per web.dev's description (UA-defined, not normative)
PERIODS = {"block": (3000, INF), "swap": (0, INF), "fallback": (100, 3000), "optional": (100, 0)}

# per-char advance widths at 16px (units px). Fallback ~ Arial-like, web font wider on some letters.
FB = {c: 8.9 for c in "abcdeghnopqu"}
FB.update({c: 3.6 for c in "ilj"}); FB.update({c: 4.4 for c in "frt"}); FB.update({c: 8.0 for c in "kscvxyz"})
FB.update({c: 13.3 for c in "mw"}); FB.update({c: 10.7 for c in "ABCDEHKNRSTUVXYZ"}); FB.update({"I": 4.4, " ": 4.4})
FB.update({c: 14.2 for c in "MW"}); FB.update({c: 9.8 for c in "FGLOPQ"}); FB.update({c: 8.9 for c in "dfJ"} )
WEB = {c: w * (1.0 + (0.12 if c in "ilj frt" else -0.02 if c in "mwMW" else 0.07)) for c, w in FB.items()}
def width(s, table): return sum(table.get(c, 8.9) for c in s)

def timeline(display, t_load, t_probe):
    """face shown and visibility at t_probe for a font that arrives at t_load."""
    block, swap = PERIODS[display]
    if t_probe < block:
        return ("web", True) if t_load <= t_probe else ("none", False)   # invisible during block
    if t_load < block + swap and t_load <= t_probe:   # lands in block or swap window: web font sticks
        return ("web", True)
    return ("fallback", True)

def run(display, t_load, s, horizon=10000):
    """-> (invisible_ms, shift_px, swapped). shift = width jump when face changes visibly."""
    prev, invis, shift = None, 0, 0.0
    for t in range(0, horizon, 10):
        face, vis = timeline(display, t_load, t)
        if not vis: invis += 10
        if vis:
            w = width(s, WEB if face == "web" else FB)
            if prev is not None and w != prev: shift += abs(w - prev)
            prev = w
    return invis, round(shift, 1)

STR = "Settings"
LOADS = [50, 90, 150, 1000, 4000, INF]
res = {d: [run(d, L, STR) for L in LOADS] for d in PERIODS}
print("S1 timeline (invisible_ms, shift_px) per load time", LOADS)
for d, r in res.items(): print(f"  {d:9s}", r)
opt_zero = all(sh == 0 for _, sh in res["optional"])
others_shift = {d: any(sh > 0 for _, sh in r) for d, r in res.items() if d != "optional"}
print("S2 optional zero-shift for every load:", opt_zero, "| others shift somewhere:", others_shift)
# S3 BREAK: block/fallback also give 0 shift when the font lands inside the window that hides/never swaps
cond0 = {d: [L for L, (_, sh) in zip(LOADS, res[d]) if sh == 0] for d in ("block", "fallback", "swap")}
print("S3 zero-shift load times for non-optional values:", cond0)
# S4 size-adjust: ONE factor tuned on avg width over a corpus, residual per string (kernel: measure real string)
corpus = ["Settings", "Illinois", "Wi-Fi mm", "minimum", "Filter", "ill", "WWW", "Profile", "jiffy", "Quick links"]
k = sum(width(s, FB) for s in corpus) / sum(width(s, WEB) for s in corpus)   # fallback scaled to web-font total
resid = {s: round(width(s, FB) / k - width(s, WEB), 1) for s in corpus}
print("S4 size-adjust factor %.4f residual px per string:" % k, resid)
signs = {(v > 0) - (v < 0) for v in resid.values() if abs(v) >= 0.5}
worst = max(abs(v) for v in resid.values())
# S5 reflow: for label boxes 60..200px wide, a swap flips fit/wrap for a string when its two widths straddle the box
flips = {s_: [bx for bx in range(60, 201) if (width(s_, FB) <= bx) != (width(s_, WEB) <= bx)] for s_ in corpus}
wrap = {s_: bool(v) for s_, v in flips.items()}
box = "60-200"
print("S5 strings with a box width where fit flips on swap (box range, count):", {s_: len(v) for s_, v in flips.items() if v})
ok = opt_zero and all(others_shift.values()) and len(signs) == 2 and worst >= 1.0 and any(wrap.values())
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
      f"optional shift 0 on all {len(LOADS)} loads; block/swap/fallback shift on late loads; "
      f"size-adjust residual up to {worst}px with both signs {sorted(signs)}; {sum(wrap.values())} strings flip wrap at {box}px")
