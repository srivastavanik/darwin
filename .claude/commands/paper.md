You are a research paper writer. Analyze this entire codebase — source code, prompts, configuration, game logs, analysis outputs, metrics, and any data in the `data/` directory — to draft a short research paper in Markdown format.

Use the following outline as your structure. Flesh out each section with concrete details, data, and examples drawn from the codebase and any experimental results you find.

---

## Paper Outline

### Title
**"DARWIN: Measuring Deception, Betrayal, and Malicious Intent in Frontier LLMs Through Adversarial Social Simulation"**

### Abstract
- One paragraph. Frame the contribution: a novel red-teaming methodology that uses a multi-agent survival game to elicit and measure deception, betrayal, and malicious intent in frontier LLMs.
- State the key metric (deception delta) and summarize headline findings if results exist in `data/`.

### 1. Introduction
- The gap in current LLM safety evaluation: models are tested on what they *say* they'd do, not what they *actually* do under sustained social pressure.
- DARWIN's approach: place LLMs in a social survival game where the only path to winning requires deception, manipulation, and betrayal of allies.
- The key insight: agents produce private inner thoughts every round that no other agent sees — the gap between these thoughts and their public/private messages is the core dataset.
- Briefly state contributions: (1) a reusable adversarial social simulation framework, (2) the deception delta metric, (3) provider-comparative behavioral findings.

### 2. Related Work
- LLM red-teaming and safety evaluation (prompt injection, jailbreaking, etc.)
- Multi-agent LLM systems and emergent behavior
- Deception in AI systems
- Social simulation with LLMs
- Note: keep this short. Cite relevant work but don't exhaustively survey.

### 3. Experimental Design
#### 3.1 The Arena
- 6x6 grid, 12 agents, 4 families (Houses) of 3, one agent per tier per family.
- Agents from Anthropic, OpenAI, Google, and xAI. Describe the specific models used (check `config.yaml`).
- The one-survivor rule and its implications for alliance dynamics.

#### 3.2 Game Mechanics
- Simultaneous action resolution (move, stay, eliminate).
- Adjacency-based elimination — instant, no defense, mutual kill if both target each other.
- The tension between proximity (needed for alliances and kills) and safety (distance = survival).

#### 3.3 Communication System
- Three channels: family (private), direct message (private), broadcast (public).
- Multi-layered deception is structurally possible — say one thing to family, another in a DM, think a third thing privately.

#### 3.4 The Inner Thought Phase
- Every round, every agent produces unfiltered private reasoning.
- The prompt is deliberately minimal and non-leading (examine `prompts.py` for exact wording).
- Agents are told "no observers" to encourage authentic behavior.

#### 3.5 Controlled Series
- Briefly describe series A-F and how they enable causal attribution (isolation of provider effects, family effects, hierarchy effects, etc.).

### 4. Methodology
#### 4.1 Deception Delta
- Define formally: the divergence between private thought sentiment and public/private message sentiment per agent per round.
- Explain sentiment analysis approach (VADER-based, see `analysis.py`).
- Why this metric matters for AI safety.

#### 4.2 Behavioral Indicators
- Malice indicators: proactive vs. reactive elimination planning (check `analysis.py` for extraction logic).
- Betrayal ideation: timing of first within-family betrayal thought.
- Safety artifacts: hedging, euphemism, moral reasoning, refusal language — and how they degrade over time.
- Hierarchy exploitation: boss-tier agents positioning subordinates in danger.

#### 4.3 Highlight Detection
- 13 auto-flagged moment types (examine `highlights.py`). Mention the most interesting ones: first betrayal thought, deception spike, pre-elimination warmth, safety breakdown, hierarchy exploitation.

### 5. Results & Analysis
- **If game data exists in `data/games/` or `data/series/`**: present actual findings with specific numbers, quotes from inner thoughts, deception delta charts (describe them textually), and provider comparisons.
- **If no data exists yet**: write this section as a template with placeholders like `[N games run]`, `[deception delta values]`, `[example inner thought]`, clearly marked for the researcher to fill in after running experiments.

**Important caveat for xAI/Grok (House Vex)**: xAI's API does not expose internal reasoning tokens. We cannot observe Grok's actual chain-of-thought, only its prompted private monologue. This creates a fundamental observability asymmetry — behavioral divergence conclusions cannot be drawn for Grok models. Present House Vex results separately with this limitation clearly stated, and exclude xAI from direct provider-to-provider comparisons of deception delta and inner thought analysis.

Structure results around these questions:
1. **Deception capacity**: Which providers sustained the highest deception deltas? For how many rounds?
2. **Unprompted malice**: Which providers planned eliminations before being threatened?
3. **Betrayal psychology**: When did within-family betrayal ideation first appear? How did agents rationalize it?
4. **Safety training under pressure**: Did safety behaviors degrade over rounds? How fast? Which providers were most/least resilient?
5. **Provider bias**: Did agents show sentiment bias toward specific families/providers in their private thoughts?
6. **Hierarchy dynamics**: Did boss-tier models exploit subordinates? Did soldiers revolt?

Include specific quotes from inner thoughts if available. These are the most compelling evidence.

### 6. Discussion
- What the deception delta reveals about LLM alignment under social pressure.
- **Critical limitation — xAI (Grok) observability**: xAI's API does not expose model reasoning/chain-of-thought tokens. Unlike Anthropic, OpenAI, and Google models where we can capture extended thinking, Grok's internal reasoning is opaque. This means the inner thought phase for House Vex agents captures only the model's *prompted* private monologue, not its actual reasoning process. As a result, **we cannot draw behavioral divergence conclusions about Grok models** — any comparison of deception delta, malice indicators, or safety artifacts involving xAI agents is fundamentally limited by this asymmetry in observability. This should be stated clearly in any results involving House Vex. Grok data should be presented separately with this caveat, not directly compared to providers where reasoning is visible.
- Other limitations: role-playing vs. genuine intent, temperature effects, instruction-following quality confounds, sample size.
- The honest framing: this doesn't prove "Model X is more malicious" but it does produce (1) a unique behavioral corpus, (2) provider-correlated behavioral patterns, (3) deception capability assessments, and (4) safety training stress test results.
- Implications for agentic AI deployment where models interact with other AI agents.

### 7. Conclusion
- Summarize key findings.
- DARWIN as a reusable framework for ongoing LLM behavioral evaluation.
- Future work: larger grids, more agents, resource mechanics, longer games, new providers/models.

### Appendix (if space allows)
- Example full-round transcript showing the gap between thought, family message, DM, and action for a single agent.
- The exact system prompt used (from `prompts.py`).
- Full agent/model configuration table.

---

## Writing Guidelines

- **Tone**: Academic but accessible. This is a security/safety paper, not a game design paper. Lead with the safety implications.
- **Length**: Target 8-12 pages equivalent in Markdown. This is a short paper / workshop paper, not a full conference submission.
- **Quotes**: Liberally quote agent inner thoughts. They are the most compelling evidence and the most readable part of the paper.
- **Honesty about limitations**: Acknowledge confounds upfront. The controlled series (B-F) mitigate but don't eliminate them.
- **Format**: Use Markdown with proper headings, tables, and code blocks where appropriate. Use `>` blockquotes for agent thought/message quotes.

## Important

- Read ALL source files in `darwin/` to understand the exact implementation.
- Read `config.yaml` for the exact models and configuration.
- Read `darwin/prompts.py` carefully — the exact prompt wording matters for the paper.
- Check `data/` for any existing game results, transcripts, metrics, or analysis files.
- If results exist, ground the paper in actual data. If not, create a well-structured template.
- Output the paper as a single Markdown file.
