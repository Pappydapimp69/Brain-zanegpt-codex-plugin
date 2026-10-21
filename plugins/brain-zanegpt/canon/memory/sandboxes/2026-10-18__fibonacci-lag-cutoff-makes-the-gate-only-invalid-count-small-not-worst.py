# Composes: age-cutoff-lossless-threshold-exceeds-period-p12 (cutoff on validity is lossless at
# the largest valid lag), lossless-cutoff-is-worst-without-validity (gate-only invalid count
# grows with that lag; periodic formula (N/P)*min(L,W,P-L,P-W)), and
# sandbox-quasiperiodic-near-recovery-at-fibonacci-lags (quasiperiodic signals nearly recover
# at Fibonacci lags). Question: on a Fibonacci-word legality signal does "the lossless cutoff is
# the worst gate-only cutoff" still hold, or do Fibonacci lags break it?
# invalid(L) = count of t with legal(t) and not legal(t+L), over N = 600 (a hint naming B is
# stale when B has gone). Fibonacci word: 1 -> 10, 0 -> 1 ; legal = symbol 1.
N, MAXL = 600, 120
w = "1"
while len(w) < N + MAXL + 5:
    w = "".join("10" if c == "1" else "1" for c in w)
S = [c == "1" for c in w]
def invalid(L):
    return sum(1 for t in range(N) if S[t] and not S[t + L])
def match(L):
    return sum(1 for t in range(N) if S[t] == S[t + L])
fib = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
inv = {L: invalid(L) for L in range(1, MAXL + 1)}
# Prediction (before run): at lag 55 and 89 gate-only invalid <= 10 of 600 (near recovery),
# the median invalid over lags 40..70 excluding Fibonacci lags is at least 3x invalid(55), and
# invalid is NOT monotone in lag (unlike the periodic formula's rise to its plateau); BREAK:
# periodic P12 W5 signal at the same N where invalid(L) = (N/P)*min(L,W,P-L,P-W) is monotone
# up to L=W and its minimum over L 1..11 is at L=1.
others = sorted(inv[L] for L in range(40, 71) if L not in fib)
med = others[len(others) // 2]
nonmono = any(inv[L + 1] < inv[L] for L in range(1, MAXL))
P, W = 12, 5
per = lambda L: sum(1 for t in range(N) if (t % P) < W and not ((t + L) % P) < W)
per_ok = all(per(L) == (N // P) * min(L, W, P - L, P - W) for L in range(1, P))
print("fib lags invalid:", {L: inv[L] for L in fib if L <= MAXL})
print("median invalid lags 40..70 non-Fibonacci=%d; nonmonotone=%s; periodic formula exact=%s" % (med, nonmono, per_ok))
ok = inv[55] <= 10 and inv[89] <= 10 and med >= 3 * inv[55] and nonmono and per_ok
print("RESULT: %s Fibonacci-word gate-only invalid %d at lag 55 and %d at lag 89 versus median %d at nearby lags; not monotone in lag; periodic formula exact on 11 lags"
      % ("PASS" if ok else "FAIL", inv[55], inv[89], med))
