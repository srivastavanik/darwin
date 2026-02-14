"use client";

import { AppTopBar } from "@/components/AppTopBar";
import { AnalysisWorkspace } from "@/components/analysis/AnalysisWorkspace";
import { useGameController } from "@/hooks/useGameController";
import { useGameState } from "@/hooks/useGameState";

export default function AnalysisPage() {
  const { games } = useGameController();
  const { setActiveGameId } = useGameState();
  return (
    <div className="h-screen flex flex-col bg-background">
      <AppTopBar status="replay" games={games} onSelectGame={setActiveGameId} />
      <AnalysisWorkspace />
    </div>
  );
}

