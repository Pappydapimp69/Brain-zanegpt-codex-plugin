# local/folded-signature-conjoint-leaves-pair-i-with-leaf-count-plus-one-minus-i — lessons

Project: local/folded-signature-conjoint-leaves-pair-i-with-leaf-count-plus-one-minus-i. Newest first.

---

## E1 — folded signature conjoint leaves pair i with leaf count plus one minus i
- Date: 2026-10-18
- Project: local/folded-signature-conjoint-leaves-pair-i-with-leaf-count-plus-one-minus-i
- Tags: [bookbinding][geometry][model][testing]
- What: Folding a strip of 2, 4, 8 and 16 panels in half repeatedly into a signature and reading the stack as a book gives, for each pair of panels facing across a fold, page numbers on the same strip face that sum to the page count plus one (for 8 pages the faces read 7,2,3,6 and 8,1,4,5), conjoint leaves that sum to the leaf count plus one, and a blank-page need of 2 for 10 pages, 0 for 12 and 2 for 30.
- Why built: Seeding a bookbinding domain from a real layout question (what goes where on a printed sheet), since no kernel or lesson covered imposition.
- Design: Physical fold simulation: a stack of layers each holding (panel, face up); each fold turns the right half over onto the left half, flipping and reversing it; the final stack read top to bottom gives leaf i with recto 2i-1 and verso 2i; then test the page-pair sums and the leaf-pair sums and compute the blanks as minus pages mod 4.
- Got right: The panel pairs summed to N+1 pages and M+1 leaves for k from 1 to 4, and the 8-page result 7,2,3,6 and 8,1,4,5 is the standard single-sheet imposition.
- Where/why it failed: Nothing in the prediction failed, but only repeated fold-in-half signatures of 4, 8, 16 and 32 pages were modeled, not letter folds, sewing, creep or binding margins, and I did not check the layout against a published imposition chart.
- Fix: Compute imposition by simulating the fold of the strip and pairing pages to sum to the page count plus one, and pad the page count to a multiple of 4 with blanks before imposing.
- Why this fix: The pairing follows from the physical order of layers, so a simulated fold gives every sheet size without a lookup table, and the multiple-of-4 rule is just the two pages on each of two sides of a folded leaf.
- Rule of thumb: In a fold-in-half signature of N pages, facing panels on one sheet face carry pages that sum to N+1 (7,2,3,6 and 8,1,4,5 at N=8), and N must be a multiple of 4, so pad 10 pages with 2 blanks.
- Provenance (verified/assumed): Verified first-hand by running the sandbox in this session; the model is the fold-in-half case only and the result was not compared with a published chart.
- Composed: N/A
- Sandbox: sandboxes/2026-10-18__folded-signature-conjoint-leaves-pair-i-with-leaf-count-plus-one-minus-i.py
- Prediction: Written into the script header before the first run: panels facing across a fold carry leaves summing to M+1 and pages summing to N+1 for k 1 to 4, with blanks 2, 0 and 2 for 10, 12 and 30 pages.
- Observed: RESULT: PASS folded strips k=1..4: facing panel pairs (0,1),(2,3).. sum to N+1 pages and conjoint leaves sum to M+1 in [(1, True), (2, True), (3, True), (4, True)]; blanks 10->2, 12->0, 30->2
- Scenarios: 1) k=1 four pages; 2) k=2 eight pages; 3) k=3 and k=4 sixteen and thirty-two pages; 4) BREAK: page counts 10, 12 and 30 that are not multiples of 4 for the blank rule
- ZaneGPT verdict: weak — the arithmetic is self-consistent (N+1 sums, minus-pages-mod-4 blanks), but it was checked only against the script's own fold model, which shares the convention it is meant to confirm, so it has not been shown to hold for real sheets, cross folds, or mixed-unit books.
- Hidden assumption: Every fold is a clean in-half fold of one strip, with the simulation's own flip-and-reverse convention matching real paper (right half over onto left, a quarter-sheet fold, and the same page-to-panel numbering). The "7,2,3,6 / 8,1,4,5" face layout, and the claim that facing panels sum to N+1, are properties of that convention, not independent facts. They are also generalized from one imposition, the single-strip fold-in-half signature.
- Would prove it wrong: A real folded and numbered sheet of 8 where facing pages on one face don't sum to 9. The same goes for a physical fold that reverses the sequence the simulation assumed. Another refutation is any k where the simulation's reading order puts recto 2i-1 on a different leaf than a hand-folded copy does. Simulating with the opposite fold direction (left over right) and getting different sums would also break it.
- Break scenario: Use 16 pages as an octavo-in-sixteenmo variant. Cut the strip, or fold the long way (a cross fold rather than an in-half fold), as real 8-up and 16-up impositions do: fold in half twice at right angles, then number the panels on a 2D grid. The pair sums and the face layout will differ from the 1D strip result. Also test 10 pages made as one 12-page signature plus a 2-page cancel, or as 3 folded sheets (a 4+4+2 plan), since "N must be a multiple of 4" is only true for a single folded signature, not for a book made of mixed or sewn units.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-18 · digest bbd9b1285502
- Link: scheduled brain train auto loop 2 pass 6 (newdomain); session_01U1GJP4ePDFrmU7psLn9wKR
- Cited-by: 2026-10-19 · projects/pappydapimp69__brainwork.md#E492 · compatible · sandboxes/2026-10-19__multi-signature-imposition-pairs-sum-locally-not-globally-and-greedy-needs-chain-sizes.py · observed RESULT: PASS local sum constant per signature, global sums [9, 25, 41] over 3 signatures; greedy chain misses 0/199; non-chain greedy worse 131/199 · brain train auto loop 2 pass 2, session 2026-10-19; session_01M3VVz3RFpipo1Jc6ecPoW2
