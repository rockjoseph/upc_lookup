/**
 * Service worker: receives a captured product from bbw_capture.js, stores
 * it, and focuses (or opens) a tab pointed at the Price Tracker frontend so
 * tracker_bridge.js can deliver it into the page.
 */
const DEFAULT_TRACKER_URL = "http://localhost:5173";

async function getTrackerUrl() {
  const { trackerUrl } = await chrome.storage.sync.get(["trackerUrl"]);
  return trackerUrl || DEFAULT_TRACKER_URL;
}

async function focusOrOpenTrackerTab(trackerUrl) {
  const trackerOrigin = new URL(trackerUrl).origin;
  const tabs = await chrome.tabs.query({});
  const existing = tabs.find((t) => t.url && t.url.startsWith(trackerOrigin));

  if (existing) {
    await chrome.tabs.update(existing.id, { active: true });
    await chrome.windows.update(existing.windowId, { focused: true });
    return existing.id;
  }

  const created = await chrome.tabs.create({ url: trackerUrl });
  return created.id;
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message && message.type === "BBW_CAPTURE_PRODUCT") {
    (async () => {
      try {
        await chrome.storage.local.set({ pendingCapture: message.product });
        const trackerUrl = await getTrackerUrl();
        const tabId = await focusOrOpenTrackerTab(trackerUrl);

        // Give a freshly-created tab a moment to load its content script
        // before pinging it; an already-open tab gets pinged immediately.
        setTimeout(() => {
          chrome.tabs.sendMessage(tabId, { type: "BBW_DELIVER_CAPTURE" }).catch(() => {
            // Tab may still be loading -- tracker_bridge.js also delivers
            // on its own load, so this isn't fatal.
          });
        }, 800);

        sendResponse({ ok: true });
      } catch (err) {
        sendResponse({ ok: false, error: String(err) });
      }
    })();
    return true; // keep the message channel open for the async response
  }
});
