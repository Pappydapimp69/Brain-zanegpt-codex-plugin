# local/sandbox-own-four-comparisons-boundary — lessons

Project: local/sandbox-own-four-comparisons-boundary. Newest first.

---

## E1 — own four comparisons boundary
- Date: 2026-10-08
- Project: local/sandbox-own-four-comparisons-boundary
- Tags: [architecture][gamedev][input][testing]
- What: Re-verified the idea kernel own-the-four-comparisons (hit testing is four comparisons, so own it rather than trust a framework transform pipeline) in a deterministic sandbox, and pushed it until it stopped holding. It holds for the arithmetic, but owning only the comparisons is not enough.
- Why built: The kernel had no memory entry building against it. Its claim (own ~20 lines: rect registry, draw-order priority, press/release pairing, exactly one live path) touches august-10/E18 (pending list vs per-key slot) and capture-layer-starves-tutorial/E3 (where a guard sits decides whether it starves consumers), so those were exercised together.
- Design: Python stdlib, exact Fractions, no RNG. 5 device configs (zoom x devicePixelRatio) x 120x120 device pixels vs one rect; pipeline = integer rounding mid-path, owned = exact comparison. Plus overlap priority, drag-off release, same-frame press pair (list vs one slot), letterbox offset, and framework+owned handlers both live.
- Got right: Owned comparison disagreed with ground truth in 0 of 72000 probes, the rounding pipeline in 319. Draw-order registry picked front/back/none correctly. A release off the armed rect fired nothing.
- Where/why it failed: Ownership stops at the input space. With a letterbox offset (8,6) skipped, the owned four comparisons were wrong on 464 of 3600 probes. Leaving the framework handler registered and live beside the owned one fired the handler 6 times for 3 taps. A one-slot pending store lost a same-frame press the list kept (0 vs 1 fires).
- Fix: Own the device-to-logical coordinate mapping together with the comparisons, keep pending presses as a list, and make the framework's hit objects inert so exactly one path fires.
- Why this fix: The only failures found were in the seams around the arithmetic (coordinate space, duplicate path, slot capacity), not in the arithmetic, so the owned surface has to include those seams.
- Rule of thumb: Owning the four comparisons removes the pipeline's rounding faults only if you also own the coordinate mapping, keep presses in a list, and disable the framework path; otherwise you relocate the bug instead of removing it.
- Provenance (verified/assumed): Verified first-hand with the sandbox in this session; the model is a simplified 2D rect and rounding model, and real browser input paths were not exercised.
- Composed: ideas:architecture/gamedev/own-the-four-comparisons, august-10/E18, sandbox-capture-layer-starves-tutorial/E3
- Sandbox: sandboxes/2026-10-08__own-four-comparisons-boundary.py
- Prediction: Owned wrong = 0 of 72000 while the pipeline is wrong on some; I expected the coordinate-offset and dual-path scenarios to break the claim.
- Observed: RESULT: PASS owned_wrong=0 pipeline_wrong=319/72000; coord-mapping break=464; dual-path doubles fires
- Scenarios: 1) device sweep owned vs pipeline; 2) overlap priority; 3) drag-off release and same-frame pair, list vs slot; 4) BREAK: letterbox offset skipped; 5) BREAK: framework and owned handlers both live
- Link: scheduled brain train session 2026-10-08
- Audited: 2026-10-12 · modeled · Read the entry and its stored sandbox. The owned-comparison zero error is built in: ground truth is the same four-comparison function on exact Fractions and the owned path is that same computation, so owned_wrong=0 could not have come out any other way, while the pipeline's 319 errors come from a hand-written rounding step chosen to produce them. The letterbox scenario counts mismatches between an offset and an unoffset call of one function, which assumes the offset exists, and the double-fire scenario is true by construction at zoom 1 (the check compares fires to twice the owned fires). The draw-order priority and press-list against one-slot scenarios do exercise real logic. The rule is about real framework and browser input pipelines, and only a hand-written 2D rounding model was tested, so the verdict is modeled, not pass. · scheduled brain train session audit pass 3 loop 2; session_01F6s6QCyGv375z4gR2Gg7J5
