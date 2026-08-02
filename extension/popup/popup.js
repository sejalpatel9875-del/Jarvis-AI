// J.A.R.V.I.S. AI OS Extension — Popup Controller
const BACKEND_URL = "https://jarvis-ai-production-eb13.up.railway.app";

document.addEventListener("DOMContentLoaded", () => {
  setupTabs();
  setupChat();
  setupSummarizer();
  setupNotes();
  setupTools();
});

// Tab Navigation
function setupTabs() {
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));

      tab.classList.add("active");
      const target = tab.getAttribute("data-tab");
      document.getElementById(target).classList.add("active");
    });
  });
}

// Quick AI Chat
function setupChat() {
  const sendBtn = document.getElementById("send-btn");
  const chatInput = document.getElementById("chat-input");
  const chatBox = document.getElementById("chat-box");

  async function handleSend() {
    const text = chatInput.value.trim();
    if (!text) return;

    appendMsg("User", text, "user");
    chatInput.value = "";

    appendMsg("JARVIS", "Thinking...", "jarvis");
    const lastJarvisMsg = chatBox.lastElementChild;

    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      lastJarvisMsg.textContent = data.response || "No response received.";
    } catch (err) {
      lastJarvisMsg.textContent = `Error: ${err.message}`;
    }
  }

  sendBtn.addEventListener("click", handleSend);
  chatInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") handleSend();
  });

  function appendMsg(sender, text, cls) {
    const div = document.createElement("div");
    div.className = `msg ${cls}`;
    div.textContent = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
  }
}

// Page Summarizer
function setupSummarizer() {
  const btn = document.getElementById("summarize-page-btn");
  const output = document.getElementById("summary-output");

  btn.addEventListener("click", () => {
    output.textContent = "Extracting page content...";
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (!tabs[0]) return;
      chrome.tabs.sendMessage(tabs[0].id, { action: "EXTRACT_PAGE_TEXT" }, async (res) => {
        if (!res || !res.pageText) {
          output.textContent = "Unable to extract page text from this tab.";
          return;
        }

        output.textContent = "Generating AI Summary...";
        try {
          const apiRes = await fetch(`${BACKEND_URL}/api/v1/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: `Summarize this webpage titled '${res.title}': ${res.pageText}` })
          });
          const data = await apiRes.json();
          output.textContent = data.response || "Summary completed.";
        } catch (err) {
          output.textContent = `Failed to generate summary: ${err.message}`;
        }
      });
    });
  });
}

// Notes
function setupNotes() {
  const saveBtn = document.getElementById("save-note-btn");
  const noteInput = document.getElementById("note-input");
  const status = document.getElementById("note-status");

  saveBtn.addEventListener("click", async () => {
    const noteText = noteInput.value.trim();
    if (!noteText) return;

    status.textContent = "Saving note to JARVIS...";
    try {
      await fetch(`${BACKEND_URL}/api/v1/reminders`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ workspace_id: "default", title: noteText })
      });
      status.textContent = "✅ Note saved successfully!";
      noteInput.value = "";
    } catch (err) {
      status.textContent = `❌ Failed to save: ${err.message}`;
    }
  });
}

// Tools (Reading Mode, Screenshot, Tab Management)
function setupTools() {
  const readingBtn = document.getElementById("reading-mode-btn");
  const shotBtn = document.getElementById("screenshot-btn");
  const closeDupesBtn = document.getElementById("close-duplicates-btn");

  readingBtn.addEventListener("click", () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        chrome.tabs.sendMessage(tabs[0].id, { action: "TOGGLE_READING_MODE" });
      }
    });
  });

  shotBtn.addEventListener("click", () => {
    chrome.runtime.sendMessage({ action: "CAPTURE_SCREENSHOT" }, (res) => {
      if (res && res.dataUrl) {
        const a = document.createElement("a");
        a.href = res.dataUrl;
        a.download = `jarvis_shot_${Date.now()}.png`;
        a.click();
      }
    });
  });

  closeDupesBtn.addEventListener("click", () => {
    chrome.runtime.sendMessage({ action: "CLOSE_DUPLICATES" }, (res) => {
      alert(`Closed ${res ? res.closedCount : 0} duplicate tab(s).`);
    });
  });
}
