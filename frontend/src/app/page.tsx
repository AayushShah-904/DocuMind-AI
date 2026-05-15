"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight,
  FileText,
  Search,
  Zap,
  MessageSquare,
  Shield,
  BarChart3,
} from "lucide-react";

const features = [
  {
    icon: FileText,
    title: "Upload Any Document",
    desc: "PDF, DOCX, and TXT — drop it in and we handle the rest.",
  },
  {
    icon: Search,
    title: "Hybrid Retrieval",
    desc: "Semantic + keyword search fused with RRF for maximum recall.",
  },
  {
    icon: Zap,
    title: "Streamed Answers",
    desc: "Token-by-token responses powered by Gemini 2.5 Flash.",
  },
  {
    icon: MessageSquare,
    title: "Cited Sources",
    desc: "Every answer links back to the exact document chunks used.",
  },
  {
    icon: Shield,
    title: "Private by Design",
    desc: "Your documents are yours — isolated per account.",
  },
  {
    icon: BarChart3,
    title: "Usage Insights",
    desc: "Track documents, queries, and response latency in your dashboard.",
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-dark-bg">
      {/* Nav */}
      <nav className="border-b border-surface-border dark:border-dark-border">
        <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
          <span className="font-semibold text-ink dark:text-ink-inverse tracking-tight">
            DocuMind <span className="text-accent">AI</span>
          </span>
          <div className="flex items-center gap-3">
            <Link href="/login" className="btn-ghost">
              Sign in
            </Link>
            <Link href="/register" className="btn-primary">
              Get started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-5xl mx-auto px-6 pt-24 pb-16 text-center">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-accent/10 text-accent mb-6">
            <Zap className="w-3 h-3" />
            Powered by Gemini 2.5 Flash
          </span>
          <h1 className="text-5xl font-bold tracking-tight text-ink dark:text-ink-inverse leading-tight mb-5">
            Ask questions about
            <br />
            <span className="text-accent">your documents</span>
          </h1>
          <p className="text-lg text-ink-secondary dark:text-ink-tertiary max-w-xl mx-auto mb-10">
            Upload PDFs, DOCX, and TXT files. Get instant, grounded answers with
            citations — no hallucinations, just your content.
          </p>
          <div className="flex items-center justify-center gap-3">
            <Link href="/register" className="btn-primary px-6 py-2.5 text-base">
              Start for free
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link href="/login" className="btn-ghost px-6 py-2.5 text-base">
              Sign in
            </Link>
          </div>
        </motion.div>

        {/* Demo preview */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-16 card p-6 text-left max-w-2xl mx-auto"
        >
          <div className="flex items-start gap-3 mb-4">
            <div className="w-8 h-8 rounded-full bg-surface-tertiary dark:bg-dark-elevated flex items-center justify-center shrink-0">
              <span className="text-sm">🧑</span>
            </div>
            <div className="bg-accent/10 rounded-xl px-4 py-2.5 text-sm text-ink dark:text-ink-inverse">
              What are the key findings in the Q3 report?
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-accent/10 flex items-center justify-center shrink-0">
              <span className="text-sm font-bold text-accent">D</span>
            </div>
            <div className="text-sm text-ink-secondary dark:text-ink-tertiary leading-relaxed">
              Based on the Q3 report, the three key findings are:
              <br />
              <br />
              <strong className="text-ink dark:text-ink-inverse">1. Revenue growth of 23%</strong> — driven
              primarily by the enterprise segment...
              <br />
              <span className="streaming-cursor" />
            </div>
          </div>
        </motion.div>
      </section>

      {/* Features */}
      <section className="max-w-5xl mx-auto px-6 py-16 border-t border-surface-border dark:border-dark-border">
        <h2 className="text-2xl font-semibold text-ink dark:text-ink-inverse text-center mb-12">
          Everything you need
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.07 }}
              className="p-5 rounded-xl border border-surface-border dark:border-dark-border hover:border-accent/30 transition-colors"
            >
              <f.icon className="w-5 h-5 text-accent mb-3" />
              <h3 className="font-medium text-ink dark:text-ink-inverse mb-1 text-sm">
                {f.title}
              </h3>
              <p className="text-ink-secondary dark:text-ink-tertiary text-sm leading-relaxed">
                {f.desc}
              </p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-surface-border dark:border-dark-border py-8">
        <div className="max-w-5xl mx-auto px-6 flex items-center justify-between text-xs text-ink-tertiary">
          <span>DocuMind AI</span>
          <span>Built with FastAPI · LangChain · MongoDB · Next.js</span>
        </div>
      </footer>
    </div>
  );
}
