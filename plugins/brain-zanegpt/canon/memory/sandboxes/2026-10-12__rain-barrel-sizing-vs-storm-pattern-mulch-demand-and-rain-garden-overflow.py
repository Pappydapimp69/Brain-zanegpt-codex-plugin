"""Deterministic 60-day model: roof catchment (0.623 gal/sqft/in) -> first flush -> barrel -> drip demand,
overflow -> rain garden (roof/6 sqft, 6in ponding). Demand from mulch/bare drip totals (E105: 424 vs 226 mm/60d)."""
ROOF=1000.0; GARDEN_SQFT=200.0; DAYS=60
GAL_PER_MM_GARDEN = GARDEN_SQFT*0.0929/3.785   # 1 mm over garden = 1 L/m2 -> gal
FF_GAL = 0.5*(ROOF*0.0929)/3.785               # 0.5 L per m2 roof, per event
GUTTER=0.05
def storms(n, inches):  # n equal storms evenly spaced
    gap=DAYS//n
    return {i*gap+1: inches for i in range(n)}
def run(storm, barrel, demand_mm_total, ff=True, gutter=GUTTER):
    dem=demand_mm_total/DAYS*GAL_PER_MM_GARDEN
    st=0.0; supplied=0.0; over=0.0; ffl=0.0; gl=0.0; gross=0.0
    for d in range(DAYS):
        if d in storm:
            g=ROOF*storm[d]*0.623; gross+=g
            f=min(g,FF_GAL) if ff else 0.0; ffl+=f
            gg=(g-f)*gutter; gl+=gg
            inflow=g-f-gg
            room=barrel-st; take=min(room,inflow); st+=take; over+=inflow-take
        use=min(st,dem); st-=use; supplied+=use
    return dict(gross=gross,ffl=ffl,gl=gl,over=over,supplied=supplied,demand=dem*DAYS,net=gross-ffl-gl)
def garden_sink(over_events_gal, area_div=6.0):
    cap=ROOF/area_div*0.5*7.48  # gal ponded at 6in
    return min(over_events_gal,cap),cap
BARE,MULCH=424.0,226.0
res=[]
print("== S1 same 3in total, three storm patterns, gross vs 10%-haircut claim")
claim=ROOF*3*0.623*0.9
for n,inch in [(2,1.5),(6,0.5),(12,0.25),(30,0.1)]:
    r=run(storms(n,inch),10**6,BARE)
    print(f"n={n:2d} x{inch}in net={r['net']:.0f} claim={claim:.0f} loss%={100*(1-r['net']/r['gross']):.1f}")
    res.append((n,100*(1-r['net']/r['gross'])))
loss={n:l for n,l in res}
s1_ok = loss[2]<10 and loss[30]>15 and loss[6]<=10   # haircut holds only for few/larger storms
print("== S2 barrel size vs coverage, 6x0.5in storms, bare vs 3in mulch")
cov={}
for b in [55,165,500,1100]:
    for lab,dm in [("bare",BARE),("mulch",MULCH)]:
        r=run(storms(6,0.5),b,dm); cov[(b,lab)]=r['supplied']/r['demand']
        print(f"barrel={b:4d} {lab:5s} coverage={100*cov[(b,lab)]:.0f}% overflow={r['over']:.0f}gal")
s2_ok = cov[(165,'mulch')]>cov[(165,'bare')] and cov[(1100,'bare')]<1 and cov[(55,'bare')]<0.2
print("== S3 BREAK: one 3in storm; barrel 55 vs 1100, rain garden roof/6 vs roof/8 absorbs overflow")
for b in [55,1100]:
    r=run(storms(1,3.0),b,BARE)
    for div in (6.0,8.0):
        sunk,cap=garden_sink(r['over'],div)
        print(f"barrel={b} overflow={r['over']:.0f} garden cap={cap:.0f} sunk={sunk:.0f} unhandled={r['over']-sunk:.0f}")
r55=run(storms(1,3.0),55,BARE); sunk,cap=garden_sink(r55['over'])
s3_ok = (r55['over']-sunk)>1000   # neither barrel nor garden handles a 3in single storm
print("== S4 first flush off vs on, 30x0.1in")
a=run(storms(30,0.1),10**6,BARE,ff=True); b2=run(storms(30,0.1),10**6,BARE,ff=False)
print(f"ff on net={a['net']:.0f} off net={b2['net']:.0f} lost to diverter={a['ffl']:.0f}")
s4_ok = a['net']<0.85*b2['net']
print("== S5 mulch halves barrel needed: smallest barrel reaching 90% of what 1100 gal gives")
def need(dm):
    full=run(storms(6,0.5),1100,dm)['supplied']
    for b in range(25,1101,25):
        if run(storms(6,0.5),b,dm)['supplied']>=0.9*full: return b
nb,nm=need(BARE),need(MULCH); print("bare",nb,"mulch",nm)
s5_ok = nm<nb
ok=s1_ok and s2_ok and s3_ok and s4_ok and s5_ok
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" haircut loss% by storm count {[(n,round(l,1)) for n,l in res]}; coverage 165gal bare {100*cov[(165,'bare')]:.0f}% mulch {100*cov[(165,'mulch')]:.0f}%; 3in single storm unhandled {r55['over']-sunk:.0f} gal; barrel needed bare {nb} mulch {nm}; flags {s1_ok,s2_ok,s3_ok,s4_ok,s5_ok}")
