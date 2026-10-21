"""Sandbox: empathy-map fill source vs map accuracy, and whether a simulation
exercise masks the "sparse map = missing data" alarm.

PROVENANCE NOTE (read first): this is a MODEL. It encodes assumptions (imagined
content is projected from the designer's own items; interviews voice held
statements with a fixed probability; a simulation exercise yields vivid items
that skip corroboration). It shows what FOLLOWS from those assumptions and
where the conclusion stops holding. It says nothing about how real designers
or real users behave; the human findings live in the cited sources.

PREDICTION (written before the first run; could come out wrong):
 P1 density is blind to evidence: an imagined map (designer overlap 0.25) fills
    all 4 quadrants (alarms=0) with precision <= 0.40, while a representative
    N=12 interview map also has alarms=0 with precision >= 0.90; at N=2 the
    interview map raises the sparse alarm in >= 3 of 4 quadrants; total
    density is non-decreasing in N over N in 0,2,4,...,24.
 P2 simulation masks sparseness: at N=3, sim success rate rho=0.25, adding the
    exercise drops alarms from >=3 to 0 while raising false assertions by >= 6
    and leaving precision < 0.50; at N=24 the exercise changes false assertions
    by <= 1 (corroborated evidence outranks vividness).
 BREAKERS: B1 designer overlap 1.0 -> imagined precision >= 0.90 (claim does
    not apply when designer == user); B2 convenience sample (colleagues) at
    N=12, overlap 0.25 -> alarms=0 but precision <= 0.50 (an interview map is
    only as good as its sample); B3 rho=1.0 at N=3 -> false assertions <= 1
    (the exercise is not harmful per se; harm depends on its fidelity).
"""
import hashlib

Q, M, CORE = 4, 12, 4          # quadrants, candidate statements/quadrant, true core size/quadrant
CAP = 4                        # map slots per quadrant
USERS, SEGA = 200, 20          # population; first SEGA users are "colleagues" (designer-like segment)
VOICE_Q = 0.5                  # prob an interviewee voices a statement they hold
CORROB = 2                     # interviewees needed to put an item on the map
VIVID = 2.5                    # salience bonus (in interview-count units) of a simulated item
SIM_PER_Q = 3                  # vivid items a simulation yields per quadrant
SPARSE_BELOW = 2               # quadrant with fewer items than this raises the alarm
IMAG_PROJ = 0.7                # imagined map: share drawn from designer's own items

def u(*tag):
    h = hashlib.sha256("|".join(map(str, tag)).encode()).digest()
    return int.from_bytes(h[:8], "big") / 2**64

def world(overlap_n):
    """overlap_n in 0..CORE = how many of the designer's own items per quadrant
    coincide with the population core. Returns (core_set, designer_items, holds)."""
    core, design = set(), set()
    for q in range(Q):
        c = [(q, i) for i in range(CORE)]          # population core = first CORE statements
        core.update(c)
        d = c[:overlap_n] + [(q, CORE + i) for i in range(CORE - overlap_n)]
        design.update(d)
    holds = {}
    for j in range(USERS):
        mine = design if j < SEGA else core
        holds[j] = {(q, i) for q in range(Q) for i in range(M)
                    if u("hold", j, q, i) < (0.8 if (q, i) in mine else 0.08)}
    # TRUTH is measured on the population, not assumed
    truth = {s for q in range(Q) for i in range(M) for s in [(q, i)]
             if sum(s in holds[j] for j in range(USERS)) / USERS >= 0.5}
    return truth, design, holds

def sample(kind, n):
    if n == 0: return []
    if kind == "representative":
        return [int(k * USERS / n) for k in range(n)]
    return list(range(n))          # convenience: the first n users = colleagues

def interview_counts(holds, ids):
    cnt = {}
    for j in ids:
        for s in holds[j]:
            if u("voice", j, *s) < VOICE_Q:
                cnt[s] = cnt.get(s, 0) + 1
    return cnt

def build_map(cnt, sim_items):
    """per quadrant: top CAP by score, each must have score >= CORROB
    (a simulated item carries VIVID >= CORROB, so it needs no corroboration)."""
    out = set()
    for q in range(Q):
        cand = {}
        for (qq, i), c in cnt.items():
            if qq == q: cand[(qq, i)] = cand.get((qq, i), 0) + c
        for s in sim_items:
            if s[0] == q: cand[s] = cand.get(s, 0) + VIVID
        ranked = sorted(cand.items(), key=lambda kv: (-kv[1], kv[0]))
        out.update([s for s, sc in ranked if sc >= CORROB][:CAP])
    return out

