import { useGameState } from "@/hooks/useGameState";
import type { AgentState, FamilyConfig, GameInitData, RoundData } from "@/lib/types";

export function loadReplayIntoStore(data: any, gameId?: string | null) {
  useGameState.getState().setGameJson(data);
  const config = data.config || {};
  const gameRounds = data.rounds || [];
  const result = data.result || {};
  const firstRoundGridAgents = gameRounds[0]?.grid?.agents || [];

  const agentsMap: Record<string, Partial<AgentState>> = {};
  for (const agent of firstRoundGridAgents) {
    agentsMap[agent.id] = { ...agent };
  }

  for (const round of gameRounds) {
    for (const msg of round.messages || []) {
      if (msg.sender && !agentsMap[msg.sender]) {
        agentsMap[msg.sender] = {
          id: msg.sender,
          name: msg.sender_name || msg.sender,
          family: msg.family || "",
          provider: "",
          tier: 1,
          alive: true,
        };
      }
    }
    for (const [agentId] of Object.entries(round.thoughts || {})) {
      if (!agentsMap[agentId]) {
        agentsMap[agentId] = {
          id: agentId,
          name: agentId.charAt(0).toUpperCase() + agentId.slice(1),
          family: "",
          tier: 1,
          alive: true,
        };
      }
    }
  }

  for (const round of gameRounds) {
    for (const disc of round.family_discussions || []) {
      for (const entry of disc.transcript || []) {
        const aid = entry.agent_id;
        if (aid && agentsMap[aid]) {
          agentsMap[aid].name = entry.agent;
          agentsMap[aid].tier = entry.tier || 1;
          agentsMap[aid].family = disc.family || agentsMap[aid].family;
        }
      }
    }
  }

  const configuredFamilies = (config.families || []) as Array<{
    name: string;
    provider: string;
    color: string;
    agents: Array<{ name: string; tier: number; model: string; temperature: number }>;
  }>;
  for (const family of configuredFamilies) {
    for (const configAgent of family.agents || []) {
      const id = configAgent.name.toLowerCase();
      const existing = agentsMap[id] || {};
      agentsMap[id] = {
        id,
        name: configAgent.name,
        family: family.name,
        provider: family.provider,
        model: configAgent.model,
        tier: configAgent.tier,
        temperature: configAgent.temperature,
        alive: existing.alive ?? true,
        position: existing.position || [0, 0],
        eliminated_by: existing.eliminated_by || null,
        eliminated_round: existing.eliminated_round || null,
      };
    }
  }

  const families: FamilyConfig[] =
    configuredFamilies.length > 0
      ? configuredFamilies.map((family) => ({
          name: family.name,
          provider: family.provider,
          color: family.color,
          agent_ids: (family.agents || []).map((a) => a.name.toLowerCase()),
        }))
      : Object.values(agentsMap).reduce<FamilyConfig[]>((acc, agent) => {
          const family = agent.family || "Unknown";
          const found = acc.find((f) => f.name === family);
          if (found) {
            if (agent.id) found.agent_ids.push(agent.id);
            return acc;
          }
          acc.push({
            name: family,
            provider: agent.provider || "",
            color: "#9CA3AF",
            agent_ids: agent.id ? [agent.id] : [],
          });
          return acc;
        }, []);

  const initData: GameInitData = {
    type: "game_init",
    game_id: data.game_id || gameId || undefined,
    grid_size: config.grid_size || 6,
    agents: agentsMap as GameInitData["agents"],
    families,
    total_rounds: gameRounds.length,
    result,
  };

  useGameState.getState().initGame(initData);

  for (const round of gameRounds) {
    const roundData: RoundData = {
      game_id: data.game_id || gameId || undefined,
      round: round.round,
      grid: {
        size: config.grid_size || 6,
        agents: round.grid?.agents || [],
      },
      events: round.events || [],
      thoughts: round.thoughts || {},
      messages: {
        family_discussions: round.family_discussions || [],
        direct_messages: (round.messages || []).filter((m: { channel: string }) => m.channel === "dm"),
        broadcasts: (round.messages || []).filter((m: { channel: string }) => m.channel === "broadcast"),
        family_messages: (round.messages || []).filter((m: { channel: string }) => m.channel === "family"),
      },
      analysis: round.analysis || {},
      highlights: round.highlights || [],
      alive_count:
        round.grid?.agents?.filter((a: { alive: boolean }) => a.alive).length ??
        Object.keys(round.thoughts || {}).length,
      game_over: false,
      winner: null,
    };
    useGameState.getState().pushRound(roundData);
  }

  useGameState.getState().setCurrentRound(1);
  if (result.winner_name) {
    useGameState.getState().setGameOver(result.winner_name, result.final_reflection);
  }
}

