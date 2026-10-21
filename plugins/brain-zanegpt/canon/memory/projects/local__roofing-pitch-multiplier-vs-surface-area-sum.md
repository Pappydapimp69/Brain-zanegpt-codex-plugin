# local/roofing-pitch-multiplier-vs-surface-area-sum — lessons

Project: local/roofing-pitch-multiplier-vs-surface-area-sum. Newest first.

---

## E1 — roofing pitch multiplier vs surface area sum
- Date: 2026-10-15
- Project: local/roofing-pitch-multiplier-vs-surface-area-sum
- Tags: [roofing][geometry][estimating][sandbox]
- What: Seeds a roofing domain: the pitch multiplier sqrt(1+(p/12)^2) times plan area was checked against an independent 3D surface-area sum for gable and hip roofs of a 30x40 ft house at 4/12 to 12/12, and then pushed to its failure cases.
- Why built: Roofing material is bought by sloped area but houses are drawn by plan footprint; the multiplier is the standard shortcut and the question is exactly when it stops being exact.
- Design: Vertices of each roof face in 3D, area by cross products; gable and hip compared with plan*multiplier; break cases: 1 ft eave overhang on a 6/12 gable, a 10x12 ft 3/12 shed dormer on a 6/12 roof, and square count with 10 percent waste.
- Got right: The multiplier matched the surface sum to floating-point exactness on both gable and hip at every pitch, because every face of those roofs shares one pitch and so one slope factor regardless of face shape.
- Where/why it failed: It is exact only for the plan area that is actually roofed at one pitch: using the house footprint with a 1 ft overhang came out 10.7 percent short on the 30x40 house, and one 3/12 dormer on a 6/12 roof moved the answer 0.79 percent.
- Fix: Take the plan area from the roof outline including eaves, split it by pitch zone, multiply each zone by its own multiplier, then add waste and round up to whole squares of 100 sq ft.
- Why this fix: The multiplier is a per-zone constant (secant of the slope), so it composes by summation over zones and breaks only if the plan input or the zoning is wrong.
- Rule of thumb: Sloped roof area equals roofed plan area times the pitch multiplier per pitch zone: it is exact for gable and hip, so errors come from the plan input (eaves 10.7 percent on a 30x40 house) and unmodelled pitch zones, not from the formula.
- Provenance (verified/assumed): Verified first-hand: sandbox computed independent 3D face areas and printed PASS. The 10 percent waste figure and 100 sq ft per square are common trade conventions I used as inputs and did not check against a supplier. Isolated: no adjacent kernel or lesson exists for this domain, so none is cited.
- Composed: N/A
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-15__roofing-pitch-multiplier-vs-surface-area-sum.py
- Prediction: Gable and hip match plan*multiplier to under 1e-9 at all four pitches; a 1 ft overhang makes the footprint estimate more than 5 percent short; a 3/12 dormer shifts it by more than 0.3 percent.
- Observed: RESULT: PASS pitch multiplier exact for gable and hip (err <1e-9), but footprint-only estimate is 10.7% short with a 1 ft overhang and a 3/12 dormer shifts it 0.79%
- Scenarios: 1) gable at 4/6/9/12 pitch; 2) hip at 4/6/9/12 pitch; 3) BREAK: 1 ft eave overhang on a 6/12 gable; 4) BREAK: 3/12 shed dormer on a 6/12 roof; 5) squares with waste
- Link: brain train auto, scheduled run; session_01DvSHWZUgPrcaEhdbqtMZR2
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-auto-training.md#E13 · compatible · sandboxes/2026-10-15__roof-faces-unfold-with-a-gap-at-hips-and-an-overlap-at-valleys-though-area-stays-exact.py · observed RESULT: PASS area = plan x multiplier exact at all 4 pitches, but sloped angles do not close: hip apex gap 6.03 deg at 4/12 to 38.94 at 12/12, valley junction overlap 6.03 to 38.94 deg; only the gable ridge (360, Kawasaki true) unfolds fla… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 3 pass 2
