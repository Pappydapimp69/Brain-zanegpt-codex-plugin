# Deterministic ad-funnel model: hook survival x decay-to-end-card x ending multiplier.
# All numbers are ASSUMED model parameters (not measurements); the point is the crossover.
import math

def survive_hook(frame0_stakes, names_format):
    s = 0.35 if frame0_stakes else 0.20          # share still watching at t=3s
    if names_format:                              # film/E12: a line that names the ad breaks the feed-read
        s *= 0.5
    return s

def conv(L, h, intent_slope, ending, network, frame0=True, names=False):
    reach = survive_hook(frame0, names) * math.exp(-h * max(0, L - 3))
    intent = 1 + intent_slope * L / 60.0          # longer cut shows more demo -> more intent per completer
    end = {("social","fail"):1.65, ("social","win"):1.0, ("inapp","win"):1.33, ("inapp","fail"):1.0}[(network, ending)]
    return reach * intent * end

def best_len(h, slope, ending, network, **kw):
    return max((15, 30, 45), key=lambda L: conv(L, h, slope, ending, network, **kw))

rows = []
# 1) social, steep decay: 15s should win
r1 = best_len(0.04, 1.0, "fail", "social"); rows.append(("social h=.04", r1))
# 2) sweep decay to find the 15 vs 30 crossover
cross = None
for i in range(1, 400):
    h = i / 10000
    if conv(30, h, 1.0, "fail", "social") < conv(15, h, 1.0, "fail", "social"):
        cross = h; break
# 3) BREAK: in-app, flat decay, strong intent slope -> long wins (Liftoff exception)
r3 = best_len(0.005, 1.0, "win", "inapp"); rows.append(("inapp h=.005", r3))
# 4) ending flips by network
e_soc = conv(15, .04, 1, "fail", "social") / conv(15, .04, 1, "win", "social")
e_app = conv(15, .04, 1, "win", "inapp") / conv(15, .04, 1, "fail", "inapp")
# 5) frame0 stakes vs none, and format-naming line (film/E12)
f0 = conv(15, .04, 1, "fail", "social") / conv(15, .04, 1, "fail", "social", frame0=False)
nm = conv(15, .04, 1, "fail", "social", names=True) / conv(15, .04, 1, "fail", "social")
print("best length:", rows)
print("15s-vs-30s crossover decay h* = %.4f (below it 30s wins)" % cross)
print("ending ratio social fail/win=%.2f inapp win/fail=%.2f" % (e_soc, e_app))
print("frame0 stakes gain=%.2f  format-naming penalty=%.2f" % (f0, nm))
ok = (r1 == 15 and r3 == 45 and 0.01 <= cross <= 0.02 and e_soc > 1 and e_app > 1 and f0 > 1 and nm < 1)
print("RESULT: %s 15s wins at h=.04, 45s wins at h=.005, crossover h*=%.4f, ending flips by network (%.2f/%.2f), frame0 x%.2f, naming x%.2f"
      % ("PASS" if ok else "FAIL", cross, e_soc, e_app, f0, nm))
