# local/sandbox-kernel-dsp-lfsr — lessons

Project: local/sandbox-kernel-dsp-lfsr. Newest first.

---

## E1 — a non primitive lfsr puts one seed in eight on a short cycle
- Date: 2026-09-28
- Project: local/sandbox-kernel-dsp-lfsr
- Tags: [dsp][audio][algorithm][emulation]
- What: Applied the ideas kernel that an LFSR's period is set by whether its taps are primitive, and that non-primitive taps split the states into several cycles whose choice depends on the seed. Walking all 65536 states of the SN76489-style register gave the exact cycle structure and how likely an off-hardware seed is to hit a short cycle.
- Why built: brain train gap listed the kernel as unapplied. sandbox-genesis-psg/E1 measured the 57337 period from the reset seed only; the other cycles and the seeds that reach them were unmeasured.
- Design: Right-shifting Fibonacci LFSRs with parity feedback into the top bit. Every state was followed until it joined a known cycle, for the 16-bit register with taps 0 and 3 (mask 0x0009), a 16-bit register with mask 0x002D, and a 15-bit register with taps 0 and 1. Reported all cycle lengths and the period reached from several seeds.
- Got right: Enumerating every state instead of stepping from one seed. From the reset seed the register just looks like it has a 57337 period.
- Where/why it failed: Taps 0 and 3 split the 65536 states into exactly four cycles: 57337, 8191, 7 and the all-zero state. The seeds tried (0x8000, 0x0001, 0x4000, 0x1234) all reached the 57337 cycle, but 8198 of the 65535 non-zero seeds, 12.5%, sit on the 8191 or 7 cycle. The 0x002D register had one 65535 cycle for every non-zero seed, and the 15-bit taps-0,1 register one 32767 cycle.
- Fix: Seed an emulated noise register with the hardware's documented reset value, never a random or zero value, and check the period from that seed. When writing a new generator, pick a primitive tap set and verify it has one cycle over all non-zero states.
- Why this fix: With a non-primitive tap set the period is a property of the seed, so an emulator that seeds differently can produce 8191-step or 7-step noise from the right taps.
- Rule of thumb: The SN76489-style 16-bit LFSR (taps 0,3) has four cycles, 57337, 8191, 7 and 1, so the reset seed gives 57337 but 12.5% of non-zero seeds (8198 of 65535) fall on the 8191- or 7-step cycle; seed with the hardware reset value, and use a primitive tap set (for example 0x002D, one 65535 cycle) for new generators.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b08.py loop 39 in Pappydapimp69/Brain, exhaustive over all states, deterministic. Observed cycle lengths 57337/8191/7/1 for 0x0009, 65535/1 for 0x002D, 32767/1 for the 15-bit taps 0,1. Whether real hardware can ever be seeded into the short cycles was not checked.
- Composed: ideas:DSP/lfsr-noise/tap-polynomial-not-width-sets-period/non-primitive-taps-fracture-the-cycle, sandbox-genesis-psg/E1
- Link: session 2026-09-28, brain train gap batch 8 loop 39
- Sandbox: sandboxes/2026-09-28__train-gap-b08.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)
- Cited-by: 2026-10-14 · projects/pappydapimp69__brainwork.md#E266 · compatible · sandboxes/2026-10-14__sandbox-psg-noise-cycle-audible-only-when-short.py · observed RESULT: PASS only the 7-step cycle shows in the spectrum (empty 0.93); the 8191-step cycle stays spectrally white (empty 0.02 at 32768) but autocorrelation at lag 8191 is 1.00 vs -0.14; spectrally audible seeds 7/65535 = 0.0107%, not 12.5% · brain train auto loop 2 pass 2 edge mode, unattended run 2026-10-14; session_018eKNqSCZk9zsMEo2AXSjsk
