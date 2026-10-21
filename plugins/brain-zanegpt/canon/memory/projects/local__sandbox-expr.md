# local/sandbox-expr — lessons

Project: local/sandbox-expr. Newest first.

---

## E2 — parsefloat silently truncates malformed numbers
- Date: 2026-07-01
- Project: local/sandbox-expr
- Tags: [process][tooling]
- What: Tokenizing numbers in a small expression parser with a greedy character class — consume runs of `[0-9.]`, then `parseFloat(slice)`.
- Why built: Simplest way to lex numeric literals including decimals.
- Design: `while (/[0-9.]/.test(s[j])) j++;` then `parseFloat(s.slice(i,j))`.
- Got right: Ordinary numbers (`3`, `1.5`, `.25`) tokenized fine.
- Where/why it failed: The character class also accepts MALFORMED numbers with multiple dots (`1.2.3`), and `parseFloat` doesn't reject them — it silently parses the valid prefix and stops (`parseFloat("1.2.3") === 1.2`). So `1.2.3` evaluated to `1.2` with no error. A silent-wrong result — the worst failure mode, because it looks like it worked.
- Fix: Validate the number token's shape rather than trusting the parser: either match a strict numeric pattern (`/^\d*\.\d+|\d+\.?\d*$/`, reject >1 dot) at lex time, or convert with `Number(slice)` (which returns `NaN` for `"1.2.3"`, so you can throw) instead of `parseFloat` (which truncates). Prefer the tool that REJECTS malformed input over the one that salvages a prefix.
- Why this fix: `parseFloat` is designed to be lenient (parse-a-prefix), which is exactly wrong for a tokenizer that must accept-or-reject a whole lexeme. `Number()`/strict regex fail loudly on garbage, turning a silent-wrong into a catchable error.
- Rule of thumb: A greedy `[0-9.]+` number lexer accepts malformed multi-dot numbers, and `parseFloat` silently truncates them (`"1.2.3"→1.2`) — validate the lexeme shape or use `Number()` (NaN-on-garbage), not `parseFloat` (prefix-salvage), so bad numeric input fails loudly instead of computing a wrong answer.
- Provenance (verified/assumed): VERIFIED first-hand — `1.2.3` evaluated to 1.2 with no error this session.
- Link: session 01KxkbJUq8YajH8GokSZYYHy; sandbox (not committed)
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-skilltree-formula.md#E5 · compatible · no sandbox · session (query brain for "train seams combination 3 sandboxes 5 loops" — loop 2/5), sandbox script loop2_csv.mjs, no code change to a shipping project

## E1 — carry source position for parser errors
- Date: 2026-07-01
- Project: local/sandbox-expr
- Tags: [tooling][process]
- What: Error reporting in a small expression parser (unclosed paren, unexpected operator, undefined variable).
- Why built: Users need to know why an expression failed.
- Design: The tokenizer produced `{t, v}` tokens WITHOUT recording each token's source index/column; the parser threw messages like "expected )".
- Got right: Errors are thrown for every malformed input (no silent success), and the messages name WHAT went wrong.
- Where/why it failed: The messages can't say WHERE — "expected )" for `((((1+2)` gives no column, so on a long expression the user can't locate the fault. The information was lost at tokenize time because positions weren't carried on the tokens.
- Fix: Record each token's start column at lex time (`{t, v, pos}`) and include it in every parse error ("expected ) at col 8"), ideally with a caret line under the source. Cheap to add up front, painful to retrofit once the parser assumes position-free tokens.
- Why this fix: Error *location* is most of an error message's value in a language/DSL tool; it can only come from position metadata threaded from the lexer. Decide to carry it before the parser is written, because every `throw` site needs the token in scope.
- Rule of thumb: Attach source position (index/column) to tokens at lex time and thread it into every parser error — "what" without "where" is nearly useless on real input, and adding positions after the fact means touching every throw site.
- Provenance (verified/assumed): VERIFIED first-hand — the sandbox parser threw correct-but-position-less errors ("expected )", "unexpected *") this session; the gap is the lesson.
- Link: session 01KxkbJUq8YajH8GokSZYYHy; sandbox (not committed)
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-skilltree-formula.md#E1 · compatible · no sandbox · session (query brain for "brain train combinations in sandbox"), sandbox scripts sweep.mjs/sweep3.mjs/sweep5.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-skilltree-formula.md#E3 · compatible · no sandbox · session (query brain for "train seams in combination, in sandbox environments"), sandbox script sweep_ratelimit.mjs, no code change to a shipping project
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-skilltree-formula.md#E5 · compatible · no sandbox · session (query brain for "train seams combination 3 sandboxes 5 loops" — loop 2/5), sandbox script loop2_csv.mjs, no code change to a shipping project
- Audited: 2026-10-14 · fail · No sandbox is stored, so I re-ran the claimed behaviour directly in Node 22. The core finding reproduces and is computed by the real runtime, not assumed: parseFloat("1.2.3") gives 1.2 and Number("1.2.3") gives NaN. But the Fix recommends the strict pattern /^\d*\.\d+|\d+\.?\d*$/ as a way to reject multi-dot lexemes, and that pattern is wrong: the alternation is not grouped, so the first branch is only anchored at the start and the second only at the end, and the pattern returns true for "1.2.3". Following the Fix's first option therefore keeps the silent-wrong behaviour. Number() also returns 0 for an empty string, so a lexer that calls it on an empty slice does not throw. The Rule of thumb (use Number or validate the shape) holds; the specific regex in the Fix does not, which is why this is a fail rather than a pass. · brain train auto loop 2 pass 3 audit mode, unattended run 2026-10-14; session_018eKNqSCZk9zsMEo2AXSjsk
