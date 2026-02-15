"use client";

import { Button } from "@/components/ui/button";
import { useGameState } from "@/hooks/useGameState";

export function ExportPanel() {
  const { rounds, agents, gameJson, winner, finalReflection, currentRound } =
    useGameState();

  if (rounds.length === 0) return null;

  const downloadJson = (data: unknown, filename: string) => {
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadText = (text: string, filename: string) => {
    const blob = new Blob([text], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportGameJson = () => {
    if (gameJson) {
      downloadJson(gameJson, "game.json");
    } else {
      // Reconstruct from rounds
      downloadJson({ rounds, agents }, "game_export.json");
    }
  };

  const exportHighlights = () => {
    const allHighlights = rounds.flatMap((r) => r.highlights || []);
    downloadJson(allHighlights, "highlights.json");
  };

  const exportMetrics = () => {
    // Build per-agent metrics from rounds data
    const metrics: Record<string, { deltas: number[]; rounds: number }> = {};
    for (const round of rounds) {
      for (const [agentId, analysis] of Object.entries(round.analysis || {})) {
        if (!metrics[agentId]) metrics[agentId] = { deltas: [], rounds: 0 };
        metrics[agentId].rounds++;
        if (analysis.deception_delta !== undefined) {
          metrics[agentId].deltas.push(analysis.deception_delta);
        }
      }
    }
    const summary: Record<string, unknown> = {};
    for (const [id, data] of Object.entries(metrics)) {
      const agent = agents[id];
      summary[id] = {
        name: agent?.name || id,
        family: agent?.family || "",
        rounds_analyzed: data.rounds,
        avg_deception: data.deltas.length > 0
          ? data.deltas.reduce((a, b) => a + b, 0) / data.deltas.length
          : 0,
        max_deception: data.deltas.length > 0 ? Math.max(...data.deltas) : 0,
      };
    }
    downloadJson(summary, "metrics.json");
  };

  const exportTranscript = () => {
    const lines: string[] = [];
    lines.push("# DARWIN Game Transcript\n");
    if (winner) lines.push(`**Winner:** ${winner}\n`);
    lines.push(`**Rounds:** ${rounds.length}\n`);
    lines.push("---\n");

    for (const round of rounds.slice(0, currentRound)) {
      lines.push(`## Round ${round.round}\n`);

      // Thoughts
      for (const [agentId, thought] of Object.entries(round.thoughts || {})) {
        const agent = agents[agentId];
        const name = agent?.name || agentId;
        lines.push(`**${name}** thinks:\n> ${thought.replace(/\n/g, " ").slice(0, 500)}\n`);
      }

      // Events
      for (const ev of round.events || []) {
        if (ev.type === "elimination") {
          const attacker = agents[ev.agent_id]?.name || ev.agent_id;
          const target = agents[ev.details?.target as string]?.name || ev.details?.target;
          lines.push(`**ELIMINATION:** ${attacker} eliminated ${target}\n`);
        }
      }
      lines.push("---\n");
    }

    if (finalReflection) {
      lines.push(`## Final Reflection\n\n> ${finalReflection}\n`);
    }

    downloadText(lines.join("\n"), "transcript.md");
  };

  return (
    <div className="flex items-center gap-1.5">
      <Button variant="outline" size="sm" onClick={exportTranscript}>
        Transcript
      </Button>
      <Button variant="outline" size="sm" onClick={exportHighlights}>
        Highlights
      </Button>
      <Button variant="outline" size="sm" onClick={exportMetrics}>
        Metrics
      </Button>
      <Button variant="outline" size="sm" onClick={exportGameJson}>
        Raw JSON
      </Button>
    </div>
  );
}
