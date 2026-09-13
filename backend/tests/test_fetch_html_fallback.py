"""Tests for fetch_html()'s static -> Playwright fallback and bot-challenge
detection (e.g. HUMAN Security / PerimeterX "px-captcha" pages)."""
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest  # noqa: E402

from app.scraper import bbw_scraper  # noqa: E402
from app.scraper.bbw_scraper import ScraperError, fetch_html  # noqa: E402

CAPTCHA_BODY = (
    '<!DOCTYPE html><html><head><meta name="description" content="px-captcha">'
    "<title>Access to this page has been denied</title></head><body></body></html>"
)
REAL_BODY = "<html><body><h1>Real product page</h1></body></html>"


def _fake_response(status_code=200, text=""):
    resp = MagicMock()
    resp.status_code = status_code
    resp.reason = "OK"
    resp.text = text
    return resp


@pytest.fixture(autouse=True)
def clear_cache():
    bbw_scraper._page_cache._store.clear()
    yield
    bbw_scraper._page_cache._store.clear()


@patch("time.sleep", return_value=None)
@patch("app.scraper.bbw_scraper.requests.get")
def test_normal_page_returns_without_fallback(mock_get, _sleep):
    mock_get.return_value = _fake_response(200, REAL_BODY)
    html = fetch_html("https://www.bathandbodyworks.com/p/example")
    assert html == REAL_BODY
    mock_get.assert_called_once()


@patch("time.sleep", return_value=None)
@patch("app.scraper.bbw_scraper.requests.get")
def test_captcha_body_with_200_status_triggers_fallback(mock_get, _sleep):
    # A bot-challenge page can be served with a perfectly normal 200 status,
    # so a status-code check alone wouldn't have caught it.
    mock_get.return_value = _fake_response(200, CAPTCHA_BODY)

    with patch("app.scraper.playwright_fallback.render_html", return_value=REAL_BODY) as mock_render:
        html = fetch_html("https://www.bathandbodyworks.com/search?Ntt=x")

    assert html == REAL_BODY
    mock_render.assert_called_once()


@patch("time.sleep", return_value=None)
@patch("app.scraper.bbw_scraper.requests.get")
def test_fallback_also_challenged_raises_clear_error(mock_get, _sleep):
    mock_get.return_value = _fake_response(200, CAPTCHA_BODY)

    with patch("app.scraper.playwright_fallback.render_html", return_value=CAPTCHA_BODY):
        with pytest.raises(ScraperError) as exc_info:
            fetch_html("https://www.bathandbodyworks.com/search?Ntt=x")

    message = str(exc_info.value)
    assert "even after JS rendering" in message


@patch("time.sleep", return_value=None)
@patch("app.scraper.bbw_scraper.requests.get")
def test_playwright_not_installed_surfaces_original_error(mock_get, _sleep):
    mock_get.return_value = _fake_response(403, "Forbidden")

    with patch(
        "app.scraper.playwright_fallback.render_html",
        side_effect=RuntimeError("Playwright is not installed."),
    ):
        with pytest.raises(ScraperError) as exc_info:
            fetch_html("https://www.bathandbodyworks.com/search?Ntt=x")

    # Should surface the ORIGINAL static-fetch error, not a confusing
    # "playwright not installed" message when JS fallback wasn't the ask.
    assert "403" in str(exc_info.value)


@patch("time.sleep", return_value=None)
@patch("app.scraper.bbw_scraper.requests.get")
def test_allow_js_fallback_false_skips_playwright_entirely(mock_get, _sleep):
    mock_get.return_value = _fake_response(200, CAPTCHA_BODY)

    with patch("app.scraper.playwright_fallback.render_html") as mock_render:
        with pytest.raises(ScraperError):
            fetch_html("https://www.bathandbodyworks.com/search?Ntt=x", allow_js_fallback=False)

    mock_render.assert_not_called()
