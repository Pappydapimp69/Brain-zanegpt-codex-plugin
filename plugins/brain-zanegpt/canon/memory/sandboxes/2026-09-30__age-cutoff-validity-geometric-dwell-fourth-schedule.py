# Deterministic sandbox: age cutoff stacked on a validity guard, geometric-dwell schedule.
# PREDICTION (written before run): dwells 1,2,4,...,128 (8 dwells, 255 ticks). A press is
# issued at every tick; its lag = ticks since its state's dwell began. Validity alone keeps
# all presses whose state is current (255 valid). Age cutoff c drops presses with lag>c.
# Predicted loss closed form: sum over dwells d of max(0, d-1-c) ... at c=0,2,8,127,128.
def schedule():
    out = []
    for k in range(8):
        d = 2 ** k
        for lag in range(d):       # lag 0..d-1 within dwell of length d
            out.append(lag)
    return out

def loss(lags, c):
    return sum(1 for l in lags if l > c)

def closed(c):
    return sum(max(0, (2 ** k - 1) - c) for k in range(8))

lags = schedule()
assert len(lags) == 255 and max(lags) == 127
res = {}
for c in (0, 2, 8, 127, 128):
    res[c] = loss(lags, c)
    assert res[c] == closed(c), (c, res[c], closed(c))
    print("cutoff", c, "lost", res[c], "of", len(lags))
# break scenario: cutoff one below max lag must lose exactly the presses at max lag (1)
assert loss(lags, 126) == 1 and loss(lags, 127) == 0
# validity alone (no cutoff) is lossless and legal: every press has a current state
assert loss(lags, 10**9) == 0
ok = res[0] == 247 and res[127] == 0
print("RESULT:", "PASS" if ok else "FAIL", "loss", res)
