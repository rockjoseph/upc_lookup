"""High-level product resolution: turns a user query (URL, UPC, or keyword)
into either a single Product or a list of candidates to disambiguate.

The static-vs-JS-rendered fallback lives in `bbw_scraper.fetch_html()` now,
so every call here (search page or product page) benefits from it
uniformly -- this module just orchestrates which URL(s) to fetch."""
from typing import List, Optional, Tuple

from app.models import Product, ProductCandidate, QueryType
from app.scraper import bbw_scraper


def _detect_query_type(query: str) -> QueryType:
    if bbw_scraper.is_url(query):
        return QueryType.url
    if bbw_scraper.is_upc(query):
        return QueryType.upc
    return QueryType.keyword


def resolve_query(
    query: str, query_type: QueryType = QueryType.auto
) -> Tuple[Optional[Product], List[ProductCandidate]]:
    """Returns (product, candidates). Exactly one will be populated:
    - `product` is set when we could resolve directly to a single item.
    - `candidates` is set when a keyword/UPC search returned multiple
      possible matches and the caller should let the user pick one.
    """
    query = query.strip()
    resolved_type = _detect_query_type(query) if query_type == QueryType.auto else query_type

    if resolved_type == QueryType.url:
        return bbw_scraper.scrape_product_by_url(query), []

    # UPC and keyword both go through the site search.
    candidates = bbw_scraper.search_products(query)

    if len(candidates) == 1:
        product = bbw_scraper.scrape_product_by_url(candidates[0].url)
        return product, []

    # For a UPC search, prefer an exact SKU match among candidates' product
    # pages only if there's a single strong hit; otherwise return the list
    # so the user can disambiguate visually.
    return None, candidates
