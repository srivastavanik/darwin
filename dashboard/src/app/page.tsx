"use client";

import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { RoundControls } from "@/components/RoundControls";
import { ThoughtStream } from "@/components/ThoughtStream";
import { GameGrid } from "@/components/GameGrid";
import { DeceptionChart } from "@/components/DeceptionChart";
import { KillTimeline } from "@/components/KillTimeline";
import { RelationshipWeb } from "@/components/RelationshipWeb";
import { AgentDetail } from "@/components/AgentDetail";
import { ExportPanel } from "@/components/ExportPanel";
import { FamilyModelPanel } from "@/components/FamilyModelPanel";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useGameState } from "@/hooks/useGameState";

export default function DashboardPage() {
  const { status } = useWebSocket();
  const { selectedAgent } = useGameState();

  return (
    <div className="h-screen flex flex-col bg-white">
      <RoundControls status={status} />
      <div className="flex-1 min-h-0">
        <ResizablePanelGroup orientation="horizontal">
          {/* Left: Thought Stream */}
          <ResizablePanel defaultSize={30} minSize={20}>
            <div className="h-full p-2">
              <ThoughtStream />
            </div>
          </ResizablePanel>

          <ResizableHandle withHandle />

          {/* Center: Grid + Charts */}
          <ResizablePanel defaultSize={40} minSize={25}>
            <div className="h-full flex flex-col p-2 gap-2">
              <div className="flex-1 min-h-0">
                <GameGrid />
              </div>
              <div className="h-[220px] shrink-0">
                <DeceptionChart />
              </div>
              <div className="h-[60px] shrink-0">
                <KillTimeline />
              </div>
            </div>
          </ResizablePanel>

          <ResizableHandle withHandle />

          {/* Right: Relationships or Agent Detail */}
          <ResizablePanel defaultSize={30} minSize={15}>
            <div className="h-full p-2 flex flex-col gap-2">
              <div className="h-[260px] shrink-0">
                <FamilyModelPanel />
              </div>
              <div className="flex-1 min-h-0">
                {selectedAgent ? <AgentDetail /> : <RelationshipWeb />}
              </div>
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>

      {/* Bottom export bar */}
      <div className="border-t px-4 py-2 flex items-center justify-end bg-white">
        <ExportPanel />
      </div>
    </div>
  );
}
