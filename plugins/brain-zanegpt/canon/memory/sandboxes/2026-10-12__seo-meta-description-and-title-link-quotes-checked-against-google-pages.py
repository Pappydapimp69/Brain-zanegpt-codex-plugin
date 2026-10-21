"""External-fact check of the SEO title-and-meta kernel against the real Google pages (stdlib, needs network).
Prediction (before run): the 2009 blog contains the 'we still don't use the description meta tag in our ranking' sentence verbatim;
the title-link page contains the 'critical to giving users a quick insight' sentence verbatim but does NOT contain the words
'ranking signal' (so the kernel's own 'not verified' caveat is right); the snippet page says snippets are automatically created
from page content and differ per search (the rewrite behaviour)."""
import re, html, urllib.request
def get(u):
    r = urllib.request.urlopen(urllib.request.Request("https://" + u, headers={"User-Agent": "Mozilla/5.0"}), timeout=30)
    t = r.read().decode("utf-8", "ignore")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).replace("’", "'")
blog = get("developers.google.com/search/blog/2009/09/google-does-not-use-keywords-meta-tag")
title = get("developers.google.com/search/docs/appearance/title-link")
snip = get("developers.google.com/search/docs/appearance/snippet")
q1 = "we still don't use the description meta tag in our ranking"
q2 = "critical to giving users a quick insight into the content of a result and why it's relevant to their query"
ok = {
    "blog_quote": q1 in blog,
    "title_quote": q2 in title,
    "no_ranking_signal_on_title_page": "ranking signal" not in title.lower(),
    "snippet_auto": "Snippets are automatically created from page content" in snip,
    "snippet_varies": "different snippets for different searches" in snip,
}
for k, v in ok.items(): print(k, v)
print(("RESULT: PASS" if all(ok.values()) else "RESULT: FAIL") + " " + ", ".join(f"{k}={v}" for k, v in ok.items()))
