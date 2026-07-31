"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { BookOpen, ChevronRight, FileText, Search, ShieldCheck } from "lucide-react";
import { PageTitle } from "@/components/ui";
import { fetchKnowledgeIncidents, fetchRunbooks } from "@/lib/api";

export default function KnowledgeBasePage() {
  const [search, setSearch] = useState("");
  const [activeTab, setActiveTab] = useState<"incidents" | "runbooks">("incidents");

  const { data: incidents = [], isLoading: loadingIncidents } = useQuery({
    queryKey: ["knowledge", "incidents"],
    queryFn: fetchKnowledgeIncidents,
  });

  const { data: runbooks = [], isLoading: loadingRunbooks } = useQuery({
    queryKey: ["knowledge", "runbooks"],
    queryFn: fetchRunbooks,
  });

  const filteredIncidents = incidents.filter(i => 
    i.title.toLowerCase().includes(search.toLowerCase()) || 
    i.root_cause.toLowerCase().includes(search.toLowerCase()) ||
    i.service.toLowerCase().includes(search.toLowerCase())
  );

  const filteredRunbooks = runbooks.filter(r => 
    r.title.toLowerCase().includes(search.toLowerCase()) || 
    r.description.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="animate-enter">
      <PageTitle 
        eyebrow="Intelligence"
        title="Knowledge Base" 
        description="Search past incidents and runbooks. AI automatically references these when suggesting remediations."
      />

      {/* ── Search Bar ── */}
      <div className="relative mt-2">
        <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
        <input 
          type="text" 
          placeholder="Search for past incidents, error messages, or runbooks..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="focus-ring w-full rounded-xl border border-slate-700/60 bg-slate-900/40 py-3.5 pl-12 pr-4 text-sm text-slate-200 placeholder-slate-500 transition focus:bg-slate-800/80"
        />
      </div>

      {/* ── Tabs ── */}
      <div className="mt-8 flex gap-6 border-b border-slate-700/60 px-1">
        <button 
          onClick={() => setActiveTab("incidents")}
          className={`pb-3 text-sm font-medium transition ${activeTab === "incidents" ? "border-b-2 border-sky-400 text-sky-400" : "text-slate-400 hover:text-slate-200"}`}
        >
          Resolved Incidents <span className="ml-2 rounded-full bg-slate-800 px-2 py-0.5 text-xs text-slate-400">{incidents.length}</span>
        </button>
        <button 
          onClick={() => setActiveTab("runbooks")}
          className={`pb-3 text-sm font-medium transition ${activeTab === "runbooks" ? "border-b-2 border-sky-400 text-sky-400" : "text-slate-400 hover:text-slate-200"}`}
        >
          Runbooks <span className="ml-2 rounded-full bg-slate-800 px-2 py-0.5 text-xs text-slate-400">{runbooks.length}</span>
        </button>
      </div>

      {/* ── Content ── */}
      <div className="mt-6">
        {activeTab === "incidents" && (
          loadingIncidents ? (
            <div className="flex h-32 items-center justify-center text-sm text-slate-500">Loading incidents...</div>
          ) : filteredIncidents.length === 0 ? (
            <div className="flex h-32 items-center justify-center text-sm text-slate-500">No matching incidents found.</div>
          ) : (
            <div className="grid gap-4 xl:grid-cols-2">
              {filteredIncidents.map(inc => (
                <article key={inc.id} className="panel-soft p-5 transition hover:-translate-y-0.5 hover:border-slate-600">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <span className="grid h-10 w-10 place-items-center rounded-xl bg-emerald-400/10 text-emerald-400">
                        <ShieldCheck size={18} />
                      </span>
                      <div>
                        <h3 className="text-sm font-semibold text-slate-100">{inc.title}</h3>
                        <p className="text-xs text-slate-500">{inc.id} • {inc.service} • {inc.date}</p>
                      </div>
                    </div>
                  </div>
                  <div className="mt-5 space-y-3 rounded-xl border border-slate-700/40 bg-slate-900/30 p-4">
                    <div>
                      <p className="text-xs font-medium text-slate-400">Root Cause</p>
                      <p className="mt-1 text-xs leading-5 text-slate-300">{inc.root_cause}</p>
                    </div>
                    <div>
                      <p className="text-xs font-medium text-slate-400">Resolution</p>
                      <p className="mt-1 text-xs leading-5 text-emerald-300">{inc.resolution}</p>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )
        )}

        {activeTab === "runbooks" && (
          loadingRunbooks ? (
            <div className="flex h-32 items-center justify-center text-sm text-slate-500">Loading runbooks...</div>
          ) : filteredRunbooks.length === 0 ? (
            <div className="flex h-32 items-center justify-center text-sm text-slate-500">No matching runbooks found.</div>
          ) : (
            <div className="grid gap-4">
              {filteredRunbooks.map(rb => (
                <details key={rb.id} className="group panel overflow-hidden rounded-xl border border-slate-700/60 bg-slate-800/20">
                  <summary className="flex cursor-pointer items-center justify-between p-5 hover:bg-slate-800/40">
                    <div className="flex items-center gap-4">
                      <span className="grid h-10 w-10 place-items-center rounded-xl bg-amber-400/10 text-amber-400">
                        <BookOpen size={18} />
                      </span>
                      <div>
                        <h3 className="text-sm font-semibold text-slate-100">{rb.title}</h3>
                        <p className="text-xs text-slate-500">{rb.id} • {rb.service}</p>
                      </div>
                    </div>
                    <ChevronRight size={18} className="text-slate-500 transition group-open:rotate-90" />
                  </summary>
                  <div className="border-t border-slate-700/40 bg-slate-900/30 p-5">
                    <p className="text-sm text-slate-300">{rb.description}</p>
                    <div className="mt-4">
                      <p className="text-xs font-medium text-slate-400">Execution Steps</p>
                      <ul className="mt-3 space-y-2">
                        {rb.steps.map((step, idx) => (
                          <li key={idx} className="flex items-start gap-3 text-sm text-slate-300">
                            <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-slate-800 text-[10px] text-slate-400">{idx + 1}</span>
                            <span className="mt-0.5 font-mono text-[11px] text-sky-200">{step}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </details>
              ))}
            </div>
          )
        )}
      </div>
    </div>
  );
}
