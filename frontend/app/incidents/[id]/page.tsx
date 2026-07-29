"use client";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { IncidentDetail } from "@/components/incident-detail";
import { fetchIncident } from "@/lib/api";

export default function IncidentDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const { data: incident, isLoading, refetch } = useQuery({
    queryKey: ["incident", id],
    queryFn: () => fetchIncident(id),
    enabled: !!id,
    refetchInterval: (query) => {
      const state = query.state?.data?.status;
      return state === "investigating" ? 2000 : false;
    },
  });

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-sky-400"></div>
      </div>
    );
  }

  if (!incident) {
    return (
      <div className="flex h-64 flex-col items-center justify-center text-slate-400">
        <p>Incident not found.</p>
        <Link href="/incidents" className="mt-4 text-sky-400 hover:underline">Return to incidents</Link>
      </div>
    );
  }

  return (
    <div>
      <Link href="/incidents" className="focus-ring mb-5 inline-flex items-center gap-2 rounded-lg px-1 py-1 text-xs font-medium text-slate-400 transition hover:text-sky-200">
        <ArrowLeft size={15} />Back to incidents
      </Link>
      <IncidentDetail incident={incident} onRefetch={() => refetch()} />
    </div>
  );
}
