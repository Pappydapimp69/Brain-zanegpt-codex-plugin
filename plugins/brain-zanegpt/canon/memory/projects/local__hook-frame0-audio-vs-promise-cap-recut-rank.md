# local/hook-frame0-audio-vs-promise-cap-recut-rank — lessons

Project: local/hook-frame0-audio-vs-promise-cap-recut-rank. Newest first.

---

## E1 — hook frame0 audio vs promise cap recut rank
- Date: 2026-10-17
- Project: local/hook-frame0-audio-vs-promise-cap-recut-rank
- Tags: [game-ads][film][testing][sandbox]
- What: Sandbox composing the cap-promise-at-delivery rule, the IPM-times-D1 ranking and film's frame-0 audio hit: a silent first second scales IPM down but does not change which cold-open promise wins on IPM times D1.
- Why built: The film lesson says a silent opening loses the hook, and the ad lessons say to rank recuts on IPM times D1; the open question was whether a missing hit could flip the promise pick.
- Design: Nine recut promises 0.2-1.0 against a fixed delivery of 0.5; IPM is linear in promise times a 0.4 factor when the first second is silent; D1 falls linearly once promise exceeds delivery. Three scenarios: all recuts with a frame-0 hit, all silent, only the phase-synced high-promise recuts silent.
- Got right: IPM times D1 picked promise 0.5 (equal to delivery) in 3 of 3 scenarios, because the silence penalty multiplies IPM and leaves the D1 term untouched.
- Where/why it failed: IPM alone is fragile: it picked 1.0 in the first two scenarios and 0.6 in the third, so a hook defect confined to the high-promise recuts quietly moved the IPM-only winner by 0.4 of promise.
- Fix: Rank recuts on IPM times D1, and make the frame-0 audio check a gate on every recut before the ranking runs, so a hook defect never biases only some candidates.
- Why this fix: A uniform defect cannot flip a multiplicative ranking, and a non-uniform one is only visible to the IPM-alone ranker; the gate removes the non-uniform case at its source.
- Rule of thumb: In a three-scenario toy model, a silent-hook defect moved the IPM-only recut winner from 1.0 to 0.6 but never moved the IPM times D1 winner off 0.5; scan every recut's first second for a hit before ranking on either metric.
- Provenance (verified/assumed): Verified first-hand by running the sandbox (RESULT: PASS); the silence cost of 0.6 and the overpromise slope of 1.5 are assumed toy values, not measured ad data.
- Composed: cold-open-promise-matches-delivery/E1, rank-ipm-times-d1-needs-fidelity-retention-link/E1, film/E14
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-17__hook-frame0-audio-vs-promise-cap-recut-rank.py
- Prediction: IPM times D1 keeps promise 0.5 in all 3 scenarios; IPM alone picks 1.0, 1.0 and 0.6. Assumes the silence cost is independent of delivery; scenario C was built to break that.
- Observed: RESULT: PASS IPM*D1 picked promise 0.5 in 3/3 scenarios; IPM alone picked [1.0, 1.0, 0.6]
- Scenarios: 1) all recuts have a frame-0 hit; 2) all recuts silent first second; 3) BREAK: only phase-synced recuts with promise 0.7 or more silent
- Link: brain train auto loop 1 pass 1; session_01696mc4JbaRUYgcwwnaPSG1
- Cited-by: 2026-10-17 · projects/pappydapimp69__brainwork.md#E419 · compatible · sandboxes/2026-10-17__silent-hook-on-the-matched-recut-flips-ipm-d1-unless-the-gate-reads-the-audio.py · observed RESULT: PASS IPM*D1 with no gate misses 0.5 in 2 of 6 scenarios (D; F); stale sidecar misses in 2; gate derived from the audio misses in 0 · session 2026-10-17 scheduled brain train, loop 2 pass 2; session_01KkkcHHGkp6Sm9GJK6fsa84
- Audited: 2026-10-18 · modeled · Read the entry and reran its stored sandbox (RESULT PASS, IPM alone 1.0, 1.0, 0.6 and IPM times D1 0.5 in all three). The picks are computed by max over a promise grid, not hard-coded, but the key result is nearly built in: silence is a multiplier on IPM, so when every recut is silent (scenario B) it cannot change the argmax, and in scenario C the 0.5 win follows from the hand-set linear D1 penalty of 1.5 per unit over delivery. Only scenario C genuinely tests the claim. The rule also advises scanning every recut's first second, which the model never exercises, and it concerns real ad metrics (IPM, D1) that were only modeled, so the evidence supports the toy-model shape and not the real-system claim. · scheduled brain train auto run 2026-10-18 loop 2 pass 3 (audit); session_01L27EvvVfmoxjFAREggXBWN
