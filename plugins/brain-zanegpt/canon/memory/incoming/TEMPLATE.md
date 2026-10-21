<!--
  Proposal template. Copy to incoming/YYYY-MM-DD__<slug>.md and fill in.
  Do NOT edit projects/*.md or PITFALLS.md yourself — a steward promotes this,
  assigns the final ID, and adds the index line to canon.

  The steward HOLDS a proposal (invisible to `brain query`) unless ALL hold:
  - Every field below is present as a `- Label:` bullet, plus the `- ID:`
    bullet. This includes Provenance and Link. A skipped line is the most
    common cause of a hold; a heading (`## Design`) does not count.
  - What, Why built, Design, Got right, Where/why it failed, Fix, Why this fix
    and Rule of thumb each have at least 30 characters of real content ("n/a"
    fails).
  - A field that runs past one line continues on the next line INDENTED by two
    or more spaces. An unindented continuation is dropped and the field can
    read as too thin.
  - Provenance says "verified" or "first-hand" and does not negate it nearby
    ("not", "never", "no", "un-" in front of verified/confirmed). "assumed
    only" fails. Mixed cases ("verified X; did not verify Y") are held, so
    keep the two apart or name the unverified part elsewhere.
  - PROPOSED INDEX LINE is ONE physical line starting with a backticked
    [tag], never wrapped.
  - The text does not quote hostile-prompt phrasing verbatim (the steward's
    injection deny-list, INJECTION_RES, holds it for a human). Describe such
    strings in your own words instead of quoting them.
  - The Rule of thumb is not a near-duplicate of an existing index line,
    When 3 or more existing index lines are each moderately close to it, it
    joins a near-duplicate family: with 3 to 7 close lines it passes if
    Composed cites at least half of them; with 8 or more (a dense cluster)
    only a Distinct from: line passes. The hold message names the lessons.
  - A shipped sandbox file carries no hostile-prompt phrasing either.
  Polarity, if present, is `compatible` or `incompatible`; `incompatible`
  needs a Composed field.
  - A trial pick (a proposal carrying `- Picked-by:`) carries the ZaneGPT
    check — the bridge's second half — written by a SEPARATE agent that did
    not make the pick: run `brain check <proposal>` after writing it. It
    fills ZaneGPT verdict, Hidden assumption, Would prove it wrong, Break
    scenario and Checked by (with a digest of What + Rule of thumb +
    Prediction). Held when missing, thin, stale (the claim changed after the
    check), when the verdict is `fails`, or when no Scenario is marked as the
    one built to break the claim. Proposals without Picked-by are untouched.
  Sandbox / Prediction / Observed / Scenarios are optional today: a composed
  or sandbox-backed proposal missing them, or a broad always/never/every rule
  with under 3 Scenarios, gets a WARN, not a hold.
  Source of truth: scripts/steward.py (REQUIRED, SUBSTANCE, MIN_SUBSTANCE,
  provenance_ok, INJECTION_RES, FAMILY_*, SANDBOX_NAME_RE, sandbox_warnings,
  POLARITIES, ZANEGPT_FIELDS, zanegpt_problems). Update
  this block in the same commit as any change to those.
-->

## FULL ENTRY

- ID: E? (steward assigns the real id on promotion)
- Date: YYYY-MM-DD
- Project: <owner>/<repo>
- Tags: [domain][modifier]   (lowercase, bracketed; reuse existing tags first — see PITFALLS.md legend)
- What:
- Why built:
- Design:
- Got right:
- Where/why it failed:
- Fix:
- Why this fix:
- Rule of thumb:
- Provenance (verified/assumed): what you confirmed first-hand vs what you assume
- Composed: (optional) if this lesson came from stress-testing SEVERAL existing
  lessons together, list them as `<slug>/E<n>` refs, comma-separated
  (e.g. `astar-replan/E2, collision/E1, anim/E4`). Omit or write `N/A` for a
  single-system lesson. This is the machine-readable edge list `brain analyze
  graph` reads to map which systems are co-verified together — writing it here
  is more reliable than having the tool guess it from your prose.
  An idea KERNEL this lesson applied can be listed too, as `ideas:` plus its
  header path (e.g. `ideas:SONGWRITING/rhyme-tooling/two-pass-letter-assignment`).
  A prefix is fine if it matches exactly one kernel. This is how a memory
  links to the idea it used; a kernel only quoted in prose counts as inferred.
- Polarity: (optional, with Composed) `compatible` (the default when omitted)
  or `incompatible` — the sandbox REFUTED the composition: the named entries do
  not combine the way it was reasoned. A refutation is a real lesson; file it.
  Its Rule of thumb says what fails and what to do instead.
- Distinct from: (optional) only when the steward held this as a family
  member: name the closest existing lesson as `<slug>/E<n>` and say in a
  sentence what this finds that it does not. A bare reference does not pass.
- Sandbox: (optional; expected whenever a sandbox verified this) the file name
  of the sandbox script, saved beside this proposal in incoming/ as
  `YYYY-MM-DD__<slug>.py`. Standard library only, deterministic, and its last
  printed line is `RESULT: PASS <summary>` or `RESULT: FAIL <summary>`. The
  steward moves it to sandboxes/ on promotion so anyone can rerun it; it never
  runs it itself.
- Prediction: (optional; pairs with Sandbox) the result you expected, written
  BEFORE the first run, specific enough that it could have come out wrong
  (a number, a count, an outcome).
- Observed: (optional; pairs with Sandbox) the sandbox's actual RESULT line
  and key numbers, copied from the run.
- Scenarios: (optional; pairs with Sandbox) the distinct cases the sandbox ran,
  as `1) … 2) … 3) …` or separated by `;`. Mark the one built to BREAK the
  claim. A Rule of thumb that says always/never/every with fewer than 3 gets a
  WARN: add scenarios, or narrow the rule to what was actually tested.
- ZaneGPT verdict / Hidden assumption / Would prove it wrong / Break scenario /
  Checked by: (trial picks only — never hand-written: `brain check <proposal>`
  starts a separate ZaneGPT agent that writes these five lines)
- Link: session / commit / PR

## PROPOSED INDEX LINE

`[domain][modifier]` one-line lesson, scannable → projects/<owner>__<repo>.md#<id>

<!-- ONE physical line, never wrapped — this line is machine-read verbatim
  into PITFALLS.md, and the `- ID:` bullet above is what the promoter keys
  body capture on. Both are enforced (steward hold / PR-time fail). -->

