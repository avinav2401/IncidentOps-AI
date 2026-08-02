"use client";

import { useMemo } from "react";
import { ReactFlow, Background, Controls, Node, Edge, Handle, Position, NodeProps } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { Server, Database, Globe, Monitor, Zap, Bot, ShieldCheck, Box, MessageSquare, Terminal } from "lucide-react";
import { PageTitle } from "@/components/ui";

const CustomNode = ({ data }: NodeProps) => {
  const label = data.label as string;
  const description = data.description as string;
  const Icon = data.icon as React.ElementType;
  const color = data.color as string;
  
  let themeStyles = "";
  switch(color) {
    case "blue": themeStyles = "border-sky-500/50 bg-sky-950/30 text-sky-200"; break;
    case "green": themeStyles = "border-emerald-500/50 bg-emerald-950/30 text-emerald-200"; break;
    case "purple": themeStyles = "border-violet-500/50 bg-violet-950/30 text-violet-200"; break;
    case "orange": themeStyles = "border-orange-500/50 bg-orange-950/30 text-orange-200"; break;
    default: themeStyles = "border-slate-500/50 bg-slate-900/50 text-slate-200"; break;
  }

  return (
    <div className={`px-4 py-3 shadow-xl rounded-xl border-2 ${themeStyles} min-w-[200px] backdrop-blur-sm`}>
      <Handle type="target" position={Position.Top} className="!w-2 !h-2 !bg-slate-400 !border-0" />
      <div className="flex items-center gap-3 mb-2">
        <div className="p-2 rounded-lg bg-black/20">
          <Icon size={16} />
        </div>
        <div className="font-semibold text-[13px] tracking-wide">{label}</div>
      </div>
      <div className="text-[10px] text-slate-300 leading-relaxed font-medium">
        {description}
      </div>
      <Handle type="source" position={Position.Bottom} className="!w-2 !h-2 !bg-slate-400 !border-0" />
    </div>
  );
};

const nodeTypes = { custom: CustomNode };

export default function ArchitecturePage() {
  const nodes: Node[] = useMemo(() => [
    {
      id: 'user',
      type: 'custom',
      position: { x: 350, y: 0 },
      data: { label: 'SRE / Engineer', description: 'Interacts with the dashboard to review AI reasoning and approve fixes.', icon: Monitor, color: 'default' },
    },
    {
      id: 'frontend',
      type: 'custom',
      position: { x: 350, y: 150 },
      data: { label: 'Next.js Frontend', description: 'React UI deployed on Vercel. Connects to backend via REST & SSE.', icon: Box, color: 'blue' },
    },
    {
      id: 'backend',
      type: 'custom',
      position: { x: 350, y: 300 },
      data: { label: 'FastAPI Backend', description: 'Python API handling orchestration, Auth, and database access.', icon: Zap, color: 'green' },
    },
    {
      id: 'supervisor',
      type: 'custom',
      position: { x: 350, y: 450 },
      data: { label: 'AI Supervisor', description: 'Orchestrates specialist agents (Monitor, Logs, Metrics) via asyncio.', icon: Bot, color: 'purple' },
    },
    {
      id: 'agents',
      type: 'custom',
      position: { x: 650, y: 450 },
      data: { label: 'Specialist Agents', description: 'Gather evidence in parallel (Logs, Deployments, Past Incidents).', icon: ShieldCheck, color: 'purple' },
    },
    {
      id: 'db',
      type: 'custom',
      position: { x: 100, y: 450 },
      data: { label: 'SQLite / PostgreSQL', description: 'Stores Incidents, Audit Logs, and AI Knowledge Base.', icon: Database, color: 'blue' },
    },
    {
      id: 'integrations',
      type: 'custom',
      position: { x: 350, y: 600 },
      data: { label: 'Slack & Jira', description: 'Communicator agent opens tickets and sends channel updates.', icon: MessageSquare, color: 'orange' },
    },
    {
      id: 'simulator',
      type: 'custom',
      position: { x: 650, y: 600 },
      data: { label: 'Incident Simulator', description: 'Mock execution environment demonstrating automated recovery.', icon: Terminal, color: 'orange' },
    }
  ], []);

  const edges: Edge[] = useMemo(() => [
    { id: 'e-user-frontend', source: 'user', target: 'frontend', animated: true, style: { stroke: '#94a3b8' } },
    { id: 'e-frontend-backend', source: 'frontend', target: 'backend', animated: true, style: { stroke: '#38bdf8', strokeWidth: 2 } },
    { id: 'e-backend-db', source: 'backend', target: 'db', animated: true, style: { stroke: '#94a3b8' }, sourceHandle: 'left', targetHandle: 'right' },
    { id: 'e-backend-supervisor', source: 'backend', target: 'supervisor', animated: true, style: { stroke: '#10b981', strokeWidth: 2 } },
    { id: 'e-supervisor-agents', source: 'supervisor', target: 'agents', animated: true, style: { stroke: '#8b5cf6', strokeWidth: 2 }, sourceHandle: 'right', targetHandle: 'left' },
    { id: 'e-supervisor-integrations', source: 'supervisor', target: 'integrations', animated: true, style: { stroke: '#f59e0b', strokeWidth: 2 } },
    { id: 'e-supervisor-simulator', source: 'supervisor', target: 'simulator', animated: true, style: { stroke: '#f59e0b', strokeWidth: 2 } },
  ], []);

  return (
    <div className="animate-enter flex flex-col h-[calc(100vh-2rem)]">
      <PageTitle
        eyebrow="System Design"
        title="Architecture"
        description="The full-stack topology powering IncidentOps AI."
      />
      
      <div className="flex-1 mt-6 rounded-xl border border-slate-700/50 bg-[#07121e] overflow-hidden relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          proOptions={{ hideAttribution: true }}
          className="touch-none"
        >
          <Background gap={24} size={1} color="#1e293b" />
          <Controls className="!bg-slate-800 !border-slate-700 !fill-slate-300" />
        </ReactFlow>
        
        {/* Legend */}
        <div className="absolute bottom-6 left-6 p-4 rounded-xl border border-slate-700/60 bg-slate-900/80 backdrop-blur-sm">
          <h3 className="text-xs font-semibold text-slate-200 mb-3 uppercase tracking-wider">Legend</h3>
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span className="w-3 h-3 rounded bg-sky-500/50 border border-sky-400"></span>
              Web / Persistence
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span className="w-3 h-3 rounded bg-emerald-500/50 border border-emerald-400"></span>
              Core API
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span className="w-3 h-3 rounded bg-violet-500/50 border border-violet-400"></span>
              AI Orchestration
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span className="w-3 h-3 rounded bg-orange-500/50 border border-orange-400"></span>
              External Integrations
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
