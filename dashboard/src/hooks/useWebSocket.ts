"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import { useGameState } from "./useGameState";
import type { GameInitData, RoundData, GameOverData } from "@/lib/types";

export type WebSocketStatus = "connecting" | "connected" | "reconnecting" | "disconnected";

export function useWebSocket(url: string = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8765") {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout>>(undefined);
  const [status, setStatus] = useState<WebSocketStatus>("connecting");
  const { initGame, pushRound, setGameOver } = useGameState();

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(url);
    wsRef.current = ws;
    setStatus("connecting");

    ws.onopen = () => {
      console.log("[WS] Connected to", url);
      setStatus("connected");
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === "game_init") {
          initGame(data as GameInitData);
        } else if (data.type === "round_update") {
          pushRound(data as RoundData);
        } else if (data.type === "game_over") {
          const go = data as GameOverData;
          setGameOver(go.winner, go.final_reflection);
        }
      } catch (e) {
        console.error("[WS] Failed to parse message:", e);
      }
    };

    ws.onclose = () => {
      console.log("[WS] Disconnected. Reconnecting in 3s...");
      setStatus("reconnecting");
      reconnectTimer.current = setTimeout(connect, 3000);
    };

    ws.onerror = (err) => {
      console.error("[WS] Error:", err);
      setStatus("disconnected");
      ws.close();
    };
  }, [url, initGame, pushRound, setGameOver]);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
      setStatus("disconnected");
    };
  }, [connect]);

  return { wsRef, status };
}
