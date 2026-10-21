# Sandbox: hand-typed sidecar (label -> id) drifting under an IPM x D1 ranking,
# with tracked-vs-ranked counts as the tripwire (composes collective-reference/E1,
# rank-ipm-times-d1.../E1, brain-film-explainer/E4).
import random

# "upstream" source of truth: variants with true conversion (ipm/1000) and D1
UP = {"v1": ("cold-open-a", .040, .30), "v2": ("cold-open-b", .045, .28),
      "v3": ("cold-open-c", .050, .22), "v4": ("cold-open-d", .035, .45),
      "v5": ("cold-open-e", .042, .31), "v6": ("cold-open-f", .038, .40)}

def measure(ids, n, seed):
    r = random.Random(seed); out = {}
    for i in ids:
        _, p, d1 = UP[i]
        inst = sum(r.random() < p for _ in range(n))
        ret = sum(r.random() < d1 for _ in range(inst))
        out[i] = (inst / n, (ret / inst) if inst else 0.0)
    return out

def pick(ids, n, seed):
    m = measure(ids, n, seed)
    return max(ids, key=lambda i: m[i][0] * m[i][1])

def pick_wins(ids, n, seeds=range(40)):
    from collections import Counter
    return Counter(pick(ids, n, s) for s in seeds)

truth = max(UP, key=lambda i: UP[i][1] * UP[i][2])   # v4 (0.0158)
# hand-typed sidecar: keyed by LABEL; upstream renamed v4's label, sidecar stale
SIDE = {UP[i][0]: i for i in UP}
SIDE.pop("cold-open-d"); SIDE["cold-open-d-old"] = "v4"
live_labels = [UP[i][0] for i in UP]
sidecar_ids = [SIDE[l] for l in live_labels if l in SIDE]
derived_ids = [i for i in UP]                        # derived from source

N = 2000
res = {}
# 1) drift: v4 silently absent, no error raised
w1 = pick_wins(sidecar_ids, N); res["drift_pick_is_truth"] = w1.get(truth, 0)
# 2) derived map: truth recovered most of the time
w2 = pick_wins(derived_ids, N); res["derived_truth_wins"] = w2.get(truth, 0)
# 3) BREAK: drift drops a non-winner (v3): pick should be unchanged
ids3 = [i for i in derived_ids if i != "v3"]
w3 = pick_wins(ids3, N); res["dropped_loser_truth_wins"] = w3.get(truth, 0)
# 4) budget: at 100 impressions even derived map is unreliable
w4 = pick_wins(derived_ids, 100); res["derived_truth_wins_at_100"] = w4.get(truth, 0)
# 5) high budget: derived map should recover truth reliably
w5 = pick_wins(derived_ids, 20000); res["derived_truth_wins_at_20000"] = w5.get(truth, 0)
# tripwire: tracked (source) vs ranked count, labelled separately
tracked, ranked = len(UP), len(sidecar_ids)
res["tracked"], res["ranked"] = tracked, ranked
print(res)
ok = (res["drift_pick_is_truth"] == 0 and res["derived_truth_wins_at_20000"] >= 20
      and res["derived_truth_wins_at_20000"] > res["derived_truth_wins"] > res["derived_truth_wins_at_100"]
      and tracked != ranked)
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
      f"drift picks truth 0/40; derived recovery 100:{res['derived_truth_wins_at_100']} "
      f"2000:{res['derived_truth_wins']} 20000:{res['derived_truth_wins_at_20000']} of 40; "
      f"loser-drop(2000) {res['dropped_loser_truth_wins']}/40; tracked {tracked} vs ranked {ranked}")
