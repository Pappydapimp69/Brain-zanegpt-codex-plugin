# Independent ratings (1-5) per fear vs forced head-to-head choice, on a fixed synthetic population.
def stats(pop):
    n=sum(c for c,_ in pop)
    mean=lambda k: sum(c*r[k] for c,r in pop)/n
    h2h_death_worse = sum(c for c,r in pop if r["D"]>r["S"])/n
    h2h_speak_worse = sum(c for c,r in pop if r["S"]>r["D"])/n
    return mean("S"), mean("D"), h2h_death_worse, h2h_speak_worse
pops = {
 "heterogeneous (60x S3/D4, 40x S5/D1)": [(60,{"S":3,"D":4}),(40,{"S":5,"D":1})],
 "homogeneous (100x S4/D3)":             [(100,{"S":4,"D":3})],
 "uniform tilt (70x S4/D3, 30x S3/D4)":  [(70,{"S":4,"D":3}),(30,{"S":3,"D":4})],
}
res={}
for k,p in pops.items():
    mS,mD,dw,sw=stats(p); res[k]=(mS,mD,dw,sw)
    print(f"{k:42s} meanS={mS:.2f} meanD={mD:.2f} rankS_above_D={mS>mD} death_worse_h2h={dw:.0%} speak_worse_h2h={sw:.0%}")
# reverse direction (speaking is NOT scarier in a head-to-head): independent rank agrees only without heterogeneity
het=res["heterogeneous (60x S3/D4, 40x S5/D1)"]; hom=res["homogeneous (100x S4/D3)"]; tilt=res["uniform tilt (70x S4/D3, 30x S3/D4)"]
# NIMH arithmetic from the kernel
sev=29.9+38.8+31.3; one_in=100/12.1
print("severity sums to %.1f; lifetime 12.1%% is 1 in %.1f; 12-month share of lifetime %.0f%%" % (sev, one_in, 7.1/12.1*100))
ok = (het[0]>het[1] and het[2]>0.5 and hom[0]>hom[1] and hom[3]==1.0 and tilt[0]>tilt[1] and tilt[3]>tilt[2]
      and abs(sev-100)<1e-9 and round(one_in,1)==8.3)
print("RESULT: %s independent mean ranks speaking above death in 3 of 3 populations but only 2 of 3 agree head-to-head; the heterogeneous one has death worse for %.0f%% (mean %.1f vs %.1f); 12.1%% lifetime is 1 in %.1f" % ("PASS" if ok else "FAIL", het[2]*100, het[0], het[1], one_in))
