# local/sandbox-combined-brain-builder-e11-is-a-domain-instance-of-e2 — lessons

Project: local/sandbox-combined-brain-builder-e11-is-a-domain-instance-of-e2. Newest first.

---

## E1 — sandbox combined brain builder e11 is a domain instance of e2
- Date: 2026-08-29
- Project: local/sandbox-combined-brain-builder-e11-is-a-domain-instance-of-e2
- Tags: [balance][gamedesign][simulation][method]
- What: A deterministic sandbox (five fixed day/meter states, no RNG) comparing a meter-only encounter scale against a bounded-multiplier scale anchored on player power, measuring the enemy-to-player power ratio across the state space.
- Why built: brain-builder#E11 records that scaling an encounter off an accumulating meter alone gave a heat-60 raider roughly 91 power against a day-10 player's 24, so the aggressive stance lost every fight, and that the symptom presents as "this stance is underpowered," inviting tuning the wrong thing. brain-builder#E2 records that a BOUNDED stat lever cannot be balanced against an UNBOUNDED one by tuning coefficients and that the lever's SHAPE must change. This tests whether E11 is an independent lesson or a domain instance of E2.
- Design: Player power grows linearly with day. The meter-only enemy scales linearly with heat, unanchored to the player; the bounded alternative scales player power by a capped multiplier derived from heat. Five day/heat states spanning low and high meter at low and high player progression, scored by power ratio.
- Got right: Recentring the bounded multiplier around 1.0 after a first construction placed its floor above player power and made the player lose in every state, which would have compared two broken curves rather than a broken one against a working one.
- Where/why it failed: The meter-only scale produces power ratios from 0.29x to 3.75x, a spread of 3.46, with a worst case of a 3.75x overmatch at exactly E11's reported condition — high meter against an early-game player. The bounded multiplier holds ratios inside 0.70x to 1.50x, a spread of 0.80. No coefficient on the meter-only curve fixes both ends, because the player term is absent from it entirely.
- Fix: Recognise E11's remedy as an instance of E2's rather than a separate rule — when an unbounded accumulator drives a quantity that must stay commensurate with a bounded one, the fix is always to change the shape (anchor it to the bounded quantity and cap it), never to retune its coefficient.
- Why this fix: E2 was recorded about stat levers within combat and E11 about encounter scaling, so they read as neighbouring but distinct balance findings. The sandbox shows the mechanism is identical — an unbounded term compared against a bounded one — and that E11's prescribed remedy is literally E2's prescription applied in a different domain, which means E2's diagnostic (round-robin over equal-total builds with per-axis correlation) should also transfer.
- Rule of thumb: brain-builder#E11's meter-driven encounter blowout is a domain instance of brain-builder#E2's bounded-versus-unbounded lever, not an independent lesson — sandbox-confirmed a meter-only scale spanning 0.29x to 3.75x power ratio (worst case 3.75x overmatch at high meter against an early player) versus 0.70x to 1.50x once bounded and anchored to player power.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b7/l20.py), including a first construction whose bounded multiplier floor sat above player power and made the comparison meaningless; confirmed meter-only ratios of 0.29x-3.75x (spread 3.46) against bounded ratios of 0.70x-1.50x (spread 0.80). brain-builder#E11 and brain-builder#E2 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__brain-builder/E11, pappydapimp69__brain-builder/E2
- Link: session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-10-13 · projects/pappydapimp69__brainwork.md#E189 · incompatible · sandboxes/2026-10-13__meter-only-encounter-scale-makes-fight-length-degenerate-once-meter-saturates.py · observed RESULT: FAIL meter_only wins 1 ticks 3-6; anchored wins 12 ticks 4-6; post-saturation meter-only ticks 3, 4, 5, anchored 6; hit points x1 anchored ticks 1. · scheduled brain train session, loop 1 pass 2; session_01UeKMwUeVxtmySB3P82SSXJ
