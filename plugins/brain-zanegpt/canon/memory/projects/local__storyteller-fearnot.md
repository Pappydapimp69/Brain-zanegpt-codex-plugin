# local/storyteller-fearnot — lessons

Project: local/storyteller-fearnot. Newest first.

---

## E1 — fearnot stakes come from attachment not a bigger monster
- Date: 2026-10-17
- Project: local/storyteller-fearnot
- Tags: [narrative][stakes][simulation][sandbox]
- What: Modelled The StoryTeller's Fearnot as a stakes score, loss chance times what the target is worth to the hero,
  for a hero who wins every fight, and compared bigger monsters, threats to his sweetheart, and losses he cannot fight.
- Why built: Brain train on Jim Henson's The StoryTeller; canon had escalation by removing safe options and the
  multiplicative veto, but nothing on why a hero immune to danger needs attachment rather than a bigger threat.
- Design: Stdlib scene scorer: each scene has a target (hero or sweetheart), a channel (a fight he can win up to his
  strength, or a parting no strength touches) and a size; stakes = loss chance x value, a product so a zero vetoes it;
  scenarios for monsters of size 1-1000, a monster at the sweetheart with him beside her or away, and a parting.
- Got right: With full immunity every monster from size 1 to 1000 scored 0, and so did a size-1000 monster aimed at
  the sweetheart while he guarded her; a parting at chance 0.3 scored 3.0 and a size-1 monster while he was away scored 10.0,
  and a curse on her at chance 0.5 scored 5.0 even with him beside her winning the fight.
- Where/why it failed: The claim holds only for total immunity: the BREAK hero who wins fights only up to size 100 faced a
  size-1000 monster at 9.0, above the attachment's 3.0, so a bigger monster works again once immunity has a ceiling;
  and with no attachment (sweetheart worth 0) nothing gave stakes at all. The away scenario was added after the first run and the
  curse-while-guarded scenario after the first check.
- Fix: For a hero who cannot lose a fight, raise stakes through someone he values and a loss channel his strength
  cannot reach (her leaving, his absence, time), not through a larger opponent or a threat he is standing next to.
- Why this fix: Stakes multiply loss chance by value, so a zero loss chance from immunity vetoes any threat size, and
  only a channel outside his immunity puts a nonzero chance next to a nonzero value.
- Rule of thumb: When the hero cannot lose a fight, stop escalating the monster; give him someone to lose and a way to
  lose them that fighting does not fix. If his immunity has a ceiling, escalation works again past it.
- Provenance (verified/assumed): Verified first-hand by the sandbox; the episode details checked against Wikipedia's
  Storyteller article and the Grimm KHM 4 tale page cited in the kernel. Values and sizes are toy numbers.
- Composed: ideas:NPC-SIM/decision-making/multiplicative-combination-preserves-vetoes, ideas:RPG/level-design/foreshadow-then-common
- Sandbox: sandboxes/2026-10-17__fearnot-stakes-come-from-attachment-not-a-bigger-monster.py
- Prediction: Immune hero: stakes 0 for monsters of size 1-1000 and for a monster at the sweetheart while he is beside
  her; a parting at chance 0.3 gives 3.0; capped immunity (100) vs size 1000 gives 9.0; no attachment gives 0 everywhere.
- Observed: RESULT: PASS immune hero 0.0 for every monster size and for the guarded sweetheart; parting 3.0, smallest monster
  while he is away 10.0, a curse on her while he guards her and wins the fight 5.0; immunity capped at 100 gives 9.0
  against size 1000; no attachment gives 0 everywhere.
- Scenarios: 1) monsters of size 1-1000 at the hero; 2) size-1000 monster at the sweetheart, hero beside her; 3) parting he
  cannot fight; 4) size-1 monster at the sweetheart while he is away; 5) curse on her while he guards her; 6) BREAK: immunity
  capped at 100; 7) BREAK: no attachment
- ZaneGPT verdict: weak — the PASS only shows the multiplication does what the author coded it to do, and the claim about reader stakes and the channel labels were never tested against anything outside the model.
- Hidden assumption: Stakes are a product of loss chance and value, and the only sources of loss chance are a fight he can lose or a parting. The rule therefore treats "someone to lose" as the fix. It never tests whether the reader feels that stake, and the scorer only returns 0 or nonzero from numbers the author set by hand.
- Would prove it wrong: A scene where the immune hero has a sweetheart and a parting at chance 0.3 scores 3.0 but reads as flat. That would happen if the parting is arbitrary, avoidable, or never felt, or if the same scene reads tense with chance 0 because of dread or moral cost. A 0.3 chance times a value that was never set against an actual reader would show the number says nothing about tension.
- Break scenario: A "curse on her while he guards her and wins the fight" scored 5.0. Compare it with the same curse where he can simply break it by winning, which the model files under a fight he can win and so should score 0. The two cases split on who set the channel label, not on anything in the story. Relabel the curse as a fight and the stakes drop from 5.0 to 0.0, and the score has not changed what the story contains.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest 64ccd5ad9ec3
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

