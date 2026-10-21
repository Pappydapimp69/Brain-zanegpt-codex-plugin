"""Compose sandbox-edges/E37 (overflow can be transient: check every intermediate
state) with sandbox-typography-measure/E1 (avg-char-width estimates err -38%..+163%).
Status bar width 200 px at 16 px; per-glyph em widths are an assumed Arial-like table.
A message sequence overwrites one slot; we compare four checkers over the sequence:
 final-only/measured, every-state/measured, every-state/avg-estimate, every-state/avg+20% slack.
Truth = measured width > BAR. Count missed overflows (false negatives) and false alarms."""
EM = {}
for c in "il.,: 1jtfI'": EM[c] = 0.27
for c in "mwMW@": EM[c] = 0.85
for c in "abcdeghnopqsuvxyzkrABCDEFGHJKLNOPQRSTUVXYZ0123456789-/": EM[c] = 0.55
def meas(s, px=16): return sum(EM.get(c, 0.55) for c in s) * px
ALPHA = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
AVG = sum(EM.get(c, 0.55) for c in ALPHA) / len(ALPHA) * 16
BAR = 200
def est(s): return AVG * len(s)
seqs = []
# 12 sequences x 5 states; deterministic message pool mixes narrow-heavy and wide-heavy text
pool = ["Illinoisill filling", "Wildlife in Willow Mill", "Saved", "Connecting to server now please wait",
        "WWW MMM WWW", "Mum swims with Wim", "Loading...", "Ill till fill", "Network error: retry later",
        "Item picked up", "MWMWMWMWMWMWMWMWMW", "Level up! Welcome to Milltown", "Quest log updated just now"]
for i in range(12):
    seqs.append([pool[(i * 5 + j * 3) % len(pool)] for j in range(5)])
def run(check, slack=1.0):
    miss = false = 0
    for seq in seqs:
        truth = [meas(m) > BAR for m in seq]
        if check == "final":
            says = [False] * 4 + [meas(seq[-1]) > BAR]
        elif check == "meas":
            says = truth
        else:
            says = [est(m) * slack > BAR for m in seq]
        miss += sum(t and not s for t, s in zip(truth, says))
        false += sum(s and not t for t, s in zip(truth, says))
    return miss, false
res = {"final_meas": run("final"), "every_meas": run("meas"),
       "every_avg": run("avg"), "every_avg_slack20": run("avg", 1.2)}
total_true = sum(meas(m) > BAR for s in seqs for m in s)
for k, v in res.items(): print(k, "missed", v[0], "false_alarms", v[1])
print("true overflow states:", total_true, "of", sum(len(s) for s in seqs), "avg char px", round(AVG, 2))
ok = (res["every_meas"] == (0, 0) and res["final_meas"][0] > 0
      and res["every_avg"][0] + res["every_avg"][1] > 0
      and res["every_avg_slack20"][0] + res["every_avg_slack20"][1] > 0)
print("RESULT:", "PASS" if ok else "FAIL",
      f"of {total_true} overflow states final-only missed {res['final_meas'][0]}; every-state avg estimate missed {res['every_avg'][0]} "
      f"+ {res['every_avg'][1]} false alarms; with 20% slack {res['every_avg_slack20'][0]} missed + {res['every_avg_slack20'][1]} false; measured every-state 0/0")
