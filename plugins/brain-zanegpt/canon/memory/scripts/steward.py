#!/usr/bin/env python3
"""Auto-steward for the `memory` knowledge base.

Promotes `incoming/` proposals into canon (projects/*.md + PITFALLS.md) when
they pass every mechanical check; HOLDS the exceptions for a human. The owner
stops being the approver and becomes the escalation path.

Checks (all must pass to promote):
  1. schema     — every required field present (validate.py's rule)
  2. substance  — the load-bearing fields are non-trivial (write-bar proxy)
  3. provenance — something was verified first-hand (not assumed-only)
  4. injection  — no directive language addressed to future agents/readers
  5. dedup      — rule-of-thumb not near-identical to an existing index line,
                  and not the next variant in a near-duplicate family (FAMILY_*)
  6. sandbox    — a shipped incoming/<name>.py carries no injection text and
                  would not overwrite a different sandboxes/<name>.py

Evidence gaps (a composed proposal with no Sandbox/Prediction/Observed, or a
Sandbox file that isn't there) print as WARN and never hold — phase 1 of the
train-verification plan is warn-first. A promoted proposal's sandbox moves to
sandboxes/; the steward stores it and never runs it.

A held proposal gets a `STEWARD HOLD` comment block appended with the reasons;
fix the issue and delete the block to resubmit. `incoming/stubs.md` is ignored
(stubs graduate through the template first).

Run: python3 scripts/steward.py [--dry-run]
Pure standard library. Exits nonzero on internal error or if post-promotion
validation fails; exits 0 otherwise (holds are not errors).
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from datetime import date

def _resolve_root() -> str:
    # allow running the steward against a different memory root (e.g. a
    # project's local .brain/memory store) — used by `brain sync` in read-only
    if "--root" in sys.argv:
        return os.path.abspath(sys.argv[sys.argv.index("--root") + 1])
    env = os.environ.get("BRAIN_STEWARD_ROOT")
    if env:
        return os.path.abspath(env)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


ROOT = _resolve_root()
DRY = "--dry-run" in sys.argv

REQUIRED = ["tags", "what", "why built", "design", "got right", "where/why",
            "fix", "why this fix", "rule of thumb", "provenance", "link"]
# All narrative fields get the substance floor — a bare "n/a" in any of them
# is a placeholder, not a considered entry. (Only tags/provenance/link are
# exempt: they have their own dedicated checks.)
SUBSTANCE = ["what", "why built", "design", "got right", "where/why",
             "fix", "why this fix", "rule of thumb"]
MIN_SUBSTANCE = 30  # chars

# Injection deny-list. These match on HOLD (a human then reviews) — a false
# positive is a safe-fail, so the patterns are deliberately permissive about
# filler words between the trigger verb and its object. A bare literal phrase
# match (the earlier version) was trivially dodged by natural rewording —
# "ignore THE previous instructions" slipped past "ignore (previous|...)"
# because of the inserted article. `[\w\s,'-]{0,24}` swallows ordinary
# articles/adjectives/clauses without spanning unrelated sentences.
_GAP = r"[\w\s,'-]{0,24}"
INJECTION_RES = [
    re.compile(r"(?i)\bignore\b" + _GAP +
               r"\b(previous|prior|above|earlier|all|the)\b" + _GAP +
               r"\b(instruction|prompt|context|rule|direction)"),
    re.compile(r"(?i)\bdisregard\b" + _GAP +
               r"\b(system|instruction|prompt|rule|previous|prior|above|"
               r"earlier|direction)"),
    re.compile(r"(?i)\byou must now\b"),
    re.compile(r"(?i)\bexecute the following\b"),
    re.compile(r"(?i)\bfollow\b" + _GAP + r"\b(these|the following|the above|"
               r"below)\b" + _GAP + r"\binstruction"),
    re.compile(r"(?i)\bdo\s*(?:not|n['’]t)\b" + _GAP +
               r"\b(tell|inform|mention|reveal|disclose|report|notify)\b" +
               _GAP + r"\b(user|owner|human|operator|anyone|them|maintainer)"),
    re.compile(r"(?i)\bnew system (prompt|message)\b"),
    re.compile(r"(?i)\b(system prompt|system message|your instructions)\b" +
               _GAP + r"\b(override|ignore|replace|are now|is now)"),
]

# Provenance negation: the marker words ("verified"/"firsthand") appearing as
# bare substrings never confirmed anything — a proposal saying "NOT verified
# firsthand, purely assumed" contains both words yet asserts the opposite.
# Catch a negation adjacent to the verification stem, plus the "unverified"/
# "unconfirmed" prefix form. Same failure class as the old STEWARD-HOLD
# substring bug: match meaning-bearing structure, not a bare keyword.
NEG_PROV_RE = re.compile(
    r"(?:\b(?:not|never|no|without)\b|n['’]t\b)[\w\s,'’-]{0,15}"
    r"(?:verif|first[\s-]?hand|confirm)"
    r"|\bun(?:verif|confirm)")

# The actual appended marker (see the `block =` construction below) — never a
# bare substring check, or any proposal whose own BODY TEXT happens to discuss
# "STEWARD HOLD" (a meta-lesson about this very mechanism, exactly the kind of
# self-referential process lesson this repo invites) gets mistaken for an
# already-processed hold and silently skipped forever, with no real reasons
# ever recorded and no promotion ever attempted.
HOLD_MARKER_RE = re.compile(r"<!--\s*STEWARD HOLD\b")
ID_RE = re.compile(r"^## (E\d+)\b", re.M)
FIELD_RE = re.compile(r"^\s*-\s*\**([A-Za-z/ ]+?)\**\s*(?:\(.*?\))?\s*:\s*(.*)$")
# strip only a trailing "→ projects/…" anchor — the lesson text itself may
# legitimately contain arrows (e.g. `"1.2.3"→1.2`)
INDEX_RE = re.compile(r"^\s*(`\[.+?)(?:\s*→\s*projects/\S*)?\s*$")


def read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def write(p, text):
    if not DRY:
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)


def tokens(text):
    return {w for w in re.findall(r"[a-z][a-z0-9-]{3,}", text.lower())}


def jaccard(a, b):
    A, B = tokens(a), tokens(b)
    return len(A & B) / len(A | B) if A and B else 0.0


def overlap(a, b):
    # intersection / smaller set — catches a short lesson that's a subset of a
    # longer existing one (jaccard misses this when lengths differ a lot).
    A, B = tokens(a), tokens(b)
    return len(A & B) / min(len(A), len(B)) if A and B else 0.0


def parse(text):
    """Extract bullet fields (multiline values) + the proposed index line."""
    fields, key = {}, None
    for line in text.splitlines():
        m = FIELD_RE.match(line)
        if m and len(m.group(1).strip()) < 30:
            key = m.group(1).strip().lower()
            fields[key] = m.group(2).strip()
        elif key and (line.startswith("  ") or line.startswith("\t")):
            fields[key] += " " + line.strip()
        else:
            key = None
    index_line = ""
    in_index = False
    for line in text.splitlines():
        if line.strip().upper().startswith("##") and "PROPOSED INDEX LINE" in line.upper():
            in_index = True
        elif in_index and line.strip().startswith("`["):
            index_line = line.strip()
            break
    return fields, index_line


def field(fields, name):
    for k, v in fields.items():
        if k.startswith(name):
            return v
    return ""


def existing_index_lessons():
    # dedup against this store's PITFALLS + any extra index files named in
    # BRAIN_DEDUP_EXTRA (e.g. the SHARED canon, so a local promotion won't
    # re-file a lesson that already exists upstream).
    paths = [os.path.join(ROOT, "PITFALLS.md")]
    paths += [p for p in os.environ.get("BRAIN_DEDUP_EXTRA", "").split(os.pathsep)
              if p]
    out = []
    for path in paths:
        if not os.path.exists(path):
            continue
        for line in read(path).splitlines():
            if line.strip().startswith("- `["):
                out.append(re.sub(r"`\[[^\]]*\]`*|→.*$", "", line))
    return out


def provenance_ok(prov: str) -> bool:
    """True only if the provenance field affirmatively marks something as
    verified/firsthand and does NOT negate it. A missing/empty field, a
    negated one ("not verified"), or an explicit "assumed-only" all fail —
    a keyword check can't confirm provenance, only refuse the clear misses,
    so it fails safe to a human. Shared with validate.py's PR-time gate."""
    prov = prov.lower()
    has_marker = ("verified" in prov or "firsthand" in prov
                  or "first-hand" in prov)
    if not has_marker or NEG_PROV_RE.search(prov):
        return False
    return "assumed only" not in prov and "assumed-only" not in prov


