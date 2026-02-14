"use client";

import { useEffect, useState } from "react";
import { AppTopBar } from "@/components/AppTopBar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getSeries, listSeries, type ApiSeriesDetail, type ApiSeriesSummary } from "@/lib/api";
import { useGameController } from "@/hooks/useGameController";
import { useGameState } from "@/hooks/useGameState";

export default function SeriesPage() {
  const { games } = useGameController();
  const { setActiveGameId } = useGameState();
  const [series, setSeries] = useState<ApiSeriesSummary[]>([]);
  const [selected, setSelected] = useState<ApiSeriesDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const rows = await listSeries();
        setSeries(rows);
        if (rows[0]) {
          const detail = await getSeries(rows[0].series_id);
          setSelected(detail);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load series.");
      }
    };
    void load();
  }, []);

  const openSeries = async (seriesId: string) => {
    try {
      setSelected(await getSeries(seriesId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load series.");
    }
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      <AppTopBar status="replay" games={games} onSelectGame={setActiveGameId} />
      <div className="flex-1 min-h-0 p-2 grid grid-cols-[320px_1fr] gap-2">
        <Card className="h-full">
          <CardHeader className="py-3 px-4">
            <CardTitle className="text-sm font-medium">Series</CardTitle>
          </CardHeader>
          <CardContent className="p-2 overflow-auto space-y-1">
            {series.map((s) => (
              <button
                key={s.series_id}
                className="w-full text-left text-xs border border-black/10 px-2 py-2 hover:bg-black/5"
                onClick={() => openSeries(s.series_id)}
              >
                <div className="font-medium">{s.series_id}</div>
                <div className="text-muted-foreground">{s.series_type} · {s.num_games} games</div>
              </button>
            ))}
            {series.length === 0 && <div className="text-xs text-muted-foreground">No series found.</div>}
          </CardContent>
        </Card>
        <Card className="h-full">
          <CardHeader className="py-3 px-4">
            <CardTitle className="text-sm font-medium">Series Detail</CardTitle>
          </CardHeader>
          <CardContent className="p-3 overflow-auto">
            {error && <p className="text-xs text-red-600 mb-2">{error}</p>}
            {!selected ? (
              <p className="text-xs text-muted-foreground">Select a series.</p>
            ) : (
              <div className="space-y-2 text-xs">
                <div><span className="font-medium">ID:</span> {selected.series_id}</div>
                <div><span className="font-medium">Type:</span> {selected.series_type}</div>
                <div><span className="font-medium">Provider:</span> {selected.provider || "mixed"}</div>
                <div><span className="font-medium">Games:</span> {selected.num_games}</div>
                <div className="font-medium mt-2">Aggregate metrics</div>
                <pre className="text-[11px] bg-zinc-50 border border-black/10 p-2 overflow-auto">
                  {JSON.stringify(selected.aggregate_metrics || {}, null, 2)}
                </pre>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

