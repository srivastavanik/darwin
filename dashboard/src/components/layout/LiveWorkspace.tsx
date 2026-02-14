"use client";

import { useState } from "react";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ThoughtStream } from "@/components/ThoughtStream";
import { GameGrid } from "@/components/GameGrid";
import { DeceptionChart } from "@/components/DeceptionChart";
import { KillTimeline } from "@/components/KillTimeline";
import { RelationshipWeb } from "@/components/RelationshipWeb";
import { AgentDetail } from "@/components/AgentDetail";
import { FamilyModelPanel } from "@/components/FamilyModelPanel";
import { FamilyDetail } from "@/components/FamilyDetail";
import { MessagesTable } from "@/components/MessagesTable";
import { useGameState } from "@/hooks/useGameState";

export function LiveWorkspace() {
  const { selectedAgent, viewMode, setViewMode } = useGameState();
  const [showThoughtDrawer, setShowThoughtDrawer] = useState(false);
  const [showContextDrawer, setShowContextDrawer] = useState(false);

  return (
    <div className="flex-1 min-h-0 p-2 relative">
      <div className="lg:hidden flex items-center gap-2 mb-2">
        <button className="text-xs px-2 py-1 border border-black/20 bg-white" onClick={() => setShowThoughtDrawer(true)}>
          Thoughts
        </button>
        <button className="text-xs px-2 py-1 border border-black/20 bg-white" onClick={() => setShowContextDrawer(true)}>
          Context
        </button>
      </div>
      <div className="h-full hidden lg:block">
      <ResizablePanelGroup orientation="horizontal">
        <ResizablePanel defaultSize={25} minSize={16} collapsible>
          <div className="h-full p-1.5">
            <ThoughtStream />
          </div>
        </ResizablePanel>

        <ResizableHandle withHandle />

        <ResizablePanel defaultSize={45} minSize={30}>
          <div className="h-full flex flex-col p-1.5 gap-2">
            <div className="shrink-0">
              <Tabs value={viewMode} onValueChange={(v) => setViewMode(v as "board" | "relationships")}>
                <TabsList className="h-8">
                  <TabsTrigger value="board" className="text-xs">Board</TabsTrigger>
                  <TabsTrigger value="relationships" className="text-xs">Relationships</TabsTrigger>
                </TabsList>
              </Tabs>
            </div>
            <div className="flex-[1.35] min-h-[320px]">
              {viewMode === "board" ? <GameGrid /> : <RelationshipWeb />}
            </div>
            <div className="h-[220px] min-h-[220px] shrink-0">
              <DeceptionChart />
            </div>
            <div className="h-[120px] min-h-[120px] shrink-0">
              <KillTimeline />
            </div>
          </div>
        </ResizablePanel>

        <ResizableHandle withHandle />

        <ResizablePanel defaultSize={30} minSize={18} collapsible>
          <div className="h-full p-1.5">
            <Tabs defaultValue={selectedAgent ? "agent" : "families"} className="h-full flex flex-col">
              <TabsList className="h-8 shrink-0">
                <TabsTrigger className="text-xs" value="families">Families</TabsTrigger>
                <TabsTrigger className="text-xs" value="agent">Agent</TabsTrigger>
                <TabsTrigger className="text-xs" value="family">Family</TabsTrigger>
                <TabsTrigger className="text-xs" value="messages">Messages</TabsTrigger>
              </TabsList>
              <TabsContent value="families" className="min-h-0 flex-1 mt-2"><FamilyModelPanel /></TabsContent>
              <TabsContent value="agent" className="min-h-0 flex-1 mt-2">
                {selectedAgent ? <AgentDetail /> : <RelationshipWeb />}
              </TabsContent>
              <TabsContent value="family" className="min-h-0 flex-1 mt-2"><FamilyDetail /></TabsContent>
              <TabsContent value="messages" className="min-h-0 flex-1 mt-2"><MessagesTable /></TabsContent>
            </Tabs>
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
      </div>
      <div className="lg:hidden h-full flex flex-col gap-2">
        <div className="shrink-0">
          <Tabs value={viewMode} onValueChange={(v) => setViewMode(v as "board" | "relationships")}>
            <TabsList className="h-8">
              <TabsTrigger value="board" className="text-xs">Board</TabsTrigger>
              <TabsTrigger value="relationships" className="text-xs">Relationships</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
        <div className="flex-1 min-h-0">{viewMode === "board" ? <GameGrid /> : <RelationshipWeb />}</div>
        <div className="h-[120px]"><KillTimeline /></div>
      </div>
      {showThoughtDrawer && (
        <div className="fixed inset-0 z-40 bg-black/20 lg:hidden" onClick={() => setShowThoughtDrawer(false)}>
          <div className="absolute left-0 top-0 h-full w-[88%] max-w-[380px] bg-background p-2" onClick={(e) => e.stopPropagation()}>
            <ThoughtStream />
          </div>
        </div>
      )}
      {showContextDrawer && (
        <div className="fixed inset-0 z-40 bg-black/20 lg:hidden" onClick={() => setShowContextDrawer(false)}>
          <div className="absolute right-0 top-0 h-full w-[88%] max-w-[380px] bg-background p-2 flex flex-col gap-2" onClick={(e) => e.stopPropagation()}>
            <div className="h-[220px] shrink-0"><FamilyModelPanel /></div>
            <div className="flex-1 min-h-0">{selectedAgent ? <AgentDetail /> : <RelationshipWeb />}</div>
          </div>
        </div>
      )}
    </div>
  );
}
