"use client";

import { useAuthStore } from "@/store/authStore";
import { logout } from "@/lib/auth";
import { useRouter } from "next/navigation";

export function Header() {
  const user = useAuthStore((s) => s.user);
  const router = useRouter();

  const handleLogout = () => {
    logout();
    useAuthStore.getState().setUser(null);
    router.push("/login");
  };

  return (
    <header className="flex h-14 items-center justify-between border-b border-slate-800 bg-slate-950 px-6">
      <p className="text-sm text-slate-400">
        Plan: <span className="capitalize text-slate-200">{user?.plan ?? "free"}</span>
      </p>
      <div className="flex items-center gap-4">
        <span className="text-sm text-slate-300">{user?.email}</span>
        <button
          type="button"
          onClick={handleLogout}
          className="rounded-lg border border-slate-700 px-3 py-1.5 text-sm text-slate-300 hover:bg-slate-800"
        >
          Log out
        </button>
      </div>
    </header>
  );
}
