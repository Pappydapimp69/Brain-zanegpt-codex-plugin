#!/usr/bin/env python3
"""T11 sandbox: which of {wrong material, z-fighting, inverted normal, broken shader}
can cheap automated checks catch, and at what false-alarm rate?

REAL render: raw WebGL (no external scripts) in headless Chromium (SwiftShader), pixels read
back with readPixels and shipped to Python through --dump-dom. Stdlib only. Deterministic
(no RNG; fixed camera/jitter constants). If no Chromium binary is found this prints
RESULT: SKIPPED (never PASS).

Run:  python3 -I this_file.py

PREDICTION (written before first run; also in pass5/prediction.txt):
 P1 null check detects 1 of ~23 defects (compile error only), 0 false alarms.
 P2 golden-diff MAE>1.0 detects >=20/23 but false-alarms on >=3/10 benign; no MAE threshold
    separates visible defects from benign (max benign MAE > min visible-defect MAE).
 P3 lighting-invariant suite detects >=18/23 with 0/10 false alarms.
 P4 material is the weakest class for invariant checks (<=4/6); inverted normal >=4/5.

Notes added after the first run (honest log): run 1 showed 1 false alarm on clean far-camera
renders because object-level checks (3b/3d) fired where the reference pass shows a single
face (no N.L variation to test). Rule added: such an object-level check is N/A, not an alarm
(MIN_PIX and N.L-range guards). Predictions were NOT edited. The exact-bytes row (C2x) was
added post-hoc. Thresholds (chroma 0.08, corr 0.9, decal 0.97, unstable 2%, MAE 1.0) were
fixed before run 1. Benign set / defect set are chosen by the author: rates are for THIS set
on ONE renderer (SwiftShader), not a population estimate; no cross-GPU variance is measured.
"""
import base64, glob, html, json, math, os, subprocess, sys, tempfile

W = H = 128
MIN_PIX = 30  # an object-level check is only evaluated when >=30 interior pixels exist
L0 = (0.5, 0.8, 0.4)

# ----------------------------------------------------------------------------- cases
BASE = dict(dist=8.0, near=0.01, far=1000.0, aa=0, decalOff=0.02,
            sphereAlb=(0.9, 0.4, 0.2), cubeAlb=(0.2, 0.4, 0.9),
            groundAlb=(0.35, 0.5, 0.35), decalAlb=(0.9, 0.8, 0.1),
            seg=(24, 16), flipSphere=0, flipCube=0, fs='ok', I=0.9, amb=0.15,
            camYaw=0.0, camDy=0.0, lightRot=0.0, clear=(0.1, 0.1, 0.15), sphereDx=0.0)
JIT = 0.004  # second render: camera yaw + 0.004 rad (~0.65 px at 128 px)

CASES = []
def add(name, cls, defect, **kw):
    c = dict(BASE); c.update(kw); c.update(name=name, cls=cls, defect=defect)
    CASES.append(c)