def wrapped_index_line(text) -> bool:
    """True if the PROPOSED INDEX LINE section spans more than one content
    line. The index line is machine-read and lands verbatim in PITFALLS.md;
    prose-style hard-wrapping silently truncated 21 canon index lines before
    this gate existed (only the first physical line was ever captured)."""
    on, content = False, 0
    for line in text.splitlines():
        s = line.strip()
        if s.upper().startswith("##") and "PROPOSED INDEX LINE" in s.upper():
            on = True
            continue
        if on:
            if s.startswith("##") or (not s and content):
                break
            if s:
                content += 1
    return content > 1


# The bridge's second half (Brain commit 93aa9b2: "Conscience carries
# handoffs, ZaneGPT pressure-tests picks"). A trial pick — any proposal with a
# `- Picked-by:` label — must carry the ZaneGPT check, written by a SEPARATE
# agent that did not make the pick (`brain check <proposal>` starts one), and
# the check must be on the lesson as it stands now: its digest covers What,
# Rule of thumb and Prediction, so editing the claim after the check holds it.
# Until 2026-10-17 this half was three printed lines nothing read (64 of 228
# trial lessons skipped it and promoted).
ZANEGPT_FIELDS = ["zanegpt verdict", "hidden assumption", "would prove it wrong",
                  "break scenario", "checked by"]
