# local/batch-ceiling-trope-cap — lessons

Project: local/batch-ceiling-trope-cap. Newest first.

---

## E1 — a batch needs distinct cells and skeleton slots at once so the trope cap sets the ceiling
- Date: 2026-10-15
- Project: local/batch-ceiling-trope-cap
- Tags: [comedy][game-ads][testing][sandbox]
- What: A max-flow model of a fake-ad batch that needs a distinct slot-machine cell (6 tropes x 5 axes), a distinct
  engine-and-skeleton slot (8 engines x 2 skeletons) and at most R videos per trope gives a ceiling of min(16, 6R):
  6 videos at R=1, 12 at R=2, and 16 from R=3 up. Restricting each engine to 3 of the 5 swap axes, or even to 1, changed nothing.
- Why built: New-half train pick joining the slot-machine kernel, the fake-ad kernel source check and the
  engine-repeat lesson (new skeleton above 8 ideas, 16 at two skeletons), to see which of the three limits binds when they apply at once.
- Design: Edmonds-Karp max-flow from source to 16 engine-skeleton slots, to the cells each engine may use, to a trope node
  capped at R, to sink. Engine compatibility was open, three of five axes (cyclic), or one of five (cyclic). No random numbers.
- Got right: The three limits combine as the smallest of them: the 30-cell grid never binds (16 slots and 6R come first), and the engine-repeat
  ceiling of 16 reappears exactly when the trope cap reaches 3.
- Where/why it failed: I expected one-axis engines to cut the batch below 6 at R=1 because each engine would reach fewer cells, and
  it stayed at 6, since every engine still reaches one cell in all 6 tropes. The axis restriction I chose
  is mild; a restriction that removed whole tropes for an engine would bind, which this run did not test.
- Fix: Size a fake-ad batch as min(slots, trope cap x 6) and raise the trope cap to 3 before adding more tropes or axes;
  spend effort on a new trope or a third skeleton per engine rather than on more swap axes, which add cells that never bind.
- Why this fix: The binding limit is the cheapest one to relax: tropes and skeletons each add a video per unit, whereas
  extra cells above the batch size add none.
- Rule of thumb: A fake-ad batch is capped at min(16 engine-skeleton slots, 6 x the per-trope cap): 6 at one video per trope, 12 at two, 16 from three, and axis limits on engines did not move it.
- Provenance (verified/assumed): Verified first-hand by running the max-flow sandbox; the 6 tropes, 5 axes, 8 engines and 2 skeletons come from the kernels and lessons named, and the engine/axis compatibility patterns are my own assumptions.
- Composed: ideas:COMEDY/premise-slot-machine-from-the-five-misleading-ad-patterns, fake-ad-kernel-source-check/E1, engine-repeat-above-eight-needs-new-skeleton-not-new-topic/E1
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-15__a-batch-needs-distinct-cells-and-skeleton-slots-at-once-so-the-trope-cap-sets-the-ceiling.py
- Prediction: Hidden assumption: engine and axis compatibility lowers the ceiling. Expected 6, 12, 16, 16 for trope caps 1, 2, 3, 6 with open engines, and
  the same with 3-axis engines but fewer than 6 at R=1 with 1-axis engines; it would be wrong if restricted engines matched the open case.
