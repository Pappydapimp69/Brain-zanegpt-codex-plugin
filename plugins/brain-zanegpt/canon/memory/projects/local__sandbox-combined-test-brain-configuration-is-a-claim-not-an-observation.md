# local/sandbox-combined-test-brain-configuration-is-a-claim-not-an-observation — lessons

Project: local/sandbox-combined-test-brain-configuration-is-a-claim-not-an-observation. Newest first.

---

## E1 — sandbox combined test brain configuration is a claim not an observation
- Date: 2026-08-29
- Project: local/sandbox-combined-test-brain-configuration-is-a-claim-not-an-observation
- Tags: [verification][process][security][method]
- What: A deterministic sandbox (fixed actor list and rule definition, no RNG) evaluating a branch-protection rule two ways — by reading its configuration, and by attempting a push with each actor the rule claims to block — where a bypass list overlaps the block list.
- Why built: test#E14 records that a branch-protection rule is a claim, not a fact, and that it must be tested with the actor it is meant to stop because apps and bypass lists can make it a silent no-op. brain#E21 records that a self-reported "N pushed, 0 held" is not a promotion because acceptance runs elsewhere. This tests whether the two are the same structural error at different layers.
- Design: Three actors against a rule blocking two of them, with a bypass list that overlaps the block list on one actor. Verification by configuration simply asks whether the rule exists; verification by refusal attempts the push and checks the outcome.
- Got right: Making the bypass overlap partial rather than total, so one blocked actor really is refused — which is what makes the configuration check look credible and the failure specific rather than global.
- Where/why it failed: Verification by configuration returns True and is worthless. The rule claims to block two actors, genuinely refuses one, and is silently bypassed for the other, so the only way to learn which is to attempt the push with each blocked actor and observe the outcome.
- Fix: Verify any access-control rule by watching it refuse the specific actor it names, and treat a configuration read as documentation of intent rather than evidence of effect — the same instruction brain#E21 gives for promotion.
- Why this fix: Both entries describe reading a self-reported state back from the system that produced it in place of an independent observation of the outcome. The layers differ — an access-control declaration versus a sync summary — but the remedy is identical: make the system actually do the thing and observe what happened. Recognising them as one error means a codebase that has internalised brain#E21 already has the discipline test#E14 needs, and vice versa.
- Rule of thumb: test#E14's branch-protection claim and brain#E21's "N pushed, 0 held" are the same error at different layers — reading a system's own declaration instead of observing an outcome; sandbox-confirmed a rule that reads as configured and genuinely refuses one blocked actor while being silently bypassed for another, detectable only by attempting the action with each named actor.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b11/l29.py) and confirmed verify-by-configuration returns True while verify-by-refusal returns True for one blocked actor and False for the other, whose push is allowed via the bypass list. test#E14 and brain#E21 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__test/E14, pappydapimp69__brain/E21
- Link: session_014mRpopK9xnhvk35tT8ozkX

