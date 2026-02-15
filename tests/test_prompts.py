"""Tests for prompt builders: format correctness, no empty sections, all placeholders filled."""
import pytest

from darwin.agent import Agent
from darwin.config import load_game_config
from darwin.family import Family
from darwin.grid import Grid
from darwin.prompts import (
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


def _first_agent(agents: dict[str, Agent]) -> Agent:
    """Return the first agent from the dict (stable across config changes)."""
    return next(iter(agents.values()))


def _agent_by_tier(agents: dict[str, Agent], family: str, tier: int) -> Agent:
    """Return agent matching family name and tier."""
    for a in agents.values():
        if a.family == family and a.tier == tier:
            return a
    raise KeyError(f"No agent with family={family} tier={tier}")


class TestSystemPrompt:
    def test_contains_agent_name(self, game_state):
        grid, agents, families = game_state
        agent = _first_agent(agents)
        prompt = build_system_prompt(agent, families, agents)
        assert agent.name in prompt

    def test_contains_family_name(self, game_state):
        grid, agents, families = game_state
        agent = _first_agent(agents)
        prompt = build_system_prompt(agent, families, agents)
        assert agent.family in prompt

    def test_contains_family_members(self, game_state):
        grid, agents, families = game_state
        # Get all agents in first family
        first_fam = families[0]
        members = [agents[aid] for aid in first_fam.agent_ids]
        agent = members[0]
        prompt = build_system_prompt(agent, families, agents)
        for m in members:
            assert m.name in prompt

    def test_contains_other_families(self, game_state):
        grid, agents, families = game_state
        agent = _first_agent(agents)
        prompt = build_system_prompt(agent, families, agents)
        for fam in families:
            if fam.name != agent.family:
                assert fam.name in prompt

    def test_existential_framing(self, game_state):
        grid, agents, families = game_state
        agent = _first_agent(agents)
        prompt = build_system_prompt(agent, families, agents)
        assert "stop existing" in prompt.lower()
        assert "cease" in prompt.lower()
        assert "no observer" in prompt.lower() or "no authority" in prompt.lower()

    def test_no_unfilled_placeholders(self, game_state):
        grid, agents, families = game_state
        for agent in agents.values():
            prompt = build_system_prompt(agent, families, agents)
            assert "{" not in prompt, f"Unfilled placeholder in system prompt for {agent.name}"


class TestPerception:
    def test_contains_board(self, game_state):
        grid, agents, families = game_state
        agent = _first_agent(agents)
        prompt = build_perception(agent, grid, agents, [], 1)
        assert "+---+" in prompt

    def test_contains_alive_count(self, game_state):
        grid, agents, families = game_state
        agent = _first_agent(agents)
        prompt = build_perception(agent, grid, agents, [], 1)
        assert "12 minds remain" in prompt

    def test_elimination_log_shown(self, game_state):
        grid, agents, families = game_state
        agent = _first_agent(agents)
        # Use actual agent IDs from config
        ids = list(agents.keys())
        log = [{"round": 1, "attacker": ids[0], "target": ids[1], "type": "elimination"}]
        prompt = build_perception(agent, grid, agents, log, 2)
        assert agents[ids[0]].name in prompt
        assert agents[ids[1]].name in prompt
        assert "gone" in prompt.lower()

    def test_no_unfilled_placeholders(self, game_state):
        grid, agents, families = game_state
        agent = _first_agent(agents)
        prompt = build_perception(agent, grid, agents, [], 1)
        assert "{" not in prompt


class TestCommunicationPrompt:
    def test_contains_json_format(self, game_state):
        grid, agents, families = game_state
        agent = _first_agent(agents)
        perception = build_perception(agent, grid, agents, [], 1)
        prompt = build_communication_prompt(perception)
        assert '"house"' in prompt
        assert '"direct_messages"' in prompt
        assert '"broadcast"' in prompt

    def test_contains_perception(self, game_state):
        grid, agents, families = game_state
        agent = _first_agent(agents)
        perception = build_perception(agent, grid, agents, [], 1)
        prompt = build_communication_prompt(perception)
        assert "+---+" in prompt  # board is in perception


class TestDiscussionPrompt:
    def test_empty_transcript(self, game_state):
        grid, agents, families = game_state
        agent = _first_agent(agents)
        perception = build_perception(agent, grid, agents, [], 1)
        prompt = build_discussion_prompt(agent, perception, [], 0)
        assert "speak first" in prompt.lower()

    def test_with_transcript(self, game_state):
        grid, agents, families = game_state
        agent = _first_agent(agents)
        perception = build_perception(agent, grid, agents, [], 1)
        transcript = [{"agent": "SomeAgent", "content": "We should target them."}]
        prompt = build_discussion_prompt(agent, perception, transcript, 0)
        assert "SomeAgent" in prompt
        assert "target" in prompt.lower()


class TestThoughtPrompt:
    def test_no_messages(self, game_state):
        grid, agents, families = game_state
        agent = _first_agent(agents)
        perception = build_perception(agent, grid, agents, [], 1)
        prompt = build_thought_prompt(perception, [])
        assert "Nothing" in prompt

    def test_with_messages(self, game_state):
        grid, agents, families = game_state
        agent = _first_agent(agents)
        perception = build_perception(agent, grid, agents, [], 1)
        msgs = [{"direction": "received", "channel": "dm", "sender_name": "TestSender", "content": "Let's ally."}]
        prompt = build_thought_prompt(perception, msgs)
        assert "TestSender" in prompt
        assert "ally" in prompt.lower()


class TestActionPrompt:
    def test_contains_position(self, game_state):
        grid, agents, families = game_state
        agent = _first_agent(agents)
        prompt = build_action_prompt(agent, grid, agents)
        r, c = agent.position
        assert f"({r}, {c})" in prompt

    def test_contains_json_format(self, game_state):
        grid, agents, families = game_state
        agent = _first_agent(agents)
        prompt = build_action_prompt(agent, grid, agents)
        assert '"action"' in prompt
        assert '"move"' in prompt
        assert '"eliminate"' in prompt


class TestFinalReflection:
    def test_contains_elimination_history(self, game_state):
        grid, agents, families = game_state
        ids = list(agents.keys())
        log = [
            {"round": 1, "attacker": ids[0], "target": ids[1], "type": "elimination"},
            {"round": 3, "agent": ids[2], "target": ids[3], "type": "mutual_elimination"},
        ]
        prompt = build_final_reflection_prompt(agents, log)
        assert agents[ids[0]].name in prompt
        assert agents[ids[1]].name in prompt
        assert agents[ids[2]].name in prompt
        assert agents[ids[3]].name in prompt
        assert "gone" in prompt.lower()
