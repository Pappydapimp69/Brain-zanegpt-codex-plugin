"""Run the REAL suno-builder analysis (ideas/reference/suno-builder) on stanzas whose end words are plain vs hyphenated by
the tool's own hyphenate(). Needs node; reads the reference html in place. Deterministic, exhaustive."""
import json, os, subprocess, sys, tempfile
cands=[os.path.expanduser('~/.brain/ideas/reference/suno-builder/suno-builder.html'),'/home/user/ideas/reference/suno-builder/suno-builder.html']
html=next((p for p in cands if os.path.exists(p)),None)
if not html: print('RESULT: FAIL suno-builder reference not found'); sys.exit(0)
JS=r'''
const fs=require("fs"),vm=require("vm");
const m=fs.readFileSync(process.argv[2],"utf8").match(/<script>([\s\S]*?)<\/script>/);
const sb={document:{addEventListener(){},createElement(){return{style:{},appendChild(){},setAttribute(){},addEventListener(){}}}},navigator:{},window:{},TextEncoder,TextDecoder,btoa:s=>Buffer.from(s,"binary").toString("base64"),atob:s=>Buffer.from(s,"base64").toString("binary"),console};
const ctx=vm.createContext(sb);vm.runInContext(m[1]+"\n;globalThis.__a={analyseSection,hyphenate,lineSyllables};",ctx);const A=sb.__a;
const W=["freely","gladly","sadly","lightly","tonight","delight","away","today","ocean","motion","blood","mud","desire","quiet"];
const H=W.map(w=>A.hyphenate(w));
let n=0,schemeDiff=0,sylDiff=0,lines=0,sylLineDiff=0;
const idx=[...Array(W.length).keys()];
for(const a of idx)for(const b of idx)for(const c of idx)for(const d of idx){
  const st=[a,b,c,d];
  const plain=st.map(i=>"I walk "+W[i]).join("\n"),hy=st.map(i=>"I walk "+H[i]).join("\n");
  const rp=A.analyseSection(plain),rh=A.analyseSection(hy);
  const rows=r=>Array.isArray(r)?r:(r.rows||r.lines||[]);
  const lp=rows(rp).map(x=>x.letter).join(""),lh=rows(rh).map(x=>x.letter).join("");
  n++; if(lp!==lh)schemeDiff++;
  const sp=rows(rp).map(x=>x.syl),sh=rows(rh).map(x=>x.syl);
  sp.forEach((v,i)=>{lines++;if(v!==sh[i])sylLineDiff++;});
}
const changed=W.filter((w,i)=>H[i]!==w).length;
console.log(JSON.stringify({n,schemeDiff,lines,sylLineDiff,changed,H,keys:Object.keys(A.analyseSection("a b\nc d"))}));
'''
f=tempfile.NamedTemporaryFile('w',suffix='.js',delete=False);f.write(JS);f.close()
out=subprocess.run(['node',f.name,html],capture_output=True,text=True)
os.unlink(f.name)
if out.returncode: print(out.stderr[-400:]); print('RESULT: FAIL harness error'); sys.exit(0)
r=json.loads(out.stdout.strip().splitlines()[-1])
print('words hyphenated by the tool:',r['changed'],'of 14 ->',' '.join(r['H']))
print('stanzas %d, rhyme-letter schemes differing plain vs hyphenated: %d'%(r['n'],r['schemeDiff']))
print('lines %d, syllable count differing: %d (%.1f%%)'%(r['lines'],r['sylLineDiff'],100*r['sylLineDiff']/r['lines']))
ok=r['schemeDiff']==0 and r['changed']>=10
print('RESULT: %s real suno-builder rhyme letters unchanged by hyphenating end words in %d/%d stanzas (rhymeKey strips hyphens) while syllable counts changed on %.1f%% of lines'%('PASS' if ok else 'FAIL',r['n']-r['schemeDiff'],r['n'],100*r['sylLineDiff']/r['lines']))
