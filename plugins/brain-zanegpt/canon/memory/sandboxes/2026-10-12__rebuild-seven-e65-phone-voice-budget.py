"""Rebuild of seven E65 (on phone speakers the voice budget is the one-place 2 'whatever the mixing';
headphones 5). Own fixture: talk share p = 0.15/0.25/0.4/0.55 (E65 fixed 0.4), and the phone also
modelled with mixing that DOES act on one speaker: ducking (all voices but one dropped by 12 dB,
treated as a masker only while the lead voice is silent) and turn-taking (voices scripted not to
overlap, as a director would), plus headphone widths 45/60/90.
Predictions written before running:
 P1 the phone one-place budget is 2 at every p (expect MISS: it is a p readout).
 P2 'whatever the mixing': with ducking or turn-taking the phone budget stays 2 (expect MISS).
 P3 headphones beat the phone at every p and width (expect hold).
"""

def one_place(p):
    b = 0
    for n in range(1, 60):
        if (1 - p) ** (n - 1) >= 0.5: b = n
        else: break
    return b

def headphones(p, w):
    b = 0
    for n in range(1, 60):
        step = 360 / n
        m = sum(1 for k in range(1, n) if min(k * step, 360 - k * step) <= w + 1e-9)
        if (1 - p) ** m >= 0.5: b = n
        else: break
    return b

def ducked(p):
    # one lead voice lands fully; the rest are texture by design. Words that must land: the lead's.
    return float("inf")  # budget not bounded by masking of the lead

def turn_taking(p):
    # scripted non-overlap: n voices fit while total talk time n*p <= 1
    return int(1 // p)

rows = {}
for p in (0.15, 0.25, 0.4, 0.55):
    rows[p] = dict(phone=one_place(p), turns=turn_taking(p), hp={w: headphones(p, w) for w in (45, 60, 90)})
    print(f"p={p}: phone one-place {rows[p]['phone']}; phone with scripted turns {rows[p]['turns']}; phone with ducking: lead always lands; "
          f"headphones w45/60/90 {rows[p]['hp'][45]}/{rows[p]['hp'][60]}/{rows[p]['hp'][90]}")
p1 = all(r["phone"] == 2 for r in rows.values())
p2 = all(r["turns"] == 2 for r in rows.values())
p3 = all(min(r["hp"].values()) > r["phone"] for r in rows.values())
checks = [("P1 phone budget 2 at every p", p1), ("P2 mixing cannot raise the phone budget", p2), ("P3 headphones always beat the phone", p3)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 3 else 'FAIL'} {held}/3; phone budget p0.15/0.25/0.4/0.55 " +
      "/".join(str(rows[p]['phone']) for p in rows) + "; scripted turns " + "/".join(str(rows[p]['turns']) for p in rows) +
      "; headphones w90 " + "/".join(str(rows[p]['hp'][90]) for p in rows))
