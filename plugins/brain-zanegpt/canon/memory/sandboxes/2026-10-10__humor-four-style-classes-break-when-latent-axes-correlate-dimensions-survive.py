"""Humor-styles structure sandbox (STRUCTURE ONLY, no claim about real people).

Models a two-axis frame (benign vs injurious x self-directed vs other-directed)
that yields four style traits, simulates respondents answering 32 stand-in items
(8 per style, original wording), then asks whether the four styles are
recoverable as hard classes (max subscale) and as dimensions.

PREDICTIONS (written before the first run; thresholds are checked below):
 P1 null control (items carry no signal): max-subscale retest agreement 0.25 +- 0.03.
 P2 clean case (axes independent, c=0.6, noise x1): mean alpha >= 0.70, retest
    class agreement >= 0.65, accuracy vs latent argmax >= 0.60, mean |inter-scale r|
    <= 0.20, >= 95% of items correlate highest with their own scale.
 P3 break case (axes corr 0.8 both, c=0.9): mean inter-scale r >= 0.55, mean
    disattenuated r >= 0.85, retest class agreement <= 0.55, >= 40% of
    respondents have a top-two margin under 0.5 SD.
 P4 dissociation in the break case: the 4-scale sum score retests at r >= 0.85
    while both axis contrasts retest below the sum score.
 P5 noise sweep (noise x0.5 -> x2.0): clean-case agreement falls by >= 0.15 and
    stays >= 0.45 at x2.0; break case at x1.0 is <= 0.55.
 P6 grid: at c=0.9 agreement is non-increasing in axis correlation (0, .4, .8);
    the first grid cell under 0.60 has mean latent style correlation in [0.3, 0.6].
 P7 abstain band in the break case (margin >= 0.75 SD): coverage <= 0.60 and
    agreement among assigned >= 0.65.
RESULT is PASS only if every prediction holds.
"""
import math
import random

N = 3000
SEED = 20261010
STYLES = ["affiliative", "self_enhancing", "aggressive", "self_defeating"]
# cell of the 2x2: (valence axis, target axis); valence B=benign J=injurious; target O=other S=self
CELL = {"affiliative": ("B", "O"), "self_enhancing": ("B", "S"),
        "aggressive": ("J", "O"), "self_defeating": ("J", "S")}
# neighbour style used for a cross-loading item: (valence-neighbour, target-neighbour)
NEIGH = {"affiliative": ("aggressive", "self_enhancing"),
         "self_enhancing": ("self_defeating", "affiliative"),
         "aggressive": ("affiliative", "self_defeating"),
         "self_defeating": ("self_enhancing", "aggressive")}

# original stand-in items (not taken from any instrument), 8 per style
ITEMS = {
 "affiliative": ["I lighten a tense room with a quick friendly quip", "I swap funny stories with new acquaintances",
   "I enjoy being the one who gets a group laughing together", "I tell a funny anecdote to help someone feel included",
   "Shared jokes are how I bond with colleagues", "I look for the playful side when a meeting drags",
   "I make others at ease by joking along with them", "I like trading banter with friends"],
 "self_enhancing": ["Finding the funny side helps me through a bad week", "When I am stressed I look for something amusing in it",
   "A wry view of my troubles keeps me steady", "I cheer myself up by noticing absurd details",
   "Even alone I can laugh my way out of a low mood", "I reframe setbacks with a bit of humor",
   "Humor is how I keep perspective", "I can chuckle at a hard situation while in it"],
 "aggressive": ["I will tease someone harder than they enjoy for a laugh", "I put people down in jest and move on",
   "I use sarcasm to cut a rival down to size", "I do not mind if a joke stings the person it targets",
   "I mock others' mistakes to get the room on my side", "My humor can leave someone feeling small",
   "I aim jokes at people who annoy me", "I press a jibe even when it clearly lands badly"],
 "self_defeating": ["I run myself down to get others to laugh", "I play the fool at my own expense to be liked",
   "I joke about my flaws so no one else can first", "I let people laugh at me to keep the mood up",
   "I exaggerate my failings for a cheap laugh", "I hide hurt behind a joke about myself",
   "I will embarrass myself if it wins a smile", "I downplay my worth in jokes to fit in"],
}
ITEM_LOAD = [0.55, 0.60, 0.65, 0.70, 0.70, 0.75, 0.78, 0.80]
CROSS_ITEMS = (6, 7)   # these two items per style also load on a neighbour style
GAMMA = 0.25


