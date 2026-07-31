"use client";

import { useMemo } from "react";
import { ReactFlow, Background, Controls, Node, Edge } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { Server, Database, Globe, CreditCard } from "lucide-react";
import type { Incident } from "@/lib/types";

function CustomNode({ data }: { data: any }) {
  const Icon = data.icon;
  const isDown = data.status === "down";
  
  return (
    <div className={`flex flex-col items-center justify-center rounded-xl border p-3 shadow-lg min-w-[120px] transition-all ${
      isDown 
        ? "border-rose-500/50 bg-rose-500/10 shadow-rose-500/20" 
        : "border-slate-700/60 bg-slate-800/80 shadow-black/40"
    }`}>
      <div className="relative">
        {isDown && <span className="absolute -inset-1 animate-ping rounded-full bg-rose-500/40" />}
        <span className={`relative grid h-10 w-10 place-items-center rounded-lg ${isDown ? "bg-rose-500 text-white" : "bg-slate-700 text-sky-300"}`}>
          <Icon size={20} />
        </span>
      </div>
      <p className={`mt-3 text-xs font-semibold ${isDown ? "text-rose-200" : "text-slate-200"}`}>{data.label}</p>
      <p className={`mt-0.5 text-[9px] uppercase tracking-wider ${isDown ? "text-rose-400 font-bold" : "text-slate-500"}`}>
        {isDown ? "Critical" : "Healthy"}
      </p>
    </div>
  );
}

const nodeTypes = { custom: CustomNode };

export function ServiceGraph({ incidents }: { incidents: Incident[] }) {
  // Check if Payment Service is down
  const paymentDown = incidents.some(i => i.service === "Payment Service" && i.status !== "resolved");

  const nodes: Node[] = useMemo(() => [
    {
      id: "api",
      type: "custom",
      position: { x: 250, y: 0 },
      data: { label: "API Gateway", icon: Globe, status: "healthy" }
    },
    {
      id: "auth",
      type: "custom",
      position: { x: 100, y: 120 },
      data: { label: "Auth Service", icon: Server, status: "healthy" }
    },
    {
      id: "payment",
      type: "custom",
      position: { x: 400, y: 120 },
      data: { label: "Payment Service", icon: CreditCard, status: paymentDown ? "down" : "healthy" }
    },
    {
      id: "db",
      type: "custom",
      position: { x: 400, y: 240 },
      data: { label: "PostgreSQL DB", icon: Database, status: "healthy" }
    }
  ], [paymentDown]);

  const edges: Edge[] = useMemo(() => [
    { id: "e1", source: "api", target: "auth", animated: true, style: { stroke: "#38bdf8", strokeWidth: 2 } },
    { id: "e2", source: "api", target: "payment", animated: !paymentDown, style: { stroke: paymentDown ? "#f43f5e" : "#38bdf8", strokeWidth: 2 } },
    { id: "e3", source: "payment", target: "db", animated: !paymentDown, style: { stroke: paymentDown ? "#f43f5e" : "#38bdf8", strokeWidth: 2 } },
  ], [paymentDown]);

  return (
    <div className="h-full w-full rounded-xl bg-[#0b1420]">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#334155" gap={16} />
        <Controls className="!bg-slate-800 !border-slate-700 !fill-slate-300" />
      </ReactFlow>
    </div>
  );
}
