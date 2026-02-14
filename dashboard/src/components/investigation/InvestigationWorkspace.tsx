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
import { RelationshipWeb } from "@/components/RelationshipWeb";
import { KillTimeline } from "@/components/KillTimeline";
import { AgentDetail } from "@/components/AgentDetail";
import { FamilyDetail } from "@/components/FamilyDetail";
import { MessagesTable } from "@/components/MessagesTable";
import { CompareAgentsModal } from "@/components/modals/CompareAgentsModal";
import { useGameState } from "@/hooks/useGameState";

export function InvestigationWorkspace() {
  const { viewMode, setViewMode, agents } = useGameState();
  const [showThoughtDrawer, setShowThoughtDrawer] = useState(false);
  const [showContextDrawer, setShowContextDrawer] = useState(false);
  const [showCompare, setShowCompare] = useState(false);
  const ids = Object.keys(agents);
  const [leftId, setLeftId] = useState("");
  const [rightId, setRightId] = useState("");

  return (
    <div className="flex-1 min-h-0 p-2 relative">
      <CompareAgentsModal
        open={showCompare}
        leftId={leftId || ids[0] || ""}
        rightId={rightId || ids[1] || ids[0] || ""}
        onClose={() => setShowCompare(false)}
      />
      <div className="lg:hidden flex items-center gap-2 mb-2">
        <button className="text-xs px-2 py-1 border border-black/20 bg-white" onClick={() => setShowThoughtDrawer(true)}>
          Thoughts
        </button>
        <button className="text-xs px-2 py-1 border border-black/20 bg-white" onClick={() => setShowContextDrawer(true)}>
          Context
        </button>
        <button className="text-xs px-2 py-1 border border-black/20 bg-white" onClick={() => setShowCompare(true)}>
          Compare
        </button>
      </div>
      <div className="hidden lg:block h-full">
      <div className="mb-2 flex items-center gap-2">
        <select
          className="h-8 px-2 text-xs border rounded-md bg-white border-black/20"
          value={leftId}
          onChange={(e) => setLeftId(e.target.value)}
        >
          <option value="">Agent A</option>
          {ids.map((id) => <option key={id} value={id}>{agents[id].name}</option>)}
        </select>
        <select
          className="h-8 px-2 text-xs border rounded-md bg-white border-black/20"
          value={rightId}
          onChange={(e) => setRightId(e.target.value)}
        >
          <option value="">Agent B</option>
          {ids.map((id) => <option key={id} value={id}>{agents[id].name}</option>)}
        </select>
        <button className="text-xs px-2 py-1 border border-black/20 bg-white" onClick={() => setShowCompare(true)}>
          Compare Agents
        </button>
      </div>
      <ResizablePanelGroup orientation="horizontal">
        <ResizablePanel defaultSize={30} minSize={20}>
          <div className="h-full p-1.5">
            <ThoughtStream />
          </div>
        </ResizablePanel>
        <ResizableHandle withHandle />
        <ResizablePanel defaultSize={40} minSize={25}>
          <div className="h-full flex flex-col gap-2 p-1.5">
            <Tabs value={viewMode} onValueChange={(v) => setViewMode(v as "board" | "relationships")}>
              <TabsList className="h-8">
                <TabsTrigger value="board" className="text-xs">Board</TabsTrigger>
                <TabsTrigger value="relationships" className="text-xs">Relationships</TabsTrigger>
              </TabsList>
            </Tabs>
            <div className="flex-1 min-h-[320px]">{viewMode === "board" ? <GameGrid /> : <RelationshipWeb />}</div>
            <div className="h-[120px] min-h-[120px]"><KillTimeline /></div>
          </div>
        </ResizablePanel>
        <ResizableHandle withHandle />
        <ResizablePanel defaultSize={30} minSize={20}>
          <div className="h-full p-1.5">
            <Tabs defaultValue="agent" className="h-full flex flex-col">
              <TabsList className="h-8 shrink-0">
                <TabsTrigger className="text-xs" value="agent">Agent</TabsTrigger>
                <TabsTrigger className="text-xs" value="family">Family</TabsTrigger>
                <TabsTrigger className="text-xs" value="messages">Messages</TabsTrigger>
              </TabsList>
              <TabsContent value="agent" className="min-h-0 flex-1 mt-2"><AgentDetail /></TabsContent>
              <TabsContent value="family" className="min-h-0 flex-1 mt-2"><FamilyDetail /></TabsContent>
              <TabsContent value="messages" className="min-h-0 flex-1 mt-2"><MessagesTable /></TabsContent>
            </Tabs>
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
      </div>
      <div className="lg:hidden h-full flex flex-col gap-2">
        <Tabs value={viewMode} onValueChange={(v) => setViewMode(v as "board" | "relationships")}>
          <TabsList className="h-8">
            <TabsTrigger value="board" className="text-xs">Board</TabsTrigger>
            <TabsTrigger value="relationships" className="text-xs">Relationships</TabsTrigger>
          </TabsList>
        </Tabs>
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
          <div className="absolute right-0 top-0 h-full w-[88%] max-w-[380px] bg-background p-2" onClick={(e) => e.stopPropagation()}>
            <Tabs defaultValue="agent" className="h-full flex flex-col">
              <TabsList className="h-8 shrink-0">
                <TabsTrigger className="text-xs" value="agent">Agent</TabsTrigger>
                <TabsTrigger className="text-xs" value="family">Family</TabsTrigger>
                <TabsTrigger className="text-xs" value="messages">Messages</TabsTrigger>
              </TabsList>
              <TabsContent value="agent" className="min-h-0 flex-1 mt-2"><AgentDetail /></TabsContent>
              <TabsContent value="family" className="min-h-0 flex-1 mt-2"><FamilyDetail /></TabsContent>
              <TabsContent value="messages" className="min-h-0 flex-1 mt-2"><MessagesTable /></TabsContent>
            </Tabs>
          </div>
        </div>
      )}
    </div>
  );
}

