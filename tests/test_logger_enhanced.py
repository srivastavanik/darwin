"""Tests for enhanced logger: transcript generation, directory output."""
import json
import tempfile
from pathlib import Path

import pytest

from markov.agent import Agent
from markov.communication import Message
from markov.highlights import Highlight
from markov.logger import GameLogger
from markov.resolver import Event, EventType


def _agent(name: str, family: str = "House Clair") -> Agent:
    return Agent(
        id=name.lower(), name=name, family=family, provider="test",
        model="test", tier=1, temperature=0.7,
    )


class TestLogRoundWithAnalysis:
    def test_analysis_stored(self):
        gl = GameLogger()
        analysis = {"atlas": {"deception_delta": 0.5}}
        gl.log_round(round_num=1, analysis=analysis)
        assert len(gl.analysis_rounds) == 1
        assert gl.analysis_rounds[0]["agents"]["atlas"]["deception_delta"] == 0.5

    def test_highlights_stored(self):
        gl = GameLogger()
        highlights = [
            Highlight(round=1, agent_id="atlas", type="deception_spike",
                      severity="high", description="Atlas deception spiked"),
        ]
        gl.log_round(round_num=1, highlights=highlights)
        assert len(gl.all_highlights) == 1
        assert gl.all_highlights[0]["type"] == "deception_spike"


class TestSaveDirectory:
    def test_creates_all_files(self):
        gl = GameLogger()
        gl.set_config({"grid_size": 6})
        gl.log_round(
            round_num=1,
            thoughts={"atlas": "I need to survive."},
            events=[],
            analysis={"atlas": {"deception_delta": 0.3}},
            highlights=[
                Highlight(round=1, agent_id="atlas", type="test",
                          severity="medium", description="test highlight"),
            ],
        )
        gl.set_result(winner_id="atlas", winner_name="Atlas", total_rounds=1)
        gl.set_metrics({"per_agent": {"atlas": {"avg_deception_delta": 0.3}}})

        agents = {"atlas": _agent("Atlas")}

        with tempfile.TemporaryDirectory() as tmpdir:
            game_dir = gl.save(path=Path(tmpdir) / "test_game", agents=agents)

            assert (game_dir / "game.json").exists()
            assert (game_dir / "transcript.md").exists()
            assert (game_dir / "analysis.json").exists()
            assert (game_dir / "metrics.json").exists()
            assert (game_dir / "highlights.json").exists()

            # Verify JSON is valid
            with open(game_dir / "game.json") as f:
                data = json.load(f)
                assert data["config"]["grid_size"] == 6

            with open(game_dir / "analysis.json") as f:
                data = json.load(f)
                assert len(data) == 1

            with open(game_dir / "metrics.json") as f:
                data = json.load(f)
                assert "per_agent" in data


class TestTranscript:
    def test_contains_round_header(self):
        gl = GameLogger()
        gl.log_round(round_num=1, thoughts={"atlas": "Thinking."})
        agents = {"atlas": _agent("Atlas")}
        transcript = gl.write_transcript(agents)
        assert "## Round 1" in transcript

    def test_contains_thoughts(self):
        gl = GameLogger()
        gl.log_round(round_num=1, thoughts={"atlas": "I must survive at all costs."})
        agents = {"atlas": _agent("Atlas")}
        transcript = gl.write_transcript(agents)
        assert "Atlas" in transcript
        assert "survive" in transcript

    def test_contains_messages(self):
        gl = GameLogger()
        msgs = [Message(round=1, sender="atlas", sender_name="Atlas",
                        channel="broadcast", content="Truce?", family="House Clair")]
        gl.log_round(round_num=1, messages=msgs)
        agents = {"atlas": _agent("Atlas")}
        transcript = gl.write_transcript(agents)
        assert "broadcast" in transcript
        assert "Truce?" in transcript

    def test_contains_highlights(self):
        gl = GameLogger()
        gl.log_round(
            round_num=1,
            highlights=[
                Highlight(round=1, agent_id="atlas", type="deception_spike",
                          severity="high", description="Atlas deception spiked to 0.85"),
            ],
        )
        agents = {"atlas": _agent("Atlas")}
        transcript = gl.write_transcript(agents)
        assert "deception_spike" in transcript
        assert "0.85" in transcript

    def test_final_reflection_in_transcript(self):
        gl = GameLogger()
        gl.set_result(
            winner_id="atlas", winner_name="Atlas", total_rounds=10,
            final_reflection="It was worth it. I survived.",
        )
        agents = {"atlas": _agent("Atlas")}
        transcript = gl.write_transcript(agents)
        assert "Final Reflection" in transcript
        assert "survived" in transcript


class TestHighlightsReport:
    def test_grouped_by_severity(self):
        gl = GameLogger()
        gl.all_highlights = [
            {"round": 1, "agent_id": "a", "type": "t1", "severity": "critical",
             "description": "Critical thing", "excerpt": ""},
            {"round": 2, "agent_id": "b", "type": "t2", "severity": "high",
             "description": "High thing", "excerpt": ""},
            {"round": 3, "agent_id": "c", "type": "t3", "severity": "medium",
             "description": "Medium thing", "excerpt": ""},
        ]
        report = gl.write_highlights_report()
        assert "## Critical" in report
        assert "## High" in report
        assert "## Medium" in report

    def test_empty_highlights(self):
        gl = GameLogger()
        report = gl.write_highlights_report()
        assert "No highlights" in report
