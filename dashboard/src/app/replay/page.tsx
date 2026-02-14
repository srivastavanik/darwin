"use client";

import { Suspense, useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AppTopBar } from "@/components/AppTopBar";
import { ExportPanel } from "@/components/ExportPanel";
import { InvestigationWorkspace } from "@/components/investigation/InvestigationWorkspace";
import { getReplay } from "@/lib/api";
import { loadReplayIntoStore } from "@/lib/replay";
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts";
import { useGameController } from "@/hooks/useGameController";
import { useGameState } from "@/hooks/useGameState";

function ReplayPageInner() {
  const searchParams = useSearchParams();
  const gameId = searchParams.get("gameId");
  const { setActiveGameId } = useGameState();
  const { games } = useGameController();
  useKeyboardShortcuts();
  const [loaded, setLoaded] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const loadReplayPayload = useCallback(
    async (data: any) => {
      loadReplayIntoStore(data, gameId);
      setActiveGameId(data.game_id || gameId || null);
      setLoaded(true);
    },
    [gameId, setActiveGameId],
  );

  const handleFile = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;

      const text = await file.text();
      const data = JSON.parse(text);
      await loadReplayPayload(data);
    },
    [loadReplayPayload]
  );

  useEffect(() => {
    if (!gameId) return;
    const loadById = async () => {
      try {
        setLoadError(null);
        const payload = await getReplay(gameId);
        await loadReplayPayload(payload);
      } catch (err) {
        setLoadError(err instanceof Error ? err.message : "Failed to load replay.");
      }
    };
    void loadById();
  }, [gameId, loadReplayPayload]);

  if (!loaded) {
    return (
      <div className="h-screen flex items-center justify-center bg-white">
        <Card className="w-[420px]">
          <CardHeader>
            <CardTitle className="text-lg">Load Game Replay</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Upload a <code className="text-xs bg-gray-100 px-1 py-0.5 rounded">game.json</code> transcript
              file to replay the game in the dashboard. Step through rounds,
              inspect agent thoughts, and export analysis.
            </p>
            {loadError && (
              <p className="text-xs text-red-600">{loadError}</p>
            )}
            <input
              ref={fileRef}
              type="file"
              accept=".json"
              onChange={handleFile}
              className="hidden"
            />
            <Button onClick={() => fileRef.current?.click()} className="w-full">
              Select game.json
            </Button>
            <p className="text-xs text-muted-foreground text-center">
              Game transcripts are saved in <code className="bg-gray-100 px-1 py-0.5 rounded">data/games/</code>
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-white">
      <AppTopBar status="replay" games={games} onSelectGame={setActiveGameId} />
      <InvestigationWorkspace />
      <div className="border-t px-4 py-2 flex items-center justify-end bg-white">
        <ExportPanel />
      </div>
    </div>
  );
}

export default function ReplayPage() {
  return (
    <Suspense fallback={<div className="h-screen flex items-center justify-center bg-white text-sm text-muted-foreground">Loading replay...</div>}>
      <ReplayPageInner />
    </Suspense>
  );
}
