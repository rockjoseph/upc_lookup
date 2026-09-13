"""Optional headless-browser fallback for pages that need JS rendering.

This module is only imported/used when `requests` + BeautifulSoup fail to
find a product on a page (see `app.scraper.bbw_scraper`). Playwright is an
optional dependency (see requirements.txt comment) -- if it isn't installed,
`render_html` raises a clear RuntimeError instead of an ImportError deep in
a stack trace.
"""
import random

from app.config import DEFAULT_HEADERS_EXTRA, REQUEST_TIMEOUT_SECONDS, USER_AGENTS


def render_html(url: str) -> str:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - exercised only w/o extra
        raise RuntimeError(
            "Playwright is not installed. Run `pip install playwright` and "
            "`playwright install chromium` to enable JS-rendered page "
            "fallback, or rely on the requests/BeautifulSoup path only."
        ) from exc

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            context = browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                extra_http_headers=DEFAULT_HEADERS_EXTRA,
            )
            page = context.new_page()
            page.goto(url, timeout=REQUEST_TIMEOUT_SECONDS * 1000, wait_until="networkidle")
            html = page.content()
        finally:
            browser.close()
    return html
