"use client";

import React, { useState } from "react";
import { Zap, ShieldCheck, Building2, Key } from "lucide-react";
import { cn } from "@/lib/utils";

export interface ModalCardProps {
  isOpen?: boolean;
  onStartChatting?: (apiKey?: string) => void;
  onMaybeLater?: () => void;
  initialKey?: string;
  className?: string;
}

export const ModalCard: React.FC<ModalCardProps> = ({
  isOpen = true,
  onStartChatting,
  onMaybeLater,
  initialKey = "",
  className,
}) => {
  const [apiKey, setApiKey] = useState(initialKey);

  if (!isOpen) return null;

  const handleStart = () => {
    onStartChatting?.(apiKey.trim());
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-md p-4 overflow-hidden">
      <div
        className={cn(
          "w-full max-w-md rounded-[28px] bg-neutral-900 border border-neutral-800/80 p-5 sm:p-6 shadow-2xl text-white overflow-hidden",
          className
        )}
      >
        {/* Header - Compact */}
        <div className="mb-4 text-center border-b border-neutral-800 pb-3">
          <h1 className="text-xl sm:text-2xl font-semibold leading-tight text-white tracking-tight">
            You're invited to explore
            <br />
            DarGlobal × Wasalt AI
          </h1>
          <p className="text-[11px] text-neutral-400 mt-1">
            Real Estate AI Advisor with Microsoft-grade security and sub-3ms caching.
          </p>
        </div>

        {/* Benefits Pillars - 2 High-Impact Items */}
        <div className="mb-4 space-y-2.5">
          {/* Pillar 1: Ultra-Low Latency */}
          <div className="flex items-start gap-3 p-2.5 rounded-xl bg-neutral-950/60 border border-neutral-800/80">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-blue-600 shadow-md shadow-blue-600/30">
              <Zap className="h-4.5 w-4.5 text-white" />
            </div>
            <div className="pt-0.5">
              <h3 className="text-xs sm:text-sm font-semibold text-white">
                Sub-3ms Latency & Streaming
              </h3>
              <p className="text-[11px] text-neutral-400 leading-relaxed mt-0.5">
                Sub-3ms LRU response cache for instant answers, backed by sub-200ms real-time token streaming.
              </p>
            </div>
          </div>

          {/* Pillar 2: Microsoft-Grade Security & Verified RAG */}
          <div className="flex items-start gap-3 p-2.5 rounded-xl bg-neutral-950/60 border border-neutral-800/80">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-blue-600 shadow-md shadow-blue-600/30">
              <ShieldCheck className="h-4.5 w-4.5 text-white" />
            </div>
            <div className="pt-0.5">
              <h3 className="text-xs sm:text-sm font-semibold text-white">
                Microsoft PromptShield & Verified RAG
              </h3>
              <p className="text-[11px] text-neutral-400 leading-relaxed mt-0.5">
                Enterprise prompt injection defense grounded in verified DarGlobal luxury & Wasalt masterplans.
              </p>
            </div>
          </div>
        </div>

        {/* OpenRouter API Key Input */}
        <div className="mb-3.5 rounded-xl border border-neutral-800 bg-neutral-950/80 p-2.5">
          <label className="mb-1 flex items-center justify-between text-xs font-semibold text-neutral-200">
            <span className="flex items-center gap-1.5">
              <Key className="h-3.5 w-3.5 text-blue-400" />
              <span>OpenRouter API Key (Optional)</span>
            </span>
            <span className="text-[10px] text-emerald-400 font-mono">Free Tier Ready</span>
          </label>
          <input
            type="password"
            placeholder="sk-or-v1-... (optional, server key is ready)"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            className="w-full rounded-lg border border-neutral-800 bg-neutral-900 px-3 py-1.5 text-xs font-mono text-white placeholder-neutral-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
          <p className="mt-1 text-[10px] text-neutral-400">
            Free models (Nemotron 3.5, Gemma 4, Liquid LFM) run automatically at zero cost.
          </p>
        </div>

        {/* Disclaimer - Small */}
        <div className="mb-3 text-center">
          <p className="text-[11px] leading-relaxed text-neutral-400">
            All recommendations are grounded in verified public real estate data.
          </p>
          <a
            href="https://darglobal.co.uk"
            target="_blank"
            rel="noopener noreferrer"
            class="mt-0.5 inline-block text-[11px] text-white underline underline-offset-4 hover:text-blue-400 transition"
          >
            Learn more about DarGlobal & Wasalt portfolios.
          </a>
        </div>

        {/* Primary Action Button */}
        <button
          onClick={handleStart}
          className="w-full rounded-full bg-blue-600 py-2.5 font-semibold text-white text-sm transition hover:bg-blue-500 mb-2.5 cursor-pointer shadow-lg shadow-blue-600/25 active:scale-[0.98]"
        >
          Start chatting
        </button>

        {/* Maybe later */}
        <div className="text-center">
          <button
            onClick={onMaybeLater}
            className="text-xs text-neutral-400 hover:text-white transition cursor-pointer"
          >
            Maybe later
          </button>
        </div>
      </div>
    </div>
  );
};
