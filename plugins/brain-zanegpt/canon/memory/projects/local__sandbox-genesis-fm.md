# local/sandbox-genesis-fm — lessons

Project: local/sandbox-genesis-fm. Newest first.

---

## E3 — fm meter silence is not idle
- Date: 2026-07-13
- Project: local/sandbox-genesis-fm
- Tags: [audio][dsp][realtime][harness][state][testing]
- What: A bounded FM output can meter as silent while the internal feedback/decay state never reaches exact idle. Peak/RMS silence is therefore not a valid realtime voice-termination oracle when the state update depends on exact zero.
- Why built: `brain train` aimed at re-verifying the edge between `sandbox-combined-audio-realtime` and `sandbox-genesis-fm`. The interaction claim was that a Genesis-style bounded operator can hide a realtime termination bug: the audible output looks silent, but the voice remains internally active forever if a subnormal decay fixed point is not flushed to zero.
- Design: Built `sandbox-genesis-fm-realtime-idle.js`, a deterministic JavaScript model with: - 30000 rendered samples. - Internal feedback initialized to `Number.MIN_VALUE`. - A decay update of `feedback *= 0.9`. - A bounded FM-style output meter using `Math.sin(feedback)`. - A meter silence floor of `1e-300`. - Two policies: no flush-to-zero, and flush-to-zero below `1e-300`.
- Got right: The sandbox measures the failure at two separate locations: the bounded audio output and the internal liveness state. That keeps the test from mistaking "inaudible" for "terminated."
- Where/why it failed: Without flush-to-zero, the feedback state stayed at `5e-324` for all 30000 samples and never reached exact idle. The output peak was also `5e-324` and RMS underflowed to `0`, so the meter read silent while `activeSamples` remained 30000.
- Fix: Use an explicit flush-to-zero or epsilon-idle threshold for the internal voice state. Do not drive realtime voice lifecycle decisions from peak/RMS meters downstream of bounded nonlinear operators.
- Why this fix: With flush-to-zero below `1e-300`, the sandbox reached exact idle at sample 1 and had only 1 active sample. The output meter still read silent in both cases, proving the fix has to live in the state/lifecycle path rather than the bounded audio meter.
- Rule of thumb: For bounded DSP operators, meter silence is an output property, not a lifecycle property. Terminate realtime voices from internal state thresholds, and flush subnormal decay state explicitly.
- Provenance (verified/assumed): Verified first-hand on 2026-07-13 by running `node sandbox-genesis-fm-realtime-idle.js` in `C:\Users\Kompooter\Documents\Brain`. Observed: no flush-to-zero = 30000 active samples, no first idle sample, final feedback `5e-324`, exact idle `false`, peak `5e-324`, RMS `0`, meter silent `true`; flush-to-zero = 1 active sample, first idle sample 1, final feedback `0`, exact idle `true`, meter silent `true`.
- Composed: sandbox-combined-audio-realtime/E2, sandbox-genesis-fm/E1
- Link: Sandbox: `sandbox-genesis-fm-realtime-idle.js`

