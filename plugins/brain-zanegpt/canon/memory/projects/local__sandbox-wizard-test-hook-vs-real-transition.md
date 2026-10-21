# local/sandbox-wizard-test-hook-vs-real-transition — lessons

Project: local/sandbox-wizard-test-hook-vs-real-transition. Newest first.

---

## E1 — wizard test hook vs real transition
- Date: 2026-10-08
- Project: local/sandbox-wizard-test-hook-vs-real-transition
- Tags: [testing][state][narrative][architecture]
- What: Composed couchbound-story-engine/E1 (route is a function of current answers; invalidate downstream on change) with dog/E24 (a test-only state-jump hook skips real transition side effects). In a sandbox, a hook that sets wizard answers directly passes route assertions while leaving derived labels empty, the overlay up, and stale downstream answers alive after a backtrack.
- Why built: Both systems share a hidden contract: one transition function owns invalidation plus derived state plus view. E1 states the contract for backtracking; E24 shows tests that bypass it are blind. Nobody had checked whether a fast-forward test hook on an adaptive wizard hits both failures at once.
- Design: Python stdlib, no RNG. Wizard with route(answers), derived labels, overlay flag. Real commit() invalidates downstream answers, recomputes derived, hides the overlay. force() only sets answers. Oracle = rebuild from final answers through commit() only. Compared six cases against it, including E2's authored-vs-autofilled distinctness at finalize.
- Got right: Real backtrack matched the fresh rebuild. A hook that delegates to the real transition also matched the oracle. Finalize kept deliberate agreement (run, run) and autofilled distinct values (run, hide).
- Where/why it failed: The force() hook passed the route assertion yet derived labels were empty and the overlay was still up. A hook-driven backtrack kept stale choice and ending answers. Even a real-path variant that cleared answers but not the derived cache left two orphan labels while the route check still passed.
- Fix: Make every test hook call the real transition (or a shared apply function) and assert against a from-scratch rebuild of the whole view, not only the route or stage.
- Why this fix: A rebuild oracle compares everything derived, so it catches whatever a shortcut forgot, including things no one thought to assert.
- Rule of thumb: In a wizard or FSM, a test hook that sets state without the real transition proves nothing about backtracking or the view; route hooks through the transition and compare the full view to a fresh rebuild.
- Provenance (verified/assumed): Verified first-hand with the sandbox in this session; the wizard is a reduced model, not the real couchbound or dog code.
- Composed: couchbound-story-engine/E1, dog/E24, couchbound-story-engine/E2
- Sandbox: sandboxes/2026-10-08__wizard-test-hook-vs-real-transition.py
- Prediction: Before running I expected the hook path to pass the route assertion yet diverge from the oracle in derived and overlay, and the delegating hook to match it.
- Observed: RESULT: PASS state-only assertions blind to hook skipping invalidation/derived/overlay; routing hook through real transition matches fresh rebuild
- Scenarios: 1) real backtrack vs rebuild; 2) force hook, state asserts only; 3) hook-driven backtrack; 4) hook delegating to commit; 5) BREAK: answers cleared but derived cache stale; 6) finalize autofill vs authored agreement
- Link: scheduled brain train session 2026-10-08
- Audited: 2026-10-12 · modeled · Read the entry and its 65-line sandbox. The oracle comparison in S1 and S4 is genuinely computed (a fresh rebuild through commit() compared to the live view). But the headline failures are built in: force() is written to only set answers, so empty derived labels, the overlay still up and stale downstream answers after a hook-driven backtrack (S2, S3) follow directly from its definition rather than being discovered, and S5 clears answers by hand while leaving the cache alone. The rule of thumb says a bypassing hook "proves nothing", which overreaches: S2 shows the route assertion does hold, so it proves the route only. The claim is about real test hooks in dog and couchbound code, tested here only against a reduced hand-written wizard, so it is modeled; the delegating-hook fix matching the oracle is the one non-trivial finding. · scheduled brain train session, loop 2 pass 3 audit; session_018RFPy3DMrymTRHnMWEoTT9
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-creative-training.md#E36 · compatible · sandboxes/2026-10-15__test-hook-fast-forward-batches-deferred-sweeps-so-a-full-view-rebuild-oracle-misses-lost-credit.py · observed RESULT: PASS delegating one-sweep hook passes full-view rebuild oracle (state==real) but credits player 2/auto 1 vs real 3/1; per-commit sweep 3/1; origin-set 3/1; rebuild has no origins (credit {'rebuild': 2, 'auto': 1}); same-tick real p… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 4 pass 2
