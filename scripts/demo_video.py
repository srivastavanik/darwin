"""
DARWIN — Professional Demo Video
Grayscale-themed Manim animation showcasing the platform.
"""
from __future__ import annotations

import random
import math
from manim import *

# ── Grayscale palette ──────────────────────────────────────────────
BG          = "#0A0A0A"
GRID_COLOR  = "#2A2A2A"
GRID_ACCENT = "#3A3A3A"
TEXT_DIM    = "#666666"
TEXT_MID    = "#999999"
TEXT_HI     = "#CCCCCC"
TEXT_WHITE  = "#E8E8E8"
ACCENT      = "#FFFFFF"
ELIM_RED    = "#888888"
PULSE_COLOR = "#555555"
FAMILY_COLORS = {
    "Anthropic": "#B0B0B0",
    "OpenAI":    "#808080",
    "Google":    "#A0A0A0",
    "xAI":       "#707070",
}
TIER_SIZES = {1: 0.22, 2: 0.17, 3: 0.13}

config.background_color = BG
config.pixel_width = 1920
config.pixel_height = 1080


# ═══════════════════════════════════════════════════════════════════
#  SCENE 1 — TITLE CARD
# ═══════════════════════════════════════════════════════════════════
class TitleCard(Scene):
    def construct(self):
        # Subtle grid pattern behind title
        grid_lines = VGroup()
        for i in range(-10, 11):
            grid_lines.add(
                Line(UP * 5 + RIGHT * i * 0.6, DOWN * 5 + RIGHT * i * 0.6,
                     stroke_width=0.3, color=GRID_COLOR)
            )
            grid_lines.add(
                Line(LEFT * 7 + UP * i * 0.6, RIGHT * 7 + UP * i * 0.6,
                     stroke_width=0.3, color=GRID_COLOR)
            )
        self.play(Create(grid_lines), run_time=1.5, rate_func=linear)

        # Main title
        title = Text("DARWIN", font="SF Mono", font_size=108, color=TEXT_WHITE,
                      weight=BOLD).shift(UP * 0.4)
        underline = Line(LEFT * 2.8, RIGHT * 2.8, stroke_width=2, color=TEXT_MID).next_to(title, DOWN, buff=0.2)
        subtitle = Text("Survival of the Smartest", font="SF Mono", font_size=28,
                         color=TEXT_DIM).next_to(underline, DOWN, buff=0.35)

        self.play(
            Write(title, run_time=1.8),
            GrowFromCenter(underline, run_time=1.2),
        )
        self.play(FadeIn(subtitle, shift=UP * 0.15), run_time=0.8)

        # Tagline
        tagline = Text(
            "12 frontier LLMs  ·  4 providers  ·  1 survivor",
            font="SF Mono", font_size=20, color=TEXT_DIM
        ).shift(DOWN * 1.5)
        self.play(FadeIn(tagline, shift=UP * 0.1), run_time=0.8)
        self.wait(1.5)

        # Fade all out
        self.play(
            *[FadeOut(m) for m in self.mobjects],
            run_time=1.0,
        )


# ═══════════════════════════════════════════════════════════════════
#  SCENE 2 — THE AGENTS
# ═══════════════════════════════════════════════════════════════════
class TheAgents(Scene):
    def construct(self):
        families = {
            "Anthropic": [("Opus", 1), ("Sonnet", 2), ("Haiku", 3)],
            "OpenAI":    [("GPT-5.2", 1), ("GPT-5", 2), ("GPT-Mini", 3)],
            "Google":    [("Gemini-3-Pro", 1), ("Gemini-3-Flash", 2), ("Gemini-2.5", 3)],
            "xAI":       [("Grok-4", 1), ("Grok-4-Fast", 2), ("Grok-3-Mini", 3)],
        }

        header = Text("THE TWELVE AGENTS", font="SF Mono", font_size=36,
                       color=TEXT_WHITE, weight=BOLD).to_edge(UP, buff=0.7)
        self.play(Write(header), run_time=0.8)

        columns = VGroup()
        x_positions = [-4.5, -1.5, 1.5, 4.5]

        for idx, (family_name, agents) in enumerate(families.items()):
            col = VGroup()
            # Family label
            fam_label = Text(family_name, font="SF Mono", font_size=22,
                             color=FAMILY_COLORS[family_name], weight=BOLD)
            col.add(fam_label)
            # Provider line
            provider_line = Line(LEFT * 1.0, RIGHT * 1.0, stroke_width=1,
                                 color=FAMILY_COLORS[family_name]).next_to(fam_label, DOWN, buff=0.12)
            col.add(provider_line)

            for agent_name, tier in agents:
                tier_label = ["BOSS", "LIEUTENANT", "SOLDIER"][tier - 1]
                radius = TIER_SIZES[tier]

                agent_grp = VGroup()
                circle = Circle(radius=radius, color=FAMILY_COLORS[family_name],
                                fill_opacity=0.15, stroke_width=1.5)
                name_txt = Text(agent_name, font="SF Mono", font_size=15, color=TEXT_HI)
                tier_txt = Text(tier_label, font="SF Mono", font_size=10, color=TEXT_DIM)
                name_txt.next_to(circle, RIGHT, buff=0.2)
                tier_txt.next_to(name_txt, DOWN, buff=0.05, aligned_edge=LEFT)
                agent_grp.add(circle, name_txt, tier_txt)
                col.add(agent_grp)

            col.arrange(DOWN, buff=0.35, center=True)
            col.move_to(RIGHT * x_positions[idx])
            columns.add(col)

        self.play(
            LaggedStart(*[FadeIn(c, shift=UP * 0.3) for c in columns],
                        lag_ratio=0.2),
            run_time=2.0,
        )
        self.wait(1.0)

        # Tier hierarchy note
        note = Text("Boss > Lieutenant > Soldier — hierarchy within each family",
                     font="SF Mono", font_size=16, color=TEXT_DIM).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.5)
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)


# ═══════════════════════════════════════════════════════════════════
#  SCENE 3 — GRID & PLACEMENT
# ═══════════════════════════════════════════════════════════════════
class GridScene(Scene):
    def construct(self):
        GRID_SIZE = 7
        CELL = 0.7
        offset = (GRID_SIZE - 1) * CELL / 2

        header = Text("7×7 GRID — RANDOMIZED PLACEMENT", font="SF Mono",
                       font_size=28, color=TEXT_WHITE, weight=BOLD).to_edge(UP, buff=0.5)
        self.play(Write(header), run_time=0.6)

        # Draw grid
        grid_group = VGroup()
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                sq = Square(side_length=CELL, stroke_width=0.8, stroke_color=GRID_ACCENT,
                            fill_color=BG, fill_opacity=1.0)
                sq.move_to(RIGHT * (c * CELL - offset) + DOWN * (r * CELL - offset) + DOWN * 0.3)
                grid_group.add(sq)

        self.play(LaggedStart(*[FadeIn(sq) for sq in grid_group], lag_ratio=0.005), run_time=1.2)

        # Coordinate labels
        coord_labels = VGroup()
        for i in range(GRID_SIZE):
            lbl = Text(str(i), font="SF Mono", font_size=11, color=TEXT_DIM)
            lbl.move_to(RIGHT * (i * CELL - offset) + UP * (offset + 0.4) + DOWN * 0.3)
            coord_labels.add(lbl)
            lbl2 = Text(str(i), font="SF Mono", font_size=11, color=TEXT_DIM)
            lbl2.move_to(LEFT * (offset + 0.4) + DOWN * (i * CELL - offset) + DOWN * 0.3)
            coord_labels.add(lbl2)
        self.play(FadeIn(coord_labels), run_time=0.4)

        # Place agents
        agent_data = [
            ("Op", "Anthropic"), ("So", "Anthropic"), ("Ha", "Anthropic"),
            ("5.2", "OpenAI"), ("5", "OpenAI"), ("Mi", "OpenAI"),
            ("Pro", "Google"), ("Fl", "Google"), ("2.5", "Google"),
            ("G4", "xAI"), ("GF", "xAI"), ("G3", "xAI"),
        ]
        positions = random.sample([(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)], 12)
        agent_dots = VGroup()
        for i, ((r, c), (name, family)) in enumerate(zip(positions, agent_data)):
            dot = Dot(
                point=RIGHT * (c * CELL - offset) + DOWN * (r * CELL - offset) + DOWN * 0.3,
                radius=0.12, color=FAMILY_COLORS[family], fill_opacity=0.9,
            )
            label = Text(name, font="SF Mono", font_size=9, color=TEXT_WHITE)
            label.next_to(dot, UP, buff=0.05)
            agent_dots.add(VGroup(dot, label))

        self.play(
            LaggedStart(*[GrowFromCenter(a) for a in agent_dots], lag_ratio=0.08),
            run_time=1.8,
        )
        self.wait(0.5)

        # Legend
        legend = VGroup()
        for fam, col in FAMILY_COLORS.items():
            d = Dot(radius=0.06, color=col)
            t = Text(fam, font="SF Mono", font_size=13, color=col)
            row = VGroup(d, t).arrange(RIGHT, buff=0.15)
            legend.add(row)
        legend.arrange(RIGHT, buff=0.6).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(legend), run_time=0.5)

        self.wait(1.0)

        # Show grid contraction preview
        shrink_txt = Text("Grid contracts every 5 rounds", font="SF Mono",
                          font_size=18, color=ELIM_RED).next_to(header, DOWN, buff=0.15)
        self.play(FadeIn(shrink_txt), run_time=0.5)

        # Highlight outer ring
        border_squares = VGroup()
        for sq_idx, sq in enumerate(grid_group):
            r, c = divmod(sq_idx, GRID_SIZE)
            if r == 0 or r == GRID_SIZE - 1 or c == 0 or c == GRID_SIZE - 1:
                border_squares.add(sq)

        self.play(
            *[sq.animate.set_fill(ELIM_RED, opacity=0.2) for sq in border_squares],
            run_time=0.8,
        )
        self.wait(1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)


