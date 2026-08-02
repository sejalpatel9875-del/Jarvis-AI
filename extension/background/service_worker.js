// J.A.R.V.I.S. AI OS Extension — Background Service Worker (Manifest V3)
const BACKEND_URL = "https://jarvis-ai-production-eb13.up.railway.app";

// 1. Initialize Context Menus on Installation
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "jarvis_summarize",
    title: "📝 Summarize Selection with JARVIS",
    contexts: ["selection"]
  });

  chrome.contextMenus.create({
    id: "jarvis_translate",
    title: "🌐 Translate Selection with JARVIS",
    contexts: ["selection"]
  });

  chrome.contextMenus.create({
    id: "jarvis_email",
    title: "✉️ Draft Email Response",
    contexts: ["selection"]
  });

  chrome.contextMenus.create({
    id: "jarvis_save_note",
    title: "💾 Save to JARVIS Notes",
    contexts: ["selection"]
  });
});

// 2. Handle Context Menu Clicks
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  const selectedText = info.selectionText || "";
  if (!selectedText) return;

  if (info.menuItemId === "jarvis_summarize") {
    const summary = await callJarvisApi("/api/v1/chat", { message: `Summarize this text: ${selectedText}` });
    sendToTab(tab.id, { action: "SHOW_OVERLAY", title: "📝 JARVIS Summary", text: summary.response || "Summary generated." });
  } else if (info.menuItemId === "jarvis_translate") {
    const translation = await callJarvisApi("/api/v1/chat", { message: `Translate to Hindi and English: ${selectedText}` });
    sendToTab(tab.id, { action: "SHOW_OVERLAY", title: "🌐 JARVIS Translation", text: translation.response || "Translation generated." });
  } else if (info.menuItemId === "jarvis_email") {
    const emailDraft = await callJarvisApi("/api/v1/chat", { message: `Draft a professional email based on: ${selectedText}` });
    sendToTab(tab.id, { action: "SHOW_OVERLAY", title: "✉️ JARVIS Email Draft", text: emailDraft.response || "Email generated." });
  } else if (info.menuItemId === "jarvis_save_note") {
    await callJarvisApi("/api/v1/reminders", { workspace_id: "default", title: `Web Note: ${selectedText.substring(0, 50)}...` });
    sendToTab(tab.id, { action: "SHOW_OVERLAY", title: "💾 Note Saved", text: "Saved to JARVIS Long-Term Memory Notes." });
  }
});

// 3. Message Listener for Popup and Content Scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "CAPTURE_SCREENSHOT") {
    chrome.tabs.captureVisibleTab(null, { format: "png" }, (dataUrl) => {
      sendResponse({ status: "SUCCESS", dataUrl: dataUrl });
    });
    return true; // Keep channel open for async response
  } else if (request.action === "GET_TABS") {
    chrome.tabs.query({}, (tabs) => {
      const tabData = tabs.map(t => ({ id: t.id, title: t.title, url: t.url, active: t.active }));
      sendResponse({ tabs: tabData });
    });
    return true;
  } else if (request.action === "CLOSE_DUPLICATES") {
    closeDuplicateTabs().then(count => sendResponse({ closedCount: count }));
    return true;
  }
});

// 4. Helper: API Call to JARVIS Backend
async function callJarvisApi(endpoint, payload) {
  try {
    const res = await fetch(`${BACKEND_URL}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    return await res.json();
  } catch (err) {
    return { response: `API Error: ${err.message}` };
  }
}

// 5. Helper: Send Message to Active Tab Content Script
function sendToTab(tabId, message) {
  if (tabId) {
    chrome.tabs.sendMessage(tabId, message);
  }
}

// 6. Helper: Tab Management - Close Duplicates
async function closeDuplicateTabs() {
  const tabs = await chrome.tabs.query({});
  const urlsSeen = new Set();
  let closedCount = 0;

  for (const tab of tabs) {
    if (urlsSeen.has(tab.url)) {
      await chrome.tabs.remove(tab.id);
      closedCount++;
    } else {
      urlsSeen.add(tab.url);
    }
  }
  return closedCount;
}
