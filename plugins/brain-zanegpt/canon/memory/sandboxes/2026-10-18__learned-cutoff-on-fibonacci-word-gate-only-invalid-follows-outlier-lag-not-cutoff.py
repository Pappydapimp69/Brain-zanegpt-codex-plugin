def fibword(n):
    a, b = "1", "0"          # 1->10, 0->1 : start "1"
    s = "1"
    while len(s) < n:
        s = "".join("10" if c == "1" else "1" for c in s)
    return [c == "1" for c in s[:n]]
S = fibword(4000)
def run(outlier, K, P=500):
    presses = []
    for i in range(P):
        t = 3 * i + 1
        lag = 1 + i % 5
        if i % 7 == 6:
            lag = outlier
        presses.append((t, lag))
    valid = [S[t] and S[t + l] for t, l in presses]
    cut = max([l for (t, l), v in zip(presses[:K], valid[:K]) if v], default=0)
    off = max([l for (t, l), v in zip(presses, valid) if v], default=0)
    def gate_inv(c):
        ex = [(t, l) for t, l in presses if l <= c]
        return sum(1 for t, l in ex if S[t] and not S[t + l]), len(ex)
    def valid_loss(c):
        return sum(1 for (t, l), v in zip(presses, valid) if v and l > c)
    global OUT_INV
    OUT_INV = sum(1 for i, (t, l) in enumerate(presses) if i % 7 == 6 and S[t] and not S[t + l])
    return cut, off, gate_inv(cut), gate_inv(off), valid_loss(cut), valid_loss(off)
res = {}
for out in (55, 89, 60, 70, 34):
    res[out] = run(out, 140)
    print("  outlier-press-only invalid (of 71):", OUT_INV)
    print("outlier", out, "learned,off", res[out][:2], "gate inv/exec at learned", res[out][2],
          "at offline", res[out][3], "valid loss learned,off", res[out][4:])
rate = lambda o: res[o][3][0] / res[o][3][1]
fib = max(rate(55), rate(89)); non = min(rate(60), rate(70))
print("rates fib %.3f nonfib %.3f" % (fib, non))
ok = fib < 0.10 and non > 0.20 and all(r[5] == 0 for r in res.values())
print("RESULT: %s offline gate-only invalid rate fib-outlier %.3f vs nonfib %.3f; offline valid loss 0; learned cutoffs %s"
      % ("PASS" if ok else "FAIL", fib, non, {o: res[o][0] for o in res}))
