from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def save_top_models_chart(counts: pd.DataFrame, output_path: str | Path, title: str) -> Path:
    chart_path = Path(output_path)
    chart_path.parent.mkdir(parents=True, exist_ok=True)

    ordered = counts.sort_values("count", ascending=True)
    plt.figure(figsize=(10, 8))
    sns.barplot(data=ordered, y="Model", x="count", color="steelblue")
    plt.title(title)
    plt.xlabel("Count")
    plt.ylabel("Model")
    plt.tight_layout()
    plt.savefig(chart_path, dpi=150)
    plt.close()
    return chart_path
