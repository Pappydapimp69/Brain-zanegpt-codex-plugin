# local/sandbox-combined-dog-e45-e19-radius-term-on-a-squared-distance — lessons

Project: local/sandbox-combined-dog-e45-e19-radius-term-on-a-squared-distance. Newest first.

---

## E1 — sandbox combined dog e45 e19 radius term on a squared distance
- Date: 2026-08-29
- Project: local/sandbox-combined-dog-e45-e19-radius-term-on-a-squared-distance
- Tags: [algorithm][gamedev][correctness][testing]
- What: A deterministic sandbox (three fixed points with differing radii, no RNG) applying dog#E19's radius-aware rejection threshold through a squared-distance helper of the kind dog#E45 warns about, compared against a correctly-rooted implementation and against the pre-E19 flat threshold.
- Why built: dog#E19 prescribes rejecting on `minDist + otherPoint.radius` once scattered points carry differing collision radii. dog#E45 warns that a "distance-like" helper whose name could mean real or squared distance must have its call sites grepped and their comparison shape copied. This tests what happens when E19's fix is applied on top of E45's unresolved ambiguity.
- Design: Three collinear points at real separations of 2.4, 2.6 and 5.0 with radii 0.5, 1.5 and 0.5, and a `dist2` helper returning squared distance. Three rejection predicates run over the same placement order: correct (square-rooted, radius-aware), the dog#E45 slip (squared distance compared against the linear `MIN + radius` threshold), and the pre-E19 form (squared distance against a correctly squared flat threshold).
- Got right: Including the pre-E19 form as a control, which is what shows the slip is not simply "worse than the fix" but worse than the code the fix replaced.
- Where/why it failed: One intended rule produces three different placements — 2 points placed under the correct predicate, 3 under the dog#E45 slip, 3 under the pre-E19 flat threshold. Adding a linear radius term to a squared comparison is dimensionally incoherent: it does not widen the rejection radius as E19 intends, it silently redefines it, and here it disables rejection entirely for the overlapping pair at separation 2.4.
- Fix: Resolve the distance helper's units before applying dog#E19's threshold change — either root the helper at the call site or square the whole threshold (`(minDist + radius)**2`) — and add an assertion that the rejection predicate actually rejects a known-overlapping fixture pair, since a dimensionally wrong threshold fails open rather than throwing.
- Why this fix: dog#E19's fix is stated as adding a term to a threshold, which reads as a purely local edit and invites applying it without inspecting the comparison's units. Because the pre-E19 code was at least dimensionally consistent, applying E19 on an unresolved E45 helper is a net regression, which is the opposite of what adopting a recorded fix is supposed to produce.
- Rule of thumb: dog#E19's `+ otherPoint.radius` threshold term is only valid once dog#E45's squared-versus-real distance ambiguity is resolved — sandbox-confirmed adding a linear radius term to a squared comparison places 3 points where the correct predicate places 2, failing open on a genuinely overlapping pair and making the fix a regression against the pre-E19 code.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b3/l10.py) and confirmed placements of 2 (correct, sqrt + radius), 3 (squared distance vs linear threshold) and 3 (squared distance vs squared flat threshold) over identical input at real separations 2.4/2.6/5.0. dog#E45 and dog#E19 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__dog/E45, pappydapimp69__dog/E19
- Link: session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-10-13 · projects/pappydapimp69__brainwork.md#E192 · compatible · sandboxes/2026-10-13__squared-distance-radius-slip-seen-across-all-placement-orders-not-one.py · observed RESULT: PASS slip invalid 120/120, correct counts [2, 3], slip more in 120, MIN=1 invalid 90. · scheduled brain train session, loop 2 pass 2; session_01UeKMwUeVxtmySB3P82SSXJ
