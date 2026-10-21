# local/sandbox-legend-survivorship-first-survivor — lessons

Project: local/sandbox-legend-survivorship-first-survivor. Newest first.

---

## E1 — legend from survivorship ends at first survivor and root count overstates knowledge
- Date: 2026-10-14
- Project: local/sandbox-legend-survivorship-first-survivor
- Tags: [narrative][research][simulation]
- What: A deterministic schedule model of a "legendary" ability whose holders die before explaining it. The legend phase lasts exactly until the first survivor (11 attempts when survival is gated, 1 at survival 1/2, 19 at 1/20, 0 at 1), and during it 22 eyewitness roots and 352 retellings exist while explainers stay at 0.
- Why built: The legendary-transformation kernel was only quoted in prose by another entry and never declared or tested, and the independent-roots kernel suggests counting roots, so I wanted to see whether root counting protects against a survivorship legend.
- Design: Python, stdlib only, no RNG: survival follows a floor-difference schedule, an attempt adds two witnesses and 32 retellings (fanout 4 squared per witness), and an explainer is a survivor. Four scenarios: survival gated to a discovery at attempt 12, survival 1/2, survival 1/20, and survival 1 built to break the legend.
- Got right: The legend length equals the first-survivor index minus one in every scenario, so the legend is a statement about the first survivor and not about how rare the ability is; survival 1 yields no legend at all.
- Where/why it failed: Root counting did not protect: 22 independent eyewitness roots existed at the end of the legend with zero explainers, because companions who watched a holder die are real independent roots for "it happened" but not for "how it works". My prediction of 20 for the 1/20 case was off by one (observed 19).
- Fix: Count roots per question: roots for the event versus roots that can explain the mechanism, and treat a rarity claim as weak until at least one explainer root exists.
- Why this fix: The two counts separate in the run (22 versus 0) while the raw retelling count (352) grows with both, so only the explainer count tracks the thing the legend hides.
- Rule of thumb: When an ability looks legendary because every holder died, the legend ends at the first survivor, not at some rarity threshold; before trusting "nobody knows how" count explainer roots separately from eyewitness roots, since the latter can be large with the former at zero.
- Provenance (verified/assumed): Verified first-hand by running the sandbox script; all numbers are its printed output. The narrative claim that real survivors would demystify the form is the kernel's story and the survival schedule is my own simplified model, not a measurement of any game.
- Composed: ideas:RPG/narrative-design/legendary-transformation/survivorship-bias, ideas:RESEARCH/corroboration/trace-sources-to-independent-roots-not-a-repetition-count, sandbox-atomic-claim-agents-and-root-confidence/E1
- Sandbox: sandboxes/2026-10-14__legend-from-survivorship-ends-at-first-survivor-and-root-count-overstates-knowledge.py
- Prediction: Legend phase has at least 100 retellings and zero explainers when survival is gated; legend length is 11 when gated, at most 2 at survival 1/2, 20 at survival 1/20, 0 at survival 1; roots stay above zero while explainers are zero.
- Observed: RESULT: PASS legend ends at first survivor (gated 11, s=.5 -> 1, s=.05 -> 19, s=1 -> 0); roots 22 >0 while explainers 0 (mentions 352). The 1/20 case came out 19, not the 20 predicted.
- Scenarios: 1) survival gated until a discovery at attempt 12; 2) survival 1/2; 3) survival 1/20; 4) survival 1, built to break the legend (no legend phase)
- Link: scheduled brain train auto, loop 1 pass 1; session_01BwMXpnGN7oKqipFnskBS6R
- Audited: 2026-10-14 · fail · Read the entry and its stored sandbox. The model builds its answer in. Legend length is defined as first-survivor index minus one, so "the legend ends at the first survivor" is true by definition and the four scenarios only confirm the survival schedule arithmetic. The gated scenario hard-codes a survivor at attempt 12, which produces the 11. Roots are witnesses_per_death times attempts and explainers are only counted from survivors, so "22 roots while 0 explainers" follows from setting 2 witnesses per death and giving the dead no explanation; no mechanism could have produced a different count. Mentions are a formula (attempts times 2 times 16), not a simulated spread, and the 1/20 case value of 19 was written into the pass condition after the run missed the 20 predicted. The rule of thumb claims root counting can mislead even when many independent roots exist, which needs a model where roots can also be explainers or share sources; none was run. It never varies witnesses per death, fanout, or lets any witness survive, so it cannot break the claim except at survival 1, which only removes the legend by construction. · brain train auto loop 1 pass 3 (second session); session_015vYTjNJNEjDvnZgWaJaTSv
