"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { usePathname } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { ApiGameSummary } from "@/lib/api";
import type { WebSocketStatus } from "@/hooks/useWebSocket";
import { useGameState } from "@/hooks/useGameState";

const STATUS_LABEL: Record<WebSocketStatus | "replay" | "idle", string> = {
  connecting: "Connecting",
  connected: "Live",
  reconnecting: "Reconnecting",
  disconnected: "Disconnected",
  idle: "Idle",
  replay: "Replay",
};

const STATUS_CLASS: Record<WebSocketStatus | "replay" | "idle", string> = {
  connecting: "bg-zinc-100 text-zinc-700 border-zinc-200",
  connected: "bg-black text-white border-black",
  reconnecting: "bg-amber-100 text-amber-800 border-amber-200",
  disconnected: "bg-red-100 text-red-700 border-red-200",
  idle: "bg-zinc-100 text-zinc-600 border-zinc-200",
  replay: "bg-blue-100 text-blue-800 border-blue-200",
};

function GameElapsedTimer({ running }: { running: boolean }) {
  const [elapsed, setElapsed] = useState(0);
  const startRef = useRef<number | null>(null);

  useEffect(() => {
    if (!running) {
      startRef.current = null;
      setElapsed(0);
      return;
    }
    if (startRef.current === null) {
      startRef.current = Date.now();
    }
    const tick = setInterval(() => {
      if (startRef.current) setElapsed(Math.floor((Date.now() - startRef.current) / 1000));
    }, 1000);
    return () => clearInterval(tick);
  }, [running]);

  if (!running || elapsed === 0) return null;

  const mins = Math.floor(elapsed / 60);
  const secs = elapsed % 60;
  return <span className="tabular-nums font-mono">{mins}:{secs.toString().padStart(2, "0")}</span>;
}

interface AppTopBarProps {
  status?: WebSocketStatus | "replay" | "idle";
  games?: ApiGameSummary[];
  onSelectGame?: (gameId: string | null) => void;
}

