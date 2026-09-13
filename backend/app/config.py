"""Application configuration and constants."""
import os

# Base site
BBW_BASE_URL = "https://www.bathandbodyworks.com"
BBW_SEARCH_URL = f"{BBW_BASE_URL}/search"

# A small pool of realistic desktop user agents. Rotated per-request so we
# don't hammer the origin with a single fingerprint. This is standard,
# polite scraping practice for a low-volume personal tool -- not intended
# to defeat any bot-detection or security control.
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/16.5 Safari/605.1.15",
]

DEFAULT_HEADERS_EXTRA = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Minimum number of seconds between outbound requests to bathandbodyworks.com.
# Keeps the tool polite / low-volume rather than hammering the origin.
MIN_REQUEST_INTERVAL_SECONDS = float(os.getenv("BBW_MIN_REQUEST_INTERVAL", "2.5"))

# How long a successfully scraped product page is cached in memory before
# we're willing to re-fetch it.
PRODUCT_CACHE_TTL_SECONDS = int(os.getenv("BBW_PRODUCT_CACHE_TTL", "300"))

# Network timeouts / retries
REQUEST_TIMEOUT_SECONDS = 15
MAX_RETRIES = 3
RETRY_BACKOFF_BASE_SECONDS = 1.5

# Where session workbooks (uploaded / created .xlsx files) are stored.
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SESSIONS_DIR = os.path.join(DATA_DIR, "sessions")
os.makedirs(SESSIONS_DIR, exist_ok=True)

# Sessions older than this are cleaned up on startup.
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", str(60 * 60 * 24)))  # 24h

# Excel sheet layout
EXCEL_SHEET_NAME = "Prices"
EXCEL_HEADERS = [
    "SKU/UPC",
    "Product Name",
    "Original Price",
    "Current Sale Price",
    "Promo Deal",
    "Last Checked Date/Time",
    "Product URL",
]
