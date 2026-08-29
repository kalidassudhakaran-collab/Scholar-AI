"use client";

import { useState } from "react";
import { TextToolLayout } from "@/components/features/TextToolLayout";
import { useTaskRun } from "@/hooks/useTaskRun";

const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "hi", label: "Hindi" },
  { code: "ml", label: "Malayalam" },
  { code: "ta", label: "Tamil" },
  { code: "te", label: "Telugu" },
];

export default function TranslatorPage() {
  const [text, setText] = useState("");
  const [sourceLang, setSourceLang] = useState("en");
  const [targetLang, setTargetLang] = useState("ml");
  const { run, output, status, progress, loading } = useTaskRun();

  return (
    <TextToolLayout
      title="Translator"
      description="English, Hindi, Malayalam, Tamil, and Telugu. Other pairs translate via English."
      text={text}
      onTextChange={setText}
      output={output}
      status={status}
      progress={progress}
      loading={loading}
      submitLabel="Translate"
      onSubmit={() =>
        run({
          endpoint: "/translator/run/",
          text,
          options: { source_language: sourceLang, target_language: targetLang },
        })
      }
      options={
        <div className="flex flex-wrap items-end gap-4">
          <label className="flex flex-col gap-1 text-sm text-slate-400">
            From
            <select
              value={sourceLang}
              onChange={(e) => setSourceLang(e.target.value)}
              className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-white"
            >
              {LANGUAGES.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.label}
                </option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm text-slate-400">
            To
            <select
              value={targetLang}
              onChange={(e) => setTargetLang(e.target.value)}
              className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-white"
            >
              {LANGUAGES.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.label}
                </option>
              ))}
            </select>
          </label>
        </div>
      }
    />
  );
}
