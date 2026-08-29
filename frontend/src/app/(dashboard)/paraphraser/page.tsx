"use client";

import { useState } from "react";
import { TextToolLayout } from "@/components/features/TextToolLayout";
import { useTaskRun } from "@/hooks/useTaskRun";

const STYLES = [
  { id: "fluent", label: "Fluent" },
  { id: "formal", label: "Formal" },
  { id: "creative", label: "Creative" },
] as const;

export default function ParaphraserPage() {
  const [text, setText] = useState("");
  const [style, setStyle] = useState<string>("fluent");
  const { run, output, status, progress, loading } = useTaskRun();

  return (
    <TextToolLayout
      title="Paraphraser"
      description="Rephrase text in fluent, formal, or creative styles."
      text={text}
      onTextChange={setText}
      output={output}
      status={status}
      progress={progress}
      loading={loading}
      submitLabel="Paraphrase"
      onSubmit={() =>
        run({
          endpoint: "/paraphraser/run/",
          text,
          options: { style },
        })
      }
      options={
        <div className="flex flex-wrap gap-2">
          <span className="w-full text-xs text-slate-500">Style</span>
          {STYLES.map(({ id, label }) => (
            <button
              key={id}
              type="button"
              onClick={() => setStyle(id)}
              className={`rounded-lg px-3 py-1.5 text-sm ${
                style === id
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
