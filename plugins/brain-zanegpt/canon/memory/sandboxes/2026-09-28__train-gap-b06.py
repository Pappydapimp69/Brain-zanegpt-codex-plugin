"""Deterministic sandbox: `brain train gap`, batch 6 (loops 26-30).

Each loop applies one ideas kernel that no memory entry had built against,
reproduces its claim, then pushes until it finds where the claim stops
holding. No real timing: every clock is a parameter. The only randomness is
a seeded splitmix64, so every run prints identical numbers. Loop 30 runs in
real Node.js (substrate varied on purpose); the rest are Python models.
"""
import math, os, struct, subprocess, tempfile, json

M64 = 0xFFFFFFFFFFFFFFFF


def splitmix64(x):
    x = (x + 0x9E3779B97F4A7C15) & M64
    z = x
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
    return z ^ (z >> 31)


class Rng:
    def __init__(self, seed):
        self.s = seed & M64

    def u(self):
        self.s = (self.s + 0x9E3779B97F4A7C15) & M64
        return (splitmix64(self.s) >> 11) / float(1 << 53)

    def below(self, n):
        return int(self.u() * n)

    def normal(self):
        a, b = max(self.u(), 1e-300), self.u()
        return math.sqrt(-2 * math.log(a)) * math.cos(2 * math.pi * b)


def banner(n, title):
    print("=" * 78); print(f"LOOP {n} -- {title}"); print("=" * 78)


# ============================================================ LOOP 26 ====
def loop26_assert_settled():
    """Kernel testing/harness/assert-on-settled-not-first-sighting: a poller
    catches a progressive reveal mid-flight; wait for the settled value
    (ends in punctuation, stable across two polls, or a later control)."""
    banner(26, "typewriter reveal: four ways to decide the text has settled")
    WORDS = "the lamp is lit so we wait here until dawn and then we go".split()

    def make_text(r):
        sents = []
        for _ in range(1 + r.below(3)):
            n = 3 + r.below(6)
            s = " ".join(WORDS[r.below(len(WORDS))] for _ in range(n))
            sents.append(s[0].upper() + s[1:] + (". " if r.u() < 0.7 else ", "))
        return "".join(sents).rstrip(", ").rstrip() + "."

    def reveal_schedule(text, r):
        """ms at which each prefix length becomes visible; punctuation pauses."""
        t, times = 0, []
        for ch in text:
            t += 30 + r.below(20)
            if ch in ".,":
                t += 400
            times.append(t)
        return times

    def run(poll, rule, seed):
        r = Rng(seed)
        text = make_text(r)
        times = reveal_schedule(text, r)
        done_at = times[-1] + 1                       # the continue control appears after
        def shown(t):
            n = sum(1 for x in times if x <= t)
            return text[:n]
        t, prev = 0, None
        while t < done_at + 5000:
            t += poll
            s = shown(t)
            if rule == "first-sighting" and s:
                return s == text
            if rule == "ends-in-punctuation" and s and s[-1] in ".!?":
                return s == text
            if rule == "stable-two-polls" and s and s == prev:
                return s == text
            if rule == "after-control" and t >= done_at:
                return s == text
            prev = s
        return False
    res = {}
    for poll in (50, 200, 500):
        row = []
        for rule in ("first-sighting", "ends-in-punctuation", "stable-two-polls", "after-control"):
            bad = sum(not run(poll, rule, s) for s in range(1000))
            res[(poll, rule)] = bad
            row.append(f"{rule} {bad}")
        print(f"  poll {poll:3d} ms, wrong text asserted in 1000 reveals: " + ", ".join(row))
    return res


