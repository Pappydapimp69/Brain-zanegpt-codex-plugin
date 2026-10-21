# local/sandbox-combined-august-10-dog-dwell-repairs-a-degenerate-level-keyed-predicate — lessons

Project: local/sandbox-combined-august-10-dog-dwell-repairs-a-degenerate-level-keyed-predicate. Newest first.

---

## E1 — sandbox combined august 10 dog dwell repairs a degenerate level keyed predicate
- Date: 2026-08-29
- Project: local/sandbox-combined-august-10-dog-dwell-repairs-a-degenerate-level-keyed-predicate
- Tags: [gamedesign][simulation][state][testing]
- What: A deterministic sandbox (fixed resource trajectories, no RNG) running an event whose open and close conditions are both keyed on a resource level, under a healthy oscillating economy and a collapsed one, then re-running the collapsed case with dog#E40's explicit dwell requirement added.
- Why built: august-10#E9 records that a termination predicate keyed on a resource level goes degenerate once that level becomes the steady state — wars ended on the tick they were declared for 90 of 100 days once forests went extinct, starving every behaviour that needed time inside the event. dog#E40 records that an agent meant to congregate must dwell on arrival rather than treating arrival as task-complete. This tests whether dog#E40's dwell idiom is the general repair for E9's degeneracy or merely a neighbouring NPC-behaviour nicety.
- Design: An event opens when the resource falls below 20 and closes when it recovers above 20. Two economies: one oscillating around a healthy level, one where drain exceeds regen so the resource pins at 0. The collapsed case is then re-run with a minimum dwell of 3 and 10 ticks before the event may close.
- Got right: Holding the resource trace completely identical between the dwell and no-dwell runs, so the change in event interiors is attributable to the termination rule alone rather than to any change in the simulated economy.
- Where/why it failed: Under the collapsed economy the level-keyed predicate opens 1 event whose interior is never reached — the resource never recovers, so the event never closes, and no behaviour inside it ever completes, exactly august-10#E9's degeneracy with nothing raising an error. Adding a 3-tick dwell requirement to the same trace yields 34 events opened with 33 interiors actually reached; a 10-tick dwell yields 10 and 10.
- Fix: Give any event or state whose lifetime is currently a function of a world variable an explicit minimum dwell measured in its own units, so its interior is reachable regardless of whether that variable still moves — dog#E40's arrival-versus-dwell distinction applied to event lifetimes rather than to agent positions.
- Why this fix: august-10#E9 identifies the failure and prescribes re-auditing threshold predicates when an equilibrium shifts, which is detection rather than repair and requires noticing the shift. dog#E40's dwell requirement removes the dependency instead: the event's interior no longer needs the world variable to move, so the degeneracy cannot recur when a future equilibrium change goes unnoticed.
- Rule of thumb: dog#E40's dwell-on-arrival requirement is the general repair for august-10#E9's level-keyed termination degeneracy, not just an NPC nicety — sandbox-confirmed a collapsed economy yields 1 event with 0 reachable interiors under a pure level predicate and 34 events with 33 interiors on the identical trace once a 3-tick minimum dwell is added.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b2/l7.py) and confirmed the collapsed economy produces 1 opened event with 0 interiors reached under the level-keyed predicate, versus 34 opened / 33 interiors at dwell 3 and 10 / 10 at dwell 10 on the same resource trace. august-10#E9 and dog#E40 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__august-10/E9, pappydapimp69__dog/E40
- Link: session_014mRpopK9xnhvk35tT8ozkX
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-august-10-dog-dwell-is-a-noop-when-phase-exceeds-travel.md#E1 · compatible · no sandbox · session https://claude.ai/code/session_01VDpEDT2ry2U1WXLUnGqdYD
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-august-10-dog-dwell-sized-by-travel-time.md#E1 · compatible · no sandbox · session https://claude.ai/code/session_01VDpEDT2ry2U1WXLUnGqdYD
