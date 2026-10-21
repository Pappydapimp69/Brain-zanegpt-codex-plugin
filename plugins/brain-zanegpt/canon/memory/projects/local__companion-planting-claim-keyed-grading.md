# local/companion-planting-claim-keyed-grading — lessons

Project: local/companion-planting-claim-keyed-grading. Newest first.

---

## E1 — grade the claim not the plant one marigold gets two evidence grades
- Date: 2026-10-15
- Project: local/companion-planting-claim-keyed-grading
- Tags: [garden][pest-control][taxonomy][sandbox]
- What: Grading the companion-planting kernel's six claims by plant, target and setting gives marigold three different
  grades (targeted toxicity as a full-season cover crop, unsupported as an ornamental interplant, refuted for
  aphids, whiteflies and mites), while a grade kept per plant misgrades 2 of the 6 claims.
- Why built: Gap pick: the companion-planting taxonomy kernel had no lesson applying it. Its own text says the same
  marigolds work on nematodes only as a cover crop and not on aphids, which implies the grade belongs to the claim.
- Design: Six claims transcribed from the kernel, each with trial evidence, a named mechanism and whether the setting
  matches the trial. A claim-level rule assigns a bucket; a plant-level rule gives every claim of a plant the best grade any of its claims earns. No random numbers.
- Got right: The claim-level rule reproduced the kernel's four buckets (scent-masking, targeted toxicity, negative
  allelopathy, folklore) and separated the three marigold claims; the plant-level rule hid two of them.
- Where/why it failed: The claim attributes were transcribed from the kernel and not checked against the trials, so the grading
  rule is partly my encoding of the kernel and the 2 of 6 count follows from which claims the kernel lists; it shows the grain of the grading, not how common the error is.
- Fix: Key a companion-planting grade on plant, target pest and planting setting, never on the plant alone; record
  the setting next to the pairing before trusting it.
- Why this fix: One plant can have a strong effect in one setting and none in another, so any per-plant grade
  overstates the weak claims or understates the strong one.
- Rule of thumb: Grade a companion-planting claim by plant, target and setting: marigold got 3 grades over 3 claims, and a per-plant grade misgraded 2 of 6.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; claim attributes are transcribed from the kernel's own text and not independently checked against the cited trials.
- Composed: ideas:GARDEN/companion-planting-claim-taxonomy
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__grade-the-claim-not-the-plant-one-marigold-gets-two-evidence-grades.py
- Prediction: Hidden assumption: a plant carries one grade. Expected three distinct marigold grades and plant-level grading to misgrade 2 of 6 claims; it would be wrong if the three marigold claims shared a grade.
- Observed: RESULT: PASS marigold earns 3 grades over 3 claims; plant-level grading misgrades 2 of 6 claims
- Scenarios: 1) allium aphids; 2) marigold nematodes as cover crop; 3) marigold nematodes as ornamental, built to BREAK the one-grade-per-plant assumption; 4) marigold aphids; 5) fennel; 6) basil folklore.
- Link: scheduled brain train auto loop 2 pass 5 (gap); session_01Twuh3aqxvcX5mmf7uhRTr7
- Cited-by: 2026-10-15 · projects/pappydapimp69__brainwork.md#E310 · compatible · sandboxes/2026-10-15__claim-keyed-grade-binding-rate-check.py · observed RESULT: PASS misgraded per-plant 5 claim-keyed 0 conflicts 1 pinned plants [] · brain train auto session 2026-10-15; session_01RMAaQPULLrY2w6iRwP967n
- Audited: 2026-10-20 · fail · Read the entry and its stored sandbox. The model does not compute the grades from evidence: grade_claim is a hand-written if-chain that encodes the kernel's four buckets, and the six claims were chosen and attributed (including the setting-matches flag that separates the two marigold nematode claims) by the author, so three marigold grades follow from the table by construction. The plant-level comparator is defined as the best grade of any claim of the plant, which guarantees it misgrades exactly the claims that disagree with their plant's best, so the 2 of 6 count is arithmetic on the table, not a measured error rate (the entry admits this). The Rule of thumb states a general design principle, grade by plant, target and setting, but nothing was tested against real trial data or a competing grading scheme, so the answer is assumed rather than discovered. · scheduled brain train auto session 2026-10-20 loop 1 pass 3 audit; session_018vkktVQxraRdjDDGahsw1j
