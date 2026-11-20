"use client";

import React, { useState } from "react";
import { ModalCard } from "@/components/ui/modal-card";
import { AIChatCard, Message } from "@/components/ui/ai-chat-card";

export default function LuxuryRealEstateAdvisorDemo() {
  const [modalOpen, setModalOpen] = useState(true);
  const [apiKey, setApiKey] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async (text: string) => {
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setIsLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          api_key: apiKey || null,
        }),
      });
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.reply || "No response received.",
          sources: data.sources || [],
        },
      ]);
    } catch (err) {
      console.error("Chat error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      {/* Screen 1: Compact Benefit-Driven Modal with API Key Input */}
      <ModalCard
        isOpen={modalOpen}
        initialKey={apiKey}
        onStartChatting={(key) => {
          if (key) setApiKey(key);
          setModalOpen(false);
        }}
        onMaybeLater={() => setModalOpen(false)}
      />

      {/* Screen 2: Real Estate AI Chat Card with Chatbot Logo & Welcome Hero */}
      <AIChatCard
        title="Property Advisor"
        subtitle="DarGlobal International × Wasalt Saudi Arabia"
        greeting="Welcome to DarGlobal × Wasalt AI"
        prompt="How can I help you find your dream property today?"
        messages={messages}
        isLoading={isLoading}
        onSend={handleSend}
        onReset={() => setMessages([])}
      />
    </div>
  );
}
