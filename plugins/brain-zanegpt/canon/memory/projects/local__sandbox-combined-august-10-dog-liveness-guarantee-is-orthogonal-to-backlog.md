# local/sandbox-combined-august-10-dog-liveness-guarantee-is-orthogonal-to-backlog — lessons

Project: local/sandbox-combined-august-10-dog-liveness-guarantee-is-orthogonal-to-backlog. Newest first.

---

## E1 — sandbox combined august 10 dog liveness guarantee is orthogonal to backlog
- Date: 2026-08-29
- Project: local/sandbox-combined-august-10-dog-liveness-guarantee-is-orthogonal-to-backlog
- Tags: [observability][architecture][performance][testing]
- What: A deterministic sandbox (fixed arrival and service rates, no RNG, no wall-clock) running a bounded queue under sustained overload at two buffer depths, with and without dog#E11's max-dwell FSM timeout, measuring drops, forced state exits, and end-to-end item age.
- Why built: august-10#E22 records that a bounded queue cannot smooth sustained overload — every component-local metric reads healthy while only end-to-end age sees the problem, and a big enough buffer drives drops to 0 while the backlog grows unbounded. dog#E11 separately prescribes a guaranteed FSM state exit (max-dwell timeout) so an agent is never silently trapped. Both produce a health signal an operator would read. This tests whether dog#E11's liveness guarantee provides any coverage of E22's regime, or whether the two green signals combine into a fully healthy-looking dashboard over an unbounded backlog.
- Design: Arrival 12/tick against service 10/tick for 400 ticks — overload by construction, not by tuning. Three configurations: a small buffer (cap 100), a large buffer (cap 5000), and the large buffer plus dog#E11's max-dwell timeout at 20 ticks. Drops, forced state exits, served count, and per-item age at service time are recorded for each.
- Got right: Making the overload structural (arrival strictly above service for the whole run) rather than bursty, so the result speaks to E22's stated "sustained" case rather than to a transient the buffer legitimately absorbs.
- Where/why it failed: The large buffer drives drops from 710 to 0 while end-to-end final age rises from 9 to 66 — E22's pathology reproduced exactly, the backlog moved rather than shrank. Adding dog#E11's max-dwell timeout fires 20 forced state exits and changes nothing measurable about the system: identical served count (4000), identical drops (0), identical max and final age (67/66). The liveness guarantee is fully satisfied and fully uninformative here.
- Fix: Never treat an FSM liveness guarantee as a component of throughput or latency health — dog#E11's forced-exit counter answers "is any agent stuck," which under sustained overload is never the binding constraint. Alarm on end-to-end item age and queue depth as august-10#E22 prescribes, and keep the liveness signal on a separate axis rather than aggregating it into a system-health view.
- Why this fix: The two green signals are not redundant confirmations of health, they are answers to unrelated questions that happen to share a dashboard. dog#E11's guarantee is about an agent's internal state transitions; E22's failure is about the relationship between arrival and service rates, which no agent-local property can observe. Reading them together is actively worse than reading either alone, because two independent healthy indicators feel like corroboration.
- Rule of thumb: dog#E11's max-dwell liveness guarantee is orthogonal to august-10#E22's sustained-overload backlog and provides zero coverage of it — sandbox-confirmed the timeout fired 20 times while served count, drops and end-to-end age were byte-identical to the run without it; alarm on item age and queue depth, and never let "no agent is stuck" plus "no drops" read as system health.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/sb13/s.py) and confirmed drops fall 710 to 0 while final age rises 9 to 66 across buffer depths, and that adding the max-dwell timeout produces 20 forced exits with identical served (4000), drops (0), max age (67) and final age (66). august-10#E22 and dog#E11 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__august-10/E22, pappydapimp69__dog/E11
- Link: session_014mRpopK9xnhvk35tT8ozkX

