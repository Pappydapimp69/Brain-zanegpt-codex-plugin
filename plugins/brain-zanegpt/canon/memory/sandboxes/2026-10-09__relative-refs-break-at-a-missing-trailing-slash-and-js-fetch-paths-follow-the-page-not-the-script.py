"""Prediction (before run): serving a bundle through a REAL local http.server under 5 path shapes (root /, /myrepo/, /html/123/,
/myrepo with a redirect to /myrepo/, and /myrepo WITHOUT a redirect), resolving every reference found in the HTML and in the
JS fetch() strings with urllib.parse.urljoin against the page URL: (1) a plain-relative-only bundle loads 100% at root, /myrepo/
and /html/123/; (2) the same bundle at /myrepo with NO redirect loads 0 of its refs, because ./app.js resolves to /app.js, which is
a bigger break than the absolute-path case; (3) an absolute-path ref ('/data.json') loads at root but not under any prefix;
(4) fetch('data.json') resolves against the PAGE, so moving the page one directory deeper (/myrepo/play/index.html) breaks it
while the script's own location is irrelevant; (5) a redirecting host (GitHub-Pages style) repairs the missing-slash case.
Deterministic: ephemeral loopback port, sequential requests, no timing. Stdlib only."""
import http.server, threading, re, urllib.request, urllib.error
from urllib.parse import urljoin, urlparse

FILES = {  # the shipped bundle, file path inside the archive -> content
    "index.html": '<html><script src="app.js"></script><link href="./style.css"><img src="img/logo.png"></html>',
    "app.js": "fetch('data.json'); fetch('lvl/one.json');",
    "style.css": "body{}", "img/logo.png": "PNG", "data.json": "{}", "lvl/one.json": "{}",
    "play/index.html": '<html><script src="../app.js"></script></html>',
}
ABS_FILES = dict(FILES)
ABS_FILES["index.html"] = '<html><script src="/app.js"></script><link href="/style.css"></html>'
ABS_FILES["app.js"] = "fetch('/data.json');"

def make_server(files, prefix, redirect):
    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a): pass
        def do_GET(self):
            p = self.path
            if prefix and p == prefix.rstrip("/"):
                if redirect:
                    self.send_response(301); self.send_header("Location", prefix); self.end_headers(); return
                p = prefix                      # naive host: serve index without redirect
                self.server.flat = True
            if prefix:
                if not p.startswith(prefix): self.send_response(404); self.end_headers(); return
                p = "/" + p[len(prefix):]
            key = p.lstrip("/") or "index.html"
            if key.endswith("/"): key += "index.html"
            if key in files:
                self.send_response(200); self.end_headers(); self.wfile.write(files[key].encode()); return
            self.send_response(404); self.end_headers()
    srv = http.server.HTTPServer(("127.0.0.1", 0), H); srv.flat = False
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv

