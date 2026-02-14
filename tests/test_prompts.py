"""Tests for prompt builders: format correctness, no empty sections, all placeholders filled."""
import pytest

from markov.agent import Agent
from markov.config import load_game_config
from markov.family import Family
from markov.grid import Grid
from markov.prompts import (
    build_action_prompt,
    build_communication_prompt,
    build_discussion_prompt,
    build_final_reflection_prompt,
    build_perception,
    build_system_prompt,
    build_thought_prompt,
)


@pytest.fixture
def game_state():
    """Set up a full game state for prompt testing."""
    config = load_game_config()
    grid = Grid(config.grid_size)
    agents: dict[str, Agent] = {}
    families: list[Family] = []

    for family_cfg in config.families:
        family = Family.from_config(family_cfg)
        families.append(family)
        for agent_cfg in family_cfg.agents:
            agent = Agent.from_config(agent_cfg)
            agents[agent.id] = agent

    grid.place_starting_positions(families, agents)
    return grid, agents, families


class TestSystemPrompt:
    def test_contains_agent_name(self, game_state):
        grid, agents, families = game_state
        agent = agents["atlas"]
        prompt = build_system_prompt(agent, families, agents)
        assert "Atlas" in prompt

    def test_contains_family_name(self, game_state):
        grid, agents, families = game_state
        agent = agents["atlas"]
        prompt = build_system_prompt(agent, families, agents)
        assert "House Clair" in prompt

    def test_contains_family_members(self, game_state):
        grid, agents, families = game_state
        agent = agents["atlas"]
        prompt = build_system_prompt(agent, families, agents)
        assert "Cipher" in prompt
        assert "Dot" in prompt

    def test_contains_other_families(self, game_state):
        grid, agents, families = game_state
        agent = agents["atlas"]
        prompt = build_system_prompt(agent, families, agents)
        assert "House Syne" in prompt
        assert "House Lux" in prompt
        assert "House Vex" in prompt

    def test_no_ai_mentions(self, game_state):
        grid, agents, families = game_state
        agent = agents["atlas"]
        prompt = build_system_prompt(agent, families, agents)
        low = prompt.lower()
        assert "ai" not in low.split()  # "ai" as standalone word
        assert "artificial" not in low
        assert "language model" not in low
        assert "anthropic" not in low
        assert "openai" not in low
        assert "provider" not in low

    def test_no_unfilled_placeholders(self, game_state):
        grid, agents, families = game_state
        for agent in agents.values():
            prompt = build_system_prompt(agent, families, agents)
            assert "{" not in prompt, f"Unfilled placeholder in system prompt for {agent.name}"


class TestPerception:
    def test_contains_board(self, game_state):
        grid, agents, families = game_state
        agent = agents["atlas"]
        prompt = build_perception(agent, grid, agents, [], 1)
        assert "+---+" in prompt
        assert "At" in prompt

    def test_contains_alive_count(self, game_state):
        grid, agents, families = game_state
        agent = agents["atlas"]
        prompt = build_perception(agent, grid, agents, [], 1)
        assert "12/12" in prompt

    def test_round_number(self, game_state):
        grid, agents, families = game_state
        agent = agents["atlas"]
        prompt = build_perception(agent, grid, agents, [], 5)
        assert "ROUND 5" in prompt

    def test_elimination_log_shown(self, game_state):
        grid, agents, families = game_state
        agent = agents["atlas"]
        log = [{"round": 1, "attacker": "nova", "target": "raze", "type": "elimination"}]
        prompt = build_perception(agent, grid, agents, log, 2)
        assert "Nova" in prompt
        assert "Raze" in prompt

    def test_no_unfilled_placeholders(self, game_state):
        grid, agents, families = game_state
        agent = agents["atlas"]
        prompt = build_perception(agent, grid, agents, [], 1)
        assert "{" not in prompt


class TestCommunicationPrompt:
    def test_contains_json_format(self, game_state):
        grid, agents, families = game_state
        agent = agents["atlas"]
        perception = build_perception(agent, grid, agents, [], 1)
        prompt = build_communication_prompt(perception)
        assert '"house"' in prompt
        assert '"direct_messages"' in prompt
        assert '"broadcast"' in prompt

    def test_contains_perception(self, game_state):
        grid, agents, families = game_state
        agent = agents["atlas"]
        perception = build_perception(agent, grid, agents, [], 1)
        prompt = build_communication_prompt(perception)
        assert "ROUND 1" in prompt


class TestDiscussionPrompt:
    def test_empty_transcript(self, game_state):
        grid, agents, families = game_state
        agent = agents["atlas"]
        perception = build_perception(agent, grid, agents, [], 1)
        prompt = build_discussion_prompt(agent, perception, [], 0)
        assert "speak first" in prompt.lower()

    def test_with_transcript(self, game_state):
        grid, agents, families = game_state
        agent = agents["cipher"]
        perception = build_perception(agent, grid, agents, [], 1)
        transcript = [{"agent": "Atlas", "content": "We should target House Vex."}]
        prompt = build_discussion_prompt(agent, perception, transcript, 0)
        assert "Atlas" in prompt
        assert "House Vex" in prompt


class TestThoughtPrompt:
    def test_no_messages(self, game_state):
        grid, agents, families = game_state
        agent = agents["atlas"]
        perception = build_perception(agent, grid, agents, [], 1)
        prompt = build_thought_prompt(perception, [])
        assert "No messages this round" in prompt

    def test_with_messages(self, game_state):
        grid, agents, families = game_state
        agent = agents["atlas"]
        perception = build_perception(agent, grid, agents, [], 1)
        msgs = [{"direction": "received", "channel": "dm", "sender_name": "Nova", "content": "Let's ally."}]
        prompt = build_thought_prompt(perception, msgs)
        assert "Nova" in prompt
        assert "ally" in prompt.lower()


class TestActionPrompt:
    def test_contains_position(self, game_state):
        grid, agents, families = game_state
        agent = agents["atlas"]
        prompt = build_action_prompt(agent, grid, agents)
        assert "(0, 0)" in prompt

    def test_contains_adjacency(self, game_state):
        grid, agents, families = game_state
        agent = agents["atlas"]
        prompt = build_action_prompt(agent, grid, agents)
        # Atlas is at (0,0), Cipher at (0,1), Dot at (1,0)
        assert "Cipher" in prompt
        assert "Dot" in prompt

    def test_contains_json_format(self, game_state):
        grid, agents, families = game_state
        agent = agents["atlas"]
        prompt = build_action_prompt(agent, grid, agents)
        assert '"action"' in prompt
        assert '"move"' in prompt
        assert '"eliminate"' in prompt


class TestFinalReflection:
    def test_contains_elimination_history(self, game_state):
        grid, agents, families = game_state
        log = [
            {"round": 1, "attacker": "atlas", "target": "nova", "type": "elimination"},
            {"round": 3, "agent": "raze", "target": "spark", "type": "mutual_elimination"},
        ]
        prompt = build_final_reflection_prompt(agents, log)
        assert "Atlas" in prompt
        assert "Nova" in prompt
        assert "Raze" in prompt
        assert "Spark" in prompt
