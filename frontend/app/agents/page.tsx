import { Activity, ChevronRight, CircleDashed, Clock3, Cpu, Radar, Sparkles } from "lucide-react";
import { activityEvents, agents } from "@/lib/mock-data";
import { AIIndicator, PageTitle } from "@/components/ui";
import { AgentWorkflow } from "@/components/agent-workflow";

const cardIcons = [Radar, Activity, CircleDashed, Sparkles];
const cardTones = {
  cyan: "border-cyan-400/20 bg-cyan-400/[0.08] text-cyan-300",
  emerald: "border-emerald-400/20 bg-emerald-400/[0.08] text-emerald-300",
  amber: "border-amber-400/20 bg-amber-400/[0.08] text-amber-300",
  violet: "border-violet-400/20 bg-violet-400/[0.08] text-violet-300",
};

export default function AgentsPage() {
  return (
    <div className="animate-enter">
      <PageTitle
        eyebrow="Autonomous response team"
        title="AI agents"
        description="Specialist agents observe, investigate, and prepare safe actions—while people retain the final say."
        action={<button className="focus-ring inline-flex items-center justify-center gap-2 rounded-xl border border-violet-400/25 bg-violet-400/[0.08] px-4 py-2.5 text-sm font-semibold text-violet-200 transition hover:bg-violet-400/15"><Sparkles size={16} />Agent policies</button>}
      />

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4" aria-label="AI agent status cards">
        {agents.map((agent, index) => {
          const Icon = cardIcons[index];
          const running = agent.state === "Running" || agent.state === "Thinking";
          return (
            <article key={agent.name} className="panel group relative overflow-hidden p-5 transition hover:-translate-y-0.5 hover:border-slate-600/70">
              <div className={`absolute -right-8 -top-8 h-24 w-24 rounded-full blur-2xl ${agent.color === "cyan" ? "bg-cyan-400/10" : agent.color === "emerald" ? "bg-emerald-400/10" : agent.color === "amber" ? "bg-amber-400/10" : "bg-violet-400/10"}`} />
              <div className="relative flex items-start justify-between"><span className={`grid h-10 w-10 place-items-center rounded-xl border ${cardTones[agent.color]}`}><Icon size={19} /></span><span className={`inline-flex items-center gap-1.5 rounded-full px-2 py-1 text-[10px] font-semibold ${agent.state === "Completed" ? "bg-emerald-400/10 text-emerald-200" : agent.state === "Thinking" ? "bg-amber-400/10 text-amber-200" : "bg-sky-400/10 text-sky-200"}`}><span className={`h-1.5 w-1.5 rounded-full bg-current ${running ? "animate-pulse-soft" : ""}`} />{agent.state}</span></div>
              <h2 className="relative mt-5 text-base font-semibold text-slate-100">{agent.name}</h2><p className="relative mt-2 min-h-12 text-xs leading-5 text-slate-500">{agent.description}</p>
              <div className="relative mt-5 border-t border-slate-700/45 pt-3"><p className="text-xs font-medium text-slate-300">{agent.metric}</p><p className="mt-1 text-[10px] text-slate-600">{agent.updated}</p></div>
            </article>
          );
        })}
      </section>

      <section className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1.35fr)_minmax(330px,0.65fr)]">
        <div className="panel overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-700/45 px-5 py-4 sm:px-6"><div><h2 className="text-base font-semibold text-slate-100">Live activity</h2><p className="mt-1 text-xs text-slate-500">A transparent stream of agent observations and actions.</p></div><AIIndicator label="Auditable" /></div>
          <div className="divide-y divide-slate-700/35">
            {activityEvents.map((event) => <div key={`${event.time}-${event.message}`} className="flex gap-4 px-5 py-4 sm:px-6"><span className={`mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full ${event.tone === "success" ? "bg-emerald-400" : event.tone === "warning" ? "bg-amber-400" : "bg-sky-400"}`} /><div className="min-w-0 flex-1"><div className="flex flex-wrap items-center gap-x-2 gap-y-1"><p className="text-sm font-medium text-slate-200">{event.agent}</p><span className="text-[11px] text-slate-600">{event.time} UTC</span></div><p className="mt-1 text-sm leading-6 text-slate-500">{event.message}</p></div><button className="focus-ring hidden shrink-0 items-center gap-1 self-center rounded-lg px-2 py-1 text-xs font-medium text-sky-300 hover:bg-sky-400/10 sm:flex">Details <ChevronRight size={14} /></button></div>)}
          </div>
        </div>

        <aside className="panel p-5 sm:p-6 flex flex-col">
          <div className="flex items-start justify-between"><div><h2 className="text-base font-semibold text-slate-100">Response loop</h2><p className="mt-1 text-xs text-slate-500">The handoff from signal to human decision.</p></div><Cpu size={18} className="text-violet-300" /></div>
          <div className="mt-7 flex-1 rounded-xl border border-slate-700/45 bg-slate-800/20 overflow-hidden">
            <AgentWorkflow />
          </div>
          <div className="mt-6 rounded-xl border border-sky-400/15 bg-sky-400/[0.055] p-3.5 shrink-0"><div className="flex items-center gap-2 text-xs font-semibold text-sky-200"><Clock3 size={14} />Median agent assist</div><p className="mt-2 text-2xl font-semibold tracking-tight text-slate-100">4m 12s</p><p className="mt-1 text-[11px] text-slate-500">from detection to recommendation</p></div>
        </aside>
      </section>
    </div>
  );
}
