"""Sandbox: holding for a laugh. When should a performer (or an editor cutting a clip) start the next line after a
punchline? Model: the laugh masks speech; the next line's first second carries its setup words.

Model inputs (stand-ins, not measured): laugh starts 0.3 s after the punchline, rises 0.3 s to a peak, then falls
linearly in dB to the floor over a decay time D (small 68 dB D 1.0 s; medium 73 dB D 2.0 s; big 78 dB D 3.5 s).
RUN 1 used an exponential intensity decay with tau 0.6/1.0/1.6 s, which is only 2.7 to 7 dB/s and kept the big laugh
above the floor for 15 s; that parameterization was replaced after run 1 (see the proposal's Observed), and the
second swell was moved to start on the laugh's tail (60% of D) because in run 1 it had died before any resume;
room floor 35 dB; voice 65 dB. Audibility per instant = clamp((SNR + 15) / 30, 0, 1), an SII-style band-audibility
mapping applied to the whole band. Laugh 'over' = laugh within 3 dB of the floor.

PREDICTION (written before the first run). Hidden assumption: a laugh decays monotonically after its peak, so the
level at the moment you resume predicts the masking of the next line. It is wrong if a re-swelling laugh steps on a
line that was resumed on the decay.
 P1 a fixed 1.0 s pause (an edit rule) leaves the big laugh's next line under 0.5 first-second audibility and gives
    the small laugh more than 0.5 s of hold past the point the line would already have been 0.9 audible.
 P2 'ride the laugh': resume when the laugh falls 10 dB below the voice -> first-second audibility >= 0.9 for all
    three sizes, and it resumes at least 1.0 s before 'wait for silence' on the big laugh.
 P3 BREAK: a second swell (72 dB) on the laugh's tail drops the ride-the-laugh line below 0.7.
"""
import math
DT = 0.01
FLOOR, VOICE = 35.0, 65.0
SIZES = {"small": (68.0, 1.0), "medium": (73.0, 2.0), "big": (78.0, 3.5)}   # (peak dB, decay time D to floor)

def db_sum(*levels):
    return 10 * math.log10(sum(10 ** (l / 10) for l in levels))

def laugh_level(t, peak, tau, swells=()):
    """laugh-only level in dB at time t after the punchline (None-safe: very low when absent)"""
    def one(t0, pk, d):
        if t < t0: return -100.0
        if t < t0 + 0.3: return pk - 30 * (1 - (t - t0) / 0.3)
        lv = pk - (pk - FLOOR) * (t - t0 - 0.3) / d
        return lv if lv > FLOOR - 20 else -100.0
    parts = [one(0.3, peak, tau)] + [one(t0, pk, tu) for (t0, pk, tu) in swells]
    return db_sum(*parts)

def noise(t, peak, tau, swells=()):
    return db_sum(laugh_level(t, peak, tau, swells), FLOOR)

def audibility(t, peak, tau, swells=()):
    snr = VOICE - noise(t, peak, tau, swells)
    return min(max((snr + 15) / 30, 0.0), 1.0)

def first_second(t0, peak, tau, swells=()):
    n = int(round(1.0 / DT))
    return sum(audibility(t0 + i * DT, peak, tau, swells) for i in range(n)) / n

def resume_ride(peak, tau, below, swells=()):
    t, past_peak = 0.0, False
    while t < 20:
        lv = laugh_level(t, peak, tau, swells)
        if t > 0.6: past_peak = True
        if past_peak and lv <= VOICE - below: return t
        t += DT
    return t

def resume_silence(peak, tau, swells=()):
    t = 0.6
    while t < 30:
        if laugh_level(t, peak, tau, swells) <= FLOOR + 3:
            # require it to stay down for 0.5 s
            if all(laugh_level(t + k * DT, peak, tau, swells) <= FLOOR + 3 for k in range(50)): return t
        t += DT
    return t

def earliest_ok(peak, tau, target=0.9, swells=()):
    t = 0.0
    while t < 30:
        if first_second(t, peak, tau, swells) >= target: return t
        t += DT
    return t

