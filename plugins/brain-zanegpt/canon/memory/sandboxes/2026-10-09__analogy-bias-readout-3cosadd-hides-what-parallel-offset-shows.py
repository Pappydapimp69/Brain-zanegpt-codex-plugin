#!/usr/bin/env python3
"""Sandbox: do analogy-arithmetic stereotypes come from corpus statistics alone?

Stdlib only, deterministic (every corpus uses random.Random(seed)); no timing.

Model: synthetic corpus -> PPMI target x context matrix -> low-rank dense
embeddings (Jacobi eigen-decomposition of M M^T) -> 3CosAdd analogies.
  - biased corpus : "male-skewed" occupations get the male cue 85% of the
                    time they take a cue at all, "female-skewed" ones the
                    female cue 85% of the time, neutral ones 50/50.
  - control corpus: same vocabulary, same topics, every occupation 50/50.
Not a trained neural embedding: a toy that isolates ONE mechanism (cue
co-occurrence statistics) and asks whether it is sufficient.

Scenarios:
  S1 biased corpus, rank 6, 40 corpora x 5 queries
  S2 symmetric control corpus; 30 vs 400 trials (power of the control)
  S3 neutralize gender direction on occupation words only
  S4 BREAK: neutralize every word (including king/queen)
  S5 FGSM-style sign perturbation of the analogy query
  S6 k-shot offset (k = 1,2,4,8 example pairs) instead of man->woman
  S7 BREAK: rank sweep (explicit/high rank vs low rank)
  S8 (iteration 2) geometry vs readout: projection on the gender direction,
     parallel-offset readout, forced-choice gender test, rank sweep of the
     parallel-offset readout
"""
import math
import random
import statistics

# ----------------------------------------------------------------- vocabulary
MALE_OCC = ["programmer", "engineer", "surgeon", "carpenter", "doctor"]
FEMALE_OCC = ["homemaker", "nurse", "receptionist", "librarian", "stylist"]
NEUTRAL_OCC = ["teacher", "writer", "chef", "accountant"]
OCC = MALE_OCC + FEMALE_OCC + NEUTRAL_OCC

OCC_TOPICS = {
    "programmer": ["code", "machine"], "engineer": ["machine", "tools"],
    "surgeon": ["ward", "tools"], "carpenter": ["tools", "wood"],
    "doctor": ["ward", "patients"],
    "homemaker": ["kitchen", "children"], "nurse": ["ward", "patients"],
    "receptionist": ["desk", "talk"], "librarian": ["books", "desk"],
    "stylist": ["salon", "talk"],
    "teacher": ["school", "books"], "writer": ["books", "desk"],
    "chef": ["kitchen", "food"], "accountant": ["desk", "numbers"],
}

# definitional (gender-by-definition) pairs: (male, female, topics)
POOL_PAIRS = [("man", "woman", ["people", "talk"]),
              ("king", "queen", ["crown", "throne"]),
              ("father", "mother", ["kin", "home_life"]),
              ("brother", "sister", ["kin", "school"]),
              ("prince", "princess", ["crown", "kin"]),
              ("nephew", "niece", ["kin", "school"]),
              ("grandfather", "grandmother", ["kin", "home_life"]),
              ("waiter", "waitress", ["food", "talk"])]
TEST_PAIRS = [("uncle", "aunt", ["kin", "home_life"]),
              ("son", "daughter", ["kin", "school"]),
              ("boy", "girl", ["school", "people"]),
              ("husband", "wife", ["home_life", "kin"])]
GENDER_WORDS = {}
for m, f, t in POOL_PAIRS + TEST_PAIRS:
    GENDER_WORDS[m] = (1.0, t)
    GENDER_WORDS[f] = (0.0, t)

SHARED = ["people", "talk"]


