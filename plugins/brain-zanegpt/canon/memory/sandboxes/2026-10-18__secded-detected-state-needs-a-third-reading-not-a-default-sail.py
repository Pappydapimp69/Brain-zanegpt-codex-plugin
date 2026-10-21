# Composes ideas:ERROR-CORRECTION/single-error-correcting-code-miscorrects-double-errors (Hamming SEC turns a double
# error into a silent wrong correction; one overall parity bit makes it a detected failure), storyteller-theseus-sail
# (a signal's default state, when nobody updates it, sends its meaning: false-bad 100, false-good 20, wait 1) and
# trial-balance-sees-only-the-unbalanced-error (a parity-type check sees only errors that change the parity).
# Model: one success/fail flag is data bit 1 of an 8-bit word sent as Hamming(12,8) (SEC) or with an overall parity bit
# (13,8, SECDED). Each bit flips independently with probability p. Exact: all 2^n flip patterns, weighted p^w(1-p)^(n-w).
# Decoder verdicts for the flag: right, flipped (silent), detected (SECDED only). Truth is success with prior 0.7.
# Policies for a detected word: default-bad (read as fail), default-good (read as success), wait (a third reading).
# PREDICTION (before run): at p 0.02 SECDED+wait costs under a third of SEC's expected cost per word; SECDED with a
# default-bad policy costs more than SECDED+wait; at p 0.30 (BREAK) the 3-flip patterns that look like one flip keep
# SECDED's silent-flipped share above 10% of words and its advantage over SEC drops under 1.5x.
import itertools
POS = [i for i in range(1, 13) if i & (i - 1)]            # 8 data positions (non powers of two) in a 12-bit word
FLAGPOS = POS[0]
def encode(bits8, ext):
    w = [0] * 13
    for p, b in zip(POS, bits8): w[p] = b
    for r in (1, 2, 4, 8):
        w[r] = sum(w[i] for i in range(1, 13) if i & r and i != r) % 2
    if ext: w[0] = sum(w[1:13]) % 2
    return w
def decode_flag(w, ext):
    s = 0
    for r in (1, 2, 4, 8):
        if sum(w[i] for i in range(1, 13) if i & r) % 2: s |= r
    par = sum(w[0:13]) % 2 if ext else None
    w = w[:]
    if ext:
        if s and par == 0: return "detected"
        if s > 12: return "detected"          # syndrome points outside the word: cannot be a single flip
        if s and par == 1: w[s] ^= 1
        elif not s and par == 1: w[0] ^= 1
    elif s and s <= 12: w[s] ^= 1
    return w[FLAGPOS]
def outcomes(ext, p):
    n = 13 if ext else 12
    res = {"right": 0.0, "flipped": 0.0, "detected": 0.0}
    for flag in (0, 1):
        data = [flag] + [1, 0, 1, 1, 0, 0, 1]
        base = encode(data, ext)
        for e in itertools.product((0, 1), repeat=n):
            wt = sum(e); pr = p ** wt * (1 - p) ** (n - wt)
            w = base[:]
            for pos, flip in zip(range(0 if ext else 1, 13), e): w[pos] ^= flip
            r = decode_flag(w, ext)
            k = "detected" if r == "detected" else ("right" if r == flag else "flipped")
            res[k] += pr / 2
    return res
COST = {"fb": 100.0, "fg": 20.0, "wait": 1.0}; PS = 0.7
def cost(res, policy):
    # flipped: success read bad costs fb, fail read good costs fg (flag 1 = success)
    flipped = res["flipped"] * (PS * COST["fb"] + (1 - PS) * COST["fg"])
    det = {"bad": PS * COST["fb"], "good": (1 - PS) * COST["fg"], "wait": COST["wait"]}[policy] * res["detected"]
    return flipped + det
rows = {}
for p in (0.02, 0.30):
    sec, sd = outcomes(False, p), outcomes(True, p)
    rows[p] = (sec, sd, cost(sec, "wait"), {k: cost(sd, k) for k in ("bad", "good", "wait")})
    print(f"p {p}: SEC right {sec['right']:.4f} flipped {sec['flipped']:.4f}; SECDED right {sd['right']:.4f} flipped {sd['flipped']:.4f} detected {sd['detected']:.4f}; "
          f"cost SEC {rows[p][2]:.3f}, SECDED bad {rows[p][3]['bad']:.3f} good {rows[p][3]['good']:.3f} wait {rows[p][3]['wait']:.3f}")
lo, hi = rows[0.02], rows[0.30]
ok = (lo[3]["wait"] < lo[2] / 3 and lo[3]["bad"] > lo[3]["wait"] and hi[1]["flipped"] > 0.10 and lo[2] / lo[3]["wait"] > 3 and hi[2] / hi[3]["wait"] < 1.5)
print(f"RESULT: {'PASS' if ok else 'FAIL'} p .02 SEC cost {lo[2]:.3f} vs SECDED+wait {lo[3]['wait']:.3f} vs SECDED+bad {lo[3]['bad']:.3f}; p .30 SECDED silent-flipped {hi[1]['flipped']:.3f}, SEC/SECDED+wait ratio {hi[2]/hi[3]['wait']:.2f}")
