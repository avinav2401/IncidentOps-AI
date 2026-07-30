"use client";

import { useQuery } from "@tanstack/react-query";
import { Shield, ShieldCheck, Eye, Crown, Users } from "lucide-react";
import { PageTitle, Avatar } from "@/components/ui";

const roleIcons: Record<string, any> = {
  incident_commander: Crown,
  admin: ShieldCheck,
  responder: Shield,
  viewer: Eye,
};

const roleLabels: Record<string, string> = {
  incident_commander: "Incident Commander",
  admin: "Admin",
  responder: "SRE Engineer",
  viewer: "Viewer",
};

const roleTones: Record<string, string> = {
  incident_commander: "border-sky-400/25 bg-sky-400/10 text-sky-200",
  admin: "border-violet-400/25 bg-violet-400/10 text-violet-200",
  responder: "border-emerald-400/25 bg-emerald-400/10 text-emerald-200",
  viewer: "border-slate-400/25 bg-slate-400/10 text-slate-300",
};

const demoUsers = [
  {
    id: "usr_maya",
    name: "Maya Chen",
    email: "maya.chen@incidentops.dev",
    role: "incident_commander",
    status: "active",
    lastLogin: "Just now",
  },
  {
    id: "usr_samir",
    name: "Samir Patel",
    email: "samir.patel@incidentops.dev",
    role: "responder",
    status: "active",
    lastLogin: "2h ago",
  },
  {
    id: "usr_lena",
    name: "Lena Ortiz",
    email: "lena.ortiz@incidentops.dev",
    role: "admin",
    status: "active",
    lastLogin: "1d ago",
  },
];

export default function UsersPage() {
  return (
    <div className="animate-enter">
      <PageTitle
        eyebrow="Team management"
        title="Users"
        description="Manage team members and their roles in the incident response workflow."
        action={
          <button
            onClick={() =>
              alert(
                "User invitations are not available in this demo workspace."
              )
            }
            className="focus-ring inline-flex items-center justify-center gap-2 rounded-xl bg-sky-400 px-4 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-sky-300"
          >
            <Users size={16} />
            Invite member
          </button>
        }
      />

      <section className="panel overflow-hidden">
        <div className="border-b border-slate-700/45 px-5 py-4 sm:px-6">
          <h2 className="text-base font-semibold text-slate-100">
            Team members
          </h2>
          <p className="mt-1 text-xs text-slate-500">
            All users with access to this IncidentOps workspace.
          </p>
        </div>
        <div className="divide-y divide-slate-700/35">
          {demoUsers.map((user) => {
            const RoleIcon = roleIcons[user.role] || Shield;
            return (
              <div
                key={user.id}
                className="flex items-center gap-4 px-5 py-4 transition hover:bg-slate-800/25 sm:px-6"
              >
                <Avatar name={user.name} />
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-slate-100">
                    {user.name}
                  </p>
                  <p className="mt-0.5 text-xs text-slate-500">{user.email}</p>
                </div>
                <span
                  className={`hidden items-center gap-1.5 rounded-md border px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.08em] sm:inline-flex ${roleTones[user.role] || roleTones.viewer}`}
                >
                  <RoleIcon size={12} />
                  {roleLabels[user.role] || user.role}
                </span>
                <span
                  className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${user.status === "active" ? "bg-emerald-400/10 text-emerald-200" : "bg-slate-700/50 text-slate-400"}`}
                >
                  {user.status}
                </span>
                <span className="hidden text-[11px] text-slate-500 lg:block">
                  {user.lastLogin}
                </span>
              </div>
            );
          })}
        </div>
      </section>

      <section className="mt-6 panel p-5 sm:p-6">
        <h2 className="text-base font-semibold text-slate-100">Role legend</h2>
        <p className="mt-1 text-xs text-slate-500">
          Each role determines what actions a user can perform.
        </p>
        <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {[
            {
              role: "incident_commander",
              desc: "Full access. Can approve AI recommendations and manage incidents.",
            },
            {
              role: "admin",
              desc: "System configuration, user management, and integration setup.",
            },
            {
              role: "responder",
              desc: "Can view, investigate, and update incidents. Cannot approve AI actions.",
            },
            {
              role: "viewer",
              desc: "Read-only access to dashboards and incident history.",
            },
          ].map((item) => {
            const Icon = roleIcons[item.role] || Shield;
            return (
              <div
                key={item.role}
                className="panel-soft p-3.5"
              >
                <div className="flex items-center gap-2">
                  <Icon size={14} className="text-slate-400" />
                  <p className="text-xs font-semibold text-slate-200">
                    {roleLabels[item.role]}
                  </p>
                </div>
                <p className="mt-2 text-[11px] leading-4 text-slate-500">
                  {item.desc}
                </p>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
