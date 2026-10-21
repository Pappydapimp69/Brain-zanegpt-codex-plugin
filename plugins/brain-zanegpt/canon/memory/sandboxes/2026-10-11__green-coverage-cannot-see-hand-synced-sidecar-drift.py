"""Sandbox (train edge): collective-reference/E1 (derive the label map, test
end-to-end on the real artifact) x sandbox-brain-selftest-coverage/E1 (a green
suite and coverage follow what tests name, not what is old and important).
Toy intake: FORM text defines id/label pairs; a body renders '### label' blocks;
parse(body, label_map) fills ids. Sidecar = hand-kept label map.
Mutations: rename one label in the form (drift), or rename one id (BREAK).
Suites: UNIT (fixture body typed from the sidecar), E2E (body built from the
real FORM text), each with sidecar or derived map. Coverage = fraction of
parse/lookup lines executed under sys.settrace by the unit suite."""
import sys, re

FORM = """\
- id: title
  label: Title of lesson
- id: tags
  label: Tags (bracketed)
- id: what
  label: What happened
- id: fix
  label: Fix applied
- id: rule
  label: Rule of thumb
- id: prov
  label: Provenance
"""
SIDECAR = {"Title of lesson": "title", "Tags (bracketed)": "tags", "What happened": "what",
           "Fix applied": "fix", "Rule of thumb": "rule", "Provenance": "prov"}

def pairs(form):
    out, cur = [], None
    for ln in form.splitlines():
        m = re.match(r"- id: (\S+)", ln)
        if m: cur = m.group(1)
        m = re.match(r"\s+label: (.+)", ln)
        if m: out.append((cur, m.group(1)))
    return out

def derive_label_map(form):
    return {lab: i for i, lab in pairs(form)}

def render(form):
    return "".join(f"### {lab}\n\nvalue-{i}\n\n" for i, lab in pairs(form))

def parse(body, label_map):
    got = {}
    for lab, val in re.findall(r"### (.+)\n\n(.+)\n", body):
        key = label_map.get(lab)
        if key:
            got[key] = val
    return got

def rename_label(form, i):
    return form.replace(pairs(form)[i][1], pairs(form)[i][1] + " v2", 1)
def rename_id(form, i):
    return form.replace("id: " + pairs(form)[i][0], "id: " + pairs(form)[i][0] + "_x", 1)

CONSUMER_KEYS = [i for i, _ in pairs(FORM)]  # downstream code keyed to the ORIGINAL ids

def unit_ok(label_map):  # fixture typed from the sidecar, not from the form
    body = "".join(f"### {lab}\n\nvalue-{i}\n\n" for lab, i in SIDECAR.items())
    return set(parse(body, label_map)) == set(SIDECAR.values())
def e2e_ok(form, label_map):  # body rendered from the real form text
    return set(parse(render(form), label_map)) == {i for i, _ in pairs(form)}
def consumer_ok(form, label_map):  # downstream still gets the ids it is keyed to
    return set(CONSUMER_KEYS) <= set(parse(render(form), label_map))

# coverage of parse() by the unit suite under a line tracer
hit = set()
def tr(frame, ev, arg):
    if frame.f_code is parse.__code__ and ev == "line": hit.add(frame.f_lineno)
    return tr
sys.settrace(tr); unit_ok(SIDECAR); sys.settrace(None)
code = parse.__code__
lines = {l for _, _, l in code.co_lines() if l and l != code.co_firstlineno}
cov = len(hit) / len(lines)

n = len(pairs(FORM))
unit_detect = e2e_detect = derived_fail = 0
for i in range(n):
    f = rename_label(FORM, i)
    unit_detect += (not unit_ok(SIDECAR))                 # sidecar fixture still passes
    e2e_detect += (not e2e_ok(f, SIDECAR))                # real-form e2e sees the drop
    derived_fail += (not e2e_ok(f, derive_label_map(f)))  # derived map follows the form
id_break = sum(1 for i in range(n)
               if e2e_ok(rename_id(FORM, i), derive_label_map(rename_id(FORM, i)))
               and not consumer_ok(rename_id(FORM, i), derive_label_map(rename_id(FORM, i))))
print(f"parse() line coverage by unit suite {cov:.0%}; unit suite green on baseline {unit_ok(SIDECAR)}")
print(f"label drift x{n}: unit detects {unit_detect}, e2e(real form)+sidecar detects {e2e_detect}, derived map fails {derived_fail}")
print(f"BREAK id rename x{n}: derived e2e green but consumer loses its key in {id_break}")
ok = cov == 1.0 and unit_detect == 0 and e2e_detect == n and derived_fail == 0 and id_break == n
print(f"RESULT: {'PASS' if ok else 'FAIL'} coverage {cov:.0%} unit-detect {unit_detect}/{n} e2e-detect {e2e_detect}/{n} derived-fail {derived_fail}/{n} id-rename-silent {id_break}/{n}")
