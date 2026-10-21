# local/storyteller-luck-child-letter — lessons

Project: local/storyteller-luck-child-letter. Newest first.

---

## E1 — luck child letter never route an order through its subject
- Date: 2026-10-17
- Project: local/storyteller-luck-child-letter
- Tags: [narrative][security][simulation][sandbox]
- What: Modelled the king's letter in The Luck Child, an order to kill the boy that the boy himself carries and that
  robbers (a forging Little Man in the episode) rewrite on the road into a marriage order, as tamper outcomes
  for a subject carrier, a neutral courier, and a tamper-evident seal over every 3-stop route.
- Why built: Brain train on Jim Henson's The StoryTeller; canon had signing payloads and forgery-resistant algorithm
  choice, but nothing on how the choice of carrier, separate from the seal, decides whether an order is tampered.
- Design: Stdlib, no randomness: every route of 3 stops over stop types (empty, inn, kind robbers who rewrite an order
  harming someone in front of them, forgers who can also fake the seal, allies who know the subject by name).
  Carrier: subject who reads, subject who never reads, neutral courier; seal on or off; tamperers rational
  (act only if they beat the seal) or naive. Outcome: silent rewrite, detected, intact.
- Got right: In the base world (64 routes) the subject who never reads got 56/64 silent rewrites unsealed and 64/64 if
  he reads it himself; a neutral courier got 0/64. A seal cut the subject case only to 37/64, the routes with
  a forger; with naive tamperers it split 28 silent, 28 detected, 8 intact.
- Where/why it failed: Run 1 matched every prediction, partly by construction, since kind robbers act only when the subject
  stands in front of them. BREAK: with an ally who knows the subject by name, a neutral courier was rewritten
  37/64 unsealed, which only the seal stopped (0/64); added before run 2, an ally who can also forge beat
  neutral courier plus seal 37/64, the same as the sealed subject, so carrier choice stops mattering when
  the only seal-beaters act by name. The neutral courier's 0/64 rests on the modelled rule that pity needs
  the subject present. With no forger anywhere, the seal alone took the subject case to 0/27.
- Fix: Never hand an order to the party it is about; send it by a courier with no stake and seal it, and keep the
  seal's forgery cost above what anyone who knows the subject by name can pay.
- Why this fix: The subject brings both the motive and the sympathy along the route, so swapping the carrier removes
  every tamperer whose motive needs the subject present; the seal is the separate layer for those who act by
  name, and only an ally who can also forge gets past both.
- Rule of thumb: Never route a sealed order through the party it is about: the subject carries his own motive and the
  sympathy of everyone he meets, so a neutral courier stops tampering that needs him present, a seal stops
  only those who cannot forge it, and neither helps against someone who knows him by name and can forge.
- Provenance (verified/assumed): Verified first-hand by the sandbox; the episode details checked against Wikipedia's
  Storyteller article and the tale against Wikipedia's KHM 29 article and the Grimm text on grimmstories.com.
  Stop types, route length and tamperer rules are toy values.
- Composed: ideas:SYSTEM/security/cheap-to-compute-and-hard-to-forge-are-opposite-requirements, ideas:SYSTEM/architecture/trust-by-source-not-by-value-type
- Sandbox: sandboxes/2026-10-17__luck-child-letter-never-route-an-order-through-its-subject.py
- Prediction: Base world: subject reads, unsealed 64/64; subject never reads, unsealed 56/64; neutral 0/64; either
  subject sealed 37/64, detected 0; neutral sealed 0/64; naive and sealed 28 silent, 28 detected, 8 intact.
  No-forger world: 19/27 unsealed, 0/27 sealed, neutral 0/27. Ally world: neutral 37/64 unsealed, 0/64 sealed,
  subject 56/64. Empty routes: 0/8 and 8/8 if he reads. Added before run 2: forging ally, neutral sealed 37/64.
  Added before run 3: forging ally, sealed subject also 37/64.
- Observed: RESULT: PASS subject carrier gets 56/64 silent rewrites unsealed (64/64 if he reads), neutral courier 0/64;
  a seal cuts the subject case only to 37/64 while forgers exist (naive tamperers: 28 silent, 28 detected);
  BREAK: an ally who knows the name rewrites 37/64 for a neutral courier, which only the seal stops; an ally
  who can also forge beats neutral courier plus seal 37/64, the same as the sealed subject 37/64
- Scenarios: 1) base world, three carriers, seal on or off; 2) naive tamperers with a seal; 3) no forger on any route;
  4) BREAK: an ally who acts by name; 5) routes with no readers; 6) BREAK: an ally who can also forge,
  neutral and subject carriers sealed
- ZaneGPT verdict: weak — the result follows from how the stop types were defined (kind robbers only act on a visible victim, and allies only on a name), the "neutral" courier is an assumption the sim doesn't test, and the headline 37/64 tie between sealed neutral and sealed subject in the forging-ally world undercuts the rule's own claim; the next move is to make tamperer behavior depend on the order's contents rather than the carrier's identity, and re-run.
- Hidden assumption: The rule treats the subject and a neutral courier as the only carrier options, and assumes that tampering which needs the subject present (kind robbers) is the main threat. The simulation stipulates that kind robbers act only on harm "in front of them", so the courier's immunity is built into the stop definitions and isn't an empirical finding. The rule also never prices the courier's own costs: a neutral courier cannot be assumed to exist, to be trusted, or to be free of any motive.
- Would prove it wrong: A run where the neutral courier, sealed, does worse than the sealed subject. For example, tamperers who act on the order's text alone, or couriers who can be bribed or can read. Neutral sealed would then exceed 37/64. Or a run where the sealed subject drops below the sealed neutral courier because the seal-capable parties are fewer on his route. Either would show the carrier choice isn't what drives the outcome.
- Break scenario: Keep the forging-ally world but add "informant" stops that tell a robber who the courier works for, or let robbers read the letter's addressee. Then a neutral courier is no longer anonymous and the neutral-sealed rate rises toward the subject's 37/64. Alternatively, sweep the forger fraction: if forgers appear on most routes, sealed and unsealed collapse to the same number for every carrier, and the rule's "never route through the subject" advice has no effect.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest d544cbe946e3
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

