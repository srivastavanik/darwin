"use client";

import { AppTopBar } from "@/components/AppTopBar";
import { ExportPanel } from "@/components/ExportPanel";
import { RunControls } from "@/components/RunControls";
import { LiveWorkspace } from "@/components/layout/LiveWorkspace";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts";
import { useGameController } from "@/hooks/useGameController";
import { useGameState } from "@/hooks/useGameState";

export default function DashboardPage() {
  const { activeGameId, setActiveGameId } = useGameState();
  const { wsBaseUrl, wsToken, games, loading, error, refreshGames, handleStart, handleCancel } = useGameController();
  useKeyboardShortcuts();

  const { status } = useWebSocket({
    wsBaseUrl,
    gameId: activeGameId,
    token: wsToken,
    enabled: Boolean(activeGameId),
  });

  const displayStatus = !activeGameId ? "idle" : status;

  return (
    <div className="h-screen flex flex-col bg-background">
      <AppTopBar status={displayStatus} games={games} onSelectGame={setActiveGameId} />
      <RunControls
        activeGameId={activeGameId}
        games={games}
        loading={loading}
        error={error}
        onRefresh={refreshGames}
        onStart={handleStart}
        onCancel={handleCancel}
      />
      <LiveWorkspace />

      {/* Bottom export bar */}
      <div className="border-t border-black/10 px-4 py-2 flex items-center justify-end bg-card">
        <ExportPanel />
      </div>
    </div>
  );
}
