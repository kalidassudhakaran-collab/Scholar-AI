function openFeedbackDialog() {
  const dialog = document.getElementById("feedback-dialog");
  if (!dialog) return;
  document.getElementById("feedback-status").textContent = "";
  document.getElementById("feedback-status").className = "feedback-status";
  const select = document.getElementById("feedback-feature");
  if (select) {
    const params = new URLSearchParams(location.search);
    const panel = params.get("panel");
    const activeNav = document.querySelector("#nav a.active");
    const feature = panel || activeNav?.dataset?.panel;
    if (feature && select.querySelector(`option[value="${feature}"]`)) {
      select.value = feature;
    }
  }
  dialog.showModal();
}

function closeFeedbackDialog() {
  const dialog = document.getElementById("feedback-dialog");
  if (dialog?.open) dialog.close();
}

function initFeedback() {
  document.querySelectorAll("[data-feedback-open]").forEach((btn) => {
    btn.onclick = (e) => {
      e.preventDefault();
      openFeedbackDialog();
    };
  });

  const dialog = document.getElementById("feedback-dialog");
  if (!dialog) return;

  document.getElementById("feedback-dialog-cancel")?.addEventListener("click", closeFeedbackDialog);

  document.getElementById("feedback-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const statusEl = document.getElementById("feedback-status");
    const submitBtn = document.getElementById("feedback-submit");
    const payload = {
      feature: document.getElementById("feedback-feature").value,
      likes: document.getElementById("feedback-likes").value,
      drawbacks: document.getElementById("feedback-drawbacks").value,
      improvements: document.getElementById("feedback-improvements").value,
    };

    submitBtn.disabled = true;
    statusEl.textContent = "Sending…";
    statusEl.className = "feedback-status";

    try {
      const res = await apiFetch("/feedback/", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      await parseJson(res);
      document.getElementById("feedback-form").reset();
      statusEl.textContent = "Thanks — your feedback was saved.";
      statusEl.className = "feedback-status feedback-status--ok";
      setTimeout(closeFeedbackDialog, 1400);
    } catch (err) {
      statusEl.textContent = err.message || "Could not send feedback.";
      statusEl.className = "feedback-status feedback-status--err";
    } finally {
      submitBtn.disabled = false;
    }
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initFeedback);
} else {
  initFeedback();
}
