# local/warden-fables — lessons

Project: warden-fables — blank-verse fables converted to ElevenLabs SSML for
audio rendering, with line-end and stanza pauses. Newest first.

---

## E1 — `<br/>` is a silent no-op in SSML
- Tags: [ssml][elevenlabs][text-processing]
- Date: 2026-06-14
- What: The blank-verse SSML file (`the_wardens_story_verse_ssml.txt`), where each verse line carries
  a trailing pause tag.
- Why built: ElevenLabs needs explicit `<break>` tags to reproduce verse lineation as audible pauses;
  punctuation alone would not preserve the line rhythm.
- Design: Append `<break time="0.3s"/>` to each line end, with longer breaks at stanza and section
  boundaries.
- Got right: The per-line break approach and the graduated timing (short at line, longer at stanza,
  longest at the three closing questions).
- Where/why it failed: While drafting, several enjambed lines received `<br/>` instead of a break tag —
  an HTML reflex leaking into an SSML file. ElevenLabs does not honor `<br/>`, so those line boundaries
  would have rendered with no pause. The error was invisible when reading the text as prose; it existed
  only at the tag level.
- Fix: `sed -i 's/<br\/>/<break time="0.3s"\/>/g'` across the file, then `grep` to confirm zero `<br/>`
  remained.
- Why this fix: It normalized every line boundary to the single pause primitive the engine reads, making
  the markup uniform rather than relying on spotting each stray tag by eye.
- Rule of thumb: In SSML, `<break>` is the only pause primitive; treat any `<br/>` as a silent failure
  and grep for it before shipping.
- Provenance (not verified): the file was never run through ElevenLabs, so the fix and the break timings
  are unverified against actual audio output.
- Link: session 2026-06-14; not committed to a repo.
- Cited-by: 2026-10-14 · projects/pappydapimp69__brainwork.md#E256 · compatible · sandboxes/2026-10-14__wpm-estimate-filters-but-duration-cannot-see-a-dropped-emphasis-tag.py · observed RESULT: PASS missed_plain=2 missed_padded=0 err_range=(-0.21,0.20) break_drop_caught=6/6 emph_drop_caught_by_duration_5pct=0/3 at_2pct=3/3 by_tag_check=3/3 · brain train auto loop 2 pass 5; session_015vYTjNJNEjDvnZgWaJaTSv
