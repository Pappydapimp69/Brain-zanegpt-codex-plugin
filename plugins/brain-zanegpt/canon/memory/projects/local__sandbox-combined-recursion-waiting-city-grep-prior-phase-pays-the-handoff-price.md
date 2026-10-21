# local/sandbox-combined-recursion-waiting-city-grep-prior-phase-pays-the-handoff-price — lessons

Project: local/sandbox-combined-recursion-waiting-city-grep-prior-phase-pays-the-handoff-price. Newest first.

---

## E1 — sandbox combined recursion waiting city grep prior phase pays the handoff price
- Date: 2026-08-29
- Project: local/sandbox-combined-recursion-waiting-city-grep-prior-phase-pays-the-handoff-price
- Tags: [process][saga][architecture][method]
- What: A deterministic sandbox (four sequential games, fixed fix list, no RNG) tracking how a bug fix discovered in the first game propagates across a saga under four build strategies — a shared runtime, rebuilding fresh, rebuilding while grepping the prior phase, and a versioned handoff code with no shared runtime.
- Why built: recursion#E10 records that a "rebuild it fresh" phase task can silently drop an already-solved sibling-phase pattern, and prescribes grepping the prior phase before scaffolding a subsystem from zero. waiting-city#E12 prescribes carrying saga state via a versioned, checksummed handoff code with no shared runtime, explicitly accepting hand-propagation of every fix as the price of backward compatibility and blast-radius isolation. This tests the relationship between the stated price and the discipline that pays it.
- Design: A fix discovered and applied in game 0 only, then tracked across three subsequent games under each strategy, counting how many games end up carrying it.
- Got right: Modelling the handoff-code strategy as carrying state but not code — which is exactly what waiting-city#E12 specifies — rather than as a weaker version of a shared runtime, so its result reflects the architecture's actual semantics.
- Where/why it failed: The handoff-code architecture propagates the fix to 1 of 4 games, since it deliberately carries no code. Rebuilding fresh also reaches 1 of 4. Rebuilding while grepping the prior phase reaches 4 of 4 — matching a shared runtime's coverage without adopting one.
- Fix: Treat recursion#E10's grep-the-prior-phase step as a mandatory part of adopting waiting-city#E12's architecture rather than as an unrelated scaffolding tip, since it is the mechanism that actually pays E12's acknowledged hand-propagation cost.
- Why this fix: waiting-city#E12 names hand-propagating every fix as an accepted price but does not specify how it gets paid, and the price is invisible at adoption time — the architecture's isolation benefits are immediate while its propagation cost only materialises when a fix from an earlier game fails to appear in a later one. recursion#E10 supplies the concrete step, and without it a team gets E12's isolation while silently defaulting on its cost.
- Rule of thumb: recursion#E10's grep-the-prior-phase step is the mechanism that pays waiting-city#E12's explicitly-accepted hand-propagation price — sandbox-confirmed a game-0 fix reaches 1 of 4 saga games under handoff-code-only and 4 of 4 once the prior phase is grepped, matching a shared runtime without adopting one; adopt E12 and E10 together or the cost silently goes unpaid.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b10/l27.py) and confirmed a game-0 discovery reaches 4/4 games under a shared runtime, 4/4 under rebuild-plus-grep-prior, and 1/4 under both rebuild-fresh and handoff-code-only. the-game-the-recursion#E10 and the-game-the-waiting-city#E12 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__the-game-the-recursion/E10, pappydapimp69__the-game-the-waiting-city/E12
- Link: session_014mRpopK9xnhvk35tT8ozkX

