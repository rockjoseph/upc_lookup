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
- On any non-200 response the client retries a bounded number of times
  with exponential backoff, then gives up and surfaces the real status
  code/reason/body snippet rather than a vague error.
- `fetch_html()` also sniffs the response body for known bot-management
  challenge-page signatures (see `BOT_CHALLENGE_MARKERS` in
  `bbw_scraper.py`) since these are sometimes served with an
  otherwise-normal status code. When one is detected, it falls back once
  to a JS-rendered fetch via Playwright (`app/scraper/playwright_fallback.py`,
  optional dependency) before giving up.

### When the site's bot-management blocks automated access outright

In practice, `bathandbodyworks.com/search` is fronted by a dedicated
bot-management vendor (HUMAN Security / PerimeterX — its challenge pages
mention "px-captcha" and the response reason phrase reads "Human BD
Forbidden"). That system is purpose-built to also fingerprint and block
headless browsers (checks like `navigator.webdriver`, canvas/WebGL
fingerprints, missing plugins, CDP artifacts), so enabling the Playwright
fallback is not guaranteed to get through it — and if it still returns a
challenge page with JS rendering enabled, `fetch_html()` raises a clear
"blocking automated access outright" error rather than silently retrying
forever.

That's an intentional stopping point, not a bug to route around: at that
point the site has a dedicated control in place specifically to block
programmatic access, and defeating it would mean stealth-patching the
browser's fingerprint, solving CAPTCHAs, or rotating IPs — techniques for
evading a security control rather than polite scraping, which this project
won't build. If you hit that wall, two options that don't involve
circumventing anything:

1. **Manual entry**: browse the site yourself in a normal browser, and use
   this app purely for the Excel matching/upsert/download logic (already
   fully self-contained and working without any scraping).
2. **Browser-extension capture**: a small extension that reads product
   data from the page while you browse normally (your own authenticated
   session) and posts it to this backend — legitimate because it's your
   own browser and no automated request is made to the site at all.

Please use this tool for personal price-tracking only, at a low request
volume, and in a way that's consistent with bathandbodyworks.com's Terms
of Service.