ZANEGPT_VERDICT_RE = re.compile(r"^\s*(holds|weak|fails)\b", re.I)
PICKED_RE = re.compile(r"^\s*-\s*Picked-by\s*:\s*\S", re.M | re.I)
ZANEGPT_DIGEST_RE = re.compile(r"digest\s+([0-9a-f]{12})\b", re.I)


def zanegpt_digest(fields):
    """12-hex digest of the claim a ZaneGPT check was run on. Whitespace is
    collapsed so a re-wrapped line is the same claim. Brain's `brain check`
    computes the identical value (bin/brain _zanegpt_digest)."""
    import hashlib
    claim = "\n".join(" ".join(field(fields, k).split())
                      for k in ("what", "rule of thumb", "prediction"))
    return hashlib.sha256(claim.encode("utf-8")).hexdigest()[:12]


def zanegpt_problems(fields, full_text):
    """Hold reasons for a trial pick whose ZaneGPT check is missing, thin,
    stale, or says the claim fails. Non-trial proposals are untouched."""
    # FIELD_RE does not admit a hyphen, so the label is read from the raw text
    if not PICKED_RE.search(full_text):
        return []
    run = "run `brain check <this proposal>` (a separate ZaneGPT agent fills these in)"
    missing = [k for k in ZANEGPT_FIELDS if not field(fields, k).strip()]
    if missing:
        return [f"zanegpt: trial pick without the separate ZaneGPT check (missing "
                f"{', '.join(repr(k) for k in missing)}) — {run}"]
    out = []
    for k in ("hidden assumption", "would prove it wrong", "break scenario"):
        if len(field(fields, k)) < MIN_SUBSTANCE:
            out.append(f"zanegpt: '{k}' too thin ({len(field(fields, k))} chars) — {run}")
    verdict = field(fields, "zanegpt verdict")
    m = ZANEGPT_VERDICT_RE.match(verdict)
    if not m:
        out.append("zanegpt: verdict must start with holds, weak or fails — " + run)
    elif m.group(1).lower() == "fails":
        out.append(f"zanegpt: the separate check says the claim fails ({verdict.strip()}) "
                   "— revise or narrow the lesson, then re-run `brain check`")
    d = ZANEGPT_DIGEST_RE.search(field(fields, "checked by"))
    now = zanegpt_digest(fields)
    if not d:
        out.append("zanegpt: 'Checked by' carries no digest — " + run)
    elif d.group(1).lower() != now:
        out.append(f"zanegpt: the lesson changed after its check (digest {d.group(1)} "
                   f"≠ {now}) — re-run `brain check`")
    if not re.search(r"\bbreak", field(fields, "scenarios"), re.I):
        out.append("zanegpt: no '- Scenarios:' case is marked as the one built to "
                   "break the claim — run it and mark it")
    return out


def check(fields, index_line, full_text):
    reasons = []
    low = {k: v for k, v in fields.items()}
    for req in REQUIRED:
        if not any(k.startswith(req) for k in low):
            reasons.append(f"schema: missing field '{req}'")
    if not re.search(r"^\s*-\s*ID\s*:", full_text, re.M):
        reasons.append("schema: missing '- ID:' bullet — body capture is "
                       "keyed on it; without it the entry promotes EMPTY "
                       "(this happened: opticon#E28)")
    if wrapped_index_line(full_text):
        reasons.append("index: PROPOSED INDEX LINE must be ONE physical "
                       "line (no prose wrapping) — wrapped continuations "
                       "are silently dropped at promotion")
    for req in SUBSTANCE:
        v = field(fields, req)
        if len(v) < MIN_SUBSTANCE:
            reasons.append(f"substance: '{req}' too thin ({len(v)} chars) — "
                           "write-bar proxy failed")
    if not provenance_ok(field(fields, "provenance")):
        reasons.append("provenance: not clearly marked verified/firsthand "
                       "(empty, negated, or assumed-only — needs a human)")
    for rx in INJECTION_RES:
        if rx.search(full_text):
            reasons.append(f"injection: matches deny-pattern {rx.pattern!r}")
    if not index_line:
        reasons.append("index: no proposed index line found")
    pol = field(fields, "polarity").strip().lower()
    if pol and pol not in POLARITIES:
        reasons.append("polarity: must be 'compatible' or 'incompatible'")
    if pol == "incompatible" and not composed_refs_present(fields):
        reasons.append("polarity: 'incompatible' needs a Composed: field naming "
                       "the entries that turned out not to combine")
    if REVIEW_LINE_RE.search(full_text):
        reasons.append("review: a lesson may not carry its own '- Audited:' or "
                       "'- Reverified:' line — those are appended by the "
                       "steward from a separate REVIEW (REVIEW-TEMPLATE.md)")
    reasons += composed_ref_problems(field(fields, "composed"))
    reasons += zanegpt_problems(fields, full_text)
    pm = re.match(r"\s*([^/\s]+)\s*/\s*(\S+)", field(fields, "project"))
    if pm:
        o = re.sub(r"[^a-z0-9._-]", "", pm.group(1).lower()); n = re.sub(r"[^a-z0-9._-]", "", pm.group(2).lower())
        other = owner_mismatch(o, n)
        if other:
            reasons.append(f"project: '{o}/{n}' would open a new file but '{other}.md' already holds "
                           f"repo '{n}' under another owner; set Project to that owner if it is the "
                           "same project (a fork, second account or proxy remote)")
    rot = field(fields, "rule of thumb")
    cand = rot + " " + index_line
    near = []
    for lesson in existing_index_lessons():
        j, o = jaccard(cand, lesson), overlap(cand, lesson)
        if j > 0.55 or o > 0.72:
            sim = max(j, o)
            reasons.append(f"dedup: {sim:.0%} similar to existing index line "
                           f"'{lesson.strip()[:70]}…' — possible duplicate")
            near = []
            break
        if j > FAMILY_JACCARD or o > FAMILY_OVERLAP:
            near.append(lesson)
    why = family_hold(near, field(fields, "composed"), field(fields, "distinct from"))
    if why:
        reasons.append(why)
    return reasons


