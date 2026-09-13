/**
 * Injects a small floating button on bathandbodyworks.com product pages.
 * Clicking it extracts the product (via extract.js) and hands it to the
 * background service worker, which stores it and focuses/opens the
 * tracker app tab.
 *
 * bathandbodyworks.com is a client-side-routed React app: navigating from
 * a search/category page to a product page updates the URL via the
 * History API without a full page load, which means a Manifest V3
 * content script matched only against "/p/*" would never (re-)inject on
 * that navigation -- you'd have to hard-refresh to see the button. To
 * avoid that, this script is injected on the whole domain (see
 * manifest.json) and watches for both real and SPA-style navigation,
 * showing/hiding the button based on the *current* URL rather than only
 * running once at initial page load.
 */
(function () {
  "use strict";

  const BUTTON_ID = "bbw-price-tracker-capture-btn";

  function isProductPage() {
    return /\/p\//.test(location.pathname);
  }

  function removeButton() {
    const btn = document.getElementById(BUTTON_ID);
    if (btn) btn.remove();
  }

  function injectButton() {
    if (!isProductPage()) {
      removeButton();
      return;
    }
    if (document.getElementById(BUTTON_ID)) return;

    const btn = document.createElement("button");
    btn.id = BUTTON_ID;
    btn.textContent = "📥 Send to Price Tracker";
    Object.assign(btn.style, {
      position: "fixed",
      bottom: "20px",
      right: "20px",
      zIndex: "2147483647",
      background: "#db2777",
      color: "#fff",
      border: "none",
      borderRadius: "9999px",
      padding: "12px 18px",
      fontSize: "14px",
      fontWeight: "600",
      fontFamily: "system-ui, sans-serif",
      boxShadow: "0 4px 14px rgba(0,0,0,0.25)",
      cursor: "pointer",
    });

    btn.addEventListener("click", handleCapture);
    document.body.appendChild(btn);
  }

  function setButtonState(state) {
    const btn = document.getElementById(BUTTON_ID);
    if (!btn) return;
    if (state === "sending") {
      btn.textContent = "Sending...";
      btn.disabled = true;
    } else if (state === "sent") {
      btn.textContent = "✓ Sent to Price Tracker";
      setTimeout(() => {
        btn.textContent = "📥 Send to Price Tracker";
        btn.disabled = false;
      }, 2500);
    } else if (state === "error") {
      btn.textContent = "⚠ Could not read product -- see console";
      setTimeout(() => {
        btn.textContent = "📥 Send to Price Tracker";
        btn.disabled = false;
      }, 3000);
    }
  }

  function handleCapture() {
    const product = window.BBWCapture.extract(document, location.href);
    if (!product) {
      console.error("[BBW Price Tracker] Could not extract product data from this page.");
      setButtonState("error");
      return;
    }
    setButtonState("sending");
    chrome.runtime.sendMessage({ type: "BBW_CAPTURE_PRODUCT", product }, (response) => {
      if (chrome.runtime.lastError || !response || !response.ok) {
        console.error(
          "[BBW Price Tracker] Failed to hand off captured product:",
          chrome.runtime.lastError || response
        );
        setButtonState("error");
        return;
      }
      setButtonState("sent");
    });
  }

  // Detect client-side (History API) navigation, since a real
  // document-level navigation event never fires when the SPA routes from
  // e.g. a search results page to a product page -- pushState/replaceState
  // are the only signal. injectButton() is idempotent (it checks
  // isProductPage() and whether the button already exists), so it's safe
  // to call liberally on any of these signals.
  ["pushState", "replaceState"].forEach((method) => {
    const original = history[method];
    history[method] = function (...args) {
      const result = original.apply(this, args);
      injectButton();
      return result;
    };
  });
  window.addEventListener("popstate", injectButton);

  injectButton();
  // Belt-and-suspenders: also re-check on DOM swaps that don't go through
  // pushState/replaceState (e.g. a re-render that replaces <body>'s
  // contents in place).
  new MutationObserver(injectButton).observe(document.body, { childList: true, subtree: true });
})();
