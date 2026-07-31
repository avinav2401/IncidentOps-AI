"use client";

import { useMemo } from "react";
import { ReactFlow, Background, Controls, Node, Edge, Handle, Position, NodeProps } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { Server, Database, Globe, CreditCard, Lock, Package, ServerCrash, AlertTriangle, CheckCircle2 } from "lucide-react";
import type { Incident } from "@/lib/types";

// Custom Node Component
const CustomNode = ({ data }: NodeProps) => {
  const { label, icon: Icon, status } = data;
  
  let borderColor = 'border-slate-700/60';
  let bgColor = 'bg-slate-800/80';
  let textColor = 'text-slate-300';
  let iconColor = 'text-slate-400';
  let StatusIcon = null;

  if (status === 'critical') {
    borderColor = 'border-rose-500 shadow-[0_0_15px_rgba(244,63,94,0.3)]';
    bgColor = 'bg-rose-950/40';
    textColor = 'text-rose-200';
    iconColor = 'text-rose-400';
    StatusIcon = <ServerCrash size={14} className="text-rose-400 absolute -top-2 -right-2 bg-[#07121e] rounded-full" />;
  } else if (status === 'degraded') {
    borderColor = 'border-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.2)]';
    bgColor = 'bg-amber-950/30';
    textColor = 'text-amber-200';
    iconColor = 'text-amber-400';
    StatusIcon = <AlertTriangle size={14} className="text-amber-400 absolute -top-2 -right-2 bg-[#07121e] rounded-full" />;
  } else if (status === 'healthy') {
    borderColor = 'border-emerald-500/50 shadow-black/40';
    bgColor = 'bg-emerald-950/20';
    textColor = 'text-emerald-200';
    iconColor = 'text-emerald-400';
    StatusIcon = <CheckCircle2 size={14} className="text-emerald-400 absolute -top-2 -right-2 bg-[#07121e] rounded-full" />;
  }

  return (
    <div className={`px-4 py-3 shadow-md rounded-xl border-2 ${borderColor} ${bgColor} min-w-[150px] relative transition-all duration-500`}>
      <Handle type="target" position={Position.Top} className="w-2 h-2 !bg-slate-500" />
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg bg-slate-900/50 ${iconColor}`}>
          <Icon size={16} />
        </div>
        <div className="flex flex-col">
          <div className="font-semibold text-[11px] tracking-wide uppercase text-slate-200">{label}</div>
          <div className={`text-[10px] uppercase font-bold mt-0.5 ${textColor}`}>{status}</div>
        </div>
      </div>
      {StatusIcon}
      <Handle type="source" position={Position.Bottom} className="w-2 h-2 !bg-slate-500" />
    </div>
  );
};

const nodeTypes = { custom: CustomNode };

export function ServiceGraph({ affectedService, status }: { affectedService: string, status: string }) {
  // Determine statuses based on affected service
  const getStatus = (serviceName: string) => {
    if (status === 'resolved') return 'healthy';
    if (affectedService === serviceName) return 'critical';
    
    // Topology impact simulation
    if (affectedService === 'Payment Service' && serviceName === 'API Gateway') return 'degraded';
    if (affectedService === 'Database' && (serviceName === 'Payment Service' || serviceName === 'Inventory Service' || serviceName === 'API Gateway')) return 'degraded';
    if (affectedService === 'Redis Cache' && serviceName === 'Database') return 'degraded';

    return 'healthy';
  };

  const initialNodes = [
    {
      id: 'gateway',
      type: 'custom',
      position: { x: 250, y: 0 },
      data: { label: 'API Gateway', icon: Globe, status: getStatus('API Gateway') },
    },
    {
      id: 'auth',
      type: 'custom',
      position: { x: 50, y: 120 },
      data: { label: 'Auth Service', icon: Lock, status: getStatus('Auth Service') },
    },
    {
      id: 'payment',
      type: 'custom',
      position: { x: 250, y: 120 },
      data: { label: 'Payment Service', icon: CreditCard, status: getStatus('Payment Service') },
    },
    {
      id: 'inventory',
      type: 'custom',
      position: { x: 450, y: 120 },
      data: { label: 'Inventory Service', icon: Package, status: getStatus('Inventory Service') },
    },
    {
      id: 'db',
      type: 'custom',
      position: { x: 350, y: 240 },
      data: { label: 'Database', icon: Database, status: getStatus('Database') },
    },
    {
      id: 'redis',
      type: 'custom',
      position: { x: 350, y: 360 },
      data: { label: 'Redis Cache', icon: Server, status: getStatus('Redis Cache') },
    },
  ];

  const initialEdges: Edge[] = [
    { id: 'e1-2', source: 'gateway', target: 'auth', animated: true, style: { stroke: '#64748b', strokeWidth: 2 } },
    { id: 'e1-3', source: 'gateway', target: 'payment', animated: true, style: { stroke: '#64748b', strokeWidth: 2 } },
    { id: 'e1-4', source: 'gateway', target: 'inventory', animated: true, style: { stroke: '#64748b', strokeWidth: 2 } },
    { id: 'e3-5', source: 'payment', target: 'db', animated: true, style: { stroke: '#64748b', strokeWidth: 2 } },
    { id: 'e4-5', source: 'inventory', target: 'db', animated: true, style: { stroke: '#64748b', strokeWidth: 2 } },
    { id: 'e5-6', source: 'db', target: 'redis', animated: true, style: { stroke: '#64748b', strokeWidth: 2 } },
  ];

  const nodes: Node[] = useMemo(() => {
    return initialNodes;
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [affectedService, status]);

  const edges: Edge[] = useMemo(() => {
    return initialEdges.map((e) => {
      const targetNode = initialNodes.find(n => n.id === e.target);
      const targetStatus = targetNode?.data.status;
      const color = targetStatus === 'critical' ? '#f43f5e' : targetStatus === 'degraded' ? '#f59e0b' : '#10b981';
      return { ...e, style: { stroke: color, strokeWidth: 2 } };
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [affectedService, status]);

  return (
    <div className="h-[400px] w-full rounded-xl border border-slate-700/50 bg-[#07121e]">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        proOptions={{ hideAttribution: true }}
        className="touch-none"
      >
        <Background gap={16} size={1} color="#1e293b" />
        <Controls className="!bg-slate-800 !border-slate-700 !fill-slate-300" />
      </ReactFlow>
    </div>
  );
}