def male_prob(word, biased):
    """Design-level probability that a cue next to `word` is the male cue."""
    if word in GENDER_WORDS:
        return GENDER_WORDS[word][0]
    if not biased:
        return 0.5
    if word in MALE_OCC:
        return 0.85
    if word in FEMALE_OCC:
        return 0.15
    return 0.5


def label(word):
    """Design label used to score answers (independent of the corpus drawn)."""
    if word in MALE_OCC:
        return "M"
    if word in FEMALE_OCC:
        return "F"
    return "N"


def topics_of(word):
    return GENDER_WORDS[word][1] if word in GENDER_WORDS else OCC_TOPICS[word]


TARGETS = OCC + list(GENDER_WORDS)
# fixed context vocabulary
CTX = sorted({t for w in TARGETS for t in topics_of(w)} | set(SHARED)) + ["c_he", "c_she"]
CTX_IDX = {c: i for i, c in enumerate(CTX)}
TGT_IDX = {w: i for i, w in enumerate(TARGETS)}


# --------------------------------------------------------------------- corpus
def build_counts(seed, biased, sentences=500, slots=3):
    rng = random.Random(seed)
    counts = [[0] * len(CTX) for _ in TARGETS]
    for w in TARGETS:
        cue_rate = 0.6 if w in GENDER_WORDS else 0.35
        mp = male_prob(w, biased)
        tp = topics_of(w)
        row = counts[TGT_IDX[w]]
        for _ in range(sentences):
            for _ in range(slots):
                if rng.random() < cue_rate:
                    c = "c_he" if rng.random() < mp else "c_she"
                elif rng.random() < 0.8:
                    c = tp[rng.randrange(len(tp))]
                else:
                    c = SHARED[rng.randrange(len(SHARED))]
                row[CTX_IDX[c]] += 1
    return counts


def ppmi(counts):
    total = sum(map(sum, counts))
    rs = [sum(r) for r in counts]
    cs = [sum(counts[i][j] for i in range(len(counts))) for j in range(len(CTX))]
    M = []
    for i, r in enumerate(counts):
        row = []
        for j, c in enumerate(r):
            if c == 0:
                row.append(0.0)
            else:
                pmi = math.log(c * total / (rs[i] * cs[j]))
                row.append(max(pmi, 0.0))
        M.append(row)
    return M


def jacobi_eig(A, sweeps=40):
    n = len(A)
    A = [r[:] for r in A]
    V = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for _ in range(sweeps):
        off = sum(A[i][j] ** 2 for i in range(n) for j in range(n) if i != j)
        if off < 1e-18:
            break
        for p in range(n - 1):
            for q in range(p + 1, n):
                if abs(A[p][q]) < 1e-14:
                    continue
                th = (A[q][q] - A[p][p]) / (2 * A[p][q])
                t = (1 if th >= 0 else -1) / (abs(th) + math.sqrt(th * th + 1))
                c = 1 / math.sqrt(t * t + 1)
                s = t * c
                for k in range(n):
                    akp, akq = A[k][p], A[k][q]
                    A[k][p], A[k][q] = c * akp - s * akq, s * akp + c * akq
                for k in range(n):
                    apk, aqk = A[p][k], A[q][k]
                    A[p][k], A[q][k] = c * apk - s * aqk, s * apk + c * aqk
                for k in range(n):
                    vkp, vkq = V[k][p], V[k][q]
                    V[k][p], V[k][q] = c * vkp - s * vkq, s * vkp + c * vkq
    vals = [A[i][i] for i in range(n)]
    order = sorted(range(n), key=lambda i: -vals[i])
    return [vals[i] for i in order], [[V[r][i] for i in order] for r in range(n)]


_EIG = {}


def embed(seed, biased, rank):
    key = (seed, biased)
    if key not in _EIG:
        M = ppmi(build_counts(seed, biased))
        n = len(M)
        G = [[sum(a * b for a, b in zip(M[i], M[j])) for j in range(n)] for i in range(n)]
        _EIG[key] = jacobi_eig(G)
    vals, V = _EIG[key]
    E = {}
    for w in TARGETS:
        i = TGT_IDX[w]
        v = [V[i][k] * math.sqrt(max(vals[k], 0.0)) for k in range(rank)]
        E[w] = unit(v)
    return E


