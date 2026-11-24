"""The FastAPI app: routes, API-key auth and error mapping."""
import secrets

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Path, Query, Request
from fastapi.responses import JSONResponse, Response

from .models import MAX_SQLITE_INT, MIN_SQLITE_INT, Page, Product, ProductIn, ProductUpdate, StockAdjustment
from .repository import Conflict, NotFound, ProductRepository


def get_repo(request: Request) -> ProductRepository:
    """Dependency: the repository stored on the app. Tests override this."""
    return request.app.state.repo


def require_api_key(request: Request, x_api_key: str | None = Header(default=None)) -> None:
    """Dependency: reject the request unless X-API-Key matches the app's key."""
    expected = request.app.state.api_key
    if x_api_key is None or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=401, detail="invalid or missing API key")


router = APIRouter(prefix="/products", tags=["products"], dependencies=[Depends(require_api_key)])


@router.post("", response_model=Product, status_code=201)
def create_product(body: ProductIn, repo: ProductRepository = Depends(get_repo)):
    return repo.create(**body.model_dump())


@router.get("", response_model=Page)
def list_products(
    q: str | None = None,
    category: str | None = None,
    min_price: float | None = Query(default=None, ge=0, allow_inf_nan=False),
    max_price: float | None = Query(default=None, ge=0, allow_inf_nan=False),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0, le=MAX_SQLITE_INT),
    repo: ProductRepository = Depends(get_repo),
):
    items, total = repo.list(q, category, min_price, max_price, limit, offset)
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int = Path(ge=MIN_SQLITE_INT, le=MAX_SQLITE_INT), repo: ProductRepository = Depends(get_repo)):
    return repo.get(product_id)


@router.patch("/{product_id}", response_model=Product)
def update_product(body: ProductUpdate, product_id: int = Path(ge=MIN_SQLITE_INT, le=MAX_SQLITE_INT), repo: ProductRepository = Depends(get_repo)):
    # exclude_none: null means "leave alone" (so category cannot be cleared; fine for now)
    return repo.update(product_id, **body.model_dump(exclude_none=True))


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int = Path(ge=MIN_SQLITE_INT, le=MAX_SQLITE_INT), repo: ProductRepository = Depends(get_repo)):
    repo.delete(product_id)
    return Response(status_code=204)


@router.post("/{product_id}/stock", response_model=Product)
def adjust_stock(body: StockAdjustment, product_id: int = Path(ge=MIN_SQLITE_INT, le=MAX_SQLITE_INT), repo: ProductRepository = Depends(get_repo)):
    return repo.adjust_stock(product_id, body.delta)


def create_app(db_path: str = ":memory:", api_key: str = "dev-key") -> FastAPI:
    """Build an app with its own repository. Each call gives an independent app."""
    app = FastAPI(title="Inventory API", version="1.0.0")
    app.state.repo = ProductRepository(db_path)
    app.state.api_key = api_key

    @app.exception_handler(NotFound)
    async def _not_found(request: Request, exc: NotFound):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(Conflict)
    async def _conflict(request: Request, exc: Conflict):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.get("/health", tags=["meta"])
    def health():
        return {"status": "ok"}

    app.include_router(router)
    return app
