"""Toy measurement model: bias in self-report of four humor styles, and two corrections.

STRUCTURE ONLY. Every number below is a stated modelling assumption, not a claim
about real people. The four-style frame (affiliative, self-enhancing, aggressive,
self-defeating) is the published questionnaire frame (recalled, not verified here);
the items here are abstract latent draws, not questionnaire items.

Model
  true profile z (4 styles, assumed correlation matrix R)
  self-report item = 0.7*z + S*d*w_style + noise, mapped to a 7-point scale
      d  = person's social-desirability intensity (mean 1, sd 0.8)
      w  = shading direction: affiliative/self-enhancing up, aggressive/self-defeating down
      acquiescence a shifts the RAW response up for every item; reverse-keyed items cancel it
  forced choice: B blocks, one statement per style, pick max of
      1.2*z + (1-q)*S*d*w + noise   (q = how well desirability is matched)
  other report: m raters, v*z + kappa*S*d_rater*w + noise; d_rater shares rho with d
Deterministic: fixed seeds, stdlib only, no timing.
"""
import math
import random

STY = ["AF", "SE", "AG", "SD"]
W = [0.5, 0.4, -0.7, -0.7]          # shading direction/size per style (assumed)
LAM = 0.7                           # item loading on true trait (assumed)
N = 1500
SEEDS = [11, 23, 37, 41, 59]
NR = 3                              # max raters generated
BMAX = 128

R_DEF = [[1, .35, .05, .00], [.35, 1, .00, -.10], [.05, .00, 1, .30], [.00, -.10, .30, 1]]
R_IND = [[1 if i == j else 0 for j in range(4)] for i in range(4)]
R_G = [[1 if i == j else .5 for j in range(4)] for i in range(4)]


def chol(R):
    n = len(R)
    L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = sum(L[i][k] * L[j][k] for k in range(j))
            L[i][j] = math.sqrt(R[i][i] - s) if i == j else (R[i][j] - s) / L[j][j]
    return L


def gen_pop(seed, R):
    rng = random.Random(seed)
    L = chol(R)
    pop = {"z": [], "d": [], "a": [], "E": [], "G": [], "NO": [], "FN": []}
    for _ in range(N):
        g = [rng.gauss(0, 1) for _ in range(4)]
        pop["z"].append([sum(L[i][k] * g[k] for k in range(i + 1)) for i in range(4)])
        pop["d"].append(rng.gauss(1, 0.8))
        pop["a"].append(rng.gauss(0, 1))
        pop["E"].append([[rng.gauss(0, 0.9) for _ in range(8)] for _ in range(4)])
        pop["G"].append([rng.gauss(0, 1) for _ in range(NR)])
        pop["NO"].append([[rng.gauss(0, 0.8) for _ in range(4)] for _ in range(NR)])
        pop["FN"].append([[rng.gauss(0, 1.0) for _ in range(4)] for _ in range(BMAX)])
    return pop


def clip17(v):
    return 1 if v < 1 else (7 if v > 7 else v)


def self_scores(pop, S, rev, acq):
    out = []
    for i in range(N):
        z, d, a, E = pop["z"][i], pop["d"][i], pop["a"][i], pop["E"][i]
        row = []
        for s in range(4):
            tot = 0
            for j in range(8):
                x = LAM * z[s] + S * d * W[s] + E[s][j]
                if j < rev:
                    tot += 8 - clip17(round(4 + 1.3 * (-x + 0.5 * acq * a)))
                else:
                    tot += clip17(round(4 + 1.3 * (x + 0.5 * acq * a)))
            row.append(tot / 8.0)
        out.append(row)
    return out


def fc_scores(pop, q, B, S):
    out = []
    for i in range(N):
        z, d = pop["z"][i], pop["d"][i]
        base = [1.2 * z[s] + (1 - q) * S * d * W[s] for s in range(4)]
        cnt = [0, 0, 0, 0]
        for b in range(B):
            fn = pop["FN"][i][b]
            best, bs = -1e9, 0
            for s in range(4):
                u = base[s] + fn[s]
                if u > best:
                    best, bs = u, s
            cnt[bs] += 1
        out.append([float(c) for c in cnt])
    return out


