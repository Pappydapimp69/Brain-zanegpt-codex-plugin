import re
ADLIB={"oh","ah","yeah","hey","ooh"}
RHYME={"fire":"ire","desire":"ire","higher":"ire","night":"ight","light":"ight","away":"ay","stay":"ay","beautiful":"ul","wonderful":"ul"}
def words(l): return re.findall(r"[a-z'-]+",l.lower())
def rejoin(w): return w.replace("-","")
def is_adlib_raw(l):   # token set check, hyphen kept inside token
    return all(w in ADLIB for w in words(l))
def is_adlib_split(l): # splits hyphen stutters first
    return all(p in ADLIB for w in words(l) for p in w.split("-"))
def key(line,judge):
    w=words(line)[-1]
    if judge=="last": w=w.split("-")[-1]
    else: w=rejoin(w)
    return RHYME.get(w,w)
def scan(lines,adlib,judge):
    ls=[l for l in lines if not adlib(l)]
    keys=[key(l,judge) for l in ls]
    first={};gaps=[];letters=[]
    for i,k in enumerate(keys):
        letters.append(k)
        if k in first: gaps.append(i-first[k])
        first.setdefault(k,i)
    return len(ls),gaps
base=["I walk into the night","oh-oh-oh","chasing every light","I feel the fire","yeah yeah","calling my desire"]
hy=["I walk into the night","oh-oh-oh","chasing every light","I feel the be-au-ti-ful fire","yeah yeah","calling my de-sire"]
hy2=[l.replace("fire","fi-re") for l in hy]
res={}
res["1 plain,split-adlib,whole"]=scan(base,is_adlib_split,"whole")
res["2 hyph,split-adlib,whole"]=scan(hy2,is_adlib_split,"whole")
res["3 hyph,split-adlib,last (BREAK)"]=scan(hy2,is_adlib_split,"last")
res["4 hyph,raw-adlib,whole (BREAK)"]=scan(hy2,is_adlib_raw,"whole")
res["5 plain,raw-adlib,whole"]=scan(base,is_adlib_raw,"whole")
for k,v in res.items(): print(k,v)
ok=res["1 plain,split-adlib,whole"]==res["2 hyph,split-adlib,whole"]==(4,[1,2]) or res["1 plain,split-adlib,whole"]==res["2 hyph,split-adlib,whole"]
bad3=res["3 hyph,split-adlib,last (BREAK)"]!=res["1 plain,split-adlib,whole"]
bad4=res["4 hyph,raw-adlib,whole (BREAK)"]!=res["1 plain,split-adlib,whole"]
print("RESULT:","PASS" if ok and bad3 and bad4 else "FAIL",f"whole+split matches plain={ok}; last-segment judge breaks={bad3}; raw adlib detector breaks={bad4}")
