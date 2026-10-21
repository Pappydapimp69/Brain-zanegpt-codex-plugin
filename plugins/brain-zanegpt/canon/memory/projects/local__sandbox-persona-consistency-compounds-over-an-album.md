# local/sandbox-persona-consistency-compounds-over-an-album — lessons

Project: local/sandbox-persona-consistency-compounds-over-an-album. Newest first.

---

## E1 — sandbox persona consistency compounds over an album
- Date: 2026-09-30
- Project: local/sandbox-persona-consistency-compounds-over-an-album
- Tags: [songwriting][suno-prompting][testing]
- What: Exact arithmetic on the personas kernel's community-reported 90 percent per-song vocal consistency, applied to the multi-song projects the kernel says personas are for. At 90 percent, a 10-song project comes out fully consistent only 34.9 percent of the time (28.2 percent for 12 songs), with about one off-voice song expected per 10, and needs about 11.1 generations on average to get 10 good ones.
- Why built: The kernel quotes a per-song rate but recommends personas for whole projects, and a per-song rate reads much better than the project-level rate it implies.
- Design: sb/music/t10_persona_album.py computes p to the n (all consistent), n times (1 - p) (expected off-voice songs) and n / p (expected generations) with exact fractions for p = 0.8, 0.9 and 0.95 and n = 1, 3, 5, 10, 12. A second part models re-seeding the persona from the previous song versus from the first song, assuming 1 unit of drift per hop and off-voice at 3 units.
- Got right: At 90 percent a 3-song EP is fully consistent 72.9 percent of the time; at 95 percent a 12-song album reaches 54.0 percent; at 80 percent it falls to 6.9 percent.
- Where/why it failed: The drift part is my assumption, not a measured Suno behavior: under linear drift, chaining gives 7 off-voice songs of 10 while anchoring to song 1 gives 0. It shows the direction of the risk only, and the 90 percent input is itself community-reported, not measured here.
- Fix: Budget re-generations for a project (about n / p), check every song against the first song's voice rather than the previous one, and re-apply the saved persona from the original song rather than from later songs.
- Why this fix: Per-song rates compound over a project, and a single fixed reference keeps errors from accumulating hop to hop.
- Rule of thumb: A 90 percent per-song persona leaves a 10-song project fully consistent only 35 percent of the time, so budget about n/p generations and check every song against the first, not the last.
- Provenance (verified/assumed): Verified first-hand by running sb/music/t10_persona_album.py; the compounding numbers are exact given the input rate. The input rate and the drift model are assumptions, named in the failure field.
- Composed: ideas:SONGWRITING/suno-prompting/personas-lock-a-vocal-identity-across-generations, sandbox-persona-seeded-tags-shrink-the-style-band-headroom/E1
- Link: scheduled training session, music batch
- Reverified: 2026-09-30 · pass · sandboxes/2026-09-30__rebuild-persona-album-consistency.py · observed RESULT: PASS exact enumeration 10 songs 34.9%, 12 songs 28.2%, E[off-voice]=1, 10/p=11.11; drift vs first stays 0.8, vs last reaches 3.6 · Own method: exact enumeration over all 2^n good/bad outcome vectors with Fraction weights, instead of the original closed forms p^n, n(1-p) and n/p, plus a drift model where each new take lands 0.4 units from the previous song with tolerance 1.0; the original modelled 1 unit of drift per hop with off-voice at 3 units (read only after the run). Enumeration gives 34.9 percent for 10 songs, 28.2 percent for 12, exactly 1 expected off-voice song per 10, and 11.11 generations for 10 good ones. In my drift model, checking against the first song keeps every accepted take within 0.8 of it, while checking against the last lets the voice walk to 3.6. The 90 percent rate is a community report and the drift behaviour is assumed in both models, so this confirms the arithmetic and the check-against-first logic given those premises, not Suno's actual consistency. · https://claude.ai/code/session_01PXuEX9SfJcr8Mxg6sK6stu