# controls (golden sources + determinism)
add('clean_near', 'clean', False)
add('clean_near_rerun', 'clean', False)
add('clean_far', 'clean', False, dist=16.0)
# wrong material (albedo of an object differs from design)
add('mat_swap', 'material', True, sphereAlb=BASE['cubeAlb'], cubeAlb=BASE['sphereAlb'])
add('mat_hue_big', 'material', True, sphereAlb=(0.2, 0.4, 0.9))
add('mat_hue_mid', 'material', True, sphereAlb=(0.85, 0.5, 0.2))
add('mat_hue_subtle', 'material', True, sphereAlb=(0.9, 0.43, 0.2))
add('mat_lum_only', 'material', True, sphereAlb=(0.72, 0.32, 0.16))   # BREAK: same hue, x0.8
add('mat_white_default', 'material', True, sphereAlb=(1.0, 1.0, 1.0))
# z-fighting (decal offset above ground, world units; depth res ~4e-4 near / ~1.5e-3 far)
add('zf_near_0', 'zfight', True, decalOff=0.0)
add('zf_near_2e-4', 'zfight', True, decalOff=2e-4)
add('zf_near_1e-3', 'zfight', True, decalOff=1e-3)
add('zf_far_1e-3', 'zfight', True, decalOff=1e-3, dist=16.0)
add('zf_far_3e-3', 'zfight', True, decalOff=3e-3, dist=16.0)
# inverted normals
add('nrm_sphere_all', 'normal', True, flipSphere=1)
add('nrm_cube_all', 'normal', True, flipCube=1)
add('nrm_cube_top', 'normal', True, flipCube='top')    # BREAK for the mirrored-light test
add('nrm_sphere_half', 'normal', True, flipSphere='half')
add('nrm_everything', 'normal', True, flipSphere=1, flipCube=1)
# broken shader
add('sh_compile_error', 'shader', True, fs='compile')
add('sh_nan_output', 'shader', True, fs='nan')
add('sh_no_normalize', 'shader', True, fs='nonorm')
add('sh_rb_swap', 'shader', True, fs='rbswap')
add('sh_light_unset', 'shader', True, fs='lightunset')
add('sh_gamma_twice', 'shader', True, fs='gamma2')
add('sh_gamma_missing', 'shader', True, fs='nogamma')
# benign variations (should NOT alarm)
add('b_aa_on', 'benign', False, aa=1)
add('b_cam_yaw', 'benign', False, camYaw=0.003)
add('b_cam_dy', 'benign', False, camDy=0.02)
add('b_light_x1.03', 'benign', False, I=0.9 * 1.03)
add('b_light_x0.95', 'benign', False, I=0.9 * 0.95)
add('b_ambient_0.17', 'benign', False, amb=0.17)
add('b_light_rot_1deg', 'benign', False, lightRot=1.0)
add('b_tessellation_32x20', 'benign', False, seg=(32, 20))
add('b_clear_colour', 'benign', False, clear=(0.12, 0.12, 0.17))
add('b_far_aa_on', 'benign', False, dist=16.0, aa=1)
add('c_content_sphere_moved', 'content', False, sphereDx=0.3)  # intentional art change

