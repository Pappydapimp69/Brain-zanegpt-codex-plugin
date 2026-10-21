# Prediction (before run): a 1D point moving at speed v with step dt hits a wall [10, 10+T] with T=2.
# Endpoint-only check (is position inside wall after a step) misses it for v*dt > T whenever the
# step lands past the wall; with v*dt exactly == T it can still hit or skip depending on phase.
# Swept check (segment overlap) never misses. Expect: endpoint misses > 0 for every v*dt > T case
# over 50 start phases, 0 misses at v*dt <= T/2, swept 0 misses everywhere.
# BREAK: a 2D thin wall with a diagonal path where only the swept test with the wall's width handles it.
T = 2.0; X0 = 10.0
def endpoint_hit(a, b): return X0 <= b <= X0 + T
def swept_hit(a, b):    return max(a, b) >= X0 and min(a, b) <= X0 + T
def run(step, check, phase):
    p = phase
    while p < 30:
        q = p + step
        if check(p, q): return True
        p = q
    return False
rows = {}
for ratio in (0.25, 0.5, 1.0, 1.01, 1.5, 3.0, 7.0):
    step = ratio * T
    phases = [i * 0.17 for i in range(50)]          # start positions 0..8.33, all left of wall
    miss_e = sum(not run(step, endpoint_hit, ph) for ph in phases)
    miss_s = sum(not run(step, swept_hit, ph) for ph in phases)
    rows[ratio] = (miss_e, miss_s)
    print("step/thickness %.2f endpoint misses %2d/50 swept misses %d/50" % (ratio, miss_e, miss_s))
# S3 BREAK: 2D diagonal path vs thin vertical wall x in [10,10+T], y in [0,1]; segment-vs-AABB swept
def seg_hits_box(p, q, box):
    (x0,y0),(x1,y1)=p,q; xmin,xmax,ymin,ymax=box
    t0,t1=0.0,1.0
    for d,lo,hi,s in ((x1-x0,xmin,xmax,x0),(y1-y0,ymin,ymax,y0)):
        if d==0:
            if s<lo or s>hi: return False
        else:
            a,b=(lo-s)/d,(hi-s)/d
            if a>b:a,b=b,a
            t0,t1=max(t0,a),min(t1,b)
            if t0>t1: return False
    return True
box=(10.0,12.0,0.0,1.0)
fast=((5.0,0.2),(17.0,0.8))        # crosses the wall within y range, no endpoint inside
ends_inside = box[0]<=fast[1][0]<=box[1] and box[2]<=fast[1][1]<=box[3]
print("S3 diagonal fast path: endpoint inside %s, swept AABB hit %s" % (ends_inside, seg_hits_box(*fast, box)))
low_ok = all(rows[r][0]==0 for r in (0.25,0.5))
tunnel = all(rows[r][0]>0 for r in (1.5,3.0,7.0))
swept_ok = all(v[1]==0 for v in rows.values())
print("RESULT: %s endpoint misses at ratios 0.25/0.5/1.0/1.01/1.5/3/7 = %s; swept misses all 0; 2D diagonal endpoint-inside=%s swept=%s"
      % ("PASS" if (low_ok and tunnel and swept_ok and (not ends_inside) and seg_hits_box(*fast, box)) else "FAIL",
         [rows[r][0] for r in sorted(rows)], ends_inside, seg_hits_box(*fast, box)))
