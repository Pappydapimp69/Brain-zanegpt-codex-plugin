# local/sandbox-combined-august-10-dog-dwell-sized-by-travel-time — lessons

Project: local/sandbox-combined-august-10-dog-dwell-sized-by-travel-time. Newest first.

---

## E1 — sandbox combined august 10 dog dwell sized by travel time
- Date: 2026-09-29
- Project: local/sandbox-combined-august-10-dog-dwell-sized-by-travel-time
- Tags: [gamedesign][simulation][state][testing]
- What: Re-verification of sandbox-combined-august-10-dog-dwell-repairs-a-degenerate-level-keyed-predicate/E1 from a dwell sweep angle. The dwell repair has a sharp threshold set by travel time and a cost above it.
- Why built: The recorded lesson showed one dwell value (3 ticks) working but never swept the value, so it is unknown how the minimum should be chosen.
- Design: Deterministic 100-tick model, resource level alternating 0 and 9 each tick against threshold 5 (a collapsed economy), event opens while level is below threshold, closes only when level is back at or above threshold AND the minimum dwell has elapsed; an interior counts as reachable if the event stayed open at least travel time (3 ticks). Dwell swept 0,1,2,3,4,6,10,20.
- Got right: The pure predicate (dwell 0) reproduces the degeneracy: 50 events opened, 0 interiors reachable. Dwell 1 is identical, so a token dwell does nothing.
- Where/why it failed: Reachable interiors flip from 0 to 25 at dwell 2 (open-to-close spans 3 ticks because of level parity), then only decline as dwell grows: events opened 25, 17, 13, 9, 5 and interiors 25, 16, 12, 8, 4 at dwell 3, 4, 6, 10, 20. Over-long dwell starves the event stream without gaining reachability.
- Fix: Size the minimum dwell to the agent travel time to the interior (the smallest value that makes interiors reachable), not to a round or generous number.
- Why this fix: Reachability is a step function of dwell at travel time, while event count falls roughly as horizon divided by dwell plus one, so any dwell above the step is pure cost.
- Rule of thumb: Derive event minimum lifetime from the cost of reaching its interior and test with a dwell sweep; a value below that cost changes nothing (0 interiors) and a value above it only removes events.
- Provenance (verified/assumed): Verified first-hand by running the sandbox in this session; all counts above are observed output from the run.
- Composed: sandbox-combined-august-10-dog-dwell-repairs-a-degenerate-level-keyed-predicate/E1, august-10/E9, dog/E40
- Link: session https://claude.ai/code/session_01VDpEDT2ry2U1WXLUnGqdYD

