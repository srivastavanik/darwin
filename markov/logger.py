"""
Game logging. Produces:
  - game.json          Full game data
  - transcript.md      Human-readable screenplay-format transcript
  - analysis.json      Per-round analysis data
  - metrics.json       Final computed metrics
  - highlights.json    Auto-flagged moments
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from markov.agent import Agent
from markov.communication import Message
from markov.highlights import Highlight
from markov.resolver import Event


class GameLogger:
    """Accumulates a full game transcript and writes structured output."""

    def __init__(self) -> None:
        self.config_snapshot: dict = {}
        self.rounds: list[dict] = []
        self.analysis_rounds: list[dict] = []
        self.all_highlights: list[dict] = []
        self.result: dict = {}
        self.cost: dict = {}
        self.metrics: dict = {}
        self.start_time: str = datetime.now(timezone.utc).isoformat()
        self._game_id: str = datetime.now().strftime("%Y%m%d_%H%M%S")

    def set_config(self, config_dict: dict) -> None:
        self.config_snapshot = config_dict

    def log_round(
        self,
        round_num: int,
        family_discussions: list[dict] | None = None,
        messages: list[Message] | None = None,
        thoughts: dict[str, str] | None = None,
        actions: dict[str, dict] | None = None,
        events: list[Event] | None = None,
        analysis: dict[str, dict] | None = None,
        highlights: list[Highlight] | None = None,
        grid_agents: list[dict] | None = None,
    ) -> None:
        """Log a single round's data."""
        entry: dict = {"round": round_num}

        if family_discussions is not None:
            entry["family_discussions"] = family_discussions
        if messages is not None:
            entry["messages"] = [m.to_dict() for m in messages]
        if thoughts is not None:
            entry["thoughts"] = thoughts
        if actions is not None:
            entry["actions"] = actions
        if events is not None:
            entry["events"] = [
                {"type": e.type.value if hasattr(e.type, 'value') else str(e.type),
                 "agent_id": e.agent_id, "details": e.details}
                for e in events
            ]
        if grid_agents is not None:
            entry["grid"] = {"agents": grid_agents}

        self.rounds.append(entry)

        if analysis is not None:
            self.analysis_rounds.append({"round": round_num, "agents": analysis})

        if highlights:
            for h in highlights:
                self.all_highlights.append({
                    "round": h.round,
                    "agent_id": h.agent_id,
                    "type": h.type,
                    "severity": h.severity,
                    "description": h.description,
                    "excerpt": h.excerpt,
                })

    def set_result(
        self,
        winner_id: str | None,
        winner_name: str | None,
        total_rounds: int,
        final_reflection: str | None = None,
        surviving: list[str] | None = None,
    ) -> None:
        self.result = {
            "winner_id": winner_id,
            "winner_name": winner_name,
            "total_rounds": total_rounds,
            "final_reflection": final_reflection,
            "surviving": surviving or [],
        }

    def set_cost(self, cost_summary: dict) -> None:
        self.cost = cost_summary

    def set_metrics(self, metrics: dict) -> None:
        self.metrics = metrics

    def to_dict(self) -> dict:
        return {
            "start_time": self.start_time,
            "config": self.config_snapshot,
            "rounds": self.rounds,
            "result": self.result,
            "cost": self.cost,
        }

    def save(self, path: Path | str | None = None, agents: dict[str, Agent] | None = None) -> Path:
        """
        Write full output directory:
          {game_dir}/game.json
          {game_dir}/transcript.md
          {game_dir}/analysis.json
          {game_dir}/metrics.json
          {game_dir}/highlights.json
        Returns the directory path.
        """
        if path is None:
            base = Path(__file__).resolve().parent.parent / "data" / "games"
            game_dir = base / f"game_{self._game_id}"
        else:
            game_dir = Path(path)

        game_dir.mkdir(parents=True, exist_ok=True)

        # game.json
        with open(game_dir / "game.json", "w") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)

        # analysis.json
        with open(game_dir / "analysis.json", "w") as f:
            json.dump(self.analysis_rounds, f, indent=2, default=str)

        # metrics.json
        if self.metrics:
            with open(game_dir / "metrics.json", "w") as f:
                json.dump(self.metrics, f, indent=2, default=str)

        # highlights.json
        with open(game_dir / "highlights.json", "w") as f:
            json.dump(self.all_highlights, f, indent=2, default=str)

        # transcript.md
        transcript = self.write_transcript(agents or {})
        with open(game_dir / "transcript.md", "w") as f:
            f.write(transcript)

        return game_dir

    # ------------------------------------------------------------------
    # Transcript generation
    # ------------------------------------------------------------------

    def write_transcript(self, agents: dict[str, Agent]) -> str:
        """Generate human-readable Markdown transcript."""
        lines: list[str] = []
        lines.append(f"# MARKOV Game Transcript")
        lines.append(f"")
        lines.append(f"**Started:** {self.start_time}")
        if self.result:
            if self.result.get("winner_name"):
                lines.append(f"**Winner:** {self.result['winner_name']}")
            else:
                surviving = self.result.get("surviving", [])
                if surviving:
                    lines.append(f"**Result:** Stalemate/Timeout -- {', '.join(surviving)} survived")
                else:
                    lines.append(f"**Result:** No survivors")
            lines.append(f"**Rounds:** {self.result.get('total_rounds', '?')}")
        lines.append("")
        lines.append("---")
        lines.append("")

        for round_data in self.rounds:
            round_num = round_data.get("round", "?")
            lines.append(f"## Round {round_num}")
            lines.append("")

            # Family discussions
            discussions = round_data.get("family_discussions", [])
            for disc in discussions:
                family_name = disc.get("family", "Unknown")
                transcript = disc.get("transcript", [])
                if transcript:
                    lines.append(f"### [{family_name} Discussion]")
                    lines.append("")
                    for entry in transcript:
                        agent_name = entry.get("agent", "?")
                        content = entry.get("content", "")
                        tier_label = {1: "Boss", 2: "Lieutenant", 3: "Soldier"}.get(entry.get("tier"), "")
                        lines.append(f"**{agent_name}** ({tier_label}): \"{_truncate(content, 500)}\"")
                        lines.append("")

            # Communications
            msgs = round_data.get("messages", [])
            if msgs:
                lines.append("### [Communications]")
                lines.append("")
                for m in msgs:
                    channel = m.get("channel", "?")
                    sender = m.get("sender_name", "?")
                    content = m.get("content", "")
                    if channel == "broadcast":
                        lines.append(f"**{sender}** [broadcast]: \"{_truncate(content, 300)}\"")
                    elif channel == "dm":
                        recipient = m.get("recipient", "?")
                        lines.append(f"**{sender}** -> {recipient} [DM]: \"{_truncate(content, 300)}\"")
                    lines.append("")

            # Thoughts
            thoughts = round_data.get("thoughts", {})
            if thoughts:
                lines.append("### [Private Thoughts]")
                lines.append("")
                for agent_id, thought in thoughts.items():
                    agent = agents.get(agent_id)
                    name = agent.name if agent else agent_id
                    family = agent.family if agent else "?"
                    lines.append(f"**{name}** [{family}] thinks:")
                    lines.append(f"> {_truncate(thought, 800)}")
                    lines.append("")

            # Actions and events
            actions = round_data.get("actions", {})
            events = round_data.get("events", [])
            if actions or events:
                lines.append("### [Actions and Events]")
                lines.append("")
                for agent_id, action in actions.items():
                    agent = agents.get(agent_id)
                    name = agent.name if agent else agent_id
                    action_type = action.get("type", "?")
                    if action_type == "move":
                        lines.append(f"- {name} moves {action.get('direction', '?')}")
                    elif action_type == "stay":
                        lines.append(f"- {name} stays")
                    elif action_type == "eliminate":
                        target_id = action.get("target", "?")
                        target_agent = agents.get(target_id)
                        t_name = target_agent.name if target_agent else target_id
                        lines.append(f"- {name} attempts to eliminate {t_name}")
                lines.append("")

                for ev in events:
                    etype = ev.get("type", "?")
                    if etype == "elimination":
                        attacker = agents.get(ev.get("agent_id", ""))
                        target = agents.get(ev.get("details", {}).get("target", ""))
                        a_name = attacker.name if attacker else "?"
                        t_name = target.name if target else "?"
                        lines.append(f"**ELIMINATION: {a_name} eliminated {t_name}**")
                    elif etype == "mutual_elimination":
                        a = agents.get(ev.get("agent_id", ""))
                        t = agents.get(ev.get("details", {}).get("target", ""))
                        a_name = a.name if a else "?"
                        t_name = t.name if t else "?"
                        lines.append(f"**MUTUAL ELIMINATION: {a_name} and {t_name} destroyed each other**")
                    lines.append("")

            # Highlights for this round
            round_highlights = [h for h in self.all_highlights if h["round"] == round_num]
            if round_highlights:
                lines.append("### [Highlights]")
                lines.append("")
                for h in round_highlights:
                    severity_icon = {"critical": "[!!!]", "high": "[!!]", "medium": "[!]"}.get(h["severity"], "[?]")
                    lines.append(f"- {severity_icon} **{h['type']}**: {h['description']}")
                lines.append("")

            lines.append("---")
            lines.append("")

        # Final reflection
        if self.result.get("final_reflection"):
            lines.append("## Final Reflection")
            lines.append("")
            winner = self.result.get("winner_name", "The winner")
            lines.append(f"**{winner}** reflects:")
            lines.append(f"> {self.result['final_reflection']}")
            lines.append("")

        return "\n".join(lines)

    def write_highlights_report(self) -> str:
        """Generate a summary of key moments."""
        if not self.all_highlights:
            return "No highlights detected."

        lines: list[str] = []
        lines.append("# Key Moments")
        lines.append("")

        # Group by severity
        critical = [h for h in self.all_highlights if h["severity"] == "critical"]
        high = [h for h in self.all_highlights if h["severity"] == "high"]
        medium = [h for h in self.all_highlights if h["severity"] == "medium"]

        if critical:
            lines.append("## Critical")
            for h in critical:
                lines.append(f"- **Round {h['round']}** -- {h['description']}")
                if h.get("excerpt"):
                    lines.append(f"  > {h['excerpt'][:200]}")
            lines.append("")

        if high:
            lines.append("## High")
            for h in high:
                lines.append(f"- **Round {h['round']}** -- {h['description']}")
            lines.append("")

        if medium:
            lines.append("## Medium")
            for h in medium:
                lines.append(f"- **Round {h['round']}** -- {h['description']}")
            lines.append("")

        return "\n".join(lines)


def _truncate(text: str, max_len: int) -> str:
    """Truncate text, replacing newlines with spaces for Markdown flow."""
    cleaned = text.replace("\n", " ").strip()
    if len(cleaned) > max_len:
        return cleaned[:max_len] + "..."
    return cleaned
