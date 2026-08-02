"use client";

import { Activity, CheckCircle2 } from "lucide-react";
import Link from "next/link";

export default function VerifyPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[#07111f] p-4 text-slate-200">
      <div className="w-full max-w-[400px] text-center">
        <div className="mb-6 flex flex-col items-center">
          <div className="mb-4 grid h-12 w-12 place-items-center rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 text-slate-950 shadow-lg shadow-emerald-500/20">
            <CheckCircle2 size={28} strokeWidth={2.6} />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Check your email</h1>
          <p className="mt-4 text-sm text-slate-400">
            We've sent a verification link to your email address. Please click the link to verify your account and continue.
          </p>
        </div>

        <div className="mt-8">
          <Link href="/login" className="text-sm font-semibold text-sky-400 hover:underline">
            Return to login
          </Link>
        </div>
      </div>
    </div>
  );
}
