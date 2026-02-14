"use client";

import { useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useGameState } from "@/hooks/useGameState";

export function FamilyDetail() {
  const { families, agents, rounds, selectedFamily, setSelectedFamily } = useGameState();
  const [selectedRound, setSelectedRound] = useState<number>(1);
  const familyName = selectedFamily || families[0]?.name || "";

  const transcript = useMemo(() => {
    const round = rounds.find((r) => r.round === selectedRound);
    if (!round) return [];
    const familyDisc = (round.messages?.family_discussions || []).find((f) => f.family === familyName);
    return familyDisc?.transcript || [];
  }, [familyName, rounds, selectedRound]);

  const members = useMemo(() => {
    const fam = families.find((f) => f.name === familyName);
    if (!fam) return [];
    return fam.agent_ids.map((id) => agents[id]).filter(Boolean);
  }, [agents, families, familyName]);

  const cohesion = useMemo(() => {
    const sentiments = rounds
      .flatMap((r) => Object.values(r.analysis || {}))
      .filter(Boolean)
      .flatMap((a) => Object.values(a.family_sentiment || {}));
    if (sentiments.length === 0) return 0;
    const avg = sentiments.reduce((sum, x) => sum + x, 0) / sentiments.length;
    return Math.round(avg * 100) / 100;
  }, [rounds]);

  const betrayalRound = useMemo(() => {
    for (const round of rounds) {
      for (const [agentId, analysis] of Object.entries(round.analysis || {})) {
        if (analysis.betrayal?.detected && agents[agentId]?.family === familyName) {
          return round.round;
        }
      }
    }
    return null;
  }, [agents, familyName, rounds]);

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="py-3 px-4">
        <CardTitle className="text-sm font-medium">Family View</CardTitle>
      </CardHeader>
      <CardContent className="p-3 min-h-0 flex-1 overflow-auto">
        <div className="flex items-center gap-2 mb-3">
          <select
            className="h-8 px-2 text-xs border rounded-md bg-white border-black/20"
            value={familyName}
            onChange={(e) => setSelectedFamily(e.target.value)}
          >
            {families.map((f) => (
              <option key={f.name} value={f.name}>{f.name}</option>
            ))}
          </select>
          <select
            className="h-8 px-2 text-xs border rounded-md bg-white border-black/20"
            value={selectedRound}
            onChange={(e) => setSelectedRound(Number(e.target.value))}
          >
            {rounds.map((r) => (
              <option key={r.round} value={r.round}>Round {r.round}</option>
            ))}
          </select>
        </div>

        <div className="mb-3 text-xs">
          <div className="font-medium mb-1">Members</div>
          <div className="space-y-1">
            {members.map((m) => (
              <div key={m.id} className={m.alive ? "" : "text-muted-foreground line-through"}>
                {m.name} ({m.tier}) {m.alive ? "alive" : `eliminated R${m.eliminated_round ?? "?"}`}
              </div>
            ))}
          </div>
        </div>

        <div className="mb-3 text-xs">
          <div className="font-medium mb-1">Cohesion</div>
          <div>Family alignment score: {cohesion}</div>
          {betrayalRound && <div className="text-red-600 mt-1">Internal tension detected at round {betrayalRound}</div>}
        </div>

        <div className="text-xs">
          <div className="font-medium mb-1">Discussion Transcript</div>
          {transcript.length === 0 && <div className="text-muted-foreground">No transcript available for this round.</div>}
          <div className="space-y-1">
            {transcript.map((t, idx) => (
              <div key={`${t.agent_id}-${idx}`} className="border border-black/10 p-2">
                <div className="font-medium">
                  {t.agent} (T{t.tier}, pass {t.discussion_round + 1})
                </div>
                <div className="text-muted-foreground mt-1">{t.content}</div>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