# ----------------------------------------------------------------------------- page
PAGE = r"""<!doctype html><meta charset=utf-8><title>t11</title><pre id=out></pre>
<script>
const CASES = __CASES__, W=__W__, H=__H__, JIT=__JIT__, L0=__L0__;
const errs=[]; window.onerror=(m)=>{errs.push(String(m))};
console.error=(...a)=>{errs.push(a.join(' '));};
function norm(v){const l=Math.hypot(...v);return v.map(x=>x/l);}
function cross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];}
function dot(a,b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
function sub(a,b){return [a[0]-b[0],a[1]-b[1],a[2]-b[2]];}
function persp(fy,as,n,f){const t=1/Math.tan(fy/2);return [t/as,0,0,0,0,t,0,0,0,0,(f+n)/(n-f),-1,0,0,2*f*n/(n-f),0];}
function lookAt(e,c,u){const z=norm(sub(e,c)),x=norm(cross(u,z)),y=cross(z,x);
 return [x[0],y[0],z[0],0,x[1],y[1],z[1],0,x[2],y[2],z[2],0,-dot(x,e),-dot(y,e),-dot(z,e),1];}
function mul(a,b){const o=new Array(16).fill(0);for(let c=0;c<4;c++)for(let r=0;r<4;r++){let s=0;for(let k=0;k<4;k++)s+=a[k*4+r]*b[c*4+k];o[c*4+r]=s;}return o;}

// ---- geometry (world space; no culling so normals are the only thing under test)
function quadGrid(n,x0,x1,z0,z1,y,altDiag){const p=[],nn=[],ix=[];
 for(let j=0;j<=n;j++)for(let i=0;i<=n;i++){p.push(x0+(x1-x0)*i/n,y,z0+(z1-z0)*j/n);nn.push(0,1,0);}
 for(let j=0;j<n;j++)for(let i=0;i<n;i++){const a=j*(n+1)+i,b=a+1,c=a+n+1,d=c+1;
  if(altDiag&&((i+j)&1)) ix.push(a,b,d,a,d,c); else ix.push(a,b,c,b,d,c);}
 return {p,n:nn,i:ix};}
function sphere(seg,r,cx,cy,cz,flip){const ns=seg[0],nt=seg[1];const p=[],n=[],ix=[];
 for(let t=0;t<=nt;t++){const th=Math.PI*t/nt;for(let s=0;s<=ns;s++){const ph=2*Math.PI*s/ns;
  const x=Math.sin(th)*Math.cos(ph),y=Math.cos(th),z=Math.sin(th)*Math.sin(ph);
  p.push(cx+r*x,cy+r*y,cz+r*z);let sg=1; if(flip===1)sg=-1; else if(flip==='half'&&y>0)sg=-1;
  n.push(sg*x,sg*y,sg*z);}}
 for(let t=0;t<nt;t++)for(let s=0;s<ns;s++){const a=t*(ns+1)+s,b=a+1,c=a+ns+1,d=c+1;ix.push(a,c,b,b,c,d);}
 return {p,n,i:ix};}
function cube(sz,cx,cy,cz,flip){const h=sz/2;const faces=[[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]];
 const p=[],n=[],ix=[];faces.forEach((f,fi)=>{const nv=f;let u,v;
  if(nv[0]) {u=[0,1,0];v=[0,0,1];} else if(nv[1]) {u=[1,0,0];v=[0,0,1];} else {u=[1,0,0];v=[0,1,0];}
  const base=p.length/3;[[-1,-1],[1,-1],[1,1],[-1,1]].forEach((ab)=>{const a=ab[0],b=ab[1];
   p.push(cx+h*(nv[0]+a*u[0]+b*v[0]),cy+h*(nv[1]+a*u[1]+b*v[1]),cz+h*(nv[2]+a*u[2]+b*v[2]));
   let sg=1; if(flip===1)sg=-1; else if(flip==='top'&&fi===2)sg=-1; n.push(sg*nv[0],sg*nv[1],sg*nv[2]);});
  ix.push(base,base+1,base+2,base,base+2,base+3);});
 return {p,n,i:ix};}

// ---- shaders
const VS=`attribute vec3 aP;attribute vec3 aN;uniform mat4 uM;varying vec3 vN;
void main(){vN=aN;gl_Position=uM*vec4(aP,1.0);}`;
function fsSrc(mod){
 let nrm='vec3 n=normalize(vN);', tail='c=pow(c,vec3(1.0/2.2));';
 let post='';
 if(mod==='compile') nrm='vec3 n=normalise(vN);';
 if(mod==='nonorm') nrm='vec3 n=vN;';
 if(mod==='gamma2') tail='c=pow(c,vec3(1.0/2.2));c=pow(c,vec3(1.0/2.2));';
 if(mod==='nogamma') tail='';
 if(mod==='rbswap') post='c=c.bgr;';
 if(mod==='nan') post='c=c*(uZero/uZero);';
 return `precision highp float;varying vec3 vN;uniform vec3 uA;uniform vec3 uL;uniform float uI;uniform float uAmb;uniform float uZero;
void main(){${nrm}float d=max(dot(n,uL),0.0);vec3 c=uA*(uAmb+uI*d);${tail}${post}gl_FragColor=vec4(c,1.0);}`;}
const FS_REF=`precision highp float;varying vec3 vN;uniform float uId;
void main(){vec3 n=normalize(vN);gl_FragColor=vec4(n*0.5+0.5,uId/255.0);}`;

const info={};
function mkCtx(aa){const cv=document.createElement('canvas');cv.width=W;cv.height=H;
 const gl=cv.getContext('webgl',{antialias:!!aa,depth:true,alpha:true,premultipliedAlpha:false,preserveDrawingBuffer:true});
 gl.__progs={};return gl;}
function prog(gl,key,fs){ if(gl.__progs[key]!==undefined) return gl.__progs[key];
 function sh(t,s){const o=gl.createShader(t);gl.shaderSource(o,s);gl.compileShader(o);
  return gl.getShaderParameter(o,gl.COMPILE_STATUS)?o:null;}
 const v=sh(gl.VERTEX_SHADER,VS),f=sh(gl.FRAGMENT_SHADER,fs);let p=null;
 if(v&&f){p=gl.createProgram();gl.attachShader(p,v);gl.attachShader(p,f);gl.bindAttribLocation(p,0,'aP');gl.bindAttribLocation(p,1,'aN');
  gl.linkProgram(p); if(!gl.getProgramParameter(p,gl.LINK_STATUS)) p=null;}
 gl.__progs[key]=p;return p;}
function drawObj(gl,g){const bp=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,bp);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(g.p),gl.STATIC_DRAW);
 gl.enableVertexAttribArray(0);gl.vertexAttribPointer(0,3,gl.FLOAT,false,0,0);
 const bn=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,bn);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(g.n),gl.STATIC_DRAW);
 gl.enableVertexAttribArray(1);gl.vertexAttribPointer(1,3,gl.FLOAT,false,0,0);
 const bi=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,bi);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint16Array(g.i),gl.STATIC_DRAW);
 gl.drawElements(gl.TRIANGLES,g.i.length,gl.UNSIGNED_SHORT,0);}
function scene(c,clean){const off=clean?0.05:c.decalOff;
 return {ground:quadGrid(1,-10,10,-10,10,0,false),
  decal:quadGrid(8,-2,2,1.5,4.5,off,true),
  sphere:sphere(c.seg,1,-1.5+c.sphereDx,1,0,clean?0:c.flipSphere),
  cube:cube(1.6,1.8,0.8,-0.5,clean?0:c.flipCube)};}
function camMVP(c,yawExtra){const th=c.camYaw+yawExtra;const t=[0,0.5,0];let e=[0,3+c.camDy*c.dist,c.dist];
 const dx=e[0]-t[0],dz=e[2]-t[2];e=[t[0]+dx*Math.cos(th)+dz*Math.sin(th),e[1],t[2]-dx*Math.sin(th)+dz*Math.cos(th)];
 return mul(persp(40*Math.PI/180,1,c.near,c.far),lookAt(e,t,[0,1,0]));}
function readRGBA(gl){const b=new Uint8Array(W*H*4);gl.readPixels(0,0,W,H,gl.RGBA,gl.UNSIGNED_BYTE,b);return b;}
function b64(u8){let s='';for(let i=0;i<u8.length;i+=8192)s+=String.fromCharCode.apply(null,u8.subarray(i,i+8192));return btoa(s);}
function rgbOnly(b){const o=new Uint8Array(W*H*3);for(let i=0,j=0;i<W*H;i++){o[j++]=b[4*i];o[j++]=b[4*i+1];o[j++]=b[4*i+2];}return o;}

const ctx=[mkCtx(0),mkCtx(1)];
info.depthBits=ctx[0].getParameter(ctx[0].DEPTH_BITS);
const dbg=ctx[0].getExtension('WEBGL_debug_renderer_info');
info.renderer=dbg?ctx[0].getParameter(dbg.UNMASKED_RENDERER_WEBGL):'n/a';
const out={info:info,cases:{}};
const refCache={};
function setup(gl,c){gl.viewport(0,0,W,H);gl.clearColor(c[0],c[1],c[2],c[3]);gl.clearDepth(1);
 gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.enable(gl.DEPTH_TEST);gl.depthFunc(gl.LESS);gl.disable(gl.BLEND);}
function renderLit(c,yawExtra){const gl=ctx[c.aa?1:0];
 const p=prog(gl,c.fs,fsSrc(c.fs));
 setup(gl,[c.clear[0],c.clear[1],c.clear[2],1]);
 gl.getError();
 const sc=scene(c,false);
 if(p){gl.useProgram(p);
  const L=norm(L0);const a=c.lightRot*Math.PI/180;const Lr=[L[0]*Math.cos(a)+L[2]*Math.sin(a),L[1],-L[0]*Math.sin(a)+L[2]*Math.cos(a)];
  const lightOff=(c.fs==='lightunset');
  gl.uniformMatrix4fv(gl.getUniformLocation(p,'uM'),false,camMVP(c,yawExtra));
  gl.uniform3fv(gl.getUniformLocation(p,'uL'),lightOff?[0,0,0]:Lr);
  gl.uniform1f(gl.getUniformLocation(p,'uI'),lightOff?0:c.I);
  gl.uniform1f(gl.getUniformLocation(p,'uAmb'),c.amb);gl.uniform1f(gl.getUniformLocation(p,'uZero'),0);
  const al=gl.getUniformLocation(p,'uA');
  gl.uniform3fv(al,c.groundAlb);drawObj(gl,sc.ground);
  gl.uniform3fv(al,c.decalAlb);drawObj(gl,sc.decal);
  gl.uniform3fv(al,c.sphereAlb);drawObj(gl,sc.sphere);
  gl.uniform3fv(al,c.cubeAlb);drawObj(gl,sc.cube);
 } else { gl.useProgram(null); drawObj(gl,sc.ground); } // naive app: tries to draw, nothing appears
 const glerr=gl.getError();
 return {rgb:rgbOnly(readRGBA(gl)),linked:!!p,glerr:glerr};}
function renderRef(c){const key=[c.dist,c.near,c.far,c.seg.join('x'),c.sphereDx,c.camYaw,c.camDy].join('|');
 if(refCache[key]) return refCache[key];
 const gl=ctx[0];const p=prog(gl,'ref',FS_REF);setup(gl,[0,0,0,0]);
 gl.useProgram(p);gl.uniformMatrix4fv(gl.getUniformLocation(p,'uM'),false,camMVP(Object.assign({},c,{camYaw:0,camDy:0}),0));
 const sc=scene(c,true);const idl=gl.getUniformLocation(p,'uId');
 gl.uniform1f(idl,1);drawObj(gl,sc.ground);gl.uniform1f(idl,2);drawObj(gl,sc.decal);
 gl.uniform1f(idl,3);drawObj(gl,sc.sphere);gl.uniform1f(idl,4);drawObj(gl,sc.cube);
 const r=b64(readRGBA(gl));refCache[key]=r;return r;}
for(const c of CASES){
 const A=renderLit(c,0),B=renderLit(c,JIT);
 out.cases[c.name]={A:b64(A.rgb),B:b64(B.rgb),ref:renderRef(c),linked:A.linked,glerr:A.glerr|B.glerr};}
out.errs=errs;
document.getElementById('out').textContent=JSON.stringify(out);
</script>"""

