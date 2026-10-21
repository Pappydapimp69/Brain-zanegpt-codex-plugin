"""Sandbox: localStorage + opt-in export telemetry vs a cookieless hit counter, deterministic (no RNG, no clock).
Prediction (written before the first run; items 1b and 3 turned out WRONG on run 1, see PREDICTION CHECK at the bottom):
 1) Aggregated per-player stats export stays under the 2000-char chat limit from 10 to 100000 runs; a raw per-run log
    export passes 2000 chars below 100 runs and hits a 5,000,000-char localStorage quota before 100000 runs, after which
    writes FAIL and data is lost.
 2) Two populations with different per-player best times but equal total runs give IDENTICAL hit-counter state (counter
    cannot answer per-player questions) yet different exports.
 3) Opt-in export is self-selected: if only high-run players export, the mean best time from exports is biased by more
    than 10% vs the true population mean, while the hit-counter total of run-completed events is exact.
 4) Zero egress until the player acts: network bytes 0 after 1000 runs, then exactly one payload after one click."""
import json

QUOTA = 5_000_000
CHAT = 2000

class Store:
    def __init__(self): self.d, self.fail = {}, 0
    def set(self, k, v):
        if len(k) + len(v) + sum(len(a) + len(b) for a, b in self.d.items() if a != k) > QUOTA:
            self.fail += 1; return False
        self.d[k] = v; return True

def run_time(i, r): return 60 + (i * 7 + r * 13) % 41     # seconds, deterministic
def died(i, r): return (i + r) % 3 == 0

def play(store, i, runs, mode):
    best, deaths, lost = 999, 0, 0
    log = []
    for r in range(runs):
        t, d = run_time(i, r), died(i, r)
        best, deaths = min(best, t), deaths + d
        if mode == "agg":
            ok = store.set("stats", json.dumps({"runs": r + 1, "deaths": deaths, "best": best}))
        else:
            log.append([t, int(d)]); ok = store.set("log", json.dumps(log))
        lost += not ok
    return lost

# S1: size vs runs, aggregate vs raw log (real Store, real json sizes, no closed forms)
def sizes_at(runs):
    a, l = Store(), Store()
    play(a, 1, runs, "agg"); play(l, 1, runs, "log")
    return len(a.d["stats"]), len(l.d["log"])
lo = next(n for n in range(1, 2000) if sizes_at(n)[1] > CHAT)           # exact first run count whose raw log exceeds chat limit
agg_max = max(sizes_at(n)[0] for n in (10, 100, 1000, 5000))
per_run = (sizes_at(5000)[1] - sizes_at(4000)[1]) / 1000
quota_runs = int(QUOTA / per_run)
q = Store(); q.d["x"] = "y" * (QUOTA - 400)
lost = play(q, 2, 200, "log")
print(f"S1 agg_max={agg_max} log_over_chat_at={lo} bytes/run={per_run:.1f} quota_at~{quota_runs} runs, writes lost on near-full origin={lost}")
s1 = agg_max < CHAT and lo < 1000 and lost > 0

# S2: hit counter vs exports on two populations with equal total runs
def population(shift):
    P = []
    for i in range(40):
        runs = 5 + (i * 7) % 30
        times = [run_time(i, r) + (shift if i % 2 else -shift) for r in range(runs)]
        P.append((i, runs, times))
    return P
def counter_state(pop):  # GoatCounter-style: path -> count
    c = {}
    for _, runs, _ in pop: c["event/run-completed"] = c.get("event/run-completed", 0) + runs
    return c
def export(pop): return [json.dumps({"p": i, "runs": n, "best": min(t)}) for i, n, t in pop]
A, B = population(0), population(20)
s2 = counter_state(A) == counter_state(B) and export(A) != export(B)
print("S2", s2, "counter", counter_state(A), "exports differ:", export(A) != export(B))

# S3 BREAK: self-selected export bias, swept over who exports (runs >= k)
pop = population(15)
true_mean = sum(min(t) for _, _, t in pop) / len(pop)
sweep = {}
for k in (5, 15, 25, 30, 33):
    ex = [min(t) for _, n, t in pop if n >= k]
    sweep[k] = (len(ex), round(abs(sum(ex) / len(ex) - true_mean) / true_mean, 3))
counter_exact = counter_state(pop)["event/run-completed"] == sum(n for _, n, _ in pop)
print("S3 (k: (exporters, relative bias)) =", sweep, "counter_exact =", counter_exact)
worst = max(b for _, b in sweep.values())

# S4: egress
store = Store(); play(store, 3, 1000, "agg")
egress = 0; e0 = egress
egress += len(store.d["stats"])
s4 = e0 == 0 and egress > 0
print("S4", s4, "egress before click", e0, "after one click", egress)

pred_quota_before_100k = quota_runs < 100000          # my prediction 1b
pred_bias_over_10pct = worst > 0.10                    # my prediction 3
print("PREDICTION CHECK: chat-limit crossover below 100 runs?", lo < 100, "| quota hit before 100000 runs?", pred_quota_before_100k,
      "| export bias > 10%?", pred_bias_over_10pct, f"(worst {worst})")
kernel_ok = s1 and s2 and counter_exact and s4
print("RESULT:", "PASS" if kernel_ok else "FAIL",
      f"kernel claims hold (agg export <= {agg_max} chars; raw log passes chat limit at {lo} runs; counter identical across populations={s2}, total exact={counter_exact}; egress 0 until click={s4}); "
      f"my numeric predictions refuted: quota needs ~{quota_runs} runs not <100000; export bias {sweep[25][1]} with {sweep[25][0]}/40 exporting, over 10% only when {sweep[33][0]}/40 export")
