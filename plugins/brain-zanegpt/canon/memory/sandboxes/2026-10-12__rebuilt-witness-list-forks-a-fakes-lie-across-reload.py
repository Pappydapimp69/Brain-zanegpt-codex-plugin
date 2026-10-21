"""Sandbox: a fake's side-stream lie survives save/resume only if the witnessed-fact
list it INDEXES is saved verbatim, even when every draw-count and state-word rule holds.

Composed: seven E1 (fixed total draws), seven E48 (save rng state words),
seven E20 (facts recorded from state), seven E40 (reading answers).
Stdlib only, deterministic (fixed seeds, sha256 side stream). Runs well under 1 s.
"""
import hashlib

NIGHT_DRAWS = 6
TRIALS = 3000
MASK = 0xFFFFFFFF


class Sfc32:
    def __init__(self, seed):
        self.a, self.b, self.c, self.d = 0, seed & MASK, (seed >> 32) & MASK, 1
        self.draws = 0
        for _ in range(12):
            self.next()
        self.draws = 0

    def next(self):
        a, b, c, d = self.a, self.b, self.c, self.d
        t = (a + b + d) & MASK
        d = (d + 1) & MASK
        a = b ^ (b >> 9)
        b = (c + (c << 3)) & MASK
        c = ((c << 21) | (c >> 11)) & MASK
        c = (c + t) & MASK
        self.a, self.b, self.c, self.d = a, b, c, d
        self.draws += 1
        return t / 4294967296.0

    def words(self):
        return (self.a, self.b, self.c, self.d)

    @classmethod
    def from_words(cls, w):
        r = cls.__new__(cls)
        r.a, r.b, r.c, r.d = w
        r.draws = 0
        return r


def side_u(*key):
    h = hashlib.sha256(repr(key).encode()).digest()
    return int.from_bytes(h[:8], "big") / 2.0 ** 64


def make_day(seed, day):
    """Run-stream day: fixed NIGHT_DRAWS draws, facts and witness flags from them."""
    r = Sfc32(seed * 1000 + day)
    us = [r.next() for _ in range(NIGHT_DRAWS)]          # constant count
    n = 4 + int(us[0] * 7)                                # 4..10 facts
    facts = []
    for i in range(n):
        u = side_u("fact", seed, day, i)                  # hash, not rng: no draws
        facts.append({"id": "f%02d" % i, "t": i, "place": side_u("place", seed, day, i),
                      "seen": u < 0.7 or i == 0 or i == 1})
    witnessed_time_order = [f["id"] for f in facts if f["seen"]]
    return r, us, facts, witnessed_time_order


def pick_index(seed, fake, day, wl):
    u = side_u("lie", seed, fake, day)                    # asking draws nothing from run stream
    return wl[int(u * len(wl))]


def pick_minhash(seed, fake, day, wl):
    return min(wl, key=lambda fid: side_u("lie", seed, fake, day, fid))


def rebuild(mode, seed, day, facts, saved):
    if mode == "verbatim":
        return list(saved)
    if mode == "reorder":       # rebuilt by scanning places instead of time: same set, new order
        seen = [f for f in facts if f["seen"]]
        return [f["id"] for f in sorted(seen, key=lambda f: f["place"])]
    if mode == "sorted":        # canonical id sort on BOTH sides (saved list compared sorted)
        return sorted(saved)
    if mode == "drop":          # lossy rebuild forgets one witnessed fact (deterministic choice)
        if len(saved) <= 1:
            return list(saved)
        k = int(side_u("drop", seed, day) * len(saved))
        return [x for j, x in enumerate(saved) if j != k]
    raise ValueError(mode)