# ----------------------------------------------------------------------------- driver
def find_chrome():
    roots = [os.environ.get('PLAYWRIGHT_BROWSERS_PATH', ''), '/opt/pw-browsers']
    for r in roots:
        if not r:
            continue
        for pat in ('chromium-*/chrome-linux/chrome', 'chromium_headless_shell-*/chrome-linux/headless_shell'):
            m = sorted(glob.glob(os.path.join(r, pat)))
            if m and os.access(m[-1], os.X_OK):
                return m[-1]
    return None

def render_all():
    chrome = find_chrome()
    if not chrome:
        return None, 'no chromium binary'
    page = (PAGE.replace('__CASES__', json.dumps(CASES)).replace('__W__', str(W)).replace('__H__', str(H))
            .replace('__JIT__', str(JIT)).replace('__L0__', json.dumps(list(L0))))
    d = tempfile.mkdtemp(prefix='t11page_')
    pth = os.path.join(d, 'scene.html')
    with open(pth, 'w') as f:
        f.write(page)
    cmd = [chrome, '--headless', '--no-sandbox', '--disable-gpu-sandbox', '--use-angle=swiftshader',
           '--use-gl=angle', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist',
           '--user-data-dir=' + os.path.join(d, 'profile'), '--virtual-time-budget=20000',
           '--dump-dom', 'file://' + pth]
    try:
        r = subprocess.run(cmd, cwd=d, capture_output=True, text=True, timeout=240)
    except Exception as e:  # noqa
        return None, 'chromium failed: %r' % (e,)
    s = r.stdout
    a = s.find('<pre id="out">')
    b = s.find('</pre>', a)
    if a < 0 or b < 0:
        return None, 'no output from page (rc=%s) %s' % (r.returncode, r.stderr[-200:])
    txt = html.unescape(s[a + len('<pre id="out">'):b])
    try:
        return json.loads(txt), chrome
    except Exception as e:
        return None, 'bad json: %r' % (e,)

