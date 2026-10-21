"""Playable-ad budget sandbox (stdlib, deterministic).

Kernel: GAME-ADS/playables single-file-html-under-5mb ... network-specs-differ-on-mraid.
Claims exercised:
  A) a single HTML file with every asset inlined as base64 must fit 5 MB (AppLovin/Unity)
     or 2 MB (Meta); base64 costs 4/3 (brainwork E179 measured 1.333x on glTF).
  B) the first tap never redirects to the store; audio stays muted until first interaction.
  C) the CTA call differs per network (mraid.open / FbPlayableAd.onCTAClick), and the Meta
     build must contain no mraid reference at all.
Pushed until it stops holding:
  - MB vs MiB ambiguity of the cap,
  - whether the cap is judged on the file or on gzip transfer size,
  - an asset that is already compressed vs one that is not.
"""
import base64
import gzip
import random

rng = random.Random(1234)
SHELL = 20_000  # bytes of HTML/JS shell around the assets (assumed)


def incompressible(n):
    return bytes(rng.getrandbits(8) for _ in range(n))


def build_html(asset_bytes, network):
    b64 = base64.b64encode(asset_bytes).decode()
    if network == "meta":
        cta = "FbPlayableAd.onCTAClick()"
        head = ""
    elif network == "unity":
        cta = "mraid.open(STORE)"
        head = '<script src="mraid.js"></script><!-- wait viewableChange -->'
    else:
        cta = "mraid.open(STORE)"
        head = '<script src="mraid.js"></script>'
    body = f'<html><head>{head}</head><body><script>var A="{b64}";function cta(){{{cta}}}</script>'
    tail = "</body></html>"
    pad = SHELL - (len(body) - len(b64)) - len(tail)  # shell incl. tail is exactly SHELL bytes
    return (body + " " * max(0, pad) + tail).encode()


CAPS = {"applovin": 5_000_000, "unity": 5_000_000, "meta": 2_000_000}
MIB5 = 5 * 1024 * 1024

checks = []

# --- A) raw-asset ceiling
ceil5 = int((CAPS["applovin"] - SHELL) * 3 / 4)
ceil2 = int((CAPS["meta"] - SHELL) * 3 / 4)
print(f"raw asset ceiling: 5MB cap -> {ceil5} B ({ceil5/5e6:.3f} of cap); 2MB cap -> {ceil2} B ({ceil2/2e6:.3f})")

# verify by actual build at the ceiling and just over it
cache = {}
def size_for(raw, net):
    key = (raw, net)
    if key not in cache:
        cache[key] = len(build_html(incompressible(raw), net))
    return cache[key]

at = size_for(ceil5, "applovin")
over = size_for(ceil5 + 3_000, "applovin")
print(f"build at ceiling: {at} B; +3000 raw: {over} B")
checks.append(("ceiling fits 5MB", at <= CAPS["applovin"] < over))

# naive budget: 3.9 MB raw "fits under 5 MB"
naive_raw = 3_900_000
naive_size = size_for(naive_raw, "applovin")
ratio = (naive_size - SHELL) / naive_raw
print(f"naive 3.9MB raw -> file {naive_size} B (base64 ratio {ratio:.4f}); "
      f"passes 5e6? {naive_size <= 5_000_000}; passes 5MiB? {naive_size <= MIB5}")
checks.append(("naive raw budget fails decimal cap", naive_size > 5_000_000))
checks.append(("same file passes 5 MiB (spec ambiguity zone)", naive_size <= MIB5))
zone_lo = int((5_000_000 - SHELL) * 3 / 4)
zone_hi = int((MIB5 - SHELL) * 3 / 4)
print(f"ambiguity zone (raw bytes that pass MiB but fail MB): {zone_lo}..{zone_hi} = {zone_hi-zone_lo} B")

