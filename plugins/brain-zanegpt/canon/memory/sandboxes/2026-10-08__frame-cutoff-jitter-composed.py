# Prediction (written before run): with L=100ms valid lag, j=5ms jitter,
# cutoff=ceil((L+j)/q) frames loses 0 valid events for every q in {16,15,19,20,33};
# cutoff=ceil(L/q) loses >0 at q where ceil(L/q)*q < L+j (q=16: 112>105 ok->0; q=20: 100<105 ->lost>0);
# floor(L/q) loses >0 for q not dividing L. Over-acceptance of invalid events stays < q ms.
import math
L, J = 100, 5
def run(q, cutoff, L=L, J=J):
    lost = 0; over = 0
    for lag in range(0, L + 1):           # valid events, nominal lag
        for jit in range(-J, J + 1):      # deterministic jitter sweep
            m = lag + jit
            if m < 0: continue
            if math.ceil(m / q) > cutoff: lost += 1
    for m in range(L + J + 1, L + J + 200):  # invalid events (measured lag beyond L+J)
        if math.ceil(m / q) <= cutoff: over += 1
    return lost, over
fails = []
for q in (16, 15, 19, 20, 33, 5, 1):
    fl = run(q, L // q); c0 = run(q, math.ceil(L / q)); cj = run(q, math.ceil((L + J) / q))
    print(f"q={q:2d} floor lost={fl[0]:4d} | ceil(L/q) lost={c0[0]:4d} | ceil((L+j)/q) lost={cj[0]} over={cj[1]}")
    if cj[0] != 0: fails.append(("jitter-ceil lost", q))
    if cj[1] >= q: fails.append(("over-accept>=q", q))
    if q > 1 and L % q and fl[0] == 0: fails.append(("floor no loss", q))
# breaker: j=0 should make ceil(L/q) sufficient
for q in (16, 19, 33):
    if run(q, math.ceil(L / q), J=0)[0] != 0: fails.append(("j=0 ceil(L/q) lost", q))
print("RESULT: " + ("PASS" if not fails else "FAIL") + f" ceil((L+j)/q) zero loss across q; fails={fails}")
