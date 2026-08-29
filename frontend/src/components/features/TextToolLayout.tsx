"use client";

import { ReactNode } from "react";
import { Copy, Check } from "lucide-react";
import { useState } from "react";

interface TextToolLayoutProps {
  title: string;
  description: string;
  text: string;
  onTextChange: (v: string) => void;
  options?: ReactNode;
  output: string;
  status: string | null;
  progress: number;
  loading: boolean;
  onSubmit: () => void;
  submitLabel?: string;
}

export function TextToolLayout({
  title,
  description,
  text,
  onTextChange,
  options,
  output,
  status,
  progress,
  loading,
  onSubmit,
  submitLabel = "Run",
}: TextToolLayoutProps) {
  const [copied, setCopied] = useState(false);

  const copyOutput = async () => {
    await navigator.clipboard.writeText(output);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-white">{title}</h1>
        <p className="mt-1 text-slate-400">{description}</p>
      </div>

      {options && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">{options}</div>
      )}

      <textarea
        value={text}
        onChange={(e) => onTextChange(e.target.value)}
        placeholder="Paste your text here..."
        className="min-h-[200px] w-full rounded-xl border border-slate-700 bg-slate-900 p-4 text-slate-100 placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none"
      />

      <button
        type="button"
        onClick={onSubmit}
        disabled={loading || !text.trim()}
        className="rounded-lg bg-indigo-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
      >
        {loading ? "Processing…" : submitLabel}
      </button>

      {loading && progress > 0 && (
        <div className="h-2 overflow-hidden rounded-full bg-slate-800">
          <div
            className="h-full bg-indigo-500 transition-all duration-300"
            style={{ width: `${Math.min(progress, 100)}%` }}
          />
        </div>
      )}

      {status && <p className="text-sm text-slate-400">{status}</p>}

      {output && (
        <div className="rounded-xl border border-slate-700 bg-slate-900 p-4">
          <div className="mb-2 flex items-center justify-between">
            <h2 className="text-sm font-medium text-slate-300">Output</h2>
            <button
              type="button"
              onClick={copyOutput}
              className="flex items-center gap-1 text-xs text-slate-400 hover:text-white"
            >
              {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
              {copied ? "Copied" : "Copy"}
            </button>
          </div>
          <p className="whitespace-pre-wrap text-slate-100">{output}</p>
        </div>
      )}
    </div>
  );
}
