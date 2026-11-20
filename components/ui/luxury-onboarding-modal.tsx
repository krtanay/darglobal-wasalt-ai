"use client";

import React, { useState } from "react";
import { Building2, ShieldCheck, Sparkles, Key, X } from "lucide-react";
import { cn } from "@/lib/utils";

export interface LuxuryOnboardingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConnectKey?: (key: string) => void;
  initialKey?: string;
  className?: string;
}

export const LuxuryOnboardingModal: React.FC<LuxuryOnboardingModalProps> = ({
  isOpen,
  onClose,
  onConnectKey,
  initialKey = "",
  className,
}) => {
  const [apiKey, setApiKey] = useState(initialKey);

  if (!isOpen) return null;

  const handleStart = () => {
    if (apiKey.trim() && onConnectKey) {
      onConnectKey(apiKey.trim());
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-md animate-fade-in">
      <div
        className={cn(
          "relative w-full max-w-lg rounded-[2rem] border border-amber-500/30 bg-neutral-950/95 p-6 sm:p-8",
          "shadow-2xl shadow-amber-500/10 text-slate-100 backdrop-blur-xl",
          className
        )}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute right-5 top-5 rounded-full p-2 text-slate-400 hover:bg-neutral-900 hover:text-white transition"
          aria-label="Close onboarding modal"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Executive Header */}
        <div className="mb-6 text-center border-b border-neutral-800 pb-5">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-amber-400 via-amber-500 to-amber-700 shadow-lg shadow-amber-500/20">
            <Building2 className="h-6 w-6 text-neutral-950" />
          </div>
          <div className="flex items-center justify-center space-x-2">
            <span className="font-serif text-base font-bold tracking-wider text-white">DARGLOBAL</span>
            <span className="text-amber-400 font-serif font-light text-sm">×</span>
            <span className="font-serif text-base font-bold tracking-wider text-slate-300">WASALT</span>
          </div>
          <h1 className="mt-1 text-xl sm:text-2xl font-bold tracking-tight text-white font-serif">
            Luxury Real Estate AI Advisor
          </h1>
          <p className="mt-1 text-xs text-slate-400">
            Grounded with verified data from DarGlobal International & Wasalt Saudi PropTech.
          </p>
        </div>

        {/* Features Pillars */}
        <div className="mb-6 space-y-3.5">
          {/* Pillar 1: DarGlobal */}
          <div className="flex items-start gap-3.5 rounded-xl border border-neutral-800/80 bg-neutral-900/60 p-3.5 transition hover:border-amber-500/30">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-amber-500/15 border border-amber-500/30">
              <Sparkles className="h-5 w-5 text-amber-400" />
            </div>
            <div>
              <h3 className="text-xs sm:text-sm font-semibold text-white">
                Branded International Luxury (DarGlobal)
              </h3>
              <p className="text-[11px] sm:text-xs text-slate-400 leading-relaxed mt-0.5">
                Villas and residences co-designed with <strong>Lamborghini</strong>, <strong>Pagani</strong>, <strong>Missoni</strong>, and <strong>Trump</strong> across Dubai, Spain, London, and Oman.
              </p>
            </div>
          </div>

          {/* Pillar 2: Wasalt */}
          <div className="flex items-start gap-3.5 rounded-xl border border-neutral-800/80 bg-neutral-900/60 p-3.5 transition hover:border-emerald-500/30">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-500/15 border border-emerald-500/30">
              <ShieldCheck className="h-5 w-5 text-emerald-400" />
            </div>
            <div>
              <h3 className="text-xs sm:text-sm font-semibold text-white">
                Saudi PropTech & REGA Licensed (Wasalt)
              </h3>
              <p className="text-[11px] sm:text-xs text-slate-400 leading-relaxed mt-0.5">
                REGA-certified master developments, townhouses, and luxury villas across Riyadh, Jeddah, and Al-Khobar.
              </p>
            </div>
          </div>
        </div>

        {/* API Key Activation Section */}
        <div className="mb-6 rounded-xl border border-amber-500/25 bg-amber-500/5 p-4">
          <label className="mb-1.5 flex items-center justify-between text-xs font-semibold text-slate-200">
            <span className="flex items-center gap-1.5">
              <Key className="h-3.5 w-3.5 text-amber-400" />
              <span>Connect OpenRouter Key (Optional)</span>
            </span>
            <span className="text-[10px] text-amber-400 font-mono">Free Tier Ready</span>
          </label>
          <input
            type="password"
            placeholder="sk-or-v1-... (leave blank for local RAG mode)"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            className="w-full rounded-lg border border-neutral-800 bg-neutral-900 px-3 py-2 text-xs font-mono text-white placeholder-slate-500 focus:border-amber-500 focus:outline-none focus:ring-1 focus:ring-amber-500"
          />
          <p className="mt-1.5 text-[10px] text-slate-400">
            Enables sub-200ms token streaming with models like Nemotron 3.5 & Gemma 4 ($0 token cost).
          </p>
        </div>

        {/* Action Buttons */}
        <div className="space-y-2.5">
          <button
            onClick={handleStart}
            className="w-full rounded-xl bg-gradient-to-r from-amber-500 via-amber-600 to-amber-700 px-6 py-3.5 text-xs sm:text-sm font-bold text-neutral-950 transition hover:from-amber-400 hover:to-amber-500 shadow-md shadow-amber-500/15"
          >
            Start Exploring Residences
          </button>
          <button
            onClick={onClose}
            className="w-full py-2 text-xs font-medium text-slate-400 transition hover:text-white"
          >
            Browse Visual Catalog Directly
          </button>
        </div>
      </div>
    </div>
  );
};

export default LuxuryOnboardingModal;
