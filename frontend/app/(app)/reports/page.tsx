"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Download, FileText, ChevronRight, CheckCircle2, Clock3 } from "lucide-react";
import { PageTitle } from "@/components/ui";
import { fetchKnowledgeIncidents, fetchPostmortemReport } from "@/lib/api";
import type { PostmortemReport } from "@/lib/types";

function ReportViewer({ incidentId }: { incidentId: string }) {
  const { data: report, isLoading } = useQuery({
    queryKey: ["report", incidentId],
    queryFn: () => fetchPostmortemReport(incidentId),
  });

  const downloadMarkdown = () => {
    if (!report) return;
    const md = `# Postmortem Report: ${report.title}

**Incident ID:** ${report.incident_id}
**Service:** ${report.service}
**Severity:** ${report.severity}
**Duration:** ${report.duration}

## Root Cause Analysis
${report.root_cause}

## Resolution Action Taken
${report.action_taken}

## Metrics Summary
${report.metrics_summary.map(m => `- ${m}`).join("\n")}

## Lessons Learned
${report.lessons_learned.map(l => `- ${l}`).join("\n")}
`;
    
    const blob = new Blob([md], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `postmortem_${report.incident_id}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const downloadJSON = () => {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `postmortem_${report.incident_id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (isLoading) return <div className="p-8 text-center text-sm text-slate-500">Generating report...</div>;
  if (!report) return <div className="p-8 text-center text-sm text-rose-400">Failed to generate report.</div>;

  return (
    <div className="rounded-xl border border-slate-700/60 bg-slate-800/20">
      <div className="flex items-center justify-between border-b border-slate-700/60 p-5">
        <div>
          <h2 className="text-base font-semibold text-slate-100">Postmortem: {report.title}</h2>
          <p className="mt-1 flex items-center gap-2 text-xs text-slate-500">
            <span>{report.incident_id}</span>
            <span>•</span>
            <span className="flex items-center gap-1"><Clock3 size={12} /> {report.duration}</span>
          </p>
        </div>
        <div className="flex gap-3">
          <button onClick={downloadJSON} className="focus-ring inline-flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900/40 px-3 py-1.5 text-xs font-medium text-slate-300 hover:bg-slate-800">
            <Download size={14} /> JSON
          </button>
          <button onClick={downloadMarkdown} className="focus-ring inline-flex items-center gap-2 rounded-lg bg-sky-500/10 px-3 py-1.5 text-xs font-medium text-sky-400 hover:bg-sky-500/20">
            <Download size={14} /> Markdown
          </button>
        </div>
      </div>
      
      <div className="p-6 space-y-8">
        <div>
          <h3 className="text-sm font-semibold text-slate-200">Root Cause</h3>
          <p className="mt-2 text-sm leading-6 text-slate-400">{report.root_cause}</p>
        </div>
        
        <div>
          <h3 className="text-sm font-semibold text-slate-200">Resolution Action</h3>
          <p className="mt-2 text-sm leading-6 text-slate-400">{report.action_taken}</p>
        </div>
        
        <div>
          <h3 className="text-sm font-semibold text-slate-200">Metrics Summary</h3>
          <ul className="mt-3 space-y-2">
            {report.metrics_summary.map((m, i) => (
              <li key={i} className="text-sm text-slate-400 flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-slate-600" /> {m}
              </li>
            ))}
          </ul>
        </div>
        
        <div>
          <h3 className="text-sm font-semibold text-emerald-300 flex items-center gap-2">
            <CheckCircle2 size={16} /> Lessons Learned
          </h3>
          <div className="mt-3 rounded-lg border border-emerald-400/20 bg-emerald-400/5 p-4">
            <ul className="space-y-3">
              {report.lessons_learned.map((l, i) => (
                <li key={i} className="text-sm text-emerald-200 flex items-start gap-2">
                  <span className="font-mono text-emerald-500/50 mt-0.5">{i+1}.</span> {l}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ReportsPage() {
  const [selectedIncident, setSelectedIncident] = useState<string | null>(null);

  const { data: incidents = [], isLoading } = useQuery({
    queryKey: ["knowledge", "incidents"],
    queryFn: fetchKnowledgeIncidents,
  });

  return (
    <div className="animate-enter">
      <PageTitle 
        eyebrow="Intelligence"
        title="Postmortem Reports" 
        description="Auto-generated postmortems for resolved incidents. Review and download for compliance."
      />

      <div className="mt-6 grid gap-6 lg:grid-cols-[300px_1fr]">
        {/* Sidebar List */}
        <div className="flex flex-col gap-2">
          {isLoading ? (
            <div className="p-4 text-sm text-slate-500">Loading incidents...</div>
          ) : incidents.length === 0 ? (
            <div className="p-4 text-sm text-slate-500">No resolved incidents found.</div>
          ) : (
            incidents.map(inc => (
              <button
                key={inc.id}
                onClick={() => setSelectedIncident(inc.id)}
                className={`flex w-full items-center justify-between rounded-xl p-4 text-left transition ${selectedIncident === inc.id ? "bg-sky-500/10 border border-sky-500/20" : "border border-slate-700/40 bg-slate-900/30 hover:bg-slate-800/40"}`}
              >
                <div>
                  <h3 className={`text-sm font-medium ${selectedIncident === inc.id ? "text-sky-300" : "text-slate-200"}`}>{inc.id}</h3>
                  <p className="mt-1 text-xs text-slate-500 line-clamp-1">{inc.title}</p>
                </div>
                <ChevronRight size={16} className={selectedIncident === inc.id ? "text-sky-400" : "text-slate-600"} />
              </button>
            ))
          )}
        </div>

        {/* Report Viewer */}
        <div>
          {selectedIncident ? (
            <ReportViewer incidentId={selectedIncident} />
          ) : (
            <div className="flex h-64 flex-col items-center justify-center rounded-xl border border-dashed border-slate-700/60 bg-slate-800/10">
              <FileText size={32} className="text-slate-600" />
              <p className="mt-4 text-sm text-slate-400">Select an incident to view its postmortem report.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
