"""High-level product resolution: turns a user query (URL, UPC, or keyword)
into either a single Product or a list of candidates to disambiguate.

Now prioritizes Open Barcode API for UPC/EAN lookups to avoid bot detection.
Falls back to BBW scraping for keyword searches and URLs.
"""
import logging
from typing import List, Optional, Tuple

from app.models import Product, ProductCandidate, QueryType
from app.scraper import bbw_scraper
from app.scraper.bbw_scraper import ScraperError
from app.scraper import openbarcode_lookup

logger = logging.getLogger("bbw_search")


def _detect_query_type(query: str) -> QueryType:
    if bbw_scraper.is_url(query):
        return QueryType.url
    if bbw_scraper.is_upc(query):
        return QueryType.upc
    return QueryType.keyword


def _scrape_with_fallback(url: str) -> Product:
    try:
        return bbw_scraper.scrape_product_by_url(url)
    except ScraperError as exc:
        logger.info("Static scrape failed for %s (%s); trying Playwright fallback", url, exc)
        try:
            from app.scraper.playwright_fallback import render_html

            html = render_html(url)
            return bbw_scraper.parse_product_page(url, html)
        except RuntimeError:
            # Playwright not installed -- surface the original error.
            raise exc
        except Exception as fallback_exc:  # noqa: BLE001
            raise ScraperError(
                f"Both static and JS-rendered scraping failed for {url}: {fallback_exc}"
            ) from fallback_exc


def resolve_query(
    query: str, query_type: QueryType = QueryType.auto
) -> Tuple[Optional[Product], List[ProductCandidate]]:
    """Returns (product, candidates). Exactly one will be populated:
    - `product` is set when we could resolve directly to a single item.
    - `candidates` is set when a keyword/UPC search returned multiple
      possible matches and the caller should let the user pick one.

    For UPC codes, tries Open Barcode first to avoid bot detection.
    Falls back to BBW search if needed.
    """
    query = query.strip()
    resolved_type = _detect_query_type(query) if query_type == QueryType.auto else query_type

    if resolved_type == QueryType.url:
        return _scrape_with_fallback(query), []

    # For UPC codes, try Open Barcode first (avoids bot detection)
    if resolved_type == QueryType.upc:
        logger.info(f"Looking up UPC {query} in Open Barcode database...")
        try:
            product = openbarcode_lookup.lookup_by_upc(query)
            if product:
                logger.info(f"Found product in Open Barcode: {product.name}")
                return product, []
            else:
                logger.info(f"UPC {query} not found in Open Barcode, trying BBW search...")
        except Exception as e:
            logger.warning(f"Open Barcode lookup failed: {e}, falling back to BBW search")

    # UPC not found in Open Barcode or is a keyword search - use BBW site search
    candidates = bbw_scraper.search_products(query)

    if len(candidates) == 1:
        product = _scrape_with_fallback(candidates[0].url)
        return product, []

    # For a UPC search, prefer an exact SKU match among candidates' product
    # pages only if there's a single strong hit; otherwise return the list
    # so the user can disambiguate visually.
    return None, candidates