res, out = {}, {}
for name, (pk, tau) in SIZES.items():
    fixed = first_second(1.0, pk, tau)
    ok_t = earliest_ok(pk, tau)
    r10 = resume_ride(pk, tau, 10)
    sil = resume_silence(pk, tau)
    out[name] = dict(fixed=fixed, ok_t=ok_t, ride_t=r10, ride_a=first_second(r10, pk, tau), sil_t=sil, sil_a=first_second(sil, pk, tau))
    o = out[name]
    print("%-6s fixed 1.0 s: aud %.3f | earliest 0.9-audible start %.2f s | ride(-10 dB) at %.2f s aud %.3f | silence at %.2f s aud %.3f"
          % (name, o["fixed"], o["ok_t"], o["ride_t"], o["ride_a"], o["sil_t"], o["sil_a"]))

print("== threshold sweep for ride-the-laugh (dB below voice): min first-second audibility over sizes, and big-laugh resume time")
sweep = {}
for below in (0, 5, 10, 15, 20):
    a = min(first_second(resume_ride(pk, tau, below), pk, tau) for pk, tau in SIZES.values())
    tb = resume_ride(*SIZES["big"], below)
    sweep[below] = (a, tb)
    print("  %2d dB below: min aud %.3f, big resumes %.2f s" % (below, a, tb))

print("== BREAK: big laugh with a second swell on its tail (72 dB, starts at 60% of D, decay 1.5 s)")
pk, tau = SIZES["big"]
sw = ((0.6 + 0.6 * tau, 72.0, 1.5),)
r_sw = resume_ride(pk, tau, 10, sw)
a_sw = first_second(r_sw, pk, tau, sw)
s_sw = resume_silence(pk, tau, sw)
print("  ride(-10) resumes %.2f s aud %.3f | silence resumes %.2f s aud %.3f" % (r_sw, a_sw, s_sw, first_second(s_sw, pk, tau, sw)))
# a guard: after the threshold, also require the level to have been falling for 0.5 s with no rise
def resume_ride_guard(peak, tau, below, swells=(), hold=0.5):
    t = resume_ride(peak, tau, below, swells)
    while t < 30:
        lv = [laugh_level(t + k * DT, peak, tau, swells) for k in range(int(hold / DT))]
        if all(b <= a + 1e-9 for a, b in zip(lv, lv[1:])) and max(lv) <= VOICE - below: return t + hold
        t += DT
    return t
g_sw = resume_ride_guard(pk, tau, 10, sw)
g_plain = resume_ride_guard(pk, tau, 10)
print("  ride + 0.5 s still-falling guard: swell case resumes %.2f s aud %.3f; no-swell case resumes %.2f s aud %.3f"
      % (g_sw, first_second(g_sw, pk, tau, sw), g_plain, first_second(g_plain, pk, tau)))

p1 = out["big"]["fixed"] < 0.5 and (1.0 - out["small"]["ok_t"]) > 0.5
p2 = all(out[n]["ride_a"] >= 0.9 for n in SIZES) and out["big"]["sil_t"] - out["big"]["ride_t"] >= 1.0
p3 = a_sw < 0.7
print("P1", p1, "P2", p2, "P3", p3)
print("RESULT: %s fixed 1.0 s pause: big aud %.2f, small could start %.2f s earlier; ride -10 dB aud small/med/big %.2f/%.2f/%.2f at %.2f/%.2f/%.2f s vs silence %.2f/%.2f/%.2f s; second swell drops ride to %.2f (guard %.2f)"
      % ("PASS" if (p1 and p2 and p3) else "FAIL", out["big"]["fixed"], 1.0 - out["small"]["ok_t"],
         out["small"]["ride_a"], out["medium"]["ride_a"], out["big"]["ride_a"],
         out["small"]["ride_t"], out["medium"]["ride_t"], out["big"]["ride_t"],
         out["small"]["sil_t"], out["medium"]["sil_t"], out["big"]["sil_t"], a_sw, first_second(g_sw, pk, tau, sw)))
