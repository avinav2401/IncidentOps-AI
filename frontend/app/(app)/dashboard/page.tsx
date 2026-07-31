"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight, CheckCircle2, ChevronRight, Clock3, ShieldAlert, Siren, Sparkles, TrendingDown, TrendingUp, Zap, Activity } from "lucide-react";
import { activityEvents } from "@/lib/mock-data";
import { AIIndicator, Avatar, MetricLink, PageTitle, SeverityBadge, StatusBadge } from "@/components/ui";
import { ServiceGraph } from "@/components/service-graph";
import { fetchIncidents, fetchAnalytics, simulateIncident } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

const metricIcons = [Zap, Siren, CheckCircle2, Clock3];
const metricStyles = ["text-sky-300 bg-sky-400/10", "text-rose-300 bg-rose-400/10", "text-emerald-300 bg-emerald-400/10", "text-violet-300 bg-violet-400/10"];

export default function DashboardPage() {
  const { user } = useAuth();
  
  const { data: incidents = [], isLoading: loadingIncidents } = useQuery({
    queryKey: ["incidents"],
    queryFn: fetchIncidents,
  });

  const { data: analytics, isLoading: loadingAnalytics } = useQuery({
    queryKey: ["analytics"],
    queryFn: fetchAnalytics,
  });

  const activeIncidents = incidents.filter((incident) => incident.status !== "resolved").slice(0, 4);
  const trendData = analytics?.trend || [];
  const weeklyIncidents = trendData.length ? trendData.map((t: any) => t.opened) : [0, 0, 0, 0, 0, 0, 0];
  const weeklyChartLabels = trendData.length ? trendData.map((t: any) => t.label) : ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const peak = Math.max(...weeklyIncidents, 1); // Avoid division by zero

  const dashboardMetrics = [
    { label: "Total incidents", value: analytics?.overview?.total_incidents?.toString() || "-", change: "This week" },
    { label: "Critical", value: analytics?.by_severity?.P1?.toString() || "0", change: "Requires attention" },
    { label: "Resolved today", value: analytics?.overview?.resolved_incidents?.toString() || "0", change: "Great job" },
    { label: "Avg. resolution", value: `${analytics?.overview?.mean_time_to_resolution_minutes || 0} min`, change: "Across all resolved" },
  ];

  if (loadingIncidents || loadingAnalytics) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-sky-400"></div>
      </div>
    );
  }

  return (
    <div className="animate-enter">
      <PageTitle
        eyebrow="On-call workspace"
        title={`Good morning, ${user?.name?.split(" ")[0] || "commander"}.`}
        description={`Here’s the operational picture across your services. ${activeIncidents.length} incidents need attention.`}
        action={
          <div className="flex gap-3">
            <button
              onClick={async () => {
                try {
                  await simulateIncident();
                  window.location.reload();
                } catch (e) {
                  console.error(e);
                }
              }}
              className="focus-ring inline-flex items-center justify-center gap-2 rounded-xl border border-slate-700/60 bg-slate-800/35 px-4 py-2.5 text-sm font-semibold text-slate-300 transition hover:bg-slate-700/50"
            >
              <Zap size={16} /> Trigger Simulation
            </button>
            <Link href="/incidents" className="focus-ring inline-flex items-center justify-center gap-2 rounded-xl bg-sky-400 px-4 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-sky-300">
              <ShieldAlert size={16} /> Review incidents
            </Link>
          </div>
        }
      />

      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4" aria-label="Incident overview statistics">
        {dashboardMetrics.map((metric, index) => {
          const Icon = metricIcons[index];
          const Trend = metric.label === "Resolved today" || metric.label === "Avg. resolution" ? TrendingDown : TrendingUp;
          return (
            <article key={metric.label} className="panel group relative overflow-hidden p-4 transition hover:-translate-y-0.5 hover:border-slate-600/70 sm:p-5">
              <div className="absolute -right-6 -top-6 h-24 w-24 rounded-full bg-sky-400/[0.035] blur-2xl" />
              <div className="relative flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-400">{metric.label}</p>
                  <p className="mt-3 text-3xl font-semibold tracking-[-0.04em] text-slate-100">{metric.value}</p>
                </div>
                <span className={`grid h-9 w-9 place-items-center rounded-xl ${metricStyles[index]}`}><Icon size={18} /></span>
              </div>
              <div className="relative mt-4 flex items-center gap-1.5 text-xs text-slate-500"><Trend size={13} className={metric.label === "Critical" ? "text-rose-300" : "text-emerald-300"} />{metric.change}</div>
            </article>
          );
        })}
      </section>

      <section className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1.6fr)_minmax(320px,0.9fr)]">
        <div className="panel overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-700/45 px-5 py-4 sm:px-6">
            <div>
              <div className="flex items-center gap-2"><h2 className="text-sm font-semibold text-slate-100">Active incidents</h2><span className="rounded-md bg-rose-400/10 px-1.5 py-0.5 text-[10px] font-semibold text-rose-200">{activeIncidents.length} active</span></div>
              <p className="mt-1 text-xs text-slate-500">Prioritized by customer impact and urgency.</p>
            </div>
            <Link href="/incidents" className="focus-ring group inline-flex items-center gap-1 text-xs font-medium text-sky-300 hover:text-sky-200">View all <ChevronRight size={14} className="transition group-hover:translate-x-0.5" /></Link>
          </div>
          <div className="divide-y divide-slate-700/35">
            {activeIncidents.length === 0 ? (
              <div className="px-5 py-8 text-center text-sm text-slate-500">No active incidents right now.</div>
            ) : (
              activeIncidents.map((incident) => (
                <Link key={incident.id} href={`/incidents/${incident.id}`} className="focus-ring group flex items-center gap-3 px-5 py-4 transition hover:bg-slate-800/25 sm:gap-4 sm:px-6">
                  <span className={`hidden h-9 w-1 rounded-full sm:block ${incident.severity === "critical" ? "bg-rose-400" : incident.severity === "high" ? "bg-amber-400" : "bg-sky-400"}`} />
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2"><span className="text-xs font-medium text-slate-500">{incident.id}</span><SeverityBadge severity={incident.severity} /></div>
                    <p className="mt-1 truncate text-sm font-medium text-slate-100 transition group-hover:text-sky-200">{incident.title}</p>
                    <p className="mt-1 truncate text-xs text-slate-500">{incident.service}</p>
                  </div>
                  <div className="hidden text-right sm:block"><StatusBadge status={incident.status} /><div className="mt-2 flex items-center justify-end gap-2 text-xs text-slate-400"><Avatar name={incident.assignee} small />{incident.assignee}</div></div>
                  <ArrowRight size={17} className="shrink-0 text-slate-600 transition group-hover:translate-x-1 group-hover:text-sky-300" />
                </Link>
              ))
            )}
          </div>
        </div>

        <aside className="panel p-5 sm:p-6">
          <div className="flex items-center justify-between"><div><h2 className="text-sm font-semibold text-slate-100">Agent activity</h2><p className="mt-1 text-xs text-slate-500">Autonomous work in your response loop.</p></div><AIIndicator label="4 agents" /></div>
          <div className="mt-6 space-y-5">
            {activityEvents.slice(0, 4).map((event, index) => (
              <div key={`${event.time}-${event.agent}`} className="relative flex gap-3">
                {index !== 3 && <span className="absolute left-[5px] top-4 h-[calc(100%+9px)] w-px bg-slate-700/55" />}
                <span className={`relative mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full ring-4 ring-[#0c1928] ${event.tone === "success" ? "bg-emerald-400" : event.tone === "warning" ? "bg-amber-400" : "bg-sky-400"}`} />
                <div className="min-w-0"><div className="flex items-center gap-2"><p className="text-xs font-medium text-slate-300">{event.agent}</p><span className="text-[10px] text-slate-600">{event.time}</span></div><p className="mt-1 text-xs leading-5 text-slate-500">{event.message}</p></div>
              </div>
            ))}
          </div>
          <Link href="/agents" className="focus-ring mt-6 flex items-center justify-center gap-2 rounded-xl border border-slate-700/60 bg-slate-800/35 px-3 py-2.5 text-xs font-medium text-slate-300 transition hover:border-slate-600 hover:bg-slate-800/70 hover:text-white">Open agent workspace <ArrowRight size={14} /></Link>
        </aside>
      </section>

      {/* ── Service Graph ── */}
      <section className="mt-6 panel flex flex-col" aria-label="Service dependencies">
        <div className="flex items-center gap-2 border-b border-slate-700/60 p-5">
          <Activity size={16} className="text-emerald-400" />
          <h2 className="text-sm font-semibold text-slate-100">Service Topology</h2>
        </div>
        <div className="flex-1 p-5 min-h-[300px]">
          <ServiceGraph />
        </div>
      </section>

      <section className="mt-6 grid gap-6 lg:grid-cols-[minmax(0,1.25fr)_minmax(310px,0.75fr)]">
        <div className="panel p-5 sm:p-6">
          <div className="flex flex-wrap items-start justify-between gap-3"><div><h2 className="text-sm font-semibold text-slate-100">Incident volume</h2><p className="mt-1 text-xs text-slate-500">Last 7 days · all severities</p></div><div className="rounded-lg border border-emerald-400/15 bg-emerald-400/[0.06] px-2.5 py-1.5 text-xs font-medium text-emerald-200">−14% vs. last week</div></div>
          <div className="mt-8 flex h-36 items-end gap-3 sm:gap-5" aria-label="Weekly incident bar chart">
            {weeklyIncidents.map((value: number, index: number) => (
              <div key={weeklyChartLabels[index] || index} className="group flex h-full min-w-0 flex-1 flex-col justify-end gap-2">
                <div className="relative flex flex-1 items-end"><div className="absolute bottom-0 left-0 right-0 rounded-t-lg bg-sky-400/15" style={{ height: `${(value / peak) * 100}%` }} /><div className="relative z-10 w-full rounded-t-lg bg-gradient-to-t from-sky-500 to-cyan-300 transition duration-300 group-hover:from-sky-400 group-hover:to-sky-200" style={{ height: `${(value / peak) * 72}%` }} title={`${value} incidents`} /></div>
                <span className="text-center text-[10px] text-slate-500">{weeklyChartLabels[index]}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="panel relative overflow-hidden p-5 sm:p-6">
          <div className="absolute right-0 top-0 h-40 w-40 rounded-full bg-violet-400/[0.07] blur-3xl" />
          <div className="relative"><div className="flex items-center justify-between"><div><h2 className="text-sm font-semibold text-slate-100">Response health</h2><p className="mt-1 text-xs text-slate-500">This week’s operating signal.</p></div><Sparkles size={18} className="text-violet-300" /></div>
            <div className="mt-7 grid grid-cols-2 gap-3"><div className="panel-soft p-3"><p className="text-[11px] text-slate-500">Automation assist</p><p className="mt-2 text-xl font-semibold tracking-tight text-slate-100">76%</p><p className="mt-1 text-[10px] text-emerald-300">+8 points</p></div><div className="panel-soft p-3"><p className="text-[11px] text-slate-500">SLO compliance</p><p className="mt-2 text-xl font-semibold tracking-tight text-slate-100">99.94%</p><p className="mt-1 text-[10px] text-emerald-300">On target</p></div></div>
            <Link href="/analytics" className="focus-ring group mt-5 flex items-center justify-between rounded-xl border border-slate-700/55 bg-slate-800/30 px-3 py-2.5 transition hover:bg-slate-800/65"><span className="text-xs text-slate-400">Explore performance analytics</span><MetricLink>View report</MetricLink></Link>
          </div>
        </div>
      </section>
    </div>
  );
}
