// J.A.R.V.I.S. AI OS Extension — Content Script

// Listen for Messages from Background Service Worker
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "EXTRACT_PAGE_TEXT") {
    const pageText = document.body.innerText.replace(/\s+/g, ' ').trim();
    sendResponse({ pageText: pageText.substring(0, 5000), title: document.title });
  } else if (request.action === "SHOW_OVERLAY") {
    showJarvisOverlay(request.title, request.text);
  } else if (request.action === "TOGGLE_READING_MODE") {
    toggleReadingMode();
  }
});

// Inject Glassmorphism Overlay
function showJarvisOverlay(title, text) {
  let existing = document.getElementById("jarvis-extension-overlay");
  if (existing) existing.remove();

  const overlay = document.createElement("div");
  overlay.id = "jarvis-extension-overlay";
  overlay.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    width: 360px;
    max-height: 80vh;
    background: rgba(17, 24, 39, 0.95);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(99, 102, 241, 0.4);
    border-radius: 12px;
    color: #F3F4F6;
    font-family: system-ui, -apple-system, sans-serif;
    padding: 16px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
    z-index: 999999;
    overflow-y: auto;
  `;

  overlay.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
      <strong style="color:#6366F1; font-size:14px;">${title}</strong>
      <button id="jarvis-close-btn" style="background:none; border:none; color:#9CA3AF; font-size:16px; cursor:pointer;">✕</button>
    </div>
    <div style="font-size:13px; line-height:1.5; white-space:pre-wrap;">${text}</div>
  `;

  document.body.appendChild(overlay);

  document.getElementById("jarvis-close-btn").addEventListener("click", () => {
    overlay.remove();
  });
}

// Distraction-Free Reading Mode
let isReadingModeActive = false;
function toggleReadingMode() {
  isReadingModeActive = !isReadingModeActive;
  let readingContainer = document.getElementById("jarvis-reading-mode-container");

  if (isReadingModeActive) {
    if (!readingContainer) {
      readingContainer = document.createElement("div");
      readingContainer.id = "jarvis-reading-mode-container";
      readingContainer.style.cssText = `
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: #090D16;
        color: #E5E7EB;
        font-family: Georgia, serif;
        font-size: 18px;
        line-height: 1.8;
        padding: 40px 20%;
        overflow-y: auto;
        z-index: 999998;
      `;
      readingContainer.innerHTML = `
        <button id="jarvis-exit-reading" style="position:fixed; top:20px; right:20px; background:#6366F1; color:#fff; border:none; padding:8px 16px; border-radius:8px; cursor:pointer;">Exit Reading Mode</button>
        <h1 style="color:#6366F1;">${document.title}</h1>
        <hr style="border-color:#1F2937; margin: 20px 0;">
        <div>${document.body.innerText.replace(/\s+/g, ' ')}</div>
      `;
      document.body.appendChild(readingContainer);
      document.getElementById("jarvis-exit-reading").addEventListener("click", toggleReadingMode);
    }
  } else if (readingContainer) {
    readingContainer.remove();
  }
}
