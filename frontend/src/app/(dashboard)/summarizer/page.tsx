"use client";

import { useState } from "react";
import { TextToolLayout } from "@/components/features/TextToolLayout";
import { useTaskRun } from "@/hooks/useTaskRun";

const SUMMARY_TYPES = [
  { id: "short", label: "Short" },
  { id: "detailed", label: "Detailed" },
  { id: "bullets", label: "Bullet points" },
] as const;

export default function SummarizerPage() {
  const [text, setText] = useState("");
  const [summaryType, setSummaryType] = useState<string>("detailed");
  const { run, output, status, progress, loading } = useTaskRun();

  return (
    <TextToolLayout
      title="Summarizer"
      description="Generate short, detailed, or bullet-point summaries. Uses DistilBART when models are installed."
      text={text}
      onTextChange={setText}
      output={output}
      status={status}
      progress={progress}
      loading={loading}
      onSubmit={() =>
        run({
          endpoint: "/summarizer/run/",
          text,
          options: { summary_type: summaryType, max_length: 200 },
        })
      }
      options={
        <div className="flex flex-wrap gap-2">
          <span className="w-full text-xs text-slate-500">Summary type</span>
          {SUMMARY_TYPES.map(({ id, label }) => (
            <button
              key={id}
              type="button"
              onClick={() => setSummaryType(id)}
              className={`rounded-lg px-3 py-1.5 text-sm ${
                summaryType === id
                  ? "bg-indigo-600 text-white"
                  : "border border-slate-700 text-slate-300 hover:bg-slate-800"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      }
    />
  );
}