def other_scores(pop, m, rho, kappa, v, S):
    out = []
    sq = math.sqrt(max(0.0, 1 - rho * rho))
    for i in range(N):
        z, d = pop["z"][i], pop["d"][i]
        row = [0.0] * 4
        for k in range(m):
            dk = 1 + rho * (d - 1) + sq * 0.8 * pop["G"][i][k]
            for s in range(4):
                row[s] += v[s] * z[s] + kappa * S * dk * W[s] + pop["NO"][i][k][s]
        out.append([r / m for r in row])
    return out


def colz(rows):
    n = len(rows)
    res = [[0.0] * 4 for _ in range(n)]
    for s in range(4):
        col = [r[s] for r in rows]
        mu = sum(col) / n
        sd = math.sqrt(sum((c - mu) ** 2 for c in col) / n) or 1.0
        for i in range(n):
            res[i][s] = (col[i] - mu) / sd
    return res


def blend(A, B, w):
    return colz([[w * a[s] + (1 - w) * b[s] for s in range(4)] for a, b in zip(A, B)])


def avg_rank(col):
    idx = sorted(range(len(col)), key=lambda i: col[i])
    r = [0.0] * len(col)
    i = 0
    while i < len(idx):
        j = i
        while j + 1 < len(idx) and col[idx[j + 1]] == col[idx[i]]:
            j += 1
        for k in range(i, j + 1):
            r[idx[k]] = (i + j) / 2.0
        i = j + 1
    return r


def pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else 0.0


def argmax(v):
    b = 0
    for k in range(1, len(v)):
        if v[k] > v[b]:
            b = k
    return b


def metrics(est, tz):
    n = len(tz)
    tzs = colz(tz)
    ez = colz(est)
    m = {}
    ta = [argmax(r) for r in tzs]
    ea = [argmax(r) for r in ez]
    m["mis"] = sum(1 for a, b in zip(ta, ea) if a != b) / n
    clear = [i for i in range(n) if sorted(tzs[i])[-1] - sorted(tzs[i])[-2] > 0.5]
    ta_min = [min(range(4), key=lambda k: r_[k]) for r_ in tzs]
    ea_min = [min(range(4), key=lambda k: r_[k]) for r_ in ez]
    m["mis_min"] = sum(1 for a, b in zip(ta_min, ea_min) if a != b) / n
    m["mis_clear"] = sum(1 for i in clear if ta[i] != ea[i]) / len(clear)
    sp, dsp = [], []
    for s in range(4):
        rt = avg_rank([r[s] for r in tzs])
        re = avg_rank([r[s] for r in ez])
        sp.append(pearson(rt, re))
        dsp.append(sum(abs(a - b) for a, b in zip(rt, re)) / n / n)
        m["sp_" + STY[s]] = sp[-1]
        if s == 2:
            thr = n * 0.75
            tq = {i for i in range(n) if rt[i] >= thr}
            eq = {i for i in range(n) if re[i] >= thr}
            m["topq_AG"] = len(tq & eq) / len(tq)
    m["sp_mean"] = sum(sp) / 4
    m["disp"] = sum(dsp) / 4
    cols = [[r[s] for r in ez] for s in range(4)]
    offs = [pearson(cols[a], cols[b]) for a in range(4) for b in range(a + 1, 4)]
    m["off_mean"] = sum(offs) / len(offs)
    m["r_AFSE"] = pearson(cols[0], cols[1])
    m["r_AGSD"] = pearson(cols[2], cols[3])
    m["n_neg"] = sum(1 for o in offs if o < 0)
    return m


def raw_metrics(raw, clean_raw, tz):
    """Absolute (un-normed) reading of the 7-point scale: what a profile report shows."""
    n = len(tz)
    tzs = colz(tz)
    ta = [argmax(r) for r in tzs]
    ea = [argmax(r) for r in raw]
    out = {"raw_mis": sum(1 for a, b in zip(ta, ea) if a != b) / n}
    out["share_AG_SD_primary"] = sum(1 for a in ea if a >= 2) / n
    cs = sorted(r[2] for r in clean_raw)
    cut = cs[int(0.75 * n)]
    rt = avg_rank([r[2] for r in tzs])
    tq = [i for i in range(n) if rt[i] >= n * 0.75]
    out["flag_sens_AG"] = sum(1 for i in tq if raw[i][2] >= cut) / len(tq)
    return out


V_DEF = [0.8, 0.4, 0.8, 0.6]


def avg_dicts(ds):
    keys = ds[0].keys()
    return {k: sum(d[k] for d in ds) / len(ds) for k in keys}


