"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  MessageSquare,
  FileText,
  Settings,
  LogOut,
} from "lucide-react";
import { useAuthStore } from "@/store/auth";
import { cn } from "@/lib/utils";

const navItems = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Chat", href: "/chat", icon: MessageSquare },
  { name: "Library", href: "/library", icon: FileText },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();

  return (
    <aside className="w-64 border-r border-surface-border dark:border-dark-border bg-surface-secondary dark:bg-dark-surface flex flex-col shrink-0 h-full">
      {/* Brand */}
      <div className="h-14 flex items-center px-6 border-b border-surface-border dark:border-dark-border">
        <Link href="/dashboard" className="font-semibold text-ink dark:text-ink-inverse">
          DocuMind <span className="text-accent">AI</span>
        </Link>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname.startsWith(item.href);
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors relative",
                isActive
                  ? "text-accent bg-accent/10"
                  : "text-ink-secondary dark:text-ink-tertiary hover:bg-surface-tertiary dark:hover:bg-dark-elevated hover:text-ink dark:hover:text-ink-inverse"
              )}
            >
              <item.icon className={cn("w-4 h-4", isActive ? "text-accent" : "opacity-70")} />
              {item.name}
              {isActive && (
                <motion.div
                  layoutId="sidebar-active"
                  className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-accent rounded-r-full"
                />
              )}
            </Link>
          );
        })}

        {user?.is_admin && (
          <div className="pt-6 mt-6 border-t border-surface-border dark:border-dark-border">
            <span className="px-3 text-xs font-medium text-ink-tertiary uppercase tracking-wider mb-2 block">
              Admin
            </span>
            <Link
              href="/admin"
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                pathname.startsWith("/admin")
                  ? "text-accent bg-accent/10"
                  : "text-ink-secondary dark:text-ink-tertiary hover:bg-surface-tertiary dark:hover:bg-dark-elevated hover:text-ink dark:hover:text-ink-inverse"
              )}
            >
              <Settings className="w-4 h-4 opacity-70" />
              Settings
            </Link>
          </div>
        )}
      </nav>

      {/* User profile / Logout */}
      <div className="p-4 border-t border-surface-border dark:border-dark-border">
        <div className="flex items-center gap-3 px-2 py-2">
          <div className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center text-accent font-medium shrink-0">
            {user?.full_name?.charAt(0) || user?.email?.charAt(0) || "U"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-ink dark:text-ink-inverse truncate">
              {user?.full_name || "User"}
            </p>
            <p className="text-xs text-ink-tertiary truncate">{user?.email}</p>
          </div>
          <button
            onClick={logout}
            className="p-1.5 text-ink-tertiary hover:text-red-500 rounded-md hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors"
            title="Log out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
