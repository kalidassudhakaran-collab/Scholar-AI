"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Star, Trash2 } from "lucide-react";
import { api } from "@/lib/api";

interface HistoryItem {
  id: string;
  feature: string;
  status: string;
  input_text: string | null;
  output_text: string | null;
  is_starred: boolean;
  created_at: string;
}

export default function HistoryPage() {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["history"],
    queryFn: async () => {
      const { data: res } = await api.get<{ results: HistoryItem[] }>("/history/");
      return (res.results ?? res) as HistoryItem[];
    },
  });

  const toggleStar = useMutation({
    mutationFn: async ({ id, starred }: { id: string; starred: boolean }) => {
      await api.patch(`/history/${id}/`, { is_starred: !starred });
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["history"] }),
  });

  const deleteItem = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/history/${id}/`);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["history"] }),
  });

  const items = data ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-white">History</h1>
        <p className="mt-1 text-slate-400">Search, star, and delete past AI operations.</p>
      </div>

      {isLoading && <p className="text-slate-400">Loading…</p>}

      <ul className="space-y-3">
        {items.map((item) => (
          <li
            key={item.id}
            className="rounded-xl border border-slate-800 bg-slate-900 p-4"
          >
            <div className="flex items-start justify-between gap-2">
              <div>
                <span className="text-sm font-medium capitalize text-indigo-300">
                  {item.feature}
                </span>
                <span className="ml-2 text-xs text-slate-500">{item.status}</span>
              </div>
              <div className="flex gap-1">
                <button
                  type="button"
                  onClick={() => toggleStar.mutate({ id: item.id, starred: item.is_starred })}
                  className="rounded p-1.5 text-slate-400 hover:bg-slate-800 hover:text-amber-400"
                  title="Star"
                >
                  <Star
                    className={`h-4 w-4 ${item.is_starred ? "fill-amber-400 text-amber-400" : ""}`}
                  />
                </button>
                <button
                  type="button"
                  onClick={() => deleteItem.mutate(item.id)}
                  className="rounded p-1.5 text-slate-400 hover:bg-slate-800 hover:text-red-400"
                  title="Delete"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
            <p className="mt-2 line-clamp-3 text-sm text-slate-400">
              {item.output_text || item.input_text || "—"}
            </p>
            <p className="mt-1 text-xs text-slate-600">
              {new Date(item.created_at).toLocaleString()}
            </p>
          </li>
        ))}
        {!isLoading && items.length === 0 && (
          <p className="text-slate-500">No history yet. Run a tool to get started.</p>
        )}
      </ul>
    </div>
  );
}