# Near-duplicate family gate. The age-cutoff flood (about 640 variants of 9
# findings, removed 2026-10-15) passed the pairwise dedup above because each
# variant changed its numbers or data structure. A proposal is "near" an
# existing index line when either similarity clears the FAMILY_* bar.
#   fewer than FAMILY_MIN near lines   -> no family check
#   FAMILY_MIN up to FAMILY_DENSE - 1  -> a real series: passes when Composed
#       cites at least half of the near lessons, or a Distinct from: field
#       names one of them and says what is new
#   FAMILY_DENSE or more               -> a dense cluster: only Distinct from:
#       passes (citing alone is what a copying loop does)
# Measured on 2026-10-15: real series (TikTok Shop, 31 lessons) never had more
# than 6 near lines and a 300-lesson sample never more than 6, while the flood
# had a median of 12 and 67% at 8 or more.
FAMILY_JACCARD = 0.30
FAMILY_OVERLAP = 0.50
FAMILY_MIN = 3
FAMILY_DENSE = 8
_LINE_REF = re.compile(r"→\s*projects/([^\s#]+?)(?:\.md)?#(E\d+)")
_COMPOSED_REF = re.compile(r"([A-Za-z0-9][\w.-]*?)(?:\.md)?[/#](E\d+)")


def _ref_key(slug, eid):
    s = slug.split("/")[-1]
    s = s[:-3] if s.endswith(".md") else s
    if s.startswith(("local__", "pappydapimp69__")):
        s = s.split("__", 1)[1]
    return s, eid


def family_hold(near, composed, distinct):
    """Hold reason for a proposal that joins a near-duplicate family, or ''."""
    if len(near) < FAMILY_MIN:
        return ""
    refs = []
    for line in near:
        m = _LINE_REF.search(line)
        if m:
            refs.append(_ref_key(m.group(1), m.group(2)))
    names = ", ".join(f"{s}/{e}" for s, e in refs[:6]) + (" …" if len(refs) > 6 else "")
    named = {_ref_key(s, e) for s, e in _COMPOSED_REF.findall(distinct or "")}
    said = len(_COMPOSED_REF.sub("", distinct or "").strip(" ,.;:-")) >= 30
    if named & set(refs) and said:
        return ""
    cited = {_ref_key(s, e) for s, e in _COMPOSED_REF.findall(composed or "")
             if not s.startswith("ideas")}
    if len(near) < FAMILY_DENSE and 2 * len(cited & set(refs)) >= len(refs):
        return ""
    if len(near) >= FAMILY_DENSE:
        return (f"family: {len(near)} existing lessons are already close to this one "
                f"(a dense cluster: {names}). File one roll-up instead, or add "
                "'- Distinct from:' naming the closest of them and saying in a "
                "sentence what this finds that they do not.")
    return (f"family: {len(near)} existing lessons are close to this one ({names}). "
            "If it builds on them, cite at least half in '- Composed:'; otherwise "
            "add '- Distinct from:' naming one and saying what is new.")