def run_all():
    res = {}

    def put(name, d):
        res.setdefault(name, []).append(d)

    for seed in SEEDS:
        popD = gen_pop(seed, R_DEF)
        tz = popD["z"]
        # --- E1 baselines on default structure
        clean = self_scores(popD, 0.0, 2, 0.0)
        put("self_clean", metrics(clean, tz))
        for S in (0.5, 1.0, 1.5, 2.0):
            sc = self_scores(popD, S, 2, 1.0)
            d = metrics(sc, tz)
            d.update(raw_metrics(sc, clean, tz))
            put("self_S%.1f" % S, d)
        sc_def = self_scores(popD, 1.0, 2, 1.0)
        # --- E3 acquiescence
        for rev in (0, 2, 4):
            for acq in (0.0, 1.0, 2.0):
                put("acq_rev%d_a%.0f" % (rev, acq), metrics(self_scores(popD, 1.0, rev, acq), tz))
        # --- E4 forced choice on default structure
        for q in (0.0, 0.25, 0.5, 0.75, 1.0):
            put("fc_q%.2f_B16" % q, metrics(fc_scores(popD, q, 16, 1.0), tz))
        for B in (8, 32):
            put("fc_q1.00_B%d" % B, metrics(fc_scores(popD, 1.0, B, 1.0), tz))
        fc1 = fc_scores(popD, 1.0, 16, 1.0)
        # --- E5 other report and blend
        for m_ in (1, 3):
            for rho in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
                oth = other_scores(popD, m_, rho, 0.5, V_DEF, 1.0)
                put("other_m%d_rho%.1f" % (m_, rho), metrics(oth, tz))
                put("blend_m%d_rho%.1f_w0.5" % (m_, rho),
                    metrics(blend(colz(sc_def), colz(oth), 0.5), tz))
        oth30 = other_scores(popD, 3, 0.0, 0.5, V_DEF, 1.0)
        for w in (0.2, 0.35, 0.5, 0.65, 0.8):
            put("blend_m3_rho0.0_w%.2f" % w, metrics(blend(colz(sc_def), colz(oth30), w), tz))
        for vse in (0.2, 0.4, 0.6, 0.8):
            v = [0.8, vse, 0.8, 0.6]
            oth = other_scores(popD, 3, 0.0, 0.5, v, 1.0)
            put("blend_vSE%.1f" % vse, metrics(blend(colz(sc_def), colz(oth), 0.5), tz))
        for kap in (0.0, 1.0, 1.5):
            oth = other_scores(popD, 3, 0.0, kap, V_DEF, 1.0)
            put("blend_kappa%.1f" % kap, metrics(blend(colz(sc_def), colz(oth), 0.5), tz))
        # --- stacking: forced choice + other report
        put("fc1_plus_other_rho0", metrics(blend(colz(fc1), colz(oth30), 0.5), tz))
        oth_r8 = other_scores(popD, 3, 0.8, 0.5, V_DEF, 1.0)
        put("fc1_plus_other_rho0.8", metrics(blend(colz(fc1), colz(oth_r8), 0.5), tz))
        # --- structure variants for the ipsative artefact and the strong-g break
        popI = gen_pop(seed + 1000, R_IND)
        put("ind_fc_q1_noshade", metrics(fc_scores(popI, 1.0, 16, 0.0), popI["z"]))
        put("ind_self_noshade", metrics(self_scores(popI, 0.0, 2, 0.0), popI["z"]))
        popG = gen_pop(seed + 2000, R_G)
        put("g_self_S1", metrics(self_scores(popG, 1.0, 2, 1.0), popG["z"]))
        put("g_fc_q1", metrics(fc_scores(popG, 1.0, 16, 1.0), popG["z"]))
        put("g_fc_q0", metrics(fc_scores(popG, 0.0, 16, 1.0), popG["z"]))
        put("g_self_clean", metrics(self_scores(popG, 0.0, 2, 0.0), popG["z"]))
        put("g_fc_clean", metrics(fc_scores(popG, 1.0, 16, 0.0), popG["z"]))
        # --- run-2 extension: matched-reliability forced choice, q x B grid
        for q in (0.0, 0.5, 0.75, 1.0):
            for B in (16, 32, 64, 128):
                put("grid_q%.2f_B%d" % (q, B), metrics(fc_scores(popD, q, B, 1.0), tz))
        for B in (16, 32, 64, 96, 128):
            put("ind_fc_clean_B%d" % B, metrics(fc_scores(popI, 1.0, B, 0.0), popI["z"]))
        # rho x kappa grid for the blend (3 raters)
        for rho in (0.0, 0.5, 1.0):
            for kap in (0.5, 1.0, 2.0, 3.0):
                oth = other_scores(popD, 3, rho, kap, V_DEF, 1.0)
                put("rk_rho%.1f_kap%.1f" % (rho, kap), metrics(blend(colz(sc_def), colz(oth), 0.5), tz))
        # fine observability sweep, 1 and 3 raters
        for m_ in (1, 3):
            for vse in (0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6):
                v = [0.8, vse, 0.8, 0.6]
                oth = other_scores(popD, m_, 0.0, 0.5, v, 1.0)
                put("obs_m%d_vSE%.2f" % (m_, vse), metrics(blend(colz(sc_def), colz(oth), 0.5), tz))
        # shading that scales with the true trait (insight-free high users shade more): break for self-report
        popT = gen_pop(seed + 3000, R_DEF)
        for i in range(N):
            popT["d"][i] = 1 + 0.5 * popT["z"][i][2] + 0.5 * popT["z"][i][3] + 0.5 * popT["d"][i] - 0.5
        put("trait_linked_self", metrics(self_scores(popT, 1.0, 2, 1.0), popT["z"]))
        put("trait_linked_fc_q0", metrics(fc_scores(popT, 0.0, 16, 1.0), popT["z"]))
        put("trait_linked_fc_q1", metrics(fc_scores(popT, 1.0, 16, 1.0), popT["z"]))
        ot = other_scores(popT, 3, 0.0, 0.5, V_DEF, 1.0)
        put("trait_linked_blend", metrics(blend(colz(self_scores(popT, 1.0, 2, 1.0)), colz(ot), 0.5), popT["z"]))
    return {k: avg_dicts(v) for k, v in res.items()}


