"use client";

import { PageTitle } from "@/components/ui";
import { CheckCircle2, XCircle, ArrowRight, Slack, Github, Database, Webhook, MonitorDot } from "lucide-react";

export default function IntegrationsPage() {
  const integrations = [
    {
      id: "slack",
      name: "Slack",
      description: "Send incident alerts and receive AI summaries in Slack channels.",
      icon: Slack,
      status: "connected",
      color: "text-purple-400",
      bg: "bg-purple-400/10",
    },
    {
      id: "datadog",
      name: "Datadog",
      description: "Ingest monitoring alerts directly into IncidentOps AI.",
      icon: MonitorDot,
      status: "connected",
      color: "text-purple-600",
      bg: "bg-purple-600/10",
    },
    {
      id: "jira",
      name: "Jira",
      description: "Automatically create and sync Jira tickets for incidents.",
      icon: Webhook, // Webhook as placeholder for Jira
      status: "connected",
      color: "text-blue-500",
      bg: "bg-blue-500/10",
    },
    {
      id: "github",
      name: "GitHub",
      description: "Link commits and PRs to root cause analysis.",
      icon: Github,
      status: "disconnected",
      color: "text-slate-200",
      bg: "bg-slate-200/10",
    },
    {
      id: "pagerduty",
      name: "PagerDuty",
      description: "Sync on-call schedules and incident states.",
      icon: Database, // Database as placeholder for PD
      status: "disconnected",
      color: "text-emerald-500",
      bg: "bg-emerald-500/10",
    }
  ];

  return (
    <div className="animate-enter">
      <PageTitle 
        eyebrow="Management"
        title="Integrations" 
        description="Connect IncidentOps AI to your existing tools for automated intelligence gathering and remediation."
      />

      <div className="mt-8 grid gap-6 xl:grid-cols-2">
        {integrations.map(integration => {
          const Icon = integration.icon;
          return (
            <div key={integration.id} className="panel flex items-start gap-5 p-6">
              <span className={`grid h-12 w-12 shrink-0 place-items-center rounded-xl ${integration.bg} ${integration.color}`}>
                <Icon size={24} />
              </span>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-semibold text-slate-100">{integration.name}</h3>
                  {integration.status === "connected" ? (
                    <span className="flex items-center gap-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2.5 py-1 text-[10px] font-medium uppercase tracking-wider text-emerald-400">
                      <CheckCircle2 size={12} /> Connected
                    </span>
                  ) : (
                    <span className="flex items-center gap-1.5 rounded-full border border-slate-500/20 bg-slate-500/10 px-2.5 py-1 text-[10px] font-medium uppercase tracking-wider text-slate-400">
                      <XCircle size={12} /> Disconnected
                    </span>
                  )}
                </div>
                <p className="mt-2 text-sm leading-relaxed text-slate-400">
                  {integration.description}
                </p>
                
                <div className="mt-5 border-t border-slate-700/60 pt-4">
                  <button className="flex items-center gap-2 text-xs font-medium text-sky-400 transition hover:text-sky-300">
                    {integration.status === "connected" ? "Configure Settings" : "Connect Integration"} <ArrowRight size={14} />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
