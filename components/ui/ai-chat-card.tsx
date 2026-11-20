"use client";

import * as React from "react";
import { ArrowUp, Building2, RefreshCw, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { useTypewriter } from "@/components/ui/ai-chat-card-utils/use-typewriter";

export interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: any[];
}

export interface AIChatCardProps {
  title?: string;
  subtitle?: string;
  greeting?: string;
  prompt?: string;
  prompts?: string[];
  autoType?: boolean;
  placeholder?: string;
  onSend?: (message: string) => void;
  onReset?: () => void;
  messages?: Message[];
  isLoading?: boolean;
  className?: string;
}

const DEFAULT_PROMPTS = [
  "Show me luxury branded residences in Dubai by DarGlobal",
  "What luxury family villas are available in Riyadh on Wasalt under 4M SAR?",
  "Tell me about the Tierra Viva Lamborghini villas in Spain and their prices",
  "Compare DarGlobal international projects with Wasalt Saudi master developments",
];

export function AIChatCard({
  title = "Property Advisor",
  subtitle = "DarGlobal International × Wasalt Saudi Arabia",
  greeting = "Welcome to DarGlobal × Wasalt AI",
  prompt = "How can I help you find your dream property today?",
  prompts = DEFAULT_PROMPTS,
  autoType = true,
  placeholder = "Ask about branded villas, pricing, or Saudi masterplans...",
  onSend,
  onReset,
  messages = [],
  isLoading = false,
  className,
}: AIChatCardProps) {
  const rootRef = React.useRef<HTMLDivElement>(null);
  const textareaRef = React.useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  const [userActive, setUserActive] = React.useState(false);
  const [userMessage, setUserMessage] = React.useState("");
  const [isRotating, setIsRotating] = React.useState(false);

  const { text: typedMessage } = useTypewriter(prompts, {
    typeMs: 45,
    deleteMs: 15,
    holdMs: 3200,
    gapMs: 800,
    enabled: autoType && !userActive && messages.length === 0,
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
      handleSend();
    }
  };

  const handleSend = () => {
    const textToSend = userActive ? userMessage.trim() : typedMessage.trim();
    if (textToSend) {
      onSend?.(textToSend);
      setUserMessage("");
      setUserActive(false);
    }
  };

  const handleResetClick = () => {
    setIsRotating(true);
    setTimeout(() => setIsRotating(false), 600);
    setUserMessage("");
    setUserActive(false);
    onReset?.();
  };

  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div
      ref={rootRef}
      className={cn(
        "flex w-full max-w-md flex-col rounded-[28px] border border-neutral-800 bg-[#121212]",
        "p-5 shadow-2xl text-white min-h-[580px] justify-between",
        className
      )}
    >
      {/* Top Header */}
      <div className="flex items-center justify-between border-b border-neutral-800/80 pb-4">
        <div>
          <h2 className="text-lg font-semibold text-white tracking-tight">{title}</h2>
          <p className="text-xs text-neutral-400 mt-0.5">{subtitle}</p>
        </div>
        <button
          onClick={handleResetClick}
          aria-label="Reset chat"
          className="flex h-8 w-8 items-center justify-center rounded-full border border-neutral-800 bg-neutral-900 text-neutral-400 hover:text-white transition cursor-pointer"
        >
          <RefreshCw className={cn("h-4 w-4 transition-transform duration-500", isRotating && "rotate-180")} />
        </button>
      </div>

      {/* Main Body */}
      <div className="flex-1 flex flex-col justify-center py-6 overflow-y-auto max-h-[380px]">
        {messages.length === 0 ? (
          /* Empty State with Chatbot Logo & Welcoming Prompt */
          <div className="text-center my-auto">
            {/* Chatbot Logo */}
            <div className="relative flex h-14 w-14 items-center justify-center rounded-2xl bg-neutral-800 border border-neutral-700/80 mx-auto mb-4 shadow-lg shadow-black/50">
              <Building2 className="h-7 w-7 text-white" />
              <div className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-blue-600 text-[9px] font-bold">
                <Sparkles className="h-2.5 w-2.5 text-white" />
              </div>
            </div>

            <h3 className="text-xl sm:text-2xl font-semibold text-white tracking-tight">
              {greeting}
            </h3>
            <p className="text-sm text-neutral-400 max-w-xs mx-auto mt-2 leading-relaxed">
              {prompt}
            </p>
            <p className="text-xs text-neutral-500 max-w-xs mx-auto mt-1">
              Inquire about branded villas in Dubai & Spain, or verified family homes in Riyadh & Jeddah.
            </p>
          </div>
        ) : (
          /* Active Conversation Stream */
          <div className="space-y-4 pr-1">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={cn(
                  "flex flex-col text-sm",
                  m.role === "user" ? "items-end" : "items-start"
                )}
              >
                <div
                  className={cn(
                    "rounded-2xl px-4 py-2.5 max-w-[85%] leading-relaxed",
                    m.role === "user"
                      ? "bg-neutral-800 text-white"
                      : "bg-neutral-900/90 border border-neutral-800 text-neutral-200"
                  )}
                >
                  <p className="whitespace-pre-wrap">{m.content}</p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex items-center space-x-1.5 text-xs text-neutral-400 pl-2">
                <span className="w-1.5 h-1.5 bg-neutral-400 rounded-full animate-bounce"></span>
                <span className="w-1.5 h-1.5 bg-neutral-400 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                <span className="w-1.5 h-1.5 bg-neutral-400 rounded-full animate-bounce [animation-delay:0.4s]"></span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Composer at Bottom */}
      <div className="rounded-2xl bg-neutral-900 border border-neutral-800 p-4">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => {
            setUserMessage(e.target.value);
            setUserActive(true);
          }}
          onFocus={takeOver}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          rows={2}
          className="w-full resize-none bg-transparent text-sm text-white placeholder-neutral-500 focus:outline-none"
        />

        <div className="flex items-center justify-end pt-3 border-t border-neutral-800/80 mt-1">
          <button
            type="button"
            onClick={handleSend}
            disabled={!message.trim()}
            className="flex h-8 w-8 items-center justify-center rounded-full bg-white text-black hover:bg-neutral-200 transition disabled:opacity-40 cursor-pointer"
            aria-label="Send message"
          >
            <ArrowUp className="h-4 w-4 stroke-[2.5]" />
          </button>
        </div>
      </div>
    </div>
  );
}
