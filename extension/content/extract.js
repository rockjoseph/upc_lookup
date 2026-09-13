/**
 * Product extraction logic, mirroring backend/app/scraper/bbw_scraper.py's
 * approach: prefer the schema.org Product JSON-LD block, fall back to
 * CSS-selector heuristics for anything missing (notably promo badges).
 *
 * This runs inside the user's own real, authenticated browser session on a
 * page they're already viewing -- there's no automated request to BBW's
 * servers here at all, so none of the bot-detection concerns that affect
 * server-side scraping apply.
 *
 * Exposed as `window.BBWCapture.extract(doc)` so it's usable from the
 * content script and independently testable (e.g. via a headless page
 * loaded from a local HTML fixture).
 */
(function (global) {
  "use strict";

  const PROMO_PATTERNS = [
    /buy\s*\d+[,]?\s*get\s*\d+\s*(free|% ?off|half ?off)/i,
    /\b\d{1,2}%\s*off\b/i,
    /\bmix\s*&?\s*match\b/i,
    /\bclearance\b/i,
    /\bfinal\s*sale\b/i,
  ];

  function parsePrice(value) {
    if (value === null || value === undefined) return null;
    if (typeof value === "number") return value;
    const match = String(value).match(/[\d,]+\.?\d*/);
    if (!match) return null;
    const num = parseFloat(match[0].replace(/,/g, ""));
    return Number.isNaN(num) ? null : num;
  }

  function extractJsonLdProduct(doc) {
    const scripts = doc.querySelectorAll('script[type="application/ld+json"]');
    for (const script of scripts) {
      let data;
      try {
        data = JSON.parse(script.textContent || "");
      } catch (e) {
        continue;
      }
      const candidates = Array.isArray(data) ? data : [data];
      for (const candidate of candidates) {
        if (!candidate || typeof candidate !== "object") continue;
        if (candidate["@type"] === "Product") return candidate;
        if (Array.isArray(candidate["@graph"])) {
          const found = candidate["@graph"].find((n) => n && n["@type"] === "Product");
          if (found) return found;
        }
      }
    }
    return null;
  }

  function findPromoText(doc) {
    const selectors = ["[class*='promo']", "[class*='badge']", "[class*='callout']", "[data-testid*='promo']"];
    const seen = new Set();
    for (const selector of selectors) {
      for (const el of doc.querySelectorAll(selector)) {
        const text = (el.textContent || "").trim();
        if (!text || seen.has(text)) continue;
        seen.add(text);
        if (PROMO_PATTERNS.some((p) => p.test(text))) return text;
      }
    }
    const bodyText = (doc.body && doc.body.textContent) || "";
    for (const pattern of PROMO_PATTERNS) {
      const match = bodyText.match(pattern);
      if (match) {
        const start = Math.max(0, match.index - 20);
        const end = Math.min(bodyText.length, match.index + match[0].length + 20);
        return bodyText.slice(start, end).trim();
      }
    }
    return null;
  }

  function extract(doc, url) {
    doc = doc || document;
    url = url || doc.location?.href || (typeof location !== "undefined" ? location.href : "");

    const ld = extractJsonLdProduct(doc);

    let name = null;
    let sku = null;
    let salePrice = null;
    let originalPrice = null;
    let stockStatus = null;
    let imageUrl = null;

    if (ld) {
      name = ld.name || null;
      sku = ld.sku || ld.mpn || ld.productID || null;
      const image = ld.image;
      if (Array.isArray(image) && image.length) imageUrl = image[0];
      else if (typeof image === "string") imageUrl = image;

      let offers = ld.offers;
      if (Array.isArray(offers) && offers.length) offers = offers[0];
      if (offers && typeof offers === "object") {
        salePrice = parsePrice(offers.price);
        const availability = (offers.availability || "").split("/").pop();
        if (availability) stockStatus = availability;
        const priceSpec = offers.priceSpecification;
        if (priceSpec && typeof priceSpec === "object") {
          originalPrice = parsePrice(priceSpec.price || priceSpec.originalPrice);
        }
      }
    }

    if (!name) {
      const titleEl = doc.querySelector("h1");
      name = titleEl ? titleEl.textContent.trim() : null;
    }

    if (salePrice === null) {
      const priceEl = doc.querySelector(
        "[class*='sale-price'], [class*='salePrice'], [data-testid*='sale-price']"
      );
      salePrice = priceEl ? parsePrice(priceEl.textContent.trim()) : null;
    }

    if (originalPrice === null) {
      const origEl = doc.querySelector(
        "[class*='original-price'], [class*='list-price'], [class*='strike'], [class*='was-price']"
      );
      originalPrice = origEl ? parsePrice(origEl.textContent.trim()) : null;
    }

    if (originalPrice === null) originalPrice = salePrice;

    if (!sku) {
      const skuEl = doc.querySelector("[class*='sku'], [data-testid*='sku'], [id*='sku']");
      if (skuEl) {
        const skuMatch = skuEl.textContent.trim().match(/\d{4,}/);
        sku = skuMatch ? skuMatch[0] : null;
      }
    }

    if (!stockStatus) {
      const oosEl = doc.querySelector("[class*='out-of-stock'], [class*='sold-out'], [class*='oos']");
      stockStatus = oosEl ? "OutOfStock" : "InStock";
    }

    const promoDeal = findPromoText(doc);

    if (!name) return null;

    return {
      sku: sku || null,
      name,
      original_price: originalPrice,
      sale_price: salePrice,
      promo_deal: promoDeal,
      stock_status: stockStatus,
      url,
      image_url: imageUrl,
    };
  }

  global.BBWCapture = global.BBWCapture || {};
  global.BBWCapture.extract = extract;
})(typeof window !== "undefined" ? window : globalThis);
