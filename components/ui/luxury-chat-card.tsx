"use client";

import * as React from "react";
import { motion, useInView } from "motion/react";
import { ArrowUp, Building2, Sparkles, RefreshCw } from "lucide-react";

import { cn } from "@/lib/utils";
import { useTypewriter } from "@/components/ui/ai-chat-card-utils/use-typewriter";

export interface LuxuryAIChatCardProps {
  title?: string;
  subtitle?: string;
  greeting?: string;
  prompt?: string;
  /** Curated luxury real estate prompts that auto-type in a loop */
  prompts?: string[];
  autoType?: boolean;
  placeholder?: string;
  icon?: React.ReactNode;
  activeSourceFilter?: string;
  onFilterChange?: (filter: string) => void;
  onSend?: (message: string) => void;
  onReset?: () => void;
  className?: string;
}

const LUXURY_REAL_ESTATE_PROMPTS = [
  "Show me luxury branded residences in Dubai by DarGlobal",
  "What luxury family villas are available in Riyadh on Wasalt under 4M SAR?",
  "Tell me about the Tierra Viva Lamborghini villas in Spain and their prices",
  "Compare DarGlobal international projects with Wasalt Saudi master developments",
  "Which properties feature private infinity pools and branded designer interiors?",
];

export function LuxuryAIChatCard({
  title = "DarGlobal × Wasalt Advisor",
  subtitle = "Bespoke Real Estate & PropTech Intelligence",
  greeting = "Welcome to Your Private Advisory",
  prompt = "Inquire about branded residences, verified pricing, or Saudi master developments.",
  prompts = LUXURY_REAL_ESTATE_PROMPTS,
  autoType = true,
  placeholder = "Ask about villas, penthouses, pricing, or follow-ups like 'what amenities does it offer?'...",
  icon,
  activeSourceFilter = "",
  onFilterChange,
  onSend,
  onReset,
  className,
}: LuxuryAIChatCardProps) {
  const rootRef = React.useRef<HTMLDivElement>(null);
  const textareaRef = React.useRef<HTMLTextAreaElement>(null);
  const inView = useInView(rootRef, { margin: "-10% 0px" });

  const [userActive, setUserActive] = React.useState(false);
  const [userMessage, setUserMessage] = React.useState("");
  const [spins, setSpins] = React.useState(0);

  const { text: typedMessage, phase } = useTypewriter(prompts, {
    typeMs: 42,
    deleteMs: 14,
    holdMs: 3200,
    gapMs: 800,
    enabled: autoType && inView && !userActive,
  });

  const message = userActive || !autoType ? userMessage : typedMessage;

  const takeOver = () => {
    if (userActive || !autoType) return;
    setUserMessage(typedMessage);
    setUserActive(true);
    requestAnimationFrame(() => textareaRef.current?.focus());
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (message.trim()) {
        onSend?.(message.trim());
        setUserMessage("");
        setUserActive(false);
      }
    }
  };

  return (
    <div
      ref={rootRef}
      className={cn(
        "flex w-full flex-col rounded-[28px] border border-neutral-800 bg-neutral-950/95",
        "shadow-[0_15px_35px_-10px_rgba(0,0,0,0.7)] backdrop-blur-xl",
        "dark:border-amber-500/25 dark:shadow-[0_0_30px_-5px_rgba(212,175,55,0.15)]",
        className,
      )}
    >
      {/* Executive Header */}
      <div className="flex items-start justify-between gap-4 border-b border-neutral-800/80 px-6 pb-4 pt-5">
        <div className="flex items-center space-x-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-amber-400 via-amber-500 to-amber-700 shadow-md shadow-amber-500/20">
            <Building2 className="h-5 w-5 text-neutral-950" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="font-serif text-[15px] font-bold tracking-wide text-white">
                {title}
              </h3>
              <span className="rounded-full border border-amber-500/30 bg-amber-500/10 px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider text-amber-400">
                PRO RAG
              </span>
            </div>
            <p className="text-xs text-neutral-400">
              {subtitle}
            </p>
          </div>
        </div>

        {/* Refresh / Reset Conversation */}
        <motion.button
          type="button"
          onClick={() => {
            setSpins((count) => count + 1);
            setUserActive(false);
            setUserMessage("");
            onReset?.();
          }}
          whileTap={{ scale: 0.9 }}
          aria-label="Reset conversation"
          title="Start fresh conversation"
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl border border-neutral-800 bg-neutral-900 text-neutral-400 transition hover:border-amber-500/40 hover:text-white"
        >
          <motion.span
            animate={{ rotate: spins * 360 }}
            transition={{ type: "spring", bounce: 0.2, duration: 0.7 }}
            className="flex"
          >
            <RefreshCw className="h-3.5 w-3.5" />
          </motion.span>
        </motion.button>
      </div>

      {/* Scope Segmented Filter Bar */}
      <div className="flex items-center justify-between border-b border-neutral-800/60 bg-neutral-900/40 px-6 py-2 text-[11px]">
        <span className="text-neutral-400 font-medium">Portfolio:</span>
        <div className="flex items-center space-x-1.5">
          <button
            onClick={() => onFilterChange?.("")}
            className={cn(
              "rounded-lg px-2.5 py-1 font-semibold transition",
              !activeSourceFilter
                ? "border border-amber-500/40 bg-amber-500/20 text-amber-300"
                : "text-neutral-400 hover:text-neutral-200"
            )}
          >
            All Portfolios
          </button>
          <button
            onClick={() => onFilterChange?.("DarGlobal")}
            className={cn(
              "rounded-lg px-2.5 py-1 font-semibold transition",
              activeSourceFilter === "DarGlobal"
                ? "border border-amber-500/40 bg-amber-500/20 text-amber-300"
                : "text-neutral-400 hover:text-neutral-200"
            )}
          >
            DarGlobal (International)
          </button>
          <button
            onClick={() => onFilterChange?.("Wasalt")}
            className={cn(
              "rounded-lg px-2.5 py-1 font-semibold transition",
              activeSourceFilter === "Wasalt"
                ? "border border-amber-500/40 bg-amber-500/20 text-amber-300"
                : "text-neutral-400 hover:text-neutral-200"
            )}
          >
            Wasalt (Saudi)
          </button>
        </div>
      </div>

      {/* Hero Welcome / Empty State */}
      <div className="flex flex-1 flex-col items-center justify-center px-8 py-10 text-center">
        <motion.div
          animate={{ y: [0, -4, 0] }}
          transition={{ duration: 3.5, repeat: Infinity, ease: "easeInOut" }}
          className="flex h-12 w-12 items-center justify-center rounded-2xl border border-amber-500/30 bg-amber-500/10 shadow-lg shadow-amber-500/10"
        >
          {icon ?? <Sparkles className="h-6 w-6 text-amber-400" />}
        </motion.div>
        
        <motion.p
          initial={{ opacity: 0, y: 8 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.15, ease: "easeOut" }}
          className="mt-4 font-serif text-[18px] font-bold tracking-wide text-white"
        >
          {greeting}
        </motion.p>
        
        <motion.p
          initial={{ opacity: 0, y: 8 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.25, ease: "easeOut" }}
          className="mt-2 max-w-[280px] text-xs leading-relaxed text-neutral-400"
        >
          {prompt}
        </motion.p>
      </div>

      {/* Composer Input Bar */}
      <div className="px-6 pb-6">
        <div className="rounded-[20px] border border-neutral-800 bg-neutral-900/80 p-3.5 transition-colors focus-within:border-amber-500/50 focus-within:bg-neutral-900">
          {userActive || !autoType ? (
            <textarea
              ref={textareaRef}
              value={userMessage}
              onChange={(e) => setUserMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              rows={2}
              className="w-full resize-none bg-transparent text-xs leading-relaxed text-white outline-none placeholder:text-neutral-500"
            />
          ) : (
            <div
              onClick={takeOver}
              className="min-h-11 w-full cursor-text text-left text-xs leading-relaxed text-slate-200"
            >
              {message}
              <motion.span
                aria-hidden
                className="ml-1 inline-block h-3.5 w-[2px] bg-amber-400 align-middle"
                animate={{ opacity: [1, 1, 0, 0] }}
                transition={{
                  duration: 0.9,
                  repeat: Infinity,
                  times: [0, 0.5, 0.5, 1],
                }}
              />
              {!message ? (
                <span className="text-neutral-500">{placeholder}</span>
              ) : null}
            </div>
          )}

          {/* Action Row */}
          <div className="mt-2.5 flex items-center justify-between pt-1">
            <span className="text-[10px] text-neutral-500">
              Press <kbd className="rounded border border-neutral-700 bg-neutral-800 px-1 font-mono text-[9px] text-neutral-400">Enter ↵</kbd> to send
            </span>

            <motion.button
              type="button"
              onClick={() => {
                if (message.trim()) {
                  onSend?.(message.trim());
                  setUserMessage("");
                  setUserActive(false);
                }
              }}
              whileHover={{
                scale: 1.05,
                transition: { type: "spring", bounce: 0.5, duration: 0.3 },
              }}
              whileTap={{ scale: 0.92 }}
              animate={
                phase === "holding" && !userActive
                  ? { scale: [1, 1.1, 1] }
                  : { scale: 1 }
              }
              transition={{
                duration: 0.5,
                ease: "easeInOut",
                times: [0, 0.35, 1],
              }}
              aria-label="Send message"
              className="group flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 text-neutral-950 shadow-md shadow-amber-500/20 hover:from-amber-400 hover:to-amber-500"
            >
              <ArrowUp className="h-4 w-4 stroke-[2.5] transition-transform duration-200 group-hover:-translate-y-0.5" />
            </motion.button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LuxuryAIChatCard;
