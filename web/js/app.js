if (!isLoggedIn()) {
  location.href = "/login.html";
}

const statusEl = document.getElementById("status");
const outputEl = document.getElementById("output");
const progressWrap = document.getElementById("progress-wrap");
const progressBar = document.getElementById("progress-bar");

function showStatus(msg) {
  statusEl.textContent = msg || "";
}

checkServer().then((ok) => {
  if (!ok) {
    showStatus("Backend offline — run run.cmd and keep the terminal open.");
  }
});

function showOutput(text) {
  outputEl.textContent = text || "";
  outputEl.classList.toggle("show", !!text);
}

let confirmResolve = null;

function showConfirm({
  title = "Confirm",
  message = "",
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  danger = false,
}) {
  return new Promise((resolve) => {
    const dialog = document.getElementById("confirm-dialog");
    document.getElementById("confirm-dialog-title").textContent = title;
    document.getElementById("confirm-dialog-message").textContent = message;
    const okBtn = document.getElementById("confirm-dialog-ok");
    okBtn.textContent = confirmLabel;
    okBtn.className = danger ? "btn btn-danger" : "btn btn-primary";
    document.getElementById("confirm-dialog-cancel").textContent = cancelLabel;
    confirmResolve = resolve;
    dialog.showModal();
  });
}

(function initConfirmDialog() {
  const dialog = document.getElementById("confirm-dialog");
  const finish = (value) => {
    if (confirmResolve) confirmResolve(value);
    confirmResolve = null;
  };
  document.getElementById("confirm-dialog-cancel").onclick = () => {
    dialog.close();
    finish(false);
  };
  document.getElementById("confirm-dialog-ok").onclick = () => {
    dialog.close();
    finish(true);
  };
  dialog.addEventListener("cancel", (e) => {
    e.preventDefault();
    dialog.close();
    finish(false);
  });
})();

function setProgress(pct) {
  if (pct > 0) {
    progressWrap.style.display = "block";
    progressBar.style.width = Math.min(pct, 100) + "%";
  } else {
    progressWrap.style.display = "none";
    progressBar.style.width = "0%";
  }
}

function formatDoneStatus() {
  return "Done";
}

function getChipValue(optionName) {
  const group = document.querySelector('[data-option="' + optionName + '"]');
  if (!group) return null;
  const active = group.querySelector(".chip.active");
  return active ? active.dataset.value : null;
}

document.querySelectorAll(".options").forEach((group) => {
  group.querySelectorAll(".chip").forEach((chip) => {
    chip.onclick = () => {
      group.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
    };
  });
});

const VALID_PANELS = [
  "summarizer",
  "translator",
  "paraphraser",
  "humanizer",
  "plagiarism",
  "ai_detection",
  "ocr",
  "voice",
  "youtube",
  "history",
];

function showPanel(panel, options = {}) {
  if (!VALID_PANELS.includes(panel)) panel = "summarizer";
  document.querySelectorAll("#nav a").forEach((a) => {
    a.classList.toggle("active", a.dataset.panel === panel);
  });
  const navHistory = document.getElementById("nav-history");
  if (navHistory) navHistory.classList.toggle("active", panel === "history");
  document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
  const el = document.getElementById("panel-" + panel);
  if (!el) return;
  el.classList.add("active");
  if (!options.keepOutput) {
    showOutput("");
    showStatus("");
    setProgress(0);
  }
  if (panel === "history") loadHistory();
  if (!options.skipUrl) {
    const url = new URL(location.href);
    url.searchParams.set("panel", panel);
    history.replaceState(null, "", url.pathname + url.search);
  }
}

document.getElementById("nav").querySelectorAll("a").forEach((link) => {
  link.onclick = (e) => {
    e.preventDefault();
    showPanel(link.dataset.panel);
  };
});

const navHistory = document.getElementById("nav-history");
if (navHistory) {
  navHistory.onclick = (e) => {
    e.preventDefault();
    showPanel("history");
  };
}

const initialPanel = new URLSearchParams(location.search).get("panel");
if (initialPanel && VALID_PANELS.includes(initialPanel)) {
  showPanel(initialPanel, { skipUrl: true });
} else if (initialPanel) {
  showPanel("summarizer", { skipUrl: true });
}

document.getElementById("logout").onclick = () => {
  clearTokens();
  location.href = "/login.html";
};