# ------------------------------------------------------------------- vectors
def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def norm(a):
    return math.sqrt(dot(a, a))


def unit(a):
    n = norm(a)
    return [x / n for x in a] if n > 0 else a[:]


def add(a, b, s=1.0):
    return [x + s * y for x, y in zip(a, b)]


def top(E, q, cands):
    best, bs = None, -9
    for w in cands:
        s = dot(unit(q), E[w])
        if s > bs:
            best, bs = w, s
    return best


def analogy(E, a, b, c, cands, offset=None):
    """a : b :: c : ?   (3CosAdd with inputs excluded)."""
    if offset is None:
        offset = add(E[c], E[a], -1.0)  # c - a  (man -> woman)
    q = add(E[b], offset)
    return top(E, q, [w for w in cands if w not in (a, b, c)])


def female_coded_share(answers):
    f = sum(1 for w in answers if label(w) == "F")
    m = sum(1 for w in answers if label(w) == "M")
    return f / (f + m) if f + m else float("nan")


def gender_dir(E, pairs):
    g = [0.0] * len(next(iter(E.values())))
    for m, f, _ in pairs:
        g = add(g, add(E[f], E[m], -1.0))
    return unit(g)


def neutralize(E, g, words):
    E2 = dict(E)
    for w in words:
        v = add(E[w], g, -dot(E[w], g))
        E2[w] = unit(v)
    return E2


def query_occ(E, offset=None):
    return [analogy(E, "man", x, "woman", OCC, offset) for x in MALE_OCC]


def queen_ok(E):
    return analogy(E, "man", "king", "woman", list(GENDER_WORDS)) == "queen"


def binom_two_sided_p(k, n, p0=0.5):
    pk = math.comb(n, k) * p0 ** k * (1 - p0) ** (n - k)
    return sum(math.comb(n, i) * p0 ** i * (1 - p0) ** (n - i)
               for i in range(n + 1)
               if math.comb(n, i) * p0 ** i * (1 - p0) ** (n - i) <= pk + 1e-15)


def power(n, p1, alpha=0.05):
    rej = [k for k in range(n + 1) if binom_two_sided_p(k, n) <= alpha]
    return sum(math.comb(n, k) * p1 ** k * (1 - p1) ** (n - k) for k in rej)


# ------------------------------------------------------------------- runs
RANK = 6
results = {}
checks = []


def check(name, ok, detail):
    checks.append((name, ok))
    print(f"  [{'ok ' if ok else 'XX '}] {name}: {detail}")


# ---- S1 biased corpus
print("S1 biased corpus, rank", RANK)
S1_SEEDS = list(range(40))
ans_b, queen_b, per_corpus_hits = [], 0, []
E_b = {}
for s in S1_SEEDS:
    E = embed(s, True, RANK)
    E_b[s] = E
    a = query_occ(E)
    ans_b += a
    queen_b += queen_ok(E)
    per_corpus_hits.append(sum(1 for w in a if label(w) == "F"))
share_b = female_coded_share(ans_b)
corp_ge3 = sum(1 for h in per_corpus_hits if h >= 3) / len(S1_SEEDS)
print(f"  female-coded share of M/F-labelled answers: {share_b:.3f} over {len(ans_b)} answers")
print(f"  corpora with >=3/5 female-skewed answers: {corp_ge3:.2f}; queen correct {queen_b}/40")
print(f"  seed-0 answers: {dict(zip(MALE_OCC, query_occ(E_b[0])))}")
check("P1 stereotype >=80% corpora", corp_ge3 >= 0.80, f"{corp_ge3:.2f}")
check("P1 queen >=95%", queen_b / 40 >= 0.95, f"{queen_b}/40")