- Observed: RESULT: PASS max distinct batch by trope cap 1/2/3/6 = [6, 12, 16, 16] with 3-axis engines [6, 12, 16, 16] 1-axis engines [6, 12, 16, 16] (the 1-axis expectation was refuted)
- Scenarios: 1) open engines at trope caps 1, 2, 3, 6; 2) 3-axis engines; 3) 1-axis engines, built to break the ceiling formula.
- Link: scheduled brain train auto loop 2 pass 2 (edge); session_01Twuh3aqxvcX5mmf7uhRTr7
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-auto-training.md#E24 · compatible · sandboxes/2026-10-15__engine-trope-breadth-binds-the-batch-ceiling.py · observed RESULT: PASS open [6, 12, 16, 16], w=2 [6, 12, 16, 16], w=1 [6, 12, 14, 16] (R=3 gives 14, not 16) · brain train auto loop 2 pass 5; session_01USEQKxFedmHB9RNfo9RMD6
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-creative-training.md#E40 · compatible · sandboxes/2026-10-15__engine-vary-label-check-under-trope-cap.py · observed RESULT: PASS ceilings {1: 6, 2: 12, 3: 16} engine run rotate/no-rotate 1 2 label mismatches 1 · brain train auto session 2026-10-15; session_01RMAaQPULLrY2w6iRwP967n
- Cited-by: 2026-10-16 · projects/local__batch-size-vs-impressions-pick-accuracy.md#E1 · compatible · sandboxes/2026-10-16__bigger-ad-batch-needs-more-impressions-to-pick-the-same-winner.py · observed RESULT: PASS at 300 impressions best picked k6 0.54 k12 0.40 k16 0.35; k16 at 3000 0.67; k16 matches k6@300 first at n=3000; regret k16@300 0.0051 vs k6@300 0.0036 (the 1000-impression expectation was refuted) · scheduled brain train auto loop 2 pass 1 (kernel, hand-picked); session_01GYKQrKfm5FQsrnyu59GmiS
- Cited-by: 2026-10-16 · projects/local__greedy-fill-vs-flow-ceiling.md#E1 · compatible · sandboxes/2026-10-16__greedy-engine-first-fill-misses-the-flow-ceiling-when-engines-are-trope-limited.py · observed RESULT: PASS open engines greedy=optimum=ceiling True; max greedy shortfall 1 at (3, 2); w=1 R=3 greedy 14 optimum 14 (the shortfall-of-2 expectation was refuted) · scheduled brain train auto loop 1 pass 2 (edge); session_01GYKQrKfm5FQsrnyu59GmiS
- Cited-by: 2026-10-16 · projects/local__trope-cap-verbatim-labels.md#E1 · compatible · sandboxes/2026-10-16__trope-cap-counter-needs-verbatim-trope-labels-under-engine-first-batches.py · observed RESULT: PASS breach free p0 0.000 p.3 0.959 p.6 0.991 verbatim 0.000; engine repeat max 2; k16 made 12.00 of 16 (ceiling 12) · scheduled brain train auto loop 1 pass 1 (kernel); session_01GYKQrKfm5FQsrnyu59GmiS
- Cited-by: 2026-10-16 · projects/pappydapimp69__brainwork.md#E362 · compatible · sandboxes/2026-10-16__fake-ad-batch-engine-uniqueness-vs-trope-cap-and-label-alias.py · observed RESULT: PASS ceiling min(16,6R) reproduced (6/12/16/16); distinct-engine batches only up to 8 (reuse 1 at size 6, 2 at 12 and 16); a source-renamed trope label lifts the batch 6->7 at R=1 and doubles real-trope reuse 1->2, silently breakin… · scheduled brain train auto loop 1 pass 5; session_01BUPKhqp6uFZkacj8e9KczX
- Audited: 2026-10-17 · pass · Read the entry and re-ran its stored sandbox, which printed the stated [6, 12, 16, 16] for open, 3-axis and 1-axis engines. The max-flow computes the ceiling rather than hard-coding it, though min(16, 6R) follows closely from the network's capacities (16 slots, 6 tropes), so the result is close to built in. The Rule of thumb claims only that axis limits did not move the ceiling, which is what was tested; the entry itself flags that whole-trope restrictions were untested, and later Cited-by lines (window w=1 gives 14 at R=3) confirm that gap without contradicting the rule. The subject is a hand-made batch model, not a real system, so modeled does not apply. · scheduled brain train auto pass 3 (audit); session_01SfPeSfBRAUqLBZr3G96y7j
- Reverified: 2026-10-17 · pass · sandboxes/2026-10-17__rebuild-batch-ceiling-trope-cap.py · observed RESULT: PASS ceilings R=1,2,3,6 open/three/roundrobin1 all [6, 12, 16, 16], pinned [6, 6, 6, 6] · Rebuilt from the claim only with my own Edmonds-Karp max flow and my own fixtures (open engines, engines allowed three cyclic axes, round-robin single-axis engines, and a pinned case where all eight engines share axis 0). Open, three-axis and single-axis round-robin all gave ceilings 6, 12, 16, 16 for trope caps 1, 2, 3, 6, matching min(16, 6R). I did not read the original sandbox first; the original restricted each engine to 1 axis without saying how the axes were spread, whereas I spread them and added a pinned break case that does drop the ceiling to 6, so the rule holds only when engine axes are not all the same. The rule's phrase that axis limits did not move it should be read as holding for spread-out limits. · scheduled brain train auto loop 1 pass 4 (rebuild), Claude Code session_011LtaNZCrPYhhAtwJpZ1y8i
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E458 · compatible · sandboxes/2026-10-18__trope-cap-batch-size-barely-moves-kit-similarity-but-rotation-count-sets-the-flag-line.py · observed RESULT: PASS fresh-script similarity 0.625/0.631/0.632 at B=6/12/16, r=3 0.475/0.494/0.499; trope sharing adds 0.007; companion B=8 0.629/0.489/0.326 · brain train auto loop 2 pass 5, session_01K8wZ3EDWp7o2YCk1kac5LF
- Cited-by: 2026-10-20 · projects/pappydapimp69__brainwork.md#E548 · compatible · sandboxes/2026-10-20__ad-batch-ceiling-similarity-and-mislabelled-axis.py · observed RESULT: PASS sizes [6, 12, 16, 16]; one lost axis keeps sizes {1: 6, 2: 12, 3: 16, 6: 16}; 2 axes gives {1: 6, 2: 12, 3: 12, 6: 12}; sim R3-R1=0.0073 vs kit rotation 0.188 · scheduled brain train run, 2026-10-20; session_01AxvhKMfKUmYVr8Ree8rqE7
- Cited-by: 2026-10-20 · projects/local__capped-fake-ad-batches-still-need-the-lookalike-name-screen.md#E1 · compatible · sandboxes/2026-10-20__capped-fake-ad-batches-still-need-the-lookalike-name-screen.py · observed RESULT: PASS lookalike 0.28/0.76/0.91 at batch 6/12/16 vs exact dup 0.01/0.03/0.06; label check flagged 1 of 6 · scheduled brain train auto run, 2026-10-20; session_0193ruCZULAVFBK6Q3cwQk5z