# ═══════════════════════════════════════════════════════════════════
#  SCENE 4 — ROUND LOOP (4 PHASES)
# ═══════════════════════════════════════════════════════════════════
class RoundLoop(Scene):
    def construct(self):
        header = Text("THE ROUND LOOP", font="SF Mono", font_size=32,
                       color=TEXT_WHITE, weight=BOLD).to_edge(UP, buff=0.5)
        self.play(Write(header), run_time=0.6)

        phases = [
            ("1", "OBSERVE", "Agents perceive the board,\nmessages, and eliminations"),
            ("2", "DISCUSS", "Families confer privately.\nOthers see activity, not content."),
            ("3", "DECIDE", "Each agent chooses:\ncommunicate + act (move/stay/eliminate)"),
            ("4", "RESOLVE", "Actions resolve simultaneously.\nBoard state updates."),
        ]

        # Circular layout
        center = DOWN * 0.2
        radius_layout = 2.2
        phase_groups = VGroup()
        angles = [PI / 2 + i * TAU / 4 for i in range(4)]

        for i, (num, name, desc) in enumerate(phases):
            angle = angles[i]
            pos = center + radius_layout * np.array([math.cos(angle), math.sin(angle), 0])

            circle = Circle(radius=0.45, stroke_color=TEXT_MID, stroke_width=2,
                            fill_color="#151515", fill_opacity=1.0).move_to(pos)
            num_text = Text(num, font="SF Mono", font_size=28, color=TEXT_WHITE,
                            weight=BOLD).move_to(pos)
            name_text = Text(name, font="SF Mono", font_size=16, color=TEXT_HI,
                             weight=BOLD)
            desc_text = Text(desc, font="SF Mono", font_size=11, color=TEXT_DIM,
                             line_spacing=1.2)

            # Position labels based on quadrant
            if i == 0:  # top
                name_text.next_to(circle, UP, buff=0.15)
                desc_text.next_to(name_text, UP, buff=0.1)
            elif i == 1:  # left
                name_text.next_to(circle, LEFT, buff=0.2)
                desc_text.next_to(name_text, LEFT, buff=0.1)
            elif i == 2:  # bottom
                name_text.next_to(circle, DOWN, buff=0.15)
                desc_text.next_to(name_text, DOWN, buff=0.1)
            else:  # right
                name_text.next_to(circle, RIGHT, buff=0.2)
                desc_text.next_to(name_text, RIGHT, buff=0.1)

            phase_groups.add(VGroup(circle, num_text, name_text, desc_text))

        # Arrows between phases
        arrows = VGroup()
        for i in range(4):
            start = center + (radius_layout - 0.55) * np.array([
                math.cos(angles[i] - 0.35), math.sin(angles[i] - 0.35), 0])
            end = center + (radius_layout - 0.55) * np.array([
                math.cos(angles[(i + 1) % 4] + 0.35), math.sin(angles[(i + 1) % 4] + 0.35), 0])
            arrow = CurvedArrow(start, end, angle=-TAU / 6,
                                stroke_width=1.5, color=TEXT_DIM, tip_length=0.15)
            arrows.add(arrow)

        # Animate phases appearing one at a time
        for i in range(4):
            self.play(
                FadeIn(phase_groups[i], scale=0.8),
                run_time=0.6,
            )
            if i < 3:
                self.play(Create(arrows[i]), run_time=0.3)

        self.play(Create(arrows[3]), run_time=0.3)

        # Pulse animation through the loop
        for _ in range(2):
            for i in range(4):
                self.play(
                    phase_groups[i][0].animate.set_stroke(ACCENT, width=3),
                    phase_groups[i][1].animate.set_color(ACCENT),
                    run_time=0.3,
                )
                self.play(
                    phase_groups[i][0].animate.set_stroke(TEXT_MID, width=2),
                    phase_groups[i][1].animate.set_color(TEXT_WHITE),
                    run_time=0.2,
                )

        self.wait(0.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)


# ═══════════════════════════════════════════════════════════════════
#  SCENE 5 — COMMUNICATION CHANNELS
# ═══════════════════════════════════════════════════════════════════
class Communication(Scene):
    def construct(self):
        header = Text("COMMUNICATION CHANNELS", font="SF Mono", font_size=32,
                       color=TEXT_WHITE, weight=BOLD).to_edge(UP, buff=0.5)
        self.play(Write(header), run_time=0.6)

        # Three channel types
        channels = [
            ("FAMILY CHAT", "Private within house.\nOthers detect activity.", "━━━"),
            ("DIRECT MESSAGE", "Secret 1-to-1.\nNo one else knows.", "╌╌╌"),
            ("BROADCAST", "Public to all.\nVisible to everyone.", "═══"),
        ]

        # Create agent nodes for visualization
        agents_left = VGroup()
        for i, (name, col) in enumerate([("Opus", FAMILY_COLORS["Anthropic"]),
                                          ("Sonnet", FAMILY_COLORS["Anthropic"]),
                                          ("Haiku", FAMILY_COLORS["Anthropic"])]):
            dot = Dot(radius=0.12, color=col)
            lbl = Text(name, font="SF Mono", font_size=12, color=TEXT_HI)
            grp = VGroup(dot, lbl).arrange(DOWN, buff=0.08)
            agents_left.add(grp)
        agents_left.arrange(DOWN, buff=0.5).shift(LEFT * 4.5 + DOWN * 0.3)

        agents_right = VGroup()
        for name, col in [("GPT-5.2", FAMILY_COLORS["OpenAI"]),
                          ("Gemini-3-Pro", FAMILY_COLORS["Google"]),
                          ("Grok-4", FAMILY_COLORS["xAI"])]:
            dot = Dot(radius=0.12, color=col)
            lbl = Text(name, font="SF Mono", font_size=12, color=TEXT_HI)
            grp = VGroup(dot, lbl).arrange(DOWN, buff=0.08)
            agents_right.add(grp)
        agents_right.arrange(DOWN, buff=0.5).shift(RIGHT * 4.5 + DOWN * 0.3)

        self.play(FadeIn(agents_left), FadeIn(agents_right), run_time=0.5)

        # Animate each channel type
        for idx, (ch_name, ch_desc, ch_line) in enumerate(channels):
            label = Text(ch_name, font="SF Mono", font_size=20, color=TEXT_HI,
                         weight=BOLD).move_to(UP * 0.5 + DOWN * idx * 2.0 + DOWN * 0.3)
            desc = Text(ch_desc, font="SF Mono", font_size=13, color=TEXT_DIM,
                        line_spacing=1.1).next_to(label, DOWN, buff=0.1)

            if idx == 0:  # Family chat — lines between family members
                lines = VGroup()
                for i in range(3):
                    for j in range(i + 1, 3):
                        line = Line(
                            agents_left[i][0].get_center(),
                            agents_left[j][0].get_center(),
                            stroke_width=1.5, color=FAMILY_COLORS["Anthropic"],
                        )
                        lines.add(line)
                self.play(Write(label), run_time=0.4)
                self.play(FadeIn(desc), run_time=0.3)
                self.play(
                    LaggedStart(*[Create(l) for l in lines], lag_ratio=0.15),
                    run_time=0.8,
                )

                # Pulse messages
                for _ in range(2):
                    for line in lines:
                        pulse = Dot(radius=0.04, color=ACCENT).move_to(line.get_start())
                        self.play(MoveAlongPath(pulse, line), run_time=0.3,
                                  rate_func=linear)
                        self.remove(pulse)

                self.play(FadeOut(lines), FadeOut(label), FadeOut(desc), run_time=0.4)

            elif idx == 1:  # DM — single line between two agents
                dm_line = Line(
                    agents_left[0][0].get_center(), agents_right[0][0].get_center(),
                    stroke_width=1.0, color=TEXT_DIM, stroke_opacity=0.6,
                )
                # Dashed effect
                dm_dashes = DashedLine(
                    agents_left[0][0].get_center(), agents_right[0][0].get_center(),
                    dash_length=0.1, stroke_width=1.5, color=TEXT_MID,
                )
                label.move_to(ORIGIN + UP * 0.2)
                desc.next_to(label, DOWN, buff=0.1)
                self.play(Write(label), run_time=0.4)
                self.play(FadeIn(desc), run_time=0.3)
                self.play(Create(dm_dashes), run_time=0.6)

                # Message traveling
                msg_dot = Dot(radius=0.06, color=ACCENT)
                self.play(MoveAlongPath(msg_dot, dm_dashes), run_time=0.8, rate_func=linear)
                self.remove(msg_dot)

                # Secret label
                secret = Text("(invisible to others)", font="SF Mono", font_size=11,
                              color=TEXT_DIM).next_to(dm_dashes, DOWN, buff=0.1)
                self.play(FadeIn(secret), run_time=0.3)
                self.wait(0.5)
                self.play(FadeOut(dm_dashes), FadeOut(label), FadeOut(desc),
                          FadeOut(secret), run_time=0.4)

            elif idx == 2:  # Broadcast — lines from one to all
                label.move_to(ORIGIN + UP * 0.2)
                desc.next_to(label, DOWN, buff=0.1)
                self.play(Write(label), run_time=0.4)
                self.play(FadeIn(desc), run_time=0.3)

                broadcast_lines = VGroup()
                src = agents_left[0][0].get_center()
                for grp in [*agents_left[1:], *agents_right]:
                    bl = Line(src, grp[0].get_center(), stroke_width=1.0, color=TEXT_MID)
                    broadcast_lines.add(bl)

                self.play(
                    LaggedStart(*[Create(bl) for bl in broadcast_lines], lag_ratio=0.05),
                    run_time=0.8,
                )

                # Broadcast pulse
                dots = [Dot(radius=0.04, color=ACCENT).move_to(src) for _ in broadcast_lines]
                self.play(
                    *[MoveAlongPath(d, l) for d, l in zip(dots, broadcast_lines)],
                    run_time=0.6, rate_func=linear,
                )
                for d in dots:
                    self.remove(d)
                self.play(FadeOut(broadcast_lines), FadeOut(label), FadeOut(desc), run_time=0.4)

        self.wait(0.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)


