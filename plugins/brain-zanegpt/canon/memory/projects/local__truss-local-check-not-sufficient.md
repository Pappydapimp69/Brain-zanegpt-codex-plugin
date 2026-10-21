# local/truss-local-check-not-sufficient — lessons

Project: local/truss-local-check-not-sufficient. Newest first.

---

## E1 — truss local check not sufficient
- Date: 2026-10-15
- Project: local/truss-local-check-not-sufficient
- Tags: [structures][physics][sandbox][testing]
- What: The truss kernel offers 'every joint held by at least two non-parallel members' as an
  alternative to the rank test; two counterexamples pass both Maxwell's count and that local
  check yet are mechanisms (rank 15 of 16): two braced squares joined by two parallel links,
  and the same squares joined at a single joint.
- Why built: Weakest-link train pick: the newly promoted truss kernel shows Maxwell's count is not
  sufficient, then names a local joint check as an equivalent confirmation; a local check
  cannot see motion between two rigid sub-bodies, so it needed a test.
- Design: Exact joint-equilibrium matrix with Fractions and Gaussian-elimination rank; pin plus roller
  supports. Trusses: triangle (control); doubly braced square joined to a singly braced square
  by two parallel horizontal links; same joined by two links meeting at one joint; singly
  braced squares joined by three non-concurrent links (count 0).
- Got right: The rank test separates them all: the triangle and the three-link truss are rigid (rank 6/6
  and 16/16), and Maxwell's count is 0 for every case, confirming the kernel's point that
  totals alone decide nothing.
- Where/why it failed: The kernel's local check passed for both mechanisms: every joint had two non-parallel
  members, but the right square can sway on the parallel links or pivot about the shared
  joint, because the local check never asks whether two rigid groups are joined by three
  independent constraints. My first rigid control (links meeting at one joint) was itself a
  mechanism.
- Fix: Use only the equilibrium-matrix rank (or a pebble-game rigidity check) to confirm
  determinacy; if a hand check is needed, check sub-bodies too: two rigid groups need three
  links that are neither all parallel nor all through one point.
- Why this fix: Rigidity is global: a mechanism can live entirely in the relative motion of two well-braced
  groups, which is invisible joint by joint; the rank of the full matrix counts every
  independent motion including those.
- Rule of thumb: 'Every joint has two non-parallel members' does not confirm a truss: two braced squares on
  parallel links pass it and Maxwell's count yet sway (rank 15/16); use matrix rank, or three
  non-concurrent links between rigid groups.
- Provenance (verified/assumed): Verified first-hand by the exact-rank sandbox below; planar pin-jointed model only.
- Composed: ideas:STRUCTURES/trusses
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__truss-local-check-not-sufficient.py
- Prediction: Written before running: the parallel-link truss has count 0 and passes the local check but
  rank 2j - 1; a diagonal link instead makes it rigid. Iteration 2 (after that control
  failed): three non-concurrent links with count 0 are rigid.
- Observed: RESULT: PASS parallel-link truss: count +0, local check True, rank 15/16 (mechanism); one-
  joint link also a mechanism, rank 15/16; three non-concurrent links count +0, rank 16/16.
- Scenarios: 1) triangle control; 2) parallel links, built to break the local check; 3) links meeting at
  one joint (my failed control, also breaks the local check); 4) three non-concurrent links.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