def gauss_pair(rng):
    return rng.gauss(0, 1), rng.gauss(0, 1)


def make_latents(rng, c, rho_v, rho_t, n=N):
    """Return per-respondent dict of axis values and style traits."""
    out = []
    sv = math.sqrt(1 - rho_v ** 2)
    st = math.sqrt(1 - rho_t ** 2)
    for _ in range(n):
        z1, z2 = gauss_pair(rng)
        z3, z4 = gauss_pair(rng)
        ax = {"B": z1, "J": rho_v * z1 + sv * z2, "S": z3, "O": rho_t * z3 + st * z4}
        th = {}
        for s in STYLES:
            v, t = CELL[s]
            th[s] = c * (ax[v] + ax[t]) / math.sqrt(2) + math.sqrt(1 - c * c) * rng.gauss(0, 1)
        out.append((ax, th))
    return out


CUTS = (-1.2, -0.4, 0.4, 1.2)


def likert(x):
    return 1 + sum(1 for k in CUTS if x > k)


def administer(rng, lat, noise, signal=1.0):
    """Return (item matrix rows: dict style -> list of 8 ints) for each respondent."""
    rows = []
    for ax, th in lat:
        r = {}
        for s in STYLES:
            vals = []
            for i in range(8):
                lam = ITEM_LOAD[i] * signal
                x = lam * th[s]
                if i in CROSS_ITEMS:
                    nb = NEIGH[s][CROSS_ITEMS.index(i)]
                    x += GAMMA * signal * th[nb]
                sd_e = math.sqrt(max(1e-9, 1 - ITEM_LOAD[i] ** 2)) * noise
                x += rng.gauss(0, sd_e)
                vals.append(likert(x))
            r[s] = vals
        rows.append(r)
    return rows


def mean(a):
    return sum(a) / len(a)


def var(a):
    m = mean(a)
    return sum((x - m) ** 2 for x in a) / (len(a) - 1)


def corr(a, b):
    ma, mb = mean(a), mean(b)
    sa = sum((x - ma) ** 2 for x in a)
    sb = sum((y - mb) ** 2 for y in b)
    if sa == 0 or sb == 0:
        return 0.0
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(sa * sb)


def scale_scores(rows):
    return {s: [sum(r[s]) for r in rows] for s in STYLES}


def zs(vec):
    m, sd = mean(vec), math.sqrt(var(vec))
    return [(x - m) / sd for x in vec]


def alpha(rows, s):
    k = 8
    item_vars = [var([r[s][i] for r in rows]) for i in range(k)]
    tot = var([sum(r[s]) for r in rows])
    return k / (k - 1) * (1 - sum(item_vars) / tot)


def argmax_class(zmat, j):
    best = max(range(4), key=lambda q: zmat[q][j])
    return best


def margin(zmat, j):
    v = sorted((zmat[q][j] for q in range(4)), reverse=True)
    return v[0] - v[1]


