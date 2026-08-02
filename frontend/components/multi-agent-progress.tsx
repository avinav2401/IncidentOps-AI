"use client";

import React, { useEffect, useState } from "react";
import { Check, LoaderCircle, Activity, FileText, Database, GitBranch, BrainCircuit, BookOpen } from "lucide-react";

interface Agent {
  id: string;
  name: string;
  icon: React.ElementType;
  progress: number;
  status: "idle" | "working" | "done" | "error";
  detail: string;
}

export function MultiAgentProgress({ incidentId, incidentStatus, onComplete }: { incidentId: string, incidentStatus: string, onComplete?: () => void }) {
  const [agents, setAgents] = useState<Agent[]>([
    { id: "monitor", name: "Monitor Agent", icon: Activity, progress: 0, status: "idle", detail: "Waiting to start..." },
    { id: "log", name: "Log Analysis Agent", icon: FileText, progress: 0, status: "idle", detail: "Waiting to start..." },
    { id: "metrics", name: "Metrics Agent", icon: Database, progress: 0, status: "idle", detail: "Waiting to start..." },
    { id: "github", name: "GitHub Commit Agent", icon: GitBranch, progress: 0, status: "idle", detail: "Waiting to start..." },
    { id: "knowledge", name: "Knowledge Agent", icon: BookOpen, progress: 0, status: "idle", detail: "Waiting to start..." },
    { id: "rootcause", name: "Root Cause Agent", icon: BrainCircuit, progress: 0, status: "idle", detail: "Waiting to start..." },
    { id: "recommendation", name: "Recommendation Agent", icon: BrainCircuit, progress: 0, status: "idle", detail: "Waiting to start..." },
  ]);

  useEffect(() => {
    if (incidentStatus === "investigating") {
      // Connect to SSE stream
      const token = localStorage.getItem("incidentops_token"); // Simple auth for demo
      const url = new URL(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/incidents/${incidentId}/stream`);
      
      const eventSource = new EventSource(url);

      // We'll simulate gradual progress for "working" agents since SSE only gives us start/end events
      const progressInterval = setInterval(() => {
        setAgents((prev) => prev.map(a => {
          if (a.status === "working" && a.progress < 90) {
            return { ...a, progress: a.progress + Math.random() * 5 };
          }
          return a;
        }));
      }, 500);

      eventSource.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          
          if (payload.type === "agent_start") {
            setAgents((prev) => prev.map(a => 
              a.name === payload.data.agent_name 
                ? { ...a, status: "working", detail: payload.data.description, progress: 10 } 
                : a
            ));
          } else if (payload.type === "agent_end") {
            setAgents((prev) => prev.map(a => 
              a.name === payload.data.agent_name 
                ? { ...a, status: "done", detail: payload.data.summary, progress: 100 } 
                : a
            ));
          } else if (payload.type === "error") {
             setAgents((prev) => prev.map(a => 
              a.name === payload.data.agent_name 
                ? { ...a, status: "error", detail: payload.data.message } 
                : a
            ));
          } else if (payload.type === "result" || payload.type === "approval" || payload.type === "done") {
             if (onComplete) onComplete();
             eventSource.close();
          }
        } catch (e) {
          console.error("Failed to parse SSE", e);
        }
      };

      eventSource.onerror = (e) => {
        console.error("SSE Error", e);
        eventSource.close();
      };

      return () => {
        clearInterval(progressInterval);
        eventSource.close();
      };
    } else if (incidentStatus !== "open") {
      // If already resolved or waiting approval, just show all done
      setAgents((prev) => prev.map(a => ({ ...a, progress: 100, status: "done", detail: "Analysis complete" })));
    }
  }, [incidentStatus, incidentId, onComplete]);

  return (
    <div className="rounded-xl border border-slate-700 bg-slate-800/50 p-5 shadow-lg backdrop-blur-md">
      <h3 className="mb-4 text-sm font-semibold text-slate-200">AI Swarm Investigation</h3>
      <div className="space-y-4">
        {agents.map((agent) => (
          <div key={agent.id} className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <agent.icon size={14} className={agent.status === "done" ? "text-emerald-400" : agent.status === "working" ? "text-sky-400" : agent.status === "error" ? "text-rose-400" : "text-slate-500"} />
                <span className={agent.status === "idle" ? "text-slate-500" : "text-slate-300 font-medium"}>
                  {agent.name}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-slate-400 truncate max-w-[200px] sm:max-w-[400px]">{agent.detail}</span>
                {agent.status === "done" && <Check size={14} className="text-emerald-400" />}
                {agent.status === "working" && <LoaderCircle size={14} className="animate-spin text-sky-400" />}
              </div>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-slate-700/50">
              <div 
                className={`h-full rounded-full transition-all duration-300 ${agent.status === "done" ? "bg-emerald-500" : agent.status === "error" ? "bg-rose-500" : "bg-sky-500"}`}
                style={{ width: `${agent.progress}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
