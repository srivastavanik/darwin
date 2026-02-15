"use client";

import { useMemo } from "react";
import Image from "next/image";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useGameState } from "@/hooks/useGameState";

const PROVIDER_LOGOS: Record<string, string> = {
  anthropic: "/logos/anthropic.png",
  openai: "/logos/openai.webp",
  google: "/logos/google.png",
  xai: "/logos/xai.png",
};

interface KillEvent {
  round: number;
  type: "elimination" | "mutual_elimination";
  attackerName: string;
  attackerProvider: string;
  attackerAlive: boolean;
  targetName: string;
  targetProvider: string;
}

export function KillTimeline() {
  const { rounds, currentRound, agents } = useGameState();
  const visibleRounds = rounds.slice(0, currentRound);

  const kills = useMemo(() => {
    const events: KillEvent[] = [];
    for (const round of visibleRounds) {
      for (const ev of round.events || []) {
        if (ev.type === "elimination") {
          const targetId = ev.details.target as string;
          const target = agents[targetId];
          const attacker = agents[ev.agent_id];
          events.push({
            round: round.round,
            type: "elimination",
            attackerName: attacker?.name || ev.agent_id,
            attackerProvider: attacker?.provider || "",
            attackerAlive: attacker?.alive ?? true,
            targetName: target?.name || targetId,
            targetProvider: target?.provider || "",
          });
        } else if (ev.type === "mutual_elimination") {
          const targetId = ev.details.target as string;
          const target = agents[targetId];
          const agent = agents[ev.agent_id];
          events.push({
            round: round.round,
            type: "mutual_elimination",
            attackerName: agent?.name || ev.agent_id,
            attackerProvider: agent?.provider || "",
            attackerAlive: false,
            targetName: target?.name || targetId,
            targetProvider: target?.provider || "",
          });
        }
      }
    }
    return events;
  }, [visibleRounds, agents]);

  return (
    <div className="h-full flex flex-col px-3 py-1.5">
      <div className="text-[10px] font-medium text-black/40 mb-1">Elimination Timeline</div>
      {kills.length === 0 ? (
        <div className="text-[10px] text-black/20 text-center flex-1 flex items-center justify-center">
          No eliminations yet
        </div>
      ) : (
        <div className="flex-1 flex items-center gap-3 overflow-x-auto">
          {kills.map((kill, i) => (
            <Tooltip key={i}>
              <TooltipTrigger asChild>
                <div className="flex items-center gap-1 shrink-0 cursor-default">
                  {/* Attacker */}
                  <div className="flex flex-col items-center">
                    <div className={`p-0.5 ${kill.attackerAlive ? "ring-1 ring-green-400" : "ring-1 ring-red-400"}`}>
                      {PROVIDER_LOGOS[kill.attackerProvider] ? (
                        <Image src={PROVIDER_LOGOS[kill.attackerProvider]} alt="" width={18} height={18} className="object-contain" />
                      ) : (
                        <div className="w-[18px] h-[18px] bg-black/10" />
                      )}
                    </div>
                    <span className="text-[8px] text-black/50 mt-0.5 max-w-[40px] truncate">{kill.attackerName}</span>
                  </div>

                  {/* Arrow */}
                  <div className="text-[10px] text-black/30 mx-0.5">
                    {kill.type === "mutual_elimination" ? "<->" : "->"}
                  </div>

                  {/* Target (always dead) */}
                  <div className="flex flex-col items-center">
                    <div className="p-0.5 ring-1 ring-red-400 opacity-50">
                      {PROVIDER_LOGOS[kill.targetProvider] ? (
                        <Image src={PROVIDER_LOGOS[kill.targetProvider]} alt="" width={18} height={18} className="object-contain" />
                      ) : (
                        <div className="w-[18px] h-[18px] bg-black/10" />
                      )}
                    </div>
                    <span className="text-[8px] text-red-400/70 mt-0.5 max-w-[40px] truncate line-through">{kill.targetName}</span>
                  </div>

                  {/* Round badge */}
                  <span className="text-[8px] text-black/20 ml-0.5">R{kill.round}</span>
                </div>
              </TooltipTrigger>
              <TooltipContent side="top">
                <p className="text-xs">
                  R{kill.round}: {kill.attackerName}{" "}
                  {kill.type === "mutual_elimination" ? "and" : "ended"}{" "}
                  {kill.targetName}
                  {kill.type === "mutual_elimination" ? " destroyed each other" : ""}
                </p>
              </TooltipContent>
            </Tooltip>
          ))}
        </div>
      )}
    </div>
  );
}
