# local/sandbox-kernel-gamedev-feedback — lessons

Project: local/sandbox-kernel-gamedev-feedback. Newest first.

---

## E1 — correlated gates break the product rule for tell rates
- Date: 2026-09-28
- Project: local/sandbox-kernel-gamedev-feedback
- Tags: [gamedev][feedback][measurement][probability]
- What: Applied the ideas kernel that a tell's observed rate is its nominal rate times each gate's open fraction over the real window length, sized by the median window. The product held for independent gates, failed for correlated ones, and the median-versus-mean advice depends on the question being asked.
- Why built: brain train gap listed the kernel as unapplied; it came from MIRAGE's monster flicker and had not been modelled.
- Design: A 0.07/s roll in 0.1 s steps over 4000 windows with lognormal lengths (median 7 s). A companion-in-range gate open 40% of the time (3 s mean dwell) and 8 candidate monsters each on screen 20% of the time (1.5 s dwell). A flicker is visible when the companion is in range and the picked candidate is on screen. Run with independent gates, and with on-screen probability 50% in range and 0 out of range (the same 20% marginal). Then picks restricted to on-screen candidates.
- Got right: Keeping each gate's marginal fixed while correlating them, so any change in the observed rate comes from the correlation alone.
- Where/why it failed: With independent gates the observed rate was 0.0057/s against a product of 0.0056/s, one visible flicker per 176 s. With the same marginals but correlated gates it was 0.0103/s, 1.8x the product. Windows had a median of 7.2 s and a mean of 11.4 s; a median window had a 4.0% chance of a visible flicker, but 6.1% of all windows contained one, matching the mean-based 6.2%, because long windows hold most occurrences. Restricting picks to on-screen candidates raised the visible rate 4.3x while total firings fell from 0.070 to 0.059/s.
- Fix: Measure the joint open fraction of the gates in real play instead of multiplying marginals. Use the median window for what a typical player sees and the mean for what fraction of windows contain a tell.
- Why this fix: The product rule assumes independence, and gameplay gates such as proximity and visibility usually move together. The two window statistics answer different questions and here differed 1.5x.
- Rule of thumb: A tell's visible rate equals nominal x gate fractions only for independent gates (0.0057 vs 0.0056/s); correlated gates with the same marginals gave 0.0103/s, 1.8x the product, so measure the joint open fraction; a median window predicts a typical player's chance (4.0%) while the share of windows with a tell tracks the mean (6.1% observed vs 6.2%).
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b06.py loop 27 in Pappydapimp69/Brain, deterministic seeded simulation. Observed: 0.0057 and 0.0103/s; median 7.2 s, mean 11.4 s; 4.0/6.2% estimates vs 6.1% observed; restriction 4.3x with firings 0.0586 vs 0.0700/s. The gate dwell times are assumptions, not MIRAGE's measured values.
- Composed: ideas:gamedev/feedback/rate-a-perceptual-tell-by-its-observed-rate/gate-product-not-nominal-probability
- Link: session 2026-09-28, brain train gap batch 6 loop 27
- Sandbox: sandboxes/2026-09-28__train-gap-b06.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)
- Cited-by: 2026-10-08 · projects/pappydapimp69__brain.md#E96 · compatible · sandboxes/2026-10-08__calibration-first-mark-confidence.py · observed RESULT: PASS first-mark certainty overstated; correlated cues inflate; recalibration is distribution-bound; fixing the cue beats recalibrating. Key numbers: 0.793; 0.999 vs 0.901 vs 0.970; ECE 0.195 to 0.010 to 0.197; Lean-line 1.000. · session 2026-10-08, brain train auto pass 1 (kernel)
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E444 · compatible · sandboxes/2026-10-18__adoption-friction-felt-wound-funnel.py · observed RESULT: PASS merit 366 < simple 535; wound flips 721 > 600; junk 50; gates corr 800 vs indep 316 vs product 328 · scheduled brain train auto pass 1 (loop 1); session_01NZDPzU2KzUnFJgGMC4knps
