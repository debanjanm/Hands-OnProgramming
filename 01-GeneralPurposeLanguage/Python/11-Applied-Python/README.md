# 11 - Applied Python

Everything here runs **locally**: no internet access. HTTP demos use servers on `127.0.0.1`, scraping uses embedded HTML, databases are in-memory or temporary, and email is built but never sent. Third-party libraries are optional; a file prints a skip line if one is missing.

| File | Covers |
|---|---|
| [01-HTTP-Clients-And-Local-Servers.py](01-HTTP-Clients-And-Local-Servers.py) · [notes](01-HTTP-Clients-And-Local-Servers.md) | HTTP basics, a local `http.server`, `urllib`/`requests`/`httpx` clients, timeouts, retries with backoff, sessions, streaming, auth and secrets |
| [02-Building-REST-APIs.py](02-Building-REST-APIs.py) · [notes](02-Building-REST-APIs.md) | REST design, the same CRUD API in Flask and FastAPI, validation, pagination, errors, token auth, OpenAPI, testing with test clients |
| [03-Async-HTTP-And-Concurrency.py](03-Async-HTTP-And-Concurrency.py) · [notes](03-Async-HTTP-And-Concurrency.md) | `asyncio` with `aiohttp`/`httpx`, `gather`, `TaskGroup`, semaphores, timeouts, retries, cancellation, producer/consumer queues |
| [04-Web-Scraping-On-Local-HTML.py](04-Web-Scraping-On-Local-HTML.py) · [notes](04-Web-Scraping-On-Local-HTML.md) | `html.parser`, BeautifulSoup, lxml XPath, CSS selectors, pagination, URL joining, robots.txt, ethics (local HTML only) |
| [05-SQLite-With-Python.py](05-SQLite-With-Python.py) · [notes](05-SQLite-With-Python.md) | `sqlite3`: parameterised queries, injection demo, transactions, `Row`, constraints, indexes and `EXPLAIN`, user functions, migrations, repository wrapper |
| [06-SQLAlchemy-Core-And-ORM.py](06-SQLAlchemy-Core-And-ORM.py) · [notes](06-SQLAlchemy-Core-And-ORM.md) | SQLAlchemy 2.0 Core and ORM, relationships, sessions, joins, lazy vs eager loading, the N+1 problem, transactions |
| [07-Data-Validation-And-Serialization.py](07-Data-Validation-And-Serialization.py) · [notes](07-Data-Validation-And-Serialization.md) | `json` in depth, dataclass validation, pydantic v2, CSV/TOML/YAML round-trips, JSON Schema idea, never unpickle untrusted data |
| [08-CLI-Apps-And-Configuration.py](08-CLI-Apps-And-Configuration.py) · [notes](08-CLI-Apps-And-Configuration.md) | `argparse` subcommands, click and typer, config layering (defaults < file < env < CLI), logging, exit codes, `main(argv)` pattern |
| [09-Automation-And-Scripting.py](09-Automation-And-Scripting.py) · [notes](09-Automation-And-Scripting.md) | batch file work with `pathlib`/`shutil`, archives, hashing, safe `subprocess`, scheduling, building (not sending) email, dry-run and idempotent scripts |
