"""Toy schedule sandbox: DOMS soreness window vs weekly training frequency vs overload steps.
Kernel facts used: soreness begins 12-24 h after eccentric work, peaks 24-72 h (doms kernel);
2x/week per muscle beats 1x/week for hypertrophy (training-frequency kernel); +2-10% load after two sessions (progressive-overload kernel).
ASSUMED by me: end of soreness at 120 h (the kernel gives no end), two profile shapes. Deterministic, stdlib only."""
def tri(h):      # peak at 48 h (middle of 24-72), zero at 12 and 120
    if h <= 12 or h >= 120: return 0.0
    return (h - 12) / 36 if h <= 48 else (120 - h) / 72
def plateau(h):  # full soreness across the whole 24-72 window, ramp from 12, decay to 120
    if h <= 12 or h >= 120: return 0.0
    if h < 24: return (h - 12) / 12
    if h <= 72: return 1.0
    return (120 - h) / 48
def start_residual(gaps, prof, overload=0.0, weeks=8):
    """mean/max soreness (fraction of the previous session's peak) present at the start of each session"""
    vals = []
    amp_prev = 1.0
    for w in range(weeks):
        for i, g in enumerate(gaps):
            n = w * len(gaps) + i
            amp = amp_prev * (1 + overload) if n % 2 == 1 else amp_prev   # step up after every two sessions
            vals.append(prof(g) * amp_prev / amp)       # residual relative to the current session's amplitude
            amp_prev = amp
    return sum(vals) / len(vals), max(vals)
SCHED = {"1x/wk": [168], "2x Mon/Thu": [72, 96], "2x even": [84, 84], "3x MWF": [48, 48, 72], "daily": [24] * 7}
res = {}
for pname, p in (("tri", tri), ("plateau", plateau)):
    for s, g in SCHED.items():
        res[(pname, s)] = start_residual(g, p, 0.0)
        print(f"{pname:8s} {s:11s} mean {res[(pname, s)][0]:.2f} max {res[(pname, s)][1]:.2f}")
# overload effect (6% step every two sessions) on the 2x even schedule
a = start_residual(SCHED["2x even"], tri, 0.0)[0]; b = start_residual(SCHED["2x even"], tri, 0.10)[0]
print("overload 10% step, 2x even tri: mean", round(a, 3), "->", round(b, 3))
ok = (all(res[(p, "1x/wk")][1] == 0.0 for p in ("tri", "plateau"))
      and all(res[(p, "2x even")][0] > 0.4 for p in ("tri", "plateau"))
      and res[("tri", "3x MWF")][1] == 1.0 and res[("plateau", "3x MWF")][1] == 1.0
      and b < a and (a - b) < 0.1 * a + 0.05)
print(("RESULT: PASS" if ok else "RESULT: FAIL") +
      f" 1x/wk starts clear; 2x even starts with {res[('tri','2x even')][0]:.2f}-{res[('plateau','2x even')][0]:.2f} of peak soreness; 3x MWF hits peak; 10% overload shifts it {a:.2f}->{b:.2f}")
