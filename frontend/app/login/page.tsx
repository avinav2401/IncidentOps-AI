"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Activity } from "lucide-react";

export default function LoginPage() {
  const [email, setEmail] = useState("maya.chen@incidentops.dev");
  const [password, setPassword] = useState("demo123");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError("");

    try {
      await login(email, password);
      router.push("/");
    } catch {
      setError("Invalid email or password");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#07111f] p-4 text-slate-200">
      <div className="w-full max-w-[400px]">
        <div className="mb-8 flex flex-col items-center">
          <div className="mb-4 grid h-12 w-12 place-items-center rounded-xl bg-gradient-to-br from-sky-400 to-indigo-500 text-slate-950 shadow-glow-blue">
            <Activity size={28} strokeWidth={2.6} />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Sign in to IncidentOps</h1>
          <p className="mt-2 text-sm text-slate-400">Welcome back, commander.</p>
        </div>

        <div className="rounded-2xl border border-slate-700/50 bg-[#081422]/90 p-8 shadow-2xl backdrop-blur-xl">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-400" htmlFor="email">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-900/50 px-4 py-2.5 text-sm outline-none transition focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                required
              />
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-400" htmlFor="password">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-900/50 px-4 py-2.5 text-sm outline-none transition focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                required
              />
            </div>
            {error && (
              <div className="rounded-lg bg-rose-500/10 p-3 text-sm text-rose-400">
                {error}
              </div>
            )}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full rounded-xl bg-sky-500 py-3 text-sm font-semibold text-white shadow-glow-blue transition hover:bg-sky-400 disabled:opacity-50"
            >
              {isSubmitting ? "Signing in..." : "Sign in"}
            </button>
          </form>
        </div>
        
        <div className="mt-8 text-center text-xs text-slate-500">
          <p>Demo accounts:</p>
          <p className="mt-1">maya.chen@incidentops.dev / demo123 (Commander)</p>
          <p>samir.patel@incidentops.dev / demo123 (Responder)</p>
          <p>lena.ortiz@incidentops.dev / demo123 (Admin)</p>
        </div>
      </div>
    </div>
  );
}
