/**
 * Loads tests/fixtures/product_page.html (the same JSON-LD fixture used in
 * the backend's parser test, for parity) in a real browser and checks
 * window.BBWCapture.extract() against expected values.
 *
 * Run: node tests/test_extract.js
 * Requires Playwright (see backend for install, or `npm i -D playwright`
 * from this extension/ directory for standalone use).
 */
const path = require("path");
const assert = require("assert");
const { chromium } = require("playwright");

const FIXTURE = "file://" + path.join(__dirname, "fixtures", "product_page.html");

(async () => {
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH || undefined,
  });
  const page = await browser.newPage();
  await page.goto(FIXTURE);

  const product = await page.evaluate(() => window.BBWCapture.extract(document, "https://example.com/p/x"));

  assert.strictEqual(product.name, "Japanese Cherry Blossom Body Cream");
  assert.strictEqual(product.sku, "012345678901");
  assert.strictEqual(product.sale_price, 9.9);
  assert.strictEqual(product.original_price, 16.5);
  assert.strictEqual(product.promo_deal, "Buy 3, Get 1 Free");
  assert.strictEqual(product.stock_status, "InStock");
  assert.strictEqual(product.image_url, "https://example.com/img.jpg");
  assert.strictEqual(product.url, "https://example.com/p/x");

  console.log("PASS: extract.js matches expected values:");
  console.log(JSON.stringify(product, null, 2));

  await browser.close();
})().catch((err) => {
  console.error("FAIL:", err.message);
  process.exit(1);
});
