"""Pass 2 sandbox: drain cap (combined-audio-realtime E1/E3) x LFSR resume and peak-meter
blindness (combined-lfsr-peak-meter E1). Deterministic, stdlib only.
A 16-bit Galois LFSR noise voice plus a driven, clipped carrier renders in 128-sample
callbacks. At resume the audio thread's generator is rebuilt from DEFAULT_SEED; the
control thread enqueues a 2048-message repair burst and one RESTORE message carrying
the live register saved at suspend. Messages cost 9 us each; budget 2800 us.
"""
import math, zlib

DEFAULT_SEED = 0xACE1
BLOCK, BUDGET_US, MSG_US = 128, 2800, 9
BURST, CAP = 2048, 64
PRE, POST_BLOCKS = 384, 64          # samples before suspend, callbacks after resume

def lfsr_step(r):
    lsb = r & 1
    r >>= 1
    if lsb:
        r ^= 0xB400
    return r

BITS = {}

def sample(r, n):
    noise = 1.0 if (r & 1) else -1.0
    carrier = math.sin(2 * math.pi * 220 * n / 48000) * 3.0   # driven hard
    return max(-1.0, min(1.0, carrier + 0.35 * noise))

def reference():
    r, out, bits = DEFAULT_SEED, [], []
    for n in range(PRE + POST_BLOCKS * BLOCK):
        r = lfsr_step(r); out.append(sample(r, n)); bits.append(r & 1)
    return out, bits[PRE:]

def resumed(policy):
    # pre-suspend part identical to reference
    r, out = DEFAULT_SEED, []
    for n in range(PRE):
        r = lfsr_step(r); out.append(sample(r, n))
    saved = r
    gen = DEFAULT_SEED                      # rebuilt generator after reload
    if policy == 'restore_first_fifo':
        queue = [('RESTORE', saved)] + [('REPAIR', i) for i in range(BURST)]
    else:
        queue = [('REPAIR', i) for i in range(BURST)] + [('RESTORE', saved)]
    worst = 0; restore_cb = None; n = PRE; bits = []
    for cb in range(POST_BLOCKS):
        cost = 0
        if policy == 'priority_slot':
            for k, m in enumerate(queue):
                if m[0] == 'RESTORE':
                    gen = m[1]; queue.pop(k); restore_cb = cb; cost += MSG_US; break
        limit = len(queue) if policy == 'uncapped_fifo' else CAP
        for _ in range(min(limit, len(queue))):
            kind, val = queue.pop(0); cost += MSG_US
            if kind == 'RESTORE':
                gen = val; restore_cb = cb
                if policy == 'capped_fifo_advance':
                    for _ in range(n - PRE):
                        gen = lfsr_step(gen)
        worst = max(worst, cost)
        for _ in range(BLOCK):
            gen = lfsr_step(gen); out.append(sample(gen, n)); bits.append(gen & 1); n += 1
    return out, worst, restore_cb, bits

def dft_mag(x, bins=32):
    N = len(x); mags = []
    for k in range(1, bins + 1):
        f = k * 7  # spread probe bins over the band
        re = sum(x[i] * math.cos(2 * math.pi * f * i / N) for i in range(N))
        im = sum(x[i] * math.sin(2 * math.pi * f * i / N) for i in range(N))
        mags.append(math.hypot(re, im))
    return mags

def main():
    ref, ref_bits = reference()
    ref_post = ref[PRE:]
    ref_mag = dft_mag(ref_post)
    rows = {}
    unclipped = sum(1 for v in ref_post if abs(v) < 1.0) / len(ref_post)
    print(f"reference post-resume samples not clipped: {unclipped*100:.1f}%")
    for policy in ('capped_fifo', 'capped_fifo_advance', 'priority_slot', 'uncapped_fifo', 'restore_first_fifo'):
        out, worst, rcb, bits = resumed(policy)
        post = out[PRE:]
        mism = sum(1 for a, b in zip(post, ref_post) if a != b)
        late_window = (rcb or 0) * BLOCK
        after = sum(1 for a, b in zip(post[late_window + BLOCK:], ref_post[late_window + BLOCK:]) if a != b)
        after_n = len(post) - late_window - BLOCK
        peak = max(abs(v) for v in post)
        delta = sum(abs(a - b) for a, b in zip(dft_mag(post), ref_mag))
        crc_same = zlib.crc32(repr(post).encode()) == zlib.crc32(repr(ref_post).encode())
        start = late_window + BLOCK
        bit_after = sum(1 for a, b in zip(bits[start:], ref_bits[start:]) if a != b) / max(1, after_n)
        before = sum(1 for a, b in zip(post[:start], ref_post[:start]) if a != b)
        rows[policy] = (mism / len(post), after / max(1, after_n), peak, delta, worst, rcb, crc_same, bit_after, before)
        print(f"{policy:19s} restore@cb {rcb:>3}  mismatch {mism/len(post)*100:5.1f}%  after-restore {after/max(1,after_n)*100:5.1f}%"
              f"  peak {peak:.3f} (ref {max(abs(v) for v in ref_post):.3f})  dft delta {delta:9.3f}  crc same {crc_same}  worst cb {worst} us")
        print(f"    noise-bit mismatch after restore {bit_after*100:.1f}%  audible mismatches before/at restore {before}")
    c, p, u, f = rows['capped_fifo'], rows['priority_slot'], rows['uncapped_fifo'], rows['restore_first_fifo']
    a = rows['capped_fifo_advance']
    print(f"run-1 prediction (>=40% audible after restore) holds: {c[1] >= 0.40}")
    ok = (c[5] == 32 and c[7] >= 0.40 and c[1] <= unclipped and a[1] == 0 and a[8] > 0 and c[2] == p[2] == 1.0 and c[3] > 0 and not c[6]
          and p[0] == 0 and p[4] <= BUDGET_US and u[0] == 0 and u[4] > BUDGET_US and f[0] == 0 and f[4] <= BUDGET_US)
    print(f"RESULT: {'PASS' if ok else 'FAIL'} capped FIFO applies the live-register restore on callback {c[5]} "
          f"and stays wrong after it ({c[1]*100:.1f}% of later samples, {c[0]*100:.1f}% overall) with peak {c[2]:.3f} = ref, "
          f"dft delta {c[3]:.1f}, crc differs; priority slot 0% at {p[4]} us worst; uncapped 0% at {u[4]} us; "
          f"restore-first FIFO {f[0]*100:.1f}% at {f[4]} us; noise bits wrong {c[7]*100:.1f}% after restore "
          f"(only {unclipped*100:.1f}% of samples unclipped); advance-on-restore 0% after, {a[8]} wrong samples before")

if __name__ == '__main__':
    main()
