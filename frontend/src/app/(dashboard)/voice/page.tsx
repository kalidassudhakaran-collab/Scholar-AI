"use client";

import { useRef } from "react";
import { Mic } from "lucide-react";
import { useFileTaskRun } from "@/hooks/useFileTaskRun";

export default function VoicePage() {
  const inputRef = useRef<HTMLInputElement>(null);
  const { runWithFile, output, status, progress, loading } = useFileTaskRun("/voice/run/");

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-white">Voice to Text</h1>
        <p className="mt-1 text-slate-400">
          Upload audio (MP3, WAV, M4A) for transcription with Whisper.
        </p>
      </div>

      <div
        role="button"
        tabIndex={0}
        onClick={() => inputRef.current?.click()}
        className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-700 bg-slate-900/50 py-12 hover:border-indigo-500"
      >
        <Mic className="mb-2 h-10 w-10 text-slate-500" />
        <p className="text-sm text-slate-400">Upload audio file</p>
        <input
          ref={inputRef}
          type="file"
          accept="audio/*,.mp3,.wav,.m4a,.ogg"
          className="hidden"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) runWithFile(f, { model_size: "small" });
          }}
        />
      </div>

      {loading && progress > 0 && (
        <div className="h-2 rounded-full bg-slate-800">
          <div className="h-full bg-indigo-500 transition-all" style={{ width: `${progress}%` }} />
        </div>
      )}
      {status && <p className="text-sm text-slate-400">{status}</p>}
      {output && (
        <div className="rounded-xl border border-slate-700 bg-slate-900 p-4">
          <p className="whitespace-pre-wrap text-slate-100">{output}</p>
        </div>
      )}
    </div>
  );
}
