#!/usr/bin/env python3
"""Sandbox: does E3's 'front-load the checksum for streaming' survive composition?

PREDICTION (written before the first run):
  P1 peak buffer on a 10,000-byte payload, chunk 500:
       trailing-whole=10000, leading-whole=500, per-chunk (all variants)=500.
  P2 one flipped byte in chunk 0: leading-whole RELEASES all 10000 bytes
       downstream before its verdict (rejects only at the end); trailing-whole
       and every per-chunk scheme release 0 unverified bytes.
  P3 dropped middle chunk: per-chunk-crc-only ACCEPTS silently; every scheme
       with a whole-stream check or seq+total rejects.
  P4 two chunks swapped: per-chunk-crc-only ACCEPTS; seq schemes reject.
  P5 tail truncation: per-chunk-crc-only AND per-chunk+seq (no declared total)
       ACCEPT; only declared-total / whole-stream schemes reject.
  P6 attacker rewrites a chunk and recomputes the (unkeyed) checksum: every
       crc scheme ACCEPTS; only the keyed per-chunk MAC rejects.
  P7 verified chunks decoded independently as UTF-8 corrupt clean text at 37 of
       the 40 wire-chunk sizes 1..40 (safe only at 11, 22, 33 = multiples of the
       11-byte repeating unit); an incremental decoder corrupts 0 of 40.
"""
import codecs
import hashlib
import hmac
import zlib

KEY = b"sandbox-key"
UNIT = "aé€\U0001F600 "           # 1+2+3+4+1 = 11 bytes
PAYLOAD = (UNIT * 909 + "x").encode("utf-8")  # 10000 bytes, valid UTF-8
assert len(PAYLOAD) == 10000
CH = 500


def split(b, n):
    return [b[i:i + n] for i in range(0, len(b), n)]


def crc(b):
    return zlib.crc32(b) & 0xFFFFFFFF


def mac(seq, total, b):
    m = hmac.new(KEY, seq.to_bytes(4, "big") + total.to_bytes(4, "big") + b, hashlib.sha256)
    return m.digest()[:8]


SCHEMES = ["trailing-whole", "leading-whole", "chunk-crc", "chunk-crc+seq",
           "chunk-crc+seq+total", "chunk-mac+seq+total"]


def tag_for(scheme, i, n, c):
    if scheme == "chunk-crc":
        return crc(c)
    if scheme == "chunk-crc+seq":
        return crc(i.to_bytes(4, "big") + c)
    if scheme == "chunk-crc+seq+total":
        return crc(i.to_bytes(4, "big") + n.to_bytes(4, "big") + c)
    if scheme == "chunk-mac+seq+total":
        return mac(i, n, c)
    return None


def build(scheme, payload=PAYLOAD):
    chunks = split(payload, CH)
    n = len(chunks)
    hdr = {"len": len(payload), "crc": crc(payload), "n": n}
    return hdr, [(i, c, tag_for(scheme, i, n, c)) for i, c in enumerate(chunks)]


def receive(scheme, hdr, items):
    """Return (accepted, peak_buffer, bytes_released_before_verdict, where_decided)."""
    peak = 0
    got = bytearray()
    if scheme == "trailing-whole":
        for i, c, tag in items:
            got += c
            peak = max(peak, len(got))
        ok = len(got) == hdr["len"] and crc(bytes(got)) == hdr["crc"]
        return ok, peak, 0, "end"
    if scheme == "leading-whole":
        run, released = 0, 0
        for i, c, tag in items:
            peak = max(peak, len(c))
            run = zlib.crc32(c, run)
            released += len(c)       # streamed on; verdict unknown until the end
            got += c
        ok = len(got) == hdr["len"] and (run & 0xFFFFFFFF) == hdr["crc"]
        return ok, peak, released, "end"
    expect = 0
    n_decl = hdr["n"]
    for i, c, tag in items:
        peak = max(peak, len(c))
        if scheme == "chunk-crc":
            good = crc(c) == tag
        elif scheme == "chunk-crc+seq":
            good = i == expect and crc(i.to_bytes(4, "big") + c) == tag
        elif scheme == "chunk-crc+seq+total":
            good = i == expect and crc(i.to_bytes(4, "big") + n_decl.to_bytes(4, "big") + c) == tag
        else:
            good = i == expect and hmac.compare_digest(mac(i, n_decl, c), tag)
        if not good:
            return False, peak, 0, "chunk%d" % i
        expect += 1
    if scheme in ("chunk-crc+seq+total", "chunk-mac+seq+total") and expect != n_decl:
        return False, peak, 0, "end-count"
    return True, peak, 0, "end"