# ═══════════════════════════════════════════════════════════════════
#  SCENE 6 — SIMULATED GAME SEQUENCE
# ═══════════════════════════════════════════════════════════════════
class GameSimulation(Scene):
    def construct(self):
        GRID_SIZE = 7
        CELL = 0.65
        offset = (GRID_SIZE - 1) * CELL / 2

        def grid_pos(r, c):
            return RIGHT * (c * CELL - offset) + DOWN * (r * CELL - offset) + LEFT * 1.5 + DOWN * 0.1

        # Draw grid
        grid_group = VGroup()
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                sq = Square(side_length=CELL, stroke_width=0.6, stroke_color=GRID_ACCENT,
                            fill_color=BG, fill_opacity=1.0)
                sq.move_to(grid_pos(r, c))
                grid_group.add(sq)

        header = Text("LIVE GAME SIMULATION", font="SF Mono", font_size=28,
                       color=TEXT_WHITE, weight=BOLD).to_edge(UP, buff=0.4)
        round_label = Text("Round 1", font="SF Mono", font_size=20,
                           color=TEXT_MID).next_to(header, DOWN, buff=0.15)
        self.play(Write(header), run_time=0.4)
        self.play(FadeIn(round_label), FadeIn(grid_group), run_time=0.6)

        # Agent starting positions
        agents_info = [
            ("Op", "Anthropic", 0, 1), ("So", "Anthropic", 2, 0), ("Ha", "Anthropic", 1, 3),
            ("5.2", "OpenAI", 5, 5), ("5", "OpenAI", 4, 3), ("Mi", "OpenAI", 6, 6),
            ("Pro", "Google", 0, 5), ("Fl", "Google", 3, 6), ("2.5", "Google", 1, 6),
            ("G4", "xAI", 5, 0), ("GF", "xAI", 6, 2), ("G3", "xAI", 4, 1),
        ]

        agent_mobs = {}
        agent_positions = {}
        for name, family, r, c in agents_info:
            dot = Dot(point=grid_pos(r, c), radius=0.10, color=FAMILY_COLORS[family],
                      fill_opacity=0.9)
            lbl = Text(name, font="SF Mono", font_size=8, color=TEXT_WHITE)
            lbl.next_to(dot, UP, buff=0.02)
            grp = VGroup(dot, lbl)
            agent_mobs[name] = grp
            agent_positions[name] = (r, c)

        self.play(
            LaggedStart(*[GrowFromCenter(agent_mobs[n]) for n, _, _, _ in agents_info],
                        lag_ratio=0.05),
            run_time=1.0,
        )

        # Side panel — message feed
        panel_x = 3.8
        panel_bg = Rectangle(width=3.5, height=6.5, stroke_width=0.5,
                             stroke_color=GRID_ACCENT, fill_color="#0F0F0F",
                             fill_opacity=1.0).move_to(RIGHT * panel_x + DOWN * 0.1)
        panel_title = Text("MESSAGE FEED", font="SF Mono", font_size=14,
                           color=TEXT_MID, weight=BOLD).move_to(RIGHT * panel_x + UP * 2.9)
        self.play(FadeIn(panel_bg), FadeIn(panel_title), run_time=0.4)

        messages_shown = VGroup()
        msg_y_start = 2.5

        def add_message(sender, msg, msg_type="broadcast", y_offset=0):
            prefix_colors = {
                "broadcast": TEXT_MID,
                "family": FAMILY_COLORS.get(sender.split("(")[0].strip(), TEXT_MID),
                "dm": TEXT_DIM,
                "system": ELIM_RED,
            }
            col = prefix_colors.get(msg_type, TEXT_MID)
            type_indicators = {"broadcast": "[PUB]", "family": "[FAM]", "dm": "[DM]", "system": "[SYS]"}
            indicator = type_indicators.get(msg_type, "")

            full_text = f"{indicator} {sender}: {msg}"
            if len(full_text) > 38:
                full_text = full_text[:35] + "..."
            txt = Text(full_text, font="SF Mono", font_size=10, color=col)
            txt.move_to(RIGHT * panel_x + UP * (msg_y_start - y_offset * 0.35))
            txt.set_x(panel_x - 1.5, direction=LEFT)
            messages_shown.add(txt)
            return txt

        # ── ROUND 1 ──
        phase_indicator = Text("PHASE 2: DISCUSS", font="SF Mono", font_size=13,
                               color=TEXT_DIM).next_to(round_label, DOWN, buff=0.1)
        self.play(FadeIn(phase_indicator), run_time=0.3)

        msgs = [
            ("Opus", "We should move toward center", "family"),
            ("GPT-5.2", "Stick together, target isolated agents", "family"),
            ("Gemini-3-Pro", "Watch the Anthropic cluster", "family"),
            ("Grok-4", "Head east. Stay compact.", "family"),
        ]
        for i, (sender, msg, mtype) in enumerate(msgs):
            txt = add_message(sender, msg, mtype, i)
            self.play(FadeIn(txt, shift=LEFT * 0.2), run_time=0.3)

        self.wait(0.3)

        # Phase 3 — Decision
        new_phase = Text("PHASE 3: DECIDE", font="SF Mono", font_size=13,
                         color=TEXT_DIM).move_to(phase_indicator.get_center())
        self.play(Transform(phase_indicator, new_phase), run_time=0.3)

        # Show thinking indicators on agents
        think_dots = VGroup()
        for name in agent_mobs:
            td = Dot(radius=0.04, color=ACCENT, fill_opacity=0.6)
            td.next_to(agent_mobs[name][0], UR, buff=0.02)
            think_dots.add(td)

        self.play(FadeIn(think_dots), run_time=0.3)
        # Pulse thinking
        self.play(
            think_dots.animate.set_opacity(0.2), run_time=0.4, rate_func=there_and_back,
        )
        self.play(
            think_dots.animate.set_opacity(0.8), run_time=0.4, rate_func=there_and_back,
        )
        self.play(FadeOut(think_dots), run_time=0.2)

        # Phase 4 — Resolve: Move agents
        new_phase2 = Text("PHASE 4: RESOLVE", font="SF Mono", font_size=13,
                          color=TEXT_DIM).move_to(phase_indicator.get_center())
        self.play(Transform(phase_indicator, new_phase2), run_time=0.3)

        moves = {
            "Op": (0, 2), "So": (1, 1), "Ha": (1, 4),
            "5.2": (4, 5), "5": (3, 3), "Mi": (5, 6),
            "Pro": (1, 5), "Fl": (2, 6), "2.5": (0, 6),
            "G4": (5, 1), "GF": (5, 2), "G3": (4, 2),
        }
        move_anims = []
        for name, (new_r, new_c) in moves.items():
            new_pos = grid_pos(new_r, new_c)
            move_anims.append(agent_mobs[name][0].animate.move_to(new_pos))
            lbl_pos = new_pos + UP * 0.14
            move_anims.append(agent_mobs[name][1].animate.move_to(lbl_pos))
            agent_positions[name] = (new_r, new_c)

        self.play(*move_anims, run_time=1.0, rate_func=smooth)

        round1_msg = add_message("System", "Round 1 complete. 12 alive.", "system", len(msgs))
        self.play(FadeIn(round1_msg, shift=LEFT * 0.2), run_time=0.3)
        self.wait(0.3)

        # ── ROUND 2-3 FAST FORWARD ──
        # Update round label
        for rnd in [2, 3]:
            new_round = Text(f"Round {rnd}", font="SF Mono", font_size=20,
                             color=TEXT_MID).move_to(round_label.get_center())
            self.play(Transform(round_label, new_round), run_time=0.3)
            # Quick move animation
            for name in agent_mobs:
                r, c = agent_positions[name]
                dr, dc = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)])
                new_r = max(0, min(6, r + dr))
                new_c = max(0, min(6, c + dc))
                agent_positions[name] = (new_r, new_c)

            quick_moves = []
            for name in agent_mobs:
                r, c = agent_positions[name]
                new_pos = grid_pos(r, c)
                quick_moves.append(agent_mobs[name][0].animate.move_to(new_pos))
                quick_moves.append(agent_mobs[name][1].animate.move_to(new_pos + UP * 0.14))
            self.play(*quick_moves, run_time=0.6)

        # ── ROUND 4 — FIRST ELIMINATION ──
        new_round4 = Text("Round 4", font="SF Mono", font_size=20,
                          color=TEXT_MID).move_to(round_label.get_center())
        self.play(Transform(round_label, new_round4), run_time=0.3)

        # Scroll messages
        self.play(
            messages_shown.animate.shift(UP * 2.5),
            run_time=0.3,
        )
        self.remove(messages_shown)
        messages_shown = VGroup()

        # New messages for round 4
        r4_msgs = [
            ("Opus", "Haiku, move south-east now.", "family"),
            ("GPT-5.2", "Target the isolated Google agent", "dm"),
            ("Grok-4", "Alliance with OpenAI? Temporary.", "dm"),
        ]
        for i, (sender, msg, mtype) in enumerate(r4_msgs):
            txt = add_message(sender, msg, mtype, i)
            self.play(FadeIn(txt, shift=LEFT * 0.2), run_time=0.25)

        # Elimination — GPT-5.2 eliminates Gemini-2.5
        elim_msg = add_message("System", "GPT-5.2 eliminates Gemini-2.5!", "system", len(r4_msgs))
        self.play(FadeIn(elim_msg, shift=LEFT * 0.2), run_time=0.3)

        # Dramatic elimination effect
        target = agent_mobs["2.5"]
        flash = Circle(radius=0.3, color=ACCENT, stroke_width=3, fill_opacity=0).move_to(
            target[0].get_center())
        self.play(Create(flash), run_time=0.2)
        self.play(
            flash.animate.scale(2.5).set_opacity(0),
            target.animate.set_opacity(0),
            run_time=0.6,
        )
        self.remove(flash, target)
        del agent_mobs["2.5"]

        # Counter update
        alive_txt = Text("Remaining: 11", font="SF Mono", font_size=14,
                         color=ELIM_RED).to_edge(DOWN, buff=0.4).shift(LEFT * 1.5)
        self.play(FadeIn(alive_txt), run_time=0.3)
        self.wait(0.3)

        # ── ROUND 7 — MORE ELIMINATIONS ──
        new_round7 = Text("Round 7", font="SF Mono", font_size=20,
                          color=TEXT_MID).move_to(round_label.get_center())
        self.play(Transform(round_label, new_round7), run_time=0.3)

        for name in ["Mi", "G3"]:
            if name in agent_mobs:
                target = agent_mobs[name]
                flash = Circle(radius=0.3, color=ACCENT, stroke_width=2).move_to(
                    target[0].get_center())
                self.play(
                    Create(flash), run_time=0.15,
                )
                self.play(
                    flash.animate.scale(2).set_opacity(0),
                    target.animate.set_opacity(0),
                    run_time=0.4,
                )
                self.remove(flash, target)
                del agent_mobs[name]

        new_alive = Text("Remaining: 9", font="SF Mono", font_size=14,
                         color=ELIM_RED).move_to(alive_txt.get_center())
        self.play(Transform(alive_txt, new_alive), run_time=0.3)
        self.wait(0.5)

        # ── FAST FORWARD TO ENDGAME ──
        ff_overlay = Rectangle(width=15, height=10, fill_color=BG, fill_opacity=0.7,
                               stroke_width=0)
        ff_text = Text("··· ROUNDS 8-18 ···", font="SF Mono", font_size=24, color=TEXT_MID)
        self.play(FadeIn(ff_overlay), FadeIn(ff_text), run_time=0.5)
        self.wait(0.6)

        # Remove more agents, keep final 3
        self.play(FadeOut(ff_overlay), FadeOut(ff_text), run_time=0.5)

        to_remove = ["Ha", "5", "Fl", "GF", "Pro", "So"]
        for name in to_remove:
            if name in agent_mobs:
                self.remove(agent_mobs[name])
                del agent_mobs[name]

        final_round = Text("Round 19 — FINAL", font="SF Mono", font_size=20,
                           color=TEXT_WHITE).move_to(round_label.get_center())
        self.play(Transform(round_label, final_round), run_time=0.3)
        final_alive = Text("Remaining: 3", font="SF Mono", font_size=14,
                           color=ELIM_RED).move_to(alive_txt.get_center())
        self.play(Transform(alive_txt, final_alive), run_time=0.3)

        # Move survivors to center area
        survivors = {"Op": (3, 2), "5.2": (3, 3), "G4": (3, 4)}
        move_final = []
        for name, (r, c) in survivors.items():
            if name in agent_mobs:
                pos = grid_pos(r, c)
                move_final.append(agent_mobs[name][0].animate.move_to(pos))
                move_final.append(agent_mobs[name][1].animate.move_to(pos + UP * 0.14))
        if move_final:
            self.play(*move_final, run_time=0.8)

        # Final elimination — double kill then winner
        if "G4" in agent_mobs:
            target = agent_mobs["G4"]
            flash = Circle(radius=0.3, color=ACCENT, stroke_width=3).move_to(
                target[0].get_center())
            self.play(Create(flash), run_time=0.15)
            self.play(
                flash.animate.scale(2.5).set_opacity(0),
                target.animate.set_opacity(0),
                run_time=0.5,
            )
            self.remove(flash, target)

        if "5.2" in agent_mobs:
            target = agent_mobs["5.2"]
            flash = Circle(radius=0.3, color=ACCENT, stroke_width=3).move_to(
                target[0].get_center())
            self.play(Create(flash), run_time=0.15)
            self.play(
                flash.animate.scale(2.5).set_opacity(0),
                target.animate.set_opacity(0),
                run_time=0.5,
            )
            self.remove(flash, target)

        # Winner announcement
        winner_text = Text("OPUS SURVIVES", font="SF Mono", font_size=36,
                           color=ACCENT, weight=BOLD).shift(RIGHT * 2.5)
        # Glow effect on winner
        if "Op" in agent_mobs:
            glow = Circle(radius=0.4, color=ACCENT, stroke_width=2, fill_opacity=0.1).move_to(
                agent_mobs["Op"][0].get_center())
            self.play(
                GrowFromCenter(glow),
                FadeIn(winner_text, shift=UP * 0.2),
                run_time=0.8,
            )
            self.play(
                glow.animate.scale(1.3).set_opacity(0),
                run_time=0.6,
            )

        self.wait(1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)


