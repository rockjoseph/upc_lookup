/**
 * Runs on the Price Tracker frontend itself (localhost/127.0.0.1). Listens
 * for a "deliver the captured product now" ping from the background
 * service worker, reads the pending product from extension storage, and
 * relays it into the page via window.postMessage -- the frontend's own
 * script (App.jsx) listens for this and renders it exactly like a normal
 * search result, so the existing Excel add/upsert/download flow is reused
 * unchanged.
 */
(function () {
  "use strict";

  function deliverPendingCapture() {
    chrome.storage.local.get(["pendingCapture"], (result) => {
      const product = result && result.pendingCapture;
      if (!product) return;
      window.postMessage({ __bbwPriceTrackerCapture: true, product }, window.location.origin);
      chrome.storage.local.remove("pendingCapture");
    });
  }

  chrome.runtime.onMessage.addListener((message) => {
    if (message && message.type === "BBW_DELIVER_CAPTURE") {
      deliverPendingCapture();
    }
  });

  // Also deliver on load, in case the tab was just opened/focused by the
  // background script for this exact purpose and the message races the
  // page's own load.
  deliverPendingCapture();
})();
