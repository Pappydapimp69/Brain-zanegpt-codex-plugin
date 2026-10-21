# local/sandbox-mismatch-formula-vs-aperiodic-lag — lessons

Project: local/sandbox-mismatch-formula-vs-aperiodic-lag. Newest first.

---

## E1 — sandbox mismatch formula vs aperiodic lag
- Date: 2026-09-30
- Project: local/sandbox-mismatch-formula-vs-aperiodic-lag
- Tags: [ui][state][input][gamedev][testing]
- What: Sandbox re-verifying the closed-form hint-mismatch count for a periodic square wave across lags 0..P, and contrasting it with an aperiodic Thue-Morse waveform.
- Why built: The full-cycle lag sweep lesson and the aperiodic waveform lesson were single-source edges; test the formula and the aliasing claim together from a fresh implementation.
- Design: 600 samples, square wave with period P and window W (P15/W5, P20/W8), mismatch count of state(t) versus state(t-lag) for every lag 0..P, compared with 600/P*2*min(lag,W,P-W,P-lag); Thue-Morse parity of popcount swept over lags 1,2,5,10,15,20,64.
- Got right: The formula matches exactly at every lag for both waves (P15: 80 per step, plateau 400 from lag 5 to 10, back to 0 at lag 15; P20: 60 per step, plateau 480 lags 8-12, 0 at lag 20). Thue-Morse never returns to 0 (400,400,300,300,250,300,384).
- Where/why it failed: Naive assumption that staleness grows monotonically with lag; on periodic state mismatch aliases to zero at whole cycles so a mismatch-based staleness test reports fresh.
- Fix: Do not detect staleness by hint-versus-state agreement on periodic state; use an age tag, and sweep lag through a full cycle when characterizing a resolver.
- Why this fix: Age is independent of waveform periodicity, whereas agreement depends on it and aliases exactly at multiples of the period.
- Rule of thumb: Mismatch is 2*(N/P)*min(lag,W,P-W,P-lag), plateaus then returns to zero at lag equal to one period on periodic signals; aperiodic signals never alias to zero, so test both.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; observed numbers listed above, exact match to the formula at all 32 lag points; the earlier per-step figures of 79/59 were approximations of 80/60.
- Composed: local__age-cutoff-roll-up/E1, sandbox-combined-action-resolver-hint-lag-full-cycle-sweep/E1
- Link: session

