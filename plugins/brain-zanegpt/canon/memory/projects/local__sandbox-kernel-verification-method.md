# local/sandbox-kernel-verification-method — lessons

Project: local/sandbox-kernel-verification-method. Newest first.

---

## E1 — a python model of js integer hashing passes checks real node fails
- Date: 2026-09-28
- Project: local/sandbox-kernel-verification-method
- Tags: [verification][testing][javascript][measurement]
- What: Applied the ideas kernel that verifications sharing one modelling substrate are one experiment, citing a `|0` versus `>>>0` defect that a Python model cannot represent. It reproduced exactly: ten Python checks agreed and ten real Node runs disagreed with all of them.
- Why built: brain train gap listed the kernel as unapplied. Every sandbox in this training run so far is a Python model, which is the kernel's own warning case.
- Design: A 32-bit integer hash written in JavaScript with Math.imul and `>>>` shifts and returning `x | 0`, used as `h(k) % 64` to pick a bucket. A Python transcription with 32-bit masking. Both hash 5000 keys from each of 10 key sets and check that every bucket index is in range. The JS ran in real Node v22.22.2, then again with `x >>> 0`.
- Got right: Running the same ten checks on the real runtime instead of adding more Python key sets. More key sets would only have added more agreeing Python results.
- Where/why it failed: The Python model passed 10 of 10 checks with 0 out-of-range indexes. Real Node failed 10 of 10, with 2384 to 2502 of 5000 indexes out of range per set, because `x | 0` is signed and JavaScript's `%` keeps the sign, so about half the buckets are negative. With `>>> 0` Node had 0 out of range and matched Python's maximum bucket load in 10 of 10 sets.
- Fix: When the claim depends on a language's numeric semantics, run at least one check on that real runtime. Count a batch of checks on one substrate as one piece of evidence, however many scenarios it covers.
- Why this fix: The Python model got 32-bit multiplication right but used Python's always-non-negative modulo; the error is in the shared substrate, so every scenario inherits it and no number of scenarios can expose it.
- Rule of thumb: Ten checks on one substrate are one experiment: a Python transcription of a JS bucket hash passed 10 of 10 range checks while real Node failed 10 of 10 (about 49% of indexes negative, from `x | 0` plus JS's sign-keeping `%`), and `>>> 0` fixed it, so run a claim that depends on numeric semantics on the real runtime at least once.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b05.py loop 23 in Pappydapimp69/Brain, running real Node v22.22.2, deterministic. Observed: Python 0 out of range in 10 sets; Node 2384 to 2502 of 5000 per set; Node with `>>> 0` 0 and the same max bucket load as Python in 10 of 10.
- Composed: ideas:VERIFICATION/method/vary-the-substrate-not-just-the-scenario/independence-is-about-shared-assumptions
- Link: session 2026-09-28, brain train gap batch 5 loop 23
- Sandbox: sandboxes/2026-09-28__train-gap-b05.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)
- Cited-by: 2026-10-10 · projects/local__sandbox-kernel-serialization.md#E1 · compatible · sandboxes/2026-10-10__json-big-id-rounding-is-runtime-specific-and-needs-an-exact-bigint-guard.py · observed RESULT: PASS 14/14 checks. Observed 500/1000 corrupted at 2^53 but 501 distinct (prediction miss, edge tie-to-even), 750/1000 and 251 distinct at 2^54, round trip 1000/1000 idempotent vs 500 wrong, string transport 0 and Number(str) 500, r… · session_01YFLLRpDsfZpRstb2KT2MQy