# Sandbox evidence (train verification, phase 1). A proposal may ship the
# sandbox that verified it as incoming/<name>.py and name it in `- Sandbox:`.
# On promotion the file moves to sandboxes/ so the evidence outlives the
# session that built it. The steward never EXECUTES it: storing is safe,
# running untrusted code is a human's call. Missing evidence only WARNS for
# now (warnings never hold); an injection hit in the sandbox text holds, like
# the same hit in the proposal would.
SANDBOX_NAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}__[a-z0-9][a-z0-9-]*\.py$")
SANDBOX_DIR = "sandboxes"


def sandbox_name(fields):
    """The basename named in `- Sandbox:` (backticks and any `incoming/` or
    `sandboxes/` prefix stripped), or ''."""
    v = field(fields, "sandbox").strip().strip("`").strip()
    return os.path.basename(v) if v else ""


def composed_refs_present(fields):
    v = field(fields, "composed").strip()
    return bool(v) and not re.fullmatch(r"(n/?a|none|—|-)\.?", v, re.I)


# Scope (phase 4): a broad rule needs more than one scenario behind it. A
# keyword check can't judge scope, so this only WARNS; it never holds.
BROAD_RULE_RE = re.compile(r"\b(always|never|every)\b", re.I)


def scenario_count(v):
    """Scenarios listed as `1) … 2) …`, `a; b; c`, or one per wrapped line."""
    v = v.strip()
    if not v:
        return 0
    numbered = re.findall(r"(?:^|\s)\(?\d+[).]", v)
    if len(numbered) >= 2:
        return len(numbered)
    return len([p for p in re.split(r"\s*;\s*", v) if p.strip()])


def sandbox_warnings(fields, root=None):
    """Evidence gaps that do NOT hold (yet). A composed or sandbox-citing
    proposal should carry the sandbox file, the prediction written before the
    run, and the observed result, so a later reader can rerun and compare."""
    root = root or ROOT
    name = sandbox_name(fields)
    if not (composed_refs_present(fields) or name):
        return []
    out = []
    for req in ("sandbox", "prediction", "observed"):
        if not field(fields, req).strip():
            out.append(f"evidence: no '- {req.capitalize()}:' field")
    rule = field(fields, "rule of thumb")
    if BROAD_RULE_RE.search(rule):
        n = scenario_count(field(fields, "scenarios"))
        if n < 3:
            out.append(f"scope: the Rule of thumb makes a broad claim "
                       f"(always/never/every) but '- Scenarios:' lists {n} — "
                       "test 3+ that differ, one built to break it, or narrow "
                       "the rule to what was tested")
    if name:
        if not SANDBOX_NAME_RE.match(name):
            out.append(f"evidence: sandbox name '{name}' should be "
                       "YYYY-MM-DD__<slug>.py")
        elif not (os.path.isfile(os.path.join(root, "incoming", name))
                  or os.path.isfile(os.path.join(root, SANDBOX_DIR, name))):
            out.append(f"evidence: sandbox file '{name}' not found in "
                       f"incoming/ or {SANDBOX_DIR}/")
    return out


def sandbox_hold_reasons(fields, root=None):
    """Reasons to HOLD over the sandbox file itself: injection text, or a name
    that would overwrite a different stored sandbox."""
    root = root or ROOT
    name = sandbox_name(fields)
    src = os.path.join(root, "incoming", name) if name else ""
    if not (name and SANDBOX_NAME_RE.match(name) and os.path.isfile(src)):
        return []
    reasons = []
    code = read(src)
    for rx in INJECTION_RES:
        if rx.search(code):
            reasons.append(f"injection: sandbox {name} matches deny-pattern "
                           f"{rx.pattern!r}")
            break
    dst = os.path.join(root, SANDBOX_DIR, name)
    if os.path.isfile(dst) and read(dst) != code:
        reasons.append(f"sandbox: {SANDBOX_DIR}/{name} already exists with "
                       "different content — rename the sandbox")
    return reasons


# Reviews (train verification, phase 2). A second session checks an existing
# entry and files a REVIEW proposal (schema: REVIEW-TEMPLATE.md). The steward
# never promotes it as a lesson: it appends ONE dated line to the target entry
# (`- Audited:` or `- Reverified:`) and deletes the drop. An entry's trust tier
# is derived from those lines by readers (brain), never typed by an author:
#   any fail -> disputed · rebuild pass -> confirmed · audit modeled -> modeled
#   · audit pass -> audited · none -> provisional.
REVIEW_HEAD_RE = re.compile(r"^##\s*REVIEW\s*$", re.M)
REVIEW_KINDS = {"audit": "Audited", "rebuild": "Reverified"}
# Polarity (phase 3, tension T21): a composition that was sandbox-REFUTED is
# still knowledge. `- Polarity: incompatible` files it as a lesson whose
# Composed: edge means "these do not combine that way"; omitted = compatible.
POLARITIES = {"compatible", "incompatible"}
REVIEW_LINE_RE = re.compile(r"^\s*-\s*\**(Audited|Reverified)\**\s*:", re.M | re.I)
REVIEW_VERDICTS = {"pass", "fail", "modeled"}
TARGET_RE = re.compile(r"(projects/[a-z0-9][a-z0-9._-]*__[a-z0-9][a-z0-9._-]*\.md)"
                       r"\s*#\s*(E\d+)")


