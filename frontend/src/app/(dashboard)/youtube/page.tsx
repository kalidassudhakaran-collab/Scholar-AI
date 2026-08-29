"use client";

import { useState } from "react";
import { useFileTaskRun } from "@/hooks/useFileTaskRun";

export default function YoutubePage() {
  const [url, setUrl] = useState("");
  const { runWithUrl, output, status, progress, loading } = useFileTaskRun("/youtube/run/");

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-white">YouTube Summarizer</h1>
        <p className="mt-1 text-slate-400">
          Paste a lecture URL — fetches captions or transcribes audio, then summarizes.
        </p>
      </div>

      <input
        type="url"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="https://www.youtube.com/watch?v=..."
        className="w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-white placeholder:text-slate-500"
      />

      <button
        type="button"
        disabled={loading || !url.trim()}
        onClick={() => runWithUrl(url)}
        className="rounded-lg bg-indigo-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
      >
        {loading ? "Processing…" : "Summarize video"}
      </button>

      {loading && progress > 0 && (
        <div className="h-2 rounded-full bg-slate-800">
          <div className="h-full bg-indigo-500 transition-all" style={{ width: `${progress}%` }} />
        </div>
      )}
      {status && <p className="text-sm text-slate-400">{status}</p>}
      {output && (
        <div className="rounded-xl border border-slate-700 bg-slate-900 p-4">
          <pre className="whitespace-pre-wrap text-sm text-slate-100">{output}</pre>
        </div>
      )}
    </div>
  );
}
