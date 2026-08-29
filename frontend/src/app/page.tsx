import Link from "next/link";
import { BookOpen, ArrowRight } from "lucide-react";

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center px-6 text-center">
      <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-600/20">
        <BookOpen className="h-8 w-8 text-indigo-400" />
      </div>
      <h1 className="max-w-2xl text-4xl font-bold tracking-tight text-white sm:text-5xl">
        Scholar AI
      </h1>
      <p className="mt-4 max-w-xl text-lg text-slate-400">
        Summarize, translate, paraphrase, transcribe, and more — one platform for academic
        productivity with offline-first AI.
      </p>
      <div className="mt-10 flex flex-wrap justify-center gap-4">
        <Link
          href="/register"
          className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-6 py-3 font-medium text-white hover:bg-indigo-500"
        >
          Get started
          <ArrowRight className="h-4 w-4" />
        </Link>
        <Link
          href="/login"
          className="rounded-lg border border-slate-700 px-6 py-3 font-medium text-slate-200 hover:bg-slate-900"
        >
          Sign in
        </Link>
      </div>
    </main>
  );
}
