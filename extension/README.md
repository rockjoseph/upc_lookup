# BBW Price Tracker Capture (browser extension)

Captures product data from bathandbodyworks.com **while you browse
normally** in your own logged-in browser, and hands it to the Price
Tracker frontend to add/update in your Excel sheet. No automated requests
to BBW's servers are made by this extension — it only reads the DOM of a
page you're already looking at — so it doesn't run into the site's
bot-management system (see the root [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md)
for why the backend scraper can hit that wall on its own).

## How it works

1. You browse to a product page on bathandbodyworks.com yourself.
2. A small "📥 Send to Price Tracker" button appears in the bottom-right
   corner. Click it.
3. The extension reads the product's name, price, promo tag, SKU, and
   stock status straight out of the page (same JSON-LD-first approach as
   the backend scraper, just running client-side), then focuses or opens
   your Price Tracker app tab and delivers the captured product into it.
4. The app shows it exactly like a normal search result — click
   **Add / Update in Excel** as usual.

## Install (unpacked, for personal/dev use)

This isn't published to the Chrome Web Store — load it as an unpacked
extension:

1. Open `chrome://extensions` (or `edge://extensions` for Edge).
2. Turn on **Developer mode** (top-right toggle).
3. Click **Load unpacked** and select this `extension/` folder.
4. Pin the extension (optional) via the puzzle-piece icon in the toolbar.

## Configure the tracker URL

By default the extension delivers captures to `http://localhost:5173`
(the frontend's default dev port). If you run the frontend elsewhere,
click the extension's toolbar icon and update the URL there.

## Usage

1. Start the backend and frontend as described in the root
   [`README.md`](../README.md).
2. Browse to any product page on bathandbodyworks.com, e.g.
   `https://www.bathandbodyworks.com/p/...`.
3. Click **📥 Send to Price Tracker**.
4. Your Price Tracker tab is focused (or opened) automatically with the
   captured product ready to add.

## Files

| File | Purpose |
|---|---|
| `manifest.json` | Manifest V3 config: permissions, content scripts, background worker |
| `content/extract.js` | Pure DOM-extraction logic (JSON-LD first, CSS-selector fallbacks) — mirrors `backend/app/scraper/bbw_scraper.py`'s approach |
| `content/bbw_capture.js` | Injects the capture button on BBW product pages, wires it to `extract.js` |
| `content/tracker_bridge.js` | Runs on the tracker frontend; relays a pending capture into the page via `postMessage` |
| `background.js` | Service worker: stores the captured product, focuses/opens the tracker tab |
| `popup.html` / `popup.js` | Toolbar popup for setting the tracker URL |

## Tests

`tests/test_extract.js` loads `tests/fixtures/product_page.html` (the same
JSON-LD fixture used in the backend's parser test, for parity) in a real
browser and checks `extract.js`'s output against expected values:

```bash
npm install --no-save playwright   # if not already available
node tests/test_extract.js
```

## Notes

- This only works on pages you're actually viewing in your own browser —
  it can't run in the background against pages you haven't opened, and
  that's by design (it's a capture tool, not a crawler).
- The `postMessage` the tracker bridge sends is scoped to the tracker
  page's own origin and carries an explicit `__bbwPriceTrackerCapture`
  marker; `App.jsx`'s listener checks both before acting on it.
