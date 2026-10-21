# Recut sheets: each sheet has 6 recuts with promise p in [0.2,1.0], hook h in [0.8,1.4]; game delivers 0.5.
# IPM = 10*h*(1+0.8*p) * 0.9**off_cues ; D1 = 0.30 - 0.6*max(0, p-0.5) (floor .05). Truth = remap recut (off_cues=0), rank IPM*D1.
# Hand edits leave off_cues in 0..4 (deterministic LCG). Compare how often the pick changes under hand edits for:
#   A) rank all on IPM*D1;  B) cap promise at delivery (<=0.5) then rank survivors on IPM alone.
# Prediction (before run): B changes the pick MORE often than A, since with D1 equal among survivors the race is IPM-only and the cue handicap
# acts on it directly. Assumption: cue errors are independent of promise. Wrong if B flips no more often than A.
class R:
    def __init__(s, seed): s.x = seed
    def u(s):
        s.x = (1103515245*s.x + 12345) % 2**31; return s.x / 2**31
def make(seed, handicap_on_low=False):
    r = R(seed); out = []
    for _ in range(6):
        p = 0.2 + .8*r.u(); h = .8 + .6*r.u(); off = int(r.u()*5)
        out.append((p, h, off))
    return out
ipm = lambda v, off: 10*v[1]*(1 + .8*v[0]) * 0.9**off
d1 = lambda p: max(.05, .30 - .6*max(0, p-.5))
def pickA(S, use_off): return max(range(6), key=lambda i: ipm(S[i], S[i][2] if use_off else 0)*d1(S[i][0]))
def pickB(S, use_off):
    surv = [i for i in range(6) if S[i][0] <= .5] or list(range(6))
    return max(surv, key=lambda i: ipm(S[i], S[i][2] if use_off else 0))
N = 2000; fa = fb = 0; worse_b = worse_a = 0
sc = lambda S, i: ipm(S[i], 0)*d1(S[i][0])
for k in range(N):
    S = make(1000+k)
    t = pickA(S, False)
    a, b = pickA(S, True), pickB(S, True)
    fa += a != t; fb += b != pickB(S, False)
    worse_a += sc(S, a) < sc(S, t) - 1e-9; worse_b += sc(S, b) < sc(S, t) - 1e-9
# BREAK scenario: cap-only vs truth (cap pre-filter without cues) -- how often does the cap itself change the winner relative to IPM*D1
cap_vs_truth = sum(pickB(make(1000+k), False) != pickA(make(1000+k), False) for k in range(N))
print(f"N={N}: pick changes under hand edits A(IPM*D1)={fa} B(cap then IPM)={fb}; lost value vs truth A={worse_a} B={worse_b}; cap pick differs from IPM*D1 truth even with remap: {cap_vs_truth}")
ok = fb > fa
print("RESULT: %s hand-edited cues change the pick in %d/%d sheets for IPM*D1 ranking and %d/%d for cap-then-IPM; cap-then-IPM already disagrees with the IPM*D1 pick in %d/%d sheets with remap" % ("PASS" if ok else "FAIL", fa, N, fb, N, cap_vs_truth, N))
