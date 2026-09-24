from pathlib import Path

import pandas as pd


def load_registrations(path: str | Path, columns: list[str] | None = None) -> pd.DataFrame:
    csv_path = Path(path)
    if not csv_path.is_file():
        raise FileNotFoundError(f"Input file not found: {csv_path}")
    return pd.read_csv(csv_path, usecols=columns)