def analyse(rows1, rows2, lat, label):
    sc1, sc2 = scale_scores(rows1), scale_scores(rows2)
    z1 = [zs(sc1[s]) for s in STYLES]
    z2 = [zs(sc2[s]) for s in STYLES]
    n = len(rows1)
    # reliability and inter-scale correlation
    al = [alpha(rows1, s) for s in STYLES]
    off, dis = [], []
    for a in range(4):
        for b in range(a + 1, 4):
            r = corr(sc1[STYLES[a]], sc1[STYLES[b]])
            off.append(r)
            dis.append(r / math.sqrt(max(al[a], 0.05) * max(al[b], 0.05)))
    # item own-scale (item-rest) vs other scales
    own_best, tot_items = 0, 0
    for s_idx, s in enumerate(STYLES):
        for i in range(8):
            col = [r[s][i] for r in rows1]
            rs = []
            for t_idx, t in enumerate(STYLES):
                if t == s:
                    rest = [sum(r[s]) - r[s][i] for r in rows1]
                else:
                    rest = sc1[t]
                rs.append(corr(col, rest))
            tot_items += 1
            if rs.index(max(rs)) == s_idx:
                own_best += 1
    # classification
    th_names = STYLES
    agree = acc = amb = 0
    for j in range(n):
        c1, c2 = argmax_class(z1, j), argmax_class(z2, j)
        truth = max(range(4), key=lambda q: lat[j][1][th_names[q]])
        agree += (c1 == c2)
        acc += (c1 == truth)
        amb += (margin(z1, j) < 0.5)
    # dimensions: sum, valence contrast, target contrast; retest r
    def comp(z, wts):
        return [sum(w * z[q][j] for q, w in enumerate(wts)) for j in range(n)]
    sumw, vw, tw = (1, 1, 1, 1), (1, 1, -1, -1), (1, -1, 1, -1)   # order: aff, se, agg, sd
    # target contrast: other-directed (aff, agg) minus self-directed (se, sd)
    tw = (1, -1, 1, -1)
    r_sum = corr(comp(z1, sumw), comp(z2, sumw))
    r_v = corr(comp(z1, vw), comp(z2, vw))
    r_t = corr(comp(z1, tw), comp(z2, tw))
    # latent style correlation (mean off-diagonal of true thetas)
    tl = []
    for a in range(4):
        for b in range(a + 1, 4):
            tl.append(corr([l[1][STYLES[a]] for l in lat], [l[1][STYLES[b]] for l in lat]))
    # abstain band
    cov = cov_agree = 0
    for j in range(n):
        if margin(z1, j) >= 0.75:
            cov += 1
            cov_agree += (argmax_class(z1, j) == argmax_class(z2, j))
    res = dict(label=label, alpha=mean(al), off=mean([abs(x) for x in off]), dis=mean(dis),
               own=own_best / tot_items, agree=agree / n, acc=acc / n, amb=amb / n,
               r_sum=r_sum, r_v=r_v, r_t=r_t, lat_corr=mean(tl),
               cov=cov / n, cov_agree=(cov_agree / cov if cov else float("nan")))
    return res


def run(seed_off, c, rho, noise, signal=1.0, label=""):
    rng = random.Random(SEED + seed_off)
    lat = make_latents(rng, c, rho, rho)
    r1 = administer(rng, lat, noise, signal)
    r2 = administer(rng, lat, noise, signal)
    return analyse(r1, r2, lat, label)


def fmt(r):
    return ("%-22s alpha=%.2f |r|=%.2f dis=%.2f own=%.2f agree=%.3f acc=%.3f amb=%.2f "
            "rSum=%.2f rV=%.2f rT=%.2f latr=%.2f cov=%.2f covAgree=%.2f" %
            (r["label"], r["alpha"], r["off"], r["dis"], r["own"], r["agree"], r["acc"], r["amb"],
             r["r_sum"], r["r_v"], r["r_t"], r["lat_corr"], r["cov"], r["cov_agree"]))


