# Sandbox: real suno-builder analyseSection letters -> closure metrics (max span, first closing line).
# Prediction (written before first run): on 7 stanzas built for the 7 SCHEME_NOTES shapes the real builder
# returns the intended scheme in >=6 of 7, and the two-metric rule (open if max span>=3 or first close>=4)
# matches the note's stable/open verdict for AABB, ABAB, ABBA, XXAA; the assonance stanza XXaa breaks it.
import subprocess, json, os, sys
REF = os.environ.get("BUILDER", "/home/user/ideas/reference/suno-builder")
JS = r'''
const fs=require("fs"),vm=require("vm");
const html=fs.readFileSync(process.argv[2]+"/suno-builder.html","utf8");
const m=html.match(/<script>([\s\S]*?)<\/script>/);
const sb={document:{addEventListener(){},createElement(){return{style:{},appendChild(){},setAttribute(){},addEventListener(){}}}},navigator:{},window:{},TextEncoder,TextDecoder,btoa:s=>Buffer.from(s,"binary").toString("base64"),atob:s=>Buffer.from(s,"base64").toString("binary"),console};
const ctx=vm.createContext(sb);
vm.runInContext(m[1]+"\n;globalThis.__a={analyseSection,SCHEME_NOTES};",ctx);
const st=JSON.parse(process.argv[3]);const out={};
for(const k in st) out[k]=sb.__a.analyseSection(st[k]).scheme;
out.__notes=Object.keys(sb.__a.SCHEME_NOTES);
console.log(JSON.stringify(out));
'''
SA = {
 "AABB": "I walk the road\nI feel the load\nthe sky is blue\nthe sun shines through",
 "ABAB": "I walk the road\nthe sky is blue\nI feel the load\nthe sun shines through",
 "ABBA": "I walk the road\nthe sky is blue\nthe sun shines through\nI feel the load",
 "XXAA": "I walk alone in town\nwe wander all around\nthe sky is blue\nthe sun shines through",
 "AAAA": "I walk the road\nI feel the load\nI carry my toad\nI know the code",
 "ABCB": "I walk alone\nthe sky is blue\nwe wander home\nthe sun shines through",
 "XAXA": "I walk alone in town\nthe sky is blue\nwe wander around\nthe sun shines through",
 "XXaa": "I walk alone in town\nwe wander all around\nthe cold wind blows\nthe long road goes",
}
# Set B: same shapes but every intended pair spelled alike (the first run showed blue/through is missed)
T={"AABB":"road load true blue","ABAB":"road true load blue","ABBA":"road true blue load",
 "XXAA":"town stone true blue","AAAA":"road load toad code","ABCB":"night true home blue",
 "XAXA":"town true stone blue"}
def mk(w): return "\n".join("I see the "+x for x in w.split())
SB={k:mk(v) for k,v in T.items()}
SB["AABB"]=mk("road load true blue"); SB["ABCB"]=mk("night true home blue")
SB["XXAA"]=mk("town stone true blue"); SB["XAXA"]=mk("town true stone blue")
SB["XXaa"]=mk("town stone cold gold".replace("gold","road"))
S=dict(SA); S.update({'B-'+k:v for k,v in SB.items()})
r = subprocess.run(["node","-e",JS,"x",REF,json.dumps(S)],capture_output=True,text=True)
if r.returncode: print(r.stderr); print("RESULT: FAIL node error"); sys.exit()
got = json.loads(r.stdout.strip().splitlines()[-1]); notes = got.pop("__notes")
def metrics(sch):
    s=sch.upper(); pos={}
    for i,c in enumerate(s):
        if c!="X": pos.setdefault(c,[]).append(i)
    spans=[b-a for p in pos.values() for a,b in zip(p,p[1:])]
    closes=[p[1] for p in pos.values() if len(p)>1]
    return (max(spans) if spans else 0, (min(closes)+1) if closes else 0)
want_open={"AABB":False,"ABAB":False,"ABBA":True,"XXAA":True}
res={"A":[0,0],"B":[0,0]}
for k,v in S.items():
    grp="B" if k.startswith("B-") else "A"; name=k[2:] if grp=="B" else k
    g=got[k]; mx,fc=metrics(g); op=(mx>=3 or fc>=4)
    print(f"{grp} {name:5} builder={g:5} maxspan={mx} firstclose={fc} open={op}")
    res[grp][0]+=(g==name)
    if name in want_open: res[grp][1]+=(op==want_open[name])
print(f"set A (first draft, blue/through): scheme {res['A'][0]}/8, verdict {res['A'][1]}/4")
print(f"set B (spelling-matched): scheme {res['B'][0]}/8, verdict {res['B'][1]}/4")
ok=res["B"][0]>=6 and res["B"][1]==4
print(("RESULT: PASS" if ok else "RESULT: FAIL"), f"A scheme {res['A'][0]}/8 B scheme {res['B'][0]}/8 B verdict {res['B'][1]}/4")
