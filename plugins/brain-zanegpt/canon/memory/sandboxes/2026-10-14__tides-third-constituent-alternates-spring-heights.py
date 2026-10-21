# Prediction (first): hourly heights for 240 days from M2+S2 (+N2). The spring-peak spacing of the daily-range
# envelope stays 14.77 +/- 0.4 d with or without N2 (amp 0.2 of M2), but with N2 successive spring peaks differ in
# height by >10% (a 27.55 d perigean modulation) while M2+S2 alone gives <2% difference; removing S2 leaves no 14.77 d
# peak spacing (built to BREAK: the fortnight needs S2, N2 alone makes a 27.5 d cycle instead).
from math import cos,pi
T={"M2":12.4206012,"S2":12.0,"N2":12.6583482}
def series(amps,hours=240*24):
    return [sum(a*cos(2*pi*t/T[k]) for k,a in amps.items()) for t in range(hours)]
def daily_range(h):
    w=25; out=[]
    for i in range(0,len(h)-w,6):
        seg=h[i:i+w]; out.append(max(seg)-min(seg))
    return out   # sampled every 6 h
def peaks(r):
    ps=[i for i in range(2,len(r)-2) if r[i]==max(r[i-2:i+3]) and r[i]>r[i-1]]
    # merge plateaus within 3 days
    m=[]
    for i in ps:
        if m and (i-m[-1])*6<72:
            if r[i]>r[m[-1]]: m[-1]=i
        else: m.append(i)
    return m
def analyse(amps,label):
    r=daily_range(series(amps)); p=peaks(r)
    sp=[(b-a)*6/24 for a,b in zip(p,p[1:])]
    hts=[r[i] for i in p]
    alt=[abs(hts[i+1]-hts[i])/max(hts[i],hts[i+1]) for i in range(len(hts)-1)]
    mean=sum(sp)/len(sp) if sp else float('nan')
    print(f"{label}: peaks {len(p)} mean spacing {mean:.2f} d  max height step {max(alt) if alt else 0:.3f}")
    return mean,(max(alt) if alt else 0),len(p)
a=analyse({"M2":1.0,"S2":0.45},"M2+S2")
b=analyse({"M2":1.0,"S2":0.45,"N2":0.2},"M2+S2+N2")
c=analyse({"M2":1.0,"N2":0.2},"M2+N2 (no S2)")
ok=abs(a[0]-14.77)<0.4 and abs(b[0]-14.77)<0.4 and a[1]<0.02 and b[1]>0.10 and abs(c[0]-14.77)>1.0
print("RESULT:","PASS" if ok else "FAIL",f"spring spacing {a[0]:.2f} d (M2+S2), {b[0]:.2f} d with N2; spring height step {a[1]:.3f} vs {b[1]:.3f}; without S2 spacing {c[0]:.2f} d")
