export type Severity = "critical" | "high" | "medium" | "low";
export type IncidentStatus = "investigating" | "mitigating" | "monitoring" | "executing" | "resolved";
export type AgentState = "Running" | "Completed" | "Thinking" | "Idle";

export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  avatar_initials: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface TimelineEvent {
  time: string;
  title: string;
  description: string;
  kind: "detection" | "update" | "action" | "ai" | "resolution";
}

export interface LogLine {
  time: string;
  level: "ERROR" | "WARN" | "INFO";
  source: string;
  message: string;
}

export interface AuditEvent {
  time: string;
  actor: string;
  action: string;
  detail: string;
}

export interface Incident {
  id: string;
  title: string;
  severity: Severity;
  service: string;
  status: IncidentStatus;
  assignee: string;
  createdAt: string;
  updatedAt: string;
  description: string;
  impact: string;
  affectedUsers: string;
  duration: string;
  tags: string[];
  timeline: TimelineEvent[];
  logs: LogLine[];
  analysis: {
    confidence: number;
    summary: string;
    signals: string[];
    rootCause: string;
    recommendation: {
      action: string;
      rationale: string;
      risk: "Low" | "Medium" | "High";
      estimatedRecovery: string;
    };
    evidenceChain?: { step: string; type: "observation" | "deduction" | "conclusion" }[];
    similarIncidents?: string[];
    modelComparisons?: { model: string; confidence: number; action: string }[];
  } | null;
  auditHistory: AuditEvent[];
}

export interface Agent {
  name: string;
  state: AgentState;
  description: string;
  metric: string;
  updated: string;
  color: "cyan" | "violet" | "amber" | "emerald";
}

export interface ActivityEvent {
  time: string;
  agent: string;
  message: string;
  tone: "info" | "success" | "warning";
}

export interface IncidentKnowledge {
  id: string;
  title: string;
  service: string;
  severity: string;
  root_cause: string;
  resolution: string;
  date: string;
}

export interface Runbook {
  id: string;
  title: string;
  service: string;
  description: string;
  steps: string[];
}

export interface PostmortemReport {
  incident_id: string;
  title: string;
  service: string;
  severity: string;
  duration: string;
  root_cause: string;
  action_taken: string;
  metrics_summary: string[];
  lessons_learned: string[];
}