def main():
    checks = []

    def chk(name, ok, detail):
        checks.append((name, ok))
        print("  [%s] %s :: %s" % ("ok" if ok else "MISS", name, detail))

    print("scenarios (N=%d, 32 stand-in items, 5-point scale)" % N)
    null = run(1, 0.6, 0.0, 1.0, signal=0.0, label="S0 null")
    clean = run(2, 0.6, 0.0, 1.0, label="S1 clean c.6 rho0")
    mid = run(3, 0.6, 0.5, 1.0, label="S2 mid c.6 rho.5")
    brk = run(4, 0.9, 0.8, 1.0, label="S3 BREAK c.9 rho.8")
    for r in (null, clean, mid, brk):
        print(fmt(r))

    print("checks")
    chk("P1 null agree", abs(null["agree"] - 0.25) <= 0.03, "%.3f" % null["agree"])
    chk("P2 clean", clean["alpha"] >= 0.70 and clean["agree"] >= 0.65 and clean["acc"] >= 0.60
        and clean["off"] <= 0.20 and clean["own"] >= 0.95,
        "alpha %.2f agree %.3f acc %.3f |r| %.2f own %.2f" % (clean["alpha"], clean["agree"], clean["acc"], clean["off"], clean["own"]))
    chk("P3 break", brk["off"] >= 0.55 and brk["dis"] >= 0.85 and brk["agree"] <= 0.55 and brk["amb"] >= 0.40,
        "|r| %.2f dis %.2f agree %.3f amb %.2f" % (brk["off"], brk["dis"], brk["agree"], brk["amb"]))
    chk("P4 dissociation", brk["r_sum"] >= 0.85 and brk["r_v"] < brk["r_sum"] and brk["r_t"] < brk["r_sum"],
        "rSum %.2f rV %.2f rT %.2f" % (brk["r_sum"], brk["r_v"], brk["r_t"]))

    print("noise sweep (multiplier on item error sd)")
    sweep_clean, sweep_brk = {}, {}
    for k, nz in enumerate((0.5, 1.0, 1.5, 2.0)):
        sweep_clean[nz] = run(10 + k, 0.6, 0.0, nz, label="clean noise x%.1f" % nz)
        sweep_brk[nz] = run(20 + k, 0.9, 0.8, nz, label="break noise x%.1f" % nz)
        print("  noise x%.1f  clean agree=%.3f alpha=%.2f | break agree=%.3f alpha=%.2f" %
              (nz, sweep_clean[nz]["agree"], sweep_clean[nz]["alpha"], sweep_brk[nz]["agree"], sweep_brk[nz]["alpha"]))
    chk("P5 sweep", sweep_clean[0.5]["agree"] - sweep_clean[2.0]["agree"] >= 0.15
        and sweep_clean[2.0]["agree"] >= 0.45 and sweep_brk[1.0]["agree"] <= 0.55,
        "clean drop %.3f, clean@2.0 %.3f, break@1.0 %.3f" %
        (sweep_clean[0.5]["agree"] - sweep_clean[2.0]["agree"], sweep_clean[2.0]["agree"], sweep_brk[1.0]["agree"]))

    print("grid: retest class agreement by c (rows) and axis corr (cols 0,.4,.8); mean latent style r in ()")
    grid = {}
    for ci, c in enumerate((0.6, 0.75, 0.9)):
        line = "  c=%.2f " % c
        for ri, rho in enumerate((0.0, 0.4, 0.8)):
            g = run(40 + 3 * ci + ri, c, rho, 1.0, label="g")
            grid[(c, rho)] = g
            line += " %.3f(%.2f)" % (g["agree"], g["lat_corr"])
        print(line)
    mono = grid[(0.9, 0.0)]["agree"] >= grid[(0.9, 0.4)]["agree"] >= grid[(0.9, 0.8)]["agree"]
    below = [(c, rho) for c in (0.6, 0.75, 0.9) for rho in (0.0, 0.4, 0.8) if grid[(c, rho)]["agree"] < 0.60]
    first = below[0] if below else None
    lc = grid[first]["lat_corr"] if first else float("nan")
    # first cell in increasing latent-correlation order
    ordered = sorted(grid.items(), key=lambda kv: kv[1]["lat_corr"])
    first_o = next((kv for kv in ordered if kv[1]["agree"] < 0.60), None)
    lc_o = first_o[1]["lat_corr"] if first_o else float("nan")
    chk("P6 grid", mono and first_o is not None and 0.3 <= lc_o <= 0.6,
        "monotone@c.9=%s, first<0.60 by latent r at cell %s latr %.2f" % (mono, first_o[0] if first_o else None, lc_o))

    chk("P7 abstain", brk["cov"] <= 0.60 and brk["cov_agree"] >= 0.65,
        "coverage %.2f agreement-among-assigned %.2f (all-respondent agree %.3f)" % (brk["cov"], brk["cov_agree"], brk["agree"]))

    miss = [n for n, ok in checks if not ok]
    if miss:
        print("RESULT: FAIL %d of %d prediction checks missed: %s" % (len(miss), len(checks), ", ".join(miss)))
    else:
        print("RESULT: PASS all %d prediction checks held" % len(checks))


if __name__ == "__main__":
    main()
