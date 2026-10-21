# local/sandbox-genesis-psg — lessons

Project: local/sandbox-genesis-psg. Newest first.

---

## E2 — seed audio engine sn76489 tap externally confirmed plus 16bit detail
- Date: 2026-07-13
- Project: local/sandbox-genesis-psg
- Tags: [audio][audio-engine][dsp]
- What: `brain train new-domain audio-engine` (0 entries tagged, despite substantial existing `[audio][dsp]` coverage of the same real Sega Genesis sound-chip emulation work — genesis-fm, genesis-mix, genesis-psg). `local__sandbox-genesis-psg.md#E1` records the SN76489 noise channel's real hardware tap mask (0x0009, feeding bit 15) producing a measured period of 57337, not the textbook maximal-length 65535, and warns against a "period must be 2^n-1" assertion that would wrongly reject correct hardware behavior. External research (WebSearch — WebFetch blocked by this session's confirmed org egress policy) against SMS Power's SN76489 development documentation confirms both the tap mask (0x0009, bits 0 and 3 fed back to bit 15) and the exact period (57337) as accurate, AND surfaces a detail genesis-psg#E1 doesn't record: for Genesis specifically, Sega's PSG implementation deliberately EXPANDS the noise generator from the original Texas Instruments 15-bit LFSR to 16 bits — the non-maximal period isn't just "a different tap on the same-size register," it's a structurally different (larger) shift register than the chip's own documented ancestor.
- Why built: genesis-psg#E1 cites the tap mask and period as a real, live-measured hardware fact but doesn't note that Sega's Genesis-era PSG core is itself a documented MODIFICATION of the original SN76489 (bit-width expansion), which is directly relevant context for anyone extending this emulation to a DIFFERENT Sega platform (Master System, Game Gear) or comparing against the original Texas Instruments chip, where the register width itself may differ.
- Design: Not a code sandbox — a pure external-fact verification and enrichment. Verified via WebSearch (`"SN76489 noise channel LFSR tap feedback period 0x0009 white noise Sega Genesis hardware documentation"`) against SMS Power's SN76489 development page, a source specifically dedicated to this chip family's hardware documentation across Sega platforms.
- Got right: genesis-psg#E1's core claim is exactly correct and independently confirmed — tap mask 0x0009, feedback to bit 15, and the specific period 57337 all match the external documentation precisely, with no discrepancy found.
- Where/why it failed: N/A — not a bug, an enrichment gap. genesis-psg#E1 states the tap/period as if it's simply "the real hardware value" without noting it's specific to Sega's WIDENED (16-bit) noise generator, not the original TI SN76489's 15-bit one — a detail that matters if this emulation code, or its "don't assume maximal length" rule of thumb, is ever reused for the original TI chip or a different Sega platform's PSG variant, where bit-width itself is a variable, not just the tap.
- Fix: Not applicable (enrichment, no defect). Record explicitly: genesis-psg#E1's cited tap (0x0009) and period (57337) are specific to Sega's Genesis-era 16-bit-expanded noise LFSR, not the original Texas Instruments SN76489's 15-bit design — if extending this emulation work to target the original TI chip or a different Sega platform, re-verify BOTH the tap mask and the register width, not just the tap.
- Why this fix: The rule of thumb genesis-psg#E1 already states ("don't assume maximal-length, measure the real period") is strengthened, not contradicted, by this — it's one more concrete instance of "don't assume the textbook/reference values transfer across silicon revisions or platform variants without checking," now with the added specificity that even the REGISTER WIDTH itself can't be assumed constant across a chip family.
- Rule of thumb: When citing a specific real-hardware constant (a tap mask, a measured period, a register width) for an emulated audio chip, record which SPECIFIC silicon/platform variant it was measured against, not just "the real hardware value" — chip families with multiple silicon revisions or platform-specific modifications (here: Sega's Genesis-era PSG widening the LFSR from 15 to 16 bits versus the original Texas Instruments design) can differ in more than the parameter you happened to be testing.
- Provenance (verified/assumed): Verified first-hand — genesis-psg#E1's text re-read directly from canon via `brain query`. External claims (tap mask, period, and the 15-bit-to-16-bit widening detail) verified via live, attributable WebSearch results describing SMS Power's SN76489 development documentation, a source specifically maintained for this chip family across Sega platforms. Direct WebFetch to smspower.org was not attempted given this session's confirmed org egress-policy block on general web hosts.
- Link: session (brain train new-domain audio-engine, external research); WebSearch query as listed in Design
- Composed: local/sandbox-genesis-psg/E1

## E1 — noise lfsr period must be measured not assumed maximal
- Date: 2026-07-05
- Project: local/sandbox-genesis-psg
- Tags: [audio][dsp][state]
- What: Emulating the Sega SN76489 PSG "white noise" channel, I assumed its
  16-bit linear-feedback shift register (taps at bits 0 and 3, mask 0x0009)
  would produce a maximal-length sequence — period 2^16 - 1 = 65535 — because
  "white noise = maximal-length LFSR" is the textbook expectation. Measuring
  the actual period showed 57337, not 65535.
- Why built: A sandbox emulation of the Genesis's second sound chip (SN76489:
  3 square tone channels + 1 LFSR noise channel), verifying square frequency,
  logarithmic attenuation, and the noise generator's sequence behavior.
