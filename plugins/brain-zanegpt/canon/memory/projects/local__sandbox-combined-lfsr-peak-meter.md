# local/sandbox-combined-lfsr-peak-meter — lessons

Project: local/sandbox-combined-lfsr-peak-meter. Newest first.

---

## E1 — lfsr resume peak meter blind
- Date: 2026-07-13
- Project: local/sandbox-combined-lfsr-peak-meter
- Tags: [audio][dsp][determinism][harness][state][testing]
- What: Reloading an audio LFSR from its default seed instead of its live register can change the rendered signal while a bounded/clipped output peak meter remains identical. A full-render spectral or canonical fingerprint detects the resume bug where a peak meter cannot.
- Why built: `brain train` aimed at re-verifying the edge between `sandbox-combined-bloom-audio` and `sandbox-genesis-fm`. The interaction claim was that the LFSR state-persistence bug from the audio/Bloom composition is not reliably observable through a Genesis-style bounded amplitude check; it needs a whole-render comparison at the signal content level.
- Design: Built `sandbox-lfsr-fm-spectrum-resume.js`, a deterministic JavaScript model with: - 256 total samples and a resume split at sample 96. - A 16-bit LFSR initialized from `DEFAULT_SEED`. - A persisted-current-register resume path and a broken default-seed resume path. - A clipped driven carrier plus LFSR noise term, bounding peak output to `[-1, 1]`. - Sample mismatch counts against a continuous reference render. - A 32-bin DFT magnitude fingerprint delta against the same reference.
- Got right: The sandbox separates amplitude safety from deterministic content identity. Both resumed renders are valid bounded audio by peak, but only one preserves the live generator state and reproduces the continuous render.
- Where/why it failed: The broken resume reloaded `DEFAULT_SEED` at the split instead of the live LFSR register. It produced 48 sample mismatches and a 32-bin spectral delta of `77.161723` against the continuous reference, while the peak meter stayed pinned at `1`, equal to the reference peak.
- Fix: Persist the current LFSR register at save/suspend points, not just the construction seed. Verify resume paths with a canonical full-render comparison or spectral fingerprint, not with peak amplitude alone.
- Why this fix: The persisted-register path reproduced the full render exactly: 0 sample mismatches, peak `1`, reference peak `1`, and spectral delta `0`. The broken default-seed path had the same peak values but different content, proving peak amplitude is structurally blind to this class of bounded-output resume failure.
- Rule of thumb: For bounded audio generators, a peak meter answers "did output stay in range," not "did the generator resume the same signal." Save live generator state and test replay/resume with content fingerprints.
- Provenance (verified/assumed): Verified first-hand on 2026-07-13 by running `node sandbox-lfsr-fm-spectrum-resume.js` in `C:\Users\Kompooter\Documents\Brain`. Observed: persisted current LFSR register = 0 mismatches, peak `1`, reference peak `1`, spectral delta `0`; reload default LFSR seed = 48 mismatches, peak `1`, reference peak `1`, spectral delta `77.161723`.
- Composed: sandbox-combined-bloom-audio/E3, sandbox-genesis-fm/E1
- Link: Sandbox: `sandbox-lfsr-fm-spectrum-resume.js`
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-creative-training.md#E2 · incompatible · sandboxes/2026-10-15__capped-drain-delays-lfsr-restore-into-permanent-phase-slip.py · observed RESULT: PASS capped FIFO applies the live-register restore on callback 32 and stays wrong after it (14.2% of later samples, 14.8% overall) with peak 1.000 = ref, dft delta 404.9, crc differs; priority slot 0% at 585 us worst; uncapped 0% a… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 5 pass 2
