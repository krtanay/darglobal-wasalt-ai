"use client";

import { useEffect, useState } from "react";

export interface TypewriterOptions {
  typeMs?: number;
  deleteMs?: number;
  holdMs?: number;
  gapMs?: number;
  enabled?: boolean;
}

export function useTypewriter(
  phrases: string[],
  {
    typeMs = 45,
    deleteMs = 15,
    holdMs = 3200,
    gapMs = 800,
    enabled = true,
  }: TypewriterOptions = {}
) {
  const [index, setIndex] = useState(0);
  const [text, setText] = useState("");
  const [phase, setPhase] = useState<"typing" | "holding" | "deleting" | "gap">("typing");

  useEffect(() => {
    if (!enabled || !phrases || !phrases.length) return;

    const currentPhrase = phrases[index % phrases.length];
    let timer: any;

    if (phase === "typing") {
      if (text.length < currentPhrase.length) {
        timer = setTimeout(() => {
          setText(currentPhrase.slice(0, text.length + 1));
        }, typeMs);
      } else {
        setPhase("holding");
      }
    } else if (phase === "holding") {
      timer = setTimeout(() => {
        setPhase("deleting");
      }, holdMs);
    } else if (phase === "deleting") {
      if (text.length > 0) {
        timer = setTimeout(() => {
          setText(text.slice(0, -1));
        }, deleteMs);
      } else {
        setPhase("gap");
      }
    } else if (phase === "gap") {
      timer = setTimeout(() => {
        setIndex((prev) => prev + 1);
        setPhase("typing");
      }, gapMs);
    }

    return () => clearTimeout(timer);
  }, [text, phase, index, phrases, enabled, typeMs, deleteMs, holdMs, gapMs]);

  return { text, phase };
}
