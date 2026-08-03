"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { fetchScenarios, simulateIncident } from "@/lib/api";
import { Play, ShieldAlert, Target, Info, Loader2 } from "lucide-react";

export default function TrainingPage() {
  const router = useRouter();
  const [scenarios, setScenarios] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [startingIndex, setStartingIndex] = useState<number | null>(null);

  useEffect(() => {
    async function loadScenarios() {
      try {
        const data = await fetchScenarios();
        setScenarios(data);
      } catch (error) {
        console.error("Failed to load scenarios", error);
      } finally {
        setLoading(false);
      }
    }
    loadScenarios();
  }, []);

  const handleStart = async (index: number) => {
    setStartingIndex(index);
    try {
      const incident = await simulateIncident(index);
      if (incident) {
        router.push(`/incidents/${incident.id}`);
      }
    } catch (error) {
      console.error("Failed to start scenario", error);
      setStartingIndex(null);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-sky-500" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-100">Training Mode</h1>
          <p className="mt-2 text-slate-400">
            Practice incident response by triggering realistic chaos engineering scenarios.
          </p>
        </div>
        <div className="flex items-center gap-2 rounded-lg border border-indigo-500/20 bg-indigo-500/10 px-4 py-2 text-sm text-indigo-300">
          <Target size={16} />
          <span>Sandbox Environment</span>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        {scenarios.map((scenario, index) => (
          <div
            key={index}
            className="group relative flex flex-col overflow-hidden rounded-xl border border-slate-700/50 bg-slate-900/50 p-6 transition-all hover:border-sky-500/30 hover:bg-slate-800/80 hover:shadow-glow-blue"
          >
            <div className="mb-4 flex items-start justify-between gap-4">
              <h3 className="font-semibold text-slate-200 line-clamp-2">{scenario.title}</h3>
              <span className={`shrink-0 rounded-md px-2 py-0.5 text-xs font-semibold ${
                scenario.severity === "P1" ? "bg-rose-500/20 text-rose-300" :
                scenario.severity === "P2" ? "bg-amber-500/20 text-amber-300" :
                "bg-sky-500/20 text-sky-300"
              }`}>
                {scenario.severity}
              </span>
            </div>
            
            <p className="mb-6 flex-1 text-sm text-slate-400">
              {scenario.description}
            </p>

            <div className="mb-6 flex flex-wrap gap-2">
              {scenario.tags?.slice(0, 3).map((tag: string) => (
                <span key={tag} className="rounded-md bg-slate-800 px-2 py-0.5 text-xs text-slate-300 border border-slate-700">
                  {tag}
                </span>
              ))}
            </div>

            <div className="mt-auto flex items-center justify-between border-t border-slate-800 pt-4">
              <div className="flex items-center gap-1.5 text-xs text-slate-500">
                <ShieldAlert size={14} />
                <span>{scenario.service}</span>
              </div>
              <button
                onClick={() => handleStart(index)}
                disabled={startingIndex !== null}
                className="focus-ring flex items-center gap-2 rounded-lg bg-sky-500 hover:bg-sky-400 px-4 py-2 text-sm font-semibold text-slate-950 transition-colors disabled:opacity-50"
              >
                {startingIndex === index ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    Starting...
                  </>
                ) : (
                  <>
                    <Play size={16} />
                    Start Simulation
                  </>
                )}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
