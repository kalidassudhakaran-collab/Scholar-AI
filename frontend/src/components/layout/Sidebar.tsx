"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BookOpen,
  FileText,
  Globe,
  History,
  Image,
  LayoutDashboard,
  Mic,
  RefreshCw,
  Shield,
  Sparkles,
  Video,
} from "lucide-react";
import { cn } from "@/lib/utils";

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/summarizer", label: "Summarizer", icon: FileText },
  { href: "/translator", label: "Translator", icon: Globe },
  { href: "/paraphraser", label: "Paraphraser", icon: RefreshCw },
  { href: "/humanizer", label: "Humanizer", icon: Sparkles },
  { href: "/plagiarism", label: "Plagiarism", icon: Shield },
  { href: "/ocr", label: "OCR", icon: Image },
  { href: "/voice", label: "Voice", icon: Mic },
  { href: "/youtube", label: "YouTube", icon: Video },
  { href: "/history", label: "History", icon: History },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-full w-56 flex-col border-r border-slate-800 bg-slate-950 p-4">
      <Link href="/dashboard" className="mb-8 flex items-center gap-2 font-semibold text-white">
        <BookOpen className="h-6 w-6 text-indigo-400" />
        Scholar AI
      </Link>
      <nav className="flex flex-1 flex-col gap-1">
        {nav.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors",
              pathname === href
                ? "bg-indigo-600/20 text-indigo-300"
                : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
            )}
          >
            <Icon className="h-4 w-4" />
            {label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
