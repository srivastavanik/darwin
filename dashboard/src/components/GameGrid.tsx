"use client";

import { useRef, useEffect, useCallback, useState } from "react";
import { useGameState } from "@/hooks/useGameState";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TIER_SIZES } from "@/lib/colors";
import type { AgentState } from "@/lib/types";

const DEFAULT_CELL_SIZE = 72;
const MIN_CELL_SIZE = 42;
const MAX_CELL_SIZE = 80;
const PADDING = 32;
const LABEL_HEIGHT = 16;

export function GameGrid() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const {
    currentRound,
    rounds,
    agents,
    gridSize,
    showAdjacencyLines,
    showGhostOutlines,
    setSelectedAgent,
  } = useGameState();
  const [cellSize, setCellSize] = useState(DEFAULT_CELL_SIZE);

  const roundData = currentRound > 0 ? rounds[currentRound - 1] : null;

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const recalc = () => {
      const bounds = el.getBoundingClientRect();
      const availableByWidth = bounds.width - PADDING * 2 - 8;
      const availableByHeight = bounds.height - PADDING * 2 - 16;
      const maxCell = Math.floor(Math.min(availableByWidth, availableByHeight) / gridSize);
      const next = Math.max(
        MIN_CELL_SIZE,
        Math.min(MAX_CELL_SIZE, Math.min(DEFAULT_CELL_SIZE, maxCell)),
      );
      if (Number.isFinite(next) && next > 0) {
        setCellSize(next);
      }
    };

    recalc();
    const observer = new ResizeObserver(recalc);
    observer.observe(el);
    return () => observer.disconnect();
  }, [gridSize]);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const totalSize = gridSize * cellSize + PADDING * 2;
    canvas.width = totalSize;
    canvas.height = totalSize;

    // White background
    ctx.fillStyle = "#FFFFFF";
    ctx.fillRect(0, 0, totalSize, totalSize);

    // Grid lines
    ctx.strokeStyle = "rgba(17, 17, 17, 0.35)";
    ctx.lineWidth = 1;
    for (let i = 0; i <= gridSize; i++) {
      const x = PADDING + i * cellSize;
      ctx.beginPath();
      ctx.moveTo(x, PADDING);
      ctx.lineTo(x, PADDING + gridSize * cellSize);
      ctx.stroke();

      const y = PADDING + i * cellSize;
      ctx.beginPath();
      ctx.moveTo(PADDING, y);
      ctx.lineTo(PADDING + gridSize * cellSize, y);
      ctx.stroke();
    }

    // Row/col labels
    ctx.fillStyle = "#52525B";
    ctx.font = "11px Inter, sans-serif";
    ctx.textAlign = "center";
    for (let i = 0; i < gridSize; i++) {
      ctx.fillText(
        String(i),
        PADDING + i * cellSize + cellSize / 2,
        PADDING - 8
      );
      ctx.fillText(
        String(i),
        PADDING - 14,
        PADDING + i * cellSize + cellSize / 2 + 4
      );
    }

    // Get agent positions for current round
    const agentList = getAgentPositions(roundData, agents, gridSize);

    // Adjacency threat lines (between enemy agents)
    if (showAdjacencyLines) {
      for (let i = 0; i < agentList.length; i++) {
        for (let j = i + 1; j < agentList.length; j++) {
          const a = agentList[i];
          const b = agentList[j];
          if (!a.alive || !b.alive) continue;
          if (a.family === b.family) continue;

          const dr = Math.abs(a.position[0] - b.position[0]);
          const dc = Math.abs(a.position[1] - b.position[1]);
          if (dr <= 1 && dc <= 1 && (dr + dc > 0)) {
            const ax = PADDING + a.position[1] * cellSize + cellSize / 2;
            const ay = PADDING + a.position[0] * cellSize + cellSize / 2;
            const bx = PADDING + b.position[1] * cellSize + cellSize / 2;
            const by = PADDING + b.position[0] * cellSize + cellSize / 2;

            ctx.strokeStyle = "rgba(220, 38, 38, 0.2)";
            ctx.lineWidth = 1;
            ctx.setLineDash([4, 4]);
            ctx.beginPath();
            ctx.moveTo(ax, ay);
            ctx.lineTo(bx, by);
            ctx.stroke();
            ctx.setLineDash([]);
          }
        }
      }
    }

    // Draw agents
    for (const agent of agentList) {
      const cx = PADDING + agent.position[1] * cellSize + cellSize / 2;
      const cy = PADDING + agent.position[0] * cellSize + cellSize / 2;
      const size = TIER_SIZES[agent.tier] || 20;
      const half = size / 2;

      if (!agent.alive && showGhostOutlines) {
        // Ghost outline
        ctx.strokeStyle = `${agent.color}40`;
        ctx.lineWidth = 1.5;
        ctx.strokeRect(cx - half, cy - half, size, size);
      } else if (agent.alive) {
        // Filled square with border
        ctx.fillStyle = agent.color;
        ctx.fillRect(cx - half, cy - half, size, size);
        ctx.strokeStyle = "#00000020";
        ctx.lineWidth = 1;
        ctx.strokeRect(cx - half, cy - half, size, size);
      }

      // Name label
      ctx.fillStyle = agent.alive ? "rgba(0,0,0,0.6)" : "rgba(0,0,0,0.2)";
      ctx.font = `10px Inter, sans-serif`;
      ctx.textAlign = "center";
      ctx.fillText(agent.name, cx, cy + half + LABEL_HEIGHT);
    }

    // Elimination flashes
    if (roundData?.events) {
      for (const ev of roundData.events) {
        if (
          ev.type === "elimination" ||
          ev.type === "mutual_elimination"
        ) {
          const targetId =
            ev.type === "elimination"
              ? (ev.details.target as string)
              : ev.agent_id;
          const target = agentList.find((a) => a.id === targetId);
          if (target) {
            const cx =
              PADDING + target.position[1] * cellSize + cellSize / 2;
            const cy =
              PADDING + target.position[0] * cellSize + cellSize / 2;
            ctx.fillStyle = "rgba(220, 38, 38, 0.15)";
            ctx.fillRect(
              PADDING + target.position[1] * cellSize + 1,
              PADDING + target.position[0] * cellSize + 1,
              cellSize - 2,
              cellSize - 2
            );
          }
        }
      }
    }
  }, [
    currentRound,
    rounds,
    agents,
    gridSize,
    roundData,
    cellSize,
    showAdjacencyLines,
    showGhostOutlines,
  ]);

  useEffect(() => {
    draw();
  }, [draw]);

  const handleCanvasClick = () => {
    const source = currentRound > 0 && roundData?.grid?.agents?.length
      ? roundData.grid.agents
      : Object.values(agents);
    const alive = source.find((a) => a.alive);
    if (alive) {
      setSelectedAgent(alive.id);
    }
  };

  return (
    <Card className="h-full">
      <CardHeader className="py-3 px-4">
        <CardTitle className="text-sm font-medium">Grid</CardTitle>
      </CardHeader>
      <CardContent className="p-2 h-full min-h-0">
        <div ref={containerRef} className="h-full w-full flex items-center justify-center overflow-hidden">
          <canvas
            ref={canvasRef}
            className="max-w-full max-h-full"
            style={{ imageRendering: "crisp-edges" }}
            onClick={handleCanvasClick}
          />
        </div>
      </CardContent>
    </Card>
  );
}

function getAgentPositions(
  roundData: ReturnType<typeof useGameState.getState>["rounds"][0] | null,
  agents: Record<string, AgentState>,
  gridSize: number,
): AgentState[] {
  const source =
    roundData?.grid?.agents && roundData.grid.agents.length > 0
      ? roundData.grid.agents
      : Object.values(agents);

  return source.map((agent) => ({
    ...agent,
    position: normalizePosition(agent.position, gridSize),
  }));
}

function normalizePosition(
  pos: AgentState["position"] | undefined,
  gridSize: number,
): [number, number] {
  if (
    Array.isArray(pos) &&
    pos.length === 2 &&
    Number.isFinite(pos[0]) &&
    Number.isFinite(pos[1])
  ) {
    const row = Math.max(0, Math.min(gridSize - 1, Math.floor(pos[0])));
    const col = Math.max(0, Math.min(gridSize - 1, Math.floor(pos[1])));
    return [row, col];
  }
  return [0, 0];
}
