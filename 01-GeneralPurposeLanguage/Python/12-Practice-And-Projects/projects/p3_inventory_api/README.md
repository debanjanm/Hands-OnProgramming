# P3 - Inventory REST API

Build a small store-inventory web API with **FastAPI**, **pydantic** and **sqlite3**.

## What you will practise
- pydantic models and validation (bad input becomes a `422` for free)
- the repository pattern: all SQL lives in one class, the web layer never touches SQL
- FastAPI dependencies (`Depends`) and `dependency_overrides` for testing
- HTTP status codes: 201, 204, 401, 404, 409, 422
- safe SQL (`?` placeholders), a `CHECK` constraint, and an atomic stock update
- testing an API with `fastapi.testclient.TestClient`

## Milestones
- [ ] 1. `models.py`: `ProductIn`, `ProductUpdate`, `Product`
- [ ] 2. `repository.py` create/get + `app.py` `create_app`, `get_repo`, `POST /products`, `GET /products/{id}`
- [ ] 3. `PATCH` and `DELETE`
- [ ] 4. `POST /products/{id}/stock` - stock must never go below 0 (`409`)
- [ ] 5. `GET /products` with `q`, `category`, `min_price`, `max_price`, `limit`, `offset`
- [ ] 6. API-key auth on every `/products` route (`X-API-Key` header, `401` otherwise)
- [ ] 7. Check `/docs` and `/openapi.json` look right

## Public API
| Method + path | Success | Errors |
|---|---|---|
| `GET /health` | 200 `{"status": "ok"}` (no key) | |
| `POST /products` | 201 product | 409 duplicate sku, 422 bad body |
| `GET /products` | 200 `{items,total,limit,offset}` | 422 bad query (`limit` 1-100, `offset` >= 0) |
| `GET /products/{id}` | 200 product | 404 |
| `PATCH /products/{id}` | 200 product (`name,sku,price,category`; `stock` is rejected) | 404, 409, 422 |
| `DELETE /products/{id}` | 204 | 404 |
| `POST /products/{id}/stock` body `{"delta": int}` | 200 product | 404, 409 not enough stock, 422 delta = 0 |

Python: `create_app(db_path=":memory:", api_key="dev-key") -> FastAPI`, `ProductRepository(db_path)`,
exceptions `NotFound`, `Conflict`, `InsufficientStock` (a `Conflict`), dependencies `get_repo`, `require_api_key`.

## Hints
- Work milestone by milestone; run the tests often. Many fail until `create_app` works - that is normal.
- Never build SQL by gluing user text into the string. Use `?` placeholders.
- `UPDATE products SET stock = stock + ? WHERE id = ? AND stock + ? >= 0` then check `cursor.rowcount`.
- Map exceptions to status codes in `create_app` with `@app.exception_handler`.

## Run and test
From `12-Practice-And-Projects/`:
```
python3 -m pytest projects/p3_inventory_api -q               # your code in starter/
python3 -m pytest projects/p3_inventory_api -q --solutions   # the reference answer
cd projects/p3_inventory_api/reference
python3 -c "import uvicorn; uvicorn.run('inventory_api:create_app', factory=True)"   # needs uvicorn
```

## Stretch goals
- Make `category` clearable in `PATCH` (hint: `exclude_unset` instead of `exclude_none`)
- Add `GET /products/low-stock?threshold=5`
- Add a `StockMovement` history table written in the same transaction as each adjustment
- Hash API keys, or allow several keys
