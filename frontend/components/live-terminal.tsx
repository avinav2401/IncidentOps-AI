"use client";

import { useEffect, useState, useRef } from "react";
import { Terminal as TerminalIcon } from "lucide-react";

interface TerminalLog {
  id: string;
  time: string;
  agent: string;
  message: string;
}

export function LiveTerminal({ incidentId }: { incidentId: string }) {
  const [logs, setLogs] = useState<TerminalLog[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let source: EventSource | null = null;
    const token = localStorage.getItem("incidentops_token");

    const connect = () => {
      source = new EventSource(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/stream?incident_id=${incidentId}&token=${token}`
      );

      source.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          
          setLogs(prev => {
            // Prevent duplicates (simple check based on content and time)
            const isDup = prev.some(l => l.message === data.message && l.agent === data.agent && l.time === new Date().toLocaleTimeString());
            if (isDup) return prev;
            
            const newLog = {
              id: Math.random().toString(36).substr(2, 9),
              time: new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute:'2-digit', second:'2-digit' }),
              agent: data.agent || "System",
              message: data.message || JSON.stringify(data)
            };
            
            return [...prev, newLog].slice(-100); // Keep last 100 logs
          });
        } catch (err) {
          console.error("Failed to parse SSE data in LiveTerminal", err);
        }
      };

      source.onerror = () => {
        source?.close();
        setTimeout(connect, 2000);
      };
    };

    connect();

    return () => {
      source?.close();
    };
  }, [incidentId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <section className="panel overflow-hidden mt-6 bg-[#07121e]/90" aria-labelledby="terminal-heading">
      <div className="flex items-center justify-between border-b border-slate-700/45 px-4 py-3">
        <div className="flex items-center gap-2">
          <TerminalIcon size={16} className="text-emerald-400" />
          <h2 id="terminal-heading" className="text-sm font-semibold text-slate-200">Live AI Terminal</h2>
        </div>
        <div className="flex gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-slate-600"></div>
          <div className="w-2.5 h-2.5 rounded-full bg-slate-600"></div>
          <div className="w-2.5 h-2.5 rounded-full bg-slate-600"></div>
        </div>
      </div>
      
      <div className="p-4 h-[300px] overflow-y-auto font-mono text-[11px] leading-relaxed">
        {logs.length === 0 ? (
          <div className="text-slate-500 italic">Waiting for AI agent logs...</div>
        ) : (
          <div className="space-y-1.5">
            {logs.map((log) => (
              <div key={log.id} className="flex gap-3 text-slate-300">
                <span className="text-slate-500 shrink-0">[{log.time}]</span>
                <span className="text-emerald-400 shrink-0 w-[100px] truncate">&lt;{log.agent}&gt;</span>
                <span className="break-words text-slate-300">{log.message}</span>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>
        )}
      </div>
    </section>
  );
}
