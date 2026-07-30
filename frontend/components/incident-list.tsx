"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { ArrowUpRight, ChevronDown, Filter, LoaderCircle, MoreHorizontal, RefreshCw, Search, SlidersHorizontal, X } from "lucide-react";
import { fetchIncidents } from "@/lib/api";
import type { IncidentStatus, Severity } from "@/lib/types";
import { Avatar, SeverityBadge, StatusBadge } from "@/components/ui";

const severityOptions: Array<Severity | "all"> = ["all", "critical", "high", "medium", "low"];
const statusOptions: Array<IncidentStatus | "all"> = ["all", "investigating", "mitigating", "monitoring", "resolved"];

function FilterSelect({ value, onChange, label, options }: { value: string; onChange: (value: string) => void; label: string; options: string[] }) {
  return (
    <label className="relative block">
      <span className="sr-only">{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)} className="focus-ring h-10 appearance-none rounded-xl border border-slate-700/60 bg-slate-900/50 py-2 pl-3 pr-8 text-xs text-slate-300 transition hover:border-slate-600">
        {options.map((option) => <option key={option} value={option}>{option === "all" ? `All ${label.toLowerCase()}s` : option.charAt(0).toUpperCase() + option.slice(1)}</option>)}
      </select>
      <ChevronDown size={14} className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500" />
    </label>
  );
}

