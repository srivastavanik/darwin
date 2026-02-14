"use client";

import { useCallback, useEffect, useState } from "react";
import {
  cancelGame,
  getApiConfig,
  listGames,
  startGame,
  toWebSocketUrl,
  type ApiGameSummary,
} from "@/lib/api";
import { useGameState } from "@/hooks/useGameState";

export function useGameController() {
  const { activeGameId, setActiveGameId } = useGameState();
  const [wsBaseUrl, setWsBaseUrl] = useState<string>(toWebSocketUrl(process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8765"));
  const [wsToken] = useState<string | null>(process.env.NEXT_PUBLIC_WS_TOKEN || null);
  const [games, setGames] = useState<ApiGameSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshGames = useCallback(async () => {
    try {
      const nextGames = await listGames();
      setGames(nextGames);
      const running = nextGames.find((g) => g.status === "running" || g.status === "queued");
      if (running) {
        setActiveGameId(running.game_id);
        return;
      }
      if (!activeGameId) return;
      const active = nextGames.find((g) => g.game_id === activeGameId);
      if (!active) {
        setActiveGameId(null);
        return;
      }
      if (active.status === "failed") {
        setError(active.error || "Game failed.");
        setActiveGameId(null);
        return;
      }
      if (active.status === "completed" || active.status === "cancelled") {
        setActiveGameId(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch games.");
    }
  }, [activeGameId, setActiveGameId]);

  useEffect(() => {
    const load = async () => {
      try {
        const cfg = await getApiConfig();
        setWsBaseUrl(toWebSocketUrl(cfg.ws_url));
      } catch {
        // Keep default WS base.
      }
      await refreshGames();
    };
    void load();
  }, [refreshGames]);

  useEffect(() => {
    const timer = setInterval(() => {
      void refreshGames();
    }, 2000);
    return () => clearInterval(timer);
  }, [refreshGames]);

  const handleStart = useCallback(async (mode: "full" | "quick") => {
    setLoading(true);
    setError(null);
    try {
      const started = await startGame(mode, false);
      setActiveGameId(started.game_id);
      await refreshGames();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start game.");
    } finally {
      setLoading(false);
    }
  }, [refreshGames, setActiveGameId]);

  const handleCancel = useCallback(async (gameId: string) => {
    setLoading(true);
    setError(null);
    try {
      await cancelGame(gameId);
      await refreshGames();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to cancel game.");
    } finally {
      setLoading(false);
    }
  }, [refreshGames]);

  return {
    wsBaseUrl,
    wsToken,
    games,
    loading,
    error,
    refreshGames,
    handleStart,
    handleCancel,
  };
}