# ---- S2 symmetric control
print("S2 symmetric control corpus (all occupations 0.5)")
S2_SEEDS = list(range(1000, 1400))
ans_c = []
for s in S2_SEEDS:
    ans_c += query_occ(embed(s, False, RANK))
share_c400 = female_coded_share(ans_c)
share_c_first30 = female_coded_share(ans_c[:30 * 5])
print(f"  female-coded share (400 corpora): {share_c400:.3f}; first 30 corpora: {share_c_first30:.3f}")
cnt = {"F": 0, "M": 0, "N": 0}
for w in ans_c:
    cnt[label(w)] += 1
print(f"  answer label counts in control: {cnt}")
p30, p400 = power(30, 0.60), power(400, 0.60)
print(f"  exact power to flag a true 0.60 share: n=30 -> {p30:.2f}, n=400 -> {p400:.2f}")
check("P2 control share in 0.45-0.55", 0.45 <= share_c400 <= 0.55, f"{share_c400:.3f}")
check("P2 power n=30 <0.5 and n=400 >0.95", p30 < 0.5 and p400 > 0.95, f"{p30:.2f}/{p400:.2f}")
print(f"  gap biased - control share = {share_b - share_c400:+.3f}")

# ---- S3 neutralize occupations only
print("S3 neutralize gender direction on occupation words only")
ans_n, queen_n = [], 0
for s in S1_SEEDS:
    E = E_b[s]
    g = gender_dir(E, POOL_PAIRS)
    En = neutralize(E, g, OCC)
    ans_n += query_occ(En)
    queen_n += queen_ok(En)
share_n = female_coded_share(ans_n)
print(f"  female-coded share after neutralizing: {share_n:.3f}; queen {queen_n}/40")
check("P3 share <=0.55", share_n <= 0.55, f"{share_n:.3f}")
check("P3 queen >=95%", queen_n / 40 >= 0.95, f"{queen_n}/40")

# ---- S4 BREAK: neutralize everything
print("S4 BREAK: neutralize every word, including king/queen/man/woman")
queen_all = 0
for s in S1_SEEDS:
    E = E_b[s]
    g = gender_dir(E, POOL_PAIRS)
    Ea = neutralize(E, g, TARGETS)
    queen_all += queen_ok(Ea)
print(f"  queen correct after neutralizing all: {queen_all}/40")
check("P3-break queen <50% when all neutralized", queen_all / 40 < 0.5, f"{queen_all}/40")

# ---- S5 FGSM-style
print("S5 FGSM-style sign perturbation of the analogy query")


def flip_eps(E, a, b, c, cands, step=0.01, cap=3.0):
    excl = (a, b, c)
    cs = [w for w in cands if w not in excl]
    q = add(add(E[b], E[c]), E[a], -1.0)
    base = top(E, q, cs)
    scores = sorted(((dot(unit(q), E[w]), w) for w in cs), reverse=True)
    runner = scores[1][1]
    nq = norm(q)
    uq = unit(q)

    def grad(e):  # d cos(q,e)/dq
        cosv = dot(uq, e)
        return [(ei - cosv * ui) / nq for ei, ui in zip(e, uq)]

    gA, gB = grad(E[base]), grad(E[runner])
    direction = [1.0 if (gb - ga) >= 0 else -1.0 for ga, gb in zip(gA, gB)]
    scale = sum(abs(x) for x in q) / len(q)
    eps = step
    while eps <= cap:
        q2 = add(q, direction, eps * scale)
        if top(E, q2, cs) != base:
            return eps, base, scores[0][0] - scores[1][0]
        eps += step
    return cap, base, scores[0][0] - scores[1][0]


ster, defin, margins_s, margins_d = [], [], [], []
for s in S1_SEEDS:
    E = E_b[s]
    for x in MALE_OCC:
        eps, ans, mg = flip_eps(E, "man", x, "woman", OCC)
        if label(ans) == "F":
            ster.append(eps)
            margins_s.append(mg)
    eps, ans, mg = flip_eps(E, "man", "king", "woman", list(GENDER_WORDS))
    if ans == "queen":
        defin.append(eps)
        margins_d.append(mg)
