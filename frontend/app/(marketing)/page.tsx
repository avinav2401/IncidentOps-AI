"use client";

import Link from "next/link";
import { Activity, ArrowRight, BarChart3, Bot, Brain, CheckCircle2, ChevronRight, Clock3, FileText, GitBranch, Globe, Layers, Lock, MessageSquare, Play, Shield, ShieldCheck, Sparkles, Terminal, Users, Zap } from "lucide-react";
import { useState } from "react";

const features = [
  { icon: Bot, title: "Multi-Agent AI", description: "Six specialized agents investigate incidents in parallel — logs, metrics, deployments, and more.", color: "from-sky-400 to-cyan-400" },
  { icon: Brain, title: "Root Cause Analysis", description: "AI synthesizes evidence from all agents to pinpoint the exact cause with confidence scores.", color: "from-violet-400 to-purple-400" },
  { icon: ShieldCheck, title: "Human Approval Gate", description: "AI recommends — humans approve. Every action is gated and audited for compliance.", color: "from-emerald-400 to-teal-400" },
  { icon: FileText, title: "Knowledge Base", description: "Learns from past incidents. AI searches solutions before suggesting new ones.", color: "from-amber-400 to-orange-400" },
  { icon: BarChart3, title: "Analytics & Reports", description: "Track MTTR, resolution rates, severity trends, and generate downloadable postmortems.", color: "from-rose-400 to-pink-400" },
  { icon: Layers, title: "Integrations", description: "Connects with Slack, Jira, GitHub, Kubernetes, Prometheus, Grafana, and more.", color: "from-indigo-400 to-blue-400" },
];

const steps = [
  { step: "01", title: "Detect", description: "Alert arrives via webhook, Slack, or manual entry. AI agents start automatically.", icon: Zap },
  { step: "02", title: "Investigate", description: "Parallel agents analyze logs, metrics, deployments, and service health in real-time.", icon: Bot },
  { step: "03", title: "Recommend", description: "Root cause identified with confidence score. AI proposes remediation with risk assessment.", icon: Brain },
  { step: "04", title: "Resolve", description: "Human approves the fix. System executes, verifies recovery, and generates a postmortem.", icon: CheckCircle2 },
];

const pricing = [
  { name: "Starter", price: "Free", description: "For small teams getting started.", features: ["5 incidents/month", "3 team members", "Basic AI analysis", "Email notifications", "7-day retention"], cta: "Start Free", highlighted: false },
  { name: "Pro", price: "$49", description: "For growing engineering teams.", features: ["Unlimited incidents", "25 team members", "Advanced AI agents", "Slack + Jira integration", "90-day retention", "Custom runbooks", "PDF reports"], cta: "Start Free Trial", highlighted: true },
  { name: "Enterprise", price: "Custom", description: "For organizations at scale.", features: ["Everything in Pro", "Unlimited team members", "SSO/SAML", "Dedicated support", "1-year retention", "API access", "Custom integrations", "SLA guarantee"], cta: "Contact Sales", highlighted: false },
];

