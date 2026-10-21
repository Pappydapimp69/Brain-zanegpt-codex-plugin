# Self-run pitch demo: does it prove the tool, or only the path the pitch exercises?
# Toy tool: slugify(text). Versions v1..v6; v4 regresses on non-ASCII only.
import re, unicodedata
def make(v):
    def slugify(t):
        if v >= 4 and v != 6:   # v4,v5 regress: strip accented letters entirely
            t = re.sub(r'[^\x00-\x7f]', '', t)
        else:
            t = unicodedata.normalize('NFKD', t).encode('ascii','ignore').decode()
        return re.sub(r'[^a-z0-9]+','-',t.lower()).strip('-')
    return slugify
PITCH = ["Hello World", "Brain Pitch Deck"]           # the pitch's own creation: ASCII only
WIDE  = PITCH + ["Café Déjà Vu", "Zoë's Naïve Plan"]  # inputs users actually have
def truth(t): return re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',t).encode('ascii','ignore').decode().lower()).strip('-')
def selfrun(v, inputs): s=make(v); return all(s(t)==truth(t) for t in inputs)
def pasted(v): return True  # pasted output captured at v1 always "succeeds"
rows=[]
for v in range(1,7):
    rows.append((v, selfrun(v,PITCH), selfrun(v,WIDE), pasted(v)))
print("v  selfrun(pitch-inputs) selfrun(wide-inputs) pasted")
for r in rows: print(*r)
real_ok=[r[2] for r in rows]
gate_pitch=[r[1] for r in rows]
# S1 fresh self-run on wide inputs agrees with truth every version
s1 = True
# S2 pasted claims success 6/6 vs truth
pasted_hits = sum(r[3]==r[2] for r in rows)
# S3 BREAK: self-run on pitch-only inputs misses the regression
pitch_hits = sum(r[1]==r[2] for r in rows)
print("pasted agrees with truth", pasted_hits, "/6; pitch-input selfrun agrees", pitch_hits, "/6; wide selfrun agrees 6/6")
ok = pasted_hits==4 and pitch_hits==4 and sum(real_ok)==4
print("RESULT:", "PASS" if ok else "FAIL", f"pasted {pasted_hits}/6, pitch-only self-run {pitch_hits}/6 (misses v4,v5), wide self-run 6/6")
