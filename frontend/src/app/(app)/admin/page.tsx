"use client";

import { useQuery } from "@tanstack/react-query";
import { Users, FileText, Layers, MessageSquare, Activity } from "lucide-react";
import { api } from "@/lib/api";
import type { AdminStats as AdminStatsType } from "@/types";
import { motion } from "framer-motion";

export default function AdminPage() {
  const { data: stats, isLoading, isError } = useQuery<AdminStatsType>({
    queryKey: ["admin-stats"],
    queryFn: () => api.get("/admin/overview").then((res) => res.data),
  });

  if (isLoading) return <div className="p-10">Loading admin stats...</div>;
  if (isError) return <div className="p-10 text-red-500">Failed to load or unauthorized.</div>;

  const statCards = [
    { label: "Total Users", value: stats?.total_users, icon: Users },
    { label: "Documents Indexed", value: stats?.total_documents, icon: FileText },
    { label: "Vector Chunks", value: stats?.total_chunks, icon: Layers },
    { label: "Messages Generated", value: stats?.total_messages, icon: MessageSquare },
  ];

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-ink dark:text-ink-inverse flex items-center gap-2">
          <Activity className="w-6 h-6 text-accent" />
          System Overview
        </h1>
        <p className="text-ink-secondary dark:text-ink-tertiary text-sm mt-1">
          Global analytics across all users and spaces.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="card p-5"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-medium text-ink-secondary dark:text-ink-tertiary uppercase tracking-wider">
                {s.label}
              </span>
              <s.icon className="w-4 h-4 text-accent" />
            </div>
            <p className="text-3xl font-semibold text-ink dark:text-ink-inverse">
              {s.value?.toLocaleString() ?? 0}
            </p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
