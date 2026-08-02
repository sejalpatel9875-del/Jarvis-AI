// J.A.R.V.I.S. Enterprise AI OS Dashboard Controller (v5.8.0)
const BACKEND_URL = "https://jarvis-ai-production-eb13.up.railway.app";
let pollInterval = null;

document.addEventListener("DOMContentLoaded", () => {
  initDashboard();
  setupKeyboardShortcuts();
  setupSearchFilter();
  setupExportModal();
});

// Initialize Telemetry Data & Polling
function initDashboard() {
  fetchTelemetry();
  pollInterval = setInterval(fetchTelemetry, 5000); // 5s Heartbeat
}

async function fetchTelemetry() {
  const workspaceId = document.getElementById("workspace-select").value || "default";
  try {
    const res = await fetch(`${BACKEND_URL}/api/v1/dashboard/telemetry?workspace_id=${workspaceId}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    renderWidgets(data.widgets);
    document.getElementById("last-updated-text").textContent = `Last Updated: ${new Date().toLocaleTimeString()}`;
  } catch (err) {
    console.warn("Telemetry polling offline fallback:", err);
  }
}

// Render Data Across All 11 Widgets
function renderWidgets(widgets) {
  if (!widgets) return;

  // 1. AI Usage
  document.getElementById("ai-total-requests").textContent = widgets.ai_usage.total_requests.toLocaleString();

  // 2. Automation Status
  document.getElementById("active-workflows").textContent = `${widgets.automation_status.active_workflows} Active`;

  // 3. Task Queue
  document.getElementById("active-tasks").textContent = `${widgets.task_queue.active_tasks} Running`;

  // 4. Notifications
  document.getElementById("unread-count").textContent = `${widgets.notifications.unread_count} Unread`;

  // 5. Knowledge Base
  document.getElementById("indexed-docs").textContent = `${widgets.knowledge_base.indexed_documents} Documents`;

  // 6. Memory Statistics
  document.getElementById("saved-facts").textContent = `${widgets.memory_stats.saved_facts} Memory Facts`;

  // 7. Performance Metrics
  document.getElementById("cpu-telemetry").textContent = `CPU: ${widgets.performance_metrics.cpu_usage_percent}%`;

  // 9. User Activity
  document.getElementById("active-users").textContent = `${widgets.user_activity.active_users_today} Active Users`;

  // 11. Revenue Dashboard
  document.getElementById("mrr-value").textContent = `$${widgets.revenue_dashboard.mrr_usd.toLocaleString()} MRR`;
}

// Global Search Filter
function setupSearchFilter() {
  const searchInput = document.getElementById("global-search");
  searchInput.addEventListener("input", (e) => {
    const query = e.target.value.toLowerCase().trim();
    const cards = document.querySelectorAll(".widget-card");

    cards.forEach(card => {
      const text = card.textContent.toLowerCase();
      if (!query || text.includes(query)) {
        card.style.display = "flex";
      } else {
        card.style.display = "none";
      }
    });
  });
}

// Keyboard Shortcuts Engine
function setupKeyboardShortcuts() {
  document.addEventListener("keydown", (e) => {
    // Cmd/Ctrl + K -> Focus Search
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      document.getElementById("global-search").focus();
    }
    // Cmd/Ctrl + E -> Open Export Modal
    else if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'e') {
      e.preventDefault();
      openExportModal();
    }
    // Cmd/Ctrl + R -> Manual Refresh
    else if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'r') {
      e.preventDefault();
      fetchTelemetry();
    }
  });
}

// Export Report Modal Controller
function setupExportModal() {
  const exportBtn = document.getElementById("export-report-btn");
  const modal = document.getElementById("export-modal");
  const closeBtn = document.getElementById("close-modal-btn");
  const confirmBtn = document.getElementById("confirm-export-btn");

  exportBtn.addEventListener("click", openExportModal);
  closeBtn.addEventListener("click", () => modal.classList.add("hidden"));

  confirmBtn.addEventListener("click", async () => {
    const format = document.getElementById("export-format").value;
    const workspaceId = document.getElementById("workspace-select").value || "default";

    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/dashboard/export?format=${format}&workspace_id=${workspaceId}`);
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `jarvis_executive_report_${Date.now()}.${format === 'markdown' ? 'md' : format}`;
      a.click();
      modal.classList.add("hidden");
    } catch (err) {
      alert(`Export failed: ${err.message}`);
    }
  });
}

function openExportModal() {
  document.getElementById("export-modal").classList.remove("hidden");
}
