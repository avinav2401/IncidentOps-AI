"use client";

import { useState } from "react";
import { Check, CheckCircle2, ChevronDown, CircleAlert, CircleCheck, Clock3, FileText, LoaderCircle, MessageSquare, ShieldCheck, Sparkles, ThumbsDown, ThumbsUp, TriangleAlert, X } from "lucide-react";
import { triggerAnalysis, submitRecommendationDecision } from "@/lib/api";
import type { Incident } from "@/lib/types";
import { AIIndicator, Avatar, SeverityBadge, StatusBadge } from "@/components/ui";

const eventIcons = {
  detection: CircleAlert,
  update: Clock3,
  action: ShieldCheck,
  ai: Sparkles,
  resolution: CircleCheck,
};

const eventTones = {
  detection: "border-rose-400/25 bg-rose-400/10 text-rose-300",
  update: "border-sky-400/25 bg-sky-400/10 text-sky-300",
  action: "border-violet-400/25 bg-violet-400/10 text-violet-300",
  ai: "border-cyan-400/25 bg-cyan-400/10 text-cyan-300",
  resolution: "border-emerald-400/25 bg-emerald-400/10 text-emerald-300",
};

export function IncidentDetail({ incident, onRefetch }: { incident: Incident, onRefetch?: () => void }) {
  const [decision, setDecision] = useState<"approved" | "rejected" | null>(null);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [analyzing, setAnalyzing] = useState(false);

  const decide = async (nextDecision: "approved" | "rejected") => {
    setSaving(true);
    const remoteSaved = await submitRecommendationDecision(incident.id, nextDecision);
    setDecision(nextDecision);
    setMessage(remoteSaved ? `Recommendation ${nextDecision} and recorded.` : `Recommendation ${nextDecision}; saved locally until the API reconnects.`);
    setSaving(false);
    if (onRefetch) onRefetch();
  };

  const handleTriggerAnalysis = async () => {
    setAnalyzing(true);
    await triggerAnalysis(incident.id);
    if (onRefetch) onRefetch();
    setAnalyzing(false);
  };

  return (
    <div className="animate-enter">
      <section className="panel overflow-hidden">
        <div className="relative overflow-hidden border-b border-slate-700/45 px-5 py-5 sm:px-7 sm:py-6">
          <div className="absolute -right-16 -top-20 h-52 w-52 rounded-full bg-rose-400/[0.07] blur-3xl" />
          <div className="relative flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2"><span className="text-xs font-medium text-slate-500">{incident.id}</span><SeverityBadge severity={incident.severity} /><StatusBadge status={incident.status} /></div>
              <h1 className="mt-3 text-2xl font-semibold tracking-[-0.035em] text-slate-100 sm:text-[30px]">{incident.title}</h1>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">{incident.description}</p>
            </div>
            <div className="flex shrink-0 items-center gap-2">
              {incident.status === "investigating" && (
                <button disabled={analyzing || incident.status === "investigating"} onClick={handleTriggerAnalysis} className="focus-ring inline-flex items-center gap-2 rounded-xl bg-violet-500/20 px-3 py-2 text-xs font-medium text-violet-300 hover:bg-violet-500/30 disabled:opacity-50">
                  {analyzing || incident.status === "investigating" ? <LoaderCircle size={14} className="animate-spin" /> : <Sparkles size={14} />}
                  {analyzing || incident.status === "investigating" ? "AI Analyzing..." : "Run AI Analysis"}
                </button>
              )}
              <button className="focus-ring inline-flex items-center gap-2 rounded-xl border border-slate-700/60 bg-slate-900/45 px-3 py-2 text-xs font-medium text-slate-300 hover:border-slate-600 hover:text-white"><MessageSquare size={14} />Notes</button><button className="focus-ring grid h-9 w-9 place-items-center rounded-xl border border-slate-700/60 bg-slate-900/45 text-slate-400 hover:border-slate-600 hover:text-white" aria-label="More incident options"><ChevronDown size={17} /></button></div>
          </div>
          <div className="relative mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <div className="panel-soft px-3.5 py-3"><p className="eyebrow">Service</p><p className="mt-1.5 text-sm font-medium text-slate-200">{incident.service}</p></div>
            <div className="panel-soft px-3.5 py-3"><p className="eyebrow">Impact</p><p className="mt-1.5 text-sm font-medium text-slate-200">{incident.affectedUsers}</p></div>
            <div className="panel-soft px-3.5 py-3"><p className="eyebrow">Duration</p><p className="mt-1.5 text-sm font-medium text-slate-200">{incident.duration}</p></div>
            <div className="panel-soft px-3.5 py-3"><p className="eyebrow">Incident lead</p><div className="mt-1.5 flex items-center gap-2"><Avatar name={incident.assignee} small /><span className="text-sm font-medium text-slate-200">{incident.assignee}</span></div></div>
          </div>
        </div>
        <div className="flex flex-wrap gap-2 px-5 py-3.5 sm:px-7"><span className="text-xs text-slate-500">Tags</span>{incident.tags.map((tag) => <span key={tag} className="rounded-md border border-slate-700/55 bg-slate-800/35 px-2 py-1 text-[10px] font-medium text-slate-400">#{tag}</span>)}</div>
      </section>

      <div className="mt-6 space-y-6">
        <section className="panel p-5 sm:p-6" aria-labelledby="timeline-heading">
          <div className="flex items-start justify-between gap-3"><div><h2 id="timeline-heading" className="text-base font-semibold text-slate-100">Timeline</h2><p className="mt-1 text-xs text-slate-500">A unified record of detection, response, and automated investigation.</p></div><span className="rounded-lg border border-slate-700/50 bg-slate-800/35 px-2 py-1 text-[10px] font-medium text-slate-400">{incident.timeline.length} events</span></div>
          <ol className="mt-6 space-y-0">
            {incident.timeline.map((event, index) => {
              const Icon = eventIcons[event.kind];
              return <li key={`${event.time}-${event.title}`} className="relative flex gap-4 pb-6 last:pb-0">{index < incident.timeline.length - 1 && <span className="absolute left-[15px] top-8 h-[calc(100%-21px)] w-px bg-slate-700/55" />}<span className={`relative z-10 grid h-8 w-8 shrink-0 place-items-center rounded-lg border ${eventTones[event.kind]}`}><Icon size={15} /></span><div className="min-w-0 pt-0.5"><div className="flex flex-wrap items-center gap-x-3 gap-y-1"><h3 className="text-sm font-medium text-slate-200">{event.title}</h3><time className="text-[11px] text-slate-600">{event.time}</time></div><p className="mt-1 text-sm leading-6 text-slate-500">{event.description}</p></div></li>;
            })}
          </ol>
        </section>

        <section className="panel overflow-hidden" aria-labelledby="logs-heading">
          <div className="flex items-start justify-between border-b border-slate-700/45 px-5 py-4 sm:px-6"><div><h2 id="logs-heading" className="text-base font-semibold text-slate-100">Logs</h2><p className="mt-1 text-xs text-slate-500">Correlated evidence selected by the Log Agent.</p></div><AIIndicator label="Correlated" /></div>
          <div className="overflow-x-auto bg-[#07121e]/70 p-1.5 sm:p-2"><div className="min-w-[670px] overflow-hidden rounded-xl border border-slate-700/45 font-mono text-[11px] leading-6"><div className="grid grid-cols-[110px_72px_130px_1fr] border-b border-slate-700/40 bg-slate-800/35 px-3 py-2 text-[10px] uppercase tracking-[0.12em] text-slate-500"><span>Time</span><span>Level</span><span>Source</span><span>Message</span></div>{incident.logs.map((log) => <div key={`${log.time}-${log.message}`} className="grid grid-cols-[110px_72px_130px_1fr] border-b border-slate-800/70 px-3 py-2 text-slate-400 last:border-0"><span className="text-slate-600">{log.time}</span><span className={log.level === "ERROR" ? "text-rose-300" : log.level === "WARN" ? "text-amber-300" : "text-sky-300"}>{log.level}</span><span className="text-violet-200">{log.source}</span><span className="text-slate-300">{log.message}</span></div>)}</div></div>
        </section>

        {incident.analysis ? (
          <>
            <section className="panel overflow-hidden" aria-labelledby="analysis-heading">
              <div className="flex flex-col gap-3 border-b border-slate-700/45 bg-gradient-to-r from-violet-400/[0.08] to-transparent px-5 py-5 sm:flex-row sm:items-start sm:justify-between sm:px-6"><div><div className="flex items-center gap-2"><Sparkles size={17} className="text-violet-300" /><h2 id="analysis-heading" className="text-base font-semibold text-slate-100">AI Analysis</h2></div><p className="mt-1.5 text-xs text-slate-400">Synthesized from telemetry, logs, deployment history, and similar incidents.</p></div><span className="inline-flex w-fit items-center gap-1.5 rounded-lg border border-emerald-400/20 bg-emerald-400/10 px-2.5 py-1.5 text-xs font-semibold text-emerald-200"><CheckCircle2 size={13} />{incident.analysis.confidence}% confidence</span></div>
              <div className="p-5 sm:p-6"><p className="text-sm leading-7 text-slate-300">{incident.analysis.summary}</p><div className="mt-5 grid gap-3 md:grid-cols-3">{incident.analysis.signals.map((signal, index) => <div key={signal} className="panel-soft p-3.5"><p className="eyebrow">Signal 0{index + 1}</p><p className="mt-2 text-xs leading-5 text-slate-300">{signal}</p></div>)}</div></div>
            </section>

            <section className="panel p-5 sm:p-6" aria-labelledby="root-cause-heading">
              <div className="flex items-center gap-2"><CircleAlert size={17} className="text-amber-300" /><h2 id="root-cause-heading" className="text-base font-semibold text-slate-100">Root Cause</h2></div>
              <div className="mt-4 rounded-xl border border-amber-400/15 bg-amber-400/[0.055] p-4"><p className="text-sm leading-7 text-amber-50/90">{incident.analysis.rootCause}</p></div>
            </section>

            <section className="panel overflow-hidden" aria-labelledby="recommendation-heading">
              <div className="border-b border-slate-700/45 px-5 py-5 sm:px-6"><div className="flex flex-wrap items-center justify-between gap-3"><div className="flex items-center gap-2"><ShieldCheck size={18} className="text-sky-300" /><div><h2 id="recommendation-heading" className="text-base font-semibold text-slate-100">Recommendation</h2><p className="mt-1 text-xs text-slate-500">A reversible plan is ready for human review.</p></div></div><span className={`rounded-md border px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.1em] ${incident.analysis.recommendation.risk === "Low" ? "border-emerald-400/25 bg-emerald-400/10 text-emerald-200" : "border-amber-400/25 bg-amber-400/10 text-amber-200"}`}>{incident.analysis.recommendation.risk} risk</span></div></div>
              <div className="p-5 sm:p-6"><p className="text-base font-medium leading-7 text-slate-100">{incident.analysis.recommendation.action}</p><p className="mt-3 text-sm leading-6 text-slate-400">{incident.analysis.recommendation.rationale}</p><div className="mt-5 flex items-center gap-2 text-xs text-slate-500"><Clock3 size={14} className="text-sky-300" />Estimated recovery <strong className="font-semibold text-slate-200">{incident.analysis.recommendation.estimatedRecovery}</strong></div></div>
            </section>

            <section className="panel p-5 sm:p-6" aria-labelledby="approval-heading">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"><div><div className="flex items-center gap-2"><FileText size={17} className="text-slate-400" /><h2 id="approval-heading" className="text-base font-semibold text-slate-100">Approve or reject</h2></div><p className="mt-1.5 max-w-xl text-xs leading-5 text-slate-500">Approval executes the staged plan through your configured automation. Rejection keeps the incident open and records your decision.</p></div><div className="flex shrink-0 flex-wrap gap-2">{decision ? <span className={`inline-flex items-center gap-2 rounded-xl border px-3.5 py-2.5 text-sm font-medium ${decision === "approved" ? "border-emerald-400/25 bg-emerald-400/10 text-emerald-200" : "border-rose-400/25 bg-rose-400/10 text-rose-200"}`}>{decision === "approved" ? <Check size={16} /> : <X size={16} />}Recommendation {decision}</span> : <><button disabled={saving} onClick={() => void decide("rejected")} className="focus-ring inline-flex items-center gap-2 rounded-xl border border-rose-400/25 bg-rose-400/[0.06] px-3.5 py-2.5 text-sm font-semibold text-rose-200 transition hover:bg-rose-400/15 disabled:cursor-wait"><ThumbsDown size={16} />Reject</button><button disabled={saving} onClick={() => void decide("approved")} className="focus-ring inline-flex items-center gap-2 rounded-xl bg-emerald-400 px-3.5 py-2.5 text-sm font-semibold text-emerald-950 transition hover:bg-emerald-300 disabled:cursor-wait">{saving ? <LoaderCircle size={16} className="animate-spin" /> : <ThumbsUp size={16} />}Approve plan</button></>}</div></div>
              {message && <p className="mt-4 rounded-lg border border-slate-700/55 bg-slate-800/30 px-3 py-2 text-xs text-slate-400">{message}</p>}
            </section>
          </>
        ) : (
          <section className="panel p-5 sm:p-6 flex flex-col items-center justify-center text-slate-400">
            <Sparkles size={24} className="mb-3 text-violet-400/50" />
            <p className="text-sm">No AI analysis available yet. Trigger an analysis to begin.</p>
          </section>
        )}

        <section className="panel p-5 sm:p-6" aria-labelledby="audit-heading">
          <div className="flex items-center gap-2"><FileText size={17} className="text-slate-400" /><div><h2 id="audit-heading" className="text-base font-semibold text-slate-100">Audit History</h2><p className="mt-1 text-xs text-slate-500">An immutable record of humans and agents involved in this response.</p></div></div>
          <div className="mt-5 divide-y divide-slate-700/35 rounded-xl border border-slate-700/45"><div className="grid grid-cols-[68px_minmax(110px,0.8fr)_minmax(130px,1fr)_minmax(0,2fr)] gap-3 bg-slate-800/30 px-3 py-2.5 text-[10px] uppercase tracking-[0.1em] text-slate-500 sm:px-4"><span>Time</span><span>Actor</span><span>Action</span><span>Detail</span></div>{incident.auditHistory.map((event) => <div key={`${event.time}-${event.action}`} className="grid grid-cols-[68px_minmax(110px,0.8fr)_minmax(130px,1fr)_minmax(0,2fr)] gap-3 px-3 py-3 text-xs sm:px-4"><span className="text-slate-600">{event.time}</span><span className="font-medium text-slate-300">{event.actor}</span><span className="text-slate-400">{event.action}</span><span className="text-slate-500">{event.detail}</span></div>)}</div>
        </section>
      </div>
    </div>
  );
}
