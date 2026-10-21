"""Prediction (before run), real Node v22 Intl.Segmenter:
 S1 flags "🇺🇸🇬🇧🇯🇵" cut to 3 by code units gives a lone-surrogate string (not valid), by code points 3 RIs = 1.5 flags,
    by graphemes exactly the 3 flags.
 S2 (BREAK, kernel scope): a grapheme cap of 6 applied BEFORE toUpperCase on "straßen-café" gives >6 graphemes after (ß->SS),
    while capping AFTER the transform stays <=6. Turkish "İ" lowercase keeps grapheme count but changes code points.
 S3 (BREAK): a grapheme cap of 10 on ten family emoji passes a grapheme limit but is 250 UTF-8 bytes; a 100-byte budget
    needs a grapheme-boundary walk, and a raw byte slice yields invalid UTF-8.
FIRST RUN FAILED the S3 prediction: a raw 100-byte slice was clean because 100 = 4 x 25-byte families (boundary-aligned by luck); budget 90 added as the real break.
Deterministic, stdlib + node."""
import json, subprocess, shutil
JS = r'''
const seg = s => [...new Intl.Segmenter("en",{granularity:"grapheme"}).segment(s)].map(x=>x.segment);
const capG = (s,n)=>seg(s).slice(0,n).join("");
const enc = new TextEncoder();
const isWellFormed = s => { try { new TextDecoder("utf-8",{fatal:true}).decode(enc.encode(s)); return !/[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/.test(s);} catch(e){return false} };
const out = {};
const flags = "🇺🇸🇬🇧🇯🇵";
const cu = flags.slice(0,3), cp = [...flags].slice(0,3).join(""), gr = capG(flags,3);
out.s1 = {cu_wellformed:isWellFormed(cu), cp_graphemes:seg(cp).length, cp_is_whole_flags:cp===flags.slice(0,cp.length)&&seg(cp).length*2===[...cp].length, gr_equals_flags:gr===flags, gr_len:seg(gr).length};
const w = "straßen-café";
const before = capG(w,6).toUpperCase(), after = capG(w.toUpperCase(),6);
out.s2 = {before_graphemes:seg(before).length, after_graphemes:seg(after).length, before, after,
  tr_i_lower_cp_delta:[..."İ".toLowerCase("tr")].length-[..."İ"].length, tr_i_lower_g_delta:seg("İ".toLowerCase()).length-seg("İ").length};
const fam = "👨‍👩‍👧‍👦".repeat(10);
const capB = (s,b)=>{let o="",n=0;for(const g of seg(s)){const l=enc.encode(g).length;if(n+l>b)break;o+=g;n+=l}return o};
const rawAt = b => new TextDecoder("utf-8").decode(enc.encode(fam).slice(0,b)).includes("\uFFFD");
const bounded = capB(fam,100);
out.s3 = {graphemes:seg(fam).length, bytes:enc.encode(fam).length, grapheme_cap10_bytes:enc.encode(capG(fam,10)).length,
  raw_slice100_has_replacement:rawAt(100), raw_slice90_has_replacement:rawAt(90), bounded_bytes:enc.encode(bounded).length, bounded_graphemes:seg(bounded).length, bounded_ok:enc.encode(bounded).length<=100&&!bounded.includes("\uFFFD")};
console.log(JSON.stringify(out));
'''
if not shutil.which("node"): print("RESULT: FAIL node missing"); raise SystemExit
o = json.loads(subprocess.run(["node","-e",JS],capture_output=True,text=True,check=True).stdout)
print(json.dumps(o,ensure_ascii=False,indent=1))
s1,s2,s3=o["s1"],o["s2"],o["s3"]
ok = (not s1["cu_wellformed"]) and s1["gr_equals_flags"] and s1["gr_len"]==3 \
 and s2["before_graphemes"]>6 and s2["after_graphemes"]<=6 and s2["tr_i_lower_cp_delta"]==1 and s2["tr_i_lower_g_delta"]==0 \
 and s3["grapheme_cap10_bytes"]>100 and (not s3["raw_slice100_has_replacement"]) and s3["raw_slice90_has_replacement"] and s3["bounded_ok"]
print("RESULT:", "PASS" if ok else "FAIL", f"flags: code-unit cut well-formed={s1['cu_wellformed']}, grapheme cut=3 flags; cap-before-upper {s2['before_graphemes']} graphemes vs cap-after {s2['after_graphemes']}; cap10 family={s3['grapheme_cap10_bytes']} bytes, byte-bounded={s3['bounded_bytes']} bytes/{s3['bounded_graphemes']} graphemes")
