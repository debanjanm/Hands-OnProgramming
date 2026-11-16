# 01. HTMLParser Basics: Collect Links
# 02. HTMLParser: Text Without script/style
# 03. HTMLParser: Table -> List of Dicts
# 04. BeautifulSoup: find and find_all
# 05. BeautifulSoup: CSS Selectors (select / select_one)
# 06. Attributes and get_text
# 07. Navigation: Parents, Children, Siblings
# 08. lxml and XPath
# 09. Table -> List of Dicts with BeautifulSoup
# 10. Relative URLs with urllib.parse
# 11. Encoding Gotchas
# 12. robots.txt with urllib.robotparser
# 13. A Local Server to Scrape (127.0.0.1, port 0)
# 14. Pagination Loop
# 15. JSON Inside a <script> Tag
# 16. Dynamic JavaScript Pages
# 17. Politeness: Delays, Headers, Caching
# 18. Legal, Ethics and When to Use an API
# 19. Defensive Parsing: Missing Elements
#
# LOCAL ONLY: every page here is an embedded string or is served by a
# stdlib server bound to 127.0.0.1 on a random free port. Nothing touches
# the internet.

import json
import threading
import urllib.error
import urllib.request
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import robotparser
from urllib.parse import urljoin, urlparse, parse_qs

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    from lxml import html as lxml_html
except ImportError:
    lxml_html = None

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <title>Tiny Shop</title>
  <style>.hidden { display: none }</style>
  <script>var tracking = "ignore me";</script>
</head>
<body>
  <h1 id="top">Tiny Shop</h1>
  <p class="intro">Welcome to the <b>demo</b> shop. <a href="/about">About</a></p>
  <ul id="menu">
    <li class="item"><a href="/products/1" class="link">Pen</a></li>
    <li class="item sale"><a href="/products/2" class="link">Notebook</a></li>
    <li class="item"><a href="../help/faq.html">FAQ</a></li>
    <li class="item"><a href="https://example.org/ext" rel="nofollow">External</a></li>
  </ul>
  <table id="prices">
    <thead><tr><th>Name</th><th>Price</th><th>Stock</th></tr></thead>
    <tbody>
      <tr><td>Pen</td><td>1.50</td><td>120</td></tr>
      <tr><td>Notebook</td><td>3.25</td><td>0</td></tr>
      <tr><td>Stapler</td><td>7.00</td><td>15</td></tr>
    </tbody>
  </table>
