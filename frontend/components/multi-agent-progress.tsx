"use client";

import React, { useEffect, useState } from "react";
import { Check, LoaderCircle, Activity, FileText, Database, GitBranch, BrainCircuit } from "lucide-react";

interface Agent {
  id: string;
  name: string;
  icon: React.ElementType;
  progress: number;
  status: "idle" | "working" | "done";
  detail: string;
}

export function MultiAgentProgress({ incidentStatus, onComplete }: { incidentStatus: string, onComplete?: () => void }) {
  const [agents, setAgents] = useState<Agent[]>([
    { id: "monitor", name: "Monitor Agent", icon: Activity, progress: 0, status: "idle", detail: "Waiting to start..." },
    { id: "log", name: "Log Agent", icon: FileText, progress: 0, status: "idle", detail: "Waiting to start..." },
    { id: "metrics", name: "Metrics Agent", icon: Database, progress: 0, status: "idle", detail: "Waiting to start..." },
    { id: "github", name: "GitHub Agent", icon: GitBranch, progress: 0, status: "idle", detail: "Waiting to start..." },
    { id: "rootcause", name: "Root Cause Agent", icon: BrainCircuit, progress: 0, status: "idle", detail: "Waiting to start..." },
  ]);

  useEffect(() => {
    if (incidentStatus === "investigating") {
      let currentAgent = 0;
      
      const interval = setInterval(() => {
        setAgents((prev) => {
          const next = [...prev];
          
          if (currentAgent >= next.length) {
            clearInterval(interval);
            if (onComplete) onComplete();
            return prev;
          }
          
          // Update current agent
          const agent = next[currentAgent];
          if (agent.status === "idle") {
            agent.status = "working";
            agent.detail = "Initializing...";
          } else if (agent.status === "working") {
            agent.progress += Math.random() * 20 + 10;
            
            if (agent.progress >= 100) {
              agent.progress = 100;
              agent.status = "done";
              agent.detail = "Analysis complete";
              currentAgent++;
            } else {
              agent.detail = agent.progress < 50 ? "Fetching data..." : "Analyzing patterns...";
            }
          }
          
          return next;
        });
      }, 600);
      
      return () => clearInterval(interval);
    } else if (incidentStatus !== "open") {
      // If already resolved or waiting approval, just show all done
      setAgents((prev) => prev.map(a => ({ ...a, progress: 100, status: "done", detail: "Analysis complete" })));
    }
  }, [incidentStatus, onComplete]);

  return (
    <div className="rounded-xl border border-slate-700 bg-slate-800/50 p-5 shadow-lg backdrop-blur-md">
      <h3 className="mb-4 text-sm font-semibold text-slate-200">AI Swarm Investigation</h3>
      <div className="space-y-4">
        {agents.map((agent) => (
          <div key={agent.id} className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <agent.icon size={14} className={agent.status === "done" ? "text-emerald-400" : agent.status === "working" ? "text-sky-400" : "text-slate-500"} />
                <span className={agent.status === "idle" ? "text-slate-500" : "text-slate-300 font-medium"}>
                  {agent.name}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-slate-400">{agent.detail}</span>
                {agent.status === "done" && <Check size={14} className="text-emerald-400" />}
                {agent.status === "working" && <LoaderCircle size={14} className="animate-spin text-sky-400" />}
              </div>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-slate-700/50">
              <div 
                className={`h-full rounded-full transition-all duration-300 ${agent.status === "done" ? "bg-emerald-500" : "bg-sky-500"}`}
                style={{ width: `${agent.progress}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