# ----------------------------------------------------------------------------- analysis
def px(raw, i):
    return raw[3 * i], raw[3 * i + 1], raw[3 * i + 2]

def lum(r, g, b):
    return 0.299 * r + 0.587 * g + 0.114 * b

def eroded(ids, target, n):
    """pixels whose (2n+1)^2 neighbourhood is all `target`"""
    out = []
    for y in range(n, H - n):
        for x in range(n, W - n):
            i = y * W + x
            if ids[i] != target:
                continue
            ok = True
            for dy in range(-n, n + 1):
                for dx in range(-n, n + 1):
                    if ids[(y + dy) * W + x + dx] != target:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                out.append(i)
    return out

def pearson(a, b):
    n = len(a)
    if n < 10:
        return None
    ma, mb = sum(a) / n, sum(b) / n
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va < 1e-9 or vb < 1e-9:
        return None  # constant: no light response at all
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(va * vb)

def median(v):
    v = sorted(v)
    return v[len(v) // 2] if v else float('nan')

def expected_chroma(alb):
    return (math.log(alb[0] / alb[1]) / 2.2, math.log(alb[2] / alb[1]) / 2.2)

def analyse(case, data, golden):
    A = base64.b64decode(data['A']); B = base64.b64decode(data['B'])
    ref = base64.b64decode(data['ref'])
    G = base64.b64decode(golden['A'])
    ids = [round(ref[4 * i + 3]) for i in range(W * H)]
    res = {}
    # ---- C0 null check: program linked and no GL error (what a "no errors" test sees)
    res['C0_null'] = (not data['linked']) or data['glerr'] != 0
    # ---- C1 pixel statistics vs golden stats (channel means +-5%, no pixel alignment needed)
    def means(raw):
        n = W * H
        return [sum(raw[3 * i + k] for i in range(n)) / n for k in range(3)]
    mA, mG = means(A), means(G)
    res['C1_stats'] = any(abs(a - g) > 0.05 * max(g, 1.0) for a, g in zip(mA, mG))
    # ---- C2 golden diff
    mae = sum(abs(A[k] - G[k]) for k in range(len(A))) / len(A)
    vis = sum(1 for i in range(W * H) if max(abs(A[3 * i + k] - G[3 * i + k]) for k in range(3)) > 12) / (W * H)
    res['mae'] = mae
    res['vis_frac'] = vis
    # ---- C3 lighting-invariant suite (needs the calibration scene + reference pass)
    sub = {}
    # 3a chroma ratios per object vs design (invariant to light intensity and ambient level)
    albs = {1: case['groundAlb'], 3: BASE['sphereAlb'], 4: BASE['cubeAlb']}
    chroma_bad = False
    chroma_worst = 0.0
    for oid, alb in albs.items():
        pix = eroded(ids, oid, 1)
        if len(pix) < MIN_PIX:
            continue  # object too small at this camera: check not evaluable (N/A), not an alarm
        vals_rg, vals_bg = [], []
        for i in pix:
            r, g, b = px(A, i)
            if min(r, g, b) < 12:
                continue
            vals_rg.append(math.log(r / g)); vals_bg.append(math.log(b / g))
        if len(vals_rg) < 10:
            chroma_bad = True
            chroma_worst = 9.0
            continue
        er, eb = expected_chroma(alb)
        dev = max(abs(median(vals_rg) - er), abs(median(vals_bg) - eb))
        chroma_worst = max(chroma_worst, dev)
        if dev > 0.08:
            chroma_bad = True
    sub['3a_chroma'] = chroma_bad
    # 3b lighting correlation against the reference normal pass: corr(lum, max(0,N.L0)) per object
    Ln = math.sqrt(sum(x * x for x in L0)); Lv = [x / Ln for x in L0]
    r_min = 1.0
    corr_bad = False
    for oid in (3, 4):
        pix = eroded(ids, oid, 1)
        if len(pix) < MIN_PIX:
            continue  # N/A at this camera
        ys, es = [], []
        for i in pix:
            nx, ny, nz = [ref[4 * i + k] / 255.0 * 2 - 1 for k in range(3)]
            es.append(max(0.0, nx * Lv[0] + ny * Lv[1] + nz * Lv[2]))
            ys.append(lum(*px(A, i)))
        if max(es) - min(es) < 0.05:
            continue  # reference shows a single face/uniform N.L: lighting response not testable here (N/A)
        r = pearson(ys, es)
        if r is None or r < 0.9:
            corr_bad = True
        r_min = min(r_min, -9 if r is None else r)
    sub['3b_lightcorr'] = corr_bad
    res['r_min'] = r_min
    # 3c z-fight: decal footprint (reference mask, eroded 2px) must be decal-coloured and stable under jitter
    dpix = eroded(ids, 2, 2)
    n_dec = 0; n_unstable = 0
    thr = 0.5 * (math.log(case['decalAlb'][0] / case['decalAlb'][2]) / 2.2)  # midpoint ground(0)..decal
    for i in dpix:
        r, g, b = px(A, i)
        if r > 0 and b > 0 and math.log(r / b) > thr:
            n_dec += 1
        if max(abs(A[3 * i + k] - B[3 * i + k]) for k in range(3)) > 24:
            n_unstable += 1
    frac_dec = n_dec / max(len(dpix), 1)
    frac_unst = n_unstable / max(len(dpix), 1)
    sub['3c_zfight'] = (frac_dec < 0.97) or (frac_unst > 0.02)
    res['decal_frac'] = frac_dec; res['decal_unstable'] = frac_unst
    # 3d sanity: lit objects are neither black nor flat
    san = False
    for oid in (3, 4):
        pix = eroded(ids, oid, 1)
        es_ = [max(0.0, sum((ref[4 * i + k] / 255.0 * 2 - 1) * Lv[k] for k in range(3))) for i in pix]
        if pix and max(es_) - min(es_) < 0.05:
            continue  # uniform expected shading (one face visible): flatness is legitimate, N/A
        ls = [lum(*px(A, i)) for i in pix]
        if len(ls) < MIN_PIX:
            continue  # N/A at this camera
        mu = sum(ls) / len(ls)
        sd = math.sqrt(sum((x - mu) ** 2 for x in ls) / len(ls))
        if mu < 15 or sd < 3:
            san = True
    sub['3d_sanity'] = san
    res.update(sub)
    res['C3_invariant'] = any(sub.values())
    res['chroma_dev'] = chroma_worst
    return res

def main():
    out, how = render_all()
    if out is None:
        print('no real render possible: %s' % how)
        print('RESULT: SKIPPED no browser/WebGL available (%s); nothing was verified' % how)
        return
    print('renderer: %s | depthBits=%s | page errors: %d %s' % (out['info']['renderer'], out['info']['depthBits'], len(out['errs']), out['errs'][:3]))
    same = out['cases']['clean_near']['A'] == out['cases']['clean_near_rerun']['A']
    print('determinism: clean render twice byte-identical = %s' % same)
    results = {}
    for c in CASES:
        golden = out['cases']['clean_far' if c['dist'] == 16.0 else 'clean_near']
        results[c['name']] = analyse(c, out['cases'][c['name']], golden)
    f = lambda b: 'X' if b else '.'
    print('\n%-24s %-8s %6s %5s | C0 C1 C2 | 3a 3b 3c 3d | C3' % ('case', 'class', 'MAE', 'vis%'))
    for c in CASES:
        r = results[c['name']]
        print('%-24s %-8s %6.2f %5.2f |  %s  %s  %s |  %s  %s  %s  %s |  %s    (r_min=%.2f decal=%.2f unst=%.2f chromaDev=%.2f)' % (
            c['name'], c['cls'], r['mae'], 100 * r['vis_frac'], f(r['C0_null']), f(r['C1_stats']), f(r['mae'] > 1.0),
            f(r['3a_chroma']), f(r['3b_lightcorr']), f(r['3c_zfight']), f(r['3d_sanity']), f(r['C3_invariant']),
            r['r_min'], r['decal_frac'], r['decal_unstable'], r['chroma_dev']))
    classes = ['material', 'zfight', 'normal', 'shader']
    defects = [c for c in CASES if c['defect']]
    benign = [c for c in CASES if c['cls'] == 'benign']
    content = [c for c in CASES if c['cls'] == 'content']
    def rate(lst, fn):
        return sum(1 for c in lst if fn(results[c['name']])), len(lst)
    checks = [('C0 null/no-errors', lambda r: r['C0_null']),
              ('C2x exact bytes', lambda r: r['mae'] > 0.0),   # post-hoc row: the fingerprint-kernel pattern
              ('C1 pixel-stats', lambda r: r['C1_stats']),
              ('C2 golden MAE>1.0', lambda r: r['mae'] > 1.0),
              ('C2 golden MAE>4.0', lambda r: r['mae'] > 4.0),
              ('C3a chroma', lambda r: r['3a_chroma']),
              ('C3b light-corr', lambda r: r['3b_lightcorr']),
              ('C3c zfight', lambda r: r['3c_zfight']),
              ('C3d sanity', lambda r: r['3d_sanity']),
              ('C3 invariant suite', lambda r: r['C3_invariant']),
              ('C0+C3 suite', lambda r: r['C3_invariant'] or r['C0_null'])]
    cd = dict(checks)
    print('\nDETECTION by class (caught/defects); FALSE ALARMS on benign n=%d and content-change n=%d' % (len(benign), len(content)))
    print('%-20s %9s %9s %9s %9s | %9s | %9s %9s' % ('check', *classes, 'ALL', 'FA benign', 'FA content'))
    summary = {}
    for name, fn in checks:
        row = []
        for cl in classes:
            k, n = rate([c for c in defects if c['cls'] == cl], fn)
            row.append('%d/%d' % (k, n))
        ka, na = rate(defects, fn)
        kb, nb = rate(benign, fn)
        kc, nc = rate(content, fn)
        summary[name] = (ka, na, kb, nb, kc, nc)
        print('%-20s %9s %9s %9s %9s | %9s | %9s %9s' % (name, *row, '%d/%d' % (ka, na), '%d/%d' % (kb, nb), '%d/%d' % (kc, nc)))
    def visible(c):
        r = results[c['name']]
        return r['vis_frac'] >= 0.002 or r['decal_frac'] < 0.97 or r['decal_unstable'] > 0.02
    vis_def = [c for c in defects if visible(c)]
    lat_def = [c for c in defects if not visible(c)]
    print('\ndefects visible by the pixel oracle (>=0.2%% px differ >12 levels vs clean): %d/%d; latent: %s' % (
        len(vis_def), len(defects), [c['name'] for c in lat_def]))
    for name in ('C2 golden MAE>1.0', 'C3 invariant suite', 'C0+C3 suite'):
        k, n = rate(vis_def, cd[name])
        print('  %-20s detects %d/%d of VISIBLE defects' % (name, k, n))
    vmae = [(results[c['name']]['mae'], c['name']) for c in vis_def]
    bmae = [(results[c['name']]['mae'], c['name']) for c in benign]
    min_vis = min(vmae); max_ben = max(bmae)
    print('\ngolden-diff separability: min visible-defect MAE = %.3f (%s); max benign MAE = %.3f (%s)' % (min_vis + max_ben))
    print('golden-diff threshold sweep (detect visible defects / false-alarm benign):')
    sweep = {}
    for t in (0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0):
        d = sum(1 for m, _ in vmae if m > t); fa = sum(1 for m, _ in bmae if m > t)
        sweep[t] = (d, fa)
        print('  MAE>%-5s detect %2d/%d (%3.0f%%)   FA %d/%d (%3.0f%%)' % (t, d, len(vmae), 100 * d / len(vmae), fa, len(bmae), 100 * fa / len(bmae)))
    best_zero = max((d for t, (d, fa) in sweep.items() if fa == 0), default=0)
    print('  best detection at zero benign false alarms: %d/%d' % (best_zero, len(vmae)))
    print('\nmissed by C3 invariant :', [c['name'] for c in defects if not results[c['name']]['C3_invariant']])
    print('missed by C0+C3        :', [c['name'] for c in defects if not (results[c['name']]['C3_invariant'] or results[c['name']]['C0_null'])])
    print('missed by golden>1.0   :', [c['name'] for c in defects if not results[c['name']]['mae'] > 1.0])
    print('golden>1.0 false alarms:', [c['name'] for c in benign + content if results[c['name']]['mae'] > 1.0])
    print('C3 false alarms        :', [c['name'] for c in benign + content if results[c['name']]['C3_invariant']])
    ka0, na = summary['C0 null/no-errors'][:2]
    p1 = (ka0 == 1 and summary['C0 null/no-errors'][2] == 0)
    kg, _, fg, nb, _, _ = summary['C2 golden MAE>1.0']
    overlap = max_ben[0] > min_vis[0]
    p2 = (kg >= 20 and fg >= 3 and overlap)
    kc, _, fc, _, _, _ = summary['C3 invariant suite']
    p3 = (kc >= 18 and fc == 0)
    mat = rate([c for c in defects if c['cls'] == 'material'], cd['C3 invariant suite'])[0]
    nrm = rate([c for c in defects if c['cls'] == 'normal'], cd['C3 invariant suite'])[0]
    p4 = (mat <= 4 and nrm >= 4)
    print('\nPREDICTION check: P1=%s (C0 caught %d/%d)  P2=%s (golden %d/%d, FA %d/%d, overlap=%s)  P3=%s (C3 %d/%d, FA %d)  P4=%s (material %d/6, normal %d/5)' % (
        p1, ka0, na, p2, kg, na, fg, nb, overlap, p3, kc, na, fc, p4, mat, nrm))
    ok = same and (p1 and p2 and p3 and p4)
    print('RESULT: %s defects=%d C0=%d golden>1.0=%d (FA %d/%d) C3=%d (FA %d/%d) C0+C3=%d; golden best-at-0FA %d/%d visible; predictions P1..P4=%s%s%s%s' % (
        'PASS' if ok else 'FAIL', na, ka0, kg, fg, nb, kc, fc, nb, summary['C0+C3 suite'][0], best_zero, len(vmae),
        'Y' if p1 else 'N', 'Y' if p2 else 'N', 'Y' if p3 else 'N', 'Y' if p4 else 'N'))

if __name__ == '__main__':
    main()
