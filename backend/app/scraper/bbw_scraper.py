"""Bath & Body Works product scraper.

Strategy
--------
Modern Salesforce-Commerce-Cloud storefronts (which bathandbodyworks.com runs
on) embed a schema.org ``Product`` JSON-LD block in every product detail page
for SEO. That block is the most stable source of truth (name, sku, price,
availability) and doesn't require executing JavaScript, so it's our primary
extraction path. We fall back to a handful of CSS-selector heuristics for
anything JSON-LD doesn't carry (notably promo badges like "Buy 3, Get 1
Free", which are rendered as marketing copy rather than structured data).

If neither JSON-LD nor the HTML heuristics find anything (e.g. because the
page genuinely requires JS to render), `render_with_playwright` can be used
as an optional, heavier fallback -- see the try/except import at the bottom.
This keeps the default install lightweight (requests + BeautifulSoup only).
"""
import json
import logging
import random
import re
import time
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from app.config import (
    BBW_BASE_URL,
    BBW_SEARCH_URL,
    DEFAULT_HEADERS_EXTRA,
    MAX_RETRIES,
    MIN_REQUEST_INTERVAL_SECONDS,
    PRODUCT_CACHE_TTL_SECONDS,
    REQUEST_TIMEOUT_SECONDS,
    RETRY_BACKOFF_BASE_SECONDS,
    USER_AGENTS,
)
from app.models import Product, ProductCandidate
from app.scraper.ratelimit import RateLimiter, TTLCache

logger = logging.getLogger("bbw_scraper")

_rate_limiter = RateLimiter(MIN_REQUEST_INTERVAL_SECONDS)
_page_cache = TTLCache(PRODUCT_CACHE_TTL_SECONDS)

PROMO_PATTERNS = [
    re.compile(r"buy\s*\d+[,]?\s*get\s*\d+\s*(free|% ?off|half ?off)", re.I),
    re.compile(r"\b\d{1,2}%\s*off\b", re.I),
    re.compile(r"\bmix\s*&?\s*match\b", re.I),
    re.compile(r"\bclearance\b", re.I),
    re.compile(r"\bfinal\s*sale\b", re.I),
]

UPC_RE = re.compile(r"^\d{8,14}$")


class ScraperError(Exception):
    """Raised when a page can't be fetched or parsed into a product."""


def _headers() -> dict:
    """Generate headers that mimic a real browser more closely.

    PerimeterX bot detection looks for missing or unusual headers,
    inconsistent user agents, and other fingerprinting techniques.
    """
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    headers.update(DEFAULT_HEADERS_EXTRA)

    # Vary referrer to look more natural (sometimes from home, sometimes from search, sometimes from product pages)
    referrer_choice = random.random()
    if referrer_choice < 0.5:
        headers["Referer"] = BBW_BASE_URL + "/"
    elif referrer_choice < 0.85:
        headers["Referer"] = BBW_BASE_URL + "/search"
    else:
        # Sometimes come from Google search
        headers["Referer"] = "https://www.google.com/"

    return headers


def _get(url: str) -> requests.Response:
    """GET a URL with politeness (rate limiting) and retry/backoff on
    transient failures or throttling responses."""
    last_exc: Optional[Exception] = None
    for attempt in range(1, MAX_RETRIES + 1):
        _rate_limiter.wait()
        try:
            resp = requests.get(url, headers=_headers(), timeout=REQUEST_TIMEOUT_SECONDS)
        except requests.RequestException as exc:
            last_exc = exc
            logger.warning("Request error on attempt %s for %s: %s", attempt, url, exc)
        else:
            if resp.status_code == 200:
                return resp
            # Any non-200 response (throttling, a bot-challenge page, an
            # unexpected redirect, a real 4xx/5xx, ...) is recorded with
            # enough detail to diagnose, then retried with backoff rather
            # than either silently dropping the reason or raising an
            # unrelated, uncaught exception via raise_for_status().
            snippet = (resp.text or "")[:200].replace("\n", " ").strip()
            last_exc = ScraperError(
                f"HTTP {resp.status_code} {resp.reason} from {url}"
                + (f" -- body starts: {snippet!r}" if snippet else "")
            )
            logger.warning(
                "Got status %s for %s (attempt %s/%s): %s",
                resp.status_code,
                url,
                attempt,
                MAX_RETRIES,
                snippet,
            )
        time.sleep(RETRY_BACKOFF_BASE_SECONDS * attempt)
    raise ScraperError(f"Failed to fetch {url} after {MAX_RETRIES} attempts: {last_exc}")


def fetch_html(url: str) -> str:
    cached = _page_cache.get(url)
    if cached is not None:
        return cached
    resp = _get(url)
    _page_cache.set(url, resp.text)
    return resp.text


def _extract_json_ld_product(soup: BeautifulSoup) -> Optional[dict]:
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        candidates = data if isinstance(data, list) else [data]
        for candidate in candidates:
            if isinstance(candidate, dict) and candidate.get("@type") in ("Product", ["Product"]):
                return candidate
            # Some sites nest the Product inside an @graph array.
            graph = candidate.get("@graph") if isinstance(candidate, dict) else None
            if graph:
                for node in graph:
                    if isinstance(node, dict) and node.get("@type") == "Product":
                        return node
    return None


