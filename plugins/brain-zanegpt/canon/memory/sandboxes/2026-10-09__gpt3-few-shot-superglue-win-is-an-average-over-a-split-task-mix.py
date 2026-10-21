"""Sandbox: does 'GPT-3 few-shot (32 ex) beat fine-tuned BERT-Large on SuperGLUE' hold,
and where does it stop holding?  Stdlib only, no RNG, no timing.

PREDICTION (written before the first run):
  P1 the SuperGLUE average recomputed from the per-task test scores matches the table
     (GPT-3 71.8, BERT-Large 69.0, SOTA 89.0) to within 0.05.
  P2 GPT-3 beats BERT-Large on exactly 4 of 8 tasks (the paper's text) -> a 4-4 split.
  P3 dropping any ONE task keeps GPT-3 ahead (no single-task flip), but dropping the two
     biggest contributors (COPA and ReCoRD) flips the sign.
  P4 over a deterministic grid of task weightings (step 1/8, all 6435 mixes) GPT-3 leads
     in a clear majority but NOT all of them: share between 50% and 65%.
  P5 worst single-task gap vs BERT-Large is at least 15 points against GPT-3 (mean +2.8
     hides a tail of big losses).

Source of the numbers: Table 3.8 of arXiv:2005.14165 (pdftotext of the PDF, test set).
"""
from itertools import product

TASKS = ["BoolQ", "CB", "COPA", "RTE", "WiC", "WSC", "MultiRC", "ReCoRD"]
# each task = list of sub-metrics, task score = mean of its sub-metrics (SuperGLUE rule)
SOTA = {"BoolQ": [91.0], "CB": [96.9, 93.9], "COPA": [94.8], "RTE": [92.5], "WiC": [76.1],
        "WSC": [93.8], "MultiRC": [62.3, 88.2], "ReCoRD": [92.5, 93.3]}
BERT = {"BoolQ": [77.4], "CB": [83.6, 75.7], "COPA": [70.6], "RTE": [71.7], "WiC": [69.6],
        "WSC": [64.6], "MultiRC": [24.1, 70.0], "ReCoRD": [71.3, 72.0]}
GPT3 = {"BoolQ": [76.4], "CB": [75.6, 52.0], "COPA": [92.0], "RTE": [69.0], "WiC": [49.4],
        "WSC": [80.1], "MultiRC": [30.5, 75.4], "ReCoRD": [90.2, 91.1]}
TABLE_AVG = {"SOTA": 89.0, "BERT": 69.0, "GPT3": 71.8}

def score(m, t):
    return sum(m[t]) / len(m[t])

def avg(m, w=None):
    w = w or {t: 1 for t in TASKS}
    return sum(w[t] * score(m, t) for t in TASKS) / sum(w.values())

results = []
def check(name, ok, detail):
    results.append(ok)
    print(("ok   " if ok else "FAIL ") + name + ": " + detail)

# --- Scenario 1: reproduce the table averages from the per-task scores
a = {k: avg(m) for k, m in (("SOTA", SOTA), ("BERT", BERT), ("GPT3", GPT3))}
print("recomputed averages:", {k: round(v, 2) for k, v in a.items()})
check("P1 averages match table", all(abs(a[k] - TABLE_AVG[k]) <= 0.05 for k in a),
      "diffs " + str({k: round(a[k] - TABLE_AVG[k], 3) for k in a}))

# --- Scenario 2: win count per task and per sub-metric
d = {t: score(GPT3, t) - score(BERT, t) for t in TASKS}
wins_t = [t for t in TASKS if d[t] > 0]
subs = [(t, i) for t in TASKS for i in range(len(GPT3[t]))]
wins_s = [s for s in subs if GPT3[s[0]][s[1]] > BERT[s[0]][s[1]]]
print("per-task gap (GPT3 - BERT):", {t: round(d[t], 2) for t in TASKS})
print("task wins:", wins_t, "| sub-metric wins: %d of %d" % (len(wins_s), len(subs)))
check("P2 4 of 8 tasks", len(wins_t) == 4, "%d of 8" % len(wins_t))
lead = a["GPT3"] - a["BERT"]
print("mean lead: %+.2f ; gap to SOTA: %.2f" % (lead, a["SOTA"] - a["GPT3"]))

# --- Scenario 3 (BREAK): drop tasks and see if the lead survives
flip1 = [t for t in TASKS if sum(d[u] for u in TASKS if u != t) <= 0]
min_lead_1 = min(sum(d[u] for u in TASKS if u != t) / 7 for t in TASKS)
top2 = sorted(TASKS, key=lambda t: -d[t])[:2]
lead_wo_top2 = sum(d[u] for u in TASKS if u not in top2) / 6
print("drop-one flips:", flip1, "| smallest drop-one lead %+.2f" % min_lead_1)
print("drop top-2 contributors", top2, "lead %+.2f" % lead_wo_top2)
check("P3 no single flip, top-2 flips", not flip1 and lead_wo_top2 < 0,
      "single flips=%d, top2 lead=%+.2f" % (len(flip1), lead_wo_top2))

# --- Scenario 4 (BREAK, Simpson-style): re-weight the task mix over a full grid
D = [d[t] for t in TASKS]
steps = 8
total = lead_pos = 0
for comp in product(range(steps + 1), repeat=len(TASKS) - 1):
    last = steps - sum(comp)
    if last < 0:
        continue
    w = list(comp) + [last]
    total += 1
    if sum(wi * di for wi, di in zip(w, D)) > 0:
        lead_pos += 1
share = lead_pos / total
print("weighting grid: %d mixes, GPT-3 ahead in %d (%.1f%%)" % (total, lead_pos, 100 * share))
check("P4 share in [50%,65%]", 0.50 <= share <= 0.65, "%.1f%% of %d mixes" % (100 * share, total))

# single-task-focused mixes: tasks where the lead flips if one family is the whole benchmark
only = {t: d[t] > 0 for t in TASKS}
print("benchmark = one task only, GPT-3 ahead:", [t for t in TASKS if only[t]])

# --- Scenario 5: metric choice (first sub-metric only / last sub-metric only)
first = {t: [GPT3[t][0]] for t in TASKS}, {t: [BERT[t][0]] for t in TASKS}
last = {t: [GPT3[t][-1]] for t in TASKS}, {t: [BERT[t][-1]] for t in TASKS}
lf = avg(first[0]) - avg(first[1]); ll = avg(last[0]) - avg(last[1])
print("lead using first sub-metric %+.2f, last sub-metric %+.2f" % (lf, ll))
check("lead survives metric choice", lf > 0 and ll > 0, "%+.2f / %+.2f" % (lf, ll))

# --- Scenario 6: the tail (mean hides it) and nearness to SOTA
worst = min(TASKS, key=lambda t: d[t])
print("worst task vs BERT: %s %+.2f ; WiC vs chance(50): GPT3 %.1f" % (worst, d[worst], GPT3["WiC"][0]))
check("P5 worst gap <= -15", d[worst] <= -15, "%s %+.2f" % (worst, d[worst]))
near = [t for t in TASKS if score(SOTA, t) - score(GPT3, t) <= 3.0]
print("tasks within 3 points of fine-tuned SOTA:", near)
check("close to SOTA on exactly 2 tasks", len(near) == 2, str(near))

ok = all(results)
print("RESULT: %s lead %+.2f on mean (71.8 vs 69.0) but %d/8 task wins, %.1f%% of %d task mixes, drop COPA+ReCoRD -> %+.2f, worst task %s %+.1f" % (
    "PASS" if ok else "FAIL", lead, len(wins_t), 100 * share, total, lead_wo_top2, worst, d[worst]))
