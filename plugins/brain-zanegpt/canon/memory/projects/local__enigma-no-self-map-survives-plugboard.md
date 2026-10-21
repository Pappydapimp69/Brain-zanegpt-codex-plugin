# local/enigma-no-self-map-survives-plugboard — lessons

Project: local/enigma-no-self-map-survives-plugboard. Newest first.

---

## E1 — enigma no self map survives plugboard
- Date: 2026-10-15
- Project: local/enigma-no-self-map-survives-plugboard
- Tags: [rotor-machines][cryptography][sandbox][testing]
- What: Enigma's never-encrypt-a-letter-to-itself property, shown in the kernel without a plugboard,
  survives a 10-pair plugboard (0 self-maps in 20,000 key presses, exact round trip), and it
  lets a codebreaker rule out where a known crib can sit: 33% of offsets for a 10-letter crib,
  55% for 20, 73% for 33, matching 1 - (25/26)^L.
- Why built: Weakest-link train pick: the rotor-machine kernel left out the plugboard used in service and
  did not measure the practical cost of its no-self-map flaw, which is the property Bletchley
  Park used to place cribs.
- Design: Enigma I with rotors I, II, III, reflector B, middle-rotor double step; check vector AAAAA
  at AAA; 10 plugboard pairs, start QEV, 20,000 LCG plaintext letters. Counted self-maps and
  decrypted the ciphertext; slid known fragments of length 10, 20 and 33 over 19,000 offsets
  and counted offsets where some crib letter equals the ciphertext letter under it.
- Got right: The kernel's vector reproduced (BDZGO) and the reflector argument extends to the plugboard:
  wrapping an involution in another involution (plugboard on both sides) keeps a fixed-point-
  free involution, so the machine still never maps a letter to itself.
- Where/why it failed: Nothing failed; the elimination rate tracked the independence estimate within 0.3 points
  (32.7/54.7/72.7% vs 32.4/54.4/72.6%), and the true crib offset always survived, so the
  filter never discards the right answer.
- Fix: When assessing a cipher, treat 'never maps to itself' as a leak, not a curiosity: a
  20-letter crib alone rules out over half of all placements; any cipher component that
  forbids fixed points gives an attacker this filter.
- Why this fix: Each crib letter has a 1/26 chance of matching the ciphertext letter under a wrong
  placement, and one match is enough to rule it out, so elimination grows as 1 - (25/26)^L
  with crib length, at no cost to the attacker.
- Rule of thumb: Enigma's no-self-map property survives the plugboard and leaks crib position: offsets ruled
  out = 1 - (25/26)^L (33% at 10 letters, 55% at 20, 73% at 33).
- Provenance (verified/assumed): Verified first-hand by the sandbox below; rotor and reflector wirings are the standard
  published tables as I know them, confirmed by reproducing the kernel's check vector BDZGO.
- Composed: ideas:ROTOR-MACHINES/enigma
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__enigma-no-self-map-survives-plugboard.py
- Prediction: Written before running: vector BDZGO; with 10 plugboard pairs 0 self-maps over 20,000
  presses and exact round trip; crib elimination within 5 points of 1 - (25/26)^L (about 54%
  at 20, 73% at 33).
- Observed: RESULT: PASS vector BDZGO; with plugboard 0 self-maps (0), round trip True; crib elimination
  L10 33%, L20 55%, L33 73% vs theory 32%/54%/73%; true offset survived at every length.
- Scenarios: 1) check vector without plugboard; 2) 20,000 presses with 10 plugboard pairs, built to break
  the no-self-map claim; 3) crib sliding at lengths 10, 20, 33.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

