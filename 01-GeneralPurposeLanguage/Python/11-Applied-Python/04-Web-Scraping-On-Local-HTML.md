# Web Scraping on Local HTML — Notes

## What this covers
Extracting data from HTML using only embedded strings and a local `127.0.0.1` server: stdlib `html.parser`, BeautifulSoup, lxml XPath, tables to dict lists, URL joining, encodings, robots.txt, pagination, JSON in script tags, dynamic pages, and the politeness/legal side.

## Key points
- `HTMLParser` (stdlib) is event-driven: override `handle_starttag` / `handle_endtag` / `handle_data`. Attributes arrive as `(name, value)` tuples — wrap in `dict()`.
- BeautifulSoup: `find()` returns the first match or `None`; `find_all()` returns a list; `select()` / `select_one()` take CSS selectors.
- `tag.get("href")` is safe for missing attributes; `tag["href"]` raises `KeyError`. `class` is a **list**.
- Navigation: `.parent`, `.parents`, `.children`, `find_next_sibling()`, `find_parent()`.
- lxml XPath: `//a/@href`, `//li[contains(@class,'sale')]`, `count(...)`. Indexes start at 1.
- A table becomes a list of dicts by zipping header cells with each row's cells — no pandas needed.
- Always resolve links with `urllib.parse.urljoin(base, link)`; never concatenate strings.
- `urllib.robotparser.RobotFileParser().parse(lines)` checks `can_fetch(agent, path)` and `crawl_delay` without any network call.
- Pagination: fetch → extract → follow "next" via `urljoin` → stop when absent, with a max-pages cap and a `seen` set.
- Many sites embed data as JSON in a `<script>` tag; `json.loads` on it beats scraping markup.

## Gotchas (the part worth revising twice)
- `soup.find("x").text` crashes with `AttributeError` when the tag is missing. Check for `None` or use `select_one` + a helper.
- `.next_sibling` is often the whitespace string `"\n"`; use `find_next_sibling("li")`.
- `.string` is `None` when a tag has more than one child; use `get_text(" ", strip=True)`.
- `HTMLParser.handle_data` also gives you `<script>` and `<style>` text — track depth to skip it.
- Network responses are **bytes**. Decoding with the wrong codec gives mojibake or `UnicodeDecodeError`; pass bytes to bs4 so it can sniff the charset.
- `urljoin("http://x/catalog", "item")` replaces `catalog` (no trailing slash means it's a file).
- `urllib` raises `HTTPError` on 4xx/5xx; `requests` does not until `raise_for_status()`.
- `urllib` may use proxy env vars even for localhost; the demo uses an empty `ProxyHandler`.
- Scraped values are strings (`"$1,299.00"`, `"N/A"`): clean, then convert, with a default.
- If the page is built by JavaScript, the data is not in the HTML you fetched — look for the JSON endpoint first, a headless browser last.
- Always `server.shutdown()` + `server_close()` for the local server; use port 0 and never print the port.

## When it matters
Whenever no clean API exists and you need structured data from pages: price trackers, research datasets, link audits. Prefer an official API or download when there is one; otherwise check Terms of Service and robots.txt, send an honest User-Agent, rate-limit, cache, and watch for personal-data rules. Scrapers break on redesigns, so keep selectors few and tests on saved HTML.

## One-line recap example
```python
from bs4 import BeautifulSoup
soup = BeautifulSoup('<ul><li class="a"><a href="/x">X</a></li></ul>', "html.parser")
print([(a.get_text(), a.get("href")) for a in soup.select("li.a a")])  # [('X', '/x')]
```
