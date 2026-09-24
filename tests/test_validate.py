import pandas as pd
import pytest

from src.validate import validate_registrations


def test_validate_accepts_valid_frame():
    data = pd.DataFrame({"Model": ["MODEL Y", "MODEL 3"]})
    assert validate_registrations(data) is data


def test_validate_rejects_missing_model_column():
    with pytest.raises(ValueError, match="Missing required columns: Model"):
        validate_registrations(pd.DataFrame({"Make": ["TESLA"]}))


def test_validate_rejects_empty_file():
    with pytest.raises(ValueError, match="no rows"):
        validate_registrations(pd.DataFrame({"Model": []}))


def test_validate_rejects_high_null_rate():
    data = pd.DataFrame({"Model": [None, None, None, "MODEL Y"]})
    with pytest.raises(ValueError, match="Model null rate"):
        validate_registrations(data)
