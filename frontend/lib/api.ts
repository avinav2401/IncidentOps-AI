import type { Incident, AuthResponse, User } from "@/lib/types";
import { getIncident as getMockIncident, incidents as mockIncidents } from "@/lib/mock-data";

const apiBase = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

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

async function request<T>(path: string, init?: RequestInit): Promise<T | undefined> {
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
  return undefined;
}

import { supabase } from "./supabase";

export async function login(email: string, password: string): Promise<AuthResponse> {
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

export async function fetchIncidents(): Promise<Incident[]> {
  const remote = await request<any>("/incidents");
  if (!remote || (!remote.items && !remote.incidents)) return mockIncidents;
  
  const items = remote.items || remote.incidents || [];
  return items.map((inc: any) => ({
    id: inc.incident_number || inc.id,
    title: inc.title,
    severity: inc.severity?.toLowerCase() || "medium",
    service: inc.service,
    status: inc.status?.toLowerCase() || "open",
    assignee: inc.owner || "Unassigned",
    createdAt: inc.created_at,
    updatedAt: inc.updated_at,
    description: inc.description,
    impact: inc.affected_users ? `${inc.affected_users} users` : "Unknown",
    affectedUsers: inc.affected_users ? `${inc.affected_users}` : "0",
    duration: "Ongoing",
    tags: inc.tags || [],
    timeline: [],
    logs: [],
    analysis: null,
    auditHistory: []
  })) as Incident[];
}

export async function fetchIncident(id: string): Promise<Incident | undefined> {
  const remote = await request<any>(`/incidents/${id}`);
  if (!remote) return getMockIncident(id);

  // Map backend IncidentDetail to frontend Incident structure
  const inc = remote.incident || remote;
  const recommendations = remote.ai_recommendations || [];
  const rec = recommendations[0] || null;
  const logs = remote.incident_logs || [];
  
  return {
    id: inc.incident_number || inc.id,
    title: inc.title,
    severity: inc.severity?.toLowerCase() || "medium",
    service: inc.service,
    status: inc.status?.toLowerCase() || "open",
    assignee: inc.owner || "Unassigned",
    createdAt: inc.created_at,
    updatedAt: inc.updated_at,
    description: inc.description,
    impact: inc.affected_users ? `${inc.affected_users} users` : "Unknown",
    affectedUsers: inc.affected_users ? `${inc.affected_users}` : "0",
    duration: "Ongoing",
    tags: inc.tags || [],
    timeline: logs.map((l: any) => ({
      time: l.created_at,
      title: l.event_type,
      description: l.message,
      kind: l.actor?.includes("Agent") ? "ai" : "update"
    })),
    logs: [],
    analysis: rec ? {
      confidence: rec.confidence,
      summary: rec.rationale,
      signals: ["Log correlation", "Commit history"],
      rootCause: rec.title,
      recommendation: {
        action: rec.title,
        rationale: rec.rationale,
        risk: rec.risk,
        estimatedRecovery: "5m"
      }
    } : null,
    auditHistory: remote.audit_logs?.map((a: any) => ({
      time: a.created_at,
      actor: a.actor,
      action: a.action,
      detail: a.message
    })) || []
  } as unknown as Incident;
}

export async function triggerAnalysis(id: string): Promise<boolean> {
  const remote = await request<any>(`/incidents/${id}/analyze`, { method: "POST" });
  return !!remote;
}
export async function submitRecommendationDecision(id: string, decision: "approved" | "rejected", reason?: string): Promise<boolean> {
  const user = getMe() || { name: "Demo User" }; // Fallback to avoid breaking
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

export async function fetchAnalytics(): Promise<any> {
  const remote = await request<any>("/analytics");
  return remote;
}
