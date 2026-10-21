# local/receiver-manipulation-needs-truncation — lessons

Project: local/receiver-manipulation-needs-truncation. Newest first.

---

## E1 — receiver manipulation needs truncation
- Date: 2026-10-15
- Project: local/receiver-manipulation-needs-truncation
- Tags: [stable-matching][game-theory][sandbox][testing]
- What: In 3,000 random 4x4 deferred-acceptance instances no proposer could ever gain by lying, and
  receivers could gain exactly when the instance had more than one stable matching (1,220
  instances, 40.7%), but only by truncating their list; reordering a complete list worked in
  just 141 instances (4.7%).
- Why built: Weakest-link train pick: the newly promoted stable-matching kernel states that only the
  receiving side can gain by misreporting, without saying how often or with what kind of lie,
  which decides whether the risk matters in a real matching market.
- Design: Deterministic LCG instances, n = 4. Proposer-optimal deferred acceptance. For every agent,
  every reordering of the full list as a lie (24 each); then truncation lies for receivers
  (true order, only the first k acceptable). Stable matchings counted by brute force over all
  24 matchings.
- Got right: Proposers never gained in any instance (strategy-proofness for the proposing side), and
  receivers never gained when the stable matching was unique (0 of 1,780), matching the kernel
  and the theory behind it.
- Where/why it failed: My first prediction (20-50% of instances manipulable) failed under reordering-only lies:
  4.7%. The manipulation that works is declaring partners unacceptable: truncation let a
  receiver gain in every one of the 1,220 multi-stable instances and in no others.
- Fix: When assessing manipulation risk in a deferred-acceptance market, ask whether participants
  can mark options unacceptable: if lists must be complete, receiver manipulation is rare; if
  truncation is allowed, it is possible whenever several stable matchings exist; let the more
  vulnerable side propose.
- Why this fix: Truncation lets a receiver reject the proposer-optimal partner and push the algorithm toward
  a better stable matching for her; a complete list keeps accepting that partner as a
  fallback, so most such moves are unavailable.
- Rule of thumb: Under deferred acceptance a receiver can gain exactly when several stable matchings exist
  (40.7% of 4x4 instances), but mainly by truncating her list (reordering alone: 4.7%);
  proposers never gain.
- Provenance (verified/assumed): Verified first-hand by the sandbox below; 4x4 uniform random preferences only; whether real
  markets allow truncation is market-specific.
- Composed: ideas:STABLE-MATCHING/deferred-acceptance
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__receiver-manipulation-needs-truncation.py
- Prediction: Iteration 1, written before running: no proposer gains; a receiver can gain in 20-50%; no
  gains when the stable matching is unique. Iteration 2, written before its run: with
  truncation a receiver can gain in exactly the multi-stable instances.
- Observed: RESULT: PASS proposers never gain (0); reordering lies: receivers gain in 4.7%; never when
  unique (0/1780); truncation: a receiver gains in 1220 = every multi-stable instance (1220).
- Scenarios: 1) reordering lies for all agents; 2) proposers' lies, built to break strategy-proofness; 3)
  truncation lies for receivers; 4) unique vs multiple stable matchings.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

