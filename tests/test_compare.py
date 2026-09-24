from pathlib import Path

import pandas as pd
import pytest

from src.compare import (
    largest_model_changes,
    model_changes,
    population_comparison,
    registration_turnover,
    save_model_change_chart,
    save_population_chart,
)


def _frame(ids, models, vehicle_types):
    return pd.DataFrame(
        {
            "DOL Vehicle ID": ids,
            "Model": models,
            "Electric Vehicle Type": vehicle_types,
        }
    )


def test_population_comparison_counts_types_and_total():
    previous = _frame(
        [1, 2, 3],
        ["MODEL Y", "LEAF", "PRIUS"],
        [
            "Battery Electric Vehicle (BEV)",
            "Battery Electric Vehicle (BEV)",
            "Plug-in Hybrid Electric Vehicle (PHEV)",
        ],
    )
    latest = _frame(
        [1, 2, 4, 5],
        ["MODEL Y", "MODEL Y", "LEAF", "PRIUS"],
        [
            "Battery Electric Vehicle (BEV)",
            "Battery Electric Vehicle (BEV)",
            "Battery Electric Vehicle (BEV)",
            "Plug-in Hybrid Electric Vehicle (PHEV)",
        ],
    )

    result = population_comparison(previous, latest).set_index("category")

    assert result.loc["Battery electric", "change"] == 1
    assert result.loc["Plug-in hybrid", "change"] == 0
    assert result.loc["All vehicles", "previous"] == 3
    assert result.loc["All vehicles", "latest"] == 4
    assert result.loc["All vehicles", "change"] == 1


def test_model_changes_and_turnover():
    previous = _frame([1, 2, 3], ["MODEL Y", "MODEL Y", "LEAF"], ["Battery Electric Vehicle (BEV)"] * 3)
    latest = _frame([1, 4, 5, 6], ["MODEL Y", "MODEL 3", "MODEL 3", "MODEL 3"], ["Battery Electric Vehicle (BEV)"] * 4)

    changes = model_changes(previous, latest).set_index("Model")
    turnover = registration_turnover(previous, latest)

    assert changes.loc["MODEL 3", "change"] == 3
    assert changes.loc["MODEL Y", "change"] == -1
    assert changes.loc["LEAF", "change"] == -1
    assert turnover == {
        "previous_vehicles": 3,
        "latest_vehicles": 4,
        "added": 3,
        "removed": 2,
        "net": 1,
    }


def test_largest_model_changes_keeps_biggest_absolute_moves():
    changes = pd.DataFrame(
        {
            "Model": ["A", "B", "C"],
            "previous": [1, 10, 5],
            "latest": [2, 1, 5],
            "change": [1, -9, 0],
        }
    )

    result = largest_model_changes(changes, limit=1)

    assert list(result["Model"]) == ["B"]


def test_largest_model_changes_rejects_invalid_limit():
    with pytest.raises(ValueError, match="limit must be at least 1"):
        largest_model_changes(pd.DataFrame({"change": [1]}), limit=0)


def test_charts_write_pngs(tmp_path: Path):
    comparison = pd.DataFrame(
        {
            "category": ["Battery electric", "All vehicles"],
            "previous": [2, 3],
            "latest": [3, 4],
            "change": [1, 1],
        }
    )
    changes = pd.DataFrame({"Model": ["MODEL Y", "LEAF"], "change": [2, -1]})

    population_path = save_population_chart(comparison, tmp_path / "population.png")
    model_path = save_model_change_chart(changes, tmp_path / "models.png")

    assert population_path.is_file()
    assert model_path.is_file()
    assert population_path.stat().st_size > 0
    assert model_path.stat().st_size > 0
