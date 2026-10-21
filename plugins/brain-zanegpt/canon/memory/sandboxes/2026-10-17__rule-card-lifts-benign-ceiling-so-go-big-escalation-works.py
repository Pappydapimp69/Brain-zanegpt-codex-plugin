# NOTE: the predicted totals below were hand-computed wrongly (run gave 0.70/1.40, 2.20/1.75, 1.67/1.40); the predicted ORDERING held.
# Prediction (before run): beat laugh = v if v<=b else max(0, v - 3*(v-b)) (v violation 0..1, b benign cover).
# 6-beat schedules: go-big v = 1/6..6/6, mild v = 1/12..6/12. No rule card: b = 0.40 fixed grounded distance
# -> go-big total 1.25 < mild total 1.75 (mild wins; escalation-needs-matching-distance). A Jones-style rule card
# (harm only to the lead's own tools, humiliated not harmed) adds +0.30 benign cover -> b=0.70 -> go-big total
# 3.00 beats mild 1.75. Hidden assumption: the rule card raises benign cover without capping violation.
# BREAK: an over-strict card that also caps violation at 0.30 gives go-big total 1.80 and mild 1.50 but both
# below the unconstrained-card go-big 3.00: the card pays only while its violation cap is above the schedule's needs.
def laugh(v, b): return v if v <= b else max(0.0, v - 3 * (v - b))
def total(sched, b, cap=1.0): return sum(laugh(min(v, cap), b) for v in sched)
big = [i / 6 for i in range(1, 7)]
mild = [i / 12 for i in range(1, 7)]
res = {
 "nocard": (total(big, 0.40), total(mild, 0.40)),
 "card": (total(big, 0.70), total(mild, 0.70)),
 "strictcard": (total(big, 0.70, 0.30), total(mild, 0.70, 0.30)),
}
for k, (a, b) in res.items(): print(k, "go-big %.2f mild %.2f winner %s" % (a, b, "go-big" if a > b else "mild"))
ok = res["nocard"][0] < res["nocard"][1] and res["card"][0] > res["card"][1] and res["strictcard"][0] < res["card"][0]
print(f"RESULT: {'PASS' if ok else 'FAIL'} no card big {res['nocard'][0]:.2f} vs mild {res['nocard'][1]:.2f}; card big {res['card'][0]:.2f} vs mild {res['card'][1]:.2f}; strict card big {res['strictcard'][0]:.2f}")
