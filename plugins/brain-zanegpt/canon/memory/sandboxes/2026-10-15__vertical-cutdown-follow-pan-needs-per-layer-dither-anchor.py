"""Edge pass: world-anchored Bayer dithering + tension-as-information-gap + fail-ad cut-downs (beat-anchored).

Hand-written model of a 1-bit fixable-fail game ad (160x90 world, 30 fps) re-cut to 9:16 (50x90 crop).
Beat sheet (from local__fail-ad-cutdowns-keep-the-gap): hook 0-3, setup 3-8, attempt 8-20, near-win 20-22,
fail 22-26, end card 26-30. The gap the ad sells: the player fails a few pixels short of a visible goal.
Gap kept = fail beat >= 2 s on screen, ending within 0.5 s of the card, AND the goal visible in >= 90%
of fail frames. Vertical framings: static centre crop, or a follow-pan on the player (clamped to world).
Dither: 4x4 Bayer, pixel on when tone > (M+0.5)/16, index from screen x, from x + foreground camera
(world-anchored, the kernel), or from each layer's own scrolled coordinate (per-layer). Background layer
scrolls at 0.5x the camera (parallax), foreground at 1x.
Swim = share of layer pixels visible in two consecutive sampled frames (every 3rd frame of the moving
attempt and near-win shots, compared when the rounded camera moved) whose bit flips.
Prediction (written before the first run): 4x4 Bayer gives 17 coverage levels. Master 16:9 static camera:
swim 0 for every anchoring, gap kept in 30 s. Centre crop: gap lost at every length (goal off-frame) even
with beat-anchored cuts. Follow-pan: goal visible, gap kept with beat-anchored cuts at 10/15/20/30 s and
truncated cuts only at 30 s; screen-anchored swim > 0.2 on both layers; world-anchored foreground swim 0
but background swim > 0.2 (break); per-layer swim 0 on both. Pure stdlib, deterministic."""

M = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
FPS, WW, WH, CW = 30, 160, 90, 50
GOAL_X, HORIZON = 152, 60
BEATS = [("hook", 0, 3), ("setup", 3, 8), ("attempt", 8, 20), ("near", 20, 22), ("fail", 22, 26), ("card", 26, 30)]

def levels17():
    cov = set()
    for k in range(0, 161):
        t = k / 160
        cov.add(sum(1 for r in M for m in r if t > (m + 0.5) / 16))
    return len(cov)

def player_x(t):  # master timeline position of the player
    if t < 3: return 10 + 20 * t / 3
    if t < 8: return 30 + 10 * (t - 3) / 5
    if t < 20: return 40 + 90 * (t - 8) / 12
    if t < 22: return 130 + 15 * (t - 20) / 2
    return 145.0

def tone(layer, lx, y):  # smooth mid-tone gradients so every Bayer level appears
    if layer == "bg": return 0.25 + 0.5 * ((lx * 7 + y * 3) % 64) / 64
    return 0.35 + 0.3 * ((lx * 5 + y * 11) % 48) / 48

def cam(framing, t):
    if framing == "master": return 0.0
    if framing == "centre": return (WW - CW) / 2
    return max(0.0, min(WW - CW, player_x(t) - CW / 2))

def frame(framing, t, anchor):
    w = WW if framing == "master" else CW
    c = cam(framing, t)
    out = {}
    for y in range(WH):
        layer, f = ("bg", 0.5) if y < HORIZON else ("fg", 1.0)
        off = round(c * f)
        for sx in range(w):
            lx = sx + off
            if anchor == "screen": ix = sx
            elif anchor == "world": ix = sx + round(c)
            else: ix = lx
            out[(layer, lx, y)] = 1 if tone(layer, lx, y) > (M[y & 3][ix & 3] + 0.5) / 16 else 0
    return out

def cut(L, how):
    """Returns list of (beat, master_start, master_end) segments in playback order."""
    if L == 30: return [(n, a, b) for n, a, b in BEATS]
    body = L - 4
    if how == "truncate":
        segs, used = [], 0.0
        for n, a, b in BEATS[:-1]:
            take = min(b - a, body - used)
            if take > 0: segs.append((n, a, a + take)); used += take
        return segs + [("card", 26, 30)]
    keep = {"hook": 3, "fail": 4}
    left = body - 7
    if left < 0: return [("hook", 0, 3), ("fail", 22, 22 + max(0, body - 3)), ("card", 26, 30)]
    segs = {}
    for n in ("near", "setup", "attempt"):
        a, b = [(x, y) for m, x, y in BEATS if m == n][0]
        take = min(b - a, left)
        if take > 0: segs[n] = (b - take, b) if n == "near" or n == "attempt" else (a, a + take)
        left -= take
    order = ["hook", "setup", "attempt", "near", "fail"]
    out = []
    for n in order:
        if n in keep: a = [x for m, x, y in BEATS if m == n][0]; out.append((n, a, a + keep[n]))
        elif n in segs: out.append((n,) + segs[n])
    return out + [("card", 26, 30)]

