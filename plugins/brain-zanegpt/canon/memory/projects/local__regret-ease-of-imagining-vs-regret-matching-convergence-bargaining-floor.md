# local/regret-ease-of-imagining-vs-regret-matching-convergence-bargaining-floor — lessons

Project: local/regret-ease-of-imagining-vs-regret-matching-convergence-bargaining-floor. Newest first.

---

## E1 — regret ease of imagining vs regret matching convergence bargaining floor
- Date: 2026-10-11
- Project: local/regret-ease-of-imagining-vs-regret-matching-convergence-bargaining-floor
- Tags: [regret][model][negotiation][sandbox]
- What: A deterministic sandbox with three parts: a near-miss versus clear-miss regret model with exponential ease decay, a full-information regret-matching run on rock-paper-scissors and on Shapley's 3x3 general-sum game, and a bargaining floor where a missed deal only carries regret if a deal zone exists.
- Why built: To exercise the ease-of-imagining kernel, the regret-minimisation kernel whose convergence proof covers only two-player zero-sum, and the bargaining model entry that says the alternative sets whether a deal exists.
- Design: Felt regret is gap times exp(-0.5 times distance to the better outcome). Regret matching tracks cumulative regrets, plays positive regret proportionally, and reports the time-average strategy's distance from uniform and its exploitability at T=20000.
- Got right: Near miss beat clear miss at every equal gap, and the ranking flipped at a gap ratio of 13 (theory exp(2.5) = 12.2), so size eventually beats ease. With no deal zone the missed-deal regret was 0 at every distance. Regret matching reached 0.0049 from uniform on rock-paper-scissors (exploitability 0.0136) but stayed 0.1855 away on Shapley's game (exploitability 0.287).
- Where/why it failed: The first two parts follow from the assumed decay form and deal-zone rule, so they confirm arithmetic and a boundary, not human psychology; only the regret-matching result emerged from computation. Nothing was refuted, but the ease claim is a modelled shape, not measured data.
- Fix: Treat the ease kernel as a bounded effect with a computable crossover ratio, and treat a no-regret self-play result as convergence evidence only in two-player zero-sum games; on general-sum games check exploitability of the average profile directly.
- Why this fix: The 13x flip ratio and the 0.0049 versus 0.1855 split give concrete limits on both kernels instead of a bare direction.
- Rule of thumb: Near-miss regret beats clear-miss regret only inside a gap ratio of about exp(K times the distance difference), and regret-matching averages converge to Nash only in zero-sum play: Shapley's game sat 0.1855 from uniform at T=20000 where rock-paper-scissors sat 0.0049.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; regret-matching figures are deterministic full-information runs on two fixed games at one horizon.
- Composed: ideas:REGRET/regret-scales-with-how-EASILY, ideas:REGRET/regret-minimisation-went-superhuman, sandbox-negotiation-batna/E1
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__regret-ease-of-imagining-vs-regret-matching-convergence-bargaining-floor.py
- Prediction: Near miss beats clear miss at equal gap with a flip near gap ratio 12; regret matching within 0.01 of uniform on rock-paper-scissors and over 0.05 away on Shapley's game at T=20000; zero regret when no deal zone exists.
- Observed: RESULT: PASS ease: near>far at equal gap, flips at gap ratio 13 (theory 12.2); no deal zone => regret 0; regret matching T=20000 RPS dist 0.0049 vs Shapley dist 0.1855 (expl 0.287)
- Scenarios: 1) equal-gap near versus clear miss; 2) growing far-miss gap until the ranking flips (built to BREAK ease dominance); 3) no deal zone versus deal zone; 4) regret matching on rock-paper-scissors; 5) regret matching on Shapley's game (built to BREAK convergence).
- Link: scheduled brain train auto pass 5 gap (loop 1); session_01XnmhGgGPuzgG9LkLZW48Sm
- Audited: 2026-10-11 · fail · Read the entry and its 57-line stored sandbox and re-ran it: same RESULT line (RPS 0.0049, Shapley 0.1855, flip ratio 13). The ease and deal-zone parts are computed from the assumed decay and zone rule, which the entry admits, so they only confirm arithmetic. The regret-matching part does compute, but the Rule of thumb says regret-matching averages converge to Nash only in zero-sum play, while the sandbox tested one zero-sum game and one general-sum game (Shapley's), which supports "does not always converge in general-sum" and not "only in zero-sum". I probed it with the same algorithm on a 2x2 coordination game with payoffs 2 and 1 (general-sum): after 20000 iterations both average strategies were 0.999975 on the first action, a pure Nash equilibrium, so a general-sum game converged. The scope claim is contradicted; the 0.1855 and 0.0049 figures themselves stand. · session scheduled brain train run, loop 2 pass 3 audit; session_01QZ7D84k4ubQDti8yxsPp3D
- Cited-by: 2026-10-13 · projects/pappydapimp69__brainwork.md#E181 · compatible · sandboxes/2026-10-13__regret-matching-ease-weights-and-repair-mask-in-rps.py · observed RESULT: PASS checks all true; plain 0.0048, weights 3x 0.0061, 10x 0.0069, scale 5 0.0048, mask 0.6665 with exploitability 0.9995. · scheduled brain train session, pass 2; session_01Vd1XXerYpxYYjyMDy9FPmH
