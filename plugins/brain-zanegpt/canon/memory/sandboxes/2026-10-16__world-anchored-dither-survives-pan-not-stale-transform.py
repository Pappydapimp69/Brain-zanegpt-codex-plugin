# Sandbox: Bayer 4x4 dither of a fixed world image (a gradient) under a camera pan, screen- vs world-anchored,
# then a renderer swap that leaves a stale camera offset for one frame.
B=[[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]
W=64;H=8
def world(wx): return (wx%32)/32.0       # world brightness ramp, repeating
def frame(cam,anchor):
    out=[]
    for y in range(H):
        row=[]
        for sx in range(W):
            wx=sx+cam
            bx=wx if anchor=="world" else sx
            thr=(B[y%4][bx%4]+0.5)/16
            row.append(1 if world(wx)>thr else 0)
        out.append(row)
    return out
def moved_err(a,b,shift):
    # fraction of pixels differing between frame b and frame a shifted by `shift` screen pixels (content should move rigidly)
    d=0;n=0
    for y in range(H):
        for x in range(W-8):
            n+=1;d+= a[y][x+shift]!=b[y][x]
    return d/n
f0w=frame(0,"world");f0s=frame(0,"screen")
res={}
for shift in(1,2,3,4,5):
    res[shift]=(moved_err(f0w,frame(shift,"world"),shift),moved_err(f0s,frame(shift,"screen"),shift))
    print("pan",shift,"world err %.3f screen err %.3f"%res[shift])
# stale transform: the right frame is cam=10 but the swap left cam=7
right=frame(10,"world");stale=frame(7,"world")
diff=sum(right[y][x]!=stale[y][x] for y in range(H) for x in range(W))
# a pure-colour (no dither) draw with the same stale cam shifts content by 3 px; a world-anchored dither also shifts consistently
shift_ok=moved_err(stale,right,3)
print("stale-vs-right differing pixels",diff,"; rigid 3px shift err %.3f"%shift_ok)
ok = all(res[s][0]==0 for s in res) and any(res[s][1]>0.05 for s in res) and diff>0 and shift_ok==0
print("RESULT: %s world-anchored pan err 0 at shifts 1-5, screen-anchored worst %.3f, stale cam off by 3 differs in %d px yet is a rigid 3px shift (err %.3f)"%("PASS" if ok else "FAIL",max(res[s][1] for s in res),diff,shift_ok))
