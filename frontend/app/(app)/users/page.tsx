"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Shield, ShieldCheck, Eye, Crown, Users, X } from "lucide-react";
import { PageTitle, Avatar } from "@/components/ui";
import { request } from "@/lib/api";

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

export default function UsersPage() {
  const queryClient = useQueryClient();
  const [isInviteOpen, setIsInviteOpen] = useState(false);
  const [inviteForm, setInviteForm] = useState({ name: "", email: "", role: "responder" });

  const { data: users = [], isLoading } = useQuery({
    queryKey: ["users"],
    queryFn: () => request<any[]>("/users"),
  });

  const inviteMutation = useMutation({
    mutationFn: (newMember: typeof inviteForm) =>
      request("/users/invite", {
        method: "POST",
        body: JSON.stringify(newMember),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      setIsInviteOpen(false);
      setInviteForm({ name: "", email: "", role: "responder" });
    },
    onError: (err: any) => {
      alert("Failed to invite user: " + err.message);
    }
  });

  const handleInviteSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    inviteMutation.mutate(inviteForm);
  };

  return (
    <div className="animate-enter relative">
      <PageTitle
        eyebrow="Team management"
        title="Users"
        description="Manage team members and their roles in the incident response workflow."
        action={
          <button
            onClick={() => setIsInviteOpen(true)}
            className="focus-ring inline-flex items-center justify-center gap-2 rounded-xl bg-sky-400 px-4 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-sky-300"
          >
            <Users size={16} />
            Invite member
          </button>
        }
      />

      {isInviteOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
          <div className="panel w-full max-w-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Invite Team Member</h3>
              <button onClick={() => setIsInviteOpen(false)} className="text-slate-400 hover:text-white">
                <X size={20} />
              </button>
            </div>
            <form onSubmit={handleInviteSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  value={inviteForm.name}
                  onChange={e => setInviteForm(f => ({ ...f, name: e.target.value }))}
                  className="w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-sm text-slate-200 focus:border-sky-500 focus:outline-none"
                  placeholder="Maya Chen"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  value={inviteForm.email}
                  onChange={e => setInviteForm(f => ({ ...f, email: e.target.value }))}
                  className="w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-sm text-slate-200 focus:border-sky-500 focus:outline-none"
                  placeholder="maya@company.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Role</label>
                <select
                  value={inviteForm.role}
                  onChange={e => setInviteForm(f => ({ ...f, role: e.target.value }))}
                  className="w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-sm text-slate-200 focus:border-sky-500 focus:outline-none"
                >
                  <option value="admin">Admin</option>
                  <option value="incident_commander">Incident Commander</option>
                  <option value="responder">SRE Engineer (Responder)</option>
                  <option value="viewer">Viewer</option>
                </select>
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setIsInviteOpen(false)}
                  className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={inviteMutation.isPending}
                  className="rounded-lg bg-sky-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-sky-400 disabled:opacity-50"
                >
                  {inviteMutation.isPending ? "Inviting..." : "Send Invite"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

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
          {isLoading && (
            <div className="px-5 py-8 text-center text-sm text-slate-500">Loading users...</div>
          )}
          {!isLoading && (users || []).map((user: any) => {
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
                <span className="rounded-full px-2 py-0.5 text-[10px] font-medium bg-emerald-400/10 text-emerald-200">
                  active
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