def fault(name, scheme, hdr, items):
    items = list(items)
    if name == "flip-chunk0":
        i, c, t = items[0]
        items[0] = (i, bytes([c[0] ^ 1]) + c[1:], t)
    elif name == "drop-mid":
        del items[10]
    elif name == "swap":
        items[4], items[5] = items[5], items[4]
    elif name == "truncate-tail":
        items = items[:-3]
    elif name == "forge":
        # attacker replaces chunk 7 and recomputes whatever is UNKEYED
        i, c, t = items[7]
        new = b"E" * len(c)
        if scheme in ("trailing-whole", "leading-whole"):
            full = b"".join(x[1] for x in items[:7]) + new + b"".join(x[1] for x in items[8:])
            hdr = dict(hdr, crc=crc(full))
            t2 = None
        elif scheme == "chunk-mac+seq+total":
            t2 = t  # cannot recompute without the key; keeps the stale tag
        else:
            t2 = tag_for(scheme, i, hdr["n"], new)
        items[7] = (i, new, t2)
    return hdr, items


FAULTS = ["clean", "flip-chunk0", "drop-mid", "swap", "truncate-tail", "forge"]


def main():
    res = {}
    for s in SCHEMES:
        for f in FAULTS:
            h, it = build(s)
            h, it = fault(f, s, h, it)
            res[(s, f)] = receive(s, h, it)
    print("scheme                fault          accept peak  released decided")
    for s in SCHEMES:
        for f in FAULTS:
            a, p, r, d = res[(s, f)]
            print("%-21s %-14s %-6s %-5d %-8d %s" % (s, f, a, p, r, d))

    checks = []

    def chk(label, cond):
        checks.append((label, cond))
        print("  [%s] %s" % ("ok" if cond else "MISS", label))

    def accepted(f):
        return [s for s in SCHEMES if res[(s, f)][0]]

    print("--- prediction checks")
    peaks = {s: res[(s, "clean")][1] for s in SCHEMES}
    chk("P1 peaks %s" % peaks,
        peaks["trailing-whole"] == 10000 and all(peaks[s] == 500 for s in SCHEMES[1:]))
    lw = res[("leading-whole", "flip-chunk0")]
    chk("P2 flip-chunk0: leading-whole rejects only at end after releasing %d; others release 0" % lw[2],
        lw[2] == 10000 and not lw[0] and lw[3] == "end"
        and all(res[(s, "flip-chunk0")][2] == 0 and not res[(s, "flip-chunk0")][0]
                for s in SCHEMES if s != "leading-whole"))
    chk("P3 drop-mid accepted by %s" % accepted("drop-mid"), accepted("drop-mid") == ["chunk-crc"])
    chk("P4 swap accepted by %s" % accepted("swap"), accepted("swap") == ["chunk-crc"])
    chk("P5 truncate-tail accepted by %s" % accepted("truncate-tail"),
        accepted("truncate-tail") == ["chunk-crc", "chunk-crc+seq"])
    chk("P6 forge accepted by %s" % accepted("forge"), accepted("forge") == SCHEMES[:5])
    chk("control: clean accepted by all, flip-chunk0 by none",
        accepted("clean") == SCHEMES and accepted("flip-chunk0") == [])

    # P7: decode verified chunks independently vs incrementally, wire chunk sizes 1..40
    bad_indep, bad_incr, safe = 0, 0, []
    original = PAYLOAD.decode("utf-8")
    for n in range(1, 41):
        cs = split(PAYLOAD, n)
        indep = "".join(c.decode("utf-8", errors="replace") for c in cs)
        dec = codecs.getincrementaldecoder("utf-8")()
        incr = "".join(dec.decode(c) for c in cs[:-1]) + dec.decode(cs[-1], final=True)
        if indep != original:
            bad_indep += 1
        else:
            safe.append(n)
        if incr != original:
            bad_incr += 1
    print("  independent decode corrupt at %d of 40 sizes (safe: %s); incremental corrupt at %d"
          % (bad_indep, safe, bad_incr))
    chk("P7 37/40 corrupt independently, safe=[11,22,33], incremental 0",
        bad_indep == 37 and safe == [11, 22, 33] and bad_incr == 0)

    miss = [l for l, c in checks if not c]
    if miss:
        print("RESULT: FAIL %d check(s) missed prediction: %s" % (len(miss), " | ".join(miss)))
    else:
        print("RESULT: PASS all %d checks match prediction (leading-whole releases 10000 bytes before verdict; "
              "chunk-crc silent on drop/swap/truncate; seq+total close them; only keyed MAC stops forge; "
              "independent decode corrupts 37/40 sizes, incremental 0/40)" % len(checks))


if __name__ == "__main__":
    main()
