"use client";

import { Plus, ShieldAlert } from "lucide-react";
import { IncidentList } from "@/components/incident-list";
import { PageTitle } from "@/components/ui";

export default function IncidentsPage() {
  return (
    <div className="animate-enter">
      <PageTitle
        eyebrow="Response queue"
        title="Incidents"
        description="Triage, investigate, and resolve operational issues with human judgment backed by AI agents."
        action={
          <button 
            onClick={() => alert("Declaring new incidents is disabled in this demo workspace.")}
            className="focus-ring inline-flex items-center justify-center gap-2 rounded-xl bg-sky-400 px-4 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-sky-300"
          >
            <Plus size={16} />
            Declare incident
          </button>
        }
      />
      <div className="mb-5 flex items-center gap-2 rounded-xl border border-amber-400/10 bg-amber-400/[0.045] px-3.5 py-3 text-xs text-amber-100/90"><ShieldAlert size={15} className="shrink-0 text-amber-300" /><span><strong className="font-semibold">3 incidents need attention.</strong> The critical payments issue has a reviewed rollback ready for approval.</span></div>
      <IncidentList />
    </div>
  );
}
