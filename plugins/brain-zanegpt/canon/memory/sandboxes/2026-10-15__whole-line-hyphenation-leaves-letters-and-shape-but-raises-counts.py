# Sandbox: hyphenate EVERY word of every line (slow-the-vocal kernel applied to whole stanzas) in the real
# suno-builder; compare two-pass letters, scheme-note verdict and per-line syllable counts before/after.
# Prediction (written before the first run): letters and shape-note verdict unchanged in 40/40 random stanzas;
# line syllable counts rise in >=25% of lines and never fall.
import subprocess, json, os, random, sys
REF = os.environ.get("BUILDER", "/home/user/ideas/reference/suno-builder")
JS = r'''
const fs=require("fs"),vm=require("vm");
const html=fs.readFileSync(process.argv[2]+"/suno-builder.html","utf8");
const m=html.match(/<script>([\s\S]*?)<\/script>/);
const sb={document:{addEventListener(){},createElement(){return{style:{},appendChild(){},setAttribute(){},addEventListener(){}}}},navigator:{},window:{},TextEncoder,TextDecoder,btoa:s=>Buffer.from(s,"binary").toString("base64"),atob:s=>Buffer.from(s,"base64").toString("binary"),console};
const ctx=vm.createContext(sb);
vm.runInContext(m[1]+"\n;globalThis.__a={analyseSection,hyphenate,SCHEME_NOTES};",ctx);
const A=sb.__a, st=JSON.parse(process.argv[3]);
const hy=t=>t.split("\n").map(l=>l.replace(/[A-Za-z']+/g,w=>A.hyphenate(w))).join("\n");
const out=st.map(t=>{const a=A.analyseSection(t),b=A.analyseSection(hy(t));
 return {a:a.scheme,b:b.scheme,na:A.SCHEME_NOTES[a.scheme.toUpperCase()]||null,nb:A.SCHEME_NOTES[b.scheme.toUpperCase()]||null,
  sa:a.rows.map(r=>r.syl),sb:b.rows.map(r=>r.syl)};});
console.log(JSON.stringify(out));
'''
rnd = random.Random(7)
ends = ["road","load","night","light","desire","fire","heart","apart","sky","high","remember","december","alone","stone","tonight","away","today","river","forever"]
mids = ["I carry the","we wander through the","she whispers in the","they follow every","beautiful and broken","hold me in the","falling into","waiting for the"]
st = []
for _ in range(40):
    st.append("\n".join(rnd.choice(mids)+" "+rnd.choice(ends) for _ in range(4)))
st.append("moon-light on the water\nI wonder where you are\nthe silence is a daughter\nof every falling star")  # pre-hyphenated words
st.append("desire\nfire\nbelieve\nreceive")  # silent-e break case
r = subprocess.run(["node","-e",JS,"x",REF,json.dumps(st)],capture_output=True,text=True)
if r.returncode: print(r.stderr); print("RESULT: FAIL node error"); sys.exit()
d = json.loads(r.stdout)
let = sum(x["a"]==x["b"] for x in d); note = sum(x["na"]==x["nb"] for x in d)
lines = sum(len(x["sa"]) for x in d)
up = sum(b>a for x in d for a,b in zip(x["sa"],x["sb"])); down = sum(b<a for x in d for a,b in zip(x["sa"],x["sb"]))
print(f"stanzas {len(d)}; letters unchanged {let}/{len(d)}; shape note unchanged {note}/{len(d)}")
print(f"lines {lines}; syllables up {up} ({100*up//lines}%), down {down}")
ok = let==len(d) and note==len(d) and down==0 and up*4>=lines
print(("RESULT: PASS" if ok else "RESULT: FAIL"), f"letters {let}/{len(d)} note {note}/{len(d)} up {up}/{lines} down {down}")
