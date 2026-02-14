"use client";

import { useEffect } from "react";
import { useGameState } from "@/hooks/useGameState";

export function useKeyboardShortcuts() {
  const {
    playing,
    setPlaying,
    stepBack,
    stepForward,
    setViewMode,
    viewMode,
    highlightsOnly,
    setHighlightsOnly,
    setSelectedAgent,
  } = useGameState();

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (
        event.target instanceof HTMLInputElement ||
        event.target instanceof HTMLTextAreaElement ||
        event.target instanceof HTMLSelectElement
      ) {
        return;
      }

      if (event.code === "Space") {
        event.preventDefault();
        setPlaying(!playing);
        return;
      }
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        stepBack();
        return;
      }
      if (event.key === "ArrowRight") {
        event.preventDefault();
        stepForward();
        return;
      }
      if (event.key.toLowerCase() === "r") {
        setViewMode(viewMode === "board" ? "relationships" : "board");
        return;
      }
      if (event.key.toLowerCase() === "h") {
        setHighlightsOnly(!highlightsOnly);
        return;
      }
      if (event.key === "Escape") {
        setSelectedAgent(null);
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [
    highlightsOnly,
    playing,
    setHighlightsOnly,
    setPlaying,
    setSelectedAgent,
    setViewMode,
    stepBack,
    stepForward,
    viewMode,
  ]);
}