def _find_promo_text(soup: BeautifulSoup) -> Optional[str]:
    # Common promo/badge containers on retail PDPs.
    selectors = [
        "[class*='promo']",
        "[class*='badge']",
        "[class*='callout']",
        "[data-testid*='promo']",
    ]
    seen = set()
    for selector in selectors:
        for el in soup.select(selector):
            text = el.get_text(" ", strip=True)
            if not text or text in seen:
                continue
            seen.add(text)
            for pattern in PROMO_PATTERNS:
                if pattern.search(text):
                    return text
    # Last resort: scan the whole page text for a promo-shaped sentence.
    body_text = soup.get_text(" ", strip=True)
    for pattern in PROMO_PATTERNS:
        match = pattern.search(body_text)
        if match:
            start = max(0, match.start() - 20)
            end = min(len(body_text), match.end() + 20)
            return body_text[start:end].strip()
    return None


def _parse_price(value) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value)
    match = re.search(r"[\d,]+\.?\d*", text)
    if not match:
        return None
    try:
        return float(match.group(0).replace(",", ""))
    except ValueError:
        return None


def parse_product_page(url: str, html: str) -> Product:
    soup = BeautifulSoup(html, "html.parser")
    ld = _extract_json_ld_product(soup)

    name = None
    sku = None
    sale_price = None
    original_price = None
    stock_status = None
    image_url = None

    if ld:
        name = ld.get("name")
        sku = ld.get("sku") or ld.get("mpn") or ld.get("productID")
        image = ld.get("image")
        if isinstance(image, list) and image:
            image_url = image[0]
        elif isinstance(image, str):
            image_url = image

        offers = ld.get("offers")
        if isinstance(offers, list) and offers:
            offers = offers[0]
        if isinstance(offers, dict):
            sale_price = _parse_price(offers.get("price"))
            availability = (offers.get("availability") or "").rsplit("/", 1)[-1]
            if availability:
                stock_status = availability  # e.g. "InStock", "OutOfStock"
            price_spec = offers.get("priceSpecification")
            if isinstance(price_spec, dict):
                original_price = _parse_price(
                    price_spec.get("price") or price_spec.get("originalPrice")
                )

    # HTML fallbacks for anything JSON-LD didn't give us.
    if not name:
        title_el = soup.select_one("h1")
        name = title_el.get_text(strip=True) if title_el else None

    if sale_price is None:
        price_el = soup.select_one("[class*='sale-price'], [class*='salePrice'], [data-testid*='sale-price']")
        sale_price = _parse_price(price_el.get_text(strip=True)) if price_el else None

    if original_price is None:
        orig_el = soup.select_one(
            "[class*='original-price'], [class*='list-price'], [class*='strike'], [class*='was-price']"
        )
        original_price = _parse_price(orig_el.get_text(strip=True)) if orig_el else None

    if original_price is None:
        original_price = sale_price

    if not sku:
        sku_el = soup.select_one("[class*='sku'], [data-testid*='sku'], [id*='sku']")
        if sku_el:
            sku_match = re.search(r"\d{4,}", sku_el.get_text(strip=True))
            sku = sku_match.group(0) if sku_match else None

    if not stock_status:
        oos_el = soup.select_one("[class*='out-of-stock'], [class*='sold-out'], [class*='oos']")
        stock_status = "OutOfStock" if oos_el else "InStock"

    promo_deal = _find_promo_text(soup)

    if not name:
        raise ScraperError(f"Could not find product name on page: {url}")

    return Product(
        sku=sku,
        name=name,
        original_price=original_price,
        sale_price=sale_price,
        promo_deal=promo_deal,
        stock_status=stock_status,
        url=url,
        image_url=image_url,
    )


def scrape_product_by_url(url: str) -> Product:
    html = fetch_html(url)
    return parse_product_page(url, html)


def search_products(query: str, limit: int = 8) -> List[ProductCandidate]:
    """Search the BBW site search for a keyword or UPC and return a list of
    candidate product links parsed from the results page."""
    search_url = f"{BBW_SEARCH_URL}?Ntt={requests.utils.quote(query)}"
    html = fetch_html(search_url)
    soup = BeautifulSoup(html, "html.parser")

    candidates: List[ProductCandidate] = []
    seen_urls = set()

    # Product tiles typically live inside anchors linking to /p/ product
    # detail pages. This selector is intentionally loose since markup can
    # change; it's a best-effort heuristic, not a scraping contract.
    for anchor in soup.select("a[href*='/p/']"):
        href = anchor.get("href")
        if not href:
            continue
        full_url = href if href.startswith("http") else BBW_BASE_URL + href
        if full_url in seen_urls:
            continue

        name = anchor.get("aria-label") or anchor.get("title")
        if not name:
            img = anchor.select_one("img")
            name = img.get("alt") if img else None
        text = anchor.get_text(strip=True)
        if not name and text:
            name = text
        if not name:
            continue

        image_el = anchor.select_one("img")
        image_url = image_el.get("src") if image_el else None

        seen_urls.add(full_url)
        candidates.append(ProductCandidate(name=name, url=full_url, image_url=image_url))
        if len(candidates) >= limit:
            break

    if not candidates:
        raise ScraperError(f"No search results found for '{query}'")

    return candidates


def is_upc(query: str) -> bool:
    return bool(UPC_RE.match(query.strip()))


def is_url(query: str) -> bool:
    return query.strip().lower().startswith(("http://", "https://"))
