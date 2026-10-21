# local/win-only-level-test-passes-tunnelling-run — lessons

Project: local/win-only-level-test-passes-tunnelling-run. Newest first.

---

## E1 — win only level test passes a run where 12 of 40 particles tunnelled
- Date: 2026-10-15
- Project: local/win-only-level-test-passes-tunnelling-run
- Tags: [testing][physics][simulation]
- What: Composed demo-disc E1 (a particle-liquid puzzle tunnels through thin walls unless speed is capped;
  prove each level with a stepped test that plays the solution and requires a win) with brain E38 (an
  outcome-only check leaves the middle of a run unchecked), on a pour-and-wall level stepped at
  several frame rates.
- Why built: Demo-disc's fix was a completability test that requires a win; E38 says outcome-only checks are
  blind to the middle. The question was whether a win-only level test can pass a run whose physics is
  already broken.
- Design: Deterministic, no rng. 40 particles (radius 3) poured left of a 2 px wall with a push toward it; the
  wall test checks only the new position. Win means at least 70 percent of particles end in the basin.
  Fixed 1/60 steps against per-frame steps at 30, 20 and 12 fps. Recorded win, tunnelled count and
  basin count, and compared a win-only test with a trajectory invariant that no particle ever crosses
  the wall.
- Got right: Fixed 1/60 steps and 30 fps never tunnelled. At 20 fps 12 of 40 particles tunnelled through the wall
  and the level was still won (28 of 40 in the basin), so the win-only test passed a broken run while
  the trajectory invariant failed it.
- Where/why it failed: I predicted 12 fps would also tunnel and still win; it tunnelled 17 and lost (23 of 40), so the win
  test did catch the worst case. The blind spot is the middle band, where physics breaks but not
  enough to cost the win; my 70 percent threshold sets how wide that band is.
- Fix: Keep the stepped completability test but add trajectory invariants for every physical claim (no
  particle inside or past a wall, conserved count), and run it at the lowest frame rate the game
  allows, not only at 60 fps.
- Why this fix: A win threshold absorbs damage up to its margin, so a level can lose a third of its liquid to
  tunnelling and still pass; the invariant fails on the first crossing regardless of the threshold.
- Rule of thumb: A win-only level test passes broken physics inside its margin: at 20 fps 12 of 40 particles
  tunnelled and the level still won, while a 'nothing crosses a wall' invariant failed it; assert
  trajectory invariants at the lowest supported frame rate.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry on a toy level; demo-disc's real engine and levels
  were not run.
- Composed: pappydapimp69__demo-disc/E38, pappydapimp69__brain/E38
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__win-only-level-test-passes-a-run-where-12-of-40-particles-tunnelled.py
- Prediction: fixed 1/60 never tunnels; at 20 and 12 fps some particles tunnel yet the level is still won; the
  invariant flags every tunnelling run; the win test flags none of the won-with-tunnelling runs.
- Observed: RESULT: PASS 3/3; fixed 60 won=True tunnelled=0 basin=40; 30fps won=True tunnelled=0; 20fps won=True
  tunnelled=12 basin=28; 12fps won=False tunnelled=17 basin=23 (12 fps lost, refuting part of my
  prediction)
- Scenarios: 1) fixed 1/60; 2) 30 fps; 3) 20 fps (built to BREAK the win-only test: it passed a broken run); 4)
  12 fps (lost, so the win test caught it)
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 1 pass 2 (edge demo-disc + brain), 2026-10-15

