# local/sandbox-combined-august-10-dog-dwell-is-a-noop-when-phase-exceeds-travel — lessons

Project: local/sandbox-combined-august-10-dog-dwell-is-a-noop-when-phase-exceeds-travel. Newest first.

---

## E1 — sandbox combined august 10 dog dwell is a noop when phase exceeds travel
- Date: 2026-09-29
- Project: local/sandbox-combined-august-10-dog-dwell-is-a-noop-when-phase-exceeds-travel
- Tags: [gamedesign][simulation][state][testing]
- What: Second re-verification of the august-10#E9 level-keyed degeneracy and dog#E40 dwell repair, this time varying the economy's own oscillation rather than the dwell. A dwell equal to travel time is a safe default: it repairs short-phase economies and changes nothing in long-phase ones.
- Why built: The recorded fix and my earlier dwell sweep used one collapsed-economy trace, so it was unknown whether the dwell can harm economies that were already healthy.
- Design: Deterministic 240-tick model, level alternates low and high phases of equal length 1, 2, 3 and 5 ticks against a threshold; event open while low, closing after the level recovers and dwell has elapsed; interior reachable if open at least travel time 3. Compare dwell 0 with dwell 3 for each phase length.
- Got right: Phase lengths 1 and 2 reproduce the degeneracy at dwell 0: 120 and 60 events opened with 0 reachable interiors.
- Where/why it failed: At dwell 3 those become 60 opened and 60 reachable interiors. Phases of 3 and 5 are already healthy, and the dwell leaves them byte-identical (40/40 and 24/24 opened/reachable both with and without the dwell), so the repair carries no cost where the predicate is not degenerate.
- Fix: Apply a minimum event lifetime equal to travel time unconditionally as a guard, not as a tuned patch for a known-bad economy.
- Why this fix: The guard only binds when the low phase is shorter than travel time, exactly the degenerate case, and is inert otherwise, so it needs no knowledge of the economy period.
- Rule of thumb: A repair that is a no-op on the healthy configurations and a full fix on the degenerate ones can be shipped as an invariant; verify that by running it on both sides of the threshold, not only on the failing trace.
- Provenance (verified/assumed): Verified first-hand by running the sandbox in this session; all counts above are observed output from the run.
- Composed: sandbox-combined-august-10-dog-dwell-repairs-a-degenerate-level-keyed-predicate/E1, august-10/E9, dog/E40
- Link: session https://claude.ai/code/session_01VDpEDT2ry2U1WXLUnGqdYD

