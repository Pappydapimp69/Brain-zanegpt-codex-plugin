"""Sandbox: a quarantine skip (memory/E10) plus a weak presence check (sandbox-edges/E48) -- do they stack?
Deterministic, stdlib only. 22 held proposals, defects assigned by index (no RNG).
PREDICTION (before first run): skip-validator reports 0 errors on the 22 held files; after fixing only the
first-failure reason (schema) and lifting holds, exactly the 4 files with a bad filename fail (second failure);
running cheap structural checks on held files reports all 4 before release; a weak non-empty check on the
`Why this fix` field lets the 5 placeholder-text files pass even after release, while a minimum-substance
check catches all 5 -- i.e. the two blind spots stack: release is clean yet 5 defects survive."""
import re
N = 22
files = []
for i in range(N):
    bad_schema = True                      # why they were held: first failure
    bad_name = i % 6 == 0                  # 0,6,12,18 -> 4 files
    placeholder = i % 5 == 1               # 1,6,11,16,21 -> 5 files (6 overlaps bad_name)
    files.append(dict(i=i, held=True, schema_ok=not bad_schema,
                      name=("proposal%d.md" % i) if bad_name else "2026-09-14__p%d.md" % i,
                      why_fix=("n/a" if placeholder else "A long concrete reason this fix was chosen over alternatives."),
                      ph=placeholder))
NAME = re.compile(r"^\d{4}-\d\d-\d\d__.+\.md$")
def full_check(f):
    errs = []
    if not f["schema_ok"]: errs.append("schema")
    if not NAME.match(f["name"]): errs.append("name")
    if len(f["why_fix"]) < 30: errs.append("thin")
    return errs
def weak_check(f):                         # presence only, as in E48's plausible-non-empty assertion
    errs = []
    if not f["schema_ok"]: errs.append("schema")
    if not NAME.match(f["name"]): errs.append("name")
    if not f["why_fix"]: errs.append("empty")
    return errs
def validate(fs, check, skip_held):
    return sum(len(check(f)) > 0 for f in fs if not (skip_held and f["held"]))
fails = []
# S1 skip-validator on held files
s1 = validate(files, full_check, True); print("S1 skip-validator errors on 22 held:", s1)
if s1 != 0: fails.append("S1")
# S2 fix schema (the only reason ever seen), lift holds, run the weak check
for f in files: f["schema_ok"] = True; f["held"] = False
s2 = validate(files, weak_check, True); print("S2 after release, weak check errors:", s2, "(names only)")
if s2 != 4: fails.append("S2")
# S3 cheap structural checks run on held files BEFORE release
for f in files: f["held"] = True; f["schema_ok"] = False
pre = sum(1 for f in files if not NAME.match(f["name"])); print("S3 pre-release structural tally:", pre)
if pre != 4: fails.append("S3")
# S4 BREAK: after fixing names too, weak check goes green while full check still sees placeholders
for f in files:
    f["held"] = False; f["schema_ok"] = True; f["name"] = "2026-09-14__p%d.md" % f["i"]
weak = validate(files, weak_check, True); full = validate(files, full_check, True)
print(f"S4 all names fixed: weak-check errors {weak}, full-check errors {full}")
if not (weak == 0 and full == 5): fails.append("S4")
# S5 hold block records only the first gate that refused
first = {tuple(full_check(dict(f, schema_ok=False))[:1]) for f in files}
print("S5 distinct hold reasons recorded:", sorted(first), "vs real defect kinds: schema,name,thin")
if first != {("schema",)}: fails.append("S5")
print("RESULT: " + ("FAIL " + ",".join(fails) if fails else
      "PASS skip hides 4 name defects (0 seen, 4 after release); weak check hides 5 placeholders even after release; pre-release structural tally finds 4"))
