# local/sandbox-csv — lessons

Project: local/sandbox-csv. Newest first.

---

## E1 — naive csv quoted newline corrupts row count
- Date: 2026-07-11
- Project: local/sandbox-csv
- Tags: [parsing][text-processing][testing]
- What: A naive "split on newline, then split on comma" CSV parser doesn't just mis-parse a single field when a quoted value contains the delimiter — a quoted NEWLINE silently splits one logical record into two separate rows, corrupting the row count.
- Why built: Sandbox to mine a genuinely new domain (delimited-text parsing) not yet covered in this repo.
- Design: First attempt (`parse_naive`) split the whole text on `\n` then each line on `,` — the obvious, natural first implementation. Second attempt (`parse_quoted`) is a real character-by-character state machine tracking an `in_quotes` flag, handling `""` as an escaped literal quote per RFC 4180.
- Got right: Testing against 4 real edge cases up front (quoted comma, quoted newline, escaped double-quote, trailing empty field) rather than just the happy path, before trusting either implementation.
- Where/why it failed: Ran both parsers against all 4 cases and compared to hand-verified expected output. The naive parser failed all 3 quoting cases, but NOT equally badly: a quoted comma (`a,"b,c",d`) mis-parses into 4 fields instead of 3 — visibly wrong, easy to catch. A quoted NEWLINE (`a,"line1\nline2",c`) is worse: it silently turns ONE row into TWO (`[['a', '"line1'], ['line2"', 'c']]`) — this doesn't just corrupt a field value, it corrupts the RECORD COUNT, which is far more dangerous for any downstream code that indexes rows by position or asserts a row count, since the corruption doesn't look like garbage — it looks like two shorter, plausible-looking rows.
- Fix: Character-by-character state machine tracking quote state; only split on `,`/`\n` when NOT inside a quoted field; `""` inside quotes becomes a literal `"`.
- Why this fix: Delimiter and record-boundary characters are not special when they appear inside quotes — a correct parser needs a mode flag before it can trust ANY delimiter, not a hopeful regex or a two-pass split.
- Rule of thumb: For any delimited/quoted text format, a "split on newline, then split on delimiter" implementation isn't a simplified-but-mostly-working parser — it's silently wrong on real data, and its worst failure mode (row-count corruption from a quoted newline) is more dangerous than its most obvious one (a mis-split field from a quoted delimiter), because a wrong row count doesn't look wrong.
- Provenance (verified/assumed): Verified first-hand — wrote both parsers, ran all 4 cases against both, and confirmed the exact wrong output the naive parser produces before writing the real state-machine parser and reconfirming all 4 cases now match hand-verified expected output.
- Link: this session, `sandbox-csv/csvparse.py` + `test_csv.py` (scratchpad, not committed — sandbox code discarded per convention, lesson kept)
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-skilltree-formula.md#E5 · compatible · no sandbox · session (query brain for "train seams combination 3 sandboxes 5 loops" — loop 2/5), sandbox script loop2_csv.mjs, no code change to a shipping project
