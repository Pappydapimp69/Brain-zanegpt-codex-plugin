# local/sandbox-combined-quest-offer-batch — lessons

Project: local/sandbox-combined-quest-offer-batch. Newest first.

---

## E1 — exclusive offer batch must be state sourced
- Date: 2026-07-13
- Project: local/sandbox-combined-quest-offer-batch
- Tags: [quest][state][security][gamedev][testing]
- What: An exclusive quest-choice accept handler is bypassable if it relies on the command payload to say which batch should be withdrawn. Omitting that metadata lets the player accept one offer without withdrawing the siblings, then accept another mutually exclusive offer.
- Why built: `brain train` selected the high-value seam `the-game-the-recursion + the-game-wrong-sky`. The interaction claim was that recursion#E2's "never trust command-supplied gate values" applies to wrong-sky#E4's exclusive-offer withdrawal: the batch/exclusivity value must come from authoritative pending-offer state, not from the accept command.
- Design: Built `sandbox-exclusive-offer-command-payload.js`, a deterministic reducer model with: - Three pending offers, `a`, `b`, and `c`, all in one exclusive `crossroads` batch. - A naive accept handler that withdraws siblings only when `command.exclusiveBatch` is present. - A fixed accept handler that reads the accepted offer's batch from state and withdraws siblings from that. - A two-command adversarial path that accepts `a` and then `b` while omitting batch metadata.
- Got right: The sandbox uses the same player-visible command shape for both handlers and only changes the source of truth for exclusivity. That isolates the trust-boundary bug from quest UI or test re-query behavior.
- Where/why it failed: The naive handler accepted `a`, left `b,c` pending because the command omitted `exclusiveBatch`, then accepted `b`. Final accepted offers were `a,b`, violating the exclusive batch. The fixed handler accepted only `a` and withdrew all competing offers immediately.
- Fix: Attach exclusivity/batch identity to the authoritative pending offer in state and read it from there during accept. Treat command payload fields as selectors or intent, not as policy values that decide whether exclusivity applies.
- Why this fix: With state-sourced batch identity, the first accept removed all siblings even when the command omitted batch metadata. The accepted count stayed at 1 and no pending offers remained. The command could no longer bypass the withdrawal rule by leaving out the field.
- Rule of thumb: If a reducer command can benefit from omitting or changing a policy value, that value belongs in state before the command exists. For exclusive choices, the accept command should identify the offer; state should identify the batch.
- Provenance (verified/assumed): Verified first-hand on 2026-07-13 by running `node sandbox-exclusive-offer-command-payload.js` in `C:\Users\Kompooter\Documents\Brain`. Observed: naive command-supplied batch = accepted `a,b`, accepted count 2, pending after first `b,c`, pending final `c`, exclusive batch violated `true`; fixed state-sourced batch = accepted `a`, accepted count 1, pending after first empty, pending final empty, exclusive batch violated `false`.
- Composed: the-game-the-recursion/E2, the-game-wrong-sky/E4
- Link: Sandbox: `sandbox-exclusive-offer-command-payload.js`

