"""Kernel: DSP/real-time-buffer/measure-worst-case-not-average/xrun-counters-and-rtsan.
Workload re-used from local__sandbox-kernel-dsp-realtime E1's 'allocation in the callback' design:
128-sample blocks at 48 kHz (period 2667 us), 900 us DSP +-10%, allocation on 30% of blocks with a
0.05% chance of a stall (assumed uniform 0..6 ms; E1 says 'up to 6 ms'). 10 simulated minutes, seeded.
Gates compared: mean callback time; a 1-in-100 sampling profiler's max; the per-callback log max and
count of callbacks over the period; and a device xrun counter with S periods of slack
(finish_k = max(k*P, finish_{k-1}) + dur_k, xrun if finish_k > (k+S)*P, then the stream resyncs).
Soak: how often a 5-minute or 1-hour zero-xrun test passes a callback with a 100x rarer stall.
PREDICTION (written before running): mean about 900 us; misses at S=1 about 20-30 (E1 saw 27);
S=2 counts about a quarter of those (about 5-8), while the per-callback log still shows 20-30 over
the period; the 1-in-100 sampler's max stays under the period in this run; for the 100x rarer bug a
5-minute zero-xrun test passes it at least 85% of the time and a 1-hour test at least 30%.
"""
import random

FS, BLK = 48000, 128
P = BLK / FS * 1e6  # 2666.7 us
MIN = 60 * FS // BLK  # blocks per minute = 22500


def dur(rng, stall_p):
    d = 900 * (1 + rng.uniform(-0.1, 0.1))
    if rng.random() < 0.30 and rng.random() < stall_p:
        d += rng.uniform(0, 6000)
    return d


def xruns(durs, S):
    n = 0
    fin = 0.0
    for k, d in enumerate(durs):
        start = max(k * P, fin)
        fin = start + d
        if fin > (k + S) * P:
            n += 1
            fin = (k + S) * P  # device resyncs; the late block is dropped
    return n


rng = random.Random(20261015)
durs = [dur(rng, 0.0005) for _ in range(10 * MIN)]
mean = sum(durs) / len(durs)
over = sum(d > P for d in durs)
worst = max(durs)
sampled_max = max(durs[::100])
x1, x2, x3 = xruns(durs, 1), xruns(durs, 2), xruns(durs, 3)
print(f"blocks {len(durs)}  period {P:.1f} us  mean {mean:.1f} us  worst {worst:.0f} us")
print(f"per-callback log: {over} callbacks over the period")
print(f"1-in-100 sampling profiler max: {sampled_max:.0f} us (under period: {sampled_max < P})")
print(f"device xrun counter: S=1 {x1}, S=2 {x2}, S=3 {x3}")

# S3 (built to BREAK 'the xrun counter is the gate'): same trace, deeper buffer -> counter reads low
hidden = over - x2

# Soak: 100x rarer stall. Simulate many independent tests; count how often a test reports 0 xruns
# (S=1) although the callback can overrun. Event-skipping keeps it fast: only stall blocks are drawn.
def soak_pass_rate(minutes, trials, seed):
    r = random.Random(seed)
    p_stall = 0.30 * 0.000005
    blocks = minutes * MIN
    passes = 0
    for _ in range(trials):
        k, bad = 0, 0
        while True:
            # geometric gap to next stall block
            u = r.random()
            gap = int(__import__('math').log(1 - u) / __import__('math').log(1 - p_stall)) + 1
            k += gap
            if k > blocks:
                break
            d = 900 * (1 + r.uniform(-0.1, 0.1)) + r.uniform(0, 6000)
            if d > P:  # at S=1 a single overrun of an isolated block is an xrun
                bad += 1
                break
        passes += bad == 0
    return passes / trials


p5 = soak_pass_rate(5, 2000, 1)
p60 = soak_pass_rate(60, 2000, 2)
p600 = soak_pass_rate(600, 2000, 3)
print(f"rare bug (100x rarer stall): zero-xrun test passes it in {p5:.1%} of 5-min runs, "
      f"{p60:.1%} of 1-h runs, {p600:.1%} of 10-h runs")

ok = (abs(mean - 900) < 10 and 20 <= over <= 30 and x1 == over and x2 < over / 2
      and sampled_max < P and p5 >= 0.85 and p60 >= 0.30)
print(f"RESULT: {'PASS' if ok else 'FAIL'} mean {mean:.0f} us of {P:.0f}; {over} callbacks over the period; "
      f"xrun counter S=1 {x1}, S=2 {x2}, S=3 {x3} ({hidden} overruns hidden at S=2); 1-in-100 sampler max "
      f"{sampled_max:.0f} us; rare-bug zero-xrun pass rate 5 min {p5:.1%}, 1 h {p60:.1%}, 10 h {p600:.1%}")