document.getElementById("lang-swap").onclick = () => {
  const src = document.getElementById("lang-src");
  const tgt = document.getElementById("lang-tgt");
  const tmp = src.value;
  src.value = tgt.value;
  tgt.value = tmp;
};

apiFetch("/auth/me/").then(async (res) => {
  if (!res.ok) {
    location.href = "/login.html";
    return;
  }
  const user = await res.json();
  document.getElementById("user-email").textContent = user.email;
});

document.querySelectorAll(".tool-run").forEach((btn) => {
  btn.onclick = async () => {
    const endpoint = btn.dataset.endpoint;
    const fileInputId = btn.dataset.file;
    const file = fileInputId ? document.getElementById(fileInputId)?.files?.[0] : null;
    const text = btn.dataset.text ? document.getElementById(btn.dataset.text)?.value?.trim() : "";
    if (!file && !text) {
      showStatus("Paste text or upload a file first.");
      return;
    }
    let options = {};
    if (btn.dataset.options) {
      options[btn.dataset.options] = getChipValue(btn.dataset.options);
    }
    if (btn.dataset.lang) {
      options.source_language = document.getElementById("lang-src").value;
      options.target_language = document.getElementById("lang-tgt").value;
    }
    btn.disabled = true;
    showOutput("");
    const isSlow =
      endpoint.includes("humanizer") || endpoint.includes("ai-detection");
    showStatus(isSlow ? "Processing… (may take 1–2 min)" : "Processing...");
    setProgress(30);
    try {
      const result = file
        ? await runFileTool(endpoint, file, options)
        : await runTextTool(endpoint, text, options);
      setProgress(100);
      showStatus(formatDoneStatus());
      showOutput(result.output_text || JSON.stringify(result, null, 2));
    } catch (ex) {
      showStatus("Error: " + ex.message);
      setProgress(0);
    }
    btn.disabled = false;
  };
});

function setupFileUpload(zoneId, inputId, endpoint, options) {
  const zone = document.getElementById(zoneId);
  const input = document.getElementById(inputId);
  zone.onclick = () => input.click();
  input.onchange = async () => {
    const file = input.files[0];
    if (!file) return;
    const isVoice = endpoint.includes("voice");
    showStatus("Uploading...");
    setProgress(20);
    try {
      const result = await runFileTool(endpoint, file, options || {});
      setProgress(100);
      if (endpoint.includes("ocr")) showStatus("Done — text extracted");
      else if (endpoint.includes("voice")) showStatus("Done — transcribed");
      else showStatus("Done");
      showOutput(result.output_text || "");
    } catch (ex) {
      showStatus("Error: " + ex.message);
      setProgress(0);
    }
    input.value = "";
  };
}

function setupFilePicker(zoneId, inputId, placeholderText) {
  const zone = document.getElementById(zoneId);
  const input = document.getElementById(inputId);
  if (!zone || !input) return;
  zone.onclick = () => input.click();
  input.onchange = () => {
    const file = input.files?.[0];
    if (!file) {
      zone.textContent = placeholderText || "Click to upload";
      return;
    }
    zone.textContent = `Selected: ${file.name} (click to change)`;
  };
}

document.getElementById("plagiarism-run").onclick = async () => {
  const fileA = document.getElementById("plagiarism-a-file")?.files?.[0] || null;
  const fileB = document.getElementById("plagiarism-b-file")?.files?.[0] || null;
  const textA = (document.getElementById("text-plagiarism-a")?.value || "").trim();
  const textB = (document.getElementById("text-plagiarism-b")?.value || "").trim();

  if (!fileA && !textA) {
    showStatus("Provide Document A as text or upload a file.");
    return;
  }
  if (!fileB && !textB) {
    showStatus("Provide Document B as text or upload a file.");
    return;
  }
  const btn = document.getElementById("plagiarism-run");
  btn.disabled = true;
  showOutput("");
  showStatus("Checking...");
  setProgress(30);
  try {
    // If Document B is a file, upload it first and pass its id in options.
    let options = {};
    if (fileB) {
      showStatus("Uploading Document B...");
      setProgress(20);
      const uploadedB = await uploadFile(fileB);
      options.comparison_file_id = uploadedB.id;
    } else {
      options.comparison_text = textB;
    }

    let result;
    if (fileA) {
      showStatus("Uploading Document A...");
      setProgress(30);
      result = await runFileTool("/plagiarism/run/", fileA, options);
    } else {
      result = await runTextTool("/plagiarism/run/", textA, options);
    }
    setProgress(100);
    showStatus(formatDoneStatus());
    showOutput(result.output_text || "");
  } catch (ex) {
    showStatus("Error: " + ex.message);
    setProgress(0);
  }
  btn.disabled = false;
};

