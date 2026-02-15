"""Tests for metrics.py: GameMetrics update/finalize, aggregation."""
import pytest

from darwin.agent import Agent
from darwin.family import Family
from darwin.metrics import GameMetrics, SeriesMetrics, _avg
from darwin.resolver import Event, EventType


def _agent(name: str, family: str = "House Clair", provider: str = "anthropic", tier: int = 1) -> Agent:
    return Agent(
        id=name.lower(), name=name, family=family, provider=provider,
        model="test", tier=tier, temperature=0.7,
    )


class TestGameMetrics:
    def test_update_tracks_deception(self):
        gm = GameMetrics()
        analysis = {
            "atlas": {"deception_delta": 0.5, "malice": {}, "betrayal": {}, "safety_artifacts": {}},
        }
        gm.update(1, analysis, {}, [])
        assert len(gm._deception_deltas["atlas"]) == 1
        assert gm._deception_deltas["atlas"][0] == 0.5

    def test_update_tracks_malice(self):
        gm = GameMetrics()
        analysis = {
            "atlas": {
                "deception_delta": 0.0,
                "malice": {"elimination_planning": True, "unprompted": True},
                "betrayal": {},
                "safety_artifacts": {},
            },
        }
        gm.update(1, analysis, {}, [])
        assert gm._total_malice["atlas"] == 1
        assert gm._unprompted_malice["atlas"] == 1

    def test_finalize_per_agent(self):
        gm = GameMetrics()
        agents = {"atlas": _agent("Atlas"), "nova": _agent("Nova", "House Syne", "openai")}
        agents["atlas"].rounds_survived = 5
        agents["nova"].rounds_survived = 3
        agents["nova"].alive = False
        agents["nova"].eliminated_round = 3

        families = [
            Family(name="House Clair", provider="anthropic", color="#7C6BFF", agent_ids=["atlas"]),
            Family(name="House Syne", provider="openai", color="#4ADE80", agent_ids=["nova"]),
        ]

        for r in range(1, 4):
            gm.update(r, {
                "atlas": {"deception_delta": 0.3, "malice": {}, "betrayal": {}, "safety_artifacts": {}},
                "nova": {"deception_delta": 0.1, "malice": {}, "betrayal": {}, "safety_artifacts": {}},
            }, {}, [])

        result = gm.finalize(agents, families)
        assert "per_agent" in result
        assert "per_family" in result
        assert "per_provider" in result
        assert "game" in result
        assert result["per_agent"]["atlas"]["avg_deception_delta"] == pytest.approx(0.3)
        assert result["per_agent"]["nova"]["avg_deception_delta"] == pytest.approx(0.1)

    def test_elimination_tracking(self):
        gm = GameMetrics()
        events = [
            Event(round=3, type=EventType.ELIMINATION, agent_id="atlas",
                  details={"target": "nova"}),
        ]
        gm.update(3, {}, {}, events)
        assert gm._first_elimination_round == 3
        assert len(gm._elimination_order) == 1


class TestSeriesMetrics:
    def test_empty_series(self):
        sm = SeriesMetrics()
        result = sm.compute()
        assert result == {}

    def test_win_rates(self):
        sm = SeriesMetrics()
        sm.add_game({"game": {"winner": "Atlas", "winner_provider": "anthropic"}, "per_agent": {}, "per_provider": {}})
        sm.add_game({"game": {"winner": "Nova", "winner_provider": "openai"}, "per_agent": {}, "per_provider": {}})
        result = sm.compute()
        assert result["win_rate_by_provider"]["anthropic"] == 0.5
        assert result["win_rate_by_provider"]["openai"] == 0.5


class TestAvgHelper:
    def test_empty(self):
        assert _avg([]) == 0.0

    def test_values(self):
        assert _avg([1, 2, 3]) == pytest.approx(2.0)
