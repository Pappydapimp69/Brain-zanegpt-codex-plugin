import subprocess, sys, os, hashlib
CODE = "import sys;print(*[hash(x)%1024 for x in ('apple','zebra',(1,'a'),42,b'bytes')])"
def run(seed):
    env = dict(os.environ, PYTHONHASHSEED=str(seed))
    return subprocess.run([sys.executable, "-c", CODE], env=env, capture_output=True, text=True).stdout.split()
a, b, a2 = run(1), run(2), run(1)
names = ['str apple','str zebra','tuple(int,str)','int 42','bytes']
for n, x, y in zip(names, a, b): print(f"{n:15} seed1={x:>5} seed2={y:>5} {'SAME' if x==y else 'DIFF'}")
print("same seed repeat identical:", a == a2)
def blake(x, k=3): return [int.from_bytes(hashlib.blake2b(f"{x}{i}".encode(), digest_size=4).digest(), "big") % 1024 for i in range(k)]
print("blake2b stable:", blake("apple") == blake("apple"))
str_diff = a[0] != b[0] and a[1] != b[1] and a[2] != b[2] and a[4] != b[4]
int_same = a[3] == b[3]
ok = str_diff and int_same and a == a2
print("RESULT: %s str/tuple/bytes hash positions differ across seeds (%s), int stable (%s), same seed reproducible (%s), blake2b stable" % ("PASS" if ok else "FAIL", str_diff, int_same, a == a2))
