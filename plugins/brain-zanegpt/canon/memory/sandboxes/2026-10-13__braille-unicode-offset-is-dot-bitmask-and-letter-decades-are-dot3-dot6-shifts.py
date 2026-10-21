# Verify against Python's unicodedata (real Unicode names): U+2800 + bitmask(dots) for all 256 cells,
# and the literary braille decade structure: a-j base, k-t = +dot3, u,v,x,y,z = +dots 3,6, w is the exception.
import unicodedata
bad=0
for n in range(256):
    name=unicodedata.name(chr(0x2800+n))
    dots=[] if name.endswith('BLANK') else [int(c) for c in name.split('DOTS-')[1]]
    if sum(1<<(d-1) for d in dots)!=n: bad+=1
base={'a':{1},'b':{1,2},'c':{1,4},'d':{1,4,5},'e':{1,5},'f':{1,2,4},'g':{1,2,4,5},'h':{1,2,5},'i':{2,4},'j':{2,4,5}}
def cell(dots): return chr(0x2800+sum(1<<(d-1) for d in dots))
def dots_of(ch):
    name=unicodedata.name(ch); return set(int(c) for c in name.split('DOTS-')[1])
# standard English braille letter patterns (from the published alphabet)
std={'k':{1,3},'l':{1,2,3},'m':{1,3,4},'n':{1,3,4,5},'o':{1,3,5},'p':{1,2,3,4},'q':{1,2,3,4,5},'r':{1,2,3,5},'s':{2,3,4},'t':{2,3,4,5},
     'u':{1,3,6},'v':{1,2,3,6},'x':{1,3,4,6},'y':{1,3,4,5,6},'z':{1,3,5,6},'w':{2,4,5,6}}
dec2=all(std[l]==base[b]|{3} for l,b in zip('klmnopqrst','abcdefghij'))
dec3=all(std[l]==base[b]|{3,6} for l,b in zip('uvxyz','abcde'))
w_exc=std['w']!=base['j']|{3,6}
# name-derived check: the glyph built by the formula carries exactly those dots in its Unicode name
named=all(dots_of(cell(d))==d for d in list(base.values())+list(std.values()))
six=sum(1 for n in range(64))-1   # non-blank 6-dot cells
print('cells whose name disagrees with bitmask formula:',bad,'of 256; 6-dot non-blank cells:',six)
print('decade2 (+dot3) holds',dec2,'decade3 (+dots3,6) holds',dec3,'w breaks the pattern',w_exc,'names agree',named)
print('RESULT: %s bitmask formula matched %d/256 Unicode names; k-t=+dot3 %s, u-z=+dots3,6 %s except w (%s)'%('PASS' if bad==0 and dec2 and dec3 and w_exc and named and six==63 else 'FAIL',256-bad,dec2,dec3,w_exc))
