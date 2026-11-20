"use client";

import React, { useState } from "react";
import { LuxuryOnboardingModal } from "@/components/ui/luxury-onboarding-modal";
import { LuxuryAIChatCard } from "@/components/ui/luxury-chat-card";

export default function LuxuryRealEstateAdvisorDemo() {
  const [modalOpen, setModalOpen] = useState(true);
  const [activeFilter, setActiveFilter] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);

  const handleSend = async (text: string) => {
    // Optimistically update conversation
    setMessages((prev) => [...prev, { role: "user", content: text }]);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          source_filter: activeFilter || null,
          api_key: apiKey || null,
        }),
      });
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.reply || "No response received." },
      ]);
    } catch (err) {
      console.error("Chat error:", err);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 p-4 sm:p-8 flex flex-col items-center justify-center">
      {/* Screen 1: Executive Onboarding Modal */}
      <LuxuryOnboardingModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        initialKey={apiKey}
        onConnectKey={(key) => {
          setApiKey(key);
          setModalOpen(false);
        }}
      />

      {/* Screen 2: Interactive Real Estate Advisory Chat Card */}
      <div className="w-full max-w-lg">
        <LuxuryAIChatCard
          activeSourceFilter={activeFilter}
          onFilterChange={(f) => setActiveFilter(f)}
          onSend={handleSend}
          onReset={() => setMessages([])}
          className="min-h-[560px]"
        />
      </div>
    </div>
  );
}
