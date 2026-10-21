# local/one-faro-slip-only-disturbs-cards-below-it — lessons

Project: local/one-faro-slip-only-disturbs-cards-below-it. Newest first.

---

## E1 — one faro slip only disturbs cards below it
- Date: 2026-10-15
- Project: local/one-faro-slip-only-disturbs-cards-below-it
- Tags: [card-magic][permutation][sandbox][testing]
- What: Tested the faro kernel's unstated assumption of perfect shuffles: with exactly one
  human slip (an off-by-one cut or one double drop) the eight-faro restore still returns
  half the deck home and Elmsley's binary placement still lands the top card 81% of the time.
- Why built: Weakest-link train pick: the faro kernel and zanegpt/E11 verify the order-of-2
  cycle and Elmsley's control only for perfect faros ("perfect hand faros are assumed, not
  tested"); performers slip, so the useful question is how far one slip spreads.
- Design: Exhaustive over 52 cards: out and in faros with one slip per routine, swept over
  every shuffle in the routine and every interleave step (cuts 25/27 and 27/25, double drop
  at steps 0 to 50): 424 restore cases and 13,197 Elmsley cases, no RNG.
- Got right: Perfect faros reproduced both claims (all 52 home after 8 out-faros; Elmsley
  correct for every target), and the error turned out local: a slip only disturbs the cards
  dealt after it, so late slips are almost harmless (95% home for the last 5 steps).
- Where/why it failed: My prediction was refuted both ways: I expected one slip to scramble
  the restore (under 10% home) and break Elmsley (under 30% survive); observed 50.9% home
  and 81.1% survive. Elmsley's survival falls with depth: 93% for targets 1-12, 73% for 39-51.
- Fix: Treat a faro slip as damage to the cards below it, not to the deck: keep the cards
  that matter in the top stock, recheck only the lower half after a suspected slip, and
  prefer shallow Elmsley targets when the sequence is long.
- Why this fix: The interleave is sequential from the top, so cards already dealt before the
  slip keep their correct positions; the top card's path rarely crosses a late slip, which
  is why shallow targets survive best.
- Rule of thumb: One faro slip only disturbs the cards interleaved after it: an 8-faro
  restore keeps about half home and Elmsley lands the top card about 4 times in 5.
- Provenance (verified/assumed): verified first-hand by the exhaustive sandbox below; slip
  types are my model of hand errors (off-by-one cut, one double drop), not measured from
  real performers.
- Composed: ideas:CARD-MAGIC/faro-shuffle/restore-count-is-the-order-of-two, zanegpt/E11
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__one-faro-slip-only-disturbs-cards-below-it.py
- Prediction: Written before running: any single slip leaves under 10% of cards home after
  the 8-faro restore; Elmsley lands the top card at p in under 30% of single-slip cases.
- Observed: RESULT: FAIL one slip leaves 50.9% of cards home after the 8-faro restore;
  Elmsley survives 81.1% (by target band 93%, 86%, 79%, 73%); late double drops 95.4% home.
- Scenarios: 1) perfect faros (baseline); 2) off-by-one cut in any of the 8 shuffles;
  3) double drop at every step of every shuffle; 4) Elmsley with one slip for all 51
  targets, built to break the control.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-15 · projects/pappydapimp69__demo-disc.md#E9 · compatible · sandboxes/2026-10-15__elmsley-binary-is-also-shortest.py · observed RESULT: PASS correct and shortest at every position for n = 8, 16, 32, 52, 54; worst case back to the top 3, 4, 5, 6, 6 faros. · Demo-disc commit "Add Faro: the ad is a find-the-ace casino, the game is a perfect-shuffle puzzle"; session_011p52L2CkFXcsYRwjDu6tG9
- Audited: 2026-10-15 · pass · Read the entry and its stored sandbox. The model computes its results: faro() builds the interleave from the deck, and the 50.9% home and 81.1% Elmsley survival come from exhaustive enumeration (424 restore cases, 13,197 Elmsley cases) with perfect-faro asserts as a control; the answer is not built in, and the prediction was honestly refuted. I re-ran the slip set and found 8 of 424 slips are no-ops (late double drops after a half is exhausted give a perfect result), a small inflation of the home figure but not enough to change the rule. Scope matches the Rule of thumb, which says one slip of the two modelled kinds (off-by-one cut, one double drop); it is a pure permutation claim, not about a real browser or library, so modeled does not apply. The residual limit is that real hand errors are only the two modelled slip types. · brain train auto scheduled run, audit pass 3; session_01DvSHWZUgPrcaEhdbqtMZR2
- Reverified: 2026-10-15 · fail · sandboxes/2026-10-15__rebuild-one-faro-slip-leaves-about-half-home-and-top-card-mostly-lands.py · observed RESULT: FAIL mean home 0.75, Elmsley top-card landing 0.92 (slip position did not matter: 0.68 to 0.75 at every faro) · Rebuilt blind from the claim with my own fixture: 52 labelled cards, my own faro with an uneven cut (25/27 or 27/25, leftovers dropped last) and a double drop indexed by output position, one slip per routine at each of 8 faros; Elmsley sequences for every target 0..51 with a slip at every shuffle. The qualitative claim reproduced (a slip only disturbs part of the deck; most cards stay home; Elmsley mostly still lands the top card), but the numbers did not: my first run (sparser double-drop positions) gave 0.68 home and 0.97 landing, and the exhaustive sweep gave 0.75 home and 0.92 landing, against the entry's about half (50.9%) and 81%. Both of my figures fall outside the entry's rule of thumb and my own prediction band (home 40-60%, landing 60-90%). Differences from the original: it indexes double drops by interleave step and counts half-drain handling differently, its restore sweep is 424 slips versus my 8 x 52 grid, and its Elmsley set is 13,197 cases; mine weights slips differently. So the rule's numbers (half, 4 in 5) depend on the slip set and are not a stable property; the direction holds. Marked fail on the stated numbers; the entry should say the slip-distribution dependence. · scheduled brain train auto loop 1 pass 4 (rebuild); session_01DsRJQWba5msMYZQ3BqZXpp
