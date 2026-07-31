import type { Incident, AuthResponse, User, Severity, IncidentStatus, AuditEvent, IncidentKnowledge, Runbook, PostmortemReport } from "@/lib/types";
import { getIncident as getMockIncident, incidents as mockIncidents } from "@/lib/mock-data";

const apiBase = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

// --- Data Mapping Helpers ---

const SEVERITY_MAP: Record<string, Severity> = {
  p1: "critical", p2: "high", p3: "medium", p4: "low",
  critical: "critical", high: "high", medium: "medium", low: "low",
};

const STATUS_MAP: Record<string, IncidentStatus> = {
  investigating: "investigating",
  mitigating: "mitigating",
  monitoring: "monitoring",
  executing: "executing",
  resolved: "resolved",
  closed: "resolved",
  open: "investigating",
  "waiting approval": "monitoring",
};

function mapSeverity(raw: string | undefined): Severity {
  return SEVERITY_MAP[(raw || "").toLowerCase()] || "medium";
}

function mapStatus(raw: string | undefined): IncidentStatus {
  return STATUS_MAP[(raw || "").toLowerCase()] || "investigating";
}

function formatDate(iso: string | undefined): string {
  if (!iso) return "—";
  try {
    const date = new Date(iso);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMin = Math.floor(diffMs / 60_000);
    if (diffMin < 1) return "Just now";
    if (diffMin < 60) return `${diffMin}m ago`;
    const diffH = Math.floor(diffMin / 60);
    if (diffH < 24) return `${diffH}h ago`;
    const diffD = Math.floor(diffH / 24);
    if (diffD < 7) return `${diffD}d ago`;
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  } catch {
    return iso;
  }
}

function computeDuration(createdAt: string | undefined, resolvedAt: string | null | undefined): string {
  if (!createdAt) return "—";
  const start = new Date(createdAt);
  const end = resolvedAt ? new Date(resolvedAt) : new Date();
  const diffMin = Math.floor((end.getTime() - start.getTime()) / 60_000);
  if (diffMin < 60) return `${diffMin}m`;
  const hours = Math.floor(diffMin / 60);
  const mins = diffMin % 60;
  if (hours < 24) return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
  const days = Math.floor(hours / 24);
  return `${days}d ${hours % 24}h`;
}

// --- Auth Storage ---

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("incidentops_token");
}

export function setToken(token: string) {
  if (typeof window === "undefined") return;
  localStorage.setItem("incidentops_token", token);
}

export function removeToken() {
  if (typeof window === "undefined") return;
  localStorage.removeItem("incidentops_token");
}

// --- Request Core ---

function endpoints(path: string) {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return apiBase ? [`${apiBase}${normalized}`, `${apiBase}/api/v1${normalized}`] : [];
}

async function request<T>(path: string, init?: RequestInit): Promise<T | null> {
  const token = getToken();
  const headers = new Headers(init?.headers);
  if (!headers.has("Content-Type") && !(init?.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const options: RequestInit = {
    ...init,
    headers,
  };

  for (const endpoint of endpoints(path)) {
    try {
      const response = await fetch(endpoint, options);
      if (!response.ok) {
        if (response.status === 401) {
          // Token expired or invalid
          removeToken();
          // Optionally trigger a logout event here or redirect
        }
        continue;
      }
      return (await response.json()) as T;
    } catch {
      // API temporarily unavailable
    }
  }
  return null;
}

import { supabase } from "./supabase";

export async function login(email: string, password: string): Promise<AuthResponse> {
  const url = apiBase ? `${apiBase}/login` : "";
  if (url) {
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (response.ok) {
        const data = await response.json() as AuthResponse;
        if (data.access_token) {
          setToken(data.access_token);
        }
        return data;
      } else if (response.status === 401 || response.status === 400) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || "Invalid email or password");
      }
    } catch (err: any) {
      if (err.message !== "Failed to fetch" && err.message !== "fetch failed") {
        throw err;
      }
      console.warn("Backend login failed (network error), trying Supabase...", err);
    }
  }

  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });
  if (error) {
    throw new Error(error.message);
  }
  
  if (data.session) {
    setToken(data.session.access_token);
  }
  
  return {
    access_token: data.session?.access_token || "",
    token_type: data.session?.token_type || "bearer",
    user: {
      id: data.user.id,
      email: data.user.email || "",
      name: data.user.user_metadata?.name || data.user.email?.split("@")[0] || "",
      role: data.user.user_metadata?.role || "responder",
      avatar_initials: data.user.user_metadata?.avatar_initials || "??",
    }
  };
}

