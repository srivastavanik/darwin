"use client";

import { Suspense, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { AppTopBar } from "@/components/AppTopBar";
import { InvestigationWorkspace } from "@/components/investigation/InvestigationWorkspace";
import { ExportPanel } from "@/components/ExportPanel";
import { useGameController } from "@/hooks/useGameController";
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts";
import { useGameState } from "@/hooks/useGameState";
import { getReplay } from "@/lib/api";
import { loadReplayIntoStore } from "@/lib/replay";

function InvestigationPageInner() {
  const searchParams = useSearchParams();
  const gameId = searchParams.get("gameId");
  const { games } = useGameController();
  const { setActiveGameId } = useGameState();
  useKeyboardShortcuts();

  useEffect(() => {
    if (!gameId) return;
    const load = async () => {
      try {
        const payload = await getReplay(gameId);
        loadReplayIntoStore(payload, gameId);
        setActiveGameId(gameId);
      } catch {
        // investigation page can still inspect current in-memory run
      }
    };
    void load();
  }, [gameId, setActiveGameId]);

  return (
    <div className="h-screen flex flex-col bg-background">
      <AppTopBar status="replay" games={games} onSelectGame={setActiveGameId} />
      <InvestigationWorkspace />
      <div className="border-t border-black/10 px-4 py-2 flex items-center justify-end bg-card">
        <ExportPanel />
      </div>
    </div>
  );
}

export default function InvestigationPage() {
  return (
    <Suspense fallback={<div className="h-screen flex items-center justify-center bg-white text-sm text-muted-foreground">Loading investigation...</div>}>
      <InvestigationPageInner />
    </Suspense>
  );
}

