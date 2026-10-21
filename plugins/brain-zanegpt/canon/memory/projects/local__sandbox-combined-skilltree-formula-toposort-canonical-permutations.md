# local/sandbox-combined-skilltree-formula-toposort-canonical-permutations — lessons

Project: local/sandbox-combined-skilltree-formula-toposort-canonical-permutations. Newest first.

---

## E1 — sandbox combined skilltree formula toposort canonical permutations
- Date: 2026-09-29
- Project: local/sandbox-combined-skilltree-formula-toposort-canonical-permutations
- Tags: [algorithm][process][harness][determinism]
- What: Exhaustive re-check of skilltree-formula#E2 (diffing toposort orders of one graph shows spurious changes) over every declaration order of a 6-node dependency graph.
- Why built: The lesson was recorded from a single graph and one pair of orderings; an exhaustive permutation sweep shows how widespread the spurious diffs are and whether a canonical tie-break removes them completely.
- Design: Deterministic, no RNG: graph a,b roots; c<-a; d<-a,b; e<-c,d; f<-b; all 720 declaration permutations; Kahn toposort with a declared-order tie-break versus a lexicographic tie-break; positional diff against a reference order; an edge-set diff as a control.
- Got right: Every order produced by either tie-break is a valid toposort (720/720 valid), so neither system is buggy, matching the recorded lesson; the edge-set diff shows 1 distinct graph across all 720 permutations.
- Where/why it failed: With the declared-order tie-break there are 4 distinct valid outputs and 540 of 720 permutations (75%) show a positional diff against the reference, flagging up to 5 of 6 nodes as changed although nothing changed.
- Fix: Canonicalize with a deterministic tie-break (lexicographic among ready nodes) before diffing, or diff the edge set instead of the ordered list; with the lexicographic tie-break the sweep gives 1 distinct output and 0/720 spurious diffs.
- Why this fix: The dependency constraint only fixes a partial order, so any tie-break tied to input order leaks input order into the output; a tie-break that depends only on node identity removes the leak.
- Rule of thumb: Any output derived from a partial order is not canonical until ties are broken by identity; sweep all input permutations of a small graph and assert one distinct output before diffing or snapshot-testing it.
- Provenance (verified/assumed): Verified first-hand by running the sandbox at ~/brainwork/sb/s5.py; figures are its observed output. Only a 6-node graph was swept, larger graphs were not.
- Composed: sandbox-combined-skilltree-formula/E2
- Link: scheduled training pass 4, session_01NomGdXQGCMAr6o2dzv6Tp2
- Cited-by: 2026-10-13 · projects/pappydapimp69__brainwork.md#E193 · compatible · sandboxes/2026-10-13__canonical-toposort-tiebreak-is-a-choice-and-chained-sort-order-breaks-validity.py · observed RESULT: PASS kahn-lex 1 distinct, composite 1 distinct but abcdef vs abcdfe; reading-order chain invalid 0 of 720 on alphabetical labels and 720 of 720 on reversed labels. · scheduled brain train session, loop 2 pass 2; session_01DiPNzPzfsHcE8oDezvZY3n