## E2 — fm instability verification inherits fft length bug
- Date: 2026-07-13
- Project: local/sandbox-genesis-fm
- Tags: [audio][dsp][testing]
- What: Combining three related genesis sandboxes at once (all connected to the main cluster but not yet directly linked to each other) to raise several edges in one sandbox. Composed: projects/local__sandbox-genesis-fm.md#E1 (a bounded-output nonlinearity — an FM operator is `sin(...)` — pins peak amplitude by construction, so a peak/amplitude meter is structurally blind to instability inside it; measure the failure where it actually lives via a full-render FFT for aliased/inharmonic energy), projects/local__sandbox-genesis-mix.md#E1 (a radix-2 FFT returns SILENT garbage on non-power-of-2 length; guard with `(n & (n-1))===0` or feed a power-of-2 slice, comparing on absolute energy), and projects/local__sandbox-genesis-psg.md#E1 (a real documented hardware noise-LFSR period — Sega SN76489, tap 0x0009 — is 57337, not a power of 2 and not `2^n-1`). Built and ran a sandbox verifying that fm#E1's OWN prescribed fix (full-render FFT) is not self-sufficient — it silently inherits mix#E1's exact vulnerability — and that psg#E1's real, documented hardware period is precisely the kind of realistic, non-contrived buffer length (not an artificial edge case) that would trigger it, since rendering one full noise-channel cycle for a test is a natural thing to do.
- Why built: fm#E1 prescribes "measure via a full-render FFT" as the fix for peak-meter blindness, without checking whether that prescribed fix itself has a length-dependent failure mode. mix#E1's bug was recorded in an unrelated context (an upstream resample/trim stage producing a non-power-of-2 length) with no connection drawn to fm#E1's verification advice. psg#E1's specific period value (57337) was recorded purely as a hardware-fidelity fact, with no connection drawn to buffer-length hazards elsewhere in the audio pipeline. None of the three entries states the others compose into a concrete, realistic danger.
- Design: `engine.mjs` renders a deterministic FM-operator-style buffer at exactly `n=57337` samples (psg#E1's real, unaltered documented period) — a low-frequency "healthy" carrier (`sin(i*0.02)`) hard-clipped to `[-1,1]` (satisfying fm#E1's peak-bounding claim), with a higher-frequency "aliased/inharmonic" artifact injected ONLY in the last 300 samples (57037–57336), standing in for instability that only manifests after extended drive time. A `naiveArtifactCheck` models mix#E1's exact bug: it only ever processes the largest power-of-2 PREFIX (32768 of 57337 samples), silently discarding the rest. A `fixedArtifactCheck` models mix#E1's own prescribed fix: zero-pad to the next power of 2 (65536) and process all 57337 real samples. Both checks are run on the artifact-present render AND on an otherwise-identical CLEAN render (no tail artifact) to make the comparison differential rather than threshold-based — a check that reports the identical result for both is, by construction, blind to the artifact.
- Got right: fm#E1's own claim about peak meters was independently confirmed in this same sandbox — the artifact-present render's peak amplitude never exceeded `1`, exactly as fm#E1 predicts, even though the render genuinely contains extra high-frequency content in its tail.
- Where/why it failed: The naive check (fm#E1's prescribed FFT-based fix, unguarded) reported the EXACT SAME energy value (`26.197353`) for the artifact-present render and the clean render — it cannot distinguish them at all, because its processed window (samples 0–32767) ends at `32768`, entirely BEFORE the artifact zone (57037–57336) even begins. fm#E1's own recommended verification technique, taken literally without also applying mix#E1's guard, is exactly as blind to this instability as the peak meter it was meant to replace.
- Fix: The guarded/fixed check (mix#E1's zero-pad-to-next-power-of-2 fix, applied to fm#E1's full-render-FFT technique) clearly distinguished the two cases — `107.913657` (artifact present) vs. `45.862631` (clean), a 2.35× difference — because it processes all 57337 real samples, including the tail where the artifact lives.
- Why this fix: None of the three individual fixes is novel — the value of this three-way composition is showing that fm#E1's fix and mix#E1's fix are not independent techniques from unrelated domains that happen to share a tag; fm#E1's fix LITERALLY REQUIRES mix#E1's guard to work at all, and psg#E1 supplies the concrete evidence that the triggering buffer length (57337) is not a hypothetical edge case but an actual, documented, realistic value a real audio-DSP pipeline would produce.
- Rule of thumb: When implementing fm#E1's own advice — verify a bounded nonlinearity's stability via a full-render FFT/spectral check rather than a peak meter — that check MUST independently guard for or handle non-power-of-2 buffer lengths (mix#E1), because real, non-contrived render lengths (a full LFSR/noise-channel cycle, an arbitrary session duration, a resampled buffer) are routinely NOT powers of 2, and psg#E1 shows a real hardware value (57337) is a completely ordinary instance of exactly the length class that would silently defeat an unguarded FFT-based check.
- Provenance (verified/assumed): VERIFIED first-hand — built `engine.mjs` (zero RNG, zero wall-clock, a fixed deterministic render function of sample index), confirmed peak amplitude stays `<=1` despite a genuine tail artifact, confirmed the naive (unguarded) FFT-style check reports IDENTICAL energy for artifact-present vs. clean renders (fully blind), and confirmed the fixed (zero-padded) check reports a clear 2.35× difference between them. One measurement-design bug was found and fixed during sandbox iteration (an initial absolute-energy threshold falsely reported the naive check as blind due to nonzero baseline high-frequency content in the healthy carrier itself — corrected to a differential artifact-vs-clean comparison, which is the methodologically sound test). Confirmed deterministic/reproducible across two independent process invocations of `node engine.mjs`, output diffed byte-identical.
- Link: session 01KxkbJUq8YajH8GokSZYYHy; combining sandbox-genesis-fm + sandbox-genesis-mix + sandbox-genesis-psg (a group-of-3, not yet directly co-verified with each other); sandbox `engine.mjs`, scratchpad `loop3-genesis-triple/` (run twice as separate process invocations, outputs diffed byte-identical)
- Composed: local/sandbox-genesis-fm/E1, local/sandbox-genesis-mix/E1, local/sandbox-genesis-psg/E1

## E1 — bounded nonlinearity hides instability from amplitude meter
- Date: 2026-07-05
- Project: local/sandbox-genesis-fm
- Tags: [audio][dsp][harness]
- What: A verification of a YM2612-style FM operator's feedback stability used
  peak sample amplitude as the pass/fail observable — expecting unstable
  feedback to "blow up" the signal. Every case (stable and unstable, correct
  and buggy feedback) reported peak = 1.00, so the test could distinguish
  nothing.
- Why built: Sandbox emulation of the Sega Genesis YM2612 FM chip (4-operator
  phase modulation with operator-1 self-feedback), checking that feedback
  averaging of the last TWO operator outputs (what the hardware does) behaves
  better than feeding back a single previous sample.
- Design: The feedback sweep rendered a note at several feedback depths, for
  both the single-sample and two-sample-average feedback paths, and compared
  `max(abs(sample))`.
- Got right: The FM synthesis core itself was correct (phase modulation, right
  native sample rate ~53267 Hz, symmetric sidebands) — the flaw was purely in
  the chosen measurement.
- Where/why it failed: An FM operator's output is `sin(phase + mod)`, which is
  intrinsically bounded to [-1, 1] no matter how violent the modulation. So
  "peak amplitude" is a quantity the failure mode literally cannot move — the
  instability of runaway FM feedback is NOT amplitude growth, it is spectral:
  the feedback generates harmonics above Nyquist that alias/fold back down into
  the band as inharmonic hash. A flat 1.00 column reads as "all cases
  identical" when they are wildly different in the spectrum.
- Fix: Measure the observable the failure actually moves — fraction of spectral
  energy NOT at integer multiples of the fundamental (aliased/inharmonic
  energy), via an FFT over the whole render. With that metric the paths
  separate cleanly (e.g. at mid feedback, single-sample 0.112 vs two-sample
  0.044 aliased-energy). Also scale the driven parameter into the chip's real
  range (feedback 0..7), or over-driving swamps the very effect under test in
  saturation-like hash for both paths.
- Why this fix: A test can only detect a failure through a quantity the failure
  changes. For a bounded nonlinearity (any `sin`/`tanh`/clipping stage), the
  output magnitude is pinned by construction, so amplitude is the one thing
  that stays constant while everything meaningful happens in the frequency
  domain. The observable has to be chosen from the failure's actual mechanism.
- Rule of thumb: A bounded-output nonlinearity (FM operator = `sin`, or any
  `tanh`/hard-clip) pins peak amplitude by construction, so an amplitude/peak
  meter is structurally blind to instability inside it — measure the failure in
  the spectrum (aliased / inharmonic energy over a full-render FFT), and drive
  the parameter only within its real range or over-driving swamps the effect.
- Provenance (verified/assumed): VERIFIED first-hand this session — observed
  the flat peak=1.00 column across all feedback depths and both feedback
  paths, then confirmed a spectral aliased-energy metric separates them, in an
  offline Node FFT harness rendering the YM2612 FM core.
- Link: session (this one, dog-game-continue-oc3xqh); scratchpad
  genesis/sandboxA_ym2612_fm.mjs.
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-bloom-audio.md#E5 · compatible · no sandbox · session (query brain for "keep training as you were"), sandbox script loop_fm_subnormal2.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-lfsr-peak-meter.md#E1 · compatible · no sandbox · Sandbox: `sandbox-lfsr-fm-spectrum-resume.js`
- Cited-by: 2026-07-13 · projects/local__sandbox-genesis-fm.md#E2 · compatible · no sandbox · session 01KxkbJUq8YajH8GokSZYYHy; combining sandbox-genesis-fm + sandbox-genesis-mix + sandbox-genesis-psg (a group-of-3, not yet directly co-verified with each other); sandbox `engine.mjs`, scratchpad `loop3-genesis-triple/` (run twice as separate process invocations, outputs diffed byte-identical)
- Cited-by: 2026-07-13 · projects/local__sandbox-genesis-fm.md#E3 · compatible · no sandbox · Sandbox: `sandbox-genesis-fm-realtime-idle.js`
- Cited-by: 2026-09-28 · projects/local__sandbox-kernel-dsp-fm.md#E1 · compatible · sandboxes/2026-09-28__train-gap-b09.py · session 2026-09-28, brain train gap batch 9 loop 43
