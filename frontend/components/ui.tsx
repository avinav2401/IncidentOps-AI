import { ArrowUpRight, Sparkles } from "lucide-react";
import type { ReactNode } from "react";
import type { IncidentStatus, Severity } from "@/lib/types";
import { initials, severityStyles, statusStyles, titleCase } from "@/lib/utils";

export function PageTitle({ eyebrow, title, description, action }: { eyebrow?: string; title: string; description: string; action?: ReactNode }) {
  return (
    <div className="mb-7 flex flex-col gap-4 sm:mb-8 sm:flex-row sm:items-end sm:justify-between">
      <div>
        {eyebrow && <p className="eyebrow mb-2">{eyebrow}</p>}
        <h1 className="text-2xl font-semibold tracking-[-0.03em] text-slate-100 sm:text-[28px]">{title}</h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">{description}</p>
      </div>
      {action}
    </div>
  );
}

export function SeverityBadge({ severity }: { severity: Severity }) {
  return <span className={`inline-flex items-center gap-1.5 rounded-md border px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.08em] ${severityStyles[severity]}`}><span className="h-1.5 w-1.5 rounded-full bg-current" />{severity}</span>;
}

export function StatusBadge({ status }: { status: IncidentStatus }) {
  return <span className={`inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-[11px] font-medium ring-1 ring-inset ${statusStyles[status]}`}><span className="h-1.5 w-1.5 rounded-full bg-current" />{titleCase(status)}</span>;
}

export function Avatar({ name, small = false }: { name: string; small?: boolean }) {
  return <span title={name} className={`grid shrink-0 place-items-center rounded-lg bg-gradient-to-br from-slate-500 to-slate-700 font-semibold text-slate-100 ${small ? "h-6 w-6 text-[8px]" : "h-8 w-8 text-[10px]"}`}>{initials(name)}</span>;
}

export function AIIndicator({ label = "AI-powered" }: { label?: string }) {
  return <span className="inline-flex items-center gap-1.5 rounded-full border border-violet-400/20 bg-violet-400/[0.08] px-2.5 py-1 text-[10px] font-medium text-violet-200"><Sparkles size={11} />{label}</span>;
}

export function MetricLink({ children }: { children: ReactNode }) {
  return <span className="inline-flex items-center gap-1 text-xs text-sky-300 transition group-hover:text-sky-200">{children}<ArrowUpRight size={13} /></span>;
}