export function AppTopBar({ status = "idle", games = [], onSelectGame }: AppTopBarProps) {
  const pathname = usePathname();
  const {
    currentRound,
    rounds,
    agents,
    gameOver,
    playing,
    playbackSpeed,
    activeGameId,
    streamingPhase,
    showAdjacencyLines,
    showGhostOutlines,
    setShowAdjacencyLines,
    setShowGhostOutlines,
    setCurrentRound,
    setPlaying,
    stepBack,
    stepForward,
    setPlaybackSpeed,
  } = useGameState();

  const eliminationRounds = useMemo(() => {
    const set = new Set<number>();
    for (const r of rounds) {
      if ((r.events || []).some((e) => e.type === "elimination" || e.type === "mutual_elimination")) {
        set.add(r.round);
      }
    }
    return Array.from(set);
  }, [rounds]);

  const aliveCount = currentRound > 0 && rounds[currentRound - 1]
    ? rounds[currentRound - 1].alive_count
    : Object.keys(agents).length;
  const totalAgents = Object.keys(agents).length || 12;
  const maxRound = rounds.length > 0 ? rounds.length : 1;
  const roundElapsedMs = currentRound > 0 && rounds[currentRound - 1]
    ? rounds[currentRound - 1].round_elapsed_ms
    : null;

  const toggleFullscreen = async () => {
    if (!document.fullscreenElement) {
      await document.documentElement.requestFullscreen();
    } else {
      await document.exitFullscreen();
    }
  };

  return (
    <div className="border-b border-black/10 bg-card px-4 py-2.5">
      <div className="grid grid-cols-3 gap-3 items-start">
        <div className="min-w-0 flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <div className="text-base tracking-tight font-medium">MARKOV</div>
            <Badge className={`text-[10px] px-2 py-0.5 border ${STATUS_CLASS[status]}`}>
              {STATUS_LABEL[status]}
            </Badge>
            {gameOver && <Badge variant="outline" className="text-[10px]">Complete</Badge>}
          </div>
          <div className="text-xs text-muted-foreground flex items-center gap-3">
            <span>Round {currentRound} / {maxRound || "?"}</span>
            <span>{aliveCount}/{totalAgents} alive</span>
            {roundElapsedMs != null && <span>round: {(roundElapsedMs / 1000).toFixed(1)}s</span>}
            <GameElapsedTimer running={status === "connected" && !gameOver && (rounds.length > 0 || !!streamingPhase)} />
            {activeGameId && <span className="truncate">Game: {activeGameId}</span>}
          </div>
          <div className="flex items-center gap-2 text-xs">
            <ModeLink href="/" active={pathname === "/" || pathname.startsWith("/live")}>Live</ModeLink>
            <ModeLink href="/investigation" active={pathname.startsWith("/investigation")}>Investigation</ModeLink>
            <ModeLink href="/analysis" active={pathname.startsWith("/analysis")}>Analysis</ModeLink>
            <ModeLink href="/series" active={pathname.startsWith("/series")}>Series</ModeLink>
            <ModeLink href="/replay" active={pathname.startsWith("/replay")}>Replay</ModeLink>
          </div>
        </div>

        <div className="min-w-0 flex flex-col gap-1">
          <div className="flex items-center justify-center gap-1.5">
            <Button variant="outline" size="sm" onClick={stepBack} disabled={currentRound <= 1}>Back</Button>
            <Button variant={playing ? "default" : "outline"} size="sm" onClick={() => setPlaying(!playing)}>
              {playing ? "Pause" : "Play"}
            </Button>
            <Button variant="outline" size="sm" onClick={stepForward} disabled={currentRound >= rounds.length}>Fwd</Button>
            <select
              className="h-8 px-2 text-xs border rounded-md bg-white border-black/20"
              value={playbackSpeed}
              onChange={(e) => setPlaybackSpeed(Number(e.target.value) as 1 | 2 | 5 | 10)}
            >
              <option value={1}>1x</option>
              <option value={2}>2x</option>
              <option value={5}>5x</option>
              <option value={10}>10x</option>
            </select>
          </div>
          <div className="relative px-1 pt-1">
            <input
              type="range"
              className="w-full"
              min={1}
              max={Math.max(maxRound, 1)}
              value={Math.min(Math.max(currentRound, 1), Math.max(maxRound, 1))}
              onChange={(e) => setCurrentRound(Number(e.target.value))}
              disabled={rounds.length === 0}
            />
            <div className="absolute inset-x-1 top-0 h-3 pointer-events-none">
              {eliminationRounds.map((r) => (
                <span
                  key={r}
                  className="absolute top-0 h-2 w-px bg-red-500"
                  style={{ left: `${(r / Math.max(maxRound, 1)) * 100}%` }}
                />
              ))}
            </div>
          </div>
        </div>

        <div className="min-w-0 flex items-center justify-end gap-2">
          <select
            className="h-8 px-2 text-xs border rounded-md bg-white border-black/20 max-w-[220px]"
            value={activeGameId ?? ""}
            onChange={(e) => onSelectGame?.(e.target.value || null)}
          >
            <option value="">Select game</option>
            {games.map((g) => (
              <option key={g.game_id} value={g.game_id}>
                {g.game_id} ({g.status})
              </option>
            ))}
          </select>
          <label className="text-xs flex items-center gap-1">
            <input
              type="checkbox"
              checked={showAdjacencyLines}
              onChange={(e) => setShowAdjacencyLines(e.target.checked)}
            />
            Lines
          </label>
          <label className="text-xs flex items-center gap-1">
            <input
              type="checkbox"
              checked={showGhostOutlines}
              onChange={(e) => setShowGhostOutlines(e.target.checked)}
            />
            Ghosts
          </label>
          <Button variant="outline" size="sm" onClick={toggleFullscreen}>Fullscreen</Button>
        </div>
      </div>
    </div>
  );
}

function ModeLink({
  href,
  active,
  children,
}: {
  href: string;
  active: boolean;
  children: React.ReactNode;
}) {
  return (
    <Link
      href={href}
      className={active ? "font-medium text-black underline underline-offset-2" : "text-black/70 hover:text-black"}
    >
      {children}
    </Link>
  );
}

