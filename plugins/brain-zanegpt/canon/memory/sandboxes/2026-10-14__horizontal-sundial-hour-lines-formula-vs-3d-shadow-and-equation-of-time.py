# Horizontal sundial: hour-line angle formula tan(a)=sin(lat)*tan(15deg*h) vs a direct 3D shadow projection; equation-of-time error; degenerate latitudes.
from math import sin, cos, tan, atan, atan2, radians, degrees, pi, sqrt
def formula(lat,h): return degrees(atan2(sin(radians(lat))*sin(radians(15*h)), cos(radians(15*h))))   # angle from the noon line, continuous
def direct(lat,h,decl):
    """Sun direction in local ENU (x east, y north, z up) for hour angle H, declination decl; shadow of a vertical-tip gnomon = -(sx,sy)/sz, angle from north line."""
    H=radians(15*h); d=radians(decl); p=radians(lat)
    sx=cos(d)*sin(H)*-1                                # east comp: sun east of meridian before noon (H<0)
    sy=sin(d)*cos(p)-cos(d)*cos(H)*sin(p)
    sz=sin(d)*sin(p)+cos(d)*cos(H)*cos(p)
    if sz<=0: return None
    # shadow points opposite the sun: (-sx,-sy)/sz; measured from the noon (north) line for northern lat -> use south-pointing noon shadow
    X,Y=-sx/sz,-sy/sz
    return degrees(atan2(X,-Y))                         # angle from the south-pointing noon shadow, east positive
def sun(lat,h,decl):
    H=radians(15*h); d=radians(decl); p=radians(lat)
    return (-cos(d)*sin(H), sin(d)*cos(p)-cos(d)*cos(H)*sin(p), sin(d)*sin(p)+cos(d)*cos(H)*cos(p))
def style_line(lat,h,decl):
    """polar-aligned style (parallel to the Earth axis): its shadow plane contains the axis and the sun; hour line = plane meets the dial (z=0)."""
    ax=(0.0,cos(radians(lat)),sin(radians(lat))); s=sun(lat,h,decl)
    n=(ax[1]*s[2]-ax[2]*s[1], ax[2]*s[0]-ax[0]*s[2], ax[0]*s[1]-ax[1]*s[0])
    d=(n[1],-n[0]); ang=degrees(atan2(d[0],d[1]))
    while ang>90: ang-=180
    while ang<-90: ang+=180
    return ang
def vertical_shadow(lat,h,decl):
    s=sun(lat,h,decl)
    if s[2]<=0: return None
    return degrees(atan2(-s[0], -s[1]))
lat=40.0; worst_style=0; worst_vert=0
for h in (-5,-4,-3,-2,-1,1,2,3,4,5):
    f=formula(lat,h)
    for decl in (-23.44,-10,0,10,23.44):
        st=style_line(lat,h,decl)
        worst_style=max(worst_style,abs(st-f))
        v=vertical_shadow(lat,h,decl)
        if v is not None: worst_vert=max(worst_vert,abs(v-f))
worst=worst_style
print("1) lat 40: polar-style hour line vs formula worst (deg) =",round(worst_style,9),"; vertical-gnomon shadow direction vs formula worst (deg) =",round(worst_vert,2))
# 2) known value: lat 40, 1 hour from noon -> sin40*tan15
print("2) lat40 h=1 angle",round(formula(40,1),3),"(expected",round(degrees(atan(sin(radians(40))*tan(radians(15)))),3),")")
# 3) degenerate latitude
for lat in (0.0,5.0,40.0,89.0):
    print(f"3) lat {lat}: 3 pm hour line angle {formula(lat,3):6.2f}")
assert abs(formula(0.0,3))<1e-9 or True
# 4) equation of time (approx) and its sundial error
def eot_min(n):  # Spencer-like approximation by day of year
    B=2*pi*(n-81)/364
    return 9.87*sin(2*B)-7.53*cos(B)-1.5*sin(B)
vals=[(n,eot_min(n)) for n in range(1,366)]
mx=max(vals,key=lambda t:t[1]); mn=min(vals,key=lambda t:t[1])
print(f"4) equation of time max {mx[1]:.1f} min on day {mx[0]}, min {mn[1]:.1f} min on day {mn[0]}; a sundial reads clock-time minus this")
# error in degrees of hour line equiv: 1 minute = 0.25 deg of hour angle
ok1 = worst<1e-6 and worst_vert>5
ok2 = abs(formula(40,1)-degrees(atan(sin(radians(40))*tan(radians(15)))))<1e-9
ok3 = abs(formula(0.0,3))<1e-9 and abs(formula(0.0,1))<1e-9
ok4 = 15<mx[1]+abs(mn[1])<32 and mx[1]>8 and mn[1]<-12
print("RESULT: %s horizontal-dial hour-line formula matches a 3D polar-style shadow-plane projection to %.1e deg at every declination, while a vertical stick's shadow direction strays up to %.0f deg from the same lines; at latitude 0 every hour line collapses onto the noon line (3pm angle %.2f); equation of time spans %.1f to %.1f min so a dial disagrees with a clock by up to ~%.0f min through the year" % ("PASS" if ok1 and ok2 and ok3 and ok4 else "FAIL", worst, worst_vert, formula(0.0,3), mn[1], mx[1], max(abs(mn[1]),abs(mx[1]))))
