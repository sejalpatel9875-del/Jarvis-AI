/**
 * J.A.R.V.I.S. AI OS — Web Dashboard Client Application Logic
 */

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const navItems = document.querySelectorAll(".nav-item");
    const tabContents = document.querySelectorAll(".tab-content");
    const chatForm = document.getElementById("chatForm");
    const userInput = document.getElementById("userInput");
    const chatMessages = document.getElementById("chatMessages");
    const clearChatBtn = document.getElementById("clearChatBtn");
    const voiceBtn = document.getElementById("voiceBtn");
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("fileInput");
    const uploadStatus = document.getElementById("uploadStatus");
    const ragQueryInput = document.getElementById("ragQueryInput");
    const ragQueryBtn = document.getElementById("ragQueryBtn");
    const ragResultsBox = document.getElementById("ragResultsBox");

    // 1. Navigation Tab Swapping
    navItems.forEach(item => {
        item.addEventListener("click", () => {
            navItems.forEach(i => i.classList.remove("active"));
            tabContents.forEach(c => c.classList.remove("active"));

            item.classList.add("active");
            const targetTab = item.getAttribute("data-tab");
            document.getElementById(targetTab).classList.add("active");

            if (targetTab === "metrics-tab") {
                fetchMetrics();
            }
        });
    });

    // 2. Quick Action Chips
    document.querySelectorAll(".chip").forEach(chip => {
        chip.addEventListener("click", () => {
            const prompt = chip.getAttribute("data-prompt");
            userInput.value = prompt;
            sendChatMessageStream(prompt);
        });
    });

    // 3. Clear Chat
    clearChatBtn.addEventListener("click", () => {
        chatMessages.innerHTML = `
            <div class="message-row assistant">
                <div class="avatar"><i class="fa-solid fa-robot"></i></div>
                <div class="message-bubble">
                    <p>Namaste, Boss! Chat reset complete. What would you like to do next?</p>
                </div>
            </div>
        `;
    });

    // 4. Voice Input (Web Speech API)
    if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "en-US";

        voiceBtn.addEventListener("click", () => {
            voiceBtn.style.color = "#ef4444";
            recognition.start();
        });

        recognition.onresult = (event) => {
            voiceBtn.style.color = "";
            const transcript = event.results[0][0].transcript;
            userInput.value = transcript;
            sendChatMessageStream(transcript);
        };

        recognition.onerror = () => {
            voiceBtn.style.color = "";
        };

        recognition.onend = () => {
            voiceBtn.style.color = "";
        };
    } else {
        voiceBtn.style.display = "none";
    }

    // 5. Submit Chat Form (Streaming Response)
    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (text) {
            sendChatMessageStream(text);
        }
    });

    async function sendChatMessageStream(message) {
        appendMessage("user", message);
        userInput.value = "";

        // Create Assistant Message Row for Live Token Streaming
        const row = document.createElement("div");
        row.className = "message-row assistant";
        const id = "msg_" + Date.now();
        row.id = id;

        row.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="message-bubble">
                <p id="p_${id}"><em>Jarvis is thinking...</em></p>
                <div style="font-size: 11px; color: #94a3b8; margin-top: 8px;"><i class="fa-solid fa-bolt"></i> Streaming Router &bull; Live</div>
            </div>
        `;
        chatMessages.appendChild(row);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        const pEl = document.getElementById(`p_${id}`);
        let fullText = "";

        try {
            const res = await fetch("/chat/stream", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: message })
            });

            if (!res.ok) throw new Error("API Error: " + res.statusText);

            const reader = res.body.getReader();
            const decoder = new TextDecoder("utf-8");
            pEl.innerHTML = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split("\n\n");

                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        const rawData = line.replace("data: ", "").trim();
                        if (rawData === "[DONE]") break;

                        try {
                            const parsed = JSON.parse(rawData);
                            if (parsed.token) {
                                fullText += parsed.token;
                                pEl.innerText = fullText;
                                chatMessages.scrollTop = chatMessages.scrollHeight;
                            }
                        } catch (e) {}
                    }
                }
            }

            if (!fullText) {
                pEl.innerText = "Command executed successfully, Boss.";
            }

        } catch (err) {
            pEl.innerText = "⚠️ Error communicating with Jarvis backend: " + err.message;
        }
    }

    function appendMessage(sender, text, provider = null, latency = null) {
        const row = document.createElement("div");
        row.className = `message-row ${sender}`;
        const id = "msg_" + Date.now();
        row.id = id;

        const avatarIcon = sender === "user" ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-robot"></i>';
        let metaHtml = "";
        if (provider && latency) {
            metaHtml = `<div style="font-size: 11px; color: #94a3b8; margin-top: 8px;"><i class="fa-solid fa-bolt"></i> ${provider} &bull; ${latency}s</div>`;
        }

        row.innerHTML = `
            <div class="avatar">${avatarIcon}</div>
            <div class="message-bubble">
                <p>${escapeHtml(text)}</p>
                ${metaHtml}
            </div>
        `;

        chatMessages.appendChild(row);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return id;
    }

    // 6. File Upload Logic
    dropzone.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            handleFileUpload(fileInput.files[0]);
        }
    });

    async function handleFileUpload(file) {
        uploadStatus.innerHTML = `<p style="color: #6366f1;">Uploading and indexing '${file.name}'...</p>`;
        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch("/upload", {
                method: "POST",
                body: formData
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Upload failed");

            uploadStatus.innerHTML = `<p style="color: #10b981;">✅ Indexed '${data.file_name}' (${data.total_pages} pages, ${data.total_chunks} chunks)</p>`;
        } catch (err) {
            uploadStatus.innerHTML = `<p style="color: #ef4444;">❌ ${err.message}</p>`;
        }
    }

    // 7. RAG Query Logic
    ragQueryBtn.addEventListener("click", executeRagQuery);
    ragQueryInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") executeRagQuery();
    });

    async function executeRagQuery() {
        const q = ragQueryInput.value.trim();
        if (!q) return;

        ragResultsBox.innerHTML = "<p>Searching persistent vector knowledge base...</p>";
        try {
            const res = await fetch("/documents/query", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: q, top_k: 3 })
            });

            const data = await res.json();
            if (data.total_matches === 0) {
                ragResultsBox.innerHTML = "<p>No matching content found in document index.</p>";
                return;
            }

            let html = `<h4>Matches Found (${data.total_matches})</h4>`;
            data.results.forEach(r => {
                html += `
                    <div style="background: rgba(30,41,59,0.5); padding: 12px; border-radius: 8px; margin-top: 10px;">
                        <span class="badge badge-success">Source: ${r.source_file} (Page ${r.page_number})</span>
                        <p style="margin-top: 6px; font-style: italic;">"${r.content}"</p>
                    </div>
                `;
            });
            ragResultsBox.innerHTML = html;
        } catch (err) {
            ragResultsBox.innerHTML = `<p style="color: #ef4444;">Error: ${err.message}</p>`;
        }
    }

    // 8. Telemetry Metrics Fetching
    async function fetchMetrics() {
        try {
            const res = await fetch("/metrics");
            const data = await res.json();
            document.getElementById("groqCallsCount").innerText = data.groq_calls;
            document.getElementById("geminiCallsCount").innerText = data.gemini_calls;
            document.getElementById("ollamaCallsCount").innerText = data.ollama_calls;
            document.getElementById("avgLatencyValue").innerText = data.avg_latency.toFixed(2) + "s";
        } catch (err) {
            console.error("Failed to fetch metrics", err);
        }
    }

    function escapeHtml(text) {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
