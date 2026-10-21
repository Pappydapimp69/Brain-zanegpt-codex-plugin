import unicodedata as u
N=u.normalize
# scenarios
A="café"; B="café"          # precomposed vs combining
fi="ﬁle"; plain="file"             # ligature
cy="pаypal"; la="paypal"           # Cyrillic a lookalike
res={}
res["raw_eq"]=(A==B)
res["nfc_eq"]=(N("NFC",A)==N("NFC",B))
res["nfc_fixes_ligature"]=(N("NFC",fi)==plain)
res["nfkc_fixes_ligature"]=(N("NFKC",fi)==plain)
res["nfkc_fixes_confusable"]=(N("NFKC",cy)==la)
# truncation after normalization: limit 4 code points on 'cafe' + combining x2
s=N("NFD","café")  # 5 code points
cut=s[:4]; res["nfd_trunc_drops_accent"]=(cut=="caf" or cut=="cafe"[:4]) 
nfc_cut=N("NFC",s)[:4]; res["nfc_trunc_keeps_accent"]=(nfc_cut==A)
# grapheme-ish: letter with 2 marks has no precomposed form
x="q̣́"; res["no_precomposed"]=(len(N("NFC",x))==3)
res["trunc_splits_mark"]=(N("NFC",x)[:2]=="q̣")  # lone-mark loss: accent dropped silently
# idempotence
res["idempotent"]=all(N("NFC",N("NFC",t))==N("NFC",t) for t in [A,B,fi,cy,x])
for k,v in res.items(): print(k,v)
exp={"raw_eq":False,"nfc_eq":True,"nfc_fixes_ligature":False,"nfkc_fixes_ligature":True,"nfkc_fixes_confusable":False,"nfc_trunc_keeps_accent":True,"no_precomposed":True,"trunc_splits_mark":True,"idempotent":True}
ok=all(res[k]==v for k,v in exp.items())
print(f"RESULT: {'PASS' if ok else 'FAIL'} NFC fixes combining-vs-precomposed (1 case), NFKC needed for ligature, neither fixes Cyrillic lookalike, NFC still truncates 2-mark grapheme")
