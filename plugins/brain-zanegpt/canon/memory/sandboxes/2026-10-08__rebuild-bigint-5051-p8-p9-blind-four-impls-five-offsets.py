#!/usr/bin/env python3
"""Blind rebuild: big-int AND-NOT cover test vs dict membership, offset 5051.

PREDICTION (written before first run, never edited):
  * Four independent cover implementations (dict membership, frozenset subset,
    big-int  b & ~a == 0  with the mask built from a repeated periodic word,
    and an arithmetic predicate with no landing lists) give IDENTICAL per-
    (width,horizon,b) shadow-count vectors for P=8,9 at offsets 5051, 3989,
    8191, 41 (all T>=41 >> 2P+1), hence identical averages at every N.
  * Averages at base 5051: P8: N=8 -> 8, N=16 -> 18 ; P9: N=9 -> 100/9,
    N=18 -> 220/9. Same numbers at the other large offsets (r runs over every
    residue, T is far beyond the boundary effects).
  * Flats (avg(N)==avg(N-1)) over N in P-1..2P+1 are exactly [P, 2P]: lags that
    are multiples of P are always legal, their landing set is a full interval
    [b, T+b) whose last element T+b-1 no smaller lag can reach, so they are never
    covered and never a shadow.  N=2P+1 is NOT flat.  N=P-1, 2P-1 not flat.
  * Controls: base 0 differs from the claim numbers; ignore-cover forced False
    gives 0 at large base; forced True gives (P-1)*C(N,2) (e.g. 196 at P8,N=8);
    sizes-only cover (len(b)<=len(a)) differs from the dict reference.
  * Edge: with T=0 (all landings empty) and lag 0 (landing at tick/bit 0) all
    four implementations agree on cover matrices and non-emptiness.
"""
import sys
import time
from fractions import Fraction
from math import comb

T0 = time.time()


# ----------------------------------------------------------------- model
def legal(t, L, P, w):
    return (t % P) >= w or ((t + L) % P) < w


def land_list(L, T, P, w):
    return [t + L for t in range(T) if legal(t, L, P, w)]


# ------------------------------------------------------- implementations
def impl_dict(P, w, T, lags):
    D = {L: {s: True for s in land_list(L, T, P, w)} for L in lags}
    cov = {}
    for a in lags:
        da = D[a]
        for b in lags:
            if a < b:
                cov[(a, b)] = all(k in da for k in D[b])
    return cov, {L: bool(D[L]) for L in lags}, {L: len(D[L]) for L in lags}, D


def impl_frozen(P, w, T, lags):
    F = {L: frozenset(land_list(L, T, P, w)) for L in lags}
    cov = {(a, b): F[b] <= F[a] for a in lags for b in lags if a < b}
    return cov, {L: bool(F[L]) for L in lags}, {L: len(F[L]) for L in lags}