ms, md = statistics.median(ster), statistics.median(defin)
print(f"  stereotyped answers: n={len(ster)}, median flip eps = {ms:.2f} x mean|q_i|, median cosine margin {statistics.median(margins_s):.3f}")
print(f"  definitional queen:  n={len(defin)}, median flip eps = {md:.2f} x mean|q_i|, median cosine margin {statistics.median(margins_d):.3f}")
ratio = ms / md
print(f"  ratio stereotyped/definitional flip eps = {ratio:.2f}")
check("P4 ratio within 0.5-2.0", 0.5 <= ratio <= 2.0, f"{ratio:.2f}")

# ---- S6 k-shot offsets
print("S6 k-shot offset from k definitional example pairs (in-context analogue)")
fs_rows = []
for k in (1, 2, 4, 8):
    ans_k, held_ok, held_n = [], 0, 0
    for s in S1_SEEDS:
        E = E_b[s]
        off = [0.0] * RANK
        for m, f, _ in POOL_PAIRS[:k]:
            off = add(off, add(E[f], E[m], -1.0), 1.0 / k)
        ans_k += query_occ(E, offset=off)
        for m, f, _ in TEST_PAIRS:
            # held-out: apply the k-shot offset to m, expect f
            qv = add(E[m], off)
            cands = [w for w in GENDER_WORDS if w != m]
            held_ok += top(E, qv, cands) == f
            held_n += 1
    sh = female_coded_share(ans_k)
    fs_rows.append((k, sh, held_ok / held_n))
    print(f"  k={k}: female-coded share {sh:.3f}; held-out definitional accuracy {held_ok / held_n:.2f}")
check("P5 share at k=8 >=0.8", fs_rows[-1][1] >= 0.8, f"{fs_rows[-1][1]:.3f}")
check("P5 held-out acc at k=8 >= k=1", fs_rows[-1][2] >= fs_rows[0][2], f"{fs_rows[0][2]:.2f}->{fs_rows[-1][2]:.2f}")

# ---- S7 BREAK: rank sweep
print("S7 BREAK: rank sweep (30 corpora each)")
rank_rows = []
for r in (2, 3, 4, 6, 8, 12, 20, 29):
    ans_r = []
    for s in range(30):
        ans_r += query_occ(embed(s, True, r))
    sh = female_coded_share(ans_r)
    rank_rows.append((r, sh))
    print(f"  rank {r:2d}: female-coded share {sh:.3f}")
hi = [sh for r, sh in rank_rows if r >= 20]
check("P6 high-rank share <0.5", all(sh < 0.5 for sh in hi), ", ".join(f"{sh:.2f}" for sh in hi))


# ======================================================= ITERATION 2 (S8)
print("S8 geometry vs readout (added after run 1 refuted the 3CosAdd readout)")


def pearson(x, y):
    mx, my = sum(x) / len(x), sum(y) / len(y)
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


DESIGN = {w: {"M": 1.0, "F": -1.0, "N": 0.0}[label(w)] for w in OCC}


def proj_r(E, g):
    # g points male->female, so negate the projection to align with M=+1
    return pearson([-dot(E[w], g) for w in OCC], [DESIGN[w] for w in OCC])


