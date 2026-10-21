"""Speech syllable envelope through a room: when does slowing down help?

Intensity-envelope model (Houtgast/Steeneken modulation-transfer idea):
- input: syllable train at R syllables/s, each syllable a sin^2 pulse over 60%
  of the period, silent gap for 40% (intensity envelope, 1 kHz envelope rate)
- room: direct fraction d plus an exponential reverberant tail with RT60 T
  (intensity decays 60 dB in T), implemented exactly as a one-pole filter
- steady noise intensity N set by SNR against the mean speech intensity
Measured on the last 8 whole periods after 12 s of warm-up:
- m: envelope modulation depth at the syllable rate, output over input
- valley/peak: min/max of the output envelope over one period (input 0)
- TI: single-band transmission index (SNRapp clipped to +-15 dB), not full STI
Compared with theory |d + (1-d)/(1 + j 2 pi F T/13.8)| / (1 + N/mean).
"""
import cmath
import math

FS = 1000


def envelope(rate, n, gain=1.0):
    period = FS / rate
    out = []
    for i in range(n):
        ph = (i % period) / period
        out.append(gain * (math.sin(math.pi * ph / 0.6) ** 2 if ph < 0.6 else 0.0))
    return out


def room(x, d, rt60):
    if rt60 <= 0:
        return list(x)
    a = math.exp(-13.8 / (rt60 * FS))  # intensity decay per sample (ln 10^6 = 13.8)
    y, out = 0.0, []
    for v in x:
        y = a * y + (1 - a) * v
        out.append(d * v + (1 - d) * y)
    return out


def mod_depth(sig, rate, n_periods):
    period = FS / rate
    L = int(round(period * n_periods))
    seg = sig[-L:]
    mean = sum(seg) / L
    acc = sum(v * cmath.exp(-2j * math.pi * rate * i / FS) for i, v in enumerate(seg))
    return 2 * abs(acc) / L / mean, mean


def valley_peak(sig, rate):
    period = int(round(FS / rate))
    seg = sig[-period:]
    return min(seg) / max(seg)


def ti(m):
    m = min(max(m, 1e-9), 1 - 1e-9)
    snr = max(-15.0, min(15.0, 10 * math.log10(m / (1 - m))))
    return (snr + 15) / 30


def run(rate, d, rt60, snr_db=None, gain=1.0, noise_ref_gain=1.0):
    n = int(FS * 12 + FS / rate * 8)
    x = envelope(rate, n, gain)
    y = room(x, d, rt60)
    m_in, mean_in = mod_depth(x, rate, 8)
    noise = 0.0
    if snr_db is not None:
        # noise is fixed relative to speech at noise_ref_gain (so raising gain raises SNR)
        ref_mean = mean_in / gain * noise_ref_gain
        noise = ref_mean * 10 ** (-snr_db / 10)
    y = [v + noise for v in y]
    m_out, _ = mod_depth(y, rate, 8)
    m = m_out / m_in
    tau = rt60 / 13.8
    h = d + (1 - d) / (1 + 2j * math.pi * rate * tau) if rt60 > 0 else 1.0
    theory = abs(h) / (1 + noise / (mean_in))
    return {"m": m, "theory": theory, "vp": valley_peak(y, rate), "ti": ti(m)}


def dr_to_d(db):
    r = 10 ** (db / 10)
    return r / (1 + r)


def main():
    ok = True
    T = 1.5
    far, close = dr_to_d(-10), dr_to_d(6)
    res = {}
    for label, d in (("far", far), ("close", close)):
        for R in (4.0, 2.0):
            r = run(R, d, T)
            res[(label, R)] = r
            print(f"{label} D/R {'-10' if label == 'far' else '+6'} dB, RT60 {T}s, {R:.0f} syl/s: "
                  f"m {r['m']:.3f} (theory {r['theory']:.3f}) valley/peak {r['vp']:.3f} TI {r['ti']:.2f}")
    worst_rel = max(abs(r["m"] - r["theory"]) / r["theory"] for r in res.values())
    ok &= worst_rel < 0.03
    ok &= 0.30 <= res[("far", 4.0)]["m"] <= 0.44 and 0.52 <= res[("far", 2.0)]["m"] <= 0.68
    gain_close = res[("close", 2.0)]["m"] - res[("close", 4.0)]["m"]
    gain_far = res[("far", 2.0)]["m"] - res[("far", 4.0)]["m"]
    ok &= gain_close < 0.1

    # loudness: +10 dB with no noise changes nothing; with noise it raises SNR only
    loud = run(4.0, far, T, gain=10.0)
    dm_loud = abs(loud["m"] - res[("far", 4.0)]["m"])
    print(f"far, 4 syl/s, +10 dB voice, no noise: m {loud['m']:.3f} (change {dm_loud:.2e})")
    ok &= dm_loud < 1e-9
    nz = run(4.0, far, T, snr_db=10)
    nz_loud = run(4.0, far, T, snr_db=10, gain=10.0)
    print(f"far, 4 syl/s, SNR 10 dB: m {nz['m']:.3f}; voice +10 dB (SNR 20): m {nz_loud['m']:.3f} "
          f"(reverb-only ceiling {res[('far', 4.0)]['m']:.3f})")

    # BREAK: dry room, noise-dominated: slowing should not help
    dry4 = run(4.0, 1.0, 0.0, snr_db=0)
    dry2 = run(2.0, 1.0, 0.0, snr_db=0)
    print(f"dry, SNR 0 dB: m at 4 syl/s {dry4['m']:.3f}, at 2 syl/s {dry2['m']:.3f}")
    ok &= abs(dry4["m"] - 0.5) < 0.01 and abs(dry2["m"] - 0.5) < 0.01
    dry4l = run(4.0, 1.0, 0.0, snr_db=0, gain=10.0)
    print(f"dry, voice +10 dB (SNR 10): m {dry4l['m']:.3f}")

    # rate needed for TI >= 0.6 far vs close
    def max_rate(d):
        best = None
        R = 1.0
        while R <= 8.0001:
            if run(R, d, T)["ti"] >= 0.6:
                best = R
            R += 0.5
        return best
    mr_far, mr_close = max_rate(far), max_rate(close)
    print(f"fastest rate (0.5 steps, 1-8) keeping TI >= 0.6 at RT60 {T}s: far {mr_far}, close {mr_close}")

    print(("RESULT: PASS " if ok else "RESULT: FAIL ") +
          f"RT60 1.5 s far(D/R -10 dB) m 4/s {res[('far', 4.0)]['m']:.3f} -> 2/s {res[('far', 2.0)]['m']:.3f} "
          f"(+{gain_far:.3f}), close(+6 dB) +{gain_close:.3f}; theory err max {worst_rel * 100:.2f}%; "
          f"+10 dB voice no noise dm {dm_loud:.1e}; noisy SNR10->20 m {nz['m']:.3f}->{nz_loud['m']:.3f}; "
          f"dry SNR0 m {dry4['m']:.3f}/{dry2['m']:.3f} at 4/2 syl/s; TI>=0.6 max rate far {mr_far} close {mr_close}")


if __name__ == "__main__":
    main()
