"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Activity, Building2, CheckCircle2, ChevronRight, LayoutDashboard, Slack, Users } from "lucide-react";

export default function WorkspaceWizard() {
  const [step, setStep] = useState(1);
  const router = useRouter();

  // Step 1: Workspace details
  const [workspaceName, setWorkspaceName] = useState("");
  const [industry, setIndustry] = useState("Technology");
  const [size, setSize] = useState("1-10");

  // Step 2: First Service
  const [serviceName, setServiceName] = useState("");
  const [repository, setRepository] = useState("");

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleCreateWorkspace = async () => {
    setIsSubmitting(true);
    setError("");
    try {
      const token = localStorage.getItem("incidentops_token");
      
      // Create Workspace
      const wsRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/workspaces`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          name: workspaceName,
          industry,
          company_size: size
        }),
      });
      
      if (!wsRes.ok) throw new Error("Failed to create workspace");

      // Create Service if provided
      if (serviceName) {
        await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/services`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
          },
          body: JSON.stringify({
            name: serviceName,
            owner_team: "Platform Engineering",
            repository
          }),
        });
      }

      setStep(3); // Go to Integrations step
    } catch (err: any) {
      setError(err.message || "Something went wrong.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFinish = () => {
    router.push("/dashboard");
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#07111f] p-4 text-slate-200">
      <div className="w-full max-w-[600px]">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 grid h-12 w-12 place-items-center rounded-xl bg-gradient-to-br from-sky-400 to-indigo-500 text-slate-950 shadow-glow-blue">
            <Activity size={28} strokeWidth={2.6} />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            {step === 1 && "Setup your workspace"}
            {step === 2 && "Add your first service"}
            {step === 3 && "Connect your tools"}
          </h1>
          <p className="mt-2 text-sm text-slate-400">
            {step === 1 && "Let's configure your company details."}
            {step === 2 && "What are you monitoring?"}
            {step === 3 && "Integrate with your existing stack."}
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8 flex justify-between px-12">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex flex-col items-center gap-2">
              <div className={`grid h-8 w-8 place-items-center rounded-full border-2 text-xs font-bold transition-colors ${step >= i ? "border-sky-500 bg-sky-500 text-white shadow-glow-blue" : "border-slate-700 bg-slate-900 text-slate-500"}`}>
                {step > i ? <CheckCircle2 size={16} /> : i}
              </div>
            </div>
          ))}
        </div>

        {/* Card */}
        <div className="rounded-2xl border border-slate-700/50 bg-[#081422]/90 p-8 shadow-2xl backdrop-blur-xl">
          {error && (
            <div className="mb-6 rounded-lg bg-rose-500/10 p-3 text-sm text-rose-400">
              {error}
            </div>
          )}

          {step === 1 && (
            <div className="space-y-5">
              <div>
                <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-400">Company Name</label>
                <div className="relative">
                  <Building2 size={18} className="absolute left-3.5 top-3 text-slate-500" />
                  <input
                    type="text"
                    value={workspaceName}
                    onChange={(e) => setWorkspaceName(e.target.value)}
                    className="w-full rounded-xl border border-slate-700 bg-slate-900/50 py-2.5 pl-10 pr-4 text-sm outline-none transition focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                    placeholder="Acme Corp"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-400">Industry</label>
                  <select
                    value={industry}
                    onChange={(e) => setIndustry(e.target.value)}
                    className="w-full rounded-xl border border-slate-700 bg-slate-900/50 px-4 py-2.5 text-sm outline-none transition focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                  >
                    <option>Technology</option>
                    <option>E-Commerce</option>
                    <option>Finance</option>
                    <option>Healthcare</option>
                    <option>Other</option>
                  </select>
                </div>
                <div>
                  <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-400">Company Size</label>
                  <select
                    value={size}
                    onChange={(e) => setSize(e.target.value)}
                    className="w-full rounded-xl border border-slate-700 bg-slate-900/50 px-4 py-2.5 text-sm outline-none transition focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                  >
                    <option>1-10</option>
                    <option>11-50</option>
                    <option>51-200</option>
                    <option>201+</option>
                  </select>
                </div>
              </div>
              <button
                onClick={() => setStep(2)}
                disabled={!workspaceName}
                className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-sky-500 py-3 text-sm font-semibold text-white shadow-glow-blue transition hover:bg-sky-400 disabled:opacity-50"
              >
                Continue <ChevronRight size={16} />
              </button>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-5">
              <div>
                <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-400">Service Name</label>
                <div className="relative">
                  <LayoutDashboard size={18} className="absolute left-3.5 top-3 text-slate-500" />
                  <input
                    type="text"
                    value={serviceName}
                    onChange={(e) => setServiceName(e.target.value)}
                    className="w-full rounded-xl border border-slate-700 bg-slate-900/50 py-2.5 pl-10 pr-4 text-sm outline-none transition focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                    placeholder="api-gateway"
                  />
                </div>
              </div>
              <div>
                <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-400">GitHub Repository (Optional)</label>
                <input
                  type="text"
                  value={repository}
                  onChange={(e) => setRepository(e.target.value)}
                  className="w-full rounded-xl border border-slate-700 bg-slate-900/50 px-4 py-2.5 text-sm outline-none transition focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                  placeholder="acme/api-gateway"
                />
              </div>
              
              <div className="flex gap-3 pt-4">
                <button
                  onClick={() => setStep(1)}
                  className="rounded-xl border border-slate-700 bg-slate-900/50 px-6 py-3 text-sm font-semibold text-slate-300 transition hover:bg-slate-800"
                >
                  Back
                </button>
                <button
                  onClick={handleCreateWorkspace}
                  disabled={isSubmitting}
                  className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-sky-500 py-3 text-sm font-semibold text-white shadow-glow-blue transition hover:bg-sky-400 disabled:opacity-50"
                >
                  {isSubmitting ? "Saving..." : "Create Workspace"} <ChevronRight size={16} />
                </button>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-6 text-center">
              <div className="mx-auto grid h-16 w-16 place-items-center rounded-2xl bg-emerald-500/10 text-emerald-400">
                <CheckCircle2 size={32} />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white">Workspace created!</h3>
                <p className="mt-2 text-sm text-slate-400">Your workspace is ready. You can connect your tools now or do it later from the dashboard.</p>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <button className="flex items-center justify-center gap-3 rounded-xl border border-slate-700 bg-slate-800/50 p-4 transition hover:border-slate-500 hover:bg-slate-700/50">
                  <Slack size={20} className="text-slate-300" />
                  <span className="text-sm font-medium">Connect Slack</span>
                </button>
                <button className="flex items-center justify-center gap-3 rounded-xl border border-slate-700 bg-slate-800/50 p-4 transition hover:border-slate-500 hover:bg-slate-700/50">
                  <Users size={20} className="text-slate-300" />
                  <span className="text-sm font-medium">Invite Team</span>
                </button>
              </div>

              <button
                onClick={handleFinish}
                className="w-full rounded-xl bg-sky-500 py-3 text-sm font-semibold text-white shadow-glow-blue transition hover:bg-sky-400"
              >
                Go to Dashboard
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
