"use client";

import { useEffect, useRef } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { useGameState } from "@/hooks/useGameState";
import type { WebSocketStatus } from "@/hooks/useWebSocket";

const STATUS_LABEL: Record<WebSocketStatus | "replay", string> = {
  connecting: "Connecting",
  connected: "Live",
  reconnecting: "Reconnecting",
  disconnected: "Disconnected",
  replay: "Replay",
};

const STATUS_CLASS: Record<WebSocketStatus | "replay", string> = {
  connecting: "bg-gray-100 text-gray-700",
  connected: "bg-black text-white",
  reconnecting: "bg-amber-100 text-amber-800",
  disconnected: "bg-red-100 text-red-700",
  replay: "bg-blue-100 text-blue-800",
};

export function RoundControls({ status = "disconnected" }: { status?: WebSocketStatus | "replay" }) {
  const {
    currentRound,
    rounds,
    gameOver,
    winner,
    playing,
    speed,
    stepForward,
    stepBack,
    setPlaying,
    setSpeed,
    setCurrentRound,
  } = useGameState();

  const timerRef = useRef<ReturnType<typeof setInterval>>(undefined);

  useEffect(() => {
    if (playing && currentRound < rounds.length) {
      timerRef.current = setInterval(() => {
        const state = useGameState.getState();
        if (state.currentRound >= state.rounds.length) {
          state.setPlaying(false);
        } else {
          state.stepForward();
        }
      }, speed);
    }
    return () => clearInterval(timerRef.current);
  }, [playing, speed, currentRound, rounds.length]);

  const aliveCount =
    currentRound > 0 && rounds[currentRound - 1]
      ? rounds[currentRound - 1].alive_count
      : Object.keys(useGameState.getState().agents).length;

  const totalAgents = Object.keys(useGameState.getState().agents).length || 12;

  return (
    <div className="flex items-center justify-between px-6 py-3 border-b bg-white">
      <div className="flex items-center gap-3">
        <h1 className="text-lg font-semibold tracking-tight text-black">
          MARKOV
        </h1>
        <div className="flex items-center gap-2">
          <Link href="/" className="text-xs font-medium text-black underline-offset-2 hover:underline">
            Live
          </Link>
          <span className="text-muted-foreground text-xs">/</span>
          <Link href="/replay" className="text-xs font-medium text-black underline-offset-2 hover:underline">
            Replay
          </Link>
        </div>
        <span className={`text-[10px] px-2 py-0.5 rounded ${STATUS_CLASS[status]}`}>
          {STATUS_LABEL[status]}
        </span>
        <span className="text-sm text-muted-foreground">
          Round {currentRound} / {rounds.length || "..."}
        </span>
        <span className="text-sm text-muted-foreground">
          {aliveCount}/{totalAgents} alive
        </span>
        {gameOver && (
          <span className="text-sm font-medium text-black">
            {winner ? `Winner: ${winner}` : "Game Over"}
          </span>
        )}
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={stepBack}
          disabled={currentRound <= 1}
        >
          Step Back
        </Button>
        <Button
          variant={playing ? "default" : "outline"}
          size="sm"
          onClick={() => setPlaying(!playing)}
          disabled={currentRound >= rounds.length && !playing}
        >
          {playing ? "Pause" : "Play"}
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={stepForward}
          disabled={currentRound >= rounds.length}
        >
          Step Fwd
        </Button>
        <select
          className="h-8 px-2 text-xs border rounded-md bg-white"
          value={speed}
          onChange={(e) => setSpeed(Number(e.target.value))}
        >
          <option value={3000}>0.3x</option>
          <option value={2000}>0.5x</option>
          <option value={1000}>1x</option>
          <option value={500}>2x</option>
          <option value={200}>5x</option>
        </select>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setCurrentRound(1)}
          disabled={currentRound <= 1}
        >
          Reset
        </Button>
      </div>
    </div>
  );
}
