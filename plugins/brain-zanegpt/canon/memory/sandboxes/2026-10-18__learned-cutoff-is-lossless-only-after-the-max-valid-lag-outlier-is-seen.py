# Composes: age-cutoff-lossless-threshold-exceeds-period-p12 (cutoff lossless exactly at the
# largest valid lag, period irrelevant), lossless-cutoff-is-worst-without-validity (the same
# cutoff admits (N/P)*min(L,W,P-L,P-W) invalid presses without validity), and
# validity-cutoff-jitter-amplitude-sweep-sixth-angle (jitter outliers set the max valid lag).
# New question: a cutoff LEARNED online as the running max valid lag -- when is it lossless?
# Wave P12 W4: B available when t mod 12 < 4. Press i issued at t_i = 3*i+1, lag L_i; valid iff
# B available at t_i+L_i. Lags: base (i%5)+1 plus a jitter on every 7th press cycling 6, 13, 21.
P, W, N = 12, 4, 140
def lag(i):
    base = i % 5 + 1
    return base + ([6, 13, 21][(i // 7) % 3] if i % 7 == 6 else 0)
presses = [(3 * i + 1, lag(i)) for i in range(N)]
valid = [((t + L) % P) < W for t, L in presses]
vlags = [L for (t, L), v in zip(presses, valid) if v]
maxv = max(vlags)
first_max = next(i for i, ((t, L), v) in enumerate(zip(presses, valid)) if v and L == maxv)
# Prediction (before run): offline cutoff = max valid lag loses 0; a cutoff learned
# from the first K presses (running max valid lag, frozen after K) loses >0 for every K up to
# the first press that carries the max valid lag and 0 from then on; BREAK: the period-based
# cutoff 12 loses all valid presses above 12.
def loss(cut):
    return sum(1 for (t, L), v in zip(presses, valid) if v and L > cut)
def learned(K):
    m = 0
    for (t, L), v in zip(presses[:K], valid[:K]):
        if v and L > m: m = L
    return m
Ks = list(range(1, N + 1))
losses = {K: loss(learned(K)) for K in Ks}
zero_from = next(K for K in Ks if all(losses[k] == 0 for k in range(K, N + 1)))
print("valid presses=%d max valid lag=%d first press with it=%d" % (len(vlags), maxv, first_max))
print("offline loss=%d period-cutoff(12) loss=%d" % (loss(maxv), loss(12)))
print("learned-cutoff loss at K=10,30,60,100: %s ; lossless from K=%d" % ([losses[k] for k in (10, 30, 60, 100)], zero_from))
ok = (loss(maxv) == 0 and loss(12) > 0 and zero_from == first_max + 1
      and all(losses[K] > 0 for K in range(1, zero_from)))
print("RESULT: %s offline max-lag cutoff %d loses 0, period cutoff 12 loses %d, learned cutoff lossless only from K=%d (first max-lag press at index %d), loss>0 for every earlier K"
      % ("PASS" if ok else "FAIL", maxv, loss(12), zero_from, first_max))
