# Building REST APIs — Notes

## What this covers
REST design (resources, verbs, status codes, pagination, filtering, versioning, idempotency, error shape) and the same small CRUD API built twice — in Flask and in FastAPI — and exercised in-process with `app.test_client()` / `TestClient` (no server, no sockets). Also token auth, CORS notes, the OpenAPI schema, testing with asserts, and production notes.

## Key points
- URLs are plural nouns (`/api/v1/items/7`); the HTTP verb is the action. No verbs in URLs.
- Use precise codes: 201 + `Location` on create, 204 on delete, 401 vs 403, 404, 409, 422. Never return 200 with an error body.
- Pick one error shape (`{"error": {"code", "message", "details"}}`) and use it everywhere.
- Keep business logic in plain Python (a `Store`); the framework is a thin HTTP layer.
- Flask: you parse and validate yourself. FastAPI: type hints + pydantic validate, return 422, and generate the OpenAPI schema (`app.openapi()`).
- FastAPI `Depends` injects shared pieces (store, auth); tests swap them via `app.dependency_overrides`.
- Paginate every list (`limit`/`offset` or cursor), cap `limit`, and return `total`.
- Idempotency: a client-sent `Idempotency-Key` makes POST retries safe (first 201, replay 200, same resource).
- Version with a URL prefix (`/api/v1`); adding fields is not breaking, removing/renaming is.
- App factory (`create_app()`) gives each test a fresh app and state.

## Gotchas (the part worth revising twice)
- FastAPI's built-in errors use `{"detail": ...}`, not your custom shape, unless you add exception handlers.
- Flask `request.get_json(silent=True)` returns `None` on bad JSON — check it; query values are always strings.
- `dependency_overrides` is keyed by the original function object — keep a reference, and clear it after use.
- DELETE twice returns 204 then 404, yet is still idempotent (same end state).
- CORS is enforced by browsers only; it is not authentication, and `*` cannot be combined with credentials.
- Never `app.run(debug=True)` in production — the debugger allows remote code execution.
- In-memory state is per-process; multiple gunicorn/uvicorn workers will each have their own copy.
- Offset pagination skips or repeats rows when data changes between pages.

## When it matters
Any backend a front end, mobile app, or other service depends on. Contracts (codes, shapes, versions) are hard to change once clients exist.

## One-line recap example
```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
app = FastAPI()
@app.get("/ping")
def ping(): return {"ok": True}
print(TestClient(app).get("/ping").json())   # {'ok': True}
```
