# Does a filter-switch transient set a mix's peak-normalize level? DF2T vs TPT SVF. Deterministic, stdlib.
import math
FS = 48000
def rbj_lp(fc, Q):
    w = 2*math.pi*fc/FS; c = math.cos(w); a = math.sin(w)/(2*Q)
    b0=(1-c)/2; b1=1-c; b2=(1-c)/2; a0=1+a; a1=-2*c; a2=1-a
    return b0/a0,b1/a0,b2/a0,a1/a0,a2/a0
def run_df2t(x, cut_fn, Q):
    z1=z2=0.0; out=[]
    for n,s in enumerate(x):
        b0,b1,b2,a1,a2 = rbj_lp(cut_fn(n), Q)
        y=b0*s+z1; z1=b1*s-a1*y+z2; z2=b2*s-a2*y
        out.append(y)
        if abs(y)>1e6: out+= [1e6]*(len(x)-n-1); break
    return out
def run_svf(x, cut_fn, Q):
    ic1=ic2=0.0; k=1.0/Q; out=[]
    for n,s in enumerate(x):
        g=math.tan(math.pi*cut_fn(n)/FS); a1=1/(1+g*(g+k)); a2=g*a1; a3=g*a2
        v3=s-ic2; v1=a1*ic1+a2*v3; v2=ic2+a2*ic1+a3*v3
        ic1=2*v1-ic1; ic2=2*v2-ic2; out.append(v2)
    return out
N=4800
dialog=[0.4*math.sin(2*math.pi*220*n/FS) for n in range(N)]
music =[0.3*math.sin(2*math.pi*1500*n/FS) for n in range(N)]
mix=[a+b for a,b in zip(dialog,music)]
def peak(v): return max(abs(t) for t in v)
def rms(v): return math.sqrt(sum(t*t for t in v)/len(v))
def norm_db(v, target=0.891):   # gain to peak-normalize to -1 dBFS
    return 20*math.log10(target/peak(v))
res={}
for Q in (0.707,10.0):
    for period in (0,7,480):
        def cut(n,p=period):
            if p==0: return 1000.0
            return 400.0 if (n//p)%2==0 else 6000.0
        for name,f in (("df2t",run_df2t),("svf",run_svf)):
            y=f(mix,cut,Q)
            # music-bed level after normalize, measured on tail (post-transient) 2400..4800
            g=10**(norm_db(y)/20); tail=rms(y[2400:])*g
            res[(Q,period,name)]=(peak(y), 20*math.log10(max(tail,1e-12)))
            print(f"Q={Q:<5} switch={period:<3} {name:5} peak={peak(y):10.3f} normGain={norm_db(y):8.2f}dB tailRMS_after_norm={res[(Q,period,name)][1]:8.2f}dBFS")
# prediction (written before first run): DF2T switching transient raises the mix peak so peak-normalize lowers the
# post-transient mix by >=6 dB vs SVF; with a stable steady filter (no switching) both agree. Diverged runs are flagged, not scored.
def diverged(k): return res[k][0] > 1e5
stable_pairs=[(0.707,7),(0.707,480),(10.0,480)]
gaps=[res[(Q,p,"svf")][1]-res[(Q,p,"df2t")][1] for Q,p in stable_pairs]
print("tail-level loss of DF2T vs SVF (dB) for stable cases", [round(g,2) for g in gaps])
print("diverged:", {k:diverged(k) for k in res if diverged(k)})
steady_same = abs(res[(0.707,0,"df2t")][1]-res[(0.707,0,"svf")][1])<1e-6
ok = all(g>=3 for g in gaps) and steady_same and diverged((10.0,7,"df2t")) and not diverged((10.0,7,"svf"))
print("RESULT:", "PASS" if ok else "FAIL", f"DF2T mix {min(gaps):.1f}-{max(gaps):.1f} dB quieter after peak-normalize; Q10 7-sample DF2T diverged, SVF peak {res[(10.0,7,'svf')][0]:.2f}")