class NoRedir(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
def get(url, follow):
    op = urllib.request.build_opener(*( [] if follow else [NoRedir]))
    try:
        r = op.open(url); return r.status, r.geturl(), r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, url, ""

def refs(html, js):
    return re.findall(r'(?:src|href)="([^"]+)"', html), re.findall(r"fetch\('([^']+)'\)", js)

def load(files, prefix, redirect, page, use_prefix_on_server=True):
    srv = make_server(files, prefix, redirect)
    base = "http://127.0.0.1:%d" % srv.server_address[1]
    code, final, html = get(base + page, follow=True)
    if code != 200:
        srv.shutdown(); return 0, 0, final
    # a no-redirect '/myrepo' leaves the document URL WITHOUT the slash: that is the page URL refs resolve against
    doc = base + page if not (redirect is False and page == prefix.rstrip("/")) else base + page
    if redirect: doc = final
    html_refs, _ = refs(html, "")
    ok = tot = 0
    script_refs = [urljoin(doc, r) for r in html_refs if r.endswith(".js")]
    js = ""
    for u in script_refs:
        c, _, body = get(u, True); js += body if c == 200 else ""
    _, fetch_refs = refs("", js)
    for r in html_refs + fetch_refs:
        u = urljoin(doc, r); c, _, _ = get(u, True); tot += 1; ok += (c == 200)
    srv.shutdown(); return ok, tot, doc

SHAPES = [("root", "", True, "/"), ("/myrepo/", "/myrepo/", True, "/myrepo/"), ("/html/123/", "/html/123/", True, "/html/123/"),
          ("/myrepo redirect", "/myrepo/", True, "/myrepo"), ("/myrepo no-redirect", "/myrepo/", False, "/myrepo")]
res = {}
for name, prefix, redir, page in SHAPES:
    res[("rel", name)] = load(FILES, prefix, redir, page)[:2]
    res[("abs", name)] = load(ABS_FILES, prefix, redir, page)[:2]
    print("%-22s relative %s   absolute-path %s" % (name, "%d/%d" % res[("rel", name)], "%d/%d" % res[("abs", name)]), flush=True)
deep = load(FILES, "/myrepo/", True, "/myrepo/play/index.html")[:2]
print("deeper page /myrepo/play/index.html (script ../app.js, fetch('data.json') is page-relative):", "%d/%d" % deep)
def full(k): return res[k][0] == res[k][1] and res[k][1] > 0
p1 = all(full(("rel", n)) for n in ("root", "/myrepo/", "/html/123/"))
p2 = res[("rel", "/myrepo no-redirect")][0] == 0
p3 = full(("abs", "root")) and not any(full(("abs", n)) for n in ("/myrepo/", "/html/123/"))
p4 = deep[0] < deep[1]
p5 = full(("rel", "/myrepo redirect"))
print("P1..P5:", p1, p2, p3, p4, p5)
# 6 stuck deploy (dbh/E6): the host reports "building" but serves nothing at the prefix; only a content check of the served URL sees it
class Stuck(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self): self.send_response(404); self.end_headers()
st = http.server.HTTPServer(("127.0.0.1", 0), Stuck); threading.Thread(target=st.serve_forever, daemon=True).start()
build_status = "building"                       # what the host's API would say; never changes in this scenario
code6, _, body6 = get("http://127.0.0.1:%d/myrepo/" % st.server_address[1], True); st.shutdown()
p6 = build_status == "building" and code6 == 404
print("S6 stuck deploy: status field says %r, served URL gives %d" % (build_status, code6))
# 7 propagation window (opticon/E8): a deploy reported success serves 404 for the first 3 requests, then 200
class Lag(http.server.BaseHTTPRequestHandler):
    n = 0
    def log_message(self, *a): pass
    def do_GET(self):
        Lag.n += 1
        if Lag.n <= 3: self.send_response(404); self.end_headers(); return
        self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
lg = http.server.HTTPServer(("127.0.0.1", 0), Lag); threading.Thread(target=lg.serve_forever, daemon=True).start()
url7 = "http://127.0.0.1:%d/myrepo/" % lg.server_address[1]
one_shot = get(url7, True)[0]
tries = 1
while get(url7, True)[0] != 200 and tries < 10: tries += 1
lg.shutdown()
print("S7 propagation window: first check gives %d, retrying reached 200 on check %d" % (one_shot, tries + 1))
p7 = one_shot == 404 and tries == 3
print("P6, P7:", p6, p7)
ok = p1 and p2 and p3 and p4 and p5 and p6 and p7
print("RESULT: %s plain-relative loads %s at root, %s at /myrepo/ but %s at /myrepo with no redirect and %s with redirect; absolute-path %s at root vs %s at /myrepo/; deeper page %d/%d; stuck deploy served %d while status said building; one-shot check 404 vs retry success on check %d" % (
    "PASS" if ok else "FAIL", "%d/%d" % res[("rel", "root")], "%d/%d" % res[("rel", "/myrepo/")], "%d/%d" % res[("rel", "/myrepo no-redirect")],
    "%d/%d" % res[("rel", "/myrepo redirect")], "%d/%d" % res[("abs", "root")], "%d/%d" % res[("abs", "/myrepo/")], deep[0], deep[1], code6, tries + 1))
