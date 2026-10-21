"""Sandbox for ideas:PRESENTATION/data-ink-ratio-cut-chartjunk, ideas:PRESENTATION/show-real-output-as-evidence-not-just-claims
and sandbox-empathy-map-density-hides-evidence-gap/E1 (a density-style proxy cannot see provenance).
PREDICTION (before first run): real SVG bar charts are generated from a 24-line request log (the 'real artifact').
 1) A chartjunk version (3D side faces, shadows, gridlines every unit, icons) has data-ink ratio < 0.5; stripping decoration
    lifts it above 0.85 while the values a reader recovers from the SVG stay identical.
 2) A stripped chart drawn from FABRICATED numbers has exactly the same data-ink ratio as the stripped real one (delta 0),
    but recomputing the values from the shown log flags it (max error >= 20 ms); the real chart's error is 0.
 3) Break case: stripping 'decoration' too far - removing the gridlines AND the value labels - leaves the ink ratio at ~1.0 but
    the recoverable values become undefined (no calibration), so the ratio rewards an unreadable chart.
Stdlib only, deterministic."""
import re
LOG = []   # (service, latency_ms), 24 deterministic lines
for i in range(24):
    svc = ('auth', 'search', 'cart')[i % 3]
    LOG.append((svc, {'auth': 40, 'search': 120, 'cart': 75}[svc] + (i * 7) % 11 - 5))
def means(log):
    out = {}
    for s, v in log: out.setdefault(s, []).append(v)
    return {s: sum(v) / len(v) for s, v in out.items()}
REAL = means(LOG)
FAKE = {'auth': 38.0, 'search': 90.0, 'cart': 70.0}     # plausible but fabricated
YMAX, H, X0 = 150, 150, 30
def chart(vals, junk=False, labels=True, grid=True):
    els = []      # (kind, svg, ink, is_data)
    for k, v in enumerate(vals.items()):
        name, val = v; x = X0 + k * 60; h = val * H / YMAX; y = H - h
        els.append(('bar', f'<rect class="bar" data-v="{val:.2f}" x="{x}" y="{y:.2f}" width="40" height="{h:.2f}"/>', 2 * (40 + h), True))
        if labels: els.append(('label', f'<text class="vl" x="{x}" y="{y-2:.2f}">{val:.1f}</text>', 6 * 5, True))
        els.append(('cat', f'<text class="cat" x="{x}" y="{H+12}">{name}</text>', 6 * len(name), True))
        if junk:
            els.append(('side3d', f'<polygon class="d3" points="{x+40},{y:.2f} {x+48},{y-6:.2f}"/>', 2 * (8 + h), False))
            els.append(('shadow', f'<rect class="shadow" x="{x+4}" y="{y+4:.2f}" width="40" height="{h:.2f}"/>', 2 * (40 + h), False))
            els.append(('icon', f'<circle class="icon" cx="{x+20}" cy="{H+30}" r="8"/>', 50, False))
    if grid:
        for g in range(0, YMAX + 1, 10 if junk else 50):
            els.append(('grid', f'<line class="grid" y="{H - g * H / YMAX:.2f}" x2="200" data-y="{g}"/>', 200, bool(not junk and g % 50 == 0) and not junk))
    return els
def ratio(els): return sum(e[2] for e in els if e[3]) / sum(e[2] for e in els)
def recover(els):
    svg = ' '.join(e[1] for e in els)
    cats = re.findall(r'class="cat"[^>]*>(\w+)<', svg)
    vl = re.findall(r'class="vl"[^>]*>([\d.]+)<', svg)
    if vl: return dict(zip(cats, map(float, vl)))                              # read printed values
    if 'class="grid"' in svg:                                                  # calibrate bar height against labelled gridlines
        return {c: float(h) * YMAX / H for c, h in zip(cats, re.findall(r'class="bar"[^>]*height="([\d.]+)"', svg))}
    return None                                                                # nothing to calibrate against
def err(rec, truth): return None if rec is None else max(abs(rec[k] - truth[k]) for k in truth)
junk = chart(REAL, junk=True); clean = chart(REAL); fake = chart(FAKE); bare = chart(REAL, labels=False, grid=False)
r_junk, r_clean, r_fake, r_bare = map(ratio, (junk, clean, fake, bare))
rec_junk, rec_clean = recover(junk), recover(clean)
same_vals = rec_junk is not None and all(abs(rec_junk[k] - rec_clean[k]) < 0.06 for k in rec_clean)
e_real, e_fake, e_bare = err(recover(clean), REAL), err(recover(fake), REAL), err(recover(bare), REAL)
print('ratios junk %.2f clean %.2f fake %.2f bare %.2f' % (r_junk, r_clean, r_fake, r_bare))
print('values preserved after strip', same_vals, '| err real %s fake %.1f bare %s' % (e_real, e_fake, e_bare))
ok = r_junk < 0.5 and r_clean > 0.85 and same_vals and abs(r_clean - r_fake) < 1e-9 and e_real is not None and e_real < 0.06 and e_fake >= 20 and e_bare is None and r_bare > 0.99
print('RESULT: %s data-ink ratio junk %.2f -> clean %.2f with values preserved; fabricated chart has identical ratio %.2f but %.0f ms error against the log; over-stripped chart ratio %.2f with values unrecoverable' % ('PASS' if ok else 'FAIL', r_junk, r_clean, r_fake, e_fake, r_bare))