def gap_kept(framing, segs):
    total = sum(b - a for _, a, b in segs)
    pos = 0.0
    for n, a, b in segs:
        if n == "fail":
            dur, end = b - a, pos + (b - a)
            frames = [a + i / FPS for i in range(int(round(dur * FPS)))]
            c = [cam(framing, t) for t in frames]
            w = WW if framing == "master" else CW
            vis = sum(1 for cc in c if cc <= GOAL_X < cc + w) / max(1, len(frames))
            return dur >= 2 and abs((total - 4) - end) <= 0.5 and vis >= 0.9, vis
        pos += b - a
    return False, 0.0

print("Bayer 4x4 coverage levels:", levels17())
table = {}
for framing in ("master", "centre", "follow"):
    for L in (6, 10, 15, 20, 30):
        for how in ("truncate", "anchor"):
            if framing == "master" and L != 30: continue
            k, vis = gap_kept(framing, cut(L, how))
            table[(framing, L, how)] = k
    print(framing, {f"{L}{h[0]}": int(v) for (f, L, h), v in table.items() if f == framing})

sw = {}
for framing in ("master", "follow"):
    segs = [s for s in cut(30, "anchor") if s[0] in ("attempt", "near")]  # the moving shots
    shots = [[a + i / FPS for i in range(int((b - a) * FPS))][::3] for _, a, b in segs]  # every 3rd frame pair-checked
    for anchor in ("screen", "world", "layer"):
        # compare consecutive sampled frames only if the camera moved between them
        flips = {"bg": [0, 0], "fg": [0, 0]}
        for times in shots:
            prev, pc = None, None
            for t in times:
                c = cam(framing, t); cur = frame(framing, t, anchor)
                if prev is not None and round(c) != round(pc):
                    for kk, v in cur.items():
                        if kk in prev: flips[kk[0]][0] += v != prev[kk]; flips[kk[0]][1] += 1
                prev, pc = cur, c
        sw[(framing, anchor)] = {l: (a / b if b else 0.0) for l, (a, b) in flips.items()}
        print(f"swim {framing:6s} {anchor:6s} bg {sw[(framing, anchor)]['bg']:.3f} fg {sw[(framing, anchor)]['fg']:.3f}")

ok = (levels17() == 17 and table[("master", 30, "anchor")]
      and not any(table[("centre", L, h)] for L in (6, 10, 15, 20, 30) for h in ("truncate", "anchor"))
      and all(table[("follow", L, "anchor")] for L in (10, 15, 20, 30)) and not table[("follow", 6, "anchor")]
      and not any(table[("follow", L, "truncate")] for L in (6, 10, 15, 20))
      and all(v == 0 for a in ("screen", "world", "layer") for v in sw[("master", a)].values())
      and sw[("follow", "screen")]["bg"] > 0.2 and sw[("follow", "screen")]["fg"] > 0.2
      and sw[("follow", "world")]["fg"] == 0 and sw[("follow", "world")]["bg"] > 0.2
      and sw[("follow", "layer")]["fg"] == 0 and sw[("follow", "layer")]["bg"] == 0)
print("RESULT:", "PASS" if ok else "FAIL",
      f"centre crop keeps the gap in 0/10 cuts (goal off-frame); follow-pan beat-anchored keeps it at 10/15/20/30 s, truncated only at 30 s; "
      f"master static swim 0 everywhere; follow-pan swim screen bg {sw[('follow','screen')]['bg']:.3f} fg {sw[('follow','screen')]['fg']:.3f}, "
      f"world-anchored fg {sw[('follow','world')]['fg']:.3f} but parallax bg {sw[('follow','world')]['bg']:.3f}, per-layer bg {sw[('follow','layer')]['bg']:.3f} fg {sw[('follow','layer')]['fg']:.3f}")
