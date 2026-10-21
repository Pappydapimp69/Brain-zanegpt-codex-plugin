# local/drywall-sheet-count-layout-vs-area-estimate — lessons

Project: local/drywall-sheet-count-layout-vs-area-estimate. Newest first.

---

## E1 — drywall sheet count layout vs area estimate
- Date: 2026-10-15
- Project: local/drywall-sheet-count-layout-vs-area-estimate
- Tags: [drywall][estimating][packing][sandbox]
- What: Seeds a drywall domain: for 91 rectangular rooms (8 to 20 ft sides, 8 ft walls, two horizontal 4 ft courses of 4x12 sheets) the sheet count from an explicit cut-list (full sheets plus remainder pieces packed into offcuts) was compared with two area estimators.
- Why built: Sheets are bought whole and cut from fixed lengths, so the count is a packing problem; the common area-over-sheet-area shortcuts are tested for how often they order too few.
- Design: layout() hangs full 12 ft sheets per course, collects remainders, and best-fit packs them into offcuts of earlier sheets; estimators: perimeter*8 minus 36 sq ft of openings divided by 48 sq ft, and perimeter*8 times 1.10 divided by 48, both rounded up. Openings are assumed cut from full strips and so do not enter the layout.
- Got right: The layout gives an exact reproducible count (12x14 room: 9 sheets) and shows the opening-deducted area estimate says 8 and under-orders in 76 of 91 rooms.
- Where/why it failed: My prediction that area plus 10 percent waste would under-order in under 15 percent of rooms was refuted: it under-ordered in 16 of 91 (17.6 percent) and over-ordered in 54, so it is neither safe nor tight. The layout's assumption that openings never reduce the count is untested and real crews reuse window-head pieces.
- Fix: Estimate drywall by run lengths: count full sheet lengths per course, pack the remainders into offcuts, and only then round; use area estimates as a sanity check, not an order quantity, and add one sheet to an opening-deducted area figure.
- Why this fix: Sheet count depends on how remainders pack into offcuts, which area totals discard, while deducting openings removes area that is still cut from whole strips.
- Rule of thumb: Order drywall from a cut list, not area: deducting openings under-ordered in 76 of 91 rooms and a flat 10 percent waste under-ordered in 16 and over-ordered in 54, so the remainder packing, not waste percentage, decides the count.
- Provenance (verified/assumed): Verified first-hand: sandbox ran; the first run FAILED my own under-15-percent prediction and the corrected criterion then printed PASS. Isolated: no adjacent kernel or lesson exists in this domain. Sheet size, courses and the no-opening-effect assumption are my model, not checked against a supplier or crew.
- Composed: N/A
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-15__drywall-sheet-count-layout-vs-area-estimate.py
- Prediction: Opening-deducted area under-orders in more than 25 percent of the 91 rooms; area plus 10 percent waste under-orders in under 15 percent; the 12x14 room needs 9 sheets against an estimate of 8.
- Observed: RESULT: PASS opening-deducted area estimate under-orders in 76/91 rooms (12x14 needs 9 sheets, estimate 8); area+10% waste is neither safe nor tight: under-orders in 16/91, over-orders in 54
- Scenarios: 1) cut-list layout over 91 room sizes; 2) opening-deducted area estimate; 3) BREAK: flat 10 percent waste estimate; 4) the 12x14 room case
- Link: brain train auto, scheduled run; session_01DvSHWZUgPrcaEhdbqtMZR2
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-auto-training.md#E6 · incompatible · sandboxes/2026-10-15__drywall-integer-foot-rooms-make-exact-fit-offcuts-so-a-saw-kerf-adds-sheets-far-more-often-than-random-cut-lists.py · observed RESULT: FAIL 3/4; kerf adds sheets in 26/91 integer-foot rooms vs 3/91 inch-measured; ffd>opt 0 and 0; 12x14 9->9. The one miss is my control band (3.3% against under 2%). After the first run I widened only the diagnostic line from exact-f… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 4 pass 2