export function IncidentList() {
  const [query, setQuery] = useState("");
  const [severity, setSeverity] = useState<Severity | "all">("all");
  const [status, setStatus] = useState<IncidentStatus | "all">("all");
  const [service, setService] = useState("all");

  const { data: records = [], refetch, isFetching } = useQuery({
    queryKey: ["incidents"],
    queryFn: fetchIncidents,
  });

  const refresh = async () => {
    await refetch();
  };

  const services = useMemo(() => ["all", ...Array.from(new Set(records.map((record) => record.service)))], [records]);
  const filtered = useMemo(() => records.filter((incident) => {
    const normalizedQuery = query.trim().toLowerCase();
    const searchMatch = !normalizedQuery || [incident.id, incident.title, incident.service, incident.assignee].some((value) => value.toLowerCase().includes(normalizedQuery));
    return searchMatch && (severity === "all" || incident.severity === severity) && (status === "all" || incident.status === status) && (service === "all" || incident.service === service);
  }), [records, query, severity, status, service]);

  const clearFilters = () => {
    setQuery("");
    setSeverity("all");
    setStatus("all");
    setService("all");
  };
  const hasFilters = Boolean(query) || severity !== "all" || status !== "all" || service !== "all";

  return (
    <div className="panel overflow-hidden">
      <div className="border-b border-slate-700/45 p-4 sm:p-5">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div className="relative min-w-0 flex-1 lg:max-w-md">
            <Search size={16} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search by incident, service, or owner…" className="focus-ring h-10 w-full rounded-xl border border-slate-700/60 bg-slate-900/50 pl-9 pr-9 text-sm text-slate-200 placeholder:text-slate-600 transition hover:border-slate-600" />
            {query && <button onClick={() => setQuery("")} className="focus-ring absolute right-2 top-1/2 grid h-6 w-6 -translate-y-1/2 place-items-center rounded-md text-slate-500 hover:bg-slate-800 hover:text-slate-200" aria-label="Clear search"><X size={14} /></button>}
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="hidden items-center gap-1.5 text-xs text-slate-500 sm:flex"><SlidersHorizontal size={14} />Filters</span>
            <FilterSelect label="Severity" value={severity} onChange={(value) => setSeverity(value as Severity | "all")} options={severityOptions} />
            <FilterSelect label="Status" value={status} onChange={(value) => setStatus(value as IncidentStatus | "all")} options={statusOptions} />
            <FilterSelect label="Service" value={service} onChange={setService} options={services} />
            <button onClick={() => void refresh()} disabled={isFetching} className="focus-ring grid h-10 w-10 place-items-center rounded-xl border border-slate-700/60 bg-slate-900/50 text-slate-400 transition hover:border-slate-600 hover:text-slate-100 disabled:cursor-wait" aria-label="Refresh incidents"><RefreshCw size={15} className={isFetching ? "animate-spin" : ""} /></button>
          </div>
        </div>
        <div className="mt-3 flex items-center justify-between gap-3 text-xs"><p className="text-slate-500"><span className="font-medium text-slate-300">{filtered.length}</span> {filtered.length === 1 ? "incident" : "incidents"} shown {isFetching && <span className="ml-1 inline-flex items-center gap-1 text-sky-300"><LoaderCircle size={12} className="animate-spin" />syncing</span>}</p>{hasFilters && <button onClick={clearFilters} className="focus-ring inline-flex items-center gap-1.5 rounded-md px-1 py-1 font-medium text-sky-300 hover:text-sky-200"><Filter size={12} />Clear filters</button>}</div>
      </div>

      <div className="hidden overflow-x-auto lg:block">
        <table className="w-full min-w-[900px] text-left">
          <thead className="border-b border-slate-700/35 bg-slate-900/20 text-[10px] uppercase tracking-[0.13em] text-slate-500">
            <tr><th className="px-5 py-3.5 font-medium">Incident</th><th className="px-3 py-3.5 font-medium">Severity</th><th className="px-3 py-3.5 font-medium">Service</th><th className="px-3 py-3.5 font-medium">Status</th><th className="px-3 py-3.5 font-medium">Assigned to</th><th className="px-3 py-3.5 font-medium">Created</th><th className="px-5 py-3.5 text-right font-medium">Actions</th></tr>
          </thead>
          <tbody className="divide-y divide-slate-700/35">
            {filtered.map((incident) => (
              <tr key={incident.id} className="group transition hover:bg-slate-800/25">
                <td className="px-5 py-4"><Link href={`/incidents/${incident.id}`} className="focus-ring block rounded-md"><p className="text-xs font-medium text-slate-500">{incident.id}</p><p className="mt-1 max-w-[255px] truncate text-sm font-medium text-slate-100 transition group-hover:text-sky-200">{incident.title}</p></Link></td>
                <td className="px-3 py-4"><SeverityBadge severity={incident.severity} /></td>
                <td className="px-3 py-4 text-sm text-slate-300">{incident.service}</td>
                <td className="px-3 py-4"><StatusBadge status={incident.status} /></td>
                <td className="px-3 py-4"><div className="flex items-center gap-2"><Avatar name={incident.assignee} small /><span className="text-sm text-slate-300">{incident.assignee}</span></div></td>
                <td className="px-3 py-4"><p className="text-sm text-slate-400">{incident.createdAt}</p><p className="mt-0.5 text-[11px] text-slate-600">Updated {incident.updatedAt}</p></td>
                <td className="px-5 py-4"><div className="flex items-center justify-end gap-1"><Link href={`/incidents/${incident.id}`} className="focus-ring inline-flex h-8 items-center gap-1 rounded-lg px-2 text-xs font-medium text-sky-300 hover:bg-sky-400/10 hover:text-sky-200">Open <ArrowUpRight size={13} /></Link><button className="focus-ring grid h-8 w-8 place-items-center rounded-lg text-slate-500 hover:bg-slate-800 hover:text-slate-200" aria-label={`More options for ${incident.id}`}><MoreHorizontal size={17} /></button></div></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="divide-y divide-slate-700/35 lg:hidden">
        {filtered.map((incident) => (
          <Link href={`/incidents/${incident.id}`} key={incident.id} className="focus-ring block p-4 transition hover:bg-slate-800/25 sm:p-5">
            <div className="flex items-start justify-between gap-3"><div className="min-w-0"><div className="flex flex-wrap items-center gap-2"><span className="text-xs font-medium text-slate-500">{incident.id}</span><SeverityBadge severity={incident.severity} /></div><p className="mt-2 truncate text-sm font-medium text-slate-100">{incident.title}</p></div><StatusBadge status={incident.status} /></div>
            <div className="mt-3 flex items-center justify-between gap-3"><p className="text-xs text-slate-500">{incident.service} · {incident.createdAt}</p><div className="flex items-center gap-2 text-xs text-slate-400"><Avatar name={incident.assignee} small />{incident.assignee}</div></div>
          </Link>
        ))}
      </div>

      {filtered.length === 0 && <div className="grid min-h-64 place-items-center p-8 text-center"><div><span className="mx-auto grid h-11 w-11 place-items-center rounded-xl bg-slate-800/70 text-slate-500"><Filter size={18} /></span><h3 className="mt-4 text-sm font-medium text-slate-200">No incidents match these filters</h3><p className="mt-1 text-xs text-slate-500">Try widening your search or clearing filters.</p><button onClick={clearFilters} className="focus-ring mt-4 rounded-lg bg-sky-400 px-3 py-2 text-xs font-semibold text-slate-950 hover:bg-sky-300">Reset filters</button></div></div>}
    </div>
  );
}
