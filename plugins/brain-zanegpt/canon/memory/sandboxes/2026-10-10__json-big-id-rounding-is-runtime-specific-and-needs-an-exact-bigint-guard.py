"""Sandbox: does JSON.parse silently round integers past 2^53, and what does
'carry big ids as strings' actually fix?  Stdlib only, deterministic, no RNG,
no timing.  Python drives a REAL Node runtime (subprocess) and also models a
JS double with float(); Python's own json is the contrasting substrate.

PREDICTION (written before the first run):
  P1  Node: JSON.parse('{"id":9007199254740993}').id -> 9007199254740992, no throw;
      Python json.loads on the same text keeps 9007199254740993 (so the defect
      is the JS-number consumer, not the JSON text format).
  P2  ids 2^53 .. 2^53+999: exactly 500 corrupted, 500 distinct values after parse.
      ids 2^54 .. 2^54+999: exactly 750 corrupted, 251 distinct values.
      [AFTER FIRST RUN: the 2^53 distinct-count part was WRONG: observed 501, not 500.
       2^53+999 is odd, ties-to-even sends it UP to 2^53+1000, a value outside the
       block, so a block of n odd-ending ids yields n/2 + 1 distinct values. The
       corrupted count 500 was right. The 2^54 block's 251 already included this edge.]
  P3  a parse->stringify->parse round trip is idempotent for ALL 1000 ids of the
      2^53 block (self-equality passes) while 500 differ from the truth.
  P4  quoted-string transport: 0 corrupted; but Number(str) on the consumer
      re-corrupts exactly the same 500.
  P5  reviver with context.source + BigInt: 0 corrupted (if the runtime has it).
  P6  detector A  String(Number(lit)) !== lit  has 0 false negatives but >=1
      FALSE POSITIVE (an exactly representable id such as 2^60 prints with
      shortest-digits, e.g. ...7000); detector B BigInt(Number(lit)) !== BigInt(lit)
      has 0 false positives and 0 false negatives on the same sweep.
  P7  BREAK attempt: evens in the 2^53 block survive, so the rule is 'ids that are
      not exactly representable', not 'ids above 2^53' -> 500 of 1000 survive
      unquoted. A digit-count guard (>15 digits) over-flags safe 16-digit ids.
"""
import json, subprocess, sys, shutil

TWO53 = 2 ** 53
results = []

def check(name, ok, detail):
    results.append(ok)
    print(("ok   " if ok else "FAIL ") + name + " :: " + detail)

NODE = shutil.which("node")
if not NODE:
    print("RESULT: FAIL node runtime not found")
    sys.exit(0)

JS = r"""
const input = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const out = {};
const lits = input.lits;
// plain parse
out.plain = lits.map(l => String(JSON.parse('{"id":' + l + '}').id));
// parse -> stringify -> parse
out.rt = lits.map(l => {
  const a = JSON.parse('{"id":' + l + '}');
  const b = JSON.parse(JSON.stringify(a));
  return b.id === a.id;
});
// string transport
out.str = lits.map(l => JSON.parse('{"id":"' + l + '"}').id);
out.strNumber = lits.map(l => String(Number(JSON.parse('{"id":"' + l + '"}').id)));
// reviver with source text
let hasSrc = true, rev = [];
try {
  rev = lits.map(l => JSON.parse('{"id":' + l + '}', function (k, v, ctx) {
    if (k === 'id' && ctx && typeof ctx.source === 'string') return BigInt(ctx.source);
    if (k === 'id') { hasSrc = false; }
    return v;
  }).id.toString());
} catch (e) { hasSrc = false; }
out.hasSrc = hasSrc; out.rev = rev;
// naive === check against a literal in source
out.eqlit = (JSON.parse('{"id":9007199254740993}').id === 9007199254740993);
// stringify of BigInt throws?
try { JSON.stringify({id: 1n}); out.bigStringify = 'ok'; } catch (e) { out.bigStringify = e.constructor.name; }
// detectors
out.detA = lits.map(l => String(Number(l)) !== l);
out.detB = lits.map(l => BigInt(Number(l)) !== BigInt(l));
out.digits = lits.map(l => l.length > 15);
console.log(JSON.stringify(out));
"""

def run_node(lits):
    p = subprocess.run([NODE, "-e", JS], input=json.dumps({"lits": lits}),
                       capture_output=True, text=True, timeout=60)
    if p.returncode != 0:
        print(p.stderr)
        raise SystemExit("RESULT: FAIL node error")
    return json.loads(p.stdout)

# --- S1: the headline case, two substrates
lit = "9007199254740993"
n = run_node([lit])
py_val = json.loads('{"id":%s}' % lit)["id"]
check("S1 node rounds, python keeps", n["plain"][0] == "9007199254740992" and py_val == 9007199254740993,
      "node=%s python=%d eq-literal-in-js-source=%s" % (n["plain"][0], py_val, n["eqlit"]))