def row(name, r, keys):
    return "%-26s " % name + " ".join("%s=%.3f" % (k, r[name][k]) for k in keys)


def main():
    r = run_all()
    S1 = r["self_S1.0"]
    print("== E1 baselines / dose response (default structure, 5 seeds x %d respondents)" % N)
    for nm in ("self_clean", "self_S0.5", "self_S1.0", "self_S1.5", "self_S2.0"):
        print(row(nm, r, ["mis", "mis_clear", "sp_mean", "sp_AG", "sp_SE", "topq_AG"]))
    for nm in ("self_S0.5", "self_S1.0", "self_S1.5", "self_S2.0"):
        print(row(nm, r, ["raw_mis", "share_AG_SD_primary", "flag_sens_AG"]))
    print("== mechanism diagnostic: top vs bottom of the profile (independent traits, no shading)")
    for nm in ("ind_self_noshade", "ind_fc_q1_noshade"):
        print(row(nm, r, ["mis", "mis_min"]))
    print("== E3 acquiescence (S=1; rev = reverse-keyed items of 8; a = acquiescence strength)")
    for rev in (0, 2, 4):
        for acq in (0.0, 1.0, 2.0):
            print(row("acq_rev%d_a%.0f" % (rev, acq), r, ["mis", "sp_mean", "off_mean"]))
    print("== E4 forced choice (S=1)")
    for nm in ("fc_q0.00_B16", "fc_q0.25_B16", "fc_q0.50_B16", "fc_q0.75_B16", "fc_q1.00_B16",
               "fc_q1.00_B8", "fc_q1.00_B32"):
        print(row(nm, r, ["mis", "sp_mean", "sp_AG", "off_mean", "r_AFSE", "n_neg"]))
    print("== ipsative artefact, independent true traits, no shading")
    print(row("ind_self_noshade", r, ["mis", "sp_mean", "off_mean", "n_neg"]))
    print(row("ind_fc_q1_noshade", r, ["mis", "sp_mean", "off_mean", "n_neg"]))
    print("== strong general factor (BREAK for ipsative)")
    for nm in ("g_self_clean", "g_fc_clean", "g_self_S1", "g_fc_q1", "g_fc_q0"):
        print(row(nm, r, ["mis", "sp_mean", "off_mean"]))
    print("== E5 other report and blend (S=1, w=0.5)")
    for m_ in (1, 3):
        for rho in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
            print(row("other_m%d_rho%.1f" % (m_, rho), r, ["mis", "sp_mean"]),
                  "|", row("blend_m%d_rho%.1f_w0.5" % (m_, rho), r, ["mis", "sp_mean", "sp_AG", "sp_SE"]))
    for w in (0.2, 0.35, 0.5, 0.65, 0.8):
        print(row("blend_m3_rho0.0_w%.2f" % w, r, ["mis", "sp_mean", "sp_SE", "sp_AG"]))
    for vse in (0.2, 0.4, 0.6, 0.8):
        print(row("blend_vSE%.1f" % vse, r, ["mis", "sp_SE", "sp_AG"]))
    for kap in (0.0, 1.0, 1.5):
        print(row("blend_kappa%.1f" % kap, r, ["mis", "sp_AG"]))
    print("== run-2 extension: forced choice q x B grid (S=1)  [self shaded: mis=%.3f sp_mean=%.3f]" % (S1["mis"], S1["sp_mean"]))
    for q in (0.0, 0.5, 0.75, 1.0):
        print("q=%.2f " % q + "  ".join("B%d mis=%.3f sp=%.3f" % (B, r["grid_q%.2f_B%d" % (q, B)]["mis"], r["grid_q%.2f_B%d" % (q, B)]["sp_mean"]) for B in (16, 32, 64, 128)))
    print("clean forced choice, independent traits (rank validity vs B; clean self sp_mean=%.3f)" % r["ind_self_noshade"]["sp_mean"])
    for B in (16, 32, 64, 96, 128):
        print("  B=%d sp_mean=%.3f mis=%.3f" % (B, r["ind_fc_clean_B%d" % B]["sp_mean"], r["ind_fc_clean_B%d" % B]["mis"]))
    print("blend rho x kappa (3 raters, w=0.5)  [self shaded mis=%.3f]" % S1["mis"])
    for rho in (0.0, 0.5, 1.0):
        print("rho=%.1f " % rho + "  ".join("kap%.1f mis=%.3f" % (k, r["rk_rho%.1f_kap%.1f" % (rho, k)]["mis"]) for k in (0.5, 1.0, 2.0, 3.0)))
    print("blend SE rank order vs observability  [self shaded sp_SE=%.3f]" % S1["sp_SE"])
    for m_ in (1, 3):
        print("m=%d " % m_ + "  ".join("v%.2f sp_SE=%.3f" % (v, r["obs_m%d_vSE%.2f" % (m_, v)]["sp_SE"]) for v in (0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6)))
    print("== stacking and trait-linked shading")
    for nm in ("fc1_plus_other_rho0", "fc1_plus_other_rho0.8", "trait_linked_self",
               "trait_linked_fc_q0", "trait_linked_fc_q1", "trait_linked_blend"):
        print(row(nm, r, ["mis", "sp_mean", "sp_AG", "topq_AG"]))

    # ---------------- prediction checks
    S1 = r["self_S1.0"]
    checks = []

    def chk(tag, ok, text):
        checks.append((tag, ok))
        print("%s %s %s" % (tag, "HELD" if ok else "REFUTED", text))

    print("== prediction checks")
    d1 = S1["mis"] - r["self_clean"]["mis"]
    chk("P1", d1 >= 0.08, "shading raises mis by %.3f (pred >= 0.08)" % d1)
    chk("P2", S1["flag_sens_AG"] < 0.60, "AG flag sensitivity %.3f (pred < 0.60)" % S1["flag_sens_AG"])
    bal = r["acq_rev4_a1"]
    nor = r["acq_rev0_a1"]
    dm = nor["mis"] - bal["mis"]
    dsp = bal["sp_mean"] - nor["sp_mean"]
    chk("P3", abs(dm) < 0.015 and dsp >= 0.03, "no-reverse vs balanced: d_mis=%.3f d_sp=%.3f" % (dm, dsp))
    fq1, fq0 = r["fc_q1.00_B16"], r["fc_q0.00_B16"]
    chk("P4", (S1["mis"] - fq1["mis"]) >= 0.05 and (S1["mis"] - fq0["mis"]) <= 0.03,
        "self-fc(q1)=%.3f self-fc(q0)=%.3f (pred >= 0.05 and <= 0.03)"
        % (S1["mis"] - fq1["mis"], S1["mis"] - fq0["mis"]))
    oi = r["ind_fc_q1_noshade"]["off_mean"]
    chk("P5", -0.41 <= oi <= -0.25 and fq1["r_AFSE"] <= 0.0,
        "independent-trait FC mean r=%.3f; default structure FC r(AF,SE)=%.3f (true +0.35)" % (oi, fq1["r_AFSE"]))
    b30 = r["blend_m3_rho0.0_w0.5"]
    gain = S1["mis"] - b30["mis"]
    cross = None
    for rho in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        if r["blend_m3_rho%.1f_w0.5" % rho]["mis"] >= S1["mis"]:
            cross = rho
            break
    chk("P6", gain >= 0.05 and cross is not None and 0.4 < cross <= 0.9,
        "blend gain at rho=0 %.3f; crossover rho*=%s (pred gain >= 0.05, rho* in (0.4,0.9])" % (gain, cross))
    b4 = r["blend_vSE0.4"]
    chk("P7", b4["sp_SE"] < S1["sp_SE"] and b4["sp_AG"] > S1["sp_AG"],
        "SE spearman blend %.3f vs self %.3f; AG blend %.3f vs self %.3f"
        % (b4["sp_SE"], S1["sp_SE"], b4["sp_AG"], S1["sp_AG"]))
    gap = r["g_self_S1"]["sp_mean"] - r["g_fc_q1"]["sp_mean"]
    chk("P8", gap >= 0.10, "strong-g mean Spearman self-minus-FC(q=1) = %.3f (pred >= 0.10)" % gap)

    # P9: matched clean rank validity
    target = r["ind_self_noshade"]["sp_mean"]
    Bm = 128
    for B in (16, 32, 64, 96, 128):
        if r["ind_fc_clean_B%d" % B]["sp_mean"] >= target:
            Bm = B
            break
    gq = {B: {q: r["grid_q%.2f_B%d" % (q, B)] for q in (0.0, 0.5, 0.75, 1.0)} for B in (16, 32, 64, 128)}
    Bg = Bm if Bm in gq else 128
    a9 = S1["mis"] - gq[Bg][1.0]["mis"]
    b9 = S1["mis"] - gq[Bg][0.0]["mis"]
    chk("P9", a9 >= 0.05 and abs(b9) <= 0.03,
        "matched B=%d (clean sp %.3f vs self %.3f): self-minus-FC mis q1=%.3f q0=%.3f"
        % (Bg, r["ind_fc_clean_B%d" % Bg]["sp_mean"], target, a9, b9))
    k11 = r["rk_rho1.0_kap2.0"]["mis"] >= S1["mis"] and r["rk_rho1.0_kap1.0"]["mis"] < S1["mis"]
    chk("P10", k11, "blend mis rho=1: kappa1=%.3f kappa2=%.3f kappa3=%.3f vs self %.3f"
        % (r["rk_rho1.0_kap1.0"]["mis"], r["rk_rho1.0_kap2.0"]["mis"], r["rk_rho1.0_kap3.0"]["mis"], S1["mis"]))
    c3 = max([v for v in (0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6) if r["obs_m3_vSE%.2f" % v]["sp_SE"] < S1["sp_SE"]] or [0])
    c1 = max([v for v in (0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6) if r["obs_m1_vSE%.2f" % v]["sp_SE"] < S1["sp_SE"]] or [0])
    chk("P11", c3 <= 0.25 and c1 >= 0.5 - 1e-9 and c1 > c3,
        "highest v_SE where blend hurts SE rank: 3 raters %.2f, 1 rater %.2f" % (c3, c1))
    chk("P12", gq[16][1.0]["sp_mean"] < S1["sp_mean"] and gq[32][1.0]["sp_mean"] > S1["sp_mean"],
        "FC q=1 sp_mean B16=%.3f B32=%.3f vs self %.3f" % (gq[16][1.0]["sp_mean"], gq[32][1.0]["sp_mean"], S1["sp_mean"]))

    ms, mf = r["ind_self_noshade"], r["ind_fc_q1_noshade"]
    chk("P13", mf["mis"] < ms["mis"] and mf["mis_min"] > ms["mis_min"],
        "argmax mis self=%.3f FC=%.3f; argmin mis self=%.3f FC=%.3f" % (ms["mis"], mf["mis"], ms["mis_min"], mf["mis_min"]))
    held = sum(1 for _, ok in checks if ok)
    bad = [t for t, ok in checks if not ok]
    if bad:
        print("RESULT: FAIL %d/%d predictions held; refuted: %s" % (held, len(checks), ",".join(bad)))
    else:
        print("RESULT: PASS %d/%d predictions held" % (held, len(checks)))


if __name__ == "__main__":
    main()
