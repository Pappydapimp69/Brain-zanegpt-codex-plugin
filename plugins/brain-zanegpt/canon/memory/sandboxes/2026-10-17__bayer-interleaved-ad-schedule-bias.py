# 4 ad variants share 16 delivery slots; slot quality w[t] varies (diurnal trend / cycle).
# Schedules: blocked (slots 0-3 -> A, ...), round-robin (t%4), Bayer (4x4 matrix value // 4).
# Prediction (before run): exposure imbalance (max/min of summed slot quality per variant) -
#   linear ramp: blocked 3.25x-ish bad, round-robin ~1.3x, Bayer <=1.15x (Bayer spreads like dither);
#   period-4 cycle: round-robin ALIASES (imbalance >2x, built to BREAK) while Bayer stays <=1.5x;
#   period-8 cycle: all three <=1.5x except blocked.
import math
B = [[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]
sched = {
 "blocked":     [t//4 for t in range(16)],
 "round_robin": [t%4 for t in range(16)],
 "bayer":       [B[t//4][t%4]//4 for t in range(16)],
}
W = {
 "ramp":    [1+t/5 for t in range(16)],
 "cycle4":  [1.5+math.sin(2*math.pi*t/4) for t in range(16)],
 "cycle8":  [1.5+math.sin(2*math.pi*t/8) for t in range(16)],
 "cycle16": [1.5+math.sin(2*math.pi*t/16) for t in range(16)],
}
imb = {}
for wn,w in W.items():
    for sn,s in sched.items():
        tot=[0.0]*4
        for t in range(16): tot[s[t]] += w[t]
        imb[(wn,sn)] = max(tot)/min(tot)
    print(wn, {sn: round(imb[(wn,sn)],2) for sn in sched})
checks = [imb[("ramp","blocked")]>2.0, imb[("ramp","bayer")]<=1.15, imb[("cycle4","round_robin")]>2.0,
          imb[("cycle4","bayer")]<=1.5, all(imb[("cycle8",s)]<=1.5 for s in ("round_robin","bayer"))]
print("checks", checks)
print("RESULT: %s %d/5; ramp blocked %.2f bayer %.2f; cycle4 round-robin %.2f bayer %.2f" % ("PASS" if all(checks) else "FAIL", sum(checks), imb[("ramp","blocked")], imb[("ramp","bayer")], imb[("cycle4","round_robin")], imb[("cycle4","bayer")]))
