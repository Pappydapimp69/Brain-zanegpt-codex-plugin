# Own fixture: wave P=10, W=3 (B available when t mod 10 < 3). Press i at t_i = 2*i+1 with
# base lag i%4+1 and, on every 6th press, a jitter cycling 5, 9, 17. valid iff B available at
# t_i+L_i. 150 presses. Cutoff learned online = running max valid lag, frozen after K presses.
# Validity policy loses valid presses with lag above the cutoff; the gate-only policy (no
# validity check) executes EVERY press with lag <= cutoff, valid or not.
# PREDICTION (before run): valid loss > 0 for every K before the first press carrying the max
# valid lag and 0 from then on (as the learned-cutoff lesson says); gate-only invalid executions
# are nondecreasing in K, equal the offline value from that same K on, and are strictly lower
# at an early K (K=10) than offline -- so the early frozen cutoff is lossy for validity but the
# cheapest for the gate, the opposite direction of the lossless-cutoff-is-worst lesson.
P, W, N = 10, 3, 150
def lag(i):
    base = i % 4 + 1
    return base + ([5, 9, 17][(i // 6) % 3] if i % 6 == 5 else 0)
presses = [(2 * i + 1, lag(i)) for i in range(N)]
valid = [((t + L) % P) < W for t, L in presses]
maxv = max(L for (t, L), v in zip(presses, valid) if v)
first_max = next(i for i, ((t, L), v) in enumerate(zip(presses, valid)) if v and L == maxv)
def learned(K):
    m = 0
    for (t, L), v in zip(presses[:K], valid[:K]):
        if v and L > m: m = L
    return m
def val_loss(c): return sum(1 for (t, L), v in zip(presses, valid) if v and L > c)
def gate_invalid(c): return sum(1 for (t, L), v in zip(presses, valid) if (not v) and L <= c)
Ks = range(1, N + 1)
vl = {K: val_loss(learned(K)) for K in Ks}
gi = {K: gate_invalid(learned(K)) for K in Ks}
off_gi = gate_invalid(maxv)
zero_from = next(K for K in Ks if all(vl[k] == 0 for k in range(K, N + 1)))
mono = all(gi[K] <= gi[K + 1] for K in range(1, N))
print("valid=%d max valid lag=%d first max press=%d offline gate invalid=%d" % (sum(valid), maxv, first_max, off_gi))
print("valid loss at K=10,30,60,100: %s ; gate invalid at same K: %s" % ([vl[k] for k in (10, 30, 60, 100)], [gi[k] for k in (10, 30, 60, 100)]))
ok = (vl[1] > 0 and all(vl[K] > 0 for K in range(1, first_max + 1)) and zero_from == first_max + 1
      and mono and all(gi[K] == off_gi for K in range(zero_from, N + 1)) and gi[10] < off_gi)
print("RESULT: %s valid loss >0 until K=%d (max-lag press at %d) then 0; gate invalid nondecreasing %s, equals offline %d from K=%d, only %d at K=10 (valid loss %d there)"
      % ("PASS" if ok else "FAIL", zero_from, first_max, mono, off_gi, zero_from, gi[10], vl[10]))