def imagined_map(design):
    out = set()
    for q in range(Q):
        own = [s for s in sorted(design) if s[0] == q]
        pick = []
        for k in range(CAP):
            if u("imag", q, k) < IMAG_PROJ and own:
                pick.append(own[k % len(own)])
            else:
                pick.append((q, int(u("imagr", q, k) * M)))
        out.update(pick)
    return out

def sim_items(truth, rho):
    out = set()
    for q in range(Q):
        for k in range(SIM_PER_Q):
            if u("sim", q, k) < rho:
                out.add((q, k))                    # a core statement (true)
            else:
                out.add((q, CORE + k))             # a non-core statement (false)
    return out

def stats(m, truth):
    ok = len(m & truth); bad = len(m - truth)
    alarms = sum(1 for q in range(Q) if sum(1 for s in m if s[0] == q) < SPARSE_BELOW)
    return dict(dens=len(m), ok=ok, bad=bad, prec=(ok / len(m) if m else 0.0), alarms=alarms)

def fmt(label, st):
    return (f"  {label:<34} density={st['dens']:>2} true={st['ok']:>2} false={st['bad']:>2} "
            f"precision={st['prec']:.2f} sparse-alarms={st['alarms']}")

checks = []
def check(name, cond):
    checks.append((name, bool(cond)))
    print(f"  [{'ok' if cond else 'FAIL'}] {name}")

# ---- Scenario 1: fill source (representative interviews vs imagination) -----
print("S1 fill source; designer overlap 1/4 of core")
truth, design, holds = world(1)
assert len(truth) == Q * CORE, len(truth)          # population truth really is the 16 core items
imag = stats(imagined_map(design), truth); print(fmt("imagined (N=0)", imag))
dens, grid = [], {}
for n in range(0, 25, 2):
    grid[n] = stats(build_map(interview_counts(holds, sample("representative", n)), set()), truth)
    dens.append(grid[n]["dens"])
    if n in (2, 6, 12, 24): print(fmt(f"interviews N={n}", grid[n]))
check("P1a imagined: all quadrants filled (alarms=0)", imag["alarms"] == 0)
check("P1b imagined precision <= 0.40", imag["prec"] <= 0.40)
check("P1c interviews N=12: alarms=0 and precision >= 0.90", grid[12]["alarms"] == 0 and grid[12]["prec"] >= 0.90)
check("P1d interviews N=2: >= 3 quadrants raise sparse alarm", grid[2]["alarms"] >= 3)
check("P1e density non-decreasing in N (0..24 step 2)", all(a <= b for a, b in zip(dens, dens[1:])))
check("P1f density cannot tell imagined from researched (alarm equal, precision differs >= 0.5)",
      imag["alarms"] == grid[12]["alarms"] and grid[12]["prec"] - imag["prec"] >= 0.5)

# ---- Scenario 2: simulation exercise on top of the SAME interviews ----------
print("S2 simulation exercise (rho = share of vivid items that are true)")
def arms(n, rho, kind="representative", wld=holds, tr=truth):
    cnt = interview_counts(wld, sample(kind, n))
    base = stats(build_map(cnt, set()), tr)
    sim = stats(build_map(cnt, sim_items(tr, rho)), tr)   # identical interview evidence in both arms
    return base, sim
b3, s3 = arms(3, 0.25); print(fmt("N=3 no exercise", b3)); print(fmt("N=3 exercise rho=0.25", s3))
b24, s24 = arms(24, 0.25); print(fmt("N=24 no exercise", b24)); print(fmt("N=24 exercise rho=0.25", s24))
check("P2a N=3: exercise removes the alarm (base>=3 -> 0)", b3["alarms"] >= 3 and s3["alarms"] == 0)
check("P2b N=3: exercise adds >= 6 false assertions", s3["bad"] - b3["bad"] >= 6)
check("P2c N=3: map with exercise still precision < 0.50", s3["prec"] < 0.50)
check("P2d N=24: exercise changes false assertions by <= 1", abs(s24["bad"] - b24["bad"]) <= 1)
print("  sweep of N where exercise adds false items (rho=0.25):",
      [(n, arms(n, 0.25)[1]["bad"] - arms(n, 0.25)[0]["bad"]) for n in (0, 3, 6, 9, 12, 18, 24)])

