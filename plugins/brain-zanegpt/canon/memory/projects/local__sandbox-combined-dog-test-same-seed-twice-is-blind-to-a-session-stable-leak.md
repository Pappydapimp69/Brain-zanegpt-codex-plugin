# local/sandbox-combined-dog-test-same-seed-twice-is-blind-to-a-session-stable-leak — lessons

Project: local/sandbox-combined-dog-test-same-seed-twice-is-blind-to-a-session-stable-leak. Newest first.

---

## E1 — sandbox combined dog test same seed twice is blind to a session stable leak
- Date: 2026-08-29
- Project: local/sandbox-combined-dog-test-same-seed-twice-is-blind-to-a-session-stable-leak
- Tags: [determinism][state][testing][save]
- What: A deterministic sandbox (explicit LCG, fixed ambient table, no wall-clock) generating a world with and without a leaked non-seeded draw, verified two ways — dog#E12's same-seed-twice byte-identity check and test#E2's stored {seed, count} accounting.
- Why built: dog#E12 records that a seed only reproduces a generated world if EVERY roll goes through the one seeded stream, and prescribes verifying that the same seed twice gives byte-identical output plus grepping the path for ambient entropy. test#E2 prescribes storing the seeded RNG's {seed, count} inside the saved world and banning ambient sources. This tests whether E12's own verification actually detects a leak.
- Design: An eight-draw generator with an optional leak at one index that pulls from a fixed ambient table instead of the seeded stream — modelling an ambient source that is stable within a session (a cached value, a fixed table, a same-millisecond clock read). Both verifications run with and without the leak.
- Got right: Making the ambient source deterministic within the run rather than random, which is the realistic and harder case — a source that varies between runs would be caught by any double-run check, so the interesting question is what happens when it does not.
- Where/why it failed: dog#E12's same-seed-twice check passes with the leak present. Both runs produce byte-identical worlds because the ambient source returns the same value each time, so the prescribed verification reports full determinism while a draw is bypassing the seeded stream entirely. test#E2's stored count catches it immediately — 7 recorded rolls where 8 were expected, because the leaked draw never advanced the stream.
- Fix: Verify seeded-stream integrity by roll-count accounting (test#E2's stored {seed, count} against an expected count for the generation path) rather than by output identity across runs, and treat dog#E12's double-run check as detecting only leaks that vary between runs.
- Why this fix: dog#E12's check is sensitive to the leaked source's VARIABILITY, not to the leak itself. Any ambient source that is stable within a session — which includes the most common real cases, a memoized value or a coarse clock read — passes it. test#E2's count is sensitive to the bypass directly, because a draw that skips the stream necessarily fails to increment it regardless of what value it returns.
- Rule of thumb: dog#E12's same-seed-twice byte-identity check detects only leaks that VARY between runs — sandbox-confirmed it passes cleanly with an ambient draw bypassing the seeded stream, while test#E2's stored roll count catches it at once (7 recorded against 8 expected); verify stream integrity by roll-count accounting, not output identity.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b9/l25.py) and confirmed the leaked run passes same-seed-twice identity (True) while its stored count reads 7 against the expected 8, and the clean run passes both checks. dog#E12 and test#E2 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__dog/E12, pappydapimp69__test/E2
- Link: session_014mRpopK9xnhvk35tT8ozkX

