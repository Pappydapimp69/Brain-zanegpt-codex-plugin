# P=15, W=5 one-sided legality. Press issued at tick s with nominal lag L lands at s+L(+J on every 7th press).
# Hint was legal at issue iff s mod P < W; press is VALID if legal at issue and legal at landing; INVALID-EXEC if
# executed by a gate although legal-at-issue and illegal at landing (one-sided, per the sandbox-one-sided lesson).
P, W, N = 15, 5, 600
LAGS = list(range(1, 25))
def presses(J):
    out = []; k = 0
    for s in range(N):
        L = LAGS[s % len(LAGS)]; k += 1
        eff = L + (J if k % 7 == 0 else 0)
        out.append((s, L, eff))
    return out
legal = lambda t: t % P < W
def stats(J):
    ps = presses(J); valid = [(s, L, e) for s, L, e in ps if legal(s) and legal(s+e)]
    inval = [(s, L, e) for s, L, e in ps if legal(s) and not legal(s+e)]
    return ps, valid, inval
rows = []
for J in (0, 2, 4, 8):
    ps, valid, inval = stats(J)
    maxvalid = max(e for _, _, e in valid)               # gate on EFFECTIVE (landing) lag
    lost = lambda c: sum(1 for _, _, e in valid if e > c)
    lossless = min(c for c in range(0, 40) if lost(c) == 0)
    gate_inv = lambda c: sum(1 for _, _, e in inval if e <= c)   # gate-only executes everything within cutoff
    allc = {c: gate_inv(c) for c in range(0, 40)}
    worst = max(allc.values()); worstc = [c for c, v in allc.items() if v == worst][0]
    maxinv = max(e for _, _, e in inval)
    rows.append((J, maxvalid, lossless, allc[lossless], worst, worstc))
    print(f"J={J}: max valid lag {maxvalid} lossless cutoff {lossless} gate-only invalid at lossless {allc[lossless]} (max over cutoffs {worst} first reached at {worstc}) highest invalid-capable effective lag {maxinv}")
ok = all(r[1] == r[2] for r in rows) and all(r[3] == r[4] for r in rows)
maxinvs=[stats(J)[2] for J in (0,2,4,8)]
maxinvs=[max(e for _,_,e in x) for x in maxinvs]
print('worst cutoff reached vs highest invalid-capable lag', [r[5] for r in rows], maxinvs)
print(f"RESULT: {'PASS' if ok else 'FAIL'} lossless == max valid effective lag at J 0/2/4/8: {[r[2] for r in rows]}; gate-only invalid at it equals the max over cutoffs in {sum(r[3]==r[4] for r in rows)}/4 cases: {[r[3] for r in rows]} vs {[r[4] for r in rows]}")
