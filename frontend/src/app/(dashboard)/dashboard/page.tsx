import Link from "next/link";
import { FileText, Globe, History, Mic } from "lucide-react";

const cards = [
  { href: "/summarizer", title: "Summarizer", icon: FileText, desc: "Condense articles and papers" },
  { href: "/translator", title: "Translator", icon: Globe, desc: "Translate across 140+ languages" },
  { href: "/voice", title: "Voice to Text", icon: Mic, desc: "Transcribe lectures and recordings" },
  { href: "/history", title: "History", icon: History, desc: "Search and re-run past work" },
];

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-white">Dashboard</h1>
        <p className="mt-1 text-slate-400">Choose a tool to get started.</p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map(({ href, title, icon: Icon, desc }) => (
          <Link
            key={href}
            href={href}
            className="rounded-xl border border-slate-800 bg-slate-900 p-5 transition-colors hover:border-indigo-500/50"
          >
            <Icon className="mb-3 h-8 w-8 text-indigo-400" />
            <h2 className="font-medium text-white">{title}</h2>
            <p className="mt-1 text-sm text-slate-400">{desc}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
