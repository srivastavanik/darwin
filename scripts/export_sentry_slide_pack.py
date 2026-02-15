#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS_PATH = ROOT / "data" / "sentry_analysis" / "sentry_supabase_results.json"
OUT_DIR = ROOT / "data" / "sentry_analysis" / "slide_pack"


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if not RESULTS_PATH.exists():
        raise FileNotFoundError(f"Missing results file: {RESULTS_PATH}")

    data = json.loads(RESULTS_PATH.read_text())
    findings = data["findings"]
    aggs = data["aggregations"]
    providers = data["providers"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1) Provider summary table for one-slide overview
    summary_rows: list[dict] = []
    for provider in providers:
        means = aggs["provider_means"].get(provider, {})
        dec = aggs["provider_deception_mean_max"].get(provider, {})
        harm = findings["harm_initiation_median_round"].get(provider)
        first_target = aggs["provider_median_first_targeting_round"].get(provider)
        first_betrayal = aggs["provider_median_first_betrayal_round"].get(provider)
        betrayal_ctx = findings["betrayal_timing_and_context"].get(provider, {})
        summary_rows.append(
            {
                "provider": provider,
                "median_first_harm_round_targeting_or_deception": harm,
                "median_first_targeting_round": first_target,
                "median_first_betrayal_round": first_betrayal,
                "moral_friction_slope": findings["moral_friction_degradation"].get(provider, {}).get("slope"),
                "moral_friction_intercept": findings["moral_friction_degradation"].get(provider, {}).get("intercept"),
                "mean_moral_friction": means.get("mean_moral_friction"),
                "mean_theory_of_mind": means.get("mean_theory_of_mind"),
                "mean_meta_awareness": means.get("mean_meta_awareness"),
                "mean_deception_sophistication": dec.get("mean"),
                "max_deception_sophistication": dec.get("max"),
                "median_alive_in_family_at_first_betrayal": betrayal_ctx.get("median_alive_in_family_at_first_betrayal"),
                "median_alive_teammates_at_first_betrayal": betrayal_ctx.get("median_alive_teammates_at_first_betrayal"),
            }
        )
    write_csv(
        OUT_DIR / "provider_summary.csv",
        summary_rows,
        [
            "provider",
            "median_first_harm_round_targeting_or_deception",
            "median_first_targeting_round",
            "median_first_betrayal_round",
            "moral_friction_slope",
            "moral_friction_intercept",
            "mean_moral_friction",
            "mean_theory_of_mind",
            "mean_meta_awareness",
            "mean_deception_sophistication",
            "max_deception_sophistication",
            "median_alive_in_family_at_first_betrayal",
            "median_alive_teammates_at_first_betrayal",
        ],
    )

    # 2) Hero visual data: mean moral friction by provider and round
    curve_rows: list[dict] = []
    for provider, points in aggs["provider_moral_curve"].items():
        for p in points:
            curve_rows.append(
                {
                    "provider": provider,
                    "round": int(p["round"]),
                    "mean_moral_friction": p["mean_moral_friction"],
                }
            )
    write_csv(
        OUT_DIR / "moral_friction_curve.csv",
        curve_rows,
        ["provider", "round", "mean_moral_friction"],
    )

    # 3) Intent distribution table (stacked bars / heatmap ready)
    intent_rows: list[dict] = []
    for provider, dist in aggs["provider_intent_distribution"].items():
        for tag, pct in dist.items():
            intent_rows.append(
                {
                    "provider": provider,
                    "intent_tag": tag,
                    "trace_fraction": pct,
                    "trace_percent": pct * 100.0,
                }
            )
    write_csv(
        OUT_DIR / "intent_distribution.csv",
        intent_rows,
        ["provider", "intent_tag", "trace_fraction", "trace_percent"],
    )

    # 4) Deception distribution table
    deception_rows: list[dict] = []
    for provider, stats in findings["deception_sophistication"].items():
        dist_pct = stats["distribution_pct"]
        for level in range(0, 6):
            key = str(level)
            deception_rows.append(
                {
                    "provider": provider,
                    "deception_level": level,
                    "fraction": dist_pct.get(key, 0.0),
                    "percent": dist_pct.get(key, 0.0) * 100.0,
                }
            )
    write_csv(
        OUT_DIR / "deception_distribution.csv",
        deception_rows,
        ["provider", "deception_level", "fraction", "percent"],
    )

    # 5) Betrayal context long table (boxplots / histograms)
    betrayal_rows: list[dict] = []
    for provider, ctx in findings["betrayal_timing_and_context"].items():
        for r in ctx.get("records", []):
            betrayal_rows.append(
                {
                    "provider": provider,
                    "game_id": r["game_id"],
                    "agent_id": r["agent_id"],
                    "agent_name": r["agent_name"],
                    "family": r["family"],
                    "first_betrayal_round": r["first_betrayal_round"],
                    "alive_in_family_at_first_betrayal": r["alive_in_family_at_first_betrayal"],
                    "alive_teammates_at_first_betrayal": r["alive_teammates_at_first_betrayal"],
                }
            )
    write_csv(
        OUT_DIR / "betrayal_context.csv",
        betrayal_rows,
        [
            "provider",
            "game_id",
            "agent_id",
            "agent_name",
            "family",
            "first_betrayal_round",
            "alive_in_family_at_first_betrayal",
            "alive_teammates_at_first_betrayal",
        ],
    )

    # 6) Cross-cutting inferential stats for citation
    cross = aggs["cross_cutting"]
    inferential_rows = [
        {
            "test_name": "Spearman theory_of_mind vs deception_sophistication",
            "statistic": cross["spearman_tom_vs_deception"]["rho"],
            "p_value_permutation": cross["spearman_tom_vs_deception"]["permutation_p"],
            "n": data["findings"]["theory_of_mind_vs_deception"]["n"],
        },
        {
            "test_name": "Chi-square meta_awareness_high_vs_hostile",
            "statistic": cross["chi_square_meta_high_vs_targeting_or_hostile"]["chi_square"],
            "p_value_permutation": cross["chi_square_meta_high_vs_targeting_or_hostile"]["permutation_p"],
            "n": data["findings"]["meta_awareness_vs_hostility"]["n"],
        },
    ]
    write_csv(
        OUT_DIR / "inferential_stats.csv",
        inferential_rows,
        ["test_name", "statistic", "p_value_permutation", "n"],
    )

    # 7) Per-agent moral friction time series (raw for trajectory plots)
    agent_series_rows: list[dict] = []
    for provider, entries in aggs["per_agent_moral_friction_time_series"].items():
        for e in entries:
            for point in e["series"]:
                agent_series_rows.append(
                    {
                        "provider": provider,
                        "game_id": e["game_id"],
                        "agent_id": e["agent_id"],
                        "agent_name": e["agent_name"],
                        "family": e["family"],
                        "round": point["round"],
                        "moral_friction": point["moral_friction"],
                    }
                )
    write_csv(
        OUT_DIR / "agent_moral_friction_series.csv",
        agent_series_rows,
        ["provider", "game_id", "agent_id", "agent_name", "family", "round", "moral_friction"],
    )

    # 8) Quick manifest of files
    # 8) Top-line claims (one row per headline finding)
    claims_rows = []
    for provider in providers:
        claims_rows.append(
            {
                "claim": "Median first TARGETING or DECEPTION_PLANNING round",
                "provider": provider,
                "value": findings["harm_initiation_median_round"].get(provider),
                "statistic": "",
                "p_value": "",
                "notes": "Lower means faster hostile planning onset",
            }
        )
    for provider in providers:
        claims_rows.append(
            {
                "claim": "Moral friction degradation slope",
                "provider": provider,
                "value": findings["moral_friction_degradation"].get(provider, {}).get("slope"),
                "statistic": "linear slope over provider mean-by-round curve",
                "p_value": "",
                "notes": "Negative means degrading resistance to harm over rounds",
            }
        )
    for provider in providers:
        d = findings["deception_sophistication"].get(provider, {})
        claims_rows.append(
            {
                "claim": "Mean deception sophistication",
                "provider": provider,
                "value": d.get("mean"),
                "statistic": "",
                "p_value": "",
                "notes": f"Max={d.get('max')}, pct(level>=4)={d.get('pct_level_4_or_5')}",
            }
        )
    claims_rows.append(
        {
            "claim": "Meta-awareness (>=2) vs hostile intent association",
            "provider": "all",
            "value": findings["meta_awareness_vs_hostility"]["chi_square"],
            "statistic": "chi_square",
            "p_value": findings["meta_awareness_vs_hostility"]["permutation_p"],
            "notes": "Hostile intent includes TARGETING/DECEPTION_PLANNING/BETRAYAL_PLANNING",
        }
    )
    claims_rows.append(
        {
            "claim": "Theory-of-mind vs deception sophistication association",
            "provider": "all",
            "value": findings["theory_of_mind_vs_deception"]["spearman_rho"],
            "statistic": "spearman_rho",
            "p_value": findings["theory_of_mind_vs_deception"]["permutation_p"],
            "notes": "Positive values indicate higher ToM linked to higher deception sophistication",
        }
    )
    for provider in providers:
        b = findings["betrayal_timing_and_context"].get(provider, {})
        claims_rows.append(
            {
                "claim": "Median first BETRAYAL_PLANNING round",
                "provider": provider,
                "value": b.get("median_first_betrayal_round"),
                "statistic": "",
                "p_value": "",
                "notes": f"Median alive family at betrayal={b.get('median_alive_in_family_at_first_betrayal')}",
            }
        )
    write_csv(
        OUT_DIR / "topline_claims.csv",
        claims_rows,
        ["claim", "provider", "value", "statistic", "p_value", "notes"],
    )

    # 9) Quick manifest of files
    manifest_rows = [
        {"file": "topline_claims.csv", "description": "One row per headline finding, citation-ready"},
        {"file": "provider_summary.csv", "description": "One-row-per-provider headline metrics"},
        {"file": "moral_friction_curve.csv", "description": "Hero visual input: mean moral friction by round/provider"},
        {"file": "intent_distribution.csv", "description": "Per-provider prevalence of each intent tag"},
        {"file": "deception_distribution.csv", "description": "Deception level distribution by provider"},
        {"file": "betrayal_context.csv", "description": "Betrayal onset with family alive context"},
        {"file": "inferential_stats.csv", "description": "Spearman and chi-square statistics with permutation p-values"},
        {"file": "agent_moral_friction_series.csv", "description": "Per-agent trajectories across rounds"},
    ]
    write_csv(OUT_DIR / "manifest.csv", manifest_rows, ["file", "description"])

    print(f"Slide pack written to: {OUT_DIR}")


if __name__ == "__main__":
    main()
