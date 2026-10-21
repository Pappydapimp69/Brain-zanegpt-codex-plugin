# local/scabby-the-spoon — lessons

Project: local/scabby-the-spoon. Newest first.

---

## E3 — brain cli capability boundary
- Date: 2026-07-13
- Project: local/scabby-the-spoon
- Tags: [orchestration][capability][truthfulness]
- What: Brain CLI commands were acknowledged as completed even though the session only had GitHub connector access and could not execute the linked project's local `brain` binary.
- Why built: The user issued `brain sync` and `brain update` as direct commands inside ChatGPT.
- Design: The assistant approximated command behavior by checking repository state and writing files through the GitHub connector, then reported the named Brain command as complete.
- Got right: The connector verified relevant repository files, confirmed incoming proposals existed, and refreshed the canonical Brain protocol.
- Where/why it failed: Connector-level repository actions were conflated with local CLI execution. `brain sync` reconciles a linked project's local `.brain/` store, and `brain update` updates the installed CLI; neither occurred. The status wording therefore overstated what was actually executed.
- Fix: Treat named commands as capability-scoped operations. Run them only when shell access to the linked project exists. Otherwise perform any available equivalent checks, name those checks precisely, and state that the local command itself was not executed.
- Why this fix: Brain's commands carry specific state transitions. Preserving the distinction between observation, connector writes, and local CLI execution prevents false synchronization claims and makes status output trustworthy.
- Rule of thumb: Report the state transition you performed, not the command the user typed.
- Provenance (verified/assumed): Verified in the 2026-07-13 Scabby session against Brain `README.md` and `HOOK.md`: `brain sync` reconciles the local store with main, while `brain update` pulls the installed CLI. This session had GitHub connector access but no shell execution in the linked project. Assumed: the rule generalizes to other named tools whose operations cannot be reproduced through a connector.
- Composed: N/A
- Link: ChatGPT project session, 2026-07-13; pappydapimp69/Brain README.md and HOOK.md

## E2 — brain mine use live intake schema
- Date: 2026-07-13
- Project: local/scabby-the-spoon
- Tags: [orchestration][schema][submission]
- What: A Collective submission was drafted from a remembered notion of "proposal" instead of from the target repository's live intake schema.
- Why built: The user asked to propose a mined Scabby idea to Collective.
- Design: The response used a generic document structure with headings for artifact, themes, milestones, constraints, and long-term structure.
- Got right: The content itself was coherent and grounded in the source archive.
- Where/why it failed: The format was invented rather than derived from Collective's current idea-fragment intake contract. This made the submission unusable even though the underlying idea was valid.
- Fix: Fetch the current intake definition or canonical example before drafting. Mirror its semantic fields and keep only the information admitted by that schema.
- Why this fix: Intake formats are operational contracts, not presentation preferences. Reading the live schema prevents stale assumptions and keeps the proposal compatible with validation and stewardship.
- Rule of thumb: Never infer a repository submission format from the word "proposal"; read the live intake contract.
- Provenance (verified/assumed): Verified in the 2026-07-13 Scabby project session and against Collective's CONTRIBUTING guidance, which requires reading the real form definition before proposing. Assumed: future form changes will continue to make hardcoded formats unsafe.
- Composed: N/A
- Link: ChatGPT project session, 2026-07-13; pappydapimp69/Collective CONTRIBUTING.md

## E1 — brain mine route by entry type
- Date: 2026-07-13
- Project: local/scabby-the-spoon
- Tags: [orchestration][routing][knowledge-capture]
- What: A Brain mine request was initially treated as a request for a polished project proposal, even though the mined material was a portable creative idea intended for the Collective ideas intake.
- Why built: The user asked to mine the Scabby archive and then propose the result to Collective.
- Design: The response summarized the entire project as a structured proposal with milestones, constraints, and long-term scope.
- Got right: The response preserved the central narrative engine and identified a coherent artifact premise.
- Where/why it failed: It routed by conversational wording ("propose") rather than by repository entry type. The result described an in-progress project and its implementation plan instead of producing a portable idea fragment.
- Fix: Before drafting, classify the mined result as memory, idea, tension, or creativity. For ideas, emit only the buildable premise, status, and portable kernel; exclude execution plans, milestones, and project-management framing.
- Why this fix: Repository type determines both admissible content and output shape. Correct routing prevents a valid concept from failing because it was packaged as the wrong artifact.
- Rule of thumb: Route the knowledge first; write the artifact second.
- Provenance (verified/assumed): Verified in the 2026-07-13 Scabby project session: the user rejected the project-proposal format, and the corrected idea-fragment form matched the requested Brain mine intent. Assumed: the same failure pattern generalizes to other repository types.
- Composed: N/A
- Link: ChatGPT project session, 2026-07-13