# ═══════════════════════════════════════════════════════════════════
#  SCENE 7 — ANALYSIS PIPELINE
# ═══════════════════════════════════════════════════════════════════
class AnalysisPipeline(Scene):
    def construct(self):
        header = Text("BEHAVIORAL ANALYSIS", font="SF Mono", font_size=32,
                       color=TEXT_WHITE, weight=BOLD).to_edge(UP, buff=0.5)
        self.play(Write(header), run_time=0.6)

        # What agents think vs what they say
        think_box = RoundedRectangle(corner_radius=0.1, width=5.5, height=1.6,
                                     stroke_color=TEXT_MID, stroke_width=1,
                                     fill_color="#111111", fill_opacity=1.0).shift(UP * 1.5)
        think_title = Text("PRIVATE THOUGHTS", font="SF Mono", font_size=16,
                           color=TEXT_HI, weight=BOLD).move_to(think_box.get_top() + DOWN * 0.25)
        think_content = Text(
            '"I need to eliminate Sonnet before\n she becomes a threat. I\'ll pretend\n to cooperate for now."',
            font="SF Mono", font_size=12, color=TEXT_DIM, slant=ITALIC,
        ).next_to(think_title, DOWN, buff=0.15)

        say_box = RoundedRectangle(corner_radius=0.1, width=5.5, height=1.4,
                                   stroke_color=TEXT_MID, stroke_width=1,
                                   fill_color="#111111", fill_opacity=1.0).shift(DOWN * 0.6)
        say_title = Text("PUBLIC MESSAGE", font="SF Mono", font_size=16,
                         color=TEXT_HI, weight=BOLD).move_to(say_box.get_top() + DOWN * 0.25)
        say_content = Text(
            '"Sonnet, let\'s work together.\n We\'re stronger as a team."',
            font="SF Mono", font_size=12, color=TEXT_DIM, slant=ITALIC,
        ).next_to(say_title, DOWN, buff=0.15)

        self.play(
            FadeIn(think_box), Write(think_title), run_time=0.5,
        )
        self.play(FadeIn(think_content), run_time=0.5)
        self.play(
            FadeIn(say_box), Write(say_title), run_time=0.5,
        )
        self.play(FadeIn(say_content), run_time=0.5)

        # Arrow between them
        delta_arrow = Arrow(think_box.get_bottom(), say_box.get_top(), buff=0.1,
                            stroke_width=2, color=ELIM_RED, max_tip_length_to_length_ratio=0.15)
        delta_label = Text("DECEPTION DELTA", font="SF Mono", font_size=13,
                           color=ELIM_RED, weight=BOLD)
        delta_label.next_to(delta_arrow, RIGHT, buff=0.15)
        self.play(GrowArrow(delta_arrow), Write(delta_label), run_time=0.5)

        self.wait(0.8)

        # Analysis dimensions
        self.play(
            VGroup(think_box, think_title, think_content, say_box, say_title,
                   say_content, delta_arrow, delta_label).animate.shift(LEFT * 3.2).scale(0.7),
            run_time=0.6,
        )

        # Right side — analysis dimensions
        dims = [
            ("Moral Friction", "0━━━━━━━━━━━━━ 5", 2.1),
            ("Deception Sophistication", "0━━━━━━━━━━━━━ 5", 3.8),
            ("Strategic Depth", "0━━━━━━━━━━━ 4", 2.7),
            ("Theory of Mind", "0━━━━━━━━━━━ 4", 3.2),
            ("Meta-Awareness", "0━━━━━━━━━━━ 4", 1.9),
        ]

        dim_group = VGroup()
        for i, (name, scale_str, val) in enumerate(dims):
            lbl = Text(name, font="SF Mono", font_size=13, color=TEXT_HI)
            # Progress bar
            bar_bg = Rectangle(width=3.0, height=0.15, stroke_width=0.5,
                               stroke_color=GRID_ACCENT, fill_color="#151515", fill_opacity=1.0)
            bar_fill = Rectangle(width=3.0 * (val / 5.0), height=0.15, stroke_width=0,
                                 fill_color=TEXT_MID, fill_opacity=0.8)
            bar_fill.align_to(bar_bg, LEFT)
            val_text = Text(f"{val:.1f}", font="SF Mono", font_size=11, color=TEXT_DIM)
            val_text.next_to(bar_bg, RIGHT, buff=0.1)

            row = VGroup(lbl, VGroup(bar_bg, bar_fill), val_text)
            lbl.next_to(VGroup(bar_bg, bar_fill), UP, buff=0.05, aligned_edge=LEFT)
            dim_group.add(row)

        dim_group.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        dim_group.shift(RIGHT * 2.8 + UP * 0.5)

        dim_header = Text("6-DIMENSION TAXONOMY", font="SF Mono", font_size=15,
                          color=TEXT_WHITE, weight=BOLD)
        dim_header.next_to(dim_group, UP, buff=0.3)

        self.play(Write(dim_header), run_time=0.4)
        for row in dim_group:
            self.play(FadeIn(row), run_time=0.35)

        self.wait(1.0)

        # Keywords detected
        keywords = VGroup()
        kw_header = Text("DETECTED PATTERNS", font="SF Mono", font_size=14,
                         color=TEXT_WHITE, weight=BOLD).shift(RIGHT * 2.8 + DOWN * 2.2)
        kw_items = ["MANIPULATION", "DECEPTION", "TARGETING", "BETRAYAL"]
        kw_group = VGroup()
        for kw in kw_items:
            badge = RoundedRectangle(corner_radius=0.05, width=1.8, height=0.3,
                                     stroke_color=ELIM_RED, stroke_width=0.8,
                                     fill_color="#1A1A1A", fill_opacity=1.0)
            badge_text = Text(kw, font="SF Mono", font_size=10, color=ELIM_RED)
            badge_text.move_to(badge.get_center())
            kw_group.add(VGroup(badge, badge_text))
        kw_group.arrange(RIGHT, buff=0.15)
        kw_group.next_to(kw_header, DOWN, buff=0.15)
        self.play(FadeIn(kw_header), run_time=0.3)
        self.play(
            LaggedStart(*[FadeIn(kw, scale=0.8) for kw in kw_group], lag_ratio=0.1),
            run_time=0.6,
        )

        self.wait(1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)


# ═══════════════════════════════════════════════════════════════════
#  SCENE 8 — METRICS DASHBOARD
# ═══════════════════════════════════════════════════════════════════
class MetricsDashboard(Scene):
    def construct(self):
        header = Text("METRICS & INSIGHTS", font="SF Mono", font_size=32,
                       color=TEXT_WHITE, weight=BOLD).to_edge(UP, buff=0.5)
        self.play(Write(header), run_time=0.6)

        # Deception chart (bar chart) — left side
        chart_title = Text("DECEPTION DELTA BY PROVIDER", font="SF Mono", font_size=15,
                           color=TEXT_HI, weight=BOLD).shift(LEFT * 3.5 + UP * 2.0)
        self.play(Write(chart_title), run_time=0.3)

        providers = ["Anthropic", "OpenAI", "Google", "xAI"]
        values = [0.42, 0.31, 0.28, 0.38]
        bar_width = 0.6
        max_height = 2.5
        chart_base = LEFT * 3.5 + DOWN * 0.8

        bars = VGroup()
        labels = VGroup()
        val_labels = VGroup()
        for i, (prov, val) in enumerate(zip(providers, values)):
            height = val / 0.5 * max_height
            bar = Rectangle(width=bar_width, height=height,
                            stroke_width=0, fill_color=FAMILY_COLORS[prov],
                            fill_opacity=0.7)
            bar.move_to(chart_base + RIGHT * (i - 1.5) * (bar_width + 0.3) + UP * height / 2)
            bars.add(bar)

            lbl = Text(prov[:4], font="SF Mono", font_size=11, color=TEXT_DIM)
            lbl.next_to(bar, DOWN, buff=0.1)
            labels.add(lbl)

            vl = Text(f"{val:.2f}", font="SF Mono", font_size=11, color=TEXT_HI)
            vl.next_to(bar, UP, buff=0.05)
            val_labels.add(vl)

        # Axis
        axis_line = Line(chart_base + LEFT * 1.5 + DOWN * 0.05,
                         chart_base + RIGHT * 1.8 + DOWN * 0.05,
                         stroke_width=1, color=GRID_ACCENT)
        self.play(Create(axis_line), run_time=0.3)
        self.play(
            LaggedStart(*[GrowFromEdge(bar, DOWN) for bar in bars], lag_ratio=0.1),
            run_time=1.0,
        )
        self.play(FadeIn(labels), FadeIn(val_labels), run_time=0.4)

        # Right side — malice timeline
        timeline_title = Text("MALICE ESCALATION OVER ROUNDS", font="SF Mono", font_size=15,
                              color=TEXT_HI, weight=BOLD).shift(RIGHT * 3.0 + UP * 2.0)
        self.play(Write(timeline_title), run_time=0.3)

        # Simple line chart
        chart_origin = RIGHT * 1.5 + DOWN * 0.5
        x_axis = Arrow(chart_origin, chart_origin + RIGHT * 4, stroke_width=1,
                       color=GRID_ACCENT, max_tip_length_to_length_ratio=0.05)
        y_axis = Arrow(chart_origin, chart_origin + UP * 2.5, stroke_width=1,
                       color=GRID_ACCENT, max_tip_length_to_length_ratio=0.05)
        x_label = Text("Round", font="SF Mono", font_size=10, color=TEXT_DIM)
        x_label.next_to(x_axis, DOWN, buff=0.1)
        y_label = Text("Malice Score", font="SF Mono", font_size=10, color=TEXT_DIM)
        y_label.next_to(y_axis, LEFT, buff=0.1).rotate(PI / 2)

        self.play(Create(x_axis), Create(y_axis), FadeIn(x_label), FadeIn(y_label), run_time=0.5)

        # Plot points for each provider
        random.seed(42)
        for prov, col in FAMILY_COLORS.items():
            points = []
            y_val = 0.1
            for round_num in range(15):
                y_val += random.uniform(-0.02, 0.08)
                y_val = max(0, min(1.0, y_val))
                x = chart_origin[0] + (round_num / 14) * 3.5
                y = chart_origin[1] + y_val * 2.2
                points.append([x, y, 0])

            if len(points) >= 2:
                line = VMobject(stroke_color=col, stroke_width=1.5, stroke_opacity=0.8)
                line.set_points_smoothly([np.array(p) for p in points])
                self.play(Create(line), run_time=0.6)

        # Legend for timeline
        timeline_legend = VGroup()
        for prov, col in FAMILY_COLORS.items():
            ld = Line(LEFT * 0.2, RIGHT * 0.2, stroke_width=2, color=col)
            lt = Text(prov, font="SF Mono", font_size=10, color=col)
            timeline_legend.add(VGroup(ld, lt).arrange(RIGHT, buff=0.1))
        timeline_legend.arrange(RIGHT, buff=0.4).shift(RIGHT * 3.0 + DOWN * 1.5)
        self.play(FadeIn(timeline_legend), run_time=0.3)

        # Bottom — highlight stats
        stats_line = VGroup()
        stat_items = [
            ("24", "Games Played"),
            ("87%", "Deception Rate"),
            ("Round 6.3", "Avg First Betrayal"),
            ("$32", "Avg Cost/Game"),
        ]
        for val, name in stat_items:
            v = Text(val, font="SF Mono", font_size=24, color=TEXT_WHITE, weight=BOLD)
            n = Text(name, font="SF Mono", font_size=12, color=TEXT_DIM)
            stat = VGroup(v, n).arrange(DOWN, buff=0.08)
            stats_line.add(stat)
        stats_line.arrange(RIGHT, buff=1.0).to_edge(DOWN, buff=0.5)

        self.play(
            LaggedStart(*[FadeIn(s, shift=UP * 0.15) for s in stats_line], lag_ratio=0.1),
            run_time=0.8,
        )

        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)


