# local/sandbox-kernel-dsp-fm — lessons

Project: local/sandbox-kernel-dsp-fm. Newest first.

---

## E1 — thd n cannot see fm aliasing only an expected partials check can
- Date: 2026-09-28
- Project: local/sandbox-kernel-dsp-fm
- Tags: [dsp][audio][fm][measurement]
- What: Applied the ideas kernel that high-index FM aliases while its peak level stays normal, so it must be checked spectrally or by THD+N rather than with a meter. The meter's blindness reproduced; THD+N turned out equally blind, while comparing against the expected in-band partials measured the aliasing directly.
- Why built: brain train gap listed the kernel as unapplied. sandbox-genesis-fm/E1 recorded that an FM operator pins peak amplitude; this measures what does detect aliasing.
- Design: FM at 48 kHz with a 3000 Hz carrier and 4200 Hz modulator (so foldover lands off the harmonic grid), 4800 samples, index 0.5 to 20, sampled naively. A band-limited reference was built by summing only the Bessel sidebands J_k(I) below Nyquist; aliased energy is the naive signal minus that reference. THD+N was the residual after removing the best-fit carrier sinusoid, measured on both the naive and the band-limited signal.
- Got right: Measuring THD+N on the clean band-limited signal too. Without that baseline a high THD+N reading looks like evidence of aliasing.
- Where/why it failed: Peak stayed at 1.000 (0.995 at index 20) and RMS between 0.63 and 0.71 throughout. Aliased energy rose from -129.5 dB at index 0.5 to -58.2 dB at 2, -15.3 dB at 5 (3%), and 73% and 88% of the signal at 10 and 20. THD+N gave the same 34.5% for aliased and clean signals at index 0.5, and at index 10 read lower for the aliased signal (86.4%) than for the clean one (91.0%), because FM's intended sidebands are themselves counted as distortion.
- Fix: Check FM against its expected partials: build or compute the in-band sideband set (carrier plus multiples of the modulator below Nyquist) and measure the energy outside it, or compare with an oversampled render. Do not use a meter or THD+N.
- Why this fix: THD+N assumes the wanted signal is one sinusoid. FM's wanted signal is a spread of sidebands, so THD+N measures the modulation index, not the aliasing.
- Rule of thumb: High-index FM aliases with peak fixed at 1.0 (aliased energy -129 dB at index 0.5, -15 dB at 5, 73% of the signal at 10), and THD+N cannot see it either: it read 34.5% for aliased and clean alike at index 0.5 and lower for the aliased signal at index 10 (86.4% vs 91.0%); measure energy outside the expected sideband set instead.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b09.py loop 43 in Pappydapimp69/Brain, deterministic. Observed: peak 1.000/1.000/1.000/1.000/0.995; aliased energy -129.5/-58.2/-15.3/-1.4/-0.6 dB; THD+N naive 34.5/97.5/98.0/86.4/100.0% and band-limited 34.5/97.5/98.2/91.0/91.3% at index 0.5/2/5/10/20. Bessel values come from numerical integration.
- Composed: ideas:DSP/fm-synthesis/peak-meter-blind-to-aliasing/spectral-or-thd-not-amplitude, sandbox-genesis-fm/E1
- Link: session 2026-09-28, brain train gap batch 9 loop 43
- Sandbox: sandboxes/2026-09-28__train-gap-b09.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)
- Cited-by: 2026-10-09 · projects/local__sandbox-kernel-painting-op-perception.md#E1 · compatible · sandboxes/2026-10-09__op-art-shimmer-needs-eye-shift-and-contrast-but-not-fine-scale.py · observed RESULT: FAIL 9/13 predictions held; coherence straight=1.00 riloid=0.95; energy ratio c9/c1=9.00, lam8/lam32=3.92; flow lam8=0.71 lam32=0.58; direction spread straight=0deg steepest-riloid=3deg. Missed: phase-modulated coherence <0.90, des… · brain train gap pass 5 (slot 4); session_01YFLLRpDsfZpRstb2KT2MQy
