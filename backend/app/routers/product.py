import logging

from fastapi import APIRouter, HTTPException

from app.models import ProductLookupRequest, ProductLookupResponse
from app.scraper.bbw_scraper import ScraperError
from app.scraper.search import resolve_query

logger = logging.getLogger("product_router")
router = APIRouter(prefix="/api/product", tags=["product"])


@router.post("/lookup", response_model=ProductLookupResponse)
def lookup_product(request: ProductLookupRequest) -> ProductLookupResponse:
    try:
        product, candidates = resolve_query(request.query, request.query_type)
    except ScraperError as exc:
        logger.warning("Lookup failed for %r: %s", request.query, exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if product:
        return ProductLookupResponse(product=product)
    if candidates:
        return ProductLookupResponse(
            candidates=candidates,
            message="Multiple matches found -- pick one to see full details.",
        )
    raise HTTPException(status_code=404, detail="No matching product found.")


@router.post("/lookup/candidate", response_model=ProductLookupResponse)
def lookup_candidate(request: ProductLookupRequest) -> ProductLookupResponse:
    """Fetch full product details for a specific candidate URL chosen by
    the user after a disambiguating search."""
    from app.models import QueryType

    try:
        product, _ = resolve_query(request.query, QueryType.url)
    except ScraperError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return ProductLookupResponse(product=product)
