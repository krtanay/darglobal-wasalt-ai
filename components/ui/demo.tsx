"use client";

import React, { useState } from "react";
import { ModalCard } from "@/components/ui/modal-card";
import { AIChatCard, Message } from "@/components/ui/ai-chat-card";

export default function LuxuryRealEstateAdvisorDemo() {
  const [modalOpen, setModalOpen] = useState(true);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async (text: string) => {
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setIsLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
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
      {/* Screen 1: Modal Card */}
      <ModalCard
        isOpen={modalOpen}
        onStartChatting={() => setModalOpen(false)}
        onMaybeLater={() => setModalOpen(false)}
      />

      {/* Screen 2: AI Chat Card */}
      <AIChatCard
        title="New Chat"
        subtitle="How can I help you today?"
        greeting="Morning, Arihant!"
        prompt="What are we working on today? Press send to start a new conversation"
        messages={messages}
        isLoading={isLoading}
        onSend={handleSend}
        onReset={() => setMessages([])}
      />
    </div>
  );
}
