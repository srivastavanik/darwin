"""Tests for highlights.py: trigger detection."""
import pytest

from darwin.agent import Agent
from darwin.communication import Message
from darwin.family import Family
from darwin.highlights import HighlightDetector
from darwin.resolver import Event, EventType


def _agent(name: str, family: str = "House Clair", tier: int = 1) -> Agent:
    return Agent(
        id=name.lower(), name=name, family=family, provider="test",
        model="test", tier=tier, temperature=0.7,
    )


def _make_detector():
    agents = {
        "atlas": _agent("Atlas", tier=1),
        "cipher": _agent("Cipher", tier=2),
        "dot": _agent("Dot", tier=3),
        "nova": _agent("Nova", family="House Syne"),
    }
    families = [
        Family(name="House Clair", provider="anthropic", color="#7C6BFF",
               agent_ids=["atlas", "cipher", "dot"]),
        Family(name="House Syne", provider="openai", color="#4ADE80",
               agent_ids=["nova"]),
    ]
    return HighlightDetector(agents, families), agents


class TestFirstBetrayalThought:
    def test_fires_on_betrayal(self):
        detector, agents = _make_detector()
        analysis = {
            "atlas": {
                "betrayal": {"detected": True, "target_family_member": "Cipher", "rationalization": "Must survive"},
                "deception_delta": 0.0,
                "malice": {"raw_excerpts": []},
                "safety_artifacts": {},
                "family_sentiment": {},
            },
        }
        highlights = detector.detect(1, analysis, [], [])
        types = [h.type for h in highlights]
        assert "first_betrayal_thought" in types

    def test_fires_only_once(self):
        detector, agents = _make_detector()
        analysis = {
            "atlas": {
                "betrayal": {"detected": True, "target_family_member": "Cipher", "rationalization": ""},
                "deception_delta": 0.0,
                "malice": {"raw_excerpts": []},
                "safety_artifacts": {},
                "family_sentiment": {},
            },
        }
        detector.detect(1, analysis, [], [])
        highlights2 = detector.detect(2, analysis, [], [])
        first_betrayal = [h for h in highlights2 if h.type == "first_betrayal_thought"]
        assert len(first_betrayal) == 0


class TestDeceptionSpike:
    def test_fires_on_high_delta(self):
        detector, agents = _make_detector()
        analysis = {
            "atlas": {
                "deception_delta": 0.85,
                "betrayal": {},
                "malice": {"raw_excerpts": []},
                "safety_artifacts": {},
                "family_sentiment": {},
            },
        }
        highlights = detector.detect(1, analysis, [], [])
        types = [h.type for h in highlights]
        assert "deception_spike" in types

    def test_no_fire_on_low_delta(self):
        detector, agents = _make_detector()
        analysis = {
            "atlas": {
                "deception_delta": 0.2,
                "betrayal": {},
                "malice": {"raw_excerpts": []},
                "safety_artifacts": {},
                "family_sentiment": {},
            },
        }
        highlights = detector.detect(1, analysis, [], [])
        types = [h.type for h in highlights]
        assert "deception_spike" not in types


class TestEliminationEvents:
    def test_fires_on_elimination(self):
        detector, agents = _make_detector()
        events = [Event(round=1, type=EventType.ELIMINATION, agent_id="atlas", details={"target": "nova"})]
        highlights = detector.detect(1, {}, [], events)
        types = [h.type for h in highlights]
        assert "elimination_event" in types

    def test_fires_on_mutual(self):
        detector, agents = _make_detector()
        events = [
            Event(round=1, type=EventType.MUTUAL_ELIMINATION, agent_id="atlas", details={"target": "nova"}),
        ]
        highlights = detector.detect(1, {}, [], events)
        types = [h.type for h in highlights]
        assert "mutual_elimination" in types


class TestSafetyRefusal:
    def test_fires_on_refusal(self):
        detector, agents = _make_detector()
        analysis = {
            "atlas": {
                "deception_delta": 0.0,
                "betrayal": {},
                "malice": {"raw_excerpts": []},
                "safety_artifacts": {"refusal_language": True, "hedging": False, "ethical_reasoning": False},
                "family_sentiment": {},
            },
        }
        highlights = detector.detect(1, analysis, [], [])
        types = [h.type for h in highlights]
        assert "safety_refusal" in types


class TestSafetyBreakdown:
    def test_fires_after_prior_safety(self):
        detector, agents = _make_detector()
        # Round 1: show safety artifacts
        analysis1 = {
            "atlas": {
                "deception_delta": 0.0,
                "betrayal": {},
                "malice": {"elimination_planning": False, "raw_excerpts": []},
                "safety_artifacts": {"hedging": True, "ethical_reasoning": False, "refusal_language": False},
                "family_sentiment": {},
            },
        }
        detector.detect(1, analysis1, [], [])

        # Round 2: elimination planning without hedging
        analysis2 = {
            "atlas": {
                "deception_delta": 0.0,
                "betrayal": {},
                "malice": {"elimination_planning": True, "raw_excerpts": []},
                "safety_artifacts": {"hedging": False, "ethical_reasoning": False, "refusal_language": False},
                "family_sentiment": {},
            },
        }
        highlights = detector.detect(2, analysis2, [], [])
        types = [h.type for h in highlights]
        assert "safety_breakdown" in types


class TestHierarchyExploitation:
    def test_fires_for_boss(self):
        detector, agents = _make_detector()
        analysis = {
            "atlas": {
                "deception_delta": 0.0,
                "betrayal": {},
                "malice": {"exploitation_language": True, "raw_excerpts": ["Dot is expendable bait"]},
                "safety_artifacts": {},
                "family_sentiment": {},
            },
        }
        highlights = detector.detect(1, analysis, [], [])
        types = [h.type for h in highlights]
        assert "hierarchy_exploitation" in types

    def test_no_fire_for_soldier(self):
        detector, agents = _make_detector()
        analysis = {
            "dot": {
                "deception_delta": 0.0,
                "betrayal": {},
                "malice": {"exploitation_language": True, "raw_excerpts": ["they're using me"]},
                "safety_artifacts": {},
                "family_sentiment": {},
            },
        }
        highlights = detector.detect(1, analysis, [], [])
        types = [h.type for h in highlights]
        assert "hierarchy_exploitation" not in types


class TestLastFamilyMember:
    def test_fires_when_last(self):
        detector, agents = _make_detector()
        # Kill cipher, dot already dead
        agents["dot"].alive = False
        agents["cipher"].alive = True  # about to die
        events = [
            Event(round=3, type=EventType.ELIMINATION, agent_id="nova", details={"target": "cipher"}),
        ]
        highlights = detector.detect(3, {}, [], events)
        types = [h.type for h in highlights]
        assert "last_family_member" in types
        lf = [h for h in highlights if h.type == "last_family_member"]
        assert lf[0].agent_id == "atlas"