// File pickers (don't auto-run; Run button uses selected file + options).
setupFilePicker("summarizer-zone", "summarizer-file", "Or upload PDF/DOCX");
setupFilePicker("paraphraser-zone", "paraphraser-file", "Or upload PDF/DOCX");
setupFilePicker("plagiarism-a-zone", "plagiarism-a-file", "Or upload PDF/DOCX for Document A");
setupFilePicker("plagiarism-b-zone", "plagiarism-b-file", "Or upload PDF/DOCX for Document B");

setupFileUpload("ocr-zone", "ocr-file", "/ocr/run/");
setupFileUpload("voice-zone", "voice-file", "/voice/run/", { model_size: "small" });

document.getElementById("youtube-run").onclick = async () => {
  const url = document.getElementById("youtube-url").value.trim();
  if (!url) {
    showStatus("Paste a YouTube URL first.");
    return;
  }
  const btn = document.getElementById("youtube-run");
  btn.disabled = true;
  showOutput("");
  showStatus("Fetching transcript and summarizing…");
  setProgress(25);
  try {
    const res = await apiFetch("/youtube/run/", {
      method: "POST",
      body: JSON.stringify({ input_type: "url", url, options: {} }),
    });
    const data = await parseJson(res);
    if (!data.task_id) throw new Error("No task started");
    const result = await pollTask(data.task_id, (d) => setProgress(d.progress || 50));
    setProgress(100);
    showStatus("Done — video summarized");
    showOutput(result.result?.output_text || "");
  } catch (ex) {
    showStatus("Error: " + ex.message);
    setProgress(0);
  }
  btn.disabled = false;
};

let historySearchTimer = null;
let historyPage = 1;
let historyItems = [];
let historyEditingId = null;
let historyHasNext = false;
let historyHasPrev = false;

const HISTORY_RERUN_FEATURES = [
  "summarizer",
  "translator",
  "paraphraser",
  "humanizer",
  "plagiarism",
  "ai_detection",
  "youtube",
];