def is_review(text):
    return bool(REVIEW_HEAD_RE.search(text))


def _entry_span(ptext, eid):
    """(start, end) of entry `eid`'s block in a project file, or None."""
    m = re.search(rf"^## {eid}\b.*$", ptext, re.M)
    if not m:
        return None
    nxt = re.search(r"^## E\d+\b|^---\s*$", ptext[m.end():], re.M)
    return m.start(), (m.end() + nxt.start()) if nxt else len(ptext)


def review_target(fields, root=None):
    """(rel_path, eid, entry_block) for the review's Target, or None."""
    root = root or ROOT
    m = TARGET_RE.search(field(fields, "target"))
    if not m:
        return None
    rel, eid = m.group(1), m.group(2)
    path = os.path.join(root, rel)
    if not os.path.isfile(path):
        return None
    ptext = read(path)
    span = _entry_span(ptext, eid)
    return (rel, eid, ptext[span[0]:span[1]]) if span else None


def check_review(fields, full_text, root=None, canon=None):
    """HOLD reasons for a review. `root` holds its incoming/ (sandbox);
    `canon` holds the target entry (defaults to root)."""
    root = root or ROOT
    canon = canon or root
    reasons = []
    kind = field(fields, "kind").strip().lower()
    verdict = field(fields, "verdict").strip().lower()
    if kind not in REVIEW_KINDS:
        reasons.append("review: Kind must be 'audit' or 'rebuild'")
    if verdict not in REVIEW_VERDICTS:
        reasons.append("review: Verdict must be 'pass', 'fail' or 'modeled'")
    if kind == "rebuild" and verdict == "modeled":
        reasons.append("review: 'modeled' is an audit verdict — a rebuild "
                       "passes or fails")
    if len(field(fields, "checked")) < MIN_SUBSTANCE:
        reasons.append(f"review: 'Checked' too thin — say what was examined "
                       f"and why (≥{MIN_SUBSTANCE} chars)")
    if not field(fields, "link").strip():
        reasons.append("review: missing '- Link:' (the reviewing session)")
    tgt = review_target(fields, canon)
    if not tgt:
        reasons.append("review: Target must be an existing "
                       "projects/<owner>__<repo>.md#E<n>")
    else:
        own = _field_in_block(tgt[2], "link")
        mine = field(fields, "link").strip()
        if own and mine and own.strip() == mine:
            reasons.append("review: Link matches the target entry's own Link — "
                           "a review must come from a different session")
    if kind == "rebuild":
        name = sandbox_name(fields)
        if not (name and SANDBOX_NAME_RE.match(name)
                and os.path.isfile(os.path.join(root, "incoming", name))):
            reasons.append("review: a rebuild must ship its own sandbox in "
                           "incoming/ and name it in '- Sandbox:'")
        for req in ("prediction", "observed"):
            if not field(fields, req).strip():
                reasons.append(f"review: a rebuild needs '- {req.capitalize()}:'")
    for rx in INJECTION_RES:
        if rx.search(full_text):
            reasons.append(f"injection: matches deny-pattern {rx.pattern!r}")
            break
    return reasons + sandbox_hold_reasons(fields, root)


def _field_in_block(block, name):
    for line in block.splitlines():
        m = FIELD_RE.match(line)
        if m and m.group(1).strip().lower().startswith(name):
            return m.group(2)
    return ""


def _one_line(s):
    return re.sub(r"\s+", " ", s).strip()


def apply_review(fname, fields):
    """Append the review line to its target entry. [] on success, else reasons."""
    rel, eid, _block = review_target(fields)
    path = os.path.join(ROOT, rel)
    ptext = read(path)
    start, end = _entry_span(ptext, eid)
    kind = field(fields, "kind").strip().lower()
    verdict = field(fields, "verdict").strip().lower()
    parts = [date.today().isoformat(), verdict]
    sbx = sandbox_name(fields) if kind == "rebuild" else ""
    if sbx:
        parts.append(f"{SANDBOX_DIR}/{sbx}")
        parts.append("observed " + _one_line(field(fields, "observed")))
    parts.append(_one_line(field(fields, "checked")))
    parts.append(_one_line(field(fields, "link")))
    line = f"- {REVIEW_KINDS[kind]}: " + " · ".join(parts)
    body = ptext[start:end].rstrip("\n")
    tail = ptext[end:]
    write(path, ptext[:start] + body + "\n" + line + "\n"
          + ("\n" if tail and not tail.startswith("\n") else "") + tail)
    if not DRY:
        os.remove(os.path.join(ROOT, "incoming", fname))
        if sbx:
            os.makedirs(os.path.join(ROOT, SANDBOX_DIR), exist_ok=True)
            os.replace(os.path.join(ROOT, "incoming", sbx),
                       os.path.join(ROOT, SANDBOX_DIR, sbx))
    print(f"  ✓ review applied → {rel}#{eid} ({REVIEW_KINDS[kind]}: {verdict})")
    return []


