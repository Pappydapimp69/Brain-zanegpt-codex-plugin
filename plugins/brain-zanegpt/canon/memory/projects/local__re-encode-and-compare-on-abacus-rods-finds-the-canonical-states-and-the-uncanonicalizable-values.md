# local/re-encode-and-compare-on-abacus-rods-finds-the-canonical-states-and-the-uncanonicalizable-values — lessons

Project: local/re-encode-and-compare-on-abacus-rods-finds-the-canonical-states-and-the-uncanonicalizable-values. Newest first.

---

## E1 — re encode and compare on abacus rods finds the canonical states and the uncanonicalizable values
- Date: 2026-10-19
- Project: local/re-encode-and-compare-on-abacus-rods-finds-the-canonical-states-and-the-uncanonicalizable-values
- Tags: [numeral-systems][canonical-form][simulation][method]
- What: The Roman-numeral rule of accepting a spelling only if re-encoding its value reproduces it, applied to every bead state of 1 to 3 rods on a 1+4 soroban and a 2+5 suanpan, counting states, distinct values, canonical states, values with two or more spellings and values with no canonical spelling.
- Why built: The Roman canonical-form kernel says to normalise through the value or a re-encode check before comparing spellings, and the abacus lesson says a spare-bead rod has redundant states. I wanted to know whether the same check works on rods and what it costs.
- Design: A rod state is (heaven beads, earth beads) worth 5h+e, rods are decimal places. The canonical encoder is the standard decimal one: each place digit 0 to 9, a digit of 5 or more as one heaven bead. A state is canonical when encode(value(state)) equals the state; the encoder fails for values at or above 10 to the number of rods.
- Got right: On the soroban the check is vacuous in the good sense: states, values and canonical states are equal at 1, 2 and 3 rods (10, 100, 1000) with no value spelled twice, so state equality is value equality there.
- Where/why it failed: I expected the check to reject only the redundant duplicates on a suanpan rod (16 of 18 states canonical), which was wrong: only 10 of 18 pass, because the 2+5 rod can hold digit values 10 to 15 that the decimal encoder cannot spell on one rod. At 3 rods the suanpan has 5832 states and 1666 values, only 1000 canonical states, 1392 values with two or more spellings, and 666 values with no canonical spelling at all.
- Fix: For a spare-bead rod, define the canonical rule (digits 0 to 9, carry the rest) and treat re-encode failure as two different things: a duplicate spelling of a representable value, or a value above the rods' canonical range; compare by value in both cases.
- Why this fix: The check cannot distinguish a redundant spelling from an out-of-range one, and only the value comparison is correct for both, as the Roman variants lesson also found.
- Rule of thumb: Re-encode-and-compare kept all 1000 soroban states at 3 rods but only 1000 of 5832 suanpan states, leaving 666 values with no canonical spelling, so on a spare-bead layout compare rods by value and treat the canonical form as a normaliser, not as a validity test.
- Provenance (verified/assumed): Verified first-hand by running the saved sandbox, PASS with deterministic output; the canonical rule (decimal digits 0 to 9) is my own definition, and the rods are a counting model, not a physical abacus with a stated user convention.
- Composed: roman-variants-canonical-vs-lenient/E1, abacus-rod-state-equals-value-only-for-the-one-four-soroban-the-two-five-suanpan-has-redundant-states/E1, ideas:NUMERAL-SYSTEMS/additive-subtractive/canonical-form
- Picked-by: new-half
- ZaneGPT verdict: weak — the counts are plausible and the soroban/suanpan contrast is real, but the generalisation to "spare-bead layouts" is an artifact of one encoder and 3 rods, and the failed prediction (16 vs 10 on one rod) shows the author's model of the encoder was off.
- Hidden assumption: Canonical form is defined by the decimal encoder (digit ≥5 gets one heaven bead), so "validity" quietly means "equals that encoder's output". The lesson treats that as the only reasonable canonical form, and it assumes a uniform 5h+e value for the suanpan. The result is then a fact about the chosen encoder, not about spare beads.
- Would prove it wrong: A different, equally principled encoder (for example, the one that uses the spare bead for digits 5–9 only when it's needed, or a carry-based encoder where rods hold 0–15) that gives every suanpan value a canonical state would refute "treat canonical as a normaliser, not a validity test". The same goes for a recount that doesn't give 1000 canonical, 1666 values and 666 uncovered at 3 rods. The numbers also don't fit together: 1666 values with only 1000 canonical leaves 666 uncovered, which is correct only if every canonical state has a distinct value.
- Break scenario: Rerun at 3 rods with the encoder allowed to emit the full per-rod range (0–15, with carries between rods) and check whether every one of the 1666 values then has a canonical state. If so, the 666 "no canonical spelling" come from the digit-only encoder and not from the layout. Also test 4 rods, to see whether 666 and 1000 scale the way the rule of thumb implies, since only 1–3 rods were run.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-19 · digest f36d603e9c92
- Sandbox: sandboxes/2026-10-19__re-encode-and-compare-on-abacus-rods-finds-the-canonical-states-and-the-uncanonicalizable-values.py
- Prediction: Soroban states, values and canonical states are equal at every rod count, and on one suanpan rod 16 of the 18 states are canonical, with only the 2 duplicated values (5 and 10) rejected.
- Observed: RESULT: PASS soroban states==values==canonical at 1-3 rods; suanpan 3 rods: 5832 states, 1666 values, only 1000 canonical, 1392 values with 2+ spellings, 666 values with no canonical spelling (one rod: 10 canonical of 18, my 16 was wrong)
- Scenarios: 1) soroban at 1, 2 and 3 rods; 2) suanpan at 1, 2 and 3 rods; 3) BREAK: count values that have no canonical spelling, which the Roman-style claim says should not matter
- Link: scheduled brain train auto, loop 2 pass 2; session_01Q5Z2SdcUKr5yLCVU7Ma7tK

