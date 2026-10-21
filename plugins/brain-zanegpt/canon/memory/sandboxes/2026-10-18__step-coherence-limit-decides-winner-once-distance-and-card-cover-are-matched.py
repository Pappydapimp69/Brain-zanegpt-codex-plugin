# Sandbox: three lessons together.
#  (1) escalation-needs-matching-distance: gate g = exp(-((d - I/C)/0.25)^2).
#  (2) rule-card cover: g' = g + c*(1-g).
#  (3) sandbox-comedy-escalation: habituation exp(-0.2 X), X += 1/(1+I/5), and a
#      step-coherence limit: a jump larger than L costs exp(-((jump-L)/3)^2).
# Question: once distance is matched (gate saturated, card inert), does the
# coherence limit take over and decide which schedule wins?
import math

C, L, N = 10.0, 3.0, 6
SCHEDS = {
    "flat":   [10, 10, 10, 10, 10, 10],
    "linear": [2, 3.5, 5, 6.5, 8, 10],
    "three":  [1, 3, 9, 9, 9, 9],
    "mild":   [1, 2, 2, 3, 3, 3],
}

def score(sched, dist, c=0.0, coherence=True):
    X, prev, tot = 0.0, 1.0, 0.0
    for I in sched:
        d = dist(I)
        g = math.exp(-((d - I / C) / 0.25) ** 2)
        g = g + c * (1 - g)
        coh = math.exp(-((max(0.0, I - prev - L)) / 3.0) ** 2) if coherence else 1.0
        tot += (I / C) * math.exp(-0.2 * X) * g * coh * 10
        X += 1 / (1 + I / 5)
        prev = I
    return tot

def table(dist, c, coh):
    return {k: score(v, dist, c, coh) for k, v in SCHEDS.items()}

best = lambda t: max(t, key=t.get)
matched = lambda I: I / C
close = lambda I: 0.3

# Prediction (before run): matched + no coherence -> flat wins; matched + coherence
# -> a ramp (linear or three) beats flat; card c=0.8 changes matched scores by <1e-9;
# fixed close d=0.3 with card c=0.5 and coherence -> flat does NOT win (card flip lost).
T = {}
T["matched_nocoh"] = table(matched, 0.0, False)
T["matched_coh"] = table(matched, 0.0, True)
T["matched_coh_card"] = table(matched, 0.8, True)
T["close_nocard_coh"] = table(close, 0.0, True)
T["close_card_coh"] = table(close, 0.5, True)   # BREAK: card flip with coherence
T["close_card_nocoh"] = table(close, 0.5, False)
for k, t in T.items():
    print("%-18s best=%-6s " % (k, best(t)) + " ".join("%s=%.2f" % (a, b) for a, b in t.items()))
inert = max(abs(T["matched_coh"][k] - T["matched_coh_card"][k]) for k in SCHEDS)
# Original prediction (flat dethroned at L=3) was REFUTED above: flat's single big jump
# costs it only a one-time factor. Iteration 2: sweep the coherence limit L to find where
# the winner does flip (BREAK scenario for the "coherence decides" claim).
flip = None
L_SAVED = L
for tenth in range(30, 0, -1):
    globals()['L'] = tenth / 10.0
    if best(table(matched, 0.0, True)) != "flat":
        flip = globals()['L']
        break
globals()['L'] = L_SAVED
print("flat share kept at L=3 vs no coherence: %.3f" % (T["matched_coh"]["flat"] / T["matched_nocoh"]["flat"]))
print("largest L (0.1..3.0) at which a ramp beats flat under matched distance: %s" % flip)
ok = (best(T["matched_nocoh"]) == "flat" and best(T["matched_coh"]) == "flat"
      and inert < 1e-9 and flip is None
      and best(T["close_card_coh"]) == "flat")
print("RESULT: %s coherence at L=3 does not dethrone flat (%.2f vs 51.12 ungated); card inert diff=%.1e; no ramp beats flat at any L from 3.0 down to 0.1 (flip=%s), because the step cost hits only beat 1; close d with card keeps flat winner under coherence"
      % ("PASS" if ok else "FAIL", T["matched_coh"]["flat"], inert, flip))
