/**
 * Regression test for the SPA-navigation bug found during real-world
 * testing: bathandbodyworks.com routes from e.g. a search page to a
 * product page via the History API (pushState) without a full page
 * load, so the extension must detect that and show the capture button
 * without requiring a hard refresh.
 *
 * Serves the fixture over a real local HTTP server (rather than file://)
 * since pushState's same-origin requirements behave more predictably
 * there, matching a real https:// page.
 *
 * Run: node tests/test_spa_navigation.js
 */
const path = require("path");
const assert = require("assert");
const http = require("http");
const { chromium } = require("playwright");

const FIXTURES_DIR = path.join(__dirname, "fixtures");
const CONTENT_DIR = path.join(__dirname, "..", "content");

function startServer() {
  const server = http.createServer((req, res) => {
    // Serve spa_shell.html for any path that isn't a static asset --
    // mimics a real SPA server always returning the same shell.
    if (req.url.startsWith("/content/")) {
      const fs = require("fs");
      const filePath = path.join(CONTENT_DIR, req.url.replace("/content/", ""));
      fs.readFile(filePath, (err, data) => {
        if (err) {
          res.writeHead(404);
          res.end();
          return;
        }
        res.writeHead(200, { "Content-Type": "application/javascript" });
        res.end(data);
      });
      return;
    }
    const fs = require("fs");
    fs.readFile(path.join(FIXTURES_DIR, "spa_shell_server.html"), (err, data) => {
      res.writeHead(200, { "Content-Type": "text/html" });
      res.end(data);
    });
  });
  return new Promise((resolve) => {
    server.listen(0, "127.0.0.1", () => resolve(server));
  });
}

(async () => {
  const server = await startServer();
  const port = server.address().port;
  const baseUrl = `http://127.0.0.1:${port}`;

  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH || undefined,
  });
  const page = await browser.newPage();

  // Start on a non-product path, same as landing on a search page.
  await page.goto(`${baseUrl}/search?q=matcha`);

  let btn = await page.$("#bbw-price-tracker-capture-btn");
  assert.strictEqual(btn, null, "Button should NOT exist on a non-product page");
  console.log("PASS: no button on /search");

  // Simulate the SPA routing to a product page via pushState -- no
  // navigation, no full page load, exactly what BBW's React app does.
  await page.evaluate(() => {
    history.pushState({}, "", "/p/pink-matcha-latte-028029434");
  });

  await page.waitForSelector("#bbw-price-tracker-capture-btn", { timeout: 2000 });
  console.log("PASS: button appeared after pushState navigation to /p/... (no reload needed)");

  // Simulate navigating back to a non-product page via pushState.
  await page.evaluate(() => {
    history.pushState({}, "", "/search?q=candle");
  });

  await page.waitForFunction(
    () => !document.getElementById("bbw-price-tracker-capture-btn"),
    { timeout: 2000 }
  );
  console.log("PASS: button removed after navigating away from /p/...");

  // And popstate (back/forward button) is handled too.
  await page.evaluate(() => {
    history.pushState({}, "", "/p/another-product-999");
  });
  await page.waitForSelector("#bbw-price-tracker-capture-btn", { timeout: 2000 });

  await page.goBack(); // triggers a popstate back to /search?q=candle
  await page.waitForFunction(
    () => !document.getElementById("bbw-price-tracker-capture-btn"),
    { timeout: 2000 }
  );
  console.log("PASS: button removed on popstate (browser back button)");

  await browser.close();
  server.close();
})().catch((err) => {
  console.error("FAIL:", err.message);
  process.exit(1);
});
