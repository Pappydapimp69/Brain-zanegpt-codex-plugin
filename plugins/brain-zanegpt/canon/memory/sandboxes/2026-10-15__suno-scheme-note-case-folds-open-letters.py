"""Does suno-builder's scheme note respect two-pass letter case? Runs the REAL
builder (ideas/reference/suno-builder/suno-builder.html) headless via node and
feeds analyseSection stanzas whose rhyme types are known from its own rhymeType.
The note shown is SCHEME_NOTES[scheme.toUpperCase()] (line ~1274), so lowercase
(assonance, 'stays open') letters get the uppercase (resolved) shape verdict.
Deterministic: fixed word lists, no RNG. Needs node and BUILDER path (argv[1])."""
import json, subprocess, sys, itertools, os

BUILDER = sys.argv[1] if len(sys.argv) > 1 else "ideas/reference/suno-builder/suno-builder.html"
JS = r"""
const fs=require("fs"),vm=require("vm");
const html=fs.readFileSync(process.argv[1],"utf8");const m=html.match(/<script>([\s\S]*?)<\/script>/);
const sb={document:{addEventListener(){},createElement(){return{style:{},appendChild(){},setAttribute(){},addEventListener(){}}}},navigator:{},window:{},TextEncoder,TextDecoder,btoa:s=>s,atob:s=>s,console};
const ctx=vm.createContext(sb);vm.runInContext(m[1]+"\n;globalThis.__a={rhymeKey,rhymeType,analyseSection,SCHEME_NOTES};",ctx);
const A=sb.__a, req=JSON.parse(fs.readFileSync(0,"utf8"));
const out={types:req.pairs.map(([a,b])=>A.rhymeType(A.rhymeKey(a),A.rhymeKey(b))),
  stanzas:req.stanzas.map(s=>{const sc=A.analyseSection(s.join("\n")).scheme;
    return {scheme:sc, note:A.SCHEME_NOTES[sc.toUpperCase()]||null, caveat:/[a-z]/.test(sc)};})};
console.log(JSON.stringify(out));
"""
P = ("love", "above")          # perfect
Q = ("sun", "run")             # perfect
AS1 = ("mind", "time")         # assonance in the builder
AS2 = ("moon", "food")         # assonance in the builder
DOC = ("read", "cheap")        # the builder's own help text calls this assonance

def st(*w): return [f"I sing of {x}" for x in w]
stanzas = {
    "perfect AABB": st(P[0], P[1], Q[0], Q[1]),
    "assonance aabb": st(AS1[0], AS1[1], AS2[0], AS2[1]),
    "assonance abab": st(AS1[0], AS2[0], AS1[1], AS2[1]),
    "assonance abba": st(AS1[0], AS2[0], AS2[1], AS1[1]),
    "mixed AAbb": st(P[0], P[1], AS2[0], AS2[1]),
    "doc example read/cheap (break)": st("night", "day", DOC[0], DOC[1]),
}
req = {"pairs": [P, Q, AS1, AS2, DOC], "stanzas": list(stanzas.values())}
r = json.loads(subprocess.run(["node", "-e", JS, BUILDER], input=json.dumps(req),
                              capture_output=True, text=True, check=True).stdout)
print("pair types:", dict(zip(["/".join(p) for p in req["pairs"]], r["types"])))
contra = 0
for (name, _), s in zip(stanzas.items(), r["stanzas"]):
    settled = bool(s["note"]) and any(k in s["note"].lower() for k in ("stable", "settled"))
    both = settled and s["caveat"]
    contra += both
    print(f"{name:32s} scheme {s['scheme']:5s} note={s['note']!r} open-caveat={s['caveat']} contradiction={both}")
doc_mismatch = r["types"][4] != "assonance"
print(f"RESULT: {'PASS' if contra >= 3 and doc_mismatch else 'FAIL'} {contra} of 4 assonance-bearing stanzas get a "
      f"stable/settled shape note beside the 'stays open' caveat; help text's read/cheap assonance example is typed "
      f"{r['types'][4]!r} by the code")
