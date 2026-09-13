/**
 * Injects a small floating button on bathandbodyworks.com product pages.
 * Clicking it extracts the product (via extract.js) and hands it to the
 * background service worker, which stores it and focuses/opens the
 * tracker app tab.
 */
(function () {
  "use strict";

  const BUTTON_ID = "bbw-price-tracker-capture-btn";

  function injectButton() {
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

  injectButton();
  // Re-inject if the page is a single-page app that swaps content without a
  // full reload (BBW's PDP can update via client-side routing).
  new MutationObserver(injectButton).observe(document.body, { childList: true, subtree: true });
})();