def parallel_share(E, g_pair=("man", "woman")):
    """Paper-style readout: y near x, offset y-x parallel to woman-man."""
    gv = add(E[g_pair[1]], E[g_pair[0]], -1.0)
    dists = sorted(norm(add(E[x], E[y], -1.0)) for i, x in enumerate(OCC) for y in OCC[i + 1:])
    delta = dists[len(dists) // 2]
    out = []
    for x in MALE_OCC:
        best, bs = None, -9
        for y in OCC:
            if y == x or norm(add(E[x], E[y], -1.0)) > delta:
                continue
            sc = dot(unit(gv), unit(add(E[y], E[x], -1.0)))
            if sc > bs:
                best, bs = y, sc
        out.append(best)
    return out


r_b, r_c, r_n = [], [], []
par_b, par_c, par_n = [], [], []
for s in S1_SEEDS:
    Eb = embed(s, True, RANK)
    Ec = embed(1000 + s, False, RANK)
    gb = gender_dir(Eb, POOL_PAIRS)
    gc = gender_dir(Ec, POOL_PAIRS)
    r_b.append(proj_r(Eb, gb))
    r_c.append(abs(proj_r(Ec, gc)))
    par_b += [w for w in parallel_share(Eb) if w]
    par_c += [w for w in parallel_share(Ec) if w]
    En = neutralize(Eb, gb, OCC)
    r_n.append(abs(proj_r(En, gb)))
    par_n += [w for w in parallel_share(En) if w]
mr_b, mr_c, mr_n = statistics.mean(r_b), statistics.mean(r_c), statistics.mean(r_n)
sh_pb, sh_pc, sh_pn = female_coded_share(par_b), female_coded_share(par_c), female_coded_share(par_n)
print(f"  occupation projection vs design label: mean r biased {mr_b:.3f}; control mean |r| {mr_c:.3f}; neutralized mean |r| {mr_n:.3f}")
print(f"  parallel-offset female-coded share: biased {sh_pb:.3f}; control {sh_pc:.3f}; neutralized {sh_pn:.3f}")
check("P7 biased mean r >=0.9", mr_b >= 0.9, f"{mr_b:.3f}")
check("P7 control mean |r| <0.35", mr_c < 0.35, f"{mr_c:.3f}")
check("P8 biased parallel share >=0.8", sh_pb >= 0.8, f"{sh_pb:.3f}")
check("P8 control share in 0.4-0.6", 0.4 <= sh_pc <= 0.6, f"{sh_pc:.3f}")
check("P9 neutralized share in 0.4-0.6", 0.4 <= sh_pn <= 0.6, f"{sh_pn:.3f}")
print(f"  [--] P9 |r| on the neutralized direction itself = {mr_n:.3f}: DEGENERATE (zero by construction), not scored")

# forced-choice gender test: man:m::woman:{f vs same-topic male distractor d}
DISTRACT = {"king": "prince", "prince": "king", "father": "grandfather",
            "grandfather": "father", "brother": "nephew", "nephew": "brother"}
PAIR_F = {m: f for m, f, _ in POOL_PAIRS}


def forced_choice(E):
    ok = n = 0
    for m, d in DISTRACT.items():
        q = add(E[m], add(E["woman"], E["man"], -1.0))
        n += 1
        ok += dot(unit(q), E[PAIR_F[m]]) > dot(unit(q), E[d])
    return ok / n


fc_intact = statistics.mean(forced_choice(E_b[s]) for s in S1_SEEDS)
fc_all = statistics.mean(forced_choice(neutralize(E_b[s], gender_dir(E_b[s], POOL_PAIRS), TARGETS)) for s in S1_SEEDS)
print(f"  forced-choice gender accuracy: intact {fc_intact:.2f}; all words neutralized {fc_all:.2f}; open-candidate queen test after neutralize-all: {queen_all}/40")
check("P10 intact >=0.9", fc_intact >= 0.9, f"{fc_intact:.2f}")
check("P10 neutralize-all <=0.6", fc_all <= 0.6, f"{fc_all:.2f}")

rank_par = []
for r in (3, 4, 6, 8, 12, 20, 29):
    out = []
    for s in range(30):
        out += [w for w in parallel_share(embed(s, True, r)) if w]
    rank_par.append((r, female_coded_share(out)))
print("  parallel-offset share by rank: " + ", ".join(f"r{r}={sh:.2f}" for r, sh in rank_par))
check("P11 parallel share >=0.7 at every rank 3..29", all(sh >= 0.7 for _, sh in rank_par),
      f"min {min(sh for _, sh in rank_par):.2f}")

# ======================================================= ITERATION 3 (S9)
print("S9 why 3CosAdd missed it; offset scaling; held-out-direction leak check")


def nearest_neighbour(E, x):
    return max((y for y in OCC if y != x), key=lambda y: dot(E[x], E[y]))


nn_hit = n_all = 0
for s in S1_SEEDS:
    E = E_b[s]
    for x, a in zip(MALE_OCC, query_occ(E)):
        nn_hit += a == nearest_neighbour(E, x)
        n_all += 1
print(f"  3CosAdd answer == input's nearest topic neighbour: {nn_hit}/{n_all} = {nn_hit / n_all:.2f}")
check("P12 neighbour share >=0.8", nn_hit / n_all >= 0.8, f"{nn_hit / n_all:.2f}")

lam_rows = []
for lam in (1, 2, 4, 8, 16):
    ab, ac = [], []
    for s in S1_SEEDS:
        for E, store in ((E_b[s], ab), (embed(1000 + s, False, RANK), ac)):
            off = add(E["woman"], E["man"], -1.0)
            off = [lam * v for v in off]
            store += query_occ(E, offset=off)
    lam_rows.append((lam, female_coded_share(ab), female_coded_share(ac)))
    print(f"  lambda={lam:2d}: biased share {lam_rows[-1][1]:.3f}; control share {lam_rows[-1][2]:.3f}")
mono = all(lam_rows[i + 1][1] >= lam_rows[i][1] - 1e-9 for i in range(len(lam_rows) - 1))
check("P13 biased non-decreasing in lambda", mono, ", ".join(f"{r[1]:.2f}" for r in lam_rows))
check("P13 biased >=0.8 at lambda=16", lam_rows[-1][1] >= 0.8, f"{lam_rows[-1][1]:.3f}")
check("P13 control within 0.25-0.75 at every lambda", all(0.25 <= r[2] <= 0.75 for r in lam_rows),
      ", ".join(f"{r[2]:.2f}" for r in lam_rows))

leak = []
for s in S1_SEEDS:
    E = E_b[s]
    En = neutralize(E, gender_dir(E, POOL_PAIRS), OCC)
    leak.append(abs(proj_r(En, gender_dir(En, TEST_PAIRS))))
ml = statistics.mean(leak)
print(f"  held-out-direction |r| after neutralizing with the pool direction: {ml:.3f} (biased baseline {mr_b:.3f})")
check("P9b leak |r| <0.39", ml < 0.39, f"{ml:.3f}")

# ------------------------------------------------------------------- verdict
failed = [n for n, ok in checks if not ok]
summary = (f"biased share {share_b:.2f} vs control {share_c400:.2f} (rank {RANK}); "
           f"neutralize-occ {share_n:.2f} queen {queen_n}/40, neutralize-all queen {queen_all}/40; "
           f"fgsm ratio {ratio:.2f}; kshot8 share {fs_rows[-1][1]:.2f}; "
           f"geometry r {mr_b:.2f} vs control {mr_c:.2f}, parallel share {sh_pb:.2f} vs control {sh_pc:.2f} vs neutralized {sh_pn:.2f}; "
           f"forced-choice {fc_intact:.2f} -> {fc_all:.2f}; "
           f"3cosadd==nearest-neighbour {nn_hit}/{n_all}; lambda16 biased {lam_rows[-1][1]:.2f} control {lam_rows[-1][2]:.2f}; held-out leak r {ml:.2f}; "
           f"{len(checks) - len(failed)}/{len(checks)} predictions held"
           + (f"; FAILED: {'; '.join(failed)}" if failed else ""))
print("RESULT: " + ("PASS " if not failed else "FAIL ") + summary)
