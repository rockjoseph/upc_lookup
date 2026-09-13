const DEFAULT_TRACKER_URL = "http://localhost:5173";

const input = document.getElementById("tracker-url");
const status = document.getElementById("status");

chrome.storage.sync.get(["trackerUrl"], ({ trackerUrl }) => {
  input.value = trackerUrl || DEFAULT_TRACKER_URL;
});

document.getElementById("save").addEventListener("click", () => {
  const value = input.value.trim() || DEFAULT_TRACKER_URL;
  chrome.storage.sync.set({ trackerUrl: value }, () => {
    status.textContent = "Saved.";
    setTimeout(() => (status.textContent = ""), 1500);
  });
});
