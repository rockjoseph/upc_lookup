# BBW Price Tracker

A lightweight full-stack app for looking up Bath & Body Works product prices
(by URL, UPC/barcode, or name) and syncing the results into an Excel
spreadsheet — update existing rows in place or append new products, then
download the updated `.xlsx`.

- **Backend**: Python + FastAPI, `requests`/BeautifulSoup scraper (optional
  Playwright fallback for JS-rendered pages), `openpyxl` for Excel I/O.
- **Frontend**: React (Vite) + Tailwind CSS.
- **Browser extension** (`extension/`): an alternative, always-works way to
  get product data in — captures it from a page you're already viewing in
  your own browser instead of scraping. See
  [`extension/README.md`](extension/README.md).

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full file tree,
data flow, and scraping/rate-limiting design.

> **Heads up on scraping**: bathandbodyworks.com fronts its search endpoint
> with a dedicated bot-management vendor (HUMAN Security / PerimeterX) that
> also targets headless browsers, so automated search/lookup may get
> blocked outright regardless of the Playwright fallback. If that happens,
> use the browser extension instead (or paste a direct product URL, which
> has a better chance of resolving than a keyword/UPC search). See the
> "Anti-bot" section of `docs/ARCHITECTURE.md` for details.

## Features

- Search by pasting a product URL, typing a UPC/barcode, or a name/keyword.
- Extracts: product name, sale price, original price, promo tag (e.g. "Buy 3
  Get 1 Free"), stock status, and SKU.
- Upload an existing `.xlsx` or start a fresh one.
- "Add / Update in Excel" matches existing rows by SKU (falling back to
  exact product name) and updates price/promo/timestamp in place, or
  appends a new row if the product isn't in the sheet yet.
- Download the updated workbook at any time.
- Polite scraping: rate-limited, cached, retried with backoff — see
  [Anti-bot / rate-limiting posture](docs/ARCHITECTURE.md#anti-bot--rate-limiting-posture).

## Prerequisites

- Python 3.10+
- Node.js 18+
- (Optional) Playwright, only if you want JS-rendered-page fallback:
  `pip install playwright && playwright install chromium`

## Setup & running locally

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API is now live at `http://localhost:8000` (interactive docs at
`http://localhost:8000/docs`). Run the test suite with:

```bash
python -m pytest tests/ -v
```

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. It talks to the backend at
`http://localhost:8000` by default — override with a `.env` file in
`frontend/` containing `VITE_API_URL=http://your-backend-host:8000` if
needed.

### 3. Using the app

1. On load, a blank spreadsheet session is created automatically — or click
   **Upload .xlsx** to seed it from an existing price-tracking sheet.
2. Search for a product by pasting its BBW product page URL, typing a
   UPC/barcode, or a name/keyword. If the search is ambiguous you'll see a
   pick-list of candidates first.
3. Review the product card (name, price, promo tag, stock status), then
   click **Add / Update in Excel**.
4. Repeat for as many products as you like — the table below updates live.
5. Click **Download Updated Excel** to save the `.xlsx` file.

## Configuration

Environment variables (backend), all optional:

| Variable | Default | Purpose |
|---|---|---|
| `BBW_MIN_REQUEST_INTERVAL` | `2.5` | Minimum seconds between outbound requests to bathandbodyworks.com |
| `BBW_PRODUCT_CACHE_TTL` | `300` | Seconds a scraped page is cached before re-fetching |
| `SESSION_TTL_SECONDS` | `86400` | Age at which stale session workbooks are cleaned up on startup |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated allowed frontend origins |

## Excel schema

Each row in the `Prices` sheet:

| SKU/UPC | Product Name | Original Price | Current Sale Price | Promo Deal | Last Checked Date/Time | Product URL |
|---|---|---|---|---|---|---|

## Notes & limitations

- BBW's storefront markup can change at any time; the scraper's HTML
  fallback selectors are best-effort heuristics layered on top of the more
  stable JSON-LD product data. If a page ever fails to parse, the API
  returns a clear error rather than silently returning bad data.
- This tool is intended for personal, low-volume price tracking. Please
  keep request volume low and use it in line with bathandbodyworks.com's
  Terms of Service.
- This was built and unit-tested (Excel read/upsert/append logic, product
  HTML parsing against a mocked JSON-LD page, and the full FastAPI request
  cycle) in a sandboxed environment without outbound access to
  bathandbodyworks.com — verify a live search against the real site as
  your first step when you run it locally.
