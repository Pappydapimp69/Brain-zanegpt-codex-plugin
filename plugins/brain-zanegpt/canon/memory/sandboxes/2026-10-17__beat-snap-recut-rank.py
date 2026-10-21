# Recut a winning 30 s master into shorter variants (cold open 2 s + 3 acts 25/50/25 of the rest + button 2 s), cut points
# snapped to a 120 bpm grid (none / beat 0.5 s / bar 2 s), ranked on IPM and IPM*D1 where D1 needs act-2 gameplay >= 12 s.
# Prediction (before run): beat-snapping moves act 2 by <=0.25 s and never changes the IPM*D1 winner vs unsnapped over 8 drop-off
# rates; bar-snapping moves act 2 by up to 1 s and flips the winner at >=1 of 8 rates. Hidden assumption: D1 penalty is a smooth
# function of act-2 length, not a cliff. Break: make D1 a cliff at act2>=12 s -> even beat-snapping should flip >=1 rate.
def snap(x, g): return x if g == 0 else round(x / g) * g
def variant(L, g):
    body = L - 4
    a1, a2 = snap(body * .25, g), snap(body * .50, g)
    a3 = body - a1 - a2
    return dict(L=L, a2=a2)
def d1(a2, cliff):
    if cliff: return 0.30 if a2 >= 12 else 0.30 * 0.6
    return 0.30 * min(1.0, a2 / 12) ** 0.5
def pick(d, g, cliff, use_d1):
    best = None
    for L in [12 + i * 0.25 for i in range(73)]:
        v = variant(L, g); score = (1 - d) ** L * (d1(v["a2"], cliff) if use_d1 else 1)
        if best is None or score > best[0] + 1e-12: best = (score, L)
    return best[1]
DS = [0.005, 0.01, 0.02, 0.03, 0.04, 0.05, 0.07, 0.10]
def flips(g, cliff): return sum(abs(pick(d, g, cliff, True) - pick(d, 0, cliff, True)) > 1 for d in DS)
maxshift = {g: max(abs(variant(L, g)["a2"] - variant(L, 0)["a2"]) for L in [12 + i * 0.25 for i in range(73)]) for g in (0.5, 2)}
f_beat, f_bar, f_beat_cliff = flips(0.5, False), flips(2, False), flips(0.5, True)
ipm_vs_d1 = sum(pick(d, 0, False, False) != pick(d, 0, False, True) for d in DS)
print("max act2 shift beat %.2f bar %.2f" % (maxshift[0.5], maxshift[2]))
print("winner flips vs unsnapped: beat %d, bar %d, beat+cliff %d ; IPM vs IPM*D1 differ at %d rates" % (f_beat, f_bar, f_beat_cliff, ipm_vs_d1))
ok = maxshift[0.5] <= 0.25 + 1e-9 and f_beat == 0 and f_bar >= 1 and f_beat_cliff >= 1
print("RESULT:", "PASS" if ok else "FAIL", "act2 shift beat %.2f s / bar %.2f s; flips beat %d, bar %d, beat with cliff D1 %d; IPM vs IPM*D1 differ %d/8" % (maxshift[0.5], maxshift[2], f_beat, f_bar, f_beat_cliff, ipm_vs_d1))