# --- gzip measurement: does transfer compression hide base64's cost?
raw_n = 1_000_000
for label, data in (("incompressible (png/ogg-like)", incompressible(raw_n)),
                    ("compressible (text-like)", (b"tile_grass,tile_water,enemy_slime;" * 40000)[:raw_n])):
    b64 = base64.b64encode(data)
    gz_raw = len(gzip.compress(data, 9, mtime=0))
    gz_b64 = len(gzip.compress(b64, 9, mtime=0))
    print(f"{label}: raw {raw_n}, b64 {len(b64)}, gzip(raw) {gz_raw}, gzip(b64) {gz_b64}, "
          f"gzip(b64)/raw {gz_b64/raw_n:.3f}, gzip(b64)/gzip(raw) {gz_b64/gz_raw:.3f}")
    if label.startswith("incompressible"):
        inc_ratio = gz_b64 / raw_n
    else:
        comp_ratio = gz_b64 / gz_raw
checks.append(("gzip recovers most of base64 cost on incompressible data (<1.05x raw)", inc_ratio < 1.05))

# --- B) first tap never redirects
class Playable:
    def __init__(self, naive):
        self.naive = naive
        self.taps = 0
        self.muted = True
        self.phase = "tutorial"
        self.redirects = []

    def tap(self, target):
        self.taps += 1
        self.muted = False  # first interaction unlocks audio
        if self.naive:
            # common shortcut: canvas-wide listener opens store
            self.redirects.append(self.taps)
            return
        if self.phase == "tutorial":
            self.phase = "play"
        elif self.phase == "play" and target == "win":
            self.phase = "endcard"
        elif self.phase == "endcard" and target == "cta":
            self.redirects.append(self.taps)


seqs = []
r2 = random.Random(7)
for _ in range(500):
    n = r2.randint(1, 8)
    seqs.append([r2.choice(["canvas", "win", "cta"]) for _ in range(n)])

naive_first = sum(1 for s in seqs if (lambda p: ([p.tap(t) for t in s], p)[1])(Playable(True)).redirects[:1] == [1])
good_first = 0
good_cta = 0
muted_before = 0
for s in seqs:
    p = Playable(False)
    if not p.muted:
        muted_before += 1
    for t in s:
        p.tap(t)
    if p.redirects[:1] == [1]:
        good_first += 1
    if p.redirects:
        good_cta += 1
print(f"500 tap sequences: naive first-tap redirects {naive_first}, guarded {good_first}; "
      f"guarded sequences that reached a CTA redirect {good_cta}; unmuted before any tap {muted_before}")
checks.append(("guarded never redirects on tap 1", good_first == 0 and naive_first == 500))
checks.append(("guarded CTA still reachable", good_cta > 0))

# --- C) per-network build hygiene
meta_html = build_html(incompressible(1000), "meta")
al_html = build_html(incompressible(1000), "applovin")
meta_clean = b"mraid" not in meta_html and b"FbPlayableAd" in meta_html
al_ok = b"mraid.open" in al_html
print(f"meta build mraid-free with FbPlayableAd CTA: {meta_clean}; applovin build uses mraid.open: {al_ok}")
checks.append(("per-network CTA adapters", meta_clean and al_ok))

# one shared build for all networks: what does Meta see?
shared = build_html(incompressible(1000), "applovin")
checks.append(("shared build would ship mraid to Meta", b"mraid" in shared))

passed = sum(ok for _, ok in checks)
for name, ok in checks:
    print(("ok   " if ok else "FAIL ") + name)
print(f"RESULT: {'PASS' if passed == len(checks) else 'FAIL'} {passed}/{len(checks)}; raw ceiling {ceil5} B for 5MB "
      f"({ceil5/5e6:.3f}), {ceil2} B for Meta 2MB; 3.9MB raw -> {naive_size} B file fails 5e6 but passes 5MiB; "
      f"gzip(b64)/raw {inc_ratio:.3f} on incompressible; naive first-tap redirects {naive_first}/500, guarded 0")
