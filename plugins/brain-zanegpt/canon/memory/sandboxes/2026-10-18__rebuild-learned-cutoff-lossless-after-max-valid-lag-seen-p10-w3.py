# own fixture: period 10 width 3 offset 4, presses every 2 ticks, 200 presses, outlier at index 150
P, W, OFF = 10, 3, 4
def legal(t): return (t + OFF) % P < W
ticks = [t for t in range(5, 2000) if legal(t)]
LAGS = [1, 2, 10, 11, 12, 20, 21]
presses = []
for i in range(200):
    t = ticks[i]
    lag = LAGS[(i * 3) % 4]            # lags 1, 11, 20, 2 -> small ones dominate
    if i % 11 == 10: lag = 12
    if i == 150: lag = 30              # single max-lag press
    presses.append((t, lag))
valid = [legal(t) and legal(t + l) for t, l in presses]   # hint available then and still legal now
vl = [l for (t, l), v in zip(presses, valid) if v]
off = max(vl)
first_max = next(i for i, ((t, l), v) in enumerate(zip(presses, valid)) if v and l == off)
def loss(c): return sum(1 for (t, l), v in zip(presses, valid) if v and l > c)
def learned(K): return max([l for (t, l), v in zip(presses[:K], valid[:K]) if v], default=0)
bad = [K for K in range(1, 201) if (loss(learned(K)) > 0) != (K <= first_max)]
print("valid", sum(valid), "offline max", off, "first max idx", first_max, "offline loss", loss(off),
      "period cutoff loss", loss(P), "loss at K=10,50,100,150,151:", [loss(learned(k)) for k in (10, 50, 100, 150, 151)])
ok = loss(off) == 0 and not bad and loss(P) > 0
print("RESULT: %s offline cutoff %d loses 0, learned loses >0 exactly for K<=%d (%d violations), period cutoff %d loses %d"
      % ("PASS" if ok else "FAIL", off, first_max, len(bad), P, loss(P)))