# ============================================================ LOOP 27 ====
def loop27_tell_rate():
    """Kernel gamedev/feedback/rate-a-perceptual-tell-by-its-observed-rate:
    the observed rate is nominal x each gate's open fraction over the true
    window length (median, not mean)."""
    banner(27, "tell rate: product of gates, gate correlation, median vs mean window")
    NOM, DT = 0.07, 0.1

    K = 8                                               # candidate monsters

    def simulate(correlated, restrict, seed, windows=4000):
        r = Rng(seed)
        total_t = vis = fired = 0
        with_one = 0
        lens = []

        def p_on(inr):
            return (0.5 if inr else 0.0) if correlated else 0.2
        for _ in range(windows):
            L = 7.0 * math.exp(1.0 * r.normal())       # lognormal, median 7 s
            lens.append(L)
            steps = int(L / DT)
            inr = r.u() < 0.4
            ons = [r.u() < p_on(inr) for _ in range(K)]
            got = 0
            for _ in range(steps):
                if r.u() < DT / 3.0:                    # range gate, mean dwell 3 s
                    inr = r.u() < 0.4
                for c in range(K):
                    if r.u() < DT / 1.5:                # each candidate's on-screen gate, dwell 1.5 s
                        ons[c] = r.u() < p_on(inr)
                if r.u() < NOM * DT:
                    if restrict:
                        pool = [c for c in range(K) if ons[c]]
                        if not pool:
                            continue                     # nothing on screen: skip the firing
                        pick = pool[r.below(len(pool))]
                    else:
                        pick = r.below(K)
                    fired += 1
                    if inr and ons[pick]:
                        vis += 1; got += 1
            total_t += steps * DT
            with_one += got > 0
        lens.sort()
        return vis / total_t, fired / total_t, with_one / windows, lens[len(lens) // 2], sum(lens) / len(lens)

    res = {}
    for correlated in (False, True):
        rate, fr, w1, med, mean = simulate(correlated, False, 27 + correlated)
        res[correlated] = rate
        tag = "correlated gates" if correlated else "independent gates"
        print(f"  {tag:17s}: product of marginals {NOM * 0.4 * 0.2:.4f}/s -> observed {rate:.4f}/s "
              f"(one per {1 / rate:.0f} s); windows with >=1 visible: {w1:.1%}")
    print(f"  window length median {med:.1f} s, mean {mean:.1f} s: P(>=1) sized by the mean "
          f"{1 - math.exp(-NOM * 0.4 * 0.2 * mean):.1%}, by the median {1 - math.exp(-NOM * 0.4 * 0.2 * med):.1%}")
    rate_r, fired_r, w1_r, _m, _mm = simulate(False, True, 99)
    _r0, fired_0, _w, _m2, _mm2 = simulate(False, False, 99)
    print(f"  restrict picks to on-screen candidates (independent gates): observed {rate_r:.4f}/s "
          f"({rate_r / res[False]:.1f}x), total firings {fired_r:.4f}/s vs {fired_0:.4f}/s unrestricted")
    return res, rate_r


# ============================================================ LOOP 28 ====
def loop28_lattice_collision():
    """Kernel SYSTEM/determinism/integer-lattice-and-collision-precision: tie
    lattice resolution to the smallest half-extent; coarse lattices drift and
    alias different half-extents to one count."""
    banner(28, "quantised vs float overlap: net count vs per-event disagreement")
    SEEDS, STEPS, BODIES = 20, 400, 12

    def run(q, half, seed):
        r = Rng(seed)
        pos = [[r.u() * 20, r.u() * 20] for _ in range(BODIES)]
        vel = [[(r.u() - 0.5) * 0.3, (r.u() - 0.5) * 0.3] for _ in range(BODIES)]
        fp = fn = both = 0
        for _ in range(STEPS):
            for p, v in zip(pos, vel):
                for k in (0, 1):
                    p[k] += v[k]
                    if p[k] < 0 or p[k] > 20:
                        v[k] = -v[k]
            qp = [[round(c / q) * q for c in p] for p in pos] if q else pos
            for i in range(BODIES):
                for j in range(i + 1, BODIES):
                    tf = abs(pos[i][0] - pos[j][0]) < 2 * half and abs(pos[i][1] - pos[j][1]) < 2 * half
                    tq = abs(qp[i][0] - qp[j][0]) < 2 * half and abs(qp[i][1] - qp[j][1]) < 2 * half
                    both += tf and tq; fp += tq and not tf; fn += tf and not tq
        return both + fn, both + fp, fp + fn

    res = {}
    for q in (0.01, 0.1, 0.5):
        row = []
        counts = {}
        for half in (0.25, 0.3, 0.5, 1.0):
            ft = qt = dis = 0
            for s in range(SEEDS):
                f, qq, d = run(q, half, s)
                ft += f; qt += qq; dis += d
            counts[half] = qt
            res[(q, half)] = (ft, qt, dis)
            row.append(f"h={half}: net {100 * (qt - ft) / ft:+5.1f}% wrong {100 * dis / ft:5.1f}%")
        print(f"  lattice {q:<4}: " + "; ".join(row))
        print(f"               quantised counts {counts}")
    return res


# ============================================================ LOOP 29 ====
def f32(x):
    return struct.unpack("f", struct.pack("f", x))[0]


def loop29_modulated_filter():
    """Kernel DSP/filter-design/modulated-resonant-filter-needs-bounded-topology:
    DF2T state misbehaves under per-sample modulation; DF1 or an SVF/TPT
    filter stays bounded."""
    banner(29, "resonant lowpass under cutoff modulation: DF1, DF2T, TPT SVF")
    FS = 48000.0

    def coeffs(fc, q):
        w = 2 * math.pi * fc / FS
        cw, sw = math.cos(w), math.sin(w)
        al = sw / (2 * q)
        a0 = 1 + al
        b0 = (1 - cw) / 2 / a0; b1 = (1 - cw) / a0; b2 = b0
        a1 = -2 * cw / a0; a2 = (1 - al) / a0
        return b0, b1, b2, a1, a2

    def run(topology, fc_of, q, n, x_of, rnd):
        x1 = x2 = y1 = y2 = 0.0
        s1 = s2 = 0.0
        ic1 = ic2 = 0.0
        peak = 0.0
        for i in range(n):
            x = x_of(i)
            fc = fc_of(i)
            if topology == "svf":
                g = math.tan(math.pi * fc / FS); k = 1 / q
                a1 = 1 / (1 + g * (g + k)); a2 = g * a1; a3 = g * a2
                v3 = rnd(x - ic2)
                v1 = rnd(a1 * ic1 + a2 * v3)
                v2 = rnd(ic2 + a2 * ic1 + a3 * v3)
                ic1 = rnd(2 * v1 - ic1); ic2 = rnd(2 * v2 - ic2)
                y = v2
            else:
                b0, b1, b2, a1, a2 = coeffs(fc, q)
                if topology == "df1":
                    y = rnd(b0 * x + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2)
                    x2, x1, y2, y1 = x1, x, y1, y
                else:                                   # DF2T
                    y = rnd(b0 * x + s1)
                    s1 = rnd(b1 * x - a1 * y + s2)
                    s2 = rnd(b2 * x - a2 * y)
            peak = max(peak, abs(y)) if y == y else float("inf")
        return peak

    r = Rng(29)
    noise = [(r.u() - 0.5) * 2 for _ in range(48000)]
    sq = lambda i: 1.0 if (i // 60) % 2 == 0 else -1.0      # 400 Hz square
    res = {}
    cases = [
        ("static 2 kHz", lambda i: 2000.0),
        ("LFO 5 Hz, 200 Hz-8 kHz", lambda i: 200.0 * 40 ** (0.5 + 0.5 * math.sin(2 * math.pi * 5 * i / FS))),
        ("jump 100 Hz<->12 kHz every 64", lambda i: 100.0 if (i // 64) % 2 else 12000.0),
        ("jump every 7 samples", lambda i: 100.0 if (i // 7) % 2 else 12000.0),
    ]
    for q in (0.707, 10.0, 40.0):
        for name, fc_of in cases:
            row = []
            for precision, rnd in (("f64", lambda v: v), ("f32", f32)):
                for topo in ("df1", "df2t", "svf"):
                    pk = run(topo, fc_of, q, 12000, lambda i: sq(i), rnd)
                    res[(q, name, precision, topo)] = pk
                    row.append(f"{topo}/{precision} {pk:8.2f}")
            print(f"  Q={q:<5} {name:30s} peak |y| (square in, peak 1): " + " ".join(row))
    return res


# ============================================================ LOOP 30 ====
JS30 = r"""
// Client prediction + server reconciliation, deterministic.
function step(p, inp) { return [p[0] + inp[0], p[1] + inp[1]]; }
function scenario(replayMode, opts) {
  let newest = null;
  const {inputs, latency, bufferCap, ackOrder, serverBlocks} = opts;
  let client = [0, 0], server = [0, 0];
  const buffer = [];               // {seq, inp}
  const acks = [];                 // {seq, pos, at}
  let bad = 0, lastAck = -1;
  for (let t = 0; t < inputs.length + latency + 3; t++) {
    if (t < inputs.length) {
      const inp = inputs[t];
      client = step(client, inp);
      buffer.push({seq: t, inp});
      if (buffer.length > bufferCap) buffer.shift();
      // server applies it (maybe blocked by a wall) and acks after latency
      const blocked = serverBlocks && serverBlocks.has(t);
      server = blocked ? server : step(server, inp);
      acks.push({seq: t, pos: server.slice(), at: t + latency + (ackOrder ? ackOrder(t) : 0)});
    }
    const due = acks.filter(a => a.at === t);
    for (const a of due) {
      if (replayMode === "buffered+drop-stale") { if (a.seq <= lastAck) continue; lastAck = a.seq; }
      if (replayMode === "discard-by-count") {
        buffer.splice(0, Math.min(buffer.length, 1));
      } else {
        while (buffer.length && buffer[0].seq <= a.seq) buffer.shift();
      }
      let p = a.pos.slice();
      const current = t < inputs.length ? inputs[t] : [0, 0];
      for (const b of buffer) p = step(p, replayMode === "current-input" ? current : b.inp);
      client = p;
      // truth: the NEWEST ack's server state plus every input predicted after it, in order
      if (!newest || a.seq > newest.seq) newest = a;
      let truth = newest.pos.slice();
      for (let s2 = newest.seq + 1; s2 <= Math.min(t, inputs.length - 1); s2++) truth = step(truth, inputs[s2]);
      if (client[0] !== truth[0] || client[1] !== truth[1]) bad++;
    }
  }
  return bad;
}
const R = [1, 0], U = [0, 1], L = [-1, 0], D = [0, -1];
const out = {};
// the kernel's example: right 2 then up 3, first ack arrives after all five were predicted
{
  const inputs = [R, R, U, U, U];
  let c = [0, 0]; for (const i of inputs) c = step(c, i);
  const ack = [1, 0];
  let good = ack.slice(), bad = ack.slice();
  for (const i of inputs.slice(1)) { good = step(good, i); bad = step(bad, U); }
  out.example = {predicted: c, buffered: good, currentInput: bad};
}
function rng(seed) { let s = BigInt(seed); return () => { s = (s * 6364136223846793005n + 1442695040888963407n) & ((1n << 64n) - 1n); return Number(s >> 33n) / 2 ** 31; }; }
const modes = ["current-input", "buffered", "discard-by-count", "buffered+drop-stale"];
for (const setup of ["steady", "wall", "reorder", "spike-small-buffer"]) {
  const errs = {}; for (const m of modes) errs[m] = 0;
  for (let seed = 0; seed < 500; seed++) {
    const r = rng(seed + 1);
    const inputs = []; let cur = R;
    for (let i = 0; i < 60; i++) { if (r() < 0.15) cur = [R, U, L, D][Math.floor(r() * 4)]; inputs.push(cur); }
    const opts = {inputs, latency: 4, bufferCap: 64, ackOrder: null, serverBlocks: null};
    if (setup === "wall") { const s = new Set(); for (let i = 0; i < 60; i++) if (r() < 0.05) s.add(i); opts.serverBlocks = s; }
    if (setup === "reorder") opts.ackOrder = t => (t % 5 === 2 ? 2 : 0);
    if (setup === "spike-small-buffer") { opts.latency = 12; opts.bufferCap = 8; }
    for (const m of modes) errs[m] += scenario(m, opts) > 0;
  }
  out[setup] = errs;
}
console.log(JSON.stringify(out));
"""


def loop30_prediction():
    """Kernel NETWORKING/client-prediction/reconciliation-must-replay-buffered-
    inputs: replay each unacked step's own buffered input, never the current
    input."""
    banner(30, "client reconciliation in real Node: replay source, acks, buffer size")
    with tempfile.TemporaryDirectory() as d:
        js = os.path.join(d, "p.js")
        open(js, "w").write(JS30)
        ver = subprocess.run(["node", "--version"], capture_output=True, text=True).stdout.strip()
        out = json.loads(subprocess.run(["node", js], capture_output=True, text=True).stdout)
    ex = out.pop("example")
    print(f"  node {ver}; kernel example (R,R,U,U,U, acked through step 1): predicted {ex['predicted']}, "
          f"buffered replay {ex['buffered']}, current-input replay {ex['currentInput']}")
    for setup, errs in out.items():
        print(f"  {setup:18s}: runs (of 500) where a reconciliation left the client off the true position: " +
              ", ".join(f"{m} {c}" for m, c in errs.items()))
    return ex, out


if __name__ == "__main__":
    loop26_assert_settled()
    loop27_tell_rate()
    loop28_lattice_collision()
    loop29_modulated_filter()
    loop30_prediction()