check("S1b naive === vs literal is blind", n["eqlit"] is True, "JS source literal rounds the same way")
# Python model of a JS double agrees with node
check("S1c float() models the double", int(float(lit)) == 9007199254740992, "int(float(lit))=%d" % int(float(lit)))

# --- S2: sweeps
def sweep(base, count=1000):
    lits = [str(base + k) for k in range(count)]
    r = run_node(lits)
    corrupted = sum(1 for l, p in zip(lits, r["plain"]) if p != l)
    distinct = len(set(r["plain"]))
    return lits, r, corrupted, distinct

lits53, r53, c53, d53 = sweep(TWO53)
check("S2a 2^53 block", c53 == 500 and d53 == 501, "corrupted=%d distinct=%d (pred 500/500; distinct 501 after edge tie-to-even, see header)" % (c53, d53))
lits54, r54, c54, d54 = sweep(2 ** 54)
check("S2b 2^54 block", c54 == 750 and d54 == 251, "corrupted=%d distinct=%d (pred 750/251)" % (c54, d54))

# --- S3: round trip is self-consistent
rt_ok = sum(r53["rt"])
check("S3 self round trip passes while wrong", rt_ok == 1000 and c53 == 500,
      "round-trip idempotent %d/1000, truth-mismatch %d/1000" % (rt_ok, c53))

# --- S4: strings
str_bad = sum(1 for l, s in zip(lits53, r53["str"]) if s != l)
strnum_bad = sum(1 for l, s in zip(lits53, r53["strNumber"]) if s != l)
check("S4 strings safe, Number(str) re-breaks", str_bad == 0 and strnum_bad == 500,
      "string-transport corrupted=%d, after Number()=%d" % (str_bad, strnum_bad))

# --- S5: reviver
if r53["hasSrc"]:
    rev_bad = sum(1 for l, s in zip(lits53, r53["rev"]) if s != l)
    check("S5 reviver(ctx.source)+BigInt", rev_bad == 0, "corrupted=%d" % rev_bad)
else:
    check("S5 reviver(ctx.source)+BigInt", True, "runtime lacks ctx.source; skipped (not a refutation)")
check("S5b BigInt stringify is loud", r53["bigStringify"] == "TypeError", "JSON.stringify({id:1n}) -> %s" % r53["bigStringify"])

# --- S6: detectors, on a sweep that includes exactly-representable big values
mix = [str(TWO53 + k) for k in range(0, 200)] + [str(2 ** 60), str(2 ** 60 + 1), str(2 ** 62), str(2 ** 62 + 3),
       str(2 ** 63 - 1), "9007199254740991", "1000000000000000", "999999999999999"]
rm = run_node(mix)
truth = [str(int(p)) != l if False else (p != l) for l, p in zip(mix, rm["plain"])]
# truth: parsed value (exact integer of the double) vs literal
truth = [int(float(l)) != int(l) for l in mix]
fnA = sum(1 for t, a in zip(truth, rm["detA"]) if t and not a)
fpA = sum(1 for t, a in zip(truth, rm["detA"]) if (not t) and a)
fnB = sum(1 for t, b in zip(truth, rm["detB"]) if t and not b)
fpB = sum(1 for t, b in zip(truth, rm["detB"]) if (not t) and b)
check("S6 detector A (print compare)", fnA == 0 and fpA >= 1, "false-neg=%d false-pos=%d" % (fnA, fpA))
check("S6 detector B (BigInt compare)", fnB == 0 and fpB == 0, "false-neg=%d false-pos=%d" % (fnB, fpB))

# --- S7: BREAK attempts on the 'every integer past 2^53' wording
survive = sum(1 for l, p in zip(lits53, r53["plain"]) if p == l)
check("S7a evens past 2^53 survive", survive == 500, "survived unquoted=%d/1000" % survive)
safe16 = ["9007199254740991", "1000000000000000", "4503599627370496"]
rs = run_node(safe16)
flag16 = sum(rs["digits"])
ok16 = all(p == l for l, p in zip(safe16, rs["plain"]))
check("S7b digit-count guard over-flags", ok16 and flag16 == 3, "16-digit ids exact=%s flagged-by->15-digits=%d/3" % (ok16, flag16))
# cents threshold: where the 'values in cents' claim starts to matter
print("note 2^53 cents = %.2f currency units" % (TWO53 / 100.0))
check("S7c cents claim is far out", TWO53 // 100 > 9 * 10 ** 13, "2^53 cents = %d units (> 9e13)" % (TWO53 // 100))

allok = all(results)
print("RESULT: %s %d/%d checks; node rounds ids that are not exactly representable (500/1000 at 2^53, 750/1000 at 2^54), "
      "python keeps them; strings/BigInt-reviver 0 corrupted; Number(str) re-corrupts; BigInt-compare detector exact, print-compare has false positives"
      % ("PASS" if allok else "FAIL", sum(results), len(results)))
