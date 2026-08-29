"use client";

import { useState } from "react";
import { api } from "@/lib/api";

interface FeatureWorkspaceProps {
  title: string;
  description: string;
  feature: string;
  endpoint: string;
}

export function FeatureWorkspace({ title, description, feature, endpoint }: FeatureWorkspaceProps) {
  const [text, setText] = useState("");
  const [output, setOutput] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    setStatus("Queuing task...");
    setOutput("");
    try {
      const { data } = await api.post(endpoint, {
        input_type: "text",
        text,
        options: { summary_type: "detailed" },
      });
      setStatus(`Task ${data.task_id?.slice(0, 8) ?? "—"}… polling`);

      if (!data.task_id) {
        setStatus("Queued (no worker — check history later)");
        setLoading(false);
        return;
      }

      const poll = async () => {
        const res = await api.get(`/tasks/${data.task_id}/status/`);
        if (res.data.status === "completed") {
          setOutput(res.data.result?.output_text ?? "");
          setStatus("Completed");
          setLoading(false);
        } else if (res.data.status === "failed") {
          setStatus("Failed");
          setLoading(false);
        } else {
          setTimeout(poll, 1500);
        }
      };
      poll();
    } catch {
      setStatus("Error — is the API running?");
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-white">{title}</h1>
        <p className="mt-1 text-slate-400">{description}</p>
        <p className="mt-1 text-xs text-slate-500">Feature: {feature}</p>
      </div>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste your text here..."
        className="min-h-[200px] w-full rounded-xl border border-slate-700 bg-slate-900 p-4 text-slate-100 placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none"
      />

      <button
        type="button"
        onClick={handleSubmit}
        disabled={loading || !text.trim()}
        className="rounded-lg bg-indigo-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
      >
        {loading ? "Processing…" : "Run"}
      </button>

      {status && <p className="text-sm text-slate-400">{status}</p>}

      {output && (
        <div className="rounded-xl border border-slate-700 bg-slate-900 p-4">
          <h2 className="mb-2 text-sm font-medium text-slate-300">Output</h2>
          <p className="whitespace-pre-wrap text-slate-100">{output}</p>
        </div>
      )}
    </div>
  );
}
