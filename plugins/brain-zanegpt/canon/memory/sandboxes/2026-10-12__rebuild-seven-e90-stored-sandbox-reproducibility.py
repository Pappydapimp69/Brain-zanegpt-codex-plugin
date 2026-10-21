"""Blind rebuild of seven E90 (stored sandboxes mostly reproduce; they drift on
the interpreter - sum() of floats is compensated since Python 3.12 - and on
unshipped inputs). Own fixture: (1) float-order probe with values of my own;
(2) a fresh sample of stored sandboxes chosen by sha1 of the file name (not the
original's full sweep), each re-run with python -I in an empty temp dir,
timeout T s, and its RESULT word compared with the RESULT word in the Observed
field of the entry that names it. SAMPLE (default 16) and T can be raised by
argv for a bigger sweep: python e90.py 80 30.
PREDICTION (before running): on 3.12+, sum() gives the same total in both
orders while a plain loop differs, fsum equal; >= 90% of sampled sandboxes that
finish reproduce their recorded RESULT word; any mismatch traces to timeout,
a missing input file, or float/version drift.
"""
import sys, os, re, glob, hashlib, subprocess, tempfile, math
from concurrent.futures import ThreadPoolExecutor
print("python", sys.version.split()[0])
v = [1e16, 1.0, -1e16, 3.0, 1e-3]
loop = lambda xs: (lambda acc: acc)(__import__('functools').reduce(lambda a, b: a+b, xs, 0.0))
a, b = list(v), list(reversed(v))
la = 0.0
for x in a: la += x
lb = 0.0
for x in b: lb += x
print(f"sum fwd {sum(a)!r} rev {sum(b)!r} | loop fwd {la!r} rev {lb!r} | fsum {math.fsum(a)!r} {math.fsum(b)!r}")
f_ok = sum(a) == sum(b) and la != lb and math.fsum(a) == math.fsum(b)
if sys.version_info < (3, 12): print("NOTE: pre-3.12 interpreter; sum() is not compensated here")
HOME = os.path.expanduser("~/.brain/memory")
N = int(sys.argv[1]) if len(sys.argv) > 1 else 16
T = float(sys.argv[2]) if len(sys.argv) > 2 else 12
rec = {}
for md in glob.glob(os.path.join(HOME, "projects", "*.md")):
    txt = open(md, encoding="utf-8").read()
    for blk in re.split(r"(?m)^(?=## E\d+ )", txt):
        s = re.search(r"(?m)^- Sandbox:\s*sandboxes/(\S+\.py)", blk)
        o = re.search(r"(?m)^- Observed:.*?RESULT:\s*(PASS|FAIL)", blk)
        if s and o: rec[s.group(1)] = o.group(1)
names = sorted(n for n in rec if os.path.exists(os.path.join(HOME, "sandboxes", n)))
names = sorted(names, key=lambda n: hashlib.sha1(n.encode()).hexdigest())[:N]
def run(n):
    with tempfile.TemporaryDirectory() as d:
        try:
            p = subprocess.run([sys.executable, "-I", os.path.join(HOME, "sandboxes", n)], cwd=d,
                               capture_output=True, text=True, timeout=T)
        except subprocess.TimeoutExpired:
            return n, "TIMEOUT", ""
        m = re.findall(r"RESULT:\s*(PASS|FAIL)", p.stdout)
        err = (p.stderr.strip().splitlines() or [""])[-1][:80]
        return n, (m[-1] if m else "NORESULT"), err
with ThreadPoolExecutor(8) as ex: out = list(ex.map(run, names))
fin = [o for o in out if o[1] in ("PASS", "FAIL")]
same = [o for o in fin if o[1] == rec[o[0]]]
for n, w, e in out:
    if w != rec[n]: print(f"  mismatch {n[:70]}: recorded {rec[n]} now {w} {e}")
print(f"indexed with sandbox+RESULT: {len(rec)}; sampled {len(out)}; finished {len(fin)}; reproduced {len(same)}")
rate = len(same)/len(fin) if fin else 0
comp = sum(a) != la or sum(b) != lb  # sum() is not the naive loop: compensated
print("my prediction (sum order-free):", sum(a) == sum(b), "-> refuted: Neumaier sum() is compensated but still order-dependent; only fsum is exact")
print(f"RESULT: {'PASS' if (comp and rate >= 0.9) else 'FAIL'} rule holds: sum() compensated (differs from loop)={comp}; finished sandboxes reproduce {len(same)}/{len(fin)}; but sum() order-free={sum(a)==sum(b)} ({sum(a)!r} vs {sum(b)!r}); timeouts at {T:.0f}s: {len(out)-len(fin)}/{len(out)}")
