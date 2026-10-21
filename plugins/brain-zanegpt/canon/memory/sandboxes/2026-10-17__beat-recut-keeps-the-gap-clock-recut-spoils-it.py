# Sandbox: recut a winning 25 s ad to shorter lengths three ways and check the information-gap reveal survives.
# Beats: (role, seconds). Checks at the target length: hook shown >=2 s, reveal present >=2 s,
# gap = reveal_start - gap_open_end >= 3 s (viewer has time to wonder), and CTA present.
ORIG = [("hook", 3), ("open", 3), ("filler", 4), ("build", 6), ("filler", 3), ("reveal", 4), ("cta", 2)]
MINS = {"hook": 2, "open": 2, "build": 3, "reveal": 2, "cta": 1}
def check(beats):
    t, open_end, rev_start, got = 0.0, None, None, {}
    for r, d in beats:
        if r == "open": open_end = t + d
        if r == "reveal": rev_start = t
        got[r] = got.get(r, 0) + d
        t += d
    ok = (got.get("hook", 0) >= 2 and got.get("reveal", 0) >= 2 and "cta" in got
          and open_end is not None and rev_start is not None and rev_start - open_end >= 3)
    return ok
def clock_tail(T):                    # keep the first T seconds
    out, t = [], 0
    for r, d in ORIG:
        if t >= T: break
        out.append((r, min(d, T - t))); t += d
    return out
def squeeze(T):                       # scale every beat by T/25
    k = T / 25
    return [(r, d * k) for r, d in ORIG]
def beat_recut(T):                    # drop filler, then shrink the rest toward minimums, never below
    beats = [(r, d) for r, d in ORIG if r != "filler"]
    excess = sum(d for _, d in beats) - T
    out = []
    for r, d in beats:
        cut = min(max(excess, 0), d - MINS[r]); excess -= cut; out.append((r, d - cut))
    return out if excess <= 1e-9 else None
res = {}
for T in (20, 15, 10, 8):
    bc = beat_recut(T)
    res[T] = (check(clock_tail(T)), check(squeeze(T)), bc is not None and check(bc))
    print("T=%2d  tail-trim:%s  squeeze:%s  beat-recut:%s" % ((T,) + tuple("ok" if x else "FAIL" for x in res[T])))
beat_pass = [T for T in res if res[T][2]]
clk_pass = [T for T in res if res[T][0]]
sq_pass = [T for T in res if res[T][1]]
ok = beat_pass == [20, 15, 10] and clk_pass == [] and sq_pass == [20]
print("RESULT: %s beat recut keeps the gap down to %ds (passes %s), tail trim passes only %s, uniform squeeze passes %s; below 10s nothing works (8s fails)"
      % ("PASS" if ok else "FAIL", min(beat_pass) if beat_pass else 0, beat_pass, clk_pass, sq_pass))
