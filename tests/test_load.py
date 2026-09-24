from pathlib import Path

import pytest

from src.load import load_registrations

FIXTURE = Path(__file__).parent / "fixtures" / "sample.csv"


def test_load_registrations_reads_rows():
    data = load_registrations(FIXTURE)
    assert len(data) == 12
    assert "Model" in data.columns


def test_load_registrations_missing_file():
    with pytest.raises(FileNotFoundError, match="Input file not found"):
        load_registrations("missing.csv")
