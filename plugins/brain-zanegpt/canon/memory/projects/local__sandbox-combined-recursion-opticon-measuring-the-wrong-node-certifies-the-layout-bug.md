# local/sandbox-combined-recursion-opticon-measuring-the-wrong-node-certifies-the-layout-bug — lessons

Project: local/sandbox-combined-recursion-opticon-measuring-the-wrong-node-certifies-the-layout-bug. Newest first.

---

## E1 — sandbox combined recursion opticon measuring the wrong node certifies the layout bug
- Date: 2026-08-29
- Project: local/sandbox-combined-recursion-opticon-measuring-the-wrong-node-certifies-the-layout-bug
- Tags: [ui][testing][layout][harness]
- What: A deterministic sandbox (fixed row list and column width, no RNG) laying out wrapping and non-wrapping text rows with recursion#E9's missing final-line cursor advance, then running a no-overlap geometry assertion twice — once measuring fixed-height chip boxes and once measuring the real multi-line labels.
- Why built: recursion#E9 records that a word-wrap row helper returning a next-line cursor must advance it after the final line too, or a stacked row overlaps by one line-height, and prescribes auditing the no-wrap path. opticon#E37 records that a geometry test passed against verbatim-broken CSS because it measured chip boxes rather than the overflowing labels, prescribing that absence-assertions first assert presence and measure the node that moves. This tests whether E37 is a general testing nicety or the precondition for detecting E9 at all.
- Design: Four rows, two of which wrap to multiple lines, laid out with a cursor that advances a single line-height regardless of lines drawn (E9's bug shape) and with the correct per-line advance. The no-overlap assertion runs against fixed-height chip boxes and against the labels' real multi-line extents.
- Got right: An initial construction made the advance bug so severe that even fixed-height chip boxes overlapped, which would have shown both measurements failing and demonstrated nothing; reducing it to the realistic single-advance form isolated the measurement variable.
- Where/why it failed: With E9's bug present the layout has one real overlap. Measuring fixed-height chip boxes the no-overlap assertion returns True; measuring the labels' real extents it correctly returns False. A suite that measures the wrong node therefore certifies the exact layout bug E9 documents.
- Fix: Measure the node whose height actually varies with content — the rendered label, not its container chip — and assert presence before asserting absence of overlap, as opticon#E37 prescribes, before treating any layout suite as covering the wrapping path.
- Why this fix: recursion#E9's prescribed remedy is to audit the no-wrap path, which presumes a test capable of observing the defect. opticon#E37 supplies that precondition, so the two are ordered rather than independent: without E37's measurement discipline, E9's audit has no instrument, and a green geometry suite is evidence about the chip container rather than about the layout.
- Rule of thumb: opticon#E37's "measure the node that MOVES" is the precondition for detecting recursion#E9's missing final-line advance, not a general testing nicety — sandbox-confirmed a no-overlap assertion returning True on fixed-height chip boxes and False on the real multi-line labels for the identical broken layout.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b12/l30.py), including a first construction whose advance bug was severe enough to overlap the chip boxes too; confirmed the corrected form yields one real overlap with the chip-box assertion passing (True) and the real-label assertion failing (False). the-game-the-recursion#E9 and opticon#E37 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__the-game-the-recursion/E9, pappydapimp69__opticon/E37
- Link: session_014mRpopK9xnhvk35tT8ozkX

