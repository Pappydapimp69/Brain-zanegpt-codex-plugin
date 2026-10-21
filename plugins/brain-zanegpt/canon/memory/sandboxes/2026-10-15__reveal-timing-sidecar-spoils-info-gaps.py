"""Information-gap reveals vs a hand-kept timing sidecar, on a real film script.
Input: the Five Days scene script (v9talk_snapshot.js): each scene's narration
lines [text, hold] and its reveal marks anchored as c[k]+offset (k = the line that
opens the gap the reveal closes). Narration time per line = max(hold, 1 + words/2.6)
as the engine sizes captions. Two schedules for the reveals:
  DERIVED  - reveal time = start of its anchor line + offset (what the engine does)
  SIDECAR  - absolute times frozen from the original script, kept by hand
Edit: lengthen ONE line by N words (a typical rewrite), for every line in turn.
A reveal is SPOILED if it fires before its anchor line starts (gap closed before
it is opened). Deterministic: no RNG.
PREDICTION (written before running): DERIVED spoils 0 reveals for any edit; SIDECAR
spoils at least one reveal for most single-line edits of +8 words."""
import re, sys
SRC = sys.argv[1] if len(sys.argv) > 1 else "2026-10-15__reveal-timing-sidecar-spoils-info-gaps.fixture.js"
src = open(SRC).read()
scenes = []
for blk in re.split(r"\nscene\(", src)[1:]:
    name = re.search(r"name:'([^']+)'", blk).group(1)
    lines_part = "[" + re.search(r"lines:\[(.*?)\]\],\s*\n\s*marks", blk, re.S).group(1) + "]"
    lines = []
    for item, h in re.findall(r'\[("(?:[^\]]*?)),\s*([\d.]+)(?:,\d+)?\]', lines_part):
        text = re.sub(r'"\s*\+\s*[^"]+?\s*\+\s*"', " X ", item).replace('"', "")   # an inserted number = one word
        lines.append((text, float(h)))
    marks = [(int(k), float(o or 0)) for k, o in re.findall(r"\[c\[(\d)\](?:\+([\d.]+))?,'", blk)]
    scenes.append((name, lines, marks))
need = lambda text, hold, extra=0: max(hold, 1 + (len(text.split()) + extra) / 2.6)
def starts(lines, edit=None, extra=0):
    t, out = 0.0, []
    for i, (txt, h) in enumerate(lines):
        out.append(t); t += need(txt, h, extra if i == edit else 0)
    return out
tot_edits = sidecar_bad_edits = derived_spoils = sidecar_spoils = 0
for name, lines, marks in scenes:
    base = starts(lines)
    frozen = [base[k] + o for k, o in marks]
    for e in range(len(lines)):
        new = starts(lines, e, 8)
        d = sum(new[k] + o < new[k] for k, o in marks)
        s = sum(f < new[k] for f, (k, o) in zip(frozen, marks))
        tot_edits += 1; derived_spoils += d; sidecar_spoils += s; sidecar_bad_edits += s > 0
    print(f"{name:20s} lines {len(lines)} reveals {len(marks)}")
# break attempt: SHORTEN each line by 8 words instead. A frozen reveal can then only
# come LATE (the gap is held after the line resolved it), never early.
late = early = 0
for name, lines, marks in scenes:
    base = starts(lines); frozen = [base[k] + o for k, o in marks]
    for e in range(len(lines)):
        new = starts(lines, e, -8)
        early += sum(f < new[k] for f, (k, o) in zip(frozen, marks))
        late += sum(f > new[k] + o + 0.5 for f, (k, o) in zip(frozen, marks))
print(f"single-line -8-word edits: SIDECAR early (spoiled) {early}, late by >0.5 s {late}")
print(f"single-line +8-word edits: {tot_edits}; DERIVED spoiled reveals {derived_spoils}; "
      f"SIDECAR spoiled reveals {sidecar_spoils}, in {sidecar_bad_edits}/{tot_edits} edits")
ok = derived_spoils == 0 and sidecar_bad_edits > tot_edits / 2
print(f"RESULT: {'PASS' if ok else 'FAIL'} derived 0 spoils: {derived_spoils == 0}; sidecar spoiled at least one reveal "
      f"in {sidecar_bad_edits}/{tot_edits} single-line edits ({sidecar_spoils} reveals)")
