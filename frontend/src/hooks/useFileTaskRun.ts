"use client";

import { useCallback, useRef, useState } from "react";
import { api } from "@/lib/api";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8001";

export function useFileTaskRun(endpoint: string) {
  const [output, setOutput] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const pollStatus = (taskId: string) => {
    const poll = async () => {
      const { data } = await api.get(`/tasks/${taskId}/status/`);
      setProgress(data.progress ?? 0);
      if (data.status === "completed") {
        setOutput(data.result?.output_text ?? "");
        setStatus("Completed");
        setLoading(false);
      } else if (data.status === "failed") {
        setStatus("Failed");
        setLoading(false);
      } else {
        setTimeout(poll, 1500);
      }
    };
    poll();
  };

  const runWithFile = useCallback(
    async (file: File, options: Record<string, unknown> = {}) => {
      setLoading(true);
      setOutput("");
      setStatus("Uploading file...");
      setProgress(0);

      try {
        const form = new FormData();
        form.append("file", file);
        const { data: uploaded } = await api.post("/files/upload/", form, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        setStatus("Queuing task...");
        const { data } = await api.post(endpoint, {
          input_type: "file",
          file_id: uploaded.id,
          options,
        });

        if (!data.task_id) {
          setStatus("Queued — start Celery worker");
          setLoading(false);
          return;
        }

        setStatus("Processing…");
        const token = sessionStorage.getItem("access_token");
        if (token) {
          const ws = new WebSocket(`${WS_URL}/ws/tasks/?token=${token}`);
          wsRef.current = ws;
          ws.onmessage = (ev) => {
            const msg = JSON.parse(ev.data);
            if (msg.task_id !== data.task_id) return;
            if (msg.progress != null) setProgress(msg.progress);
            if (msg.message) setStatus(msg.message);
            if (msg.event === "task.complete" && msg.result) {
              setOutput(msg.result.output_text ?? "");
              setStatus("Completed");
              setLoading(false);
              ws.close();
            }
          };
        }
        pollStatus(data.task_id);
      } catch {
        setStatus("Error — check API and file type");
        setLoading(false);
      }
    },
    [endpoint]
  );

  const runWithUrl = useCallback(
    async (url: string, options: Record<string, unknown> = {}) => {
      setLoading(true);
      setOutput("");
      setStatus("Queuing task...");
      try {
        const { data } = await api.post(endpoint, {
          input_type: "url",
          url,
          options,
        });
        if (data.task_id) pollStatus(data.task_id);
        else {
          setStatus("Queued — start Celery worker");
          setLoading(false);
        }
      } catch {
        setStatus("Error");
        setLoading(false);
      }
    },
    [endpoint]
  );

  return { runWithFile, runWithUrl, output, status, progress, loading };
}
