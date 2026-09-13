# Architecture

## Overview

```
┌─────────────────────┐        HTTP/JSON        ┌──────────────────────────┐
│   React frontend     │ ──────────────────────▶ │   FastAPI backend         │
│   (Vite + Tailwind)  │ ◀────────────────────── │                            │
└─────────────────────┘                          │  ┌──────────────────────┐ │
                                                  │  │ scraper/             │ │
                                                  │  │  - bbw_scraper.py    │ │
                                                  │  │  - search.py         │ │──▶ bathandbodyworks.com
                                                  │  │  - ratelimit.py      │ │
                                                  │  │  - playwright_       │ │
                                                  │  │    fallback.py (opt) │ │
                                                  │  └──────────────────────┘ │
                                                  │  ┌──────────────────────┐ │
                                                  │  │ excel/               │ │
                                                  │  │  - excel_service.py  │ │──▶ backend/data/sessions/*.xlsx
                                                  │  └──────────────────────┘ │
                                                  └──────────────────────────┘
```

## File tree

```
upc_lookup/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app instance, CORS, startup cleanup
│   │   ├── config.py                # Headers, rate limits, cache TTLs, Excel schema
│   │   ├── models.py                # Pydantic request/response schemas
│   │   ├── scraper/
│   │   │   ├── bbw_scraper.py       # HTTP fetch + JSON-LD/HTML product parsing
│   │   │   ├── search.py            # Query resolution: URL vs UPC vs keyword
│   │   │   ├── ratelimit.py         # Token-interval limiter + TTL page cache
│   │   │   └── playwright_fallback.py  # Optional JS-rendering fallback
│   │   ├── excel/
│   │   │   └── excel_service.py     # openpyxl read/upsert/append/export
│   │   └── routers/
│   │       ├── product.py           # POST /api/product/lookup(+/candidate)
│   │       └── excel.py             # /api/excel/* (new, upload, update, download)
│   ├── data/sessions/               # Per-session .xlsx files (gitignored)
│   ├── tests/test_excel_service.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx                  # Top-level state + wiring
│   │   ├── api.js                   # fetch() wrappers for the backend API
│   │   └── components/
│   │       ├── SearchBar.jsx
│   │       ├── ProductCard.jsx
│   │       ├── CandidateList.jsx
│   │       └── ExcelPanel.jsx
│   └── package.json
└── docs/ARCHITECTURE.md
```

## Data flow

1. **On load**, the frontend calls `POST /api/excel/new` to get a blank
   in-memory-workbook `session_id` (or the user uploads an existing `.xlsx`
   via `POST /api/excel/upload`, which seeds a session from it).
2. **Search**: the user enters a product URL, UPC, or keyword.
   `POST /api/product/lookup` auto-detects the query type:
   - **URL** → fetched and parsed directly.
   - **UPC / keyword** → run through BBW's site search
     (`/search?Ntt=...`); a single strong match is scraped immediately, or
     multiple candidates are returned for the user to disambiguate via
     `POST /api/product/lookup/candidate`.
3. **Extraction** (`bbw_scraper.py`) prefers the schema.org `Product`
   JSON-LD block embedded in the page (name, SKU, price, availability) and
   falls back to CSS-selector heuristics for anything missing, notably
   promo badges ("Buy 3, Get 1 Free", "40% Off", etc.) which are marketing
   copy rather than structured data.
4. **Add to Excel**: `POST /api/excel/update` finds an existing row by
   SKU (preferred) or exact product-name match and updates its price/promo/
   timestamp columns in place; otherwise it appends a new row.
5. **Download**: `GET /api/excel/{session_id}/download` streams the
   current workbook back as a `.xlsx` file.

## Anti-bot / rate-limiting posture

This is a low-volume personal tool, not a crawler, so the scraper is
deliberately polite rather than aggressive:

- A single in-process rate limiter enforces a minimum delay
  (`BBW_MIN_REQUEST_INTERVAL`, default 2.5s) between any two outbound
  requests to bathandbodyworks.com.
- Responses are cached in memory for a few minutes
  (`BBW_PRODUCT_CACHE_TTL`) so re-searching the same product doesn't
  re-fetch it.
- Requests use realistic desktop `User-Agent` / `Accept-Language` /
  `Referer` headers (rotated from a small pool), matching what any normal
  browser would send — this is not an attempt to defeat bot detection or
  CAPTCHAs, just to avoid being trivially misidentified as a non-browser
  client.
- On `403`/`429`/`503` responses the client retries a bounded number of
  times with exponential backoff, then gives up and surfaces a clear error
  rather than looping indefinitely.
- An optional Playwright fallback (not installed by default) can render
  JS-heavy pages if the static HTML path finds nothing — see
  `app/scraper/playwright_fallback.py`.

Please use this tool for personal price-tracking only, at a low request
volume, and in a way that's consistent with bathandbodyworks.com's Terms
of Service.
