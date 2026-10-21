# local/sandbox-genesis-mix — lessons

Project: local/sandbox-genesis-mix. Newest first.

---

## E1 — radix2 fft silent garbage on nonpow2 after resample
- Date: 2026-07-05
- Project: local/sandbox-genesis-mix
- Tags: [audio][dsp][harness]
- What: Verifying a resampling stage (Genesis FM native 53267 Hz → host 44100
  Hz) with an FFT, the "naive decimation" and "lowpass-then-decimate" paths
  produced BYTE-IDENTICAL spectra — masquerading as "the two algorithms are
  equivalent." They are not; the FFT was silently returning garbage.
- Why built: A sandbox for the Genesis audio output stage — summing the FM and
  PSG chips and resampling to 44100 — testing that low-passing before
  decimation removes the alias a naive resample introduces.
- Why it mattered: The whole point of the test was to distinguish a correct
  resampler from a broken one; instead it reported them identical, which would
  have "confirmed" that skipping the anti-alias filter is fine.
- Design: An iterative radix-2 (Cooley-Tukey) FFT computed the spectrum of each
  resampled buffer. The resampler output length is `inLen / (53267/44100)` ≈
  27128.
- Got right: The resampling and mixing math were fine; the FFT is correct — for
  power-of-two lengths.
- Where/why it failed: A radix-2 FFT is only defined for power-of-two lengths.
  Resampling changes the buffer length to a NON-power-of-two (27128), and the
  bit-reversal + butterfly loops run anyway on that length, producing
  meaningless output with no error. Because both paths yielded equal-length
  garbage, they came out identical — a false "they match." The buffer length
  silently drifted off a power of two the moment a length-changing stage
  (resampling) sat upstream of the FFT.
- Fix: Guard the FFT explicitly — `if (n < 2 || (n & (n-1)) !== 0) throw` —
  so a non-power-of-two length fails LOUDLY instead of returning garbage. Then
  feed the FFT a power-of-two slice (largest po2 prefix) of the resampled
  buffer. (Separately: the comparison metric must be ABSOLUTE energy, not a
  per-buffer-normalized spectrum, or a near-silent filtered buffer's loudest
  residual still normalizes to 1.0 and hides the filter's effect.)
- Why this fix: The precondition (power-of-two length) is cheap to check and
  exactly the thing an upstream length-changing stage violates. Asserting it
  converts a silent-wrong result into an immediate, located failure; without
  the guard the error surfaces only as a nonsensical downstream conclusion.
- Rule of thumb: A radix-2 FFT returns silent garbage on a non-power-of-two
  length — guard it with `(n & (n-1)) === 0` and throw, because any upstream
  stage that changes buffer length (resampling, trimming, windowing to an odd
  size) will violate it and two different inputs can then both produce
  identical garbage, faking a "they match." Feed it a power-of-two slice, and
  compare with ABSOLUTE energy, not a per-buffer-normalized spectrum.
- Provenance (verified/assumed): VERIFIED first-hand this session — the two
  resample paths printed identical garbage spectra until an added
  power-of-two guard fired on the length-27128 buffer; after slicing to a
  power of two and switching to absolute-RMS comparison, the alias (25 kHz →
  19100 Hz ghost) and the filter's ~99% attenuation both showed cleanly.
- Link: session (this one, dog-game-continue-oc3xqh); scratchpad
  genesis/sandboxC_mix_resample_dac.mjs.
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-bloom-audio.md#E2 · compatible · no sandbox · session (query brain for "5 loops" — loop 3/5), sandbox script loop3_psg_fft.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-bloom-audio.md#E7 · compatible · no sandbox · session (query brain for "loop: aim, compose from recorded lessons, sandbox, file" — loop 1), sandbox scripts reverify1_mix_psg.mjs/reverify1b.mjs/reverify1c_period.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/local__sandbox-genesis-fm.md#E2 · compatible · no sandbox · session 01KxkbJUq8YajH8GokSZYYHy; combining sandbox-genesis-fm + sandbox-genesis-mix + sandbox-genesis-psg (a group-of-3, not yet directly co-verified with each other); sandbox `engine.mjs`, scratchpad `loop3-genesis-triple/` (run twice as separate process invocations, outputs diffed byte-identical)
