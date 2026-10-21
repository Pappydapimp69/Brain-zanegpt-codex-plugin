"""Deterministic model of the empathy-selection task.
Agent i has effort cost c_i (evenly spaced 0..1, 100 agents). Each trial it picks the
empathy deck iff efficacy_belief * BENEFIT - cost > 0 (BENEFIT=1.0). No RNG."""
N = 100
COSTS = [(i + 0.5) / N for i in range(N)]
B = 1.0

def share(eff, cost_shift=0.0, moral=0.0, costs=COSTS):
    return sum(1 for c in costs if eff * B + moral - (c + cost_shift) > 0) / len(costs)

checks = []
def chk(name, ok, detail):
    checks.append(ok); print(("ok   " if ok else "MISS ") + name + ": " + detail)

# S1 control: baseline belief 0.355 -> ~35% choose empathy (kernel: 35.53%)
base = share(0.355)
chk("S1 control share ~0.35", abs(base - 0.355) <= 0.02, f"{base:.3f}")

# S2 false efficacy feedback (belief raised, true accuracy untouched)
TRUE_ACC = 0.30
fb = share(0.51)
chk("S2 false feedback lifts share to ~0.5", abs(fb - 0.51) <= 0.02 and TRUE_ACC == 0.30,
    f"{base:.2f}->{fb:.2f}, true accuracy still {TRUE_ACC}")

# S3 REAL feedback (belief tracks true accuracy 0.30 < prior 0.355): avoidance WORSENS
real = share(TRUE_ACC)
chk("S3 honest feedback lowers share", real < base, f"{base:.2f}->{real:.2f}")

# S4 BREAK: cost ceiling. Raise efficacy to max 1.0 -> only agents with cost<1 flip;
# with a high-cost subpopulation (cost>=1, overload e.g. moderators) feedback is inert.
heavy = [1.0 + i / N for i in range(40)] + COSTS[:60]
h0, h1 = share(0.355, costs=heavy), share(1.0, costs=heavy)
chk("S4 break: feedback cannot flip cost>=benefit agents", h1 <= 0.60 + 1e-9 and h1 < 1.0,
    f"share {h0:.2f}->{h1:.2f} (40% overloaded stay out)")

# S5 hot-cold gap (sibling kernel): choice FORECAST in calm state vs actual in hot state
HOT_SHIFT = 0.25
forecast = share(0.51)                    # calm forecast, post-feedback
actual = share(0.51, cost_shift=HOT_SHIFT)
chk("S5 calm forecast overstates hot-state empathy", forecast - actual >= 0.2,
    f"forecast {forecast:.2f} vs actual {actual:.2f}")

# S6 exhortation (moral term) vs feedback of equal size
exh = share(0.355, moral=0.155)
chk("S6 exhortation equal-size lever matches in calm", abs(exh - fb) <= 0.02, f"{exh:.2f}")
exh_hot = share(0.355, cost_shift=HOT_SHIFT, moral=0.155)
chk("S6b both levers decay under hot cost", abs(exh_hot - actual) <= 0.02, f"{exh_hot:.2f} vs {actual:.2f}")

ok = all(checks)
print(f"RESULT: {'PASS' if ok else 'FAIL'} {sum(checks)}/{len(checks)} checks; control {base:.2f}, false-feedback {fb:.2f}, honest {real:.2f}, overloaded {h0:.2f}->{h1:.2f}, calm-forecast {forecast:.2f} vs hot {actual:.2f}")