export default function LandingPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#06101b] text-slate-200">
      {/* ── Navbar ── */}
      <nav className="fixed top-0 z-50 w-full border-b border-slate-800/60 bg-[#06101b]/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
          <Link href="/" className="flex items-center gap-3">
            <span className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-sky-400 to-indigo-500 text-slate-950 shadow-lg shadow-sky-400/20">
              <Activity size={20} strokeWidth={2.6} />
            </span>
            <span className="text-lg font-bold tracking-tight text-white">IncidentOps<span className="text-sky-400"> AI</span></span>
          </Link>
          <div className="hidden items-center gap-8 md:flex">
            <a href="#features" className="text-sm text-slate-400 transition hover:text-white">Features</a>
            <a href="#how-it-works" className="text-sm text-slate-400 transition hover:text-white">How it Works</a>
            <a href="#pricing" className="text-sm text-slate-400 transition hover:text-white">Pricing</a>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login" className="hidden text-sm font-medium text-slate-300 transition hover:text-white md:block">Sign in</Link>
            <Link href="/dashboard" className="rounded-xl bg-sky-500 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-sky-500/25 transition hover:bg-sky-400 hover:shadow-sky-400/30">Get Started</Link>
          </div>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="relative overflow-hidden pt-32 pb-20 sm:pt-40 sm:pb-28">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(56,189,248,0.08),transparent_60%)]" />
        <div className="absolute top-20 left-1/2 -translate-x-1/2 h-[500px] w-[800px] rounded-full bg-sky-500/[0.04] blur-[120px]" />
        <div className="relative mx-auto max-w-4xl px-6 text-center">
          <div className="mx-auto mb-6 inline-flex items-center gap-2 rounded-full border border-sky-400/20 bg-sky-400/[0.06] px-4 py-1.5 text-xs font-medium text-sky-300">
            <Sparkles size={13} /> Powered by Multi-Agent AI
          </div>
          <h1 className="text-4xl font-bold tracking-tight text-white sm:text-6xl lg:text-7xl">
            AI-Powered<br />
            <span className="bg-gradient-to-r from-sky-400 via-cyan-300 to-indigo-400 bg-clip-text text-transparent">Incident Response</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-slate-400 sm:text-xl">
            Reduce MTTR by 80% using autonomous AI agents that investigate, diagnose, and resolve production incidents — with human oversight at every step.
          </p>
          <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
            <Link href="/dashboard" className="group inline-flex items-center gap-2 rounded-xl bg-sky-500 px-6 py-3.5 text-sm font-semibold text-white shadow-xl shadow-sky-500/25 transition hover:bg-sky-400 hover:shadow-sky-400/30">
              Start Free <ArrowRight size={16} className="transition group-hover:translate-x-1" />
            </Link>
            <Link href="/dashboard" className="inline-flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-900/50 px-6 py-3.5 text-sm font-semibold text-slate-300 transition hover:border-slate-600 hover:bg-slate-800/60 hover:text-white">
              <Play size={16} /> Live Demo
            </Link>
          </div>
          <div className="mt-12 flex items-center justify-center gap-6 text-xs text-slate-500">
            <span className="flex items-center gap-1.5"><CheckCircle2 size={13} className="text-emerald-400" /> No credit card</span>
            <span className="flex items-center gap-1.5"><Lock size={13} className="text-emerald-400" /> SOC2 ready</span>
            <span className="flex items-center gap-1.5"><Globe size={13} className="text-emerald-400" /> Deploy anywhere</span>
          </div>
        </div>
      </section>

      {/* ── Features ── */}
      <section id="features" className="relative py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6">
          <div className="text-center">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-sky-400">Features</p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-white sm:text-4xl">Everything you need to fight incidents</h2>
            <p className="mx-auto mt-4 max-w-2xl text-base text-slate-400">From detection to postmortem, IncidentOps AI handles the entire lifecycle.</p>
          </div>
          <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature) => {
              const Icon = feature.icon;
              return (
                <article key={feature.title} className="group rounded-2xl border border-slate-800/60 bg-slate-900/30 p-6 transition hover:-translate-y-1 hover:border-slate-700/80 hover:bg-slate-900/50 hover:shadow-xl hover:shadow-sky-500/[0.03]">
                  <span className={`grid h-12 w-12 place-items-center rounded-xl bg-gradient-to-br ${feature.color} text-slate-950 shadow-lg`}>
                    <Icon size={22} />
                  </span>
                  <h3 className="mt-5 text-lg font-semibold text-white">{feature.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-400">{feature.description}</p>
                </article>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── How It Works ── */}
      <section id="how-it-works" className="relative border-y border-slate-800/60 bg-slate-900/20 py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6">
          <div className="text-center">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-sky-400">How it works</p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-white sm:text-4xl">From alert to resolution in minutes</h2>
          </div>
          <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {steps.map((step, idx) => {
              const Icon = step.icon;
              return (
                <div key={step.step} className="relative text-center">
                  {idx < steps.length - 1 && (
                    <div className="absolute right-0 top-8 hidden h-px w-8 translate-x-full bg-gradient-to-r from-sky-400/40 to-transparent lg:block" />
                  )}
                  <span className="mx-auto grid h-16 w-16 place-items-center rounded-2xl border border-sky-400/20 bg-sky-400/[0.06]">
                    <Icon size={28} className="text-sky-400" />
                  </span>
                  <p className="mt-1 text-xs font-bold text-sky-400/60">{step.step}</p>
                  <h3 className="mt-3 text-lg font-semibold text-white">{step.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-400">{step.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── Pricing ── */}
      <section id="pricing" className="py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6">
          <div className="text-center">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-sky-400">Pricing</p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-white sm:text-4xl">Simple, transparent pricing</h2>
            <p className="mx-auto mt-4 max-w-xl text-base text-slate-400">Start free. Scale as you grow.</p>
          </div>
          <div className="mt-16 grid gap-6 lg:grid-cols-3">
            {pricing.map((plan) => (
              <article key={plan.name} className={`relative rounded-2xl border p-8 transition ${plan.highlighted ? "border-sky-400/40 bg-sky-400/[0.04] shadow-xl shadow-sky-500/[0.06]" : "border-slate-800/60 bg-slate-900/30"}`}>
                {plan.highlighted && (
                  <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-sky-500 px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-white">Most popular</span>
                )}
                <h3 className="text-lg font-semibold text-white">{plan.name}</h3>
                <p className="mt-1 text-sm text-slate-400">{plan.description}</p>
                <p className="mt-6">
                  <span className="text-4xl font-bold tracking-tight text-white">{plan.price}</span>
                  {plan.price !== "Custom" && plan.price !== "Free" && <span className="text-sm text-slate-400">/month</span>}
                </p>
                <Link href="/dashboard" className={`mt-8 block rounded-xl py-3 text-center text-sm font-semibold transition ${plan.highlighted ? "bg-sky-500 text-white shadow-lg shadow-sky-500/25 hover:bg-sky-400" : "border border-slate-700 bg-slate-800/40 text-slate-300 hover:bg-slate-700/60 hover:text-white"}`}>
                  {plan.cta}
                </Link>
                <ul className="mt-8 space-y-3">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-2 text-sm text-slate-400">
                      <CheckCircle2 size={15} className="mt-0.5 shrink-0 text-emerald-400" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="border-t border-slate-800/60 bg-gradient-to-b from-sky-500/[0.04] to-transparent py-24">
        <div className="mx-auto max-w-3xl px-6 text-center">
          <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">Ready to transform your incident response?</h2>
          <p className="mt-4 text-lg text-slate-400">Join teams reducing MTTR by 80% with AI-powered operations.</p>
          <div className="mt-8 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
            <Link href="/dashboard" className="inline-flex items-center gap-2 rounded-xl bg-sky-500 px-6 py-3.5 text-sm font-semibold text-white shadow-xl shadow-sky-500/25 transition hover:bg-sky-400">
              Get Started Free <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-slate-800/60 py-12">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-6 px-6 sm:flex-row">
          <div className="flex items-center gap-3">
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-gradient-to-br from-sky-400 to-indigo-500 text-slate-950">
              <Activity size={16} strokeWidth={2.6} />
            </span>
            <span className="text-sm font-semibold text-slate-300">IncidentOps AI</span>
          </div>
          <p className="text-xs text-slate-600">© 2026 IncidentOps AI. Built for the future of incident response.</p>
          <div className="flex gap-6 text-xs text-slate-500">
            <a href="#" className="hover:text-slate-300">Privacy</a>
            <a href="#" className="hover:text-slate-300">Terms</a>
            <a href="https://github.com" className="hover:text-slate-300">GitHub</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
