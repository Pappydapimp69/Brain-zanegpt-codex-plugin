"""Perfect-copy fake-ad parody vs loose copy: when does copying the ad exactly, then turning, win?

Funnel model (deterministic, no RNG). A viewer recognises the parodied trope with probability R(k),
k = trope-unique features left on screen, taken from brain-creative-training E6's reader
(0 left 0/6, 1 left 15/51, 2 left 45/54, 3 left 9/9). Recognition completes at t_rec = 2 s.
Before the turn: everyone skips at base hazard h0 until t_rec; then recognisers (who believe it is a real
ad) skip at h_ad, non-recognisers (confused) at h_c. At the turn T, a recogniser who is still watching
gets payoff 1 (expectation set, then violated); a non-recogniser gets w = 0.1 ("weirdness alone").
A turn before t_rec finds nobody holding the expectation: payoff w for all.
Score = expected payoff per impression.
"""
import math

R = {0: 0 / 6, 1: 15 / 51, 2: 45 / 54, 3: 9 / 9}
T_REC = 2.0
H0 = 0.10
W = 0.10


def survival(T, h_after):
    return math.exp(-H0 * min(T, T_REC) - h_after * max(0.0, T - T_REC))


def score(k, T, h_ad, h_c):
    if T < T_REC:  # turn lands before anyone recognises the format
        return survival(T, 0) * W
    r = R[k]
    return r * survival(T, h_ad) * 1.0 + (1 - r) * survival(T, h_c) * W


def crossover_T(h_ad, h_c, k_hi=3, k_lo=1):
    """first T (0.1 s grid, up to 15 s) where the faithful copy stops beating the loose copy"""
    for i in range(int(T_REC * 10), 151):
        T = i / 10
        if score(k_hi, T, h_ad, h_c) <= score(k_lo, T, h_ad, h_c):
            return T
    return None


lines = []
ok = True

# S1: kernel claim at a typical turn (T=3 s), moderate ad aversion
h_ad, h_c = 0.25, 0.15
s = {k: score(k, 3.0, h_ad, h_c) for k in R}
print("S1 turn at 3 s, h_ad=0.25 h_c=0.15:", {k: round(v, 3) for k, v in s.items()})
ok &= s[3] > s[2] > s[1] > s[0]
ratio_31 = s[3] / s[1]
print(f"   faithful(k=3)/loose(k=1) = {ratio_31:.2f}x")

# S2: turn timing sweep for the faithful copy -> where is the peak, where is half the peak
sweep = [(i / 2, score(3, i / 2, h_ad, h_c)) for i in range(0, 31)]
peakT, peak = max(sweep, key=lambda x: x[1])
halfT = next(T for T, v in sweep if T > peakT and v < peak / 2)
print(f"S2 sweep k=3: peak {peak:.3f} at T={peakT}s; score(T=0)={sweep[0][1]:.3f}; "
      f"falls below half peak at T={halfT}s; score(T=10)={score(3, 10, h_ad, h_c):.3f}")
early = score(3, 1.0, h_ad, h_c), score(1, 1.0, h_ad, h_c)
print(f"   turn at 1 s (before recognition): k=3 {early[0]:.3f} vs k=1 {early[1]:.3f} -> fidelity buys nothing")
ok &= early[0] == early[1] and peakT == T_REC

# S3 (built to BREAK the claim): heavy ad aversion -- viewers who think it is a real ad skip fast.
# Analytic prediction: faithful beats loose iff exp(-(h_ad-h_c)(T-t_rec)) > W, i.e. (h_ad-h_c)(T-2) < ln 10
for h_ad3 in (0.25, 0.5, 0.8, 1.2):
    xT = crossover_T(h_ad3, h_c)
    analytic = T_REC + math.log(1 / W) / (h_ad3 - h_c)
    print(f"S3 h_ad={h_ad3}: faithful stops beating loose at T={xT} s (analytic {analytic:.2f} s)")
    if xT is not None:
        ok &= abs(xT - analytic) <= 0.1
x08 = crossover_T(0.8, h_c)
s3_late = score(3, 6.0, 0.8, h_c), score(1, 6.0, 0.8, h_c)
print(f"   h_ad=0.8, turn at 6 s: k=3 {s3_late[0]:.4f} vs k=1 {s3_late[1]:.4f}")
ok &= s3_late[0] < s3_late[1]

# S4: zero ad aversion difference -> faithful wins at every T
ok &= crossover_T(h_c, h_c) is None
print("S4 h_ad=h_c: faithful never loses (crossover None)")

print(f"RESULT: {'PASS' if ok else 'FAIL'} perfect copy (k=3) beats loose (k=1) {ratio_31:.2f}x at a 3 s turn; "
      f"peak at the recognition point T=2 s ({peak:.3f}), below half by T={halfT} s; a turn before "
      f"recognition gives fidelity nothing; heavy ad-skipping (h_ad=0.8) flips it to loose-wins from T={x08} s")
