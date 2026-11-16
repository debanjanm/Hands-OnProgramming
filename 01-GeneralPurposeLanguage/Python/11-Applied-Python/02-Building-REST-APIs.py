# 01. REST In One Page: Resources And Verbs
# 02. Status Codes You Actually Use
# 03. A Consistent Error Shape
# 04. The Shared Domain: A Tiny In-Memory Store
# 05. Flask: The Same CRUD API (Micro-Framework Style)
# 06. Flask: Auth Via Bearer Token
# 07. FastAPI: The Same CRUD API (Type-Driven Style)
# 08. FastAPI: Validation Errors (422) For Free
# 09. FastAPI: Path And Query Parameters
# 10. FastAPI: Dependency Injection And Overrides
# 11. One Test Script, Two Frameworks
# 12. Pagination
# 13. Filtering And Sorting
# 14. Idempotency (Safe Retries For POST)
# 15. Versioning
# 16. OpenAPI Schema
# 17. CORS Notes
# 18. Testing APIs With Asserts
# 19. Production Notes

# No server is started anywhere: Flask's app.test_client() and FastAPI's
# TestClient call the app in-process. No sockets, no internet.

import json

try:
    import flask
    from flask import Flask, jsonify, request
except ImportError:
    flask = None

try:
    from fastapi import Depends, FastAPI, Header, HTTPException, Query, Response
    from fastapi.testclient import TestClient
    from pydantic import BaseModel, Field
except ImportError:
    FastAPI = None

API_TOKEN = "demo-token"  # demo only; real apps read os.environ["API_TOKEN"]

# 01. REST In One Page: Resources And Verbs
# ----------------------------
# - REST models your API as RESOURCES (nouns) identified by URLs, acted on
#   by HTTP verbs. The URL names the thing; the verb says what to do.
# - Collection: /api/v1/items      Single item: /api/v1/items/7
# - GET    /items        list              GET    /items/7   read one
# - POST   /items        create            PUT    /items/7   replace whole
# - PATCH  /items/7      partial update    DELETE /items/7   remove
# - Plural nouns, lowercase, no verbs in the URL: /items/7, not /getItem?id=7.
# - Stateless: every request carries everything needed (auth included).
#   The server keeps no "session" between calls.
# - Responses are usually JSON with Content-Type: application/json.

print("collection URL :", "/api/v1/items")
print("single item URL:", "/api/v1/items/7")
for verb, meaning in [("GET", "read"), ("POST", "create"), ("PUT", "replace"), ("PATCH", "partial update"), ("DELETE", "remove")]:
    print(f"{verb:7}-> {meaning}")
print("# Gotcha: /api/createItem and /api/deleteItem are RPC, not REST. Let the verb do that job.")

# 02. Status Codes You Actually Use
# ----------------------------
# - 200 OK (read/update)        201 Created (+ Location header of new thing)
# - 204 No Content (delete ok)  400 Bad Request (malformed input)
# - 401 Unauthorized (no/bad credentials)   403 Forbidden (not allowed)
# - 404 Not Found               409 Conflict (duplicate / state clash)
# - 422 Unprocessable (well-formed but fails validation - FastAPI default)
# - 429 Too Many Requests       500 Server error (a bug - never intended)
# - Rule: the status code is for machines, the body for humans. Do not
#   return 200 with {"error": ...} inside - clients and monitors read codes.

# 03. A Consistent Error Shape
# ----------------------------
# - Pick ONE error body shape and use it everywhere so clients write one
#   handler. We use: {"error": {"code": "...", "message": "...", "details": [...]}}
# - "code" is a stable machine string (not_found); "message" can change.
# - Never leak stack traces or SQL in error bodies - log them server-side.
# - Standard alternative: RFC 9457 "problem details" (application/problem+json).