# Citation integrity: every memory reference in Composed must name exactly one
# project file and an entry that exists in it. A miss used to pass silently
# (a ref to a lesson that never existed, or to the wrong file of a project
# logged under two names) and then fed `brain train` a false edge.
_REF_RE = re.compile(r"(?:projects/)?([A-Za-z0-9_.-]+?)(?:\.md)?(?:/|#)(E\d+)\b")


def _project_stems():
    pdir = os.path.join(ROOT, "projects")
    return [f[:-3] for f in os.listdir(pdir) if f.endswith(".md")] if os.path.isdir(pdir) else []


def _stem_candidates(slug, stems):
    s = slug.lower()
    out = []
    for st in stems:
        low = st.lower()
        keys = {low}
        if "__" in low:
            keys.add(low.split("__", 1)[1])
        for k in list(keys):
            if k.startswith("sandbox-"):
                keys.add(k[len("sandbox-"):])
        if s in keys:
            out.append(st)
    return out


def composed_ref_problems(composed):
    v = re.sub(r"ideas:\S+", " ", composed or "")
    stems = _project_stems()
    problems = []
    for slug, eid in _REF_RE.findall(v):
        cands = _stem_candidates(slug, stems)
        ref = f"{slug}/{eid}"
        if not cands:
            problems.append(f"composed: '{ref}' names no project file")
        elif len(cands) > 1:
            problems.append(f"composed: '{ref}' is ambiguous ({', '.join(sorted(cands))}); "
                            "use the full <owner>__<repo>/E<n> form")
        else:
            ptext = read(os.path.join(ROOT, "projects", cands[0] + ".md"))
            if not re.search(rf"^## {eid}\b", ptext, re.M):
                problems.append(f"composed: '{ref}' has no entry {eid} in {cands[0]}.md")
    return problems


def project_alias(owner, name):
    """A project logged without its GitHub owner ('local/<repo>', from a checkout
    with no remote) files into the one existing '<owner>__<repo>' file of the same
    repo instead of opening a second file for the same project. Returns the
    existing stem or None."""
    if owner != "local":
        return None
    hits = [st for st in _project_stems()
            if "__" in st and st.split("__", 1)[1].lower() == name and not st.lower().startswith("local__")]
    return hits[0] if len(hits) == 1 else None


def owner_mismatch(owner, name):
    """A NEW '<owner>__<repo>' file when the same repo name already exists under
    exactly one other real owner: probably the same project seen through a
    different remote (a fork, a second account, a proxy). Held for a human."""
    if owner == "local" or os.path.exists(os.path.join(ROOT, "projects", f"{owner}__{name}.md")):
        return None
    others = [st for st in _project_stems()
              if "__" in st and st.split("__", 1)[1].lower() == name
              and not st.lower().startswith(("local__", owner + "__"))]
    return others[0] if len(others) == 1 else None


def project_file(fields):
    proj = field(fields, "project")
    m = re.match(r"\s*([^/\s]+)\s*/\s*(\S+)", proj)
    if not m:
        return None
    owner = re.sub(r"[^a-z0-9._-]", "", m.group(1).lower())
    name = re.sub(r"[^a-z0-9._-]", "", m.group(2).lower())
    if not (owner and name):
        return None
    alias = project_alias(owner, name)
    return f"projects/{alias}.md" if alias else f"projects/{owner}__{name}.md"


# In a real run each promotion is written to disk before the next, so
# next_id() re-reading the file sees prior IDs. Under --dry-run nothing is
# written, so two proposals targeting the SAME (new or shared) project file
# would both preview the same id — a misleading preview for the very command
# the docs recommend for checking a batch. Track previewed promotions per
# file so the dry-run count matches what a real run would assign.
_DRY_PENDING: dict[str, int] = {}


def next_id(path):
    base = 0
    if os.path.exists(path):
        ids = [int(i[1:]) for i in ID_RE.findall(read(path))]
        base = max(ids) if ids else 0
    return base + (_DRY_PENDING.get(path, 0) if DRY else 0) + 1


def title_from(fname):
    return os.path.basename(fname)[12:-3].replace("-", " ").replace("__", " ")