</body>
</html>"""


# 01. HTMLParser Basics: Collect Links
# ------------------------------------
# - html.parser.HTMLParser is in the standard library: no install needed.
# - You subclass it and override handle_starttag / handle_endtag /
#   handle_data. The parser CALLS YOU as it walks the text (event style).
# - attrs arrive as a list of (name, value) tuples, so wrap in dict().
# - Good for small, simple jobs. For anything tree-shaped, use bs4/lxml.



class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attrs = dict(attrs)
            if "href" in attrs:
                self.links.append(attrs["href"])


collector = LinkCollector()
collector.feed(PAGE)
print("links found:", collector.links)
print("# Gotcha: attribute names are lower-cased for you; a value-less attribute has value None.")

# 02. HTMLParser: Text Without script/style
# ------------------------------------
# - handle_data gets ALL text, including the contents of <script> and
#   <style>. You usually do not want that, so track where you are.
# - Parser methods are called in document order, so a small "state"
#   attribute is the usual trick.



class TextExtractor(HTMLParser):
    SKIP = {"script", "style"}

    def __init__(self):
        super().__init__()
        self.skip_depth = 0
        self.chunks = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self.skip_depth -= 1

    def handle_data(self, data):
        if not self.skip_depth and data.strip():
            self.chunks.append(data.strip())


extractor = TextExtractor()
extractor.feed(PAGE)
print("text chunks:", extractor.chunks[:6], "...")
print("script text leaked in?", any("tracking" in c for c in extractor.chunks))

# 03. HTMLParser: Table -> List of Dicts
# ------------------------------------
# - Scraping a table by hand with events: remember the current row and
#   cell, append when the tag closes.
# - Header row gives the dict keys; each body row becomes one dict.
# - Values are always STRINGS - convert types yourself afterwards.



class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self._row = None
        self._cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._row = []
        elif tag in ("td", "th"):
            self._cell = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None:
            self._row.append("".join(self._cell).strip())
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


tp = TableParser()
tp.feed(PAGE)
header, *body = tp.rows
records = [dict(zip(header, row)) for row in body]
print("header:", header)
for rec in records:
    print(rec)
total = sum(float(r["Price"]) * int(r["Stock"]) for r in records)
print("stock value (after converting strings):", total)

# 04. BeautifulSoup: find and find_all
# ------------------------------------
# - bs4 builds a tree you can search. 'html.parser' is the built-in
#   backend (no extra install); 'lxml' is faster if installed.
# - find() returns the FIRST match or None; find_all() returns a list
#   (possibly empty).
# - Filter by tag name, attributes (class_ has a trailing underscore
#   because 'class' is a Python keyword), or a function.


if BeautifulSoup is None:
    print("beautifulsoup4 not installed: skipping sections 04-07 and 09 (pip install beautifulsoup4)")
    soup = None
else:
    soup = BeautifulSoup(PAGE, "html.parser")
    print("title:", soup.title.string)
    print("first h1:", soup.find("h1").get_text())
    print("all li class lists:", [li["class"] for li in soup.find_all("li")])
    print("li with class 'sale':", [li.get_text(strip=True) for li in soup.find_all("li", class_="sale")])
    print("by id:", soup.find(id="menu").name)
    print("find missing ->", soup.find("video"))
    print("limit=2:", [a.get_text() for a in soup.find_all("a", limit=2)])
    print("by function:", [a.get_text() for a in soup.find_all(lambda t: t.name == "a" and t.has_attr("rel"))])
    print("# Gotcha: soup.find('x').text on a missing tag raises AttributeError (None has no .text).")

# 05. BeautifulSoup: CSS Selectors (select / select_one)
# ------------------------------------
# - select() takes a CSS selector and returns a list; select_one()
#   returns the first match or None.
# - Selectors you already know from the browser dev tools work:
#   tag, .class, #id, parent > child, ancestor descendant, [attr],
#   [attr^=prefix], :nth-of-type().
# - Often shorter and clearer than chained find() calls.


if soup is not None:
    print("ul#menu > li.item a.link:", [a.get_text() for a in soup.select("ul#menu > li.item a.link")])
    print("a[href^='/products']:", [a["href"] for a in soup.select("a[href^='/products']")])
    print("a[href^='https']:", [a["href"] for a in soup.select("a[href^='https']")])
    print("li.sale:", soup.select_one("li.sale").get_text(strip=True))
    print("second li:", soup.select_one("li:nth-of-type(2)").get_text(strip=True))
    print("table rows in tbody:", len(soup.select("table#prices tbody tr")))
    print("select_one miss ->", soup.select_one("div.nothing"))

# 06. Attributes and get_text
# ------------------------------------
# - tag["href"] raises KeyError if absent; tag.get("href") returns None
#   (or a default). Prefer .get() on scraped data.
# - class is a MULTI-VALUED attribute: you get a LIST, not a string.
# - get_text(strip=True) joins text; separator=" " keeps words apart.
# - tag.string is None when a tag has more than one child.


if soup is not None:
    link = soup.select_one("a.link")
    print("attrs dict:", link.attrs)
    print("class value type:", type(link["class"]).__name__)
    print("get('missing'):", link.get("missing"), "| with default:", link.get("missing", "n/a"))
    intro = soup.select_one("p.intro")
    print("get_text():", repr(intro.get_text()))
    print("get_text(' ', strip=True):", repr(intro.get_text(" ", strip=True)))
    print(".string of <p> with children:", intro.string)
    print(".string of <b>:", intro.b.string)

# 07. Navigation: Parents, Children, Siblings
# ------------------------------------
# - From any tag you can walk the tree: .parent, .parents,
#   .children / .contents, .next_sibling / .previous_sibling and the
#   *_siblings generators, .find_next / .find_parent.
# - Gotcha: whitespace between tags is a text node, so
#   .next_sibling is often "\n". Use find_next_sibling() to skip it.


if soup is not None:
    second = soup.select("li.item")[1]
    print("parent tag:", second.parent.name, "id =", second.parent["id"])
    print("ancestor names:", [p.name for p in second.parents])
    print("children count (tags only):", len(list(second.children)))
    print("next_sibling repr:", repr(second.next_sibling))
    print("find_next_sibling:", second.find_next_sibling("li").get_text(strip=True))
    print("previous li:", second.find_previous_sibling("li").get_text(strip=True))
    print("all following siblings:", [s.get_text(strip=True) for s in second.find_next_siblings("li")])
    print("closest ul via find_parent:", second.find_parent("ul")["id"])
    th = soup.find("th", string="Price")
    print("label -> value trick:", th.find_next("td").get_text())

# 08. lxml and XPath
# ------------------------------------
# - lxml is fast and supports XPath, a query language for trees.
# - Key XPath pieces: //tag (anywhere), /tag (child), [@attr='v'],
#   [1] (1-based!), text(), @attr, contains(), starts-with().
# - Handy for "the td after the th that says Price" style queries.


if lxml_html is None:
    print("lxml not installed: skipping this section (pip install lxml)")
else:
    tree = lxml_html.fromstring(PAGE)
    print("all hrefs:", tree.xpath("//a/@href"))
    print("sale item text:", tree.xpath("//li[contains(@class,'sale')]/a/text()"))
    print("first product link:", tree.xpath("(//a[starts-with(@href,'/products')])[1]/@href"))
    print("price cells:", tree.xpath("//table[@id='prices']//tr/td[2]/text()"))
    print("count of rows:", tree.xpath("count(//tbody/tr)"))
    print("xpath() returns a", type(tree.xpath("//h1")).__name__, "of elements, strings or numbers")
    print("# Gotcha: XPath indexes start at 1, not 0.")

# 09. Table -> List of Dicts with BeautifulSoup
# ------------------------------------
# - No pandas needed for small tables: read the header cells, then zip
#   them with each row's cells.
# - Write a tiny reusable function; scraping code is full of this shape.



def table_to_dicts(table):
    heads = [th.get_text(strip=True) for th in table.select("thead th")]
    out = []
    for tr in table.select("tbody tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all("td")]
        out.append(dict(zip(heads, cells)))
    return out


if soup is not None:
    rows = table_to_dicts(soup.find("table", id="prices"))
    print(rows)
    in_stock = [r["Name"] for r in rows if int(r["Stock"]) > 0]
    print("in stock:", in_stock)
    print("# Gotcha: colspan/rowspan break the zip trick; handle them explicitly if present.")

# 10. Relative URLs with urllib.parse
# ------------------------------------
# - Links are often relative ('/a', '../b', '?page=2'). Never glue
#   strings; use urljoin(base, link).
# - urlparse / parse_qs split a URL into parts for filtering or
#   de-duplicating.
# - Gotcha: base URL without a trailing slash treats the last segment
#   as a FILE, so it is replaced.


base = "http://shop.test/catalog/list/index.html"
for link in ["/about", "../help/faq.html", "item?id=7", "?page=2", "//cdn.test/x.js", "https://example.org/ext", "#top"]:
    print(f"urljoin(base, {link!r:28}) ->", urljoin(base, link))
print("no slash on dir:", urljoin("http://shop.test/catalog", "item"), "vs", urljoin("http://shop.test/catalog/", "item"))
parts = urlparse("http://shop.test/search?q=pen&page=2#results")
print("scheme/host/path:", parts.scheme, parts.netloc, parts.path)
print("query dict:", parse_qs(parts.query), "| fragment:", parts.fragment)

# 11. Encoding Gotchas
# ------------------------------------
# - Network gives BYTES. Decode with the right charset: the HTTP
#   Content-Type header, then <meta charset>, then a guess.
# - Decoding with the wrong codec gives mojibake (garbled text) or
#   UnicodeDecodeError.
# - bs4 accepts bytes and sniffs the encoding itself (original_encoding).
# - HTML entities (&amp; &eacute; &#8364;) are decoded by the parsers;
#   html.unescape does it for stray strings.


import html as html_lib

raw = "<p>café €5 &amp; more</p>".encode("utf-8")
print("utf-8 bytes:", raw)
print("decoded as latin-1 (wrong):", raw.decode("latin-1"))
print("decoded as utf-8 (right):", raw.decode("utf-8"))
try:
    "café".encode("latin-1").decode("utf-8")
except UnicodeDecodeError as exc:
    print("latin-1 bytes read as utf-8 ->", type(exc).__name__)
print("errors='replace':", "café".encode("latin-1").decode("utf-8", errors="replace"))
print("html.unescape:", html_lib.unescape("Tom &amp; Jerry &lt;3 &eacute; &#8364;"))
if BeautifulSoup is not None:
    meta_page = '<meta charset="iso-8859-1"><p>café</p>'.encode("iso-8859-1")
    s2 = BeautifulSoup(meta_page, "html.parser")
    print("bs4 from bytes:", s2.p.get_text(), "| detected:", s2.original_encoding)
print("# Tip: pass response BYTES to bs4 and let it sniff, or decode using the header charset yourself.")

# 12. robots.txt with urllib.robotparser
# ------------------------------------
# - robots.txt tells crawlers what the site owner asks them to avoid.
#   It is a request, not security - but respecting it is basic manners
#   and often a legal/ToS expectation.
# - RobotFileParser.parse() takes a list of lines, so we can test with a
#   string and never touch the network (read() would fetch a URL).


ROBOTS = """User-agent: *
Disallow: /private/
Disallow: /cart
Crawl-delay: 2
Allow: /

