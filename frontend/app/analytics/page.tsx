import { BarChart3, CheckCircle2, Clock3, Download, TrendingDown, TrendingUp } from "lucide-react";
import { mttrSeries, resolutionRate, severityBreakdown, weeklyIncidents, weeklyLabels } from "@/lib/mock-data";
import { PageTitle } from "@/components/ui";

function linePath(values: number[], width: number, height: number, padding = 8) {
  const max = Math.max(...values);
  const min = Math.min(...values);
  const range = Math.max(max - min, 1);
  return values.map((value, index) => {
    const x = padding + (index * (width - padding * 2)) / (values.length - 1);
    const y = height - padding - ((value - min) / range) * (height - padding * 2);
    return `${index === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
}

export default function AnalyticsPage() {
  const weeklyPeak = Math.max(...weeklyIncidents);
  const donutStops = severityBreakdown.reduce<{ value: number; stops: string[] }>((acc, item) => {
    const start = acc.value;
    const end = start + item.value;
    acc.stops.push(`${item.color} ${start}% ${end}%`);
    return { value: end, stops: acc.stops };
  }, { value: 0, stops: [] }).stops.join(", ");
  const mttrPath = linePath(mttrSeries, 600, 180);

  return (
    <div className="animate-enter">
      <PageTitle
        eyebrow="Performance intelligence"
        title="Analytics"
        description="Measure the health of your incident response program and the impact of AI-assisted operations."
        action={<button className="focus-ring inline-flex items-center justify-center gap-2 rounded-xl border border-slate-700/60 bg-slate-900/45 px-4 py-2.5 text-sm font-semibold text-slate-300 transition hover:border-slate-600 hover:text-white"><Download size={16} />Export report</button>}
      />

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {[{ label: "Incidents this month", value: "86", detail: "−14% vs. prior month", icon: BarChart3, tone: "sky" }, { label: "Mean time to resolve", value: "24m", detail: "−6m improvement", icon: Clock3, tone: "violet" }, { label: "Resolution rate", value: "94.8%", detail: "+2.3 points", icon: CheckCircle2, tone: "emerald" }, { label: "Automation assist", value: "76%", detail: "+8 points", icon: TrendingUp, tone: "amber" }].map((metric) => {
          const Icon = metric.icon;
          const colors = metric.tone === "emerald" ? "bg-emerald-400/10 text-emerald-300" : metric.tone === "violet" ? "bg-violet-400/10 text-violet-300" : metric.tone === "amber" ? "bg-amber-400/10 text-amber-300" : "bg-sky-400/10 text-sky-300";
          return <article key={metric.label} className="panel p-5"><div className="flex items-start justify-between"><div><p className="text-sm text-slate-400">{metric.label}</p><p className="mt-3 text-3xl font-semibold tracking-[-0.04em] text-slate-100">{metric.value}</p></div><span className={`grid h-9 w-9 place-items-center rounded-xl ${colors}`}><Icon size={18} /></span></div><p className="mt-4 inline-flex items-center gap-1 text-xs text-emerald-300"><TrendingDown size={13} />{metric.detail}</p></article>;
        })}
      </section>

      <section className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1.3fr)_minmax(320px,0.7fr)]">
        <div className="panel p-5 sm:p-6"><div className="flex flex-wrap items-start justify-between gap-3"><div><h2 className="text-base font-semibold text-slate-100">Weekly incidents</h2><p className="mt-1 text-xs text-slate-500">New incidents opened across all services.</p></div><span className="rounded-lg border border-slate-700/55 bg-slate-800/35 px-2.5 py-1.5 text-xs text-slate-400">Jul 18–24</span></div><div className="mt-9 flex h-52 items-end gap-3 sm:gap-6">{weeklyIncidents.map((value, index) => <div key={weeklyLabels[index]} className="group flex h-full flex-1 flex-col justify-end gap-2"><div className="relative flex flex-1 items-end"><span className="absolute -top-6 left-1/2 hidden -translate-x-1/2 rounded bg-slate-700 px-1.5 py-0.5 text-[10px] text-slate-200 group-hover:block">{value}</span><div className="w-full rounded-t-lg bg-gradient-to-t from-sky-600 to-cyan-300 transition duration-300 group-hover:from-sky-400 group-hover:to-cyan-100" style={{ height: `${(value / weeklyPeak) * 100}%` }} /></div><span className="text-center text-[10px] text-slate-500">{weeklyLabels[index]}</span></div>)}</div></div>
        <aside className="panel p-5 sm:p-6"><div><h2 className="text-base font-semibold text-slate-100">Severity mix</h2><p className="mt-1 text-xs text-slate-500">Distribution of resolved incidents this month.</p></div><div className="mt-7 flex flex-col items-center gap-7 sm:flex-row xl:flex-col 2xl:flex-row"><div className="relative grid h-36 w-36 shrink-0 place-items-center rounded-full" style={{ background: `conic-gradient(${donutStops})` }}><div className="grid h-24 w-24 place-items-center rounded-full bg-[#0c1928]"><div className="text-center"><p className="text-2xl font-semibold tracking-tight text-slate-100">86</p><p className="text-[10px] uppercase tracking-wider text-slate-500">Total</p></div></div></div><div className="w-full space-y-3">{severityBreakdown.map((entry) => <div key={entry.name} className="flex items-center justify-between text-xs"><span className="flex items-center gap-2 text-slate-400"><span className="h-2 w-2 rounded-full" style={{ backgroundColor: entry.color }} />{entry.name}</span><span className="font-medium text-slate-200">{entry.value}%</span></div>)}</div></div></aside>
      </section>

      <section className="mt-6 grid gap-6 lg:grid-cols-2">
        <div className="panel overflow-hidden"><div className="flex items-start justify-between border-b border-slate-700/45 px-5 py-5 sm:px-6"><div><h2 className="text-base font-semibold text-slate-100">MTTR trend</h2><p className="mt-1 text-xs text-slate-500">Mean time to resolution, in minutes.</p></div><span className="text-sm font-semibold text-emerald-300">24m</span></div><div className="relative h-52 px-5 pb-5 pt-6 sm:px-6"><div className="absolute inset-x-5 top-[36%] border-t border-dashed border-slate-700/40 sm:inset-x-6" /><div className="absolute inset-x-5 top-[65%] border-t border-dashed border-slate-700/40 sm:inset-x-6" /><svg viewBox="0 0 600 180" preserveAspectRatio="none" className="relative h-full w-full overflow-visible" role="img" aria-label="Mean time to resolution trend falling from 39 to 24 minutes"><defs><linearGradient id="area" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="#38bdf8" stopOpacity="0.3" /><stop offset="100%" stopColor="#38bdf8" stopOpacity="0" /></linearGradient></defs><path d={`${mttrPath} L592,172 L8,172 Z`} fill="url(#area)" /><path d={mttrPath} fill="none" stroke="#38bdf8" strokeWidth="3" vectorEffect="non-scaling-stroke" strokeLinecap="round" strokeLinejoin="round" />{mttrSeries.map((value, index) => { const x = 8 + (index * 584) / (mttrSeries.length - 1); const min = Math.min(...mttrSeries); const max = Math.max(...mttrSeries); const y = 172 - ((value - min) / (max - min)) * 164; return <circle key={index} cx={x} cy={y} r="4" fill="#07111f" stroke="#7dd3fc" strokeWidth="2" vectorEffect="non-scaling-stroke" />; })}</svg></div><div className="flex justify-between px-5 pb-5 text-[10px] text-slate-600 sm:px-6">{weeklyLabels.map((label) => <span key={label}>{label}</span>)}</div></div>
        <div className="panel p-5 sm:p-6"><div className="flex items-start justify-between"><div><h2 className="text-base font-semibold text-slate-100">Resolution rate</h2><p className="mt-1 text-xs text-slate-500">Incidents resolved within their response objective.</p></div><CheckCircle2 size={18} className="text-emerald-300" /></div><div className="mt-7 flex flex-col items-center gap-6 sm:flex-row"><div className="relative grid h-36 w-36 place-items-center rounded-full" style={{ background: `conic-gradient(#34d399 ${resolutionRate}%, rgba(52,211,153,.12) 0)` }}><div className="grid h-28 w-28 place-items-center rounded-full bg-[#0c1928]"><p className="text-2xl font-semibold tracking-tight text-slate-100">{resolutionRate}%</p></div></div><div className="w-full space-y-3"><div className="flex items-center justify-between rounded-xl border border-slate-700/45 bg-slate-800/25 px-3 py-3"><span className="text-xs text-slate-400">Target</span><span className="text-xs font-semibold text-slate-200">≥ 92%</span></div><div className="flex items-center justify-between rounded-xl border border-emerald-400/15 bg-emerald-400/[0.05] px-3 py-3"><span className="text-xs text-emerald-100">On track</span><span className="text-xs font-semibold text-emerald-200">+2.8 pts</span></div><p className="text-[11px] leading-5 text-slate-600">AI recommendations were involved in 64% of resolutions that met the objective.</p></div></div></div>
      </section>
    </div>
  );
}
