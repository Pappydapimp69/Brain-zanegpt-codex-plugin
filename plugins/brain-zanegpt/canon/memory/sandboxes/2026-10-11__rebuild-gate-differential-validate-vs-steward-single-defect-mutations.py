"""Rebuild of gate-differential/E1, own fixture. PREDICTION (written before first run): over 16 single-defect mutations of one
good proposal (fixture is mine, not the original's), a clean base is accepted by both gates; S (steward dry run) and V
(validate.py) DISAGREE on at least 3 mutations, at least one with S-stricter and at least one with V-stricter (V alone
catches a committed secret-like token; S alone catches thin/negated-provenance fields), so neither accepted set contains
the other. Runs the real scripts on a scratch copy of the memory repo; stdlib only."""
import os, re, shutil, subprocess, sys, tempfile
SRC = os.environ.get("MEMORY_REPO", "/home/user/memory")
tmp = tempfile.mkdtemp(prefix="gatediff_")
R = os.path.join(tmp, "m")
shutil.copytree(SRC, R, symlinks=True)
inc = os.path.join(R, "incoming")
for f in os.listdir(inc):
    if f not in ("README.md", "TEMPLATE.md", "stubs.md"):
        os.remove(os.path.join(inc, f))
GOOD = """## FULL ENTRY

- ID: E? (steward assigns the real id on promotion)
- Date: 2026-10-11
- Project: local/gatediff-fixture-zeta
- Tags: [testing][gates]
- What: A fixture lesson about a ring buffer that drops its oldest sample when the writer laps the reader by one full turn.
- Why built: To see whether a lap counter or a fill flag is the safer way to tell a full buffer from an empty one.
- Design: Capacity 8, a writer index and a reader index, both advancing modulo 8, plus a separate lap counter for each.
- Got right: The lap counter distinguished full from empty in all 24 interleavings of pushes and pops that were tried.
- Where/why it failed: Comparing indices alone read a full buffer as empty after exactly 8 consecutive pushes without a pop.
- Fix: Compare index and lap together so equal indices with different laps mean full, equal laps mean empty.
- Why this fix: The pair of values is a total order over the buffer states, so no state is ambiguous.
- Rule of thumb: Equal read and write indices are ambiguous in a ring buffer; carry one extra bit of lap state to tell full from empty.
- Provenance (verified/assumed): Verified first-hand by running the fixture simulation over the interleavings listed above.
- Link: scratch session fixture

## PROPOSED INDEX LINE

`[testing][gates]` Equal ring-buffer indices are ambiguous; carry a lap bit to tell full from empty → projects/local__gatediff-fixture-zeta.md#E?
"""
def sub(old, new):
    def f(t):
        assert old in t, old
        return t.replace(old, new, 1)
    return f
MUT = [
 ("clean", lambda t: t),
 ("what_na", sub("- What: A fixture lesson about a ring buffer that drops its oldest sample when the writer laps the reader by one full turn.", "- What: n/a")),
 ("link_missing", sub("- Link: scratch session fixture\n", "")),
 ("prov_assumed_only", sub("Verified first-hand by running the fixture simulation over the interleavings listed above.", "assumed only, from reading the buffer code")),
 ("prov_not_verified", sub("Verified first-hand by running the fixture simulation over the interleavings listed above.", "This was not verified by any run at all.")),
 ("secret_token", sub("- Link: scratch session fixture", "- Link: scratch session fixture ghp_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8")),
 ("index_wrapped", sub("carry a lap bit to tell full from empty →", "carry a lap bit\nto tell full from empty →")),
 ("index_no_backticks", sub("`[testing][gates]` Equal", "[testing][gates] Equal")),
 ("polarity_incompat_no_composed", sub("- Link:", "- Polarity: incompatible\n- Link:")),
 ("polarity_bogus", sub("- Link:", "- Polarity: maybe\n- Link:")),
 ("unindented_continuation", sub("- Why built: To see whether a lap counter or a fill flag is the safer way to tell a full buffer from an empty one.", "- Why built: To see whether\na lap counter or a fill flag is the safer way to tell a full buffer from an empty one.")),
 ("sandbox_bad_name", sub("- Link:", "- Sandbox: my sandbox.py\n- Link:")),
 ("tags_uppercase", sub("- Tags: [testing][gates]", "- Tags: [Testing][GATES]")),
 ("id_missing", sub("- ID: E? (steward assigns the real id on promotion)\n", "")),
 ("composed_nonexistent", sub("- Link:", "- Composed: no-such-slug-anywhere/E9\n- Link:")),
 ("date_malformed", sub("- Date: 2026-10-11", "- Date: 11/10/2026")),
]
NAME = "2026-10-11__gatediff-fixture-zeta.md"
def run(cmd):
    return subprocess.run([sys.executable] + cmd, cwd=R, capture_output=True, text=True)
def gates(text):
    for f in os.listdir(inc):
        if f not in ("README.md", "TEMPLATE.md", "stubs.md"): os.remove(os.path.join(inc, f))
    p = os.path.join(inc, NAME); open(p, "w").write(text)
    s = run(["scripts/steward.py", "--dry-run"]).stdout
    s_rej = "HOLD" in s.split(NAME + ":", 1)[-1].split("promoted")[0]
    v = run(["scripts/validate.py"])
    v_rej = any(NAME in l and "✗" in l for l in (v.stdout + v.stderr).splitlines())
    return s_rej, v_rej
rows = []
for name, fn in MUT:
    s_rej, v_rej = gates(fn(GOOD))
    rows.append((name, s_rej, v_rej)); print("%-30s S_reject=%-5s V_reject=%-5s" % (name, s_rej, v_rej), flush=True)
shutil.rmtree(tmp, ignore_errors=True)
Sx = [n for n, s, v in rows if s and not v]; Vx = [n for n, s, v in rows if v and not s]
both = [n for n, s, v in rows if s and v]; ok_both = [n for n, s, v in rows if not s and not v]
clean_ok = rows[0][1:] == (False, False)
ok = clean_ok and len(Sx) + len(Vx) >= 3 and Sx and Vx
print("S-stricter", len(Sx), Sx); print("V-stricter", len(Vx), Vx)
print("RESULT: %s clean base accepted=%s; S-stricter %d, V-stricter %d, both reject %d, both accept %d (incl clean) over %d cases" % ("PASS" if ok else "FAIL", clean_ok, len(Sx), len(Vx), len(both), len(ok_both), len(rows)))
