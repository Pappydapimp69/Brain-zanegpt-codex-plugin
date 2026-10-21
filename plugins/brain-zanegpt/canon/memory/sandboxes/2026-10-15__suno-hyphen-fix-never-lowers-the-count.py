"""suno-builder's 'way over budget' fix hyphenates the longest word to force syllable
timing (ideas:SONGWRITING/hyphenate-words-to-slow-a-rushed-vocal-line). Does the fix
keep two-pass rhyme letters, and does it lower or RAISE the syllable count the warning
is based on? Runs the REAL builder headless via node. Deterministic word list.
PREDICTION (written before the first run): letters change in 0 stanzas; the counted
syllables of the hyphenated word go UP for at least 30% of 2+ syllable words."""
import json, subprocess, sys
BUILDER = sys.argv[1] if len(sys.argv) > 1 else "ideas/reference/suno-builder/suno-builder.html"
JS = r"""
const fs=require("fs"),vm=require("vm");
const html=fs.readFileSync(process.argv[1],"utf8");const m=html.match(/<script>([\s\S]*?)<\/script>/);
const sb={document:{addEventListener(){},createElement(){return{style:{},appendChild(){},setAttribute(){},addEventListener(){}}}},navigator:{},window:{},TextEncoder,TextDecoder,btoa:s=>s,atob:s=>s,console};
const ctx=vm.createContext(sb);vm.runInContext(m[1]+"\n;globalThis.__a={hyphenate,syllablesInWord,analyseSection};",ctx);
const A=sb.__a, req=JSON.parse(fs.readFileSync(0,"utf8"));
const words=req.words.map(w=>{const h=A.hyphenate(w);return {w,h,before:A.syllablesInWord(w),after:A.syllablesInWord(h)};});
const stanzas=req.stanzas.map(s=>{const before=A.analyseSection(s.join("\n")).scheme;
  const hy=s.map(l=>{const ws=l.split(" ");const last=ws.pop();return ws.concat([A.hyphenate(last)]).join(" ");});
  return {before, after:A.analyseSection(hy.join("\n")).scheme, hy};});
console.log(JSON.stringify({words,stanzas}));
"""
WORDS = ["desire","quiet","poem","piano","believe","forever","yesterday","beautiful","tomorrow",
         "remember","together","electric","another","fire","lion","create","idea","radio","hollow",
         "shadow","morning","evening","diamond","violet","river","silence","heaven","golden",
         "wonder","danger","flower","power","alone","awake","higher","desire","table","little","only","every"]
STANZAS = [["I want desire","you light the fire","we climb higher","a burning wire"],
           ["walk the river","hands that shiver","keep forever","I will never"],
           ["sing it quiet","start a riot","say tomorrow","borrow sorrow"],
           ["violet morning","golden warning","into evening","heaven leaving"]]
r = json.loads(subprocess.run(["node","-e",JS,BUILDER],input=json.dumps({"words":WORDS,"stanzas":STANZAS}),
                              capture_output=True,text=True,check=True).stdout)
multi = [w for w in r["words"] if w["before"] >= 2]
up = [w for w in multi if w["after"] > w["before"]]
down = [w for w in multi if w["after"] < w["before"]]
for w in r["words"]:
    flag = "UP" if w["after"] > w["before"] else ("down" if w["after"] < w["before"] else "")
    print(f"{w['w']:10s} -> {w['h']:12s} {w['before']} -> {w['after']} {flag}")
changed = 0
for s in r["stanzas"]:
    changed += s["before"] != s["after"]
    print(f"stanza {s['before']} -> {s['after']}  {s['hy']}")
share = len(up) / len(multi)
ok = changed == 0 and share >= 0.30
print(f"RESULT: {'PASS' if ok else 'FAIL'} letters changed in {changed}/{len(r['stanzas'])} stanzas; "
      f"hyphenating raised the counted syllables for {len(up)}/{len(multi)} 2+ syllable words ({share:.0%}), lowered {len(down)}")