def run(mode, picker, canon_sort=False):
    changed = 0
    run_stream_ok = 0
    draws = set()
    for trial in range(TRIALS):
        seed = 7001 + trial
        day = 1 + trial % 9
        fake = "m%d" % (trial % 5)
        r, us, facts, wl = make_day(seed, day)
        draws.add(r.draws)
        saved_wl = sorted(wl) if canon_sort else wl
        before = picker(seed, fake, day, saved_wl)
        words = r.words()
        nxt_true = r.next()
        # reload: rng from state words, witness list per mode
        r2 = Sfc32.from_words(words)
        if r2.next() == nxt_true:
            run_stream_ok += 1
        wl2 = rebuild(mode, seed, day, facts, saved_wl)
        if canon_sort:
            wl2 = sorted(wl2)
        after = picker(seed, fake, day, wl2)
        if after != before:
            changed += 1
    return changed / TRIALS, run_stream_ok / TRIALS, draws


def main():
    results = {}
    rows = [
        ("S1 verbatim save, index pick", "verbatim", pick_index, False),
        ("S2 reorder rebuild, index pick", "reorder", pick_index, False),
        ("S3 drop-one rebuild, index pick", "drop", pick_index, False),
        ("S4 reorder rebuild, min-hash pick", "reorder", pick_minhash, False),
        ("S5 drop-one rebuild, min-hash pick", "drop", pick_minhash, False),
        ("S6 BREAK: reorder rebuild, canonical sort, index pick", "reorder", pick_index, True),
        ("S7 drop-one rebuild, canonical sort, index pick", "drop", pick_index, True),
    ]
    for name, mode, picker, cs in rows:
        ch, ok, dr = run(mode, picker, cs)
        results[name] = (ch, ok, dr)
        # ask-reload-ask: real account never changes; story that changed = fake
        acc = 0.5 + 0.5 * ch
        print("%-55s lie changed %.3f  id-acc %.3f  run-stream resume %.3f  draws %s"
              % (name, ch, acc, ok, sorted(dr)))

    g = lambda k: results[k][0]
    all_resume = all(v[1] == 1.0 for v in results.values())
    all_const = all(v[2] == {NIGHT_DRAWS} for v in results.values())
    checks = [
        ("verbatim stable 0.000", g("S1 verbatim save, index pick") == 0.0),
        ("reorder index >= 0.70", g("S2 reorder rebuild, index pick") >= 0.70),
        ("drop index >= 0.60", g("S3 drop-one rebuild, index pick") >= 0.60),
        ("min-hash reorder 0.000", g("S4 reorder rebuild, min-hash pick") == 0.0),
        ("min-hash drop <= 0.25", g("S5 drop-one rebuild, min-hash pick") <= 0.25),
        ("canonical sort fixes reorder", g("S6 BREAK: reorder rebuild, canonical sort, index pick") == 0.0),
        ("canonical sort does not fix drop (>=0.40)", g("S7 drop-one rebuild, canonical sort, index pick") >= 0.40),
        ("run stream resumes exactly everywhere", all_resume),
        ("draw count constant everywhere", all_const),
        ("ask-reload-ask id-acc >= 0.85 under reorder", 0.5 + 0.5 * g("S2 reorder rebuild, index pick") >= 0.85),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("ok   " if ok else "MISS ") + n)
    summ = ("%d/%d; changed verbatim %.3f reorder %.3f drop %.3f; minhash reorder %.3f drop %.3f; "
            "sorted reorder %.3f drop %.3f; resume+draws constant %s"
            % (held, len(checks), g("S1 verbatim save, index pick"), g("S2 reorder rebuild, index pick"),
               g("S3 drop-one rebuild, index pick"), g("S4 reorder rebuild, min-hash pick"),
               g("S5 drop-one rebuild, min-hash pick"),
               g("S6 BREAK: reorder rebuild, canonical sort, index pick"),
               g("S7 drop-one rebuild, canonical sort, index pick"), all_resume and all_const))
    print("RESULT: %s %s" % ("PASS" if held == len(checks) else "FAIL", summ))


if __name__ == "__main__":
    main()