- Design: The LFSR steps `reg = (reg >> 1) | (parity(reg & tap) << (width-1))`,
  output = LSB. Period was measured by counting steps until the register
  returned to its reset state (0x8000).
- Got right: Everything else checked out — square freq = clock/(32n) with the
  n=0→1 edge guarded, 2 dB-per-step logarithmic attenuation (0.7943x/step),
  and the periodic-noise mode (tap bit 0 only) cycling with period = register
  width (16). The measurement method itself was sound.
- Where/why it failed: The assumption, not the code. A white-noise LFSR is
  maximal-length ONLY if its tap mask corresponds to a PRIMITIVE polynomial.
  The Sega tap 0x0009 is not primitive, so the register visits only a subset
  of states and cycles early: period 57337 = 7 × 8191 (8191 = 2^13 - 1), a
  genuine LFSR sub-cycle. Had I "verified" the emulator by asserting period ==
  65535, I'd have swapped in a maximal-length tap and made the noise sound
  audibly wrong versus the hardware it's meant to reproduce. (Adjacent runs
  confirmed how tap-sensitive this is: a plausible wrong 16-bit tap 0x0003
  collapses the period to 255; the 15-bit TI variant IS maximal at 32767.)
- Fix: Measure the LFSR's real period empirically and treat THAT as the spec —
  never assert maximal length as a correctness gate. When the goal is hardware
  fidelity, match the actual (possibly non-primitive) tap mask the silicon
  uses, even though it produces a shorter, "less white" sequence.
- Why this fix: Period is a computable, exact property of (width, tap); it's
  cheap to measure and it's the ground truth. "Should be maximal" is an
  aesthetic expectation that real hardware routinely violates — and for an
  emulator, matching the hardware's imperfect sequence IS the correctness
  criterion, not textbook maximal-length whiteness.
- Rule of thumb: Don't assume a noise/PRNG LFSR is maximal-length — measure its
  period (steps until the state repeats). A tap mask is maximal only for a
  primitive polynomial, and real hardware (e.g. the Sega SN76489 white-noise
  tap 0x0009 → period 57337, not 65535) often uses a non-primitive one on
  purpose; a "period must be 2^n-1" assertion rejects the hardware-correct
  behavior. For fidelity, copy the actual tap, not the textbook one.
- Provenance (verified/assumed): VERIFIED first-hand this session — computed
  period 57337 (= 7 × 8191) for the 16-bit 0x0009 tap in an offline Node
  LFSR harness, contradicting the maximal-length assumption; confirmed
  tap-sensitivity across several (width, tap) configs. ASSUMED (widely cited
  but not verified against silicon here) that 0x0009 is the exact Sega tap;
  the lesson holds regardless of that specific attribution.
- Link: session (this one, dog-game-continue-oc3xqh); scratchpad
  genesis/sandboxB_sn76489_psg.mjs.
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-bloom-audio.md#E2 · compatible · no sandbox · session (query brain for "5 loops" — loop 3/5), sandbox script loop3_psg_fft.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-bloom-audio.md#E3 · compatible · no sandbox · session (query brain for "5 loops" — loop 5/5), sandbox script loop5_psg_save.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-bloom-audio.md#E7 · compatible · no sandbox · session (query brain for "loop: aim, compose from recorded lessons, sandbox, file" — loop 1), sandbox scripts reverify1_mix_psg.mjs/reverify1b.mjs/reverify1c_period.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/local__sandbox-genesis-fm.md#E2 · compatible · no sandbox · session 01KxkbJUq8YajH8GokSZYYHy; combining sandbox-genesis-fm + sandbox-genesis-mix + sandbox-genesis-psg (a group-of-3, not yet directly co-verified with each other); sandbox `engine.mjs`, scratchpad `loop3-genesis-triple/` (run twice as separate process invocations, outputs diffed byte-identical)
- Cited-by: 2026-07-13 · projects/local__sandbox-genesis-psg.md#E2 · compatible · no sandbox · session (brain train new-domain audio-engine, external research); WebSearch query as listed in Design
- Cited-by: 2026-09-28 · projects/local__sandbox-kernel-dsp-lfsr.md#E1 · compatible · sandboxes/2026-09-28__train-gap-b08.py · session 2026-09-28, brain train gap batch 8 loop 39
- Audited: 2026-10-13 · modeled · No sandbox file for this entry is stored, so I judged the entry text and re-ran its stated recurrence myself in Python (shift right, parity of bits under mask 0x0009 into bit 15, start 0x8000): the period computes as 57337 (equal to 7 times 8191), a mask of 0x0003 gives 255, and the 15-bit variant at 0x0003 gives 32767, all matching the entry, and a sweep over all 65535 nonzero start states found exactly three cycles of lengths 57337, 8191 and 7, so the period is computed, not assumed, and the 57337 cycle holds the reset state. The measured-not-assumed rule of thumb is therefore sound as arithmetic. What was tested is a hand-written LFSR, though, and the claim that this is the actual Sega SN76489 white-noise tap and behaviour, and that it differs from the textbook tap on purpose, is about real hardware and was not checked against a datasheet, a chip dump or a reference emulator; the entry's hardware fidelity half is therefore modeled rather than pass. It also does not cover the other start states (a different seed can land on the 8191 or 7 cycle). · scheduled brain train session, 2026-10-13, audit pass; session_01KgwUVJ8YiFpBjfevwrK7fS
