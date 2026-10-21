# local/sandbox-combined-dog-e16-e43-position-assertion-cannot-verify-its-own-fix — lessons

Project: local/sandbox-combined-dog-e16-e43-position-assertion-cannot-verify-its-own-fix. Newest first.

---

## E1 — sandbox combined dog e16 e43 position assertion cannot verify its own fix
- Date: 2026-08-29
- Project: local/sandbox-combined-dog-e16-e43-position-assertion-cannot-verify-its-own-fix
- Tags: [testing][state][gamedev][architecture]
- What: A deterministic sandbox (four agents, fixed claim order, no RNG) contending for one shared resource with and without dog#E16's per-action re-validation, scored by a position-only assertion and by an FSM-state assertion.
- Why built: dog#E16 records that independent agents can commit to the same shared resource without a lock, but only if every agent re-validates the resource is still available immediately before each dependent action rather than only at commit time. dog#E43 records that a shared-resource stress test asserting only on position is blind to an FSM-driven agent silently advancing its decision state before a commit-time veto confirms it won. This tests whether E16's fix can be verified by the test E16's own recipe implies.
- Design: Four agents claim the resource, all advancing their FSM to "approaching"; then each performs a dependent action, with re-validation either enabled or disabled. Both assertions run on the result — exactly one agent physically at the resource, and no non-owner having advanced to "using".
- Got right: Letting the FSM advance during the claim phase in both configurations, so the difference measured is solely whether the dependent action re-checks ownership, not whether the agents ever considered the resource.
- Where/why it failed: Without re-validation the position assertion still passes — exactly one agent occupies the resource — while three non-owners have silently advanced their FSM into "using". The stress test dog#E16's own recipe suggests ("exactly one succeeds, the rest revert cleanly") is satisfied identically whether E16's fix is present or absent, so it cannot verify the fix it accompanies.
- Fix: Pair every shared-resource stress test with dog#E43's FSM assertion — no non-owner may have advanced past the claim state — since that is the only assertion whose result differs between the fixed and unfixed implementations.
- Why this fix: dog#E16 and dog#E43 are one mechanism seen from opposite ends: E16 states the fix, E43 states that the natural test for it is blind. Adopting E16 alone therefore produces an unverifiable discipline — the code may be correct, but the suite would look identical if a later refactor removed the re-validation, which is precisely the condition under which such a fix silently regresses.
- Rule of thumb: dog#E16's per-action re-validation cannot be verified by a position-only stress test — sandbox-confirmed the "exactly one succeeds" assertion passes identically with and without the fix while three non-owners silently advance their FSM to "using"; add dog#E43's non-owner-FSM assertion, the only one whose result changes.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b10/l26.py) and confirmed the position assertion returns True in both configurations while the FSM assertion returns True with re-validation and False without, with non-owners [1, 2, 3] left in "using". dog#E16 and dog#E43 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__dog/E16, pappydapimp69__dog/E43
- Link: session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-10-13 · projects/pappydapimp69__brainwork.md#E177 · compatible · sandboxes/2026-10-13__assertion-discrimination-matrix-capture-layer-and-shared-resource-fsm.py · observed RESULT: PASS checks all true; generic 0.015, pinned 1.000, resolver 1.000, position 0.000, fsm 1.000, any-green 64/65 on buggy, all-pass 0/65, inverted-bug pinned green 1.000. · scheduled brain train session, loop 2 pass 2; session_01Vd1XXerYpxYYjyMDy9FPmH
