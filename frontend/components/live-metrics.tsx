"use client";

import React, { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { Activity } from "lucide-react";

interface MetricPoint {
  time: string;
  cpu: number;
  memory: number;
  latency: number;
}

export function LiveMetrics({ incidentStatus }: { incidentStatus: string }) {
  const [data, setData] = useState<MetricPoint[]>([]);

  useEffect(() => {
    // Generate initial baseline
    const now = new Date();
    const initialData: MetricPoint[] = Array.from({ length: 20 }).map((_, i) => {
      const t = new Date(now.getTime() - (20 - i) * 2000);
      return {
        time: t.toLocaleTimeString([], { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" }),
        cpu: incidentStatus === "resolved" ? 15 + Math.random() * 10 : 85 + Math.random() * 14,
        memory: incidentStatus === "resolved" ? 40 + Math.random() * 5 : 95 + Math.random() * 4,
        latency: incidentStatus === "resolved" ? 45 + Math.random() * 20 : 800 + Math.random() * 400,
      };
    });
    setData(initialData);

    const interval = setInterval(() => {
      setData((prev) => {
        const next = [...prev.slice(1)]; // keep last 20 points
        const t = new Date();
        
        // If resolved, go back to healthy baseline. If investigating, stay highly erratic.
        const isHealthy = incidentStatus !== "investigating" && incidentStatus !== "open";
        
        next.push({
          time: t.toLocaleTimeString([], { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" }),
          cpu: isHealthy ? 15 + Math.random() * 10 : 85 + Math.random() * 14,
          memory: isHealthy ? 40 + Math.random() * 5 : 95 + Math.random() * 4,
          latency: isHealthy ? 45 + Math.random() * 20 : 800 + Math.random() * 400,
        });
        
        return next;
      });
    }, 2000);

    return () => clearInterval(interval);
  }, [incidentStatus]);

  return (
    <div className="panel overflow-hidden" aria-labelledby="metrics-heading">
      <div className="flex items-start justify-between border-b border-slate-700/45 px-5 py-4 sm:px-6">
        <div>
          <h2 id="metrics-heading" className="text-base font-semibold text-slate-100 flex items-center gap-2">
            <Activity size={16} className="text-sky-400" />
            Live Telemetry
          </h2>
          <p className="mt-1 text-xs text-slate-500">Streaming metrics for the affected service.</p>
        </div>
        <div className="flex gap-4 text-xs font-medium">
          <span className="flex items-center gap-1.5 text-sky-400"><span className="h-2 w-2 rounded-full bg-sky-400"></span>CPU</span>
          <span className="flex items-center gap-1.5 text-violet-400"><span className="h-2 w-2 rounded-full bg-violet-400"></span>Memory</span>
          <span className="flex items-center gap-1.5 text-amber-400"><span className="h-2 w-2 rounded-full bg-amber-400"></span>Latency</span>
        </div>
      </div>
      <div className="p-5 sm:p-6 h-[250px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
            <XAxis dataKey="time" stroke="#64748b" fontSize={10} tickMargin={10} minTickGap={20} />
            <YAxis stroke="#64748b" fontSize={10} />
            <Tooltip 
              contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "8px", fontSize: "12px" }} 
              itemStyle={{ color: "#e2e8f0" }}
            />
            <Line type="monotone" dataKey="cpu" stroke="#38bdf8" strokeWidth={2} dot={false} isAnimationActive={false} />
            <Line type="monotone" dataKey="memory" stroke="#a78bfa" strokeWidth={2} dot={false} isAnimationActive={false} />
            <Line type="monotone" dataKey="latency" stroke="#fbbf24" strokeWidth={2} dot={false} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
