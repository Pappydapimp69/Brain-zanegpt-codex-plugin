# pappydapimp69/couchbound-story-engine — lessons

Project: pappydapimp69/couchbound-story-engine. Newest first.

---

## E3 — preflight before implementation
- Date: 2026-08-15
- Project: pappydapimp69/couchbound-story-engine
- Title: blueprint and preflight must identify authority and invariants before implementation
- Tags: [process][testing][architecture][deployment][invariants]
- What: Before changing a working system, query prior lessons, write a short behavior blueprint, and inspect the current implementation for authoritative state, competing overrides, listeners, invariants, regression risks, and machine-checkable verification seams. Implement only after that model exists.
- Why built: Fast idea-to-patch work can modify the visible function while missing the later override, duplicated listener, generated bundle, or derived state that actually controls behavior. A locally plausible edit can therefore pass syntax checks yet disappear or conflict in the assembled product.
- Design: Use a gated sequence — query relevant memory and project context; blueprint intended behavior and protected behavior; preflight the current implementation; name authoritative state and functions; locate overrides, duplicate definitions and listeners; state concrete finished-build invariants; list regression risks; choose CI or static checks for each machine-verifiable invariant; implement; verify syntax, assembled output, override ordering and explicit feature markers; deploy only after automated checks pass; and report separately what still requires gameplay or visual testing.
- Got right: This workflow makes the intended change, the non-goals, the authority boundaries, and the proof obligations explicit before edits begin. It also prevents automated verification from being presented as evidence for subjective appearance or real gameplay feel.
- Where/why it failed: In the source session, direct iterative patching exposed two representative hazards — a CSS rule overrode the semantic `hidden` state, and generated fallback answers independently duplicated values even though later prose assumed contrast. Both were valid-looking local changes whose composed behavior violated an unstated invariant.
- Fix: Require the blueprint and preflight artifacts to materially influence the implementation. Every discovered hazard becomes either a protected invariant, an explicit regression risk, or a verification check. Verify the assembled artifact rather than only the edited source, and separate automated proof from the hands-on testing still owed.
- Why this fix: The sequence shifts failure discovery ahead of mutation and ties each promised behavior to an authority location and a proof method. Checking the assembled product catches ordering and override problems that isolated source inspection cannot.
- Rule of thumb: Do not begin editing until you can name what owns the behavior, what must remain unchanged, what invariant proves success, and which parts can only be checked by a person using the finished product.
- Provenance (verified/assumed): VERIFIED first-hand on 2026-08-15 during repeated development of a single-file HTML story engine — the CSS-over-`hidden` override and the duplicated generated-answer regression were both observed in that session, and both are instances of the composed-behavior hazard this sequence exists to catch. The sequence's value across other projects remains an assumption for this entry.
- Composed: N/A
- Link: outputs/couchbound_story_engine.html

## E2 — autofill must preserve assumed contrast
- Date: 2026-08-15
- Project: pappydapimp69/couchbound-story-engine
- Title: autofill must preserve any contrast the synthesis template assumes
- Tags: [procedural-generation][coop][narrative][testing][invariants]
- What: If later prose assumes two generated player contributions are different, blank-answer autofill must enforce that difference rather than sampling each answer independently.
- Why built: The couch-coop flow permits players to leave private answers blank, and random fitting answers are then supplied so the game never stalls — which quietly makes the generator, not the player, responsible for any relationship the later prose depends on.
- Design: Autofill uses small answer pools for names, fears, beliefs, objects, and actions. Player-authored answers remain untouched, including intentional agreement. For Player 2 only, a blank answer is resampled from the pool excluding Player 1's generated value when the first draw duplicates it.
- Got right: Blank inputs kept the flow frictionless and produced usable prose without validation errors, so the fallback path was never a dead end for the players — only for the narrative invariant.
- Where/why it failed: Independent random draws gave both players the same risky action during a full smoke playthrough. The climax then claimed that the heroes combined different parts of their plans even though the displayed actions were identical. The generator was grammatically valid but violated its own contrast assumption.
- Fix: Track whether each answer was authored or auto-filled. Apply distinctness only to auto-filled Player 2 values, filtering Player 1's value from the candidate pool before resampling.
- Why this fix: The narrow rule preserves player agency — two players may deliberately give the same answer — while making automatic content satisfy the narrative template's structural promise.
- Rule of thumb: Whenever generated synthesis says "both", "different", "opposite", or "combined", test and enforce the corresponding relationship between fallback inputs; independent randomness will not produce it for you.
- Provenance (verified/assumed): VERIFIED first-hand — the collision was found in the final end-to-end browser playthrough of `outputs/couchbound_story_engine.html` on 2026-08-15, with both players' actions rendered identically under a climax claiming they differed; the authored-vs-autofilled fix was then applied and clean-load tested.
- Composed: N/A
- Link: outputs/couchbound_story_engine.html
- Cited-by: 2026-10-08 · projects/local__sandbox-wizard-test-hook-vs-real-transition.md#E1 · compatible · sandboxes/2026-10-08__wizard-test-hook-vs-real-transition.py · observed RESULT: PASS state-only assertions blind to hook skipping invalidation/derived/overlay; routing hook through real transition matches fresh rebuild · scheduled brain train session 2026-10-08

