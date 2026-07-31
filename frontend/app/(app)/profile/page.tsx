"use client";

import { PageTitle, Avatar } from "@/components/ui";
import { useAuth } from "@/lib/auth-context";
import { LogOut, Mail, User as UserIcon, Shield, Key } from "lucide-react";
import { useRouter } from "next/navigation";

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  if (!user) return null;

  return (
    <div className="animate-enter">
      <PageTitle 
        eyebrow="Management"
        title="Profile Settings" 
        description="Manage your account, preferences, and personal details."
      />

      <div className="mt-8 grid gap-6 lg:grid-cols-[1fr_300px]">
        {/* Profile Form */}
        <div className="panel p-6 sm:p-8">
          <div className="flex items-center gap-6">
            <Avatar name={user.name} />
            <div>
              <h2 className="text-xl font-semibold text-slate-100">{user.name}</h2>
              <p className="text-sm text-slate-400 capitalize">{user.role}</p>
            </div>
          </div>

          <div className="mt-10 space-y-6">
            <div className="grid gap-6 sm:grid-cols-2">
              <div className="space-y-2">
                <label className="flex items-center gap-2 text-sm font-medium text-slate-300">
                  <UserIcon size={16} className="text-slate-500" /> Full Name
                </label>
                <input 
                  type="text" 
                  defaultValue={user.name}
                  className="w-full rounded-xl border border-slate-700/60 bg-slate-900/50 px-4 py-2.5 text-sm text-slate-200 transition focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
                />
              </div>
              <div className="space-y-2">
                <label className="flex items-center gap-2 text-sm font-medium text-slate-300">
                  <Mail size={16} className="text-slate-500" /> Email Address
                </label>
                <input 
                  type="email" 
                  defaultValue={user.email}
                  disabled
                  className="w-full rounded-xl border border-slate-700/60 bg-slate-800/50 px-4 py-2.5 text-sm text-slate-500 cursor-not-allowed"
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm font-medium text-slate-300">
                <Shield size={16} className="text-slate-500" /> Role
              </label>
              <input 
                type="text" 
                defaultValue={user.role}
                disabled
                className="w-full rounded-xl border border-slate-700/60 bg-slate-800/50 px-4 py-2.5 text-sm text-slate-500 cursor-not-allowed capitalize"
              />
            </div>
            
            <div className="pt-6 flex justify-end">
              <button className="focus-ring rounded-xl bg-sky-500 px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-sky-400">
                Save Changes
              </button>
            </div>
          </div>
        </div>

        {/* Sidebar Settings */}
        <div className="space-y-6">
          <div className="panel p-6">
            <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
              <Key size={16} className="text-slate-400" /> Security
            </h3>
            <p className="mt-2 text-xs text-slate-400 leading-relaxed">
              Update your password or configure two-factor authentication (2FA).
            </p>
            <button className="mt-4 w-full rounded-lg border border-slate-700/60 bg-slate-800/50 py-2 text-xs font-medium text-slate-300 transition hover:bg-slate-700">
              Change Password
            </button>
          </div>
          
          <div className="panel p-6 border-rose-500/20 bg-rose-500/5">
            <h3 className="text-sm font-semibold text-rose-300">Danger Zone</h3>
            <p className="mt-2 text-xs text-rose-400/70 leading-relaxed">
              Sign out of your account on this device.
            </p>
            <button 
              onClick={handleLogout}
              className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-rose-500/10 py-2 text-xs font-medium text-rose-400 transition hover:bg-rose-500/20"
            >
              <LogOut size={14} /> Sign Out
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