User-agent: BadBot
Disallow: /
"""
rp = robotparser.RobotFileParser()
rp.parse(ROBOTS.splitlines())
for agent, path in [("MyBot", "/products/1"), ("MyBot", "/private/data"), ("MyBot", "/cart"), ("BadBot", "/products/1")]:
    print(f"can_fetch({agent!r}, {path!r}) ->", rp.can_fetch(agent, path))
print("crawl_delay for MyBot:", rp.crawl_delay("MyBot"))
print("# Gotcha: parse() does not fetch anything; in real code you call set_url(...) then read(), and decide what to do if robots.txt itself 404s.")

# 13. A Local Server to Scrape (127.0.0.1, port 0)
# ------------------------------------
# - http.server + a thread gives us a safe practice website.
# - Port 0 means "OS, pick a free port" - we read it back from
#   server.server_address, and never print it (output stays stable).
# - We ALWAYS shut down: server.shutdown() then server_close().
# - urllib may honour proxy env vars even for 127.0.0.1, so we build an
#   opener with an empty ProxyHandler to stay purely local.


ITEMS = [f"item-{n:02d}" for n in range(1, 8)]
PER_PAGE = 3
REQUEST_LOG = []


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # keep stderr silent
        pass

    def _send(self, status, body, ctype="text/html; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        REQUEST_LOG.append(parsed.path + ("?" + parsed.query if parsed.query else ""))
        if parsed.path == "/robots.txt":
            self._send(200, "User-agent: *\nDisallow: /secret\n", "text/plain")
        elif parsed.path == "/items":
            page = int(parse_qs(parsed.query).get("page", ["1"])[0])
            start = (page - 1) * PER_PAGE
            chunk = ITEMS[start:start + PER_PAGE]
            nxt = f'<a class="next" href="/items?page={page + 1}">Next</a>' if start + PER_PAGE < len(ITEMS) else ""
            lis = "".join(f'<li class="it"><a href="/item/{i}">{i}</a></li>' for i in chunk)
            self._send(200, f"<html><body><h1>Page {page}</h1><ul>{lis}</ul>{nxt}</body></html>")
        elif parsed.path == "/data":
            doc = {"products": [{"sku": "A1", "price": 9.5}, {"sku": "B2", "price": 12.0}], "ok": True}
            self._send(200, "<html><head><title>Embedded</title></head><body><script id=\"__DATA__\" type=\"application/json\">"
                       + json.dumps(doc) + "</script><div id=\"app\"></div></body></html>")
        elif parsed.path == "/spa":
            self._send(200, '<html><body><div id="app"></div><script>render()</script></body></html>')
        else:
            self._send(404, "<html><body>Not found</body></html>")


server = HTTPServer(("127.0.0.1", 0), Handler)
port = server.server_address[1]
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
BASE = f"http://127.0.0.1:{port}"
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def fetch(path, user_agent="LearningBot/1.0 (local demo)"):
    req = urllib.request.Request(urljoin(BASE, path), headers={"User-Agent": user_agent})
    with opener.open(req, timeout=5) as resp:
        return resp.status, resp.headers.get_content_charset(), resp.read()


try:
    status, charset, body = fetch("/items")
    print("status:", status, "| charset from header:", charset, "| bytes:", len(body))
    te = TextExtractor()
    te.feed(body.decode(charset))
    print("text via HTMLParser:", te.chunks[:2])
    try:
        fetch("/nope")
    except urllib.error.HTTPError as exc:
        print("404 raises HTTPError, code =", exc.code)
    print("# Gotcha: urllib raises HTTPError for 4xx/5xx; requests would not (until raise_for_status).")

    # 14. Pagination Loop
    # ------------------------------------
    # - Pattern: fetch page, extract items, find the 'next' link, repeat
    #   until there is none.
    # - Always resolve next with urljoin, add a MAX_PAGES safety cap, and
    #   keep a 'seen' set so a link loop cannot run forever.


    class ItemPage(HTMLParser):
        def __init__(self):
            super().__init__()
            self.items, self.next_href = [], None
            self._in_li = False

        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            if tag == "li" and a.get("class") == "it":
                self._in_li = True
            elif tag == "a" and self._in_li:
                self.items.append(a["href"])
            elif tag == "a" and a.get("class") == "next":
                self.next_href = a["href"]

        def handle_endtag(self, tag):
            if tag == "li":
                self._in_li = False

    url, seen, collected, MAX_PAGES = "/items", set(), [], 10
    while url and url not in seen and len(seen) < MAX_PAGES:
        seen.add(url)
        _, charset, body = fetch(url)
        page = ItemPage()
        page.feed(body.decode(charset or "utf-8"))
        collected.extend(page.items)
        print("fetched", url, "->", len(page.items), "items")
        url = urljoin(url, page.next_href) if page.next_href else None
    print("total items:", len(collected), "| first/last:", collected[0], collected[-1])

    # 15. JSON Inside a <script> Tag
    # ------------------------------------
    # - Modern sites often embed their data as JSON in a <script> tag
    #   (type="application/json", __NEXT_DATA__, ld+json ...).
    # - That is easier and more reliable than scraping the rendered
    #   markup: find the tag, json.loads its text.
    # - Gotcha: bs4 .string works for script contents with html.parser;
    #   with other parsers use .get_text() or .text.


    _, charset, body = fetch("/data")
    text = body.decode(charset or "utf-8")
    if BeautifulSoup is not None:
        data = json.loads(BeautifulSoup(text, "html.parser").find("script", id="__DATA__").string)
    else:
        start = text.index('type="application/json">') + len('type="application/json">')
        data = json.loads(text[start:text.index("</script>", start)])
        print("(bs4 missing: sliced the string by hand)")
    print("parsed:", data)
    print("prices:", {p["sku"]: p["price"] for p in data["products"]})

    # 16. Dynamic JavaScript Pages
    # ------------------------------------
    # - requests/urllib only get the HTML the server sent. If the page
    #   fills itself in with JavaScript, the data is NOT in that HTML.
    # - Options: (1) find the JSON/XHR endpoint in the browser's Network
    #   tab and call it directly; (2) look for embedded JSON (section
    #   15); (3) last resort, drive a real browser (Playwright/Selenium).


    _, charset, body = fetch("/spa")
    print("served HTML:", body.decode(charset))
    if BeautifulSoup is not None:
        app = BeautifulSoup(body, "html.parser").find(id="app")
        print("div#app children:", len(app.contents), "(empty: JS would fill it in a browser)")

    # 17. Politeness: Delays, Headers, Caching
    # ------------------------------------
    # - Identify yourself with a clear User-Agent (and contact if
    #   possible). Never fake being a person.
    # - Rate-limit: sleep between requests (honour Crawl-delay); use
    #   backoff on 429/503; cap concurrency.
    # - Cache pages you already fetched (a dict or files) so you do not
    #   re-download while debugging your parser.
    # - Here the "delay" is 0 so the demo stays fast; the structure is
    #   what matters.


    cache = {}
    DELAY = 0  # real crawls: rp.crawl_delay(agent) or at least 1 second

    def polite_get(path):
        if path in cache:
            return cache[path], True
        import time
        time.sleep(DELAY)
        cache[path] = fetch(path)[2]
        return cache[path], False

    before = len(REQUEST_LOG)
    for _ in range(3):
        _, hit = polite_get("/items?page=2")
        print("cache hit:", hit)
    print("server saw", len(REQUEST_LOG) - before, "request for 3 calls")
    print("allowed by local robots?", rp.can_fetch("LearningBot", "/items"))
    local_rp = robotparser.RobotFileParser()
    local_rp.parse(fetch("/robots.txt")[2].decode().splitlines())
    print("/secret allowed?", local_rp.can_fetch("LearningBot", "/secret"), "| /items allowed?", local_rp.can_fetch("LearningBot", "/items"))
finally:
    server.shutdown()
    server.server_close()
    thread.join()
print("server stopped:", not thread.is_alive())

# 18. Legal, Ethics and When to Use an API
# ------------------------------------
# - Check, in order: is there an official API or data download? (best:
#   stable, allowed, structured). Then: Terms of Service, robots.txt,
#   copyright and database rights, personal-data/privacy law (GDPR etc.).
# - Public does not mean free to reuse. Logging in or bypassing
#   technical barriers (CAPTCHAs, paywalls) is a different risk level.
# - Be gentle: low rate, off-peak, cache, stop if asked. You can get
#   your IP blocked or worse.
# - Scraped HTML is fragile: a redesign breaks selectors. APIs have
#   versions and documented fields.
# - This is general education, not legal advice - ask when unsure.


checklist = [
    "official API or dataset exists?  -> use it",
    "terms of service allow it?       -> read them",
    "robots.txt allows the path?      -> respect it",
    "personal data involved?          -> privacy law applies",
    "rate low, User-Agent honest?     -> be a good guest",
]
for n, line in enumerate(checklist, 1):
    print(f"  {n}. {line}")

# 19. Defensive Parsing: Missing Elements
# ------------------------------------
# - Real pages are messy: missing tags, empty cells, odd prices
#   ("N/A", "$1,299.00"). Code must not crash on the first oddity.
# - Pattern: small helper that returns a default, plus explicit
#   cleaning before converting types.
# - Broken HTML (unclosed tags) is tolerated by html.parser/bs4/lxml,
#   but each may build a slightly DIFFERENT tree - test your parser.


MESSY = '<div class="card"><h2>Lamp</h2><span class="p">$1,299.00</span></div><div class="card"><h2>Mystery</h2></div><div class="card"><h2>Fan<span class="p">N/A'


def to_price(text):
    cleaned = (text or "").replace("$", "").replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


if BeautifulSoup is not None:
    for card in BeautifulSoup(MESSY, "html.parser").select("div.card"):
        price_tag = card.select_one(".p")
        name = card.h2.get_text(strip=True)
        print(f"{name!r:12} price tag found: {price_tag is not None!s:5} ->", to_price(price_tag.get_text() if price_tag else None))
else:
    print("bs4 missing: skipped")
print("to_price tests:", to_price("$1,299.00"), to_price("N/A"), to_price(None))
