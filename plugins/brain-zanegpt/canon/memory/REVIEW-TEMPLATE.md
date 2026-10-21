<!--
  Review template. A review checks an EXISTING entry; it is not a new lesson.
  Copy to incoming/YYYY-MM-DD__review-<slug>.md and fill in. The steward does
  not promote it: it appends one dated line to the target entry
  (`- Audited:` for an audit, `- Reverified:` for a rebuild) and deletes the drop.

  Kinds:
  - audit   — read the entry AND its stored sandbox (sandboxes/…). Judge whether
              the model actually TESTS the claim: it must not assume its own
              answer, and it must cover the scope the Rule of thumb states.
              Verdict pass | fail | modeled (modeled = the claim is about a real
              system — browser, library, API — but only a hand-written model
              was tested).
  - rebuild — from the entry's claim and prediction ONLY (do not open its
              sandbox first), build your own sandbox and run it. Ship it beside
              this file as incoming/YYYY-MM-DD__<slug>.py. Verdict pass | fail.
              Use your OWN fixture and inputs: a rebuild that reuses the
              original's setup shares its blind spots and proves little
              (august-10#E14). Say in Checked what differs.

  The steward HOLDS a review unless: Target names an existing
  projects/<owner>__<repo>.md#E<n>; Kind and Verdict use the words above;
  Checked has at least 30 characters; Link is present and differs from the
  target entry's own Link (a review comes from a different session); a rebuild
  ships its sandbox and fills Prediction and Observed; nothing matches the
  injection deny-list. Source of truth: scripts/steward.py (check_review).

  Readers derive the entry's tier from these lines, never from a field an
  author writes: any fail → disputed · rebuild pass → confirmed ·
  audit modeled → modeled · audit pass → audited · none → provisional.
  A third steward line, `- Cited-by:` (scripts/cited_by.py), is written when a
  NEW lesson names this entry in Composed:; with a sandbox and a compatible
  result it lifts a provisional entry to `composed` (built on, and the build
  passed), one step below audited. An incompatible Cited-by refutes that
  composition only, never the entry.
-->

## REVIEW

- Target: projects/<owner>__<repo>.md#E<n>
- Kind: audit | rebuild
- Verdict: pass | fail | modeled
- Checked: what you examined and why that verdict (one paragraph)
- Sandbox: (rebuild only) YYYY-MM-DD__<slug>.py
- Prediction: (rebuild only) the result you expected, written before running
- Observed: (rebuild only) the RESULT line and key numbers
- Link: this session / commit
