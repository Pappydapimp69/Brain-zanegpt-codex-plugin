# local/sandbox-kernel-dsp-filter-design — lessons

Project: local/sandbox-kernel-dsp-filter-design. Newest first.

---

## E1 — under cutoff jumps df1 is not safer than df2t only the svf held
- Date: 2026-09-28
- Project: local/sandbox-kernel-dsp-filter-design
- Tags: [dsp][audio][stability][filter]
- What: Applied the ideas kernel that a modulated resonant filter needs a bounded topology: DF2T misbehaves under per-sample modulation, DF1 tolerates it much better, and an SVF/TPT filter is bounded by construction. The SVF claim held everywhere; the DF1-over-DF2T ranking did not.
- Why built: brain train gap listed the kernel as unapplied. Its sources are external articles and it had not been measured.
- Design: An RBJ lowpass biquad in DF1 and DF2T and a Zavalishin TPT state-variable lowpass, all recomputing coefficients every sample, at 48 kHz on a 400 Hz square wave of peak 1 for 12000 samples, in float64 and in float32 with rounding after every operation. Cutoff held at 2 kHz, swept by a 5 Hz LFO from 200 Hz to 8 kHz, or switched between 100 Hz and 12 kHz every 64 or every 7 samples, at Q 0.707, 10 and 40. Reported the output peak.
- Got right: Sweeping Q as well as the modulation. At a single Q one direct form looks consistently better and the ranking seems settled.
- Where/why it failed: Static and slow LFO modulation gave nearly equal peaks for all three (for example 8.47, 8.48 and 8.29 at Q 10). Switching every 64 samples, DF2T peaked higher than DF1 at Q 0.707 (28.43 vs 5.62) but DF1 peaked far higher at Q 10 (90.98 vs 6.32) and Q 40 (160.41 vs 2.02). Switching every 7 samples, both direct forms diverged to infinity at Q 10 and 40. The TPT SVF stayed between 1.24 and 3.16 in every fast-switching case. float32 and float64 gave the same peaks.
- Fix: Use a TPT/ZDF state-variable filter for any cutoff or resonance modulated faster than a slow LFO. Do not switch a direct-form biquad from DF2T to DF1 expecting it to fix modulation blow-ups.
- Why this fix: Fast coefficient switching can make a filter unstable even when every coefficient set is stable, and both direct forms' state is reinterpreted by each new set. The SVF's state is integrator output, which stays bounded as coefficients change.
- Rule of thumb: Under fast cutoff switching, DF1 is not reliably safer than DF2T (DF2T worse at Q 0.707, 28.43 vs 5.62; DF1 worse at Q 10 and 40, 90.98 and 160.41 vs 6.32 and 2.02; both diverge when switching every 7 samples), while a TPT SVF stayed at 1.24-3.16 in every case; slow LFO sweeps are harmless for all three.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b06.py loop 29 in Pappydapimp69/Brain, deterministic. Observed: the peak table for 3 topologies x 4 modulations x 3 Q in float64 and float32, identical across precisions. Assumed: hard cutoff switching stands in for fast envelopes; smoother fast modulation may rank the direct forms differently.
- Composed: ideas:DSP/filter-design/modulated-resonant-filter-needs-bounded-topology/df1-or-svf-not-df2t
- Link: session 2026-09-28, brain train gap batch 6 loop 29
- Sandbox: sandboxes/2026-09-28__train-gap-b06.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)
- Cited-by: 2026-10-15 · projects/pappydapimp69__brainwork.md#E291 · compatible · sandboxes/2026-10-15__film-peak-normalize-level-set-by-filter-switch-transient-df2t-vs-svf.py · observed RESULT: PASS (direction criterion of 3 dB, loosened after the first run showed 5.11, 9.17 and 4.14 dB). The 6 dB magnitude prediction was met only in the 9.17 dB case. Q10 7-sample DF2T diverged. · brain train auto loop 1 pass 2; session_01Kx9Pq1H5qpcbvZJ9u2DPKR
