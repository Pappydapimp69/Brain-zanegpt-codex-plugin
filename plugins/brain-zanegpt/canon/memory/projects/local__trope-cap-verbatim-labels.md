# local/trope-cap-verbatim-labels — lessons

Project: local/trope-cap-verbatim-labels. Newest first.

---

## E1 — trope cap counter needs verbatim trope labels under engine first batches
- Date: 2026-10-16
- Project: local/trope-cap-verbatim-labels
- Tags: [comedy][game-ads][testing][sandbox]
- What: In an engine-first fake-ad batch (8 engines x 2 skeletons, 6 tropes, per-trope cap of 2 so a ceiling of 12), a cap counter keyed on free-text trope labels let a trope exceed the cap in 96% of 12-video batches once 30% of labels were paraphrased, while a closed verbatim trope list breached 0%.
- Why built: New-half train pick joining the vary-the-comic-engine kernel, the fake-ad kernel source check (a paraphrased label 'borrowed fame' for 'popular externalization') and the batch-ceiling trope cap, to see whether the label-drift problem also breaks the trope cap and not only the engine counter.
- Design: Seeded 2000-batch simulation. Engines are assigned round-robin (engine-first), a trope is drawn per video, and the counter redraws once when the written label is at the cap. Paraphrase rate 0, 0.3 and 0.6 with free text, 0.6 with a closed list that rejects non-verbatim labels, and a 16-video request past the ceiling.
- Got right: Engine-first held the max engine repeat at 2 in every scenario, and with no paraphrase the cap held exactly (0 breaches), so the label is the only failure source; the 16-video request produced only 12 videos, matching the ceiling min(16, 6R).
- Where/why it failed: I predicted only a modest breach rate (over 10%) at 30% paraphrase; it was 96%, because one paraphrased label gives a trope a second counter bucket and the redraw sends videos back to it.
- Fix: Make the trope cap counter use the same closed verbatim name list as the engine counter and reject any label not on it, costing a relabelling step, before trusting either cap.
- Why this fix: Every cap in the batch is a count over names, so any name that can drift splits one bucket into two and silently doubles the cap; one closed list protects all counters at once.
- Rule of thumb: Key the per-trope cap on a closed verbatim list: at 30% paraphrased labels a free-text counter let a trope exceed a cap of 2 in 96% of 12-video batches, versus 0% with the closed list.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the trope list, cap of 2 and 8x2 slots come from the named lessons, and the paraphrase rates are my own assumptions.
- Composed: ideas:COMEDY-CRAFT/vary-the-comic-engine-not-the-topic, fake-ad-kernel-source-check/E1, batch-ceiling-trope-cap/E1
- Picked-by: new-half
- Distinct from: brain-auto-training/E23 (that lesson shows the engine-repeat counter needs verbatim labels; this finds the same drift also breaks the per-trope cap, 96% breach at 30% paraphrase).
- Sandbox: sandboxes/2026-10-16__trope-cap-counter-needs-verbatim-trope-labels-under-engine-first-batches.py
- Prediction: Hidden assumption: a counter keyed on free text still roughly enforces the cap. Expected 0 breaches with no paraphrase and over 10% breaches at 30%; it would be wrong if free text at 30% matched 0 breaches.
- Observed: RESULT: PASS breach free p0 0.000 p.3 0.959 p.6 0.991 verbatim 0.000; engine repeat max 2; k16 made 12.00 of 16 (ceiling 12)
- Scenarios: 1) free text, no paraphrase; 2) free text 30% paraphrase, built to break the cap; 3) free text 60%; 4) closed verbatim list at 60%; 5) 16 videos requested past the ceiling.
- Link: scheduled brain train auto loop 1 pass 1 (kernel); session_01GYKQrKfm5FQsrnyu59GmiS

