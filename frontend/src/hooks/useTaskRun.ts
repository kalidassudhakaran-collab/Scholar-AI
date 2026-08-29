"use client";

import { useCallback, useRef, useState } from "react";
import { api } from "@/lib/api";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8001";

interface RunTaskOptions {
  endpoint: string;
  text: string;
  options?: Record<string, unknown>;
}

export function useTaskRun() {
  const [output, setOutput] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const cleanupWs = () => {
    wsRef.current?.close();
    wsRef.current = null;
  };

  const pollStatus = useCallback((taskId: string) => {
    const poll = async () => {
      try {
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
          setStatus(data.status === "processing" ? "Processing…" : "Queued…");
          setTimeout(poll, 1500);
        }
      } catch {
        setStatus("Error checking task status");
        setLoading(false);
      }
    };
    poll();
  }, []);

  const connectWebSocket = useCallback(
    (taskId: string, onComplete: (text: string) => void) => {
      const token =
        typeof window !== "undefined" ? sessionStorage.getItem("access_token") : null;
      if (!token) return false;

      try {
        const ws = new WebSocket(`${WS_URL}/ws/tasks/?token=${token}`);
        wsRef.current = ws;

        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          if (data.task_id && data.task_id !== taskId) return;

          if (data.progress != null) setProgress(data.progress);
          if (data.message) setStatus(data.message);

          if (data.event === "task.complete" || data.result) {
            const text = data.result?.output_text ?? "";
            onComplete(text);
            setStatus("Completed");
            setLoading(false);
            cleanupWs();
          }
        };

        ws.onerror = () => cleanupWs();
        return true;
      } catch {
        return false;
      }
    },
    []
  );

  const run = useCallback(
    async ({ endpoint, text, options = {} }: RunTaskOptions) => {
      setLoading(true);
      setOutput("");
      setProgress(0);
      setStatus("Queuing task...");
      cleanupWs();

      try {
        const { data } = await api.post(endpoint, {
          input_type: "text",
          text,
          options,
        });

        if (!data.task_id) {
          setStatus("Queued — start Celery worker for results");
          setLoading(false);
          return;
        }

        setStatus(`Task ${String(data.task_id).slice(0, 8)}…`);

        const wsOk = connectWebSocket(data.task_id, (resultText) => {
          setOutput(resultText);
        });

        if (!wsOk) {
          pollStatus(data.task_id);
        } else {
          pollStatus(data.task_id);
        }
      } catch {
        setStatus("Error — is the API running?");
        setLoading(false);
      }
    },
    [connectWebSocket, pollStatus]
  );

  return { run, output, status, progress, loading, setOutput };
}
