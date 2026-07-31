"use client";

import React from "react";
import { GitCommit, Activity, FileText, ChevronDown, CheckCircle } from "lucide-react";

interface EvidenceStep {
  step: string;
  type: "observation" | "deduction" | "conclusion";
}

interface DecisionTreeProps {
  evidenceChain: EvidenceStep[];
}

export function DecisionTree({ evidenceChain }: DecisionTreeProps) {
  if (!evidenceChain || evidenceChain.length === 0) {
    return <div className="text-sm text-slate-500">No reasoning available.</div>;
  }

  return (
    <div className="relative mt-4 mb-2 pl-4">
      {/* Vertical line connecting nodes */}
      <div className="absolute left-[27px] top-4 h-[calc(100%-32px)] w-px bg-slate-700/60" />

      <div className="flex flex-col gap-5">
        {evidenceChain.map((item, index) => {
          const isConclusion = item.type === "conclusion";
          const isDeduction = item.type === "deduction";

          let Icon = FileText;
          let bgColor = "bg-slate-800/80";
          let borderColor = "border-slate-700/50";
          let textColor = "text-slate-300";

          if (isConclusion) {
            Icon = CheckCircle;
            bgColor = "bg-emerald-900/30";
            borderColor = "border-emerald-500/30";
            textColor = "text-emerald-300";
          } else if (isDeduction) {
            Icon = Activity;
            bgColor = "bg-violet-900/20";
            borderColor = "border-violet-500/30";
            textColor = "text-violet-300";
          }

          return (
            <div key={index} className="relative flex items-start gap-4">
              <div className={`relative z-10 grid h-7 w-7 shrink-0 place-items-center rounded-full border shadow-sm ${bgColor} ${borderColor} ${textColor}`}>
                <Icon size={12} />
              </div>
              <div className={`flex flex-col pt-1`}>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-0.5">{item.type}</span>
                <span className={`text-sm ${textColor} font-medium leading-relaxed max-w-[90%]`}>
                  {item.step}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
