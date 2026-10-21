"""Sandbox: do 'what' comments (restating code) go stale more than 'why' comments?
Real python source is generated, mutated, and audited with tokenize/ast. Deterministic."""
import io, re, tokenize, ast

CONSTS = {"RETRY_LIMIT": 3, "TIMEOUT_S": 30, "PAGE_SIZE": 50, "CACHE_TTL": 300, "MAX_BATCH": 100, "BACKOFF_MS": 250}
WHY = {  # rationale keyed to a premise id, deliberately free of the literal value
    "RETRY_LIMIT": "upstream drops about one call in ten, so several tries beat failing the user",
    "TIMEOUT_S": "the vendor SLA caps a slow response, we stop waiting past it",
    "PAGE_SIZE": "the mobile client renders one screenful at a time",
    "CACHE_TTL": "prices change on a slow schedule, stale-by-minutes is acceptable",
    "MAX_BATCH": "the bulk endpoint rejects bodies over its payload limit",
    "BACKOFF_MS": "short enough to feel responsive, long enough to let a restart finish",
}

def build(consts, style):
    out = []
    for k, v in consts.items():
        c = f"# set {k.lower().replace('_',' ')} to {v}" if style == "what" else f"# why: {WHY[k]}"
        out += [c, f"{k} = {v}"]
    return "\n".join(out) + "\n"

def audit(src):
    """Mechanical checker: a comment is flagged stale if it embeds a number that differs from the next assignment."""
    toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    comments = {t.start[0]: t.string for t in toks if t.type == tokenize.COMMENT}
    vals = {}
    for n in ast.parse(src).body:
        vals[n.lineno] = n.value.value
    flagged = 0
    for ln, c in comments.items():
        nums = re.findall(r"\d+", c)
        if nums and int(nums[0]) != vals[ln + 1]:
            flagged += 1
    return flagged

def mutate_values(consts):
    return {k: v * 2 + 1 for k, v in consts.items()}

def true_stale(style, value_changed, premise_changed):
    # ground truth: what-comment is wrong iff value changed; why-comment wrong iff premise changed
    n = len(CONSTS)
    return n if (style == "what" and value_changed) or (style == "why" and premise_changed) else 0

rows = []
for name, vc, pc in [("value-only refactor", True, False),
                     ("premise-only change (BREAK: value identical)", False, True),
                     ("both change", True, True)]:
    for style in ("what", "why"):
        consts = mutate_values(CONSTS) if vc else dict(CONSTS)
        # comments were written against the ORIGINAL code; code is mutated afterwards
        stale_src = build(CONSTS, style).splitlines()
        new_src = build(consts, style).splitlines()
        merged = []
        for i in range(0, len(stale_src), 2):
            merged += [stale_src[i], new_src[i + 1]]
        flagged = audit("\n".join(merged) + "\n")
        truth = true_stale(style, vc, pc)
        rows.append((name, style, truth, flagged))
        print(f"{name:48s} {style:4s} truly_stale={truth} checker_flagged={flagged}")

d = {(r[0], r[1]): r for r in rows}
a = d[("value-only refactor", "what")]; b = d[("value-only refactor", "why")]
c = d[("premise-only change (BREAK: value identical)", "why")]
ok = (a[2] == 6 and a[3] == 6 and b[2] == 0 and b[3] == 0 and c[2] == 6 and c[3] == 0)
print("RESULT:", "PASS" if ok else "FAIL",
      f"value-only: what-comments stale {a[2]}/6 (checker caught {a[3]}), why-comments {b[2]}/6; "
      f"premise-only: why-comments stale {c[2]}/6 but checker caught {c[3]}")