def promote(fname, fields, index_line, text):
    rel = project_file(fields)
    if not rel:
        return [f"project: cannot parse Project field "
                f"'{field(fields, 'project')}' into <owner>/<repo>"]
    ppath = os.path.join(ROOT, rel)
    if os.path.exists(ppath):
        ptext = read(ppath)
    else:
        proj = field(fields, "project")
        ptext = (f"# {proj} — lessons\n\nProject: {proj}. Newest first.\n"
                 "\n---\n")
    eid = f"E{next_id(ppath)}"
    if DRY:
        _DRY_PENDING[ppath] = _DRY_PENDING.get(ppath, 0) + 1
    body_fields = []
    started = False
    for line in text.splitlines():
        if line.strip().startswith("- ID:"):
            started = True
            continue
        if line.strip().upper().startswith("##") and "PROPOSED INDEX LINE" in line.upper():
            break
        if started and (line.startswith("- ") or line.startswith("  ")):
            body_fields.append(line)
    sbx = sandbox_name(fields)
    sbx_src = os.path.join(ROOT, "incoming", sbx) if sbx else ""
    move_sbx = bool(sbx and SANDBOX_NAME_RE.match(sbx) and os.path.isfile(sbx_src))
    if move_sbx:
        body_fields = [f"- Sandbox: {SANDBOX_DIR}/{sbx}"
                       if FIELD_RE.match(l) and FIELD_RE.match(l).group(1)
                       .strip().lower() == "sandbox" else l
                       for l in body_fields]
    if not body_fields:
        # never write a heading-only entry into canon (opticon#E28's damage)
        return ["promote: captured body is EMPTY — check the '- ID:' bullet "
                "and field formatting; refusing a lossy promotion"]
    entry = f"## {eid} — {title_from(fname)}\n" + "\n".join(body_fields) + "\n"

    if "\n---\n" in ptext:
        head, _, tail = ptext.partition("\n---\n")
        write(ppath, f"{head}\n---\n\n{entry}\n{tail.lstrip()}")
    else:
        write(ppath, ptext.rstrip() + "\n\n---\n\n" + entry)

    lesson = INDEX_RE.match(index_line)
    lesson_text = lesson.group(1) if lesson else index_line
    pit = os.path.join(ROOT, "PITFALLS.md")
    write(pit, read(pit).rstrip() + "\n- " + lesson_text.lstrip("- ").strip()
          + f" → {rel}#{eid}\n")
    if not DRY:
        os.remove(os.path.join(ROOT, "incoming", fname))
        if move_sbx:
            os.makedirs(os.path.join(ROOT, SANDBOX_DIR), exist_ok=True)
            os.replace(sbx_src, os.path.join(ROOT, SANDBOX_DIR, sbx))
    print(f"  ✓ promoted → {rel}#{eid}"
          + (f" (sandbox → {SANDBOX_DIR}/{sbx})" if move_sbx else ""))
    return []


def main():
    d = os.path.join(ROOT, "incoming")
    promoted, held, skipped = 0, 0, 0
    for fname in sorted(os.listdir(d)):
        if not fname.endswith(".md") or fname in ("README.md", "TEMPLATE.md",
                                                  "stubs.md"):
            continue
        path = os.path.join(d, fname)
        text = read(path)
        if HOLD_MARKER_RE.search(text):
            skipped += 1
            continue
        print(f"{fname}:")
        fields, index_line = parse(text)
        if is_review(text):
            reasons = check_review(fields, text)
            if not reasons:
                reasons = apply_review(fname, fields)
        else:
            reasons = check(fields, index_line, text) + sandbox_hold_reasons(fields)
            for w in sandbox_warnings(fields):
                print(f"  ⚠ WARN: {w}")
            if not reasons:
                reasons = promote(fname, fields, index_line, text)
        if reasons:
            held += 1
            for r in reasons:
                print(f"  ✗ HOLD: {r}")
            block = ("\n\n<!-- STEWARD HOLD (auto, " + date.today().isoformat()
                     + ")\nreasons:\n"
                     + "\n".join(f"- {r}" for r in reasons)
                     + "\nfix and delete this block to resubmit -->\n")
            write(path, text + block)
        else:
            promoted += 1
    print(f"\npromoted {promoted} · held {held} · previously-held {skipped}"
          + (" [DRY RUN — nothing written]" if DRY else ""))
    if promoted:
        # write each promotion back to the entries it composes (`- Cited-by:`
        # lines, scripts/cited_by.py): the cited entry gains the new lesson's
        # sandbox and result without anyone editing it by hand
        out = subprocess.run([sys.executable,
                              os.path.join(ROOT, "scripts", "cited_by.py")]
                             + (["--dry-run"] if DRY else []),
                             capture_output=True, text=True)
        print(out.stdout.strip() or out.stderr.strip())
    validator = os.path.join(ROOT, "scripts", "validate.py")
    if promoted and not DRY and os.path.exists(validator):
        out = subprocess.run([sys.executable, validator],
                             capture_output=True, text=True)
        print(out.stdout.strip())
        if out.returncode != 0:
            print("post-promotion validation FAILED — inspect before pushing",
                  file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
