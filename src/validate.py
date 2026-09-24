import pandas as pd

REQUIRED_COLUMNS = ("Model",)


def validate_registrations(
    data: pd.DataFrame,
    max_model_null_rate: float = 0.05,
) -> pd.DataFrame:
    if data.empty:
        raise ValueError("Registration file has no rows.")

    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    null_rate = float(data["Model"].isna().mean())
    if null_rate > max_model_null_rate:
        raise ValueError(
            f"Model null rate {null_rate:.1%} exceeds allowed {max_model_null_rate:.1%}."
        )

    return data
