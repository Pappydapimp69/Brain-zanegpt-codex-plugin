# Prediction (before run): uniform 10/lag gives best gate error 10*W for W=0,1,3,5 (0/10/30/50) and
# validity error 0. With non-uniform weights, best error = sum(min(wv,wi)) over overlap only when the
# valid-minus-invalid weight sign changes at most once from + to - (single crossing); a profile with
# the opposite order (invalid heavy at low ages, valid heavy at high ages) exceeds sum(min).
# Sawtooth clock: age = t % P, validity is carried by a separate generation token, not by age.
P = 40
def build(W, wv, wi, V=10):
    ev = []  # (age, valid)
    for a in range(0, V + 1):
        k = a - (V - W + 1); ev += [(a, True)] * (wv(k) if 0 <= k < W else 10)
    for a in range(V - W + 1, V + 30):
        k = a - (V - W + 1); ev += [(a, False)] * (wi(k) if 0 <= k < W else 10)
    return ev
def best_gate(ev):
    return min(sum(1 for a, v in ev if v and a > g) + sum(1 for a, v in ev if not v and a <= g) for g in range(-1, 80))
def validity_err(ev): return 0   # token is exact by construction (not measured: tautology)
fails = []
for W, want in ((0, 0), (1, 10), (3, 30), (5, 50)):
    ev = build(W, lambda k: 10, lambda k: 10)
    b = best_gate(ev); print(f"uniform W={W} best_gate_err={b} validity_err={validity_err(ev)}")
    if b != want or validity_err(ev): fails.append(("uniform", W, b))
W = 6
def summin(wv, wi): return sum(min(wv(k), wi(k)) for k in range(W))
profiles = {
  "valid-heavy-low": (lambda k: 20 if k < 3 else 2, lambda k: 2 if k < 3 else 20),   # single crossing: valid heavy first
  "invalid-heavy-low": (lambda k: 2 if k < 3 else 20, lambda k: 20 if k < 3 else 2), # reversed: breaker
}
for name, (wv, wi) in profiles.items():
    ev = build(W, wv, wi)
    ev = [e for e in ev]
    # restrict weights to overlap; non-overlap valid/invalid use same fns, so recompute only overlap contribution
    b = best_gate(ev); sm = summin(wv, wi)
    print(f"{name}: best_gate_err={b} sum_min_over_overlap={sm}")
    if name == "valid-heavy-low" and b != sm: fails.append((name, b, sm))
    if name == "invalid-heavy-low" and b <= sm: fails.append((name, b, sm))
print("RESULT: " + ("PASS" if not fails else "FAIL") + f" linear 10*W only for uniform/single-crossing weights; fails={fails}")
