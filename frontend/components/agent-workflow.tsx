"use client";

import { useCallback } from "react";
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

const initialNodes: Node[] = [
  {
    id: "1",
    type: "input",
    position: { x: 250, y: 5 },
    data: { label: "Trigger: Critical Incident" },
    style: { background: "#0ea5e9", color: "#fff", border: "none", borderRadius: "8px" },
  },
  {
    id: "2",
    position: { x: 100, y: 100 },
    data: { label: "Log Analysis Agent" },
    style: { background: "#1e293b", color: "#38bdf8", border: "1px solid #334155", borderRadius: "8px" },
  },
  {
    id: "3",
    position: { x: 400, y: 100 },
    data: { label: "GitHub Agent" },
    style: { background: "#1e293b", color: "#38bdf8", border: "1px solid #334155", borderRadius: "8px" },
  },
  {
    id: "4",
    position: { x: 250, y: 200 },
    data: { label: "Root Cause Agent" },
    style: { background: "#1e293b", color: "#10b981", border: "1px solid #334155", borderRadius: "8px" },
  },
  {
    id: "5",
    type: "output",
    position: { x: 250, y: 300 },
    data: { label: "Recommendation Agent" },
    style: { background: "#1e293b", color: "#f59e0b", border: "1px solid #334155", borderRadius: "8px" },
  },
];

const initialEdges: Edge[] = [
  { id: "e1-2", source: "1", target: "2", animated: true, style: { stroke: "#94a3b8" } },
  { id: "e1-3", source: "1", target: "3", animated: true, style: { stroke: "#94a3b8" } },
  { id: "e2-4", source: "2", target: "4", animated: true, style: { stroke: "#94a3b8" } },
  { id: "e3-4", source: "3", target: "4", animated: true, style: { stroke: "#94a3b8" } },
  { id: "e4-5", source: "4", target: "5", animated: true, style: { stroke: "#94a3b8" } },
];

export function AgentWorkflow() {
  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: Connection | Edge) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  return (
    <div style={{ width: "100%", height: "100%", minHeight: "400px" }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      >
        <Controls style={{ background: "#0f172a", fill: "#94a3b8" }} />
        <MiniMap nodeStrokeColor="#38bdf8" nodeColor="#1e293b" maskColor="rgba(15, 23, 42, 0.8)" />
        <Background color="#334155" gap={16} />
      </ReactFlow>
    </div>
  );
}
