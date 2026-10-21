# Rebuild of: an age filter (above threshold) on top of validity costs exactly (N/P)*min(lag,W,P-W,P-lag) hint uses.
# Own fixture: hint = legal(t-lag); fidelity = presses whose final action equals the hint's action.
# validity-only: keep hint unless it says "go" while live is illegal (then re-derive -> "no").
# validity + age filter (lag > thr): always re-derive from live state.
def legal(t, P, W): return ((t + 7) % P) < W
def fid(N, P, W, lag, thr, age):
    f = 0
    for t in range(N):
        hint, live = legal(t - lag, P, W), legal(t, P, W)
        if age and lag > thr: act = live
        elif hint and not live: act = False
        else: act = hint
        f += act == hint
    return f
thr = 1
cases = [(720, 12, 5, 4, "base"), (720, 12, 5, 7, "base lag>P/2"), (720, 12, 9, 3, "W>P/2"), (720, 12, 5, 12, "whole-cycle lag -> 0"),
         (700, 20, 3, 10, "W small"), (725, 12, 5, 4, "BREAK N%P!=0"), (720, 12, 5, 1, "BREAK lag<=thr -> filter inactive")]
ok = True; out = []
for N, P, W, lag, lab in cases:
    v, a = fid(N, P, W, lag, thr, False), fid(N, P, W, lag, thr, True)
    pred = (N / P) * min(lag, W, P - W, P - lag) if lag > thr else 0
    hit = (v - a) == pred
    print(f"{lab:28s} N{N} P{P} W{W} lag{lag}: validity={v} +age={a} cost={v-a} formula={pred:.2f} match={hit}")
    if not lab.startswith("BREAK"): ok &= hit
    else: out.append((lab, v - a, pred))
print("RESULT: %s cost = (N/P)*min(lag,W,P-W,P-lag) on all 5 in-scope shapes incl. W>P/2 and whole-cycle 0; break: %s" % ("PASS" if ok else "FAIL", "; ".join(f"{l} cost {c} vs {p:.2f}" for l, c, p in out)))
