import argparse
import json
from pathlib import Path

from src.chart import save_top_models_chart
from src.load import load_registrations
from src.transform import quality_metrics, top_models
from src.validate import validate_registrations


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize Washington EV registration counts by model."
    )
    parser.add_argument("--input", default="asset/Data.csv", help="Path to the registration CSV")
    parser.add_argument("--top-n", type=int, default=30, help="Number of models to keep")
    parser.add_argument("--output-dir", default="outputs", help="Directory for table, chart, and metrics")
    parser.add_argument("--title", default=None, help="Chart title override")
    return parser.parse_args(argv)


def run(args: argparse.Namespace) -> int:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    data = validate_registrations(load_registrations(args.input))
    counts = top_models(data, top_n=args.top_n)
    metrics = quality_metrics(data, counts)
    title = args.title or f"Top {args.top_n} EV models (Washington registrations)"

    table_path = output_dir / "top_models.csv"
    chart_path = output_dir / "top_models.png"
    metrics_path = output_dir / "metrics.json"

    counts.to_csv(table_path, index=False)
    save_top_models_chart(counts, chart_path, title)
    metrics_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {table_path}")
    print(f"Wrote {chart_path}")
    print(f"Wrote {metrics_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    return run(parse_args(argv))
