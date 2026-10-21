# local/sandbox-combined-mirage-wrong-sky-emit-collision-plus-zero-magnitude — lessons

Project: local/sandbox-combined-mirage-wrong-sky-emit-collision-plus-zero-magnitude. Newest first.

---

## E1 — sandbox combined mirage wrong sky emit collision plus zero magnitude
- Date: 2026-08-29
- Project: local/sandbox-combined-mirage-wrong-sky-emit-collision-plus-zero-magnitude
- Tags: [state][events][gamedev][testing]
- What: A deterministic sandbox (fixed event payloads, no RNG) combining mirage#E1's spread-order emit bug with wrong-sky#E5's truthy-versus-existence read on a legitimately-zero magnitude, measuring what each defect does alone and what they do together.
- Why built: mirage#E1 records that a "base fields + ...opts" emit helper must spread opts BEFORE its reserved fields, or a caller opt sharing a reserved name silently wins and the event's own type never reaches its readers. wrong-sky#E5 records that a sparse map whose values can legitimately be 0 must be existence-checked, never truthy-checked. Both are silent, both concern the same event object, so this tests what a single event carrying both defects actually does.
- Design: Two emit helpers differing only in spread order, and two readers differing only in truthy versus `in` checking. A zero-magnitude damage event is constructed whose opts also collide with the reserved `kind` field, then read through both readers.
- Got right: Isolating each defect on its own first (the collision alone, the zero-magnitude read alone) before combining them, so the compound behaviour is attributable to the interaction rather than being an unexplained single result.
- Where/why it failed: Together the defects produce a silent double misroute. The event's `kind` becomes `ui_hint` instead of `damage`, so it reaches the wrong handler entirely, and its real amount of 0 reads as absent through the truthy check. Critically, each single fix makes the other bug look fixed: repairing the emitter yields a correctly-routed event whose 0 magnitude is still dropped, and repairing the reader yields a correct 0 delivered to the wrong handler. Nothing throws in any configuration.
- Fix: Apply both repairs in the same change — spread opts before reserved fields in the emitter, and existence-check rather than truthy-check every magnitude that can legitimately be zero — and write the regression fixture as a zero-magnitude event with a colliding key, since neither defect's own natural test case contains the other.
- Why this fix: The compound failure is not additive but masking. After either single fix the event is still wrong and still silent, but the remaining symptom moves — from "the handler never ran" to "the handler ran with no effect," or vice versa — which reads as a new, unrelated bug rather than as the original one persisting, so the second defect is likely to be re-diagnosed from scratch.
- Rule of thumb: mirage#E1's emit-collision and wrong-sky#E5's truthy-read compose into a silent double misroute where each single fix makes the other look fixed — sandbox-confirmed a zero-magnitude event with a colliding key routes to `ui_hint` AND reads as absent; fix both together and use a zero-magnitude colliding-key event as the fixture, since neither defect's own test contains the other.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b2/l9.py) and confirmed opts-last yields kind='ui_hint' while opts-first yields 'damage', the truthy read returns None on a real amount of 0 where the existence read returns 0, and the combined event carries both faults with no exception raised. mirage#E1 and the-game-wrong-sky#E5 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__mirage/E1, pappydapimp69__the-game-wrong-sky/E5
- Link: session_014mRpopK9xnhvk35tT8ozkX

