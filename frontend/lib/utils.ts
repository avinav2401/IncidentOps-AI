import type { IncidentStatus, Severity } from "@/lib/types";

export const severityStyles: Record<Severity, string> = {
  critical: "border-rose-400/25 bg-rose-400/10 text-rose-200",
  high: "border-amber-400/25 bg-amber-400/10 text-amber-200",
  medium: "border-sky-400/25 bg-sky-400/10 text-sky-200",
  low: "border-violet-400/25 bg-violet-400/10 text-violet-200",
};

export const statusStyles: Record<IncidentStatus, string> = {
  investigating: "bg-amber-400/10 text-amber-200 ring-amber-400/20",
  mitigating: "bg-sky-400/10 text-sky-200 ring-sky-400/20",
  monitoring: "bg-violet-400/10 text-violet-200 ring-violet-400/20",
  resolved: "bg-emerald-400/10 text-emerald-200 ring-emerald-400/20",
};

export function titleCase(value: string) {
  return value.replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function initials(name: string) {
  return name.split(" ").map((part) => part[0]).join("").slice(0, 2).toUpperCase();
}