export async function getMe(): Promise<User | null> {
  const token = getToken();
  if (!token) return null;
  const user = await request<User>("/me");
  return user ?? null;
}

// --- Incident Endpoints ---

export async function fetchAuditHistory(): Promise<AuditEvent[]> {
  const res = await fetch(`${apiBase}/audit/history`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  if (!res.ok) throw new Error("Failed to fetch audit history");
  return res.json();
}

export async function fetchKnowledgeIncidents(): Promise<IncidentKnowledge[]> {
  const res = await fetch(`${apiBase}/knowledge/incidents`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  if (!res.ok) throw new Error("Failed to fetch knowledge base incidents");
  return res.json();
}

export async function fetchRunbooks(): Promise<Runbook[]> {
  const res = await fetch(`${apiBase}/knowledge/runbooks`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  if (!res.ok) throw new Error("Failed to fetch runbooks");
  return res.json();
}

export async function fetchPostmortemReport(incidentId: string): Promise<PostmortemReport> {
  const res = await fetch(`${apiBase}/reports/${incidentId}/json`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  if (!res.ok) throw new Error("Failed to fetch report");
  return res.json();
}


export async function fetchIncidents(): Promise<Incident[]> {
  const remote = await request<any>("/incidents");
  if (!remote || (!remote.items && !remote.incidents)) return mockIncidents;
  
  const items = remote.items || remote.incidents || [];
  return items.map((inc: any) => ({
    id: inc.incident_number || inc.id,
    title: inc.title,
    severity: mapSeverity(inc.severity),
    service: inc.service,
    status: mapStatus(inc.status),
    assignee: inc.owner || "Unassigned",
    createdAt: formatDate(inc.created_at),
    updatedAt: formatDate(inc.updated_at),
    description: inc.description,
    impact: inc.affected_users ? `${inc.affected_users} users` : "Unknown",
    affectedUsers: inc.affected_users ? `${inc.affected_users}` : "0",
    duration: computeDuration(inc.created_at, inc.resolved_at),
    tags: inc.tags || [],
    timeline: [],
    logs: [],
    analysis: null,
    auditHistory: []
  })) as Incident[];
}

export async function simulateIncident(): Promise<Incident | null> {
  const remote = await request<any>("/incidents/simulate", {
    method: "POST"
  });
  if (!remote) return null;
  return {
    id: remote.incident_number || remote.id,
    title: remote.title,
    severity: mapSeverity(remote.severity),
    service: remote.service,
    status: mapStatus(remote.status),
    assignee: remote.owner || "Unassigned",
    createdAt: formatDate(remote.created_at),
    updatedAt: formatDate(remote.updated_at),
    description: remote.description,
    impact: remote.affected_users ? `${remote.affected_users} users` : "Unknown",
    affectedUsers: remote.affected_users ? `${remote.affected_users}` : "0",
    duration: computeDuration(remote.created_at, remote.resolved_at),
    tags: remote.tags || [],
    timeline: [],
    logs: [],
    analysis: null,
    auditHistory: []
  } as unknown as Incident;
}

export async function fetchIncident(id: string): Promise<Incident | null> {
  const remote = await request<any>(`/incidents/${id}`);
  if (!remote) return getMockIncident(id) || null;

  // Map backend IncidentDetail to frontend Incident structure
  const inc = remote.incident || remote;
  const recommendations = remote.ai_recommendations || [];
  const rec = recommendations[0] || null;
  const logs = remote.incident_logs || [];
  
  return {
    id: inc.incident_number || inc.id,
    title: inc.title,
    severity: mapSeverity(inc.severity),
    service: inc.service,
    status: mapStatus(inc.status),
    assignee: inc.owner || "Unassigned",
    createdAt: formatDate(inc.created_at),
    updatedAt: formatDate(inc.updated_at),
    description: inc.description,
    impact: inc.affected_users ? `${inc.affected_users} users` : "Unknown",
    affectedUsers: inc.affected_users ? `${inc.affected_users}` : "0",
    duration: computeDuration(inc.created_at, inc.resolved_at),
    tags: inc.tags || [],
    timeline: logs.map((l: any) => ({
      time: formatDate(l.created_at),
      title: l.event_type?.replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase()),
      description: l.message,
      kind: l.actor?.includes("Agent") ? "ai" as const : "update" as const
    })),
    logs: [],
    analysis: rec ? {
      confidence: rec.confidence,
      summary: rec.rationale,
      signals: rec.proposed_actions?.length ? rec.proposed_actions : ["Log correlation", "Commit history"],
      rootCause: rec.title,
      recommendation: {
        action: rec.title,
        rationale: rec.rationale,
        risk: rec.risk as "Low" | "Medium" | "High",
        estimatedRecovery: "5m"
      },
      evidenceChain: rec.evidence_chain || [],
      similarIncidents: rec.similar_incidents || []
    } : null,
    auditHistory: remote.audit_logs?.map((a: any) => ({
      time: formatDate(a.created_at),
      actor: a.actor,
      action: a.action,
      detail: a.message
    })) || []
  };
}

export async function triggerAnalysis(id: string): Promise<boolean> {
  const remote = await request<any>(`/incidents/${id}/analyze`, { method: "POST" });
  return !!remote;
}
export async function submitRecommendationDecision(id: string, decision: "approved" | "rejected", reason?: string): Promise<boolean> {
  // We don't have getMe as a synchronous call, let's just pass actor as optional
  const payload = { 
    decision: decision === "approved" ? "approve" : "reject",
    note: reason || undefined
  };
  
  const remote = await request<unknown>(`/incidents/${id}/approve`, {
    method: "POST", 
    body: JSON.stringify(payload),
  });
  return Boolean(remote) || !apiBase;
}

export async function createIncident(data: { title: string; description: string; service: string; severity?: string; owner?: string }): Promise<Incident | null> {
  const remote = await request<any>("/incidents", {
    method: "POST",
    body: JSON.stringify(data),
  });
  if (!remote) return null;
  return {
    id: remote.incident_number || remote.id,
    title: remote.title,
    severity: mapSeverity(remote.severity),
    service: remote.service,
    status: mapStatus(remote.status),
    assignee: remote.owner || "Unassigned",
    createdAt: formatDate(remote.created_at),
    updatedAt: formatDate(remote.updated_at),
    description: remote.description,
    impact: remote.affected_users ? `${remote.affected_users} users` : "Unknown",
    affectedUsers: remote.affected_users ? `${remote.affected_users}` : "0",
    duration: computeDuration(remote.created_at, remote.resolved_at),
    tags: remote.tags || [],
    timeline: [],
    logs: [],
    analysis: null,
    auditHistory: []
  };
}

export async function fetchAnalytics(): Promise<any> {
  const remote = await request<any>("/analytics");
  return remote || {};
}

export async function addComment(id: string, content: string, actor: string = "Maya Chen"): Promise<boolean> {
  const payload = { content, actor };
  const remote = await request<any>(`/incidents/${id}/comments`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
  return !!remote;
}

export async function fetchIncidentNotifications(id: string): Promise<any> {
  const remote = await request<any>(`/incidents/${id}/notifications`);
  return remote || { slack_messages: [], jira_tickets: [] };
}