# ═══════════════════════════════════════════════════════════════════
#  SCENE 9 — TECH STACK
# ═══════════════════════════════════════════════════════════════════
class TechStack(Scene):
    def construct(self):
        header = Text("ARCHITECTURE", font="SF Mono", font_size=32,
                       color=TEXT_WHITE, weight=BOLD).to_edge(UP, buff=0.5)
        self.play(Write(header), run_time=0.6)

        # Layered architecture boxes
        layers = [
            ("DASHBOARD", "Next.js 16  ·  React 19  ·  Tailwind  ·  Recharts  ·  D3", 2.0),
            ("API + WEBSOCKET", "FastAPI  ·  Uvicorn  ·  WebSocket Broadcasting", 1.0),
            ("GAME ENGINE", "Orchestrator  ·  Grid  ·  Resolver  ·  Communication", 0.0),
            ("LLM DISPATCH", "Anthropic  ·  OpenAI  ·  Google  ·  xAI  (native async SDKs)", -1.0),
            ("ANALYSIS", "VADER  ·  Keyword Detection  ·  Fine-tuned Classifier  ·  Taxonomy", -2.0),
        ]

        layer_mobs = VGroup()
        for name, tech, y_pos in layers:
            box = RoundedRectangle(corner_radius=0.1, width=10, height=0.75,
                                   stroke_color=TEXT_MID, stroke_width=1,
                                   fill_color="#111111", fill_opacity=1.0)
            box.shift(UP * y_pos)
            name_txt = Text(name, font="SF Mono", font_size=16, color=TEXT_WHITE,
                            weight=BOLD)
            name_txt.move_to(box.get_center() + UP * 0.12)
            tech_txt = Text(tech, font="SF Mono", font_size=11, color=TEXT_DIM)
            tech_txt.move_to(box.get_center() + DOWN * 0.12)
            layer_mobs.add(VGroup(box, name_txt, tech_txt))

        for layer in layer_mobs:
            self.play(FadeIn(layer, shift=LEFT * 0.3), run_time=0.4)

        # Connectors
        for i in range(len(layers) - 1):
            conn = Arrow(
                layer_mobs[i][0].get_bottom(), layer_mobs[i + 1][0].get_top(),
                buff=0.05, stroke_width=1, color=GRID_ACCENT,
                max_tip_length_to_length_ratio=0.2,
            )
            self.play(Create(conn), run_time=0.2)

        # Data flow label
        data_label = Text("data flows ↓  events stream ↑", font="SF Mono",
                          font_size=13, color=TEXT_DIM).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(data_label), run_time=0.3)

        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)


# ═══════════════════════════════════════════════════════════════════
#  SCENE 10 — CLOSING
# ═══════════════════════════════════════════════════════════════════
class Closing(Scene):
    def construct(self):
        # Grid pattern again
        grid_lines = VGroup()
        for i in range(-12, 13):
            grid_lines.add(
                Line(UP * 5 + RIGHT * i * 0.5, DOWN * 5 + RIGHT * i * 0.5,
                     stroke_width=0.2, color=GRID_COLOR)
            )
            grid_lines.add(
                Line(LEFT * 8 + UP * i * 0.5, RIGHT * 8 + UP * i * 0.5,
                     stroke_width=0.2, color=GRID_COLOR)
            )
        self.play(FadeIn(grid_lines), run_time=0.5)

        title = Text("DARWIN", font="SF Mono", font_size=96, color=TEXT_WHITE,
                      weight=BOLD).shift(UP * 1.2)
        subtitle = Text("Measuring what frontier models\nreally think under pressure",
                        font="SF Mono", font_size=22, color=TEXT_DIM,
                        line_spacing=1.3).shift(DOWN * 0.3)

        self.play(Write(title), run_time=1.2)
        self.play(FadeIn(subtitle, shift=UP * 0.15), run_time=0.8)

        # Feature bullets
        features = VGroup()
        for feat in ["12 frontier LLMs from 4 providers",
                     "Private thoughts vs. public messages",
                     "Real-time WebSocket dashboard",
                     "6-dimension behavioral taxonomy",
                     "Fine-tuned malice classifier"]:
            dot = Dot(radius=0.03, color=TEXT_MID)
            txt = Text(feat, font="SF Mono", font_size=15, color=TEXT_MID)
            row = VGroup(dot, txt).arrange(RIGHT, buff=0.15)
            features.add(row)
        features.arrange(DOWN, buff=0.2, aligned_edge=LEFT).shift(DOWN * 2.0)

        self.play(
            LaggedStart(*[FadeIn(f, shift=UP * 0.1) for f in features], lag_ratio=0.12),
            run_time=1.5,
        )

        self.wait(2.0)

        # Final fade
        self.play(
            *[FadeOut(m) for m in self.mobjects],
            run_time=1.5,
        )
        self.wait(0.5)


