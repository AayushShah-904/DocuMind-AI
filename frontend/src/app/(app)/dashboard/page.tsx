"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  FileText,
  MessageSquare,
  Layers,
  Activity,
  ArrowRight,
} from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/auth";
import { formatRelativeTime } from "@/lib/utils";
import type { Document } from "@/types";

function StatCard({
  label,
  value,
  icon: Icon,
  delay,
}: {
  label: string;
  value: number | string;
  icon: React.ElementType;
  delay: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="card p-5"
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-ink-secondary dark:text-ink-tertiary uppercase tracking-wider">
          {label}
        </span>
        <Icon className="w-4 h-4 text-accent" />
      </div>
      <p className="text-2xl font-semibold text-ink dark:text-ink-inverse">
        {value}
      </p>
    </motion.div>
  );
}

export default function DashboardPage() {
  const { user } = useAuthStore();

  const { data: docsData } = useQuery({
    queryKey: ["documents"],
    queryFn: () => api.get("/library").then((r) => r.data),
  });

  const docs: Document[] = docsData?.documents || [];
  const readyDocs = docs.filter((d) => d.status === "ready");
  const totalChunks = readyDocs.reduce((acc, d) => acc + d.chunk_count, 0);

  const stats = [
    { label: "Documents", value: docsData?.total ?? 0, icon: FileText },
    { label: "Chunks indexed", value: totalChunks, icon: Layers },
    { label: "Conversations", value: "—", icon: MessageSquare },
    { label: "Status", value: "Online", icon: Activity },
  ];

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-ink dark:text-ink-inverse">
          Good {getGreeting()},{" "}
          {user?.full_name?.split(" ")[0] || user?.email?.split("@")[0]}
        </h1>
        <p className="text-ink-secondary dark:text-ink-tertiary text-sm mt-1">
          Your workspace at a glance
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((s, i) => (
          <StatCard
            key={s.label}
            label={s.label}
            value={s.value}
            icon={s.icon}
            delay={i * 0.07}
          />
        ))}
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <Link
          href="/chat"
          className="card p-5 flex items-center justify-between group hover:border-accent/30 transition-colors"
        >
          <div>
            <p className="font-medium text-ink dark:text-ink-inverse text-sm">
              Start a conversation
            </p>
            <p className="text-ink-secondary dark:text-ink-tertiary text-xs mt-0.5">
              Ask questions across your documents
            </p>
          </div>
          <ArrowRight className="w-4 h-4 text-ink-tertiary group-hover:text-accent transition-colors" />
        </Link>
        <Link
          href="/library"
          className="card p-5 flex items-center justify-between group hover:border-accent/30 transition-colors"
        >
          <div>
            <p className="font-medium text-ink dark:text-ink-inverse text-sm">
              Upload documents
            </p>
            <p className="text-ink-secondary dark:text-ink-tertiary text-xs mt-0.5">
              PDF, DOCX, and TXT supported
            </p>
          </div>
          <ArrowRight className="w-4 h-4 text-ink-tertiary group-hover:text-accent transition-colors" />
        </Link>
      </div>

      {/* Recent docs */}
      {docs.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-ink-secondary dark:text-ink-tertiary mb-3">
            Recent documents
          </h2>
          <div className="space-y-2">
            {docs.slice(0, 5).map((doc) => (
              <div
                key={doc.id}
                className="card px-4 py-3 flex items-center gap-3"
              >
                <FileText className="w-4 h-4 text-ink-tertiary shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-ink dark:text-ink-inverse truncate">
                    {doc.original_filename}
                  </p>
                  <p className="text-xs text-ink-tertiary">
                    {formatRelativeTime(doc.created_at)}
                  </p>
                </div>
                <span
                  className={`badge text-xs ${
                    doc.status === "ready"
                      ? "bg-emerald-50 text-emerald-600 dark:bg-emerald-950/30"
                      : doc.status === "processing"
                      ? "bg-blue-50 text-blue-500 dark:bg-blue-950/30"
                      : "bg-gray-100 text-ink-secondary dark:bg-dark-elevated"
                  }`}
                >
                  {doc.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function getGreeting() {
  const h = new Date().getHours();
  if (h < 12) return "morning";
  if (h < 17) return "afternoon";
  return "evening";
}
