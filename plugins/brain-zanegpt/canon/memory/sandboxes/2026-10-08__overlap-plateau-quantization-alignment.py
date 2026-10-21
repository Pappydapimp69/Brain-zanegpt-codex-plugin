# Prediction (before run): with N=10 events per lag, valid lags 0..V, invalid lags V-W+1..V+60,
# the unquantized best gate error is N*W on a plateau of W+1 gates (V-W..V).
# A gate quantized to g = k*q-1 reaches N*W iff that plateau contains such a g,
# so quantization raises the floor for SOME (q,V) pairs (misaligned) and never for q <= W+1.
N = 10
def err(g, V, W):
    lost = sum(N for lag in range(0, V + 1) if lag > g)
    wrong = sum(N for lag in range(V - W + 1, V + 61) if lag <= g)
    return lost + wrong
fails = []; mis = 0; tot = 0
for V in (40, 47, 55, 63):
    for W in (1, 3, 10):
        floor = min(err(g, V, W) for g in range(-1, V + 70))
        plateau = [g for g in range(-1, V + 70) if err(g, V, W) == floor]
        for q in (4, 10, 16, 20, 25):
            gs = [k * q - 1 for k in range(0, 20)]
            qb = min(err(g, V, W) for g in gs)
            has = any(g in plateau for g in gs)
            tot += 1; mis += (qb > floor)
            ok = (qb == floor) == has and floor == N * W and len(plateau) == W + 1 and (q > W + 1 or True)
            if q <= W + 1 and qb != floor: ok = False
            if not ok: fails.append((V, W, q, floor, qb))
print(f"cases={tot} floor_inflated_by_quantization={mis} plateau_len=W+1 floor=N*W")
print("RESULT: " + ("PASS" if not fails else "FAIL") + f" quantized floor == N*W iff plateau holds a frame edge; fails={fails}")
