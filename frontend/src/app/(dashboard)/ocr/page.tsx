"use client";

import { useRef } from "react";
import { Upload } from "lucide-react";
import { useFileTaskRun } from "@/hooks/useFileTaskRun";

export default function OcrPage() {
  const inputRef = useRef<HTMLInputElement>(null);
  const { runWithFile, output, status, progress, loading } = useFileTaskRun("/ocr/run/");

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-white">Image to Text (OCR)</h1>
        <p className="mt-1 text-slate-400">
          Upload images or PDFs to extract text. Tesseract + pdfplumber when installed on the server.
        </p>
      </div>

      <div
        role="button"
        tabIndex={0}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
        className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-700 bg-slate-900/50 py-12 hover:border-indigo-500"
      >
        <Upload className="mb-2 h-10 w-10 text-slate-500" />
        <p className="text-sm text-slate-400">Drop or click to upload PDF, PNG, JPG</p>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.png,.jpg,.jpeg,.webp"
          className="hidden"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) runWithFile(f);
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
          <pre className="whitespace-pre-wrap text-sm text-slate-100">{output}</pre>
        </div>
      )}
    </div>
  );
}
