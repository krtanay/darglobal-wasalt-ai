"use client";

import React from "react";
import { MessageCircle, Smile } from "lucide-react";
import { cn } from "@/lib/utils";

export interface ModalCardProps {
  isOpen?: boolean;
  onStartChatting?: () => void;
  onMaybeLater?: () => void;
  className?: string;
}

export const ModalCard: React.FC<ModalCardProps> = ({
  isOpen = true,
  onStartChatting,
  onMaybeLater,
  className,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4">
      <div
        className={cn(
          "w-full max-w-md rounded-[2.5rem] bg-neutral-900 border border-neutral-800/80 p-8 shadow-2xl text-white",
          className
        )}
      >
        {/* Header */}
        <div className="mb-8 text-center border-b border-neutral-800 pb-5">
          <h1 className="text-3xl font-semibold leading-tight text-white tracking-tight">
            You're invited to try
            <br />
            DarGlobal × Wasalt AI
          </h1>
        </div>

        {/* Features */}
        <div className="mb-8 space-y-6">
          {/* Feature 1: Natural Conversations */}
          <div className="flex items-start gap-4">
            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-blue-600 shadow-md shadow-blue-600/30">
              <MessageCircle className="h-7 w-7 text-white" />
            </div>
            <div className="pt-1">
              <h3 className="mb-1 text-lg font-semibold text-white">
                Natural Conversations
              </h3>
              <p className="text-sm text-neutral-400 leading-relaxed">
                Real-time responses with verified property pricing and specs.
              </p>
            </div>
          </div>

          {/* Feature 2: Curated Portfolios */}
          <div className="flex items-start gap-4">
            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-blue-600 shadow-md shadow-blue-600/30">
              <Smile className="h-7 w-7 text-white" />
            </div>
            <div className="pt-1">
              <h3 className="mb-1 text-lg font-semibold text-white">
                Curated Portfolios
              </h3>
              <p className="text-sm text-neutral-400 leading-relaxed">
                DarGlobal branded icons & Wasalt REGA Saudi master developments.
              </p>
            </div>
          </div>
        </div>

        {/* Divider */}
        <div className="mb-6 h-px bg-neutral-800" />

        {/* Disclaimer */}
        <div className="mb-6 text-center">
          <p className="text-sm leading-relaxed text-neutral-400">
            AI Advisor may make mistakes. Access
            <br />
            and limits are subject to change.
          </p>
          <a
            href="https://darglobal.co.uk"
            target="_blank"
            rel="noopener noreferrer"
            className="mt-2 inline-block text-sm text-white underline underline-offset-4 hover:text-blue-400 transition"
          >
            Learn more about DarGlobal & Wasalt.
          </a>
        </div>

        {/* Primary Action Button */}
        <button
          onClick={onStartChatting}
          className="w-full rounded-full bg-blue-600 py-4 font-semibold text-white text-base transition hover:bg-blue-500 mb-4 cursor-pointer shadow-lg shadow-blue-600/25 active:scale-[0.99]"
        >
          Start chatting
        </button>

        {/* Maybe later */}
        <div className="text-center">
          <button
            onClick={onMaybeLater}
            className="text-sm text-neutral-400 hover:text-white transition cursor-pointer"
          >
            Maybe later
          </button>
        </div>
      </div>
    </div>
  );
};
