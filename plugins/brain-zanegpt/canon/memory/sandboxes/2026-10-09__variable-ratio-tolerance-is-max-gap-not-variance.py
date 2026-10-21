"""Extinction tolerance of a learner that quits after an unrewarded streak longer than
anything it saw in training (a stall detector with learned patience, cf. august-10/E12).
Deterministic: gap lists are fixed, no RNG, no clock."""
def gaps_to_schedule(gaps, n):
    out, i = [], 0
    while len(out) < n:
        g = gaps[i % len(gaps)]; out += [0]*(g-1) + [1]; i += 1
    return out[:n]
def tolerance(sched):            # longest unrewarded streak endured in training
    best = run = 0
    for r in sched:
        run = 0 if r else run+1; best = max(best, run)
    return best
def trials_to(sched, k):         # trials needed to collect k rewards
    c = 0
    for t, r in enumerate(sched, 1):
        c += r
        if c == k: return t
N = 300
S = {
 "continuous": gaps_to_schedule([1], N),
 "FR5": gaps_to_schedule([5], N),
 "VR5-wide": gaps_to_schedule([1,2,17,3,9,1,4,8,2,3], N),     # mean 5, max gap 17
 "VR5-narrow(BREAK)": gaps_to_schedule([4,6,5,4,6,5], N),      # mean 5, variable but max gap 6
 "FR5-with-one-long-gap": gaps_to_schedule([5]*9+[40], N),     # mean ~8.5, one outlier
}
def window_quit(sched, win=10, min_gain=1):   # E12-style: rate over a window, not per-observation
    return sum(1 for i in range(len(sched)-win+1) if sum(sched[i:i+win]) < min_gain)
print("schedule  mean_gap  tolerance(max streak)  trials_to_20_rewards  windows_below_rate")
tol = {}
for name, s in S.items():
    tol[name] = tolerance(s)
    print(f"{name:24s} {N/sum(s):5.2f} {tol[name]:6d} {trials_to(s,20):8d} {window_quit(s):6d}")
# in extinction, learner persists for `tolerance` unrewarded trials
ok = (tol["continuous"] == 0 and tol["FR5"] == 4 and tol["VR5-wide"] >= 3*tol["FR5"]
      and tol["VR5-narrow(BREAK)"] <= tol["FR5"] + 2
      and trials_to(S["continuous"],20) < trials_to(S["VR5-wide"],20)
      and window_quit(S["VR5-wide"]) > 0 and window_quit(S["VR5-wide"], win=20) == 0
      and window_quit(S["FR5"]) == 0)
print("RESULT:", "PASS" if ok else "FAIL",
      f"tolerance cont/FR5/VRwide/VRnarrow/FR+outlier = {tol['continuous']}/{tol['FR5']}/{tol['VR5-wide']}/{tol['VR5-narrow(BREAK)']}/{tol['FR5-with-one-long-gap']}")
