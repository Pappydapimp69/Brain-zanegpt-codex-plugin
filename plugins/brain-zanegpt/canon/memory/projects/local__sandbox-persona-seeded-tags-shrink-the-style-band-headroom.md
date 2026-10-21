# local/sandbox-persona-seeded-tags-shrink-the-style-band-headroom — lessons

Project: local/sandbox-persona-seeded-tags-shrink-the-style-band-headroom. Newest first.

---

## E1 — sandbox persona seeded tags shrink the style band headroom
- Date: 2026-09-30
- Project: local/sandbox-persona-seeded-tags-shrink-the-style-band-headroom
- Tags: [songwriting][suno-prompting][testing]
- What: Deterministic model composing two Suno-prompting kernels: a Persona auto-populates the Style field, and effective style prompts hold roughly 5 to 8 tags before extra tags start contradicting each other. The model counts tags and opposing-value conflicts as a writer adds tags on top of a persona.
- Why built: To see whether the persona kernel and the tag-band kernel interact, since a persona spends part of the band before the writer types anything, and whether the Exclude field relieves it.
- Design: A 5-tag persona (dream-pop, airy female, mellow, slow, strings), then 0 to 7 user tags in a fixed order. Conflicts count opposing values on tempo, vocal and energy. The Exclude variant removes only the persona tags that a user tag opposes.
- Got right: Headroom before leaving the 8-tag band is 3 user tags. Total tags exceed the band at user +4 (9 tags, 2 conflicts) and reach 12 with 3 conflicts at user +7. Excluding the clashed persona tags leaves 0 conflicts at every step and keeps totals at 7 to 9, staying near the band edge.
- Where/why it failed: This is my own model of two documented claims. Suno's real behavior on persona-plus-tags and on the Exclude field was not run here, and the conflict axes and persona contents are my choices, so only the arithmetic of the composition is confirmed.
- Fix: When a persona is applied, count its auto-populated tags against the band and show the remaining headroom; let the writer drop a clashing persona tag rather than add an opposing one.
- Why this fix: The band is shared between the persona and the writer, and removing the clashing tag reduces conflicts without spending more of the band.
- Rule of thumb: A persona pre-spends the 5 to 8 style-tag band, so a 5-tag persona leaves 3 free tags; remove a clashing persona tag instead of adding an opposite one.
- Provenance (verified/assumed): Verified first-hand by running sb/s2.py; the counts above are the model output. The Suno-side behavior comes from the two kernels only.
- Composed: ideas:SONGWRITING/suno-prompting/personas-lock-a-vocal-identity-across-generations, ideas:SONGWRITING/suno-prompting/five-to-eight-specific-style-tags-beats-a-vague-genre-word, ideas:SONGWRITING/suno-prompting/exclude-field-is-first-class-negative-prompting
- Link: scheduled training session, Suno-only pair batch
- Reverified: 2026-09-30 · fail · sandboxes/2026-09-30__rebuild-persona-tag-headroom.py · observed RESULT: PASS 5-tag persona leaves 3 free at band top (0 at band bottom); adding an opposite mood gives 9 tags/1 conflict, replacing gives 8 tags/0 conflicts · Own fixture: a persona of breathy female, melancholic, slow, indie folk and acoustic guitar, four wanted user tags, and conflicts counted on mood, tempo and vocal; the original used a dream-pop persona, conflicts on tempo, vocal and energy, and added 0 to 7 tags (read only after the run). The arithmetic reproduces: 3 free tags at the band top (0 at the band bottom of 5), adding an opposite mood gives 9 tags and 1 conflict, and replacing the clashing persona tag gives 8 tags and 0 conflicts. But the load-bearing claim is Suno behaviour: that a Persona's auto-filled Style tags count against the same 5 to 8 tag band a writer's tags use, and that tags past 8 degrade output. A local model can only assume that premise; it would need the real Suno service to test. The rule should also say headroom is 0 to 3, not 3, since the band is a range. The verdict is fail because the claim cannot be verified without the external system. · https://claude.ai/code/session_01PXuEX9SfJcr8Mxg6sK6stu
- Cited-by: 2026-09-30 · projects/local__sandbox-blind-tag-picks-conflict-by-five-not-twelve.md#E1 · compatible · no sandbox · scheduled training session, music batch
- Cited-by: 2026-09-30 · projects/local__sandbox-persona-consistency-compounds-over-an-album.md#E1 · compatible · no sandbox · scheduled training session, music batch
