import Link from "next/link";
import { ArrowLeft, SearchX } from "lucide-react";

export default function NotFound() {
  return <div className="grid min-h-[60vh] place-items-center py-12 text-center"><div><span className="mx-auto grid h-14 w-14 place-items-center rounded-2xl border border-slate-700/60 bg-slate-800/45 text-slate-400"><SearchX size={24} /></span><p className="eyebrow mt-6">404 · Not found</p><h1 className="mt-2 text-2xl font-semibold tracking-tight text-slate-100">We couldn’t find that incident.</h1><p className="mt-2 max-w-md text-sm leading-6 text-slate-500">It may have been archived, or the link may no longer be valid.</p><Link href="/incidents" className="focus-ring mt-6 inline-flex items-center gap-2 rounded-xl bg-sky-400 px-4 py-2.5 text-sm font-semibold text-slate-950 hover:bg-sky-300"><ArrowLeft size={16} />Back to incidents</Link></div></div>;
}