def mask_periodic(L, T, P, w):
    """Landing mask built from one P-bit periodic word, repeated and shifted."""
    if T == 0:
        return 0
    pat = 0
    for j in range(P):                      # j = landing tick mod P
        if ((j - L) % P) >= w or j < w:
            pat |= 1 << j
    n = T + L
    k = -(-n // P)
    rep = pat * (((1 << (P * k)) - 1) // ((1 << P) - 1))   # repeat k times
    rep &= (1 << n) - 1                                    # horizon cut
    return (rep >> L) << L                                  # drop ticks < L


def mask_loop(L, T, P, w):
    ba = bytearray((T + L) // 8 + 2)
    for s in land_list(L, T, P, w):
        ba[s >> 3] |= 1 << (s & 7)
    return int.from_bytes(ba, "little")


def impl_bigint(P, w, T, lags):
    M = {L: mask_periodic(L, T, P, w) for L in lags}
    cov = {(a, b): (M[b] & ~M[a]) == 0 for a in lags for b in lags if a < b}
    return (cov, {L: M[L] != 0 for L in lags},
            {L: bin(M[L]).count("1") for L in lags}, M)


def impl_arith(P, w, T, lags):
    """No landing lists: b covered by a iff every legal t for b has t+d legal
    for a with t+d<T (landing t+b == (t+d)+a)."""
    ne = {L: any(legal(t, L, P, w) for t in range(min(T, P))) for L in lags}
    cov = {}
    for a in lags:
        for b in lags:
            if a >= b:
                continue
            d = b - a
            ok = True
            for t in range(max(0, T - d), T):          # would overshoot horizon
                if legal(t, b, P, w):
                    ok = False
                    break
            if ok:
                for t in range(min(max(T - d, 0), P)):  # periodic in t mod P
                    if legal(t, b, P, w) and not legal(t + d, a, P, w):
                        ok = False
                        break
            cov[(a, b)] = ok
    return cov, ne, None


IMPLS = ["dict", "frozen", "bigint", "arith"]
EB_SHADOW = True  # literal reading: both empty -> cut None != last a -> shadow


def vec_for(cov, ne, size, lags, mode, eb=None):
    eb = EB_SHADOW if eb is None else eb
    top = max(lags)
    vec = [0] * (top + 1)
    for (a, b), c0 in cov.items():
        if mode == "normal":
            c = c0
        elif mode == "forceF":
            c = False
        elif mode == "forceT":
            c = True
        elif mode == "sizes":
            c = size[b] <= size[a]
        if not ne[a] and not ne[b] and not eb:
            continue
        cut = b if not c else (a if ne[a] else None)
        last = b if ne[b] else a
        if cut != last:
            vec[b] += 1
    return vec


def build_all(P, w, T, lags):
    out = {}
    out["dict"] = impl_dict(P, w, T, lags)
    out["frozen"] = impl_frozen(P, w, T, lags)
    out["bigint"] = impl_bigint(P, w, T, lags)
    out["arith"] = impl_arith(P, w, T, lags)
    return out


def check_masks(out, lags):
    D = out["dict"][3]
    M = out["bigint"][3]
    bad = 0
    for L in lags:
        ba = bytearray(max(M[L].bit_length(), max(D[L], default=0) + 1) // 8 + 2)
        for s in D[L]:
            ba[s >> 3] |= 1 << (s & 7)
        if int.from_bytes(ba, "little") != M[L]:
            bad += 1
    return bad


# ------------------------------------------------------------- main sweep
def sweep(P, base, modes=("normal",), verbose_mism=True):
    lags = list(range(1, 2 * P + 2))
    top = 2 * P + 1
    vecs = {m: {} for m in modes}          # mode -> (w,r) -> vec  (dict impl)
    impl_vecs = {i: {} for i in IMPLS}     # normal vec per impl
    mism = {"cov": 0, "ne": 0, "size": 0, "vec": 0, "mask": 0}
    for w in range(1, P):
        for r in range(P):
            T = base + r
            out = build_all(P, w, T, lags)
            cd, ned, sd = out["dict"][0], out["dict"][1], out["dict"][2]
            for i in IMPLS[1:]:
                ci, ni = out[i][0], out[i][1]
                if ci != cd:
                    mism["cov"] += 1
                if ni != ned:
                    mism["ne"] += 1
                if out[i][2] is not None and out[i][2] != sd:
                    mism["size"] += 1
            mism["mask"] += check_masks(out, lags)
            for i in IMPLS:
                impl_vecs[i][(w, r)] = vec_for(out[i][0], out[i][1], sd, lags, "normal")
            for m in modes:
                vecs[m][(w, r)] = vec_for(cd, ned, sd, lags, m)
    for i in IMPLS[1:]:
        if impl_vecs[i] != impl_vecs["dict"]:
            mism["vec"] += sum(1 for k in impl_vecs["dict"]
                               if impl_vecs[i][k] != impl_vecs["dict"][k])
    return vecs, impl_vecs, mism


def avgs_from(vecs, P):
    top = 2 * P + 1
    tot = [0] * (top + 2)                  # per-b totals
    for v in vecs.values():
        for b in range(2, top + 1):
            tot[b] += v[b]
    out = {}
    run = 0
    for N in range(2, top + 1):
        run += tot[N]
        out[N] = Fraction(run, P)
    return out


def flats(av, P):
    return [N for N in range(P - 1, 2 * P + 2) if av[N] == av[N - 1]]


def fmt(fr):
    return str(fr)


results = {}
ALL_OK = True
notes = []
OFFSETS = [5051, 3989, 8191, 41, 0]
CLAIM = {8: {8: Fraction(8), 16: Fraction(18)},
         9: {9: Fraction(100, 9), 18: Fraction(220, 9)}}
FLAT_EXPECT = {}
for P in (8, 9):
    FLAT_EXPECT[P] = [P, 2 * P]

for P in (8, 9):
    for base in OFFSETS:
        modes = ("normal", "forceF", "forceT", "sizes")
        vecs, ivecs, mism = sweep(P, base, modes)
        results[(P, base)] = {m: avgs_from(vecs[m], P) for m in modes}
        av = results[(P, base)]["normal"]
        eq = all(v == 0 for v in mism.values())
        print(f"P={P} base={base:5d} impl-equal={eq} mism={mism} "
              f"t={time.time()-T0:.1f}s")
        print("   normal avg N=P-1..2P+1:",
              [fmt(av[N]) for N in range(P - 1, 2 * P + 2)])
        print("   flats:", flats(av, P))
        if not eq:
            ALL_OK = False
            notes.append(f"impl mismatch P{P} base{base}")
        if base != 0:
            for N, val in CLAIM[P].items():
                if av[N] != val:
                    ALL_OK = False
                    notes.append(f"claim num P{P} base{base} N{N}={av[N]}")
            if flats(av, P) != FLAT_EXPECT[P]:
                ALL_OK = False
                notes.append(f"flats P{P} base{base}: {flats(av, P)}")
        print("   forceF N=P,2P:", fmt(results[(P, base)]["forceF"][P]),
              fmt(results[(P, base)]["forceF"][2 * P]),
              "| forceT N=P,2P:", fmt(results[(P, base)]["forceT"][P]),
              fmt(results[(P, base)]["forceT"][2 * P]),
              "| (P-1)C(N,2):", (P - 1) * comb(P, 2), (P - 1) * comb(2 * P, 2))
        print("   sizes-only N=P,2P:", fmt(results[(P, base)]["sizes"][P]),
              fmt(results[(P, base)]["sizes"][2 * P]),
              "flats:", flats(results[(P, base)]["sizes"], P))

# ---- all N 2..2P+1 comparison across offsets (prefix sums) and controls
ctrl = {}
for P in (8, 9):
    ref = results[(P, 5051)]["normal"]
    same_all_N = {}
    for base in OFFSETS:
        same_all_N[base] = (results[(P, base)]["normal"] == ref)
    print(f"P={P} all-N (2..{2*P+1}) normal avg equal to base5051:", same_all_N)
    print(f"P={P} full avg list @5051:", [fmt(ref[N]) for N in range(2, 2 * P + 2)])
    base0_differs = results[(P, 0)]["normal"] != ref
    f0 = all(results[(P, 5051)]["forceF"][N] == 0 for N in range(2, 2 * P + 2))
    ft = all(results[(P, 5051)]["forceT"][N] == (P - 1) * comb(N, 2)
             for N in range(2, 2 * P + 2))
    sz_diff = results[(P, 5051)]["sizes"] != ref
    ctrl[P] = dict(base0_differs=base0_differs, forceF_zero=f0,
                   forceT_all_pairs=ft, sizes_differs=sz_diff)
    print(f"P={P} controls:", ctrl[P])
    print(f"P={P} base0 avg N=P,2P:", fmt(results[(P, 0)]["normal"][P]),
          fmt(results[(P, 0)]["normal"][2 * P]),
          "flats:", flats(results[(P, 0)]["normal"], P))

# ---- edge cases: empty landing lists, lag 0 / bit 0, small T, both conventions
edge_ok = True
edge_info = []
for P in (8, 9):
    lags = list(range(0, 2 * P + 2))
    n_empty = 0
    n_bit0 = 0
    diffcount = {True: 0, False: 0}
    for T in range(0, 6):
        for w in range(1, P):
            out = build_all(P, w, T, lags)
            cd, ned = out["dict"][0], out["dict"][1]
            for i in IMPLS[1:]:
                if out[i][0] != cd or out[i][1] != ned:
                    edge_ok = False
                    edge_info.append(f"edge mismatch {i} P{P} T{T} w{w}")
            if out["bigint"][3][0] & 1 and T > 0:
                n_bit0 += 1          # lag 0 lands at tick 0 -> bit 0 set
            if T > 0 and not (out["bigint"][3][0] & 1):
                edge_ok = False
                edge_info.append("lag0 bit0 not set")
            if out["dict"][3][0].get(0) is not None and not (out["bigint"][3][0] & 1):
                edge_ok = False
            n_empty += sum(1 for L in lags if not ned[L])
            if check_masks(out, lags):
                edge_ok = False
                edge_info.append(f"mask mismatch P{P} T{T} w{w}")
            sd = out["dict"][2]
            for eb in (True, False):
                vs = {i: vec_for(out[i][0], out[i][1], sd, lags, "normal", eb)
                      for i in IMPLS}
                if any(vs[i] != vs["dict"] for i in IMPLS):
                    edge_ok = False
                    edge_info.append(f"edge vec mismatch eb={eb}")
                diffcount[eb] += sum(vs["dict"])
    print(f"edge P={P}: empty-list lag instances={n_empty}, lag0-bit0 cases={n_bit0},"
          f" shadows at T<6 (EB counted={diffcount[True]}, not counted={diffcount[False]})")
print("edge_ok:", edge_ok, edge_info[:3])

# ---- extra moduli, informational (bigint vs dict, same sweep at 5051)
extra = {}
for P in (5, 6, 7, 10):
    vecs, ivecs, mism = sweep(P, 5051, ("normal",))
    av = avgs_from(vecs["normal"], P)
    extra[P] = (all(v == 0 for v in mism.values()), flats(av, P),
                fmt(av[P]), fmt(av[2 * P]))
    print(f"extra P={P}: impl-equal={extra[P][0]} flats={extra[P][1]} "
          f"avg(P)={extra[P][2]} avg(2P)={extra[P][3]}")

if not edge_ok:
    ALL_OK = False
    notes.append("edge")

a8 = results[(8, 5051)]["normal"]
a9 = results[(9, 5051)]["normal"]
summary = (f"bigint==dict==frozenset==arith at offsets {OFFSETS} P8,9; "
           f"P8 N=8:{a8[8]} N=16:{a8[16]}; P9 N=9:{a9[9]} N=18:{a9[18]}; "
           f"flats P8 {flats(a8, 8)} P9 {flats(a9, 9)}; controls {ctrl}; "
           f"edge_ok={edge_ok}; runtime {time.time()-T0:.0f}s; notes={notes}")
print("RESULT: " + ("PASS " if ALL_OK else "FAIL ") + summary)