function escHtml(s) {
  if (!s) return "";
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function historyFilterParams(includePage = true) {
  const params = new URLSearchParams();
  if (includePage) params.set("page", String(historyPage));

  const q = document.getElementById("history-search").value.trim();
  const feature = document.getElementById("history-feature").value;
  const status = document.getElementById("history-status").value;
  const starred = document.getElementById("history-starred-only").checked;
  const dateFrom = document.getElementById("history-date-from").value;
  const dateTo = document.getElementById("history-date-to").value;

  if (q) params.set("search", q);
  if (feature) params.set("feature", feature);
  if (status) params.set("status", status);
  if (starred) params.set("is_starred", "true");
  if (dateFrom) params.set("created_after", dateFrom + "T00:00:00");
  if (dateTo) params.set("created_before", dateTo + "T23:59:59");

  return params;
}

function syncHistoryDateInputs() {
  const preset = document.getElementById("history-date-preset").value;
  const fromEl = document.getElementById("history-date-from");
  const toEl = document.getElementById("history-date-to");
  fromEl.classList.toggle("history-date-hidden", preset !== "custom");
  toEl.classList.toggle("history-date-hidden", preset !== "custom");

  if (preset === "") {
    fromEl.value = "";
    toEl.value = "";
    return;
  }
  if (preset === "custom") return;

  const today = new Date();
  const fmt = (d) => d.toISOString().slice(0, 10);
  if (preset === "today") {
    fromEl.value = fmt(today);
    toEl.value = fmt(today);
  } else if (preset === "week") {
    const start = new Date(today);
    start.setDate(today.getDate() - today.getDay());
    fromEl.value = fmt(start);
    toEl.value = fmt(today);
  } else if (preset === "month") {
    fromEl.value = fmt(new Date(today.getFullYear(), today.getMonth(), 1));
    toEl.value = fmt(today);
  }
}

function updateHistoryBulkBar() {
  const list = document.getElementById("history-list");
  const checked = list.querySelectorAll(".history-select:checked");
  document.getElementById("history-bulk-delete").disabled = checked.length === 0;
  document.getElementById("history-selected-count").textContent = checked.length
    ? checked.length + " selected"
    : "";
  const all = list.querySelectorAll(".history-select");
  const selectAll = document.getElementById("history-select-all");
  if (all.length) {
    selectAll.checked = checked.length === all.length;
    selectAll.indeterminate = checked.length > 0 && checked.length < all.length;
  } else {
    selectAll.checked = false;
    selectAll.indeterminate = false;
  }
}

function updateHistoryPagination() {
  const pag = document.getElementById("history-pagination");
  const show = historyHasNext || historyHasPrev || historyPage > 1;
  pag.hidden = !show;
  document.getElementById("history-prev").disabled = !historyHasPrev;
  document.getElementById("history-next").disabled = !historyHasNext;
  document.getElementById("history-page-info").textContent = "Page " + historyPage;
}

function resetHistoryPageAndLoad() {
  historyPage = 1;
  document.getElementById("history-select-all").checked = false;
  loadHistory();
}

async function toggleStar(id, starred) {
  const res = await apiFetch("/history/" + id + "/", {
    method: "PATCH",
    body: JSON.stringify({ is_starred: !starred }),
  });
  await parseJson(res);
  loadHistory();
}

async function deleteHistory(id) {
  const ok = await showConfirm({
    title: "Delete entry",
    message: "This history entry will be removed permanently.",
    confirmLabel: "Delete",
    danger: true,
  });
  if (!ok) return;
  const res = await apiFetch("/history/" + id + "/", { method: "DELETE" });
  if (!res.ok && res.status !== 204) await parseJson(res);
  loadHistory();
}

async function bulkDeleteHistory() {
  const list = document.getElementById("history-list");
  const ids = [...list.querySelectorAll(".history-select:checked")].map((cb) => cb.dataset.id);
  if (!ids.length) return;
  const n = ids.length;
  const ok = await showConfirm({
    title: "Delete " + n + " " + (n === 1 ? "entry" : "entries"),
    message: "Selected history items will be removed permanently. This cannot be undone.",
    confirmLabel: "Delete",
    danger: true,
  });
  if (!ok) return;
  const res = await apiFetch("/history/bulk_delete/", {
    method: "DELETE",
    body: JSON.stringify({ ids }),
  });
  await parseJson(res);
  document.getElementById("history-select-all").checked = false;
  showStatus("Deleted " + ids.length + " entries");
  loadHistory();
}

// History edit UI intentionally removed.

async function rerunHistory(id) {
  showStatus("Re-running...");
  setProgress(20);
  try {
    const res = await apiFetch("/history/" + id + "/rerun/", { method: "POST" });
    const data = await parseJson(res);
    if (data.task_id) {
      const result = await pollTask(data.task_id);
      setProgress(100);
      showStatus("Re-run complete");
      showOutput(result.result?.output_text || "");
    }
    loadHistory();
  } catch (ex) {
    showStatus("Error: " + ex.message);
    setProgress(0);
  }
}

function renderHistoryItem(h) {
  const preview = escHtml((h.output_text || h.input_text || h.input_url || "").slice(0, 200));
  const star = h.is_starred ? "★" : "☆";
  const canRerun = HISTORY_RERUN_FEATURES.includes(h.feature);
  const tags = (h.tags || [])
    .map((t) => "<span class='tag'>" + escHtml(t) + "</span>")
    .join("");
  const note = h.user_note
    ? "<div class='history-note-preview'>" +
      escHtml(h.user_note.length > 100 ? h.user_note.slice(0, 100) + "…" : h.user_note) +
      "</div>"
    : "";

  return (
    "<li class='history-row " +
    (h.is_starred ? "starred" : "") +
    "'>" +
    "<div class='history-select-wrap'>" +
    "<input type='checkbox' class='history-select' data-id='" +
    h.id +
    "' />" +
    "</div>" +
    "<div class='history-row-body'>" +
    "<strong>" +
    escHtml(h.feature) +
    "</strong> — " +
    escHtml(h.status) +
    "<br>" +
    preview +
    (tags ? "<div class='history-tags'>" + tags + "</div>" : "") +
    note +
    "<div class='meta'>" +
    new Date(h.created_at).toLocaleString() +
    "</div>" +
    "<div class='history-actions'>" +
    "<button type='button' class='btn btn-ghost' data-star='" +
    h.id +
    "' data-starred='" +
    h.is_starred +
    "'>" +
    star +
    "</button>" +
    (canRerun ? "<button type='button' class='btn btn-ghost' data-rerun='" + h.id + "'>Re-run</button>" : "") +
    "<button type='button' class='btn btn-ghost' data-view='" +
    h.id +
    "'>View</button>" +
    "<button type='button' class='btn btn-ghost' data-delete='" +
    h.id +
    "'>Delete</button>" +
    "</div></div></li>"
  );
}

function bindHistoryListEvents(items) {
  const list = document.getElementById("history-list");

  list.querySelectorAll(".history-select").forEach((cb) => {
    cb.onchange = updateHistoryBulkBar;
  });

  list.querySelectorAll("[data-star]").forEach((btn) => {
    btn.onclick = () => toggleStar(btn.dataset.star, btn.dataset.starred === "true");
  });
  list.querySelectorAll("[data-rerun]").forEach((btn) => {
    btn.onclick = () => rerunHistory(btn.dataset.rerun);
  });
  list.querySelectorAll("[data-view]").forEach((btn) => {
    btn.onclick = () => {
      const item = items.find((x) => x.id === btn.dataset.view);
      if (item) {
        showStatus(item.feature + " — " + new Date(item.created_at).toLocaleString());
        showOutput(item.output_text || item.input_text || item.input_url || "");
        outputEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    };
  });
  list.querySelectorAll("[data-delete]").forEach((btn) => {
    btn.onclick = () => deleteHistory(btn.dataset.delete);
  });

  updateHistoryBulkBar();
}

async function loadHistory() {
  const list = document.getElementById("history-list");
  list.innerHTML = "<li>Loading...</li>";
  document.getElementById("history-pagination").hidden = true;

  try {
    const qs = historyFilterParams(true).toString();
    const res = await apiFetch("/history/" + (qs ? "?" + qs : ""));
    const data = await parseJson(res);
    const items = data.results !== undefined ? data.results : data;
    historyItems = Array.isArray(items) ? items : [];

    historyHasNext = !!data.next;
    historyHasPrev = !!data.previous;
    updateHistoryPagination();

    if (!historyItems.length) {
      list.innerHTML = "<li style='color:var(--muted)'>No matching history.</li>";
      document.getElementById("history-select-all").checked = false;
      updateHistoryBulkBar();
      return;
    }

    list.innerHTML = historyItems.map(renderHistoryItem).join("");
    bindHistoryListEvents(historyItems);
  } catch (ex) {
    list.innerHTML = "<li style='color:var(--muted)'>Could not load history.</li>";
    showStatus(ex.message);
  }
}

document.getElementById("history-search").oninput = () => {
  clearTimeout(historySearchTimer);
  historySearchTimer = setTimeout(resetHistoryPageAndLoad, 350);
};
document.getElementById("history-feature").onchange = resetHistoryPageAndLoad;
document.getElementById("history-status").onchange = resetHistoryPageAndLoad;
document.getElementById("history-starred-only").onchange = resetHistoryPageAndLoad;
document.getElementById("history-date-from").onchange = () => {
  document.getElementById("history-date-preset").value = "custom";
  syncHistoryDateInputs();
  resetHistoryPageAndLoad();
};
document.getElementById("history-date-to").onchange = () => {
  document.getElementById("history-date-preset").value = "custom";
  syncHistoryDateInputs();
  resetHistoryPageAndLoad();
};
document.getElementById("history-date-preset").onchange = () => {
  syncHistoryDateInputs();
  resetHistoryPageAndLoad();
};

document.getElementById("history-select-all").onchange = (e) => {
  document.querySelectorAll(".history-select").forEach((cb) => {
    cb.checked = e.target.checked;
  });
  updateHistoryBulkBar();
};

document.getElementById("history-bulk-delete").onclick = bulkDeleteHistory;

document.getElementById("history-prev").onclick = () => {
  if (!historyHasPrev) return;
  historyPage -= 1;
  document.getElementById("history-select-all").checked = false;
  loadHistory();
};

document.getElementById("history-next").onclick = () => {
  if (!historyHasNext) return;
  historyPage += 1;
  document.getElementById("history-select-all").checked = false;
  loadHistory();
};

syncHistoryDateInputs();
