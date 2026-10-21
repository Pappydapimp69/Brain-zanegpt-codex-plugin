# local/sandbox-blind-tag-picks-conflict-by-five-not-twelve — lessons

Project: local/sandbox-blind-tag-picks-conflict-by-five-not-twelve. Newest first.

---

## E1 — sandbox blind tag picks conflict by five not twelve
- Date: 2026-09-30
- Project: local/sandbox-blind-tag-picks-conflict-by-five-not-twelve
- Tags: [songwriting][suno-prompting][testing]
- What: Exact combinatorial count of style-tag conflicts over a 24-tag palette (6 axes of 4 values, with vocal, tempo and energy allowed only one value). Picking tags without regard to axis, half of all 5-tag sets already contain a conflict (49.4 percent) and 85.7 percent of 8-tag sets do, far earlier than the kernel's point of roughly 10 to 12 tags. On top of a 5-tag persona that already holds a value on each single-valued axis, one extra blind tag conflicts 47.4 percent of the time.
- Why built: To test where the five-to-eight kernel's contradiction point actually falls, and to re-check my earlier persona entry, which said a 5-tag persona leaves 3 free tags.
- Design: sb/music/t5_tag_conflicts.py counts non-conflicting n-subsets exactly (each single-valued axis contributes zero or one of its 4 values, the other 12 tags are free) and divides by C(24, n). The persona case removes the 5 held tags and counts subsets that avoid the other 9 values on the single axes.
- Got right: Small cases check by hand: 2 tags conflict in 18 of 276 pairs (6.5 percent). The count is exact, so no sampling error.
- Where/why it failed: The kernel's 10 to 12 threshold and my persona entry's 3 free tags both hold only if every tag is chosen on a different axis. Choosing blind, the conflict rate crosses 50 percent between 5 and 6 tags, and the persona's headroom is effectively zero for a writer who does not check axes.
- Fix: Treat the 5 to 8 band as one tag per axis, not as a count, and check each new tag against the axes already filled (including the persona's) before adding it.
- Why this fix: Conflicts come from filling a single-valued axis twice, which a raw count cannot see, and the probability rises steeply with count only when axes are ignored.
- Rule of thumb: A tag-count band hides the real limit: picked without regard to axis, half of 5-tag style prompts already conflict and a persona's spare slots vanish, so fill one axis per tag instead.
- Provenance (verified/assumed): Verified first-hand by running sb/music/t5_tag_conflicts.py; percentages are exact counts. The 24-tag palette and the choice of single-valued axes are my modelling assumptions, not Suno data.
- Composed: ideas:SONGWRITING/suno-prompting/five-to-eight-specific-style-tags-beats-a-vague-genre-word, ideas:SONGWRITING/suno-prompting/personas-lock-a-vocal-identity-across-generations, sandbox-persona-seeded-tags-shrink-the-style-band-headroom/E1
- Link: scheduled training session, music batch
- Reverified: 2026-09-30 · pass · sandboxes/2026-09-30__rebuild-blind-tag-conflict-combinatorics.py · observed RESULT: PASS 6x4 palette: 5-tag 49.4%, 8-tag 85.7%, persona+1 47.4% by enumeration; other palette (5x5, 2 single) 5-tag 47.2%, half reached at 6 tags · Own method: brute-force enumeration of every k-subset of the palette rather than the original closed-form count (read only after the run), plus a second palette of 5 axes by 5 values with 2 single-valued axes as the break attempt. Enumeration reproduces 49.4 percent at 5 tags and 85.7 percent at 8 tags, and a blind extra tag on a persona holding one value per single axis conflicts 9 of 19 = 47.4 percent (closed form in my sandbox). On the other palette, 5 tags conflict 47.2 percent and half is first reached at 6 tags (81.9 percent at 8), so the exact numbers are palette-specific but the claim that conflicts arrive around 5 to 6 tags, well before 10 to 12, holds on both. Whether real style prompts degrade on these conflicts is a Suno premise that this model does not test. · https://claude.ai/code/session_01PXuEX9SfJcr8Mxg6sK6stu
