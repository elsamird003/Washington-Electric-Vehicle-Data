import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd

from src.load import load_registrations

COMPARE_COLUMNS = ["DOL Vehicle ID", "Model", "Electric Vehicle Type"]
TYPE_LABELS = {
    "Battery Electric Vehicle (BEV)": "Battery electric",
    "Plug-in Hybrid Electric Vehicle (PHEV)": "Plug-in hybrid",
}


def population_comparison(previous: pd.DataFrame, latest: pd.DataFrame) -> pd.DataFrame:
    previous_counts = previous["Electric Vehicle Type"].value_counts()
    latest_counts = latest["Electric Vehicle Type"].value_counts()
    rows = []
    for raw_label, label in TYPE_LABELS.items():
        old_count = int(previous_counts.get(raw_label, 0))
        new_count = int(latest_counts.get(raw_label, 0))
        rows.append(
            {
                "category": label,
                "previous": old_count,
                "latest": new_count,
                "change": new_count - old_count,
            }
        )
    rows.append(
        {
            "category": "All vehicles",
            "previous": int(len(previous)),
            "latest": int(len(latest)),
            "change": int(len(latest) - len(previous)),
        }
    )
    return pd.DataFrame(rows)


def model_changes(previous: pd.DataFrame, latest: pd.DataFrame) -> pd.DataFrame:
    previous_counts = _model_counts(previous)
    latest_counts = _model_counts(latest)
    changes = (
        pd.concat(
            [previous_counts.rename("previous"), latest_counts.rename("latest")],
            axis=1,
        )
        .fillna(0)
        .astype(int)
        .rename_axis("Model")
        .reset_index()
    )
    changes["change"] = changes["latest"] - changes["previous"]
    return changes.sort_values(["change", "Model"], ascending=[False, True]).reset_index(drop=True)


def registration_turnover(previous: pd.DataFrame, latest: pd.DataFrame) -> dict[str, int]:
    previous_ids = set(previous["DOL Vehicle ID"])
    latest_ids = set(latest["DOL Vehicle ID"])
    return {
        "previous_vehicles": len(previous_ids),
        "latest_vehicles": len(latest_ids),
        "added": len(latest_ids - previous_ids),
        "removed": len(previous_ids - latest_ids),
        "net": len(latest_ids) - len(previous_ids),
    }


def largest_model_changes(changes: pd.DataFrame, limit: int = 12) -> pd.DataFrame:
    if limit < 1:
        raise ValueError("limit must be at least 1.")
    ranked = changes.reindex(changes["change"].abs().sort_values(ascending=False).index)
    return ranked.head(limit).sort_values("change", ascending=True)


def save_population_chart(comparison: pd.DataFrame, output_path: str | Path) -> Path:
    chart_path = Path(output_path)
    chart_path.parent.mkdir(parents=True, exist_ok=True)

    positions = range(len(comparison))
    width = 0.36
    figure, axis = plt.subplots(figsize=(10, 6))
    previous_bars = axis.bar(
        [position - width / 2 for position in positions],
        comparison["previous"],
        width,
        label="Previous extract",
        color="#8FA4B8",
    )
    latest_bars = axis.bar(
        [position + width / 2 for position in positions],
        comparison["latest"],
        width,
        label="Latest extract",
        color="#1F4E79",
    )
    axis.set_xticks(list(positions))
    axis.set_xticklabels(comparison["category"])
    axis.set_ylabel("Registered vehicles")
    axis.set_title("Registered EVs grew in the latest Washington extract")
    axis.legend(frameon=False)
    axis.yaxis.set_major_formatter(ticker.FuncFormatter(lambda value, _: f"{int(value):,}"))
    axis.set_ylim(0, comparison[["previous", "latest"]].to_numpy().max() * 1.18)
    for bars in (previous_bars, latest_bars):
        axis.bar_label(
            bars,
            labels=[f"{int(value):,}" for value in bars.datavalues],
            padding=3,
            fontsize=9,
        )
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    figure.tight_layout()
    figure.savefig(chart_path, dpi=150)
    plt.close(figure)
    return chart_path


def save_model_change_chart(changes: pd.DataFrame, output_path: str | Path) -> Path:
    chart_path = Path(output_path)
    chart_path.parent.mkdir(parents=True, exist_ok=True)

    colors = ["#2C6E49" if change >= 0 else "#9B3D3D" for change in changes["change"]]
    figure, axis = plt.subplots(figsize=(10, 7))
    axis.barh(changes["Model"], changes["change"], color=colors)
    axis.axvline(0, color="#333333", linewidth=0.8)
    axis.set_xlabel("Change in registered vehicles (latest − previous)")
    axis.set_title("Models with the largest change between extracts")
    axis.xaxis.set_major_formatter(ticker.FuncFormatter(lambda value, _: f"{int(value):,}"))
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    figure.tight_layout()
    figure.savefig(chart_path, dpi=150)
    plt.close(figure)
    return chart_path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare two Washington EV registration extracts and write two charts."
    )
    parser.add_argument("--previous", default="asset/Data.csv", help="Earlier registration CSV")
    parser.add_argument("--latest", default="asset/export.csv", help="Later registration CSV")
    parser.add_argument("--output-dir", default="outputs", help="Directory for the two charts")
    parser.add_argument("--top-n", type=int, default=12, help="Models to include in the change chart")
    return parser.parse_args(argv)


def run(args: argparse.Namespace) -> int:
    previous = load_registrations(args.previous, columns=COMPARE_COLUMNS)
    latest = load_registrations(args.latest, columns=COMPARE_COLUMNS)
    comparison = population_comparison(previous, latest)
    changes = largest_model_changes(model_changes(previous, latest), limit=args.top_n)
    turnover = registration_turnover(previous, latest)

    output_dir = Path(args.output_dir)
    population_path = save_population_chart(comparison, output_dir / "compare_population.png")
    model_path = save_model_change_chart(changes, output_dir / "compare_model_change.png")

    _print_summary(comparison, turnover, changes)
    print(f"Wrote {population_path}")
    print(f"Wrote {model_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    return run(parse_args(argv))


def _model_counts(data: pd.DataFrame) -> pd.Series:
    models = data["Model"].dropna().astype(str).str.strip()
    return models[models != ""].value_counts()


def _print_summary(comparison: pd.DataFrame, turnover: dict[str, int], changes: pd.DataFrame) -> None:
    totals = comparison.loc[comparison["category"] == "All vehicles"].iloc[0]
    print(
        "Registered vehicles: "
        f"{int(totals['previous']):,} -> {int(totals['latest']):,} "
        f"({int(totals['change']):+,})"
    )
    print(
        "Vehicle IDs only in the latest extract: "
        f"{turnover['added']:,}"
    )
    print(
        "Vehicle IDs only in the previous extract: "
        f"{turnover['removed']:,}"
    )
    print("Largest model changes:")
    for row in changes.sort_values("change", ascending=False).itertuples(index=False):
        print(f"  {row.Model}: {int(row.change):+,}")
