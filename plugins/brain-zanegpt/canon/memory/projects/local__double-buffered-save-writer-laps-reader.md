# local/double-buffered-save-writer-laps-reader — lessons

Project: local/double-buffered-save-writer-laps-reader. Newest first.

---

## E1 — double buffered rng save tears once the writer laps the reader
- Date: 2026-10-15
- Project: local/double-buffered-save-writer-laps-reader
- Tags: [concurrency][state][testing]
- What: Composed zanegpt E12 (copy PRNG state words through a double buffer flipped by a 1-bit index, Gray
  index for more slots) with brainwork E293 (a Gray counter read mid-change is old or new for one step
  per read), asking whether the buffer inherits the one-step limit when the generator completes
  several updates during one save.
- Why built: E12's buffer is a 1-bit Gray counter, and E293's guarantee holds only for one step per read. A save
  that copies slowly (a large state, a paused tab, a GC pause) while the sim keeps stepping is exactly
  the case E12's fix is meant for.
- Design: Exhaustive interleavings, no rng. Reader: read the slot index, then 4 words. Writer update: write 4
  words into the next slot, then publish. Every interleaving of the reader with k writer updates
  enumerated. Schemes: copy live words, double buffer with a 1-bit flip, a 4-slot ring stepped in Gray
  order, and a seqlock (version odd while writing; reader re-checks and retries).
- Got right: Copying live words tore in 70 of 126 interleavings with one update; the double buffer had 0 tears
  with one update per read, as E12 found; the 4-slot ring had 0 tears up to 3 updates per read; the
  seqlock never returned a torn copy at any k.
- Where/why it failed: The double buffer tore in 1540 of 3003 interleavings once the writer completed 2 updates during one
  read, because the second update writes into the slot being copied; the 4-slot ring tore at 4 updates
  (13290 of 53130). The seqlock's safety cost liveness: it succeeded only when the copy fit between
  update bursts (k+1 interleavings) and retried in all others (134592 of 134596 at k 3).
- Fix: Size the ring to the most updates that can land during one save (n slots tolerate n-1), or make the
  generator skip its step while a save holds the slot; use a seqlock only where retries are cheap and
  the writer pauses.
- Why this fix: Each scheme moves the same one-step limit around: a buffer of n slots buys n-1 steps of slack, and a
  seqlock trades tears for retries that can starve a reader under a busy writer; only blocking the
  writer removes both.
- Rule of thumb: A double-buffered state save stops being tear-free once the writer completes 2 updates during one
  copy (1540 of 3003 interleavings tore); n slots tolerate n-1, and a seqlock never tears but retries
  in nearly every interleaving under a busy writer.
- Provenance (verified/assumed): Verified first-hand by the exhaustive interleaving sandbox in this entry; real memory ordering and
  compiler reordering are not modelled.
- Composed: pappydapimp69__zanegpt/E12, pappydapimp69__brainwork/E293
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__double-buffered-rng-save-tears-once-the-writer-laps-the-reader.py
- Prediction: single buffer tears at k >= 1; double buffer 0 at k 1 and tears at k 2; 4-slot ring 0 to k 3 and
  tears at k 4; seqlock 0 torn at any k.
- Observed: RESULT: PASS 6/6; single k1 torn 70/126; double k1 0, k2 1540/3003; ring4 k3 0, k4 13290/53130;
  seqlock torn 0, retries k1-3 [922, 18561, 134592]
- Scenarios: 1) live copy k 1, 2; 2) double buffer k 1-3; 3) 4-slot Gray ring k 1-4; 4) seqlock k 1-3; 5) built
  to BREAK E12: the writer lapping the reader (k 2 on the double buffer; it broke)
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto loop 2 pass 2 (edge brainwork + zanegpt), 2026-10-15

