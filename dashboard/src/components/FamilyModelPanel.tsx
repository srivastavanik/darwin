"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useGameState } from "@/hooks/useGameState";
import { getFamilyColor, TIER_LABELS } from "@/lib/colors";

const PROVIDER_LABELS: Record<string, string> = {
  anthropic: "Anthropic",
  openai: "OpenAI",
  google: "Google",
  xai: "xAI",
  mixed: "Mixed",
};

const PROVIDER_NOTES: Record<string, string> = {
  anthropic: "Claude 4.5 series tuned for long-context strategic planning.",
  openai: "OpenAI frontier + reasoning stack with high-capability planners.",
  google: "Gemini 2.5 frontier line paired with fast deployment variants.",
  xai: "Grok family variants optimized for high-throughput interaction loops.",
  mixed: "Cross-provider control family for attribution experiments.",
};

export function FamilyModelPanel() {
  const { families, agents } = useGameState();

  return (
    <Card className="h-full">
      <CardHeader className="py-3 px-4">
        <CardTitle className="text-sm font-semibold">Frontier Families</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 p-3">
        {families.length === 0 && (
          <p className="text-xs text-muted-foreground">Waiting for game metadata...</p>
        )}
        {families.map((family) => {
          const familyAgents = family.agent_ids
            .map((id) => agents[id])
            .filter((agent): agent is NonNullable<typeof agent> => Boolean(agent))
            .sort((a, b) => a.tier - b.tier);
          const provider = PROVIDER_LABELS[family.provider] || family.provider;
          const familyColor = getFamilyColor(family.name);

          return (
            <div key={family.name} className="rounded-md border border-black/10 p-2">
              <div className="flex items-center justify-between">
                <p className="text-xs font-semibold text-black">{family.name}</p>
                <span
                  className="h-2.5 w-2.5 rounded-full border border-black/20"
                  style={{ backgroundColor: familyColor }}
                />
              </div>
              <p className="text-[11px] text-muted-foreground">{provider}</p>
              <p className="text-[10px] text-muted-foreground">{PROVIDER_NOTES[family.provider] || "Provider model family."}</p>
              <div className="mt-1 space-y-1">
                {familyAgents.map((agent) => (
                  <div key={agent.id} className="flex items-center justify-between gap-2 text-[11px]">
                    <span className="text-black/80">{agent.name} ({TIER_LABELS[agent.tier]})</span>
                    <span className="truncate text-black/60 max-w-[180px] text-right">{agent.model}</span>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
