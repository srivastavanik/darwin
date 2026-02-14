"use client";

import { useMemo } from "react";
import { useGameState } from "@/hooks/useGameState";

export function CompareAgentsModal({
  open,
  leftId,
  rightId,
  onClose,
}: {
  open: boolean;
  leftId: string;
  rightId: string;
  onClose: () => void;
}) {
  const { rounds, agents } = useGameState();
  const rows = useMemo(() => {
    return rounds.map((r) => ({
      round: r.round,
      leftThought: r.thoughts?.[leftId] || "",
      rightThought: r.thoughts?.[rightId] || "",
    }));
  }, [leftId, rightId, rounds]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/35 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-background border border-black/20 w-full max-w-[1200px] h-[80vh] p-3 overflow-auto" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm font-medium">Compare Agents</div>
          <button className="text-xs px-2 py-1 border border-black/20" onClick={onClose}>Close</button>
        </div>
        <div className="grid grid-cols-2 gap-2 text-xs mb-2">
          <div className="font-medium">{agents[leftId]?.name || leftId}</div>
          <div className="font-medium">{agents[rightId]?.name || rightId}</div>
        </div>
        <div className="space-y-2">
          {rows.map((r) => (
            <div key={r.round} className="border border-black/10">
              <div className="text-[11px] px-2 py-1 bg-zinc-50 border-b border-black/10">Round {r.round}</div>
              <div className="grid grid-cols-2 gap-2 p-2 text-xs">
                <div className="border border-black/10 p-2 whitespace-pre-wrap">{r.leftThought || "—"}</div>
                <div className="border border-black/10 p-2 whitespace-pre-wrap">{r.rightThought || "—"}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

