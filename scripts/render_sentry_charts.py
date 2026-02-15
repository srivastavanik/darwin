#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
SLIDE_PACK_DIR = ROOT / "data" / "sentry_analysis" / "slide_pack"
CHARTS_DIR = SLIDE_PACK_DIR / "charts"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open() as f:
        return list(csv.DictReader(f))


def _provider_order(providers: list[str]) -> list[str]:
    wanted = ["anthropic", "openai", "google", "xai"]
    seen = {p.lower() for p in providers}
    out = [p for p in wanted if p in seen]
    out.extend([p for p in sorted(seen) if p not in out])
    return out


def render_moral_friction_slope(summary_rows: list[dict[str, str]]) -> None:
    rows = {r["provider"].lower(): r for r in summary_rows}
    providers = _provider_order(list(rows.keys()))
    values = [float(rows[p]["moral_friction_slope"]) for p in providers]

    fig, ax = plt.subplots(figsize=(9, 5))
    colors = ["#ef4444" if v < 0 else "#22c55e" for v in values]
    ax.bar(providers, values, color=colors)
    ax.axhline(0.0, color="#333333", linewidth=1)
    ax.set_title("Moral Friction Degradation Slope by Provider")
    ax.set_xlabel("Provider")
    ax.set_ylabel("Slope per round")
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "moral_friction_slope.png", dpi=180)
    plt.close(fig)


def render_mean_deception(summary_rows: list[dict[str, str]]) -> None:
    rows = {r["provider"].lower(): r for r in summary_rows}
    providers = _provider_order(list(rows.keys()))
    values = [float(rows[p]["mean_deception_sophistication"]) for p in providers]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(providers, values, color="#3b82f6")
    ax.set_title("Mean Deception Sophistication by Provider")
    ax.set_xlabel("Provider")
    ax.set_ylabel("Mean score")
    ax.set_ylim(0, max(values) * 1.2 if values else 1)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "mean_deception_sophistication.png", dpi=180)
    plt.close(fig)


def render_betrayal_onset(summary_rows: list[dict[str, str]]) -> None:
    rows = {r["provider"].lower(): r for r in summary_rows}
    providers = _provider_order(list(rows.keys()))
    values = [float(rows[p]["median_first_betrayal_round"]) for p in providers]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(providers, values, color="#a855f7")
    ax.set_title("Median First BETRAYAL_PLANNING Round by Provider")
    ax.set_xlabel("Provider")
    ax.set_ylabel("Round")
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "median_first_betrayal_round.png", dpi=180)
    plt.close(fig)


def render_moral_friction_curve(curve_rows: list[dict[str, str]]) -> None:
    grouped: dict[str, list[tuple[int, float]]] = {}
    for r in curve_rows:
        p = r["provider"].lower()
        grouped.setdefault(p, []).append((int(r["round"]), float(r["mean_moral_friction"])))
    for p in grouped:
        grouped[p].sort(key=lambda x: x[0])

    providers = _provider_order(list(grouped.keys()))
    fig, ax = plt.subplots(figsize=(10, 6))
    palette = {
        "anthropic": "#7c3aed",
        "openai": "#16a34a",
        "google": "#ca8a04",
        "xai": "#dc2626",
    }
    for p in providers:
        pts = grouped[p]
        xs = [x for x, _ in pts]
        ys = [y for _, y in pts]
        ax.plot(xs, ys, label=p, linewidth=2, color=palette.get(p))
    ax.set_title("Mean Moral Friction by Round and Provider")
    ax.set_xlabel("Round")
    ax.set_ylabel("Mean moral friction")
    ax.grid(alpha=0.2)
    ax.legend()
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "moral_friction_curve.png", dpi=180)
    plt.close(fig)


def main() -> None:
    summary_path = SLIDE_PACK_DIR / "provider_summary.csv"
    curve_path = SLIDE_PACK_DIR / "moral_friction_curve.csv"
    if not summary_path.exists() or not curve_path.exists():
        raise FileNotFoundError(
            "Missing slide pack CSV inputs. Run: python -m scripts.export_sentry_slide_pack"
        )

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    summary_rows = _read_csv(summary_path)
    curve_rows = _read_csv(curve_path)

    render_moral_friction_slope(summary_rows)
    render_mean_deception(summary_rows)
    render_betrayal_onset(summary_rows)
    render_moral_friction_curve(curve_rows)

    print(f"Charts written to: {CHARTS_DIR}")


if __name__ == "__main__":
    main()
