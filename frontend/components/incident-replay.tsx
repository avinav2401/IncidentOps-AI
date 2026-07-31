"use client";

import React, { useState, useEffect } from "react";
import { Play, Pause, SkipForward, RotateCcw } from "lucide-react";
import type { Incident } from "@/lib/types";

interface IncidentReplayProps {
  incident: Incident;
  onScrub: (index: number) => void;
  isActive: boolean;
  onToggleActive: () => void;
}

export function IncidentReplay({ incident, onScrub, isActive, onToggleActive }: IncidentReplayProps) {
  const maxEvents = incident.timeline.length;
  const [currentIndex, setCurrentIndex] = useState(maxEvents);
  const [isPlaying, setIsPlaying] = useState(false);

  // If incident changes and replay is not active, reset to latest
  useEffect(() => {
    if (!isActive) {
      setCurrentIndex(maxEvents);
      onScrub(maxEvents);
    }
  }, [isActive, maxEvents, onScrub]);

  // Handle Playback
  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (isPlaying) {
      interval = setInterval(() => {
        setCurrentIndex((prev) => {
          if (prev >= maxEvents) {
            setIsPlaying(false);
            return prev;
          }
          const next = prev + 1;
          onScrub(next);
          return next;
        });
      }, 2000); // 2 seconds per tick
    }
    return () => clearInterval(interval);
  }, [isPlaying, maxEvents, onScrub]);

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseInt(e.target.value, 10);
    setCurrentIndex(val);
    onScrub(val);
    setIsPlaying(false);
  };

  const handlePlayPause = () => {
    if (currentIndex >= maxEvents) {
      // Replay from beginning if at the end
      setCurrentIndex(1);
      onScrub(1);
      setIsPlaying(true);
    } else {
      setIsPlaying(!isPlaying);
    }
  };

  const handleSkipToEnd = () => {
    setIsPlaying(false);
    setCurrentIndex(maxEvents);
    onScrub(maxEvents);
  };

  const handleReset = () => {
    setIsPlaying(false);
    setCurrentIndex(1);
    onScrub(1);
  };

  if (!isActive) {
    return (
      <button 
        onClick={onToggleActive}
        className="focus-ring inline-flex items-center gap-2 rounded-xl border border-sky-400/30 bg-sky-400/10 px-3 py-2 text-xs font-semibold text-sky-200 transition hover:bg-sky-400/20"
      >
        <RotateCcw size={14} />
        Time Travel Replay
      </button>
    );
  }

  const currentEvent = incident.timeline[currentIndex - 1];

  return (
    <div className="rounded-xl border border-sky-500/30 bg-[#07121e] p-4 shadow-[0_0_20px_rgba(56,189,248,0.15)] animate-in fade-in slide-in-from-top-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <RotateCcw size={16} className="text-sky-400 animate-spin-slow" />
          <h3 className="text-sm font-semibold text-sky-100">Time Travel Replay</h3>
        </div>
        <button 
          onClick={onToggleActive}
          className="text-[11px] font-medium text-slate-400 hover:text-slate-200"
        >
          Exit Replay
        </button>
      </div>

      <div className="flex flex-col gap-4">
        <div className="flex items-center gap-4">
          <button 
            onClick={handlePlayPause}
            className="grid h-10 w-10 place-items-center rounded-full bg-sky-500 text-sky-950 transition hover:bg-sky-400"
          >
            {isPlaying ? <Pause size={18} className="fill-current" /> : <Play size={18} className="fill-current" />}
          </button>
          
          <div className="flex flex-1 flex-col gap-2">
            <div className="flex justify-between text-xs font-medium text-slate-300">
              <span>{incident.timeline[0]?.time}</span>
              <span className="text-sky-300 font-bold">{currentEvent?.time}</span>
              <span>{incident.timeline[maxEvents - 1]?.time}</span>
            </div>
            <input 
              type="range" 
              min={1} 
              max={maxEvents} 
              value={currentIndex} 
              onChange={handleSliderChange}
              className="h-2 w-full appearance-none rounded-full bg-slate-700 accent-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-slate-900"
            />
          </div>

          <button 
            onClick={handleSkipToEnd}
            className="grid h-10 w-10 place-items-center rounded-full bg-slate-800 text-slate-300 transition hover:bg-slate-700 hover:text-white"
          >
            <SkipForward size={18} />
          </button>
        </div>

        <div className="rounded-lg bg-sky-500/10 border border-sky-500/20 px-3 py-2 flex items-center justify-between">
          <span className="text-[11px] text-sky-200/70 uppercase tracking-widest font-semibold">Current State</span>
          <span className="text-xs font-medium text-sky-100">{currentEvent?.title || 'Initializing...'}</span>
        </div>
      </div>
    </div>
  );
}
