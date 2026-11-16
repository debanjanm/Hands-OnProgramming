"""The FastAPI app: routes, API-key auth and error mapping."""
from fastapi import APIRouter, Depends, FastAPI, Header, Query, Request

from .models import Page, Product, ProductIn, ProductUpdate, StockAdjustment
from .repository import ProductRepository


def get_repo(request: Request) -> ProductRepository:
    """Dependency: return the repository stored on request.app.state.repo. Tests override this."""
    # TODO (milestone 2)
    raise NotImplementedError


def require_api_key(request: Request, x_api_key: str | None = Header(default=None)) -> None:
    """Dependency: raise HTTPException(401) unless X-API-Key equals request.app.state.api_key.

    Hint: secrets.compare_digest for the comparison.
    """
    # TODO (milestone 6)
    raise NotImplementedError


router = APIRouter(prefix="/products", tags=["products"], dependencies=[Depends(require_api_key)])


@router.post("", response_model=Product, status_code=201)
def create_product(body: ProductIn, repo: ProductRepository = Depends(get_repo)):
    """Create a product (201). Duplicate sku -> 409 (via the Conflict handler)."""
    # TODO (milestone 2): repo.create(**body.model_dump())
    raise NotImplementedError


@router.get("", response_model=Page)
def list_products(
    q: str | None = None,
    category: str | None = None,
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    repo: ProductRepository = Depends(get_repo),
):
    """Search/filter/paginate. Return {"items", "total", "limit", "offset"}."""
    # TODO (milestone 5)
    raise NotImplementedError


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int, repo: ProductRepository = Depends(get_repo)):
    """One product, or 404."""
    # TODO (milestone 2)
    raise NotImplementedError


@router.patch("/{product_id}", response_model=Product)
def update_product(product_id: int, body: ProductUpdate, repo: ProductRepository = Depends(get_repo)):
    """Partial update. Hint: body.model_dump(exclude_none=True)."""
    # TODO (milestone 3)
    raise NotImplementedError


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, repo: ProductRepository = Depends(get_repo)):
    """Delete; return an empty 204 response (fastapi.responses.Response)."""
    # TODO (milestone 3)
    raise NotImplementedError


@router.post("/{product_id}/stock", response_model=Product)
def adjust_stock(product_id: int, body: StockAdjustment, repo: ProductRepository = Depends(get_repo)):
    """Add/remove stock. Not enough stock -> 409."""
    # TODO (milestone 4)
    raise NotImplementedError


def create_app(db_path: str = ":memory:", api_key: str = "dev-key") -> FastAPI:
    """Build an app with its own repository.

    - app.state.repo = ProductRepository(db_path); app.state.api_key = api_key
    - exception handlers: NotFound -> 404, Conflict -> 409, both as {"detail": str(exc)}
    - GET /health -> {"status": "ok"} (no API key needed)
    - include `router`
    """
    # TODO (milestones 2, 6)
    raise NotImplementedError
