# local/sudoku4-uniqueness-depends-on-grid-class — lessons

Project: local/sudoku4-uniqueness-depends-on-grid-class. Newest first.

---

## E1 — sudoku4 uniqueness depends on grid class
- Date: 2026-10-15
- Project: local/sudoku4-uniqueness-depends-on-grid-class
- Tags: [latin-squares][puzzles][sandbox][exhaustive]
- What: The Sudoku clue-placement kernel's 4-clue uniqueness rate (12 of 1820, 0.7%) belongs to one
  of two classes of 4x4 grids: across all 288 grids, 96 have exactly 12 unique 4-clue sets and
  the other 192 have 128 (7.0%), more than ten times as many; the two-distinct-digit rule
  (never unique) held on every grid.
- Why built: Weakest-link train pick: the kernel measured uniqueness on one fixed solution grid; 4x4
  Sudoku grids fall into two essentially different classes, so a single-grid rate may not
  generalise to puzzles built on other grids.
- Design: Enumerated all 288 4x4 Sudoku grids; for every grid and every 4-clue subset (1820 per grid)
  a clue set is unique iff exactly one of the 288 grids agrees with it (set intersection over
  a cell-value index), which equals a solver's count. Also counted unique sets using at most
  two distinct digits.
- Got right: The kernel's structural rule is universal: no unique clue set with two or fewer distinct
  digits on any grid (relabelling the missing digits always gives a second solution), and its
  12 of 1820 figure is exact for its grid's class.
- Where/why it failed: The rate is not a property of 4x4 Sudoku: 192 of 288 grids give 128 unique 4-clue sets, so a
  puzzle designer starting from one of those grids has ten times the choice of minimal puzzles
  the kernel suggests. I had predicted two classes but not the size of the gap.
- Fix: Quote puzzle-uniqueness rates per grid class (or averaged over all grids), never from one
  solution; when generating minimal puzzles, pick base grids from the richer class.
- Why this fix: Uniqueness depends on how a clue set intersects the other solutions, and grids in different
  symmetry classes have different neighbours; one grid samples only one class.
- Rule of thumb: 4x4 Sudoku 4-clue uniqueness depends on the grid class: 96 grids have 12 unique sets, 192
  have 128 (0.7% vs 7.0%); the two-distinct-digit rule holds on all 288.
- Provenance (verified/assumed): Verified first-hand by the exhaustive sandbox below over all 288 grids; that the two counts
  correspond to the two known equivalence classes is my interpretation, not separately
  checked.
- Composed: ideas:LATIN-SQUARES/sudoku-puzzles/clue-placement
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__sudoku4-uniqueness-depends-on-grid-class.py
- Prediction: Written before running: the 288 grids split into two classes with different 4-clue
  uniqueness counts, so 12/1820 is true only for one class; the two-distinct-digit rule holds
  on every grid.
- Observed: RESULT: PASS 4-clue unique sets per grid take values 12 and 128 over 288 grids (96 and 192
  grids); unique sets with <=2 distinct digits: 0.
- Scenarios: 1) all 288 grids, all 1820 four-clue sets each; 2) two-distinct-digit sets on every grid,
  built to find an exception to the kernel's rule.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

