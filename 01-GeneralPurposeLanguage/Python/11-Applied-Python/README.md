# 11 - Applied Python

Everything here runs **locally**: no internet access. HTTP demos use servers on `127.0.0.1`, scraping uses embedded HTML, databases are in-memory or temporary, and email is built but never sent. Third-party libraries are optional; a file prints a skip line if one is missing.

| File | Covers |
|---|---|
| [01-HTTP-Clients-And-Local-Servers](01-HTTP-Clients-And-Local-Servers.ipynb) | HTTP basics, a local `http.server`, `urllib`/`requests`/`httpx` clients, timeouts, retries with backoff, sessions, streaming, auth and secrets |
| [02-Building-REST-APIs](02-Building-REST-APIs.ipynb) | REST design, the same CRUD API in Flask and FastAPI, validation, pagination, errors, token auth, OpenAPI, testing with test clients |
| [03-Async-HTTP-And-Concurrency](03-Async-HTTP-And-Concurrency.ipynb) | `asyncio` with `aiohttp`/`httpx`, `gather`, `TaskGroup`, semaphores, timeouts, retries, cancellation, producer/consumer queues |
| [04-Web-Scraping-On-Local-HTML](04-Web-Scraping-On-Local-HTML.ipynb) | `html.parser`, BeautifulSoup, lxml XPath, CSS selectors, pagination, URL joining, robots.txt, ethics (local HTML only) |
| [05-SQLite-With-Python](05-SQLite-With-Python.ipynb) | `sqlite3`: parameterised queries, injection demo, transactions, `Row`, constraints, indexes and `EXPLAIN`, user functions, migrations, repository wrapper |
| [06-SQLAlchemy-Core-And-ORM](06-SQLAlchemy-Core-And-ORM.ipynb) | SQLAlchemy 2.0 Core and ORM, relationships, sessions, joins, lazy vs eager loading, the N+1 problem, transactions |
| [07-Data-Validation-And-Serialization](07-Data-Validation-And-Serialization.ipynb) | `json` in depth, dataclass validation, pydantic v2, CSV/TOML/YAML round-trips, JSON Schema idea, never unpickle untrusted data |
| [08-CLI-Apps-And-Configuration](08-CLI-Apps-And-Configuration.ipynb) | `argparse` subcommands, click and typer, config layering (defaults < file < env < CLI), logging, exit codes, `main(argv)` pattern |
| [09-Automation-And-Scripting](09-Automation-And-Scripting.ipynb) | batch file work with `pathlib`/`shutil`, archives, hashing, safe `subprocess`, scheduling, building (not sending) email, dry-run and idempotent scripts |