def err(code, message, details=None):
    body = {"error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = details
    return body

print("example error:", json.dumps(err("not_found", "item 99 does not exist")))

# 04. The Shared Domain: A Tiny In-Memory Store
# ----------------------------
# - Both frameworks below wrap the SAME business logic, which is the
#   healthy way to structure a service: framework = thin HTTP layer,
#   domain = plain Python you can test without HTTP at all.
# - In-memory dict stands in for a database. Create one Store per app so
#   tests do not leak state into each other.

class Store:
    def __init__(self):
        self.items = {}
        self.next_id = 1
        self.idem = {}  # Idempotency-Key -> item id

    def list(self, q=None, limit=10, offset=0, sort="id"):
        rows = [i for i in self.items.values() if not q or q.lower() in i["name"].lower()]
        rows.sort(key=lambda i: i[sort])
        return {"items": rows[offset:offset + limit], "total": len(rows), "limit": limit, "offset": offset}

    def create(self, data, key=None):
        if key and key in self.idem:                 # replay of an earlier POST
            return self.items[self.idem[key]], False
        item = {"id": self.next_id, **data}
        self.items[item["id"]] = item
        self.next_id += 1
        if key:
            self.idem[key] = item["id"]
        return item, True

    def get(self, item_id):
        return self.items.get(item_id)

    def replace(self, item_id, data):
        if item_id not in self.items:
            return None
        self.items[item_id] = {"id": item_id, **data}
        return self.items[item_id]

    def delete(self, item_id):
        return self.items.pop(item_id, None) is not None


s = Store()
s.create({"name": "pen", "price": 1.5})
print("plain-Python domain works without HTTP:", s.list())

# 05. Flask: The Same CRUD API (Micro-Framework Style)
# ----------------------------
# - Flask (pip install flask): decorators map URL+verb to functions.
# - You parse and validate input yourself; request.get_json(silent=True)
#   returns None (instead of raising) on bad JSON.
# - Return (body, status) or use jsonify. Headers go in a third item.
# - app.test_client() calls the app directly - no server needed.
# - An app FACTORY (create_app) gives every test a fresh app and store.

def validate_item(data):
    errors = []
    if not isinstance(data, dict):
        return [{"field": "body", "problem": "must be a JSON object"}]
    if not isinstance(data.get("name"), str) or not data["name"].strip():
        errors.append({"field": "name", "problem": "required non-empty string"})
    price = data.get("price")
    if isinstance(price, bool) or not isinstance(price, (int, float)) or price <= 0:
        errors.append({"field": "price", "problem": "required number > 0"})
    return errors


def create_flask_app():
    app = Flask(__name__)
    app.testing = True
    store = Store()

    def need_token(fn):  # section 06
        from functools import wraps

        @wraps(fn)
        def wrapper(*a, **kw):
            if request.headers.get("Authorization") != f"Bearer {API_TOKEN}":
                return jsonify(err("unauthorized", "missing or bad token")), 401
            return fn(*a, **kw)
        return wrapper

    @app.get("/api/v1/items")
    def list_items():
        try:
            limit = int(request.args.get("limit", 10))
            offset = int(request.args.get("offset", 0))
        except ValueError:
            return jsonify(err("bad_query", "limit/offset must be integers")), 422
        if not 1 <= limit <= 100 or offset < 0:
            return jsonify(err("bad_query", "limit in 1..100, offset >= 0")), 422
        return jsonify(store.list(request.args.get("q"), limit, offset, request.args.get("sort", "id")))

    @app.post("/api/v1/items")
    @need_token
    def create_item():
        data = request.get_json(silent=True)
        problems = validate_item(data)
        if problems:
            return jsonify(err("validation_error", "invalid item", problems)), 422
        item, created = store.create({"name": data["name"], "price": data["price"]},
                                     request.headers.get("Idempotency-Key"))
        resp = jsonify(item)
        resp.status_code = 201 if created else 200
        resp.headers["Location"] = f"/api/v1/items/{item['id']}"
        return resp

    @app.get("/api/v1/items/<int:item_id>")
    def get_item(item_id):
        item = store.get(item_id)
        return (jsonify(item), 200) if item else (jsonify(err("not_found", f"item {item_id} does not exist")), 404)

    @app.put("/api/v1/items/<int:item_id>")
    @need_token
    def put_item(item_id):
        data = request.get_json(silent=True)
        problems = validate_item(data)
        if problems:
            return jsonify(err("validation_error", "invalid item", problems)), 422
        item = store.replace(item_id, {"name": data["name"], "price": data["price"]})
        return (jsonify(item), 200) if item else (jsonify(err("not_found", f"item {item_id} does not exist")), 404)

    @app.delete("/api/v1/items/<int:item_id>")
    @need_token
    def delete_item(item_id):
        if store.delete(item_id):
            return "", 204
        return jsonify(err("not_found", f"item {item_id} does not exist")), 404

    @app.errorhandler(404)  # unknown URLs also use our error shape
    def not_found(_):
        return jsonify(err("not_found", "no such route")), 404

    return app


# 06. Flask: Auth Via Bearer Token
# ----------------------------
# - Simple token auth: client sends "Authorization: Bearer <token>"; the
#   server compares it. Reads stay public here, writes need the token.
# - Missing/invalid credentials -> 401. Valid but not permitted -> 403.
# - Real life: compare with hmac.compare_digest (constant time), store
#   hashed tokens, support expiry, and use HTTPS always.
# - Token comes from the environment, never from source code (topic 01).

AUTH = {"Authorization": f"Bearer {API_TOKEN}"}
if flask is None:
    print("SKIP: flask is not installed (pip install flask)")
else:
    c = create_flask_app().test_client()
    print("write without token:", c.post("/api/v1/items", json={"name": "x", "price": 1}).status_code)
    print("write with bad token:", c.post("/api/v1/items", json={"name": "x", "price": 1},
                                          headers={"Authorization": "Bearer nope"}).status_code)
    print("write with token:", c.post("/api/v1/items", json={"name": "x", "price": 1}, headers=AUTH).status_code)
    print("read without token:", c.get("/api/v1/items").status_code)
    print("unknown route:", c.get("/nope").get_json())

# 07. FastAPI: The Same CRUD API (Type-Driven Style)
# ----------------------------
# - FastAPI (pip install fastapi; server: uvicorn) builds on Starlette and
#   pydantic. Type hints ARE the validation, the docs and the schema.
# - Pydantic models describe request/response bodies; response_model
#   filters what leaves the API (e.g. hides password fields).
# - FastAPI's TestClient runs the app in-process (it uses httpx).
# - Gotcha: FastAPI's own 422/404 bodies use {"detail": ...}; to match our
#   {"error": ...} shape you register exception handlers (not done here, so
#   notice the FastAPI 404 body below is wrapped in "detail").

if FastAPI is not None:
    class ItemIn(BaseModel):
        name: str = Field(min_length=1, max_length=50)
        price: float = Field(gt=0)

    class ItemOut(ItemIn):
        id: int

    class Page(BaseModel):
        items: list[ItemOut]
        total: int
        limit: int
        offset: int

    def create_fastapi_app():
        app = FastAPI(title="Items API", version="1.0.0")
        store = Store()

        def get_store():  # dependency (section 10)
            return store

        def require_token(authorization: str | None = Header(default=None)):
            if authorization != f"Bearer {API_TOKEN}":
                raise HTTPException(status_code=401, detail=err("unauthorized", "missing or bad token")["error"])

        @app.get("/api/v1/items", response_model=Page, tags=["items"])
        def list_items(q: str | None = None,
                       limit: int = Query(10, ge=1, le=100),
                       offset: int = Query(0, ge=0),
                       sort: str = Query("id", pattern="^(id|name|price)$"),
                       st: Store = Depends(get_store)):
            return st.list(q, limit, offset, sort)

        @app.post("/api/v1/items", response_model=ItemOut, status_code=201, tags=["items"],
                  dependencies=[Depends(require_token)])
        def create_item(body: ItemIn, response: Response,
                        idempotency_key: str | None = Header(default=None),
                        st: Store = Depends(get_store)):
            item, created = st.create(body.model_dump(), idempotency_key)
            response.status_code = 201 if created else 200
            response.headers["Location"] = f"/api/v1/items/{item['id']}"
            return item

        @app.get("/api/v1/items/{item_id}", response_model=ItemOut, tags=["items"])
        def get_item(item_id: int, st: Store = Depends(get_store)):
            item = st.get(item_id)
            if not item:
                raise HTTPException(404, detail={"code": "not_found", "message": f"item {item_id} does not exist"})
            return item

        @app.put("/api/v1/items/{item_id}", response_model=ItemOut, tags=["items"],
                 dependencies=[Depends(require_token)])
        def put_item(item_id: int, body: ItemIn, st: Store = Depends(get_store)):
            item = st.replace(item_id, body.model_dump())
            if not item:
                raise HTTPException(404, detail={"code": "not_found", "message": f"item {item_id} does not exist"})
            return item

        @app.delete("/api/v1/items/{item_id}", status_code=204, tags=["items"],
                    dependencies=[Depends(require_token)])
        def delete_item(item_id: int, st: Store = Depends(get_store)):
            if not st.delete(item_id):
                raise HTTPException(404, detail={"code": "not_found", "message": f"item {item_id} does not exist"})
            return Response(status_code=204)

        app.state.get_store = get_store
        app.state.require_token = require_token
        return app

    fc = TestClient(create_fastapi_app())
    r = fc.post("/api/v1/items", json={"name": "pen", "price": 1.5}, headers=AUTH)
    print("FastAPI create:", r.status_code, r.json(), "| Location:", r.headers["location"])
    print("FastAPI read  :", fc.get("/api/v1/items/1").json())
    print("FastAPI 404   :", fc.get("/api/v1/items/99").json())
    print("write without token:", fc.post("/api/v1/items", json={"name": "x", "price": 1}).status_code)
    print("response_model hides unknown fields; ItemOut fields:", list(ItemOut.model_fields))
else:
    print("SKIP: fastapi/pydantic not installed (pip install fastapi httpx)")

# 08. FastAPI: Validation Errors (422) For Free
# ----------------------------
# - Wrong types, missing fields, constraint failures (gt=0, min_length)
#   are rejected BEFORE your function runs, with status 422 and a list of
#   problems: loc (where), msg (why), type (machine tag).
# - Pydantic v2 coerces some input ("2" -> 2.0 in lax mode); use strict
#   types when coercion would hide bugs.
# - Your handler only ever sees valid data - no defensive checks needed.

if FastAPI is not None:
    r = fc.post("/api/v1/items", json={"name": "", "price": -1}, headers=AUTH)
    print("status:", r.status_code)
    for d in r.json()["detail"]:
        print("  loc:", d["loc"], "| type:", d["type"])
    r = fc.post("/api/v1/items", json={"name": "ok"}, headers=AUTH)
    print("missing field ->", r.status_code, [d["type"] for d in r.json()["detail"]])
    r = fc.post("/api/v1/items", content="{not json", headers={**AUTH, "Content-Type": "application/json"})
    print("malformed JSON ->", r.status_code)
    print("# Gotcha: Flask has none of this built in - you write validate_item() yourself")
    print("#   (or add marshmallow / pydantic).")

# 09. FastAPI: Path And Query Parameters
# ----------------------------
# - Names in the URL template {item_id} are PATH params; other function
#   args with simple types are QUERY params (?limit=5).
# - The annotation does the parsing: item_id: int turns "7" into 7 and
#   rejects "abc" with 422 - no manual int() try/except.
# - Query(...) adds constraints (ge, le, pattern); defaults make it optional.
# - Flask equivalent: <int:item_id> converter in the route, and
#   request.args.get(...) (strings!) for the query.

if FastAPI is not None:
    print("path 'abc'      ->", fc.get("/api/v1/items/abc").status_code)
    print("limit=0         ->", fc.get("/api/v1/items", params={"limit": 0}).status_code)
    print("limit=abc       ->", fc.get("/api/v1/items", params={"limit": "abc"}).status_code)
    print("sort=bogus      ->", fc.get("/api/v1/items", params={"sort": "bogus"}).status_code)
    print("limit=5 is fine ->", fc.get("/api/v1/items", params={"limit": 5}).status_code)
if flask is not None:
    c = create_flask_app().test_client()
    print("Flask path 'abc'->", c.get("/api/v1/items/abc").status_code, "(no int converter match -> 404)")
    print("Flask limit=abc ->", c.get("/api/v1/items?limit=abc").status_code)

# 10. FastAPI: Dependency Injection And Overrides
# ----------------------------
# - Depends(fn) tells FastAPI: "call fn, pass me the result." Used for DB
#   sessions, current user, settings, pagination params, auth checks.
# - Dependencies can depend on other dependencies; FastAPI builds the tree.
# - Tests swap them with app.dependency_overrides[original] = replacement -
#   no monkeypatching, no real database or real auth.
# - Overrides are keyed by the ORIGINAL function object, so keep a handle
#   to it (here stored on app.state).
# - Remember to clear overrides afterwards.

if FastAPI is not None:
    app2 = create_fastapi_app()
    t2 = TestClient(app2)
    print("without override:", t2.post("/api/v1/items", json={"name": "a", "price": 1}).status_code)
    app2.dependency_overrides[app2.state.require_token] = lambda: None  # "auth always passes"
    print("auth overridden :", t2.post("/api/v1/items", json={"name": "a", "price": 1}).status_code)
    fake = Store()
    fake.create({"name": "seeded", "price": 9.0})
    app2.dependency_overrides[app2.state.get_store] = lambda: fake      # swap the data layer
    print("seeded store    :", [i["name"] for i in t2.get("/api/v1/items").json()["items"]])
    app2.dependency_overrides.clear()
    print("after clear     :", t2.get("/api/v1/items").json()["total"])

# 11. One Test Script, Two Frameworks
# ----------------------------
# - Because both test clients expose get/post/put/delete(json=, headers=),
#   one function can drive either app. Only the JSON accessor differs:
#   Flask's response has .get_json(), Starlette's has .json().
# - If both print identical results, the APIs behave identically.

def body_of(resp):
    return resp.get_json() if hasattr(resp, "get_json") else resp.json()


def crud_script(client):
    out = []
    r = client.post("/api/v1/items", json={"name": "pen", "price": 1.5}, headers=AUTH)
    out.append(("create", r.status_code, body_of(r)))
    r = client.get("/api/v1/items/1")
    out.append(("read", r.status_code, body_of(r)))
    r = client.put("/api/v1/items/1", json={"name": "pencil", "price": 2.0}, headers=AUTH)
    out.append(("replace", r.status_code, body_of(r)))
    r = client.get("/api/v1/items")
    out.append(("list", r.status_code, body_of(r)["total"]))
    r = client.delete("/api/v1/items/1", headers=AUTH)
    out.append(("delete", r.status_code, None))
    r = client.delete("/api/v1/items/1", headers=AUTH)
    out.append(("delete again", r.status_code, None))
    r = client.get("/api/v1/items/1")
    out.append(("read gone", r.status_code, None))
    return out


results = {}
if flask is not None:
    results["flask"] = crud_script(create_flask_app().test_client())
if FastAPI is not None:
    results["fastapi"] = crud_script(TestClient(create_fastapi_app()))
for name, steps in results.items():
    print(name, "->", [(a, b) for a, b, _ in steps])
if len(results) == 2:
    print("same status flow:", [b for _, b, _ in results["flask"]] == [b for _, b, _ in results["fastapi"]])
print("# Gotcha: DELETE twice -> second gives 404 (the item is gone) yet the END STATE is")
print("#   identical, which is why DELETE counts as idempotent.")

# 12. Pagination
# ----------------------------
# - Never return an unbounded list. Two common styles:
#   * offset/limit (?limit=10&offset=20): simple, can skip/duplicate rows
#     when data changes between pages, and gets slow for big offsets.
#   * cursor/keyset (?after=<last id>): stable and fast; slightly harder.
# - Always return the metadata (total, limit, offset or next cursor) and
#   cap limit server-side (le=100) so nobody asks for a million rows.

def seed(client, n=7):
    for i in range(n):
        client.post("/api/v1/items", json={"name": f"item-{i}", "price": i + 1}, headers=AUTH)


if FastAPI is not None:
    pc = TestClient(create_fastapi_app())
    seed(pc)
    page = pc.get("/api/v1/items", params={"limit": 3, "offset": 3}).json()
    print("page 2:", [i["name"] for i in page["items"]], "| total:", page["total"])
    print("last page:", [i["name"] for i in pc.get("/api/v1/items", params={"limit": 3, "offset": 6}).json()["items"]])
    print("past the end:", pc.get("/api/v1/items", params={"offset": 99}).json()["items"])
    print("limit over cap:", pc.get("/api/v1/items", params={"limit": 1000}).status_code)

# 13. Filtering And Sorting
# ----------------------------
# - Filters are query parameters on the collection (?q=item-1&sort=price),
#   not new URLs. Whitelist sortable fields - never sort by a raw
#   user-supplied attribute name.
# - Keep the semantics boring and documented: what does q match, is it
#   case-sensitive, what is the default order?

if FastAPI is not None:
    print("q=item-1:", [i["name"] for i in pc.get("/api/v1/items", params={"q": "item-1"}).json()["items"]])
    print("sort=price (first 3):", [i["price"] for i in pc.get("/api/v1/items", params={"sort": "price", "limit": 3}).json()["items"]])
if flask is not None:
    fl = create_flask_app().test_client()
    seed(fl)
    print("Flask q=ITEM-2 (case-insensitive):", [i["name"] for i in fl.get("/api/v1/items?q=ITEM-2").get_json()["items"]])

# 14. Idempotency (Safe Retries For POST)
# ----------------------------
# - The network can drop the RESPONSE after the server already created the
#   thing. A client that retries a plain POST makes a duplicate (a double
#   charge in a payments API!).
# - Fix: client sends a unique Idempotency-Key header per logical action;
#   the server remembers key -> result and replays it instead of re-doing.
# - First call -> 201 Created; replay -> 200 with the SAME resource.
# - GET, PUT, DELETE are idempotent by definition; POST and PATCH are not.

def idem_demo(client, label):
    h = {**AUTH, "Idempotency-Key": "order-42"}
    a = client.post("/api/v1/items", json={"name": "once", "price": 5}, headers=h)
    b = client.post("/api/v1/items", json={"name": "once", "price": 5}, headers=h)
    total = body_of(client.get("/api/v1/items"))["total"]
    print(f"{label}: first={a.status_code} replay={b.status_code} same id={body_of(a)['id'] == body_of(b)['id']} total={total}")


if flask is not None:
    idem_demo(create_flask_app().test_client(), "flask")
if FastAPI is not None:
    idem_demo(TestClient(create_fastapi_app()), "fastapi")
print("# Gotcha: real servers expire keys and compare the request body, rejecting")
print("#   the same key with a DIFFERENT payload (usually 409/422).")

# 15. Versioning
# ----------------------------
# - Once clients exist you cannot change responses freely. Version so you can.
# - Common styles: URL prefix (/api/v1/...) - simplest and most visible;
#   header (Accept: application/vnd.app.v2+json) - cleaner URLs, harder to
#   test in a browser; query (?version=2) - discouraged.
# - Adding optional fields is NOT breaking. Removing/renaming fields or
#   changing meaning IS breaking -> new version.
# - Run old and new versions side by side, announce deprecation, then retire.
# - In FastAPI use APIRouter(prefix="/api/v1"); in Flask use Blueprint(url_prefix=...).

if FastAPI is not None:
    print("v1 exists:", fc.get("/api/v1/items").status_code, "| v2 not yet:", fc.get("/api/v2/items").status_code)

# 16. OpenAPI Schema
# ----------------------------
# - FastAPI generates an OpenAPI 3 document from your routes and types:
#   app.openapi() returns it as a dict. The server also exposes /docs
#   (Swagger UI) and /redoc and /openapi.json.
# - Clients, SDK generators and API gateways consume this schema.
# - Flask has no built-in schema: add flask-smorest, apispec or
#   flask-openapi3 if you want one.

if FastAPI is not None:
    spec = create_fastapi_app().openapi()
    print("top-level keys:", sorted(spec))
    print("openapi version:", spec["openapi"], "| title:", spec["info"]["title"])
    print("paths:", sorted(spec["paths"]))
    print("methods on collection:", sorted(spec["paths"]["/api/v1/items"]))
    print("schemas:", sorted(spec["components"]["schemas"]))
    print("ItemIn required:", spec["components"]["schemas"]["ItemIn"]["required"])
    print("POST responses:", sorted(spec["paths"]["/api/v1/items"]["post"]["responses"]))

# 17. CORS Notes
# ----------------------------
# - CORS (Cross-Origin Resource Sharing) is a BROWSER rule: JavaScript on
#   https://app.example may not read responses from https://api.example
#   unless the API says so with Access-Control-Allow-Origin headers.
# - curl, Python clients and server-to-server calls ignore CORS entirely.
# - "Preflight": for non-simple requests (JSON POST, custom headers) the
#   browser first sends OPTIONS and checks Allow-* headers.
# - FastAPI: app.add_middleware(CORSMiddleware, allow_origins=[...]).
#   Flask: the flask-cors package.
# - Gotchas: allow_origins=["*"] cannot be combined with credentials
#   (cookies); never reflect any origin blindly; CORS is not authentication.

# 18. Testing APIs With Asserts
# ----------------------------
# - Test the CONTRACT: status code, body shape, headers, and the sad paths
#   (401, 404, 422) - not only the happy path.
# - Fresh app (factory) per test = no shared state = order-independent tests.
# - In real projects use pytest; here plain asserts show the idea.
# - Compare with ==, not "is"; assert on specific fields, not whole giant
#   dicts that break whenever you add a field.

def contract_tests(client):
    r = client.post("/api/v1/items", json={"name": "a", "price": 2}, headers=AUTH)
    assert r.status_code == 201 and body_of(r)["id"] == 1
    assert r.headers["Location"] == "/api/v1/items/1"
    assert client.post("/api/v1/items", json={"name": "a", "price": 2}).status_code == 401
    assert client.post("/api/v1/items", json={"name": "a", "price": 0}, headers=AUTH).status_code == 422
    assert client.get("/api/v1/items/42").status_code == 404
    assert client.delete("/api/v1/items/1", headers=AUTH).status_code == 204
    assert body_of(client.get("/api/v1/items"))["total"] == 0
    return "passed"


if flask is not None:
    print("flask contract tests:", contract_tests(create_flask_app().test_client()))
if FastAPI is not None:
    print("fastapi contract tests:", contract_tests(TestClient(create_fastapi_app())))

# 19. Production Notes
# ----------------------------
# - Never ship app.run(debug=True): Flask's debugger allows REMOTE CODE
#   EXECUTION. app.run() / "flask run" is a dev server only.
# - Flask in production: gunicorn -w 4 "module:create_app()" behind nginx.
# - FastAPI in production: uvicorn module:app (or gunicorn -k
#   uvicorn.workers.UvicornWorker), reverse proxy in front, TLS terminated there.
# - Config and secrets from environment variables; separate dev/prod settings.
# - Add: request logging with a request id, rate limiting (429), body-size
#   limits, timeouts, health endpoint (/healthz), graceful shutdown.
# - Do not return raw exception text; log it and send the generic error shape.
# - Real storage: a database with transactions; the in-memory Store is
#   per-process, so multiple workers would each see different data.
# - Mutating a shared dict from many threads/workers needs real locking;
#   another reason to use a proper database.

print("production checklist items:", ["no debug=True", "gunicorn/uvicorn", "env secrets", "rate limits", "health check"])
