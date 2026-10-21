# Deterministic sandbox: treat commit-veto refusals as contradicting observations to a held target belief.
# Prediction (before run): hold-forever wastes all ticks when A is permanently blocked (0 work);
# release-on-first-refusal thrashes under 1-in-4 transient refusals (< 80% of the work of staying put);
# recent-margin release (3 refusals in last 6) gets the best total across the 3 streams, except it
# loses to hold on a 3-tick transient burst (the break case).
T = 40; SWITCH_COST = 2; VAL = {"A": 2, "B": 1}
def streams():
    perm = {t: ("A",) if True else () for t in range(T)}            # A refused every tick
    perm_ref = lambda t, tgt: tgt == "A"
    noise_ref = lambda t, tgt: tgt == "A" and t % 4 == 3            # transient 1-in-4
    burst_ref = lambda t, tgt: tgt == "A" and 10 <= t < 13           # 3-tick burst, then free
    return {"permanent": perm_ref, "noise": noise_ref, "burst3": burst_ref}
def run(policy, refused):
    cur, work, wasted, hist, stall, switches, banned = "A", 0, 0, [], 0, 0, set()
    for t in range(T):
        if stall > 0:
            stall -= 1; wasted += 1; continue
        if t < 5 and False: pass
        ok = not refused(t, cur)
        hist.append(0 if ok else 1)
        if ok: work += VAL[cur]
        else: wasted += 1
        refusals = sum(hist[-6:])
        release = (policy == "first" and not ok) or (policy == "margin" and refusals >= 3)
        if release and cur == "A" and t >= 0:
            # B only becomes visible from tick 5 (predicate widening); hold never looks anyway
            if t >= 5 or True:
                cur = "B"; stall = SWITCH_COST; switches += 1; hist = []
        if policy == "first" and cur == "B" and not refused(t + 1, "A"):
            cur = "A"; stall = SWITCH_COST; switches += 1; hist = []   # re-evaluating selector prefers best-ranked
    return work, wasted, switches
out = {}
for name, ref in streams().items():
    out[name] = {p: run(p, ref) for p in ("hold", "first", "margin")}
    print(name, out[name])
tot = {p: sum(out[n][p][0] for n in out) for p in ("hold", "first", "margin")}
print("total work", tot)
c1 = out["permanent"]["hold"][0] == 0
c2 = out["noise"]["first"][0] < 0.8 * out["noise"]["hold"][0]
c3 = tot["margin"] > tot["hold"] and tot["margin"] > tot["first"]
c4 = out["burst3"]["margin"][0] < out["burst3"]["hold"][0]
print("checks", c1, c2, c3, c4)
print("RESULT: %s totals %s; permanent hold work %d; noise first %d vs hold %d; burst3 margin %d vs hold %d"
      % ("PASS" if (c1 and c2 and c3 and c4) else "FAIL", tot, out["permanent"]["hold"][0],
         out["noise"]["first"][0], out["noise"]["hold"][0], out["burst3"]["margin"][0], out["burst3"]["hold"][0]))
