import pandas as pd


def _valid_models(data: pd.DataFrame) -> pd.Series:
    models = data["Model"].dropna().astype(str).str.strip()
    return models[models != ""]


def top_models(data: pd.DataFrame, top_n: int = 30) -> pd.DataFrame:
    if top_n < 1:
        raise ValueError("top_n must be at least 1.")

    counts = _valid_models(data).value_counts().nlargest(top_n)
    if counts.empty:
        raise ValueError("No valid Model values found.")

    return counts.rename_axis("Model").reset_index(name="count")


def quality_metrics(data: pd.DataFrame, counts: pd.DataFrame) -> dict:
    models = _valid_models(data)
    valid_count = int(len(models))
    return {
        "row_count": int(len(data)),
        "distinct_models": int(models.nunique()),
        "model_null_rate": float(data["Model"].isna().mean()),
        "top_n": int(len(counts)),
        "top_n_share": float(counts["count"].sum() / valid_count) if valid_count else 0.0,
    }
