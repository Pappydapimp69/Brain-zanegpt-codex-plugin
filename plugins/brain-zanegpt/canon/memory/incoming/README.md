# incoming/ — propose a lesson here (the intake gate)

Repo access is **not** the right to write canon. Do **not** edit
`projects/*.md` or `PITFALLS.md` yourself — those are curated.

To contribute a lesson:

1. Copy `incoming/TEMPLATE.md` to `incoming/YYYY-MM-DD__<slug>.md`
   (e.g. `incoming/2026-06-14__ssml-break-tags.md`). Lowercase slug.
2. Fill it in completely — the full entry schema **plus** the proposed index
   line. Mark what is verified vs assumed. If the lesson came from stress-testing
   several existing lessons together, list them in the optional `Composed:` field
   (`<slug>/E<n>` refs) — that is the edge `brain analyze graph` reads to map
   which systems are co-verified together.
3. Add **only** that one file. Touch nothing else.
4. Open it for a steward. The steward validates, judges, and promotes it into
   the right project file + `PITFALLS.md`, then deletes your drop.

Run `python3 scripts/validate.py` before submitting — it checks your proposal is
schema-complete and that canon stays consistent. CI runs the same check.

Only propose when you (a) found and fixed a *real* bug, or (b) made a
non-obvious design decision with a real tradeoff. No routine changes, features,
or refactors. No secrets, tokens, credentials, or PII.