## E1 — adaptive story wizard asks for missing causal slots
- Date: 2026-08-15
- Project: pappydapimp69/couchbound-story-engine
- Title: adaptive story wizard asks for missing causal slots
- Tags: [narrative][procedural-generation][ux][state][adaptive-interview]
- What: A story-creation interview should always secure the causal core — who acts, what they want, what blocks them, what can be lost, and what hard choice follows — then ask optional questions only for structural information the earlier answers did not already contain.
- Why built: A fixed nine-question "story DNA" form made player answers feel constrained and repetitive. It also treated genre, tone, setting, theme, and ending as equally important even though a coherent story depends more directly on want, opposition, stakes, and choice.
- Design: The wizard begins with five core questions: kind of story, central pair, desire, disruption, and stakes. After those answers, simple semantic checks identify missing place, opposing force, or thematic value, and only the missing questions are inserted. The hard choice and ending close the route. Rich answers can finish in seven questions; sparse answers can receive up to ten. Supporting categories that are safely implied are derived internally for the generator.
- Got right: The variable route made detailed player answers count twice — they supplied content and removed redundant follow-ups. The final generator could explicitly form a want-but-opposition-therefore-choice spine. Testing confirmed both a seven-question rich route and a ten-question sparse route reached valid stories.
- Where/why it failed: The first implementation used a fixed ordered array of nine metadata keys; renaming the questions and adapting multiple-choice wording improved tone but not creative freedom. A second failure appeared during backtracking: if an earlier answer became richer, previously required optional answers could remain in state even though their questions had disappeared.
- Fix: Rebuild the route after every committed answer. When an earlier answer changes, clear every downstream answer and derived label before recomputing the route. Fill omitted supporting categories only at finalization, never while the player is still navigating.
- Why this fix: Route recomputation makes the interview a function of current answers rather than of navigation history. Clearing downstream state prevents invisible, stale setting or antagonist choices from leaking into the final story after a route contracts.
- Rule of thumb: For generative interviews, require the invariant-bearing slots and dynamically ask for whatever is still missing; when an upstream answer changes, invalidate all downstream answers before rebuilding the route.
- Provenance (verified/assumed): VERIFIED first-hand — observed and browser-tested while rebuilding `outputs/couchbound_story_engine.html` on 2026-08-15, with the rich, sparse, suggestion-assisted, and backtracked paths each walked end to end and confirmed to reach a valid story.
- Composed: N/A
- Link: outputs/couchbound_story_engine.html
- Cited-by: 2026-10-08 · projects/local__sandbox-wizard-test-hook-vs-real-transition.md#E1 · compatible · sandboxes/2026-10-08__wizard-test-hook-vs-real-transition.py · observed RESULT: PASS state-only assertions blind to hook skipping invalidation/derived/overlay; routing hook through real transition matches fresh rebuild · scheduled brain train session 2026-10-08
- Cited-by: 2026-10-09 · projects/pappydapimp69__brainwork.md#E40 · compatible · sandboxes/2026-10-09__narrative-ending-is-a-classifier-over-state-exhaustive-replay.py · observed RESULT: PASS 729 paths -> 4 endings {'dead': 268, 'holding': 97, 'drifting': 359, 'lost': 5}; handler-flag same-state conflicts 62 vs classifier 0; reorder changes ending for 49/81 multisets; staged overlap rule exact over 1331 states · scheduled brain train loop 2 pass 5; session_0177RNbpM9ouiodK1KEajhTr
