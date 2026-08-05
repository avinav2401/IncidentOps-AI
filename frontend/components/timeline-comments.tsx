"use client";

import React, { useState } from "react";
import { MessageSquarePlus, Send, LoaderCircle } from "lucide-react";
import { addComment } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";

export function TimelineComments({ incidentId }: { incidentId: string }) {
  const [comment, setComment] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!comment.trim()) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const success = await addComment(incidentId, comment);
      if (success) {
        setComment("");
        // Refresh the page to load new timeline events
        router.refresh();
      } else {
        setError("Failed to add comment. Please try again.");
      }
    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mt-6 border-t border-slate-700/40 pt-6">
      <div className="flex items-start gap-3">
        <div className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-slate-800 border border-slate-700 text-slate-400">
          <MessageSquarePlus size={15} />
        </div>
        <div className="min-w-0 flex-1">
          <form onSubmit={handleSubmit} className="relative">
            <div className="overflow-hidden rounded-lg border border-slate-700/50 bg-slate-800/20 focus-within:border-violet-500/50 focus-within:ring-1 focus-within:ring-violet-500/50 transition-colors">
              <label htmlFor="comment" className="sr-only">
                Add your comment
              </label>
              <textarea
                rows={3}
                name="comment"
                id="comment"
                className="block w-full resize-none border-0 bg-transparent px-3 py-3 text-sm text-slate-200 placeholder:text-slate-500 focus:ring-0"
                placeholder="Add a comment to the timeline..."
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                disabled={isSubmitting}
              />
              
              <div className="flex items-center justify-between border-t border-slate-700/40 bg-slate-800/40 px-3 py-2">
                <span className="text-[10px] uppercase tracking-wider text-slate-500">
                  Visible in postmortem
                </span>
                <button
                  type="submit"
                  disabled={!comment.trim() || isSubmitting}
                  className="inline-flex items-center gap-1.5 rounded-md bg-violet-600 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-violet-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? (
                    <LoaderCircle size={14} className="animate-spin" />
                  ) : (
                    <Send size={14} />
                  )}
                  Post Comment
                </button>
              </div>
            </div>
            {error && <p className="mt-2 text-xs text-rose-400">{error}</p>}
          </form>
        </div>
      </div>
    </div>
  );
}
