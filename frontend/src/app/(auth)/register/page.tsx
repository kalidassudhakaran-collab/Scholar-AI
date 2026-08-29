"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { register, fetchMe } from "@/lib/auth";
import { useAuthStore } from "@/store/authStore";

export default function RegisterPage() {
  const router = useRouter();
  const setUser = useAuthStore((s) => s.setUser);
  const [form, setForm] = useState({
    email: "",
    username: "",
    password: "",
    password_confirm: "",
    full_name: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await register(form);
      const user = await fetchMe();
      setUser(user);
      router.push("/dashboard");
    } catch {
      setError("Registration failed. Check your details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md space-y-4 rounded-2xl border border-slate-800 bg-slate-900 p-8"
      >
        <h1 className="text-2xl font-semibold text-white">Create account</h1>
        {error && <p className="text-sm text-red-400">{error}</p>}
        {(["email", "username", "full_name", "password", "password_confirm"] as const).map(
          (field) => (
            <input
              key={field}
              type={field.includes("password") ? "password" : field === "email" ? "email" : "text"}
              required={field !== "full_name"}
              placeholder={field.replace("_", " ")}
              value={form[field]}
              onChange={(e) => setForm({ ...form, [field]: e.target.value })}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-2.5 text-white capitalize placeholder:normal-case"
            />
          )
        )}
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-indigo-600 py-2.5 font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
        >
          {loading ? "Creating…" : "Register"}
        </button>
        <p className="text-center text-sm text-slate-400">
          Already have an account?{" "}
          <Link href="/login" className="text-indigo-400 hover:underline">
            Sign in
          </Link>
        </p>
      </form>
    </main>
  );
}
