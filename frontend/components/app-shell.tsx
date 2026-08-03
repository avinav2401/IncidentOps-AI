"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";
import { useState, useEffect, type ReactNode } from "react";
import {
  Activity,
  BarChart3,
  Bell,
  BookOpen,
  Bot,
  ChevronDown,
  Command,
  FileText,
  LayoutDashboard,
  Layers,
  Menu,
  Network,
  Search,
  Settings,
  ShieldAlert,
  User,
  Users,
  X,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

const mainNavigation: { label: string; href: string; icon: LucideIcon }[] = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Incidents", href: "/incidents", icon: ShieldAlert },
  { label: "AI Investigation", href: "/agents", icon: Bot },
  { label: "Training", href: "/training", icon: Command },
  { label: "Analytics", href: "/analytics", icon: BarChart3 },
];

const intelligenceNavigation: { label: string; href: string; icon: LucideIcon }[] = [
  { label: "Knowledge Base", href: "/knowledge", icon: BookOpen },
  { label: "Reports", href: "/reports", icon: FileText },
  { label: "Architecture", href: "/architecture", icon: Network },
];

function Navigation({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();
  const isActive = (href: string) => pathname.startsWith(href);

  return (
    <nav className="flex h-full flex-col px-3 py-5" aria-label="Main navigation">
      <Link href="/dashboard" className="focus-ring mb-9 flex items-center gap-3 rounded-xl px-3 py-2" onClick={onNavigate}>
        <span className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-sky-400 to-indigo-500 text-slate-950 shadow-glow-blue">
          <Activity size={20} strokeWidth={2.6} />
        </span>
        <span>
          <span className="block text-sm font-semibold tracking-tight text-slate-100">IncidentOps</span>
          <span className="block text-[10px] font-semibold uppercase tracking-[0.2em] text-sky-300">AI Command</span>
        </span>
      </Link>

      <p className="eyebrow px-3 pb-2">Workspace</p>
      <div className="space-y-1">
        {mainNavigation.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onNavigate}
              className={`focus-ring flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition ${active ? "bg-sky-400/10 font-medium text-sky-100 shadow-[inset_0_0_0_1px_rgba(56,189,248,0.14)]" : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-100"}`}
            >
              <Icon size={18} strokeWidth={active ? 2.35 : 1.9} />
              <span>{item.label}</span>
              {item.label === "Incidents" && <span className="ml-auto rounded-md bg-rose-400/15 px-1.5 py-0.5 text-[10px] font-semibold text-rose-200">3</span>}
            </Link>
          );
        })}
      </div>

      <p className="eyebrow px-3 pb-2 mt-6">Intelligence</p>
      <div className="space-y-1">
        {intelligenceNavigation.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onNavigate}
              className={`focus-ring flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition ${active ? "bg-sky-400/10 font-medium text-sky-100 shadow-[inset_0_0_0_1px_rgba(56,189,248,0.14)]" : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-100"}`}
            >
              <Icon size={18} strokeWidth={active ? 2.35 : 1.9} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </div>

      <div className="mt-auto space-y-1 border-t border-slate-700/50 pt-4">
        <p className="eyebrow px-3 pb-2">Management</p>
        <Link
          href="/integrations"
          onClick={onNavigate}
          className={`focus-ring flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition ${isActive("/integrations") ? "bg-sky-400/10 font-medium text-sky-100" : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-100"}`}
        >
          <Layers size={18} strokeWidth={1.9} />
          Integrations
        </Link>
        <Link
          href="/users"
          onClick={onNavigate}
          className={`focus-ring flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition ${isActive("/users") ? "bg-sky-400/10 font-medium text-sky-100" : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-100"}`}
        >
          <Users size={18} strokeWidth={1.9} />
          Users
        </Link>
        <Link
          href="/settings"
          onClick={onNavigate}
          className={`focus-ring flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition ${isActive("/settings") ? "bg-sky-400/10 font-medium text-sky-100" : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-100"}`}
        >
          <Settings size={18} strokeWidth={1.9} />
          Settings
        </Link>
        <Link
          href="/profile"
          onClick={onNavigate}
          className={`focus-ring flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition ${isActive("/profile") ? "bg-sky-400/10 font-medium text-sky-100" : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-100"}`}
        >
          <User size={18} strokeWidth={1.9} />
          Profile
        </Link>
        <div className="mt-3 rounded-xl border border-emerald-400/10 bg-emerald-400/[0.045] px-3 py-3">
          <div className="flex items-center gap-2 text-xs font-medium text-emerald-200"><span className="h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,.8)]" />All systems operational</div>
          <p className="mt-1 text-[11px] leading-4 text-slate-500">42 services are reporting healthy telemetry.</p>
        </div>
      </div>
    </nav>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const pathname = usePathname();
  const { isAuthenticated, loading, user, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !isAuthenticated && pathname !== "/login") {
      router.push("/login");
    }
  }, [isAuthenticated, loading, pathname, router]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setSearchOpen(prev => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  if (pathname === "/login") {
    return <>{children}</>;
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#07111f]">
        <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-sky-400"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[250px_1fr]">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-[250px] border-r border-slate-700/50 bg-[#081422]/90 backdrop-blur-xl lg:block">
        <Navigation />
      </aside>

      {menuOpen && (
        <div className="fixed inset-0 z-40 lg:hidden" role="dialog" aria-modal="true" aria-label="Navigation menu">
          <button className="absolute inset-0 bg-slate-950/70 backdrop-blur-sm" aria-label="Close navigation" onClick={() => setMenuOpen(false)} />
          <aside className="relative h-full w-[276px] border-r border-slate-700/60 bg-[#081422] shadow-2xl">
            <button className="focus-ring absolute right-3 top-5 grid h-9 w-9 place-items-center rounded-lg text-slate-400 hover:bg-slate-800 hover:text-white" onClick={() => setMenuOpen(false)} aria-label="Close navigation">
              <X size={18} />
            </button>
            <Navigation onNavigate={() => setMenuOpen(false)} />
          </aside>
        </div>
      )}

      {searchOpen && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 bg-slate-950/70 backdrop-blur-sm" onClick={() => setSearchOpen(false)}>
          <div className="w-full max-w-xl rounded-xl border border-slate-700 bg-slate-900 shadow-2xl overflow-hidden animate-in fade-in slide-in-from-top-4 duration-200" onClick={e => e.stopPropagation()}>
            <div className="flex items-center px-4 py-3 border-b border-slate-800">
              <Search size={18} className="text-slate-500" />
              <input autoFocus placeholder="Search incidents, services, or commands..." className="w-full bg-transparent px-3 py-1 text-sm text-slate-200 outline-none placeholder:text-slate-500" />
              <kbd className="hidden sm:inline-block rounded border border-slate-700 bg-slate-800 px-1.5 py-0.5 text-[10px] text-slate-400">ESC</kbd>
            </div>
            <div className="p-8 text-center text-xs text-slate-500">
              No recent searches. Start typing to find resources.
            </div>
          </div>
        </div>
      )}

      <main className="min-w-0 lg:col-start-2">
        <header className="sticky top-0 z-20 flex h-[70px] items-center justify-between border-b border-slate-700/40 bg-[#07111f]/80 px-4 backdrop-blur-xl sm:px-7 lg:px-10">
          <div className="flex min-w-0 items-center gap-3">
            <button className="focus-ring grid h-9 w-9 place-items-center rounded-lg text-slate-300 hover:bg-slate-800 lg:hidden" aria-label="Open navigation" onClick={() => setMenuOpen(true)}>
              <Menu size={20} />
            </button>
            <div className="hidden items-center gap-2 text-xs text-slate-500 sm:flex">
              <Command size={14} />
              <span>Command center</span>
              <span className="h-1 w-1 rounded-full bg-slate-600" />
              <span className="text-emerald-300">Live</span>
            </div>
          </div>
          <div className="flex items-center gap-2 sm:gap-3">
            <button onClick={() => setSearchOpen(true)} className="focus-ring hidden h-9 items-center gap-2 rounded-lg border border-slate-700/60 bg-slate-900/45 px-3 text-xs text-slate-500 transition hover:border-slate-600 hover:text-slate-300 md:flex" aria-label="Search command center">
              <Search size={14} />
              <span>Search</span>
              <kbd className="rounded border border-slate-700 bg-slate-800 px-1.5 py-0.5 text-[10px] text-slate-400">⌘ K</kbd>
            </button>
            <div className="relative">
              <button onClick={() => setNotifOpen(!notifOpen)} className="focus-ring relative grid h-9 w-9 place-items-center rounded-lg text-slate-400 hover:bg-slate-800 hover:text-slate-100" aria-label="Notifications">
                <Bell size={18} />
                <span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-rose-400 ring-2 ring-[#0b1725]" />
              </button>
              {notifOpen && (
                <div className="absolute right-0 top-full mt-2 w-72 sm:w-80 rounded-xl border border-slate-700 bg-slate-900 shadow-2xl overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
                  <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800">
                    <span className="text-sm font-semibold text-slate-200">Notifications</span>
                    <button onClick={() => setNotifOpen(false)} className="text-xs text-sky-400 hover:text-sky-300">Mark all read</button>
                  </div>
                  <div className="p-6 text-center text-xs text-slate-500">
                    <div className="mx-auto mb-2 grid h-10 w-10 place-items-center rounded-full bg-slate-800">
                      <Bell size={16} className="text-slate-400" />
                    </div>
                    You&apos;re all caught up!
                  </div>
                </div>
              )}
            </div>
            <button 
              onClick={() => logout()}
              className="focus-ring flex items-center gap-2 rounded-lg py-1 pl-1 pr-0.5 text-left transition hover:bg-slate-800" 
              aria-label="Open profile menu (Logout for now)"
              title="Click to logout"
            >
              <span className="grid h-8 w-8 place-items-center rounded-lg bg-gradient-to-br from-violet-400 to-sky-400 text-[10px] font-bold text-slate-950 uppercase">
                {user?.avatar_initials || "U"}
              </span>
              <span className="hidden pr-1 sm:block">
                <span className="block text-xs font-medium text-slate-200">{user?.name || "User"}</span>
                <span className="block text-[10px] text-slate-500 capitalize">{user?.role?.replace("_", " ")}</span>
              </span>
              <ChevronDown size={14} className="hidden text-slate-500 sm:block" />
            </button>
          </div>
        </header>
        <div className="mx-auto w-full max-w-[1600px] px-4 py-6 sm:px-7 sm:py-8 lg:px-10">
          {children}
        </div>
      </main>
    </div>
  );
}
