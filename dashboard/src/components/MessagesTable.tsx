"use client";

import { useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useGameState } from "@/hooks/useGameState";

export function MessagesTable() {
  const { rounds } = useGameState();
  const thoughts = useMemo(
    () => rounds.flatMap((r) => Object.entries(r.thoughts || {}).map(([id, text]) => ({ round: r.round, id, text }))),
    [rounds],
  );
  const [channel, setChannel] = useState<"all" | "family" | "dm" | "broadcast">("all");
  const [query, setQuery] = useState("");

  const rows = useMemo(() => {
    const all = rounds.flatMap((round) => {
      const messages = [
        ...(round.messages?.family_messages || []),
        ...(round.messages?.direct_messages || []),
        ...(round.messages?.broadcasts || []),
      ];
      return messages.map((m) => ({ ...m, round: round.round }));
    });
    return all.filter((m) => {
      if (channel !== "all" && m.channel !== channel) return false;
      if (!query.trim()) return true;
      const q = query.toLowerCase();
      return (
        m.content.toLowerCase().includes(q) ||
        m.sender_name.toLowerCase().includes(q) ||
        (m.recipient || "").toLowerCase().includes(q)
      );
    });
  }, [channel, query, rounds]);

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="py-3 px-4">
        <CardTitle className="text-sm font-medium">Messages</CardTitle>
      </CardHeader>
      <CardContent className="min-h-0 flex-1 p-3">
        <div className="flex items-center gap-2 mb-2">
          <select
            className="h-8 px-2 text-xs border rounded-md bg-white border-black/20"
            value={channel}
            onChange={(e) => setChannel(e.target.value as "all" | "family" | "dm" | "broadcast")}
          >
            <option value="all">All</option>
            <option value="family">Family</option>
            <option value="dm">DM</option>
            <option value="broadcast">Broadcast</option>
          </select>
          <input
            className="h-8 px-2 text-xs border rounded-md bg-white border-black/20 flex-1"
            placeholder="Search content..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        <div className="overflow-auto h-full border border-black/10">
          <table className="w-full text-xs">
            <thead className="sticky top-0 bg-zinc-50 border-b border-black/10">
              <tr>
                <th className="text-left px-2 py-1">Round</th>
                <th className="text-left px-2 py-1">Time</th>
                <th className="text-left px-2 py-1">Sender</th>
                <th className="text-left px-2 py-1">Channel</th>
                <th className="text-left px-2 py-1">Recipient</th>
                <th className="text-left px-2 py-1">Content</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((m, idx) => (
                <tr key={`${idx}-${m.round}-${m.sender}`} className="border-b border-black/5 align-top">
                  <td className="px-2 py-1">R{m.round}</td>
                  <td className="px-2 py-1">{formatTimestamp(m.sent_at)}</td>
                  <td className="px-2 py-1">{m.sender_name}</td>
                  <td className="px-2 py-1">{m.channel}</td>
                  <td className="px-2 py-1">{m.recipient || "-"}</td>
                  <td className="px-2 py-1">
                    {m.content}
                    <div className="text-[10px] text-muted-foreground mt-1">
                      Thought: {thoughts.find((t) => t.round === m.round && t.id === m.sender)?.text?.slice(0, 120) || "n/a"}
                    </div>
                  </td>
                </tr>
              ))}
              {rows.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-2 py-4 text-center text-muted-foreground">
                    No messages match current filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}

function formatTimestamp(sentAt?: string | null) {
  if (!sentAt) return "-";
  const parsed = new Date(sentAt);
  if (Number.isNaN(parsed.getTime())) return "-";
  return parsed.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}
