const API = "/api";

function getToken() {
  return sessionStorage.getItem("access_token");
}

function setTokens(access, refresh) {
  sessionStorage.setItem("access_token", access);
  sessionStorage.setItem("refresh_token", refresh);
}

function clearTokens() {
  sessionStorage.removeItem("access_token");
  sessionStorage.removeItem("refresh_token");
}

function isLoggedIn() {
  return !!getToken();
}

async function apiFetch(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const token = getToken();
  if (token) headers.Authorization = "Bearer " + token;

  let res;
  try {
    res = await fetch(API + path, { ...options, headers });
  } catch {
    throw new Error(
      "Cannot reach the server. Run run.cmd from the project folder and keep that window open."
    );
  }

  if (res.status === 401 && sessionStorage.getItem("refresh_token")) {
    const refresh = await fetch(API + "/auth/token/refresh/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: sessionStorage.getItem("refresh_token") }),
    });
    if (refresh.ok) {
      const data = await refresh.json();
      sessionStorage.setItem("access_token", data.access);
      headers.Authorization = "Bearer " + data.access;
      res = await fetch(API + path, { ...options, headers });
    } else {
      clearTokens();
      window.location.href = "/login.html";
    }
  }

  return res;
}

async function parseJson(res) {
  const text = await res.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    throw new Error(
      res.ok
        ? "Invalid server response"
        : "Server error — restart backend and try again. First AI run downloads a large model."
    );
  }
  if (!res.ok) {
    const detail = data.detail || data.message || "";
    if (res.status === 429) {
      throw new Error(
        typeof detail === "string" && detail
          ? detail
          : "Too many requests — wait a minute and try again."
      );
    }
    throw new Error(
      typeof detail === "string" ? detail : detail[0] || "Request failed"
    );
  }
  return data;
}

async function pollTask(taskId, onProgress) {
  const maxWaitSec = 360;
  for (let i = 0; i < maxWaitSec; i++) {
    const res = await apiFetch("/tasks/" + taskId + "/status/");
    const data = await parseJson(res);
    if (onProgress) onProgress(data);
    if (data.status === "completed") return data;
    if (data.status === "failed") throw new Error(data.error || "Task failed");
    if (i % 5 === 0 && onProgress) onProgress({ ...data, progress: Math.min(90, 20 + i / 3) });
    await new Promise((r) => setTimeout(r, 1000));
  }
  throw new Error("Timed out — try again or use a shorter paragraph.");
}

async function runTextTool(endpoint, text, options) {
  const res = await apiFetch(endpoint, {
    method: "POST",
    body: JSON.stringify({ input_type: "text", text, options }),
  });
  const data = await parseJson(res);
  if (!data.task_id) return { output_text: "Queued - check History" };
  const result = await pollTask(data.task_id);
  const out = result.result || {};
  if (result.model_used) out.model_used = result.model_used;
  return out;
}

async function uploadFile(file) {
  const form = new FormData();
  form.append("file", file);
  const token = getToken();
  const res = await fetch(API + "/files/upload/", {
    method: "POST",
    headers: token ? { Authorization: "Bearer " + token } : {},
    body: form,
  });
  if (!res.ok) throw new Error("Upload failed");
  return res.json();
}

async function checkServer() {
  try {
    const res = await fetch(API + "/health/");
    return res.ok;
  } catch {
    return false;
  }
}

async function runFileTool(endpoint, file, options) {
  const uploaded = await uploadFile(file);
  const res = await apiFetch(endpoint, {
    method: "POST",
    body: JSON.stringify({ input_type: "file", file_id: uploaded.id, options }),
  });
  const data = await parseJson(res);
  if (!res.ok) throw new Error(data.detail || "Task failed");
  const result = await pollTask(data.task_id);
  return result.result || {};
}
