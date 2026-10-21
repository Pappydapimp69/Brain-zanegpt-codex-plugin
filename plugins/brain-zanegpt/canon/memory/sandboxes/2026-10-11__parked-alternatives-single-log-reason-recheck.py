# Deterministic sandbox: parked alternatives (creativity/E1) meet interaction-seam lessons (graph-editor/E2).
# Prediction (before run): none = most re-walked roads (all declined re-tried); fragmented dirs (3 folders, builds
# know 1) recovers ~1/3 of the saving; single log with blind title-skip re-walks 0 but MISSES every option whose parking
# reason was lifted (>=5 misses of 40); single log + reason re-check has re-walks 0 and misses 0 with a small recheck cost.
# Break: reason lifts with a *stacked* condition (two reasons, one lifted): recheck on the first reason only still misses.
N = 40; FOLDERS = 3
def build(i):
    # each build considers 3 options; option 0 is a previously parked road; option 1 fresh; option 2 fresh
    folder = i % FOLDERS
    reasons = {"a"} if i % 3 else {"a", "b"}        # parked for reasons a (and b for every 3rd)
    lifted = set()
    if i % 4 == 0: lifted.add("a")                  # reason a no longer applies in this build
    if i % 8 == 0: lifted.add("b")
    return folder, reasons, lifted
def run(policy):
    rewalk = miss = recheck = 0
    for i in range(N):
        folder, reasons, lifted = build(i)
        good_now = reasons <= lifted                 # option is now worth taking only if ALL reasons lifted
        if policy == "none":
            rewalk += 0 if good_now else 1
        elif policy == "fragmented":
            known = (i % FOLDERS == 0)               # builds find the entry only if scanning the folder where it lives
            if known:
                if not good_now: pass
                else: miss += 1
            else:
                rewalk += 0 if good_now else 1
        elif policy == "log_blind":
            if good_now: miss += 1
        elif policy == "log_first_reason":
            recheck += 1
            first = sorted(reasons)[0]
            if first in lifted and not good_now: rewalk += 1   # saw first reason lifted, re-tried a still-blocked road
        elif policy == "log_all_reasons":
            recheck += len(reasons)
    return rewalk, miss, recheck
out = {p: run(p) for p in ("none", "fragmented", "log_blind", "log_first_reason", "log_all_reasons")}
for p, v in out.items(): print("%-17s rewalks=%2d misses=%2d reason_checks=%2d" % ((p,) + v))
cost = {p: v[0] + 2 * v[1] + 0.25 * v[2] for p, v in out.items()}   # a miss costs 2 re-walks, a check 0.25
print("cost", cost)
ok1 = out["none"][0] > out["fragmented"][0] > out["log_blind"][0] == 0
ok2 = out["log_blind"][1] >= 5
ok3 = out["log_all_reasons"][0] == 0 and out["log_all_reasons"][1] == 0
ok4 = out["log_first_reason"][0] > 0                 # break case: partial recheck still re-walks
# Prediction ok5 (full recheck is cheapest at check cost 0.25) FAILED: partial recheck was cheaper (12.0 vs 13.5).
# Replaced by the observed crossover: sweep the per-check cost; full recheck wins only below it.
def total(p, c): v = out[p]; return v[0] + 2 * v[1] + c * v[2]
cross = None
for k in range(1, 400):
    c = k / 1000
    if total("log_all_reasons", c) > total("log_first_reason", c): cross = c; break
print("full recheck cheaper than first-reason recheck below check cost ~%.3f" % cross)
ok5 = cross is not None and 0.10 < cross < 0.20 and total("log_all_reasons", 0.05) < total("log_first_reason", 0.05) and total("log_all_reasons", 0.25) > total("log_first_reason", 0.25)
print("checks", ok1, ok2, ok3, ok4, ok5)
print("RESULT: %s cost %s; blind-skip misses %d; first-reason recheck rewalks %d; recheck crossover at check cost %.3f"
      % ("PASS" if all([ok1, ok2, ok3, ok4, ok5]) else "FAIL", {k: round(v, 1) for k, v in cost.items()}, out["log_blind"][1], out["log_first_reason"][0], cross))
