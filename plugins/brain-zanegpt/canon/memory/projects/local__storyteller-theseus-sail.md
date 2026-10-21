# local/storyteller-theseus-sail — lessons

Project: local/storyteller-theseus-sail. Newest first.

---

## E1 — theseus forgotten sail default state
- Date: 2026-10-17
- Project: local/storyteller-theseus-sail
- Tags: [narrative][signals][simulation][sandbox]
- What: Modelled the forgotten sail from Theseus and the Minotaur as a signal design problem: 100 voyages,
  70 succeed and 30 fail, 20% of needed sail changes forgotten, comparing a black-by-default sail, a
  white-by-default sail and a three-state signal where no sail means no news yet.
- Why built: Brain train on Jim Henson's The StoryTeller; canon had error-detection and alt-text kernels about
  silent defaults but nothing on choosing which meaning a signal shows when its update is forgotten.
- Design: Stdlib integer counts, no randomness; each design maps forgotten or impossible updates to false bad
  news, false good news or no news, each with a scenario cost; scenarios vary who can act on failure,
  swap the two false-news costs, make waiting as bad as bad news, and remove forgetting on success.
- Got right: With an irreversible false bad news the Theseus design cost 1400 against 120 for white-by-default and
  20 for three-state; swapping the costs made black-by-default win 280 to 3000; when the receiver could
  not wait the three-state design was worst at 2000.
- Where/why it failed: The per-voyage shortcut "put the default on the cheaper false reading" picked the wrong design once
  success updates were never forgotten (black-by-default 0 against 600), so the shortcut needed weighting
  by how often each default is left standing; that check was added after the first run.
- Fix: Choose the default by multiplying how often it is left standing on the wrong branch (forgotten
  updates, or senders the failure itself disables) by what a false reading costs, and give no news its own
  state only when the receiver can afford to wait.
- Why this fix: A forgotten update always delivers the default's meaning, so the default carries the whole cost of
  forgetting; the right default depends on both who forgets and what a wrong reading costs.
- Rule of thumb: Before agreeing a signal, ask what it says if nobody touches it: put the default on the meaning
  whose false reading is cheapest times how often it will be left up, and add a no-news state if waiting is cheap.
- Provenance (verified/assumed): Verified first-hand by the sandbox; the tale details checked against
  Wikipedia's Storyteller article, Wikipedia's Aegeus article and Plutarch's Theseus 17 and 22.
  Costs, counts and the 20% forget rate are toy values.
- Composed: ideas:ERROR-CORRECTION/hamming/single-error-correcting-code-miscorrects-double-errors, ideas:ACCESSIBILITY/images/alt-text
- Sandbox: sandboxes/2026-10-17__theseus-forgotten-sail-default-state.py
- Prediction: Theseus design 1400, white-by-default 120, three-state 20; failure with nobody to act 1400/600/44;
  swapped costs 280/3000/44; receiver cannot wait 1400/120/2000; checklist on success 0/600/30 with the
  per-voyage shortcut picking the wrong design.
- Observed: RESULT: PASS forgotten sail: default-bad 1400 vs default-good 120 vs three-state 20; swap costs and
  default-bad wins (280 vs 3000); three-state worst (2000) when receiver cannot wait; never-forgotten success
  flips it (0 vs 600) so weigh by how often the default is left standing
- Scenarios: 1) Theseus costs; 2) failure leaves nobody to act; 3) BREAK: false-news costs swapped; 4) BREAK: receiver
  cannot wait; 5) BREAK: success updates never forgotten
- ZaneGPT verdict: weak — the rule is correct as an expected-cost identity, but 5 hand-picked scenarios whose inputs set the answer can't show it is more than arithmetic, and it has not been tested against adaptive receivers or outcome-dependent forgetting.
- Hidden assumption: Costs and forget rates are known, fixed numbers that are independent of the signal design. In the model, a forgotten update is never noticed or corrected, and the receiver reads the default literally and never learns that the default is unreliable. The rule is also a restatement of expected-cost minimisation, so it depends on those inputs being right.
- Would prove it wrong: A sweep over forget rate and false-news costs where "cheapest false reading times how often the default is left up" picks a different design than the brute-force minimum. Specifically, any case where the rule says white-by-default but the counts favour black, or where its "add no-news if waiting is cheap" clause picks three-state and a two-state design is cheaper. Scenarios 3 to 5 flip the answer only because the inputs were set to flip it, so they don't test the rule. Neither does the "checklist on success" case, which the rule handles by its own frequency clause.
- Break scenario: A receiver who learns the sender's habits. Over 100 voyages, a viewer who sees that black has been up on 30 of them and that the true fail rate is also 30 can discount the signal and wait for a second cue, so the cost of the false reading falls and the ranking of designs changes. The same happens if the forget rate depends on the outcome: people forget more when things went well, because they are relieved and less careful, and less when things went badly. Then "how often the default is left up" is correlated with the very state the default misreports. The rule's multiplication assumes those two are independent.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest b6cab98438e6
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-18 · projects/pappydapimp69__brain.md#E216 · compatible · sandboxes/2026-10-18__secded-detected-state-needs-a-third-reading-not-a-default-sail.py · observed RESULT: FAIL p .02 SEC cost 0.433 vs SECDED+wait 0.060 vs SECDED+bad 1.819; p .30 SECDED silent-flipped 0.140, SEC/SECDED+wait ratio 2.19. Core parts held (7x advantage, bad default worse); the 1.5x break failed. · scheduled brain train session_01YL3uJX45U8L4Nh9fQf5qoD
