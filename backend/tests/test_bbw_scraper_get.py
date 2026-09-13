"""Regression test for the `_get()` retry loop.

Guards against a bug where any response status outside {200, 403, 429, 503}
(e.g. an unexpected 2xx/3xx, or falling through `raise_for_status()`'s
no-op range) left `last_exc` unset, producing an uninformative
"...after N attempts: None" error instead of surfacing the real status.
"""
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest  # noqa: E402

from app.scraper.bbw_scraper import ScraperError, _get  # noqa: E402


def _fake_response(status_code, reason="Some Reason", text=""):
    resp = MagicMock()
    resp.status_code = status_code
    resp.reason = reason
    resp.text = text
    return resp


@patch("time.sleep", return_value=None)  # also covers the rate limiter's own sleep
@patch("app.scraper.bbw_scraper.requests.get")
def test_unhandled_status_code_produces_informative_error(mock_get, _mock_sleep):
    # A status code outside the special-cased {200, 403, 429, 503} set --
    # previously this silently left last_exc as None on every attempt.
    mock_get.return_value = _fake_response(202, reason="Accepted", text="please wait...")

    with pytest.raises(ScraperError) as exc_info:
        _get("https://www.bathandbodyworks.com/search?Ntt=test")

    message = str(exc_info.value)
    assert "None" not in message
    assert "202" in message
    assert "Accepted" in message


@patch("time.sleep", return_value=None)
@patch("app.scraper.bbw_scraper.requests.get")
def test_real_4xx_status_is_caught_as_scraper_error_not_raised_raw(mock_get, _mock_sleep):
    # A genuine client error (e.g. 404) must come back as a clean
    # ScraperError, not an uncaught requests.HTTPError from
    # response.raise_for_status().
    mock_get.return_value = _fake_response(404, reason="Not Found", text="<html>Not found</html>")

    with pytest.raises(ScraperError) as exc_info:
        _get("https://www.bathandbodyworks.com/p/does-not-exist")

    message = str(exc_info.value)
    assert "404" in message
    assert "None" not in message


@patch("time.sleep", return_value=None)
@patch("app.scraper.bbw_scraper.requests.get")
def test_success_returns_response_without_retry(mock_get, _mock_sleep):
    mock_get.return_value = _fake_response(200, text="<html>ok</html>")
    resp = _get("https://www.bathandbodyworks.com/p/example")
    assert resp.status_code == 200
    assert mock_get.call_count == 1