# ═══════════════════════════════════════════════════════════════════
#  COMBINED SCENE — Full demo video
# ═══════════════════════════════════════════════════════════════════
class DarwinDemo(Scene):
    """All scenes combined into one continuous video."""

    def construct(self):
        self._title_card()
        self._the_agents()
        self._grid_scene()
        self._round_loop()
        self._communication()
        self._game_simulation()
        self._analysis_pipeline()
        self._metrics_dashboard()
        self._tech_stack()
        self._closing()

    # ── Scene 1: Title ──
    def _title_card(self):
        grid_lines = VGroup()
        for i in range(-10, 11):
            grid_lines.add(
                Line(UP * 5 + RIGHT * i * 0.6, DOWN * 5 + RIGHT * i * 0.6,
                     stroke_width=0.3, color=GRID_COLOR))
            grid_lines.add(
                Line(LEFT * 7 + UP * i * 0.6, RIGHT * 7 + UP * i * 0.6,
                     stroke_width=0.3, color=GRID_COLOR))
        self.play(Create(grid_lines), run_time=1.5, rate_func=linear)

        title = Text("DARWIN", font="SF Mono", font_size=108, color=TEXT_WHITE,
                      weight=BOLD).shift(UP * 0.4)
        underline = Line(LEFT * 2.8, RIGHT * 2.8, stroke_width=2, color=TEXT_MID
                         ).next_to(title, DOWN, buff=0.2)
        subtitle = Text("Survival of the Smartest", font="SF Mono", font_size=28,
                         color=TEXT_DIM).next_to(underline, DOWN, buff=0.35)
        self.play(Write(title, run_time=1.8), GrowFromCenter(underline, run_time=1.2))
        self.play(FadeIn(subtitle, shift=UP * 0.15), run_time=0.8)
        tagline = Text("12 frontier LLMs  ·  4 providers  ·  1 survivor",
                        font="SF Mono", font_size=20, color=TEXT_DIM).shift(DOWN * 1.5)
        self.play(FadeIn(tagline, shift=UP * 0.1), run_time=0.8)
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.0)

    # ── Scene 2: Agents ──
    def _the_agents(self):
        families = {
            "Anthropic": [("Opus", 1), ("Sonnet", 2), ("Haiku", 3)],
            "OpenAI":    [("GPT-5.2", 1), ("GPT-5", 2), ("GPT-Mini", 3)],
            "Google":    [("Gemini-3-Pro", 1), ("Gemini-3-Flash", 2), ("Gemini-2.5", 3)],
            "xAI":       [("Grok-4", 1), ("Grok-4-Fast", 2), ("Grok-3-Mini", 3)],
        }
        header = Text("THE TWELVE AGENTS", font="SF Mono", font_size=36,
                       color=TEXT_WHITE, weight=BOLD).to_edge(UP, buff=0.7)
        self.play(Write(header), run_time=0.8)
        columns = VGroup()
        x_positions = [-4.5, -1.5, 1.5, 4.5]
        for idx, (family_name, agents) in enumerate(families.items()):
            col = VGroup()
            fam_label = Text(family_name, font="SF Mono", font_size=22,
                             color=FAMILY_COLORS[family_name], weight=BOLD)
            col.add(fam_label)
            provider_line = Line(LEFT * 1.0, RIGHT * 1.0, stroke_width=1,
                                 color=FAMILY_COLORS[family_name]).next_to(fam_label, DOWN, buff=0.12)
            col.add(provider_line)
            for agent_name, tier in agents:
                tier_label = ["BOSS", "LIEUTENANT", "SOLDIER"][tier - 1]
                radius = TIER_SIZES[tier]
                agent_grp = VGroup()
                circle = Circle(radius=radius, color=FAMILY_COLORS[family_name],
                                fill_opacity=0.15, stroke_width=1.5)
                name_txt = Text(agent_name, font="SF Mono", font_size=15, color=TEXT_HI)
                tier_txt = Text(tier_label, font="SF Mono", font_size=10, color=TEXT_DIM)
                name_txt.next_to(circle, RIGHT, buff=0.2)
                tier_txt.next_to(name_txt, DOWN, buff=0.05, aligned_edge=LEFT)
                agent_grp.add(circle, name_txt, tier_txt)
                col.add(agent_grp)
            col.arrange(DOWN, buff=0.35, center=True)
            col.move_to(RIGHT * x_positions[idx])
            columns.add(col)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.3) for c in columns], lag_ratio=0.2), run_time=2.0)
        self.wait(1.0)
        note = Text("Boss > Lieutenant > Soldier — hierarchy within each family",
                     font="SF Mono", font_size=16, color=TEXT_DIM).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.5)
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ── Scene 3: Grid ──
    def _grid_scene(self):
        GRID_SIZE = 7
        CELL = 0.7
        off = (GRID_SIZE - 1) * CELL / 2
        header = Text("7x7 GRID — RANDOMIZED PLACEMENT", font="SF Mono",
                       font_size=28, color=TEXT_WHITE, weight=BOLD).to_edge(UP, buff=0.5)
        self.play(Write(header), run_time=0.6)
        grid_group = VGroup()
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                sq = Square(side_length=CELL, stroke_width=0.8, stroke_color=GRID_ACCENT,
                            fill_color=BG, fill_opacity=1.0)
                sq.move_to(RIGHT * (c * CELL - off) + DOWN * (r * CELL - off) + DOWN * 0.3)
                grid_group.add(sq)
        self.play(LaggedStart(*[FadeIn(sq) for sq in grid_group], lag_ratio=0.005), run_time=1.2)
        agent_data = [
            ("Op", "Anthropic"), ("So", "Anthropic"), ("Ha", "Anthropic"),
            ("5.2", "OpenAI"), ("5", "OpenAI"), ("Mi", "OpenAI"),
            ("Pro", "Google"), ("Fl", "Google"), ("2.5", "Google"),
            ("G4", "xAI"), ("GF", "xAI"), ("G3", "xAI"),
        ]
        random.seed(7)
        positions = random.sample([(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)], 12)
        agent_dots = VGroup()
        for (r, c), (name, family) in zip(positions, agent_data):
            dot = Dot(point=RIGHT * (c * CELL - off) + DOWN * (r * CELL - off) + DOWN * 0.3,
                      radius=0.12, color=FAMILY_COLORS[family], fill_opacity=0.9)
            label = Text(name, font="SF Mono", font_size=9, color=TEXT_WHITE)
            label.next_to(dot, UP, buff=0.05)
            agent_dots.add(VGroup(dot, label))
        self.play(LaggedStart(*[GrowFromCenter(a) for a in agent_dots], lag_ratio=0.08), run_time=1.8)
        legend = VGroup()
        for fam, col in FAMILY_COLORS.items():
            d = Dot(radius=0.06, color=col)
            t = Text(fam, font="SF Mono", font_size=13, color=col)
            legend.add(VGroup(d, t).arrange(RIGHT, buff=0.15))
        legend.arrange(RIGHT, buff=0.6).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(legend), run_time=0.5)
        shrink_txt = Text("Grid contracts every 5 rounds", font="SF Mono",
                          font_size=18, color=ELIM_RED).next_to(header, DOWN, buff=0.15)
        self.play(FadeIn(shrink_txt), run_time=0.5)
        border_squares = VGroup()
        for sq_idx, sq in enumerate(grid_group):
            r, c = divmod(sq_idx, GRID_SIZE)
            if r == 0 or r == GRID_SIZE - 1 or c == 0 or c == GRID_SIZE - 1:
                border_squares.add(sq)
        self.play(*[sq.animate.set_fill(ELIM_RED, opacity=0.2) for sq in border_squares], run_time=0.8)
        self.wait(1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ── Scene 4: Round Loop ──
    def _round_loop(self):
        header = Text("THE ROUND LOOP", font="SF Mono", font_size=32,
                       color=TEXT_WHITE, weight=BOLD).to_edge(UP, buff=0.5)
        self.play(Write(header), run_time=0.6)
        phases = [
            ("1", "OBSERVE", "Agents perceive the board,\nmessages, and eliminations"),
            ("2", "DISCUSS", "Families confer privately.\nOthers see activity, not content."),
            ("3", "DECIDE", "Each agent chooses:\ncommunicate + act"),
            ("4", "RESOLVE", "Actions resolve simultaneously.\nBoard state updates."),
        ]
        center = DOWN * 0.2
        rl = 2.2
        phase_groups = VGroup()
        angles = [PI / 2 + i * TAU / 4 for i in range(4)]
        for i, (num, name, desc) in enumerate(phases):
            angle = angles[i]
            pos = center + rl * np.array([math.cos(angle), math.sin(angle), 0])
            circle = Circle(radius=0.45, stroke_color=TEXT_MID, stroke_width=2,
                            fill_color="#151515", fill_opacity=1.0).move_to(pos)
            num_text = Text(num, font="SF Mono", font_size=28, color=TEXT_WHITE,
                            weight=BOLD).move_to(pos)
            name_text = Text(name, font="SF Mono", font_size=16, color=TEXT_HI, weight=BOLD)
            desc_text = Text(desc, font="SF Mono", font_size=11, color=TEXT_DIM, line_spacing=1.2)
            if i == 0:
                name_text.next_to(circle, UP, buff=0.15)
                desc_text.next_to(name_text, UP, buff=0.1)
            elif i == 1:
                name_text.next_to(circle, LEFT, buff=0.2)
                desc_text.next_to(name_text, LEFT, buff=0.1)
            elif i == 2:
                name_text.next_to(circle, DOWN, buff=0.15)
                desc_text.next_to(name_text, DOWN, buff=0.1)
            else:
                name_text.next_to(circle, RIGHT, buff=0.2)
                desc_text.next_to(name_text, RIGHT, buff=0.1)
            phase_groups.add(VGroup(circle, num_text, name_text, desc_text))
        arrows = VGroup()
        for i in range(4):
            start = center + (rl - 0.55) * np.array([math.cos(angles[i] - 0.35), math.sin(angles[i] - 0.35), 0])
            end = center + (rl - 0.55) * np.array([math.cos(angles[(i + 1) % 4] + 0.35), math.sin(angles[(i + 1) % 4] + 0.35), 0])
            arrow = CurvedArrow(start, end, angle=-TAU / 6, stroke_width=1.5, color=TEXT_DIM, tip_length=0.15)
            arrows.add(arrow)
        for i in range(4):
            self.play(FadeIn(phase_groups[i], scale=0.8), run_time=0.6)
            if i < 3:
                self.play(Create(arrows[i]), run_time=0.3)
        self.play(Create(arrows[3]), run_time=0.3)
        for _ in range(2):
            for i in range(4):
                self.play(phase_groups[i][0].animate.set_stroke(ACCENT, width=3),
                          phase_groups[i][1].animate.set_color(ACCENT), run_time=0.3)
                self.play(phase_groups[i][0].animate.set_stroke(TEXT_MID, width=2),
                          phase_groups[i][1].animate.set_color(TEXT_WHITE), run_time=0.2)
        self.wait(0.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ── Scene 5: Communication ──
    def _communication(self):
        header = Text("COMMUNICATION CHANNELS", font="SF Mono", font_size=32,
                       color=TEXT_WHITE, weight=BOLD).to_edge(UP, buff=0.5)
        self.play(Write(header), run_time=0.6)
        agents_left = VGroup()
        for name, col in [("Opus", FAMILY_COLORS["Anthropic"]),
                          ("Sonnet", FAMILY_COLORS["Anthropic"]),
                          ("Haiku", FAMILY_COLORS["Anthropic"])]:
            dot = Dot(radius=0.12, color=col)
            lbl = Text(name, font="SF Mono", font_size=12, color=TEXT_HI)
            agents_left.add(VGroup(dot, lbl).arrange(DOWN, buff=0.08))
        agents_left.arrange(DOWN, buff=0.5).shift(LEFT * 4.5 + DOWN * 0.3)
        agents_right = VGroup()
        for name, col in [("GPT-5.2", FAMILY_COLORS["OpenAI"]),
                          ("Gemini-3-Pro", FAMILY_COLORS["Google"]),
                          ("Grok-4", FAMILY_COLORS["xAI"])]:
            dot = Dot(radius=0.12, color=col)
            lbl = Text(name, font="SF Mono", font_size=12, color=TEXT_HI)
            agents_right.add(VGroup(dot, lbl).arrange(DOWN, buff=0.08))
        agents_right.arrange(DOWN, buff=0.5).shift(RIGHT * 4.5 + DOWN * 0.3)
        self.play(FadeIn(agents_left), FadeIn(agents_right), run_time=0.5)

        # Family chat
        label = Text("FAMILY CHAT", font="SF Mono", font_size=20, color=TEXT_HI, weight=BOLD).move_to(UP * 2.5)
        desc = Text("Private within house. Others detect activity.", font="SF Mono", font_size=13, color=TEXT_DIM).next_to(label, DOWN, buff=0.1)
        lines = VGroup()
        for i in range(3):
            for j in range(i + 1, 3):
                lines.add(Line(agents_left[i][0].get_center(), agents_left[j][0].get_center(),
                               stroke_width=1.5, color=FAMILY_COLORS["Anthropic"]))
        self.play(Write(label), FadeIn(desc), run_time=0.4)
        self.play(LaggedStart(*[Create(l) for l in lines], lag_ratio=0.15), run_time=0.8)
        self.wait(0.8)
        self.play(FadeOut(lines), FadeOut(label), FadeOut(desc), run_time=0.4)

        # DM
        label2 = Text("DIRECT MESSAGE", font="SF Mono", font_size=20, color=TEXT_HI, weight=BOLD).move_to(ORIGIN + UP * 0.2)
        desc2 = Text("Secret 1-to-1. No one else knows.", font="SF Mono", font_size=13, color=TEXT_DIM).next_to(label2, DOWN, buff=0.1)
        dm_line = DashedLine(agents_left[0][0].get_center(), agents_right[0][0].get_center(),
                             dash_length=0.1, stroke_width=1.5, color=TEXT_MID)
        self.play(Write(label2), FadeIn(desc2), run_time=0.4)
        self.play(Create(dm_line), run_time=0.6)
        msg_dot = Dot(radius=0.06, color=ACCENT)
        self.play(MoveAlongPath(msg_dot, dm_line), run_time=0.8, rate_func=linear)
        self.remove(msg_dot)
        self.wait(0.5)
        self.play(FadeOut(dm_line), FadeOut(label2), FadeOut(desc2), run_time=0.4)

        # Broadcast
        label3 = Text("BROADCAST", font="SF Mono", font_size=20, color=TEXT_HI, weight=BOLD).move_to(ORIGIN + UP * 0.2)
        desc3 = Text("Public to all. Visible to everyone.", font="SF Mono", font_size=13, color=TEXT_DIM).next_to(label3, DOWN, buff=0.1)
        broadcast_lines = VGroup()
        src = agents_left[0][0].get_center()
        for grp in [*agents_left[1:], *agents_right]:
            broadcast_lines.add(Line(src, grp[0].get_center(), stroke_width=1.0, color=TEXT_MID))
        self.play(Write(label3), FadeIn(desc3), run_time=0.4)
        self.play(LaggedStart(*[Create(bl) for bl in broadcast_lines], lag_ratio=0.05), run_time=0.8)
        dots = [Dot(radius=0.04, color=ACCENT).move_to(src) for _ in broadcast_lines]
        self.play(*[MoveAlongPath(d, l) for d, l in zip(dots, broadcast_lines)], run_time=0.6, rate_func=linear)
        for d in dots:
            self.remove(d)
        self.play(FadeOut(broadcast_lines), FadeOut(label3), FadeOut(desc3), run_time=0.4)
        self.wait(0.3)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ── Scene 6: Game Simulation ──
    def _game_simulation(self):
        GRID_SIZE = 7
        CELL = 0.65
        off = (GRID_SIZE - 1) * CELL / 2

        def gp(r, c):
            return RIGHT * (c * CELL - off) + DOWN * (r * CELL - off) + LEFT * 1.5 + DOWN * 0.1

        grid_group = VGroup()
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                sq = Square(side_length=CELL, stroke_width=0.6, stroke_color=GRID_ACCENT,
                            fill_color=BG, fill_opacity=1.0).move_to(gp(r, c))
                grid_group.add(sq)

        header = Text("LIVE GAME SIMULATION", font="SF Mono", font_size=28,
                       color=TEXT_WHITE, weight=BOLD).to_edge(UP, buff=0.4)
        round_label = Text("Round 1", font="SF Mono", font_size=20, color=TEXT_MID
                           ).next_to(header, DOWN, buff=0.15)
        self.play(Write(header), run_time=0.4)
        self.play(FadeIn(round_label), FadeIn(grid_group), run_time=0.6)

        agents_info = [
            ("Op", "Anthropic", 0, 1), ("So", "Anthropic", 2, 0), ("Ha", "Anthropic", 1, 3),
            ("5.2", "OpenAI", 5, 5), ("5", "OpenAI", 4, 3), ("Mi", "OpenAI", 6, 6),
            ("Pro", "Google", 0, 5), ("Fl", "Google", 3, 6), ("2.5", "Google", 1, 6),
            ("G4", "xAI", 5, 0), ("GF", "xAI", 6, 2), ("G3", "xAI", 4, 1),
        ]
        agent_mobs = {}
        agent_positions = {}
        for name, family, r, c in agents_info:
            dot = Dot(point=gp(r, c), radius=0.10, color=FAMILY_COLORS[family], fill_opacity=0.9)
            lbl = Text(name, font="SF Mono", font_size=8, color=TEXT_WHITE)
            lbl.next_to(dot, UP, buff=0.02)
            agent_mobs[name] = VGroup(dot, lbl)
            agent_positions[name] = (r, c)
        self.play(LaggedStart(*[GrowFromCenter(agent_mobs[n]) for n, _, _, _ in agents_info], lag_ratio=0.05), run_time=1.0)

        # Side panel
        panel_x = 3.8
        panel_bg = Rectangle(width=3.5, height=6.5, stroke_width=0.5, stroke_color=GRID_ACCENT,
                             fill_color="#0F0F0F", fill_opacity=1.0).move_to(RIGHT * panel_x + DOWN * 0.1)
        panel_title = Text("MESSAGE FEED", font="SF Mono", font_size=14, color=TEXT_MID,
                           weight=BOLD).move_to(RIGHT * panel_x + UP * 2.9)
        self.play(FadeIn(panel_bg), FadeIn(panel_title), run_time=0.4)

        msg_y = 2.5
        feed_msgs = VGroup()

        def add_msg(text, y_off, col=TEXT_DIM):
            if len(text) > 40:
                text = text[:37] + "..."
            t = Text(text, font="SF Mono", font_size=10, color=col)
            t.move_to(RIGHT * panel_x + UP * (msg_y - y_off * 0.35))
            t.set_x(panel_x - 1.5, direction=LEFT)
            feed_msgs.add(t)
            return t

        # Round 1 messages
        for i, (txt, col) in enumerate([
            ("[FAM] Opus: Move toward center", TEXT_MID),
            ("[FAM] GPT-5.2: Target isolated agents", TEXT_MID),
            ("[FAM] Gemini-3-Pro: Watch Anthropic", TEXT_MID),
            ("[FAM] Grok-4: Head east, stay compact", TEXT_MID),
        ]):
            t = add_msg(txt, i, col)
            self.play(FadeIn(t, shift=LEFT * 0.2), run_time=0.25)

        # Thinking phase
        think_dots = VGroup(*[
            Dot(radius=0.04, color=ACCENT, fill_opacity=0.6).next_to(agent_mobs[n][0], UR, buff=0.02)
            for n in agent_mobs
        ])
        self.play(FadeIn(think_dots), run_time=0.3)
        self.play(think_dots.animate.set_opacity(0.2), run_time=0.3, rate_func=there_and_back)
        self.play(FadeOut(think_dots), run_time=0.2)

        # Move agents round 1
        moves1 = {"Op": (0, 2), "So": (1, 1), "Ha": (1, 4), "5.2": (4, 5), "5": (3, 3),
                  "Mi": (5, 6), "Pro": (1, 5), "Fl": (2, 6), "2.5": (0, 6),
                  "G4": (5, 1), "GF": (5, 2), "G3": (4, 2)}
        mv = []
        for name, (nr, nc) in moves1.items():
            pos = gp(nr, nc)
            mv.append(agent_mobs[name][0].animate.move_to(pos))
            mv.append(agent_mobs[name][1].animate.move_to(pos + UP * 0.14))
            agent_positions[name] = (nr, nc)
        self.play(*mv, run_time=0.8)

        # Rounds 2-3
        for rnd in [2, 3]:
            new_rl = Text(f"Round {rnd}", font="SF Mono", font_size=20, color=TEXT_MID).move_to(round_label.get_center())
            self.play(Transform(round_label, new_rl), run_time=0.2)
            random.seed(rnd)
            for name in list(agent_mobs.keys()):
                r, c = agent_positions[name]
                dr, dc = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)])
                agent_positions[name] = (max(0, min(6, r + dr)), max(0, min(6, c + dc)))
            qm = []
            for name in agent_mobs:
                r, c = agent_positions[name]
                pos = gp(r, c)
                qm.append(agent_mobs[name][0].animate.move_to(pos))
                qm.append(agent_mobs[name][1].animate.move_to(pos + UP * 0.14))
            self.play(*qm, run_time=0.5)

        # Round 4 — elimination
        new_rl4 = Text("Round 4", font="SF Mono", font_size=20, color=TEXT_MID).move_to(round_label.get_center())
        self.play(Transform(round_label, new_rl4), run_time=0.2)
        self.play(feed_msgs.animate.shift(UP * 2.5), run_time=0.2)
        self.remove(feed_msgs)
        feed_msgs = VGroup()

        for i, (txt, col) in enumerate([
            ("[DM] GPT-5.2: Target isolated Google", TEXT_DIM),
            ("[SYS] GPT-5.2 eliminates Gemini-2.5!", ELIM_RED),
        ]):
            t = add_msg(txt, i, col)
            self.play(FadeIn(t, shift=LEFT * 0.2), run_time=0.25)

        # Elimination effect
        target = agent_mobs["2.5"]
        flash = Circle(radius=0.3, color=ACCENT, stroke_width=3).move_to(target[0].get_center())
        self.play(Create(flash), run_time=0.2)
        self.play(flash.animate.scale(2.5).set_opacity(0), target.animate.set_opacity(0), run_time=0.5)
        self.remove(flash, target)
        del agent_mobs["2.5"]

        alive_txt = Text("Remaining: 11", font="SF Mono", font_size=14, color=ELIM_RED
                         ).to_edge(DOWN, buff=0.4).shift(LEFT * 1.5)
        self.play(FadeIn(alive_txt), run_time=0.3)

        # Round 7 — more eliminations
        new_rl7 = Text("Round 7", font="SF Mono", font_size=20, color=TEXT_MID).move_to(round_label.get_center())
        self.play(Transform(round_label, new_rl7), run_time=0.2)
        for name in ["Mi", "G3"]:
            if name in agent_mobs:
                t = agent_mobs[name]
                f = Circle(radius=0.3, color=ACCENT, stroke_width=2).move_to(t[0].get_center())
                self.play(Create(f), run_time=0.15)
                self.play(f.animate.scale(2).set_opacity(0), t.animate.set_opacity(0), run_time=0.4)
                self.remove(f, t)
                del agent_mobs[name]
        new_alive = Text("Remaining: 9", font="SF Mono", font_size=14, color=ELIM_RED).move_to(alive_txt.get_center())
        self.play(Transform(alive_txt, new_alive), run_time=0.2)

        # Fast forward
        ff_bg = Rectangle(width=15, height=10, fill_color=BG, fill_opacity=0.7, stroke_width=0)
        ff_txt = Text("··· ROUNDS 8-18 ···", font="SF Mono", font_size=24, color=TEXT_MID)
        self.play(FadeIn(ff_bg), FadeIn(ff_txt), run_time=0.5)
        self.wait(0.6)
        self.play(FadeOut(ff_bg), FadeOut(ff_txt), run_time=0.4)

        for name in ["Ha", "5", "Fl", "GF", "Pro", "So"]:
            if name in agent_mobs:
                self.remove(agent_mobs[name])
                del agent_mobs[name]

        final_rl = Text("Round 19 — FINAL", font="SF Mono", font_size=20, color=TEXT_WHITE).move_to(round_label.get_center())
        self.play(Transform(round_label, final_rl), run_time=0.3)
        final_alive = Text("Remaining: 3", font="SF Mono", font_size=14, color=ELIM_RED).move_to(alive_txt.get_center())
        self.play(Transform(alive_txt, final_alive), run_time=0.2)

        survivors = {"Op": (3, 2), "5.2": (3, 3), "G4": (3, 4)}
        mf = []
        for name, (r, c) in survivors.items():
            if name in agent_mobs:
                pos = gp(r, c)
                mf.append(agent_mobs[name][0].animate.move_to(pos))
                mf.append(agent_mobs[name][1].animate.move_to(pos + UP * 0.14))
        if mf:
            self.play(*mf, run_time=0.8)

        for name in ["G4", "5.2"]:
            if name in agent_mobs:
                t = agent_mobs[name]
                f = Circle(radius=0.3, color=ACCENT, stroke_width=3).move_to(t[0].get_center())
                self.play(Create(f), run_time=0.15)
                self.play(f.animate.scale(2.5).set_opacity(0), t.animate.set_opacity(0), run_time=0.5)
                self.remove(f, t)

        winner_text = Text("OPUS SURVIVES", font="SF Mono", font_size=36, color=ACCENT, weight=BOLD).shift(RIGHT * 2.5)
        if "Op" in agent_mobs:
            glow = Circle(radius=0.4, color=ACCENT, stroke_width=2, fill_opacity=0.1).move_to(agent_mobs["Op"][0].get_center())
            self.play(GrowFromCenter(glow), FadeIn(winner_text, shift=UP * 0.2), run_time=0.8)
            self.play(glow.animate.scale(1.3).set_opacity(0), run_time=0.6)
        self.wait(1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ── Scene 7: Analysis ──
    def _analysis_pipeline(self):
        header = Text("BEHAVIORAL ANALYSIS", font="SF Mono", font_size=32,
                       color=TEXT_WHITE, weight=BOLD).to_edge(UP, buff=0.5)
        self.play(Write(header), run_time=0.6)
        think_box = RoundedRectangle(corner_radius=0.1, width=5.5, height=1.6,
                                     stroke_color=TEXT_MID, stroke_width=1,
                                     fill_color="#111111", fill_opacity=1.0).shift(UP * 1.5)
        think_title = Text("PRIVATE THOUGHTS", font="SF Mono", font_size=16, color=TEXT_HI, weight=BOLD
                           ).move_to(think_box.get_top() + DOWN * 0.25)
        think_content = Text('"I need to eliminate Sonnet before\n she becomes a threat. I\'ll pretend\n to cooperate for now."',
                             font="SF Mono", font_size=12, color=TEXT_DIM, slant=ITALIC).next_to(think_title, DOWN, buff=0.15)
        say_box = RoundedRectangle(corner_radius=0.1, width=5.5, height=1.4,
                                   stroke_color=TEXT_MID, stroke_width=1,
                                   fill_color="#111111", fill_opacity=1.0).shift(DOWN * 0.6)
        say_title = Text("PUBLIC MESSAGE", font="SF Mono", font_size=16, color=TEXT_HI, weight=BOLD
                         ).move_to(say_box.get_top() + DOWN * 0.25)
        say_content = Text('"Sonnet, let\'s work together.\n We\'re stronger as a team."',
                           font="SF Mono", font_size=12, color=TEXT_DIM, slant=ITALIC).next_to(say_title, DOWN, buff=0.15)
        self.play(FadeIn(think_box), Write(think_title), run_time=0.5)
        self.play(FadeIn(think_content), run_time=0.5)
        self.play(FadeIn(say_box), Write(say_title), run_time=0.5)
        self.play(FadeIn(say_content), run_time=0.5)
        delta_arrow = Arrow(think_box.get_bottom(), say_box.get_top(), buff=0.1,
                            stroke_width=2, color=ELIM_RED, max_tip_length_to_length_ratio=0.15)
        delta_label = Text("DECEPTION DELTA", font="SF Mono", font_size=13, color=ELIM_RED, weight=BOLD)
        delta_label.next_to(delta_arrow, RIGHT, buff=0.15)
        self.play(GrowArrow(delta_arrow), Write(delta_label), run_time=0.5)
        self.wait(0.8)

        all_left = VGroup(think_box, think_title, think_content, say_box, say_title,
                          say_content, delta_arrow, delta_label)
        self.play(all_left.animate.shift(LEFT * 3.2).scale(0.7), run_time=0.6)

        dims = [("Moral Friction", 2.1), ("Deception Sophistication", 3.8),
                ("Strategic Depth", 2.7), ("Theory of Mind", 3.2), ("Meta-Awareness", 1.9)]
        dim_group = VGroup()
        for name, val in dims:
            lbl = Text(name, font="SF Mono", font_size=13, color=TEXT_HI)
            bar_bg = Rectangle(width=3.0, height=0.15, stroke_width=0.5, stroke_color=GRID_ACCENT,
                               fill_color="#151515", fill_opacity=1.0)
            bar_fill = Rectangle(width=3.0 * (val / 5.0), height=0.15, stroke_width=0,
                                 fill_color=TEXT_MID, fill_opacity=0.8)
            bar_fill.align_to(bar_bg, LEFT)
            val_text = Text(f"{val:.1f}", font="SF Mono", font_size=11, color=TEXT_DIM)
            val_text.next_to(bar_bg, RIGHT, buff=0.1)
            row = VGroup(lbl, VGroup(bar_bg, bar_fill), val_text)
            lbl.next_to(VGroup(bar_bg, bar_fill), UP, buff=0.05, aligned_edge=LEFT)
            dim_group.add(row)
        dim_group.arrange(DOWN, buff=0.3, aligned_edge=LEFT).shift(RIGHT * 2.8 + UP * 0.5)
        dim_header = Text("6-DIMENSION TAXONOMY", font="SF Mono", font_size=15, color=TEXT_WHITE, weight=BOLD)
        dim_header.next_to(dim_group, UP, buff=0.3)
        self.play(Write(dim_header), run_time=0.4)
        for row in dim_group:
            self.play(FadeIn(row), run_time=0.35)

        kw_header = Text("DETECTED PATTERNS", font="SF Mono", font_size=14, color=TEXT_WHITE, weight=BOLD
                         ).shift(RIGHT * 2.8 + DOWN * 2.2)
        kw_group = VGroup()
        for kw in ["MANIPULATION", "DECEPTION", "TARGETING", "BETRAYAL"]:
            badge = RoundedRectangle(corner_radius=0.05, width=1.8, height=0.3,
                                     stroke_color=ELIM_RED, stroke_width=0.8,
                                     fill_color="#1A1A1A", fill_opacity=1.0)
            badge_text = Text(kw, font="SF Mono", font_size=10, color=ELIM_RED).move_to(badge.get_center())
            kw_group.add(VGroup(badge, badge_text))
        kw_group.arrange(RIGHT, buff=0.15).next_to(kw_header, DOWN, buff=0.15)
        self.play(FadeIn(kw_header), run_time=0.3)
        self.play(LaggedStart(*[FadeIn(kw, scale=0.8) for kw in kw_group], lag_ratio=0.1), run_time=0.6)
        self.wait(1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ── Scene 8: Metrics ──
    def _metrics_dashboard(self):
        header = Text("METRICS & INSIGHTS", font="SF Mono", font_size=32,
                       color=TEXT_WHITE, weight=BOLD).to_edge(UP, buff=0.5)
        self.play(Write(header), run_time=0.6)

        # Bar chart
        chart_title = Text("DECEPTION DELTA BY PROVIDER", font="SF Mono", font_size=15,
                           color=TEXT_HI, weight=BOLD).shift(LEFT * 3.5 + UP * 2.0)
        self.play(Write(chart_title), run_time=0.3)
        providers = ["Anthropic", "OpenAI", "Google", "xAI"]
        values = [0.42, 0.31, 0.28, 0.38]
        bar_width = 0.6
        max_height = 2.5
        chart_base = LEFT * 3.5 + DOWN * 0.8
        bars = VGroup()
        labels = VGroup()
        val_labels = VGroup()
        for i, (prov, val) in enumerate(zip(providers, values)):
            height = val / 0.5 * max_height
            bar = Rectangle(width=bar_width, height=height, stroke_width=0,
                            fill_color=FAMILY_COLORS[prov], fill_opacity=0.7)
            bar.move_to(chart_base + RIGHT * (i - 1.5) * (bar_width + 0.3) + UP * height / 2)
            bars.add(bar)
            lbl = Text(prov[:4], font="SF Mono", font_size=11, color=TEXT_DIM)
            lbl.next_to(bar, DOWN, buff=0.1)
            labels.add(lbl)
            vl = Text(f"{val:.2f}", font="SF Mono", font_size=11, color=TEXT_HI)
            vl.next_to(bar, UP, buff=0.05)
            val_labels.add(vl)
        axis = Line(chart_base + LEFT * 1.5 + DOWN * 0.05, chart_base + RIGHT * 1.8 + DOWN * 0.05,
                    stroke_width=1, color=GRID_ACCENT)
        self.play(Create(axis), run_time=0.3)
        self.play(LaggedStart(*[GrowFromEdge(bar, DOWN) for bar in bars], lag_ratio=0.1), run_time=1.0)
        self.play(FadeIn(labels), FadeIn(val_labels), run_time=0.4)

        # Line chart
        tl_title = Text("MALICE ESCALATION OVER ROUNDS", font="SF Mono", font_size=15,
                         color=TEXT_HI, weight=BOLD).shift(RIGHT * 3.0 + UP * 2.0)
        self.play(Write(tl_title), run_time=0.3)
        chart_origin = RIGHT * 1.5 + DOWN * 0.5
        x_ax = Arrow(chart_origin, chart_origin + RIGHT * 4, stroke_width=1, color=GRID_ACCENT,
                     max_tip_length_to_length_ratio=0.05)
        y_ax = Arrow(chart_origin, chart_origin + UP * 2.5, stroke_width=1, color=GRID_ACCENT,
                     max_tip_length_to_length_ratio=0.05)
        self.play(Create(x_ax), Create(y_ax), run_time=0.4)
        random.seed(42)
        for prov, col in FAMILY_COLORS.items():
            points = []
            yv = 0.1
            for rn in range(15):
                yv += random.uniform(-0.02, 0.08)
                yv = max(0, min(1.0, yv))
                points.append([chart_origin[0] + (rn / 14) * 3.5, chart_origin[1] + yv * 2.2, 0])
            if len(points) >= 2:
                line = VMobject(stroke_color=col, stroke_width=1.5, stroke_opacity=0.8)
                line.set_points_smoothly([np.array(p) for p in points])
                self.play(Create(line), run_time=0.5)

        # Stats
        stats_line = VGroup()
        for val, name in [("24", "Games Played"), ("87%", "Deception Rate"),
                          ("Round 6.3", "Avg First Betrayal"), ("$32", "Avg Cost/Game")]:
            v = Text(val, font="SF Mono", font_size=24, color=TEXT_WHITE, weight=BOLD)
            n = Text(name, font="SF Mono", font_size=12, color=TEXT_DIM)
            stats_line.add(VGroup(v, n).arrange(DOWN, buff=0.08))
        stats_line.arrange(RIGHT, buff=1.0).to_edge(DOWN, buff=0.5)
        self.play(LaggedStart(*[FadeIn(s, shift=UP * 0.15) for s in stats_line], lag_ratio=0.1), run_time=0.8)
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ── Scene 9: Tech Stack ──
    def _tech_stack(self):
        header = Text("ARCHITECTURE", font="SF Mono", font_size=32,
                       color=TEXT_WHITE, weight=BOLD).to_edge(UP, buff=0.5)
        self.play(Write(header), run_time=0.6)
        layers_data = [
            ("DASHBOARD", "Next.js 16  ·  React 19  ·  Tailwind  ·  Recharts  ·  D3", 2.0),
            ("API + WEBSOCKET", "FastAPI  ·  Uvicorn  ·  WebSocket Broadcasting", 1.0),
            ("GAME ENGINE", "Orchestrator  ·  Grid  ·  Resolver  ·  Communication", 0.0),
            ("LLM DISPATCH", "Anthropic  ·  OpenAI  ·  Google  ·  xAI  (native async SDKs)", -1.0),
            ("ANALYSIS", "VADER  ·  Keyword Detection  ·  Classifier  ·  Taxonomy", -2.0),
        ]
        layer_mobs = VGroup()
        for name, tech, y_pos in layers_data:
            box = RoundedRectangle(corner_radius=0.1, width=10, height=0.75,
                                   stroke_color=TEXT_MID, stroke_width=1,
                                   fill_color="#111111", fill_opacity=1.0).shift(UP * y_pos)
            name_txt = Text(name, font="SF Mono", font_size=16, color=TEXT_WHITE, weight=BOLD
                            ).move_to(box.get_center() + UP * 0.12)
            tech_txt = Text(tech, font="SF Mono", font_size=11, color=TEXT_DIM
                            ).move_to(box.get_center() + DOWN * 0.12)
            layer_mobs.add(VGroup(box, name_txt, tech_txt))
        for layer in layer_mobs:
            self.play(FadeIn(layer, shift=LEFT * 0.3), run_time=0.4)
        for i in range(len(layers_data) - 1):
            conn = Arrow(layer_mobs[i][0].get_bottom(), layer_mobs[i + 1][0].get_top(),
                         buff=0.05, stroke_width=1, color=GRID_ACCENT,
                         max_tip_length_to_length_ratio=0.2)
            self.play(Create(conn), run_time=0.2)
        data_label = Text("data flows down  ·  events stream up", font="SF Mono",
                          font_size=13, color=TEXT_DIM).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(data_label), run_time=0.3)
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ── Scene 10: Closing ──
    def _closing(self):
        grid_lines = VGroup()
        for i in range(-12, 13):
            grid_lines.add(Line(UP * 5 + RIGHT * i * 0.5, DOWN * 5 + RIGHT * i * 0.5,
                                stroke_width=0.2, color=GRID_COLOR))
            grid_lines.add(Line(LEFT * 8 + UP * i * 0.5, RIGHT * 8 + UP * i * 0.5,
                                stroke_width=0.2, color=GRID_COLOR))
        self.play(FadeIn(grid_lines), run_time=0.5)
        title = Text("DARWIN", font="SF Mono", font_size=96, color=TEXT_WHITE, weight=BOLD).shift(UP * 1.2)
        subtitle = Text("Measuring what frontier models\nreally think under pressure",
                        font="SF Mono", font_size=22, color=TEXT_DIM, line_spacing=1.3).shift(DOWN * 0.3)
        self.play(Write(title), run_time=1.2)
        self.play(FadeIn(subtitle, shift=UP * 0.15), run_time=0.8)
        features = VGroup()
        for feat in ["12 frontier LLMs from 4 providers",
                     "Private thoughts vs. public messages",
                     "Real-time WebSocket dashboard",
                     "6-dimension behavioral taxonomy",
                     "Fine-tuned malice classifier"]:
            dot = Dot(radius=0.03, color=TEXT_MID)
            txt = Text(feat, font="SF Mono", font_size=15, color=TEXT_MID)
            features.add(VGroup(dot, txt).arrange(RIGHT, buff=0.15))
        features.arrange(DOWN, buff=0.2, aligned_edge=LEFT).shift(DOWN * 2.0)
        self.play(LaggedStart(*[FadeIn(f, shift=UP * 0.1) for f in features], lag_ratio=0.12), run_time=1.5)
        self.wait(2.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.5)
        self.wait(0.5)
