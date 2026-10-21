# local/game-languages-gdscript — lessons

Project: local/game-languages-gdscript. Newest first.

---

## E1 — gdscript type the whole dependent chain
- Date: 2026-10-17
- Project: local/game-languages-gdscript
- Tags: [game-languages][gdscript][performance][sandbox]
- What: Seeded GAME-PROGRAMMING-LANGUAGES with Godot's documented rule that typed GDScript gets optimized opcodes
  when operand types are known at compile time, modelled as a toy interpreter where generic ops cost
  three times a typed op.
- Why built: Brain train newdomain: coding languages for games; GDScript is Godot's main language and canon held
  nothing on where its typing pays.
- Design: Ten-statement hot loop run 1000 times; a statement is typed only if all its inputs are typed; tested a
  dependent chain (each step uses the previous result) with one untyped value at the head, middle or
  tail, and ten independent statements with one untyped.
- Got right: All typed cost 10000 and all untyped 30000; one untyped value at the tail cost 12000, and in independent
  statements one untyped op also cost 12000, keeping 90 percent of the typed gain.
- Where/why it failed: One untyped value at the head of the dependent chain made all 10 operations generic and cost 30000,
  keeping none of the typed gain; at the middle it made 5 generic (20000).
- Fix: Type the values that feed a dependent chain first, starting from its head, before typing leaf or
  independent statements.
- Why this fix: Where an untyped value sits matters more than how many there are: the head of a chain spreads to
  every step after it, a leaf touches only itself.
- Rule of thumb: In a GDScript hot loop, type the head of each dependent chain first: one untyped value there makes every
  later step generic, while the same value at a leaf costs only its own operation.
- Provenance (verified/assumed): Verified first-hand by the toy interpreter; Godot's rule that typed code uses optimized opcodes when types
  are known at compile time checked against the Godot docs. How far an untyped result spreads, and the
  1-versus-3 op costs, are modelling assumptions.
- Composed: N/A
- Sandbox: sandboxes/2026-10-17__gdscript-type-the-whole-dependent-chain.py
- Prediction: An untyped value at the head of a 10-step chain makes all 10 generic and loses the whole typed gain; at
  the tail it costs one op; among independent statements one untyped op keeps about 90 percent.
- Observed: RESULT: PASS head: 10 generic ops, 30000 (0 percent of the gain kept); middle: 5, 20000; tail: 1, 12000;
  independent with one untyped: 12000, 90 percent kept.
- Scenarios: 1) all typed; 2) all untyped; 3) BREAK: untyped at the head of the chain; 4) untyped in the middle;
  5) untyped at the tail; 6) independent statements, one untyped
- ZaneGPT verdict: weak — the PASS only confirms the toy's own propagation rule, which was written into it, so it tests arithmetic rather than Godot, and the rule of thumb needs a measurement in the real engine before it counts as a lesson.
- Hidden assumption: The "typed only if all inputs typed" propagation is the toy's own rule, not a measured Godot behavior. It assumes inference never rescues a chain: that a `var x := ...` or typed assignment after an untyped head can't re-establish a known type, and that the 3x generic cost is real.
- Would prove it wrong: A benchmark in Godot 4.x, comparing a 10-step chain with an untyped head against the same chain with an explicitly typed local or return annotation at step 2. If step 2 onward runs at typed speed (or the generic penalty is nowhere near 3x), the "head first" ordering and the 0 percent figure are artifacts of the toy.
- Break scenario: The head is untyped, but step 1 immediately assigns into a typed local (`var a: float = untyped_val`), or the chain is built from typed function returns or typed constants. Real GDScript re-types at that boundary, so the "tail costs one op" and "head loses everything" asymmetry collapses to roughly one generic op wherever the untyped value sits.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest 232753c69aad
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