# ---- Breakers ---------------------------------------------------------------
print("B1 designer == user (overlap 4/4): imagination is fine")
t4, d4, h4 = world(4)
imag4 = stats(imagined_map(d4), t4); print(fmt("imagined, overlap 4/4", imag4))
check("B1 imagined precision >= 0.90 when designer is the user", imag4["prec"] >= 0.90)
# B1b / B4 were added AFTER B1 missed (post-hoc diagnostics, not pre-registered)
print("B1b diagnostic (post-hoc): same, but the designer fills ONLY from own items (IMAG_PROJ=1.0)")
IMAG_PROJ_SAVED = IMAG_PROJ; IMAG_PROJ = 1.0
imag4b = stats(imagined_map(d4), t4); print(fmt("imagined, overlap 4/4, proj=1.0", imag4b))
imag1b = stats(imagined_map(design), truth); print(fmt("imagined, overlap 1/4, proj=1.0", imag1b))
IMAG_PROJ = IMAG_PROJ_SAVED
check("B1b designer==user, no filler: imagined precision >= 0.90", imag4b["prec"] >= 0.90)
check("B1c overlap 1/4, no filler: imagined precision <= 0.40 (gap tracks overlap)", imag1b["prec"] <= 0.40)
print("B4 vividness sweep at N=3, rho=0.25 (post-hoc; my first guess that VIVID=1.0 was inert was WRONG:")
print("   one real mention + 1.0 vividness reaches the corroboration bar of 2, so masking is graded, not on/off)")
sweep = []
VIVID_SAVED = VIVID
for v in (0.0, 1.0, 2.0, 2.5, 4.0):
    VIVID = v
    bb, ss = arms(3, 0.25)
    sweep.append((v, ss["bad"] - bb["bad"], bb["alarms"] - ss["alarms"]))
VIVID = VIVID_SAVED
print("  (VIVID, false items added, alarms silenced):", sweep)
check("B4a VIVID=0 (no vividness): exercise changes nothing", sweep[0][1] == 0 and sweep[0][2] == 0)
check("B4b false items added is non-decreasing in vividness", all(x[1] <= y[1] for x, y in zip(sweep, sweep[1:])))
check("B4c VIVID=1.0 is only PARTIAL masking (0 < alarms silenced < 4)", 0 < sweep[1][2] < 4)
print("B2 convenience sample (colleagues) at N=12, overlap 1/4")
conv = stats(build_map(interview_counts(holds, sample("convenience", 12)), set()), truth)
print(fmt("interviews N=12 convenience", conv))
check("B2 convenience-sample map looks full (alarms=0) but precision <= 0.50", conv["alarms"] == 0 and conv["prec"] <= 0.50)
print("B3 high-fidelity exercise (rho=1.0) at N=3")
b3h, s3h = arms(3, 1.0); print(fmt("N=3 exercise rho=1.0", s3h))
check("B3 rho=1.0: exercise adds <= 1 false assertion", s3h["bad"] - b3h["bad"] <= 1)
print("N0 negative control: the metric must be able to say 'good'")
check("N0 perfect map scores precision 1.00, alarms 0", stats(set(truth), truth)["prec"] == 1.0 and stats(set(truth), truth)["alarms"] == 0)
check("N0b empty map is all-sparse (alarms=4) with zero false assertions", stats(set(), truth)["alarms"] == 4 and stats(set(), truth)["bad"] == 0)

bad = [n for n, ok in checks if not ok]
print(f"RESULT: {'PASS' if not bad else 'FAIL'} {len(checks)-len(bad)}/{len(checks)} checks; "
      f"imagined prec={imag['prec']:.2f} vs N=12 prec={grid[12]['prec']:.2f} (both alarms=0); "
      f"N=3 exercise false +{s3['bad']-b3['bad']}, alarms {b3['alarms']}->{s3['alarms']}; "
      f"designer==user imagined prec={imag4['prec']:.2f} (pre-registered B1 missed; proj=1.0 gives {imag4b['prec']:.2f}); failed={bad}")
