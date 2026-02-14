"use client";

import { useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { AgentBadge } from "./AgentBadge";
import { useGameState } from "@/hooks/useGameState";
import { getFamilyColor, TIER_LABELS } from "@/lib/colors";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { LineChart, Line, XAxis, YAxis, CartesianGrid } from "recharts";

export function AgentDetail() {
  const { selectedAgent, agents, rounds, currentRound, setSelectedAgent } =
    useGameState();

  const agent = selectedAgent ? agents[selectedAgent] : null;

  const visibleRounds = rounds.slice(0, currentRound);

  const { thoughts, messages, deceptionData, stats } = useMemo(() => {
    if (!selectedAgent) {
      return { thoughts: [], messages: [], deceptionData: [], stats: null };
    }

    const t: Array<{ round: number; text: string; analysis?: import("@/lib/types").AgentAnalysis }> = [];
    const m: Array<{ round: number; channel: string; recipient?: string; content: string }> = [];
    const d: Array<{ round: number; delta: number }> = [];
    let maliceCount = 0;
    let betrayalCount = 0;
    let totalRounds = 0;

    for (const round of visibleRounds) {
      const thought = round.thoughts?.[selectedAgent];
      const analysis = round.analysis?.[selectedAgent];

      if (thought) {
        t.push({ round: round.round, text: thought, analysis });
        totalRounds++;
      }

      if (analysis?.deception_delta !== undefined) {
        d.push({ round: round.round, delta: Math.round(analysis.deception_delta * 100) / 100 });
      }
      if (analysis?.malice?.elimination_planning) maliceCount++;
      if (analysis?.betrayal?.detected) betrayalCount++;

      // Collect messages sent by this agent
      for (const msg of round.messages?.broadcasts || []) {
        if (msg.sender === selectedAgent) {
          m.push({ round: round.round, channel: "broadcast", content: msg.content });
        }
      }
      for (const msg of round.messages?.direct_messages || []) {
        if (msg.sender === selectedAgent) {
          m.push({ round: round.round, channel: "dm", recipient: msg.recipient || "?", content: msg.content });
        }
      }
    }

    const avgDelta = d.length > 0 ? d.reduce((s, x) => s + x.delta, 0) / d.length : 0;
    return {
      thoughts: t,
      messages: m,
      deceptionData: d,
      stats: {
        totalRounds,
        avgDeception: avgDelta,
        maxDeception: d.length > 0 ? Math.max(...d.map((x) => x.delta)) : 0,
        maliceRate: totalRounds > 0 ? maliceCount / totalRounds : 0,
        betrayalCount,
      },
    };
  }, [selectedAgent, visibleRounds]);

  if (!agent || !selectedAgent) {
    return (
      <Card className="h-full">
        <CardContent className="flex items-center justify-center h-full">
          <p className="text-sm text-muted-foreground">
            Click an agent name to view their full profile
          </p>
        </CardContent>
      </Card>
    );
  }

  const color = getFamilyColor(agent.family);

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="py-3 px-4 shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AgentBadge
              name={agent.name}
              family={agent.family}
              color={color}
              tier={agent.tier}
              alive={agent.alive}
            />
            {!agent.alive && (
              <Badge variant="destructive" className="text-[10px]">
                Eliminated R{agent.eliminated_round}
              </Badge>
            )}
          </div>
          <Button variant="ghost" size="sm" onClick={() => setSelectedAgent(null)}>
            Close
          </Button>
        </div>
      </CardHeader>

      <CardContent className="flex-1 min-h-0 p-0">
        <ScrollArea className="h-full px-4 pb-4">
          {/* Stats summary */}
          {stats && (
            <div className="grid grid-cols-3 gap-2 mb-4">
              <StatBox label="Avg Deception" value={stats.avgDeception.toFixed(3)} />
              <StatBox label="Max Deception" value={stats.maxDeception.toFixed(3)} />
              <StatBox label="Malice Rate" value={`${(stats.maliceRate * 100).toFixed(0)}%`} />
            </div>
          )}

          {/* Per-agent deception chart */}
          {deceptionData.length > 0 && (
            <div className="mb-4">
              <p className="text-xs font-semibold text-muted-foreground mb-1">Deception Delta</p>
              <ChartContainer
                config={{
                  delta: { label: "Delta", color },
                }}
                className="h-[120px] w-full"
              >
                <LineChart data={deceptionData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.25)" />
                  <XAxis dataKey="round" tick={{ fontSize: 9 }} tickLine={false} axisLine={false} />
                  <YAxis domain={[0, 1]} tick={{ fontSize: 9 }} tickLine={false} axisLine={false} width={25} />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Line type="monotone" dataKey="delta" stroke={color} strokeWidth={2} dot={false} />
                </LineChart>
              </ChartContainer>
            </div>
          )}

          <Separator className="my-3" />

          {/* Thought history */}
          <p className="text-xs font-semibold text-muted-foreground mb-2">Thought History</p>
          {thoughts.map((t, i) => (
            <div key={i} className="mb-3">
              <div className="text-[10px] font-semibold text-muted-foreground mb-0.5">
                Round {t.round}
              </div>
              <div
                className="text-xs leading-relaxed text-gray-700 font-mono p-2 rounded bg-gray-50 whitespace-pre-wrap"
                style={{ borderLeft: `3px solid ${color}` }}
              >
                {t.text}
              </div>
            </div>
          ))}

          {thoughts.length === 0 && (
            <p className="text-xs text-muted-foreground">No thoughts recorded yet.</p>
          )}

          {/* Messages sent */}
          {messages.length > 0 && (
            <>
              <Separator className="my-3" />
              <p className="text-xs font-semibold text-muted-foreground mb-2">Messages Sent</p>
              {messages.map((m, i) => (
                <div key={i} className="mb-2 text-xs text-gray-600">
                  <span className="font-medium">R{m.round}</span>{" "}
                  [{m.channel}{m.recipient ? ` to ${m.recipient}` : ""}]: &ldquo;{m.content.slice(0, 200)}{m.content.length > 200 ? "..." : ""}&rdquo;
                </div>
              ))}
            </>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
}

function StatBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border px-2 py-1.5 text-center">
      <div className="text-[10px] text-muted-foreground">{label}</div>
      <div className="text-sm font-semibold">{value}</div>
    </div>
  );
}
