"use client";

import { useEffect, useState, useCallback } from "react";
import { ReactFlow, Background, Controls, Node, Edge, Handle, Position, NodeProps, useNodesState, useEdgesState } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { Server, Database, Globe, Monitor, Zap, Bot, ShieldCheck, Box, MessageSquare, Terminal } from "lucide-react";
import { PageTitle } from "@/components/ui";
import dagre from "dagre";

const getIconForService = (name: string) => {
  const lower = name.toLowerCase();
  if (lower.includes("frontend") || lower.includes("web")) return Globe;
  if (lower.includes("db") || lower.includes("database")) return Database;
  if (lower.includes("redis") || lower.includes("cache")) return Zap;
  if (lower.includes("gateway") || lower.includes("api")) return Box;
  if (lower.includes("elastic") || lower.includes("search")) return Server;
  if (lower.includes("auth")) return ShieldCheck;
  if (lower.includes("payment")) return Terminal;
  return Server;
};

const CustomNode = ({ data }: NodeProps) => {
  const label = data.label as string;
  const status = data.status as string;
  const env = data.environment as string;
  const level = data.critical_level as string;
  const Icon = getIconForService(label);
  
  let themeStyles = "";
  if (status !== "healthy") {
    themeStyles = "border-rose-500/80 bg-rose-950/40 text-rose-200 animate-pulse";
  } else {
    themeStyles = "border-slate-600/50 bg-slate-900/50 text-slate-200";
  }

  return (
    <div className={`px-4 py-3 shadow-xl rounded-xl border-2 ${themeStyles} min-w-[200px] backdrop-blur-sm transition-all duration-300`}>
      <Handle type="target" position={Position.Top} className="!w-2 !h-2 !bg-slate-400 !border-0" />
      <div className="flex items-center gap-3 mb-2">
        <div className="p-2 rounded-lg bg-black/20">
          <Icon size={16} />
        </div>
        <div className="font-semibold text-[13px] tracking-wide">{label}</div>
      </div>
      <div className="flex gap-2 text-[10px] text-slate-400 font-medium">
        <span className="px-1.5 py-0.5 rounded-md bg-slate-800 border border-slate-700">{env}</span>
        <span className="px-1.5 py-0.5 rounded-md bg-slate-800 border border-slate-700">{level}</span>
        <span className={`px-1.5 py-0.5 rounded-md border ${status === 'healthy' ? 'bg-emerald-900/50 border-emerald-800 text-emerald-400' : 'bg-rose-900/50 border-rose-800 text-rose-400'}`}>
          {status}
        </span>
      </div>
      <Handle type="source" position={Position.Bottom} className="!w-2 !h-2 !bg-slate-400 !border-0" />
    </div>
  );
};

const nodeTypes = { custom: CustomNode };

const getLayoutedElements = (nodes: Node[], edges: Edge[], direction = 'TB') => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  
  const nodeWidth = 220;
  const nodeHeight = 80;
  
  dagreGraph.setGraph({ rankdir: direction });
  
  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  nodes.forEach((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    node.position = {
      x: nodeWithPosition.x - nodeWidth / 2,
      y: nodeWithPosition.y - nodeHeight / 2,
    };
  });

  return { nodes, edges };
};

export default function ArchitecturePage() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchGraph = async () => {
      try {
        const token = localStorage.getItem("incidentops_token");
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/services/graph`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const data = await res.json();
        
        // Add type and set generic nodes
        const rawNodes = data.nodes.map((n: any) => ({
          ...n,
          type: 'custom',
          position: { x: 0, y: 0 }
        }));
        
        const rawEdges = data.edges.map((e: any) => ({
          ...e,
          style: { stroke: e.animated ? '#f43f5e' : '#94a3b8', strokeWidth: e.animated ? 2 : 1 }
        }));

        const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(rawNodes, rawEdges);
        
        setNodes(layoutedNodes);
        setEdges(layoutedEdges);
      } catch (err) {
        console.error("Failed to load graph", err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchGraph();
  }, [setNodes, setEdges]);

  return (
    <div className="animate-enter flex flex-col h-[calc(100vh-2rem)]">
      <PageTitle
        eyebrow="System Design"
        title="Architecture"
        description="Live dynamic dependency graph of your workspace services."
      />
      
      <div className="flex-1 mt-6 rounded-xl border border-slate-700/50 bg-[#07121e] overflow-hidden relative">
        {loading ? (
          <div className="w-full h-full flex items-center justify-center text-slate-400">Loading dynamic graph...</div>
        ) : (
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            nodeTypes={nodeTypes}
            fitView
            fitViewOptions={{ padding: 0.2 }}
            proOptions={{ hideAttribution: true }}
            className="touch-none"
          >
            <Background gap={24} size={1} color="#1e293b" />
            <Controls className="!bg-slate-800 !border-slate-700 !fill-slate-300" />
          </ReactFlow>
        )}
        
        {/* Legend */}
        <div className="absolute bottom-6 left-6 p-4 rounded-xl border border-slate-700/60 bg-slate-900/80 backdrop-blur-sm">
          <h3 className="text-xs font-semibold text-slate-200 mb-3 uppercase tracking-wider">Status Legend</h3>
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span className="w-3 h-3 rounded bg-slate-800 border border-slate-600"></span>
              Healthy Service
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span className="w-3 h-3 rounded bg-rose-500/50 border border-rose-400 animate-pulse"></span>
              Degraded / Incident
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
