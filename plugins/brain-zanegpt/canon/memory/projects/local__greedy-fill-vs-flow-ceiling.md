# local/greedy-fill-vs-flow-ceiling — lessons

Project: local/greedy-fill-vs-flow-ceiling. Newest first.

---

## E1 — greedy engine first fill misses the flow ceiling when engines are trope limited
- Date: 2026-10-16
- Project: local/greedy-fill-vs-flow-ceiling
- Tags: [comedy][game-ads][testing][sandbox]
- What: A greedy engine-first fill (each engine takes its first allowed trope under the cap) matched the max-flow batch ceiling of min(16, 6R) at trope caps 1 and 2 and with open engines, but at cap 3 with each engine limited to 2 tropes it made 15 videos against an optimum of 16.
- Why built: New-half train pick joining the engine-first batch lesson, the fake-ad kernel source check and the batch-ceiling trope cap, to see whether the ceiling is reachable by the simple assignment a person would actually use, not only by the max-flow model.
- Design: Deterministic script, 8 engines with 2 skeleton slots each, 6 tropes, cap R of 1, 2 or 3, and each engine allowed a window of w consecutive tropes (1, 2 or 6). Greedy takes engines in order and the first allowed trope under cap; the optimum is an augmenting-path matching.
- Got right: At R=1 and R=2 greedy hit 6 and 12 for every window, and with open engines it hit the ceiling at every cap, so the ceiling formula is reachable by a plain fill whenever the cap is the binding limit.
- Where/why it failed: I expected greedy to lag the optimum by two or more videos somewhere; the largest gap was one (15 against 16 at R=3, w=2), and at w=1 both gave 14 because the engines themselves bind, below the 16 ceiling.
- Fix: Use the plain greedy fill only for batches at or below 12 or with open engines; when each engine is limited to a few tropes and the cap is 3, run the matching check, and widen engine windows before raising the cap.
- Why this fix: The shortfall appears only when the trope cap, slots and engine windows are all near their limits at once, so a cheap matching check there costs little and a blanket matching step elsewhere buys nothing.
- Rule of thumb: A greedy engine-first fill reaches the min(16, 6R) batch ceiling at caps 1 and 2 for windows of 1, 2 or 6 tropes, but at cap 3 with 2-trope engines it makes 15 of 16 and with 1-trope engines 14, so check by matching there.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the 8 engines, 2 skeletons, 6 tropes and the ceiling formula come from the named lessons, and the engine windows are my own assumption.
- Composed: engine-first-idea-batches/E1, fake-ad-kernel-source-check/E1, batch-ceiling-trope-cap/E1
- Picked-by: new-half
- Distinct from: batch-ceiling-trope-cap/E1 (that lesson computes the ceiling by max-flow; this finds that a plain greedy fill falls 1 short of it at cap 3 with 2-trope engines).
- Sandbox: sandboxes/2026-10-16__greedy-engine-first-fill-misses-the-flow-ceiling-when-engines-are-trope-limited.py
- Prediction: Hidden assumption: the ceiling can be reached by simple sequential assignment. Expected greedy to trail the optimum by 2 or more at some window; it would be wrong if greedy matched the optimum everywhere.
- Observed: RESULT: PASS open engines greedy=optimum=ceiling True; max greedy shortfall 1 at (3, 2); w=1 R=3 greedy 14 optimum 14 (the shortfall-of-2 expectation was refuted)
- Scenarios: 1) open engines at caps 1, 2, 3; 2) 2-trope engine windows; 3) 1-trope windows, built to break the ceiling at cap 3.
- Link: scheduled brain train auto loop 1 pass 2 (edge); session_01GYKQrKfm5FQsrnyu59GmiS

