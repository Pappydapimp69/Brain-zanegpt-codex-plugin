# local/sandbox-kernel-dsp-chip-emulation — lessons

Project: local/sandbox-kernel-dsp-chip-emulation. Newest first.

---

## E1 — phase truncation sets a fixed point oscillators spur floor
- Date: 2026-09-28
- Project: local/sandbox-kernel-dsp-chip-emulation
- Tags: [dsp][emulation][fixed-point][audio]
- What: Applied the ideas kernel that when the target is a specific chip, its bit widths and truncation are the spec, and a floating-point cleanup measurably diverges. It diverged on most samples and in the spectrum, and the size of the spectral difference depended on which truncation the frequency exercised.
- Why built: brain train gap listed the kernel as unapplied, and memory had no bit-exact emulation entry.
- Design: A chip-style oscillator: 20-bit phase accumulator, 10-bit sine table indexed by the top phase bits with a half-step offset, 12-bit amplitude, beside a float version computing sin of the exact phase at the same amplitude. 4096 samples at three phase increments placed on whole FFT bins: 1024 (no phase bits truncated), 3328 and 9472 (phase truncation active). Compared samples after rounding and the largest spur relative to the fundamental from a 4096-point FFT.
- Got right: Choosing whole-bin frequencies, so neither version shows window leakage and every spur measured is the arithmetic's own.
- Where/why it failed: The fixed-point samples differed from the rounded float samples in 3888, 2820 and 2820 of 4096 cases, by up to 6.8 LSB. The float version's largest spur was about -270 dBc, the numerical floor. The fixed-point version's was -88.1 dBc when the increment truncated no phase bits (amplitude quantisation only) and -59.3 dBc when phase truncation was active, 29 dB higher.
- Fix: Reproduce the chip's phase width, table size, table offset and amplitude width exactly, and test the emulator against bit-exact golden samples; a float version cannot pass that test and removes spurs the hardware has.
- Why this fix: Truncation error is part of the chip's output, periodic and frequency-dependent. Phase truncation contributed the dominant spur here, so a cleanup that keeps amplitude width but computes exact phase still sounds different.
- Rule of thumb: A float cleanup of a fixed-point oscillator (20-bit phase, 10-bit table, 12-bit output) differed on 69-95% of samples by up to 6.8 LSB and erased spurs the fixed version has: -59.3 dBc when phase truncation is active, -88.1 dBc when it is not, against -270 dBc for float, so emulate the exact widths and test against bit-exact golden samples.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b09.py loop 44 in Pappydapimp69/Brain, deterministic. Observed: 3888/2820/2820 of 4096 samples differing, max 6.8 LSB; spurs -88.1/-59.3/-59.3 dBc fixed vs about -270 dBc float. The oscillator's widths follow the common chip pattern, not a specific die transcription such as Nuked-OPN2.
- Composed: ideas:DSP/chip-emulation/bit-exact-precision-is-the-target/float-cleanup-measurably-diverges
- Link: session 2026-09-28, brain train gap batch 9 loop 44
- Sandbox: sandboxes/2026-09-28__train-gap-b09.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)
- Cited-by: 2026-10-14 · projects/pappydapimp69__brainwork.md#E266 · compatible · sandboxes/2026-10-14__sandbox-psg-noise-cycle-audible-only-when-short.py · observed RESULT: PASS only the 7-step cycle shows in the spectrum (empty 0.93); the 8191-step cycle stays spectrally white (empty 0.02 at 32768) but autocorrelation at lag 8191 is 1.00 vs -0.14; spectrally audible seeds 7/65535 = 0.0107%, not 12.5% · brain train auto loop 2 pass 2 edge mode, unattended run 2026-10-14; session_018eKNqSCZk9zsMEo2AXSjsk
